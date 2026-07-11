# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: google_docs_reader.py
"""Reader for Google Docs via the Google Drive export api.

The Google API client libraries are imported lazily so the reader can be
registered without the heavyweight dependencies installed. Authentication uses
a service account json path supplied through ``ext_info`` or the
``GOOGLE_SERVICE_ACCOUNT_JSON`` environment variable.
"""
import os
from typing import Dict, List, Optional

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderConfigError,
    ReaderDependencyError,
    ReaderLoadError,
    ReaderParseError,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.util.logging.logging_util import LOGGER


class GoogleDocsReader(Reader):
    """Reader for Google Docs via Google Drive export.

    Requires:
        pip install google-api-python-client google-auth google-auth-oauthlib
    Credentials:
        Use a service account JSON or OAuth credentials; pass via env or ext_info.
    """

    def _load_data(self, doc_id: str, ext_info: Optional[Dict] = None) -> List[Document]:
        """Load a Google Doc by id and return it as a Document.

        Args:
            doc_id (str): The Google Docs document id.
            ext_info (Optional[Dict]): Optional runtime configuration, supports:
                - GOOGLE_SERVICE_ACCOUNT_JSON (str): path to a service account json.

        Returns:
            List[Document]: Documents produced from the Google Doc.

        Raises:
            ReaderConfigError: If doc_id or service account config is missing.
            ReaderDependencyError: If a required optional dependency is missing.
            ReaderLoadError: If the document cannot be exported.
        """
        if not doc_id:
            raise ReaderConfigError(
                "GoogleDocsReader requires a doc_id.",
                reader_name=self.__class__.__name__,
            )
        LOGGER.debug(f"GoogleDocsReader start load doc_id={doc_id}")

        service = self._build_drive_service(ext_info)
        html = self._export_html(service, doc_id)
        text = self._html_to_text(html)

        metadata: Dict = {"source": "google_docs", "doc_id": doc_id}
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=text, metadata=metadata)]

    def _build_drive_service(self, ext_info: Optional[Dict]):
        """Build an authenticated Google Drive service client.

        Args:
            ext_info (Optional[Dict]): Optional runtime configuration.

        Returns:
            The Google Drive resource service.

        Raises:
            ReaderDependencyError: If the Google API deps are not installed.
            ReaderConfigError: If the service account json path is missing.
        """
        try:
            from google.oauth2.service_account import Credentials  # type: ignore
            from googleapiclient.discovery import build  # type: ignore
        except ImportError as e:
            raise ReaderDependencyError(
                "Install Google API deps to use GoogleDocsReader: "
                "`pip install google-api-python-client google-auth google-auth-oauthlib`",
                reader_name=self.__class__.__name__,
            ) from e

        scopes = ['https://www.googleapis.com/auth/drive.readonly']
        sa_path = (ext_info or {}).get('GOOGLE_SERVICE_ACCOUNT_JSON') or \
            os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        if not sa_path:
            raise ReaderConfigError(
                "Provide GOOGLE_SERVICE_ACCOUNT_JSON path (via ext_info or env) "
                "for service account usage.",
                reader_name=self.__class__.__name__,
            )
        creds = Credentials.from_service_account_file(sa_path, scopes=scopes)
        return build('drive', 'v3', credentials=creds)

    def _export_html(self, drive, file_id: str) -> str:
        """Export a Google Doc as html via the Drive api.

        Args:
            drive: The authenticated Google Drive service.
            file_id (str): The Google Docs document id.

        Returns:
            str: The exported html content.

        Raises:
            ReaderLoadError: If the export download fails.
        """
        from googleapiclient.http import MediaIoBaseDownload  # type: ignore
        import io
        LOGGER.debug(f"GoogleDocsReader exporting doc {file_id} as HTML")
        request = drive.files().export(fileId=file_id, mimeType='text/html')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        try:
            done = False
            while done is False:
                _, done = downloader.next_chunk()
        except Exception as e:
            raise ReaderLoadError(
                f"Failed to export Google Doc {file_id}: {e}",
                reader_name=self.__class__.__name__,
            ) from e
        return fh.getvalue().decode('utf-8', errors='ignore')

    def _html_to_text(self, html: str) -> str:
        """Convert exported Google Docs html to plain text.

        Args:
            html (str): The exported html content.

        Returns:
            str: Cleaned plain text content.

        Raises:
            ReaderDependencyError: If beautifulsoup4/lxml is not installed.
            ReaderParseError: If the html cannot be parsed.
        """
        try:
            from bs4 import BeautifulSoup  # type: ignore
        except ImportError as e:
            raise ReaderDependencyError(
                "Install beautifulsoup4 and lxml for GoogleDocsReader: "
                "`pip install beautifulsoup4 lxml`",
                reader_name=self.__class__.__name__,
            ) from e
        try:
            soup = BeautifulSoup(html, "lxml")
            for tag in soup(["script", "style", "noscript"]):
                tag.extract()
            text = soup.get_text("\n")
            return "\n".join([line.strip() for line in text.splitlines() if line.strip()])
        except Exception as e:
            raise ReaderParseError(
                f"Failed to parse Google Docs html body: {e}",
                reader_name=self.__class__.__name__,
            ) from e
