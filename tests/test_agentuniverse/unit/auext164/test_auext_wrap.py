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
        ("round 164: the quick brown fox jumps over the lazy dog", 4),
        ["round", "164:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 164: the quick brown fox jumps over the lazy dog", 8),
        ["round", "164: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 164: the quick brown fox jumps over the lazy dog", 12),
        ["round 164:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 164: the quick brown fox jumps over the lazy dog", 16),
        ["round 164: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 164: the quick brown fox jumps over the lazy dog", 24),
        ["round 164: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 164: the quick brown fox jumps over the lazy dog", 32),
        ["round 164: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 164: agentuniverse is a framework for multi agents", 4),
        ["round", "164:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 164: agentuniverse is a framework for multi agents", 8),
        ["round", "164:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 164: agentuniverse is a framework for multi agents", 12),
        ["round 164:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 164: agentuniverse is a framework for multi agents", 16),
        ["round 164:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 164: agentuniverse is a framework for multi agents", 24),
        ["round 164: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 164: agentuniverse is a framework for multi agents", 32),
        ["round 164: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 164: knowledge stored as vectors enables retrieval", 4),
        ["round", "164:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 164: knowledge stored as vectors enables retrieval", 8),
        ["round", "164:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 164: knowledge stored as vectors enables retrieval", 12),
        ["round 164:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 164: knowledge stored as vectors enables retrieval", 16),
        ["round 164:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 164: knowledge stored as vectors enables retrieval", 24),
        ["round 164: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 164: knowledge stored as vectors enables retrieval", 32),
        ["round 164: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 164: the processor reads the record then stops", 4),
        ["round", "164:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 164: the processor reads the record then stops", 8),
        ["round", "164: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 164: the processor reads the record then stops", 12),
        ["round 164:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 164: the processor reads the record then stops", 16),
        ["round 164: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 164: the processor reads the record then stops", 24),
        ["round 164: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 164: the processor reads the record then stops", 32),
        ["round 164: the processor reads", "the record then stops"],
    ),
    (
        ("round 164: a worker pulls the next task from the queue", 4),
        ["round", "164:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 164: a worker pulls the next task from the queue", 8),
        ["round", "164: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 164: a worker pulls the next task from the queue", 12),
        ["round 164: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 164: a worker pulls the next task from the queue", 16),
        ["round 164: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 164: a worker pulls the next task from the queue", 24),
        ["round 164: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 164: a worker pulls the next task from the queue", 32),
        ["round 164: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 164: signals travel through the network layer", 4),
        ["round", "164:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 164: signals travel through the network layer", 8),
        ["round", "164:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 164: signals travel through the network layer", 12),
        ["round 164:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 164: signals travel through the network layer", 16),
        ["round 164:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 164: signals travel through the network layer", 24),
        ["round 164: signals", "travel through the", "network layer"],
    ),
    (
        ("round 164: signals travel through the network layer", 32),
        ["round 164: signals travel", "through the network layer"],
    ),
    (
        ("round 164: the gateway routes each request by policy", 4),
        ["round", "164:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 164: the gateway routes each request by policy", 8),
        ["round", "164: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 164: the gateway routes each request by policy", 12),
        ["round 164:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 164: the gateway routes each request by policy", 16),
        ["round 164: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 164: the gateway routes each request by policy", 24),
        ["round 164: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 164: the gateway routes each request by policy", 32),
        ["round 164: the gateway routes", "each request by policy"],
    ),
    (
        ("round 164: memory grows until the buffer is full", 4),
        ["round", "164:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 164: memory grows until the buffer is full", 8),
        ["round", "164:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 164: memory grows until the buffer is full", 12),
        ["round 164:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 164: memory grows until the buffer is full", 16),
        ["round 164:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 164: memory grows until the buffer is full", 24), ["round 164: memory grows", "until the buffer is full"]),
    (("round 164: memory grows until the buffer is full", 32), ["round 164: memory grows until", "the buffer is full"]),
    (
        ("round 164: the cluster mirrors every packet twice", 4),
        ["round", "164:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 164: the cluster mirrors every packet twice", 8),
        ["round", "164: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 164: the cluster mirrors every packet twice", 12),
        ["round 164:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 164: the cluster mirrors every packet twice", 16),
        ["round 164: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 164: the cluster mirrors every packet twice", 24),
        ["round 164: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 164: the cluster mirrors every packet twice", 32),
        ["round 164: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 164: ranking uses tokens learned from the corpus", 4),
        ["round", "164:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 164: ranking uses tokens learned from the corpus", 8),
        ["round", "164:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 164: ranking uses tokens learned from the corpus", 12),
        ["round 164:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 164: ranking uses tokens learned from the corpus", 16),
        ["round 164:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 164: ranking uses tokens learned from the corpus", 24),
        ["round 164: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 164: ranking uses tokens learned from the corpus", 32),
        ["round 164: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 164: a long session ends when the candle dies", 4),
        ["round", "164:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 164: a long session ends when the candle dies", 8),
        ["round", "164: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 164: a long session ends when the candle dies", 12),
        ["round 164: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 164: a long session ends when the candle dies", 16),
        ["round 164: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 164: a long session ends when the candle dies", 24),
        ["round 164: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 164: a long session ends when the candle dies", 32),
        ["round 164: a long session ends", "when the candle dies"],
    ),
    (
        ("round 164: encode the prompt then map the result", 4),
        ["round", "164:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 164: encode the prompt then map the result", 8),
        ["round", "164:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 164: encode the prompt then map the result", 12),
        ["round 164:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 164: encode the prompt then map the result", 16),
        ["round 164:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 164: encode the prompt then map the result", 24),
        ["round 164: encode the", "prompt then map the", "result"],
    ),
    (("round 164: encode the prompt then map the result", 32), ["round 164: encode the prompt", "then map the result"]),
    (
        ("round 164: the kernel wakes the worker at dawn", 4),
        ["round", "164:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 164: the kernel wakes the worker at dawn", 8),
        ["round", "164: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 164: the kernel wakes the worker at dawn", 12),
        ["round 164:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 164: the kernel wakes the worker at dawn", 16), ["round 164: the", "kernel wakes the", "worker at dawn"]),
    (("round 164: the kernel wakes the worker at dawn", 24), ["round 164: the kernel", "wakes the worker at dawn"]),
    (("round 164: the kernel wakes the worker at dawn", 32), ["round 164: the kernel wakes the", "worker at dawn"]),
    (
        ("round 164: service latency drops after the patch", 4),
        ["round", "164:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 164: service latency drops after the patch", 8),
        ["round", "164:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 164: service latency drops after the patch", 12),
        ["round 164:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 164: service latency drops after the patch", 16),
        ["round 164:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 164: service latency drops after the patch", 24),
        ["round 164: service", "latency drops after the", "patch"],
    ),
    (("round 164: service latency drops after the patch", 32), ["round 164: service latency drops", "after the patch"]),
    (
        ("round 164: the library caches every vector it sees", 4),
        ["round", "164:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 164: the library caches every vector it sees", 8),
        ["round", "164: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 164: the library caches every vector it sees", 12),
        ["round 164:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 164: the library caches every vector it sees", 16),
        ["round 164: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 164: the library caches every vector it sees", 24),
        ["round 164: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 164: the library caches every vector it sees", 32),
        ["round 164: the library caches", "every vector it sees"],
    ),
    (
        ("round 164: agents argue then the debate resolves", 4),
        ["round", "164:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 164: agents argue then the debate resolves", 8),
        ["round", "164:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 164: agents argue then the debate resolves", 12),
        ["round 164:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 164: agents argue then the debate resolves", 16),
        ["round 164:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 164: agents argue then the debate resolves", 24), ["round 164: agents argue", "then the debate resolves"]),
    (("round 164: agents argue then the debate resolves", 32), ["round 164: agents argue then the", "debate resolves"]),
    (
        ("round 164: the filter keeps only strong matches", 4),
        ["round", "164:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 164: the filter keeps only strong matches", 8),
        ["round", "164: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 164: the filter keeps only strong matches", 12),
        ["round 164:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 164: the filter keeps only strong matches", 16),
        ["round 164: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 164: the filter keeps only strong matches", 24),
        ["round 164: the filter", "keeps only strong", "matches"],
    ),
    (("round 164: the filter keeps only strong matches", 32), ["round 164: the filter keeps only", "strong matches"]),
    (
        ("round 164: the model answers with a short reply", 4),
        ["round", "164:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 164: the model answers with a short reply", 8),
        ["round", "164: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 164: the model answers with a short reply", 12),
        ["round 164:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 164: the model answers with a short reply", 16),
        ["round 164: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 164: the model answers with a short reply", 24),
        ["round 164: the model", "answers with a short", "reply"],
    ),
    (("round 164: the model answers with a short reply", 32), ["round 164: the model answers", "with a short reply"]),
    (
        ("round 164: the recorder stores the reasoning trace", 4),
        ["round", "164:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 164: the recorder stores the reasoning trace", 8),
        ["round", "164: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 164: the recorder stores the reasoning trace", 12),
        ["round 164:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 164: the recorder stores the reasoning trace", 16),
        ["round 164: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 164: the recorder stores the reasoning trace", 24),
        ["round 164: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 164: the recorder stores the reasoning trace", 32),
        ["round 164: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 164: the angel watches the processor run", 4),
        ["round", "164:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 164: the angel watches the processor run", 8),
        ["round", "164: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 164: the angel watches the processor run", 12),
        ["round 164:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 164: the angel watches the processor run", 16),
        ["round 164: the", "angel watches", "the processor", "run"],
    ),
    (("round 164: the angel watches the processor run", 24), ["round 164: the angel", "watches the processor", "run"]),
    (("round 164: the angel watches the processor run", 32), ["round 164: the angel watches the", "processor run"]),
    (
        ("round 164: angle of the vector decides the match", 4),
        ["round", "164:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 164: angle of the vector decides the match", 8),
        ["round", "164:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 164: angle of the vector decides the match", 12),
        ["round 164:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 164: angle of the vector decides the match", 16),
        ["round 164: angle", "of the vector", "decides the", "match"],
    ),
    (("round 164: angle of the vector decides the match", 24), ["round 164: angle of the", "vector decides the match"]),
    (("round 164: angle of the vector decides the match", 32), ["round 164: angle of the vector", "decides the match"]),
    (
        ("round 164: the candle burns twice as long at night", 4),
        ["round", "164:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 164: the candle burns twice as long at night", 8),
        ["round", "164: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 164: the candle burns twice as long at night", 12),
        ["round 164:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 164: the candle burns twice as long at night", 16),
        ["round 164: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 164: the candle burns twice as long at night", 24),
        ["round 164: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 164: the candle burns twice as long at night", 32),
        ["round 164: the candle burns", "twice as long at night"],
    ),
    (
        ("round 164: a mirror of the universe in one line", 4),
        ["round", "164:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 164: a mirror of the universe in one line", 8),
        ["round", "164: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 164: a mirror of the universe in one line", 12),
        ["round 164: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 164: a mirror of the universe in one line", 16),
        ["round 164: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 164: a mirror of the universe in one line", 24), ["round 164: a mirror of", "the universe in one line"]),
    (("round 164: a mirror of the universe in one line", 32), ["round 164: a mirror of the", "universe in one line"]),
    (
        ("round 164: the queue drains before the storm", 4),
        ["round", "164:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 164: the queue drains before the storm", 8),
        ["round", "164: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 164: the queue drains before the storm", 12),
        ["round 164:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 164: the queue drains before the storm", 16), ["round 164: the", "queue drains", "before the storm"]),
    (("round 164: the queue drains before the storm", 24), ["round 164: the queue", "drains before the storm"]),
    (("round 164: the queue drains before the storm", 32), ["round 164: the queue drains", "before the storm"]),
    (
        ("kitten164 sitting164 agent164 angle164 universe164 memory164", 6),
        ["kitten164", "sitting164", "agent164", "angle164", "universe164", "memory164"],
    ),
    (
        ("kitten164 sitting164 agent164 angle164 universe164 memory164", 10),
        ["kitten164", "sitting164", "agent164", "angle164", "universe164", "memory164"],
    ),
    (
        ("kitten164 sitting164 agent164 angle164 universe164 memory164", 18),
        ["kitten164", "sitting164", "agent164 angle164", "universe164", "memory164"],
    ),
    (
        ("kitten164 sitting164 agent164 angle164 universe164 memory164", 28),
        ["kitten164 sitting164", "agent164 angle164", "universe164 memory164"],
    ),
    (
        ("sitting164 agent164 angle164 universe164 memory164 stream164", 6),
        ["sitting164", "agent164", "angle164", "universe164", "memory164", "stream164"],
    ),
    (
        ("sitting164 agent164 angle164 universe164 memory164 stream164", 10),
        ["sitting164", "agent164", "angle164", "universe164", "memory164", "stream164"],
    ),
    (
        ("sitting164 agent164 angle164 universe164 memory164 stream164", 18),
        ["sitting164", "agent164 angle164", "universe164", "memory164", "stream164"],
    ),
    (
        ("sitting164 agent164 angle164 universe164 memory164 stream164", 28),
        ["sitting164 agent164 angle164", "universe164 memory164", "stream164"],
    ),
    (
        ("agent164 angle164 universe164 memory164 stream164 context164", 6),
        ["agent164", "angle164", "universe164", "memory164", "stream164", "context164"],
    ),
    (
        ("agent164 angle164 universe164 memory164 stream164 context164", 10),
        ["agent164", "angle164", "universe164", "memory164", "stream164", "context164"],
    ),
    (
        ("agent164 angle164 universe164 memory164 stream164 context164", 18),
        ["agent164 angle164", "universe164", "memory164", "stream164", "context164"],
    ),
    (
        ("agent164 angle164 universe164 memory164 stream164 context164", 28),
        ["agent164 angle164", "universe164 memory164", "stream164 context164"],
    ),
    (
        ("angle164 universe164 memory164 stream164 context164 knowledge164", 6),
        ["angle164", "universe164", "memory164", "stream164", "context164", "knowledge164"],
    ),
    (
        ("angle164 universe164 memory164 stream164 context164 knowledge164", 10),
        ["angle164", "universe164", "memory164", "stream164", "context164", "knowledge164"],
    ),
    (
        ("angle164 universe164 memory164 stream164 context164 knowledge164", 18),
        ["angle164", "universe164", "memory164", "stream164", "context164", "knowledge164"],
    ),
    (
        ("angle164 universe164 memory164 stream164 context164 knowledge164", 28),
        ["angle164 universe164", "memory164 stream164", "context164 knowledge164"],
    ),
    (
        ("universe164 memory164 stream164 context164 knowledge164 vector164", 6),
        ["universe164", "memory164", "stream164", "context164", "knowledge164", "vector164"],
    ),
    (
        ("universe164 memory164 stream164 context164 knowledge164 vector164", 10),
        ["universe164", "memory164", "stream164", "context164", "knowledge164", "vector164"],
    ),
    (
        ("universe164 memory164 stream164 context164 knowledge164 vector164", 18),
        ["universe164", "memory164", "stream164", "context164", "knowledge164", "vector164"],
    ),
    (
        ("universe164 memory164 stream164 context164 knowledge164 vector164", 28),
        ["universe164 memory164", "stream164 context164", "knowledge164 vector164"],
    ),
    (
        ("memory164 stream164 context164 knowledge164 vector164 processor164", 6),
        ["memory164", "stream164", "context164", "knowledge164", "vector164", "processor164"],
    ),
    (
        ("memory164 stream164 context164 knowledge164 vector164 processor164", 10),
        ["memory164", "stream164", "context164", "knowledge164", "vector164", "processor164"],
    ),
    (
        ("memory164 stream164 context164 knowledge164 vector164 processor164", 18),
        ["memory164", "stream164", "context164", "knowledge164", "vector164", "processor164"],
    ),
    (
        ("memory164 stream164 context164 knowledge164 vector164 processor164", 28),
        ["memory164 stream164", "context164 knowledge164", "vector164 processor164"],
    ),
    (
        ("stream164 context164 knowledge164 vector164 processor164 reasoning164", 6),
        ["stream164", "context164", "knowledge164", "vector164", "processor164", "reasoning164"],
    ),
    (
        ("stream164 context164 knowledge164 vector164 processor164 reasoning164", 10),
        ["stream164", "context164", "knowledge164", "vector164", "processor164", "reasoning164"],
    ),
    (
        ("stream164 context164 knowledge164 vector164 processor164 reasoning164", 18),
        ["stream164", "context164", "knowledge164", "vector164", "processor164", "reasoning164"],
    ),
    (
        ("stream164 context164 knowledge164 vector164 processor164 reasoning164", 28),
        ["stream164 context164", "knowledge164 vector164", "processor164 reasoning164"],
    ),
    (
        ("context164 knowledge164 vector164 processor164 reasoning164 machine164", 6),
        ["context164", "knowledge164", "vector164", "processor164", "reasoning164", "machine164"],
    ),
    (
        ("context164 knowledge164 vector164 processor164 reasoning164 machine164", 10),
        ["context164", "knowledge164", "vector164", "processor164", "reasoning164", "machine164"],
    ),
    (
        ("context164 knowledge164 vector164 processor164 reasoning164 machine164", 18),
        ["context164", "knowledge164", "vector164", "processor164", "reasoning164", "machine164"],
    ),
    (
        ("context164 knowledge164 vector164 processor164 reasoning164 machine164", 28),
        ["context164 knowledge164", "vector164 processor164", "reasoning164 machine164"],
    ),
    (
        ("knowledge164 vector164 processor164 reasoning164 machine164 learning164", 6),
        ["knowledge164", "vector164", "processor164", "reasoning164", "machine164", "learning164"],
    ),
    (
        ("knowledge164 vector164 processor164 reasoning164 machine164 learning164", 10),
        ["knowledge164", "vector164", "processor164", "reasoning164", "machine164", "learning164"],
    ),
    (
        ("knowledge164 vector164 processor164 reasoning164 machine164 learning164", 18),
        ["knowledge164", "vector164", "processor164", "reasoning164", "machine164", "learning164"],
    ),
    (
        ("knowledge164 vector164 processor164 reasoning164 machine164 learning164", 28),
        ["knowledge164 vector164", "processor164 reasoning164", "machine164 learning164"],
    ),
    (
        ("vector164 processor164 reasoning164 machine164 learning164 model164", 6),
        ["vector164", "processor164", "reasoning164", "machine164", "learning164", "model164"],
    ),
    (
        ("vector164 processor164 reasoning164 machine164 learning164 model164", 10),
        ["vector164", "processor164", "reasoning164", "machine164", "learning164", "model164"],
    ),
    (
        ("vector164 processor164 reasoning164 machine164 learning164 model164", 18),
        ["vector164", "processor164", "reasoning164", "machine164", "learning164", "model164"],
    ),
    (
        ("vector164 processor164 reasoning164 machine164 learning164 model164", 28),
        ["vector164 processor164", "reasoning164 machine164", "learning164 model164"],
    ),
    (
        ("processor164 reasoning164 machine164 learning164 model164 token164", 6),
        ["processor164", "reasoning164", "machine164", "learning164", "model164", "token164"],
    ),
    (
        ("processor164 reasoning164 machine164 learning164 model164 token164", 10),
        ["processor164", "reasoning164", "machine164", "learning164", "model164", "token164"],
    ),
    (
        ("processor164 reasoning164 machine164 learning164 model164 token164", 18),
        ["processor164", "reasoning164", "machine164", "learning164", "model164 token164"],
    ),
    (
        ("processor164 reasoning164 machine164 learning164 model164 token164", 28),
        ["processor164 reasoning164", "machine164 learning164", "model164 token164"],
    ),
    (
        ("reasoning164 machine164 learning164 model164 token164 prompt164", 6),
        ["reasoning164", "machine164", "learning164", "model164", "token164", "prompt164"],
    ),
    (
        ("reasoning164 machine164 learning164 model164 token164 prompt164", 10),
        ["reasoning164", "machine164", "learning164", "model164", "token164", "prompt164"],
    ),
    (
        ("reasoning164 machine164 learning164 model164 token164 prompt164", 18),
        ["reasoning164", "machine164", "learning164", "model164 token164", "prompt164"],
    ),
    (
        ("reasoning164 machine164 learning164 model164 token164 prompt164", 28),
        ["reasoning164 machine164", "learning164 model164", "token164 prompt164"],
    ),
    (
        ("machine164 learning164 model164 token164 prompt164 session164", 6),
        ["machine164", "learning164", "model164", "token164", "prompt164", "session164"],
    ),
    (
        ("machine164 learning164 model164 token164 prompt164 session164", 10),
        ["machine164", "learning164", "model164", "token164", "prompt164", "session164"],
    ),
    (
        ("machine164 learning164 model164 token164 prompt164 session164", 18),
        ["machine164", "learning164", "model164 token164", "prompt164", "session164"],
    ),
    (
        ("machine164 learning164 model164 token164 prompt164 session164", 28),
        ["machine164 learning164", "model164 token164 prompt164", "session164"],
    ),
    (
        ("learning164 model164 token164 prompt164 session164 library164", 6),
        ["learning164", "model164", "token164", "prompt164", "session164", "library164"],
    ),
    (
        ("learning164 model164 token164 prompt164 session164 library164", 10),
        ["learning164", "model164", "token164", "prompt164", "session164", "library164"],
    ),
    (
        ("learning164 model164 token164 prompt164 session164 library164", 18),
        ["learning164", "model164 token164", "prompt164", "session164", "library164"],
    ),
    (
        ("learning164 model164 token164 prompt164 session164 library164", 28),
        ["learning164 model164", "token164 prompt164", "session164 library164"],
    ),
    (
        ("model164 token164 prompt164 session164 library164 service164", 6),
        ["model164", "token164", "prompt164", "session164", "library164", "service164"],
    ),
    (
        ("model164 token164 prompt164 session164 library164 service164", 10),
        ["model164", "token164", "prompt164", "session164", "library164", "service164"],
    ),
    (
        ("model164 token164 prompt164 session164 library164 service164", 18),
        ["model164 token164", "prompt164", "session164", "library164", "service164"],
    ),
    (
        ("model164 token164 prompt164 session164 library164 service164", 28),
        ["model164 token164 prompt164", "session164 library164", "service164"],
    ),
    (
        ("token164 prompt164 session164 library164 service164 gateway164", 6),
        ["token164", "prompt164", "session164", "library164", "service164", "gateway164"],
    ),
    (
        ("token164 prompt164 session164 library164 service164 gateway164", 10),
        ["token164", "prompt164", "session164", "library164", "service164", "gateway164"],
    ),
    (
        ("token164 prompt164 session164 library164 service164 gateway164", 18),
        ["token164 prompt164", "session164", "library164", "service164", "gateway164"],
    ),
    (
        ("token164 prompt164 session164 library164 service164 gateway164", 28),
        ["token164 prompt164", "session164 library164", "service164 gateway164"],
    ),
    (
        ("prompt164 session164 library164 service164 gateway164 storage164", 6),
        ["prompt164", "session164", "library164", "service164", "gateway164", "storage164"],
    ),
    (
        ("prompt164 session164 library164 service164 gateway164 storage164", 10),
        ["prompt164", "session164", "library164", "service164", "gateway164", "storage164"],
    ),
    (
        ("prompt164 session164 library164 service164 gateway164 storage164", 18),
        ["prompt164", "session164", "library164", "service164", "gateway164", "storage164"],
    ),
    (
        ("prompt164 session164 library164 service164 gateway164 storage164", 28),
        ["prompt164 session164", "library164 service164", "gateway164 storage164"],
    ),
    (
        ("session164 library164 service164 gateway164 storage164 network164", 6),
        ["session164", "library164", "service164", "gateway164", "storage164", "network164"],
    ),
    (
        ("session164 library164 service164 gateway164 storage164 network164", 10),
        ["session164", "library164", "service164", "gateway164", "storage164", "network164"],
    ),
    (
        ("session164 library164 service164 gateway164 storage164 network164", 18),
        ["session164", "library164", "service164", "gateway164", "storage164", "network164"],
    ),
    (
        ("session164 library164 service164 gateway164 storage164 network164", 28),
        ["session164 library164", "service164 gateway164", "storage164 network164"],
    ),
    (
        ("library164 service164 gateway164 storage164 network164 latency164", 6),
        ["library164", "service164", "gateway164", "storage164", "network164", "latency164"],
    ),
    (
        ("library164 service164 gateway164 storage164 network164 latency164", 10),
        ["library164", "service164", "gateway164", "storage164", "network164", "latency164"],
    ),
    (
        ("library164 service164 gateway164 storage164 network164 latency164", 18),
        ["library164", "service164", "gateway164", "storage164", "network164", "latency164"],
    ),
    (
        ("library164 service164 gateway164 storage164 network164 latency164", 28),
        ["library164 service164", "gateway164 storage164", "network164 latency164"],
    ),
    (
        ("service164 gateway164 storage164 network164 latency164 buffer164", 6),
        ["service164", "gateway164", "storage164", "network164", "latency164", "buffer164"],
    ),
    (
        ("service164 gateway164 storage164 network164 latency164 buffer164", 10),
        ["service164", "gateway164", "storage164", "network164", "latency164", "buffer164"],
    ),
    (
        ("service164 gateway164 storage164 network164 latency164 buffer164", 18),
        ["service164", "gateway164", "storage164", "network164", "latency164", "buffer164"],
    ),
    (
        ("service164 gateway164 storage164 network164 latency164 buffer164", 28),
        ["service164 gateway164", "storage164 network164", "latency164 buffer164"],
    ),
    (
        ("gateway164 storage164 network164 latency164 buffer164 queue164", 6),
        ["gateway164", "storage164", "network164", "latency164", "buffer164", "queue164"],
    ),
    (
        ("gateway164 storage164 network164 latency164 buffer164 queue164", 10),
        ["gateway164", "storage164", "network164", "latency164", "buffer164", "queue164"],
    ),
    (
        ("gateway164 storage164 network164 latency164 buffer164 queue164", 18),
        ["gateway164", "storage164", "network164", "latency164", "buffer164 queue164"],
    ),
    (
        ("gateway164 storage164 network164 latency164 buffer164 queue164", 28),
        ["gateway164 storage164", "network164 latency164", "buffer164 queue164"],
    ),
    (
        ("storage164 network164 latency164 buffer164 queue164 worker164", 6),
        ["storage164", "network164", "latency164", "buffer164", "queue164", "worker164"],
    ),
    (
        ("storage164 network164 latency164 buffer164 queue164 worker164", 10),
        ["storage164", "network164", "latency164", "buffer164", "queue164", "worker164"],
    ),
    (
        ("storage164 network164 latency164 buffer164 queue164 worker164", 18),
        ["storage164", "network164", "latency164", "buffer164 queue164", "worker164"],
    ),
    (
        ("storage164 network164 latency164 buffer164 queue164 worker164", 28),
        ["storage164 network164", "latency164 buffer164", "queue164 worker164"],
    ),
    (
        ("network164 latency164 buffer164 queue164 worker164 kernel164", 6),
        ["network164", "latency164", "buffer164", "queue164", "worker164", "kernel164"],
    ),
    (
        ("network164 latency164 buffer164 queue164 worker164 kernel164", 10),
        ["network164", "latency164", "buffer164", "queue164", "worker164", "kernel164"],
    ),
    (
        ("network164 latency164 buffer164 queue164 worker164 kernel164", 18),
        ["network164", "latency164", "buffer164 queue164", "worker164", "kernel164"],
    ),
    (
        ("network164 latency164 buffer164 queue164 worker164 kernel164", 28),
        ["network164 latency164", "buffer164 queue164 worker164", "kernel164"],
    ),
    (
        ("latency164 buffer164 queue164 worker164 kernel164 signal164", 6),
        ["latency164", "buffer164", "queue164", "worker164", "kernel164", "signal164"],
    ),
    (
        ("latency164 buffer164 queue164 worker164 kernel164 signal164", 10),
        ["latency164", "buffer164", "queue164", "worker164", "kernel164", "signal164"],
    ),
    (
        ("latency164 buffer164 queue164 worker164 kernel164 signal164", 18),
        ["latency164", "buffer164 queue164", "worker164", "kernel164", "signal164"],
    ),
    (
        ("latency164 buffer164 queue164 worker164 kernel164 signal164", 28),
        ["latency164 buffer164", "queue164 worker164 kernel164", "signal164"],
    ),
    (
        ("buffer164 queue164 worker164 kernel164 signal164 packet164", 6),
        ["buffer164", "queue164", "worker164", "kernel164", "signal164", "packet164"],
    ),
    (
        ("buffer164 queue164 worker164 kernel164 signal164 packet164", 10),
        ["buffer164", "queue164", "worker164", "kernel164", "signal164", "packet164"],
    ),
    (
        ("buffer164 queue164 worker164 kernel164 signal164 packet164", 18),
        ["buffer164 queue164", "worker164", "kernel164", "signal164", "packet164"],
    ),
    (
        ("buffer164 queue164 worker164 kernel164 signal164 packet164", 28),
        ["buffer164 queue164 worker164", "kernel164 signal164", "packet164"],
    ),
    (
        ("queue164 worker164 kernel164 signal164 packet164 router164", 6),
        ["queue164", "worker164", "kernel164", "signal164", "packet164", "router164"],
    ),
    (
        ("queue164 worker164 kernel164 signal164 packet164 router164", 10),
        ["queue164", "worker164", "kernel164", "signal164", "packet164", "router164"],
    ),
    (
        ("queue164 worker164 kernel164 signal164 packet164 router164", 18),
        ["queue164 worker164", "kernel164", "signal164", "packet164", "router164"],
    ),
    (
        ("queue164 worker164 kernel164 signal164 packet164 router164", 28),
        ["queue164 worker164 kernel164", "signal164 packet164", "router164"],
    ),
    (
        ("worker164 kernel164 signal164 packet164 router164 cluster164", 6),
        ["worker164", "kernel164", "signal164", "packet164", "router164", "cluster164"],
    ),
    (
        ("worker164 kernel164 signal164 packet164 router164 cluster164", 10),
        ["worker164", "kernel164", "signal164", "packet164", "router164", "cluster164"],
    ),
    (
        ("worker164 kernel164 signal164 packet164 router164 cluster164", 18),
        ["worker164", "kernel164", "signal164", "packet164", "router164", "cluster164"],
    ),
    (
        ("worker164 kernel164 signal164 packet164 router164 cluster164", 28),
        ["worker164 kernel164", "signal164 packet164", "router164 cluster164"],
    ),
    (
        ("kernel164 signal164 packet164 router164 cluster164 mirror164", 6),
        ["kernel164", "signal164", "packet164", "router164", "cluster164", "mirror164"],
    ),
    (
        ("kernel164 signal164 packet164 router164 cluster164 mirror164", 10),
        ["kernel164", "signal164", "packet164", "router164", "cluster164", "mirror164"],
    ),
    (
        ("kernel164 signal164 packet164 router164 cluster164 mirror164", 18),
        ["kernel164", "signal164", "packet164", "router164", "cluster164", "mirror164"],
    ),
    (
        ("kernel164 signal164 packet164 router164 cluster164 mirror164", 28),
        ["kernel164 signal164", "packet164 router164", "cluster164 mirror164"],
    ),
    (
        ("signal164 packet164 router164 cluster164 mirror164 filter164", 6),
        ["signal164", "packet164", "router164", "cluster164", "mirror164", "filter164"],
    ),
    (
        ("signal164 packet164 router164 cluster164 mirror164 filter164", 10),
        ["signal164", "packet164", "router164", "cluster164", "mirror164", "filter164"],
    ),
    (
        ("signal164 packet164 router164 cluster164 mirror164 filter164", 18),
        ["signal164", "packet164", "router164", "cluster164", "mirror164", "filter164"],
    ),
    (
        ("signal164 packet164 router164 cluster164 mirror164 filter164", 28),
        ["signal164 packet164", "router164 cluster164", "mirror164 filter164"],
    ),
    (
        ("packet164 router164 cluster164 mirror164 filter164 ranking164", 6),
        ["packet164", "router164", "cluster164", "mirror164", "filter164", "ranking164"],
    ),
    (
        ("packet164 router164 cluster164 mirror164 filter164 ranking164", 10),
        ["packet164", "router164", "cluster164", "mirror164", "filter164", "ranking164"],
    ),
    (
        ("packet164 router164 cluster164 mirror164 filter164 ranking164", 18),
        ["packet164", "router164", "cluster164", "mirror164", "filter164", "ranking164"],
    ),
    (
        ("packet164 router164 cluster164 mirror164 filter164 ranking164", 28),
        ["packet164 router164", "cluster164 mirror164", "filter164 ranking164"],
    ),
    (
        ("router164 cluster164 mirror164 filter164 ranking164 encoding164", 6),
        ["router164", "cluster164", "mirror164", "filter164", "ranking164", "encoding164"],
    ),
    (
        ("router164 cluster164 mirror164 filter164 ranking164 encoding164", 10),
        ["router164", "cluster164", "mirror164", "filter164", "ranking164", "encoding164"],
    ),
    (
        ("router164 cluster164 mirror164 filter164 ranking164 encoding164", 18),
        ["router164", "cluster164", "mirror164", "filter164", "ranking164", "encoding164"],
    ),
    (
        ("router164 cluster164 mirror164 filter164 ranking164 encoding164", 28),
        ["router164 cluster164", "mirror164 filter164", "ranking164 encoding164"],
    ),
    (
        ("cluster164 mirror164 filter164 ranking164 encoding164 mapping164", 6),
        ["cluster164", "mirror164", "filter164", "ranking164", "encoding164", "mapping164"],
    ),
    (
        ("cluster164 mirror164 filter164 ranking164 encoding164 mapping164", 10),
        ["cluster164", "mirror164", "filter164", "ranking164", "encoding164", "mapping164"],
    ),
    (
        ("cluster164 mirror164 filter164 ranking164 encoding164 mapping164", 18),
        ["cluster164", "mirror164", "filter164", "ranking164", "encoding164", "mapping164"],
    ),
    (
        ("cluster164 mirror164 filter164 ranking164 encoding164 mapping164", 28),
        ["cluster164 mirror164", "filter164 ranking164", "encoding164 mapping164"],
    ),
    (
        ("mirror164 filter164 ranking164 encoding164 mapping164 record164", 6),
        ["mirror164", "filter164", "ranking164", "encoding164", "mapping164", "record164"],
    ),
    (
        ("mirror164 filter164 ranking164 encoding164 mapping164 record164", 10),
        ["mirror164", "filter164", "ranking164", "encoding164", "mapping164", "record164"],
    ),
    (
        ("mirror164 filter164 ranking164 encoding164 mapping164 record164", 18),
        ["mirror164", "filter164", "ranking164", "encoding164", "mapping164", "record164"],
    ),
    (
        ("mirror164 filter164 ranking164 encoding164 mapping164 record164", 28),
        ["mirror164 filter164", "ranking164 encoding164", "mapping164 record164"],
    ),
    (
        ("filter164 ranking164 encoding164 mapping164 record164 candle164", 6),
        ["filter164", "ranking164", "encoding164", "mapping164", "record164", "candle164"],
    ),
    (
        ("filter164 ranking164 encoding164 mapping164 record164 candle164", 10),
        ["filter164", "ranking164", "encoding164", "mapping164", "record164", "candle164"],
    ),
    (
        ("filter164 ranking164 encoding164 mapping164 record164 candle164", 18),
        ["filter164", "ranking164", "encoding164", "mapping164", "record164", "candle164"],
    ),
    (
        ("filter164 ranking164 encoding164 mapping164 record164 candle164", 28),
        ["filter164 ranking164", "encoding164 mapping164", "record164 candle164"],
    ),
    (
        ("ranking164 encoding164 mapping164 record164 candle164 thread164", 6),
        ["ranking164", "encoding164", "mapping164", "record164", "candle164", "thread164"],
    ),
    (
        ("ranking164 encoding164 mapping164 record164 candle164 thread164", 10),
        ["ranking164", "encoding164", "mapping164", "record164", "candle164", "thread164"],
    ),
    (
        ("ranking164 encoding164 mapping164 record164 candle164 thread164", 18),
        ["ranking164", "encoding164", "mapping164", "record164", "candle164", "thread164"],
    ),
    (
        ("ranking164 encoding164 mapping164 record164 candle164 thread164", 28),
        ["ranking164 encoding164", "mapping164 record164", "candle164 thread164"],
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
