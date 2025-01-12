import os
from typing import Dict, Any, Optional, List

from src.base import BaseReader
from src.gateways import S3Client


class S3BucketReader(BaseReader):
    """S3 Bucket Reader. Reads files from an S3 bucket."""

    def __init__(
            self,
            client_config: Dict[str, Any] = None
    ):
        """Initialize S3 bucket reader.
        Args:
            client_config: Kept for backwards compatibility. Only user and token are used from this.
        """
        self.user = client_config.get("user")
        self.prefix = client_config.get("prefix")

        self.client = S3Client()

    def _build_path(self, key: str) -> str:
        return key

    def download_file(self, file_key: str, filepath: str) -> str:
        try:
            return self.client.download_file(file_key, filepath)
        except Exception as e:
            print(f"Error downloading file {file_key}: {e}")

    def load_items(self) -> Optional[List[Any]]:
        files = self.client.list_files(prefix=self.prefix)

        items = []

        print(f"Successfully collected: {len(files)} files from S3 for {self.user.id}")

        for f in files:
            if not f['Key'].endswith('/'):
                items.append({
                    "name": os.path.basename(f['Key']),
                    "provider_id": f['Key'],
                    "mimeType": self._get_mimetype(f['Key']),
                    "created_time": f['LastModified'].isoformat(),
                    "modified_time": f['LastModified'].isoformat(),
                    "size": f['Size'],
                    "path": self._build_path(f['Key']),
                    "provider": "aws_s3",
                    "parents": [{
                        "id": os.path.dirname(f['Key']),
                        "name": os.path.dirname(f['Key'])
                    }],
                    "owners": [self.user.id],
                    "shared": [self.user.id],
                })

        return items

    def _get_mimetype(self, key: str) -> str:
        import mimetypes
        mime_type, _ = mimetypes.guess_type(key)
        return mime_type or 'application/octet-stream'
