import boto3
from config import REGION, STREAM_NAME

_kvs = boto3.client("kinesisvideo", region_name=REGION)

def get_data_endpoint():
    resp = _kvs.get_data_endpoint(
        StreamName=STREAM_NAME,
        APIName="GET_MEDIA"
    )
    return resp["DataEndpoint"]