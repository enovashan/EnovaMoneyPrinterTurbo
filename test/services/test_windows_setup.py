from pathlib import Path

import pytest
import toml

from scripts import configure_windows


@pytest.fixture
def local_root(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[2]
    (tmp_path / "config.example.toml").write_bytes(
        (root / "config.example.toml").read_bytes()
    )
    monkeypatch.setattr(
        configure_windows, "__file__", str(tmp_path / "scripts" / "configure_windows.py")
    )
    return tmp_path


def test_creates_local_cpu_configuration(local_root, monkeypatch):
    monkeypatch.setattr(
        configure_windows.shutil, "which", lambda name: r"C:\FFmpeg\ffmpeg.exe"
    )
    configure_windows.main()
    settings = toml.load(local_root / "config.toml")
    assert settings["listen_host"] == "127.0.0.1"
    assert settings["app"]["llm_provider"] == "ollama"
    assert settings["app"]["ollama_model_name"] == "qwen2.5:3b"
    assert settings["app"]["video_source"] == "local"
    assert settings["app"]["ffmpeg_path"] == r"C:\FFmpeg\ffmpeg.exe"
    assert settings["app"]["max_concurrent_tasks"] == 1
    assert settings["app"]["upload_post_auto_upload"] is False
    assert settings["app"]["pexels_api_keys"] == []
    assert settings["whisper"]["device"] == "cpu"
    assert settings["whisper"]["compute_type"] == "int8"
    assert (local_root / "storage" / "local_videos").is_dir()


def test_preserves_existing_configuration(local_root, monkeypatch):
    destination = local_root / "config.toml"
    contents = b'[app]\npexels_api_keys = ["private-test-placeholder"]\n'
    destination.write_bytes(contents)
    monkeypatch.setattr(configure_windows.shutil, "which", lambda name: None)
    configure_windows.main()
    assert destination.read_bytes() == contents


def test_missing_ffmpeg_does_not_create_configuration(local_root, monkeypatch):
    monkeypatch.setattr(configure_windows.shutil, "which", lambda name: None)
    with pytest.raises(SystemExit, match="FFmpeg is missing"):
        configure_windows.main()
    assert not (local_root / "config.toml").exists()
