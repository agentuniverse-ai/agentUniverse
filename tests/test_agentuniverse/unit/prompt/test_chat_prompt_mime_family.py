#!/usr/bin/env python3

from agentuniverse.prompt.chat_prompt import ChatPrompt


def test_generate_image_prompt_uses_tiff_mime_type(tmp_path):
    image_path = tmp_path / "scan.tif"
    image_path.write_bytes(b"II*\x00")
    prompt = ChatPrompt()

    prompt.generate_image_prompt([str(image_path)])

    image_url = prompt.messages[-1].content[0]["image_url"]["url"]
    assert image_url.startswith("data:image/tiff;base64,")


def test_generate_image_prompt_accepts_long_tiff_spelling(tmp_path):
    image_path = tmp_path / "scan.tiff"
    image_path.write_bytes(b"II*\x00")
    prompt = ChatPrompt()

    prompt.generate_image_prompt([str(image_path)])

    image_url = prompt.messages[-1].content[0]["image_url"]["url"]
    assert image_url.startswith("data:image/tiff;base64,")


def test_generate_image_prompt_uses_svg_mime_type(tmp_path):
    image_path = tmp_path / "icon.svg"
    image_path.write_bytes(b"<svg/>")
    prompt = ChatPrompt()

    prompt.generate_image_prompt([str(image_path)])

    image_url = prompt.messages[-1].content[0]["image_url"]["url"]
    assert image_url.startswith("data:image/svg+xml;base64,")


def test_generate_image_prompt_uses_x_icon_mime_type(tmp_path):
    image_path = tmp_path / "favicon.ico"
    image_path.write_bytes(b"AA")
    prompt = ChatPrompt()

    prompt.generate_image_prompt([str(image_path)])

    image_url = prompt.messages[-1].content[0]["image_url"]["url"]
    assert image_url.startswith("data:image/x-icon;base64,")


def test_generate_image_prompt_maps_jfif_to_jpeg(tmp_path):
    image_path = tmp_path / "map.jfif"
    image_path.write_bytes(b"data")
    prompt = ChatPrompt()

    prompt.generate_image_prompt([str(image_path)])

    image_url = prompt.messages[-1].content[0]["image_url"]["url"]
    assert image_url.startswith("data:image/jpeg;base64,")


def test_generate_image_prompt_keeps_canonical_passthrough(tmp_path):
    checks = [
        ("pic.png", "image/png"),
        ("ani.gif", "image/gif"),
        ("shot.webp", "image/webp"),
        ("deep.bmp", "image/bmp"),
    ]
    for name, mime in checks:
        image_path = tmp_path / name
        image_path.write_bytes(b"data")
        prompt = ChatPrompt()

        prompt.generate_image_prompt([str(image_path)])

        image_url = prompt.messages[-1].content[0]["image_url"]["url"]
        assert image_url.startswith("data:%s;base64," % mime), name


def test_generate_image_prompt_skips_unknown_extension(tmp_path):
    image_path = tmp_path / "notes.heic"
    image_path.write_bytes(b"data")
    prompt = ChatPrompt()

    prompt.generate_image_prompt([str(image_path)])

    assert prompt.messages == []
