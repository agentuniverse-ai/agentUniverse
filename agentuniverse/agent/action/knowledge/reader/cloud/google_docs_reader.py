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
        print(f"debugging: GoogleDocsReader start load doc_id={doc_id}")
        if not doc_id:
            raise ValueError("GoogleDocsReader requires doc_id")

        service = self._build_drive_service(ext_info)
        html = self._export_html(service, doc_id)
        text = self._html_to_text(html)

        metadata: Dict = {"source": "google_docs", "doc_id": doc_id}
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=text, metadata=metadata)]

    def _build_drive_service(self, ext_info: Optional[Dict]):
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
        try:
            from bs4 import BeautifulSoup  # type: ignore
        except Exception:
            raise ImportError("Install beautifulsoup4 and lxml for GoogleDocsReader")
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()
        text = soup.get_text("\n")
        return "\n".join([line.strip() for line in text.splitlines() if line.strip()])
