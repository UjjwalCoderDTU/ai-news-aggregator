from datetime import datetime, timezone
from typing import Any

from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi


def normalize_channel(channel: str) -> str:
    """Convert channel handle to a standard uploads URL."""
    channel = channel.strip()
    if not channel.startswith("@"):
        channel = f"@{channel}"
    return f"https://www.youtube.com/{channel}/videos"


def get_channel_videos(channel_url: str, hours: float, max_videos: int = 100) -> list[dict[str, Any]]:
    """Fetch videos uploaded within the last N hours."""
    cutoff = datetime.now(timezone.utc).timestamp() - (hours * 3600)

    flat_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "playlistend": max_videos,
    }

    with YoutubeDL(flat_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)

    if not info or not info.get("entries"):
        return []

    videos = []
    for entry in info["entries"]:
        if not entry or not entry.get("id"):
            continue

        video_id = entry["id"]

        video_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }

        with YoutubeDL(video_opts) as ydl:
            video_info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}",
                download=False
            )

        if not video_info:
            continue

        upload_date = video_info.get("upload_date")
        video_time = video_info.get("timestamp", 0) or 0

        if upload_date and not video_time:
            try:
                video_time = datetime.strptime(upload_date, "%Y%m%d").replace(
                    tzinfo=timezone.utc
                ).timestamp()
            except ValueError:
                video_time = 0

        if video_time < cutoff:
            break

        videos.append({
            "id": video_id,
            "title": video_info.get("title", entry.get("title", "")),
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "published_at": datetime.fromtimestamp(
                video_time, tz=timezone.utc
            ).isoformat() if video_time else None,
        })

    return videos


# 🔥 IMPROVED TRANSCRIPT FUNCTION
def get_transcript(video_id: str) -> str | None:
    # ✅ 1. Try manual transcript
    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, languages=['en', 'en-US']
        )
        return " ".join([t['text'] for t in transcript])
    except Exception:
        pass

    # ✅ 2. Try auto-generated transcript
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_generated_transcript(['en'])
        return " ".join([t['text'] for t in transcript.fetch()])
    except Exception:
        pass

    # ✅ 3. Try translation fallback (any language → English)
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        for t in transcript_list:
            try:
                translated = t.translate('en').fetch()
                return " ".join([x['text'] for x in translated])
            except Exception:
                continue
    except Exception:
        pass

    # ❌ Final fallback
    print(f"⚠️ No transcript available for {video_id}")
    return None


def scrape_channel(channel: str, hours: float = 24) -> list[dict[str, Any]]:
    url = normalize_channel(channel)
    videos = get_channel_videos(url, hours, max_videos=100)

    results = []
    for video in videos:
        try:
            transcript = get_transcript(video["id"])

            result = {
                "id": video["id"],
                "title": video["title"],
                "url": video["url"],
                "published_at": video["published_at"],
                "transcript": transcript,
            }

            results.append(result)

        except Exception as e:
            print(f"❌ Error processing video {video['id']}: {e}")
            continue

    return results


if __name__ == "__main__":
    videos = scrape_channel(
        channel="@vaibhavsisinty",
        hours=24
    )

    for video in videos:
        print(f"\nTitle: {video['title']}")
        print(f"URL: {video['url']}")
        print(f"Published: {video['published_at']}")
        if video["transcript"]:
            print(f"Transcript: {video['transcript'][:200]}...")
        else:
            print("Transcript: Not available")