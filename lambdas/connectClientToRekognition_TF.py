import json
import boto3
import base64
import os
import uuid
from io import BytesIO


def lambda_handler(event, context):
    try:
        # Parse the incoming JSON payload
        body = json.loads(event.get('body', '{}'))
        image_data = base64.b64decode(body['image'])
    except Exception as e:
        error_msg = f"Error parsing payload: {str(e)}"
        print(error_msg)
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid payload', 'details': error_msg})
        }
   
    # Initialize the Rekognition client
    rekognition = boto3.client('rekognition', region_name='us-east-1')


    try:
        # Call the detect_protective_equipment API with SummarizationAttributes
        rek_response = rekognition.detect_protective_equipment(Image={'Bytes': image_data})
    except Exception as e:
        error_msg = f"Rekognition call error: {str(e)}"
        print(error_msg)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Rekognition error', 'details': error_msg})
        }
   
    # Filter response for head covering PPE detections on the HEAD body part
    head_coverings = []
    for person in rek_response.get('Persons', []):
        for body_part in person.get('BodyParts',[]):
            if body_part.get('Name') == 'HEAD':
                for equipment in body_part.get('EquipmentDetections', []):
                    if equipment.get('Type') == 'HEAD_COVER':
                        head_coverings.append({
                            'Type': equipment.get('Type'),
                            'Confidence': equipment.get('Confidence'),
                            'BoundingBox': equipment.get('BoundingBox')
                        })
   
    result = {
        'HeadCoverings': head_coverings,            # All found head coverings
        'FullResponse': rek_response,               # Full JSON output from Rekognition
    }


    # Save the result to s3
    s3 = boto3.client('s3')
    bucket_name = os.environ['BUCKET_NAME']
    if not bucket_name:
        error_msg = "BUCKET_NAME environment variable not set"
        print(error_msg)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Configuration error', 'details': error_msg})
        }


    # Generate a unique key for the S3 object
    file_key = f"rekognition_results/{uuid.uuid4()}.json"


    # Attempt to put the object in S3
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=json.dumps(result),
            ContentType='application/json'
        )
    except Exception as e:
        error_msg = f"Error saving to S3: {str(e)}"
        print(error_msg)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'S3 error', 'details': error_msg})
        }
   
    # Save the result along with the S3 file location (for returning purposes)
    response_payload = {
        'result': result,
        's3_file': file_key
    }


    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(response_payload)
    }