import yt_dlp
import os
import sys
import shutil
import re
import json
import urllib.parse
from pathlib import Path
from datetime import datetime

CONFIG_FILE = Path(__file__).parent / "config.json"
HISTORY_FILE = Path(__file__).parent / "history.json"

QUALITY_PRESETS = {
    'best': ('bv*+ba/b', 'best'),
    '2160': ('bestvideo[height<=2160]+bestaudio/best[height<=2160]', 'best[height<=2160]'),
    '1080': ('bestvideo[height<=1080]+bestaudio/best[height<=1080]', 'best[height<=1080]'),
    '720':  ('bestvideo[height<=720]+bestaudio/best[height<=720]',   'best[height<=720]'),
    '480':  ('bestvideo[height<=480]+bestaudio/best[height<=480]',   'best[height<=480]'),
}


def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def check_ffmpeg():
    return shutil.which('ffmpeg') is not None


def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_history(entry):
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def show_history():
    history = load_history()
    if not history:
        print("\n   No download history.")
        return
    print(f"\n   Last {min(10, len(history))} downloads:")
    for entry in history[-10:]:
        tag = 'A' if entry.get('mode') == 'audio' else 'V'
        p = entry.get('path', '')
        print(f"   [{entry['date']}] [{tag}] {entry.get('title', '?')[:50]}")
        print(f"   {p if p else '(path not recorded)'}")
    print()


def get_download_path():
    config = load_config()
    last_path = config.get('last_path', '')

    if last_path:
        print(f"\n   Last folder: {last_path}")
        c = input("   Same folder? (Y/n): ").strip().lower()
        if c != 'n':
            p = Path(last_path)
            p.mkdir(parents=True, exist_ok=True)
            return str(p)

    inp = input("   Enter download path: ").strip()
    while not inp:
        inp = input("   Path cannot be empty. Enter path: ").strip()
    p = Path(inp)
    p.mkdir(parents=True, exist_ok=True)
    config['last_path'] = str(p)
    save_config(config)
    return str(p)


def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        down = d.get('downloaded_bytes', 0)
        speed = d.get('speed', 0)
        eta = d.get('eta', 0)
        pct = (down / total * 100) if total else 0
        bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
        spd = speed / 1024 / 1024 if speed else 0
        sys.stdout.write(f"\r   {bar} {pct:.1f}% | {spd:.1f} MB/s | ETA: {eta}s")
        sys.stdout.flush()
    elif d['status'] == 'finished':
        print(f"\n   Downloaded: {os.path.basename(d['filename'])}")


def download_video(url, path, mode='video', quality='best', audio_bitrate='best'):
    has_fm = check_ffmpeg()

    if mode == 'audio':
        fmt = 'ba/b' if has_fm else 'bestaudio/best'
    else:
        p = QUALITY_PRESETS.get(quality, QUALITY_PRESETS['best'])
        fmt = p[0] if has_fm else p[1]

    opts = {
        'format': fmt,
        'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'quiet': True,
        'no_warnings': True,
        'windowsfilenames': True,
    }

    if has_fm and mode == 'video':
        opts['merge_output_format'] = 'mkv'

    if mode == 'audio' and has_fm:
        pp = {'key': 'FFmpegExtractAudio', 'preferredcodec': 'm4a'}
        if audio_bitrate != 'best':
            pp['preferredquality'] = audio_bitrate
        opts['postprocessors'] = [pp]

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Unknown')
            save_history({
                'url': url,
                'title': title,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'mode': mode,
                'path': path,
            })
            print(f"\n   Saved to: {path}")
            return title
    except Exception as e:
        print(f"\n   Error: {e}")
        return None


def detect_link_type(url):
    ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        if info.get('_type') == 'playlist' or 'entries' in info:
            return 'playlist', info
        return 'video', info
    except Exception as e:
        return 'error', str(e)


def strip_playlist_param(url):
    return re.sub(r'[?&]list=[^&]+', '', url).rstrip('?&')


def is_downloaded_before(url):
    for entry in load_history():
        if entry.get('url') == url:
            return True
    return False


