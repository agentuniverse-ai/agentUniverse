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
        ("round 180: the quick brown fox jumps over the lazy dog", 4),
        ["round", "180:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 180: the quick brown fox jumps over the lazy dog", 8),
        ["round", "180: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 180: the quick brown fox jumps over the lazy dog", 12),
        ["round 180:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 180: the quick brown fox jumps over the lazy dog", 16),
        ["round 180: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 180: the quick brown fox jumps over the lazy dog", 24),
        ["round 180: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 180: the quick brown fox jumps over the lazy dog", 32),
        ["round 180: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 180: agentuniverse is a framework for multi agents", 4),
        ["round", "180:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 180: agentuniverse is a framework for multi agents", 8),
        ["round", "180:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 180: agentuniverse is a framework for multi agents", 12),
        ["round 180:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 180: agentuniverse is a framework for multi agents", 16),
        ["round 180:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 180: agentuniverse is a framework for multi agents", 24),
        ["round 180: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 180: agentuniverse is a framework for multi agents", 32),
        ["round 180: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 180: knowledge stored as vectors enables retrieval", 4),
        ["round", "180:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 180: knowledge stored as vectors enables retrieval", 8),
        ["round", "180:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 180: knowledge stored as vectors enables retrieval", 12),
        ["round 180:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 180: knowledge stored as vectors enables retrieval", 16),
        ["round 180:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 180: knowledge stored as vectors enables retrieval", 24),
        ["round 180: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 180: knowledge stored as vectors enables retrieval", 32),
        ["round 180: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 180: the processor reads the record then stops", 4),
        ["round", "180:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 180: the processor reads the record then stops", 8),
        ["round", "180: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 180: the processor reads the record then stops", 12),
        ["round 180:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 180: the processor reads the record then stops", 16),
        ["round 180: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 180: the processor reads the record then stops", 24),
        ["round 180: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 180: the processor reads the record then stops", 32),
        ["round 180: the processor reads", "the record then stops"],
    ),
    (
        ("round 180: a worker pulls the next task from the queue", 4),
        ["round", "180:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 180: a worker pulls the next task from the queue", 8),
        ["round", "180: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 180: a worker pulls the next task from the queue", 12),
        ["round 180: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 180: a worker pulls the next task from the queue", 16),
        ["round 180: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 180: a worker pulls the next task from the queue", 24),
        ["round 180: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 180: a worker pulls the next task from the queue", 32),
        ["round 180: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 180: signals travel through the network layer", 4),
        ["round", "180:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 180: signals travel through the network layer", 8),
        ["round", "180:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 180: signals travel through the network layer", 12),
        ["round 180:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 180: signals travel through the network layer", 16),
        ["round 180:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 180: signals travel through the network layer", 24),
        ["round 180: signals", "travel through the", "network layer"],
    ),
    (
        ("round 180: signals travel through the network layer", 32),
        ["round 180: signals travel", "through the network layer"],
    ),
    (
        ("round 180: the gateway routes each request by policy", 4),
        ["round", "180:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 180: the gateway routes each request by policy", 8),
        ["round", "180: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 180: the gateway routes each request by policy", 12),
        ["round 180:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 180: the gateway routes each request by policy", 16),
        ["round 180: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 180: the gateway routes each request by policy", 24),
        ["round 180: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 180: the gateway routes each request by policy", 32),
        ["round 180: the gateway routes", "each request by policy"],
    ),
    (
        ("round 180: memory grows until the buffer is full", 4),
        ["round", "180:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 180: memory grows until the buffer is full", 8),
        ["round", "180:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 180: memory grows until the buffer is full", 12),
        ["round 180:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 180: memory grows until the buffer is full", 16),
        ["round 180:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 180: memory grows until the buffer is full", 24), ["round 180: memory grows", "until the buffer is full"]),
    (("round 180: memory grows until the buffer is full", 32), ["round 180: memory grows until", "the buffer is full"]),
    (
        ("round 180: the cluster mirrors every packet twice", 4),
        ["round", "180:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 180: the cluster mirrors every packet twice", 8),
        ["round", "180: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 180: the cluster mirrors every packet twice", 12),
        ["round 180:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 180: the cluster mirrors every packet twice", 16),
        ["round 180: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 180: the cluster mirrors every packet twice", 24),
        ["round 180: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 180: the cluster mirrors every packet twice", 32),
        ["round 180: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 180: ranking uses tokens learned from the corpus", 4),
        ["round", "180:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 180: ranking uses tokens learned from the corpus", 8),
        ["round", "180:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 180: ranking uses tokens learned from the corpus", 12),
        ["round 180:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 180: ranking uses tokens learned from the corpus", 16),
        ["round 180:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 180: ranking uses tokens learned from the corpus", 24),
        ["round 180: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 180: ranking uses tokens learned from the corpus", 32),
        ["round 180: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 180: a long session ends when the candle dies", 4),
        ["round", "180:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 180: a long session ends when the candle dies", 8),
        ["round", "180: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 180: a long session ends when the candle dies", 12),
        ["round 180: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 180: a long session ends when the candle dies", 16),
        ["round 180: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 180: a long session ends when the candle dies", 24),
        ["round 180: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 180: a long session ends when the candle dies", 32),
        ["round 180: a long session ends", "when the candle dies"],
    ),
    (
        ("round 180: encode the prompt then map the result", 4),
        ["round", "180:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 180: encode the prompt then map the result", 8),
        ["round", "180:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 180: encode the prompt then map the result", 12),
        ["round 180:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 180: encode the prompt then map the result", 16),
        ["round 180:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 180: encode the prompt then map the result", 24),
        ["round 180: encode the", "prompt then map the", "result"],
    ),
    (("round 180: encode the prompt then map the result", 32), ["round 180: encode the prompt", "then map the result"]),
    (
        ("round 180: the kernel wakes the worker at dawn", 4),
        ["round", "180:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 180: the kernel wakes the worker at dawn", 8),
        ["round", "180: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 180: the kernel wakes the worker at dawn", 12),
        ["round 180:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 180: the kernel wakes the worker at dawn", 16), ["round 180: the", "kernel wakes the", "worker at dawn"]),
    (("round 180: the kernel wakes the worker at dawn", 24), ["round 180: the kernel", "wakes the worker at dawn"]),
    (("round 180: the kernel wakes the worker at dawn", 32), ["round 180: the kernel wakes the", "worker at dawn"]),
    (
        ("round 180: service latency drops after the patch", 4),
        ["round", "180:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 180: service latency drops after the patch", 8),
        ["round", "180:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 180: service latency drops after the patch", 12),
        ["round 180:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 180: service latency drops after the patch", 16),
        ["round 180:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 180: service latency drops after the patch", 24),
        ["round 180: service", "latency drops after the", "patch"],
    ),
    (("round 180: service latency drops after the patch", 32), ["round 180: service latency drops", "after the patch"]),
    (
        ("round 180: the library caches every vector it sees", 4),
        ["round", "180:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 180: the library caches every vector it sees", 8),
        ["round", "180: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 180: the library caches every vector it sees", 12),
        ["round 180:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 180: the library caches every vector it sees", 16),
        ["round 180: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 180: the library caches every vector it sees", 24),
        ["round 180: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 180: the library caches every vector it sees", 32),
        ["round 180: the library caches", "every vector it sees"],
    ),
    (
        ("round 180: agents argue then the debate resolves", 4),
        ["round", "180:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 180: agents argue then the debate resolves", 8),
        ["round", "180:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 180: agents argue then the debate resolves", 12),
        ["round 180:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 180: agents argue then the debate resolves", 16),
        ["round 180:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 180: agents argue then the debate resolves", 24), ["round 180: agents argue", "then the debate resolves"]),
    (("round 180: agents argue then the debate resolves", 32), ["round 180: agents argue then the", "debate resolves"]),
    (
        ("round 180: the filter keeps only strong matches", 4),
        ["round", "180:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 180: the filter keeps only strong matches", 8),
        ["round", "180: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 180: the filter keeps only strong matches", 12),
        ["round 180:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 180: the filter keeps only strong matches", 16),
        ["round 180: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 180: the filter keeps only strong matches", 24),
        ["round 180: the filter", "keeps only strong", "matches"],
    ),
    (("round 180: the filter keeps only strong matches", 32), ["round 180: the filter keeps only", "strong matches"]),
    (
        ("round 180: the model answers with a short reply", 4),
        ["round", "180:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 180: the model answers with a short reply", 8),
        ["round", "180: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 180: the model answers with a short reply", 12),
        ["round 180:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 180: the model answers with a short reply", 16),
        ["round 180: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 180: the model answers with a short reply", 24),
        ["round 180: the model", "answers with a short", "reply"],
    ),
    (("round 180: the model answers with a short reply", 32), ["round 180: the model answers", "with a short reply"]),
    (
        ("round 180: the recorder stores the reasoning trace", 4),
        ["round", "180:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 180: the recorder stores the reasoning trace", 8),
        ["round", "180: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 180: the recorder stores the reasoning trace", 12),
        ["round 180:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 180: the recorder stores the reasoning trace", 16),
        ["round 180: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 180: the recorder stores the reasoning trace", 24),
        ["round 180: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 180: the recorder stores the reasoning trace", 32),
        ["round 180: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 180: the angel watches the processor run", 4),
        ["round", "180:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 180: the angel watches the processor run", 8),
        ["round", "180: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 180: the angel watches the processor run", 12),
        ["round 180:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 180: the angel watches the processor run", 16),
        ["round 180: the", "angel watches", "the processor", "run"],
    ),
    (("round 180: the angel watches the processor run", 24), ["round 180: the angel", "watches the processor", "run"]),
    (("round 180: the angel watches the processor run", 32), ["round 180: the angel watches the", "processor run"]),
    (
        ("round 180: angle of the vector decides the match", 4),
        ["round", "180:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 180: angle of the vector decides the match", 8),
        ["round", "180:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 180: angle of the vector decides the match", 12),
        ["round 180:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 180: angle of the vector decides the match", 16),
        ["round 180: angle", "of the vector", "decides the", "match"],
    ),
    (("round 180: angle of the vector decides the match", 24), ["round 180: angle of the", "vector decides the match"]),
    (("round 180: angle of the vector decides the match", 32), ["round 180: angle of the vector", "decides the match"]),
    (
        ("round 180: the candle burns twice as long at night", 4),
        ["round", "180:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 180: the candle burns twice as long at night", 8),
        ["round", "180: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 180: the candle burns twice as long at night", 12),
        ["round 180:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 180: the candle burns twice as long at night", 16),
        ["round 180: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 180: the candle burns twice as long at night", 24),
        ["round 180: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 180: the candle burns twice as long at night", 32),
        ["round 180: the candle burns", "twice as long at night"],
    ),
    (
        ("round 180: a mirror of the universe in one line", 4),
        ["round", "180:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 180: a mirror of the universe in one line", 8),
        ["round", "180: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 180: a mirror of the universe in one line", 12),
        ["round 180: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 180: a mirror of the universe in one line", 16),
        ["round 180: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 180: a mirror of the universe in one line", 24), ["round 180: a mirror of", "the universe in one line"]),
    (("round 180: a mirror of the universe in one line", 32), ["round 180: a mirror of the", "universe in one line"]),
    (
        ("round 180: the queue drains before the storm", 4),
        ["round", "180:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 180: the queue drains before the storm", 8),
        ["round", "180: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 180: the queue drains before the storm", 12),
        ["round 180:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 180: the queue drains before the storm", 16), ["round 180: the", "queue drains", "before the storm"]),
    (("round 180: the queue drains before the storm", 24), ["round 180: the queue", "drains before the storm"]),
    (("round 180: the queue drains before the storm", 32), ["round 180: the queue drains", "before the storm"]),
    (
        ("kitten180 sitting180 agent180 angle180 universe180 memory180", 6),
        ["kitten180", "sitting180", "agent180", "angle180", "universe180", "memory180"],
    ),
    (
        ("kitten180 sitting180 agent180 angle180 universe180 memory180", 10),
        ["kitten180", "sitting180", "agent180", "angle180", "universe180", "memory180"],
    ),
    (
        ("kitten180 sitting180 agent180 angle180 universe180 memory180", 18),
        ["kitten180", "sitting180", "agent180 angle180", "universe180", "memory180"],
    ),
    (
        ("kitten180 sitting180 agent180 angle180 universe180 memory180", 28),
        ["kitten180 sitting180", "agent180 angle180", "universe180 memory180"],
    ),
    (
        ("sitting180 agent180 angle180 universe180 memory180 stream180", 6),
        ["sitting180", "agent180", "angle180", "universe180", "memory180", "stream180"],
    ),
    (
        ("sitting180 agent180 angle180 universe180 memory180 stream180", 10),
        ["sitting180", "agent180", "angle180", "universe180", "memory180", "stream180"],
    ),
    (
        ("sitting180 agent180 angle180 universe180 memory180 stream180", 18),
        ["sitting180", "agent180 angle180", "universe180", "memory180", "stream180"],
    ),
    (
        ("sitting180 agent180 angle180 universe180 memory180 stream180", 28),
        ["sitting180 agent180 angle180", "universe180 memory180", "stream180"],
    ),
    (
        ("agent180 angle180 universe180 memory180 stream180 context180", 6),
        ["agent180", "angle180", "universe180", "memory180", "stream180", "context180"],
    ),
    (
        ("agent180 angle180 universe180 memory180 stream180 context180", 10),
        ["agent180", "angle180", "universe180", "memory180", "stream180", "context180"],
    ),
    (
        ("agent180 angle180 universe180 memory180 stream180 context180", 18),
        ["agent180 angle180", "universe180", "memory180", "stream180", "context180"],
    ),
    (
        ("agent180 angle180 universe180 memory180 stream180 context180", 28),
        ["agent180 angle180", "universe180 memory180", "stream180 context180"],
    ),
    (
        ("angle180 universe180 memory180 stream180 context180 knowledge180", 6),
        ["angle180", "universe180", "memory180", "stream180", "context180", "knowledge180"],
    ),
    (
        ("angle180 universe180 memory180 stream180 context180 knowledge180", 10),
        ["angle180", "universe180", "memory180", "stream180", "context180", "knowledge180"],
    ),
    (
        ("angle180 universe180 memory180 stream180 context180 knowledge180", 18),
        ["angle180", "universe180", "memory180", "stream180", "context180", "knowledge180"],
    ),
    (
        ("angle180 universe180 memory180 stream180 context180 knowledge180", 28),
        ["angle180 universe180", "memory180 stream180", "context180 knowledge180"],
    ),
    (
        ("universe180 memory180 stream180 context180 knowledge180 vector180", 6),
        ["universe180", "memory180", "stream180", "context180", "knowledge180", "vector180"],
    ),
    (
        ("universe180 memory180 stream180 context180 knowledge180 vector180", 10),
        ["universe180", "memory180", "stream180", "context180", "knowledge180", "vector180"],
    ),
    (
        ("universe180 memory180 stream180 context180 knowledge180 vector180", 18),
        ["universe180", "memory180", "stream180", "context180", "knowledge180", "vector180"],
    ),
    (
        ("universe180 memory180 stream180 context180 knowledge180 vector180", 28),
        ["universe180 memory180", "stream180 context180", "knowledge180 vector180"],
    ),
    (
        ("memory180 stream180 context180 knowledge180 vector180 processor180", 6),
        ["memory180", "stream180", "context180", "knowledge180", "vector180", "processor180"],
    ),
    (
        ("memory180 stream180 context180 knowledge180 vector180 processor180", 10),
        ["memory180", "stream180", "context180", "knowledge180", "vector180", "processor180"],
    ),
    (
        ("memory180 stream180 context180 knowledge180 vector180 processor180", 18),
        ["memory180", "stream180", "context180", "knowledge180", "vector180", "processor180"],
    ),
    (
        ("memory180 stream180 context180 knowledge180 vector180 processor180", 28),
        ["memory180 stream180", "context180 knowledge180", "vector180 processor180"],
    ),
    (
        ("stream180 context180 knowledge180 vector180 processor180 reasoning180", 6),
        ["stream180", "context180", "knowledge180", "vector180", "processor180", "reasoning180"],
    ),
    (
        ("stream180 context180 knowledge180 vector180 processor180 reasoning180", 10),
        ["stream180", "context180", "knowledge180", "vector180", "processor180", "reasoning180"],
    ),
    (
        ("stream180 context180 knowledge180 vector180 processor180 reasoning180", 18),
        ["stream180", "context180", "knowledge180", "vector180", "processor180", "reasoning180"],
    ),
    (
        ("stream180 context180 knowledge180 vector180 processor180 reasoning180", 28),
        ["stream180 context180", "knowledge180 vector180", "processor180 reasoning180"],
    ),
    (
        ("context180 knowledge180 vector180 processor180 reasoning180 machine180", 6),
        ["context180", "knowledge180", "vector180", "processor180", "reasoning180", "machine180"],
    ),
    (
        ("context180 knowledge180 vector180 processor180 reasoning180 machine180", 10),
        ["context180", "knowledge180", "vector180", "processor180", "reasoning180", "machine180"],
    ),
    (
        ("context180 knowledge180 vector180 processor180 reasoning180 machine180", 18),
        ["context180", "knowledge180", "vector180", "processor180", "reasoning180", "machine180"],
    ),
    (
        ("context180 knowledge180 vector180 processor180 reasoning180 machine180", 28),
        ["context180 knowledge180", "vector180 processor180", "reasoning180 machine180"],
    ),
    (
        ("knowledge180 vector180 processor180 reasoning180 machine180 learning180", 6),
        ["knowledge180", "vector180", "processor180", "reasoning180", "machine180", "learning180"],
    ),
    (
        ("knowledge180 vector180 processor180 reasoning180 machine180 learning180", 10),
        ["knowledge180", "vector180", "processor180", "reasoning180", "machine180", "learning180"],
    ),
    (
        ("knowledge180 vector180 processor180 reasoning180 machine180 learning180", 18),
        ["knowledge180", "vector180", "processor180", "reasoning180", "machine180", "learning180"],
    ),
    (
        ("knowledge180 vector180 processor180 reasoning180 machine180 learning180", 28),
        ["knowledge180 vector180", "processor180 reasoning180", "machine180 learning180"],
    ),
    (
        ("vector180 processor180 reasoning180 machine180 learning180 model180", 6),
        ["vector180", "processor180", "reasoning180", "machine180", "learning180", "model180"],
    ),
    (
        ("vector180 processor180 reasoning180 machine180 learning180 model180", 10),
        ["vector180", "processor180", "reasoning180", "machine180", "learning180", "model180"],
    ),
    (
        ("vector180 processor180 reasoning180 machine180 learning180 model180", 18),
        ["vector180", "processor180", "reasoning180", "machine180", "learning180", "model180"],
    ),
    (
        ("vector180 processor180 reasoning180 machine180 learning180 model180", 28),
        ["vector180 processor180", "reasoning180 machine180", "learning180 model180"],
    ),
    (
        ("processor180 reasoning180 machine180 learning180 model180 token180", 6),
        ["processor180", "reasoning180", "machine180", "learning180", "model180", "token180"],
    ),
    (
        ("processor180 reasoning180 machine180 learning180 model180 token180", 10),
        ["processor180", "reasoning180", "machine180", "learning180", "model180", "token180"],
    ),
    (
        ("processor180 reasoning180 machine180 learning180 model180 token180", 18),
        ["processor180", "reasoning180", "machine180", "learning180", "model180 token180"],
    ),
    (
        ("processor180 reasoning180 machine180 learning180 model180 token180", 28),
        ["processor180 reasoning180", "machine180 learning180", "model180 token180"],
    ),
    (
        ("reasoning180 machine180 learning180 model180 token180 prompt180", 6),
        ["reasoning180", "machine180", "learning180", "model180", "token180", "prompt180"],
    ),
    (
        ("reasoning180 machine180 learning180 model180 token180 prompt180", 10),
        ["reasoning180", "machine180", "learning180", "model180", "token180", "prompt180"],
    ),
    (
        ("reasoning180 machine180 learning180 model180 token180 prompt180", 18),
        ["reasoning180", "machine180", "learning180", "model180 token180", "prompt180"],
    ),
    (
        ("reasoning180 machine180 learning180 model180 token180 prompt180", 28),
        ["reasoning180 machine180", "learning180 model180", "token180 prompt180"],
    ),
    (
        ("machine180 learning180 model180 token180 prompt180 session180", 6),
        ["machine180", "learning180", "model180", "token180", "prompt180", "session180"],
    ),
    (
        ("machine180 learning180 model180 token180 prompt180 session180", 10),
        ["machine180", "learning180", "model180", "token180", "prompt180", "session180"],
    ),
    (
        ("machine180 learning180 model180 token180 prompt180 session180", 18),
        ["machine180", "learning180", "model180 token180", "prompt180", "session180"],
    ),
    (
        ("machine180 learning180 model180 token180 prompt180 session180", 28),
        ["machine180 learning180", "model180 token180 prompt180", "session180"],
    ),
    (
        ("learning180 model180 token180 prompt180 session180 library180", 6),
        ["learning180", "model180", "token180", "prompt180", "session180", "library180"],
    ),
    (
        ("learning180 model180 token180 prompt180 session180 library180", 10),
        ["learning180", "model180", "token180", "prompt180", "session180", "library180"],
    ),
    (
        ("learning180 model180 token180 prompt180 session180 library180", 18),
        ["learning180", "model180 token180", "prompt180", "session180", "library180"],
    ),
    (
        ("learning180 model180 token180 prompt180 session180 library180", 28),
        ["learning180 model180", "token180 prompt180", "session180 library180"],
    ),
    (
        ("model180 token180 prompt180 session180 library180 service180", 6),
        ["model180", "token180", "prompt180", "session180", "library180", "service180"],
    ),
    (
        ("model180 token180 prompt180 session180 library180 service180", 10),
        ["model180", "token180", "prompt180", "session180", "library180", "service180"],
    ),
    (
        ("model180 token180 prompt180 session180 library180 service180", 18),
        ["model180 token180", "prompt180", "session180", "library180", "service180"],
    ),
    (
        ("model180 token180 prompt180 session180 library180 service180", 28),
        ["model180 token180 prompt180", "session180 library180", "service180"],
    ),
    (
        ("token180 prompt180 session180 library180 service180 gateway180", 6),
        ["token180", "prompt180", "session180", "library180", "service180", "gateway180"],
    ),
    (
        ("token180 prompt180 session180 library180 service180 gateway180", 10),
        ["token180", "prompt180", "session180", "library180", "service180", "gateway180"],
    ),
    (
        ("token180 prompt180 session180 library180 service180 gateway180", 18),
        ["token180 prompt180", "session180", "library180", "service180", "gateway180"],
    ),
    (
        ("token180 prompt180 session180 library180 service180 gateway180", 28),
        ["token180 prompt180", "session180 library180", "service180 gateway180"],
    ),
    (
        ("prompt180 session180 library180 service180 gateway180 storage180", 6),
        ["prompt180", "session180", "library180", "service180", "gateway180", "storage180"],
    ),
    (
        ("prompt180 session180 library180 service180 gateway180 storage180", 10),
        ["prompt180", "session180", "library180", "service180", "gateway180", "storage180"],
    ),
    (
        ("prompt180 session180 library180 service180 gateway180 storage180", 18),
        ["prompt180", "session180", "library180", "service180", "gateway180", "storage180"],
    ),
    (
        ("prompt180 session180 library180 service180 gateway180 storage180", 28),
        ["prompt180 session180", "library180 service180", "gateway180 storage180"],
    ),
    (
        ("session180 library180 service180 gateway180 storage180 network180", 6),
        ["session180", "library180", "service180", "gateway180", "storage180", "network180"],
    ),
    (
        ("session180 library180 service180 gateway180 storage180 network180", 10),
        ["session180", "library180", "service180", "gateway180", "storage180", "network180"],
    ),
    (
        ("session180 library180 service180 gateway180 storage180 network180", 18),
        ["session180", "library180", "service180", "gateway180", "storage180", "network180"],
    ),
    (
        ("session180 library180 service180 gateway180 storage180 network180", 28),
        ["session180 library180", "service180 gateway180", "storage180 network180"],
    ),
    (
        ("library180 service180 gateway180 storage180 network180 latency180", 6),
        ["library180", "service180", "gateway180", "storage180", "network180", "latency180"],
    ),
    (
        ("library180 service180 gateway180 storage180 network180 latency180", 10),
        ["library180", "service180", "gateway180", "storage180", "network180", "latency180"],
    ),
    (
        ("library180 service180 gateway180 storage180 network180 latency180", 18),
        ["library180", "service180", "gateway180", "storage180", "network180", "latency180"],
    ),
    (
        ("library180 service180 gateway180 storage180 network180 latency180", 28),
        ["library180 service180", "gateway180 storage180", "network180 latency180"],
    ),
    (
        ("service180 gateway180 storage180 network180 latency180 buffer180", 6),
        ["service180", "gateway180", "storage180", "network180", "latency180", "buffer180"],
    ),
    (
        ("service180 gateway180 storage180 network180 latency180 buffer180", 10),
        ["service180", "gateway180", "storage180", "network180", "latency180", "buffer180"],
    ),
    (
        ("service180 gateway180 storage180 network180 latency180 buffer180", 18),
        ["service180", "gateway180", "storage180", "network180", "latency180", "buffer180"],
    ),
    (
        ("service180 gateway180 storage180 network180 latency180 buffer180", 28),
        ["service180 gateway180", "storage180 network180", "latency180 buffer180"],
    ),
    (
        ("gateway180 storage180 network180 latency180 buffer180 queue180", 6),
        ["gateway180", "storage180", "network180", "latency180", "buffer180", "queue180"],
    ),
    (
        ("gateway180 storage180 network180 latency180 buffer180 queue180", 10),
        ["gateway180", "storage180", "network180", "latency180", "buffer180", "queue180"],
    ),
    (
        ("gateway180 storage180 network180 latency180 buffer180 queue180", 18),
        ["gateway180", "storage180", "network180", "latency180", "buffer180 queue180"],
    ),
    (
        ("gateway180 storage180 network180 latency180 buffer180 queue180", 28),
        ["gateway180 storage180", "network180 latency180", "buffer180 queue180"],
    ),
    (
        ("storage180 network180 latency180 buffer180 queue180 worker180", 6),
        ["storage180", "network180", "latency180", "buffer180", "queue180", "worker180"],
    ),
    (
        ("storage180 network180 latency180 buffer180 queue180 worker180", 10),
        ["storage180", "network180", "latency180", "buffer180", "queue180", "worker180"],
    ),
    (
        ("storage180 network180 latency180 buffer180 queue180 worker180", 18),
        ["storage180", "network180", "latency180", "buffer180 queue180", "worker180"],
    ),
    (
        ("storage180 network180 latency180 buffer180 queue180 worker180", 28),
        ["storage180 network180", "latency180 buffer180", "queue180 worker180"],
    ),
    (
        ("network180 latency180 buffer180 queue180 worker180 kernel180", 6),
        ["network180", "latency180", "buffer180", "queue180", "worker180", "kernel180"],
    ),
    (
        ("network180 latency180 buffer180 queue180 worker180 kernel180", 10),
        ["network180", "latency180", "buffer180", "queue180", "worker180", "kernel180"],
    ),
    (
        ("network180 latency180 buffer180 queue180 worker180 kernel180", 18),
        ["network180", "latency180", "buffer180 queue180", "worker180", "kernel180"],
    ),
    (
        ("network180 latency180 buffer180 queue180 worker180 kernel180", 28),
        ["network180 latency180", "buffer180 queue180 worker180", "kernel180"],
    ),
    (
        ("latency180 buffer180 queue180 worker180 kernel180 signal180", 6),
        ["latency180", "buffer180", "queue180", "worker180", "kernel180", "signal180"],
    ),
    (
        ("latency180 buffer180 queue180 worker180 kernel180 signal180", 10),
        ["latency180", "buffer180", "queue180", "worker180", "kernel180", "signal180"],
    ),
    (
        ("latency180 buffer180 queue180 worker180 kernel180 signal180", 18),
        ["latency180", "buffer180 queue180", "worker180", "kernel180", "signal180"],
    ),
    (
        ("latency180 buffer180 queue180 worker180 kernel180 signal180", 28),
        ["latency180 buffer180", "queue180 worker180 kernel180", "signal180"],
    ),
    (
        ("buffer180 queue180 worker180 kernel180 signal180 packet180", 6),
        ["buffer180", "queue180", "worker180", "kernel180", "signal180", "packet180"],
    ),
    (
        ("buffer180 queue180 worker180 kernel180 signal180 packet180", 10),
        ["buffer180", "queue180", "worker180", "kernel180", "signal180", "packet180"],
    ),
    (
        ("buffer180 queue180 worker180 kernel180 signal180 packet180", 18),
        ["buffer180 queue180", "worker180", "kernel180", "signal180", "packet180"],
    ),
    (
        ("buffer180 queue180 worker180 kernel180 signal180 packet180", 28),
        ["buffer180 queue180 worker180", "kernel180 signal180", "packet180"],
    ),
    (
        ("queue180 worker180 kernel180 signal180 packet180 router180", 6),
        ["queue180", "worker180", "kernel180", "signal180", "packet180", "router180"],
    ),
    (
        ("queue180 worker180 kernel180 signal180 packet180 router180", 10),
        ["queue180", "worker180", "kernel180", "signal180", "packet180", "router180"],
    ),
    (
        ("queue180 worker180 kernel180 signal180 packet180 router180", 18),
        ["queue180 worker180", "kernel180", "signal180", "packet180", "router180"],
    ),
    (
        ("queue180 worker180 kernel180 signal180 packet180 router180", 28),
        ["queue180 worker180 kernel180", "signal180 packet180", "router180"],
    ),
    (
        ("worker180 kernel180 signal180 packet180 router180 cluster180", 6),
        ["worker180", "kernel180", "signal180", "packet180", "router180", "cluster180"],
    ),
    (
        ("worker180 kernel180 signal180 packet180 router180 cluster180", 10),
        ["worker180", "kernel180", "signal180", "packet180", "router180", "cluster180"],
    ),
    (
        ("worker180 kernel180 signal180 packet180 router180 cluster180", 18),
        ["worker180", "kernel180", "signal180", "packet180", "router180", "cluster180"],
    ),
    (
        ("worker180 kernel180 signal180 packet180 router180 cluster180", 28),
        ["worker180 kernel180", "signal180 packet180", "router180 cluster180"],
    ),
    (
        ("kernel180 signal180 packet180 router180 cluster180 mirror180", 6),
        ["kernel180", "signal180", "packet180", "router180", "cluster180", "mirror180"],
    ),
    (
        ("kernel180 signal180 packet180 router180 cluster180 mirror180", 10),
        ["kernel180", "signal180", "packet180", "router180", "cluster180", "mirror180"],
    ),
    (
        ("kernel180 signal180 packet180 router180 cluster180 mirror180", 18),
        ["kernel180", "signal180", "packet180", "router180", "cluster180", "mirror180"],
    ),
    (
        ("kernel180 signal180 packet180 router180 cluster180 mirror180", 28),
        ["kernel180 signal180", "packet180 router180", "cluster180 mirror180"],
    ),
    (
        ("signal180 packet180 router180 cluster180 mirror180 filter180", 6),
        ["signal180", "packet180", "router180", "cluster180", "mirror180", "filter180"],
    ),
    (
        ("signal180 packet180 router180 cluster180 mirror180 filter180", 10),
        ["signal180", "packet180", "router180", "cluster180", "mirror180", "filter180"],
    ),
    (
        ("signal180 packet180 router180 cluster180 mirror180 filter180", 18),
        ["signal180", "packet180", "router180", "cluster180", "mirror180", "filter180"],
    ),
    (
        ("signal180 packet180 router180 cluster180 mirror180 filter180", 28),
        ["signal180 packet180", "router180 cluster180", "mirror180 filter180"],
    ),
    (
        ("packet180 router180 cluster180 mirror180 filter180 ranking180", 6),
        ["packet180", "router180", "cluster180", "mirror180", "filter180", "ranking180"],
    ),
    (
        ("packet180 router180 cluster180 mirror180 filter180 ranking180", 10),
        ["packet180", "router180", "cluster180", "mirror180", "filter180", "ranking180"],
    ),
    (
        ("packet180 router180 cluster180 mirror180 filter180 ranking180", 18),
        ["packet180", "router180", "cluster180", "mirror180", "filter180", "ranking180"],
    ),
    (
        ("packet180 router180 cluster180 mirror180 filter180 ranking180", 28),
        ["packet180 router180", "cluster180 mirror180", "filter180 ranking180"],
    ),
    (
        ("router180 cluster180 mirror180 filter180 ranking180 encoding180", 6),
        ["router180", "cluster180", "mirror180", "filter180", "ranking180", "encoding180"],
    ),
    (
        ("router180 cluster180 mirror180 filter180 ranking180 encoding180", 10),
        ["router180", "cluster180", "mirror180", "filter180", "ranking180", "encoding180"],
    ),
    (
        ("router180 cluster180 mirror180 filter180 ranking180 encoding180", 18),
        ["router180", "cluster180", "mirror180", "filter180", "ranking180", "encoding180"],
    ),
    (
        ("router180 cluster180 mirror180 filter180 ranking180 encoding180", 28),
        ["router180 cluster180", "mirror180 filter180", "ranking180 encoding180"],
    ),
    (
        ("cluster180 mirror180 filter180 ranking180 encoding180 mapping180", 6),
        ["cluster180", "mirror180", "filter180", "ranking180", "encoding180", "mapping180"],
    ),
    (
        ("cluster180 mirror180 filter180 ranking180 encoding180 mapping180", 10),
        ["cluster180", "mirror180", "filter180", "ranking180", "encoding180", "mapping180"],
    ),
    (
        ("cluster180 mirror180 filter180 ranking180 encoding180 mapping180", 18),
        ["cluster180", "mirror180", "filter180", "ranking180", "encoding180", "mapping180"],
    ),
    (
        ("cluster180 mirror180 filter180 ranking180 encoding180 mapping180", 28),
        ["cluster180 mirror180", "filter180 ranking180", "encoding180 mapping180"],
    ),
    (
        ("mirror180 filter180 ranking180 encoding180 mapping180 record180", 6),
        ["mirror180", "filter180", "ranking180", "encoding180", "mapping180", "record180"],
    ),
    (
        ("mirror180 filter180 ranking180 encoding180 mapping180 record180", 10),
        ["mirror180", "filter180", "ranking180", "encoding180", "mapping180", "record180"],
    ),
    (
        ("mirror180 filter180 ranking180 encoding180 mapping180 record180", 18),
        ["mirror180", "filter180", "ranking180", "encoding180", "mapping180", "record180"],
    ),
    (
        ("mirror180 filter180 ranking180 encoding180 mapping180 record180", 28),
        ["mirror180 filter180", "ranking180 encoding180", "mapping180 record180"],
    ),
    (
        ("filter180 ranking180 encoding180 mapping180 record180 candle180", 6),
        ["filter180", "ranking180", "encoding180", "mapping180", "record180", "candle180"],
    ),
    (
        ("filter180 ranking180 encoding180 mapping180 record180 candle180", 10),
        ["filter180", "ranking180", "encoding180", "mapping180", "record180", "candle180"],
    ),
    (
        ("filter180 ranking180 encoding180 mapping180 record180 candle180", 18),
        ["filter180", "ranking180", "encoding180", "mapping180", "record180", "candle180"],
    ),
    (
        ("filter180 ranking180 encoding180 mapping180 record180 candle180", 28),
        ["filter180 ranking180", "encoding180 mapping180", "record180 candle180"],
    ),
    (
        ("ranking180 encoding180 mapping180 record180 candle180 thread180", 6),
        ["ranking180", "encoding180", "mapping180", "record180", "candle180", "thread180"],
    ),
    (
        ("ranking180 encoding180 mapping180 record180 candle180 thread180", 10),
        ["ranking180", "encoding180", "mapping180", "record180", "candle180", "thread180"],
    ),
    (
        ("ranking180 encoding180 mapping180 record180 candle180 thread180", 18),
        ["ranking180", "encoding180", "mapping180", "record180", "candle180", "thread180"],
    ),
    (
        ("ranking180 encoding180 mapping180 record180 candle180 thread180", 28),
        ["ranking180 encoding180", "mapping180 record180", "candle180 thread180"],
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
