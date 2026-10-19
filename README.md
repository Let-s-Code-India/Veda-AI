<p align="center"><img src="logo.svg" alt="Veda AI logo" height="90"></p>

<h1 align="center">Veda AI</h1>

<p align="center"><b>Your own team of AI agents, running on your own device.</b><br>
Bring a free Groq API key. No account, no cloud server, no model picking.<br>
Works on Android (Termux), Windows, macOS and Linux.</p>

<p align="center">Created by <b>Ayush Giri</b>, founder of <a href="https://github.com/Let-s-Code-India">Let's Code India</a> &middot; <a href="mailto:ayushgiri.ai.21@gmail.com">YOUR-EMAIL@example.com</a></p>

---

## What is this?

Veda AI is a small chatbot website that runs **on your own computer or phone** (at `http://localhost:5000`).
You type a message, attach an image, a video, an audio file or a PDF, or paste a link.
A router called **Sarathi** reads it, picks the right specialist **agent**, and sends it to the right Groq model.
You never choose a model. You only paste your own API key once.

Your chats and memory are stored in a file on your own device. Nothing goes anywhere except to Groq, which answers your questions.

## Features

- **15 specialist agents** with detailed instructions: coding, stories, poetry, maths, tutoring, health information, money, critique, translation, research, summaries, notes, images and audio.
- **Automatic routing** (Sarathi). Or tap an agent yourself.
- **Understands everything:** images, audio, video, PDF, text and code files, and web links.
- **Deep mode:** two models write drafts in parallel and a third step merges the best answer.
- **Two kinds of memory**
  - *Skill memory:* what every agent knows about you (language, goals, projects). Shared by all agents. Survives chat deletion. You can add, edit, delete, export and import it.
  - *Chat memory:* a running summary of each chat so an agent can continue where you left off. It is deleted with the chat.
- **Voice input:** tap the microphone and speak (Whisper transcribes it).
- **Safe deleting:** deleting a chat or memory shows a 10-second **Undo**.
- **Auto-cleanup (optional):** old chats get a red dot, you get a short warning, then they are removed to save storage. Pin a chat to keep it forever.
- **Your own agents:** create agents with your own instructions, export and share them as JSON.
- **Light and dark themes**, mobile friendly layout, chat export to Markdown, full backup to JSON.
- **Your logo:** drop a `logo.svg` in the project folder and it is used everywhere.

## The agents

| Agent | Does |
|---|---|
| Sarathi | The router. Picks the agent for you |
| Vishwakarma | Coding and terminal help |
| Saraswati | Stories, scripts, fight scenes |
| Valmiki | Poetry, shayari, lyrics |
| Chanakya | Strategy, reasoning, general questions |
| Aryabhata | Maths and science |
| Dronacharya | Tutor and exam preparation |
| Dhanvantari | Health information (not a doctor) |
| Kubera | Money, business, careers |
| Vidura | Honest critic and reviewer |
| Panini | Translation, grammar, writing |
| Narada | Reads links and web pages |
| Sanjaya | Summaries of long text and files |
| Chitragupta | Notes, tables, lists, data |
| Drishti | Understands images |
| Shruti | Understands audio and video |

Models have three levels: **Sutra** (fast), **Shloka** (balanced) and **Veda** (deep). Which Groq model sits at each level is set in `.env`.

---

## Before you start (2 minutes)

1. Get a **free Groq API key**: open <https://console.groq.com/keys>, sign in, click **Create API Key**, and copy the key. It starts with `gsk_`.
2. Keep that key private. Never post it online.

---

## Install

Pick your device. Every route ends with `http://localhost:5000` in your browser.

### Android (Termux)

