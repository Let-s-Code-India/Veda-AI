<p align="center"><img src="logo.svg" alt="Veda AI logo" height="90"></p>

<h1 align="center">Veda AI</h1>

<p align="center"><b>आपके अपने device पर चलने वाली AI agents की अपनी टीम।</b><br>
बस एक मुफ़्त Groq API key चाहिए। न account, न cloud server, न model चुनने की झंझट।<br>
Android (Termux), Windows, macOS और Linux पर चलता है।</p>

<p align="center"><a href="README.md">Read in English</a></p>

---

## यह क्या है?

Veda AI एक छोटा chatbot वेबसाइट है जो **आपके अपने फ़ोन या कंप्यूटर पर** चलता है (`http://localhost:5000` पर)।
आप संदेश लिखते हैं, या image, video, audio, PDF जोड़ते हैं, या कोई link डालते हैं।
**Sarathi** नाम का router उसे पढ़कर सही **agent** चुनता है और सही Groq model को भेजता है।
Model आपको चुनना नहीं पड़ता। आपको बस एक बार अपनी API key डालनी है।

आपकी chats और memory आपके अपने device की एक file में रहती हैं। जवाब लेने के लिए सिर्फ़ Groq को संदेश जाता है, और कहीं नहीं।

## खूबियाँ

- **15 विशेषज्ञ agents:** coding, कहानी, कविता, maths, पढ़ाई, health की जानकारी, पैसा, समीक्षा, अनुवाद, research, सारांश, notes, image और audio।
- **अपने आप चुनाव (Sarathi)।** या आप खुद agent चुन सकते हैं।
- **सब कुछ समझता है:** image, audio, video, PDF, text और code files, और web links।
- **Deep mode:** दो models अलग-अलग जवाब बनाते हैं, फिर एक सबसे अच्छा जवाब तैयार करता है।
- **दो तरह की memory**
  - *Skill memory:* हर agent आपके बारे में क्या जानता है (भाषा, लक्ष्य, projects)। सब agents में साझा रहती है और chat मिटाने पर भी बनी रहती है। आप इसे जोड़, बदल, मिटा, export और import कर सकते हैं।
  - *Chat memory:* हर chat का चलता हुआ सारांश, ताकि agent वहीं से आगे बढ़े जहाँ आपने छोड़ा था। chat के साथ यह भी मिट जाती है।
- **बोलकर पूछना:** mic दबाकर बोलें, Whisper उसे लिख देगा।
- **सुरक्षित delete:** chat या memory मिटाने पर 10 सेकंड का **Undo** दिखता है।
- **Auto-cleanup (वैकल्पिक):** पुरानी chats पर लाल निशान आता है, छोटी चेतावनी मिलती है, फिर storage बचाने के लिए हट जाती हैं। Pin की हुई chat हमेशा बनी रहती है।
- **अपने agents:** अपने निर्देशों से agent बनाएँ, JSON में export करके दूसरों से बाँटें।
- **Light और Dark theme**, phone के हिसाब से बना layout, chat का Markdown export, पूरा backup JSON में।
- **आपका logo:** project folder में `logo.svg` रख दें, वही हर जगह दिखेगा।

## Agents

| Agent | काम |
|---|---|
| Sarathi | Router, आपके लिए agent चुनता है |
| Vishwakarma | Coding और terminal की मदद |
| Saraswati | कहानी, scripts, fight scenes |
| Valmiki | कविता, shayari, lyrics |
| Chanakya | रणनीति, तर्क, आम सवाल |
| Aryabhata | Maths और science |
| Dronacharya | पढ़ाई और exam की तैयारी |
| Dhanvantari | Health की जानकारी (डॉक्टर नहीं) |
| Kubera | पैसा, business, career |
| Vidura | ईमानदार समीक्षक |
| Panini | अनुवाद, grammar, लेखन |
| Narada | Links और web pages पढ़ता है |
| Sanjaya | लंबे text और files का सारांश |
| Chitragupta | Notes, tables, lists, data |
| Drishti | Image समझता है |
| Shruti | Audio और video समझता है |

