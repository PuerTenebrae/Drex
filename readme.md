# Drex

Descargador de música y video con interfaz gráfica construida sobre yt-dlp y ffmpeg.  
Pegás un link de YouTube, SoundCloud, o cualquier sitio compatible con yt-dlp, elegís el formato, y descarga directo a la carpeta que configuraste.  

yt-dlp maneja la descarga, ffmpeg la conversión a MP3 o MP4.

Soporta descarga como MP3 (audio) o MP4 (video), con conversión automática vía ffmpeg.

---

## Instalación

1. Descargá el ejecutable desde [Releases](https://github.com/PuerTenebrae/Drex/releases)
2. Colocá `Drex.exe` y `ffmpeg.exe` en la misma carpeta (`yt-dlp.exe` ya esta incluido en el release)
3. Editá `config.ini` con tu carpeta de descarga
4. Ejecutá `Drex.exe`

> `ffmpeg.exe` no está incluido — descargalo desde [ffmpeg.org](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z)

---

## Configuración

| Clave | Default | Descripción |
|---|---|---|
| `[paths] download_folder` | *(vacío)* | Carpeta destino de las descargas |
| `[paths] ffmpeg_path` | `ffmpeg.exe` | Ruta al ejecutable de ffmpeg |
| `[defaults] format` | `MP3 (mejor calidad)` | Formato por defecto al iniciar |
| `[defaults] show_log` | `true` | Mostrar log en pantalla |

---

## Comportamiento

- Al pegar un link y confirmar, inicia la descarga en segundo plano sin bloquear la UI
- El formato se puede cambiar antes de cada descarga desde el selector en pantalla
- Si `show_log = true`, los mensajes de progreso se muestran en tiempo real dentro de la app
- Los errores no cierran la aplicación — se muestran en el log sin crashear

---

## Preview

*(screenshot pendiente)*

---

## Para desarrolladores

**Requisitos:** Python 3.10+, `customtkinter`

```bash
pip install customtkinter
```

**Build:**

```bash
pyinstaller --onefile --windowed main.py
```

---

# Drex

Music and video downloader with a GUI built on top of yt-dlp and ffmpeg.  
Paste a link from YouTube, SoundCloud, or any yt-dlp-compatible site, pick a format, and it downloads straight to your configured folder.  

yt-dlp handles the downloading, ffmpeg handles the conversion to MP3 or MP4.

Supports MP3 (audio) and MP4 (video) output with automatic conversion via ffmpeg.

---

## Installation

1. Download the executable from [Releases](https://github.com/PuerTenebrae/Drex/releases)
2. Place `Drex.exe` and `ffmpeg.exe` in the same folder (`yt-dlp.exe` is already bundled in the release)
3. Edit `config.ini` with your download path
4. Run `Drex.exe`

> `ffmpeg.exe` is not bundled — download it from [ffmpeg.org](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z)