1. Install **Termux from F-Droid** (<https://f-droid.org/packages/com.termux/>). The Play Store version is outdated.
2. Open Termux and run these one at a time:

```bash
pkg update -y && pkg upgrade -y
pkg install -y python git
git clone https://github.com/Let-s-Code-India/Veda-AI.git
cd Veda-AI
bash install.sh
```

3. Open the settings file and paste your key:

```bash
nano .env
```

Type your key after `GROQ_API_KEY=`. Save with **Ctrl + O**, **Enter**, then exit with **Ctrl + X**.
(Termux has no Ctrl key by default: use the extra keys row above the keyboard.)

4. Start the app:

```bash
bash start.sh
```

(You can also run `python app.py`. It does the same thing.)

5. Open **Chrome** and go to `http://localhost:5000`.

Tips for Termux:
- To stop the app press **Ctrl + C**. To start again later: `cd Veda-AI && bash start.sh`
- Pull down the Termux notification and tap **Acquire wakelock** so Android does not stop it in the background.
- If `pkg install ffmpeg` shows a `CANNOT LINK EXECUTABLE` error, run `pkg upgrade -y` and then `pkg install -y ffmpeg` again.

### Windows

1. Install **Python 3.10 or newer** from <https://www.python.org/downloads/>. On the first screen **tick "Add Python to PATH"**.
2. Install **Git** from <https://git-scm.com/download/win> (or download the project as a ZIP from GitHub and unzip it).
3. Open **PowerShell** and run:

```powershell
git clone https://github.com/Let-s-Code-India/Veda-AI.git
cd Veda-AI
.\install.bat
```

4. Open the settings file in Notepad and paste your key after `GROQ_API_KEY=`:

```powershell
notepad .env
```

5. Start the app: double-click **start.bat** (or run `py app.py`).
6. Open your browser at `http://localhost:5000`.

### Linux and macOS

```bash
git clone https://github.com/Let-s-Code-India/Veda-AI.git
cd Veda-AI
bash install.sh
nano .env          # paste your key after GROQ_API_KEY=
bash start.sh
```

Then open `http://localhost:5000`. If `bash start.sh` does not work, run `python3 app.py`.

### Manual install (any system)

If you do not want to use the scripts:

```bash
python3 -m venv .venv                 # optional but recommended
source .venv/bin/activate             # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                  # Windows: copy .env.example .env
# edit .env and paste your key
python app.py
```

---

## Using the app

1. **Just type.** Sarathi chooses the agent. The badge above each answer shows which agent and models worked.
2. **Pick an agent yourself** with the chips under the title.
3. **Attach files** with the **+** button: images, audio, video, PDFs, text and code. A link in your message is read automatically.
4. **Speak** with the microphone button. Your words appear in the text box so you can fix them before sending.
5. **Deep mode** (button above the text box) is slower and uses more of your free quota, but gives the best answer for hard questions.
6. **Memory** (sidebar): add, edit or delete what agents know about you. Export it to move to another device.
7. **Agents** (sidebar): create your own agent, export it, or import one a friend shared.
8. **Settings** (sidebar): auto-cleanup, full backup, and a status check for your key and optional tools.
9. Header buttons: **pin** a chat, **export** it as Markdown, switch **light / dark**.

### About ffmpeg (optional)

ffmpeg is a small free tool that converts files. Veda AI uses it **only** when needed: for audio such as `.aac`, video such as `.mkv` or `.mov`, and very large photos. Common formats (mp3, wav, m4a, mp4, webm) work without it. If a file needs it and it is missing, the app tells you how to install it. `install.sh` and `install.bat` try to install it for you.

| System | Command |
|---|---|
| Termux | `pkg install ffmpeg` |
| Windows | `winget install ffmpeg` |
| macOS | `brew install ffmpeg` |
| Linux | `sudo apt install ffmpeg` |
| Any (fallback) | `pip install imageio-ffmpeg` |

---

## Settings reference (`.env`)

| Setting | Meaning | Default |
|---|---|---|
| `GROQ_API_KEY` | Your Groq key. **Required** | empty |
| `PORT` | Port number of the website | `5000` |
| `HOST` | `127.0.0.1` = this device only. `0.0.0.0` = other devices on your network too | `127.0.0.1` |
| `APP_PASSWORD` | Optional password (any username). Use it when `HOST=0.0.0.0` | empty |
| `APP_NAME`, `APP_TAGLINE` | Text next to your logo. Empty name hides it | `Veda AI` |
| `MODEL_SUTRA / SHLOKA / VEDA` | Models for the three levels | see `.env.example` |
| `MODEL_SARATHI` | Model that routes your messages | `openai/gpt-oss-20b` |
| `MODEL_DRISHTI` | Model that understands images (must support vision) | `qwen/qwen3.8-27b` |
| `MODEL_SHRUTI` | Speech model for audio, video and the microphone | `whisper-large-v3-turbo` |
| `LEVEL_<AGENT>` | Level each agent uses: `sutra`, `shloka` or `veda` | see `.env.example` |
| `DB_PATH` | Database file name | `memory.db` |

Edit `.env` any time. Model and level changes apply to the next message with no restart. Change `PORT`, `HOST` or the password, then restart.

**Groq renames models now and then.** If you see an error like *"model does not exist"*, open the model list in the Groq playground, copy the current name, and paste it into `.env`.

## Use it from another device on your Wi-Fi or hotspot

1. In `.env` set `HOST=0.0.0.0` and a password: `APP_PASSWORD=choose-something`.
2. Restart the app. It prints a line like `http://192.168.1.5:5000`.
3. Open that address on the other device.

Notes: everyone who opens it uses **your** Groq key, so always set a password. The microphone only works on `localhost` or `https`, so on other devices typing, files and images work but voice may be blocked by the browser.

## Updating

```bash
git pull
```

Your `.env` and `memory.db` are never touched, because they are not part of the repository. If new settings appear in `.env.example`, copy them into your `.env`.

## Troubleshooting

| Problem | What to do |
|---|---|
| Browser shows a blank page or "refused to connect" | The app is not running. Start it again and keep the terminal open |
| `Address already in use` / port busy | An old copy is running. Termux/Linux/macOS: `pkill -f app.py`. Windows: close the old window. Or change `PORT` in `.env` |
| "No API key found" or "rejected your API key" | Check `GROQ_API_KEY` in `.env`: no spaces, no quotes needed, the full `gsk_...` key |
| "model does not exist" | Put a current model name in `.env` (see above) |
| "Rate limit reached" | You hit the free quota. Wait a minute. Deep mode uses 3 calls per message |
| Image answer fails | Make sure `MODEL_DRISHTI` is a model that supports image input |
| Audio or video fails | Install ffmpeg (see table above). Files over 100 MB are rejected |
| Voice button says microphone unavailable | Open the app at `http://localhost:5000`, and allow the microphone in Chrome |
| `./start.sh: Permission denied` | Run it with `bash start.sh`, or run `python app.py` |
| Termux: `CANNOT LINK EXECUTABLE` | Run `pkg upgrade -y` and install the package again |
| Changes in `.env` ignored | Save the file. Port/host/password need a restart |

## Privacy and safety

- Chats, memory and agents live in `memory.db` on your device. Delete the file to erase everything.
- Your messages and files are sent to Groq to get answers. Read Groq's terms for how they treat data.
- The API key stays in `.env`, which is excluded from Git by `.gitignore`. **Never commit or share `.env`.**
- Web links you paste are fetched by your own computer. Private and local addresses are blocked so nobody can use the app to reach your home network.
- Agents are AI. They can be wrong. Health, money and legal answers are information only, not professional advice.

## Project layout

```
app.py                 the web server and API
core.py                model calls, routing, memory, pipelines
agents.py              the agents and their instructions
db.py                  SQLite storage, undo and auto-cleanup
media.py               audio, video, image and PDF handling (ffmpeg)
logo.svg               your logo (replace this file)
static/                the website (HTML, CSS, JavaScript)
.env.example           settings template (copy to .env)
requirements.txt       Python packages
requirements-optional.txt  optional ffmpeg fallback
install.sh / install.bat   one-command setup
start.sh / start.bat       start the app
```

## Change the logo

Replace `logo.svg` in the project folder with your own SVG. It is used in the sidebar, the welcome screen, the browser tab and the home-screen icon, and it resizes automatically. For best results the SVG should have a `viewBox` attribute. Use `APP_NAME=` (empty) in `.env` if your logo already contains the name.

## Contributing

Issues and pull requests are welcome. Keep it simple: one small change per pull request, and test it on a phone-sized screen.
The `main` branch is protected: every change goes through a pull request that the maintainer reviews and approves. To add an agent, add an entry to `agents.py` and a `LEVEL_` line to `.env.example`.

## License

MIT. See [LICENSE](LICENSE).

## Credits

Created by **Ayush Giri**, founder of [Let's Code India](https://github.com/Let-s-Code-India).
