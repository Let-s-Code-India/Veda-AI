"""Veda AI engine: model calls, routing, agents, pipelines and memory."""
import os, re, time, ipaddress, socket, threading, requests
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor

import db, media
from agents import BASE, BUILTIN, SKIP_ROUTE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API = "https://api.groq.com/openai/v1"
VERSION = "1.0.0"

DEFAULT_MODELS = {
    "SUTRA": "openai/gpt-oss-20b",
    "SHLOKA": "qwen/qwen3.8-27b",
    "VEDA": "openai/gpt-oss-120b",
    "SARATHI": "openai/gpt-oss-20b",
    "DRISHTI": "qwen/qwen3.8-27b",
    "SHRUTI": "whisper-large-v3-turbo",
}
UA = {"User-Agent": "Mozilla/5.0 (VedaAI)"}


class UserError(Exception):
    """An expected failure that is safe and useful to show to the user."""


# ---------------------------------------------------------------- settings
def load_env():
    """Read .env on every call so model names can be changed without a restart."""
    path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")


load_env()


def env(k, d=""):
    return os.environ.get(k, d)


def api_key():
    return env("GROQ_API_KEY").strip()


def platform_kind(user_agent=""):
    ua = (user_agent or "").lower()
    if "ish" in ua or "ipad" in ua or "iphone" in ua or "ipod" in ua:
        return "ios"
    if "android" in ua:
        return "android"
    if "windows" in ua:
        return "windows"
    if "mac os" in ua or "darwin" in ua:
        return "macos"
    if "linux" in ua:
        return "linux"
    return "unknown"


def model_for(level):
    lv = level.upper()
    return env("MODEL_" + lv) or DEFAULT_MODELS.get(lv) or DEFAULT_MODELS["SUTRA"]


def all_agents():
    out = {}
    for k, a in BUILTIN.items():
        a = dict(a)
        a["level"] = env("LEVEL_" + k.upper(), a["level"]).lower()
        a.update(key=k, custom=False, id=None)
        out[k] = a
    for r in db.q("SELECT * FROM custom"):
        k = "c%d" % r["id"]
        out[k] = dict(key=k, id=r["id"], name=r["name"], role=r["role"], prompt=r["prompt"],
                      level=r["level"], pipe="single", custom=True, use=r["role"])
    return out


# ---------------------------------------------------------------- model calls
def _friendly(status, msg):
    if status == 401:
        return "Groq rejected your API key. Check GROQ_API_KEY in your .env file."
    if status == 429:
        return "Rate limit reached. Wait a minute and try again. " + msg[:120]
    if status == 413:
        return "The request was too large for this model. Try a shorter message or smaller file."
    return msg


def chat(model, messages, temp=0.7):
    if not api_key():
        raise UserError("No API key found. Add GROQ_API_KEY to your .env file (see the README).")
    err = "unknown error"
    isimg = isinstance(messages[-1].get("content"), list)
    tries = [model] if isimg else list(dict.fromkeys([model, model_for("sutra")]))
    for m in tries:
        try:
            r = requests.post(API + "/chat/completions", headers={"Authorization": "Bearer " + api_key()},
                              timeout=120, json={"model": m, "messages": messages, "temperature": temp})
            try:
                j = r.json()
            except Exception:
                j = {}
            if r.status_code == 200:
                t = j["choices"][0]["message"].get("content") or ""
                t = re.sub(r"(?s)<think>.*?</think>", "", t).strip()
                if t:
                    return t, m
                err = "%s: empty reply" % m
                continue
            msg = j.get("error", {}).get("message", r.text[:200])
            err = "%s: %s" % (m, _friendly(r.status_code, msg))
            if r.status_code in (401, 429):
                break
        except requests.exceptions.RequestException as e:
            err = "Could not reach Groq. Check your internet connection. (%s)" % e.__class__.__name__
            break
    raise UserError(err)


