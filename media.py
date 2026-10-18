"""File handling: audio, video, images and PDFs.

ffmpeg is optional. It is used only when a file needs converting or shrinking
(for example .aac audio, .mkv video, or a very large photo). If it is missing
and a file needs it, the user gets a clear message with install instructions.
"""
import io, os, shutil, subprocess, tempfile, base64, mimetypes

AUDIO_OK = {".flac", ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".ogg", ".opus", ".wav", ".webm"}
AUDIO_EXT = AUDIO_OK | {".aac", ".amr", ".wma", ".3gp", ".caf", ".aiff"}
VIDEO_EXT = {".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv", ".3gp", ".m4v", ".mpg"}
MAX_AUDIO = 24 * 1024 * 1024          # Groq transcription limit is 25 MB
IMG_SOFT = int(2.5 * 1024 * 1024)     # shrink photos above this size
IMG_HARD = int(3.0 * 1024 * 1024)     # Groq limit is 4 MB of base64

HELP = ("This file needs ffmpeg to convert it. Install ffmpeg: "
        "Termux: pkg install ffmpeg | Windows: winget install ffmpeg | "
        "Mac: brew install ffmpeg | Linux: sudo apt install ffmpeg. "
        "Or run: pip install imageio-ffmpeg")


class MediaError(Exception):
    pass


def ffmpeg_path():
    p = shutil.which("ffmpeg")
    if p:
        return p
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def _ffmpeg(args, data, in_ext, out_name):
    ff = ffmpeg_path()
    if not ff:
        raise MediaError(HELP)
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "in" + in_ext), os.path.join(d, out_name)
        with open(a, "wb") as fh:
            fh.write(data)
        try:
            subprocess.run([ff, "-y", "-i", a] + args + [b], capture_output=True, timeout=240, check=True)
        except subprocess.TimeoutExpired:
            raise MediaError("Converting took too long. Try a shorter file.")
        except subprocess.CalledProcessError:
            raise MediaError("Could not read this file. Is it a valid audio, video or image file?")
        except OSError:
            raise MediaError(HELP)
        with open(b, "rb") as fh:
            return fh.read()


def prepare_audio(data, filename, is_video=False):
    """Return (bytes, filename) that Groq Whisper accepts."""
    ext = os.path.splitext(filename or "")[1].lower()
    if ffmpeg_path() and (is_video or ext not in AUDIO_OK or len(data) > 12 * 1024 * 1024):
        out = _ffmpeg(["-vn", "-ac", "1", "-ar", "16000", "-b:a", "32k"], data, ext or ".bin", "out.mp3")
        return out, "audio.mp3"
    if ext in AUDIO_OK:
        if len(data) > MAX_AUDIO:
            raise MediaError("This file is larger than 24 MB. Install ffmpeg so it can be compressed, or trim it. " + HELP)
        return data, "audio" + ext
    raise MediaError(HELP)


def prepare_image(data, mime):
    """Return a data: URL, shrinking big photos when ffmpeg is available."""
    if len(data) > IMG_SOFT:
        if ffmpeg_path():
            ext = mimetypes.guess_extension(mime) or ".jpg"
            data = _ffmpeg(["-vf", "scale='min(1600,iw)':-2", "-q:v", "4"], data, ext, "out.jpg")
            mime = "image/jpeg"
        elif len(data) > IMG_HARD:
            raise MediaError("This image is too large (limit about 3 MB). Use a smaller image, or install ffmpeg so it can be shrunk. " + HELP)
    return "data:%s;base64,%s" % (mime, base64.b64encode(data).decode())


def pdf_text(data, limit=12000):
    try:
        from pypdf import PdfReader
    except ImportError:
        raise MediaError("PDF support needs the pypdf package. Run: pip install pypdf")
    try:
        reader = PdfReader(io.BytesIO(data))
        out, n = [], 0
        for page in reader.pages[:60]:
            t = page.extract_text() or ""
            out.append(t)
            n += len(t)
            if n > limit:
                break
    except Exception:
        raise MediaError("Could not read this PDF.")
    text = "\n".join(out).strip()
    if not text:
        raise MediaError("No selectable text found in this PDF (it may be scanned). Send the pages as images instead.")
    return text[:limit]