Models के तीन स्तर हैं: **Sutra** (तेज़), **Shloka** (संतुलित) और **Veda** (गहरा)। हर स्तर पर कौन सा Groq model लगे, यह `.env` में तय होता है।

---

## शुरू करने से पहले (2 मिनट)

1. **मुफ़्त Groq API key** लें: <https://console.groq.com/keys> खोलें, login करें, **Create API Key** दबाएँ और key copy करें। वह `gsk_` से शुरू होती है।
2. यह key निजी रखें। इसे कभी online न डालें।

---

## Install करना

अपना device चुनें। हर रास्ते का अंत browser में `http://localhost:5000` खोलने पर होता है।

### Android (Termux)

1. **F-Droid से Termux** install करें (<https://f-droid.org/packages/com.termux/>)। Play Store वाला पुराना है।
2. Termux खोलकर ये एक-एक करके चलाएँ:

```bash
pkg update -y && pkg upgrade -y
pkg install -y python git
git clone https://github.com/YOUR-ORG/YOUR-REPO.git
cd YOUR-REPO
bash install.sh
```

3. Settings file खोलकर अपनी key डालें:

```bash
nano .env
```

`GROQ_API_KEY=` के बाद अपनी key लिखें। Save करने के लिए **Ctrl + O**, फिर **Enter**, और बाहर आने के लिए **Ctrl + X**।
(Termux में Ctrl की जगह keyboard के ऊपर वाली extra keys की पंक्ति इस्तेमाल करें।)

4. चलाएँ:

```bash
./start.sh
```

5. **Chrome** खोलकर `http://localhost:5000` पर जाएँ।

Termux के लिए सुझाव:
- रोकने के लिए **Ctrl + C**। बाद में दोबारा चलाने के लिए: `cd YOUR-REPO && ./start.sh`
- Termux की notification नीचे खींचकर **Acquire wakelock** दबा दें, ताकि Android इसे background में बंद न करे।
- अगर `pkg install ffmpeg` पर `CANNOT LINK EXECUTABLE` error आए, तो `pkg upgrade -y` चलाकर फिर से install करें।

### Windows

1. <https://www.python.org/downloads/> से **Python 3.10 या नया** install करें। पहली screen पर **"Add Python to PATH" पर टिक** ज़रूर लगाएँ।
2. <https://git-scm.com/download/win> से **Git** install करें (या GitHub से project को ZIP में download करके unzip कर लें)।
3. **PowerShell** खोलकर चलाएँ:

```powershell
git clone https://github.com/YOUR-ORG/YOUR-REPO.git
cd YOUR-REPO
.\install.bat
```

4. Notepad में settings file खोलें और `GROQ_API_KEY=` के बाद अपनी key डालें:

```powershell
notepad .env
```

5. **start.bat** पर double-click करें (या `py app.py` चलाएँ)।
6. Browser में `http://localhost:5000` खोलें।

### Linux और macOS

```bash
git clone https://github.com/YOUR-ORG/YOUR-REPO.git
cd YOUR-REPO
bash install.sh
nano .env          # GROQ_API_KEY= के बाद अपनी key डालें
./start.sh
```

फिर `http://localhost:5000` खोलें।

### हाथ से install (किसी भी system पर)

```bash
python3 -m venv .venv                 # वैकल्पिक पर अच्छा
source .venv/bin/activate             # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                  # Windows: copy .env.example .env
# .env खोलकर अपनी key डालें
python app.py
```

---

## इस्तेमाल कैसे करें

1. **बस लिखिए।** Sarathi agent चुनता है। हर जवाब के ऊपर का badge बताता है कि कौन सा agent और model चला।
2. **खुद agent चुनें:** title के नीचे की chips से।
3. **Files जोड़ें:** **+** बटन से image, audio, video, PDF, text और code। संदेश में link हो तो वह अपने आप पढ़ा जाता है।
4. **बोलें:** mic बटन से। आपके शब्द text box में आएँगे, भेजने से पहले सुधार सकते हैं।
5. **Deep mode** (text box के ऊपर का बटन) धीमा है और free quota ज़्यादा खाता है, पर कठिन सवालों पर सबसे अच्छा जवाब देता है।
6. **Memory** (sidebar): agents आपके बारे में क्या जानते हैं, उसे जोड़ें, बदलें या मिटाएँ। दूसरे device पर ले जाने के लिए export करें।
7. **Agents** (sidebar): अपना agent बनाएँ, export करें, या किसी दोस्त का बाँटा हुआ import करें।
8. **Settings** (sidebar): auto-cleanup, पूरा backup, और key व वैकल्पिक tools की स्थिति।
9. ऊपर के बटन: chat को **pin** करें, Markdown में **export** करें, **light / dark** बदलें।

### ffmpeg के बारे में (वैकल्पिक)

ffmpeg एक छोटा मुफ़्त tool है जो files को बदलता है। Veda AI इसे **सिर्फ़ ज़रूरत पड़ने पर** इस्तेमाल करता है: `.aac` जैसी audio, `.mkv` या `.mov` जैसी video, और बहुत बड़ी photos के लिए। आम formats (mp3, wav, m4a, mp4, webm) इसके बिना चलते हैं। किसी file को इसकी ज़रूरत हो और यह न मिले, तो app खुद बताता है कि कैसे install करें। `install.sh` और `install.bat` इसे आपके लिए install करने की कोशिश भी करते हैं।

| System | Command |
|---|---|
| Termux | `pkg install ffmpeg` |
| Windows | `winget install ffmpeg` |
| macOS | `brew install ffmpeg` |
| Linux | `sudo apt install ffmpeg` |
| कोई भी (विकल्प) | `pip install imageio-ffmpeg` |

---

## Settings की सूची (`.env`)

| Setting | मतलब | Default |
|---|---|---|
| `GROQ_API_KEY` | आपकी Groq key। **ज़रूरी** | खाली |
| `PORT` | वेबसाइट का port नंबर | `5000` |
| `HOST` | `127.0.0.1` = सिर्फ़ यही device। `0.0.0.0` = आपके network के बाकी devices भी | `127.0.0.1` |
| `APP_PASSWORD` | वैकल्पिक password (username कुछ भी)। `HOST=0.0.0.0` हो तो ज़रूर रखें | खाली |
| `APP_NAME`, `APP_TAGLINE` | Logo के पास दिखने वाला text। नाम खाली छोड़ने पर छिप जाता है | `Veda AI` |
| `MODEL_SUTRA / SHLOKA / VEDA` | तीन स्तरों के models | `.env.example` देखें |
| `MODEL_SARATHI` | संदेश चुनने वाला model | `openai/gpt-oss-20b` |
| `MODEL_DRISHTI` | Image समझने वाला model (vision वाला होना चाहिए) | `qwen/qwen3.8-27b` |
| `MODEL_SHRUTI` | Audio, video और mic के लिए speech model | `whisper-large-v3-turbo` |
| `LEVEL_<AGENT>` | हर agent का स्तर: `sutra`, `shloka` या `veda` | `.env.example` देखें |
| `DB_PATH` | Database file का नाम | `memory.db` |

`.env` कभी भी बदल सकते हैं। Model और level का बदलाव अगले संदेश पर लग जाता है, restart नहीं चाहिए। `PORT`, `HOST` या password बदलने पर restart करें।

**Groq समय-समय पर models के नाम बदलता है।** अगर *"model does not exist"* जैसा error दिखे, तो Groq playground की model list से मौजूदा नाम copy करके `.env` में डाल दें।

## दूसरे device से खोलना (वही Wi-Fi या hotspot)

1. `.env` में `HOST=0.0.0.0` और password रखें: `APP_PASSWORD=कुछ-भी-चुनें`।
2. App दोबारा चलाएँ। वह `http://192.168.1.5:5000` जैसा पता छापेगा।
3. दूसरे device पर वही पता खोलें।

ध्यान दें: जो भी इसे खोलेगा वह **आपकी** Groq key इस्तेमाल करेगा, इसलिए password ज़रूर रखें। Mic सिर्फ़ `localhost` या `https` पर चलता है, इसलिए दूसरे device पर टाइपिंग, files और images चलेंगे पर browser voice रोक सकता है।

## Update करना

```bash
git pull
```

आपकी `.env` और `memory.db` कभी नहीं छुई जातीं, क्योंकि वे repository का हिस्सा नहीं हैं। `.env.example` में नई settings आएँ तो उन्हें अपनी `.env` में जोड़ लें।

## दिक्कत आए तो

| समस्या | क्या करें |
|---|---|
| Browser में खाली पन्ना या "refused to connect" | App चालू नहीं है। दोबारा चलाएँ और terminal खुला रखें |
| `Address already in use` / port busy | पुरानी copy चल रही है। Termux/Linux/macOS: `pkill -f app.py`। Windows: पुरानी window बंद करें। या `.env` में `PORT` बदलें |
| "No API key found" या "rejected your API key" | `.env` में `GROQ_API_KEY` देखें: बीच में space नहीं, पूरी `gsk_...` key |
| "model does not exist" | `.env` में मौजूदा model का नाम डालें (ऊपर देखें) |
| "Rate limit reached" | Free quota पूरी हुई। एक मिनट रुकें। Deep mode में एक संदेश पर 3 calls लगती हैं |
| Image वाला जवाब fail | देखें कि `MODEL_DRISHTI` ऐसा model है जो image input समझता हो |
| Audio या video fail | ffmpeg install करें (ऊपर की table)। 100 MB से बड़ी files स्वीकार नहीं होतीं |
| Mic बटन कहता है microphone unavailable | App को `http://localhost:5000` पर खोलें और Chrome में microphone की अनुमति दें |
| Termux: `CANNOT LINK EXECUTABLE` | `pkg upgrade -y` चलाकर package दोबारा install करें |
| `.env` का बदलाव नहीं दिख रहा | File save करें। Port, host और password के लिए restart चाहिए |

## निजता और सुरक्षा

- Chats, memory और agents आपके device की `memory.db` में रहते हैं। सब कुछ मिटाना हो तो वह file हटा दें।
- जवाब पाने के लिए आपके संदेश और files Groq को भेजे जाते हैं। वे डेटा के साथ क्या करते हैं, यह Groq की शर्तों में देखें।
- API key `.env` में रहती है, जिसे `.gitignore` Git से बाहर रखता है। **`.env` को कभी commit या share न करें।**
- आप जो web links डालते हैं, उन्हें आपका अपना कंप्यूटर खोलता है। निजी और local पते बंद हैं, ताकि कोई इस app से आपके घर के network तक न पहुँच सके।
- Agents AI हैं और गलत हो सकते हैं। Health, पैसे और कानून के जवाब सिर्फ़ जानकारी हैं, पेशेवर सलाह नहीं।

## Project की बनावट

```
app.py                 वेब server और API
core.py                model calls, routing, memory, pipelines
agents.py              agents और उनके निर्देश
db.py                  SQLite, undo और auto-cleanup
media.py               audio, video, image और PDF (ffmpeg)
logo.svg               आपका logo (इसे बदल दें)
static/                वेबसाइट (HTML, CSS, JavaScript)
.env.example           settings का template (.env में copy करें)
requirements.txt       Python packages
requirements-optional.txt  वैकल्पिक ffmpeg विकल्प
install.sh / install.bat   एक command में setup
start.sh / start.bat       app चलाना
```

## Logo बदलना

Project folder में `logo.svg` को अपने SVG से बदल दें। वह sidebar, welcome screen, browser tab और home-screen icon में दिखेगा और अपने आप छोटा-बड़ा होगा। सबसे अच्छे नतीजे के लिए SVG में `viewBox` होना चाहिए। अगर आपके logo में नाम पहले से है, तो `.env` में `APP_NAME=` खाली छोड़ दें।

## योगदान

Issues और pull requests का स्वागत है। एक pull request में एक छोटा बदलाव रखें और phone जितनी छोटी screen पर परखें। Agent जोड़ने के लिए `agents.py` में एक entry और `.env.example` में एक `LEVEL_` line जोड़ें।

## License

MIT। देखें [LICENSE](LICENSE)।
