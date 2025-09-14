import boto3
from config import S3_ENDPOINT_URL, AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, S3_BUCKET_NAME
from botocore.exceptions import ClientError

class ImageBucket:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )

        self.bucketName = S3_BUCKET_NAME
        self._create_bucket(self.bucketName)

    
    def _create_bucket(self, bucketName: str):
        try:
            self.s3.head_bucket(Bucket=bucketName)
            print(f'Bucket {self.bucketName} has already existed')
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                self.s3.create_bucket(
                    Bucket=self.bucketName,
                    CreateBucketConfiguration={
                        'LocationConstraint': AWS_REGION
                    }
                )
                print(f'Bucket {self.bucketName} is created')
            else:
                raise
                
    def check_if_exist(self, fileName: str):
        try:
            self.s3.head_object(Bucket=self.bucketName, Key=fileName)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                raise

    def upload_image_to_s3(self, fileName: str, data: bytes, contentType: str = "image/png"):
        if self.check_if_exist(fileName):
            raise FileExistsError(f"{fileName} already exists in bucket")
        else:
            self.s3.put_object(
                Bucket=self.bucketName,
                Key=fileName,
                Body=data,
                ContentType=contentType
            )
