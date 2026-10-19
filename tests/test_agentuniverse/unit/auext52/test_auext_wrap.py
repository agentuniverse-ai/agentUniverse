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
        ("round 52: the quick brown fox jumps over the lazy dog", 4),
        ["round", "52:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 52: the quick brown fox jumps over the lazy dog", 8),
        ["round", "52: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 52: the quick brown fox jumps over the lazy dog", 12),
        ["round 52:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 52: the quick brown fox jumps over the lazy dog", 16),
        ["round 52: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 52: the quick brown fox jumps over the lazy dog", 24),
        ["round 52: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 52: the quick brown fox jumps over the lazy dog", 32),
        ["round 52: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 52: agentuniverse is a framework for multi agents", 4),
        ["round", "52:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 52: agentuniverse is a framework for multi agents", 8),
        ["round", "52:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 52: agentuniverse is a framework for multi agents", 12),
        ["round 52:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 52: agentuniverse is a framework for multi agents", 16),
        ["round 52:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 52: agentuniverse is a framework for multi agents", 24),
        ["round 52: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 52: agentuniverse is a framework for multi agents", 32),
        ["round 52: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 52: knowledge stored as vectors enables retrieval", 4),
        ["round", "52:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 52: knowledge stored as vectors enables retrieval", 8),
        ["round", "52:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 52: knowledge stored as vectors enables retrieval", 12),
        ["round 52:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 52: knowledge stored as vectors enables retrieval", 16),
        ["round 52:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 52: knowledge stored as vectors enables retrieval", 24),
        ["round 52: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 52: knowledge stored as vectors enables retrieval", 32),
        ["round 52: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 52: the processor reads the record then stops", 4),
        ["round", "52:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 52: the processor reads the record then stops", 8),
        ["round", "52: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 52: the processor reads the record then stops", 12),
        ["round 52:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 52: the processor reads the record then stops", 16),
        ["round 52: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 52: the processor reads the record then stops", 24),
        ["round 52: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 52: the processor reads the record then stops", 32),
        ["round 52: the processor reads", "the record then stops"],
    ),
    (
        ("round 52: a worker pulls the next task from the queue", 4),
        ["round", "52:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 52: a worker pulls the next task from the queue", 8),
        ["round", "52: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 52: a worker pulls the next task from the queue", 12),
        ["round 52: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 52: a worker pulls the next task from the queue", 16),
        ["round 52: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 52: a worker pulls the next task from the queue", 24),
        ["round 52: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 52: a worker pulls the next task from the queue", 32),
        ["round 52: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 52: signals travel through the network layer", 4),
        ["round", "52:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 52: signals travel through the network layer", 8),
        ["round", "52:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 52: signals travel through the network layer", 12),
        ["round 52:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 52: signals travel through the network layer", 16),
        ["round 52:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 52: signals travel through the network layer", 24),
        ["round 52: signals travel", "through the network", "layer"],
    ),
    (
        ("round 52: signals travel through the network layer", 32),
        ["round 52: signals travel through", "the network layer"],
    ),
    (
        ("round 52: the gateway routes each request by policy", 4),
        ["round", "52:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 52: the gateway routes each request by policy", 8),
        ["round", "52: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 52: the gateway routes each request by policy", 12),
        ["round 52:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 52: the gateway routes each request by policy", 16),
        ["round 52: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 52: the gateway routes each request by policy", 24),
        ["round 52: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 52: the gateway routes each request by policy", 32),
        ["round 52: the gateway routes", "each request by policy"],
    ),
    (
        ("round 52: memory grows until the buffer is full", 4),
        ["round", "52:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 52: memory grows until the buffer is full", 8),
        ["round", "52:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 52: memory grows until the buffer is full", 12),
        ["round 52:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 52: memory grows until the buffer is full", 16),
        ["round 52: memory", "grows until the", "buffer is full"],
    ),
    (("round 52: memory grows until the buffer is full", 24), ["round 52: memory grows", "until the buffer is full"]),
    (("round 52: memory grows until the buffer is full", 32), ["round 52: memory grows until the", "buffer is full"]),
    (
        ("round 52: the cluster mirrors every packet twice", 4),
        ["round", "52:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 52: the cluster mirrors every packet twice", 8),
        ["round", "52: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 52: the cluster mirrors every packet twice", 12),
        ["round 52:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 52: the cluster mirrors every packet twice", 16),
        ["round 52: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 52: the cluster mirrors every packet twice", 24),
        ["round 52: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 52: the cluster mirrors every packet twice", 32), ["round 52: the cluster mirrors", "every packet twice"]),
    (
        ("round 52: ranking uses tokens learned from the corpus", 4),
        ["round", "52:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 52: ranking uses tokens learned from the corpus", 8),
        ["round", "52:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 52: ranking uses tokens learned from the corpus", 12),
        ["round 52:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 52: ranking uses tokens learned from the corpus", 16),
        ["round 52:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 52: ranking uses tokens learned from the corpus", 24),
        ["round 52: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 52: ranking uses tokens learned from the corpus", 32),
        ["round 52: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 52: a long session ends when the candle dies", 4),
        ["round", "52:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 52: a long session ends when the candle dies", 8),
        ["round", "52: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 52: a long session ends when the candle dies", 12),
        ["round 52: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 52: a long session ends when the candle dies", 16),
        ["round 52: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 52: a long session ends when the candle dies", 24),
        ["round 52: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 52: a long session ends when the candle dies", 32),
        ["round 52: a long session ends", "when the candle dies"],
    ),
    (
        ("round 52: encode the prompt then map the result", 4),
        ["round", "52:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 52: encode the prompt then map the result", 8),
        ["round", "52:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 52: encode the prompt then map the result", 12),
        ["round 52:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 52: encode the prompt then map the result", 16),
        ["round 52: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 52: encode the prompt then map the result", 24),
        ["round 52: encode the", "prompt then map the", "result"],
    ),
    (("round 52: encode the prompt then map the result", 32), ["round 52: encode the prompt then", "map the result"]),
    (
        ("round 52: the kernel wakes the worker at dawn", 4),
        ["round", "52:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 52: the kernel wakes the worker at dawn", 8),
        ["round", "52: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 52: the kernel wakes the worker at dawn", 12),
        ["round 52:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 52: the kernel wakes the worker at dawn", 16), ["round 52: the", "kernel wakes the", "worker at dawn"]),
    (("round 52: the kernel wakes the worker at dawn", 24), ["round 52: the kernel", "wakes the worker at dawn"]),
    (("round 52: the kernel wakes the worker at dawn", 32), ["round 52: the kernel wakes the", "worker at dawn"]),
    (
        ("round 52: service latency drops after the patch", 4),
        ["round", "52:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 52: service latency drops after the patch", 8),
        ["round", "52:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 52: service latency drops after the patch", 12),
        ["round 52:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 52: service latency drops after the patch", 16),
        ["round 52:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 52: service latency drops after the patch", 24),
        ["round 52: service", "latency drops after the", "patch"],
    ),
    (("round 52: service latency drops after the patch", 32), ["round 52: service latency drops", "after the patch"]),
    (
        ("round 52: the library caches every vector it sees", 4),
        ["round", "52:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 52: the library caches every vector it sees", 8),
        ["round", "52: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 52: the library caches every vector it sees", 12),
        ["round 52:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 52: the library caches every vector it sees", 16),
        ["round 52: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 52: the library caches every vector it sees", 24),
        ["round 52: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 52: the library caches every vector it sees", 32),
        ["round 52: the library caches", "every vector it sees"],
    ),
    (
        ("round 52: agents argue then the debate resolves", 4),
        ["round", "52:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 52: agents argue then the debate resolves", 8),
        ["round", "52:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 52: agents argue then the debate resolves", 12),
        ["round 52:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 52: agents argue then the debate resolves", 16),
        ["round 52: agents", "argue then the", "debate resolves"],
    ),
    (("round 52: agents argue then the debate resolves", 24), ["round 52: agents argue", "then the debate resolves"]),
    (("round 52: agents argue then the debate resolves", 32), ["round 52: agents argue then the", "debate resolves"]),
    (
        ("round 52: the filter keeps only strong matches", 4),
        ["round", "52:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 52: the filter keeps only strong matches", 8),
        ["round", "52: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 52: the filter keeps only strong matches", 12),
        ["round 52:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 52: the filter keeps only strong matches", 16),
        ["round 52: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 52: the filter keeps only strong matches", 24), ["round 52: the filter", "keeps only strong", "matches"]),
    (("round 52: the filter keeps only strong matches", 32), ["round 52: the filter keeps only", "strong matches"]),
    (
        ("round 52: the model answers with a short reply", 4),
        ["round", "52:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 52: the model answers with a short reply", 8),
        ["round", "52: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 52: the model answers with a short reply", 12),
        ["round 52:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 52: the model answers with a short reply", 16),
        ["round 52: the", "model answers", "with a short", "reply"],
    ),
    (("round 52: the model answers with a short reply", 24), ["round 52: the model", "answers with a short", "reply"]),
    (("round 52: the model answers with a short reply", 32), ["round 52: the model answers with", "a short reply"]),
    (
        ("round 52: the recorder stores the reasoning trace", 4),
        ["round", "52:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 52: the recorder stores the reasoning trace", 8),
        ["round", "52: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 52: the recorder stores the reasoning trace", 12),
        ["round 52:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 52: the recorder stores the reasoning trace", 16),
        ["round 52: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 52: the recorder stores the reasoning trace", 24),
        ["round 52: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 52: the recorder stores the reasoning trace", 32),
        ["round 52: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 52: the angel watches the processor run", 4),
        ["round", "52:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 52: the angel watches the processor run", 8),
        ["round", "52: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 52: the angel watches the processor run", 12),
        ["round 52:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 52: the angel watches the processor run", 16), ["round 52: the", "angel watches", "the processor", "run"]),
    (("round 52: the angel watches the processor run", 24), ["round 52: the angel", "watches the processor", "run"]),
    (("round 52: the angel watches the processor run", 32), ["round 52: the angel watches the", "processor run"]),
    (
        ("round 52: angle of the vector decides the match", 4),
        ["round", "52:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 52: angle of the vector decides the match", 8),
        ["round", "52:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 52: angle of the vector decides the match", 12),
        ["round 52:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 52: angle of the vector decides the match", 16),
        ["round 52: angle", "of the vector", "decides the", "match"],
    ),
    (("round 52: angle of the vector decides the match", 24), ["round 52: angle of the", "vector decides the match"]),
    (("round 52: angle of the vector decides the match", 32), ["round 52: angle of the vector", "decides the match"]),
    (
        ("round 52: the candle burns twice as long at night", 4),
        ["round", "52:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 52: the candle burns twice as long at night", 8),
        ["round", "52: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 52: the candle burns twice as long at night", 12),
        ["round 52:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 52: the candle burns twice as long at night", 16),
        ["round 52: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 52: the candle burns twice as long at night", 24),
        ["round 52: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 52: the candle burns twice as long at night", 32),
        ["round 52: the candle burns twice", "as long at night"],
    ),
    (
        ("round 52: a mirror of the universe in one line", 4),
        ["round", "52:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 52: a mirror of the universe in one line", 8),
        ["round", "52: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 52: a mirror of the universe in one line", 12),
        ["round 52: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 52: a mirror of the universe in one line", 16),
        ["round 52: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 52: a mirror of the universe in one line", 24), ["round 52: a mirror of", "the universe in one line"]),
    (("round 52: a mirror of the universe in one line", 32), ["round 52: a mirror of the", "universe in one line"]),
    (
        ("round 52: the queue drains before the storm", 4),
        ["round", "52:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 52: the queue drains before the storm", 8),
        ["round", "52: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 52: the queue drains before the storm", 12), ["round 52:", "the queue", "drains", "before the", "storm"]),
    (("round 52: the queue drains before the storm", 16), ["round 52: the", "queue drains", "before the storm"]),
    (("round 52: the queue drains before the storm", 24), ["round 52: the queue", "drains before the storm"]),
    (("round 52: the queue drains before the storm", 32), ["round 52: the queue drains", "before the storm"]),
    (
        ("kitten52 sitting52 agent52 angle52 universe52 memory52", 6),
        ["kitten52", "sitting52", "agent52", "angle52", "universe52", "memory52"],
    ),
    (
        ("kitten52 sitting52 agent52 angle52 universe52 memory52", 10),
        ["kitten52", "sitting52", "agent52", "angle52", "universe52", "memory52"],
    ),
    (
        ("kitten52 sitting52 agent52 angle52 universe52 memory52", 18),
        ["kitten52 sitting52", "agent52 angle52", "universe52", "memory52"],
    ),
    (
        ("kitten52 sitting52 agent52 angle52 universe52 memory52", 28),
        ["kitten52 sitting52 agent52", "angle52 universe52 memory52"],
    ),
    (
        ("sitting52 agent52 angle52 universe52 memory52 stream52", 6),
        ["sitting52", "agent52", "angle52", "universe52", "memory52", "stream52"],
    ),
    (
        ("sitting52 agent52 angle52 universe52 memory52 stream52", 10),
        ["sitting52", "agent52", "angle52", "universe52", "memory52", "stream52"],
    ),
    (
        ("sitting52 agent52 angle52 universe52 memory52 stream52", 18),
        ["sitting52 agent52", "angle52 universe52", "memory52 stream52"],
    ),
    (
        ("sitting52 agent52 angle52 universe52 memory52 stream52", 28),
        ["sitting52 agent52 angle52", "universe52 memory52 stream52"],
    ),
    (
        ("agent52 angle52 universe52 memory52 stream52 context52", 6),
        ["agent52", "angle52", "universe52", "memory52", "stream52", "context52"],
    ),
    (
        ("agent52 angle52 universe52 memory52 stream52 context52", 10),
        ["agent52", "angle52", "universe52", "memory52", "stream52", "context52"],
    ),
    (
        ("agent52 angle52 universe52 memory52 stream52 context52", 18),
        ["agent52 angle52", "universe52", "memory52 stream52", "context52"],
    ),
    (
        ("agent52 angle52 universe52 memory52 stream52 context52", 28),
        ["agent52 angle52 universe52", "memory52 stream52 context52"],
    ),
    (
        ("angle52 universe52 memory52 stream52 context52 knowledge52", 6),
        ["angle52", "universe52", "memory52", "stream52", "context52", "knowledge52"],
    ),
    (
        ("angle52 universe52 memory52 stream52 context52 knowledge52", 10),
        ["angle52", "universe52", "memory52", "stream52", "context52", "knowledge52"],
    ),
    (
        ("angle52 universe52 memory52 stream52 context52 knowledge52", 18),
        ["angle52 universe52", "memory52 stream52", "context52", "knowledge52"],
    ),
    (
        ("angle52 universe52 memory52 stream52 context52 knowledge52", 28),
        ["angle52 universe52 memory52", "stream52 context52", "knowledge52"],
    ),
    (
        ("universe52 memory52 stream52 context52 knowledge52 vector52", 6),
        ["universe52", "memory52", "stream52", "context52", "knowledge52", "vector52"],
    ),
    (
        ("universe52 memory52 stream52 context52 knowledge52 vector52", 10),
        ["universe52", "memory52", "stream52", "context52", "knowledge52", "vector52"],
    ),
    (
        ("universe52 memory52 stream52 context52 knowledge52 vector52", 18),
        ["universe52", "memory52 stream52", "context52", "knowledge52", "vector52"],
    ),
    (
        ("universe52 memory52 stream52 context52 knowledge52 vector52", 28),
        ["universe52 memory52 stream52", "context52 knowledge52", "vector52"],
    ),
    (
        ("memory52 stream52 context52 knowledge52 vector52 processor52", 6),
        ["memory52", "stream52", "context52", "knowledge52", "vector52", "processor52"],
    ),
    (
        ("memory52 stream52 context52 knowledge52 vector52 processor52", 10),
        ["memory52", "stream52", "context52", "knowledge52", "vector52", "processor52"],
    ),
    (
        ("memory52 stream52 context52 knowledge52 vector52 processor52", 18),
        ["memory52 stream52", "context52", "knowledge52", "vector52", "processor52"],
    ),
    (
        ("memory52 stream52 context52 knowledge52 vector52 processor52", 28),
        ["memory52 stream52 context52", "knowledge52 vector52", "processor52"],
    ),
    (
        ("stream52 context52 knowledge52 vector52 processor52 reasoning52", 6),
        ["stream52", "context52", "knowledge52", "vector52", "processor52", "reasoning52"],
    ),
    (
        ("stream52 context52 knowledge52 vector52 processor52 reasoning52", 10),
        ["stream52", "context52", "knowledge52", "vector52", "processor52", "reasoning52"],
    ),
    (
        ("stream52 context52 knowledge52 vector52 processor52 reasoning52", 18),
        ["stream52 context52", "knowledge52", "vector52", "processor52", "reasoning52"],
    ),
    (
        ("stream52 context52 knowledge52 vector52 processor52 reasoning52", 28),
        ["stream52 context52", "knowledge52 vector52", "processor52 reasoning52"],
    ),
    (
        ("context52 knowledge52 vector52 processor52 reasoning52 machine52", 6),
        ["context52", "knowledge52", "vector52", "processor52", "reasoning52", "machine52"],
    ),
    (
        ("context52 knowledge52 vector52 processor52 reasoning52 machine52", 10),
        ["context52", "knowledge52", "vector52", "processor52", "reasoning52", "machine52"],
    ),
    (
        ("context52 knowledge52 vector52 processor52 reasoning52 machine52", 18),
        ["context52", "knowledge52", "vector52", "processor52", "reasoning52", "machine52"],
    ),
    (
        ("context52 knowledge52 vector52 processor52 reasoning52 machine52", 28),
        ["context52 knowledge52", "vector52 processor52", "reasoning52 machine52"],
    ),
    (
        ("knowledge52 vector52 processor52 reasoning52 machine52 learning52", 6),
        ["knowledge52", "vector52", "processor52", "reasoning52", "machine52", "learning52"],
    ),
    (
        ("knowledge52 vector52 processor52 reasoning52 machine52 learning52", 10),
        ["knowledge52", "vector52", "processor52", "reasoning52", "machine52", "learning52"],
    ),
    (
        ("knowledge52 vector52 processor52 reasoning52 machine52 learning52", 18),
        ["knowledge52", "vector52", "processor52", "reasoning52", "machine52", "learning52"],
    ),
    (
        ("knowledge52 vector52 processor52 reasoning52 machine52 learning52", 28),
        ["knowledge52 vector52", "processor52 reasoning52", "machine52 learning52"],
    ),
    (
        ("vector52 processor52 reasoning52 machine52 learning52 model52", 6),
        ["vector52", "processor52", "reasoning52", "machine52", "learning52", "model52"],
    ),
    (
        ("vector52 processor52 reasoning52 machine52 learning52 model52", 10),
        ["vector52", "processor52", "reasoning52", "machine52", "learning52", "model52"],
    ),
    (
        ("vector52 processor52 reasoning52 machine52 learning52 model52", 18),
        ["vector52", "processor52", "reasoning52", "machine52", "learning52 model52"],
    ),
    (
        ("vector52 processor52 reasoning52 machine52 learning52 model52", 28),
        ["vector52 processor52", "reasoning52 machine52", "learning52 model52"],
    ),
    (
        ("processor52 reasoning52 machine52 learning52 model52 token52", 6),
        ["processor52", "reasoning52", "machine52", "learning52", "model52", "token52"],
    ),
    (
        ("processor52 reasoning52 machine52 learning52 model52 token52", 10),
        ["processor52", "reasoning52", "machine52", "learning52", "model52", "token52"],
    ),
    (
        ("processor52 reasoning52 machine52 learning52 model52 token52", 18),
        ["processor52", "reasoning52", "machine52", "learning52 model52", "token52"],
    ),
    (
        ("processor52 reasoning52 machine52 learning52 model52 token52", 28),
        ["processor52 reasoning52", "machine52 learning52 model52", "token52"],
    ),
    (
        ("reasoning52 machine52 learning52 model52 token52 prompt52", 6),
        ["reasoning52", "machine52", "learning52", "model52", "token52", "prompt52"],
    ),
    (
        ("reasoning52 machine52 learning52 model52 token52 prompt52", 10),
        ["reasoning52", "machine52", "learning52", "model52", "token52", "prompt52"],
    ),
    (
        ("reasoning52 machine52 learning52 model52 token52 prompt52", 18),
        ["reasoning52", "machine52", "learning52 model52", "token52 prompt52"],
    ),
    (
        ("reasoning52 machine52 learning52 model52 token52 prompt52", 28),
        ["reasoning52 machine52", "learning52 model52 token52", "prompt52"],
    ),
    (
        ("machine52 learning52 model52 token52 prompt52 session52", 6),
        ["machine52", "learning52", "model52", "token52", "prompt52", "session52"],
    ),
    (
        ("machine52 learning52 model52 token52 prompt52 session52", 10),
        ["machine52", "learning52", "model52", "token52", "prompt52", "session52"],
    ),
    (
        ("machine52 learning52 model52 token52 prompt52 session52", 18),
        ["machine52", "learning52 model52", "token52 prompt52", "session52"],
    ),
    (
        ("machine52 learning52 model52 token52 prompt52 session52", 28),
        ["machine52 learning52 model52", "token52 prompt52 session52"],
    ),
    (
        ("learning52 model52 token52 prompt52 session52 library52", 6),
        ["learning52", "model52", "token52", "prompt52", "session52", "library52"],
    ),
    (
        ("learning52 model52 token52 prompt52 session52 library52", 10),
        ["learning52", "model52", "token52", "prompt52", "session52", "library52"],
    ),
    (
        ("learning52 model52 token52 prompt52 session52 library52", 18),
        ["learning52 model52", "token52 prompt52", "session52", "library52"],
    ),
    (
        ("learning52 model52 token52 prompt52 session52 library52", 28),
        ["learning52 model52 token52", "prompt52 session52 library52"],
    ),
    (
        ("model52 token52 prompt52 session52 library52 service52", 6),
        ["model52", "token52", "prompt52", "session52", "library52", "service52"],
    ),
    (
        ("model52 token52 prompt52 session52 library52 service52", 10),
        ["model52", "token52", "prompt52", "session52", "library52", "service52"],
    ),
    (
        ("model52 token52 prompt52 session52 library52 service52", 18),
        ["model52 token52", "prompt52 session52", "library52", "service52"],
    ),
    (
        ("model52 token52 prompt52 session52 library52 service52", 28),
        ["model52 token52 prompt52", "session52 library52", "service52"],
    ),
    (
        ("token52 prompt52 session52 library52 service52 gateway52", 6),
        ["token52", "prompt52", "session52", "library52", "service52", "gateway52"],
    ),
    (
        ("token52 prompt52 session52 library52 service52 gateway52", 10),
        ["token52", "prompt52", "session52", "library52", "service52", "gateway52"],
    ),
    (
        ("token52 prompt52 session52 library52 service52 gateway52", 18),
        ["token52 prompt52", "session52", "library52", "service52", "gateway52"],
    ),
    (
        ("token52 prompt52 session52 library52 service52 gateway52", 28),
        ["token52 prompt52 session52", "library52 service52", "gateway52"],
    ),
    (
        ("prompt52 session52 library52 service52 gateway52 storage52", 6),
        ["prompt52", "session52", "library52", "service52", "gateway52", "storage52"],
    ),
    (
        ("prompt52 session52 library52 service52 gateway52 storage52", 10),
        ["prompt52", "session52", "library52", "service52", "gateway52", "storage52"],
    ),
    (
        ("prompt52 session52 library52 service52 gateway52 storage52", 18),
        ["prompt52 session52", "library52", "service52", "gateway52", "storage52"],
    ),
    (
        ("prompt52 session52 library52 service52 gateway52 storage52", 28),
        ["prompt52 session52 library52", "service52 gateway52", "storage52"],
    ),
    (
        ("session52 library52 service52 gateway52 storage52 network52", 6),
        ["session52", "library52", "service52", "gateway52", "storage52", "network52"],
    ),
    (
        ("session52 library52 service52 gateway52 storage52 network52", 10),
        ["session52", "library52", "service52", "gateway52", "storage52", "network52"],
    ),
    (
        ("session52 library52 service52 gateway52 storage52 network52", 18),
        ["session52", "library52", "service52", "gateway52", "storage52", "network52"],
    ),
    (
        ("session52 library52 service52 gateway52 storage52 network52", 28),
        ["session52 library52", "service52 gateway52", "storage52 network52"],
    ),
    (
        ("library52 service52 gateway52 storage52 network52 latency52", 6),
        ["library52", "service52", "gateway52", "storage52", "network52", "latency52"],
    ),
    (
        ("library52 service52 gateway52 storage52 network52 latency52", 10),
        ["library52", "service52", "gateway52", "storage52", "network52", "latency52"],
    ),
    (
        ("library52 service52 gateway52 storage52 network52 latency52", 18),
        ["library52", "service52", "gateway52", "storage52", "network52", "latency52"],
    ),
    (
        ("library52 service52 gateway52 storage52 network52 latency52", 28),
        ["library52 service52", "gateway52 storage52", "network52 latency52"],
    ),
    (
        ("service52 gateway52 storage52 network52 latency52 buffer52", 6),
        ["service52", "gateway52", "storage52", "network52", "latency52", "buffer52"],
    ),
    (
        ("service52 gateway52 storage52 network52 latency52 buffer52", 10),
        ["service52", "gateway52", "storage52", "network52", "latency52", "buffer52"],
    ),
    (
        ("service52 gateway52 storage52 network52 latency52 buffer52", 18),
        ["service52", "gateway52", "storage52", "network52", "latency52 buffer52"],
    ),
    (
        ("service52 gateway52 storage52 network52 latency52 buffer52", 28),
        ["service52 gateway52", "storage52 network52", "latency52 buffer52"],
    ),
    (
        ("gateway52 storage52 network52 latency52 buffer52 queue52", 6),
        ["gateway52", "storage52", "network52", "latency52", "buffer52", "queue52"],
    ),
    (
        ("gateway52 storage52 network52 latency52 buffer52 queue52", 10),
        ["gateway52", "storage52", "network52", "latency52", "buffer52", "queue52"],
    ),
    (
        ("gateway52 storage52 network52 latency52 buffer52 queue52", 18),
        ["gateway52", "storage52", "network52", "latency52 buffer52", "queue52"],
    ),
    (
        ("gateway52 storage52 network52 latency52 buffer52 queue52", 28),
        ["gateway52 storage52", "network52 latency52 buffer52", "queue52"],
    ),
    (
        ("storage52 network52 latency52 buffer52 queue52 worker52", 6),
        ["storage52", "network52", "latency52", "buffer52", "queue52", "worker52"],
    ),
    (
        ("storage52 network52 latency52 buffer52 queue52 worker52", 10),
        ["storage52", "network52", "latency52", "buffer52", "queue52", "worker52"],
    ),
    (
        ("storage52 network52 latency52 buffer52 queue52 worker52", 18),
        ["storage52", "network52", "latency52 buffer52", "queue52 worker52"],
    ),
    (
        ("storage52 network52 latency52 buffer52 queue52 worker52", 28),
        ["storage52 network52", "latency52 buffer52 queue52", "worker52"],
    ),
    (
        ("network52 latency52 buffer52 queue52 worker52 kernel52", 6),
        ["network52", "latency52", "buffer52", "queue52", "worker52", "kernel52"],
    ),
    (
        ("network52 latency52 buffer52 queue52 worker52 kernel52", 10),
        ["network52", "latency52", "buffer52", "queue52", "worker52", "kernel52"],
    ),
    (
        ("network52 latency52 buffer52 queue52 worker52 kernel52", 18),
        ["network52", "latency52 buffer52", "queue52 worker52", "kernel52"],
    ),
    (
        ("network52 latency52 buffer52 queue52 worker52 kernel52", 28),
        ["network52 latency52 buffer52", "queue52 worker52 kernel52"],
    ),
    (
        ("latency52 buffer52 queue52 worker52 kernel52 signal52", 6),
        ["latency52", "buffer52", "queue52", "worker52", "kernel52", "signal52"],
    ),
    (
        ("latency52 buffer52 queue52 worker52 kernel52 signal52", 10),
        ["latency52", "buffer52", "queue52", "worker52", "kernel52", "signal52"],
    ),
    (
        ("latency52 buffer52 queue52 worker52 kernel52 signal52", 18),
        ["latency52 buffer52", "queue52 worker52", "kernel52 signal52"],
    ),
    (
        ("latency52 buffer52 queue52 worker52 kernel52 signal52", 28),
        ["latency52 buffer52 queue52", "worker52 kernel52 signal52"],
    ),
    (
        ("buffer52 queue52 worker52 kernel52 signal52 packet52", 6),
        ["buffer52", "queue52", "worker52", "kernel52", "signal52", "packet52"],
    ),
    (
        ("buffer52 queue52 worker52 kernel52 signal52 packet52", 10),
        ["buffer52", "queue52", "worker52", "kernel52", "signal52", "packet52"],
    ),
    (
        ("buffer52 queue52 worker52 kernel52 signal52 packet52", 18),
        ["buffer52 queue52", "worker52 kernel52", "signal52 packet52"],
    ),
    (
        ("buffer52 queue52 worker52 kernel52 signal52 packet52", 28),
        ["buffer52 queue52 worker52", "kernel52 signal52 packet52"],
    ),
    (
        ("queue52 worker52 kernel52 signal52 packet52 router52", 6),
        ["queue52", "worker52", "kernel52", "signal52", "packet52", "router52"],
    ),
    (
        ("queue52 worker52 kernel52 signal52 packet52 router52", 10),
        ["queue52", "worker52", "kernel52", "signal52", "packet52", "router52"],
    ),
    (
        ("queue52 worker52 kernel52 signal52 packet52 router52", 18),
        ["queue52 worker52", "kernel52 signal52", "packet52 router52"],
    ),
    (
        ("queue52 worker52 kernel52 signal52 packet52 router52", 28),
        ["queue52 worker52 kernel52", "signal52 packet52 router52"],
    ),
    (
        ("worker52 kernel52 signal52 packet52 router52 cluster52", 6),
        ["worker52", "kernel52", "signal52", "packet52", "router52", "cluster52"],
    ),
    (
        ("worker52 kernel52 signal52 packet52 router52 cluster52", 10),
        ["worker52", "kernel52", "signal52", "packet52", "router52", "cluster52"],
    ),
    (
        ("worker52 kernel52 signal52 packet52 router52 cluster52", 18),
        ["worker52 kernel52", "signal52 packet52", "router52 cluster52"],
    ),
    (
        ("worker52 kernel52 signal52 packet52 router52 cluster52", 28),
        ["worker52 kernel52 signal52", "packet52 router52 cluster52"],
    ),
    (
        ("kernel52 signal52 packet52 router52 cluster52 mirror52", 6),
        ["kernel52", "signal52", "packet52", "router52", "cluster52", "mirror52"],
    ),
    (
        ("kernel52 signal52 packet52 router52 cluster52 mirror52", 10),
        ["kernel52", "signal52", "packet52", "router52", "cluster52", "mirror52"],
    ),
    (
        ("kernel52 signal52 packet52 router52 cluster52 mirror52", 18),
        ["kernel52 signal52", "packet52 router52", "cluster52 mirror52"],
    ),
    (
        ("kernel52 signal52 packet52 router52 cluster52 mirror52", 28),
        ["kernel52 signal52 packet52", "router52 cluster52 mirror52"],
    ),
    (
        ("signal52 packet52 router52 cluster52 mirror52 filter52", 6),
        ["signal52", "packet52", "router52", "cluster52", "mirror52", "filter52"],
    ),
    (
        ("signal52 packet52 router52 cluster52 mirror52 filter52", 10),
        ["signal52", "packet52", "router52", "cluster52", "mirror52", "filter52"],
    ),
    (
        ("signal52 packet52 router52 cluster52 mirror52 filter52", 18),
        ["signal52 packet52", "router52 cluster52", "mirror52 filter52"],
    ),
    (
        ("signal52 packet52 router52 cluster52 mirror52 filter52", 28),
        ["signal52 packet52 router52", "cluster52 mirror52 filter52"],
    ),
    (
        ("packet52 router52 cluster52 mirror52 filter52 ranking52", 6),
        ["packet52", "router52", "cluster52", "mirror52", "filter52", "ranking52"],
    ),
    (
        ("packet52 router52 cluster52 mirror52 filter52 ranking52", 10),
        ["packet52", "router52", "cluster52", "mirror52", "filter52", "ranking52"],
    ),
    (
        ("packet52 router52 cluster52 mirror52 filter52 ranking52", 18),
        ["packet52 router52", "cluster52 mirror52", "filter52 ranking52"],
    ),
    (
        ("packet52 router52 cluster52 mirror52 filter52 ranking52", 28),
        ["packet52 router52 cluster52", "mirror52 filter52 ranking52"],
    ),
    (
        ("router52 cluster52 mirror52 filter52 ranking52 encoding52", 6),
        ["router52", "cluster52", "mirror52", "filter52", "ranking52", "encoding52"],
    ),
    (
        ("router52 cluster52 mirror52 filter52 ranking52 encoding52", 10),
        ["router52", "cluster52", "mirror52", "filter52", "ranking52", "encoding52"],
    ),
    (
        ("router52 cluster52 mirror52 filter52 ranking52 encoding52", 18),
        ["router52 cluster52", "mirror52 filter52", "ranking52", "encoding52"],
    ),
    (
        ("router52 cluster52 mirror52 filter52 ranking52 encoding52", 28),
        ["router52 cluster52 mirror52", "filter52 ranking52", "encoding52"],
    ),
    (
        ("cluster52 mirror52 filter52 ranking52 encoding52 mapping52", 6),
        ["cluster52", "mirror52", "filter52", "ranking52", "encoding52", "mapping52"],
    ),
    (
        ("cluster52 mirror52 filter52 ranking52 encoding52 mapping52", 10),
        ["cluster52", "mirror52", "filter52", "ranking52", "encoding52", "mapping52"],
    ),
    (
        ("cluster52 mirror52 filter52 ranking52 encoding52 mapping52", 18),
        ["cluster52 mirror52", "filter52 ranking52", "encoding52", "mapping52"],
    ),
    (
        ("cluster52 mirror52 filter52 ranking52 encoding52 mapping52", 28),
        ["cluster52 mirror52 filter52", "ranking52 encoding52", "mapping52"],
    ),
    (
        ("mirror52 filter52 ranking52 encoding52 mapping52 record52", 6),
        ["mirror52", "filter52", "ranking52", "encoding52", "mapping52", "record52"],
    ),
    (
        ("mirror52 filter52 ranking52 encoding52 mapping52 record52", 10),
        ["mirror52", "filter52", "ranking52", "encoding52", "mapping52", "record52"],
    ),
    (
        ("mirror52 filter52 ranking52 encoding52 mapping52 record52", 18),
        ["mirror52 filter52", "ranking52", "encoding52", "mapping52 record52"],
    ),
    (
        ("mirror52 filter52 ranking52 encoding52 mapping52 record52", 28),
        ["mirror52 filter52 ranking52", "encoding52 mapping52", "record52"],
    ),
    (
        ("filter52 ranking52 encoding52 mapping52 record52 candle52", 6),
        ["filter52", "ranking52", "encoding52", "mapping52", "record52", "candle52"],
    ),
    (
        ("filter52 ranking52 encoding52 mapping52 record52 candle52", 10),
        ["filter52", "ranking52", "encoding52", "mapping52", "record52", "candle52"],
    ),
    (
        ("filter52 ranking52 encoding52 mapping52 record52 candle52", 18),
        ["filter52 ranking52", "encoding52", "mapping52 record52", "candle52"],
    ),
    (
        ("filter52 ranking52 encoding52 mapping52 record52 candle52", 28),
        ["filter52 ranking52", "encoding52 mapping52", "record52 candle52"],
    ),
    (
        ("ranking52 encoding52 mapping52 record52 candle52 thread52", 6),
        ["ranking52", "encoding52", "mapping52", "record52", "candle52", "thread52"],
    ),
    (
        ("ranking52 encoding52 mapping52 record52 candle52 thread52", 10),
        ["ranking52", "encoding52", "mapping52", "record52", "candle52", "thread52"],
    ),
    (
        ("ranking52 encoding52 mapping52 record52 candle52 thread52", 18),
        ["ranking52", "encoding52", "mapping52 record52", "candle52 thread52"],
    ),
    (
        ("ranking52 encoding52 mapping52 record52 candle52 thread52", 28),
        ["ranking52 encoding52", "mapping52 record52 candle52", "thread52"],
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
