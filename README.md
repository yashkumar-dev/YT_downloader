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
- **Skip duplicates** — warns if a video was already downloaded
- **YouTube search** — directly search without pasting a URL

## Requirements

- Python 3.8+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (installed automatically via pip)

## Pre-built binaries (recommended — no Python or ffmpeg required)

Download the latest executable for your OS from [Releases](https://github.com/yashkumar-dev/YT_downloader/releases):

| Platform | File | Size |
|----------|------|------|
| Windows | `ytd-Windows.exe` | ~51 MB |
| macOS | `ytd-macOS` | ~29 MB |
| Linux | `ytd-Linux` | ~125 MB |

Just download, double-click (or `chmod +x` on Linux/macOS), and run.

**ffmpeg is bundled inside the executable** — high-quality downloads (1080p/4K) work out of the box with no manual setup.

## Installation (from source)

```bash
git clone https://github.com/yashkumar-dev/YT_downloader.git
cd YT_downloader
pip install yt-dlp
```

> **Note:** If running from source, [ffmpeg](https://ffmpeg.org/download.html) is recommended for best quality video+audio merging.  
> Install it via: `winget install ffmpeg` (Windows) / `brew install ffmpeg` (macOS) / `sudo apt install ffmpeg` (Linux).

## Usage (Python)

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
├── ytd.py                    # Main script
├── ytd.bat                   # Windows batch shortcut
├── .github/workflows/build.yml # CI: builds + bundles ffmpeg into EXE
├── config.json               # Stores last download path (auto-generated)
├── history.json              # Download history (auto-generated)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Notes

- **Pre-built binaries** include ffmpeg — high-quality downloads work immediately
- When running from source, ffmpeg is required for best quality (merges separate video + audio streams); without it, falls back to best single-stream (usually 720p max)
- Output format: `.mkv` (video), `.m4a` (audio)
