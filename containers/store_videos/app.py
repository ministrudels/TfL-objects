import os
import sys
import requests
import hashlib
import urllib.request
from datetime import datetime, timezone

API_ENDPOINT =  "http://localhost:8080/TFLcamera/"

def choose_feeds(lower, upper):
    r = requests.get("https://api.tfl.gov.uk/Place/Type/JamCam").json()
    return r[lower:upper]


def get_md5_hash(mp4url):
    hasher = hashlib.md5()
    data = urllib.request.urlopen(mp4url)
    hasher.update(data.read())
    return hasher


def get_mp4_url(camera):
    mp4url = None
    for property in camera['additionalProperties']:
        if property['key'] == 'videoUrl':
            mp4url = property['value']
    return mp4url

def store_video(camera, md5hash, dt):
    if not os.path.exists('/TfL_videos/'):
            os.mkdir('/TfL_videos/')

    id = camera['id']
    datetime = dt
    checksum = md5hash.hexdigest()
    downloadUrl = get_mp4_url(camera)
    checksum_exists = requests.get(API_ENDPOINT + "checksum_exists/" + checksum).json()['result']
    if checksum_exists:
        print('already exists', checksum)
        return 0
    else:
        print('adding', checksum)

        # Download to container storage
        filepath = '/TfL_videos/' + checksum + '.mp4'
        urllib.request.urlretrieve(downloadUrl, filepath)
        videoUrl = 'http://0.0.0.0:8000' + filepath

        # Upload video metadata 
        args = {
            'id': id,
            'datetime': datetime,
            'checksum': checksum,
            'videoUrl': videoUrl
        }
        requests.get(API_ENDPOINT + 'video_details/insert', args)
        return 1

def main(argv):
    current_dt = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    print('Downloading latest videos at', current_dt)
    feeds = choose_feeds(int(argv[1]), int(argv[2]))

    # Create downloader object
    videos_downloaded = 0
    for camera in feeds:
        mp4url = get_mp4_url(camera)
        md5hash = get_md5_hash(mp4url)
        videos_downloaded += store_video(camera, md5hash, current_dt)
        sys.stdout.flush()
    print('New videos downloaded:', videos_downloaded)


if __name__ == "__main__":
    main(sys.argv)
