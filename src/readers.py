import logging

from typing import Any, Optional, List, Dict

from src.base import BaseReader
from src.gateways import JiraClient

logger = logging.getLogger(__name__)


class JiraReader(BaseReader):
    """Jira reader. Reads issues and their related data."""

    def __init__(self):
        self.client = JiraClient()

    def _get_epic_data(self, epic_key: str) -> Optional[Dict[str, Any]]:
        try:
            return self.client.get_issue_data(epic_key)
        except Exception as e:
            logger.warning(f"Failed to fetch epic data for {epic_key}: {str(e)}")
            return None

    def _build_issue_path(self, issue_data: Dict[str, Any]) -> str:
        print("Building issue path")
        fields = issue_data["fields"]
        project_key = fields["project"]["key"]

        epic_key = fields.get("customfield_10014")
        if not epic_key:
            epic_key = fields.get("parent", {}).get("key") if fields.get("parent") else None

        epic_name = None
        if epic_key:
            epic_data = self._get_epic_data(epic_key)
            if epic_data:
                epic_name = epic_data["fields"]["summary"]
            else:
                epic_name = epic_key
        return f"{project_key}/{epic_name}/{issue_data['key']}"

    def _extract_sprint_info(self, sprints: List[Dict[str, Any]]) -> str:
        print("Extracting sprint info")
        if not sprints:
            return ""

        active_sprint = next((sprint for sprint in sprints if sprint.get("state") == "active"), None)
        return active_sprint["name"] if active_sprint else sprints[0]["name"]

    def _get_issue_data(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        print("Obtaining issue data")
        try:
            data = self.client.get_issue_data(issue["id"])
            fields = data["fields"]

            if not fields.get("summary"):
                return None

            path = self._build_issue_path(data)

            description_raw = fields.get("description", "")
            description_rendered = data.get("renderedFields", {}).get("description", "")

            return {
                "id": data["id"],
                "key": data["key"],
                "title": fields["summary"],
                "description": description_raw,
                "description_html": description_rendered,
                "type": fields["issuetype"]["name"],
                "project_id": fields["project"]["id"],
                "project_name": fields["project"]["name"],
                "project_key": fields["project"]["key"],
                "path": str(path),
                "watches": str(fields["watches"]["watchCount"]),
                "sprint": self._extract_sprint_info(fields.get("customfield_10020", [])),
                "priority": fields["priority"]["name"] if fields.get("priority") else "",
                "status": fields["status"]["name"],
                "labels": fields.get("labels", []),
                "assignees": [fields["assignee"]["displayName"]] if fields.get("assignee") else [],
                "creator": fields["creator"]["displayName"],
                "reporter": fields["reporter"]["displayName"],
                "subtasks": [subtask["key"] for subtask in fields.get("subtasks", [])],
                "provider": "jira",
                "user_id": "test_id",
                "provider_id": data["id"],
                "created_at": fields["created"],
                "updated_at": fields["updated"]
            }
        except Exception as e:
            logger.error(f"Error processing issue {issue.get('id')}: {str(e)}")
            return None

    def load_items(self) -> Optional[List[Dict[str, Any]]]:
        processed_issues = []

        try:
            print("Listing Issues")
            issues = self.client.list_issues()
            print(f"Issues extracted: {len(issues)}")

            for issue in issues:
                print(f"Extracting Issue Data")
                data = self._get_issue_data(issue)
                print(f"Extracted data: {data}")
                if not data:
                    continue
                processed_issues.append(data)

            logger.info(f"Successfully collected {len(processed_issues)} issues from Jira")
            return processed_issues

        except Exception as e:
            logger.error(f"Failed to load Jira issues: {str(e)}")
            return None
