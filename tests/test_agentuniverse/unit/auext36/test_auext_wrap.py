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
        ("round 36: the quick brown fox jumps over the lazy dog", 4),
        ["round", "36:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 36: the quick brown fox jumps over the lazy dog", 8),
        ["round", "36: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 36: the quick brown fox jumps over the lazy dog", 12),
        ["round 36:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 36: the quick brown fox jumps over the lazy dog", 16),
        ["round 36: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 36: the quick brown fox jumps over the lazy dog", 24),
        ["round 36: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 36: the quick brown fox jumps over the lazy dog", 32),
        ["round 36: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 36: agentuniverse is a framework for multi agents", 4),
        ["round", "36:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 36: agentuniverse is a framework for multi agents", 8),
        ["round", "36:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 36: agentuniverse is a framework for multi agents", 12),
        ["round 36:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 36: agentuniverse is a framework for multi agents", 16),
        ["round 36:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 36: agentuniverse is a framework for multi agents", 24),
        ["round 36: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 36: agentuniverse is a framework for multi agents", 32),
        ["round 36: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 36: knowledge stored as vectors enables retrieval", 4),
        ["round", "36:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 36: knowledge stored as vectors enables retrieval", 8),
        ["round", "36:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 36: knowledge stored as vectors enables retrieval", 12),
        ["round 36:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 36: knowledge stored as vectors enables retrieval", 16),
        ["round 36:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 36: knowledge stored as vectors enables retrieval", 24),
        ["round 36: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 36: knowledge stored as vectors enables retrieval", 32),
        ["round 36: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 36: the processor reads the record then stops", 4),
        ["round", "36:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 36: the processor reads the record then stops", 8),
        ["round", "36: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 36: the processor reads the record then stops", 12),
        ["round 36:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 36: the processor reads the record then stops", 16),
        ["round 36: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 36: the processor reads the record then stops", 24),
        ["round 36: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 36: the processor reads the record then stops", 32),
        ["round 36: the processor reads", "the record then stops"],
    ),
    (
        ("round 36: a worker pulls the next task from the queue", 4),
        ["round", "36:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 36: a worker pulls the next task from the queue", 8),
        ["round", "36: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 36: a worker pulls the next task from the queue", 12),
        ["round 36: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 36: a worker pulls the next task from the queue", 16),
        ["round 36: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 36: a worker pulls the next task from the queue", 24),
        ["round 36: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 36: a worker pulls the next task from the queue", 32),
        ["round 36: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 36: signals travel through the network layer", 4),
        ["round", "36:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 36: signals travel through the network layer", 8),
        ["round", "36:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 36: signals travel through the network layer", 12),
        ["round 36:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 36: signals travel through the network layer", 16),
        ["round 36:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 36: signals travel through the network layer", 24),
        ["round 36: signals travel", "through the network", "layer"],
    ),
    (
        ("round 36: signals travel through the network layer", 32),
        ["round 36: signals travel through", "the network layer"],
    ),
    (
        ("round 36: the gateway routes each request by policy", 4),
        ["round", "36:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 36: the gateway routes each request by policy", 8),
        ["round", "36: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 36: the gateway routes each request by policy", 12),
        ["round 36:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 36: the gateway routes each request by policy", 16),
        ["round 36: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 36: the gateway routes each request by policy", 24),
        ["round 36: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 36: the gateway routes each request by policy", 32),
        ["round 36: the gateway routes", "each request by policy"],
    ),
    (
        ("round 36: memory grows until the buffer is full", 4),
        ["round", "36:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 36: memory grows until the buffer is full", 8),
        ["round", "36:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 36: memory grows until the buffer is full", 12),
        ["round 36:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 36: memory grows until the buffer is full", 16),
        ["round 36: memory", "grows until the", "buffer is full"],
    ),
    (("round 36: memory grows until the buffer is full", 24), ["round 36: memory grows", "until the buffer is full"]),
    (("round 36: memory grows until the buffer is full", 32), ["round 36: memory grows until the", "buffer is full"]),
    (
        ("round 36: the cluster mirrors every packet twice", 4),
        ["round", "36:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 36: the cluster mirrors every packet twice", 8),
        ["round", "36: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 36: the cluster mirrors every packet twice", 12),
        ["round 36:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 36: the cluster mirrors every packet twice", 16),
        ["round 36: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 36: the cluster mirrors every packet twice", 24),
        ["round 36: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 36: the cluster mirrors every packet twice", 32), ["round 36: the cluster mirrors", "every packet twice"]),
    (
        ("round 36: ranking uses tokens learned from the corpus", 4),
        ["round", "36:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 36: ranking uses tokens learned from the corpus", 8),
        ["round", "36:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 36: ranking uses tokens learned from the corpus", 12),
        ["round 36:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 36: ranking uses tokens learned from the corpus", 16),
        ["round 36:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 36: ranking uses tokens learned from the corpus", 24),
        ["round 36: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 36: ranking uses tokens learned from the corpus", 32),
        ["round 36: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 36: a long session ends when the candle dies", 4),
        ["round", "36:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 36: a long session ends when the candle dies", 8),
        ["round", "36: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 36: a long session ends when the candle dies", 12),
        ["round 36: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 36: a long session ends when the candle dies", 16),
        ["round 36: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 36: a long session ends when the candle dies", 24),
        ["round 36: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 36: a long session ends when the candle dies", 32),
        ["round 36: a long session ends", "when the candle dies"],
    ),
    (
        ("round 36: encode the prompt then map the result", 4),
        ["round", "36:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 36: encode the prompt then map the result", 8),
        ["round", "36:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 36: encode the prompt then map the result", 12),
        ["round 36:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 36: encode the prompt then map the result", 16),
        ["round 36: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 36: encode the prompt then map the result", 24),
        ["round 36: encode the", "prompt then map the", "result"],
    ),
    (("round 36: encode the prompt then map the result", 32), ["round 36: encode the prompt then", "map the result"]),
    (
        ("round 36: the kernel wakes the worker at dawn", 4),
        ["round", "36:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 36: the kernel wakes the worker at dawn", 8),
        ["round", "36: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 36: the kernel wakes the worker at dawn", 12),
        ["round 36:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 36: the kernel wakes the worker at dawn", 16), ["round 36: the", "kernel wakes the", "worker at dawn"]),
    (("round 36: the kernel wakes the worker at dawn", 24), ["round 36: the kernel", "wakes the worker at dawn"]),
    (("round 36: the kernel wakes the worker at dawn", 32), ["round 36: the kernel wakes the", "worker at dawn"]),
    (
        ("round 36: service latency drops after the patch", 4),
        ["round", "36:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 36: service latency drops after the patch", 8),
        ["round", "36:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 36: service latency drops after the patch", 12),
        ["round 36:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 36: service latency drops after the patch", 16),
        ["round 36:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 36: service latency drops after the patch", 24),
        ["round 36: service", "latency drops after the", "patch"],
    ),
    (("round 36: service latency drops after the patch", 32), ["round 36: service latency drops", "after the patch"]),
    (
        ("round 36: the library caches every vector it sees", 4),
        ["round", "36:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 36: the library caches every vector it sees", 8),
        ["round", "36: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 36: the library caches every vector it sees", 12),
        ["round 36:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 36: the library caches every vector it sees", 16),
        ["round 36: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 36: the library caches every vector it sees", 24),
        ["round 36: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 36: the library caches every vector it sees", 32),
        ["round 36: the library caches", "every vector it sees"],
    ),
    (
        ("round 36: agents argue then the debate resolves", 4),
        ["round", "36:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 36: agents argue then the debate resolves", 8),
        ["round", "36:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 36: agents argue then the debate resolves", 12),
        ["round 36:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 36: agents argue then the debate resolves", 16),
        ["round 36: agents", "argue then the", "debate resolves"],
    ),
    (("round 36: agents argue then the debate resolves", 24), ["round 36: agents argue", "then the debate resolves"]),
    (("round 36: agents argue then the debate resolves", 32), ["round 36: agents argue then the", "debate resolves"]),
    (
        ("round 36: the filter keeps only strong matches", 4),
        ["round", "36:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 36: the filter keeps only strong matches", 8),
        ["round", "36: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 36: the filter keeps only strong matches", 12),
        ["round 36:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 36: the filter keeps only strong matches", 16),
        ["round 36: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 36: the filter keeps only strong matches", 24), ["round 36: the filter", "keeps only strong", "matches"]),
    (("round 36: the filter keeps only strong matches", 32), ["round 36: the filter keeps only", "strong matches"]),
    (
        ("round 36: the model answers with a short reply", 4),
        ["round", "36:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 36: the model answers with a short reply", 8),
        ["round", "36: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 36: the model answers with a short reply", 12),
        ["round 36:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 36: the model answers with a short reply", 16),
        ["round 36: the", "model answers", "with a short", "reply"],
    ),
    (("round 36: the model answers with a short reply", 24), ["round 36: the model", "answers with a short", "reply"]),
    (("round 36: the model answers with a short reply", 32), ["round 36: the model answers with", "a short reply"]),
    (
        ("round 36: the recorder stores the reasoning trace", 4),
        ["round", "36:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 36: the recorder stores the reasoning trace", 8),
        ["round", "36: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 36: the recorder stores the reasoning trace", 12),
        ["round 36:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 36: the recorder stores the reasoning trace", 16),
        ["round 36: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 36: the recorder stores the reasoning trace", 24),
        ["round 36: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 36: the recorder stores the reasoning trace", 32),
        ["round 36: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 36: the angel watches the processor run", 4),
        ["round", "36:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 36: the angel watches the processor run", 8),
        ["round", "36: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 36: the angel watches the processor run", 12),
        ["round 36:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 36: the angel watches the processor run", 16), ["round 36: the", "angel watches", "the processor", "run"]),
    (("round 36: the angel watches the processor run", 24), ["round 36: the angel", "watches the processor", "run"]),
    (("round 36: the angel watches the processor run", 32), ["round 36: the angel watches the", "processor run"]),
    (
        ("round 36: angle of the vector decides the match", 4),
        ["round", "36:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 36: angle of the vector decides the match", 8),
        ["round", "36:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 36: angle of the vector decides the match", 12),
        ["round 36:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 36: angle of the vector decides the match", 16),
        ["round 36: angle", "of the vector", "decides the", "match"],
    ),
    (("round 36: angle of the vector decides the match", 24), ["round 36: angle of the", "vector decides the match"]),
    (("round 36: angle of the vector decides the match", 32), ["round 36: angle of the vector", "decides the match"]),
    (
        ("round 36: the candle burns twice as long at night", 4),
        ["round", "36:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 36: the candle burns twice as long at night", 8),
        ["round", "36: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 36: the candle burns twice as long at night", 12),
        ["round 36:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 36: the candle burns twice as long at night", 16),
        ["round 36: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 36: the candle burns twice as long at night", 24),
        ["round 36: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 36: the candle burns twice as long at night", 32),
        ["round 36: the candle burns twice", "as long at night"],
    ),
    (
        ("round 36: a mirror of the universe in one line", 4),
        ["round", "36:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 36: a mirror of the universe in one line", 8),
        ["round", "36: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 36: a mirror of the universe in one line", 12),
        ["round 36: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 36: a mirror of the universe in one line", 16),
        ["round 36: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 36: a mirror of the universe in one line", 24), ["round 36: a mirror of", "the universe in one line"]),
    (("round 36: a mirror of the universe in one line", 32), ["round 36: a mirror of the", "universe in one line"]),
    (
        ("round 36: the queue drains before the storm", 4),
        ["round", "36:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 36: the queue drains before the storm", 8),
        ["round", "36: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 36: the queue drains before the storm", 12), ["round 36:", "the queue", "drains", "before the", "storm"]),
    (("round 36: the queue drains before the storm", 16), ["round 36: the", "queue drains", "before the storm"]),
    (("round 36: the queue drains before the storm", 24), ["round 36: the queue", "drains before the storm"]),
    (("round 36: the queue drains before the storm", 32), ["round 36: the queue drains", "before the storm"]),
    (
        ("kitten36 sitting36 agent36 angle36 universe36 memory36", 6),
        ["kitten36", "sitting36", "agent36", "angle36", "universe36", "memory36"],
    ),
    (
        ("kitten36 sitting36 agent36 angle36 universe36 memory36", 10),
        ["kitten36", "sitting36", "agent36", "angle36", "universe36", "memory36"],
    ),
    (
        ("kitten36 sitting36 agent36 angle36 universe36 memory36", 18),
        ["kitten36 sitting36", "agent36 angle36", "universe36", "memory36"],
    ),
    (
        ("kitten36 sitting36 agent36 angle36 universe36 memory36", 28),
        ["kitten36 sitting36 agent36", "angle36 universe36 memory36"],
    ),
    (
        ("sitting36 agent36 angle36 universe36 memory36 stream36", 6),
        ["sitting36", "agent36", "angle36", "universe36", "memory36", "stream36"],
    ),
    (
        ("sitting36 agent36 angle36 universe36 memory36 stream36", 10),
        ["sitting36", "agent36", "angle36", "universe36", "memory36", "stream36"],
    ),
    (
        ("sitting36 agent36 angle36 universe36 memory36 stream36", 18),
        ["sitting36 agent36", "angle36 universe36", "memory36 stream36"],
    ),
    (
        ("sitting36 agent36 angle36 universe36 memory36 stream36", 28),
        ["sitting36 agent36 angle36", "universe36 memory36 stream36"],
    ),
    (
        ("agent36 angle36 universe36 memory36 stream36 context36", 6),
        ["agent36", "angle36", "universe36", "memory36", "stream36", "context36"],
    ),
    (
        ("agent36 angle36 universe36 memory36 stream36 context36", 10),
        ["agent36", "angle36", "universe36", "memory36", "stream36", "context36"],
    ),
    (
        ("agent36 angle36 universe36 memory36 stream36 context36", 18),
        ["agent36 angle36", "universe36", "memory36 stream36", "context36"],
    ),
    (
        ("agent36 angle36 universe36 memory36 stream36 context36", 28),
        ["agent36 angle36 universe36", "memory36 stream36 context36"],
    ),
    (
        ("angle36 universe36 memory36 stream36 context36 knowledge36", 6),
        ["angle36", "universe36", "memory36", "stream36", "context36", "knowledge36"],
    ),
    (
        ("angle36 universe36 memory36 stream36 context36 knowledge36", 10),
        ["angle36", "universe36", "memory36", "stream36", "context36", "knowledge36"],
    ),
    (
        ("angle36 universe36 memory36 stream36 context36 knowledge36", 18),
        ["angle36 universe36", "memory36 stream36", "context36", "knowledge36"],
    ),
    (
        ("angle36 universe36 memory36 stream36 context36 knowledge36", 28),
        ["angle36 universe36 memory36", "stream36 context36", "knowledge36"],
    ),
    (
        ("universe36 memory36 stream36 context36 knowledge36 vector36", 6),
        ["universe36", "memory36", "stream36", "context36", "knowledge36", "vector36"],
    ),
    (
        ("universe36 memory36 stream36 context36 knowledge36 vector36", 10),
        ["universe36", "memory36", "stream36", "context36", "knowledge36", "vector36"],
    ),
    (
        ("universe36 memory36 stream36 context36 knowledge36 vector36", 18),
        ["universe36", "memory36 stream36", "context36", "knowledge36", "vector36"],
    ),
    (
        ("universe36 memory36 stream36 context36 knowledge36 vector36", 28),
        ["universe36 memory36 stream36", "context36 knowledge36", "vector36"],
    ),
    (
        ("memory36 stream36 context36 knowledge36 vector36 processor36", 6),
        ["memory36", "stream36", "context36", "knowledge36", "vector36", "processor36"],
    ),
    (
        ("memory36 stream36 context36 knowledge36 vector36 processor36", 10),
        ["memory36", "stream36", "context36", "knowledge36", "vector36", "processor36"],
    ),
    (
        ("memory36 stream36 context36 knowledge36 vector36 processor36", 18),
        ["memory36 stream36", "context36", "knowledge36", "vector36", "processor36"],
    ),
    (
        ("memory36 stream36 context36 knowledge36 vector36 processor36", 28),
        ["memory36 stream36 context36", "knowledge36 vector36", "processor36"],
    ),
    (
        ("stream36 context36 knowledge36 vector36 processor36 reasoning36", 6),
        ["stream36", "context36", "knowledge36", "vector36", "processor36", "reasoning36"],
    ),
    (
        ("stream36 context36 knowledge36 vector36 processor36 reasoning36", 10),
        ["stream36", "context36", "knowledge36", "vector36", "processor36", "reasoning36"],
    ),
    (
        ("stream36 context36 knowledge36 vector36 processor36 reasoning36", 18),
        ["stream36 context36", "knowledge36", "vector36", "processor36", "reasoning36"],
    ),
    (
        ("stream36 context36 knowledge36 vector36 processor36 reasoning36", 28),
        ["stream36 context36", "knowledge36 vector36", "processor36 reasoning36"],
    ),
    (
        ("context36 knowledge36 vector36 processor36 reasoning36 machine36", 6),
        ["context36", "knowledge36", "vector36", "processor36", "reasoning36", "machine36"],
    ),
    (
        ("context36 knowledge36 vector36 processor36 reasoning36 machine36", 10),
        ["context36", "knowledge36", "vector36", "processor36", "reasoning36", "machine36"],
    ),
    (
        ("context36 knowledge36 vector36 processor36 reasoning36 machine36", 18),
        ["context36", "knowledge36", "vector36", "processor36", "reasoning36", "machine36"],
    ),
    (
        ("context36 knowledge36 vector36 processor36 reasoning36 machine36", 28),
        ["context36 knowledge36", "vector36 processor36", "reasoning36 machine36"],
    ),
    (
        ("knowledge36 vector36 processor36 reasoning36 machine36 learning36", 6),
        ["knowledge36", "vector36", "processor36", "reasoning36", "machine36", "learning36"],
    ),
    (
        ("knowledge36 vector36 processor36 reasoning36 machine36 learning36", 10),
        ["knowledge36", "vector36", "processor36", "reasoning36", "machine36", "learning36"],
    ),
    (
        ("knowledge36 vector36 processor36 reasoning36 machine36 learning36", 18),
        ["knowledge36", "vector36", "processor36", "reasoning36", "machine36", "learning36"],
    ),
    (
        ("knowledge36 vector36 processor36 reasoning36 machine36 learning36", 28),
        ["knowledge36 vector36", "processor36 reasoning36", "machine36 learning36"],
    ),
    (
        ("vector36 processor36 reasoning36 machine36 learning36 model36", 6),
        ["vector36", "processor36", "reasoning36", "machine36", "learning36", "model36"],
    ),
    (
        ("vector36 processor36 reasoning36 machine36 learning36 model36", 10),
        ["vector36", "processor36", "reasoning36", "machine36", "learning36", "model36"],
    ),
    (
        ("vector36 processor36 reasoning36 machine36 learning36 model36", 18),
        ["vector36", "processor36", "reasoning36", "machine36", "learning36 model36"],
    ),
    (
        ("vector36 processor36 reasoning36 machine36 learning36 model36", 28),
        ["vector36 processor36", "reasoning36 machine36", "learning36 model36"],
    ),
    (
        ("processor36 reasoning36 machine36 learning36 model36 token36", 6),
        ["processor36", "reasoning36", "machine36", "learning36", "model36", "token36"],
    ),
    (
        ("processor36 reasoning36 machine36 learning36 model36 token36", 10),
        ["processor36", "reasoning36", "machine36", "learning36", "model36", "token36"],
    ),
    (
        ("processor36 reasoning36 machine36 learning36 model36 token36", 18),
        ["processor36", "reasoning36", "machine36", "learning36 model36", "token36"],
    ),
    (
        ("processor36 reasoning36 machine36 learning36 model36 token36", 28),
        ["processor36 reasoning36", "machine36 learning36 model36", "token36"],
    ),
    (
        ("reasoning36 machine36 learning36 model36 token36 prompt36", 6),
        ["reasoning36", "machine36", "learning36", "model36", "token36", "prompt36"],
    ),
    (
        ("reasoning36 machine36 learning36 model36 token36 prompt36", 10),
        ["reasoning36", "machine36", "learning36", "model36", "token36", "prompt36"],
    ),
    (
        ("reasoning36 machine36 learning36 model36 token36 prompt36", 18),
        ["reasoning36", "machine36", "learning36 model36", "token36 prompt36"],
    ),
    (
        ("reasoning36 machine36 learning36 model36 token36 prompt36", 28),
        ["reasoning36 machine36", "learning36 model36 token36", "prompt36"],
    ),
    (
        ("machine36 learning36 model36 token36 prompt36 session36", 6),
        ["machine36", "learning36", "model36", "token36", "prompt36", "session36"],
    ),
    (
        ("machine36 learning36 model36 token36 prompt36 session36", 10),
        ["machine36", "learning36", "model36", "token36", "prompt36", "session36"],
    ),
    (
        ("machine36 learning36 model36 token36 prompt36 session36", 18),
        ["machine36", "learning36 model36", "token36 prompt36", "session36"],
    ),
    (
        ("machine36 learning36 model36 token36 prompt36 session36", 28),
        ["machine36 learning36 model36", "token36 prompt36 session36"],
    ),
    (
        ("learning36 model36 token36 prompt36 session36 library36", 6),
        ["learning36", "model36", "token36", "prompt36", "session36", "library36"],
    ),
    (
        ("learning36 model36 token36 prompt36 session36 library36", 10),
        ["learning36", "model36", "token36", "prompt36", "session36", "library36"],
    ),
    (
        ("learning36 model36 token36 prompt36 session36 library36", 18),
        ["learning36 model36", "token36 prompt36", "session36", "library36"],
    ),
    (
        ("learning36 model36 token36 prompt36 session36 library36", 28),
        ["learning36 model36 token36", "prompt36 session36 library36"],
    ),
    (
        ("model36 token36 prompt36 session36 library36 service36", 6),
        ["model36", "token36", "prompt36", "session36", "library36", "service36"],
    ),
    (
        ("model36 token36 prompt36 session36 library36 service36", 10),
        ["model36", "token36", "prompt36", "session36", "library36", "service36"],
    ),
    (
        ("model36 token36 prompt36 session36 library36 service36", 18),
        ["model36 token36", "prompt36 session36", "library36", "service36"],
    ),
    (
        ("model36 token36 prompt36 session36 library36 service36", 28),
        ["model36 token36 prompt36", "session36 library36", "service36"],
    ),
    (
        ("token36 prompt36 session36 library36 service36 gateway36", 6),
        ["token36", "prompt36", "session36", "library36", "service36", "gateway36"],
    ),
    (
        ("token36 prompt36 session36 library36 service36 gateway36", 10),
        ["token36", "prompt36", "session36", "library36", "service36", "gateway36"],
    ),
    (
        ("token36 prompt36 session36 library36 service36 gateway36", 18),
        ["token36 prompt36", "session36", "library36", "service36", "gateway36"],
    ),
    (
        ("token36 prompt36 session36 library36 service36 gateway36", 28),
        ["token36 prompt36 session36", "library36 service36", "gateway36"],
    ),
    (
        ("prompt36 session36 library36 service36 gateway36 storage36", 6),
        ["prompt36", "session36", "library36", "service36", "gateway36", "storage36"],
    ),
    (
        ("prompt36 session36 library36 service36 gateway36 storage36", 10),
        ["prompt36", "session36", "library36", "service36", "gateway36", "storage36"],
    ),
    (
        ("prompt36 session36 library36 service36 gateway36 storage36", 18),
        ["prompt36 session36", "library36", "service36", "gateway36", "storage36"],
    ),
    (
        ("prompt36 session36 library36 service36 gateway36 storage36", 28),
        ["prompt36 session36 library36", "service36 gateway36", "storage36"],
    ),
    (
        ("session36 library36 service36 gateway36 storage36 network36", 6),
        ["session36", "library36", "service36", "gateway36", "storage36", "network36"],
    ),
    (
        ("session36 library36 service36 gateway36 storage36 network36", 10),
        ["session36", "library36", "service36", "gateway36", "storage36", "network36"],
    ),
    (
        ("session36 library36 service36 gateway36 storage36 network36", 18),
        ["session36", "library36", "service36", "gateway36", "storage36", "network36"],
    ),
    (
        ("session36 library36 service36 gateway36 storage36 network36", 28),
        ["session36 library36", "service36 gateway36", "storage36 network36"],
    ),
    (
        ("library36 service36 gateway36 storage36 network36 latency36", 6),
        ["library36", "service36", "gateway36", "storage36", "network36", "latency36"],
    ),
    (
        ("library36 service36 gateway36 storage36 network36 latency36", 10),
        ["library36", "service36", "gateway36", "storage36", "network36", "latency36"],
    ),
    (
        ("library36 service36 gateway36 storage36 network36 latency36", 18),
        ["library36", "service36", "gateway36", "storage36", "network36", "latency36"],
    ),
    (
        ("library36 service36 gateway36 storage36 network36 latency36", 28),
        ["library36 service36", "gateway36 storage36", "network36 latency36"],
    ),
    (
        ("service36 gateway36 storage36 network36 latency36 buffer36", 6),
        ["service36", "gateway36", "storage36", "network36", "latency36", "buffer36"],
    ),
    (
        ("service36 gateway36 storage36 network36 latency36 buffer36", 10),
        ["service36", "gateway36", "storage36", "network36", "latency36", "buffer36"],
    ),
    (
        ("service36 gateway36 storage36 network36 latency36 buffer36", 18),
        ["service36", "gateway36", "storage36", "network36", "latency36 buffer36"],
    ),
    (
        ("service36 gateway36 storage36 network36 latency36 buffer36", 28),
        ["service36 gateway36", "storage36 network36", "latency36 buffer36"],
    ),
    (
        ("gateway36 storage36 network36 latency36 buffer36 queue36", 6),
        ["gateway36", "storage36", "network36", "latency36", "buffer36", "queue36"],
    ),
    (
        ("gateway36 storage36 network36 latency36 buffer36 queue36", 10),
        ["gateway36", "storage36", "network36", "latency36", "buffer36", "queue36"],
    ),
    (
        ("gateway36 storage36 network36 latency36 buffer36 queue36", 18),
        ["gateway36", "storage36", "network36", "latency36 buffer36", "queue36"],
    ),
    (
        ("gateway36 storage36 network36 latency36 buffer36 queue36", 28),
        ["gateway36 storage36", "network36 latency36 buffer36", "queue36"],
    ),
    (
        ("storage36 network36 latency36 buffer36 queue36 worker36", 6),
        ["storage36", "network36", "latency36", "buffer36", "queue36", "worker36"],
    ),
    (
        ("storage36 network36 latency36 buffer36 queue36 worker36", 10),
        ["storage36", "network36", "latency36", "buffer36", "queue36", "worker36"],
    ),
    (
        ("storage36 network36 latency36 buffer36 queue36 worker36", 18),
        ["storage36", "network36", "latency36 buffer36", "queue36 worker36"],
    ),
    (
        ("storage36 network36 latency36 buffer36 queue36 worker36", 28),
        ["storage36 network36", "latency36 buffer36 queue36", "worker36"],
    ),
    (
        ("network36 latency36 buffer36 queue36 worker36 kernel36", 6),
        ["network36", "latency36", "buffer36", "queue36", "worker36", "kernel36"],
    ),
    (
        ("network36 latency36 buffer36 queue36 worker36 kernel36", 10),
        ["network36", "latency36", "buffer36", "queue36", "worker36", "kernel36"],
    ),
    (
        ("network36 latency36 buffer36 queue36 worker36 kernel36", 18),
        ["network36", "latency36 buffer36", "queue36 worker36", "kernel36"],
    ),
    (
        ("network36 latency36 buffer36 queue36 worker36 kernel36", 28),
        ["network36 latency36 buffer36", "queue36 worker36 kernel36"],
    ),
    (
        ("latency36 buffer36 queue36 worker36 kernel36 signal36", 6),
        ["latency36", "buffer36", "queue36", "worker36", "kernel36", "signal36"],
    ),
    (
        ("latency36 buffer36 queue36 worker36 kernel36 signal36", 10),
        ["latency36", "buffer36", "queue36", "worker36", "kernel36", "signal36"],
    ),
    (
        ("latency36 buffer36 queue36 worker36 kernel36 signal36", 18),
        ["latency36 buffer36", "queue36 worker36", "kernel36 signal36"],
    ),
    (
        ("latency36 buffer36 queue36 worker36 kernel36 signal36", 28),
        ["latency36 buffer36 queue36", "worker36 kernel36 signal36"],
    ),
    (
        ("buffer36 queue36 worker36 kernel36 signal36 packet36", 6),
        ["buffer36", "queue36", "worker36", "kernel36", "signal36", "packet36"],
    ),
    (
        ("buffer36 queue36 worker36 kernel36 signal36 packet36", 10),
        ["buffer36", "queue36", "worker36", "kernel36", "signal36", "packet36"],
    ),
    (
        ("buffer36 queue36 worker36 kernel36 signal36 packet36", 18),
        ["buffer36 queue36", "worker36 kernel36", "signal36 packet36"],
    ),
    (
        ("buffer36 queue36 worker36 kernel36 signal36 packet36", 28),
        ["buffer36 queue36 worker36", "kernel36 signal36 packet36"],
    ),
    (
        ("queue36 worker36 kernel36 signal36 packet36 router36", 6),
        ["queue36", "worker36", "kernel36", "signal36", "packet36", "router36"],
    ),
    (
        ("queue36 worker36 kernel36 signal36 packet36 router36", 10),
        ["queue36", "worker36", "kernel36", "signal36", "packet36", "router36"],
    ),
    (
        ("queue36 worker36 kernel36 signal36 packet36 router36", 18),
        ["queue36 worker36", "kernel36 signal36", "packet36 router36"],
    ),
    (
        ("queue36 worker36 kernel36 signal36 packet36 router36", 28),
        ["queue36 worker36 kernel36", "signal36 packet36 router36"],
    ),
    (
        ("worker36 kernel36 signal36 packet36 router36 cluster36", 6),
        ["worker36", "kernel36", "signal36", "packet36", "router36", "cluster36"],
    ),
    (
        ("worker36 kernel36 signal36 packet36 router36 cluster36", 10),
        ["worker36", "kernel36", "signal36", "packet36", "router36", "cluster36"],
    ),
    (
        ("worker36 kernel36 signal36 packet36 router36 cluster36", 18),
        ["worker36 kernel36", "signal36 packet36", "router36 cluster36"],
    ),
    (
        ("worker36 kernel36 signal36 packet36 router36 cluster36", 28),
        ["worker36 kernel36 signal36", "packet36 router36 cluster36"],
    ),
    (
        ("kernel36 signal36 packet36 router36 cluster36 mirror36", 6),
        ["kernel36", "signal36", "packet36", "router36", "cluster36", "mirror36"],
    ),
    (
        ("kernel36 signal36 packet36 router36 cluster36 mirror36", 10),
        ["kernel36", "signal36", "packet36", "router36", "cluster36", "mirror36"],
    ),
    (
        ("kernel36 signal36 packet36 router36 cluster36 mirror36", 18),
        ["kernel36 signal36", "packet36 router36", "cluster36 mirror36"],
    ),
    (
        ("kernel36 signal36 packet36 router36 cluster36 mirror36", 28),
        ["kernel36 signal36 packet36", "router36 cluster36 mirror36"],
    ),
    (
        ("signal36 packet36 router36 cluster36 mirror36 filter36", 6),
        ["signal36", "packet36", "router36", "cluster36", "mirror36", "filter36"],
    ),
    (
        ("signal36 packet36 router36 cluster36 mirror36 filter36", 10),
        ["signal36", "packet36", "router36", "cluster36", "mirror36", "filter36"],
    ),
    (
        ("signal36 packet36 router36 cluster36 mirror36 filter36", 18),
        ["signal36 packet36", "router36 cluster36", "mirror36 filter36"],
    ),
    (
        ("signal36 packet36 router36 cluster36 mirror36 filter36", 28),
        ["signal36 packet36 router36", "cluster36 mirror36 filter36"],
    ),
    (
        ("packet36 router36 cluster36 mirror36 filter36 ranking36", 6),
        ["packet36", "router36", "cluster36", "mirror36", "filter36", "ranking36"],
    ),
    (
        ("packet36 router36 cluster36 mirror36 filter36 ranking36", 10),
        ["packet36", "router36", "cluster36", "mirror36", "filter36", "ranking36"],
    ),
    (
        ("packet36 router36 cluster36 mirror36 filter36 ranking36", 18),
        ["packet36 router36", "cluster36 mirror36", "filter36 ranking36"],
    ),
    (
        ("packet36 router36 cluster36 mirror36 filter36 ranking36", 28),
        ["packet36 router36 cluster36", "mirror36 filter36 ranking36"],
    ),
    (
        ("router36 cluster36 mirror36 filter36 ranking36 encoding36", 6),
        ["router36", "cluster36", "mirror36", "filter36", "ranking36", "encoding36"],
    ),
    (
        ("router36 cluster36 mirror36 filter36 ranking36 encoding36", 10),
        ["router36", "cluster36", "mirror36", "filter36", "ranking36", "encoding36"],
    ),
    (
        ("router36 cluster36 mirror36 filter36 ranking36 encoding36", 18),
        ["router36 cluster36", "mirror36 filter36", "ranking36", "encoding36"],
    ),
    (
        ("router36 cluster36 mirror36 filter36 ranking36 encoding36", 28),
        ["router36 cluster36 mirror36", "filter36 ranking36", "encoding36"],
    ),
    (
        ("cluster36 mirror36 filter36 ranking36 encoding36 mapping36", 6),
        ["cluster36", "mirror36", "filter36", "ranking36", "encoding36", "mapping36"],
    ),
    (
        ("cluster36 mirror36 filter36 ranking36 encoding36 mapping36", 10),
        ["cluster36", "mirror36", "filter36", "ranking36", "encoding36", "mapping36"],
    ),
    (
        ("cluster36 mirror36 filter36 ranking36 encoding36 mapping36", 18),
        ["cluster36 mirror36", "filter36 ranking36", "encoding36", "mapping36"],
    ),
    (
        ("cluster36 mirror36 filter36 ranking36 encoding36 mapping36", 28),
        ["cluster36 mirror36 filter36", "ranking36 encoding36", "mapping36"],
    ),
    (
        ("mirror36 filter36 ranking36 encoding36 mapping36 record36", 6),
        ["mirror36", "filter36", "ranking36", "encoding36", "mapping36", "record36"],
    ),
    (
        ("mirror36 filter36 ranking36 encoding36 mapping36 record36", 10),
        ["mirror36", "filter36", "ranking36", "encoding36", "mapping36", "record36"],
    ),
    (
        ("mirror36 filter36 ranking36 encoding36 mapping36 record36", 18),
        ["mirror36 filter36", "ranking36", "encoding36", "mapping36 record36"],
    ),
    (
        ("mirror36 filter36 ranking36 encoding36 mapping36 record36", 28),
        ["mirror36 filter36 ranking36", "encoding36 mapping36", "record36"],
    ),
    (
        ("filter36 ranking36 encoding36 mapping36 record36 candle36", 6),
        ["filter36", "ranking36", "encoding36", "mapping36", "record36", "candle36"],
    ),
    (
        ("filter36 ranking36 encoding36 mapping36 record36 candle36", 10),
        ["filter36", "ranking36", "encoding36", "mapping36", "record36", "candle36"],
    ),
    (
        ("filter36 ranking36 encoding36 mapping36 record36 candle36", 18),
        ["filter36 ranking36", "encoding36", "mapping36 record36", "candle36"],
    ),
    (
        ("filter36 ranking36 encoding36 mapping36 record36 candle36", 28),
        ["filter36 ranking36", "encoding36 mapping36", "record36 candle36"],
    ),
    (
        ("ranking36 encoding36 mapping36 record36 candle36 thread36", 6),
        ["ranking36", "encoding36", "mapping36", "record36", "candle36", "thread36"],
    ),
    (
        ("ranking36 encoding36 mapping36 record36 candle36 thread36", 10),
        ["ranking36", "encoding36", "mapping36", "record36", "candle36", "thread36"],
    ),
    (
        ("ranking36 encoding36 mapping36 record36 candle36 thread36", 18),
        ["ranking36", "encoding36", "mapping36 record36", "candle36 thread36"],
    ),
    (
        ("ranking36 encoding36 mapping36 record36 candle36 thread36", 28),
        ["ranking36 encoding36", "mapping36 record36 candle36", "thread36"],
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
