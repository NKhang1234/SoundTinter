import boto3
from config import S3_ENDPOINT_URL, S3_BUCKET_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY, S3_REGION

class ImageBucket:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=S3_REGION,
        )
        self.bucketName = S3_BUCKET_NAME

    def download_image_from_s3(self, image_id: str) -> bytes:
        response = self.s3.get_object(Bucket=self.bucketName, Key=image_id)
        return response["Body"].read()

