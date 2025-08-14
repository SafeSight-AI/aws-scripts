import boto3
import cv2
from datetime import datetime, timezone

from kvs_client import get_live_frame
from config import S3_BUCKET, REGION, STREAM_NAME

def upload_frame_to_s3(frame):
    """
    Encodes a given image frame as JPEG and uploads it to an AWS S3 bucket.
    The S3 object key is generated using the stream name and the current UTC timestamp.
    The frame is encoded as a JPEG image before uploading.
    Args:
        frame (numpy.ndarray): The image frame to upload.
    Raises:
        ValueError: If the frame cannot be encoded as JPEG.
    Returns:
        None
    """

    # Connect to S3
    s3 = boto3.client('s3', region_name=REGION)

    # Build object key
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    key = f"{STREAM_NAME}_{timestamp}.jpg"

    # Encode as JPEG
    success, jpeg = cv2.imencode(".jpg", frame)
    if not success:
        return ValueError("Failed to encode frame as JPEG")
    
    # Upload to S3
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=jpeg.tobytes(),
        ContentType='image/jpeg'
    )

    print(f"Uploaded frame to s3://{S3_BUCKET}/{key}")

# TODO: Test code, remove before completing DEV-26
frame = get_live_frame()
if frame is not None:
    upload_frame_to_s3(frame)
else:
    print("No frame captured")