def show_info_and_confirm(url, audio_bitrate='best'):
    if is_downloaded_before(url):
        c = input("\n   Already downloaded before! Download again? (y/N): ").strip().lower()
        if c != 'y':
            print("   Skipped.")
            return False

    ydl_opts = {'quiet': True, 'no_warnings': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            dur = info.get('duration', 0)
            dur_int = int(dur or 0)
            dur_str = f"{dur_int//3600:02d}:{(dur_int%3600)//60:02d}:{dur_int%60:02d}" if dur_int else "?"
            res_set = set()
            for f in info.get('formats') or []:
                if f.get('height') and f.get('vcodec') and f['vcodec'] != 'none':
                    res_set.add(f['height'])
            res_str = ', '.join(f'{r}p' for r in sorted(res_set, reverse=True)[:8]) if res_set else "?"
            abr = info.get('abr', None)

            print(f"\n   Title: {title}")
            print(f"   Duration: {dur_str}")
            if res_str != '?':
                print(f"   Resolutions: {res_str}")
            if abr:
                print(f"   Audio: {abr}kbps")
    except Exception as e:
        print(f"\n   Could not fetch video info: {e}")

    c = input("\n   Download? (Y/n): ").strip().lower()
    return c != 'n'


def handle_single_video(url, mode, quality, audio_bitrate='best'):
    print(f"\n   Single Video [{'A' if mode == 'audio' else 'V'}]")
    path = get_download_path()
    if show_info_and_confirm(url, audio_bitrate):
        download_video(url, path, mode, quality, audio_bitrate)


def handle_video_in_playlist(url, mode, quality, audio_bitrate='best'):
    print("\n   This video is part of a playlist!")
    c = input("   Download this video only (1) or whole playlist (2)? [1/2]: ").strip()
    if c == '2':
        handle_playlist(url, mode, quality, audio_bitrate)
    else:
        handle_single_video(strip_playlist_param(url), mode, quality, audio_bitrate)


def handle_playlist(url, mode, quality, audio_bitrate='best'):
    print("\n   Playlist detected, fetching info...")
    ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    raw_entries = info.get('entries') or []
    entries = [e for e in raw_entries if e and e.get('id')]
    if not entries:
        print("   No videos found.")
        return

    title = info.get('title', 'Unknown')
    print(f"\n   Playlist: {title}")
    print(f"   Videos: {len(entries)}")

    print("\n   Options:")
    print("   1. Download ALL videos")
    print("   2. Download range (e.g. 1-10)")
    print("   3. Choose video(s) by title")
    print("   4. Download a single video")

    choice = input("\n   Choice (1/2/3/4): ").strip()

    if choice in ('3', '4'):
        print(f"\n   {'#':<4} Title")
        print("   " + "-" * 60)
        for i, e in enumerate(entries, 1):
            t = e.get('title', 'Unknown')
            print(f"   {i:<4} {t[:57]}")

    path = None

    if choice == '1':
        path = path or get_download_path()
        for i, e in enumerate(entries, 1):
            vid = e.get('id')
            vu = f"https://youtube.com/watch?v={vid}"
            print(f"\n   [{i}/{len(entries)}] {e.get('title', 'Unknown')}")
            download_video(vu, path, mode, quality, audio_bitrate)

    elif choice == '2':
        r = input("\n   Enter range (e.g. 1-10): ").strip()
        m = re.match(r'^(\d+)\s*-\s*(\d+)$', r)
        if m:
            start, end = int(m.group(1)), int(m.group(2))
            if start < 1:
                start = 1
            if end > len(entries):
                end = len(entries)
            if start <= end:
                path = get_download_path()
                for i in range(start, end + 1):
                    e = entries[i - 1]
                    vid = e.get('id')
                    vu = f"https://youtube.com/watch?v={vid}"
                    print(f"\n   [{i}/{len(entries)}] {e.get('title', 'Unknown')}")
                    download_video(vu, path, mode, quality, audio_bitrate)

    elif choice == '3':
        sel = input("\n   Enter numbers (comma-separated, e.g. 1,3,5): ").strip()
        idxs = [int(x.strip()) for x in sel.split(',') if x.strip().isdigit()]
        path = get_download_path()
        for idx in idxs:
            if 1 <= idx <= len(entries):
                e = entries[idx - 1]
                vid = e.get('id')
                if vid:
                    print(f"\n   Downloading: {e.get('title', 'Unknown')}")
                    download_video(f"https://youtube.com/watch?v={vid}", path, mode, quality, audio_bitrate)

    elif choice == '4':
        i = input("\n   Enter video number: ").strip()
        if i.isdigit():
            n = int(i)
            if 1 <= n <= len(entries):
                e = entries[n - 1]
                vid = e.get('id')
                if vid:
                    path = get_download_path()
                    print(f"\n   Downloading: {e.get('title', 'Unknown')}")
                    download_video(f"https://youtube.com/watch?v={vid}", path, mode, quality, audio_bitrate)


def choose_quality():
    print("\n   Video Quality:")
    print("   b - Best (no limit)")
    print("   4 - 4K (2160p)")
    print("   1 - 1080p")
    print("   7 - 720p")
    print("   8 - 480p")
    q = input("   Choose [b]: ").strip().lower()
    return {'b': 'best', '4': '2160', '1': '1080', '7': '720', '8': '480'}.get(q, 'best')


def choose_audio_bitrate():
    print("\n   Audio Quality:")
    print("   b - Best (no re-encode)")
    print("   3 - 320kbps")
    print("   1 - 192kbps")
    print("   2 - 128kbps")
    print("   6 - 64kbps")
    q = input("   Choose [b]: ").strip().lower()
    return {'b': 'best', '3': '320', '1': '192', '2': '128', '6': '64'}.get(q, 'best')


def is_url(text):
    text = text.strip()
    if text.startswith('http://') or text.startswith('https://'):
        return True
    if 'youtube.com' in text or 'youtu.be' in text:
        return True
    if 'youtube' in text and '.' in text:
        return True
    return False


def search_youtube(query, max_results=10):
    print(f"\n   Searching YouTube for: {query}")
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'default_search': 'ytsearch',
    }
    search_url = f"ytsearch{max_results}:{query}"
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)
            entries = info.get('entries', [])
            if not entries:
                print("   No results found.")
                return None
            print(f"\n   Results:")
            print(f"   {'#':<4} {'Title':<50} {'Duration':<10} Channel")
            print("   " + "-" * 90)
            results = []
            for i, e in enumerate(entries, 1):
                title = (e.get('title') or 'Unknown')[:48]
                dur = e.get('duration', 0) or 0
                dur_int = int(dur)
                if dur_int >= 3600:
                    dur_str = f"{dur_int//3600:02d}:{(dur_int%3600)//60:02d}:{dur_int%60:02d}"
                elif dur_int:
                    dur_str = f"{dur_int//60:02d}:{dur_int%60:02d}"
                else:
                    dur_str = "?:??"
                channel = (e.get('channel') or e.get('uploader') or '?')[:20]
                print(f"   {i:<4} {title:<50} {dur_str:<10} {channel}")
                vid = e.get('id')
                if vid:
                    results.append((i, title.strip(), f"https://youtube.com/watch?v={vid}"))
            return results
    except Exception as e:
        print(f"   Search error: {e}")
        return None


