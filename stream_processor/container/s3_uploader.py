import boto3
import time
import cv2
import numpy as np
from datetime import datetime, timezone

from config import REGION, STREAM_NAME, S3_BUCKET, INTERVAL_SECONDS
from kvs_client import get_data_endpoint

# def extract_frame_from_kvs():
#     # Create a media client on each call
#     endpoint = get_data_endpoint()
#     media = boto3.client("kinesis-video-media", endpoint_url=endpoint, region_name=REGION)
#     resp = media.get_media(
#         StreamName=STREAM_NAME,
#         StartSelector={"StartSelectorType": "NOW"}
#     )
#     payload = resp["Payload"]

#     # Read a chink, adjust size as needed to cover at least 1 video frame
#     chunk = payload.read(1024*1024)
#     arr = np.frombuffer(chunk, dtype=np.uint8)
#     frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
#     return frame

def extract_frame_from_kvs():
    # create a 640×480 gray image with a timestamp
    img = np.full((480, 640, 3), 127, dtype=np.uint8)
    cv2.putText(img, datetime.now().isoformat(), (50,240),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    return img

def upload_frame(frame):
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    key = STREAM_NAME
    _, jpeg = cv2.imencode(".jpg", frame)
    s3 = boto3.client("s3", region_name=REGION)
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=jpeg.tobytes(),
        ContentType="image/jpeg"
    )
    print(f"[{ts}] Uploaded s3://{S3_BUCKET}/{key}")

def run_uploader():
    print(f"Starting frame loop ({INTERVAL_SECONDS}s interval)…")
    while True:
        frame = extract_frame_from_kvs()
        if frame is not None:
            upload_frame(frame)
        else:
            print("No frame decoded; retrying…")
        time.sleep(INTERVAL_SECONDS)