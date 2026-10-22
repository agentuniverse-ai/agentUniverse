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
        ("round 13: the quick brown fox jumps over the lazy dog", 4),
        ["round", "13:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 13: the quick brown fox jumps over the lazy dog", 8),
        ["round", "13: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 13: the quick brown fox jumps over the lazy dog", 12),
        ["round 13:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 13: the quick brown fox jumps over the lazy dog", 16),
        ["round 13: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 13: the quick brown fox jumps over the lazy dog", 24),
        ["round 13: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 13: the quick brown fox jumps over the lazy dog", 32),
        ["round 13: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 13: agentuniverse is a framework for multi agents", 4),
        ["round", "13:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 13: agentuniverse is a framework for multi agents", 8),
        ["round", "13:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 13: agentuniverse is a framework for multi agents", 12),
        ["round 13:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 13: agentuniverse is a framework for multi agents", 16),
        ["round 13:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 13: agentuniverse is a framework for multi agents", 24),
        ["round 13: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 13: agentuniverse is a framework for multi agents", 32),
        ["round 13: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 13: knowledge stored as vectors enables retrieval", 4),
        ["round", "13:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 13: knowledge stored as vectors enables retrieval", 8),
        ["round", "13:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 13: knowledge stored as vectors enables retrieval", 12),
        ["round 13:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 13: knowledge stored as vectors enables retrieval", 16),
        ["round 13:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 13: knowledge stored as vectors enables retrieval", 24),
        ["round 13: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 13: knowledge stored as vectors enables retrieval", 32),
        ["round 13: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 13: the processor reads the record then stops", 4),
        ["round", "13:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 13: the processor reads the record then stops", 8),
        ["round", "13: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 13: the processor reads the record then stops", 12),
        ["round 13:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 13: the processor reads the record then stops", 16),
        ["round 13: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 13: the processor reads the record then stops", 24),
        ["round 13: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 13: the processor reads the record then stops", 32),
        ["round 13: the processor reads", "the record then stops"],
    ),
    (
        ("round 13: a worker pulls the next task from the queue", 4),
        ["round", "13:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 13: a worker pulls the next task from the queue", 8),
        ["round", "13: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 13: a worker pulls the next task from the queue", 12),
        ["round 13: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 13: a worker pulls the next task from the queue", 16),
        ["round 13: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 13: a worker pulls the next task from the queue", 24),
        ["round 13: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 13: a worker pulls the next task from the queue", 32),
        ["round 13: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 13: signals travel through the network layer", 4),
        ["round", "13:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 13: signals travel through the network layer", 8),
        ["round", "13:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 13: signals travel through the network layer", 12),
        ["round 13:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 13: signals travel through the network layer", 16),
        ["round 13:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 13: signals travel through the network layer", 24),
        ["round 13: signals travel", "through the network", "layer"],
    ),
    (
        ("round 13: signals travel through the network layer", 32),
        ["round 13: signals travel through", "the network layer"],
    ),
    (
        ("round 13: the gateway routes each request by policy", 4),
        ["round", "13:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 13: the gateway routes each request by policy", 8),
        ["round", "13: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 13: the gateway routes each request by policy", 12),
        ["round 13:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 13: the gateway routes each request by policy", 16),
        ["round 13: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 13: the gateway routes each request by policy", 24),
        ["round 13: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 13: the gateway routes each request by policy", 32),
        ["round 13: the gateway routes", "each request by policy"],
    ),
    (
        ("round 13: memory grows until the buffer is full", 4),
        ["round", "13:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 13: memory grows until the buffer is full", 8),
        ["round", "13:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 13: memory grows until the buffer is full", 12),
        ["round 13:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 13: memory grows until the buffer is full", 16),
        ["round 13: memory", "grows until the", "buffer is full"],
    ),
    (("round 13: memory grows until the buffer is full", 24), ["round 13: memory grows", "until the buffer is full"]),
    (("round 13: memory grows until the buffer is full", 32), ["round 13: memory grows until the", "buffer is full"]),
    (
        ("round 13: the cluster mirrors every packet twice", 4),
        ["round", "13:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 13: the cluster mirrors every packet twice", 8),
        ["round", "13: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 13: the cluster mirrors every packet twice", 12),
        ["round 13:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 13: the cluster mirrors every packet twice", 16),
        ["round 13: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 13: the cluster mirrors every packet twice", 24),
        ["round 13: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 13: the cluster mirrors every packet twice", 32), ["round 13: the cluster mirrors", "every packet twice"]),
    (
        ("round 13: ranking uses tokens learned from the corpus", 4),
        ["round", "13:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 13: ranking uses tokens learned from the corpus", 8),
        ["round", "13:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 13: ranking uses tokens learned from the corpus", 12),
        ["round 13:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 13: ranking uses tokens learned from the corpus", 16),
        ["round 13:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 13: ranking uses tokens learned from the corpus", 24),
        ["round 13: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 13: ranking uses tokens learned from the corpus", 32),
        ["round 13: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 13: a long session ends when the candle dies", 4),
        ["round", "13:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 13: a long session ends when the candle dies", 8),
        ["round", "13: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 13: a long session ends when the candle dies", 12),
        ["round 13: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 13: a long session ends when the candle dies", 16),
        ["round 13: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 13: a long session ends when the candle dies", 24),
        ["round 13: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 13: a long session ends when the candle dies", 32),
        ["round 13: a long session ends", "when the candle dies"],
    ),
    (
        ("round 13: encode the prompt then map the result", 4),
        ["round", "13:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 13: encode the prompt then map the result", 8),
        ["round", "13:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 13: encode the prompt then map the result", 12),
        ["round 13:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 13: encode the prompt then map the result", 16),
        ["round 13: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 13: encode the prompt then map the result", 24),
        ["round 13: encode the", "prompt then map the", "result"],
    ),
    (("round 13: encode the prompt then map the result", 32), ["round 13: encode the prompt then", "map the result"]),
    (
        ("round 13: the kernel wakes the worker at dawn", 4),
        ["round", "13:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 13: the kernel wakes the worker at dawn", 8),
        ["round", "13: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 13: the kernel wakes the worker at dawn", 12),
        ["round 13:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 13: the kernel wakes the worker at dawn", 16), ["round 13: the", "kernel wakes the", "worker at dawn"]),
    (("round 13: the kernel wakes the worker at dawn", 24), ["round 13: the kernel", "wakes the worker at dawn"]),
    (("round 13: the kernel wakes the worker at dawn", 32), ["round 13: the kernel wakes the", "worker at dawn"]),
    (
        ("round 13: service latency drops after the patch", 4),
        ["round", "13:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 13: service latency drops after the patch", 8),
        ["round", "13:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 13: service latency drops after the patch", 12),
        ["round 13:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 13: service latency drops after the patch", 16),
        ["round 13:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 13: service latency drops after the patch", 24),
        ["round 13: service", "latency drops after the", "patch"],
    ),
    (("round 13: service latency drops after the patch", 32), ["round 13: service latency drops", "after the patch"]),
    (
        ("round 13: the library caches every vector it sees", 4),
        ["round", "13:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 13: the library caches every vector it sees", 8),
        ["round", "13: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 13: the library caches every vector it sees", 12),
        ["round 13:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 13: the library caches every vector it sees", 16),
        ["round 13: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 13: the library caches every vector it sees", 24),
        ["round 13: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 13: the library caches every vector it sees", 32),
        ["round 13: the library caches", "every vector it sees"],
    ),
    (
        ("round 13: agents argue then the debate resolves", 4),
        ["round", "13:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 13: agents argue then the debate resolves", 8),
        ["round", "13:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 13: agents argue then the debate resolves", 12),
        ["round 13:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 13: agents argue then the debate resolves", 16),
        ["round 13: agents", "argue then the", "debate resolves"],
    ),
    (("round 13: agents argue then the debate resolves", 24), ["round 13: agents argue", "then the debate resolves"]),
    (("round 13: agents argue then the debate resolves", 32), ["round 13: agents argue then the", "debate resolves"]),
    (
        ("round 13: the filter keeps only strong matches", 4),
        ["round", "13:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 13: the filter keeps only strong matches", 8),
        ["round", "13: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 13: the filter keeps only strong matches", 12),
        ["round 13:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 13: the filter keeps only strong matches", 16),
        ["round 13: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 13: the filter keeps only strong matches", 24), ["round 13: the filter", "keeps only strong", "matches"]),
    (("round 13: the filter keeps only strong matches", 32), ["round 13: the filter keeps only", "strong matches"]),
    (
        ("round 13: the model answers with a short reply", 4),
        ["round", "13:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 13: the model answers with a short reply", 8),
        ["round", "13: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 13: the model answers with a short reply", 12),
        ["round 13:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 13: the model answers with a short reply", 16),
        ["round 13: the", "model answers", "with a short", "reply"],
    ),
    (("round 13: the model answers with a short reply", 24), ["round 13: the model", "answers with a short", "reply"]),
    (("round 13: the model answers with a short reply", 32), ["round 13: the model answers with", "a short reply"]),
    (
        ("round 13: the recorder stores the reasoning trace", 4),
        ["round", "13:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 13: the recorder stores the reasoning trace", 8),
        ["round", "13: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 13: the recorder stores the reasoning trace", 12),
        ["round 13:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 13: the recorder stores the reasoning trace", 16),
        ["round 13: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 13: the recorder stores the reasoning trace", 24),
        ["round 13: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 13: the recorder stores the reasoning trace", 32),
        ["round 13: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 13: the angel watches the processor run", 4),
        ["round", "13:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 13: the angel watches the processor run", 8),
        ["round", "13: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 13: the angel watches the processor run", 12),
        ["round 13:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 13: the angel watches the processor run", 16), ["round 13: the", "angel watches", "the processor", "run"]),
    (("round 13: the angel watches the processor run", 24), ["round 13: the angel", "watches the processor", "run"]),
    (("round 13: the angel watches the processor run", 32), ["round 13: the angel watches the", "processor run"]),
    (
        ("round 13: angle of the vector decides the match", 4),
        ["round", "13:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 13: angle of the vector decides the match", 8),
        ["round", "13:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 13: angle of the vector decides the match", 12),
        ["round 13:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 13: angle of the vector decides the match", 16),
        ["round 13: angle", "of the vector", "decides the", "match"],
    ),
    (("round 13: angle of the vector decides the match", 24), ["round 13: angle of the", "vector decides the match"]),
    (("round 13: angle of the vector decides the match", 32), ["round 13: angle of the vector", "decides the match"]),
    (
        ("round 13: the candle burns twice as long at night", 4),
        ["round", "13:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 13: the candle burns twice as long at night", 8),
        ["round", "13: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 13: the candle burns twice as long at night", 12),
        ["round 13:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 13: the candle burns twice as long at night", 16),
        ["round 13: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 13: the candle burns twice as long at night", 24),
        ["round 13: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 13: the candle burns twice as long at night", 32),
        ["round 13: the candle burns twice", "as long at night"],
    ),
    (
        ("round 13: a mirror of the universe in one line", 4),
        ["round", "13:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 13: a mirror of the universe in one line", 8),
        ["round", "13: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 13: a mirror of the universe in one line", 12),
        ["round 13: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 13: a mirror of the universe in one line", 16),
        ["round 13: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 13: a mirror of the universe in one line", 24), ["round 13: a mirror of", "the universe in one line"]),
    (("round 13: a mirror of the universe in one line", 32), ["round 13: a mirror of the", "universe in one line"]),
    (
        ("round 13: the queue drains before the storm", 4),
        ["round", "13:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 13: the queue drains before the storm", 8),
        ["round", "13: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 13: the queue drains before the storm", 12), ["round 13:", "the queue", "drains", "before the", "storm"]),
    (("round 13: the queue drains before the storm", 16), ["round 13: the", "queue drains", "before the storm"]),
    (("round 13: the queue drains before the storm", 24), ["round 13: the queue", "drains before the storm"]),
    (("round 13: the queue drains before the storm", 32), ["round 13: the queue drains", "before the storm"]),
    (
        ("kitten13 sitting13 agent13 angle13 universe13 memory13", 6),
        ["kitten13", "sitting13", "agent13", "angle13", "universe13", "memory13"],
    ),
    (
        ("kitten13 sitting13 agent13 angle13 universe13 memory13", 10),
        ["kitten13", "sitting13", "agent13", "angle13", "universe13", "memory13"],
    ),
    (
        ("kitten13 sitting13 agent13 angle13 universe13 memory13", 18),
        ["kitten13 sitting13", "agent13 angle13", "universe13", "memory13"],
    ),
    (
        ("kitten13 sitting13 agent13 angle13 universe13 memory13", 28),
        ["kitten13 sitting13 agent13", "angle13 universe13 memory13"],
    ),
    (
        ("sitting13 agent13 angle13 universe13 memory13 stream13", 6),
        ["sitting13", "agent13", "angle13", "universe13", "memory13", "stream13"],
    ),
    (
        ("sitting13 agent13 angle13 universe13 memory13 stream13", 10),
        ["sitting13", "agent13", "angle13", "universe13", "memory13", "stream13"],
    ),
    (
        ("sitting13 agent13 angle13 universe13 memory13 stream13", 18),
        ["sitting13 agent13", "angle13 universe13", "memory13 stream13"],
    ),
    (
        ("sitting13 agent13 angle13 universe13 memory13 stream13", 28),
        ["sitting13 agent13 angle13", "universe13 memory13 stream13"],
    ),
    (
        ("agent13 angle13 universe13 memory13 stream13 context13", 6),
        ["agent13", "angle13", "universe13", "memory13", "stream13", "context13"],
    ),
    (
        ("agent13 angle13 universe13 memory13 stream13 context13", 10),
        ["agent13", "angle13", "universe13", "memory13", "stream13", "context13"],
    ),
    (
        ("agent13 angle13 universe13 memory13 stream13 context13", 18),
        ["agent13 angle13", "universe13", "memory13 stream13", "context13"],
    ),
    (
        ("agent13 angle13 universe13 memory13 stream13 context13", 28),
        ["agent13 angle13 universe13", "memory13 stream13 context13"],
    ),
    (
        ("angle13 universe13 memory13 stream13 context13 knowledge13", 6),
        ["angle13", "universe13", "memory13", "stream13", "context13", "knowledge13"],
    ),
    (
        ("angle13 universe13 memory13 stream13 context13 knowledge13", 10),
        ["angle13", "universe13", "memory13", "stream13", "context13", "knowledge13"],
    ),
    (
        ("angle13 universe13 memory13 stream13 context13 knowledge13", 18),
        ["angle13 universe13", "memory13 stream13", "context13", "knowledge13"],
    ),
    (
        ("angle13 universe13 memory13 stream13 context13 knowledge13", 28),
        ["angle13 universe13 memory13", "stream13 context13", "knowledge13"],
    ),
    (
        ("universe13 memory13 stream13 context13 knowledge13 vector13", 6),
        ["universe13", "memory13", "stream13", "context13", "knowledge13", "vector13"],
    ),
    (
        ("universe13 memory13 stream13 context13 knowledge13 vector13", 10),
        ["universe13", "memory13", "stream13", "context13", "knowledge13", "vector13"],
    ),
    (
        ("universe13 memory13 stream13 context13 knowledge13 vector13", 18),
        ["universe13", "memory13 stream13", "context13", "knowledge13", "vector13"],
    ),
    (
        ("universe13 memory13 stream13 context13 knowledge13 vector13", 28),
        ["universe13 memory13 stream13", "context13 knowledge13", "vector13"],
    ),
    (
        ("memory13 stream13 context13 knowledge13 vector13 processor13", 6),
        ["memory13", "stream13", "context13", "knowledge13", "vector13", "processor13"],
    ),
    (
        ("memory13 stream13 context13 knowledge13 vector13 processor13", 10),
        ["memory13", "stream13", "context13", "knowledge13", "vector13", "processor13"],
    ),
    (
        ("memory13 stream13 context13 knowledge13 vector13 processor13", 18),
        ["memory13 stream13", "context13", "knowledge13", "vector13", "processor13"],
    ),
    (
        ("memory13 stream13 context13 knowledge13 vector13 processor13", 28),
        ["memory13 stream13 context13", "knowledge13 vector13", "processor13"],
    ),
    (
        ("stream13 context13 knowledge13 vector13 processor13 reasoning13", 6),
        ["stream13", "context13", "knowledge13", "vector13", "processor13", "reasoning13"],
    ),
    (
        ("stream13 context13 knowledge13 vector13 processor13 reasoning13", 10),
        ["stream13", "context13", "knowledge13", "vector13", "processor13", "reasoning13"],
    ),
    (
        ("stream13 context13 knowledge13 vector13 processor13 reasoning13", 18),
        ["stream13 context13", "knowledge13", "vector13", "processor13", "reasoning13"],
    ),
    (
        ("stream13 context13 knowledge13 vector13 processor13 reasoning13", 28),
        ["stream13 context13", "knowledge13 vector13", "processor13 reasoning13"],
    ),
    (
        ("context13 knowledge13 vector13 processor13 reasoning13 machine13", 6),
        ["context13", "knowledge13", "vector13", "processor13", "reasoning13", "machine13"],
    ),
    (
        ("context13 knowledge13 vector13 processor13 reasoning13 machine13", 10),
        ["context13", "knowledge13", "vector13", "processor13", "reasoning13", "machine13"],
    ),
    (
        ("context13 knowledge13 vector13 processor13 reasoning13 machine13", 18),
        ["context13", "knowledge13", "vector13", "processor13", "reasoning13", "machine13"],
    ),
    (
        ("context13 knowledge13 vector13 processor13 reasoning13 machine13", 28),
        ["context13 knowledge13", "vector13 processor13", "reasoning13 machine13"],
    ),
    (
        ("knowledge13 vector13 processor13 reasoning13 machine13 learning13", 6),
        ["knowledge13", "vector13", "processor13", "reasoning13", "machine13", "learning13"],
    ),
    (
        ("knowledge13 vector13 processor13 reasoning13 machine13 learning13", 10),
        ["knowledge13", "vector13", "processor13", "reasoning13", "machine13", "learning13"],
    ),
    (
        ("knowledge13 vector13 processor13 reasoning13 machine13 learning13", 18),
        ["knowledge13", "vector13", "processor13", "reasoning13", "machine13", "learning13"],
    ),
    (
        ("knowledge13 vector13 processor13 reasoning13 machine13 learning13", 28),
        ["knowledge13 vector13", "processor13 reasoning13", "machine13 learning13"],
    ),
    (
        ("vector13 processor13 reasoning13 machine13 learning13 model13", 6),
        ["vector13", "processor13", "reasoning13", "machine13", "learning13", "model13"],
    ),
    (
        ("vector13 processor13 reasoning13 machine13 learning13 model13", 10),
        ["vector13", "processor13", "reasoning13", "machine13", "learning13", "model13"],
    ),
    (
        ("vector13 processor13 reasoning13 machine13 learning13 model13", 18),
        ["vector13", "processor13", "reasoning13", "machine13", "learning13 model13"],
    ),
    (
        ("vector13 processor13 reasoning13 machine13 learning13 model13", 28),
        ["vector13 processor13", "reasoning13 machine13", "learning13 model13"],
    ),
    (
        ("processor13 reasoning13 machine13 learning13 model13 token13", 6),
        ["processor13", "reasoning13", "machine13", "learning13", "model13", "token13"],
    ),
    (
        ("processor13 reasoning13 machine13 learning13 model13 token13", 10),
        ["processor13", "reasoning13", "machine13", "learning13", "model13", "token13"],
    ),
    (
        ("processor13 reasoning13 machine13 learning13 model13 token13", 18),
        ["processor13", "reasoning13", "machine13", "learning13 model13", "token13"],
    ),
    (
        ("processor13 reasoning13 machine13 learning13 model13 token13", 28),
        ["processor13 reasoning13", "machine13 learning13 model13", "token13"],
    ),
    (
        ("reasoning13 machine13 learning13 model13 token13 prompt13", 6),
        ["reasoning13", "machine13", "learning13", "model13", "token13", "prompt13"],
    ),
    (
        ("reasoning13 machine13 learning13 model13 token13 prompt13", 10),
        ["reasoning13", "machine13", "learning13", "model13", "token13", "prompt13"],
    ),
    (
        ("reasoning13 machine13 learning13 model13 token13 prompt13", 18),
        ["reasoning13", "machine13", "learning13 model13", "token13 prompt13"],
    ),
    (
        ("reasoning13 machine13 learning13 model13 token13 prompt13", 28),
        ["reasoning13 machine13", "learning13 model13 token13", "prompt13"],
    ),
    (
        ("machine13 learning13 model13 token13 prompt13 session13", 6),
        ["machine13", "learning13", "model13", "token13", "prompt13", "session13"],
    ),
    (
        ("machine13 learning13 model13 token13 prompt13 session13", 10),
        ["machine13", "learning13", "model13", "token13", "prompt13", "session13"],
    ),
    (
        ("machine13 learning13 model13 token13 prompt13 session13", 18),
        ["machine13", "learning13 model13", "token13 prompt13", "session13"],
    ),
    (
        ("machine13 learning13 model13 token13 prompt13 session13", 28),
        ["machine13 learning13 model13", "token13 prompt13 session13"],
    ),
    (
        ("learning13 model13 token13 prompt13 session13 library13", 6),
        ["learning13", "model13", "token13", "prompt13", "session13", "library13"],
    ),
    (
        ("learning13 model13 token13 prompt13 session13 library13", 10),
        ["learning13", "model13", "token13", "prompt13", "session13", "library13"],
    ),
    (
        ("learning13 model13 token13 prompt13 session13 library13", 18),
        ["learning13 model13", "token13 prompt13", "session13", "library13"],
    ),
    (
        ("learning13 model13 token13 prompt13 session13 library13", 28),
        ["learning13 model13 token13", "prompt13 session13 library13"],
    ),
    (
        ("model13 token13 prompt13 session13 library13 service13", 6),
        ["model13", "token13", "prompt13", "session13", "library13", "service13"],
    ),
    (
        ("model13 token13 prompt13 session13 library13 service13", 10),
        ["model13", "token13", "prompt13", "session13", "library13", "service13"],
    ),
    (
        ("model13 token13 prompt13 session13 library13 service13", 18),
        ["model13 token13", "prompt13 session13", "library13", "service13"],
    ),
    (
        ("model13 token13 prompt13 session13 library13 service13", 28),
        ["model13 token13 prompt13", "session13 library13", "service13"],
    ),
    (
        ("token13 prompt13 session13 library13 service13 gateway13", 6),
        ["token13", "prompt13", "session13", "library13", "service13", "gateway13"],
    ),
    (
        ("token13 prompt13 session13 library13 service13 gateway13", 10),
        ["token13", "prompt13", "session13", "library13", "service13", "gateway13"],
    ),
    (
        ("token13 prompt13 session13 library13 service13 gateway13", 18),
        ["token13 prompt13", "session13", "library13", "service13", "gateway13"],
    ),
    (
        ("token13 prompt13 session13 library13 service13 gateway13", 28),
        ["token13 prompt13 session13", "library13 service13", "gateway13"],
    ),
    (
        ("prompt13 session13 library13 service13 gateway13 storage13", 6),
        ["prompt13", "session13", "library13", "service13", "gateway13", "storage13"],
    ),
    (
        ("prompt13 session13 library13 service13 gateway13 storage13", 10),
        ["prompt13", "session13", "library13", "service13", "gateway13", "storage13"],
    ),
    (
        ("prompt13 session13 library13 service13 gateway13 storage13", 18),
        ["prompt13 session13", "library13", "service13", "gateway13", "storage13"],
    ),
    (
        ("prompt13 session13 library13 service13 gateway13 storage13", 28),
        ["prompt13 session13 library13", "service13 gateway13", "storage13"],
    ),
    (
        ("session13 library13 service13 gateway13 storage13 network13", 6),
        ["session13", "library13", "service13", "gateway13", "storage13", "network13"],
    ),
    (
        ("session13 library13 service13 gateway13 storage13 network13", 10),
        ["session13", "library13", "service13", "gateway13", "storage13", "network13"],
    ),
    (
        ("session13 library13 service13 gateway13 storage13 network13", 18),
        ["session13", "library13", "service13", "gateway13", "storage13", "network13"],
    ),
    (
        ("session13 library13 service13 gateway13 storage13 network13", 28),
        ["session13 library13", "service13 gateway13", "storage13 network13"],
    ),
    (
        ("library13 service13 gateway13 storage13 network13 latency13", 6),
        ["library13", "service13", "gateway13", "storage13", "network13", "latency13"],
    ),
    (
        ("library13 service13 gateway13 storage13 network13 latency13", 10),
        ["library13", "service13", "gateway13", "storage13", "network13", "latency13"],
    ),
    (
        ("library13 service13 gateway13 storage13 network13 latency13", 18),
        ["library13", "service13", "gateway13", "storage13", "network13", "latency13"],
    ),
    (
        ("library13 service13 gateway13 storage13 network13 latency13", 28),
        ["library13 service13", "gateway13 storage13", "network13 latency13"],
    ),
    (
        ("service13 gateway13 storage13 network13 latency13 buffer13", 6),
        ["service13", "gateway13", "storage13", "network13", "latency13", "buffer13"],
    ),
    (
        ("service13 gateway13 storage13 network13 latency13 buffer13", 10),
        ["service13", "gateway13", "storage13", "network13", "latency13", "buffer13"],
    ),
    (
        ("service13 gateway13 storage13 network13 latency13 buffer13", 18),
        ["service13", "gateway13", "storage13", "network13", "latency13 buffer13"],
    ),
    (
        ("service13 gateway13 storage13 network13 latency13 buffer13", 28),
        ["service13 gateway13", "storage13 network13", "latency13 buffer13"],
    ),
    (
        ("gateway13 storage13 network13 latency13 buffer13 queue13", 6),
        ["gateway13", "storage13", "network13", "latency13", "buffer13", "queue13"],
    ),
    (
        ("gateway13 storage13 network13 latency13 buffer13 queue13", 10),
        ["gateway13", "storage13", "network13", "latency13", "buffer13", "queue13"],
    ),
    (
        ("gateway13 storage13 network13 latency13 buffer13 queue13", 18),
        ["gateway13", "storage13", "network13", "latency13 buffer13", "queue13"],
    ),
    (
        ("gateway13 storage13 network13 latency13 buffer13 queue13", 28),
        ["gateway13 storage13", "network13 latency13 buffer13", "queue13"],
    ),
    (
        ("storage13 network13 latency13 buffer13 queue13 worker13", 6),
        ["storage13", "network13", "latency13", "buffer13", "queue13", "worker13"],
    ),
    (
        ("storage13 network13 latency13 buffer13 queue13 worker13", 10),
        ["storage13", "network13", "latency13", "buffer13", "queue13", "worker13"],
    ),
    (
        ("storage13 network13 latency13 buffer13 queue13 worker13", 18),
        ["storage13", "network13", "latency13 buffer13", "queue13 worker13"],
    ),
    (
        ("storage13 network13 latency13 buffer13 queue13 worker13", 28),
        ["storage13 network13", "latency13 buffer13 queue13", "worker13"],
    ),
    (
        ("network13 latency13 buffer13 queue13 worker13 kernel13", 6),
        ["network13", "latency13", "buffer13", "queue13", "worker13", "kernel13"],
    ),
    (
        ("network13 latency13 buffer13 queue13 worker13 kernel13", 10),
        ["network13", "latency13", "buffer13", "queue13", "worker13", "kernel13"],
    ),
    (
        ("network13 latency13 buffer13 queue13 worker13 kernel13", 18),
        ["network13", "latency13 buffer13", "queue13 worker13", "kernel13"],
    ),
    (
        ("network13 latency13 buffer13 queue13 worker13 kernel13", 28),
        ["network13 latency13 buffer13", "queue13 worker13 kernel13"],
    ),
    (
        ("latency13 buffer13 queue13 worker13 kernel13 signal13", 6),
        ["latency13", "buffer13", "queue13", "worker13", "kernel13", "signal13"],
    ),
    (
        ("latency13 buffer13 queue13 worker13 kernel13 signal13", 10),
        ["latency13", "buffer13", "queue13", "worker13", "kernel13", "signal13"],
    ),
    (
        ("latency13 buffer13 queue13 worker13 kernel13 signal13", 18),
        ["latency13 buffer13", "queue13 worker13", "kernel13 signal13"],
    ),
    (
        ("latency13 buffer13 queue13 worker13 kernel13 signal13", 28),
        ["latency13 buffer13 queue13", "worker13 kernel13 signal13"],
    ),
    (
        ("buffer13 queue13 worker13 kernel13 signal13 packet13", 6),
        ["buffer13", "queue13", "worker13", "kernel13", "signal13", "packet13"],
    ),
    (
        ("buffer13 queue13 worker13 kernel13 signal13 packet13", 10),
        ["buffer13", "queue13", "worker13", "kernel13", "signal13", "packet13"],
    ),
    (
        ("buffer13 queue13 worker13 kernel13 signal13 packet13", 18),
        ["buffer13 queue13", "worker13 kernel13", "signal13 packet13"],
    ),
    (
        ("buffer13 queue13 worker13 kernel13 signal13 packet13", 28),
        ["buffer13 queue13 worker13", "kernel13 signal13 packet13"],
    ),
    (
        ("queue13 worker13 kernel13 signal13 packet13 router13", 6),
        ["queue13", "worker13", "kernel13", "signal13", "packet13", "router13"],
    ),
    (
        ("queue13 worker13 kernel13 signal13 packet13 router13", 10),
        ["queue13", "worker13", "kernel13", "signal13", "packet13", "router13"],
    ),
    (
        ("queue13 worker13 kernel13 signal13 packet13 router13", 18),
        ["queue13 worker13", "kernel13 signal13", "packet13 router13"],
    ),
    (
        ("queue13 worker13 kernel13 signal13 packet13 router13", 28),
        ["queue13 worker13 kernel13", "signal13 packet13 router13"],
    ),
    (
        ("worker13 kernel13 signal13 packet13 router13 cluster13", 6),
        ["worker13", "kernel13", "signal13", "packet13", "router13", "cluster13"],
    ),
    (
        ("worker13 kernel13 signal13 packet13 router13 cluster13", 10),
        ["worker13", "kernel13", "signal13", "packet13", "router13", "cluster13"],
    ),
    (
        ("worker13 kernel13 signal13 packet13 router13 cluster13", 18),
        ["worker13 kernel13", "signal13 packet13", "router13 cluster13"],
    ),
    (
        ("worker13 kernel13 signal13 packet13 router13 cluster13", 28),
        ["worker13 kernel13 signal13", "packet13 router13 cluster13"],
    ),
    (
        ("kernel13 signal13 packet13 router13 cluster13 mirror13", 6),
        ["kernel13", "signal13", "packet13", "router13", "cluster13", "mirror13"],
    ),
    (
        ("kernel13 signal13 packet13 router13 cluster13 mirror13", 10),
        ["kernel13", "signal13", "packet13", "router13", "cluster13", "mirror13"],
    ),
    (
        ("kernel13 signal13 packet13 router13 cluster13 mirror13", 18),
        ["kernel13 signal13", "packet13 router13", "cluster13 mirror13"],
    ),
    (
        ("kernel13 signal13 packet13 router13 cluster13 mirror13", 28),
        ["kernel13 signal13 packet13", "router13 cluster13 mirror13"],
    ),
    (
        ("signal13 packet13 router13 cluster13 mirror13 filter13", 6),
        ["signal13", "packet13", "router13", "cluster13", "mirror13", "filter13"],
    ),
    (
        ("signal13 packet13 router13 cluster13 mirror13 filter13", 10),
        ["signal13", "packet13", "router13", "cluster13", "mirror13", "filter13"],
    ),
    (
        ("signal13 packet13 router13 cluster13 mirror13 filter13", 18),
        ["signal13 packet13", "router13 cluster13", "mirror13 filter13"],
    ),
    (
        ("signal13 packet13 router13 cluster13 mirror13 filter13", 28),
        ["signal13 packet13 router13", "cluster13 mirror13 filter13"],
    ),
    (
        ("packet13 router13 cluster13 mirror13 filter13 ranking13", 6),
        ["packet13", "router13", "cluster13", "mirror13", "filter13", "ranking13"],
    ),
    (
        ("packet13 router13 cluster13 mirror13 filter13 ranking13", 10),
        ["packet13", "router13", "cluster13", "mirror13", "filter13", "ranking13"],
    ),
    (
        ("packet13 router13 cluster13 mirror13 filter13 ranking13", 18),
        ["packet13 router13", "cluster13 mirror13", "filter13 ranking13"],
    ),
    (
        ("packet13 router13 cluster13 mirror13 filter13 ranking13", 28),
        ["packet13 router13 cluster13", "mirror13 filter13 ranking13"],
    ),
    (
        ("router13 cluster13 mirror13 filter13 ranking13 encoding13", 6),
        ["router13", "cluster13", "mirror13", "filter13", "ranking13", "encoding13"],
    ),
    (
        ("router13 cluster13 mirror13 filter13 ranking13 encoding13", 10),
        ["router13", "cluster13", "mirror13", "filter13", "ranking13", "encoding13"],
    ),
    (
        ("router13 cluster13 mirror13 filter13 ranking13 encoding13", 18),
        ["router13 cluster13", "mirror13 filter13", "ranking13", "encoding13"],
    ),
    (
        ("router13 cluster13 mirror13 filter13 ranking13 encoding13", 28),
        ["router13 cluster13 mirror13", "filter13 ranking13", "encoding13"],
    ),
    (
        ("cluster13 mirror13 filter13 ranking13 encoding13 mapping13", 6),
        ["cluster13", "mirror13", "filter13", "ranking13", "encoding13", "mapping13"],
    ),
    (
        ("cluster13 mirror13 filter13 ranking13 encoding13 mapping13", 10),
        ["cluster13", "mirror13", "filter13", "ranking13", "encoding13", "mapping13"],
    ),
    (
        ("cluster13 mirror13 filter13 ranking13 encoding13 mapping13", 18),
        ["cluster13 mirror13", "filter13 ranking13", "encoding13", "mapping13"],
    ),
    (
        ("cluster13 mirror13 filter13 ranking13 encoding13 mapping13", 28),
        ["cluster13 mirror13 filter13", "ranking13 encoding13", "mapping13"],
    ),
    (
        ("mirror13 filter13 ranking13 encoding13 mapping13 record13", 6),
        ["mirror13", "filter13", "ranking13", "encoding13", "mapping13", "record13"],
    ),
    (
        ("mirror13 filter13 ranking13 encoding13 mapping13 record13", 10),
        ["mirror13", "filter13", "ranking13", "encoding13", "mapping13", "record13"],
    ),
    (
        ("mirror13 filter13 ranking13 encoding13 mapping13 record13", 18),
        ["mirror13 filter13", "ranking13", "encoding13", "mapping13 record13"],
    ),
    (
        ("mirror13 filter13 ranking13 encoding13 mapping13 record13", 28),
        ["mirror13 filter13 ranking13", "encoding13 mapping13", "record13"],
    ),
    (
        ("filter13 ranking13 encoding13 mapping13 record13 candle13", 6),
        ["filter13", "ranking13", "encoding13", "mapping13", "record13", "candle13"],
    ),
    (
        ("filter13 ranking13 encoding13 mapping13 record13 candle13", 10),
        ["filter13", "ranking13", "encoding13", "mapping13", "record13", "candle13"],
    ),
    (
        ("filter13 ranking13 encoding13 mapping13 record13 candle13", 18),
        ["filter13 ranking13", "encoding13", "mapping13 record13", "candle13"],
    ),
    (
        ("filter13 ranking13 encoding13 mapping13 record13 candle13", 28),
        ["filter13 ranking13", "encoding13 mapping13", "record13 candle13"],
    ),
    (
        ("ranking13 encoding13 mapping13 record13 candle13 thread13", 6),
        ["ranking13", "encoding13", "mapping13", "record13", "candle13", "thread13"],
    ),
    (
        ("ranking13 encoding13 mapping13 record13 candle13 thread13", 10),
        ["ranking13", "encoding13", "mapping13", "record13", "candle13", "thread13"],
    ),
    (
        ("ranking13 encoding13 mapping13 record13 candle13 thread13", 18),
        ["ranking13", "encoding13", "mapping13 record13", "candle13 thread13"],
    ),
    (
        ("ranking13 encoding13 mapping13 record13 candle13 thread13", 28),
        ["ranking13 encoding13", "mapping13 record13 candle13", "thread13"],
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
