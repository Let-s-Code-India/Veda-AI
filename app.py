"""Veda AI - run with:  python app.py"""
import os
os.environ.setdefault("FLASK_SKIP_DOTENV", "1")

import io, json, time, socket, threading
from flask import Flask, request, jsonify, send_from_directory, Response
from werkzeug.exceptions import HTTPException

import core, db, media

BASE_DIR = core.BASE_DIR
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"), static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
db.init(os.path.join(BASE_DIR, core.env("DB_PATH", "memory.db")))

PERIOD_LABELS = {600: "10 minutes", 86400: "1 day", 864000: "10 days", 2592000: "30 days",
                 5184000: "60 days", 7776000: "90 days", 31536000: "1 year"}


# ------------------------------------------------------------ security + errors
@app.before_request
def guard():
    pw = core.env("APP_PASSWORD")
    if pw:
        a = request.authorization
        if not a or a.password != pw:
            return Response("Password required", 401, {"WWW-Authenticate": 'Basic realm="Veda AI"'})


@app.errorhandler(Exception)
def on_error(e):
    code = e.code if isinstance(e, HTTPException) else 500
    msg = e.description if isinstance(e, HTTPException) else str(e)
    if code == 413:
        msg = "File is too large (limit 100 MB)."
    if request.path.startswith("/api/"):
        if code >= 500:
            app.logger.exception("Unhandled API error", exc_info=e)
            msg = "An unexpected server error occurred. Check the server log for details."
        return jsonify(error=msg), code
    if isinstance(e, HTTPException):
        return e
    app.logger.exception("Unhandled request error", exc_info=e)
    return Response("Internal server error", 500)


def body():
    return request.get_json(silent=True) or {}


# ------------------------------------------------------------ pages
@app.get("/")
def home():
    return send_from_directory(os.path.join(BASE_DIR, "static"), "index.html")


@app.get("/logo.svg")
def logo():
    r = send_from_directory(BASE_DIR, "logo.svg")
    r.headers["Cache-Control"] = "no-cache"
    return r


@app.get("/api/config")
def config():
    core.load_env()
    return jsonify(name=core.env("APP_NAME", "Veda AI"), tagline=core.env("APP_TAGLINE", "Your team of minds"),
                   version=core.VERSION)


@app.get("/api/platform")
def platform():
    ua = request.headers.get("User-Agent", "")
    kind = core.platform_kind(ua)
    is_mobile = kind in {"ios", "android"}
    return jsonify(platform=kind, is_mobile=is_mobile, is_ios=kind == "ios", is_android=kind == "android")


@app.get("/api/status")
def status():
    core.load_env()
    try:
        import pypdf  # noqa: F401
        pdf = True
    except ImportError:
        pdf = False
    return jsonify(key=bool(core.api_key()), ffmpeg=bool(media.ffmpeg_path()), pdf=pdf,
                   host=core.env("HOST", "127.0.0.1"), version=core.VERSION,
                   password=bool(core.env("APP_PASSWORD")))


@app.get("/api/settings")
def get_settings():
    s = db.settings()
    return jsonify(cleanup_enabled=s["cleanup_enabled"] == "1", cleanup_secs=int(s["cleanup_secs"]),
                   periods=[dict(secs=p, label=PERIOD_LABELS[p]) for p in db.PERIODS])


@app.post("/api/settings")
def save_settings():
    d = body()
    if "cleanup_enabled" in d:
        db.set_setting("cleanup_enabled", "1" if d["cleanup_enabled"] else "0")
    if "cleanup_secs" in d and int(d["cleanup_secs"]) in db.PERIODS:
        db.set_setting("cleanup_secs", int(d["cleanup_secs"]))
    db.sweep()
    return get_settings()


# ------------------------------------------------------------ agents and models
@app.get("/api/agents")
def agents():
    core.load_env()
    out = []
    for a in core.all_agents().values():
        out.append(dict(key=a["key"], id=a["id"], name=a["name"], role=a["role"], level=a["level"],
                        custom=a["custom"], model=core.model_for(a["level"])))
    return jsonify(out)


