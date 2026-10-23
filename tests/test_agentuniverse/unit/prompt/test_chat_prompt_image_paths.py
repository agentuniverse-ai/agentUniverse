"""Local image filenames and file URIs use different escaping rules."""

import base64
from unittest.mock import mock_open, patch

import pytest

from agentuniverse.prompt.chat_prompt import ChatPrompt

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aWQAAAABJRU5ErkJggg==")


@pytest.mark.parametrize("filename", ["plain.png", "two words.png", "chart#1.PNG", "literal%20name.png", "图表.png"])
@pytest.mark.parametrize("as_uri", [False, True])
def test_local_image_paths_keep_filename_characters(tmp_path, filename, as_uri):
    """File URIs are decoded once; plain filenames must not be URL-decoded."""
    path = tmp_path / filename
    path.write_bytes(PNG)
    prompt = ChatPrompt()
    prompt.generate_image_prompt([path.as_uri() if as_uri else str(path)])
    assert len(prompt.messages) == 1
    url = prompt.messages[0].content[0]["image_url"]["url"]
    prefix, data = url.split(",", 1)
    assert prefix == "data:image/png;base64"
    assert base64.b64decode(data) == PNG


def test_remote_image_url_and_detail_mapping_are_unchanged():
    """Remote URLs are passed through without decoding or fetching them."""
    url = "https://example.invalid/chart%20one.png?size=2#view"
    detail = {"url": url, "detail": "low"}
    prompt = ChatPrompt()
    prompt.generate_image_prompt([url, detail])
    assert [message.content[0]["image_url"] for message in prompt.messages] == [{"url": url}, detail]


def test_windows_drive_path_is_treated_as_a_local_image():
    """A drive-qualified Windows path must not be mistaken for a URL scheme."""
    prompt = ChatPrompt()
    with patch("builtins.open", mock_open(read_data=PNG)) as opened:
        prompt.generate_image_prompt([r"C:\\images\\photo.png"])

    opened.assert_called_once_with(r"C:\\images\\photo.png", "rb")
    assert len(prompt.messages) == 1
    prefix, data = prompt.messages[0].content[0]["image_url"]["url"].split(",", 1)
    assert prefix == "data:image/png;base64"
    assert base64.b64decode(data) == PNG
