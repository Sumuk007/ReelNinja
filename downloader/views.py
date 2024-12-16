from django.shortcuts import render
import os
import urllib3
from urllib3.exceptions import NewConnectionError, MaxRetryError
from urllib3.exceptions import NameResolutionError
from django.http import HttpResponse, FileResponse
import instaloader
from moviepy.video.io.VideoFileClip import VideoFileClip
from instaloader.exceptions import (
    InvalidArgumentException,
    PrivateProfileNotFollowedException,
    BadResponseException,
    LoginRequiredException,
)

# Create your views here.
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def index(request):
    return render(request, 'index.html')

def download(request):
    if request.method == "POST":
        try:
            error_message = ''
            # Getting URL format from the form
            reel_url = request.POST['reel_url']
            download_format = request.POST['format']
            
            # Extracting shortcode from the URL
            shortcode = reel_url.split("/")[-2]

            loader = instaloader.Instaloader(download_videos=True)
            post = instaloader.Post.from_shortcode(loader.context, shortcode)

            # Initiating download
            loader.download_post(post, target=DOWNLOAD_FOLDER)
            
            # Listing all files in the DOWNLOAD_FOLDER
            files = os.listdir(DOWNLOAD_FOLDER)
            
            # Locating the downloaded video file
            video_path = None
            for file in files:
                if file.endswith('.mp4'):
                    video_path = os.path.join(DOWNLOAD_FOLDER, file)
                    break

            if video_path is None:
                raise FileNotFoundError(f"The video file for shortcode {shortcode} was not found in {DOWNLOAD_FOLDER}")

            # Converting to audio if required
            if download_format == "audio":
                audio_path = os.path.join(DOWNLOAD_FOLDER, f"{shortcode}.mp3")
                video_clip = VideoFileClip(video_path)
                try:
                    video_clip.audio.write_audiofile(audio_path)
                finally:
                    video_clip.close()
                return FileResponse(open(audio_path, 'rb'), as_attachment=True)  # Sending audio file

            # Sending video file
            return FileResponse(open(video_path, 'rb'), as_attachment=True)
        
        except MaxRetryError as e:
            error_message = "Check your internet connection!!" 
        except NewConnectionError as e:
            error_message = "Check your internet connection!!" 
        except ConnectionError as e:
            error_message = "Check your internet connection!!" 
        except NameResolutionError:
            print("Check your internet connection")
        except InvalidArgumentException:
            error_message = "Invalid URL. Please enter a valid Instagram Reel URL."
        except BadResponseException:
            error_message = "The post could not be fetched. Please check if the URL is correct, the post exists, or if the account is private."
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
        if error_message:
            return render(request, "index.html", {"error_message": error_message})
    
    return HttpResponse("Invalid request method")
