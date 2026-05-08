import os
import tkinter as tk

import customtkinter as ctk

from config_manager import ConfigManager
from downloader import Downloader

# ── Palette ──────────────────────────────────────────────────────────────────
BG_MAIN     = "#080812"   # dark navy-black
BG_PANEL    = "#0e0e1e"   # panel / card
BG_INPUT    = "#0b0b18"   # entry fields
BG_BUTTON   = "#17102e"   # button fill (dark purple)
BORDER      = "#1e1a3a"   # purple-tinted border

COLOR_BRAND = "#cc33ff"   # magenta — title "DREX"
ACCENT      = "#00cccc"   # cyan — primary action / progress
ACCENT_ERR  = "#ff3366"   # error
ACCENT_OK   = "#00cc66"   # success

TEXT_PRI    = "#f0f0f0"
TEXT_SEC    = "#8899cc"   # muted blue-gray, legible
TEXT_LOG    = "#7788aa"   # log text

FONT_MONO   = "Consolas"

FORMATS = [
    "MP4 (mejor calidad)",
    "MP4 720p",
    "MP4 480p",
    "MP3 (mejor calidad)",
    "MP3 192kbps",
    "MP3 128kbps",
    "FLAC",
    "WAV",
]

_SITES_HINT = (
    "YouTube · Twitter/X · Instagram · TikTok · SoundCloud · "
    "Twitch · Facebook · Vimeo · +1000 más"
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sec_label(parent, text) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(family=FONT_MONO, size=11, weight="bold"),
        text_color=TEXT_SEC,
        anchor="w",
    )


def _divider(parent) -> ctk.CTkFrame:
    return ctk.CTkFrame(parent, height=1, fg_color=BORDER, corner_radius=0)


def _dot_label(parent, text: str, ok: bool) -> ctk.CTkLabel:
    color = ACCENT_OK if ok else ACCENT_ERR
    return ctk.CTkLabel(
        parent,
        text=f"● {text}",
        font=ctk.CTkFont(family=FONT_MONO, size=11),
        text_color=color,
    )


# ── Main window ───────────────────────────────────────────────────────────────

