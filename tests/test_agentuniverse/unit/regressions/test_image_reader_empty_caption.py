from agentuniverse.agent.action.knowledge.reader.image.image_reader import ImageReader


def test_image_reader_handles_empty_caption_pipeline_result():
    reader = ImageReader()
    reader._description_pipeline = lambda image: []

    assert reader.generate_description(object()) == ""
