import configparser
import os
import sys
from pathlib import Path


def _get_app_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


CONFIG_FILE = os.path.join(_get_app_dir(), "config.ini")
DEFAULT_DOWNLOAD_FOLDER = str(Path.home() / "Downloads")


class ConfigManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self._load()

    def _load(self):
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE, encoding="utf-8")
        self._ensure_defaults()

    def _ensure_defaults(self):
        changed = False

        for section in ("paths", "defaults", "discord"):
            if section not in self.config:
                self.config[section] = {}
                changed = True

        paths    = self.config["paths"]
        defaults = self.config["defaults"]
        discord  = self.config["discord"]

        for key, val in [
            ("download_folder", DEFAULT_DOWNLOAD_FOLDER),
            ("ytdlp_path", "yt-dlp"),
            ("ffmpeg_path", "ffmpeg.exe"),
        ]:
            if key not in paths:
                paths[key] = val
                changed = True

        for key, val in [
            ("format", "MP4 (mejor calidad)"),
            ("show_log", "true"),
        ]:
            if key not in defaults:
                defaults[key] = val
                changed = True

        for key, val in [
            ("token", "TU_TOKEN_AQUI"),
            ("allowed_channel_ids", ""),
        ]:
            if key not in discord:
                discord[key] = val
                changed = True

        if changed:
            self._save()

    def _save(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            self.config.write(f)

    @property
    def download_folder(self) -> str:
        return self.config["paths"]["download_folder"]

    @download_folder.setter
    def download_folder(self, value: str):
        self.config["paths"]["download_folder"] = value
        self._save()

    @staticmethod
    def _resolve_binary(raw: str) -> str:
        """Return the absolute path to a binary, trying several locations."""
        # 1. Absolute path that exists.
        if os.path.isabs(raw) and os.path.isfile(raw):
            return raw

        # 2. Relative path with a separator → resolve against app dir.
        if not os.path.isabs(raw) and (os.sep in raw or "/" in raw):
            resolved = os.path.normpath(os.path.join(_get_app_dir(), raw))
            if os.path.isfile(resolved):
                return resolved

        # 3. Plain name → check app dir (for bundled exes like ffmpeg.exe)
        #    then the venv Scripts dir (for pip-installed tools like yt-dlp).
        for search_dir in (_get_app_dir(), os.path.dirname(sys.executable)):
            for candidate in (raw, raw + ".exe"):
                full = os.path.join(search_dir, candidate)
                if os.path.isfile(full):
                    return full

        # 4. Fall back to raw; caller uses shutil.which or lets subprocess fail.
        return raw

    @property
    def ytdlp_path(self) -> str:
        return self._resolve_binary(self.config["paths"]["ytdlp_path"])

    @property
    def ffmpeg_path(self) -> str:
        return self._resolve_binary(self.config["paths"]["ffmpeg_path"])

    @property
    def default_format(self) -> str:
        return self.config["defaults"]["format"]

    @default_format.setter
    def default_format(self, value: str):
        self.config["defaults"]["format"] = value
        self._save()

    @property
    def show_log(self) -> bool:
        return self.config["defaults"].getboolean("show_log", True)

    @show_log.setter
    def show_log(self, value: bool):
        self.config["defaults"]["show_log"] = str(value).lower()
        self._save()

    @property
    def discord_token(self) -> str:
        return self.config["discord"].get("token", "")

    @property
    def discord_allowed_channels(self) -> set[int]:
        raw = self.config["discord"].get("allowed_channel_ids", "")
        result = set()
        for part in raw.split(","):
            part = part.strip()
            if part.isdigit():
                result.add(int(part))
        return result