class App(ctk.CTk):
    def __init__(self, config: ConfigManager, downloader: Downloader):
        super().__init__()
        self._cfg = config
        self._dl  = downloader
        self._log_visible = True

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("Drex Downloader")
        self.geometry("660x620")
        self.minsize(560, 500)
        self.configure(fg_color=BG_MAIN)
        self.resizable(True, True)

        self._build()
        self._load_config()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        root = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        root.pack(fill="both", expand=True, padx=28, pady=22)

        # ── Title row ─────────────────────────────────────────────────────────
        title_row = ctk.CTkFrame(root, fg_color="transparent")
        title_row.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            title_row,
            text="DREX",
            font=ctk.CTkFont(family=FONT_MONO, size=22, weight="bold"),
            text_color=COLOR_BRAND,
        ).pack(side="left")
        ctk.CTkLabel(
            title_row,
            text=" DOWNLOADER",
            font=ctk.CTkFont(family=FONT_MONO, size=22, weight="bold"),
            text_color=TEXT_PRI,
        ).pack(side="left")

        # Binary status indicators — right side of title
        ytdlp_ok  = self._dl.is_ytdlp_available()
        ffmpeg_ok = self._dl.is_ffmpeg_available()

        status_row = ctk.CTkFrame(title_row, fg_color="transparent")
        status_row.pack(side="right", anchor="center")
        _dot_label(status_row, "yt-dlp", ytdlp_ok).pack(side="left", padx=(0, 10))
        _dot_label(status_row, "ffmpeg", ffmpeg_ok).pack(side="left")

        _divider(root).pack(fill="x", pady=(6, 16))

        # ── URL ───────────────────────────────────────────────────────────────
        _sec_label(root, "URL").pack(anchor="w")
        self._url_entry = ctk.CTkEntry(
            root,
            placeholder_text="https://...",
            height=38,
            fg_color=BG_INPUT,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT_PRI,
            placeholder_text_color=TEXT_SEC,
            font=ctk.CTkFont(family=FONT_MONO, size=12),
            corner_radius=3,
        )
        self._url_entry.pack(fill="x", pady=(4, 4))

        ctk.CTkLabel(
            root,
            text=_SITES_HINT,
            font=ctk.CTkFont(family=FONT_MONO, size=11),
            text_color="#6655aa",
            anchor="w",
        ).pack(anchor="w", pady=(0, 16))

        # ── Format + Options row ──────────────────────────────────────────────
        mid = ctk.CTkFrame(root, fg_color="transparent")
        mid.pack(fill="x", pady=(0, 16))
        mid.columnconfigure(0, weight=2)
        mid.columnconfigure(1, weight=1)

        # Format column
        fmt_col = ctk.CTkFrame(mid, fg_color="transparent")
        fmt_col.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        _sec_label(fmt_col, "FORMATO").pack(anchor="w")
        self._fmt_var = tk.StringVar(value=self._cfg.default_format)
        ctk.CTkOptionMenu(
            fmt_col,
            variable=self._fmt_var,
            values=FORMATS,
            height=38,
            fg_color=BG_INPUT,
            button_color=BG_BUTTON,
            button_hover_color="#1e1a3a",
            dropdown_fg_color=BG_PANEL,
            dropdown_hover_color="#17102e",
            text_color=TEXT_PRI,
            dropdown_text_color=TEXT_PRI,
            font=ctk.CTkFont(family=FONT_MONO, size=12),
            corner_radius=3,
            command=self._on_fmt_change,
        ).pack(fill="x", pady=(4, 0))

        # Options column (checkboxes)
        opt_col = ctk.CTkFrame(mid, fg_color="transparent")
        opt_col.grid(row=0, column=1, sticky="nsew")
        _sec_label(opt_col, "OPCIONES").pack(anchor="w")

        chk_frame = ctk.CTkFrame(opt_col, fg_color="transparent")
        chk_frame.pack(anchor="w", pady=(6, 0))

        self._thumb_var = tk.BooleanVar(value=False)
        self._meta_var  = tk.BooleanVar(value=False)

        _chk_style = dict(
            fg_color=ACCENT,
            hover_color="#1e1a3a",
            border_color=BORDER,
            border_width=1,
            checkmark_color="#000000",
            corner_radius=2,
            text_color=TEXT_PRI,
            font=ctk.CTkFont(family=FONT_MONO, size=11),
        )
        ctk.CTkCheckBox(
            chk_frame, text="Thumbnail", variable=self._thumb_var, **_chk_style
        ).pack(anchor="w", pady=(0, 8))
        ctk.CTkCheckBox(
            chk_frame, text="Metadata",  variable=self._meta_var,  **_chk_style
        ).pack(anchor="w")

        # ── Download button ───────────────────────────────────────────────────
        self._dl_btn = ctk.CTkButton(
            root,
            text="DESCARGAR",
            height=44,
            fg_color=ACCENT,
            hover_color="#00aaaa",
            text_color="#000000",
            font=ctk.CTkFont(family=FONT_MONO, size=14, weight="bold"),
            corner_radius=3,
            command=self._start,
        )
        self._dl_btn.pack(fill="x", pady=(0, 18))

        _divider(root).pack(fill="x", pady=(0, 14))

        # ── Progress ──────────────────────────────────────────────────────────
        _sec_label(root, "PROGRESO").pack(anchor="w")
        self._progress = ctk.CTkProgressBar(
            root,
            height=6,
            corner_radius=2,
            fg_color=BG_PANEL,
            progress_color=TEXT_SEC,
            border_width=0,
        )
        self._progress.set(0)
        self._progress.pack(fill="x", pady=(6, 5))

        self._status_lbl = ctk.CTkLabel(
            root,
            text="Listo.",
            font=ctk.CTkFont(family=FONT_MONO, size=12),
            text_color=TEXT_SEC,
            anchor="w",
        )
        self._status_lbl.pack(fill="x", pady=(0, 14))

        _divider(root).pack(fill="x", pady=(0, 10))

        # ── Log ───────────────────────────────────────────────────────────────
        log_hdr = ctk.CTkFrame(root, fg_color="transparent")
        log_hdr.pack(fill="x", pady=(0, 6))
        _sec_label(log_hdr, "OUTPUT LOG").pack(side="left")
        self._toggle_btn = ctk.CTkButton(
            log_hdr,
            text="▲ ocultar",
            width=82,
            height=20,
            fg_color="transparent",
            hover_color=BG_PANEL,
            text_color=TEXT_SEC,
            font=ctk.CTkFont(family=FONT_MONO, size=11),
            corner_radius=2,
            command=self._toggle_log,
        )
        self._toggle_btn.pack(side="right")

        self._log_frame = ctk.CTkFrame(root, fg_color=BG_PANEL, corner_radius=3)
        self._log_frame.pack(fill="both", expand=True)
        self._log_text = ctk.CTkTextbox(
            self._log_frame,
            fg_color=BG_PANEL,
            text_color=TEXT_LOG,
            font=ctk.CTkFont(family=FONT_MONO, size=12),
            corner_radius=3,
            border_width=1,
            border_color=BORDER,
            wrap="none",
            state="disabled",
        )
        self._log_text.pack(fill="both", expand=True, padx=1, pady=1)

    # ── Config ────────────────────────────────────────────────────────────────

    def _load_config(self):
        self._fmt_var.set(self._cfg.default_format)
        if not self._cfg.show_log:
            self._toggle_log()

    # ── Actions ───────────────────────────────────────────────────────────────

    def _on_fmt_change(self, value: str):
        self._cfg.default_format = value

    def _toggle_log(self):
        if self._log_visible:
            self._log_frame.pack_forget()
            self._toggle_btn.configure(text="▼ mostrar")
            self._log_visible = False
            self._cfg.show_log = False
        else:
            self._log_frame.pack(fill="both", expand=True)
            self._toggle_btn.configure(text="▲ ocultar")
            self._log_visible = True
            self._cfg.show_log = True

    def _start(self):
        url = self._url_entry.get().strip()
        if not url:
            self._set_status("Ingresá una URL.", error=True)
            return

        folder = self._cfg.download_folder
        if not os.path.isdir(folder):
            try:
                os.makedirs(folder, exist_ok=True)
            except Exception as exc:
                self._set_status(f"Carpeta inválida: {exc}", error=True)
                return

        if not self._dl.is_ytdlp_available():
            msg = f"yt-dlp no encontrado en '{self._dl.ytdlp_path}'."
            self._set_status(msg, error=True)
            self._append_log(f"[ERROR] {msg}")
            return

        self._set_busy(True)
        self._clear_log()
        self._set_progress(0, state="idle")
        self._set_status("Iniciando descarga...")

        self._dl.download(
            url=url,
            fmt=self._fmt_var.get(),
            output_folder=folder,
            embed_thumbnail=self._thumb_var.get(),
            embed_metadata=self._meta_var.get(),
            on_progress=lambda p, s, e: self.after(0, lambda: self._on_progress(p, s, e)),
            on_log=lambda line: self.after(0, lambda l=line: self._append_log(l)),
            on_done=lambda: self.after(0, self._on_done),
            on_error=lambda msg: self.after(0, lambda m=msg: self._on_error(m)),
        )

    # ── Download callbacks ────────────────────────────────────────────────────

    def _on_progress(self, percent: float, speed: str, eta: str):
        self._set_progress(percent / 100.0, state="active")
        self._set_status(f"{percent:.1f}%  ·  {speed}  ·  ETA {eta}")

    def _on_done(self):
        self._set_progress(1.0, state="done")
        self._set_status("Descarga completa.")
        self._set_busy(False)

    def _on_error(self, message: str):
        self._set_progress(0, state="error")
        self._set_status(f"Error: {message.splitlines()[0]}", error=True)
        self._append_log(f"\n[ERROR] {message}")
        self._set_busy(False)

    # ── UI state helpers ──────────────────────────────────────────────────────

    def _set_busy(self, busy: bool):
        if busy:
            self._dl_btn.configure(
                state="disabled",
                text="DESCARGANDO...",
                fg_color="#12102a",
                text_color=TEXT_SEC,
            )
        else:
            self._dl_btn.configure(
                state="normal",
                text="DESCARGAR",
                fg_color=ACCENT,
                hover_color="#00aaaa",
                text_color="#000000",
            )

    def _set_progress(self, value: float, state: str = "idle"):
        color_map = {
            "idle":   TEXT_SEC,
            "active": ACCENT,
            "done":   ACCENT_OK,
            "error":  ACCENT_ERR,
        }
        self._progress.set(value)
        self._progress.configure(progress_color=color_map.get(state, TEXT_SEC))

    def _set_status(self, text: str, error: bool = False):
        self._status_lbl.configure(
            text=text,
            text_color=ACCENT_ERR if error else TEXT_SEC,
        )

    def _append_log(self, line: str):
        self._log_text.configure(state="normal")
        self._log_text.insert("end", line + "\n")
        self._log_text.see("end")
        self._log_text.configure(state="disabled")

    def _clear_log(self):
        self._log_text.configure(state="normal")
        self._log_text.delete("1.0", "end")
        self._log_text.configure(state="disabled")
