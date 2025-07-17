import boto3
from config import S3_ENDPOINT_URL, S3_BUCKET_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY, S3_REGION

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=S3_REGION,
)

def download_image_from_s3(image_id: str) -> bytes:
    response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=image_id)
    return response["Body"].read()
