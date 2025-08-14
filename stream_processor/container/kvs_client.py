import boto3, cv2
from datetime import datetime, timedelta, timezone
from config import REGION, STREAM_NAME

def get_data_endpoint():
    """
    Retrieves the data endpoint URL for a specified Kinesis Video Stream.
    Uses the boto3 Kinesis Video client to request the data endpoint for media retrieval
    (APIName="GET_MEDIA") for the stream defined by STREAM_NAME in the specified REGION.
    Returns:
        str: The data endpoint URL for the Kinesis Video Stream.
    Raises:
        botocore.exceptions.BotoCoreError: If there is an error communicating with AWS Kinesis Video.
        botocore.exceptions.ClientError: If the request to get the data endpoint fails.
    """

    _kvs = boto3.client("kinesisvideo", region_name=REGION)
    resp = _kvs.get_data_endpoint(
        StreamName=STREAM_NAME,
        APIName="GET_MEDIA"
    )
    return resp["DataEndpoint"]

def get_live_frame():
    """
    Retrieves a single live video frame from an AWS Kinesis Video Stream.
    This function connects to the specified Kinesis Video Stream, fetches a small chunk of media data,
    saves it temporarily as an MKV file, and extracts the first frame using OpenCV.
    Returns:
        numpy.ndarray or None: The extracted video frame as a NumPy array if successful, otherwise None.
    Raises:
        botocore.exceptions.BotoCoreError: If there is an error communicating with AWS services.
        cv2.error: If there is an error reading the MKV file with OpenCV.
    Note:
        The function creates a temporary file "temp.mkv" in the current working directory.
        Ensure that the required AWS credentials and permissions are configured.
    """
    # Find the camera stream's endpoint
    kvs = boto3.client("kinesisvideo", region_name=REGION)
    endpoint = kvs.get_data_endpoint(
        StreamName=STREAM_NAME,
        APIName="GET_MEDIA"
    )["DataEndpoint"]

    # Connect to the stream
    kvam = boto3.client("kinesis-video-media", endpoint_url=endpoint, region_name=REGION)
    stream = kvam.get_media(
        StreamName=STREAM_NAME,
        StartSelector={"StartSelectorType": "NOW"}
    )["Payload"]

    # Save a few bytes to a temp MKV file and decode
    with open("temp.mkv", "wb") as f:
        f.write(stream.read(1024*1024))  # read first MB or so

    # Use OpenCV to read the frame from the MKV file
    cap = cv2.VideoCapture("temp.mkv")
    ret, frame = cap.read()
    cap.release()

    return frame if ret else None

# TODO: Test usage, upload to S3 instead of writing a sample file
frame = get_live_frame()
if frame is not None:
    cv2.imwrite("frame.jpg", frame)
    print("Frame saved as frame.jpg")
else:
    print("No frame captured")