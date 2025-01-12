from typing import Dict, Any, Optional, List

import boto3
from botocore.exceptions import ClientError

from src.config import settings


class BaseAWSClient:

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize AWS client with credentials from settings.
        Args:
            config: Kept for backwards compatibility, not used. All config comes from settings.
        """
        self._config = config
        self.credentials = self._authenticate()
        self.session = self._create_session()
        self.sts_client = self.create_client('sts')

    def _authenticate(self) -> Dict[str, Any]:
        base_creds = {
            'access_key_id': settings.AWS_ACCESS_KEY_ID,
            'secret_access_key': settings.AWS_SECRET_ACCESS_KEY,
            'region': settings.AWS_REGION if hasattr(settings, 'AWS_REGION') else 'us-east-1'
        }

        if hasattr(settings, 'AWS_USE_STS') and settings.AWS_USE_STS:
            session_creds = self._get_session_token(
                duration_seconds=getattr(settings, 'AWS_SESSION_DURATION', 3600),
                serial_number=getattr(settings, 'AWS_MFA_SERIAL', None),
                token_code=getattr(settings, 'AWS_MFA_TOKEN', None)
            )
            base_creds.update(session_creds)

        return base_creds

    def _get_session_token(self, duration_seconds: int = 3600,
                           serial_number: Optional[str] = None,
                           token_code: Optional[str] = None) -> Dict[str, Any]:
        """Get temporary session credentials using AWS STS.

        Args:
            duration_seconds: How long the credentials should remain valid
            serial_number: ARN of MFA device if MFA is required
            token_code: Current MFA code if MFA is required

        Returns:
            Dictionary containing temporary credentials
        """
        try:
            sts = boto3.client(
                'sts',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION if hasattr(settings, 'AWS_REGION') else 'us-east-1'
            )

            params = {
                'DurationSeconds': duration_seconds
            }

            if serial_number and token_code:
                params.update({
                    'SerialNumber': serial_number,
                    'TokenCode': token_code
                })

            response = sts.get_session_token(**params)

            credentials = response['Credentials']
            return {
                'access_key_id': credentials['AccessKeyId'],
                'secret_access_key': credentials['SecretAccessKey'],
                'session_token': credentials['SessionToken'],
                'expiration': credentials['Expiration']
            }

        except ClientError as e:
            print(f"Failed to get session token: {str(e)}")
            raise

    def _create_session(self) -> boto3.Session:
        return boto3.Session(
            aws_access_key_id=self.credentials['access_key_id'],
            aws_secret_access_key=self.credentials['secret_access_key'],
            aws_session_token=self.credentials['session_token'],
            region_name=self.credentials['region']
        )

    def create_client(self, service_name: str) -> boto3.client:
        return self.session.client(service_name)

    def create_resource(self, service_name: str) -> boto3.resource:
        return self.session.resource(service_name)

    def get_credentials(self) -> Dict[str, str]:
        return {
            'aws_access_key_id': self.credentials['access_key_id'],
            'aws_secret_access_key': self.credentials['secret_access_key'],
            'aws_session_token': self.credentials['session_token'],
            'region': self.credentials['region']
        }


class S3Client(BaseAWSClient):

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize S3 client with bucket name from settings.
        Args:
            config: Kept for backwards compatibility, not used. All config comes from settings.
        """
        super().__init__(config)
        self.bucket_name = settings.AWS_BUCKET_NAME

        self.s3_client = self.create_client('s3')
        self.s3_resource = self.create_resource('s3')
        self.bucket = self.s3_resource.Bucket(self.bucket_name)

    def download_file(self, file_key: str, filename: str) -> str:
        try:
            self.bucket.download_file(file_key, filename)
            return filename
        except ClientError as e:
            raise ValueError(f"Error downloading file: {str(e)}")

    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        items = []
        paginator = self.s3_client.get_paginator('list_objects_v2')

        try:
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                if 'Contents' in page:
                    items.extend(page['Contents'])
        except ClientError as e:
            raise ValueError(f"Error listing files: {str(e)}")

        return items

    def get_file_metadata(self, file_key: str) -> Dict[str, Any]:
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            return {
                'ContentLength': response.get('ContentLength', 0),
                'LastModified': response.get('LastModified'),
                'ContentType': response.get('ContentType'),
                'Metadata': response.get('Metadata', {})
            }
        except ClientError as e:
            raise ValueError(f"Error getting file metadata: {str(e)}")