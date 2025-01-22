import logging
import requests

from typing import Dict, Any, List
from urllib.parse import urljoin

from src.config import settings

logger = logging.getLogger(__name__)


class JiraClient:
    def __init__(self):
        """
        Initialize JiraClient with basic authentication.

        config should contain:
        - domain: Your Jira domain (e.g., 'your-domain.atlassian.net')
        - email: Your Atlassian account email
        - api_token: API token generated from Atlassian account settings
        """
        self._domain = settings.ATLASSIAN_DOMAIN
        self._base_url = f"https://{self._domain}"
        self._auth = (settings.ATLASSIAN_EMAIL, settings.ATLASSIAN_API_TOKEN)
        self._api_version = "3"

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the Jira API."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        try:
            url = urljoin(self._base_url, endpoint)
            response = requests.request(
                method,
                url,
                auth=self._auth,
                headers=headers,
                **kwargs
            )

            if response.status_code >= 400:
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")

            return response.json()

        except Exception as e:
            raise Exception(f"Jira API error: {str(e)}") from e

    def list_issues(self) -> List[Dict[str, Any]]:
        """List Jira issues with pagination."""
        try:
            issues = []
            start_at = 0
            batch_size = 100

            while True:
                endpoint = f"/rest/api/{self._api_version}/search"
                query = {
                    "jql": "order by created DESC",
                    "startAt": start_at,
                    "maxResults": batch_size,
                    "fields": ["key", "project"]
                }

                response = self._request("POST", endpoint, json=query)
                batch_issues = response.get("issues", [])

                if not batch_issues:
                    break

                issues.extend(batch_issues)
                start_at += batch_size

                if len(batch_issues) < batch_size:
                    break

            return issues

        except Exception as e:
            logger.error(f"Error listing issues: {str(e)}")
            return []

    def get_issue_data(self, issue_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific issue."""
        endpoint = f"/rest/api/{self._api_version}/issue/{issue_id}"
        params = {
            "expand": "renderedFields,names,schema,transitions,operations,editmeta,changelog"
        }
        return self._request("GET", endpoint, params=params)


# Example usage:
if __name__ == "__main__":
    config = {
        "domain": "your-domain.atlassian.net",
        "email": "your-email@example.com",
        "api_token": "your-api-token"
    }

    client = JiraClient()

    # List issues
    issues = client.list_issues()
    print(f"Found {len(issues)} issues")

    # Get specific issue
    if issues:
        issue_key = issues[0]["key"]
        issue_data = client.get_issue_data(issue_key)
        print(f"Retrieved data for issue {issue_key}")
