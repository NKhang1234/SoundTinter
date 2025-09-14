import boto3
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, DYNAMODB_ENDPOINT_URL, DYNAMODB_TABLE_NAME, DYNAMODB_PARTITION_KEY, DYNAMODB_SORT_KEY
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

class FeatureDynamo:
    def __init__(self):
        # Connect to DynamoDB Local
        self.__dynamodb = boto3.resource(
            'dynamodb',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            endpoint_url=DYNAMODB_ENDPOINT_URL
        )
        self.__table_name = DYNAMODB_TABLE_NAME
        self.__partition_key = DYNAMODB_PARTITION_KEY
        self.__sort_key = DYNAMODB_SORT_KEY

        # Create or get table
        self.__table = self._create_or_get_table()


    def _create_or_get_table(self) -> None:
        try:
            table = self.__dynamodb.Table(self.__table_name)
            table.load()  # will throw if table doesn't exist
            print(f"Table {self.__table_name} already exists")
            return table
        except ClientError as err:
            try:
                table = self.__dynamodb.create_table(
                    TableName=self.__table_name,
                    KeySchema=[
                        {"AttributeName": self.__partition_key, "KeyType": "HASH"},
                        {"AttributeName": self.__sort_key, "KeyType": "RANGE"}
                    ],
                    AttributeDefinitions=[
                        {"AttributeName": self.__partition_key, "AttributeType": "S"},
                        {"AttributeName": self.__sort_key, "AttributeType": "S"},
                    ],
                    BillingMode="PAY_PER_REQUEST"
                )
                table.wait_until_exists()
                return table

            except ClientError as err:
                print(
                    f"Couldn't create table {self.__table_name}. "
                    f"Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}"
                )
                raise
    
    def add_item(self, item: dict) -> dict:
        try:
            return self.__table.put_item(Item=item)
        except ClientError as err:
            print(
                    f"Couldn't add item {item} to table {self.__table_name}. "
                    f"Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}"
                )
            raise

    def get_item(self, partition_key: str, sort_key: str) -> dict:
        try:
            res = self.__table.get_item(
                Key={self.__partition_key: partition_key, self.__sort_key: sort_key}
            )
            return res.get("Item", None)
        except ClientError as err:
            print(
                    f"Couldn't get item {partition_key} - {sort_key} from table {self.__table_name}. " 
                    f"Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}"
                )
            raise

    def update_item(self, item: dict) -> dict:
        try:
            return self.__table.put_item(Item=item)
        except ClientError as err:
            print(
                    f"Couldn't update item {item} to table {self.__table_name}. "
                    f"Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}"
                )
            raise

    def query_item(self, partition_key: str) -> list[dict]:
        try:
            res = self.__table.query(KeyConditionExpression=Key(self.__partition_key).eq(partition_key))
            return res["Items"]
        except ClientError as err:
            print(
                    f"Couldn't query item by {partition_key} on table {self.__table_name}. " 
                    f"Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}"
                )
            raise

    def delete_item(self, partition_key: str, sort_key: str) -> dict:
        try:
            return self.__table.delete_item(
                Key={self.__partition_key: partition_key, self.__sort_key: sort_key}
            )
        except ClientError as err:
            print(
                f"Couldn't delete item {partition_key}-{sort_key} from table {self.__table_name}. "
                f"Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}"
            )
            raise