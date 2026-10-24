# Veda AI

<p align="center">
  <img src="logo.svg" alt="Veda AI logo" width="120">
</p>

Veda AI is a self-hosted, local-first AI workspace. Run it as a Python web application on your own computer or server, then use a browser to chat with a team of specialist AI agents, work with documents and media, and keep chat history and skill memory in a local SQLite database.

The browser interface is responsive and can be installed as a Progressive Web App (PWA) on supported mobile browsers. Veda AI is **not** a native iOS, Android, Windows, or macOS application. Model requests are sent to Groq; the web application and its local database run on the machine where you start the server.

## Contents

- [Highlights](#highlights)
- [How it works](#how-it-works)
- [Built-in agents](#built-in-agents)
- [Requirements](#requirements)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [Using Veda AI](#using-veda-ai)
- [Supported platforms](#supported-platforms)
- [Privacy and security](#privacy-and-security)
- [Troubleshooting](#troubleshooting)
- [Development and project layout](#development-and-project-layout)
- [Contributing](#contributing)
- [License](#license)

## Highlights

- **A team of specialist agents:** ask Veda AI to route a prompt or choose an agent for coding, research, writing, tutoring, and more.
- **Configurable models:** use Groq-hosted models with a single API key, and override model IDs or agent depth in `.env`.
- **Documents and media:** work with text and code files, extract selectable text from PDFs, ask questions about images, and transcribe supported audio or video.
- **Local persistence:** chat history, settings, custom agents, and skill memory are stored in SQLite on the server machine.
- **Custom agents:** create agents with your own role and instructions, then import or export their definitions.
- **Mobile-friendly access:** use the responsive browser UI, install it as a PWA where supported, or access it from another device on your LAN.
- **Portable setup:** shell scripts support Linux, macOS, and Termux; Windows batch scripts are included.

## How it works

Veda AI is a local web application with a hosted model provider:

1. Start the Python service on your computer or server.
2. Open the service in a browser and send a prompt, optionally with supported files.
3. Veda AI selects or uses the relevant specialist agent and calls the configured Groq model.
4. Chat history and app data are saved to the configured local SQLite database.

The server and database stay on the host running Veda AI, but prompts, attached content needed for inference, and transcription requests are sent to Groq. This is not offline inference. Review Groq's current policies and the sensitivity of your data before submitting private content.

### Technical stack

| Component | Implementation |
|---|---|---|
| Backend | Python, Flask, Waitress dependency |
| Model provider | Groq API, using chat completions and audio transcription endpoints |
| Data storage | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Optional media conversion | ffmpeg or the optional `imageio-ffmpeg` package |
| PDF text extraction | `pypdf` |

## Built-in agents

Veda AI includes focused agents that can use different model-depth levels. Agent model assignments can be changed in `.env`.

| Agent | Focus |
|---|---|
| Vishwakarma | Software development, code, debugging, scripts, and APIs |
| Saraswati | Stories, screenplays, characters, and creative writing |
| Valmiki | Poetry, shayari, lyrics, and captions |
| Chanakya | Strategy, decisions, explanations, and general questions |
| Aryabhata | Mathematics and science |
| Dronacharya | Tutoring, study help, and exam preparation |
| Dhanvantari | Health and wellness information |
| Kubera | Business, money concepts, and careers |
| Vidura | Critique, review, and identifying gaps or risks |
| Panini | Translation, grammar, and language assistance |
| Narada | Links, web pages, and research based on provided page content |
| Sanjaya | Summaries of long text and files |
| Chitragupta | Notes, lists, tables, and data organization |
| Drishti | Image understanding |
| Shruti | Audio and video transcription workflows |

You can also add custom agents in the app. Agent responses are AI-generated and should be checked, especially for high-impact decisions.

## Quick start

### Requirements

- Python 3.10 or newer
- A Groq API key for model and transcription requests
- Git, if you are cloning the repository
- A current browser to use the interface
- Optional: ffmpeg for converting some less common or larger media formats

### 1) Install dependencies

On Linux, macOS, and Android Termux:

```bash
git clone https://github.com/Let-s-Code-India/Veda-AI.git
cd Veda-AI
bash install.sh
```

On Windows, use PowerShell or Command Prompt:

```powershell
git clone https://github.com/Let-s-Code-India/Veda-AI.git
cd Veda-AI
.\install.bat
```

The installer installs the Python requirements and creates `.env` from `.env.example` if it does not exist. On supported desktop Unix systems it also creates a `.venv` virtual environment. Termux uses its system Python environment.

### 2) Configure your API key

If the installer did not create `.env`, copy the example:

```bash
cp .env.example .env
```

Edit `.env` and set your key:

```dotenv
GROQ_API_KEY=gsk_your_key_here
```

Keep this key private. Do not commit or share `.env`.

### 3) Start Veda AI

On Linux, macOS, and Termux:
```bash
bash start.sh
```

On Windows:

```powershell
start.bat
```

Open the local address:

- `http://127.0.0.1:5000` or `http://localhost:5000` on the same device.
- `http://<your-local-ip>:5000` from another device on your LAN after enabling LAN access as described below.

You can also start the server directly with `python app.py` (or `python3 app.py` on systems where that is the Python 3 command).

## Configuration

Veda AI reads settings from `.env` in the project directory. The sample file documents the supported values:

| Variable | Purpose | Example / default |
|---|---|---|
| `GROQ_API_KEY` | Groq credential; required for model requests | Set your own key |
| `HOST` | Interface to bind the web server to | `127.0.0.1` |
| `PORT` | Port used by the web server | `5000` |
| `APP_PASSWORD` | Optional HTTP Basic password, useful for LAN access | Empty (disabled) |
| `APP_NAME` | Name shown in the interface | `Veda AI` |
| `APP_TAGLINE` | Secondary app label | `Your team of minds` |
| `MODEL_SUTRA` | Fast-level model ID | `openai/gpt-oss-20b` |
| `MODEL_SHLOKA` | Balanced-level model ID | `qwen/qwen3.8-27b` |
| `MODEL_VEDA` | Deep-level model ID | `openai/gpt-oss-120b` |
| `MODEL_SARATHI` | Routing model ID | `openai/gpt-oss-20b` |
| `MODEL_DRISHTI` | Image model ID | `qwen/qwen3.8-27b` |
| `MODEL_SHRUTI` | Transcription model ID | `whisper-large-v3-turbo` |
| `LEVEL_<AGENT>` | Model depth for a built-in agent (`sutra`, `shloka`, or `veda`) | See `.env.example` |
| `DB_PATH` | SQLite database path | `memory.db` |

The model IDs above are example defaults and may change or become unavailable. Check the current Groq model catalog if an ID is rejected, then update the corresponding variable. The application loads environment settings dynamically for model/agent configuration, though restarting after configuration changes is a reliable way to apply them consistently.

### Enable access from other devices

By default, the server binds to `127.0.0.1`, so it is available only on the host machine. To allow devices on the same trusted local network to connect, set:

```dotenv
HOST=0.0.0.0
PORT=5000
APP_PASSWORD=use-a-long-unique-password
```

Restart Veda AI, find the host's LAN IP address, and open `http://<your-local-ip>:5000` on the other device. Use a strong password and firewall rules appropriate for your network. Do not expose this development server directly to the public internet.

## Using Veda AI

### Chat and agent selection

Start a conversation in the browser and select a specialist agent or use the router to direct your request. Agents have model levels for fast, balanced, and deep responses. The selected model and agent can be adjusted through the app and `.env` configuration.

### Files, documents, and media

Veda AI supports file workflows for images, PDFs, audio, video, and text/code files. Processing depends on file type and configured model:

- **PDFs:** selectable text is extracted with `pypdf`; scanned pages without a text layer need to be provided as images. Extraction is bounded and does not perform OCR.
- **Images:** sent to the image-capable model; larger images may be resized when ffmpeg is available.
- **Audio and video:** audio is sent to the configured transcription model. Video workflows extract audio; the transcript agent does not analyze the video's visuals.
- **Text and code:** attach content for summarization, explanation, review, or other supported chat tasks.

The service enforces a 100 MB request limit, and model/provider limits may be lower. Files processed for model responses are transmitted to Groq.

### Memory, history, and exports

Chat history and app settings are stored in the SQLite database. Skill memory is shared across agents and is separate from an individual chat summary. The interface provides chat and app export, as well as custom-agent import/export. Back up the database and exports yourself if you need to preserve them.

Automatic chat cleanup is enabled by default. The cleanup interval and enablement can be changed in the app's settings. Pinned chats are excluded from automatic cleanup; deleted items have a short undo window before permanent deletion.

## Supported platforms

Veda AI is a Python web service rather than a native app. Use a browser on the server itself, or connect over a trusted LAN.

| Platform | Recommended use | Notes |
|---|---|---|
| Linux | Local browser or self-hosted machine | Shell setup and launcher included |
| macOS | Local browser on a workstation | Shell setup and launcher included |
| Windows | Local browser on a workstation | Batch setup and launcher included |
| Android | Chrome PWA or Termux | Browser PWA or local Python service |
| iPhone / iPad | Safari PWA or iSH shell | Add to Home Screen; not a native app |

### Install the web app on mobile

1. Start Veda AI on the computer or phone that will host the service.
2. Open its address in Safari on iPhone/iPad or Chrome on Android.
3. Use the browser's **Add to Home Screen** or **Install app** action when available.
4. Launch the saved shortcut. The server must remain running on the host.

### Android Termux installation

```bash
pkg update -y && pkg upgrade -y
pkg install -y python git
git clone https://github.com/Let-s-Code-India/Veda-AI.git
cd Veda-AI
bash install.sh
bash start.sh
```

Before starting, edit `.env` and provide `GROQ_API_KEY`. Open the local address in the Android browser.

### iOS with iSH shell

If you want to run the Python service inside the iOS iSH shell app, install the available packages and clone the repository:

```bash
apk update
apk add --no-cache git python3 py3-pip
git clone https://github.com/Let-s-Code-India/Veda-AI.git
cd Veda-AI
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your Groq key, then start the app:

```bash
nano .env
python3 app.py
```

Open `http://127.0.0.1:5000` from the iSH environment to check that the service responds. Browser access to iSH loopback can vary; LAN access may work better when the server is bound to `HOST=0.0.0.0`. Be aware that iSH has its own resource and compatibility limitations.

### Windows setup

```powershell
git clone https://github.com/Let-s-Code-India/Veda-AI.git
cd Veda-AI
.\install.bat
```

Edit `.env` with a text editor, add your Groq key, and run `start.bat`.

## Privacy and security

- The SQLite database is stored on the machine running the app (by default, `memory.db` alongside the project).
- Model prompts, relevant uploaded content, and audio transcription requests are sent to Groq for processing. Local hosting does not mean offline or provider-free inference.
- Keep `.env` private; it contains your API key and may contain your LAN password. Do not commit it or include it in public backups.
- The app blocks unsafe private/local destinations when it fetches URL-based content, but this does not replace careful network configuration.
- `APP_PASSWORD` is optional and disabled when empty. Set it before enabling LAN access.
- Restrict LAN use to trusted networks. The included server setup is intended for personal/local use, not direct public production deployment.
- AI responses can be incorrect. Do not treat them as medical, legal, or financial advice.

## Troubleshooting

### App will not start

- Confirm Python 3.10 or newer is installed and install dependencies with `bash install.sh` or `.\install.bat`.
- Make sure `.env` exists. For model requests, make sure `GROQ_API_KEY` contains a valid key.
- Check whether another process is using the configured port, then change `PORT` if needed.
- On Unix, try `bash start.sh`; if you installed dependencies in a virtual environment manually, activate it first.

### Browser cannot connect

- Confirm the app process is still running and use the correct `PORT`.
- For same-device access, use `http://127.0.0.1:<port>`.
- For another device, set `HOST=0.0.0.0`, use the server's LAN IP, and check that both devices share a network and the firewall allows the port.
- A PWA shortcut does not host the backend; the server machine still needs to be running.

### Model errors

If Groq reports that a model does not exist or is unavailable:

1. Check the current model IDs available to your Groq account.
2. Set the relevant `MODEL_*` value in `.env` to a supported ID.
3. Retry. Rate limits and provider availability can also affect requests.

For authentication errors, confirm that `GROQ_API_KEY` is correct and has not been revoked.

### Voice fails on mobile devices

Browser microphone access generally requires a secure context (HTTPS or localhost) and explicit permission. Browser behavior on a LAN address or mobile device can vary. If microphone capture is unavailable, try uploading a supported audio file.

### PDF has no extracted text

Scanned/image-only PDFs do not contain selectable text for `pypdf` to extract. Provide the relevant pages as images instead; OCR is not built into this PDF extraction path.

### ffmpeg warnings

ffmpeg is optional. Install it if you need conversion for unusual audio/video formats or resizing for large images:

- Termux: `pkg install ffmpeg`
- macOS: `brew install ffmpeg` (Homebrew)
- Debian/Ubuntu Linux: `sudo apt install ffmpeg`
- Windows: `winget install ffmpeg`

The installer may offer the optional `imageio-ffmpeg` Python package as an alternative on supported desktop environments.

## Development and project layout

```text
app.py                    Flask application, API routes, and server startup
core.py                   Model calls, routing, memory, and platform logic
agents.py                 Built-in agent definitions and instructions
db.py                     SQLite schema, history, and cleanup
media.py                  PDF, image, audio, and video preparation
static/                   Browser UI assets
tests/                    Automated tests
.env.example              Documented sample configuration
requirements.txt          Runtime Python dependencies
requirements-optional.txt  Optional media conversion dependency
install.sh / install.bat  Setup scripts
start.sh / start.bat      Launch scripts
logo.svg                  App logo and PWA icon
```

### Run tests

Run the test suite from the repository root:

```bash
python -m pytest
```

## Contributing

Issues and pull requests are welcome. Keep changes focused, test the behavior you change, and check the responsive interface at phone-sized widths. The `main` branch is protected: submit changes through a pull request for maintainer review rather than pushing directly to `main`.

To add a built-in agent, define it in `agents.py` and document its `LEVEL_` setting in `.env.example`. Keep API keys and other secrets out of commits.

## Logo customization

Replace `logo.svg` with your own SVG to update the in-app and PWA logo. A `viewBox` helps it scale cleanly. If the logo includes the product name, set `APP_NAME=` in `.env` to hide the separate name label.

## License

This project is licensed under the [MIT License](LICENSE).

## Credits

Created by **Ayush Giri**, founder of [Let's Code India](https://github.com/Let-s-Code-India).
