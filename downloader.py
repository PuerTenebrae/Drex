import os
import re
import shutil
import subprocess
import threading
from typing import Callable, Optional

_CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

FORMAT_ARGS: dict[str, list[str]] = {
    "MP4 (mejor calidad)": [
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
    ],
    "MP4 720p": [
        "-f", "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]",
        "--merge-output-format", "mp4",
    ],
    "MP4 480p": [
        "-f", "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best[height<=480]",
        "--merge-output-format", "mp4",
    ],
    "MP3 (mejor calidad)": ["-x", "--audio-format", "mp3", "--audio-quality", "0"],
    "MP3 192kbps":          ["-x", "--audio-format", "mp3", "--audio-quality", "192K"],
    "MP3 128kbps":          ["-x", "--audio-format", "mp3", "--audio-quality", "128K"],
    "FLAC":                 ["-x", "--audio-format", "flac"],
    "WAV":                  ["-x", "--audio-format", "wav"],
}

_PROGRESS_RE = re.compile(
    r"\[download\]\s+([\d.]+)%\s+of\s+\S+\s+at\s+(\S+)\s+ETA\s+(\S+)"
)


class Downloader:
    def __init__(self, ytdlp_path: str = "yt-dlp", ffmpeg_path: str = ""):
        self.ytdlp_path = ytdlp_path
        self.ffmpeg_path = ffmpeg_path
        self._process: Optional[subprocess.Popen] = None
        self._cancelled = False

    def is_ytdlp_available(self) -> bool:
        path = self.ytdlp_path
        if os.path.isfile(path):
            return True
        return shutil.which(path) is not None

    def is_ffmpeg_available(self) -> bool:
        path = self.ffmpeg_path
        if os.path.isfile(path):
            return True
        return shutil.which(path) is not None

    def download(
        self,
        url: str,
        fmt: str,
        output_folder: str,
        embed_thumbnail: bool = False,
        embed_metadata: bool = False,
        inject_args: Optional[list] = None,
        on_progress: Optional[Callable[[float, str, str], None]] = None,
        on_log: Optional[Callable[[str], None]] = None,
        on_done: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        self._cancelled = False
        t = threading.Thread(
            target=self._run,
            args=(url, fmt, output_folder, embed_thumbnail, embed_metadata,
                  inject_args or [], on_progress, on_log, on_done, on_error),
            daemon=True,
        )
        t.start()

    def cancel(self):
        self._cancelled = True
        if self._process:
            try:
                self._process.terminate()
            except Exception:
                pass

    def _run(self, url, fmt, output_folder, embed_thumbnail, embed_metadata,
             inject_args, on_progress, on_log, on_done, on_error):
        format_args = FORMAT_ARGS.get(fmt, FORMAT_ARGS["MP4 (mejor calidad)"])
        output_template = os.path.join(output_folder, "%(title)s.%(ext)s")

        ffmpeg_args = []
        if self.ffmpeg_path and os.path.isfile(self.ffmpeg_path):
            ffmpeg_args = ["--ffmpeg-location", self.ffmpeg_path]

        embed_args = []
        if embed_thumbnail:
            embed_args.append("--embed-thumbnail")
        if embed_metadata:
            embed_args.append("--embed-metadata")

        cmd = [
            self.ytdlp_path,
            *ffmpeg_args,
            *format_args,
            *embed_args,
            *inject_args,
            "--output", output_template,
            "--newline",
            "--progress",
            url,
        ]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=_CREATE_NO_WINDOW,
            )
            self._process = process  # expuesto solo para cancel()

            for raw_line in process.stdout:
                if self._cancelled:
                    break
                line = raw_line.rstrip()
                if line and on_log:
                    on_log(line)
                m = _PROGRESS_RE.search(line)
                if m and on_progress:
                    on_progress(float(m.group(1)), m.group(2), m.group(3))

            process.wait()

            if self._cancelled:
                if on_error:
                    on_error("Descarga cancelada.")
            elif process.returncode == 0:
                if on_done:
                    on_done()
            else:
                if on_error:
                    on_error(f"yt-dlp terminó con código {process.returncode}.")

        except FileNotFoundError:
            if on_error:
                on_error(
                    f"yt-dlp no encontrado en '{self.ytdlp_path}'.\n"
                    "Instalalo con:  pip install yt-dlp\n"
                    "o descargá el .exe desde github.com/yt-dlp/yt-dlp"
                )
        except Exception as exc:
            if on_error:
                on_error(str(exc))
        finally:
            self._process = None
