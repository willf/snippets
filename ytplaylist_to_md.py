import yt_dlp


def get_playlist_markdown(url):
    # Configure options to only get info (no download)
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "force_generic_extractor": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract playlist information
            result = ydl.extract_info(url, download=False)

            if "entries" not in result:
                print("Could not find any videos in this playlist.")
                return

            print(f"## {result.get('title', 'YouTube Playlist')}\n")

            for entry in result["entries"]:
                title = entry.get("title")
                # Construct the full URL
                video_url = f"https://www.youtube.com/watch?v={entry.get('id')}"

                # Print in Markdown format
                print(f"{title}\t{video_url}")

        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    playlist_url = (
        "https://www.youtube.com/playlist?list=PL74DkXOkGrtgTVxyWlPl0xCvpfCizwD7N"
    )
    get_playlist_markdown(playlist_url)
