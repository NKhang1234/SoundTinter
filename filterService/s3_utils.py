import boto3
from botocore.exceptions import ClientError
from config import S3_ENDPOINT_URL, AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION
import logging

logger = logging.getLogger(__name__)

class ImageBucket:
    def __init__(self, bucketName):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION,
        )
        self.bucketName = bucketName
        self._create_bucket(self.bucketName)

    def _create_bucket(self, bucketName: str):
        try:
            self.s3.head_bucket(Bucket=bucketName)
            logger.warning(f'Bucket {self.bucketName} has already existed')
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                self.s3.create_bucket(
                    Bucket=self.bucketName,
                    CreateBucketConfiguration={
                        'LocationConstraint': AWS_REGION
                    }
                )
                logger.info(f'Bucket {self.bucketName} is created')
            else:
                raise

    def download_image_from_s3(self, image_id: str) -> bytes:
        response = self.s3.get_object(Bucket=self.bucketName, Key=image_id)
        return response["Body"].read()

    def upload_image_to_s3(self, image_id: str, image_bytes: bytes):
        self.s3.put_object(Bucket=self.bucketName, Key=image_id, Body=image_bytes)
        logger.info(f'Image {image_id} uploaded to bucket {self.bucketName}')


   

