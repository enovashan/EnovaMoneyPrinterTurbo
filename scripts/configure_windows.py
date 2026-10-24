"""Create a private, CPU-friendly local configuration without overwriting secrets."""

import shutil
from pathlib import Path

import toml


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    destination = root / "config.toml"
    if destination.exists():
        print("Existing config.toml preserved. Edit it locally to change providers.")
        return

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise SystemExit("FFmpeg is missing from PATH. Install FFmpeg and try again.")

    settings = toml.load(root / "config.example.toml")
    settings.update(listen_host="127.0.0.1", listen_port=8080, log_level="INFO")
    settings["app"].update(
        llm_provider="ollama",
        ollama_base_url="http://127.0.0.1:11434/v1",
        ollama_model_name="qwen2.5:3b",
        video_source="local",
        subtitle_provider="edge",
        ffmpeg_path=ffmpeg,
        video_codec="libx264",
        material_concurrency=1,
        video_clip_concurrency=1,
        max_concurrent_tasks=1,
        enable_redis=False,
        upload_post_enabled=False,
        upload_post_auto_upload=False,
    )
    settings["whisper"].update(
        model_size="large-v3-turbo", device="cpu", compute_type="int8"
    )
    settings["ui"].update(
        language="en",
        video_language="en-US",
        tts_server="azure-tts-v1",
        voice_name="en-US-AriaNeural-Female",
        bgm_type="random",
        bgm_volume=0.2,
        font_name="MicrosoftYaHeiBold.ttc",
        open_task_folder_on_completion=False,
    )
    with destination.open("x", encoding="utf-8") as stream:
        toml.dump(settings, stream)
    (root / "storage" / "local_videos").mkdir(parents=True, exist_ok=True)
    print("Created ignored config.toml; local footage needs no stock-media API key.")
    print("Optional free stock footage: add a Pexels or Pixabay key in the WebUI.")


if __name__ == "__main__":
    main()
