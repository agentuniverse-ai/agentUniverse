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
        ("round 87: the quick brown fox jumps over the lazy dog", 4),
        ["round", "87:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 87: the quick brown fox jumps over the lazy dog", 8),
        ["round", "87: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 87: the quick brown fox jumps over the lazy dog", 12),
        ["round 87:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 87: the quick brown fox jumps over the lazy dog", 16),
        ["round 87: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 87: the quick brown fox jumps over the lazy dog", 24),
        ["round 87: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 87: the quick brown fox jumps over the lazy dog", 32),
        ["round 87: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 87: agentuniverse is a framework for multi agents", 4),
        ["round", "87:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 87: agentuniverse is a framework for multi agents", 8),
        ["round", "87:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 87: agentuniverse is a framework for multi agents", 12),
        ["round 87:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 87: agentuniverse is a framework for multi agents", 16),
        ["round 87:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 87: agentuniverse is a framework for multi agents", 24),
        ["round 87: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 87: agentuniverse is a framework for multi agents", 32),
        ["round 87: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 87: knowledge stored as vectors enables retrieval", 4),
        ["round", "87:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 87: knowledge stored as vectors enables retrieval", 8),
        ["round", "87:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 87: knowledge stored as vectors enables retrieval", 12),
        ["round 87:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 87: knowledge stored as vectors enables retrieval", 16),
        ["round 87:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 87: knowledge stored as vectors enables retrieval", 24),
        ["round 87: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 87: knowledge stored as vectors enables retrieval", 32),
        ["round 87: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 87: the processor reads the record then stops", 4),
        ["round", "87:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 87: the processor reads the record then stops", 8),
        ["round", "87: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 87: the processor reads the record then stops", 12),
        ["round 87:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 87: the processor reads the record then stops", 16),
        ["round 87: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 87: the processor reads the record then stops", 24),
        ["round 87: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 87: the processor reads the record then stops", 32),
        ["round 87: the processor reads", "the record then stops"],
    ),
    (
        ("round 87: a worker pulls the next task from the queue", 4),
        ["round", "87:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 87: a worker pulls the next task from the queue", 8),
        ["round", "87: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 87: a worker pulls the next task from the queue", 12),
        ["round 87: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 87: a worker pulls the next task from the queue", 16),
        ["round 87: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 87: a worker pulls the next task from the queue", 24),
        ["round 87: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 87: a worker pulls the next task from the queue", 32),
        ["round 87: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 87: signals travel through the network layer", 4),
        ["round", "87:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 87: signals travel through the network layer", 8),
        ["round", "87:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 87: signals travel through the network layer", 12),
        ["round 87:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 87: signals travel through the network layer", 16),
        ["round 87:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 87: signals travel through the network layer", 24),
        ["round 87: signals travel", "through the network", "layer"],
    ),
    (
        ("round 87: signals travel through the network layer", 32),
        ["round 87: signals travel through", "the network layer"],
    ),
    (
        ("round 87: the gateway routes each request by policy", 4),
        ["round", "87:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 87: the gateway routes each request by policy", 8),
        ["round", "87: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 87: the gateway routes each request by policy", 12),
        ["round 87:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 87: the gateway routes each request by policy", 16),
        ["round 87: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 87: the gateway routes each request by policy", 24),
        ["round 87: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 87: the gateway routes each request by policy", 32),
        ["round 87: the gateway routes", "each request by policy"],
    ),
    (
        ("round 87: memory grows until the buffer is full", 4),
        ["round", "87:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 87: memory grows until the buffer is full", 8),
        ["round", "87:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 87: memory grows until the buffer is full", 12),
        ["round 87:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 87: memory grows until the buffer is full", 16),
        ["round 87: memory", "grows until the", "buffer is full"],
    ),
    (("round 87: memory grows until the buffer is full", 24), ["round 87: memory grows", "until the buffer is full"]),
    (("round 87: memory grows until the buffer is full", 32), ["round 87: memory grows until the", "buffer is full"]),
    (
        ("round 87: the cluster mirrors every packet twice", 4),
        ["round", "87:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 87: the cluster mirrors every packet twice", 8),
        ["round", "87: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 87: the cluster mirrors every packet twice", 12),
        ["round 87:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 87: the cluster mirrors every packet twice", 16),
        ["round 87: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 87: the cluster mirrors every packet twice", 24),
        ["round 87: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 87: the cluster mirrors every packet twice", 32), ["round 87: the cluster mirrors", "every packet twice"]),
    (
        ("round 87: ranking uses tokens learned from the corpus", 4),
        ["round", "87:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 87: ranking uses tokens learned from the corpus", 8),
        ["round", "87:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 87: ranking uses tokens learned from the corpus", 12),
        ["round 87:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 87: ranking uses tokens learned from the corpus", 16),
        ["round 87:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 87: ranking uses tokens learned from the corpus", 24),
        ["round 87: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 87: ranking uses tokens learned from the corpus", 32),
        ["round 87: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 87: a long session ends when the candle dies", 4),
        ["round", "87:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 87: a long session ends when the candle dies", 8),
        ["round", "87: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 87: a long session ends when the candle dies", 12),
        ["round 87: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 87: a long session ends when the candle dies", 16),
        ["round 87: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 87: a long session ends when the candle dies", 24),
        ["round 87: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 87: a long session ends when the candle dies", 32),
        ["round 87: a long session ends", "when the candle dies"],
    ),
    (
        ("round 87: encode the prompt then map the result", 4),
        ["round", "87:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 87: encode the prompt then map the result", 8),
        ["round", "87:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 87: encode the prompt then map the result", 12),
        ["round 87:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 87: encode the prompt then map the result", 16),
        ["round 87: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 87: encode the prompt then map the result", 24),
        ["round 87: encode the", "prompt then map the", "result"],
    ),
    (("round 87: encode the prompt then map the result", 32), ["round 87: encode the prompt then", "map the result"]),
    (
        ("round 87: the kernel wakes the worker at dawn", 4),
        ["round", "87:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 87: the kernel wakes the worker at dawn", 8),
        ["round", "87: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 87: the kernel wakes the worker at dawn", 12),
        ["round 87:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 87: the kernel wakes the worker at dawn", 16), ["round 87: the", "kernel wakes the", "worker at dawn"]),
    (("round 87: the kernel wakes the worker at dawn", 24), ["round 87: the kernel", "wakes the worker at dawn"]),
    (("round 87: the kernel wakes the worker at dawn", 32), ["round 87: the kernel wakes the", "worker at dawn"]),
    (
        ("round 87: service latency drops after the patch", 4),
        ["round", "87:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 87: service latency drops after the patch", 8),
        ["round", "87:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 87: service latency drops after the patch", 12),
        ["round 87:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 87: service latency drops after the patch", 16),
        ["round 87:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 87: service latency drops after the patch", 24),
        ["round 87: service", "latency drops after the", "patch"],
    ),
    (("round 87: service latency drops after the patch", 32), ["round 87: service latency drops", "after the patch"]),
    (
        ("round 87: the library caches every vector it sees", 4),
        ["round", "87:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 87: the library caches every vector it sees", 8),
        ["round", "87: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 87: the library caches every vector it sees", 12),
        ["round 87:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 87: the library caches every vector it sees", 16),
        ["round 87: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 87: the library caches every vector it sees", 24),
        ["round 87: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 87: the library caches every vector it sees", 32),
        ["round 87: the library caches", "every vector it sees"],
    ),
    (
        ("round 87: agents argue then the debate resolves", 4),
        ["round", "87:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 87: agents argue then the debate resolves", 8),
        ["round", "87:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 87: agents argue then the debate resolves", 12),
        ["round 87:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 87: agents argue then the debate resolves", 16),
        ["round 87: agents", "argue then the", "debate resolves"],
    ),
    (("round 87: agents argue then the debate resolves", 24), ["round 87: agents argue", "then the debate resolves"]),
    (("round 87: agents argue then the debate resolves", 32), ["round 87: agents argue then the", "debate resolves"]),
    (
        ("round 87: the filter keeps only strong matches", 4),
        ["round", "87:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 87: the filter keeps only strong matches", 8),
        ["round", "87: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 87: the filter keeps only strong matches", 12),
        ["round 87:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 87: the filter keeps only strong matches", 16),
        ["round 87: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 87: the filter keeps only strong matches", 24), ["round 87: the filter", "keeps only strong", "matches"]),
    (("round 87: the filter keeps only strong matches", 32), ["round 87: the filter keeps only", "strong matches"]),
    (
        ("round 87: the model answers with a short reply", 4),
        ["round", "87:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 87: the model answers with a short reply", 8),
        ["round", "87: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 87: the model answers with a short reply", 12),
        ["round 87:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 87: the model answers with a short reply", 16),
        ["round 87: the", "model answers", "with a short", "reply"],
    ),
    (("round 87: the model answers with a short reply", 24), ["round 87: the model", "answers with a short", "reply"]),
    (("round 87: the model answers with a short reply", 32), ["round 87: the model answers with", "a short reply"]),
    (
        ("round 87: the recorder stores the reasoning trace", 4),
        ["round", "87:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 87: the recorder stores the reasoning trace", 8),
        ["round", "87: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 87: the recorder stores the reasoning trace", 12),
        ["round 87:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 87: the recorder stores the reasoning trace", 16),
        ["round 87: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 87: the recorder stores the reasoning trace", 24),
        ["round 87: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 87: the recorder stores the reasoning trace", 32),
        ["round 87: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 87: the angel watches the processor run", 4),
        ["round", "87:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 87: the angel watches the processor run", 8),
        ["round", "87: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 87: the angel watches the processor run", 12),
        ["round 87:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 87: the angel watches the processor run", 16), ["round 87: the", "angel watches", "the processor", "run"]),
    (("round 87: the angel watches the processor run", 24), ["round 87: the angel", "watches the processor", "run"]),
    (("round 87: the angel watches the processor run", 32), ["round 87: the angel watches the", "processor run"]),
    (
        ("round 87: angle of the vector decides the match", 4),
        ["round", "87:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 87: angle of the vector decides the match", 8),
        ["round", "87:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 87: angle of the vector decides the match", 12),
        ["round 87:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 87: angle of the vector decides the match", 16),
        ["round 87: angle", "of the vector", "decides the", "match"],
    ),
    (("round 87: angle of the vector decides the match", 24), ["round 87: angle of the", "vector decides the match"]),
    (("round 87: angle of the vector decides the match", 32), ["round 87: angle of the vector", "decides the match"]),
    (
        ("round 87: the candle burns twice as long at night", 4),
        ["round", "87:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 87: the candle burns twice as long at night", 8),
        ["round", "87: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 87: the candle burns twice as long at night", 12),
        ["round 87:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 87: the candle burns twice as long at night", 16),
        ["round 87: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 87: the candle burns twice as long at night", 24),
        ["round 87: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 87: the candle burns twice as long at night", 32),
        ["round 87: the candle burns twice", "as long at night"],
    ),
    (
        ("round 87: a mirror of the universe in one line", 4),
        ["round", "87:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 87: a mirror of the universe in one line", 8),
        ["round", "87: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 87: a mirror of the universe in one line", 12),
        ["round 87: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 87: a mirror of the universe in one line", 16),
        ["round 87: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 87: a mirror of the universe in one line", 24), ["round 87: a mirror of", "the universe in one line"]),
    (("round 87: a mirror of the universe in one line", 32), ["round 87: a mirror of the", "universe in one line"]),
    (
        ("round 87: the queue drains before the storm", 4),
        ["round", "87:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 87: the queue drains before the storm", 8),
        ["round", "87: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 87: the queue drains before the storm", 12), ["round 87:", "the queue", "drains", "before the", "storm"]),
    (("round 87: the queue drains before the storm", 16), ["round 87: the", "queue drains", "before the storm"]),
    (("round 87: the queue drains before the storm", 24), ["round 87: the queue", "drains before the storm"]),
    (("round 87: the queue drains before the storm", 32), ["round 87: the queue drains", "before the storm"]),
    (
        ("kitten87 sitting87 agent87 angle87 universe87 memory87", 6),
        ["kitten87", "sitting87", "agent87", "angle87", "universe87", "memory87"],
    ),
    (
        ("kitten87 sitting87 agent87 angle87 universe87 memory87", 10),
        ["kitten87", "sitting87", "agent87", "angle87", "universe87", "memory87"],
    ),
    (
        ("kitten87 sitting87 agent87 angle87 universe87 memory87", 18),
        ["kitten87 sitting87", "agent87 angle87", "universe87", "memory87"],
    ),
    (
        ("kitten87 sitting87 agent87 angle87 universe87 memory87", 28),
        ["kitten87 sitting87 agent87", "angle87 universe87 memory87"],
    ),
    (
        ("sitting87 agent87 angle87 universe87 memory87 stream87", 6),
        ["sitting87", "agent87", "angle87", "universe87", "memory87", "stream87"],
    ),
    (
        ("sitting87 agent87 angle87 universe87 memory87 stream87", 10),
        ["sitting87", "agent87", "angle87", "universe87", "memory87", "stream87"],
    ),
    (
        ("sitting87 agent87 angle87 universe87 memory87 stream87", 18),
        ["sitting87 agent87", "angle87 universe87", "memory87 stream87"],
    ),
    (
        ("sitting87 agent87 angle87 universe87 memory87 stream87", 28),
        ["sitting87 agent87 angle87", "universe87 memory87 stream87"],
    ),
    (
        ("agent87 angle87 universe87 memory87 stream87 context87", 6),
        ["agent87", "angle87", "universe87", "memory87", "stream87", "context87"],
    ),
    (
        ("agent87 angle87 universe87 memory87 stream87 context87", 10),
        ["agent87", "angle87", "universe87", "memory87", "stream87", "context87"],
    ),
    (
        ("agent87 angle87 universe87 memory87 stream87 context87", 18),
        ["agent87 angle87", "universe87", "memory87 stream87", "context87"],
    ),
    (
        ("agent87 angle87 universe87 memory87 stream87 context87", 28),
        ["agent87 angle87 universe87", "memory87 stream87 context87"],
    ),
    (
        ("angle87 universe87 memory87 stream87 context87 knowledge87", 6),
        ["angle87", "universe87", "memory87", "stream87", "context87", "knowledge87"],
    ),
    (
        ("angle87 universe87 memory87 stream87 context87 knowledge87", 10),
        ["angle87", "universe87", "memory87", "stream87", "context87", "knowledge87"],
    ),
    (
        ("angle87 universe87 memory87 stream87 context87 knowledge87", 18),
        ["angle87 universe87", "memory87 stream87", "context87", "knowledge87"],
    ),
    (
        ("angle87 universe87 memory87 stream87 context87 knowledge87", 28),
        ["angle87 universe87 memory87", "stream87 context87", "knowledge87"],
    ),
    (
        ("universe87 memory87 stream87 context87 knowledge87 vector87", 6),
        ["universe87", "memory87", "stream87", "context87", "knowledge87", "vector87"],
    ),
    (
        ("universe87 memory87 stream87 context87 knowledge87 vector87", 10),
        ["universe87", "memory87", "stream87", "context87", "knowledge87", "vector87"],
    ),
    (
        ("universe87 memory87 stream87 context87 knowledge87 vector87", 18),
        ["universe87", "memory87 stream87", "context87", "knowledge87", "vector87"],
    ),
    (
        ("universe87 memory87 stream87 context87 knowledge87 vector87", 28),
        ["universe87 memory87 stream87", "context87 knowledge87", "vector87"],
    ),
    (
        ("memory87 stream87 context87 knowledge87 vector87 processor87", 6),
        ["memory87", "stream87", "context87", "knowledge87", "vector87", "processor87"],
    ),
    (
        ("memory87 stream87 context87 knowledge87 vector87 processor87", 10),
        ["memory87", "stream87", "context87", "knowledge87", "vector87", "processor87"],
    ),
    (
        ("memory87 stream87 context87 knowledge87 vector87 processor87", 18),
        ["memory87 stream87", "context87", "knowledge87", "vector87", "processor87"],
    ),
    (
        ("memory87 stream87 context87 knowledge87 vector87 processor87", 28),
        ["memory87 stream87 context87", "knowledge87 vector87", "processor87"],
    ),
    (
        ("stream87 context87 knowledge87 vector87 processor87 reasoning87", 6),
        ["stream87", "context87", "knowledge87", "vector87", "processor87", "reasoning87"],
    ),
    (
        ("stream87 context87 knowledge87 vector87 processor87 reasoning87", 10),
        ["stream87", "context87", "knowledge87", "vector87", "processor87", "reasoning87"],
    ),
    (
        ("stream87 context87 knowledge87 vector87 processor87 reasoning87", 18),
        ["stream87 context87", "knowledge87", "vector87", "processor87", "reasoning87"],
    ),
    (
        ("stream87 context87 knowledge87 vector87 processor87 reasoning87", 28),
        ["stream87 context87", "knowledge87 vector87", "processor87 reasoning87"],
    ),
    (
        ("context87 knowledge87 vector87 processor87 reasoning87 machine87", 6),
        ["context87", "knowledge87", "vector87", "processor87", "reasoning87", "machine87"],
    ),
    (
        ("context87 knowledge87 vector87 processor87 reasoning87 machine87", 10),
        ["context87", "knowledge87", "vector87", "processor87", "reasoning87", "machine87"],
    ),
    (
        ("context87 knowledge87 vector87 processor87 reasoning87 machine87", 18),
        ["context87", "knowledge87", "vector87", "processor87", "reasoning87", "machine87"],
    ),
    (
        ("context87 knowledge87 vector87 processor87 reasoning87 machine87", 28),
        ["context87 knowledge87", "vector87 processor87", "reasoning87 machine87"],
    ),
    (
        ("knowledge87 vector87 processor87 reasoning87 machine87 learning87", 6),
        ["knowledge87", "vector87", "processor87", "reasoning87", "machine87", "learning87"],
    ),
    (
        ("knowledge87 vector87 processor87 reasoning87 machine87 learning87", 10),
        ["knowledge87", "vector87", "processor87", "reasoning87", "machine87", "learning87"],
    ),
    (
        ("knowledge87 vector87 processor87 reasoning87 machine87 learning87", 18),
        ["knowledge87", "vector87", "processor87", "reasoning87", "machine87", "learning87"],
    ),
    (
        ("knowledge87 vector87 processor87 reasoning87 machine87 learning87", 28),
        ["knowledge87 vector87", "processor87 reasoning87", "machine87 learning87"],
    ),
    (
        ("vector87 processor87 reasoning87 machine87 learning87 model87", 6),
        ["vector87", "processor87", "reasoning87", "machine87", "learning87", "model87"],
    ),
    (
        ("vector87 processor87 reasoning87 machine87 learning87 model87", 10),
        ["vector87", "processor87", "reasoning87", "machine87", "learning87", "model87"],
    ),
    (
        ("vector87 processor87 reasoning87 machine87 learning87 model87", 18),
        ["vector87", "processor87", "reasoning87", "machine87", "learning87 model87"],
    ),
    (
        ("vector87 processor87 reasoning87 machine87 learning87 model87", 28),
        ["vector87 processor87", "reasoning87 machine87", "learning87 model87"],
    ),
    (
        ("processor87 reasoning87 machine87 learning87 model87 token87", 6),
        ["processor87", "reasoning87", "machine87", "learning87", "model87", "token87"],
    ),
    (
        ("processor87 reasoning87 machine87 learning87 model87 token87", 10),
        ["processor87", "reasoning87", "machine87", "learning87", "model87", "token87"],
    ),
    (
        ("processor87 reasoning87 machine87 learning87 model87 token87", 18),
        ["processor87", "reasoning87", "machine87", "learning87 model87", "token87"],
    ),
    (
        ("processor87 reasoning87 machine87 learning87 model87 token87", 28),
        ["processor87 reasoning87", "machine87 learning87 model87", "token87"],
    ),
    (
        ("reasoning87 machine87 learning87 model87 token87 prompt87", 6),
        ["reasoning87", "machine87", "learning87", "model87", "token87", "prompt87"],
    ),
    (
        ("reasoning87 machine87 learning87 model87 token87 prompt87", 10),
        ["reasoning87", "machine87", "learning87", "model87", "token87", "prompt87"],
    ),
    (
        ("reasoning87 machine87 learning87 model87 token87 prompt87", 18),
        ["reasoning87", "machine87", "learning87 model87", "token87 prompt87"],
    ),
    (
        ("reasoning87 machine87 learning87 model87 token87 prompt87", 28),
        ["reasoning87 machine87", "learning87 model87 token87", "prompt87"],
    ),
    (
        ("machine87 learning87 model87 token87 prompt87 session87", 6),
        ["machine87", "learning87", "model87", "token87", "prompt87", "session87"],
    ),
    (
        ("machine87 learning87 model87 token87 prompt87 session87", 10),
        ["machine87", "learning87", "model87", "token87", "prompt87", "session87"],
    ),
    (
        ("machine87 learning87 model87 token87 prompt87 session87", 18),
        ["machine87", "learning87 model87", "token87 prompt87", "session87"],
    ),
    (
        ("machine87 learning87 model87 token87 prompt87 session87", 28),
        ["machine87 learning87 model87", "token87 prompt87 session87"],
    ),
    (
        ("learning87 model87 token87 prompt87 session87 library87", 6),
        ["learning87", "model87", "token87", "prompt87", "session87", "library87"],
    ),
    (
        ("learning87 model87 token87 prompt87 session87 library87", 10),
        ["learning87", "model87", "token87", "prompt87", "session87", "library87"],
    ),
    (
        ("learning87 model87 token87 prompt87 session87 library87", 18),
        ["learning87 model87", "token87 prompt87", "session87", "library87"],
    ),
    (
        ("learning87 model87 token87 prompt87 session87 library87", 28),
        ["learning87 model87 token87", "prompt87 session87 library87"],
    ),
    (
        ("model87 token87 prompt87 session87 library87 service87", 6),
        ["model87", "token87", "prompt87", "session87", "library87", "service87"],
    ),
    (
        ("model87 token87 prompt87 session87 library87 service87", 10),
        ["model87", "token87", "prompt87", "session87", "library87", "service87"],
    ),
    (
        ("model87 token87 prompt87 session87 library87 service87", 18),
        ["model87 token87", "prompt87 session87", "library87", "service87"],
    ),
    (
        ("model87 token87 prompt87 session87 library87 service87", 28),
        ["model87 token87 prompt87", "session87 library87", "service87"],
    ),
    (
        ("token87 prompt87 session87 library87 service87 gateway87", 6),
        ["token87", "prompt87", "session87", "library87", "service87", "gateway87"],
    ),
    (
        ("token87 prompt87 session87 library87 service87 gateway87", 10),
        ["token87", "prompt87", "session87", "library87", "service87", "gateway87"],
    ),
    (
        ("token87 prompt87 session87 library87 service87 gateway87", 18),
        ["token87 prompt87", "session87", "library87", "service87", "gateway87"],
    ),
    (
        ("token87 prompt87 session87 library87 service87 gateway87", 28),
        ["token87 prompt87 session87", "library87 service87", "gateway87"],
    ),
    (
        ("prompt87 session87 library87 service87 gateway87 storage87", 6),
        ["prompt87", "session87", "library87", "service87", "gateway87", "storage87"],
    ),
    (
        ("prompt87 session87 library87 service87 gateway87 storage87", 10),
        ["prompt87", "session87", "library87", "service87", "gateway87", "storage87"],
    ),
    (
        ("prompt87 session87 library87 service87 gateway87 storage87", 18),
        ["prompt87 session87", "library87", "service87", "gateway87", "storage87"],
    ),
    (
        ("prompt87 session87 library87 service87 gateway87 storage87", 28),
        ["prompt87 session87 library87", "service87 gateway87", "storage87"],
    ),
    (
        ("session87 library87 service87 gateway87 storage87 network87", 6),
        ["session87", "library87", "service87", "gateway87", "storage87", "network87"],
    ),
    (
        ("session87 library87 service87 gateway87 storage87 network87", 10),
        ["session87", "library87", "service87", "gateway87", "storage87", "network87"],
    ),
    (
        ("session87 library87 service87 gateway87 storage87 network87", 18),
        ["session87", "library87", "service87", "gateway87", "storage87", "network87"],
    ),
    (
        ("session87 library87 service87 gateway87 storage87 network87", 28),
        ["session87 library87", "service87 gateway87", "storage87 network87"],
    ),
    (
        ("library87 service87 gateway87 storage87 network87 latency87", 6),
        ["library87", "service87", "gateway87", "storage87", "network87", "latency87"],
    ),
    (
        ("library87 service87 gateway87 storage87 network87 latency87", 10),
        ["library87", "service87", "gateway87", "storage87", "network87", "latency87"],
    ),
    (
        ("library87 service87 gateway87 storage87 network87 latency87", 18),
        ["library87", "service87", "gateway87", "storage87", "network87", "latency87"],
    ),
    (
        ("library87 service87 gateway87 storage87 network87 latency87", 28),
        ["library87 service87", "gateway87 storage87", "network87 latency87"],
    ),
    (
        ("service87 gateway87 storage87 network87 latency87 buffer87", 6),
        ["service87", "gateway87", "storage87", "network87", "latency87", "buffer87"],
    ),
    (
        ("service87 gateway87 storage87 network87 latency87 buffer87", 10),
        ["service87", "gateway87", "storage87", "network87", "latency87", "buffer87"],
    ),
    (
        ("service87 gateway87 storage87 network87 latency87 buffer87", 18),
        ["service87", "gateway87", "storage87", "network87", "latency87 buffer87"],
    ),
    (
        ("service87 gateway87 storage87 network87 latency87 buffer87", 28),
        ["service87 gateway87", "storage87 network87", "latency87 buffer87"],
    ),
    (
        ("gateway87 storage87 network87 latency87 buffer87 queue87", 6),
        ["gateway87", "storage87", "network87", "latency87", "buffer87", "queue87"],
    ),
    (
        ("gateway87 storage87 network87 latency87 buffer87 queue87", 10),
        ["gateway87", "storage87", "network87", "latency87", "buffer87", "queue87"],
    ),
    (
        ("gateway87 storage87 network87 latency87 buffer87 queue87", 18),
        ["gateway87", "storage87", "network87", "latency87 buffer87", "queue87"],
    ),
    (
        ("gateway87 storage87 network87 latency87 buffer87 queue87", 28),
        ["gateway87 storage87", "network87 latency87 buffer87", "queue87"],
    ),
    (
        ("storage87 network87 latency87 buffer87 queue87 worker87", 6),
        ["storage87", "network87", "latency87", "buffer87", "queue87", "worker87"],
    ),
    (
        ("storage87 network87 latency87 buffer87 queue87 worker87", 10),
        ["storage87", "network87", "latency87", "buffer87", "queue87", "worker87"],
    ),
    (
        ("storage87 network87 latency87 buffer87 queue87 worker87", 18),
        ["storage87", "network87", "latency87 buffer87", "queue87 worker87"],
    ),
    (
        ("storage87 network87 latency87 buffer87 queue87 worker87", 28),
        ["storage87 network87", "latency87 buffer87 queue87", "worker87"],
    ),
    (
        ("network87 latency87 buffer87 queue87 worker87 kernel87", 6),
        ["network87", "latency87", "buffer87", "queue87", "worker87", "kernel87"],
    ),
    (
        ("network87 latency87 buffer87 queue87 worker87 kernel87", 10),
        ["network87", "latency87", "buffer87", "queue87", "worker87", "kernel87"],
    ),
    (
        ("network87 latency87 buffer87 queue87 worker87 kernel87", 18),
        ["network87", "latency87 buffer87", "queue87 worker87", "kernel87"],
    ),
    (
        ("network87 latency87 buffer87 queue87 worker87 kernel87", 28),
        ["network87 latency87 buffer87", "queue87 worker87 kernel87"],
    ),
    (
        ("latency87 buffer87 queue87 worker87 kernel87 signal87", 6),
        ["latency87", "buffer87", "queue87", "worker87", "kernel87", "signal87"],
    ),
    (
        ("latency87 buffer87 queue87 worker87 kernel87 signal87", 10),
        ["latency87", "buffer87", "queue87", "worker87", "kernel87", "signal87"],
    ),
    (
        ("latency87 buffer87 queue87 worker87 kernel87 signal87", 18),
        ["latency87 buffer87", "queue87 worker87", "kernel87 signal87"],
    ),
    (
        ("latency87 buffer87 queue87 worker87 kernel87 signal87", 28),
        ["latency87 buffer87 queue87", "worker87 kernel87 signal87"],
    ),
    (
        ("buffer87 queue87 worker87 kernel87 signal87 packet87", 6),
        ["buffer87", "queue87", "worker87", "kernel87", "signal87", "packet87"],
    ),
    (
        ("buffer87 queue87 worker87 kernel87 signal87 packet87", 10),
        ["buffer87", "queue87", "worker87", "kernel87", "signal87", "packet87"],
    ),
    (
        ("buffer87 queue87 worker87 kernel87 signal87 packet87", 18),
        ["buffer87 queue87", "worker87 kernel87", "signal87 packet87"],
    ),
    (
        ("buffer87 queue87 worker87 kernel87 signal87 packet87", 28),
        ["buffer87 queue87 worker87", "kernel87 signal87 packet87"],
    ),
    (
        ("queue87 worker87 kernel87 signal87 packet87 router87", 6),
        ["queue87", "worker87", "kernel87", "signal87", "packet87", "router87"],
    ),
    (
        ("queue87 worker87 kernel87 signal87 packet87 router87", 10),
        ["queue87", "worker87", "kernel87", "signal87", "packet87", "router87"],
    ),
    (
        ("queue87 worker87 kernel87 signal87 packet87 router87", 18),
        ["queue87 worker87", "kernel87 signal87", "packet87 router87"],
    ),
    (
        ("queue87 worker87 kernel87 signal87 packet87 router87", 28),
        ["queue87 worker87 kernel87", "signal87 packet87 router87"],
    ),
    (
        ("worker87 kernel87 signal87 packet87 router87 cluster87", 6),
        ["worker87", "kernel87", "signal87", "packet87", "router87", "cluster87"],
    ),
    (
        ("worker87 kernel87 signal87 packet87 router87 cluster87", 10),
        ["worker87", "kernel87", "signal87", "packet87", "router87", "cluster87"],
    ),
    (
        ("worker87 kernel87 signal87 packet87 router87 cluster87", 18),
        ["worker87 kernel87", "signal87 packet87", "router87 cluster87"],
    ),
    (
        ("worker87 kernel87 signal87 packet87 router87 cluster87", 28),
        ["worker87 kernel87 signal87", "packet87 router87 cluster87"],
    ),
    (
        ("kernel87 signal87 packet87 router87 cluster87 mirror87", 6),
        ["kernel87", "signal87", "packet87", "router87", "cluster87", "mirror87"],
    ),
    (
        ("kernel87 signal87 packet87 router87 cluster87 mirror87", 10),
        ["kernel87", "signal87", "packet87", "router87", "cluster87", "mirror87"],
    ),
    (
        ("kernel87 signal87 packet87 router87 cluster87 mirror87", 18),
        ["kernel87 signal87", "packet87 router87", "cluster87 mirror87"],
    ),
    (
        ("kernel87 signal87 packet87 router87 cluster87 mirror87", 28),
        ["kernel87 signal87 packet87", "router87 cluster87 mirror87"],
    ),
    (
        ("signal87 packet87 router87 cluster87 mirror87 filter87", 6),
        ["signal87", "packet87", "router87", "cluster87", "mirror87", "filter87"],
    ),
    (
        ("signal87 packet87 router87 cluster87 mirror87 filter87", 10),
        ["signal87", "packet87", "router87", "cluster87", "mirror87", "filter87"],
    ),
    (
        ("signal87 packet87 router87 cluster87 mirror87 filter87", 18),
        ["signal87 packet87", "router87 cluster87", "mirror87 filter87"],
    ),
    (
        ("signal87 packet87 router87 cluster87 mirror87 filter87", 28),
        ["signal87 packet87 router87", "cluster87 mirror87 filter87"],
    ),
    (
        ("packet87 router87 cluster87 mirror87 filter87 ranking87", 6),
        ["packet87", "router87", "cluster87", "mirror87", "filter87", "ranking87"],
    ),
    (
        ("packet87 router87 cluster87 mirror87 filter87 ranking87", 10),
        ["packet87", "router87", "cluster87", "mirror87", "filter87", "ranking87"],
    ),
    (
        ("packet87 router87 cluster87 mirror87 filter87 ranking87", 18),
        ["packet87 router87", "cluster87 mirror87", "filter87 ranking87"],
    ),
    (
        ("packet87 router87 cluster87 mirror87 filter87 ranking87", 28),
        ["packet87 router87 cluster87", "mirror87 filter87 ranking87"],
    ),
    (
        ("router87 cluster87 mirror87 filter87 ranking87 encoding87", 6),
        ["router87", "cluster87", "mirror87", "filter87", "ranking87", "encoding87"],
    ),
    (
        ("router87 cluster87 mirror87 filter87 ranking87 encoding87", 10),
        ["router87", "cluster87", "mirror87", "filter87", "ranking87", "encoding87"],
    ),
    (
        ("router87 cluster87 mirror87 filter87 ranking87 encoding87", 18),
        ["router87 cluster87", "mirror87 filter87", "ranking87", "encoding87"],
    ),
    (
        ("router87 cluster87 mirror87 filter87 ranking87 encoding87", 28),
        ["router87 cluster87 mirror87", "filter87 ranking87", "encoding87"],
    ),
    (
        ("cluster87 mirror87 filter87 ranking87 encoding87 mapping87", 6),
        ["cluster87", "mirror87", "filter87", "ranking87", "encoding87", "mapping87"],
    ),
    (
        ("cluster87 mirror87 filter87 ranking87 encoding87 mapping87", 10),
        ["cluster87", "mirror87", "filter87", "ranking87", "encoding87", "mapping87"],
    ),
    (
        ("cluster87 mirror87 filter87 ranking87 encoding87 mapping87", 18),
        ["cluster87 mirror87", "filter87 ranking87", "encoding87", "mapping87"],
    ),
    (
        ("cluster87 mirror87 filter87 ranking87 encoding87 mapping87", 28),
        ["cluster87 mirror87 filter87", "ranking87 encoding87", "mapping87"],
    ),
    (
        ("mirror87 filter87 ranking87 encoding87 mapping87 record87", 6),
        ["mirror87", "filter87", "ranking87", "encoding87", "mapping87", "record87"],
    ),
    (
        ("mirror87 filter87 ranking87 encoding87 mapping87 record87", 10),
        ["mirror87", "filter87", "ranking87", "encoding87", "mapping87", "record87"],
    ),
    (
        ("mirror87 filter87 ranking87 encoding87 mapping87 record87", 18),
        ["mirror87 filter87", "ranking87", "encoding87", "mapping87 record87"],
    ),
    (
        ("mirror87 filter87 ranking87 encoding87 mapping87 record87", 28),
        ["mirror87 filter87 ranking87", "encoding87 mapping87", "record87"],
    ),
    (
        ("filter87 ranking87 encoding87 mapping87 record87 candle87", 6),
        ["filter87", "ranking87", "encoding87", "mapping87", "record87", "candle87"],
    ),
    (
        ("filter87 ranking87 encoding87 mapping87 record87 candle87", 10),
        ["filter87", "ranking87", "encoding87", "mapping87", "record87", "candle87"],
    ),
    (
        ("filter87 ranking87 encoding87 mapping87 record87 candle87", 18),
        ["filter87 ranking87", "encoding87", "mapping87 record87", "candle87"],
    ),
    (
        ("filter87 ranking87 encoding87 mapping87 record87 candle87", 28),
        ["filter87 ranking87", "encoding87 mapping87", "record87 candle87"],
    ),
    (
        ("ranking87 encoding87 mapping87 record87 candle87 thread87", 6),
        ["ranking87", "encoding87", "mapping87", "record87", "candle87", "thread87"],
    ),
    (
        ("ranking87 encoding87 mapping87 record87 candle87 thread87", 10),
        ["ranking87", "encoding87", "mapping87", "record87", "candle87", "thread87"],
    ),
    (
        ("ranking87 encoding87 mapping87 record87 candle87 thread87", 18),
        ["ranking87", "encoding87", "mapping87 record87", "candle87 thread87"],
    ),
    (
        ("ranking87 encoding87 mapping87 record87 candle87 thread87", 28),
        ["ranking87 encoding87", "mapping87 record87 candle87", "thread87"],
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
