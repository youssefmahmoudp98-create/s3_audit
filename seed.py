"""Creates 3 demo buckets with different security postures."""
import json

from botocore.exceptions import ClientError

from config import s3_client

s3 = s3_client()

ALL_BLOCKED = {
    "BlockPublicAcls": True,
    "IgnorePublicAcls": True,
    "BlockPublicPolicy": True,
    "RestrictPublicBuckets": True,
}


def make_bucket(name):
    try:
        s3.create_bucket(Bucket=name)
        print(f"created {name}")
    except ClientError as e:
        if e.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
            print(f"{name} already exists")
        else:
            raise


# 1) Bad: public policy, no public access block, no versioning
make_bucket("demo-open-bucket")
public_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "PublicRead",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::demo-open-bucket/*",
    }],
}
s3.put_bucket_policy(Bucket="demo-open-bucket", Policy=json.dumps(public_policy))

# 2) Half good: public access blocked, but no versioning
make_bucket("demo-half-secure-bucket")
s3.put_public_access_block(
    Bucket="demo-half-secure-bucket",
    PublicAccessBlockConfiguration=ALL_BLOCKED,
)

# 3) Good: public access blocked and versioning enabled
make_bucket("demo-secure-bucket")
s3.put_public_access_block(
    Bucket="demo-secure-bucket",
    PublicAccessBlockConfiguration=ALL_BLOCKED,
)
s3.put_bucket_versioning(
    Bucket="demo-secure-bucket",
    VersioningConfiguration={"Status": "Enabled"},
)

print("done")
