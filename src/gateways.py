import json
import logging
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

from typing import Dict, Any, List
from urllib.parse import urljoin, parse_qs, urlparse, urlencode

from src.config import settings

logger = logging.getLogger(__name__)


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)

        OAuthCallbackHandler.auth_code = query_components.get('code', [None])[0]

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Authentication successful! You can close this window.")

        self.server.stop = True


class StoppableHTTPServer(HTTPServer):
    def serve_forever(self):
        self.stop = False
        while not self.stop:
            self.handle_request()


class JiraClient:
    def __init__(self):
        """Initialize JiraClient with OAuth authentication."""
        self._domain = settings.ATLASSIAN_DOMAIN
        self._base_url = f"https://{self._domain}"
        self._client_id = settings.ATLASSIAN_CLIENT_ID
        self._client_secret = settings.ATLASSIAN_CLIENT_SECRET
        self._redirect_uri = settings.ATLASSIAN_REDIRECT_URI
        self._access_token = None
        self._api_version = "3"

    def _get_authorization_code(self) -> str:
        """Get authorization code via browser."""
        # Authorization URL
        auth_url = "https://auth.atlassian.com/authorize"
        params = {
            'audience': 'api.atlassian.com',
            'client_id': self._client_id,
            'scope': 'read:jira-work read:jira-user',
            'redirect_uri': self._redirect_uri,
            'response_type': 'code',
            'prompt': 'consent'
        }

        # Start local server to receive callback
        server = StoppableHTTPServer(('localhost', 8080), OAuthCallbackHandler)

        # Open browser for authentication
        auth_url_with_params = f"{auth_url}?{urlencode(params)}"
        logger.info(f"Opening browser for authentication: {auth_url_with_params}")
        webbrowser.open(auth_url_with_params)

        # Wait for callback
        server.serve_forever()

        if not hasattr(OAuthCallbackHandler, 'auth_code'):
            raise Exception("Failed to get authorization code")

        return OAuthCallbackHandler.auth_code

    def _get_access_token(self) -> str:
        """Get OAuth access token."""
        if not self._access_token:
            # Get authorization code
            auth_code = self._get_authorization_code()

            # Exchange code for token
            token_url = "https://auth.atlassian.com/oauth/token"
            data = {
                "grant_type": "authorization_code",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "code": auth_code,
                "redirect_uri": self._redirect_uri
            }

            response = requests.post(token_url, json=data)
            if response.status_code != 200:
                raise Exception(f"Failed to get access token: {response.text}")

            token_data = response.json()
            self._access_token = token_data["access_token"]

            # Save token for reuse
            self._save_token(token_data)

        return self._access_token

    def _save_token(self, token_data: Dict[str, Any]):
        """Save token data to file."""
        with open('.token_cache.json', 'w') as f:
            json.dump(token_data, f)

    def _load_token(self) -> bool:
        """Load token data from file."""
        try:
            with open('.token_cache.json', 'r') as f:
                token_data = json.load(f)
                self._access_token = token_data["access_token"]
                return True
        except:
            return False

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the Jira API."""
        if not self._access_token:
            self._load_token()

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._get_access_token()}"
        }

        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        try:
            url = urljoin(self._base_url, endpoint)
            logger.info(f"Making request to: {url}")

            response = requests.request(
                method,
                url,
                headers=headers,
                **kwargs
            )

            if response.status_code >= 400:
                logger.error(f"Response status: {response.status_code}")
                logger.error(f"Response body: {response.text}")
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")

            return response.json()

        except Exception as e:
            raise Exception(f"Jira API error: {str(e)}") from e

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all accessible Jira projects."""
        try:
            endpoint = f"/rest/api/{self._api_version}/project"
            response = self._request("GET", endpoint)
            print(response)
            projects = response if isinstance(response, list) else []

            for project in projects:
                logger.info(f"Project Key: {project.get('key')}, Name: {project.get('name')}")

            return projects
        except Exception as e:
            logger.error(f"Error listing projects: {str(e)}")
            return []

    def list_issues(self) -> List[Dict[str, Any]]:
        """List Jira issues with pagination."""
        try:
            issues = []
            start_at = 0
            batch_size = 100

            while True:
                endpoint = f"/rest/api/{self._api_version}/search"

                jql_query = (
                    "project = MON"
                )

                query = {
                    "jql": jql_query,
                    "startAt": start_at,
                    "maxResults": batch_size,
                    "fields": [
                        "key",
                        "project",
                        "summary",
                        "description",
                        "issuetype",
                        "priority",
                        "status",
                        "assignee",
                        "creator",
                        "reporter",
                        "created",
                        "updated",
                        "customfield_10014",
                        "customfield_10020"
                    ]
                }

                response = self._request("POST", endpoint, json=query)
                batch_issues = response.get("issues", [])

                if not batch_issues:
                    break

                issues.extend(batch_issues)
                start_at += batch_size

                if len(batch_issues) < batch_size:
                    break

                logger.info(f"Retrieved {len(issues)} issues so far...")

            logger.info(f"Total issues retrieved: {len(issues)}")
            return issues

        except Exception as e:
            logger.error(f"Error listing issues: {str(e)}")
            return []

    def get_issue_data(self, issue_id: str) -> Dict[str, Any]:
        endpoint = f"/rest/api/{self._api_version}/issue/{issue_id}"
        params = {
            "expand": "renderedFields,names,schema,transitions,operations,editmeta,changelog"
        }
        return self._request("GET", endpoint, params=params)

