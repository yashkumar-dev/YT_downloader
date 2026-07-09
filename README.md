# YouTube Downloader

A Python-based CLI tool to download YouTube videos/playlists in the highest quality, with smart auto-detection of links and an interactive menu system.

## Features

- **Auto-detect** link type — video, playlist, or video inside a playlist
- **Video mode** — download at Best / 4K / 1080p / 720p / 480p
- **Audio mode** — extract audio at Best / 320k / 192k / 128k / 64k
- **Playlist modes** — download all, range (1-10), choose by title, or single
- **Smart prompts** — shows video info (title, duration, resolutions) before download
- **History** — tracks what you've downloaded and where
- **Path memory** — remembers last download folder
- **Skip duplicates** — warns if a video was already downloaded (detected by video ID)
- **YouTube search** — directly search without pasting a URL
- **PO Token protection** — generates proof-of-origin tokens to avoid bot blocks
- **Client rotation** — 7-client fallback chain (web_safari → android → web → tv_downgraded → web_embedded → mweb → ios) handles blocks automatically

## Pre-built binaries (recommended — nothing to install)

Download the latest executable for your OS from [Releases](https://github.com/yashkumar-dev/YT_downloader/releases):

| Platform | File | Size |
|----------|------|------|
| Windows | `ytd-Windows.exe` | ~136 MB |
| macOS | `ytd-macOS` | ~92 MB |
| Linux | `ytd-Linux` | ~194 MB |

Just download, double-click (or `chmod +x` on Linux/macOS), and run.  
**No Python, no ffmpeg, no Deno, no setup required** — everything is bundled inside the executable.

## Installation (from source)

```bash
git clone https://github.com/yashkumar-dev/YT_downloader.git
cd YT_downloader
pip install yt-dlp bgutil-ytdlp-pot-provider
deno install  # optional, enables PO Token server
```

> **Note:** If running from source, [ffmpeg](https://ffmpeg.org/download.html) is recommended for best quality video+audio merging.  
> Install it via: `winget install ffmpeg` (Windows) / `brew install ffmpeg` (macOS) / `sudo apt install ffmpeg` (Linux).

## Usage

```bash
# Using Python:
python ytd.py

# Or on Windows, double-click ytd.bat
```

### Interactive flow

1. Choose **Mode**: Video or Audio
2. Choose **Quality** (4K, 1080p, etc. or audio bitrate)
3. Paste a YouTube URL or type a **search query**
4. View video info and confirm download
5. Choose where to save

### Supported inputs

| Input | Behavior |
|-------|----------|
| `https://youtube.com/watch?v=xxx` | Downloads single video |
| `https://youtube.com/playlist?list=yyy` | Opens playlist menu |
| `https://youtube.com/watch?v=xxx&list=yyy` | Asks: download just this video or whole playlist |
| `python tutorial` | Searches YouTube and shows top 10 results |
| `h` | Shows download history |
| `q` | Quit |

### Playlist menu options

1. **Download ALL** — downloads every video
2. **Download range** — specify start-end (e.g. `1-10`)
3. **Choose by title** — pick specific videos by number
4. **Download single** — download one video from the playlist

## File structure

```
YT_downloader/
├── ytd.py                             # Main script
├── ytd.bat                            # Windows batch shortcut
├── bgutil-ytdlp-pot-provider/         # PO Token server files (bundled in exe)
├── .github/workflows/build.yml        # CI: builds + bundles everything into exe
├── config.json                        # Stores last download path (auto-generated)
├── history.json                       # Download history (auto-generated)
└── README.md                          # This file
```

## Notes

- **Pre-built binaries** include ffmpeg + PO Token server + Deno runtime — everything works immediately
- When running from source, ffmpeg is required for best quality (merges separate video + audio streams); without it, falls back to best single-stream (usually 720p max)
- Output format: `.mkv` (video), `.m4a` (audio)
- No cookies, no login required — works anonymously using PO Token + client rotation