def handle_search(query, mode, quality, audio_bitrate='best'):
    results = search_youtube(query)
    if not results:
        return

    sel = input("\n   Enter video number to download (or Enter to cancel): ").strip()
    if not sel.isdigit():
        return
    n = int(sel)
    matching = [r for r in results if r[0] == n]
    if not matching:
        print("   Invalid number.")
        return

    _, title, url = matching[0]
    print(f"\n   Selected: {title}")
    handle_single_video(url, mode, quality, audio_bitrate)


def main():
    if not check_ffmpeg():
        print("ffmpeg not found! Install for best quality:")
        print("https://ffmpeg.org/download.html\n")

    print("=" * 50)
    print("   YOUTUBE DOWNLOADER - Highest Quality")
    print("=" * 50)

    m = input("\nMode: (V)ideo or (A)udio [V]: ").strip().lower()
    mode = 'audio' if m == 'a' else 'video'

    if mode == 'video':
        quality = choose_quality()
        audio_bitrate = 'best'
    else:
        quality = 'best'
        audio_bitrate = choose_audio_bitrate()

    abr_label = f" | Audio: {audio_bitrate}kbps" if audio_bitrate != 'best' else ''
    print(f"   Mode: {'Audio' if mode == 'audio' else 'Video'} | Quality: {quality}{abr_label}")

    while True:
        inp = input("\nPaste URL / Search (or 'q' to quit, 'h' for history): ").strip()
        if inp.lower() in ('q', 'quit', 'exit'):
            break
        if inp.lower() == 'h':
            show_history()
            continue
        if not inp:
            continue

        if is_url(inp):
            print("\nDetecting...")
            ltype, info = detect_link_type(inp)

            if ltype == 'error':
                print(f"Error: {info}")
                continue

            has_list = 'list=' in inp and 'watch?' in inp

            if ltype == 'video' and has_list:
                handle_video_in_playlist(inp, mode, quality, audio_bitrate)
            elif ltype == 'video':
                handle_single_video(inp, mode, quality, audio_bitrate)
            else:
                handle_playlist(inp, mode, quality, audio_bitrate)
        else:
            handle_search(inp, mode, quality, audio_bitrate)

    show_history()
    print("\nBye!")


if __name__ == '__main__':
    main()
