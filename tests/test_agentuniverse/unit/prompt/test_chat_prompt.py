from agentuniverse.prompt.chat_prompt import ChatPrompt


def test_generate_image_prompt_uses_standard_jpeg_mime_type(tmp_path):
    image_path = tmp_path / "photo.jpg"
    image_path.write_bytes(b"jpeg data")
    prompt = ChatPrompt()

    prompt.generate_image_prompt([str(image_path)])

    image_url = prompt.messages[-1].content[0]["image_url"]["url"]
    assert image_url.startswith("data:image/jpeg;base64,")
