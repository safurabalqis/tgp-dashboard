import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def get_bedrock_client(region=None):
    return boto3.client(
        "bedrock-runtime",
        region_name=region or os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