def transcribe(data, filename, is_video=False):
    if not api_key():
        raise UserError("No API key found. Add GROQ_API_KEY to your .env file (see the README).")
    data, name = media.prepare_audio(data, filename, is_video)
    try:
        r = requests.post(API + "/audio/transcriptions", headers={"Authorization": "Bearer " + api_key()},
                          timeout=300, files={"file": (name, data)}, data={"model": model_for("shruti")})
    except requests.exceptions.RequestException as e:
        raise UserError("Could not reach Groq. Check your internet connection. (%s)" % e.__class__.__name__)
    if r.status_code != 200:
        try:
            msg = r.json().get("error", {}).get("message", r.text[:200])
        except Exception:
            msg = r.text[:200]
        raise UserError("Transcription failed: " + _friendly(r.status_code, msg))
    return (r.json().get("text") or "").strip()


# ---------------------------------------------------------------- links (SSRF safe)
def safe_url(u):
    p = urlparse(u)
    if p.scheme not in ("http", "https") or not p.hostname:
        return False
    try:
        for info in socket.getaddrinfo(p.hostname, p.port or (443 if p.scheme == "https" else 80)):
            ip = ipaddress.ip_address(info[4][0])
            if (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
                    or ip.is_multicast or ip.is_unspecified):
                return False
    except Exception:
        return False
    return True


def fetch_page(u):
    for _ in range(4):
        if not safe_url(u):
            raise Exception("this address is not allowed")
        r = requests.get(u, timeout=15, headers=UA, allow_redirects=False, stream=True)
        if r.status_code in (301, 302, 303, 307, 308) and r.headers.get("Location"):
            u = urljoin(u, r.headers["Location"])
            continue
        raw = next(r.iter_content(1500000), b"")
        if "pdf" in r.headers.get("Content-Type", "").lower():
            return media.pdf_text(raw, 6000)
        txt = raw.decode(r.encoding or "utf-8", "ignore")
        txt = re.sub(r"(?s)<(script|style|noscript).*?</\1>", " ", txt)
        txt = re.sub(r"<[^>]+>", " ", txt)
        return re.sub(r"\s+", " ", txt)[:6000]
    raise Exception("too many redirects")


def find_links(text):
    return [u.rstrip(".,;:!?") for u in re.findall(r"https?://[^\s)>\]\"']+", text)][:3]


def read_links(text):
    out = ""
    for u in find_links(text):
        try:
            out += "\n\n[Page %s]:\n%s" % (u, fetch_page(u))
        except Exception as e:
            out += "\n[Could not open %s: %s]" % (u, e)
    return out


# ---------------------------------------------------------------- routing
def route(text, kind, has_link):
    if kind == "image":
        return "drishti"
    if kind == "av":
        return "shruti"
    if has_link:
        return "narada"
    ags = all_agents()
    menu = "\n".join("%s = %s" % (k, a.get("use", a["role"])) for k, a in ags.items() if k not in SKIP_ROUTE)
    p = ("You are Sarathi, the router of a team of agents. Pick the single best agent for the user's message. "
         "Reply with only the agent key, nothing else. If unsure, reply chanakya.\n\n" + menu +
         "\n\nUser message: " + text[:600])
    try:
        out, _ = chat(model_for("sarathi"), [{"role": "user", "content": p}], 0)
        out = re.sub(r"[^a-z0-9]", "", out.lower())
        if out in ags and out not in SKIP_ROUTE:
            return out
    except Exception:
        pass
    return "chanakya"


# ---------------------------------------------------------------- memory
def recall():
    """Skill memory: shared by every agent."""
    rows = db.q("SELECT fact FROM memory WHERE deleted_at IS NULL ORDER BY ts DESC LIMIT 15")
    return "\n".join("- " + r["fact"] for r in rows)


def _looks_secret(s):
    return bool(re.search(r"gsk_|sk-[A-Za-z0-9]|api[_ ]?key|password", s, re.I))


