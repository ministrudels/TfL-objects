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
import json
import datetime
import requests

from JamCam_detections import get_model
from bson import ObjectId
from flask import Blueprint, jsonify, Response, request, render_template

crud = Blueprint('crud', __name__)
JamCam_res = requests.get("https://api.tfl.gov.uk/Place/Type/JamCam").json()


class JSONEncoder(json.JSONEncoder):
    ''' extend json-encoder class'''

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


@crud.route("/")
def list():
    return 'Hello this is the mongoAPI for TFL camera detected objects'


# Return the https://api.tfl.gov.uk/Place/Type/JamCam response modified to gcloud stored videos and checksums for videos
@crud.route("/JamCam")
def JamCam():
    return jsonify(JamCam_res)


### Writes

# Update the global response object
@crud.route("/update_JamCam_res")
def update_jamcam_res():
    res = requests.get("https://api.tfl.gov.uk/Place/Type/JamCam").json()
    for camera in res:
        for property in camera['additionalProperties']:
            if property['key'] == 'videoUrl':
                property['checksum'], property['value'] = get_model().find_latest_video(camera['id'])
                break
    global JamCam_res
    JamCam_res = res
    print('Response object updated!')
    return 'Updated'


# Update video details
@crud.route('/video_details/update')
def update_video_details():
    checksum = request.args.get('checksum')
    debug_url = request.args.get('debug_url')
    get_model().add_debug_video(checksum, debug_url)
    return 'Updated'


# Insert video metadata
@crud.route('/video_details/insert')
def insert_video_metadata():
    id = request.args.get('id')
    datetime = request.args.get('datetime')
    checksum = request.args.get('checksum')
    videoUrl = request.args.get('videoUrl')
    if None in (id, datetime, checksum, videoUrl):
        return 'All args not specified'

    db_object = {
        'id': id,
        'datetime': datetime,
        'checksum': checksum,
        'videoUrl': videoUrl
    }
    get_model().add_video_metadata(db_object)
    return 'Inserted'


# Insert detection for video
@crud.route('/insert_video_detection', methods=['POST'])
def insert_video_detection():
    payload = request.get_json()
    if None in (payload['id'], payload['datetime'], payload['checksum'], payload['status']):
        return 'All args not specified'
    get_model().add_video_detection(payload)
    return 'Inserted'


### Reads

# Return detections of the latest video from camera, referred to by camera id
@crud.route('/JamCam/<camera_id>')
def camera_detection(camera_id):
    latest_detection = get_model().find_latest_detection(camera_id)
    return Response(JSONEncoder().encode(latest_detection), mimetype='application/json')


# Return detections of a video, referred by its checksum
@crud.route('/video/<checksum>')
def video(checksum):
    video_detections = get_model().get_video_detections(checksum)
    return Response(JSONEncoder().encode(video_detections), mimetype='application/json')


# Return video details of a checksum
@crud.route('/video_details/<checksum>')
def video_details(checksum):
    video_dets = get_model().get_video_details(checksum)
    return Response(JSONEncoder().encode(video_dets), mimetype='application/json')


# Return video details of last 10 videos of a camera, referred to by its camera id
@crud.route('/videos/<camera_id>')
def videos(camera_id):
    latest_videos = get_model().find_latest_videos(camera_id)
    return Response(JSONEncoder().encode(latest_videos), mimetype='application/json')


# Boolean check
@crud.route('/checksum_exists/<checksum>')
def checksum_exists(checksum):
    response = {'result': get_model().checksum_exists(checksum)}
    return Response(JSONEncoder().encode(response), mimetype='application/json')


@crud.route('/checksum_detection_exists/<checksum>')
def checksum_detection_exists(checksum):
    response = {'result': get_model().checksum_detection_exists(checksum)}
    return Response(JSONEncoder().encode(response), mimetype='application/json')


