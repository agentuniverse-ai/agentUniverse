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
        ("round 29: the quick brown fox jumps over the lazy dog", 4),
        ["round", "29:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 29: the quick brown fox jumps over the lazy dog", 8),
        ["round", "29: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 29: the quick brown fox jumps over the lazy dog", 12),
        ["round 29:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 29: the quick brown fox jumps over the lazy dog", 16),
        ["round 29: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 29: the quick brown fox jumps over the lazy dog", 24),
        ["round 29: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 29: the quick brown fox jumps over the lazy dog", 32),
        ["round 29: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 29: agentuniverse is a framework for multi agents", 4),
        ["round", "29:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 29: agentuniverse is a framework for multi agents", 8),
        ["round", "29:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 29: agentuniverse is a framework for multi agents", 12),
        ["round 29:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 29: agentuniverse is a framework for multi agents", 16),
        ["round 29:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 29: agentuniverse is a framework for multi agents", 24),
        ["round 29: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 29: agentuniverse is a framework for multi agents", 32),
        ["round 29: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 29: knowledge stored as vectors enables retrieval", 4),
        ["round", "29:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 29: knowledge stored as vectors enables retrieval", 8),
        ["round", "29:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 29: knowledge stored as vectors enables retrieval", 12),
        ["round 29:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 29: knowledge stored as vectors enables retrieval", 16),
        ["round 29:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 29: knowledge stored as vectors enables retrieval", 24),
        ["round 29: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 29: knowledge stored as vectors enables retrieval", 32),
        ["round 29: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 29: the processor reads the record then stops", 4),
        ["round", "29:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 29: the processor reads the record then stops", 8),
        ["round", "29: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 29: the processor reads the record then stops", 12),
        ["round 29:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 29: the processor reads the record then stops", 16),
        ["round 29: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 29: the processor reads the record then stops", 24),
        ["round 29: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 29: the processor reads the record then stops", 32),
        ["round 29: the processor reads", "the record then stops"],
    ),
    (
        ("round 29: a worker pulls the next task from the queue", 4),
        ["round", "29:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 29: a worker pulls the next task from the queue", 8),
        ["round", "29: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 29: a worker pulls the next task from the queue", 12),
        ["round 29: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 29: a worker pulls the next task from the queue", 16),
        ["round 29: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 29: a worker pulls the next task from the queue", 24),
        ["round 29: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 29: a worker pulls the next task from the queue", 32),
        ["round 29: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 29: signals travel through the network layer", 4),
        ["round", "29:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 29: signals travel through the network layer", 8),
        ["round", "29:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 29: signals travel through the network layer", 12),
        ["round 29:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 29: signals travel through the network layer", 16),
        ["round 29:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 29: signals travel through the network layer", 24),
        ["round 29: signals travel", "through the network", "layer"],
    ),
    (
        ("round 29: signals travel through the network layer", 32),
        ["round 29: signals travel through", "the network layer"],
    ),
    (
        ("round 29: the gateway routes each request by policy", 4),
        ["round", "29:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 29: the gateway routes each request by policy", 8),
        ["round", "29: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 29: the gateway routes each request by policy", 12),
        ["round 29:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 29: the gateway routes each request by policy", 16),
        ["round 29: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 29: the gateway routes each request by policy", 24),
        ["round 29: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 29: the gateway routes each request by policy", 32),
        ["round 29: the gateway routes", "each request by policy"],
    ),
    (
        ("round 29: memory grows until the buffer is full", 4),
        ["round", "29:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 29: memory grows until the buffer is full", 8),
        ["round", "29:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 29: memory grows until the buffer is full", 12),
        ["round 29:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 29: memory grows until the buffer is full", 16),
        ["round 29: memory", "grows until the", "buffer is full"],
    ),
    (("round 29: memory grows until the buffer is full", 24), ["round 29: memory grows", "until the buffer is full"]),
    (("round 29: memory grows until the buffer is full", 32), ["round 29: memory grows until the", "buffer is full"]),
    (
        ("round 29: the cluster mirrors every packet twice", 4),
        ["round", "29:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 29: the cluster mirrors every packet twice", 8),
        ["round", "29: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 29: the cluster mirrors every packet twice", 12),
        ["round 29:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 29: the cluster mirrors every packet twice", 16),
        ["round 29: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 29: the cluster mirrors every packet twice", 24),
        ["round 29: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 29: the cluster mirrors every packet twice", 32), ["round 29: the cluster mirrors", "every packet twice"]),
    (
        ("round 29: ranking uses tokens learned from the corpus", 4),
        ["round", "29:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 29: ranking uses tokens learned from the corpus", 8),
        ["round", "29:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 29: ranking uses tokens learned from the corpus", 12),
        ["round 29:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 29: ranking uses tokens learned from the corpus", 16),
        ["round 29:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 29: ranking uses tokens learned from the corpus", 24),
        ["round 29: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 29: ranking uses tokens learned from the corpus", 32),
        ["round 29: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 29: a long session ends when the candle dies", 4),
        ["round", "29:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 29: a long session ends when the candle dies", 8),
        ["round", "29: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 29: a long session ends when the candle dies", 12),
        ["round 29: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 29: a long session ends when the candle dies", 16),
        ["round 29: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 29: a long session ends when the candle dies", 24),
        ["round 29: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 29: a long session ends when the candle dies", 32),
        ["round 29: a long session ends", "when the candle dies"],
    ),
    (
        ("round 29: encode the prompt then map the result", 4),
        ["round", "29:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 29: encode the prompt then map the result", 8),
        ["round", "29:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 29: encode the prompt then map the result", 12),
        ["round 29:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 29: encode the prompt then map the result", 16),
        ["round 29: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 29: encode the prompt then map the result", 24),
        ["round 29: encode the", "prompt then map the", "result"],
    ),
    (("round 29: encode the prompt then map the result", 32), ["round 29: encode the prompt then", "map the result"]),
    (
        ("round 29: the kernel wakes the worker at dawn", 4),
        ["round", "29:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 29: the kernel wakes the worker at dawn", 8),
        ["round", "29: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 29: the kernel wakes the worker at dawn", 12),
        ["round 29:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 29: the kernel wakes the worker at dawn", 16), ["round 29: the", "kernel wakes the", "worker at dawn"]),
    (("round 29: the kernel wakes the worker at dawn", 24), ["round 29: the kernel", "wakes the worker at dawn"]),
    (("round 29: the kernel wakes the worker at dawn", 32), ["round 29: the kernel wakes the", "worker at dawn"]),
    (
        ("round 29: service latency drops after the patch", 4),
        ["round", "29:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 29: service latency drops after the patch", 8),
        ["round", "29:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 29: service latency drops after the patch", 12),
        ["round 29:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 29: service latency drops after the patch", 16),
        ["round 29:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 29: service latency drops after the patch", 24),
        ["round 29: service", "latency drops after the", "patch"],
    ),
    (("round 29: service latency drops after the patch", 32), ["round 29: service latency drops", "after the patch"]),
    (
        ("round 29: the library caches every vector it sees", 4),
        ["round", "29:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 29: the library caches every vector it sees", 8),
        ["round", "29: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 29: the library caches every vector it sees", 12),
        ["round 29:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 29: the library caches every vector it sees", 16),
        ["round 29: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 29: the library caches every vector it sees", 24),
        ["round 29: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 29: the library caches every vector it sees", 32),
        ["round 29: the library caches", "every vector it sees"],
    ),
    (
        ("round 29: agents argue then the debate resolves", 4),
        ["round", "29:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 29: agents argue then the debate resolves", 8),
        ["round", "29:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 29: agents argue then the debate resolves", 12),
        ["round 29:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 29: agents argue then the debate resolves", 16),
        ["round 29: agents", "argue then the", "debate resolves"],
    ),
    (("round 29: agents argue then the debate resolves", 24), ["round 29: agents argue", "then the debate resolves"]),
    (("round 29: agents argue then the debate resolves", 32), ["round 29: agents argue then the", "debate resolves"]),
    (
        ("round 29: the filter keeps only strong matches", 4),
        ["round", "29:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 29: the filter keeps only strong matches", 8),
        ["round", "29: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 29: the filter keeps only strong matches", 12),
        ["round 29:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 29: the filter keeps only strong matches", 16),
        ["round 29: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 29: the filter keeps only strong matches", 24), ["round 29: the filter", "keeps only strong", "matches"]),
    (("round 29: the filter keeps only strong matches", 32), ["round 29: the filter keeps only", "strong matches"]),
    (
        ("round 29: the model answers with a short reply", 4),
        ["round", "29:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 29: the model answers with a short reply", 8),
        ["round", "29: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 29: the model answers with a short reply", 12),
        ["round 29:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 29: the model answers with a short reply", 16),
        ["round 29: the", "model answers", "with a short", "reply"],
    ),
    (("round 29: the model answers with a short reply", 24), ["round 29: the model", "answers with a short", "reply"]),
    (("round 29: the model answers with a short reply", 32), ["round 29: the model answers with", "a short reply"]),
    (
        ("round 29: the recorder stores the reasoning trace", 4),
        ["round", "29:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 29: the recorder stores the reasoning trace", 8),
        ["round", "29: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 29: the recorder stores the reasoning trace", 12),
        ["round 29:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 29: the recorder stores the reasoning trace", 16),
        ["round 29: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 29: the recorder stores the reasoning trace", 24),
        ["round 29: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 29: the recorder stores the reasoning trace", 32),
        ["round 29: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 29: the angel watches the processor run", 4),
        ["round", "29:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 29: the angel watches the processor run", 8),
        ["round", "29: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 29: the angel watches the processor run", 12),
        ["round 29:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 29: the angel watches the processor run", 16), ["round 29: the", "angel watches", "the processor", "run"]),
    (("round 29: the angel watches the processor run", 24), ["round 29: the angel", "watches the processor", "run"]),
    (("round 29: the angel watches the processor run", 32), ["round 29: the angel watches the", "processor run"]),
    (
        ("round 29: angle of the vector decides the match", 4),
        ["round", "29:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 29: angle of the vector decides the match", 8),
        ["round", "29:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 29: angle of the vector decides the match", 12),
        ["round 29:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 29: angle of the vector decides the match", 16),
        ["round 29: angle", "of the vector", "decides the", "match"],
    ),
    (("round 29: angle of the vector decides the match", 24), ["round 29: angle of the", "vector decides the match"]),
    (("round 29: angle of the vector decides the match", 32), ["round 29: angle of the vector", "decides the match"]),
    (
        ("round 29: the candle burns twice as long at night", 4),
        ["round", "29:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 29: the candle burns twice as long at night", 8),
        ["round", "29: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 29: the candle burns twice as long at night", 12),
        ["round 29:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 29: the candle burns twice as long at night", 16),
        ["round 29: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 29: the candle burns twice as long at night", 24),
        ["round 29: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 29: the candle burns twice as long at night", 32),
        ["round 29: the candle burns twice", "as long at night"],
    ),
    (
        ("round 29: a mirror of the universe in one line", 4),
        ["round", "29:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 29: a mirror of the universe in one line", 8),
        ["round", "29: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 29: a mirror of the universe in one line", 12),
        ["round 29: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 29: a mirror of the universe in one line", 16),
        ["round 29: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 29: a mirror of the universe in one line", 24), ["round 29: a mirror of", "the universe in one line"]),
    (("round 29: a mirror of the universe in one line", 32), ["round 29: a mirror of the", "universe in one line"]),
    (
        ("round 29: the queue drains before the storm", 4),
        ["round", "29:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 29: the queue drains before the storm", 8),
        ["round", "29: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 29: the queue drains before the storm", 12), ["round 29:", "the queue", "drains", "before the", "storm"]),
    (("round 29: the queue drains before the storm", 16), ["round 29: the", "queue drains", "before the storm"]),
    (("round 29: the queue drains before the storm", 24), ["round 29: the queue", "drains before the storm"]),
    (("round 29: the queue drains before the storm", 32), ["round 29: the queue drains", "before the storm"]),
    (
        ("kitten29 sitting29 agent29 angle29 universe29 memory29", 6),
        ["kitten29", "sitting29", "agent29", "angle29", "universe29", "memory29"],
    ),
    (
        ("kitten29 sitting29 agent29 angle29 universe29 memory29", 10),
        ["kitten29", "sitting29", "agent29", "angle29", "universe29", "memory29"],
    ),
    (
        ("kitten29 sitting29 agent29 angle29 universe29 memory29", 18),
        ["kitten29 sitting29", "agent29 angle29", "universe29", "memory29"],
    ),
    (
        ("kitten29 sitting29 agent29 angle29 universe29 memory29", 28),
        ["kitten29 sitting29 agent29", "angle29 universe29 memory29"],
    ),
    (
        ("sitting29 agent29 angle29 universe29 memory29 stream29", 6),
        ["sitting29", "agent29", "angle29", "universe29", "memory29", "stream29"],
    ),
    (
        ("sitting29 agent29 angle29 universe29 memory29 stream29", 10),
        ["sitting29", "agent29", "angle29", "universe29", "memory29", "stream29"],
    ),
    (
        ("sitting29 agent29 angle29 universe29 memory29 stream29", 18),
        ["sitting29 agent29", "angle29 universe29", "memory29 stream29"],
    ),
    (
        ("sitting29 agent29 angle29 universe29 memory29 stream29", 28),
        ["sitting29 agent29 angle29", "universe29 memory29 stream29"],
    ),
    (
        ("agent29 angle29 universe29 memory29 stream29 context29", 6),
        ["agent29", "angle29", "universe29", "memory29", "stream29", "context29"],
    ),
    (
        ("agent29 angle29 universe29 memory29 stream29 context29", 10),
        ["agent29", "angle29", "universe29", "memory29", "stream29", "context29"],
    ),
    (
        ("agent29 angle29 universe29 memory29 stream29 context29", 18),
        ["agent29 angle29", "universe29", "memory29 stream29", "context29"],
    ),
    (
        ("agent29 angle29 universe29 memory29 stream29 context29", 28),
        ["agent29 angle29 universe29", "memory29 stream29 context29"],
    ),
    (
        ("angle29 universe29 memory29 stream29 context29 knowledge29", 6),
        ["angle29", "universe29", "memory29", "stream29", "context29", "knowledge29"],
    ),
    (
        ("angle29 universe29 memory29 stream29 context29 knowledge29", 10),
        ["angle29", "universe29", "memory29", "stream29", "context29", "knowledge29"],
    ),
    (
        ("angle29 universe29 memory29 stream29 context29 knowledge29", 18),
        ["angle29 universe29", "memory29 stream29", "context29", "knowledge29"],
    ),
    (
        ("angle29 universe29 memory29 stream29 context29 knowledge29", 28),
        ["angle29 universe29 memory29", "stream29 context29", "knowledge29"],
    ),
    (
        ("universe29 memory29 stream29 context29 knowledge29 vector29", 6),
        ["universe29", "memory29", "stream29", "context29", "knowledge29", "vector29"],
    ),
    (
        ("universe29 memory29 stream29 context29 knowledge29 vector29", 10),
        ["universe29", "memory29", "stream29", "context29", "knowledge29", "vector29"],
    ),
    (
        ("universe29 memory29 stream29 context29 knowledge29 vector29", 18),
        ["universe29", "memory29 stream29", "context29", "knowledge29", "vector29"],
    ),
    (
        ("universe29 memory29 stream29 context29 knowledge29 vector29", 28),
        ["universe29 memory29 stream29", "context29 knowledge29", "vector29"],
    ),
    (
        ("memory29 stream29 context29 knowledge29 vector29 processor29", 6),
        ["memory29", "stream29", "context29", "knowledge29", "vector29", "processor29"],
    ),
    (
        ("memory29 stream29 context29 knowledge29 vector29 processor29", 10),
        ["memory29", "stream29", "context29", "knowledge29", "vector29", "processor29"],
    ),
    (
        ("memory29 stream29 context29 knowledge29 vector29 processor29", 18),
        ["memory29 stream29", "context29", "knowledge29", "vector29", "processor29"],
    ),
    (
        ("memory29 stream29 context29 knowledge29 vector29 processor29", 28),
        ["memory29 stream29 context29", "knowledge29 vector29", "processor29"],
    ),
    (
        ("stream29 context29 knowledge29 vector29 processor29 reasoning29", 6),
        ["stream29", "context29", "knowledge29", "vector29", "processor29", "reasoning29"],
    ),
    (
        ("stream29 context29 knowledge29 vector29 processor29 reasoning29", 10),
        ["stream29", "context29", "knowledge29", "vector29", "processor29", "reasoning29"],
    ),
    (
        ("stream29 context29 knowledge29 vector29 processor29 reasoning29", 18),
        ["stream29 context29", "knowledge29", "vector29", "processor29", "reasoning29"],
    ),
    (
        ("stream29 context29 knowledge29 vector29 processor29 reasoning29", 28),
        ["stream29 context29", "knowledge29 vector29", "processor29 reasoning29"],
    ),
    (
        ("context29 knowledge29 vector29 processor29 reasoning29 machine29", 6),
        ["context29", "knowledge29", "vector29", "processor29", "reasoning29", "machine29"],
    ),
    (
        ("context29 knowledge29 vector29 processor29 reasoning29 machine29", 10),
        ["context29", "knowledge29", "vector29", "processor29", "reasoning29", "machine29"],
    ),
    (
        ("context29 knowledge29 vector29 processor29 reasoning29 machine29", 18),
        ["context29", "knowledge29", "vector29", "processor29", "reasoning29", "machine29"],
    ),
    (
        ("context29 knowledge29 vector29 processor29 reasoning29 machine29", 28),
        ["context29 knowledge29", "vector29 processor29", "reasoning29 machine29"],
    ),
    (
        ("knowledge29 vector29 processor29 reasoning29 machine29 learning29", 6),
        ["knowledge29", "vector29", "processor29", "reasoning29", "machine29", "learning29"],
    ),
    (
        ("knowledge29 vector29 processor29 reasoning29 machine29 learning29", 10),
        ["knowledge29", "vector29", "processor29", "reasoning29", "machine29", "learning29"],
    ),
    (
        ("knowledge29 vector29 processor29 reasoning29 machine29 learning29", 18),
        ["knowledge29", "vector29", "processor29", "reasoning29", "machine29", "learning29"],
    ),
    (
        ("knowledge29 vector29 processor29 reasoning29 machine29 learning29", 28),
        ["knowledge29 vector29", "processor29 reasoning29", "machine29 learning29"],
    ),
    (
        ("vector29 processor29 reasoning29 machine29 learning29 model29", 6),
        ["vector29", "processor29", "reasoning29", "machine29", "learning29", "model29"],
    ),
    (
        ("vector29 processor29 reasoning29 machine29 learning29 model29", 10),
        ["vector29", "processor29", "reasoning29", "machine29", "learning29", "model29"],
    ),
    (
        ("vector29 processor29 reasoning29 machine29 learning29 model29", 18),
        ["vector29", "processor29", "reasoning29", "machine29", "learning29 model29"],
    ),
    (
        ("vector29 processor29 reasoning29 machine29 learning29 model29", 28),
        ["vector29 processor29", "reasoning29 machine29", "learning29 model29"],
    ),
    (
        ("processor29 reasoning29 machine29 learning29 model29 token29", 6),
        ["processor29", "reasoning29", "machine29", "learning29", "model29", "token29"],
    ),
    (
        ("processor29 reasoning29 machine29 learning29 model29 token29", 10),
        ["processor29", "reasoning29", "machine29", "learning29", "model29", "token29"],
    ),
    (
        ("processor29 reasoning29 machine29 learning29 model29 token29", 18),
        ["processor29", "reasoning29", "machine29", "learning29 model29", "token29"],
    ),
    (
        ("processor29 reasoning29 machine29 learning29 model29 token29", 28),
        ["processor29 reasoning29", "machine29 learning29 model29", "token29"],
    ),
    (
        ("reasoning29 machine29 learning29 model29 token29 prompt29", 6),
        ["reasoning29", "machine29", "learning29", "model29", "token29", "prompt29"],
    ),
    (
        ("reasoning29 machine29 learning29 model29 token29 prompt29", 10),
        ["reasoning29", "machine29", "learning29", "model29", "token29", "prompt29"],
    ),
    (
        ("reasoning29 machine29 learning29 model29 token29 prompt29", 18),
        ["reasoning29", "machine29", "learning29 model29", "token29 prompt29"],
    ),
    (
        ("reasoning29 machine29 learning29 model29 token29 prompt29", 28),
        ["reasoning29 machine29", "learning29 model29 token29", "prompt29"],
    ),
    (
        ("machine29 learning29 model29 token29 prompt29 session29", 6),
        ["machine29", "learning29", "model29", "token29", "prompt29", "session29"],
    ),
    (
        ("machine29 learning29 model29 token29 prompt29 session29", 10),
        ["machine29", "learning29", "model29", "token29", "prompt29", "session29"],
    ),
    (
        ("machine29 learning29 model29 token29 prompt29 session29", 18),
        ["machine29", "learning29 model29", "token29 prompt29", "session29"],
    ),
    (
        ("machine29 learning29 model29 token29 prompt29 session29", 28),
        ["machine29 learning29 model29", "token29 prompt29 session29"],
    ),
    (
        ("learning29 model29 token29 prompt29 session29 library29", 6),
        ["learning29", "model29", "token29", "prompt29", "session29", "library29"],
    ),
    (
        ("learning29 model29 token29 prompt29 session29 library29", 10),
        ["learning29", "model29", "token29", "prompt29", "session29", "library29"],
    ),
    (
        ("learning29 model29 token29 prompt29 session29 library29", 18),
        ["learning29 model29", "token29 prompt29", "session29", "library29"],
    ),
    (
        ("learning29 model29 token29 prompt29 session29 library29", 28),
        ["learning29 model29 token29", "prompt29 session29 library29"],
    ),
    (
        ("model29 token29 prompt29 session29 library29 service29", 6),
        ["model29", "token29", "prompt29", "session29", "library29", "service29"],
    ),
    (
        ("model29 token29 prompt29 session29 library29 service29", 10),
        ["model29", "token29", "prompt29", "session29", "library29", "service29"],
    ),
    (
        ("model29 token29 prompt29 session29 library29 service29", 18),
        ["model29 token29", "prompt29 session29", "library29", "service29"],
    ),
    (
        ("model29 token29 prompt29 session29 library29 service29", 28),
        ["model29 token29 prompt29", "session29 library29", "service29"],
    ),
    (
        ("token29 prompt29 session29 library29 service29 gateway29", 6),
        ["token29", "prompt29", "session29", "library29", "service29", "gateway29"],
    ),
    (
        ("token29 prompt29 session29 library29 service29 gateway29", 10),
        ["token29", "prompt29", "session29", "library29", "service29", "gateway29"],
    ),
    (
        ("token29 prompt29 session29 library29 service29 gateway29", 18),
        ["token29 prompt29", "session29", "library29", "service29", "gateway29"],
    ),
    (
        ("token29 prompt29 session29 library29 service29 gateway29", 28),
        ["token29 prompt29 session29", "library29 service29", "gateway29"],
    ),
    (
        ("prompt29 session29 library29 service29 gateway29 storage29", 6),
        ["prompt29", "session29", "library29", "service29", "gateway29", "storage29"],
    ),
    (
        ("prompt29 session29 library29 service29 gateway29 storage29", 10),
        ["prompt29", "session29", "library29", "service29", "gateway29", "storage29"],
    ),
    (
        ("prompt29 session29 library29 service29 gateway29 storage29", 18),
        ["prompt29 session29", "library29", "service29", "gateway29", "storage29"],
    ),
    (
        ("prompt29 session29 library29 service29 gateway29 storage29", 28),
        ["prompt29 session29 library29", "service29 gateway29", "storage29"],
    ),
    (
        ("session29 library29 service29 gateway29 storage29 network29", 6),
        ["session29", "library29", "service29", "gateway29", "storage29", "network29"],
    ),
    (
        ("session29 library29 service29 gateway29 storage29 network29", 10),
        ["session29", "library29", "service29", "gateway29", "storage29", "network29"],
    ),
    (
        ("session29 library29 service29 gateway29 storage29 network29", 18),
        ["session29", "library29", "service29", "gateway29", "storage29", "network29"],
    ),
    (
        ("session29 library29 service29 gateway29 storage29 network29", 28),
        ["session29 library29", "service29 gateway29", "storage29 network29"],
    ),
    (
        ("library29 service29 gateway29 storage29 network29 latency29", 6),
        ["library29", "service29", "gateway29", "storage29", "network29", "latency29"],
    ),
    (
        ("library29 service29 gateway29 storage29 network29 latency29", 10),
        ["library29", "service29", "gateway29", "storage29", "network29", "latency29"],
    ),
    (
        ("library29 service29 gateway29 storage29 network29 latency29", 18),
        ["library29", "service29", "gateway29", "storage29", "network29", "latency29"],
    ),
    (
        ("library29 service29 gateway29 storage29 network29 latency29", 28),
        ["library29 service29", "gateway29 storage29", "network29 latency29"],
    ),
    (
        ("service29 gateway29 storage29 network29 latency29 buffer29", 6),
        ["service29", "gateway29", "storage29", "network29", "latency29", "buffer29"],
    ),
    (
        ("service29 gateway29 storage29 network29 latency29 buffer29", 10),
        ["service29", "gateway29", "storage29", "network29", "latency29", "buffer29"],
    ),
    (
        ("service29 gateway29 storage29 network29 latency29 buffer29", 18),
        ["service29", "gateway29", "storage29", "network29", "latency29 buffer29"],
    ),
    (
        ("service29 gateway29 storage29 network29 latency29 buffer29", 28),
        ["service29 gateway29", "storage29 network29", "latency29 buffer29"],
    ),
    (
        ("gateway29 storage29 network29 latency29 buffer29 queue29", 6),
        ["gateway29", "storage29", "network29", "latency29", "buffer29", "queue29"],
    ),
    (
        ("gateway29 storage29 network29 latency29 buffer29 queue29", 10),
        ["gateway29", "storage29", "network29", "latency29", "buffer29", "queue29"],
    ),
    (
        ("gateway29 storage29 network29 latency29 buffer29 queue29", 18),
        ["gateway29", "storage29", "network29", "latency29 buffer29", "queue29"],
    ),
    (
        ("gateway29 storage29 network29 latency29 buffer29 queue29", 28),
        ["gateway29 storage29", "network29 latency29 buffer29", "queue29"],
    ),
    (
        ("storage29 network29 latency29 buffer29 queue29 worker29", 6),
        ["storage29", "network29", "latency29", "buffer29", "queue29", "worker29"],
    ),
    (
        ("storage29 network29 latency29 buffer29 queue29 worker29", 10),
        ["storage29", "network29", "latency29", "buffer29", "queue29", "worker29"],
    ),
    (
        ("storage29 network29 latency29 buffer29 queue29 worker29", 18),
        ["storage29", "network29", "latency29 buffer29", "queue29 worker29"],
    ),
    (
        ("storage29 network29 latency29 buffer29 queue29 worker29", 28),
        ["storage29 network29", "latency29 buffer29 queue29", "worker29"],
    ),
    (
        ("network29 latency29 buffer29 queue29 worker29 kernel29", 6),
        ["network29", "latency29", "buffer29", "queue29", "worker29", "kernel29"],
    ),
    (
        ("network29 latency29 buffer29 queue29 worker29 kernel29", 10),
        ["network29", "latency29", "buffer29", "queue29", "worker29", "kernel29"],
    ),
    (
        ("network29 latency29 buffer29 queue29 worker29 kernel29", 18),
        ["network29", "latency29 buffer29", "queue29 worker29", "kernel29"],
    ),
    (
        ("network29 latency29 buffer29 queue29 worker29 kernel29", 28),
        ["network29 latency29 buffer29", "queue29 worker29 kernel29"],
    ),
    (
        ("latency29 buffer29 queue29 worker29 kernel29 signal29", 6),
        ["latency29", "buffer29", "queue29", "worker29", "kernel29", "signal29"],
    ),
    (
        ("latency29 buffer29 queue29 worker29 kernel29 signal29", 10),
        ["latency29", "buffer29", "queue29", "worker29", "kernel29", "signal29"],
    ),
    (
        ("latency29 buffer29 queue29 worker29 kernel29 signal29", 18),
        ["latency29 buffer29", "queue29 worker29", "kernel29 signal29"],
    ),
    (
        ("latency29 buffer29 queue29 worker29 kernel29 signal29", 28),
        ["latency29 buffer29 queue29", "worker29 kernel29 signal29"],
    ),
    (
        ("buffer29 queue29 worker29 kernel29 signal29 packet29", 6),
        ["buffer29", "queue29", "worker29", "kernel29", "signal29", "packet29"],
    ),
    (
        ("buffer29 queue29 worker29 kernel29 signal29 packet29", 10),
        ["buffer29", "queue29", "worker29", "kernel29", "signal29", "packet29"],
    ),
    (
        ("buffer29 queue29 worker29 kernel29 signal29 packet29", 18),
        ["buffer29 queue29", "worker29 kernel29", "signal29 packet29"],
    ),
    (
        ("buffer29 queue29 worker29 kernel29 signal29 packet29", 28),
        ["buffer29 queue29 worker29", "kernel29 signal29 packet29"],
    ),
    (
        ("queue29 worker29 kernel29 signal29 packet29 router29", 6),
        ["queue29", "worker29", "kernel29", "signal29", "packet29", "router29"],
    ),
    (
        ("queue29 worker29 kernel29 signal29 packet29 router29", 10),
        ["queue29", "worker29", "kernel29", "signal29", "packet29", "router29"],
    ),
    (
        ("queue29 worker29 kernel29 signal29 packet29 router29", 18),
        ["queue29 worker29", "kernel29 signal29", "packet29 router29"],
    ),
    (
        ("queue29 worker29 kernel29 signal29 packet29 router29", 28),
        ["queue29 worker29 kernel29", "signal29 packet29 router29"],
    ),
    (
        ("worker29 kernel29 signal29 packet29 router29 cluster29", 6),
        ["worker29", "kernel29", "signal29", "packet29", "router29", "cluster29"],
    ),
    (
        ("worker29 kernel29 signal29 packet29 router29 cluster29", 10),
        ["worker29", "kernel29", "signal29", "packet29", "router29", "cluster29"],
    ),
    (
        ("worker29 kernel29 signal29 packet29 router29 cluster29", 18),
        ["worker29 kernel29", "signal29 packet29", "router29 cluster29"],
    ),
    (
        ("worker29 kernel29 signal29 packet29 router29 cluster29", 28),
        ["worker29 kernel29 signal29", "packet29 router29 cluster29"],
    ),
    (
        ("kernel29 signal29 packet29 router29 cluster29 mirror29", 6),
        ["kernel29", "signal29", "packet29", "router29", "cluster29", "mirror29"],
    ),
    (
        ("kernel29 signal29 packet29 router29 cluster29 mirror29", 10),
        ["kernel29", "signal29", "packet29", "router29", "cluster29", "mirror29"],
    ),
    (
        ("kernel29 signal29 packet29 router29 cluster29 mirror29", 18),
        ["kernel29 signal29", "packet29 router29", "cluster29 mirror29"],
    ),
    (
        ("kernel29 signal29 packet29 router29 cluster29 mirror29", 28),
        ["kernel29 signal29 packet29", "router29 cluster29 mirror29"],
    ),
    (
        ("signal29 packet29 router29 cluster29 mirror29 filter29", 6),
        ["signal29", "packet29", "router29", "cluster29", "mirror29", "filter29"],
    ),
    (
        ("signal29 packet29 router29 cluster29 mirror29 filter29", 10),
        ["signal29", "packet29", "router29", "cluster29", "mirror29", "filter29"],
    ),
    (
        ("signal29 packet29 router29 cluster29 mirror29 filter29", 18),
        ["signal29 packet29", "router29 cluster29", "mirror29 filter29"],
    ),
    (
        ("signal29 packet29 router29 cluster29 mirror29 filter29", 28),
        ["signal29 packet29 router29", "cluster29 mirror29 filter29"],
    ),
    (
        ("packet29 router29 cluster29 mirror29 filter29 ranking29", 6),
        ["packet29", "router29", "cluster29", "mirror29", "filter29", "ranking29"],
    ),
    (
        ("packet29 router29 cluster29 mirror29 filter29 ranking29", 10),
        ["packet29", "router29", "cluster29", "mirror29", "filter29", "ranking29"],
    ),
    (
        ("packet29 router29 cluster29 mirror29 filter29 ranking29", 18),
        ["packet29 router29", "cluster29 mirror29", "filter29 ranking29"],
    ),
    (
        ("packet29 router29 cluster29 mirror29 filter29 ranking29", 28),
        ["packet29 router29 cluster29", "mirror29 filter29 ranking29"],
    ),
    (
        ("router29 cluster29 mirror29 filter29 ranking29 encoding29", 6),
        ["router29", "cluster29", "mirror29", "filter29", "ranking29", "encoding29"],
    ),
    (
        ("router29 cluster29 mirror29 filter29 ranking29 encoding29", 10),
        ["router29", "cluster29", "mirror29", "filter29", "ranking29", "encoding29"],
    ),
    (
        ("router29 cluster29 mirror29 filter29 ranking29 encoding29", 18),
        ["router29 cluster29", "mirror29 filter29", "ranking29", "encoding29"],
    ),
    (
        ("router29 cluster29 mirror29 filter29 ranking29 encoding29", 28),
        ["router29 cluster29 mirror29", "filter29 ranking29", "encoding29"],
    ),
    (
        ("cluster29 mirror29 filter29 ranking29 encoding29 mapping29", 6),
        ["cluster29", "mirror29", "filter29", "ranking29", "encoding29", "mapping29"],
    ),
    (
        ("cluster29 mirror29 filter29 ranking29 encoding29 mapping29", 10),
        ["cluster29", "mirror29", "filter29", "ranking29", "encoding29", "mapping29"],
    ),
    (
        ("cluster29 mirror29 filter29 ranking29 encoding29 mapping29", 18),
        ["cluster29 mirror29", "filter29 ranking29", "encoding29", "mapping29"],
    ),
    (
        ("cluster29 mirror29 filter29 ranking29 encoding29 mapping29", 28),
        ["cluster29 mirror29 filter29", "ranking29 encoding29", "mapping29"],
    ),
    (
        ("mirror29 filter29 ranking29 encoding29 mapping29 record29", 6),
        ["mirror29", "filter29", "ranking29", "encoding29", "mapping29", "record29"],
    ),
    (
        ("mirror29 filter29 ranking29 encoding29 mapping29 record29", 10),
        ["mirror29", "filter29", "ranking29", "encoding29", "mapping29", "record29"],
    ),
    (
        ("mirror29 filter29 ranking29 encoding29 mapping29 record29", 18),
        ["mirror29 filter29", "ranking29", "encoding29", "mapping29 record29"],
    ),
    (
        ("mirror29 filter29 ranking29 encoding29 mapping29 record29", 28),
        ["mirror29 filter29 ranking29", "encoding29 mapping29", "record29"],
    ),
    (
        ("filter29 ranking29 encoding29 mapping29 record29 candle29", 6),
        ["filter29", "ranking29", "encoding29", "mapping29", "record29", "candle29"],
    ),
    (
        ("filter29 ranking29 encoding29 mapping29 record29 candle29", 10),
        ["filter29", "ranking29", "encoding29", "mapping29", "record29", "candle29"],
    ),
    (
        ("filter29 ranking29 encoding29 mapping29 record29 candle29", 18),
        ["filter29 ranking29", "encoding29", "mapping29 record29", "candle29"],
    ),
    (
        ("filter29 ranking29 encoding29 mapping29 record29 candle29", 28),
        ["filter29 ranking29", "encoding29 mapping29", "record29 candle29"],
    ),
    (
        ("ranking29 encoding29 mapping29 record29 candle29 thread29", 6),
        ["ranking29", "encoding29", "mapping29", "record29", "candle29", "thread29"],
    ),
    (
        ("ranking29 encoding29 mapping29 record29 candle29 thread29", 10),
        ["ranking29", "encoding29", "mapping29", "record29", "candle29", "thread29"],
    ),
    (
        ("ranking29 encoding29 mapping29 record29 candle29 thread29", 18),
        ["ranking29", "encoding29", "mapping29 record29", "candle29 thread29"],
    ),
    (
        ("ranking29 encoding29 mapping29 record29 candle29 thread29", 28),
        ["ranking29 encoding29", "mapping29 record29 candle29", "thread29"],
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
