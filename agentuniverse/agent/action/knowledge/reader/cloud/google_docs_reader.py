# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: google_docs_reader.py
from typing import List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class GoogleDocsReader(Reader):
    """Reader for Google Docs via Google Drive export.

    Requires:
        pip install google-api-python-client google-auth google-auth-oauthlib
    Credentials:
        Use a service account JSON or OAuth credentials; pass via env or ext_info.
    """

    def _load_data(self, doc_id: str, ext_info: Optional[Dict] = None) -> List[Document]:
        """Load a Google Docs document and return it as a list with a single Document.

        Args:
            doc_id(str): The Google Drive file id of the document.
            ext_info(Optional[Dict]): Extra information, such as credentials metadata.

        Returns:
            List[Document]: A one-element list containing the loaded document.

        Raises:
            ValueError: If doc_id is empty.
        """
        print(f"debugging: GoogleDocsReader start load doc_id={doc_id}")
        if not doc_id:
            raise ValueError("GoogleDocsReader requires doc_id")

        service = self._build_drive_service(ext_info)
        html = self._export_html(service, doc_id)
        text = self._html_to_text(html)

        metadata: Dict = {"source": "google_docs", "doc_id": doc_id}
        if ext_info:
            metadata.update(self._public_metadata(ext_info))
        return [Document(text=text, metadata=metadata)]

    @staticmethod
    def _public_metadata(ext_info: Dict) -> Dict:
        """Filter ext_info down to non-sensitive entries by removing credential-like keys.

        Args:
            ext_info(Dict): The raw extra information dict.

        Returns:
            Dict: The filtered metadata dict.
        """
        sensitive_keys = {
            "GOOGLE_SERVICE_ACCOUNT_JSON",
            "google_service_account_json",
            "service_account_json",
            "credentials",
        }
        return {key: value for key, value in ext_info.items() if key not in sensitive_keys}

    def _build_drive_service(self, ext_info: Optional[Dict]):
        """Build a Google Drive v3 service using a service account credentials file.

        Args:
            ext_info(Optional[Dict]): Extra information that may carry the service account json path.

        Returns:
            The built Drive service.

        Raises:
            ImportError: If the Google API client packages are not installed.
            EnvironmentError: If no service account json path is configured.
        """
        try:
            from google.oauth2.service_account import Credentials  # type: ignore
            from googleapiclient.discovery import build  # type: ignore
        except Exception:
            raise ImportError("Install Google API deps: `pip install google-api-python-client google-auth google-auth-oauthlib`")

        import os
        scopes = ['https://www.googleapis.com/auth/drive.readonly']
        sa_path = (ext_info or {}).get('GOOGLE_SERVICE_ACCOUNT_JSON') or os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        if not sa_path:
            raise EnvironmentError("Provide GOOGLE_SERVICE_ACCOUNT_JSON path for service account usage")
        creds = Credentials.from_service_account_file(sa_path, scopes=scopes)
        return build('drive', 'v3', credentials=creds)

    def _export_html(self, drive, file_id: str) -> str:
        """Export a Google Docs file as an HTML string through the Drive API.

        Args:
            drive: The Google Drive service.
            file_id(str): The Google Drive file id to export.

        Returns:
            str: The exported HTML content.
        """
        from googleapiclient.http import MediaIoBaseDownload  # type: ignore
        import io
        print("debugging: GoogleDocsReader exporting as HTML")
        request = drive.files().export(fileId=file_id, mimeType='text/html')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        html = fh.getvalue().decode('utf-8', errors='ignore')
        return html

    def _html_to_text(self, html: str) -> str:
        """Convert an HTML string into cleaned plain text by removing scripts, styles and empty lines.

        Args:
            html(str): The HTML content to convert.

        Returns:
            str: The extracted plain text.

        Raises:
            ImportError: If beautifulsoup4 is not installed.
        """
        try:
            from bs4 import BeautifulSoup  # type: ignore
        except Exception:
            raise ImportError("Install beautifulsoup4 and lxml for GoogleDocsReader")
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()
        text = soup.get_text("\n")
        return "\n".join([line.strip() for line in text.splitlines() if line.strip()])
