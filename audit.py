"""Audits every S3 bucket for 3 common misconfigurations and writes report.json.

Exit code is 1 if any CRITICAL or HIGH finding exists, so it can run in CI.
"""
import json
import sys

from botocore.exceptions import ClientError

from config import s3_client

PAB_KEYS = [
    "BlockPublicAcls",
    "IgnorePublicAcls",
    "BlockPublicPolicy",
    "RestrictPublicBuckets",
]


def check_public_access_block(s3, bucket):
    try:
        cfg = s3.get_public_access_block(Bucket=bucket)["PublicAccessBlockConfiguration"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
            return "HIGH", "Public access block is not configured"
        raise
    missing = [k for k in PAB_KEYS if not cfg.get(k)]
    if missing:
        return "HIGH", f"Public access block missing: {', '.join(missing)}"
    return None


def check_policy(s3, bucket):
    try:
        policy = json.loads(s3.get_bucket_policy(Bucket=bucket)["Policy"])
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucketPolicy":
            return None
        raise
    for statement in policy.get("Statement", []):
        principal = statement.get("Principal")
        is_public = principal == "*" or (
            isinstance(principal, dict) and principal.get("AWS") == "*"
        )
        if statement.get("Effect") == "Allow" and is_public:
            return "CRITICAL", "Bucket policy allows everyone (Principal: *)"
    return None


def check_versioning(s3, bucket):
    status = s3.get_bucket_versioning(Bucket=bucket).get("Status")
    if status != "Enabled":
        return "MEDIUM", "Versioning is not enabled"
    return None


CHECKS = [check_public_access_block, check_policy, check_versioning]


def main():
    s3 = s3_client()
    report = []

    for bucket in s3.list_buckets()["Buckets"]:
        name = bucket["Name"]
        findings = []
        for check in CHECKS:
            result = check(s3, name)
            if result:
                findings.append({"severity": result[0], "issue": result[1]})
        report.append({"bucket": name, "findings": findings})

    for entry in report:
        status = "OK" if not entry["findings"] else "ISSUES"
        print(f"\n[{status}] {entry['bucket']}")
        for f in entry["findings"]:
            print(f"   - {f['severity']}: {f['issue']}")

    with open("report.json", "w") as fh:
        json.dump(report, fh, indent=2)
    print("\nSaved report.json")

    serious = any(
        f["severity"] in ("CRITICAL", "HIGH")
        for entry in report
        for f in entry["findings"]
    )
    sys.exit(1 if serious else 0)


if __name__ == "__main__":
    main()
