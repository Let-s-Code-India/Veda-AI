"""SQLite storage: chats, messages, skill memory, custom agents, settings.

Chat memory  = the per-chat summary stored in convs.summary (deleted with the chat).
Skill memory = the `memory` table: facts about the user, shared by every agent and
               kept even when chats are deleted.
"""
import os, time, sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "memory.db")

UNDO_GRACE = 15                      # seconds a deleted item can still be restored
PERIODS = [600, 86400, 864000, 2592000, 5184000, 7776000, 31536000]
DEFAULTS = {"cleanup_enabled": "1", "cleanup_secs": "2592000"}


def conn():
    c = sqlite3.connect(DB, timeout=15)
    c.row_factory = sqlite3.Row
    return c


def q(sql, args=(), one=False):
    c = conn()
    try:
        rows = [dict(r) for r in c.execute(sql, args).fetchall()]
    finally:
        c.close()
    if one:
        return rows[0] if rows else None
    return rows


def run(sql, args=()):
    """Execute a write. Returns lastrowid."""
    c = conn()
    try:
        cur = c.execute(sql, args)
        c.commit()
        return cur.lastrowid
    finally:
        c.close()


ins = run


def _add_col(c, table, col, ddl):
    cols = [r[1] for r in c.execute("PRAGMA table_info(%s)" % table)]
    if col not in cols:
        c.execute("ALTER TABLE %s ADD COLUMN %s %s" % (table, col, ddl))


def init(path=None):
    global DB
    if path:
        DB = path
    c = conn()
    try:
        try:
            c.execute("PRAGMA journal_mode=WAL")
        except Exception:
            pass
        c.executescript("""
        CREATE TABLE IF NOT EXISTS convs(id INTEGER PRIMARY KEY, title TEXT, agent TEXT, ts REAL);
        CREATE TABLE IF NOT EXISTS msgs(id INTEGER PRIMARY KEY, conv INTEGER, role TEXT, content TEXT, agent TEXT, model TEXT, ts REAL);
        CREATE TABLE IF NOT EXISTS memory(id INTEGER PRIMARY KEY, agent TEXT, fact TEXT, ts REAL);
        CREATE TABLE IF NOT EXISTS custom(id INTEGER PRIMARY KEY, name TEXT, role TEXT, prompt TEXT, level TEXT);
        CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY, v TEXT);
        CREATE INDEX IF NOT EXISTS idx_msgs_conv ON msgs(conv);
        """)
        # upgrades for databases created by older versions
        _add_col(c, "convs", "pinned", "INTEGER DEFAULT 0")
        _add_col(c, "convs", "summary", "TEXT DEFAULT ''")
        _add_col(c, "convs", "kept", "REAL")
        _add_col(c, "convs", "warn_at", "REAL")
        _add_col(c, "convs", "deleted_at", "REAL")
        _add_col(c, "memory", "src", "TEXT DEFAULT 'auto'")
        _add_col(c, "memory", "deleted_at", "REAL")
        c.commit()
    finally:
        c.close()
    sweep()


# ---------- settings ----------
def settings():
    s = dict(DEFAULTS)
    for r in q("SELECT k, v FROM settings"):
        s[r["k"]] = r["v"]
    return s


def set_setting(k, v):
    run("INSERT INTO settings(k, v) VALUES(?, ?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, str(v)))


def warn_window(period):
    """How long a chat stays marked red before it is deleted."""
    return min(172800, period / 5.0)


# ---------- deleting ----------
def delete_conv_hard(i):
    run("DELETE FROM msgs WHERE conv=?", (i,))
    run("DELETE FROM convs WHERE id=?", (i,))


def sweep():
    """Housekeeping: purge soft-deleted items and apply the auto-cleanup policy."""
    now = time.time()
    cutoff = now - UNDO_GRACE
    for r in q("SELECT id FROM convs WHERE deleted_at IS NOT NULL AND deleted_at < ?", (cutoff,)):
        delete_conv_hard(r["id"])
    run("DELETE FROM memory WHERE deleted_at IS NOT NULL AND deleted_at < ?", (cutoff,))

    s = settings()
    if s["cleanup_enabled"] != "1":
        run("UPDATE convs SET warn_at=NULL WHERE warn_at IS NOT NULL")
        return
    try:
        period = int(s["cleanup_secs"])
    except ValueError:
        period = int(DEFAULTS["cleanup_secs"])
    warn = warn_window(period)
    # 1) chats untouched for `period` get a red mark; the warning clock starts now
    run("UPDATE convs SET warn_at=? WHERE deleted_at IS NULL AND pinned=0 AND warn_at IS NULL "
        "AND MAX(COALESCE(ts,0), COALESCE(kept,0)) < ?", (now, now - period))
    # 2) chats whose warning ran out are deleted with their chat memory
    for r in q("SELECT id FROM convs WHERE deleted_at IS NULL AND pinned=0 AND warn_at IS NOT NULL AND warn_at < ?",
               (now - warn,)):
        delete_conv_hard(r["id"])
