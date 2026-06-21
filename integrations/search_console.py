"""
آماده برای اتصال به Google Search Console.
فعلاً placeholder است - در فاز بعدی پیاده‌سازی می‌شود.
"""
import logging

logger = logging.getLogger(__name__)


class SearchConsoleClient:
    def __init__(self, credentials: dict):
        self.credentials = credentials
        self._service = None

    def connect(self):
        """
        اتصال به Google Search Console API.
        نیاز به google-auth و google-api-python-client دارد.
        """
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            creds = Credentials(**self.credentials)
            self._service = build(
                "searchconsole", "v1", credentials=creds
            )
            return True
        except Exception as e:
            logger.error(f"Search Console connection error: {e}")
            return False

    def get_top_queries(
        self,
        site_url: str,
        days: int = 90,
        limit: int = 50
    ) -> list[dict]:
        """
        برترین کوئری‌های سایت را برمی‌گرداند.
        """
        if not self._service:
            return []
        try:
            from datetime import date, timedelta
            end_date = date.today().strftime("%Y-%m-%d")
            start_date = (
                date.today() - timedelta(days=days)
            ).strftime("%Y-%m-%d")

            body = {
                "startDate": start_date,
                "endDate": end_date,
                "dimensions": ["query"],
                "rowLimit": limit,
                "orderBy": [{"fieldName": "clicks", "sortOrder": "DESCENDING"}]
            }
            response = (
                self._service
                .searchanalytics()
                .query(siteUrl=site_url, body=body)
                .execute()
            )
            return response.get("rows", [])
        except Exception as e:
            logger.error(f"Search Console query error: {e}")
            return []

    def get_top_pages(
        self,
        site_url: str,
        days: int = 90,
        limit: int = 30
    ) -> list[dict]:
        if not self._service:
            return []
        try:
            from datetime import date, timedelta
            end_date = date.today().strftime("%Y-%m-%d")
            start_date = (
                date.today() - timedelta(days=days)
            ).strftime("%Y-%m-%d")

            body = {
                "startDate": start_date,
                "endDate": end_date,
                "dimensions": ["page"],
                "rowLimit": limit,
                "orderBy": [{"fieldName": "clicks", "sortOrder": "DESCENDING"}]
            }
            response = (
                self._service
                .searchanalytics()
                .query(siteUrl=site_url, body=body)
                .execute()
            )
            return response.get("rows", [])
        except Exception as e:
            logger.error(f"Search Console pages error: {e}")
            return []