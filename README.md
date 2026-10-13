# LocalStack S3 Security Audit

A small Python tool that audits S3 buckets for common misconfigurations, running entirely on [LocalStack](https://github.com/localstack/localstack) (no AWS account or cost).

## What it checks
| Check | Severity |
|---|---|
| Bucket policy allows `Principal: *` | CRITICAL |
| Public access block missing or incomplete | HIGH |
| Versioning not enabled | MEDIUM |

## Run it
```bash
docker run --rm -d -p 4566:4566 --name localstack localstack/localstack
pip install -r requirements.txt
python seed.py     # creates 3 demo buckets (good, half-good, bad)
python audit.py    # prints findings and writes report.json
```

## Expected result
- `demo-open-bucket`: CRITICAL + HIGH + MEDIUM
- `demo-half-secure-bucket`: MEDIUM
- `demo-secure-bucket`: OK

`audit.py` exits with code 1 on CRITICAL/HIGH findings, so it can gate a CI pipeline.

