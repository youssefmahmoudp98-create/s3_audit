import boto3

LOCALSTACK_URL = "http://localhost:4566"


def s3_client():
    """S3 client pointed at LocalStack. The credentials are fake on purpose."""
    return boto3.client(
        "s3",
        endpoint_url=LOCALSTACK_URL,
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )
