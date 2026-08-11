import queue
import threading

from agentuniverse.base.util.common_util import stream_output


def test_stream_output_waits_for_space_in_a_full_queue():
    output_stream = queue.Queue(maxsize=1)
    output_stream.put_nowait("first")

    producer = threading.Thread(
        target=lambda: stream_output(output_stream, "second")
    )
    producer.start()
    producer.join(timeout=0.05)

    assert producer.is_alive()
    assert output_stream.get_nowait() == "first"
    producer.join(timeout=1)

    assert not producer.is_alive()
    assert output_stream.get_nowait() == "second"
