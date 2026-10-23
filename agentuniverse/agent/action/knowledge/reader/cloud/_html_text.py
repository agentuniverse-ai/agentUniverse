"""Shared text extraction for parsed cloud-document HTML."""
from typing import Any


_BLOCK_TAGS = (
    'address', 'article', 'aside', 'blockquote', 'body', 'caption', 'dd', 'details',
    'dialog', 'div', 'dl', 'dt', 'fieldset', 'figcaption', 'figure', 'footer',
    'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hgroup', 'hr',
    'li', 'main', 'nav', 'ol', 'p', 'pre', 'section', 'summary', 'table',
    'tbody', 'td', 'tfoot', 'th', 'thead', 'tr', 'ul',
)


def extract_cloud_html_text(soup: Any) -> str:
    """Extract text, keeping inline fragments together and block breaks apart.

    Mutates the caller's freshly parsed tree. As in the cloud readers' existing
    output, blank lines are omitted and each remaining line is stripped.
    BeautifulSoup remains a lazy dependency owned by the reader entry points.
    """
    for tag in soup(['script', 'style', 'noscript']):
        tag.extract()
    for tag in soup.find_all('br'):
        tag.replace_with('\n')
    for tag in soup.find_all(_BLOCK_TAGS):
        tag.insert_before('\n')
        tag.insert_after('\n')
    return '\n'.join(line.strip() for line in soup.get_text().splitlines()
                     if line.strip())
