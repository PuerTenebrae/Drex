import os
import sys

# When frozen by PyInstaller, keep CWD at the exe's directory so config.ini
# is found/created next to the executable, not in the temp extraction dir.
if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))

from config_manager import ConfigManager
from downloader import Downloader
from ui import App


def main():
    config = ConfigManager()
    downloader = Downloader(ytdlp_path=config.ytdlp_path, ffmpeg_path=config.ffmpeg_path)
    app = App(config, downloader)
    app.mainloop()


if __name__ == "__main__":
    main()
