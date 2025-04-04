import yt_dlp
import os

class YouTubeDownloader:
    def __init__(self, download_folder):
        self.download_folder = download_folder

    def download_audio(self, url, progress_callback=None):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [self.progress_hook(progress_callback)],  # Agregar el hook de progreso
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', None)
            downloaded_file = os.path.join(self.download_folder, f"{video_title}.mp3")
            return downloaded_file

    def progress_hook(self, progress_callback):
        def hook(d):
            if d['status'] == 'downloading' and progress_callback:
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded_bytes = d.get('downloaded_bytes')
                if total_bytes:
                    progress = int(downloaded_bytes / total_bytes * 100)
                    progress_callback(progress)
        return hook
