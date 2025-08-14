from s3_uploader import run_uploader, get_kvs_stream, extract_frame_from_kvs
from kvs_client import get_data_endpoint

import boto3
from botocore.exceptions import ClientError
from config import REGION, STREAM_NAME

if __name__ == "__main__":
    frame = extract_frame_from_kvs()
    if frame is not None:
        print("Got a frame from KVS!")
        with open("frame.jpg", "wb") as f:
            f.write(frame)
    else:
        print("No frame received from KVS.")