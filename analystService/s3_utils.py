import boto3
from config import S3_ENDPOINT_URL, S3_BUCKET_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION
import botocore.exceptions
import logging

logger = logging.getLogger(__name__)

class SongBucket:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION,
        )
        self.bucketName = S3_BUCKET_NAME
        self._create_bucket(self.bucketName)
    
    def _create_bucket(self, bucketName: str):
        try:
            self.s3.head_bucket(Bucket=bucketName)
            logger.warning(f'Bucket {self.bucketName} has already existed')
        except botocore.exceptions.ClientError as e:
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
    
    def check_if_exist(self, fileName: str):
        try:
            self.s3.head_object(Bucket=self.bucketName, Key=fileName)
            return True
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                raise
            
    def download_song_from_s3(self, image_id: str) -> bytes:
        response = self.s3.get_object(Bucket=self.bucketName, Key=image_id)
        return response["Body"].read()

    def upload_song_to_s3(self, fileName: str, data: bytes, contentType: str = "audio/mpeg") -> None:
        if self.check_if_exist(fileName):
            raise FileExistsError(f"{fileName} already exists in bucket")
        else:
            self.s3.put_object(
                Bucket=self.bucketName,
                Key=fileName,
                Body=data,
                ContentType=contentType
            )