@app.get("/api/models")
def models():
    core.load_env()
    rows = [("Sutra", "SUTRA", "fast"), ("Shloka", "SHLOKA", "balanced"), ("Veda", "VEDA", "deep"),
            ("Sarathi", "SARATHI", "router"), ("Drishti", "DRISHTI", "images"), ("Shruti", "SHRUTI", "audio and video")]
    return jsonify([dict(name=n, role=r, model=core.model_for(k)) for n, k, r in rows])


@app.post("/api/custom")
def custom_add():
    d = body()
    name = (d.get("name") or "").strip()[:30]
    if not name:
        return jsonify(error="Name is required"), 400
    lv = d.get("level") if d.get("level") in ("sutra", "shloka", "veda") else "sutra"
    db.run("INSERT INTO custom(name,role,prompt,level) VALUES(?,?,?,?)",
           (name, (d.get("role") or "Custom agent")[:60],
            (d.get("prompt") or "You are a helpful assistant.")[:3000], lv))
    return jsonify(ok=1)


@app.delete("/api/custom/<int:i>")
def custom_del(i):
    db.run("DELETE FROM custom WHERE id=?", (i,))
    return jsonify(ok=1)


@app.get("/api/custom/export")
def custom_export():
    rows = db.q("SELECT name, role, prompt, level FROM custom ORDER BY id")
    return download(json.dumps({"veda_agents": 1, "agents": rows}, indent=2, ensure_ascii=False), "veda-agents.json")


@app.post("/api/custom/import")
def custom_import():
    d = request.get_json(silent=True)
    items = d.get("agents") if isinstance(d, dict) else d
    if not isinstance(items, list):
        return jsonify(error="This file is not a Veda agents export."), 400
    n = 0
    for a in items[:50]:
        if not isinstance(a, dict) or not str(a.get("name", "")).strip():
            continue
        lv = a.get("level") if a.get("level") in ("sutra", "shloka", "veda") else "sutra"
        db.run("INSERT INTO custom(name,role,prompt,level) VALUES(?,?,?,?)",
               (str(a["name"]).strip()[:30], str(a.get("role") or "Custom agent")[:60],
                str(a.get("prompt") or "You are a helpful assistant.")[:3000], lv))
        n += 1
    return jsonify(imported=n)


# ------------------------------------------------------------ chats
@app.get("/api/convs")
def convs():
    db.sweep()
    s = db.settings()
    period = int(s["cleanup_secs"])
    warn = db.warn_window(period)
    now = time.time()
    rows = db.q("SELECT id,title,agent,ts,pinned,warn_at FROM convs WHERE deleted_at IS NULL "
                "ORDER BY pinned DESC, ts DESC LIMIT 300")
    for r in rows:
        r["expires_in"] = max(0, int(r["warn_at"] + warn - now)) if r["warn_at"] else None
        del r["warn_at"]
    return jsonify(items=rows, period=period, period_label=PERIOD_LABELS.get(period, "a while"),
                   enabled=s["cleanup_enabled"] == "1")


@app.post("/api/convs")
def conv_new():
    # reuse the newest chat if it is still empty
    last = db.q("SELECT id FROM convs WHERE deleted_at IS NULL AND title='New chat' ORDER BY id DESC LIMIT 1", one=True)
    if last and not db.q("SELECT 1 FROM msgs WHERE conv=? LIMIT 1", (last["id"],)):
        db.run("UPDATE convs SET ts=?, warn_at=NULL WHERE id=?", (time.time(), last["id"]))
        return jsonify(id=last["id"])
    i = db.run("INSERT INTO convs(title,agent,ts) VALUES(?,?,?)", ("New chat", "auto", time.time()))
    return jsonify(id=i)


@app.delete("/api/convs/<int:i>")
def conv_del(i):
    db.run("UPDATE convs SET deleted_at=? WHERE id=?", (time.time(), i))
    return jsonify(ok=1, undo_seconds=10)


