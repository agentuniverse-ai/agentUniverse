"""IPv4 redaction must not consume four parts of a longer numeric token."""
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.sensitive_data_redactor import (
    SensitiveDataRedactor,
)
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize("token", [
    "1.2.3.4.5",
    "0.1.2.3.4",
    "255.255.255.255.0",
    "999.1.2.3.4",
    "1.2.3.4.999",
    "1.2.3.4.5.6",
    "1.2.3.4.5.6.7.8",
])
def test_longer_dotted_numeric_token_is_not_partially_redacted(token):
    text = "Version " + token + " is documented."
    source = Document(text=text, metadata={"source": "release.txt"})

    output = SensitiveDataRedactor(entities=["ip_address"]).process_docs([source])

    assert output[0] is source
    assert source.text == text
    assert source.metadata == {"source": "release.txt", "redaction_summary": {}}


@pytest.mark.parametrize("text,expected", [
    ("Server 192.0.2.1 ready", "Server [REDACTED] ready"),
    ("Server 192.0.2.1. Next sentence.", "Server [REDACTED]. Next sentence."),
    ("(192.0.2.1)", "([REDACTED])"),
    ("Connect 192.0.2.1:443", "Connect [REDACTED]:443"),
    ("Subnet 192.0.2.1/24", "Subnet [REDACTED]/24"),
    ("Server .192.0.2.1.", "Server .[REDACTED]."),
])
def test_standalone_addresses_keep_existing_punctuation_handling(text, expected):
    source = Document(text=text)

    output = SensitiveDataRedactor(entities=["ip_address"]).process_docs([source])

    assert output[0].text == expected
    assert output[0].metadata["redaction_summary"] == {"ip_address": 1}


def test_long_numeric_token_does_not_suppress_a_separate_address():
    source = Document(text="Version 1.2.3.4.5; server 192.0.2.1. Next 9.8.7.6.5.")

    SensitiveDataRedactor(entities=["ip_address"]).process_docs([source])

    assert source.text == "Version 1.2.3.4.5; server [REDACTED]. Next 9.8.7.6.5."
    assert source.metadata["redaction_summary"] == {"ip_address": 1}


@pytest.mark.parametrize("text", [
    "Invalid 999.999.999.999",
    "Invalid 1.2.3.256",
    "Incomplete 1.2.3",
    "Identifier x192.0.2.1",
])
def test_existing_invalid_and_embedded_address_controls_remain_unredacted(text):
    source = Document(text=text)

    SensitiveDataRedactor(entities=["ip_address"]).process_docs([source])

    assert source.text == text
    assert source.metadata["redaction_summary"] == {}


def test_disabled_ip_entity_and_custom_replacement_contract():
    text = "Version 1.2.3.4.5; server 192.0.2.1."
    untouched = Document(text=text)
    SensitiveDataRedactor(entities=[]).process_docs([untouched])
    assert untouched.text == text
    assert untouched.metadata["redaction_summary"] == {}

    source = Document(text=text)
    SensitiveDataRedactor(entities=["ip_address"], replacement="[IP]", log_key=None).process_docs([source])
    assert source.text == "Version 1.2.3.4.5; server [IP]."
    assert source.metadata is None
