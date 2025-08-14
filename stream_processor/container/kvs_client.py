import boto3, base64, cv2, numpy as np
from datetime import datetime, timedelta, timezone
from config import REGION, STREAM_NAME

def get_data_endpoint():
    _kvs = boto3.client("kinesisvideo", region_name=REGION)
    resp = _kvs.get_data_endpoint(
        StreamName=STREAM_NAME,
        APIName="GET_MEDIA"
    )
    return resp["DataEndpoint"]

def get_live_frame():
    kvs = boto3.client("kinesisvideo", region_name=REGION)
    endpoint = kvs.get_data_endpoint(
        StreamName=STREAM_NAME,
        APIName="GET_MEDIA"
    )["DataEndpoint"]

    kvam = boto3.client("kinesis-video-media", endpoint_url=endpoint, region_name=REGION)
    stream = kvam.get_media(
        StreamName=STREAM_NAME,
        StartSelector={"StartSelectorType": "NOW"}
    )["Payload"]

    # Save a few bytes to a temp MKV file and decode
    with open("temp.mkv", "wb") as f:
        f.write(stream.read(1024*1024))  # read first MB or so

    cap = cv2.VideoCapture("temp.mkv")
    ret, frame = cap.read()
    cap.release()

    return frame if ret else None

frame = get_live_frame()
if frame is not None:
    cv2.imwrite("frame.jpg", frame)
    print("Frame saved as frame.jpg")
else:
    print("No frame captured")