# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from bson.objectid import ObjectId
from flask_pymongo import PyMongo


builtin_list = list

mongo = None
video_detections = None
tfl_videos = None

def _id(id):
    if not isinstance(id, ObjectId):
        return ObjectId(id)
    return id


# [START from_mongo]
def from_mongo(data):
    """
    Translates the MongoDB dictionary format into the format that's expected
    by the application.
    """
    if not data:
        return None

    data['id'] = str(data['_id'])
    return data
# [END from_mongo]


def init_app(app):
    global mongo
    global video_detections
    global tfl_videos
    mongo = PyMongo(app)
    mongo.init_app(app)

    # Set database collections which are used by the API
    video_detections = mongo.db.videoDetections
    tfl_videos = mongo.db.TfLvideos

    # Index on fields which get sorted on for faster query performance
    tfl_videos.create_index('datetime')


# Return latest camera detection based off JamCam ID
def find_latest_detection(camera_id):
    global video_detections
    cursor = video_detections.find({'id': camera_id})
    latest_detection = None
    for detection in cursor:
        if latest_detection is None:
            latest_detection = detection
        if detection['datetime'] > latest_detection['datetime']:
            latest_detection = detection
    return latest_detection


# Latest video from the JamCam id
def find_latest_video(camera_id):
    global tfl_videos
    cursor = tfl_videos.find({'id': camera_id}).limit(1).sort('datetime', -1)
    if cursor.count() == 0:
        return None, None
    latest_camera = cursor.next()
    return latest_camera['checksum'], latest_camera['videoUrl']


# Latest 10 videos from the JamCam id
def find_latest_videos(camera_id):
    global tfl_videos
    cursor = tfl_videos.find({'id': camera_id}).limit(10).sort('datetime', -1)
    return list(cursor)


# Get detections off a video checksum
def get_video_detections(checksum):
    global video_detections
    cursor = video_detections.find({'checksum': checksum})
    return list(cursor)[0]


# Get video details off a checksum
def get_video_details(checksum):
    global tfl_videos
    cursor = tfl_videos.find({'checksum': checksum})
    return list(cursor)[0]


#
# Writes!
#
def add_video_metadata(video_metadata):
    global tfl_videos
    tfl_videos.insert_one(video_metadata)
    return


# Add debug video URL
def add_debug_video(checksum, debug_url):
    global tfl_videos
    tfl_videos.update_one({'checksum': checksum}, {'$set': {"videoUrl_debug": debug_url}})
    return


def add_video_detection(document):
    global video_detections
    video_detections.insert_one(document)
    return


#
# Boolean helper
#
def checksum_exists(checksum):
    global tfl_videos
    cursor = tfl_videos.find({'checksum': checksum}).limit(1)
    return True if len(list(cursor)) == 1 else False


def checksum_detection_exists(checksum):
    global video_detections
    cursor = video_detections.find({'checksum': checksum}).limit(1)
    return True if len(list(cursor)) == 1 else False

