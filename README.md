# Veda AI

Veda AI is a self-hosted local AI workspace: a web application that runs on your own machine and lets you chat with a set of specialist agents, attach documents and media, and keep memory on-device.

This project is designed as a local-first, browser-based experience with mobile install support. It is not a native app binary for iPhone, iPad, Android, Windows, or macOS. Instead, it runs as a local Python service with a responsive web UI that can be installed as a PWA on mobile devices and used as a desktop app on laptops and workstations.

## What this project does

- Routes each prompt to the most relevant specialist agent
- Supports file uploads including images, PDFs, audio, video, and text/code files
- Supports Groq-backed model calls with a single API key in `.env`
- Stores conversations and skill memory in a local SQLite database
- Runs on desktop and mobile browsers through a responsive web interface
- Can be exposed to devices on the same LAN with `HOST=0.0.0.0`
- Works well as a local AI workspace for day-to-day use, prototyping, and private document analysis

## Architecture

The project is intentionally simple and privacy-focused:

- `app.py` hosts the Flask API and web app
- `core.py` contains model routing, memory, and platform-aware logic
- `agents.py` defines the built-in specialist agents and routing prompt behavior
- `db.py` stores chat history, skill memory, custom agents, and settings in SQLite
- `media.py` handles PDFs, media conversion, and file preparation
- `static/` contains the HTML, CSS, and JavaScript frontend

The result is a secure local-first architecture: the app stays on your device, your SQLite data stays on your device, and only the model requests leave your device to Groq.

## Platform support matrix

| Platform | Recommended path | Notes |
|---|---|---|
| iPhone / iPad | Safari -> Add to Home Screen | Works as a PWA, not a native binary |
| iOS via iSH shell | Install iSH, then run the app inside the Linux environment | Good for users who want a Linux shell and local Python runtime on iOS |
| Android | Chrome -> Install app / use Termux | Works as a PWA or a local Termux install |
| Windows | Local Python app or run the `.bat` scripts | Best for desktop use |
| macOS | Local Python app or run the shell scripts | Best for local workstation use |
| Linux | Local Python app or run the shell scripts | Great for headless or local server deployments |

Important: the app is a local web app with mobile installability. If you want a native iOS/Android app store app, that requires a separate wrapper project such as Capacitor, React Native, or a custom shell for each platform.

### iOS with iSH shell

If you want to run this app inside iOS using the iSH shell app:

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

Then edit `.env` and add your Groq key:

```bash
nano .env
```

Start the app:

```bash
python3 app.py
```

Open the service from inside the iSH environment with:

```bash
curl http://127.0.0.1:5000
```

or access the server from the same local network if the container is bound to `HOST=0.0.0.0`. Safari on iOS may not reach the iSH loopback the same way a desktop browser would, so the most reliable iSH workflow is usually to use the local shell for setup and local testing while keeping the server bound to a LAN address when needed.

### Android (Termux)

```bash
pkg update -y && pkg upgrade -y
pkg install -y python git
git clone https://github.com/Let-s-Code-India/Veda-AI.git
cd Veda-AI
bash install.sh
```

Then set your API key and run:

```bash
bash start.sh
```

## Quick start

### 1) Install dependencies

```bash
git clone https://github.com/Let-s-Code-India/Veda-AI.git
cd Veda-AI
bash install.sh
```

On Windows:

```powershell
git clone https://github.com/Let-s-Code-India/Veda-AI.git
cd Veda-AI
.\install.bat
```

### 2) Add your API key

Copy `.env.example` to `.env` and add your Groq API key:

```bash
cp .env.example .env
```

Then edit `.env` and set:

```dotenv
GROQ_API_KEY=gsk_your_key_here
```

### 3) Start the app

```bash
bash start.sh
```

or on Windows:

```powershell
start.bat
```

Open:

- `http://localhost:5000` on the same device
- `http://<your-local-ip>:5000` from other devices on your LAN when `HOST=0.0.0.0`

## Mobile install and cross-device use

### iPhone and iPad

1. Start the app on the machine it is running on.
2. Open the app in Safari on the iPhone or iPad.
3. Tap the Share button.
4. Choose Add to Home Screen.
5. Launch it from the home screen.

This gives you an app-like experience, but the backend still runs on your local machine or LAN.

### Android

1. Run the app on your local machine or Termux environment.
2. Open the app in Chrome.
3. Use the browser menu to Install app or Add to Home Screen.
4. Launch the icon like a normal app.

### Desktop use

Use the browser directly or install a lightweight wrapper like a local browser shortcut or desktop launcher. The app already exposes a responsive interface and works well on desktop browsers without any extra platform code.

### LAN / network access

For other devices on the same network:

```dotenv
HOST=0.0.0.0
APP_PASSWORD=choose-a-strong-password
```

