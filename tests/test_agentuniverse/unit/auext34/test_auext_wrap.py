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
        ("round 34: the quick brown fox jumps over the lazy dog", 4),
        ["round", "34:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 34: the quick brown fox jumps over the lazy dog", 8),
        ["round", "34: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 34: the quick brown fox jumps over the lazy dog", 12),
        ["round 34:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 34: the quick brown fox jumps over the lazy dog", 16),
        ["round 34: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 34: the quick brown fox jumps over the lazy dog", 24),
        ["round 34: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 34: the quick brown fox jumps over the lazy dog", 32),
        ["round 34: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 34: agentuniverse is a framework for multi agents", 4),
        ["round", "34:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 34: agentuniverse is a framework for multi agents", 8),
        ["round", "34:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 34: agentuniverse is a framework for multi agents", 12),
        ["round 34:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 34: agentuniverse is a framework for multi agents", 16),
        ["round 34:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 34: agentuniverse is a framework for multi agents", 24),
        ["round 34: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 34: agentuniverse is a framework for multi agents", 32),
        ["round 34: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 34: knowledge stored as vectors enables retrieval", 4),
        ["round", "34:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 34: knowledge stored as vectors enables retrieval", 8),
        ["round", "34:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 34: knowledge stored as vectors enables retrieval", 12),
        ["round 34:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 34: knowledge stored as vectors enables retrieval", 16),
        ["round 34:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 34: knowledge stored as vectors enables retrieval", 24),
        ["round 34: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 34: knowledge stored as vectors enables retrieval", 32),
        ["round 34: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 34: the processor reads the record then stops", 4),
        ["round", "34:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 34: the processor reads the record then stops", 8),
        ["round", "34: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 34: the processor reads the record then stops", 12),
        ["round 34:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 34: the processor reads the record then stops", 16),
        ["round 34: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 34: the processor reads the record then stops", 24),
        ["round 34: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 34: the processor reads the record then stops", 32),
        ["round 34: the processor reads", "the record then stops"],
    ),
    (
        ("round 34: a worker pulls the next task from the queue", 4),
        ["round", "34:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 34: a worker pulls the next task from the queue", 8),
        ["round", "34: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 34: a worker pulls the next task from the queue", 12),
        ["round 34: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 34: a worker pulls the next task from the queue", 16),
        ["round 34: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 34: a worker pulls the next task from the queue", 24),
        ["round 34: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 34: a worker pulls the next task from the queue", 32),
        ["round 34: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 34: signals travel through the network layer", 4),
        ["round", "34:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 34: signals travel through the network layer", 8),
        ["round", "34:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 34: signals travel through the network layer", 12),
        ["round 34:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 34: signals travel through the network layer", 16),
        ["round 34:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 34: signals travel through the network layer", 24),
        ["round 34: signals travel", "through the network", "layer"],
    ),
    (
        ("round 34: signals travel through the network layer", 32),
        ["round 34: signals travel through", "the network layer"],
    ),
    (
        ("round 34: the gateway routes each request by policy", 4),
        ["round", "34:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 34: the gateway routes each request by policy", 8),
        ["round", "34: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 34: the gateway routes each request by policy", 12),
        ["round 34:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 34: the gateway routes each request by policy", 16),
        ["round 34: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 34: the gateway routes each request by policy", 24),
        ["round 34: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 34: the gateway routes each request by policy", 32),
        ["round 34: the gateway routes", "each request by policy"],
    ),
    (
        ("round 34: memory grows until the buffer is full", 4),
        ["round", "34:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 34: memory grows until the buffer is full", 8),
        ["round", "34:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 34: memory grows until the buffer is full", 12),
        ["round 34:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 34: memory grows until the buffer is full", 16),
        ["round 34: memory", "grows until the", "buffer is full"],
    ),
    (("round 34: memory grows until the buffer is full", 24), ["round 34: memory grows", "until the buffer is full"]),
    (("round 34: memory grows until the buffer is full", 32), ["round 34: memory grows until the", "buffer is full"]),
    (
        ("round 34: the cluster mirrors every packet twice", 4),
        ["round", "34:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 34: the cluster mirrors every packet twice", 8),
        ["round", "34: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 34: the cluster mirrors every packet twice", 12),
        ["round 34:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 34: the cluster mirrors every packet twice", 16),
        ["round 34: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 34: the cluster mirrors every packet twice", 24),
        ["round 34: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 34: the cluster mirrors every packet twice", 32), ["round 34: the cluster mirrors", "every packet twice"]),
    (
        ("round 34: ranking uses tokens learned from the corpus", 4),
        ["round", "34:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 34: ranking uses tokens learned from the corpus", 8),
        ["round", "34:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 34: ranking uses tokens learned from the corpus", 12),
        ["round 34:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 34: ranking uses tokens learned from the corpus", 16),
        ["round 34:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 34: ranking uses tokens learned from the corpus", 24),
        ["round 34: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 34: ranking uses tokens learned from the corpus", 32),
        ["round 34: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 34: a long session ends when the candle dies", 4),
        ["round", "34:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 34: a long session ends when the candle dies", 8),
        ["round", "34: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 34: a long session ends when the candle dies", 12),
        ["round 34: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 34: a long session ends when the candle dies", 16),
        ["round 34: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 34: a long session ends when the candle dies", 24),
        ["round 34: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 34: a long session ends when the candle dies", 32),
        ["round 34: a long session ends", "when the candle dies"],
    ),
    (
        ("round 34: encode the prompt then map the result", 4),
        ["round", "34:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 34: encode the prompt then map the result", 8),
        ["round", "34:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 34: encode the prompt then map the result", 12),
        ["round 34:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 34: encode the prompt then map the result", 16),
        ["round 34: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 34: encode the prompt then map the result", 24),
        ["round 34: encode the", "prompt then map the", "result"],
    ),
    (("round 34: encode the prompt then map the result", 32), ["round 34: encode the prompt then", "map the result"]),
    (
        ("round 34: the kernel wakes the worker at dawn", 4),
        ["round", "34:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 34: the kernel wakes the worker at dawn", 8),
        ["round", "34: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 34: the kernel wakes the worker at dawn", 12),
        ["round 34:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 34: the kernel wakes the worker at dawn", 16), ["round 34: the", "kernel wakes the", "worker at dawn"]),
    (("round 34: the kernel wakes the worker at dawn", 24), ["round 34: the kernel", "wakes the worker at dawn"]),
    (("round 34: the kernel wakes the worker at dawn", 32), ["round 34: the kernel wakes the", "worker at dawn"]),
    (
        ("round 34: service latency drops after the patch", 4),
        ["round", "34:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 34: service latency drops after the patch", 8),
        ["round", "34:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 34: service latency drops after the patch", 12),
        ["round 34:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 34: service latency drops after the patch", 16),
        ["round 34:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 34: service latency drops after the patch", 24),
        ["round 34: service", "latency drops after the", "patch"],
    ),
    (("round 34: service latency drops after the patch", 32), ["round 34: service latency drops", "after the patch"]),
    (
        ("round 34: the library caches every vector it sees", 4),
        ["round", "34:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 34: the library caches every vector it sees", 8),
        ["round", "34: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 34: the library caches every vector it sees", 12),
        ["round 34:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 34: the library caches every vector it sees", 16),
        ["round 34: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 34: the library caches every vector it sees", 24),
        ["round 34: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 34: the library caches every vector it sees", 32),
        ["round 34: the library caches", "every vector it sees"],
    ),
    (
        ("round 34: agents argue then the debate resolves", 4),
        ["round", "34:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 34: agents argue then the debate resolves", 8),
        ["round", "34:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 34: agents argue then the debate resolves", 12),
        ["round 34:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 34: agents argue then the debate resolves", 16),
        ["round 34: agents", "argue then the", "debate resolves"],
    ),
    (("round 34: agents argue then the debate resolves", 24), ["round 34: agents argue", "then the debate resolves"]),
    (("round 34: agents argue then the debate resolves", 32), ["round 34: agents argue then the", "debate resolves"]),
    (
        ("round 34: the filter keeps only strong matches", 4),
        ["round", "34:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 34: the filter keeps only strong matches", 8),
        ["round", "34: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 34: the filter keeps only strong matches", 12),
        ["round 34:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 34: the filter keeps only strong matches", 16),
        ["round 34: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 34: the filter keeps only strong matches", 24), ["round 34: the filter", "keeps only strong", "matches"]),
    (("round 34: the filter keeps only strong matches", 32), ["round 34: the filter keeps only", "strong matches"]),
    (
        ("round 34: the model answers with a short reply", 4),
        ["round", "34:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 34: the model answers with a short reply", 8),
        ["round", "34: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 34: the model answers with a short reply", 12),
        ["round 34:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 34: the model answers with a short reply", 16),
        ["round 34: the", "model answers", "with a short", "reply"],
    ),
    (("round 34: the model answers with a short reply", 24), ["round 34: the model", "answers with a short", "reply"]),
    (("round 34: the model answers with a short reply", 32), ["round 34: the model answers with", "a short reply"]),
    (
        ("round 34: the recorder stores the reasoning trace", 4),
        ["round", "34:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 34: the recorder stores the reasoning trace", 8),
        ["round", "34: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 34: the recorder stores the reasoning trace", 12),
        ["round 34:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 34: the recorder stores the reasoning trace", 16),
        ["round 34: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 34: the recorder stores the reasoning trace", 24),
        ["round 34: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 34: the recorder stores the reasoning trace", 32),
        ["round 34: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 34: the angel watches the processor run", 4),
        ["round", "34:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 34: the angel watches the processor run", 8),
        ["round", "34: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 34: the angel watches the processor run", 12),
        ["round 34:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 34: the angel watches the processor run", 16), ["round 34: the", "angel watches", "the processor", "run"]),
    (("round 34: the angel watches the processor run", 24), ["round 34: the angel", "watches the processor", "run"]),
    (("round 34: the angel watches the processor run", 32), ["round 34: the angel watches the", "processor run"]),
    (
        ("round 34: angle of the vector decides the match", 4),
        ["round", "34:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 34: angle of the vector decides the match", 8),
        ["round", "34:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 34: angle of the vector decides the match", 12),
        ["round 34:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 34: angle of the vector decides the match", 16),
        ["round 34: angle", "of the vector", "decides the", "match"],
    ),
    (("round 34: angle of the vector decides the match", 24), ["round 34: angle of the", "vector decides the match"]),
    (("round 34: angle of the vector decides the match", 32), ["round 34: angle of the vector", "decides the match"]),
    (
        ("round 34: the candle burns twice as long at night", 4),
        ["round", "34:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 34: the candle burns twice as long at night", 8),
        ["round", "34: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 34: the candle burns twice as long at night", 12),
        ["round 34:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 34: the candle burns twice as long at night", 16),
        ["round 34: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 34: the candle burns twice as long at night", 24),
        ["round 34: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 34: the candle burns twice as long at night", 32),
        ["round 34: the candle burns twice", "as long at night"],
    ),
    (
        ("round 34: a mirror of the universe in one line", 4),
        ["round", "34:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 34: a mirror of the universe in one line", 8),
        ["round", "34: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 34: a mirror of the universe in one line", 12),
        ["round 34: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 34: a mirror of the universe in one line", 16),
        ["round 34: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 34: a mirror of the universe in one line", 24), ["round 34: a mirror of", "the universe in one line"]),
    (("round 34: a mirror of the universe in one line", 32), ["round 34: a mirror of the", "universe in one line"]),
    (
        ("round 34: the queue drains before the storm", 4),
        ["round", "34:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 34: the queue drains before the storm", 8),
        ["round", "34: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 34: the queue drains before the storm", 12), ["round 34:", "the queue", "drains", "before the", "storm"]),
    (("round 34: the queue drains before the storm", 16), ["round 34: the", "queue drains", "before the storm"]),
    (("round 34: the queue drains before the storm", 24), ["round 34: the queue", "drains before the storm"]),
    (("round 34: the queue drains before the storm", 32), ["round 34: the queue drains", "before the storm"]),
    (
        ("kitten34 sitting34 agent34 angle34 universe34 memory34", 6),
        ["kitten34", "sitting34", "agent34", "angle34", "universe34", "memory34"],
    ),
    (
        ("kitten34 sitting34 agent34 angle34 universe34 memory34", 10),
        ["kitten34", "sitting34", "agent34", "angle34", "universe34", "memory34"],
    ),
    (
        ("kitten34 sitting34 agent34 angle34 universe34 memory34", 18),
        ["kitten34 sitting34", "agent34 angle34", "universe34", "memory34"],
    ),
    (
        ("kitten34 sitting34 agent34 angle34 universe34 memory34", 28),
        ["kitten34 sitting34 agent34", "angle34 universe34 memory34"],
    ),
    (
        ("sitting34 agent34 angle34 universe34 memory34 stream34", 6),
        ["sitting34", "agent34", "angle34", "universe34", "memory34", "stream34"],
    ),
    (
        ("sitting34 agent34 angle34 universe34 memory34 stream34", 10),
        ["sitting34", "agent34", "angle34", "universe34", "memory34", "stream34"],
    ),
    (
        ("sitting34 agent34 angle34 universe34 memory34 stream34", 18),
        ["sitting34 agent34", "angle34 universe34", "memory34 stream34"],
    ),
    (
        ("sitting34 agent34 angle34 universe34 memory34 stream34", 28),
        ["sitting34 agent34 angle34", "universe34 memory34 stream34"],
    ),
    (
        ("agent34 angle34 universe34 memory34 stream34 context34", 6),
        ["agent34", "angle34", "universe34", "memory34", "stream34", "context34"],
    ),
    (
        ("agent34 angle34 universe34 memory34 stream34 context34", 10),
        ["agent34", "angle34", "universe34", "memory34", "stream34", "context34"],
    ),
    (
        ("agent34 angle34 universe34 memory34 stream34 context34", 18),
        ["agent34 angle34", "universe34", "memory34 stream34", "context34"],
    ),
    (
        ("agent34 angle34 universe34 memory34 stream34 context34", 28),
        ["agent34 angle34 universe34", "memory34 stream34 context34"],
    ),
    (
        ("angle34 universe34 memory34 stream34 context34 knowledge34", 6),
        ["angle34", "universe34", "memory34", "stream34", "context34", "knowledge34"],
    ),
    (
        ("angle34 universe34 memory34 stream34 context34 knowledge34", 10),
        ["angle34", "universe34", "memory34", "stream34", "context34", "knowledge34"],
    ),
    (
        ("angle34 universe34 memory34 stream34 context34 knowledge34", 18),
        ["angle34 universe34", "memory34 stream34", "context34", "knowledge34"],
    ),
    (
        ("angle34 universe34 memory34 stream34 context34 knowledge34", 28),
        ["angle34 universe34 memory34", "stream34 context34", "knowledge34"],
    ),
    (
        ("universe34 memory34 stream34 context34 knowledge34 vector34", 6),
        ["universe34", "memory34", "stream34", "context34", "knowledge34", "vector34"],
    ),
    (
        ("universe34 memory34 stream34 context34 knowledge34 vector34", 10),
        ["universe34", "memory34", "stream34", "context34", "knowledge34", "vector34"],
    ),
    (
        ("universe34 memory34 stream34 context34 knowledge34 vector34", 18),
        ["universe34", "memory34 stream34", "context34", "knowledge34", "vector34"],
    ),
    (
        ("universe34 memory34 stream34 context34 knowledge34 vector34", 28),
        ["universe34 memory34 stream34", "context34 knowledge34", "vector34"],
    ),
    (
        ("memory34 stream34 context34 knowledge34 vector34 processor34", 6),
        ["memory34", "stream34", "context34", "knowledge34", "vector34", "processor34"],
    ),
    (
        ("memory34 stream34 context34 knowledge34 vector34 processor34", 10),
        ["memory34", "stream34", "context34", "knowledge34", "vector34", "processor34"],
    ),
    (
        ("memory34 stream34 context34 knowledge34 vector34 processor34", 18),
        ["memory34 stream34", "context34", "knowledge34", "vector34", "processor34"],
    ),
    (
        ("memory34 stream34 context34 knowledge34 vector34 processor34", 28),
        ["memory34 stream34 context34", "knowledge34 vector34", "processor34"],
    ),
    (
        ("stream34 context34 knowledge34 vector34 processor34 reasoning34", 6),
        ["stream34", "context34", "knowledge34", "vector34", "processor34", "reasoning34"],
    ),
    (
        ("stream34 context34 knowledge34 vector34 processor34 reasoning34", 10),
        ["stream34", "context34", "knowledge34", "vector34", "processor34", "reasoning34"],
    ),
    (
        ("stream34 context34 knowledge34 vector34 processor34 reasoning34", 18),
        ["stream34 context34", "knowledge34", "vector34", "processor34", "reasoning34"],
    ),
    (
        ("stream34 context34 knowledge34 vector34 processor34 reasoning34", 28),
        ["stream34 context34", "knowledge34 vector34", "processor34 reasoning34"],
    ),
    (
        ("context34 knowledge34 vector34 processor34 reasoning34 machine34", 6),
        ["context34", "knowledge34", "vector34", "processor34", "reasoning34", "machine34"],
    ),
    (
        ("context34 knowledge34 vector34 processor34 reasoning34 machine34", 10),
        ["context34", "knowledge34", "vector34", "processor34", "reasoning34", "machine34"],
    ),
    (
        ("context34 knowledge34 vector34 processor34 reasoning34 machine34", 18),
        ["context34", "knowledge34", "vector34", "processor34", "reasoning34", "machine34"],
    ),
    (
        ("context34 knowledge34 vector34 processor34 reasoning34 machine34", 28),
        ["context34 knowledge34", "vector34 processor34", "reasoning34 machine34"],
    ),
    (
        ("knowledge34 vector34 processor34 reasoning34 machine34 learning34", 6),
        ["knowledge34", "vector34", "processor34", "reasoning34", "machine34", "learning34"],
    ),
    (
        ("knowledge34 vector34 processor34 reasoning34 machine34 learning34", 10),
        ["knowledge34", "vector34", "processor34", "reasoning34", "machine34", "learning34"],
    ),
    (
        ("knowledge34 vector34 processor34 reasoning34 machine34 learning34", 18),
        ["knowledge34", "vector34", "processor34", "reasoning34", "machine34", "learning34"],
    ),
    (
        ("knowledge34 vector34 processor34 reasoning34 machine34 learning34", 28),
        ["knowledge34 vector34", "processor34 reasoning34", "machine34 learning34"],
    ),
    (
        ("vector34 processor34 reasoning34 machine34 learning34 model34", 6),
        ["vector34", "processor34", "reasoning34", "machine34", "learning34", "model34"],
    ),
    (
        ("vector34 processor34 reasoning34 machine34 learning34 model34", 10),
        ["vector34", "processor34", "reasoning34", "machine34", "learning34", "model34"],
    ),
    (
        ("vector34 processor34 reasoning34 machine34 learning34 model34", 18),
        ["vector34", "processor34", "reasoning34", "machine34", "learning34 model34"],
    ),
    (
        ("vector34 processor34 reasoning34 machine34 learning34 model34", 28),
        ["vector34 processor34", "reasoning34 machine34", "learning34 model34"],
    ),
    (
        ("processor34 reasoning34 machine34 learning34 model34 token34", 6),
        ["processor34", "reasoning34", "machine34", "learning34", "model34", "token34"],
    ),
    (
        ("processor34 reasoning34 machine34 learning34 model34 token34", 10),
        ["processor34", "reasoning34", "machine34", "learning34", "model34", "token34"],
    ),
    (
        ("processor34 reasoning34 machine34 learning34 model34 token34", 18),
        ["processor34", "reasoning34", "machine34", "learning34 model34", "token34"],
    ),
    (
        ("processor34 reasoning34 machine34 learning34 model34 token34", 28),
        ["processor34 reasoning34", "machine34 learning34 model34", "token34"],
    ),
    (
        ("reasoning34 machine34 learning34 model34 token34 prompt34", 6),
        ["reasoning34", "machine34", "learning34", "model34", "token34", "prompt34"],
    ),
    (
        ("reasoning34 machine34 learning34 model34 token34 prompt34", 10),
        ["reasoning34", "machine34", "learning34", "model34", "token34", "prompt34"],
    ),
    (
        ("reasoning34 machine34 learning34 model34 token34 prompt34", 18),
        ["reasoning34", "machine34", "learning34 model34", "token34 prompt34"],
    ),
    (
        ("reasoning34 machine34 learning34 model34 token34 prompt34", 28),
        ["reasoning34 machine34", "learning34 model34 token34", "prompt34"],
    ),
    (
        ("machine34 learning34 model34 token34 prompt34 session34", 6),
        ["machine34", "learning34", "model34", "token34", "prompt34", "session34"],
    ),
    (
        ("machine34 learning34 model34 token34 prompt34 session34", 10),
        ["machine34", "learning34", "model34", "token34", "prompt34", "session34"],
    ),
    (
        ("machine34 learning34 model34 token34 prompt34 session34", 18),
        ["machine34", "learning34 model34", "token34 prompt34", "session34"],
    ),
    (
        ("machine34 learning34 model34 token34 prompt34 session34", 28),
        ["machine34 learning34 model34", "token34 prompt34 session34"],
    ),
    (
        ("learning34 model34 token34 prompt34 session34 library34", 6),
        ["learning34", "model34", "token34", "prompt34", "session34", "library34"],
    ),
    (
        ("learning34 model34 token34 prompt34 session34 library34", 10),
        ["learning34", "model34", "token34", "prompt34", "session34", "library34"],
    ),
    (
        ("learning34 model34 token34 prompt34 session34 library34", 18),
        ["learning34 model34", "token34 prompt34", "session34", "library34"],
    ),
    (
        ("learning34 model34 token34 prompt34 session34 library34", 28),
        ["learning34 model34 token34", "prompt34 session34 library34"],
    ),
    (
        ("model34 token34 prompt34 session34 library34 service34", 6),
        ["model34", "token34", "prompt34", "session34", "library34", "service34"],
    ),
    (
        ("model34 token34 prompt34 session34 library34 service34", 10),
        ["model34", "token34", "prompt34", "session34", "library34", "service34"],
    ),
    (
        ("model34 token34 prompt34 session34 library34 service34", 18),
        ["model34 token34", "prompt34 session34", "library34", "service34"],
    ),
    (
        ("model34 token34 prompt34 session34 library34 service34", 28),
        ["model34 token34 prompt34", "session34 library34", "service34"],
    ),
    (
        ("token34 prompt34 session34 library34 service34 gateway34", 6),
        ["token34", "prompt34", "session34", "library34", "service34", "gateway34"],
    ),
    (
        ("token34 prompt34 session34 library34 service34 gateway34", 10),
        ["token34", "prompt34", "session34", "library34", "service34", "gateway34"],
    ),
    (
        ("token34 prompt34 session34 library34 service34 gateway34", 18),
        ["token34 prompt34", "session34", "library34", "service34", "gateway34"],
    ),
    (
        ("token34 prompt34 session34 library34 service34 gateway34", 28),
        ["token34 prompt34 session34", "library34 service34", "gateway34"],
    ),
    (
        ("prompt34 session34 library34 service34 gateway34 storage34", 6),
        ["prompt34", "session34", "library34", "service34", "gateway34", "storage34"],
    ),
    (
        ("prompt34 session34 library34 service34 gateway34 storage34", 10),
        ["prompt34", "session34", "library34", "service34", "gateway34", "storage34"],
    ),
    (
        ("prompt34 session34 library34 service34 gateway34 storage34", 18),
        ["prompt34 session34", "library34", "service34", "gateway34", "storage34"],
    ),
    (
        ("prompt34 session34 library34 service34 gateway34 storage34", 28),
        ["prompt34 session34 library34", "service34 gateway34", "storage34"],
    ),
    (
        ("session34 library34 service34 gateway34 storage34 network34", 6),
        ["session34", "library34", "service34", "gateway34", "storage34", "network34"],
    ),
    (
        ("session34 library34 service34 gateway34 storage34 network34", 10),
        ["session34", "library34", "service34", "gateway34", "storage34", "network34"],
    ),
    (
        ("session34 library34 service34 gateway34 storage34 network34", 18),
        ["session34", "library34", "service34", "gateway34", "storage34", "network34"],
    ),
    (
        ("session34 library34 service34 gateway34 storage34 network34", 28),
        ["session34 library34", "service34 gateway34", "storage34 network34"],
    ),
    (
        ("library34 service34 gateway34 storage34 network34 latency34", 6),
        ["library34", "service34", "gateway34", "storage34", "network34", "latency34"],
    ),
    (
        ("library34 service34 gateway34 storage34 network34 latency34", 10),
        ["library34", "service34", "gateway34", "storage34", "network34", "latency34"],
    ),
    (
        ("library34 service34 gateway34 storage34 network34 latency34", 18),
        ["library34", "service34", "gateway34", "storage34", "network34", "latency34"],
    ),
    (
        ("library34 service34 gateway34 storage34 network34 latency34", 28),
        ["library34 service34", "gateway34 storage34", "network34 latency34"],
    ),
    (
        ("service34 gateway34 storage34 network34 latency34 buffer34", 6),
        ["service34", "gateway34", "storage34", "network34", "latency34", "buffer34"],
    ),
    (
        ("service34 gateway34 storage34 network34 latency34 buffer34", 10),
        ["service34", "gateway34", "storage34", "network34", "latency34", "buffer34"],
    ),
    (
        ("service34 gateway34 storage34 network34 latency34 buffer34", 18),
        ["service34", "gateway34", "storage34", "network34", "latency34 buffer34"],
    ),
    (
        ("service34 gateway34 storage34 network34 latency34 buffer34", 28),
        ["service34 gateway34", "storage34 network34", "latency34 buffer34"],
    ),
    (
        ("gateway34 storage34 network34 latency34 buffer34 queue34", 6),
        ["gateway34", "storage34", "network34", "latency34", "buffer34", "queue34"],
    ),
    (
        ("gateway34 storage34 network34 latency34 buffer34 queue34", 10),
        ["gateway34", "storage34", "network34", "latency34", "buffer34", "queue34"],
    ),
    (
        ("gateway34 storage34 network34 latency34 buffer34 queue34", 18),
        ["gateway34", "storage34", "network34", "latency34 buffer34", "queue34"],
    ),
    (
        ("gateway34 storage34 network34 latency34 buffer34 queue34", 28),
        ["gateway34 storage34", "network34 latency34 buffer34", "queue34"],
    ),
    (
        ("storage34 network34 latency34 buffer34 queue34 worker34", 6),
        ["storage34", "network34", "latency34", "buffer34", "queue34", "worker34"],
    ),
    (
        ("storage34 network34 latency34 buffer34 queue34 worker34", 10),
        ["storage34", "network34", "latency34", "buffer34", "queue34", "worker34"],
    ),
    (
        ("storage34 network34 latency34 buffer34 queue34 worker34", 18),
        ["storage34", "network34", "latency34 buffer34", "queue34 worker34"],
    ),
    (
        ("storage34 network34 latency34 buffer34 queue34 worker34", 28),
        ["storage34 network34", "latency34 buffer34 queue34", "worker34"],
    ),
    (
        ("network34 latency34 buffer34 queue34 worker34 kernel34", 6),
        ["network34", "latency34", "buffer34", "queue34", "worker34", "kernel34"],
    ),
    (
        ("network34 latency34 buffer34 queue34 worker34 kernel34", 10),
        ["network34", "latency34", "buffer34", "queue34", "worker34", "kernel34"],
    ),
    (
        ("network34 latency34 buffer34 queue34 worker34 kernel34", 18),
        ["network34", "latency34 buffer34", "queue34 worker34", "kernel34"],
    ),
    (
        ("network34 latency34 buffer34 queue34 worker34 kernel34", 28),
        ["network34 latency34 buffer34", "queue34 worker34 kernel34"],
    ),
    (
        ("latency34 buffer34 queue34 worker34 kernel34 signal34", 6),
        ["latency34", "buffer34", "queue34", "worker34", "kernel34", "signal34"],
    ),
    (
        ("latency34 buffer34 queue34 worker34 kernel34 signal34", 10),
        ["latency34", "buffer34", "queue34", "worker34", "kernel34", "signal34"],
    ),
    (
        ("latency34 buffer34 queue34 worker34 kernel34 signal34", 18),
        ["latency34 buffer34", "queue34 worker34", "kernel34 signal34"],
    ),
    (
        ("latency34 buffer34 queue34 worker34 kernel34 signal34", 28),
        ["latency34 buffer34 queue34", "worker34 kernel34 signal34"],
    ),
    (
        ("buffer34 queue34 worker34 kernel34 signal34 packet34", 6),
        ["buffer34", "queue34", "worker34", "kernel34", "signal34", "packet34"],
    ),
    (
        ("buffer34 queue34 worker34 kernel34 signal34 packet34", 10),
        ["buffer34", "queue34", "worker34", "kernel34", "signal34", "packet34"],
    ),
    (
        ("buffer34 queue34 worker34 kernel34 signal34 packet34", 18),
        ["buffer34 queue34", "worker34 kernel34", "signal34 packet34"],
    ),
    (
        ("buffer34 queue34 worker34 kernel34 signal34 packet34", 28),
        ["buffer34 queue34 worker34", "kernel34 signal34 packet34"],
    ),
    (
        ("queue34 worker34 kernel34 signal34 packet34 router34", 6),
        ["queue34", "worker34", "kernel34", "signal34", "packet34", "router34"],
    ),
    (
        ("queue34 worker34 kernel34 signal34 packet34 router34", 10),
        ["queue34", "worker34", "kernel34", "signal34", "packet34", "router34"],
    ),
    (
        ("queue34 worker34 kernel34 signal34 packet34 router34", 18),
        ["queue34 worker34", "kernel34 signal34", "packet34 router34"],
    ),
    (
        ("queue34 worker34 kernel34 signal34 packet34 router34", 28),
        ["queue34 worker34 kernel34", "signal34 packet34 router34"],
    ),
    (
        ("worker34 kernel34 signal34 packet34 router34 cluster34", 6),
        ["worker34", "kernel34", "signal34", "packet34", "router34", "cluster34"],
    ),
    (
        ("worker34 kernel34 signal34 packet34 router34 cluster34", 10),
        ["worker34", "kernel34", "signal34", "packet34", "router34", "cluster34"],
    ),
    (
        ("worker34 kernel34 signal34 packet34 router34 cluster34", 18),
        ["worker34 kernel34", "signal34 packet34", "router34 cluster34"],
    ),
    (
        ("worker34 kernel34 signal34 packet34 router34 cluster34", 28),
        ["worker34 kernel34 signal34", "packet34 router34 cluster34"],
    ),
    (
        ("kernel34 signal34 packet34 router34 cluster34 mirror34", 6),
        ["kernel34", "signal34", "packet34", "router34", "cluster34", "mirror34"],
    ),
    (
        ("kernel34 signal34 packet34 router34 cluster34 mirror34", 10),
        ["kernel34", "signal34", "packet34", "router34", "cluster34", "mirror34"],
    ),
    (
        ("kernel34 signal34 packet34 router34 cluster34 mirror34", 18),
        ["kernel34 signal34", "packet34 router34", "cluster34 mirror34"],
    ),
    (
        ("kernel34 signal34 packet34 router34 cluster34 mirror34", 28),
        ["kernel34 signal34 packet34", "router34 cluster34 mirror34"],
    ),
    (
        ("signal34 packet34 router34 cluster34 mirror34 filter34", 6),
        ["signal34", "packet34", "router34", "cluster34", "mirror34", "filter34"],
    ),
    (
        ("signal34 packet34 router34 cluster34 mirror34 filter34", 10),
        ["signal34", "packet34", "router34", "cluster34", "mirror34", "filter34"],
    ),
    (
        ("signal34 packet34 router34 cluster34 mirror34 filter34", 18),
        ["signal34 packet34", "router34 cluster34", "mirror34 filter34"],
    ),
    (
        ("signal34 packet34 router34 cluster34 mirror34 filter34", 28),
        ["signal34 packet34 router34", "cluster34 mirror34 filter34"],
    ),
    (
        ("packet34 router34 cluster34 mirror34 filter34 ranking34", 6),
        ["packet34", "router34", "cluster34", "mirror34", "filter34", "ranking34"],
    ),
    (
        ("packet34 router34 cluster34 mirror34 filter34 ranking34", 10),
        ["packet34", "router34", "cluster34", "mirror34", "filter34", "ranking34"],
    ),
    (
        ("packet34 router34 cluster34 mirror34 filter34 ranking34", 18),
        ["packet34 router34", "cluster34 mirror34", "filter34 ranking34"],
    ),
    (
        ("packet34 router34 cluster34 mirror34 filter34 ranking34", 28),
        ["packet34 router34 cluster34", "mirror34 filter34 ranking34"],
    ),
    (
        ("router34 cluster34 mirror34 filter34 ranking34 encoding34", 6),
        ["router34", "cluster34", "mirror34", "filter34", "ranking34", "encoding34"],
    ),
    (
        ("router34 cluster34 mirror34 filter34 ranking34 encoding34", 10),
        ["router34", "cluster34", "mirror34", "filter34", "ranking34", "encoding34"],
    ),
    (
        ("router34 cluster34 mirror34 filter34 ranking34 encoding34", 18),
        ["router34 cluster34", "mirror34 filter34", "ranking34", "encoding34"],
    ),
    (
        ("router34 cluster34 mirror34 filter34 ranking34 encoding34", 28),
        ["router34 cluster34 mirror34", "filter34 ranking34", "encoding34"],
    ),
    (
        ("cluster34 mirror34 filter34 ranking34 encoding34 mapping34", 6),
        ["cluster34", "mirror34", "filter34", "ranking34", "encoding34", "mapping34"],
    ),
    (
        ("cluster34 mirror34 filter34 ranking34 encoding34 mapping34", 10),
        ["cluster34", "mirror34", "filter34", "ranking34", "encoding34", "mapping34"],
    ),
    (
        ("cluster34 mirror34 filter34 ranking34 encoding34 mapping34", 18),
        ["cluster34 mirror34", "filter34 ranking34", "encoding34", "mapping34"],
    ),
    (
        ("cluster34 mirror34 filter34 ranking34 encoding34 mapping34", 28),
        ["cluster34 mirror34 filter34", "ranking34 encoding34", "mapping34"],
    ),
    (
        ("mirror34 filter34 ranking34 encoding34 mapping34 record34", 6),
        ["mirror34", "filter34", "ranking34", "encoding34", "mapping34", "record34"],
    ),
    (
        ("mirror34 filter34 ranking34 encoding34 mapping34 record34", 10),
        ["mirror34", "filter34", "ranking34", "encoding34", "mapping34", "record34"],
    ),
    (
        ("mirror34 filter34 ranking34 encoding34 mapping34 record34", 18),
        ["mirror34 filter34", "ranking34", "encoding34", "mapping34 record34"],
    ),
    (
        ("mirror34 filter34 ranking34 encoding34 mapping34 record34", 28),
        ["mirror34 filter34 ranking34", "encoding34 mapping34", "record34"],
    ),
    (
        ("filter34 ranking34 encoding34 mapping34 record34 candle34", 6),
        ["filter34", "ranking34", "encoding34", "mapping34", "record34", "candle34"],
    ),
    (
        ("filter34 ranking34 encoding34 mapping34 record34 candle34", 10),
        ["filter34", "ranking34", "encoding34", "mapping34", "record34", "candle34"],
    ),
    (
        ("filter34 ranking34 encoding34 mapping34 record34 candle34", 18),
        ["filter34 ranking34", "encoding34", "mapping34 record34", "candle34"],
    ),
    (
        ("filter34 ranking34 encoding34 mapping34 record34 candle34", 28),
        ["filter34 ranking34", "encoding34 mapping34", "record34 candle34"],
    ),
    (
        ("ranking34 encoding34 mapping34 record34 candle34 thread34", 6),
        ["ranking34", "encoding34", "mapping34", "record34", "candle34", "thread34"],
    ),
    (
        ("ranking34 encoding34 mapping34 record34 candle34 thread34", 10),
        ["ranking34", "encoding34", "mapping34", "record34", "candle34", "thread34"],
    ),
    (
        ("ranking34 encoding34 mapping34 record34 candle34 thread34", 18),
        ["ranking34", "encoding34", "mapping34 record34", "candle34 thread34"],
    ),
    (
        ("ranking34 encoding34 mapping34 record34 candle34 thread34", 28),
        ["ranking34 encoding34", "mapping34 record34 candle34", "thread34"],
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
