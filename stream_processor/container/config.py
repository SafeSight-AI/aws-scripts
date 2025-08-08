import boto3

ssm = boto3.client('ssm')

def get_ssm_parameter(name, with_decryption=False):
    response = ssm.get_parameter(
        Name=name,
        WithDecryption=with_decryption
    )
    return response['Parameter']['Value']

# Load parameters from SSM
S3_BUCKET = get_ssm_parameter('/stream-processor/s3_bucket_name')
INTERVAL_SECONDS = int(get_ssm_parameter('/stream-processor/interval_seconds'))
REGION = get_ssm_parameter('/stream-processor/region')

STREAM_NAME = "office-wifi" # TODO NOT SCALABLE, find a better way to find active streams

print(f"S3_BUCKET: {S3_BUCKET}")
print(f"INTERVAL_SECONDS: {INTERVAL_SECONDS}")
print(f"REGION: {REGION}")
print(f"STREAM_NAME: {STREAM_NAME}")
