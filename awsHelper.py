import boto3


S3_BUCKET = 'granicus'
AWS_REGION = 'ap-south-1'

# AWS S3 client
s3_client = boto3.client('s3', region_name='ap-south-1')

def upload_to_s3(filepath, filename):
    with open(filepath, "rb") as f:
        s3_client.upload_fileobj(f, S3_BUCKET, filename)
    s3_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{filename}"
    return s3_url