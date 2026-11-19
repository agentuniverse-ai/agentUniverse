"""Greedy word wrapping: deterministic known-answer vectors (auext)."""

def _ref_wrap_words(case):
    """Greedy word wrapping: pack words into lines of at most ``width`` chars.

    Words longer than the width occupy their own line; empty text yields no
    lines; non-positive width returns the text unsplit.
    """
    text, width = case
    words = text.split()
    if not words:
        return []
    if width <= 0:
        return [text]
    lines = []
    cur = words[0]
    for w in words[1:]:
        if len(cur) + 1 + len(w) <= width:
            cur = cur + " " + w
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines

_CASES = [
    (
        ("round 201: the quick brown fox jumps over the lazy dog", 4),
        ["round", "201:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 201: the quick brown fox jumps over the lazy dog", 8),
        ["round", "201: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 201: the quick brown fox jumps over the lazy dog", 12),
        ["round 201:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 201: the quick brown fox jumps over the lazy dog", 16),
        ["round 201: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 201: the quick brown fox jumps over the lazy dog", 24),
        ["round 201: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 201: the quick brown fox jumps over the lazy dog", 32),
        ["round 201: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 201: agentuniverse is a framework for multi agents", 4),
        ["round", "201:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 201: agentuniverse is a framework for multi agents", 8),
        ["round", "201:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 201: agentuniverse is a framework for multi agents", 12),
        ["round 201:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 201: agentuniverse is a framework for multi agents", 16),
        ["round 201:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 201: agentuniverse is a framework for multi agents", 24),
        ["round 201: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 201: agentuniverse is a framework for multi agents", 32),
        ["round 201: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 201: knowledge stored as vectors enables retrieval", 4),
        ["round", "201:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 201: knowledge stored as vectors enables retrieval", 8),
        ["round", "201:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 201: knowledge stored as vectors enables retrieval", 12),
        ["round 201:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 201: knowledge stored as vectors enables retrieval", 16),
        ["round 201:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 201: knowledge stored as vectors enables retrieval", 24),
        ["round 201: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 201: knowledge stored as vectors enables retrieval", 32),
        ["round 201: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 201: the processor reads the record then stops", 4),
        ["round", "201:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 201: the processor reads the record then stops", 8),
        ["round", "201: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 201: the processor reads the record then stops", 12),
        ["round 201:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 201: the processor reads the record then stops", 16),
        ["round 201: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 201: the processor reads the record then stops", 24),
        ["round 201: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 201: the processor reads the record then stops", 32),
        ["round 201: the processor reads", "the record then stops"],
    ),
    (
        ("round 201: a worker pulls the next task from the queue", 4),
        ["round", "201:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 201: a worker pulls the next task from the queue", 8),
        ["round", "201: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 201: a worker pulls the next task from the queue", 12),
        ["round 201: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 201: a worker pulls the next task from the queue", 16),
        ["round 201: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 201: a worker pulls the next task from the queue", 24),
        ["round 201: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 201: a worker pulls the next task from the queue", 32),
        ["round 201: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 201: signals travel through the network layer", 4),
        ["round", "201:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 201: signals travel through the network layer", 8),
        ["round", "201:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 201: signals travel through the network layer", 12),
        ["round 201:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 201: signals travel through the network layer", 16),
        ["round 201:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 201: signals travel through the network layer", 24),
        ["round 201: signals", "travel through the", "network layer"],
    ),
    (
        ("round 201: signals travel through the network layer", 32),
        ["round 201: signals travel", "through the network layer"],
    ),
    (
        ("round 201: the gateway routes each request by policy", 4),
        ["round", "201:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 201: the gateway routes each request by policy", 8),
        ["round", "201: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 201: the gateway routes each request by policy", 12),
        ["round 201:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 201: the gateway routes each request by policy", 16),
        ["round 201: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 201: the gateway routes each request by policy", 24),
        ["round 201: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 201: the gateway routes each request by policy", 32),
        ["round 201: the gateway routes", "each request by policy"],
    ),
    (
        ("round 201: memory grows until the buffer is full", 4),
        ["round", "201:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 201: memory grows until the buffer is full", 8),
        ["round", "201:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 201: memory grows until the buffer is full", 12),
        ["round 201:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 201: memory grows until the buffer is full", 16),
        ["round 201:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 201: memory grows until the buffer is full", 24), ["round 201: memory grows", "until the buffer is full"]),
    (("round 201: memory grows until the buffer is full", 32), ["round 201: memory grows until", "the buffer is full"]),
    (
        ("round 201: the cluster mirrors every packet twice", 4),
        ["round", "201:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 201: the cluster mirrors every packet twice", 8),
        ["round", "201: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 201: the cluster mirrors every packet twice", 12),
        ["round 201:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 201: the cluster mirrors every packet twice", 16),
        ["round 201: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 201: the cluster mirrors every packet twice", 24),
        ["round 201: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 201: the cluster mirrors every packet twice", 32),
        ["round 201: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 201: ranking uses tokens learned from the corpus", 4),
        ["round", "201:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 201: ranking uses tokens learned from the corpus", 8),
        ["round", "201:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 201: ranking uses tokens learned from the corpus", 12),
        ["round 201:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 201: ranking uses tokens learned from the corpus", 16),
        ["round 201:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 201: ranking uses tokens learned from the corpus", 24),
        ["round 201: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 201: ranking uses tokens learned from the corpus", 32),
        ["round 201: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 201: a long session ends when the candle dies", 4),
        ["round", "201:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 201: a long session ends when the candle dies", 8),
        ["round", "201: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 201: a long session ends when the candle dies", 12),
        ["round 201: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 201: a long session ends when the candle dies", 16),
        ["round 201: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 201: a long session ends when the candle dies", 24),
        ["round 201: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 201: a long session ends when the candle dies", 32),
        ["round 201: a long session ends", "when the candle dies"],
    ),
    (
        ("round 201: encode the prompt then map the result", 4),
        ["round", "201:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 201: encode the prompt then map the result", 8),
        ["round", "201:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 201: encode the prompt then map the result", 12),
        ["round 201:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 201: encode the prompt then map the result", 16),
        ["round 201:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 201: encode the prompt then map the result", 24),
        ["round 201: encode the", "prompt then map the", "result"],
    ),
    (("round 201: encode the prompt then map the result", 32), ["round 201: encode the prompt", "then map the result"]),
    (
        ("round 201: the kernel wakes the worker at dawn", 4),
        ["round", "201:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 201: the kernel wakes the worker at dawn", 8),
        ["round", "201: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 201: the kernel wakes the worker at dawn", 12),
        ["round 201:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 201: the kernel wakes the worker at dawn", 16), ["round 201: the", "kernel wakes the", "worker at dawn"]),
    (("round 201: the kernel wakes the worker at dawn", 24), ["round 201: the kernel", "wakes the worker at dawn"]),
    (("round 201: the kernel wakes the worker at dawn", 32), ["round 201: the kernel wakes the", "worker at dawn"]),
    (
        ("round 201: service latency drops after the patch", 4),
        ["round", "201:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 201: service latency drops after the patch", 8),
        ["round", "201:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 201: service latency drops after the patch", 12),
        ["round 201:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 201: service latency drops after the patch", 16),
        ["round 201:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 201: service latency drops after the patch", 24),
        ["round 201: service", "latency drops after the", "patch"],
    ),
    (("round 201: service latency drops after the patch", 32), ["round 201: service latency drops", "after the patch"]),
    (
        ("round 201: the library caches every vector it sees", 4),
        ["round", "201:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 201: the library caches every vector it sees", 8),
        ["round", "201: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 201: the library caches every vector it sees", 12),
        ["round 201:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 201: the library caches every vector it sees", 16),
        ["round 201: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 201: the library caches every vector it sees", 24),
        ["round 201: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 201: the library caches every vector it sees", 32),
        ["round 201: the library caches", "every vector it sees"],
    ),
    (
        ("round 201: agents argue then the debate resolves", 4),
        ["round", "201:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 201: agents argue then the debate resolves", 8),
        ["round", "201:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 201: agents argue then the debate resolves", 12),
        ["round 201:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 201: agents argue then the debate resolves", 16),
        ["round 201:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 201: agents argue then the debate resolves", 24), ["round 201: agents argue", "then the debate resolves"]),
    (("round 201: agents argue then the debate resolves", 32), ["round 201: agents argue then the", "debate resolves"]),
    (
        ("round 201: the filter keeps only strong matches", 4),
        ["round", "201:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 201: the filter keeps only strong matches", 8),
        ["round", "201: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 201: the filter keeps only strong matches", 12),
        ["round 201:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 201: the filter keeps only strong matches", 16),
        ["round 201: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 201: the filter keeps only strong matches", 24),
        ["round 201: the filter", "keeps only strong", "matches"],
    ),
    (("round 201: the filter keeps only strong matches", 32), ["round 201: the filter keeps only", "strong matches"]),
    (
        ("round 201: the model answers with a short reply", 4),
        ["round", "201:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 201: the model answers with a short reply", 8),
        ["round", "201: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 201: the model answers with a short reply", 12),
        ["round 201:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 201: the model answers with a short reply", 16),
        ["round 201: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 201: the model answers with a short reply", 24),
        ["round 201: the model", "answers with a short", "reply"],
    ),
    (("round 201: the model answers with a short reply", 32), ["round 201: the model answers", "with a short reply"]),
    (
        ("round 201: the recorder stores the reasoning trace", 4),
        ["round", "201:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 201: the recorder stores the reasoning trace", 8),
        ["round", "201: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 201: the recorder stores the reasoning trace", 12),
        ["round 201:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 201: the recorder stores the reasoning trace", 16),
        ["round 201: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 201: the recorder stores the reasoning trace", 24),
        ["round 201: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 201: the recorder stores the reasoning trace", 32),
        ["round 201: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 201: the angel watches the processor run", 4),
        ["round", "201:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 201: the angel watches the processor run", 8),
        ["round", "201: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 201: the angel watches the processor run", 12),
        ["round 201:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 201: the angel watches the processor run", 16),
        ["round 201: the", "angel watches", "the processor", "run"],
    ),
    (("round 201: the angel watches the processor run", 24), ["round 201: the angel", "watches the processor", "run"]),
    (("round 201: the angel watches the processor run", 32), ["round 201: the angel watches the", "processor run"]),
    (
        ("round 201: angle of the vector decides the match", 4),
        ["round", "201:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 201: angle of the vector decides the match", 8),
        ["round", "201:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 201: angle of the vector decides the match", 12),
        ["round 201:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 201: angle of the vector decides the match", 16),
        ["round 201: angle", "of the vector", "decides the", "match"],
    ),
    (("round 201: angle of the vector decides the match", 24), ["round 201: angle of the", "vector decides the match"]),
    (("round 201: angle of the vector decides the match", 32), ["round 201: angle of the vector", "decides the match"]),
    (
        ("round 201: the candle burns twice as long at night", 4),
        ["round", "201:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 201: the candle burns twice as long at night", 8),
        ["round", "201: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 201: the candle burns twice as long at night", 12),
        ["round 201:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 201: the candle burns twice as long at night", 16),
        ["round 201: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 201: the candle burns twice as long at night", 24),
        ["round 201: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 201: the candle burns twice as long at night", 32),
        ["round 201: the candle burns", "twice as long at night"],
    ),
    (
        ("round 201: a mirror of the universe in one line", 4),
        ["round", "201:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 201: a mirror of the universe in one line", 8),
        ["round", "201: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 201: a mirror of the universe in one line", 12),
        ["round 201: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 201: a mirror of the universe in one line", 16),
        ["round 201: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 201: a mirror of the universe in one line", 24), ["round 201: a mirror of", "the universe in one line"]),
    (("round 201: a mirror of the universe in one line", 32), ["round 201: a mirror of the", "universe in one line"]),
    (
        ("round 201: the queue drains before the storm", 4),
        ["round", "201:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 201: the queue drains before the storm", 8),
        ["round", "201: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 201: the queue drains before the storm", 12),
        ["round 201:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 201: the queue drains before the storm", 16), ["round 201: the", "queue drains", "before the storm"]),
    (("round 201: the queue drains before the storm", 24), ["round 201: the queue", "drains before the storm"]),
    (("round 201: the queue drains before the storm", 32), ["round 201: the queue drains", "before the storm"]),
    (
        ("kitten201 sitting201 agent201 angle201 universe201 memory201", 6),
        ["kitten201", "sitting201", "agent201", "angle201", "universe201", "memory201"],
    ),
    (
        ("kitten201 sitting201 agent201 angle201 universe201 memory201", 10),
        ["kitten201", "sitting201", "agent201", "angle201", "universe201", "memory201"],
    ),
    (
        ("kitten201 sitting201 agent201 angle201 universe201 memory201", 18),
        ["kitten201", "sitting201", "agent201 angle201", "universe201", "memory201"],
    ),
    (
        ("kitten201 sitting201 agent201 angle201 universe201 memory201", 28),
        ["kitten201 sitting201", "agent201 angle201", "universe201 memory201"],
    ),
    (
        ("sitting201 agent201 angle201 universe201 memory201 stream201", 6),
        ["sitting201", "agent201", "angle201", "universe201", "memory201", "stream201"],
    ),
    (
        ("sitting201 agent201 angle201 universe201 memory201 stream201", 10),
        ["sitting201", "agent201", "angle201", "universe201", "memory201", "stream201"],
    ),
    (
        ("sitting201 agent201 angle201 universe201 memory201 stream201", 18),
        ["sitting201", "agent201 angle201", "universe201", "memory201", "stream201"],
    ),
    (
        ("sitting201 agent201 angle201 universe201 memory201 stream201", 28),
        ["sitting201 agent201 angle201", "universe201 memory201", "stream201"],
    ),
    (
        ("agent201 angle201 universe201 memory201 stream201 context201", 6),
        ["agent201", "angle201", "universe201", "memory201", "stream201", "context201"],
    ),
    (
        ("agent201 angle201 universe201 memory201 stream201 context201", 10),
        ["agent201", "angle201", "universe201", "memory201", "stream201", "context201"],
    ),
    (
        ("agent201 angle201 universe201 memory201 stream201 context201", 18),
        ["agent201 angle201", "universe201", "memory201", "stream201", "context201"],
    ),
    (
        ("agent201 angle201 universe201 memory201 stream201 context201", 28),
        ["agent201 angle201", "universe201 memory201", "stream201 context201"],
    ),
    (
        ("angle201 universe201 memory201 stream201 context201 knowledge201", 6),
        ["angle201", "universe201", "memory201", "stream201", "context201", "knowledge201"],
    ),
    (
        ("angle201 universe201 memory201 stream201 context201 knowledge201", 10),
        ["angle201", "universe201", "memory201", "stream201", "context201", "knowledge201"],
    ),
    (
        ("angle201 universe201 memory201 stream201 context201 knowledge201", 18),
        ["angle201", "universe201", "memory201", "stream201", "context201", "knowledge201"],
    ),
    (
        ("angle201 universe201 memory201 stream201 context201 knowledge201", 28),
        ["angle201 universe201", "memory201 stream201", "context201 knowledge201"],
    ),
    (
        ("universe201 memory201 stream201 context201 knowledge201 vector201", 6),
        ["universe201", "memory201", "stream201", "context201", "knowledge201", "vector201"],
    ),
    (
        ("universe201 memory201 stream201 context201 knowledge201 vector201", 10),
        ["universe201", "memory201", "stream201", "context201", "knowledge201", "vector201"],
    ),
    (
        ("universe201 memory201 stream201 context201 knowledge201 vector201", 18),
        ["universe201", "memory201", "stream201", "context201", "knowledge201", "vector201"],
    ),
    (
        ("universe201 memory201 stream201 context201 knowledge201 vector201", 28),
        ["universe201 memory201", "stream201 context201", "knowledge201 vector201"],
    ),
    (
        ("memory201 stream201 context201 knowledge201 vector201 processor201", 6),
        ["memory201", "stream201", "context201", "knowledge201", "vector201", "processor201"],
    ),
    (
        ("memory201 stream201 context201 knowledge201 vector201 processor201", 10),
        ["memory201", "stream201", "context201", "knowledge201", "vector201", "processor201"],
    ),
    (
        ("memory201 stream201 context201 knowledge201 vector201 processor201", 18),
        ["memory201", "stream201", "context201", "knowledge201", "vector201", "processor201"],
    ),
    (
        ("memory201 stream201 context201 knowledge201 vector201 processor201", 28),
        ["memory201 stream201", "context201 knowledge201", "vector201 processor201"],
    ),
    (
        ("stream201 context201 knowledge201 vector201 processor201 reasoning201", 6),
        ["stream201", "context201", "knowledge201", "vector201", "processor201", "reasoning201"],
    ),
    (
        ("stream201 context201 knowledge201 vector201 processor201 reasoning201", 10),
        ["stream201", "context201", "knowledge201", "vector201", "processor201", "reasoning201"],
    ),
    (
        ("stream201 context201 knowledge201 vector201 processor201 reasoning201", 18),
        ["stream201", "context201", "knowledge201", "vector201", "processor201", "reasoning201"],
    ),
    (
        ("stream201 context201 knowledge201 vector201 processor201 reasoning201", 28),
        ["stream201 context201", "knowledge201 vector201", "processor201 reasoning201"],
    ),
    (
        ("context201 knowledge201 vector201 processor201 reasoning201 machine201", 6),
        ["context201", "knowledge201", "vector201", "processor201", "reasoning201", "machine201"],
    ),
    (
        ("context201 knowledge201 vector201 processor201 reasoning201 machine201", 10),
        ["context201", "knowledge201", "vector201", "processor201", "reasoning201", "machine201"],
    ),
    (
        ("context201 knowledge201 vector201 processor201 reasoning201 machine201", 18),
        ["context201", "knowledge201", "vector201", "processor201", "reasoning201", "machine201"],
    ),
    (
        ("context201 knowledge201 vector201 processor201 reasoning201 machine201", 28),
        ["context201 knowledge201", "vector201 processor201", "reasoning201 machine201"],
    ),
    (
        ("knowledge201 vector201 processor201 reasoning201 machine201 learning201", 6),
        ["knowledge201", "vector201", "processor201", "reasoning201", "machine201", "learning201"],
    ),
    (
        ("knowledge201 vector201 processor201 reasoning201 machine201 learning201", 10),
        ["knowledge201", "vector201", "processor201", "reasoning201", "machine201", "learning201"],
    ),
    (
        ("knowledge201 vector201 processor201 reasoning201 machine201 learning201", 18),
        ["knowledge201", "vector201", "processor201", "reasoning201", "machine201", "learning201"],
    ),
    (
        ("knowledge201 vector201 processor201 reasoning201 machine201 learning201", 28),
        ["knowledge201 vector201", "processor201 reasoning201", "machine201 learning201"],
    ),
    (
        ("vector201 processor201 reasoning201 machine201 learning201 model201", 6),
        ["vector201", "processor201", "reasoning201", "machine201", "learning201", "model201"],
    ),
    (
        ("vector201 processor201 reasoning201 machine201 learning201 model201", 10),
        ["vector201", "processor201", "reasoning201", "machine201", "learning201", "model201"],
    ),
    (
        ("vector201 processor201 reasoning201 machine201 learning201 model201", 18),
        ["vector201", "processor201", "reasoning201", "machine201", "learning201", "model201"],
    ),
    (
        ("vector201 processor201 reasoning201 machine201 learning201 model201", 28),
        ["vector201 processor201", "reasoning201 machine201", "learning201 model201"],
    ),
    (
        ("processor201 reasoning201 machine201 learning201 model201 token201", 6),
        ["processor201", "reasoning201", "machine201", "learning201", "model201", "token201"],
    ),
    (
        ("processor201 reasoning201 machine201 learning201 model201 token201", 10),
        ["processor201", "reasoning201", "machine201", "learning201", "model201", "token201"],
    ),
    (
        ("processor201 reasoning201 machine201 learning201 model201 token201", 18),
        ["processor201", "reasoning201", "machine201", "learning201", "model201 token201"],
    ),
    (
        ("processor201 reasoning201 machine201 learning201 model201 token201", 28),
        ["processor201 reasoning201", "machine201 learning201", "model201 token201"],
    ),
    (
        ("reasoning201 machine201 learning201 model201 token201 prompt201", 6),
        ["reasoning201", "machine201", "learning201", "model201", "token201", "prompt201"],
    ),
    (
        ("reasoning201 machine201 learning201 model201 token201 prompt201", 10),
        ["reasoning201", "machine201", "learning201", "model201", "token201", "prompt201"],
    ),
    (
        ("reasoning201 machine201 learning201 model201 token201 prompt201", 18),
        ["reasoning201", "machine201", "learning201", "model201 token201", "prompt201"],
    ),
    (
        ("reasoning201 machine201 learning201 model201 token201 prompt201", 28),
        ["reasoning201 machine201", "learning201 model201", "token201 prompt201"],
    ),
    (
        ("machine201 learning201 model201 token201 prompt201 session201", 6),
        ["machine201", "learning201", "model201", "token201", "prompt201", "session201"],
    ),
    (
        ("machine201 learning201 model201 token201 prompt201 session201", 10),
        ["machine201", "learning201", "model201", "token201", "prompt201", "session201"],
    ),
    (
        ("machine201 learning201 model201 token201 prompt201 session201", 18),
        ["machine201", "learning201", "model201 token201", "prompt201", "session201"],
    ),
    (
        ("machine201 learning201 model201 token201 prompt201 session201", 28),
        ["machine201 learning201", "model201 token201 prompt201", "session201"],
    ),
    (
        ("learning201 model201 token201 prompt201 session201 library201", 6),
        ["learning201", "model201", "token201", "prompt201", "session201", "library201"],
    ),
    (
        ("learning201 model201 token201 prompt201 session201 library201", 10),
        ["learning201", "model201", "token201", "prompt201", "session201", "library201"],
    ),
    (
        ("learning201 model201 token201 prompt201 session201 library201", 18),
        ["learning201", "model201 token201", "prompt201", "session201", "library201"],
    ),
    (
        ("learning201 model201 token201 prompt201 session201 library201", 28),
        ["learning201 model201", "token201 prompt201", "session201 library201"],
    ),
    (
        ("model201 token201 prompt201 session201 library201 service201", 6),
        ["model201", "token201", "prompt201", "session201", "library201", "service201"],
    ),
    (
        ("model201 token201 prompt201 session201 library201 service201", 10),
        ["model201", "token201", "prompt201", "session201", "library201", "service201"],
    ),
    (
        ("model201 token201 prompt201 session201 library201 service201", 18),
        ["model201 token201", "prompt201", "session201", "library201", "service201"],
    ),
    (
        ("model201 token201 prompt201 session201 library201 service201", 28),
        ["model201 token201 prompt201", "session201 library201", "service201"],
    ),
    (
        ("token201 prompt201 session201 library201 service201 gateway201", 6),
        ["token201", "prompt201", "session201", "library201", "service201", "gateway201"],
    ),
    (
        ("token201 prompt201 session201 library201 service201 gateway201", 10),
        ["token201", "prompt201", "session201", "library201", "service201", "gateway201"],
    ),
    (
        ("token201 prompt201 session201 library201 service201 gateway201", 18),
        ["token201 prompt201", "session201", "library201", "service201", "gateway201"],
    ),
    (
        ("token201 prompt201 session201 library201 service201 gateway201", 28),
        ["token201 prompt201", "session201 library201", "service201 gateway201"],
    ),
    (
        ("prompt201 session201 library201 service201 gateway201 storage201", 6),
        ["prompt201", "session201", "library201", "service201", "gateway201", "storage201"],
    ),
    (
        ("prompt201 session201 library201 service201 gateway201 storage201", 10),
        ["prompt201", "session201", "library201", "service201", "gateway201", "storage201"],
    ),
    (
        ("prompt201 session201 library201 service201 gateway201 storage201", 18),
        ["prompt201", "session201", "library201", "service201", "gateway201", "storage201"],
    ),
    (
        ("prompt201 session201 library201 service201 gateway201 storage201", 28),
        ["prompt201 session201", "library201 service201", "gateway201 storage201"],
    ),
    (
        ("session201 library201 service201 gateway201 storage201 network201", 6),
        ["session201", "library201", "service201", "gateway201", "storage201", "network201"],
    ),
    (
        ("session201 library201 service201 gateway201 storage201 network201", 10),
        ["session201", "library201", "service201", "gateway201", "storage201", "network201"],
    ),
    (
        ("session201 library201 service201 gateway201 storage201 network201", 18),
        ["session201", "library201", "service201", "gateway201", "storage201", "network201"],
    ),
    (
        ("session201 library201 service201 gateway201 storage201 network201", 28),
        ["session201 library201", "service201 gateway201", "storage201 network201"],
    ),
    (
        ("library201 service201 gateway201 storage201 network201 latency201", 6),
        ["library201", "service201", "gateway201", "storage201", "network201", "latency201"],
    ),
    (
        ("library201 service201 gateway201 storage201 network201 latency201", 10),
        ["library201", "service201", "gateway201", "storage201", "network201", "latency201"],
    ),
    (
        ("library201 service201 gateway201 storage201 network201 latency201", 18),
        ["library201", "service201", "gateway201", "storage201", "network201", "latency201"],
    ),
    (
        ("library201 service201 gateway201 storage201 network201 latency201", 28),
        ["library201 service201", "gateway201 storage201", "network201 latency201"],
    ),
    (
        ("service201 gateway201 storage201 network201 latency201 buffer201", 6),
        ["service201", "gateway201", "storage201", "network201", "latency201", "buffer201"],
    ),
    (
        ("service201 gateway201 storage201 network201 latency201 buffer201", 10),
        ["service201", "gateway201", "storage201", "network201", "latency201", "buffer201"],
    ),
    (
        ("service201 gateway201 storage201 network201 latency201 buffer201", 18),
        ["service201", "gateway201", "storage201", "network201", "latency201", "buffer201"],
    ),
    (
        ("service201 gateway201 storage201 network201 latency201 buffer201", 28),
        ["service201 gateway201", "storage201 network201", "latency201 buffer201"],
    ),
    (
        ("gateway201 storage201 network201 latency201 buffer201 queue201", 6),
        ["gateway201", "storage201", "network201", "latency201", "buffer201", "queue201"],
    ),
    (
        ("gateway201 storage201 network201 latency201 buffer201 queue201", 10),
        ["gateway201", "storage201", "network201", "latency201", "buffer201", "queue201"],
    ),
    (
        ("gateway201 storage201 network201 latency201 buffer201 queue201", 18),
        ["gateway201", "storage201", "network201", "latency201", "buffer201 queue201"],
    ),
    (
        ("gateway201 storage201 network201 latency201 buffer201 queue201", 28),
        ["gateway201 storage201", "network201 latency201", "buffer201 queue201"],
    ),
    (
        ("storage201 network201 latency201 buffer201 queue201 worker201", 6),
        ["storage201", "network201", "latency201", "buffer201", "queue201", "worker201"],
    ),
    (
        ("storage201 network201 latency201 buffer201 queue201 worker201", 10),
        ["storage201", "network201", "latency201", "buffer201", "queue201", "worker201"],
    ),
    (
        ("storage201 network201 latency201 buffer201 queue201 worker201", 18),
        ["storage201", "network201", "latency201", "buffer201 queue201", "worker201"],
    ),
    (
        ("storage201 network201 latency201 buffer201 queue201 worker201", 28),
        ["storage201 network201", "latency201 buffer201", "queue201 worker201"],
    ),
    (
        ("network201 latency201 buffer201 queue201 worker201 kernel201", 6),
        ["network201", "latency201", "buffer201", "queue201", "worker201", "kernel201"],
    ),
    (
        ("network201 latency201 buffer201 queue201 worker201 kernel201", 10),
        ["network201", "latency201", "buffer201", "queue201", "worker201", "kernel201"],
    ),
    (
        ("network201 latency201 buffer201 queue201 worker201 kernel201", 18),
        ["network201", "latency201", "buffer201 queue201", "worker201", "kernel201"],
    ),
    (
        ("network201 latency201 buffer201 queue201 worker201 kernel201", 28),
        ["network201 latency201", "buffer201 queue201 worker201", "kernel201"],
    ),
    (
        ("latency201 buffer201 queue201 worker201 kernel201 signal201", 6),
        ["latency201", "buffer201", "queue201", "worker201", "kernel201", "signal201"],
    ),
    (
        ("latency201 buffer201 queue201 worker201 kernel201 signal201", 10),
        ["latency201", "buffer201", "queue201", "worker201", "kernel201", "signal201"],
    ),
    (
        ("latency201 buffer201 queue201 worker201 kernel201 signal201", 18),
        ["latency201", "buffer201 queue201", "worker201", "kernel201", "signal201"],
    ),
    (
        ("latency201 buffer201 queue201 worker201 kernel201 signal201", 28),
        ["latency201 buffer201", "queue201 worker201 kernel201", "signal201"],
    ),
    (
        ("buffer201 queue201 worker201 kernel201 signal201 packet201", 6),
        ["buffer201", "queue201", "worker201", "kernel201", "signal201", "packet201"],
    ),
    (
        ("buffer201 queue201 worker201 kernel201 signal201 packet201", 10),
        ["buffer201", "queue201", "worker201", "kernel201", "signal201", "packet201"],
    ),
    (
        ("buffer201 queue201 worker201 kernel201 signal201 packet201", 18),
        ["buffer201 queue201", "worker201", "kernel201", "signal201", "packet201"],
    ),
    (
        ("buffer201 queue201 worker201 kernel201 signal201 packet201", 28),
        ["buffer201 queue201 worker201", "kernel201 signal201", "packet201"],
    ),
    (
        ("queue201 worker201 kernel201 signal201 packet201 router201", 6),
        ["queue201", "worker201", "kernel201", "signal201", "packet201", "router201"],
    ),
    (
        ("queue201 worker201 kernel201 signal201 packet201 router201", 10),
        ["queue201", "worker201", "kernel201", "signal201", "packet201", "router201"],
    ),
    (
        ("queue201 worker201 kernel201 signal201 packet201 router201", 18),
        ["queue201 worker201", "kernel201", "signal201", "packet201", "router201"],
    ),
    (
        ("queue201 worker201 kernel201 signal201 packet201 router201", 28),
        ["queue201 worker201 kernel201", "signal201 packet201", "router201"],
    ),
    (
        ("worker201 kernel201 signal201 packet201 router201 cluster201", 6),
        ["worker201", "kernel201", "signal201", "packet201", "router201", "cluster201"],
    ),
    (
        ("worker201 kernel201 signal201 packet201 router201 cluster201", 10),
        ["worker201", "kernel201", "signal201", "packet201", "router201", "cluster201"],
    ),
    (
        ("worker201 kernel201 signal201 packet201 router201 cluster201", 18),
        ["worker201", "kernel201", "signal201", "packet201", "router201", "cluster201"],
    ),
    (
        ("worker201 kernel201 signal201 packet201 router201 cluster201", 28),
        ["worker201 kernel201", "signal201 packet201", "router201 cluster201"],
    ),
    (
        ("kernel201 signal201 packet201 router201 cluster201 mirror201", 6),
        ["kernel201", "signal201", "packet201", "router201", "cluster201", "mirror201"],
    ),
    (
        ("kernel201 signal201 packet201 router201 cluster201 mirror201", 10),
        ["kernel201", "signal201", "packet201", "router201", "cluster201", "mirror201"],
    ),
    (
        ("kernel201 signal201 packet201 router201 cluster201 mirror201", 18),
        ["kernel201", "signal201", "packet201", "router201", "cluster201", "mirror201"],
    ),
    (
        ("kernel201 signal201 packet201 router201 cluster201 mirror201", 28),
        ["kernel201 signal201", "packet201 router201", "cluster201 mirror201"],
    ),
    (
        ("signal201 packet201 router201 cluster201 mirror201 filter201", 6),
        ["signal201", "packet201", "router201", "cluster201", "mirror201", "filter201"],
    ),
    (
        ("signal201 packet201 router201 cluster201 mirror201 filter201", 10),
        ["signal201", "packet201", "router201", "cluster201", "mirror201", "filter201"],
    ),
    (
        ("signal201 packet201 router201 cluster201 mirror201 filter201", 18),
        ["signal201", "packet201", "router201", "cluster201", "mirror201", "filter201"],
    ),
    (
        ("signal201 packet201 router201 cluster201 mirror201 filter201", 28),
        ["signal201 packet201", "router201 cluster201", "mirror201 filter201"],
    ),
    (
        ("packet201 router201 cluster201 mirror201 filter201 ranking201", 6),
        ["packet201", "router201", "cluster201", "mirror201", "filter201", "ranking201"],
    ),
    (
        ("packet201 router201 cluster201 mirror201 filter201 ranking201", 10),
        ["packet201", "router201", "cluster201", "mirror201", "filter201", "ranking201"],
    ),
    (
        ("packet201 router201 cluster201 mirror201 filter201 ranking201", 18),
        ["packet201", "router201", "cluster201", "mirror201", "filter201", "ranking201"],
    ),
    (
        ("packet201 router201 cluster201 mirror201 filter201 ranking201", 28),
        ["packet201 router201", "cluster201 mirror201", "filter201 ranking201"],
    ),
    (
        ("router201 cluster201 mirror201 filter201 ranking201 encoding201", 6),
        ["router201", "cluster201", "mirror201", "filter201", "ranking201", "encoding201"],
    ),
    (
        ("router201 cluster201 mirror201 filter201 ranking201 encoding201", 10),
        ["router201", "cluster201", "mirror201", "filter201", "ranking201", "encoding201"],
    ),
    (
        ("router201 cluster201 mirror201 filter201 ranking201 encoding201", 18),
        ["router201", "cluster201", "mirror201", "filter201", "ranking201", "encoding201"],
    ),
    (
        ("router201 cluster201 mirror201 filter201 ranking201 encoding201", 28),
        ["router201 cluster201", "mirror201 filter201", "ranking201 encoding201"],
    ),
    (
        ("cluster201 mirror201 filter201 ranking201 encoding201 mapping201", 6),
        ["cluster201", "mirror201", "filter201", "ranking201", "encoding201", "mapping201"],
    ),
    (
        ("cluster201 mirror201 filter201 ranking201 encoding201 mapping201", 10),
        ["cluster201", "mirror201", "filter201", "ranking201", "encoding201", "mapping201"],
    ),
    (
        ("cluster201 mirror201 filter201 ranking201 encoding201 mapping201", 18),
        ["cluster201", "mirror201", "filter201", "ranking201", "encoding201", "mapping201"],
    ),
    (
        ("cluster201 mirror201 filter201 ranking201 encoding201 mapping201", 28),
        ["cluster201 mirror201", "filter201 ranking201", "encoding201 mapping201"],
    ),
    (
        ("mirror201 filter201 ranking201 encoding201 mapping201 record201", 6),
        ["mirror201", "filter201", "ranking201", "encoding201", "mapping201", "record201"],
    ),
    (
        ("mirror201 filter201 ranking201 encoding201 mapping201 record201", 10),
        ["mirror201", "filter201", "ranking201", "encoding201", "mapping201", "record201"],
    ),
    (
        ("mirror201 filter201 ranking201 encoding201 mapping201 record201", 18),
        ["mirror201", "filter201", "ranking201", "encoding201", "mapping201", "record201"],
    ),
    (
        ("mirror201 filter201 ranking201 encoding201 mapping201 record201", 28),
        ["mirror201 filter201", "ranking201 encoding201", "mapping201 record201"],
    ),
    (
        ("filter201 ranking201 encoding201 mapping201 record201 candle201", 6),
        ["filter201", "ranking201", "encoding201", "mapping201", "record201", "candle201"],
    ),
    (
        ("filter201 ranking201 encoding201 mapping201 record201 candle201", 10),
        ["filter201", "ranking201", "encoding201", "mapping201", "record201", "candle201"],
    ),
    (
        ("filter201 ranking201 encoding201 mapping201 record201 candle201", 18),
        ["filter201", "ranking201", "encoding201", "mapping201", "record201", "candle201"],
    ),
    (
        ("filter201 ranking201 encoding201 mapping201 record201 candle201", 28),
        ["filter201 ranking201", "encoding201 mapping201", "record201 candle201"],
    ),
    (
        ("ranking201 encoding201 mapping201 record201 candle201 thread201", 6),
        ["ranking201", "encoding201", "mapping201", "record201", "candle201", "thread201"],
    ),
    (
        ("ranking201 encoding201 mapping201 record201 candle201 thread201", 10),
        ["ranking201", "encoding201", "mapping201", "record201", "candle201", "thread201"],
    ),
    (
        ("ranking201 encoding201 mapping201 record201 candle201 thread201", 18),
        ["ranking201", "encoding201", "mapping201", "record201", "candle201", "thread201"],
    ),
    (
        ("ranking201 encoding201 mapping201 record201 candle201 thread201", 28),
        ["ranking201 encoding201", "mapping201 record201", "candle201 thread201"],
    ),
    (("", 10), []),
    (("single", 1), ["single"]),
    (("verylongwordwithnospace", 5), ["verylongwordwithnospace"]),
]

_EXPECTED_COUNT = 287

def test_vector_count_frozen():
    """The vector table size is part of the frozen contract."""
    assert len(_CASES) == _EXPECTED_COUNT

def test_vectors_000():
    """Known-answer vectors 0..119."""
    for case, expected in _CASES[0:120]:
        assert _ref_wrap_words(case) == expected

def test_vectors_120():
    """Known-answer vectors 120..239."""
    for case, expected in _CASES[120:240]:
        assert _ref_wrap_words(case) == expected

def test_vectors_240():
    """Known-answer vectors 240..286."""
    for case, expected in _CASES[240:287]:
        assert _ref_wrap_words(case) == expected

def test_repeat_head_stable():
    """Head vectors return identical results on repeated calls."""
    for case, expected in _CASES[:64]:
        assert _ref_wrap_words(case) == expected
        assert _ref_wrap_words(case) == expected

def test_repeat_tail_stable():
    """Tail vectors return identical results on repeated calls."""
    for case, expected in _CASES[-64:]:
        assert _ref_wrap_words(case) == expected
        assert _ref_wrap_words(case) == expected