Then restart the app and open the displayed LAN IP, such as:

```text
http://192.168.1.15:5000
```

This is useful for tablets, phones, or laptops on the same network.

## Environment and settings

The primary runtime settings live in `.env`:

| Setting | Purpose |
|---|---|
| `GROQ_API_KEY` | Required Groq API key |
| `PORT` | The port used by the app |
| `HOST` | Local-only or LAN-accessible binding |
| `APP_PASSWORD` | Optional basic auth for networked access |
| `APP_NAME` | Branding shown in the UI |
| `APP_TAGLINE` | Secondary brand text |
| `MODEL_*` | Override Groq model names |
| `LEVEL_*` | Agent depth selection |
| `DB_PATH` | Database file location |

A full example is in `.env.example`.

## Features

- Specialist agent routing with Sarathi
- Model-level routing and deep-answer modes
- Chat export and full app export
- Skill memory that persists across chats
- Custom agent creation and import/export
- Voice transcription support for local microphone input
- Local SQLite chat history and settings
- Multi-device LAN access with an optional password
- Light and dark themes

## Operating system notes

### Android (Termux)

```bash
pkg update -y && pkg upgrade -y
pkg install -y python git
git clone https://github.com/Let-s-Code-India/Veda-AI.git
cd Veda-AI
bash install.sh
```

Then edit `.env`, start the app, and visit the local address in Chrome.

### Windows

1. Install Python 3.10+
2. Install Git
3. Run:

```powershell
git clone https://github.com/Let-s-Code-India/Veda-AI.git
cd Veda-AI
.\install.bat
```

### macOS and Linux

```bash
git clone https://github.com/Let-s-Code-India/Veda-AI.git
cd Veda-AI
bash install.sh
nano .env
bash start.sh
```

## Troubleshooting

### App will not start

- Ensure Python dependencies are installed
- Confirm `.env` exists and contains a valid `GROQ_API_KEY`
- Check whether the port is already in use

### Browser cannot connect

- Confirm the app is still running
- Check `HOST` and `PORT` values in `.env`
- If using LAN access, ensure the device is on the same network and the firewall allows the port

### Model errors

Groq frequently renames models. If you see a model mismatch error:

1. Open the Groq model list in the dashboard
2. Copy the current model identifier
3. Update `.env` and restart if needed

### Voice fails on mobile devices

The browser microphone requires a secure origin or localhost. This means local native use or LAN-based access may behave differently depending on the browser. Tapping the mic on a browser page can require permission and may not work on all mobile browsers.

### ffmpeg warnings

ffmpeg is optional but useful for unusual media formats. Install it as needed:

- Termux: `pkg install ffmpeg`
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`
- Windows: `winget install ffmpeg`

## Privacy and safety

- Your chat history and skill memory live in a local SQLite file on your device
- Your `.env` file contains your API key and should never be committed or shared
- The app intentionally blocks unsafe local/private network addresses when reading URL-based content
- Always use `APP_PASSWORD` when exposing the app on a LAN or hotspot
- Treat AI output as assistive information, not legal, medical, or financial advice

## Project layout

```text
app.py                  Flask app and HTTP routes
core.py                 AI logic, memory orchestration, routing, platform detection
agents.py               Agent definitions and system prompt logic
db.py                   SQLite storage and cleanup logic
media.py                Media preparation and PDF handling
static/                 Frontend assets (HTML, CSS, JS)
.env.example            Sample environment file
requirements.txt        Runtime dependencies
requirements-optional.txt  Optional tooling
install.sh              Unix installer
install.bat             Windows installer
start.sh                Unix launcher
start.bat               Windows launcher
README.md               Project documentation
```

## Future hardening opportunities

This project is already usable as a local-first AI workspace. Production hardening opportunities include:

- custom TLS termination behind a reverse proxy
- stronger admin/user access controls for LAN deployments
- packaging as a native wrapper for iOS and Android using Capacitor or similar tooling
- background sync and local backups for multi-device setups
- structured logging and audit trails

## License

This project is available under the terms of the included license file.


## Change the logo

Replace `logo.svg` in the project folder with your own SVG. It is used in the sidebar, the welcome screen, the browser tab and the home-screen icon, and it resizes automatically. For best results the SVG should have a `viewBox` attribute. Use `APP_NAME=` (empty) in `.env` if your logo already contains the name.

## Contributing

Issues and pull requests are welcome. Keep it simple: one small change per pull request, and test it on a phone-sized screen.
The `main` branch is protected: every change goes through a pull request that the maintainer reviews and approves. To add an agent, add an entry to `agents.py` and a `LEVEL_` line to `.env.example`.

## License

MIT. See [LICENSE](LICENSE).

## Credits

Created by **Ayush Giri**, founder of [Let's Code India](https://github.com/Let-s-Code-India).
