# scripts/remediate_secrets.py
import os
import requests
from typing import List, Dict

class SecretRemediator:
    """Secret Scanning 알림 자동 처리"""

    def __init__(self, github_token: str, repo: str):
        self.token = github_token
        self.repo = repo
        self.api_base = "https://api.github.com"

    def get_secret_alerts(self, state: str = "open") -> List[Dict]:
        """Secret Scanning 알림 조회"""
        url = f"{self.api_base}/repos/{self.repo}/secret-scanning/alerts"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        params = {"state": state}

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def revoke_aws_key(self, access_key_id: str) -> bool:
        """AWS 액세스 키 자동 폐기"""
        import boto3

        try:
            iam = boto3.client('iam')
            # 액세스 키 비활성화
            iam.update_access_key(
                AccessKeyId=access_key_id,
                Status='Inactive'
            )
            # 알림 전송
            self._send_slack_alert(
                f"🚨 AWS Access Key 자동 폐기: {access_key_id}"
            )
            return True
        except Exception as e:
            print(f"Failed to revoke key: {e}")
            return False

    def close_alert(self, alert_number: int, resolution: str = "revoked"):
        """알림 종료"""
        url = f"{self.api_base}/repos/{self.repo}/secret-scanning/alerts/{alert_number}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        }
        data = {
            "state": "resolved",
            "resolution": resolution  # revoked, false_positive, used_in_tests
        }

        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()

    def _send_slack_alert(self, message: str):
        """Slack 알림 전송"""
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        if webhook_url:
            requests.post(webhook_url, json={"text": message})

# 사용 예시
if __name__ == "__main__":
    remediator = SecretRemediator(
        github_token=os.getenv('GITHUB_TOKEN'),
        repo="myorg/myrepo"
    )

    alerts = remediator.get_secret_alerts()
    for alert in alerts:
        if alert['secret_type'] == 'aws_access_key_id':
            key_id = alert['secret']
            if remediator.revoke_aws_key(key_id):
                remediator.close_alert(alert['number'], resolution='revoked')