def maintain(conv, user, reply):
    """Background job: update this chat's summary and the shared skill memory."""
    try:
        c = db.q("SELECT summary FROM convs WHERE id=?", (conv,), one=True)
        if c is None:
            return
        old = c.get("summary") or ""
        facts = db.q("SELECT id, fact FROM memory WHERE deleted_at IS NULL ORDER BY ts DESC LIMIT 25")
        listing = "\n".join("%d. %s" % (i + 1, f["fact"]) for i, f in enumerate(facts)) or "(none)"
        p = ("You maintain two things for a chat assistant.\n"
             "1) SUMMARY: update the running summary of this conversation in at most 100 words: what the user wants, "
             "key decisions, facts given and open tasks. Plain text.\n"
             "2) MEMORY: long-term facts about the USER (name, language, preferences, projects, skills, goals) that stay "
             "useful in any future chat. Current numbered facts:\n" + listing + "\n"
             "If the exchange reveals a new lasting fact reply `ADD: <short sentence>`. If it changes or corrects fact N "
             "reply `UPDATE N: <new sentence>`. Otherwise reply `NONE`. Never store one-off requests, secrets, passwords "
             "or API keys.\n\nReply exactly in this format:\nSUMMARY: <text>\nMEMORY: <ADD / UPDATE / NONE>\n\n"
             "Previous summary: " + (old or "(none)") + "\nUser: " + user[:800] + "\nAssistant: " + reply[:800])
        out, _ = chat(model_for("sutra"), [{"role": "user", "content": p}], 0)
        m = re.search(r"SUMMARY:\s*(.*?)(?=\n\s*MEMORY:|\Z)", out, re.S)
        if m and m.group(1).strip():
            db.run("UPDATE convs SET summary=? WHERE id=?", (m.group(1).strip()[:900], conv))
        m = re.search(r"MEMORY:\s*(.*)", out, re.S)
        line = (m.group(1).strip().splitlines() or [""])[0].strip() if m else ""
        now = time.time()
        if line.upper().startswith("ADD:"):
            fact = line[4:].strip()
            if fact and len(fact) < 200 and not _looks_secret(fact):
                if not any(fact.lower() == f["fact"].lower() for f in facts):
                    db.run("INSERT INTO memory(agent,fact,ts,src) VALUES('all',?,?,'auto')", (fact, now))
        elif line.upper().startswith("UPDATE"):
            mm = re.match(r"UPDATE\s+(\d+)\s*:\s*(.+)", line, re.I)
            if mm:
                n, fact = int(mm.group(1)), mm.group(2).strip()
                if 1 <= n <= len(facts) and fact and len(fact) < 200 and not _looks_secret(fact):
                    db.run("UPDATE memory SET fact=?, ts=? WHERE id=?", (fact, now, facts[n - 1]["id"]))
    except Exception:
        pass


# ---------------------------------------------------------------- pipelines
def _safe(model, msgs, temp):
    try:
        return chat(model, msgs, temp)
    except Exception:
        return None


def council(sysmsg, msgs, question):
    """Deep mode (Panchayat): two models draft in parallel, the Veda model merges."""
    ma, mb = model_for("veda"), model_for("shloka")
    with ThreadPoolExecutor(2) as ex:
        fa, fb = ex.submit(_safe, ma, msgs, 0.6), ex.submit(_safe, mb, msgs, 0.6)
        ra, rb = fa.result(), fb.result()
    drafts = [r for r in (ra, rb) if r]
    if not drafts:
        raise UserError("Both models failed. Check the model names in your .env file.")
    if len(drafts) == 1:
        return drafts[0][0], "one draft: " + drafts[0][1].split("/")[-1]
    merge = [{"role": "system", "content": sysmsg},
             {"role": "user", "content":
              "Question:\n%s\n\nDraft A:\n%s\n\nDraft B:\n%s\n\n"
              "Write the single best final answer. Keep what is correct, fix mistakes, drop repetition, "
              "and keep the user's language and format. Do not mention the drafts." % (question[:3000], ra[0], rb[0])}]
    final, used = chat(ma, merge, 0.4)
    return final, "%s + %s draft -> %s merges" % (ra[1].split("/")[-1], rb[1].split("/")[-1], used.split("/")[-1])


def read_attachment(f):
    """Return (image_data_url, extra_text, kind)."""
    name = f.filename or "file"
    mime = (f.mimetype or "").lower()
    ext = os.path.splitext(name)[1].lower()
    data = f.read()
    if mime.startswith("image/"):
        return media.prepare_image(data, mime), "", "image"
    is_video = mime.startswith("video/") or ext in media.VIDEO_EXT
    if is_video or mime.startswith("audio/") or ext in media.AUDIO_EXT:
        text = transcribe(data, name, is_video)
        return None, "\n\n[Transcript of %s]:\n%s" % (name, text[:8000]), "av"
    if ext == ".pdf" or mime == "application/pdf":
        return None, "\n\n[PDF %s]:\n%s" % (name, media.pdf_text(data)), "doc"
    if b"\x00" in data[:4000]:
        raise Exception("This file type is not supported yet. Supported: images, audio, video, PDF and text or code files.")
    return None, "\n\n[File %s]:\n%s" % (name, data.decode("utf-8", "ignore")[:8000]), "doc"


