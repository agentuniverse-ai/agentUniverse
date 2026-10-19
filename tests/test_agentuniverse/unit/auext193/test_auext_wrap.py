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
        ("round 193: the quick brown fox jumps over the lazy dog", 4),
        ["round", "193:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 193: the quick brown fox jumps over the lazy dog", 8),
        ["round", "193: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 193: the quick brown fox jumps over the lazy dog", 12),
        ["round 193:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 193: the quick brown fox jumps over the lazy dog", 16),
        ["round 193: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 193: the quick brown fox jumps over the lazy dog", 24),
        ["round 193: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 193: the quick brown fox jumps over the lazy dog", 32),
        ["round 193: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 193: agentuniverse is a framework for multi agents", 4),
        ["round", "193:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 193: agentuniverse is a framework for multi agents", 8),
        ["round", "193:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 193: agentuniverse is a framework for multi agents", 12),
        ["round 193:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 193: agentuniverse is a framework for multi agents", 16),
        ["round 193:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 193: agentuniverse is a framework for multi agents", 24),
        ["round 193: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 193: agentuniverse is a framework for multi agents", 32),
        ["round 193: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 193: knowledge stored as vectors enables retrieval", 4),
        ["round", "193:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 193: knowledge stored as vectors enables retrieval", 8),
        ["round", "193:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 193: knowledge stored as vectors enables retrieval", 12),
        ["round 193:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 193: knowledge stored as vectors enables retrieval", 16),
        ["round 193:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 193: knowledge stored as vectors enables retrieval", 24),
        ["round 193: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 193: knowledge stored as vectors enables retrieval", 32),
        ["round 193: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 193: the processor reads the record then stops", 4),
        ["round", "193:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 193: the processor reads the record then stops", 8),
        ["round", "193: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 193: the processor reads the record then stops", 12),
        ["round 193:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 193: the processor reads the record then stops", 16),
        ["round 193: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 193: the processor reads the record then stops", 24),
        ["round 193: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 193: the processor reads the record then stops", 32),
        ["round 193: the processor reads", "the record then stops"],
    ),
    (
        ("round 193: a worker pulls the next task from the queue", 4),
        ["round", "193:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 193: a worker pulls the next task from the queue", 8),
        ["round", "193: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 193: a worker pulls the next task from the queue", 12),
        ["round 193: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 193: a worker pulls the next task from the queue", 16),
        ["round 193: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 193: a worker pulls the next task from the queue", 24),
        ["round 193: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 193: a worker pulls the next task from the queue", 32),
        ["round 193: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 193: signals travel through the network layer", 4),
        ["round", "193:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 193: signals travel through the network layer", 8),
        ["round", "193:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 193: signals travel through the network layer", 12),
        ["round 193:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 193: signals travel through the network layer", 16),
        ["round 193:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 193: signals travel through the network layer", 24),
        ["round 193: signals", "travel through the", "network layer"],
    ),
    (
        ("round 193: signals travel through the network layer", 32),
        ["round 193: signals travel", "through the network layer"],
    ),
    (
        ("round 193: the gateway routes each request by policy", 4),
        ["round", "193:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 193: the gateway routes each request by policy", 8),
        ["round", "193: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 193: the gateway routes each request by policy", 12),
        ["round 193:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 193: the gateway routes each request by policy", 16),
        ["round 193: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 193: the gateway routes each request by policy", 24),
        ["round 193: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 193: the gateway routes each request by policy", 32),
        ["round 193: the gateway routes", "each request by policy"],
    ),
    (
        ("round 193: memory grows until the buffer is full", 4),
        ["round", "193:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 193: memory grows until the buffer is full", 8),
        ["round", "193:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 193: memory grows until the buffer is full", 12),
        ["round 193:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 193: memory grows until the buffer is full", 16),
        ["round 193:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 193: memory grows until the buffer is full", 24), ["round 193: memory grows", "until the buffer is full"]),
    (("round 193: memory grows until the buffer is full", 32), ["round 193: memory grows until", "the buffer is full"]),
    (
        ("round 193: the cluster mirrors every packet twice", 4),
        ["round", "193:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 193: the cluster mirrors every packet twice", 8),
        ["round", "193: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 193: the cluster mirrors every packet twice", 12),
        ["round 193:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 193: the cluster mirrors every packet twice", 16),
        ["round 193: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 193: the cluster mirrors every packet twice", 24),
        ["round 193: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 193: the cluster mirrors every packet twice", 32),
        ["round 193: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 193: ranking uses tokens learned from the corpus", 4),
        ["round", "193:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 193: ranking uses tokens learned from the corpus", 8),
        ["round", "193:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 193: ranking uses tokens learned from the corpus", 12),
        ["round 193:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 193: ranking uses tokens learned from the corpus", 16),
        ["round 193:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 193: ranking uses tokens learned from the corpus", 24),
        ["round 193: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 193: ranking uses tokens learned from the corpus", 32),
        ["round 193: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 193: a long session ends when the candle dies", 4),
        ["round", "193:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 193: a long session ends when the candle dies", 8),
        ["round", "193: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 193: a long session ends when the candle dies", 12),
        ["round 193: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 193: a long session ends when the candle dies", 16),
        ["round 193: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 193: a long session ends when the candle dies", 24),
        ["round 193: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 193: a long session ends when the candle dies", 32),
        ["round 193: a long session ends", "when the candle dies"],
    ),
    (
        ("round 193: encode the prompt then map the result", 4),
        ["round", "193:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 193: encode the prompt then map the result", 8),
        ["round", "193:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 193: encode the prompt then map the result", 12),
        ["round 193:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 193: encode the prompt then map the result", 16),
        ["round 193:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 193: encode the prompt then map the result", 24),
        ["round 193: encode the", "prompt then map the", "result"],
    ),
    (("round 193: encode the prompt then map the result", 32), ["round 193: encode the prompt", "then map the result"]),
    (
        ("round 193: the kernel wakes the worker at dawn", 4),
        ["round", "193:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 193: the kernel wakes the worker at dawn", 8),
        ["round", "193: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 193: the kernel wakes the worker at dawn", 12),
        ["round 193:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 193: the kernel wakes the worker at dawn", 16), ["round 193: the", "kernel wakes the", "worker at dawn"]),
    (("round 193: the kernel wakes the worker at dawn", 24), ["round 193: the kernel", "wakes the worker at dawn"]),
    (("round 193: the kernel wakes the worker at dawn", 32), ["round 193: the kernel wakes the", "worker at dawn"]),
    (
        ("round 193: service latency drops after the patch", 4),
        ["round", "193:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 193: service latency drops after the patch", 8),
        ["round", "193:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 193: service latency drops after the patch", 12),
        ["round 193:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 193: service latency drops after the patch", 16),
        ["round 193:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 193: service latency drops after the patch", 24),
        ["round 193: service", "latency drops after the", "patch"],
    ),
    (("round 193: service latency drops after the patch", 32), ["round 193: service latency drops", "after the patch"]),
    (
        ("round 193: the library caches every vector it sees", 4),
        ["round", "193:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 193: the library caches every vector it sees", 8),
        ["round", "193: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 193: the library caches every vector it sees", 12),
        ["round 193:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 193: the library caches every vector it sees", 16),
        ["round 193: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 193: the library caches every vector it sees", 24),
        ["round 193: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 193: the library caches every vector it sees", 32),
        ["round 193: the library caches", "every vector it sees"],
    ),
    (
        ("round 193: agents argue then the debate resolves", 4),
        ["round", "193:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 193: agents argue then the debate resolves", 8),
        ["round", "193:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 193: agents argue then the debate resolves", 12),
        ["round 193:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 193: agents argue then the debate resolves", 16),
        ["round 193:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 193: agents argue then the debate resolves", 24), ["round 193: agents argue", "then the debate resolves"]),
    (("round 193: agents argue then the debate resolves", 32), ["round 193: agents argue then the", "debate resolves"]),
    (
        ("round 193: the filter keeps only strong matches", 4),
        ["round", "193:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 193: the filter keeps only strong matches", 8),
        ["round", "193: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 193: the filter keeps only strong matches", 12),
        ["round 193:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 193: the filter keeps only strong matches", 16),
        ["round 193: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 193: the filter keeps only strong matches", 24),
        ["round 193: the filter", "keeps only strong", "matches"],
    ),
    (("round 193: the filter keeps only strong matches", 32), ["round 193: the filter keeps only", "strong matches"]),
    (
        ("round 193: the model answers with a short reply", 4),
        ["round", "193:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 193: the model answers with a short reply", 8),
        ["round", "193: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 193: the model answers with a short reply", 12),
        ["round 193:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 193: the model answers with a short reply", 16),
        ["round 193: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 193: the model answers with a short reply", 24),
        ["round 193: the model", "answers with a short", "reply"],
    ),
    (("round 193: the model answers with a short reply", 32), ["round 193: the model answers", "with a short reply"]),
    (
        ("round 193: the recorder stores the reasoning trace", 4),
        ["round", "193:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 193: the recorder stores the reasoning trace", 8),
        ["round", "193: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 193: the recorder stores the reasoning trace", 12),
        ["round 193:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 193: the recorder stores the reasoning trace", 16),
        ["round 193: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 193: the recorder stores the reasoning trace", 24),
        ["round 193: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 193: the recorder stores the reasoning trace", 32),
        ["round 193: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 193: the angel watches the processor run", 4),
        ["round", "193:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 193: the angel watches the processor run", 8),
        ["round", "193: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 193: the angel watches the processor run", 12),
        ["round 193:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 193: the angel watches the processor run", 16),
        ["round 193: the", "angel watches", "the processor", "run"],
    ),
    (("round 193: the angel watches the processor run", 24), ["round 193: the angel", "watches the processor", "run"]),
    (("round 193: the angel watches the processor run", 32), ["round 193: the angel watches the", "processor run"]),
    (
        ("round 193: angle of the vector decides the match", 4),
        ["round", "193:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 193: angle of the vector decides the match", 8),
        ["round", "193:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 193: angle of the vector decides the match", 12),
        ["round 193:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 193: angle of the vector decides the match", 16),
        ["round 193: angle", "of the vector", "decides the", "match"],
    ),
    (("round 193: angle of the vector decides the match", 24), ["round 193: angle of the", "vector decides the match"]),
    (("round 193: angle of the vector decides the match", 32), ["round 193: angle of the vector", "decides the match"]),
    (
        ("round 193: the candle burns twice as long at night", 4),
        ["round", "193:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 193: the candle burns twice as long at night", 8),
        ["round", "193: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 193: the candle burns twice as long at night", 12),
        ["round 193:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 193: the candle burns twice as long at night", 16),
        ["round 193: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 193: the candle burns twice as long at night", 24),
        ["round 193: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 193: the candle burns twice as long at night", 32),
        ["round 193: the candle burns", "twice as long at night"],
    ),
    (
        ("round 193: a mirror of the universe in one line", 4),
        ["round", "193:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 193: a mirror of the universe in one line", 8),
        ["round", "193: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 193: a mirror of the universe in one line", 12),
        ["round 193: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 193: a mirror of the universe in one line", 16),
        ["round 193: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 193: a mirror of the universe in one line", 24), ["round 193: a mirror of", "the universe in one line"]),
    (("round 193: a mirror of the universe in one line", 32), ["round 193: a mirror of the", "universe in one line"]),
    (
        ("round 193: the queue drains before the storm", 4),
        ["round", "193:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 193: the queue drains before the storm", 8),
        ["round", "193: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 193: the queue drains before the storm", 12),
        ["round 193:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 193: the queue drains before the storm", 16), ["round 193: the", "queue drains", "before the storm"]),
    (("round 193: the queue drains before the storm", 24), ["round 193: the queue", "drains before the storm"]),
    (("round 193: the queue drains before the storm", 32), ["round 193: the queue drains", "before the storm"]),
    (
        ("kitten193 sitting193 agent193 angle193 universe193 memory193", 6),
        ["kitten193", "sitting193", "agent193", "angle193", "universe193", "memory193"],
    ),
    (
        ("kitten193 sitting193 agent193 angle193 universe193 memory193", 10),
        ["kitten193", "sitting193", "agent193", "angle193", "universe193", "memory193"],
    ),
    (
        ("kitten193 sitting193 agent193 angle193 universe193 memory193", 18),
        ["kitten193", "sitting193", "agent193 angle193", "universe193", "memory193"],
    ),
    (
        ("kitten193 sitting193 agent193 angle193 universe193 memory193", 28),
        ["kitten193 sitting193", "agent193 angle193", "universe193 memory193"],
    ),
    (
        ("sitting193 agent193 angle193 universe193 memory193 stream193", 6),
        ["sitting193", "agent193", "angle193", "universe193", "memory193", "stream193"],
    ),
    (
        ("sitting193 agent193 angle193 universe193 memory193 stream193", 10),
        ["sitting193", "agent193", "angle193", "universe193", "memory193", "stream193"],
    ),
    (
        ("sitting193 agent193 angle193 universe193 memory193 stream193", 18),
        ["sitting193", "agent193 angle193", "universe193", "memory193", "stream193"],
    ),
    (
        ("sitting193 agent193 angle193 universe193 memory193 stream193", 28),
        ["sitting193 agent193 angle193", "universe193 memory193", "stream193"],
    ),
    (
        ("agent193 angle193 universe193 memory193 stream193 context193", 6),
        ["agent193", "angle193", "universe193", "memory193", "stream193", "context193"],
    ),
    (
        ("agent193 angle193 universe193 memory193 stream193 context193", 10),
        ["agent193", "angle193", "universe193", "memory193", "stream193", "context193"],
    ),
    (
        ("agent193 angle193 universe193 memory193 stream193 context193", 18),
        ["agent193 angle193", "universe193", "memory193", "stream193", "context193"],
    ),
    (
        ("agent193 angle193 universe193 memory193 stream193 context193", 28),
        ["agent193 angle193", "universe193 memory193", "stream193 context193"],
    ),
    (
        ("angle193 universe193 memory193 stream193 context193 knowledge193", 6),
        ["angle193", "universe193", "memory193", "stream193", "context193", "knowledge193"],
    ),
    (
        ("angle193 universe193 memory193 stream193 context193 knowledge193", 10),
        ["angle193", "universe193", "memory193", "stream193", "context193", "knowledge193"],
    ),
    (
        ("angle193 universe193 memory193 stream193 context193 knowledge193", 18),
        ["angle193", "universe193", "memory193", "stream193", "context193", "knowledge193"],
    ),
    (
        ("angle193 universe193 memory193 stream193 context193 knowledge193", 28),
        ["angle193 universe193", "memory193 stream193", "context193 knowledge193"],
    ),
    (
        ("universe193 memory193 stream193 context193 knowledge193 vector193", 6),
        ["universe193", "memory193", "stream193", "context193", "knowledge193", "vector193"],
    ),
    (
        ("universe193 memory193 stream193 context193 knowledge193 vector193", 10),
        ["universe193", "memory193", "stream193", "context193", "knowledge193", "vector193"],
    ),
    (
        ("universe193 memory193 stream193 context193 knowledge193 vector193", 18),
        ["universe193", "memory193", "stream193", "context193", "knowledge193", "vector193"],
    ),
    (
        ("universe193 memory193 stream193 context193 knowledge193 vector193", 28),
        ["universe193 memory193", "stream193 context193", "knowledge193 vector193"],
    ),
    (
        ("memory193 stream193 context193 knowledge193 vector193 processor193", 6),
        ["memory193", "stream193", "context193", "knowledge193", "vector193", "processor193"],
    ),
    (
        ("memory193 stream193 context193 knowledge193 vector193 processor193", 10),
        ["memory193", "stream193", "context193", "knowledge193", "vector193", "processor193"],
    ),
    (
        ("memory193 stream193 context193 knowledge193 vector193 processor193", 18),
        ["memory193", "stream193", "context193", "knowledge193", "vector193", "processor193"],
    ),
    (
        ("memory193 stream193 context193 knowledge193 vector193 processor193", 28),
        ["memory193 stream193", "context193 knowledge193", "vector193 processor193"],
    ),
    (
        ("stream193 context193 knowledge193 vector193 processor193 reasoning193", 6),
        ["stream193", "context193", "knowledge193", "vector193", "processor193", "reasoning193"],
    ),
    (
        ("stream193 context193 knowledge193 vector193 processor193 reasoning193", 10),
        ["stream193", "context193", "knowledge193", "vector193", "processor193", "reasoning193"],
    ),
    (
        ("stream193 context193 knowledge193 vector193 processor193 reasoning193", 18),
        ["stream193", "context193", "knowledge193", "vector193", "processor193", "reasoning193"],
    ),
    (
        ("stream193 context193 knowledge193 vector193 processor193 reasoning193", 28),
        ["stream193 context193", "knowledge193 vector193", "processor193 reasoning193"],
    ),
    (
        ("context193 knowledge193 vector193 processor193 reasoning193 machine193", 6),
        ["context193", "knowledge193", "vector193", "processor193", "reasoning193", "machine193"],
    ),
    (
        ("context193 knowledge193 vector193 processor193 reasoning193 machine193", 10),
        ["context193", "knowledge193", "vector193", "processor193", "reasoning193", "machine193"],
    ),
    (
        ("context193 knowledge193 vector193 processor193 reasoning193 machine193", 18),
        ["context193", "knowledge193", "vector193", "processor193", "reasoning193", "machine193"],
    ),
    (
        ("context193 knowledge193 vector193 processor193 reasoning193 machine193", 28),
        ["context193 knowledge193", "vector193 processor193", "reasoning193 machine193"],
    ),
    (
        ("knowledge193 vector193 processor193 reasoning193 machine193 learning193", 6),
        ["knowledge193", "vector193", "processor193", "reasoning193", "machine193", "learning193"],
    ),
    (
        ("knowledge193 vector193 processor193 reasoning193 machine193 learning193", 10),
        ["knowledge193", "vector193", "processor193", "reasoning193", "machine193", "learning193"],
    ),
    (
        ("knowledge193 vector193 processor193 reasoning193 machine193 learning193", 18),
        ["knowledge193", "vector193", "processor193", "reasoning193", "machine193", "learning193"],
    ),
    (
        ("knowledge193 vector193 processor193 reasoning193 machine193 learning193", 28),
        ["knowledge193 vector193", "processor193 reasoning193", "machine193 learning193"],
    ),
    (
        ("vector193 processor193 reasoning193 machine193 learning193 model193", 6),
        ["vector193", "processor193", "reasoning193", "machine193", "learning193", "model193"],
    ),
    (
        ("vector193 processor193 reasoning193 machine193 learning193 model193", 10),
        ["vector193", "processor193", "reasoning193", "machine193", "learning193", "model193"],
    ),
    (
        ("vector193 processor193 reasoning193 machine193 learning193 model193", 18),
        ["vector193", "processor193", "reasoning193", "machine193", "learning193", "model193"],
    ),
    (
        ("vector193 processor193 reasoning193 machine193 learning193 model193", 28),
        ["vector193 processor193", "reasoning193 machine193", "learning193 model193"],
    ),
    (
        ("processor193 reasoning193 machine193 learning193 model193 token193", 6),
        ["processor193", "reasoning193", "machine193", "learning193", "model193", "token193"],
    ),
    (
        ("processor193 reasoning193 machine193 learning193 model193 token193", 10),
        ["processor193", "reasoning193", "machine193", "learning193", "model193", "token193"],
    ),
    (
        ("processor193 reasoning193 machine193 learning193 model193 token193", 18),
        ["processor193", "reasoning193", "machine193", "learning193", "model193 token193"],
    ),
    (
        ("processor193 reasoning193 machine193 learning193 model193 token193", 28),
        ["processor193 reasoning193", "machine193 learning193", "model193 token193"],
    ),
    (
        ("reasoning193 machine193 learning193 model193 token193 prompt193", 6),
        ["reasoning193", "machine193", "learning193", "model193", "token193", "prompt193"],
    ),
    (
        ("reasoning193 machine193 learning193 model193 token193 prompt193", 10),
        ["reasoning193", "machine193", "learning193", "model193", "token193", "prompt193"],
    ),
    (
        ("reasoning193 machine193 learning193 model193 token193 prompt193", 18),
        ["reasoning193", "machine193", "learning193", "model193 token193", "prompt193"],
    ),
    (
        ("reasoning193 machine193 learning193 model193 token193 prompt193", 28),
        ["reasoning193 machine193", "learning193 model193", "token193 prompt193"],
    ),
    (
        ("machine193 learning193 model193 token193 prompt193 session193", 6),
        ["machine193", "learning193", "model193", "token193", "prompt193", "session193"],
    ),
    (
        ("machine193 learning193 model193 token193 prompt193 session193", 10),
        ["machine193", "learning193", "model193", "token193", "prompt193", "session193"],
    ),
    (
        ("machine193 learning193 model193 token193 prompt193 session193", 18),
        ["machine193", "learning193", "model193 token193", "prompt193", "session193"],
    ),
    (
        ("machine193 learning193 model193 token193 prompt193 session193", 28),
        ["machine193 learning193", "model193 token193 prompt193", "session193"],
    ),
    (
        ("learning193 model193 token193 prompt193 session193 library193", 6),
        ["learning193", "model193", "token193", "prompt193", "session193", "library193"],
    ),
    (
        ("learning193 model193 token193 prompt193 session193 library193", 10),
        ["learning193", "model193", "token193", "prompt193", "session193", "library193"],
    ),
    (
        ("learning193 model193 token193 prompt193 session193 library193", 18),
        ["learning193", "model193 token193", "prompt193", "session193", "library193"],
    ),
    (
        ("learning193 model193 token193 prompt193 session193 library193", 28),
        ["learning193 model193", "token193 prompt193", "session193 library193"],
    ),
    (
        ("model193 token193 prompt193 session193 library193 service193", 6),
        ["model193", "token193", "prompt193", "session193", "library193", "service193"],
    ),
    (
        ("model193 token193 prompt193 session193 library193 service193", 10),
        ["model193", "token193", "prompt193", "session193", "library193", "service193"],
    ),
    (
        ("model193 token193 prompt193 session193 library193 service193", 18),
        ["model193 token193", "prompt193", "session193", "library193", "service193"],
    ),
    (
        ("model193 token193 prompt193 session193 library193 service193", 28),
        ["model193 token193 prompt193", "session193 library193", "service193"],
    ),
    (
        ("token193 prompt193 session193 library193 service193 gateway193", 6),
        ["token193", "prompt193", "session193", "library193", "service193", "gateway193"],
    ),
    (
        ("token193 prompt193 session193 library193 service193 gateway193", 10),
        ["token193", "prompt193", "session193", "library193", "service193", "gateway193"],
    ),
    (
        ("token193 prompt193 session193 library193 service193 gateway193", 18),
        ["token193 prompt193", "session193", "library193", "service193", "gateway193"],
    ),
    (
        ("token193 prompt193 session193 library193 service193 gateway193", 28),
        ["token193 prompt193", "session193 library193", "service193 gateway193"],
    ),
    (
        ("prompt193 session193 library193 service193 gateway193 storage193", 6),
        ["prompt193", "session193", "library193", "service193", "gateway193", "storage193"],
    ),
    (
        ("prompt193 session193 library193 service193 gateway193 storage193", 10),
        ["prompt193", "session193", "library193", "service193", "gateway193", "storage193"],
    ),
    (
        ("prompt193 session193 library193 service193 gateway193 storage193", 18),
        ["prompt193", "session193", "library193", "service193", "gateway193", "storage193"],
    ),
    (
        ("prompt193 session193 library193 service193 gateway193 storage193", 28),
        ["prompt193 session193", "library193 service193", "gateway193 storage193"],
    ),
    (
        ("session193 library193 service193 gateway193 storage193 network193", 6),
        ["session193", "library193", "service193", "gateway193", "storage193", "network193"],
    ),
    (
        ("session193 library193 service193 gateway193 storage193 network193", 10),
        ["session193", "library193", "service193", "gateway193", "storage193", "network193"],
    ),
    (
        ("session193 library193 service193 gateway193 storage193 network193", 18),
        ["session193", "library193", "service193", "gateway193", "storage193", "network193"],
    ),
    (
        ("session193 library193 service193 gateway193 storage193 network193", 28),
        ["session193 library193", "service193 gateway193", "storage193 network193"],
    ),
    (
        ("library193 service193 gateway193 storage193 network193 latency193", 6),
        ["library193", "service193", "gateway193", "storage193", "network193", "latency193"],
    ),
    (
        ("library193 service193 gateway193 storage193 network193 latency193", 10),
        ["library193", "service193", "gateway193", "storage193", "network193", "latency193"],
    ),
    (
        ("library193 service193 gateway193 storage193 network193 latency193", 18),
        ["library193", "service193", "gateway193", "storage193", "network193", "latency193"],
    ),
    (
        ("library193 service193 gateway193 storage193 network193 latency193", 28),
        ["library193 service193", "gateway193 storage193", "network193 latency193"],
    ),
    (
        ("service193 gateway193 storage193 network193 latency193 buffer193", 6),
        ["service193", "gateway193", "storage193", "network193", "latency193", "buffer193"],
    ),
    (
        ("service193 gateway193 storage193 network193 latency193 buffer193", 10),
        ["service193", "gateway193", "storage193", "network193", "latency193", "buffer193"],
    ),
    (
        ("service193 gateway193 storage193 network193 latency193 buffer193", 18),
        ["service193", "gateway193", "storage193", "network193", "latency193", "buffer193"],
    ),
    (
        ("service193 gateway193 storage193 network193 latency193 buffer193", 28),
        ["service193 gateway193", "storage193 network193", "latency193 buffer193"],
    ),
    (
        ("gateway193 storage193 network193 latency193 buffer193 queue193", 6),
        ["gateway193", "storage193", "network193", "latency193", "buffer193", "queue193"],
    ),
    (
        ("gateway193 storage193 network193 latency193 buffer193 queue193", 10),
        ["gateway193", "storage193", "network193", "latency193", "buffer193", "queue193"],
    ),
    (
        ("gateway193 storage193 network193 latency193 buffer193 queue193", 18),
        ["gateway193", "storage193", "network193", "latency193", "buffer193 queue193"],
    ),
    (
        ("gateway193 storage193 network193 latency193 buffer193 queue193", 28),
        ["gateway193 storage193", "network193 latency193", "buffer193 queue193"],
    ),
    (
        ("storage193 network193 latency193 buffer193 queue193 worker193", 6),
        ["storage193", "network193", "latency193", "buffer193", "queue193", "worker193"],
    ),
    (
        ("storage193 network193 latency193 buffer193 queue193 worker193", 10),
        ["storage193", "network193", "latency193", "buffer193", "queue193", "worker193"],
    ),
    (
        ("storage193 network193 latency193 buffer193 queue193 worker193", 18),
        ["storage193", "network193", "latency193", "buffer193 queue193", "worker193"],
    ),
    (
        ("storage193 network193 latency193 buffer193 queue193 worker193", 28),
        ["storage193 network193", "latency193 buffer193", "queue193 worker193"],
    ),
    (
        ("network193 latency193 buffer193 queue193 worker193 kernel193", 6),
        ["network193", "latency193", "buffer193", "queue193", "worker193", "kernel193"],
    ),
    (
        ("network193 latency193 buffer193 queue193 worker193 kernel193", 10),
        ["network193", "latency193", "buffer193", "queue193", "worker193", "kernel193"],
    ),
    (
        ("network193 latency193 buffer193 queue193 worker193 kernel193", 18),
        ["network193", "latency193", "buffer193 queue193", "worker193", "kernel193"],
    ),
    (
        ("network193 latency193 buffer193 queue193 worker193 kernel193", 28),
        ["network193 latency193", "buffer193 queue193 worker193", "kernel193"],
    ),
    (
        ("latency193 buffer193 queue193 worker193 kernel193 signal193", 6),
        ["latency193", "buffer193", "queue193", "worker193", "kernel193", "signal193"],
    ),
    (
        ("latency193 buffer193 queue193 worker193 kernel193 signal193", 10),
        ["latency193", "buffer193", "queue193", "worker193", "kernel193", "signal193"],
    ),
    (
        ("latency193 buffer193 queue193 worker193 kernel193 signal193", 18),
        ["latency193", "buffer193 queue193", "worker193", "kernel193", "signal193"],
    ),
    (
        ("latency193 buffer193 queue193 worker193 kernel193 signal193", 28),
        ["latency193 buffer193", "queue193 worker193 kernel193", "signal193"],
    ),
    (
        ("buffer193 queue193 worker193 kernel193 signal193 packet193", 6),
        ["buffer193", "queue193", "worker193", "kernel193", "signal193", "packet193"],
    ),
    (
        ("buffer193 queue193 worker193 kernel193 signal193 packet193", 10),
        ["buffer193", "queue193", "worker193", "kernel193", "signal193", "packet193"],
    ),
    (
        ("buffer193 queue193 worker193 kernel193 signal193 packet193", 18),
        ["buffer193 queue193", "worker193", "kernel193", "signal193", "packet193"],
    ),
    (
        ("buffer193 queue193 worker193 kernel193 signal193 packet193", 28),
        ["buffer193 queue193 worker193", "kernel193 signal193", "packet193"],
    ),
    (
        ("queue193 worker193 kernel193 signal193 packet193 router193", 6),
        ["queue193", "worker193", "kernel193", "signal193", "packet193", "router193"],
    ),
    (
        ("queue193 worker193 kernel193 signal193 packet193 router193", 10),
        ["queue193", "worker193", "kernel193", "signal193", "packet193", "router193"],
    ),
    (
        ("queue193 worker193 kernel193 signal193 packet193 router193", 18),
        ["queue193 worker193", "kernel193", "signal193", "packet193", "router193"],
    ),
    (
        ("queue193 worker193 kernel193 signal193 packet193 router193", 28),
        ["queue193 worker193 kernel193", "signal193 packet193", "router193"],
    ),
    (
        ("worker193 kernel193 signal193 packet193 router193 cluster193", 6),
        ["worker193", "kernel193", "signal193", "packet193", "router193", "cluster193"],
    ),
    (
        ("worker193 kernel193 signal193 packet193 router193 cluster193", 10),
        ["worker193", "kernel193", "signal193", "packet193", "router193", "cluster193"],
    ),
    (
        ("worker193 kernel193 signal193 packet193 router193 cluster193", 18),
        ["worker193", "kernel193", "signal193", "packet193", "router193", "cluster193"],
    ),
    (
        ("worker193 kernel193 signal193 packet193 router193 cluster193", 28),
        ["worker193 kernel193", "signal193 packet193", "router193 cluster193"],
    ),
    (
        ("kernel193 signal193 packet193 router193 cluster193 mirror193", 6),
        ["kernel193", "signal193", "packet193", "router193", "cluster193", "mirror193"],
    ),
    (
        ("kernel193 signal193 packet193 router193 cluster193 mirror193", 10),
        ["kernel193", "signal193", "packet193", "router193", "cluster193", "mirror193"],
    ),
    (
        ("kernel193 signal193 packet193 router193 cluster193 mirror193", 18),
        ["kernel193", "signal193", "packet193", "router193", "cluster193", "mirror193"],
    ),
    (
        ("kernel193 signal193 packet193 router193 cluster193 mirror193", 28),
        ["kernel193 signal193", "packet193 router193", "cluster193 mirror193"],
    ),
    (
        ("signal193 packet193 router193 cluster193 mirror193 filter193", 6),
        ["signal193", "packet193", "router193", "cluster193", "mirror193", "filter193"],
    ),
    (
        ("signal193 packet193 router193 cluster193 mirror193 filter193", 10),
        ["signal193", "packet193", "router193", "cluster193", "mirror193", "filter193"],
    ),
    (
        ("signal193 packet193 router193 cluster193 mirror193 filter193", 18),
        ["signal193", "packet193", "router193", "cluster193", "mirror193", "filter193"],
    ),
    (
        ("signal193 packet193 router193 cluster193 mirror193 filter193", 28),
        ["signal193 packet193", "router193 cluster193", "mirror193 filter193"],
    ),
    (
        ("packet193 router193 cluster193 mirror193 filter193 ranking193", 6),
        ["packet193", "router193", "cluster193", "mirror193", "filter193", "ranking193"],
    ),
    (
        ("packet193 router193 cluster193 mirror193 filter193 ranking193", 10),
        ["packet193", "router193", "cluster193", "mirror193", "filter193", "ranking193"],
    ),
    (
        ("packet193 router193 cluster193 mirror193 filter193 ranking193", 18),
        ["packet193", "router193", "cluster193", "mirror193", "filter193", "ranking193"],
    ),
    (
        ("packet193 router193 cluster193 mirror193 filter193 ranking193", 28),
        ["packet193 router193", "cluster193 mirror193", "filter193 ranking193"],
    ),
    (
        ("router193 cluster193 mirror193 filter193 ranking193 encoding193", 6),
        ["router193", "cluster193", "mirror193", "filter193", "ranking193", "encoding193"],
    ),
    (
        ("router193 cluster193 mirror193 filter193 ranking193 encoding193", 10),
        ["router193", "cluster193", "mirror193", "filter193", "ranking193", "encoding193"],
    ),
    (
        ("router193 cluster193 mirror193 filter193 ranking193 encoding193", 18),
        ["router193", "cluster193", "mirror193", "filter193", "ranking193", "encoding193"],
    ),
    (
        ("router193 cluster193 mirror193 filter193 ranking193 encoding193", 28),
        ["router193 cluster193", "mirror193 filter193", "ranking193 encoding193"],
    ),
    (
        ("cluster193 mirror193 filter193 ranking193 encoding193 mapping193", 6),
        ["cluster193", "mirror193", "filter193", "ranking193", "encoding193", "mapping193"],
    ),
    (
        ("cluster193 mirror193 filter193 ranking193 encoding193 mapping193", 10),
        ["cluster193", "mirror193", "filter193", "ranking193", "encoding193", "mapping193"],
    ),
    (
        ("cluster193 mirror193 filter193 ranking193 encoding193 mapping193", 18),
        ["cluster193", "mirror193", "filter193", "ranking193", "encoding193", "mapping193"],
    ),
    (
        ("cluster193 mirror193 filter193 ranking193 encoding193 mapping193", 28),
        ["cluster193 mirror193", "filter193 ranking193", "encoding193 mapping193"],
    ),
    (
        ("mirror193 filter193 ranking193 encoding193 mapping193 record193", 6),
        ["mirror193", "filter193", "ranking193", "encoding193", "mapping193", "record193"],
    ),
    (
        ("mirror193 filter193 ranking193 encoding193 mapping193 record193", 10),
        ["mirror193", "filter193", "ranking193", "encoding193", "mapping193", "record193"],
    ),
    (
        ("mirror193 filter193 ranking193 encoding193 mapping193 record193", 18),
        ["mirror193", "filter193", "ranking193", "encoding193", "mapping193", "record193"],
    ),
    (
        ("mirror193 filter193 ranking193 encoding193 mapping193 record193", 28),
        ["mirror193 filter193", "ranking193 encoding193", "mapping193 record193"],
    ),
    (
        ("filter193 ranking193 encoding193 mapping193 record193 candle193", 6),
        ["filter193", "ranking193", "encoding193", "mapping193", "record193", "candle193"],
    ),
    (
        ("filter193 ranking193 encoding193 mapping193 record193 candle193", 10),
        ["filter193", "ranking193", "encoding193", "mapping193", "record193", "candle193"],
    ),
    (
        ("filter193 ranking193 encoding193 mapping193 record193 candle193", 18),
        ["filter193", "ranking193", "encoding193", "mapping193", "record193", "candle193"],
    ),
    (
        ("filter193 ranking193 encoding193 mapping193 record193 candle193", 28),
        ["filter193 ranking193", "encoding193 mapping193", "record193 candle193"],
    ),
    (
        ("ranking193 encoding193 mapping193 record193 candle193 thread193", 6),
        ["ranking193", "encoding193", "mapping193", "record193", "candle193", "thread193"],
    ),
    (
        ("ranking193 encoding193 mapping193 record193 candle193 thread193", 10),
        ["ranking193", "encoding193", "mapping193", "record193", "candle193", "thread193"],
    ),
    (
        ("ranking193 encoding193 mapping193 record193 candle193 thread193", 18),
        ["ranking193", "encoding193", "mapping193", "record193", "candle193", "thread193"],
    ),
    (
        ("ranking193 encoding193 mapping193 record193 candle193 thread193", 28),
        ["ranking193 encoding193", "mapping193 record193", "candle193 thread193"],
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
