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
        ("round 737: the quick brown fox jumps over the lazy dog", 4),
        ["round", "737:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 737: the quick brown fox jumps over the lazy dog", 8),
        ["round", "737: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 737: the quick brown fox jumps over the lazy dog", 12),
        ["round 737:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 737: the quick brown fox jumps over the lazy dog", 16),
        ["round 737: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 737: the quick brown fox jumps over the lazy dog", 24),
        ["round 737: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 737: the quick brown fox jumps over the lazy dog", 32),
        ["round 737: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 737: agentuniverse is a framework for multi agents", 4),
        ["round", "737:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 737: agentuniverse is a framework for multi agents", 8),
        ["round", "737:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 737: agentuniverse is a framework for multi agents", 12),
        ["round 737:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 737: agentuniverse is a framework for multi agents", 16),
        ["round 737:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 737: agentuniverse is a framework for multi agents", 24),
        ["round 737: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 737: agentuniverse is a framework for multi agents", 32),
        ["round 737: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 737: knowledge stored as vectors enables retrieval", 4),
        ["round", "737:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 737: knowledge stored as vectors enables retrieval", 8),
        ["round", "737:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 737: knowledge stored as vectors enables retrieval", 12),
        ["round 737:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 737: knowledge stored as vectors enables retrieval", 16),
        ["round 737:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 737: knowledge stored as vectors enables retrieval", 24),
        ["round 737: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 737: knowledge stored as vectors enables retrieval", 32),
        ["round 737: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 737: the processor reads the record then stops", 4),
        ["round", "737:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 737: the processor reads the record then stops", 8),
        ["round", "737: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 737: the processor reads the record then stops", 12),
        ["round 737:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 737: the processor reads the record then stops", 16),
        ["round 737: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 737: the processor reads the record then stops", 24),
        ["round 737: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 737: the processor reads the record then stops", 32),
        ["round 737: the processor reads", "the record then stops"],
    ),
    (
        ("round 737: a worker pulls the next task from the queue", 4),
        ["round", "737:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 737: a worker pulls the next task from the queue", 8),
        ["round", "737: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 737: a worker pulls the next task from the queue", 12),
        ["round 737: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 737: a worker pulls the next task from the queue", 16),
        ["round 737: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 737: a worker pulls the next task from the queue", 24),
        ["round 737: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 737: a worker pulls the next task from the queue", 32),
        ["round 737: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 737: signals travel through the network layer", 4),
        ["round", "737:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 737: signals travel through the network layer", 8),
        ["round", "737:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 737: signals travel through the network layer", 12),
        ["round 737:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 737: signals travel through the network layer", 16),
        ["round 737:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 737: signals travel through the network layer", 24),
        ["round 737: signals", "travel through the", "network layer"],
    ),
    (
        ("round 737: signals travel through the network layer", 32),
        ["round 737: signals travel", "through the network layer"],
    ),
    (
        ("round 737: the gateway routes each request by policy", 4),
        ["round", "737:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 737: the gateway routes each request by policy", 8),
        ["round", "737: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 737: the gateway routes each request by policy", 12),
        ["round 737:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 737: the gateway routes each request by policy", 16),
        ["round 737: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 737: the gateway routes each request by policy", 24),
        ["round 737: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 737: the gateway routes each request by policy", 32),
        ["round 737: the gateway routes", "each request by policy"],
    ),
    (
        ("round 737: memory grows until the buffer is full", 4),
        ["round", "737:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 737: memory grows until the buffer is full", 8),
        ["round", "737:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 737: memory grows until the buffer is full", 12),
        ["round 737:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 737: memory grows until the buffer is full", 16),
        ["round 737:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 737: memory grows until the buffer is full", 24), ["round 737: memory grows", "until the buffer is full"]),
    (("round 737: memory grows until the buffer is full", 32), ["round 737: memory grows until", "the buffer is full"]),
    (
        ("round 737: the cluster mirrors every packet twice", 4),
        ["round", "737:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 737: the cluster mirrors every packet twice", 8),
        ["round", "737: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 737: the cluster mirrors every packet twice", 12),
        ["round 737:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 737: the cluster mirrors every packet twice", 16),
        ["round 737: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 737: the cluster mirrors every packet twice", 24),
        ["round 737: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 737: the cluster mirrors every packet twice", 32),
        ["round 737: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 737: ranking uses tokens learned from the corpus", 4),
        ["round", "737:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 737: ranking uses tokens learned from the corpus", 8),
        ["round", "737:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 737: ranking uses tokens learned from the corpus", 12),
        ["round 737:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 737: ranking uses tokens learned from the corpus", 16),
        ["round 737:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 737: ranking uses tokens learned from the corpus", 24),
        ["round 737: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 737: ranking uses tokens learned from the corpus", 32),
        ["round 737: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 737: a long session ends when the candle dies", 4),
        ["round", "737:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 737: a long session ends when the candle dies", 8),
        ["round", "737: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 737: a long session ends when the candle dies", 12),
        ["round 737: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 737: a long session ends when the candle dies", 16),
        ["round 737: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 737: a long session ends when the candle dies", 24),
        ["round 737: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 737: a long session ends when the candle dies", 32),
        ["round 737: a long session ends", "when the candle dies"],
    ),
    (
        ("round 737: encode the prompt then map the result", 4),
        ["round", "737:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 737: encode the prompt then map the result", 8),
        ["round", "737:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 737: encode the prompt then map the result", 12),
        ["round 737:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 737: encode the prompt then map the result", 16),
        ["round 737:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 737: encode the prompt then map the result", 24),
        ["round 737: encode the", "prompt then map the", "result"],
    ),
    (("round 737: encode the prompt then map the result", 32), ["round 737: encode the prompt", "then map the result"]),
    (
        ("round 737: the kernel wakes the worker at dawn", 4),
        ["round", "737:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 737: the kernel wakes the worker at dawn", 8),
        ["round", "737: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 737: the kernel wakes the worker at dawn", 12),
        ["round 737:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 737: the kernel wakes the worker at dawn", 16), ["round 737: the", "kernel wakes the", "worker at dawn"]),
    (("round 737: the kernel wakes the worker at dawn", 24), ["round 737: the kernel", "wakes the worker at dawn"]),
    (("round 737: the kernel wakes the worker at dawn", 32), ["round 737: the kernel wakes the", "worker at dawn"]),
    (
        ("round 737: service latency drops after the patch", 4),
        ["round", "737:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 737: service latency drops after the patch", 8),
        ["round", "737:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 737: service latency drops after the patch", 12),
        ["round 737:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 737: service latency drops after the patch", 16),
        ["round 737:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 737: service latency drops after the patch", 24),
        ["round 737: service", "latency drops after the", "patch"],
    ),
    (("round 737: service latency drops after the patch", 32), ["round 737: service latency drops", "after the patch"]),
    (
        ("round 737: the library caches every vector it sees", 4),
        ["round", "737:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 737: the library caches every vector it sees", 8),
        ["round", "737: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 737: the library caches every vector it sees", 12),
        ["round 737:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 737: the library caches every vector it sees", 16),
        ["round 737: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 737: the library caches every vector it sees", 24),
        ["round 737: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 737: the library caches every vector it sees", 32),
        ["round 737: the library caches", "every vector it sees"],
    ),
    (
        ("round 737: agents argue then the debate resolves", 4),
        ["round", "737:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 737: agents argue then the debate resolves", 8),
        ["round", "737:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 737: agents argue then the debate resolves", 12),
        ["round 737:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 737: agents argue then the debate resolves", 16),
        ["round 737:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 737: agents argue then the debate resolves", 24), ["round 737: agents argue", "then the debate resolves"]),
    (("round 737: agents argue then the debate resolves", 32), ["round 737: agents argue then the", "debate resolves"]),
    (
        ("round 737: the filter keeps only strong matches", 4),
        ["round", "737:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 737: the filter keeps only strong matches", 8),
        ["round", "737: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 737: the filter keeps only strong matches", 12),
        ["round 737:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 737: the filter keeps only strong matches", 16),
        ["round 737: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 737: the filter keeps only strong matches", 24),
        ["round 737: the filter", "keeps only strong", "matches"],
    ),
    (("round 737: the filter keeps only strong matches", 32), ["round 737: the filter keeps only", "strong matches"]),
    (
        ("round 737: the model answers with a short reply", 4),
        ["round", "737:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 737: the model answers with a short reply", 8),
        ["round", "737: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 737: the model answers with a short reply", 12),
        ["round 737:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 737: the model answers with a short reply", 16),
        ["round 737: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 737: the model answers with a short reply", 24),
        ["round 737: the model", "answers with a short", "reply"],
    ),
    (("round 737: the model answers with a short reply", 32), ["round 737: the model answers", "with a short reply"]),
    (
        ("round 737: the recorder stores the reasoning trace", 4),
        ["round", "737:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 737: the recorder stores the reasoning trace", 8),
        ["round", "737: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 737: the recorder stores the reasoning trace", 12),
        ["round 737:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 737: the recorder stores the reasoning trace", 16),
        ["round 737: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 737: the recorder stores the reasoning trace", 24),
        ["round 737: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 737: the recorder stores the reasoning trace", 32),
        ["round 737: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 737: the angel watches the processor run", 4),
        ["round", "737:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 737: the angel watches the processor run", 8),
        ["round", "737: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 737: the angel watches the processor run", 12),
        ["round 737:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 737: the angel watches the processor run", 16),
        ["round 737: the", "angel watches", "the processor", "run"],
    ),
    (("round 737: the angel watches the processor run", 24), ["round 737: the angel", "watches the processor", "run"]),
    (("round 737: the angel watches the processor run", 32), ["round 737: the angel watches the", "processor run"]),
    (
        ("round 737: angle of the vector decides the match", 4),
        ["round", "737:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 737: angle of the vector decides the match", 8),
        ["round", "737:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 737: angle of the vector decides the match", 12),
        ["round 737:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 737: angle of the vector decides the match", 16),
        ["round 737: angle", "of the vector", "decides the", "match"],
    ),
    (("round 737: angle of the vector decides the match", 24), ["round 737: angle of the", "vector decides the match"]),
    (("round 737: angle of the vector decides the match", 32), ["round 737: angle of the vector", "decides the match"]),
    (
        ("round 737: the candle burns twice as long at night", 4),
        ["round", "737:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 737: the candle burns twice as long at night", 8),
        ["round", "737: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 737: the candle burns twice as long at night", 12),
        ["round 737:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 737: the candle burns twice as long at night", 16),
        ["round 737: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 737: the candle burns twice as long at night", 24),
        ["round 737: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 737: the candle burns twice as long at night", 32),
        ["round 737: the candle burns", "twice as long at night"],
    ),
    (
        ("round 737: a mirror of the universe in one line", 4),
        ["round", "737:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 737: a mirror of the universe in one line", 8),
        ["round", "737: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 737: a mirror of the universe in one line", 12),
        ["round 737: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 737: a mirror of the universe in one line", 16),
        ["round 737: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 737: a mirror of the universe in one line", 24), ["round 737: a mirror of", "the universe in one line"]),
    (("round 737: a mirror of the universe in one line", 32), ["round 737: a mirror of the", "universe in one line"]),
    (
        ("round 737: the queue drains before the storm", 4),
        ["round", "737:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 737: the queue drains before the storm", 8),
        ["round", "737: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 737: the queue drains before the storm", 12),
        ["round 737:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 737: the queue drains before the storm", 16), ["round 737: the", "queue drains", "before the storm"]),
    (("round 737: the queue drains before the storm", 24), ["round 737: the queue", "drains before the storm"]),
    (("round 737: the queue drains before the storm", 32), ["round 737: the queue drains", "before the storm"]),
    (
        ("kitten737 sitting737 agent737 angle737 universe737 memory737", 6),
        ["kitten737", "sitting737", "agent737", "angle737", "universe737", "memory737"],
    ),
    (
        ("kitten737 sitting737 agent737 angle737 universe737 memory737", 10),
        ["kitten737", "sitting737", "agent737", "angle737", "universe737", "memory737"],
    ),
    (
        ("kitten737 sitting737 agent737 angle737 universe737 memory737", 18),
        ["kitten737", "sitting737", "agent737 angle737", "universe737", "memory737"],
    ),
    (
        ("kitten737 sitting737 agent737 angle737 universe737 memory737", 28),
        ["kitten737 sitting737", "agent737 angle737", "universe737 memory737"],
    ),
    (
        ("sitting737 agent737 angle737 universe737 memory737 stream737", 6),
        ["sitting737", "agent737", "angle737", "universe737", "memory737", "stream737"],
    ),
    (
        ("sitting737 agent737 angle737 universe737 memory737 stream737", 10),
        ["sitting737", "agent737", "angle737", "universe737", "memory737", "stream737"],
    ),
    (
        ("sitting737 agent737 angle737 universe737 memory737 stream737", 18),
        ["sitting737", "agent737 angle737", "universe737", "memory737", "stream737"],
    ),
    (
        ("sitting737 agent737 angle737 universe737 memory737 stream737", 28),
        ["sitting737 agent737 angle737", "universe737 memory737", "stream737"],
    ),
    (
        ("agent737 angle737 universe737 memory737 stream737 context737", 6),
        ["agent737", "angle737", "universe737", "memory737", "stream737", "context737"],
    ),
    (
        ("agent737 angle737 universe737 memory737 stream737 context737", 10),
        ["agent737", "angle737", "universe737", "memory737", "stream737", "context737"],
    ),
    (
        ("agent737 angle737 universe737 memory737 stream737 context737", 18),
        ["agent737 angle737", "universe737", "memory737", "stream737", "context737"],
    ),
    (
        ("agent737 angle737 universe737 memory737 stream737 context737", 28),
        ["agent737 angle737", "universe737 memory737", "stream737 context737"],
    ),
    (
        ("angle737 universe737 memory737 stream737 context737 knowledge737", 6),
        ["angle737", "universe737", "memory737", "stream737", "context737", "knowledge737"],
    ),
    (
        ("angle737 universe737 memory737 stream737 context737 knowledge737", 10),
        ["angle737", "universe737", "memory737", "stream737", "context737", "knowledge737"],
    ),
    (
        ("angle737 universe737 memory737 stream737 context737 knowledge737", 18),
        ["angle737", "universe737", "memory737", "stream737", "context737", "knowledge737"],
    ),
    (
        ("angle737 universe737 memory737 stream737 context737 knowledge737", 28),
        ["angle737 universe737", "memory737 stream737", "context737 knowledge737"],
    ),
    (
        ("universe737 memory737 stream737 context737 knowledge737 vector737", 6),
        ["universe737", "memory737", "stream737", "context737", "knowledge737", "vector737"],
    ),
    (
        ("universe737 memory737 stream737 context737 knowledge737 vector737", 10),
        ["universe737", "memory737", "stream737", "context737", "knowledge737", "vector737"],
    ),
    (
        ("universe737 memory737 stream737 context737 knowledge737 vector737", 18),
        ["universe737", "memory737", "stream737", "context737", "knowledge737", "vector737"],
    ),
    (
        ("universe737 memory737 stream737 context737 knowledge737 vector737", 28),
        ["universe737 memory737", "stream737 context737", "knowledge737 vector737"],
    ),
    (
        ("memory737 stream737 context737 knowledge737 vector737 processor737", 6),
        ["memory737", "stream737", "context737", "knowledge737", "vector737", "processor737"],
    ),
    (
        ("memory737 stream737 context737 knowledge737 vector737 processor737", 10),
        ["memory737", "stream737", "context737", "knowledge737", "vector737", "processor737"],
    ),
    (
        ("memory737 stream737 context737 knowledge737 vector737 processor737", 18),
        ["memory737", "stream737", "context737", "knowledge737", "vector737", "processor737"],
    ),
    (
        ("memory737 stream737 context737 knowledge737 vector737 processor737", 28),
        ["memory737 stream737", "context737 knowledge737", "vector737 processor737"],
    ),
    (
        ("stream737 context737 knowledge737 vector737 processor737 reasoning737", 6),
        ["stream737", "context737", "knowledge737", "vector737", "processor737", "reasoning737"],
    ),
    (
        ("stream737 context737 knowledge737 vector737 processor737 reasoning737", 10),
        ["stream737", "context737", "knowledge737", "vector737", "processor737", "reasoning737"],
    ),
    (
        ("stream737 context737 knowledge737 vector737 processor737 reasoning737", 18),
        ["stream737", "context737", "knowledge737", "vector737", "processor737", "reasoning737"],
    ),
    (
        ("stream737 context737 knowledge737 vector737 processor737 reasoning737", 28),
        ["stream737 context737", "knowledge737 vector737", "processor737 reasoning737"],
    ),
    (
        ("context737 knowledge737 vector737 processor737 reasoning737 machine737", 6),
        ["context737", "knowledge737", "vector737", "processor737", "reasoning737", "machine737"],
    ),
    (
        ("context737 knowledge737 vector737 processor737 reasoning737 machine737", 10),
        ["context737", "knowledge737", "vector737", "processor737", "reasoning737", "machine737"],
    ),
    (
        ("context737 knowledge737 vector737 processor737 reasoning737 machine737", 18),
        ["context737", "knowledge737", "vector737", "processor737", "reasoning737", "machine737"],
    ),
    (
        ("context737 knowledge737 vector737 processor737 reasoning737 machine737", 28),
        ["context737 knowledge737", "vector737 processor737", "reasoning737 machine737"],
    ),
    (
        ("knowledge737 vector737 processor737 reasoning737 machine737 learning737", 6),
        ["knowledge737", "vector737", "processor737", "reasoning737", "machine737", "learning737"],
    ),
    (
        ("knowledge737 vector737 processor737 reasoning737 machine737 learning737", 10),
        ["knowledge737", "vector737", "processor737", "reasoning737", "machine737", "learning737"],
    ),
    (
        ("knowledge737 vector737 processor737 reasoning737 machine737 learning737", 18),
        ["knowledge737", "vector737", "processor737", "reasoning737", "machine737", "learning737"],
    ),
    (
        ("knowledge737 vector737 processor737 reasoning737 machine737 learning737", 28),
        ["knowledge737 vector737", "processor737 reasoning737", "machine737 learning737"],
    ),
    (
        ("vector737 processor737 reasoning737 machine737 learning737 model737", 6),
        ["vector737", "processor737", "reasoning737", "machine737", "learning737", "model737"],
    ),
    (
        ("vector737 processor737 reasoning737 machine737 learning737 model737", 10),
        ["vector737", "processor737", "reasoning737", "machine737", "learning737", "model737"],
    ),
    (
        ("vector737 processor737 reasoning737 machine737 learning737 model737", 18),
        ["vector737", "processor737", "reasoning737", "machine737", "learning737", "model737"],
    ),
    (
        ("vector737 processor737 reasoning737 machine737 learning737 model737", 28),
        ["vector737 processor737", "reasoning737 machine737", "learning737 model737"],
    ),
    (
        ("processor737 reasoning737 machine737 learning737 model737 token737", 6),
        ["processor737", "reasoning737", "machine737", "learning737", "model737", "token737"],
    ),
    (
        ("processor737 reasoning737 machine737 learning737 model737 token737", 10),
        ["processor737", "reasoning737", "machine737", "learning737", "model737", "token737"],
    ),
    (
        ("processor737 reasoning737 machine737 learning737 model737 token737", 18),
        ["processor737", "reasoning737", "machine737", "learning737", "model737 token737"],
    ),
    (
        ("processor737 reasoning737 machine737 learning737 model737 token737", 28),
        ["processor737 reasoning737", "machine737 learning737", "model737 token737"],
    ),
    (
        ("reasoning737 machine737 learning737 model737 token737 prompt737", 6),
        ["reasoning737", "machine737", "learning737", "model737", "token737", "prompt737"],
    ),
    (
        ("reasoning737 machine737 learning737 model737 token737 prompt737", 10),
        ["reasoning737", "machine737", "learning737", "model737", "token737", "prompt737"],
    ),
    (
        ("reasoning737 machine737 learning737 model737 token737 prompt737", 18),
        ["reasoning737", "machine737", "learning737", "model737 token737", "prompt737"],
    ),
    (
        ("reasoning737 machine737 learning737 model737 token737 prompt737", 28),
        ["reasoning737 machine737", "learning737 model737", "token737 prompt737"],
    ),
    (
        ("machine737 learning737 model737 token737 prompt737 session737", 6),
        ["machine737", "learning737", "model737", "token737", "prompt737", "session737"],
    ),
    (
        ("machine737 learning737 model737 token737 prompt737 session737", 10),
        ["machine737", "learning737", "model737", "token737", "prompt737", "session737"],
    ),
    (
        ("machine737 learning737 model737 token737 prompt737 session737", 18),
        ["machine737", "learning737", "model737 token737", "prompt737", "session737"],
    ),
    (
        ("machine737 learning737 model737 token737 prompt737 session737", 28),
        ["machine737 learning737", "model737 token737 prompt737", "session737"],
    ),
    (
        ("learning737 model737 token737 prompt737 session737 library737", 6),
        ["learning737", "model737", "token737", "prompt737", "session737", "library737"],
    ),
    (
        ("learning737 model737 token737 prompt737 session737 library737", 10),
        ["learning737", "model737", "token737", "prompt737", "session737", "library737"],
    ),
    (
        ("learning737 model737 token737 prompt737 session737 library737", 18),
        ["learning737", "model737 token737", "prompt737", "session737", "library737"],
    ),
    (
        ("learning737 model737 token737 prompt737 session737 library737", 28),
        ["learning737 model737", "token737 prompt737", "session737 library737"],
    ),
    (
        ("model737 token737 prompt737 session737 library737 service737", 6),
        ["model737", "token737", "prompt737", "session737", "library737", "service737"],
    ),
    (
        ("model737 token737 prompt737 session737 library737 service737", 10),
        ["model737", "token737", "prompt737", "session737", "library737", "service737"],
    ),
    (
        ("model737 token737 prompt737 session737 library737 service737", 18),
        ["model737 token737", "prompt737", "session737", "library737", "service737"],
    ),
    (
        ("model737 token737 prompt737 session737 library737 service737", 28),
        ["model737 token737 prompt737", "session737 library737", "service737"],
    ),
    (
        ("token737 prompt737 session737 library737 service737 gateway737", 6),
        ["token737", "prompt737", "session737", "library737", "service737", "gateway737"],
    ),
    (
        ("token737 prompt737 session737 library737 service737 gateway737", 10),
        ["token737", "prompt737", "session737", "library737", "service737", "gateway737"],
    ),
    (
        ("token737 prompt737 session737 library737 service737 gateway737", 18),
        ["token737 prompt737", "session737", "library737", "service737", "gateway737"],
    ),
    (
        ("token737 prompt737 session737 library737 service737 gateway737", 28),
        ["token737 prompt737", "session737 library737", "service737 gateway737"],
    ),
    (
        ("prompt737 session737 library737 service737 gateway737 storage737", 6),
        ["prompt737", "session737", "library737", "service737", "gateway737", "storage737"],
    ),
    (
        ("prompt737 session737 library737 service737 gateway737 storage737", 10),
        ["prompt737", "session737", "library737", "service737", "gateway737", "storage737"],
    ),
    (
        ("prompt737 session737 library737 service737 gateway737 storage737", 18),
        ["prompt737", "session737", "library737", "service737", "gateway737", "storage737"],
    ),
    (
        ("prompt737 session737 library737 service737 gateway737 storage737", 28),
        ["prompt737 session737", "library737 service737", "gateway737 storage737"],
    ),
    (
        ("session737 library737 service737 gateway737 storage737 network737", 6),
        ["session737", "library737", "service737", "gateway737", "storage737", "network737"],
    ),
    (
        ("session737 library737 service737 gateway737 storage737 network737", 10),
        ["session737", "library737", "service737", "gateway737", "storage737", "network737"],
    ),
    (
        ("session737 library737 service737 gateway737 storage737 network737", 18),
        ["session737", "library737", "service737", "gateway737", "storage737", "network737"],
    ),
    (
        ("session737 library737 service737 gateway737 storage737 network737", 28),
        ["session737 library737", "service737 gateway737", "storage737 network737"],
    ),
    (
        ("library737 service737 gateway737 storage737 network737 latency737", 6),
        ["library737", "service737", "gateway737", "storage737", "network737", "latency737"],
    ),
    (
        ("library737 service737 gateway737 storage737 network737 latency737", 10),
        ["library737", "service737", "gateway737", "storage737", "network737", "latency737"],
    ),
    (
        ("library737 service737 gateway737 storage737 network737 latency737", 18),
        ["library737", "service737", "gateway737", "storage737", "network737", "latency737"],
    ),
    (
        ("library737 service737 gateway737 storage737 network737 latency737", 28),
        ["library737 service737", "gateway737 storage737", "network737 latency737"],
    ),
    (
        ("service737 gateway737 storage737 network737 latency737 buffer737", 6),
        ["service737", "gateway737", "storage737", "network737", "latency737", "buffer737"],
    ),
    (
        ("service737 gateway737 storage737 network737 latency737 buffer737", 10),
        ["service737", "gateway737", "storage737", "network737", "latency737", "buffer737"],
    ),
    (
        ("service737 gateway737 storage737 network737 latency737 buffer737", 18),
        ["service737", "gateway737", "storage737", "network737", "latency737", "buffer737"],
    ),
    (
        ("service737 gateway737 storage737 network737 latency737 buffer737", 28),
        ["service737 gateway737", "storage737 network737", "latency737 buffer737"],
    ),
    (
        ("gateway737 storage737 network737 latency737 buffer737 queue737", 6),
        ["gateway737", "storage737", "network737", "latency737", "buffer737", "queue737"],
    ),
    (
        ("gateway737 storage737 network737 latency737 buffer737 queue737", 10),
        ["gateway737", "storage737", "network737", "latency737", "buffer737", "queue737"],
    ),
    (
        ("gateway737 storage737 network737 latency737 buffer737 queue737", 18),
        ["gateway737", "storage737", "network737", "latency737", "buffer737 queue737"],
    ),
    (
        ("gateway737 storage737 network737 latency737 buffer737 queue737", 28),
        ["gateway737 storage737", "network737 latency737", "buffer737 queue737"],
    ),
    (
        ("storage737 network737 latency737 buffer737 queue737 worker737", 6),
        ["storage737", "network737", "latency737", "buffer737", "queue737", "worker737"],
    ),
    (
        ("storage737 network737 latency737 buffer737 queue737 worker737", 10),
        ["storage737", "network737", "latency737", "buffer737", "queue737", "worker737"],
    ),
    (
        ("storage737 network737 latency737 buffer737 queue737 worker737", 18),
        ["storage737", "network737", "latency737", "buffer737 queue737", "worker737"],
    ),
    (
        ("storage737 network737 latency737 buffer737 queue737 worker737", 28),
        ["storage737 network737", "latency737 buffer737", "queue737 worker737"],
    ),
    (
        ("network737 latency737 buffer737 queue737 worker737 kernel737", 6),
        ["network737", "latency737", "buffer737", "queue737", "worker737", "kernel737"],
    ),
    (
        ("network737 latency737 buffer737 queue737 worker737 kernel737", 10),
        ["network737", "latency737", "buffer737", "queue737", "worker737", "kernel737"],
    ),
    (
        ("network737 latency737 buffer737 queue737 worker737 kernel737", 18),
        ["network737", "latency737", "buffer737 queue737", "worker737", "kernel737"],
    ),
    (
        ("network737 latency737 buffer737 queue737 worker737 kernel737", 28),
        ["network737 latency737", "buffer737 queue737 worker737", "kernel737"],
    ),
    (
        ("latency737 buffer737 queue737 worker737 kernel737 signal737", 6),
        ["latency737", "buffer737", "queue737", "worker737", "kernel737", "signal737"],
    ),
    (
        ("latency737 buffer737 queue737 worker737 kernel737 signal737", 10),
        ["latency737", "buffer737", "queue737", "worker737", "kernel737", "signal737"],
    ),
    (
        ("latency737 buffer737 queue737 worker737 kernel737 signal737", 18),
        ["latency737", "buffer737 queue737", "worker737", "kernel737", "signal737"],
    ),
    (
        ("latency737 buffer737 queue737 worker737 kernel737 signal737", 28),
        ["latency737 buffer737", "queue737 worker737 kernel737", "signal737"],
    ),
    (
        ("buffer737 queue737 worker737 kernel737 signal737 packet737", 6),
        ["buffer737", "queue737", "worker737", "kernel737", "signal737", "packet737"],
    ),
    (
        ("buffer737 queue737 worker737 kernel737 signal737 packet737", 10),
        ["buffer737", "queue737", "worker737", "kernel737", "signal737", "packet737"],
    ),
    (
        ("buffer737 queue737 worker737 kernel737 signal737 packet737", 18),
        ["buffer737 queue737", "worker737", "kernel737", "signal737", "packet737"],
    ),
    (
        ("buffer737 queue737 worker737 kernel737 signal737 packet737", 28),
        ["buffer737 queue737 worker737", "kernel737 signal737", "packet737"],
    ),
    (
        ("queue737 worker737 kernel737 signal737 packet737 router737", 6),
        ["queue737", "worker737", "kernel737", "signal737", "packet737", "router737"],
    ),
    (
        ("queue737 worker737 kernel737 signal737 packet737 router737", 10),
        ["queue737", "worker737", "kernel737", "signal737", "packet737", "router737"],
    ),
    (
        ("queue737 worker737 kernel737 signal737 packet737 router737", 18),
        ["queue737 worker737", "kernel737", "signal737", "packet737", "router737"],
    ),
    (
        ("queue737 worker737 kernel737 signal737 packet737 router737", 28),
        ["queue737 worker737 kernel737", "signal737 packet737", "router737"],
    ),
    (
        ("worker737 kernel737 signal737 packet737 router737 cluster737", 6),
        ["worker737", "kernel737", "signal737", "packet737", "router737", "cluster737"],
    ),
    (
        ("worker737 kernel737 signal737 packet737 router737 cluster737", 10),
        ["worker737", "kernel737", "signal737", "packet737", "router737", "cluster737"],
    ),
    (
        ("worker737 kernel737 signal737 packet737 router737 cluster737", 18),
        ["worker737", "kernel737", "signal737", "packet737", "router737", "cluster737"],
    ),
    (
        ("worker737 kernel737 signal737 packet737 router737 cluster737", 28),
        ["worker737 kernel737", "signal737 packet737", "router737 cluster737"],
    ),
    (
        ("kernel737 signal737 packet737 router737 cluster737 mirror737", 6),
        ["kernel737", "signal737", "packet737", "router737", "cluster737", "mirror737"],
    ),
    (
        ("kernel737 signal737 packet737 router737 cluster737 mirror737", 10),
        ["kernel737", "signal737", "packet737", "router737", "cluster737", "mirror737"],
    ),
    (
        ("kernel737 signal737 packet737 router737 cluster737 mirror737", 18),
        ["kernel737", "signal737", "packet737", "router737", "cluster737", "mirror737"],
    ),
    (
        ("kernel737 signal737 packet737 router737 cluster737 mirror737", 28),
        ["kernel737 signal737", "packet737 router737", "cluster737 mirror737"],
    ),
    (
        ("signal737 packet737 router737 cluster737 mirror737 filter737", 6),
        ["signal737", "packet737", "router737", "cluster737", "mirror737", "filter737"],
    ),
    (
        ("signal737 packet737 router737 cluster737 mirror737 filter737", 10),
        ["signal737", "packet737", "router737", "cluster737", "mirror737", "filter737"],
    ),
    (
        ("signal737 packet737 router737 cluster737 mirror737 filter737", 18),
        ["signal737", "packet737", "router737", "cluster737", "mirror737", "filter737"],
    ),
    (
        ("signal737 packet737 router737 cluster737 mirror737 filter737", 28),
        ["signal737 packet737", "router737 cluster737", "mirror737 filter737"],
    ),
    (
        ("packet737 router737 cluster737 mirror737 filter737 ranking737", 6),
        ["packet737", "router737", "cluster737", "mirror737", "filter737", "ranking737"],
    ),
    (
        ("packet737 router737 cluster737 mirror737 filter737 ranking737", 10),
        ["packet737", "router737", "cluster737", "mirror737", "filter737", "ranking737"],
    ),
    (
        ("packet737 router737 cluster737 mirror737 filter737 ranking737", 18),
        ["packet737", "router737", "cluster737", "mirror737", "filter737", "ranking737"],
    ),
    (
        ("packet737 router737 cluster737 mirror737 filter737 ranking737", 28),
        ["packet737 router737", "cluster737 mirror737", "filter737 ranking737"],
    ),
    (
        ("router737 cluster737 mirror737 filter737 ranking737 encoding737", 6),
        ["router737", "cluster737", "mirror737", "filter737", "ranking737", "encoding737"],
    ),
    (
        ("router737 cluster737 mirror737 filter737 ranking737 encoding737", 10),
        ["router737", "cluster737", "mirror737", "filter737", "ranking737", "encoding737"],
    ),
    (
        ("router737 cluster737 mirror737 filter737 ranking737 encoding737", 18),
        ["router737", "cluster737", "mirror737", "filter737", "ranking737", "encoding737"],
    ),
    (
        ("router737 cluster737 mirror737 filter737 ranking737 encoding737", 28),
        ["router737 cluster737", "mirror737 filter737", "ranking737 encoding737"],
    ),
    (
        ("cluster737 mirror737 filter737 ranking737 encoding737 mapping737", 6),
        ["cluster737", "mirror737", "filter737", "ranking737", "encoding737", "mapping737"],
    ),
    (
        ("cluster737 mirror737 filter737 ranking737 encoding737 mapping737", 10),
        ["cluster737", "mirror737", "filter737", "ranking737", "encoding737", "mapping737"],
    ),
    (
        ("cluster737 mirror737 filter737 ranking737 encoding737 mapping737", 18),
        ["cluster737", "mirror737", "filter737", "ranking737", "encoding737", "mapping737"],
    ),
    (
        ("cluster737 mirror737 filter737 ranking737 encoding737 mapping737", 28),
        ["cluster737 mirror737", "filter737 ranking737", "encoding737 mapping737"],
    ),
    (
        ("mirror737 filter737 ranking737 encoding737 mapping737 record737", 6),
        ["mirror737", "filter737", "ranking737", "encoding737", "mapping737", "record737"],
    ),
    (
        ("mirror737 filter737 ranking737 encoding737 mapping737 record737", 10),
        ["mirror737", "filter737", "ranking737", "encoding737", "mapping737", "record737"],
    ),
    (
        ("mirror737 filter737 ranking737 encoding737 mapping737 record737", 18),
        ["mirror737", "filter737", "ranking737", "encoding737", "mapping737", "record737"],
    ),
    (
        ("mirror737 filter737 ranking737 encoding737 mapping737 record737", 28),
        ["mirror737 filter737", "ranking737 encoding737", "mapping737 record737"],
    ),
    (
        ("filter737 ranking737 encoding737 mapping737 record737 candle737", 6),
        ["filter737", "ranking737", "encoding737", "mapping737", "record737", "candle737"],
    ),
    (
        ("filter737 ranking737 encoding737 mapping737 record737 candle737", 10),
        ["filter737", "ranking737", "encoding737", "mapping737", "record737", "candle737"],
    ),
    (
        ("filter737 ranking737 encoding737 mapping737 record737 candle737", 18),
        ["filter737", "ranking737", "encoding737", "mapping737", "record737", "candle737"],
    ),
    (
        ("filter737 ranking737 encoding737 mapping737 record737 candle737", 28),
        ["filter737 ranking737", "encoding737 mapping737", "record737 candle737"],
    ),
    (
        ("ranking737 encoding737 mapping737 record737 candle737 thread737", 6),
        ["ranking737", "encoding737", "mapping737", "record737", "candle737", "thread737"],
    ),
    (
        ("ranking737 encoding737 mapping737 record737 candle737 thread737", 10),
        ["ranking737", "encoding737", "mapping737", "record737", "candle737", "thread737"],
    ),
    (
        ("ranking737 encoding737 mapping737 record737 candle737 thread737", 18),
        ["ranking737", "encoding737", "mapping737", "record737", "candle737", "thread737"],
    ),
    (
        ("ranking737 encoding737 mapping737 record737 candle737 thread737", 28),
        ["ranking737 encoding737", "mapping737 record737", "candle737 thread737"],
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