def respond(conv, key, text, f, deep=False):
    load_env()
    c = db.q("SELECT id, title, summary FROM convs WHERE id=? AND deleted_at IS NULL", (conv,), one=True)
    if not c:
        raise UserError("This chat no longer exists. Start a new chat.")
    ags = all_agents()
    image, extra, kind = None, "", ""
    if f:
        image, extra, kind = read_attachment(f)
    links = find_links(text)
    extra += read_links(text)

    routed = False
    if key == "auto" or key not in ags:
        key = route(text or "attachment", kind, bool(links))
        routed = True
    ag = ags[key]
    trace = []
    full = (text or "Please look at the attached content.") + extra

    hist = db.q("SELECT role, content FROM msgs WHERE conv=? ORDER BY id DESC LIMIT 10", (conv,))[::-1]
    sysmsg = BASE + "\n\nToday is " + time.strftime("%A, %d %B %Y") + ".\n\n" + ag["prompt"]
    mem = recall()
    if mem:
        sysmsg += "\n\nWhat you know about the user (use only when relevant):\n" + mem
    if c.get("summary"):
        sysmsg += "\n\nSummary of this chat so far (older context):\n" + c["summary"]

    level = ag["level"]
    if level == "shruti":
        level = "sutra"
    if image and key == "drishti":
        model = model_for("drishti")
        content = [{"type": "text", "text": full}, {"type": "image_url", "image_url": {"url": image}}]
        msgs = [{"role": "system", "content": sysmsg}] + hist + [{"role": "user", "content": content}]
        reply, used = chat(model, msgs)
        trace.append("Drishti: " + used)
    else:
        if image:
            d, _ = chat(model_for("drishti"), [{"role": "user", "content": [
                {"type": "text", "text": "Describe this image in detail. Transcribe any visible text exactly."},
                {"type": "image_url", "image_url": {"url": image}}]}], 0.2)
            full += "\n\n[Image description from Drishti]:\n" + d
            trace.append("Drishti sees")
        if level in ("drishti",):
            level = "shloka"
        if ag["pipe"] == "plan" and len(full) > 150 and not deep:
            plan, _ = chat(model_for("sutra"), [{"role": "user", "content":
                "Make a short numbered plan (max 5 steps) for answering this well. Plan only, do not answer:\n" + full[:1500]}], 0.3)
            sysmsg += "\n\nFollow this plan silently and do not mention it:\n" + plan
            trace.append("Sutra plans")
        msgs = [{"role": "system", "content": sysmsg}] + hist + [{"role": "user", "content": full}]
        if deep:
            reply, used = council(sysmsg, msgs, full)
            trace.append("Panchayat: " + used)
        else:
            reply, used = chat(model_for(level), msgs)
            trace.append("%s: %s" % (level.capitalize(), used))
    label = " -> ".join(trace)

    now = time.time()
    who = ag["name"] + (" (auto)" if routed else "")
    saved = text + ("\n[attachment: %s]" % f.filename if f else "")
    db.run("INSERT INTO msgs(conv,role,content,agent,model,ts) VALUES(?,?,?,?,?,?)", (conv, "user", saved, "", "", now))
    db.run("INSERT INTO msgs(conv,role,content,agent,model,ts) VALUES(?,?,?,?,?,?)", (conv, "assistant", reply, who, label, now))
    if c["title"] == "New chat":
        db.run("UPDATE convs SET title=? WHERE id=?", ((text or (f.filename if f else "") or "Chat")[:40], conv))
    db.run("UPDATE convs SET ts=?, warn_at=NULL WHERE id=?", (now, conv))
    if len(text) >= 12:
        threading.Thread(target=maintain, args=(conv, text, reply), daemon=True).start()
    return dict(reply=reply, agent=who, label=label, key=key)
