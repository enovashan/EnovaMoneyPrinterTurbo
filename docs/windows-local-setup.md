# EnovaMoneyPrinterTurbo: local Windows setup

This fork retains upstream's MIT license and history. The application and all
optional Python extras are installed in `.venv` using the unchanged `uv.lock`.
Python 3.12 is supported by upstream's Python >=3.11 requirement.

## Start

Open PowerShell in the project folder. Start Ollama from the Windows Start menu
first, or run `ollama serve` in another terminal if it is not already running.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Start-Local.ps1
```

WebUI: <http://127.0.0.1:8501>

For the REST API, use a second terminal:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Start-Local.ps1 -Service API
```

API documentation: <http://127.0.0.1:8080/docs>. Stop each server with Ctrl+C.
These launchers stay in the foreground and do not install background services.
Both interfaces are local-only. Do not expose the unauthenticated WebUI to the
internet. Configure `[app].api_key` before exposing the API, and use a properly
secured reverse proxy if remote access is required.

## Default configuration

- **Scripts and keywords:** Ollama `qwen2.5:3b`, running locally on CPU. No API key.
- **Footage:** local uploads, so the default does not depend on stock-media keys.
  Upload your own licensed images/videos in the WebUI. Video inputs should be at
  least 480 pixels in both dimensions; low-resolution clips can be rejected.
- **Voice:** Azure TTS V1 / Edge TTS, `en-US-AriaNeural`. No key, but an internet
  connection and access to Microsoft's speech service are required.
- **Subtitles:** Edge timings by default. For uploaded narration or transcription,
  choose Whisper; `large-v3-turbo` uses CPU/int8. Its downloaded files are under
  `models\whisper-large-v3-turbo`. CPU transcription is slower than a CUDA GPU.
- **Video:** existing system FFmpeg, software `libx264`, one concurrent render.
  MoviePy 2 uses Pillow for captions; ImageMagick is not required.
- **Music and fonts:** upstream's bundled resources; user files can be uploaded.
- **Task state:** upstream's in-memory backend; Redis is optional, not required.
  Running/queued jobs do not survive process termination.
- **Publishing and paid generation:** disabled by default; never automatically
  submit paid requests or publish videos.

## Credentials and external features

`config.toml` is the local secrets file and is ignored by Git. Add credentials in
the WebUI settings or edit the matching section there. Restart running services
after manual edits. Do not put secrets in `config.example.toml`, scripts, issues,
or commits.

| Capability | What you must supply |
| --- | --- |
| Automatic stock footage | A free [Pexels API key](https://www.pexels.com/api/) or [Pixabay API key](https://pixabay.com/api/docs/); select that video source |
| Cloud LLMs | The chosen provider's key, model and endpoint; optional instead of Ollama |
| Paid AI-generated footage/images/music | An account, key and sufficient balance with the selected provider; review pricing before confirming generation |
| Azure V2 / commercial voices | Corresponding speech-provider credentials |
| Kokoro / Chatterbox voices | A separately deployed compatible TTS server; installing the application does not deploy these optional servers |
| TwelveLabs matching | TwelveLabs API key; its optional Python SDK is installed |
| Social publishing | Upload-Post account/key, linked social accounts and explicit publishing configuration |
| Redis task state | A separately provisioned private Redis server and matching settings; not needed for normal single-PC use |

Installing SDKs cannot enable third-party accounts or bypass provider access,
quotas, network restrictions, service terms or billing. Not all integrations can
be live-tested without their corresponding credentials.

## Reproduce the environment

Install Python 3.12, Git, FFmpeg and Ollama, then:

```powershell
python -m pip install --user uv
python -m uv sync --frozen --python 3.12 --all-extras
.\.venv\Scripts\python.exe .\scripts\configure_windows.py
ollama pull qwen2.5:3b
.\.venv\Scripts\python.exe -c "from huggingface_hub import snapshot_download; snapshot_download('mobiuslabsgmbh/faster-whisper-large-v3-turbo', local_dir=r'models\whisper-large-v3-turbo')"
python -m uv pip check --python .\.venv\Scripts\python.exe
```

The configuration helper preserves an existing `config.toml`, including secrets.
The Whisper model and Ollama model are separate downloads, not Git content.
Dependencies, models, generated files, logs and local credentials stay untracked.
Retain the checked-in dependency lock; do not upgrade packages individually.

The CLI defaults to Pexels even when the WebUI uses local footage. Specify local
mode explicitly when using your own material:

```powershell
.\.venv\Scripts\python.exe cli.py --video-subject "A short nature story" --video-source local --video-materials "C:\Media\nature.mp4" --voice-name en-US-AriaNeural-Female
```

The CLI prints a task summary; videos and other outputs are under `storage\tasks`.
Only run commands using material you own or have permission to use.

## Installation verification

Verified on this Windows installation on October 24, 2026:

- All 122 installed Python packages passed the dependency compatibility check.
- 227 focused upstream tests and 141 subtests passed; the three added setup
  tests also passed, including preservation of existing local credentials.
- The WebUI rendered its generation controls without application exceptions.
  Its health endpoint and the API ping returned HTTP 200, with both servers
  listening only on `127.0.0.1`.
- The application generated a script and three search phrases through Ollama.
- Edge TTS produced playable narration and subtitle timestamps.
- The downloaded Whisper model loaded offline and correctly transcribed the
  test narration using CPU/int8.
- A complete local-footage render produced a 1920x1080 H.264/AAC MP4 with
  narration, subtitles and bundled background music; FFmpeg decoded the entire
  output without errors. On this CPU, even a short HD video can take minutes.

These checks do not certify unconfigured stock-media, paid-generation,
publishing, Redis or external TTS services.

## Updating from upstream

`origin` points to `enovashan/EnovaMoneyPrinterTurbo`; `upstream` points to
`harry0703/MoneyPrinterTurbo`. Review upstream changes before merging, then rerun
the frozen sync command. Back up the ignored configuration and your generated
videos separately; GitHub intentionally does not contain them.
