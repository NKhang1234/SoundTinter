import boto3
from config import S3_ENDPOINT_URL, S3_BUCKET_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY, S3_REGION
import botocore.exceptions

class SongBucket:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=S3_REGION,
        )
        self.bucketName = S3_BUCKET_NAME

    def download_song_from_s3(self, image_id: str) -> bytes:
        response = self.s3.get_object(Bucket=self.bucketName, Key=image_id)
        return response["Body"].read()

    def upload_song_to_s3(self, filename: str, data: bytes, content_type: str = "audio/mpeg") -> None:
        try:
            self.s3.head_object(Bucket=self.bucketName, Key=filename)
            raise FileExistsError(f"{filename} already exists in bucket")
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                self.s3.put_object(
                    Bucket=self.bucketName,
                    Key=filename,
                    Body=data,
                    ContentType=content_type
                )
            else:
                raise