import re
import sys
import json
from typing import Dict, Any, Optional

# --- API ---
try:
    from googleapiclient.discovery import build
except Exception:
    build = None

# --- Scrape ---
try:
    import yt_dlp
except Exception:
    yt_dlp = None

VIDEO_ID_RE = re.compile(
    r"""(?x)
    (?:v=|/v/|/embed/|/shorts/|youtu\.be/)
    ([0-9A-Za-z_-]{11})
    """
)

def extract_video_id(url_or_id: str) -> Optional[str]:
    if re.fullmatch(r"[0-9A-Za-z_-]{11}", url_or_id):
        return url_or_id
    m = VIDEO_ID_RE.search(url_or_id)
    return m.group(1) if m else None

def iso8601_duration_to_seconds(s: Optional[str]) -> Optional[int]:
    """Минимальный парсер ISO8601 (PnDTnHnMnS/ PTnHnMnS) в секунды."""
    if not s:
        return None
    p = re.compile(
        r"^P(?:(?P<days>\d+)D)?(?:T(?:(?P<h>\d+)H)?(?:(?P<m>\d+)M)?(?:(?P<sec>\d+)S)?)?$"
    )
    m = p.match(s)
    if not m:
        return None
    days = int(m.group("days") or 0)
    h = int(m.group("h") or 0)
    m_ = int(m.group("m") or 0)
    sec = int(m.group("sec") or 0)
    return days*86400 + h*3600 + m_*60 + sec

def safe_int(x):
    try:
        return int(x) if x is not None else None
    except Exception:
        return None

# =========================
#         API
# =========================
def get_stats_api(api_key: str, url_or_id: str) -> Dict[str, Any]:
    if build is None:
        raise RuntimeError("Установи google-api-python-client")
    vid = extract_video_id(url_or_id)
    if not vid:
        raise ValueError("Не удалось распознать video_id")

    svc = build("youtube", "v3", developerKey=api_key)
    parts = "snippet,statistics,contentDetails"
    data = svc.videos().list(part=parts, id=vid, maxResults=1).execute()
    items = data.get("items", [])
    if not items:
        return {}
    it = items[0]
    sn, st, cd = it.get("snippet", {}), it.get("statistics", {}), it.get("contentDetails", {})

    return {
        "videoId": it.get("id"),
        "url": f"https://www.youtube.com/watch?v={it.get('id')}",
        "title": sn.get("title"),
        "publishedAt": sn.get("publishedAt"),            # ISO8601
        "channelId": sn.get("channelId"),
        "channelTitle": sn.get("channelTitle"),
        "durationSec": iso8601_duration_to_seconds(cd.get("duration")),
        "viewCount": safe_int(st.get("viewCount")),
        "likeCount": safe_int(st.get("likeCount")),      # может быть None
        "commentCount": safe_int(st.get("commentCount")),# только число, без выгрузки
        "thumbnails": sn.get("thumbnails"),
    }

# =========================
#        SCRAPE
# =========================
def get_stats_scrape(url_or_id: str) -> Dict[str, Any]:
    if yt_dlp is None:
        raise RuntimeError("Установи yt-dlp")
    vid = extract_video_id(url_or_id) or url_or_id
    url = f"https://www.youtube.com/watch?v={vid}"
    ydl_opts = {"skip_download": True, "quiet": True, "nocheckcertificate": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return {
        "videoId": info.get("id"),
        "url": info.get("webpage_url"),
        "title": info.get("title"),
        "publishedAt": info.get("upload_date"),          # YYYYMMDD
        "channelId": info.get("channel_id"),
        "channelTitle": info.get("uploader"),
        "durationSec": info.get("duration"),
        "viewCount": info.get("view_count"),
        "likeCount": info.get("like_count"),             # если доступно публично
        "commentCount": info.get("comment_count"),
        "thumbnails": info.get("thumbnails"),
    }

# =========================
#          CLI
# =========================
HELP = """\
Использование:
  python youtube_stats.py api <API_KEY> <VIDEO_URL_OR_ID>
  python youtube_stats.py scrape <VIDEO_URL_OR_ID>

Примеры:
  python youtube_stats.py api AIza... https://youtu.be/dQw4w9WgXcQ
  python youtube_stats.py scrape dQw4w9WgXcQ
"""

def main(argv):
    if len(argv) < 2 or argv[1] in {"-h", "--help"}:
        print(HELP); return
    mode = argv[1]

    if mode == "api":
        if len(argv) < 4:
            print("Нужно: api <API_KEY> <VIDEO_URL_OR_ID>"); return
        api_key, url_or_id = argv[2], argv[3]
        print(json.dumps(get_stats_api(api_key, url_or_id), ensure_ascii=False, indent=2))
    elif mode == "scrape":
        if len(argv) < 3:
            print("Нужно: scrape <VIDEO_URL_OR_ID>"); return
        url_or_id = argv[2]
        print(json.dumps(get_stats_scrape(url_or_id), ensure_ascii=False, indent=2))
    else:
        print(HELP)

if __name__ == "__main__":
    main(sys.argv)