@app.post("/api/convs/<int:i>/restore")
def conv_restore(i):
    if not db.q("SELECT 1 FROM convs WHERE id=?", (i,)):
        return jsonify(error="Too late: this chat was already removed."), 410
    db.run("UPDATE convs SET deleted_at=NULL, ts=? WHERE id=?", (time.time(), i))
    return jsonify(ok=1)


@app.post("/api/convs/<int:i>/keep")
def conv_keep(i):
    db.run("UPDATE convs SET kept=?, warn_at=NULL WHERE id=?", (time.time(), i))
    return jsonify(ok=1)


@app.post("/api/convs/<int:i>/pin")
def conv_pin(i):
    pinned = 1 if body().get("pinned") else 0
    db.run("UPDATE convs SET pinned=?, warn_at=NULL WHERE id=?", (pinned, i))
    return jsonify(ok=1, pinned=pinned)


@app.get("/api/convs/<int:i>/msgs")
def conv_msgs(i):
    return jsonify(db.q("SELECT role,content,agent,model FROM msgs WHERE conv=? ORDER BY id", (i,)))


@app.get("/api/convs/<int:i>/summary")
def summary_get(i):
    r = db.q("SELECT summary FROM convs WHERE id=?", (i,), one=True)
    return jsonify(summary=(r or {}).get("summary") or "")


@app.put("/api/convs/<int:i>/summary")
def summary_put(i):
    db.run("UPDATE convs SET summary=? WHERE id=?", ((body().get("summary") or "").strip()[:900], i))
    return jsonify(ok=1)


def download(text, filename, mime="application/json"):
    return Response(text, mimetype=mime,
                    headers={"Content-Disposition": 'attachment; filename="%s"' % filename})


@app.get("/api/convs/<int:i>/export")
def conv_export(i):
    c = db.q("SELECT title FROM convs WHERE id=?", (i,), one=True)
    if not c:
        return jsonify(error="Chat not found"), 404
    lines = ["# " + c["title"], ""]
    for m in db.q("SELECT role,content,agent,model FROM msgs WHERE conv=? ORDER BY id", (i,)):
        who = "You" if m["role"] == "user" else "%s (%s)" % (m["agent"], m["model"])
        lines += ["**%s**" % who, "", m["content"], "", "---", ""]
    return download("\n".join(lines), "veda-chat-%d.md" % i, "text/markdown")


@app.get("/api/export")
def export_all():
    data = {"veda_backup": 1, "exported_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "skill_memory": db.q("SELECT fact, src, ts FROM memory WHERE deleted_at IS NULL ORDER BY id"),
            "agents": db.q("SELECT name, role, prompt, level FROM custom ORDER BY id"), "chats": []}
    for c in db.q("SELECT id,title,summary,ts FROM convs WHERE deleted_at IS NULL ORDER BY id"):
        c["messages"] = db.q("SELECT role,content,agent,model,ts FROM msgs WHERE conv=? ORDER BY id", (c["id"],))
        data["chats"].append(c)
    return download(json.dumps(data, indent=2, ensure_ascii=False), "veda-backup.json")


# ------------------------------------------------------------ talking to the models
@app.post("/api/chat")
def chat():
    try:
        out = core.respond(int(request.form.get("conv", "0")), request.form.get("agent", "auto"),
                           request.form.get("text", "").strip(), request.files.get("file"),
                           request.form.get("deep") == "1")
        return jsonify(out)
    except media.MediaError as e:
        return jsonify(error=str(e)), 400
    except core.UserError as e:
        return jsonify(error=str(e)), 500
    except Exception:
        app.logger.exception("Chat request failed")
        return jsonify(error="An unexpected server error occurred. Check the server log for details."), 500


@app.post("/api/transcribe")
def transcribe():
    f = request.files.get("audio")
    if not f:
        return jsonify(error="No audio received."), 400
    try:
        text = core.transcribe(f.read(), f.filename or "voice.webm")
    except media.MediaError as e:
        return jsonify(error=str(e)), 400
    except core.UserError as e:
        return jsonify(error=str(e)), 500
    except Exception:
        app.logger.exception("Transcription request failed")
        return jsonify(error="An unexpected server error occurred. Check the server log for details."), 500
    return jsonify(text=text)


# ------------------------------------------------------------ skill memory
@app.get("/api/memory")
def mem_list():
    return jsonify(db.q("SELECT id,fact,src,ts FROM memory WHERE deleted_at IS NULL ORDER BY ts DESC LIMIT 300"))


@app.post("/api/memory")
def mem_add():
    t = (body().get("fact") or "").strip()[:300]
    if not t:
        return jsonify(error="Write something to remember."), 400
    db.run("INSERT INTO memory(agent,fact,ts,src) VALUES('all',?,?,'user')", (t, time.time()))
    return jsonify(ok=1)


@app.put("/api/memory/<int:i>")
def mem_edit(i):
    t = (body().get("fact") or "").strip()[:300]
    if not t:
        return jsonify(error="Memory cannot be empty."), 400
    db.run("UPDATE memory SET fact=?, ts=?, src='user' WHERE id=?", (t, time.time(), i))
    return jsonify(ok=1)


@app.delete("/api/memory/<int:i>")
def mem_del(i):
    db.run("UPDATE memory SET deleted_at=? WHERE id=?", (time.time(), i))
    return jsonify(ok=1)


@app.post("/api/memory/<int:i>/restore")
def mem_restore(i):
    db.run("UPDATE memory SET deleted_at=NULL WHERE id=?", (i,))
    return jsonify(ok=1)


@app.post("/api/memory/clear")
def mem_clear():
    db.run("DELETE FROM memory")
    return jsonify(ok=1)


@app.get("/api/memory/export")
def mem_export():
    rows = db.q("SELECT fact FROM memory WHERE deleted_at IS NULL ORDER BY id")
    return download(json.dumps({"veda_memory": 1, "memory": [r["fact"] for r in rows]}, indent=2, ensure_ascii=False),
                    "veda-memory.json")


@app.post("/api/memory/import")
def mem_import():
    d = request.get_json(silent=True)
    items = d.get("memory") if isinstance(d, dict) else d
    if not isinstance(items, list):
        return jsonify(error="This file is not a Veda memory export."), 400
    have = {r["fact"].lower() for r in db.q("SELECT fact FROM memory WHERE deleted_at IS NULL")}
    n = 0
    for it in items[:500]:
        fact = (it.get("fact") if isinstance(it, dict) else str(it)).strip()[:300]
        if fact and fact.lower() not in have:
            db.run("INSERT INTO memory(agent,fact,ts,src) VALUES('all',?,?,'user')", (fact, time.time()))
            have.add(fact.lower())
            n += 1
    return jsonify(imported=n)


# ------------------------------------------------------------ start up
def sweeper():
    while True:
        time.sleep(5)
        try:
            db.sweep()
        except Exception:
            pass


def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def main():
    host, port = core.env("HOST", "127.0.0.1"), int(core.env("PORT", "5000"))
    threading.Thread(target=sweeper, daemon=True).start()
    print("\n  %s v%s" % (core.env("APP_NAME", "Veda AI"), core.VERSION))
    print("  Open in your browser:  http://localhost:%d" % port)
    if host == "0.0.0.0":
        ip = lan_ip()
        if ip:
            print("  Other devices on this network:  http://%s:%d" % (ip, port))
        if not core.env("APP_PASSWORD"):
            print("  Tip: set APP_PASSWORD in .env so only people you trust can use your API key.")
    if not core.api_key():
        print("\n  ! No GROQ_API_KEY found. Copy .env.example to .env and paste your key.\n")
    if not media.ffmpeg_path():
        print("  (ffmpeg not found. Optional: only needed for unusual audio/video formats.)")
    print("  Press Ctrl + C to stop.\n")
    try:
        try:
            from waitress import serve
        except ImportError:
            serve = None
        if serve:
            serve(app, host=host, port=port, threads=8, channel_timeout=300, ident="veda")
        else:
            app.run(host=host, port=port, threaded=True)
    except OSError:
        print("\n  Port %d is already in use. Stop the other server (pkill -f app.py) "
              "or change PORT in .env.\n" % port)


if __name__ == "__main__":
    main()
