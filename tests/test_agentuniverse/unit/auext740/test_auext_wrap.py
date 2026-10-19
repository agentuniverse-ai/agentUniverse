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
        ("round 740: the quick brown fox jumps over the lazy dog", 4),
        ["round", "740:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 740: the quick brown fox jumps over the lazy dog", 8),
        ["round", "740: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 740: the quick brown fox jumps over the lazy dog", 12),
        ["round 740:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 740: the quick brown fox jumps over the lazy dog", 16),
        ["round 740: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 740: the quick brown fox jumps over the lazy dog", 24),
        ["round 740: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 740: the quick brown fox jumps over the lazy dog", 32),
        ["round 740: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 740: agentuniverse is a framework for multi agents", 4),
        ["round", "740:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 740: agentuniverse is a framework for multi agents", 8),
        ["round", "740:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 740: agentuniverse is a framework for multi agents", 12),
        ["round 740:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 740: agentuniverse is a framework for multi agents", 16),
        ["round 740:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 740: agentuniverse is a framework for multi agents", 24),
        ["round 740: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 740: agentuniverse is a framework for multi agents", 32),
        ["round 740: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 740: knowledge stored as vectors enables retrieval", 4),
        ["round", "740:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 740: knowledge stored as vectors enables retrieval", 8),
        ["round", "740:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 740: knowledge stored as vectors enables retrieval", 12),
        ["round 740:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 740: knowledge stored as vectors enables retrieval", 16),
        ["round 740:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 740: knowledge stored as vectors enables retrieval", 24),
        ["round 740: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 740: knowledge stored as vectors enables retrieval", 32),
        ["round 740: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 740: the processor reads the record then stops", 4),
        ["round", "740:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 740: the processor reads the record then stops", 8),
        ["round", "740: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 740: the processor reads the record then stops", 12),
        ["round 740:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 740: the processor reads the record then stops", 16),
        ["round 740: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 740: the processor reads the record then stops", 24),
        ["round 740: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 740: the processor reads the record then stops", 32),
        ["round 740: the processor reads", "the record then stops"],
    ),
    (
        ("round 740: a worker pulls the next task from the queue", 4),
        ["round", "740:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 740: a worker pulls the next task from the queue", 8),
        ["round", "740: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 740: a worker pulls the next task from the queue", 12),
        ["round 740: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 740: a worker pulls the next task from the queue", 16),
        ["round 740: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 740: a worker pulls the next task from the queue", 24),
        ["round 740: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 740: a worker pulls the next task from the queue", 32),
        ["round 740: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 740: signals travel through the network layer", 4),
        ["round", "740:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 740: signals travel through the network layer", 8),
        ["round", "740:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 740: signals travel through the network layer", 12),
        ["round 740:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 740: signals travel through the network layer", 16),
        ["round 740:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 740: signals travel through the network layer", 24),
        ["round 740: signals", "travel through the", "network layer"],
    ),
    (
        ("round 740: signals travel through the network layer", 32),
        ["round 740: signals travel", "through the network layer"],
    ),
    (
        ("round 740: the gateway routes each request by policy", 4),
        ["round", "740:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 740: the gateway routes each request by policy", 8),
        ["round", "740: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 740: the gateway routes each request by policy", 12),
        ["round 740:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 740: the gateway routes each request by policy", 16),
        ["round 740: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 740: the gateway routes each request by policy", 24),
        ["round 740: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 740: the gateway routes each request by policy", 32),
        ["round 740: the gateway routes", "each request by policy"],
    ),
    (
        ("round 740: memory grows until the buffer is full", 4),
        ["round", "740:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 740: memory grows until the buffer is full", 8),
        ["round", "740:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 740: memory grows until the buffer is full", 12),
        ["round 740:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 740: memory grows until the buffer is full", 16),
        ["round 740:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 740: memory grows until the buffer is full", 24), ["round 740: memory grows", "until the buffer is full"]),
    (("round 740: memory grows until the buffer is full", 32), ["round 740: memory grows until", "the buffer is full"]),
    (
        ("round 740: the cluster mirrors every packet twice", 4),
        ["round", "740:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 740: the cluster mirrors every packet twice", 8),
        ["round", "740: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 740: the cluster mirrors every packet twice", 12),
        ["round 740:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 740: the cluster mirrors every packet twice", 16),
        ["round 740: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 740: the cluster mirrors every packet twice", 24),
        ["round 740: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 740: the cluster mirrors every packet twice", 32),
        ["round 740: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 740: ranking uses tokens learned from the corpus", 4),
        ["round", "740:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 740: ranking uses tokens learned from the corpus", 8),
        ["round", "740:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 740: ranking uses tokens learned from the corpus", 12),
        ["round 740:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 740: ranking uses tokens learned from the corpus", 16),
        ["round 740:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 740: ranking uses tokens learned from the corpus", 24),
        ["round 740: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 740: ranking uses tokens learned from the corpus", 32),
        ["round 740: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 740: a long session ends when the candle dies", 4),
        ["round", "740:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 740: a long session ends when the candle dies", 8),
        ["round", "740: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 740: a long session ends when the candle dies", 12),
        ["round 740: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 740: a long session ends when the candle dies", 16),
        ["round 740: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 740: a long session ends when the candle dies", 24),
        ["round 740: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 740: a long session ends when the candle dies", 32),
        ["round 740: a long session ends", "when the candle dies"],
    ),
    (
        ("round 740: encode the prompt then map the result", 4),
        ["round", "740:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 740: encode the prompt then map the result", 8),
        ["round", "740:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 740: encode the prompt then map the result", 12),
        ["round 740:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 740: encode the prompt then map the result", 16),
        ["round 740:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 740: encode the prompt then map the result", 24),
        ["round 740: encode the", "prompt then map the", "result"],
    ),
    (("round 740: encode the prompt then map the result", 32), ["round 740: encode the prompt", "then map the result"]),
    (
        ("round 740: the kernel wakes the worker at dawn", 4),
        ["round", "740:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 740: the kernel wakes the worker at dawn", 8),
        ["round", "740: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 740: the kernel wakes the worker at dawn", 12),
        ["round 740:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 740: the kernel wakes the worker at dawn", 16), ["round 740: the", "kernel wakes the", "worker at dawn"]),
    (("round 740: the kernel wakes the worker at dawn", 24), ["round 740: the kernel", "wakes the worker at dawn"]),
    (("round 740: the kernel wakes the worker at dawn", 32), ["round 740: the kernel wakes the", "worker at dawn"]),
    (
        ("round 740: service latency drops after the patch", 4),
        ["round", "740:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 740: service latency drops after the patch", 8),
        ["round", "740:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 740: service latency drops after the patch", 12),
        ["round 740:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 740: service latency drops after the patch", 16),
        ["round 740:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 740: service latency drops after the patch", 24),
        ["round 740: service", "latency drops after the", "patch"],
    ),
    (("round 740: service latency drops after the patch", 32), ["round 740: service latency drops", "after the patch"]),
    (
        ("round 740: the library caches every vector it sees", 4),
        ["round", "740:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 740: the library caches every vector it sees", 8),
        ["round", "740: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 740: the library caches every vector it sees", 12),
        ["round 740:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 740: the library caches every vector it sees", 16),
        ["round 740: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 740: the library caches every vector it sees", 24),
        ["round 740: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 740: the library caches every vector it sees", 32),
        ["round 740: the library caches", "every vector it sees"],
    ),
    (
        ("round 740: agents argue then the debate resolves", 4),
        ["round", "740:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 740: agents argue then the debate resolves", 8),
        ["round", "740:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 740: agents argue then the debate resolves", 12),
        ["round 740:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 740: agents argue then the debate resolves", 16),
        ["round 740:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 740: agents argue then the debate resolves", 24), ["round 740: agents argue", "then the debate resolves"]),
    (("round 740: agents argue then the debate resolves", 32), ["round 740: agents argue then the", "debate resolves"]),
    (
        ("round 740: the filter keeps only strong matches", 4),
        ["round", "740:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 740: the filter keeps only strong matches", 8),
        ["round", "740: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 740: the filter keeps only strong matches", 12),
        ["round 740:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 740: the filter keeps only strong matches", 16),
        ["round 740: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 740: the filter keeps only strong matches", 24),
        ["round 740: the filter", "keeps only strong", "matches"],
    ),
    (("round 740: the filter keeps only strong matches", 32), ["round 740: the filter keeps only", "strong matches"]),
    (
        ("round 740: the model answers with a short reply", 4),
        ["round", "740:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 740: the model answers with a short reply", 8),
        ["round", "740: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 740: the model answers with a short reply", 12),
        ["round 740:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 740: the model answers with a short reply", 16),
        ["round 740: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 740: the model answers with a short reply", 24),
        ["round 740: the model", "answers with a short", "reply"],
    ),
    (("round 740: the model answers with a short reply", 32), ["round 740: the model answers", "with a short reply"]),
    (
        ("round 740: the recorder stores the reasoning trace", 4),
        ["round", "740:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 740: the recorder stores the reasoning trace", 8),
        ["round", "740: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 740: the recorder stores the reasoning trace", 12),
        ["round 740:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 740: the recorder stores the reasoning trace", 16),
        ["round 740: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 740: the recorder stores the reasoning trace", 24),
        ["round 740: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 740: the recorder stores the reasoning trace", 32),
        ["round 740: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 740: the angel watches the processor run", 4),
        ["round", "740:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 740: the angel watches the processor run", 8),
        ["round", "740: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 740: the angel watches the processor run", 12),
        ["round 740:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 740: the angel watches the processor run", 16),
        ["round 740: the", "angel watches", "the processor", "run"],
    ),
    (("round 740: the angel watches the processor run", 24), ["round 740: the angel", "watches the processor", "run"]),
    (("round 740: the angel watches the processor run", 32), ["round 740: the angel watches the", "processor run"]),
    (
        ("round 740: angle of the vector decides the match", 4),
        ["round", "740:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 740: angle of the vector decides the match", 8),
        ["round", "740:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 740: angle of the vector decides the match", 12),
        ["round 740:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 740: angle of the vector decides the match", 16),
        ["round 740: angle", "of the vector", "decides the", "match"],
    ),
    (("round 740: angle of the vector decides the match", 24), ["round 740: angle of the", "vector decides the match"]),
    (("round 740: angle of the vector decides the match", 32), ["round 740: angle of the vector", "decides the match"]),
    (
        ("round 740: the candle burns twice as long at night", 4),
        ["round", "740:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 740: the candle burns twice as long at night", 8),
        ["round", "740: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 740: the candle burns twice as long at night", 12),
        ["round 740:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 740: the candle burns twice as long at night", 16),
        ["round 740: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 740: the candle burns twice as long at night", 24),
        ["round 740: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 740: the candle burns twice as long at night", 32),
        ["round 740: the candle burns", "twice as long at night"],
    ),
    (
        ("round 740: a mirror of the universe in one line", 4),
        ["round", "740:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 740: a mirror of the universe in one line", 8),
        ["round", "740: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 740: a mirror of the universe in one line", 12),
        ["round 740: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 740: a mirror of the universe in one line", 16),
        ["round 740: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 740: a mirror of the universe in one line", 24), ["round 740: a mirror of", "the universe in one line"]),
    (("round 740: a mirror of the universe in one line", 32), ["round 740: a mirror of the", "universe in one line"]),
    (
        ("round 740: the queue drains before the storm", 4),
        ["round", "740:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 740: the queue drains before the storm", 8),
        ["round", "740: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 740: the queue drains before the storm", 12),
        ["round 740:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 740: the queue drains before the storm", 16), ["round 740: the", "queue drains", "before the storm"]),
    (("round 740: the queue drains before the storm", 24), ["round 740: the queue", "drains before the storm"]),
    (("round 740: the queue drains before the storm", 32), ["round 740: the queue drains", "before the storm"]),
    (
        ("kitten740 sitting740 agent740 angle740 universe740 memory740", 6),
        ["kitten740", "sitting740", "agent740", "angle740", "universe740", "memory740"],
    ),
    (
        ("kitten740 sitting740 agent740 angle740 universe740 memory740", 10),
        ["kitten740", "sitting740", "agent740", "angle740", "universe740", "memory740"],
    ),
    (
        ("kitten740 sitting740 agent740 angle740 universe740 memory740", 18),
        ["kitten740", "sitting740", "agent740 angle740", "universe740", "memory740"],
    ),
    (
        ("kitten740 sitting740 agent740 angle740 universe740 memory740", 28),
        ["kitten740 sitting740", "agent740 angle740", "universe740 memory740"],
    ),
    (
        ("sitting740 agent740 angle740 universe740 memory740 stream740", 6),
        ["sitting740", "agent740", "angle740", "universe740", "memory740", "stream740"],
    ),
    (
        ("sitting740 agent740 angle740 universe740 memory740 stream740", 10),
        ["sitting740", "agent740", "angle740", "universe740", "memory740", "stream740"],
    ),
    (
        ("sitting740 agent740 angle740 universe740 memory740 stream740", 18),
        ["sitting740", "agent740 angle740", "universe740", "memory740", "stream740"],
    ),
    (
        ("sitting740 agent740 angle740 universe740 memory740 stream740", 28),
        ["sitting740 agent740 angle740", "universe740 memory740", "stream740"],
    ),
    (
        ("agent740 angle740 universe740 memory740 stream740 context740", 6),
        ["agent740", "angle740", "universe740", "memory740", "stream740", "context740"],
    ),
    (
        ("agent740 angle740 universe740 memory740 stream740 context740", 10),
        ["agent740", "angle740", "universe740", "memory740", "stream740", "context740"],
    ),
    (
        ("agent740 angle740 universe740 memory740 stream740 context740", 18),
        ["agent740 angle740", "universe740", "memory740", "stream740", "context740"],
    ),
    (
        ("agent740 angle740 universe740 memory740 stream740 context740", 28),
        ["agent740 angle740", "universe740 memory740", "stream740 context740"],
    ),
    (
        ("angle740 universe740 memory740 stream740 context740 knowledge740", 6),
        ["angle740", "universe740", "memory740", "stream740", "context740", "knowledge740"],
    ),
    (
        ("angle740 universe740 memory740 stream740 context740 knowledge740", 10),
        ["angle740", "universe740", "memory740", "stream740", "context740", "knowledge740"],
    ),
    (
        ("angle740 universe740 memory740 stream740 context740 knowledge740", 18),
        ["angle740", "universe740", "memory740", "stream740", "context740", "knowledge740"],
    ),
    (
        ("angle740 universe740 memory740 stream740 context740 knowledge740", 28),
        ["angle740 universe740", "memory740 stream740", "context740 knowledge740"],
    ),
    (
        ("universe740 memory740 stream740 context740 knowledge740 vector740", 6),
        ["universe740", "memory740", "stream740", "context740", "knowledge740", "vector740"],
    ),
    (
        ("universe740 memory740 stream740 context740 knowledge740 vector740", 10),
        ["universe740", "memory740", "stream740", "context740", "knowledge740", "vector740"],
    ),
    (
        ("universe740 memory740 stream740 context740 knowledge740 vector740", 18),
        ["universe740", "memory740", "stream740", "context740", "knowledge740", "vector740"],
    ),
    (
        ("universe740 memory740 stream740 context740 knowledge740 vector740", 28),
        ["universe740 memory740", "stream740 context740", "knowledge740 vector740"],
    ),
    (
        ("memory740 stream740 context740 knowledge740 vector740 processor740", 6),
        ["memory740", "stream740", "context740", "knowledge740", "vector740", "processor740"],
    ),
    (
        ("memory740 stream740 context740 knowledge740 vector740 processor740", 10),
        ["memory740", "stream740", "context740", "knowledge740", "vector740", "processor740"],
    ),
    (
        ("memory740 stream740 context740 knowledge740 vector740 processor740", 18),
        ["memory740", "stream740", "context740", "knowledge740", "vector740", "processor740"],
    ),
    (
        ("memory740 stream740 context740 knowledge740 vector740 processor740", 28),
        ["memory740 stream740", "context740 knowledge740", "vector740 processor740"],
    ),
    (
        ("stream740 context740 knowledge740 vector740 processor740 reasoning740", 6),
        ["stream740", "context740", "knowledge740", "vector740", "processor740", "reasoning740"],
    ),
    (
        ("stream740 context740 knowledge740 vector740 processor740 reasoning740", 10),
        ["stream740", "context740", "knowledge740", "vector740", "processor740", "reasoning740"],
    ),
    (
        ("stream740 context740 knowledge740 vector740 processor740 reasoning740", 18),
        ["stream740", "context740", "knowledge740", "vector740", "processor740", "reasoning740"],
    ),
    (
        ("stream740 context740 knowledge740 vector740 processor740 reasoning740", 28),
        ["stream740 context740", "knowledge740 vector740", "processor740 reasoning740"],
    ),
    (
        ("context740 knowledge740 vector740 processor740 reasoning740 machine740", 6),
        ["context740", "knowledge740", "vector740", "processor740", "reasoning740", "machine740"],
    ),
    (
        ("context740 knowledge740 vector740 processor740 reasoning740 machine740", 10),
        ["context740", "knowledge740", "vector740", "processor740", "reasoning740", "machine740"],
    ),
    (
        ("context740 knowledge740 vector740 processor740 reasoning740 machine740", 18),
        ["context740", "knowledge740", "vector740", "processor740", "reasoning740", "machine740"],
    ),
    (
        ("context740 knowledge740 vector740 processor740 reasoning740 machine740", 28),
        ["context740 knowledge740", "vector740 processor740", "reasoning740 machine740"],
    ),
    (
        ("knowledge740 vector740 processor740 reasoning740 machine740 learning740", 6),
        ["knowledge740", "vector740", "processor740", "reasoning740", "machine740", "learning740"],
    ),
    (
        ("knowledge740 vector740 processor740 reasoning740 machine740 learning740", 10),
        ["knowledge740", "vector740", "processor740", "reasoning740", "machine740", "learning740"],
    ),
    (
        ("knowledge740 vector740 processor740 reasoning740 machine740 learning740", 18),
        ["knowledge740", "vector740", "processor740", "reasoning740", "machine740", "learning740"],
    ),
    (
        ("knowledge740 vector740 processor740 reasoning740 machine740 learning740", 28),
        ["knowledge740 vector740", "processor740 reasoning740", "machine740 learning740"],
    ),
    (
        ("vector740 processor740 reasoning740 machine740 learning740 model740", 6),
        ["vector740", "processor740", "reasoning740", "machine740", "learning740", "model740"],
    ),
    (
        ("vector740 processor740 reasoning740 machine740 learning740 model740", 10),
        ["vector740", "processor740", "reasoning740", "machine740", "learning740", "model740"],
    ),
    (
        ("vector740 processor740 reasoning740 machine740 learning740 model740", 18),
        ["vector740", "processor740", "reasoning740", "machine740", "learning740", "model740"],
    ),
    (
        ("vector740 processor740 reasoning740 machine740 learning740 model740", 28),
        ["vector740 processor740", "reasoning740 machine740", "learning740 model740"],
    ),
    (
        ("processor740 reasoning740 machine740 learning740 model740 token740", 6),
        ["processor740", "reasoning740", "machine740", "learning740", "model740", "token740"],
    ),
    (
        ("processor740 reasoning740 machine740 learning740 model740 token740", 10),
        ["processor740", "reasoning740", "machine740", "learning740", "model740", "token740"],
    ),
    (
        ("processor740 reasoning740 machine740 learning740 model740 token740", 18),
        ["processor740", "reasoning740", "machine740", "learning740", "model740 token740"],
    ),
    (
        ("processor740 reasoning740 machine740 learning740 model740 token740", 28),
        ["processor740 reasoning740", "machine740 learning740", "model740 token740"],
    ),
    (
        ("reasoning740 machine740 learning740 model740 token740 prompt740", 6),
        ["reasoning740", "machine740", "learning740", "model740", "token740", "prompt740"],
    ),
    (
        ("reasoning740 machine740 learning740 model740 token740 prompt740", 10),
        ["reasoning740", "machine740", "learning740", "model740", "token740", "prompt740"],
    ),
    (
        ("reasoning740 machine740 learning740 model740 token740 prompt740", 18),
        ["reasoning740", "machine740", "learning740", "model740 token740", "prompt740"],
    ),
    (
        ("reasoning740 machine740 learning740 model740 token740 prompt740", 28),
        ["reasoning740 machine740", "learning740 model740", "token740 prompt740"],
    ),
    (
        ("machine740 learning740 model740 token740 prompt740 session740", 6),
        ["machine740", "learning740", "model740", "token740", "prompt740", "session740"],
    ),
    (
        ("machine740 learning740 model740 token740 prompt740 session740", 10),
        ["machine740", "learning740", "model740", "token740", "prompt740", "session740"],
    ),
    (
        ("machine740 learning740 model740 token740 prompt740 session740", 18),
        ["machine740", "learning740", "model740 token740", "prompt740", "session740"],
    ),
    (
        ("machine740 learning740 model740 token740 prompt740 session740", 28),
        ["machine740 learning740", "model740 token740 prompt740", "session740"],
    ),
    (
        ("learning740 model740 token740 prompt740 session740 library740", 6),
        ["learning740", "model740", "token740", "prompt740", "session740", "library740"],
    ),
    (
        ("learning740 model740 token740 prompt740 session740 library740", 10),
        ["learning740", "model740", "token740", "prompt740", "session740", "library740"],
    ),
    (
        ("learning740 model740 token740 prompt740 session740 library740", 18),
        ["learning740", "model740 token740", "prompt740", "session740", "library740"],
    ),
    (
        ("learning740 model740 token740 prompt740 session740 library740", 28),
        ["learning740 model740", "token740 prompt740", "session740 library740"],
    ),
    (
        ("model740 token740 prompt740 session740 library740 service740", 6),
        ["model740", "token740", "prompt740", "session740", "library740", "service740"],
    ),
    (
        ("model740 token740 prompt740 session740 library740 service740", 10),
        ["model740", "token740", "prompt740", "session740", "library740", "service740"],
    ),
    (
        ("model740 token740 prompt740 session740 library740 service740", 18),
        ["model740 token740", "prompt740", "session740", "library740", "service740"],
    ),
    (
        ("model740 token740 prompt740 session740 library740 service740", 28),
        ["model740 token740 prompt740", "session740 library740", "service740"],
    ),
    (
        ("token740 prompt740 session740 library740 service740 gateway740", 6),
        ["token740", "prompt740", "session740", "library740", "service740", "gateway740"],
    ),
    (
        ("token740 prompt740 session740 library740 service740 gateway740", 10),
        ["token740", "prompt740", "session740", "library740", "service740", "gateway740"],
    ),
    (
        ("token740 prompt740 session740 library740 service740 gateway740", 18),
        ["token740 prompt740", "session740", "library740", "service740", "gateway740"],
    ),
    (
        ("token740 prompt740 session740 library740 service740 gateway740", 28),
        ["token740 prompt740", "session740 library740", "service740 gateway740"],
    ),
    (
        ("prompt740 session740 library740 service740 gateway740 storage740", 6),
        ["prompt740", "session740", "library740", "service740", "gateway740", "storage740"],
    ),
    (
        ("prompt740 session740 library740 service740 gateway740 storage740", 10),
        ["prompt740", "session740", "library740", "service740", "gateway740", "storage740"],
    ),
    (
        ("prompt740 session740 library740 service740 gateway740 storage740", 18),
        ["prompt740", "session740", "library740", "service740", "gateway740", "storage740"],
    ),
    (
        ("prompt740 session740 library740 service740 gateway740 storage740", 28),
        ["prompt740 session740", "library740 service740", "gateway740 storage740"],
    ),
    (
        ("session740 library740 service740 gateway740 storage740 network740", 6),
        ["session740", "library740", "service740", "gateway740", "storage740", "network740"],
    ),
    (
        ("session740 library740 service740 gateway740 storage740 network740", 10),
        ["session740", "library740", "service740", "gateway740", "storage740", "network740"],
    ),
    (
        ("session740 library740 service740 gateway740 storage740 network740", 18),
        ["session740", "library740", "service740", "gateway740", "storage740", "network740"],
    ),
    (
        ("session740 library740 service740 gateway740 storage740 network740", 28),
        ["session740 library740", "service740 gateway740", "storage740 network740"],
    ),
    (
        ("library740 service740 gateway740 storage740 network740 latency740", 6),
        ["library740", "service740", "gateway740", "storage740", "network740", "latency740"],
    ),
    (
        ("library740 service740 gateway740 storage740 network740 latency740", 10),
        ["library740", "service740", "gateway740", "storage740", "network740", "latency740"],
    ),
    (
        ("library740 service740 gateway740 storage740 network740 latency740", 18),
        ["library740", "service740", "gateway740", "storage740", "network740", "latency740"],
    ),
    (
        ("library740 service740 gateway740 storage740 network740 latency740", 28),
        ["library740 service740", "gateway740 storage740", "network740 latency740"],
    ),
    (
        ("service740 gateway740 storage740 network740 latency740 buffer740", 6),
        ["service740", "gateway740", "storage740", "network740", "latency740", "buffer740"],
    ),
    (
        ("service740 gateway740 storage740 network740 latency740 buffer740", 10),
        ["service740", "gateway740", "storage740", "network740", "latency740", "buffer740"],
    ),
    (
        ("service740 gateway740 storage740 network740 latency740 buffer740", 18),
        ["service740", "gateway740", "storage740", "network740", "latency740", "buffer740"],
    ),
    (
        ("service740 gateway740 storage740 network740 latency740 buffer740", 28),
        ["service740 gateway740", "storage740 network740", "latency740 buffer740"],
    ),
    (
        ("gateway740 storage740 network740 latency740 buffer740 queue740", 6),
        ["gateway740", "storage740", "network740", "latency740", "buffer740", "queue740"],
    ),
    (
        ("gateway740 storage740 network740 latency740 buffer740 queue740", 10),
        ["gateway740", "storage740", "network740", "latency740", "buffer740", "queue740"],
    ),
    (
        ("gateway740 storage740 network740 latency740 buffer740 queue740", 18),
        ["gateway740", "storage740", "network740", "latency740", "buffer740 queue740"],
    ),
    (
        ("gateway740 storage740 network740 latency740 buffer740 queue740", 28),
        ["gateway740 storage740", "network740 latency740", "buffer740 queue740"],
    ),
    (
        ("storage740 network740 latency740 buffer740 queue740 worker740", 6),
        ["storage740", "network740", "latency740", "buffer740", "queue740", "worker740"],
    ),
    (
        ("storage740 network740 latency740 buffer740 queue740 worker740", 10),
        ["storage740", "network740", "latency740", "buffer740", "queue740", "worker740"],
    ),
    (
        ("storage740 network740 latency740 buffer740 queue740 worker740", 18),
        ["storage740", "network740", "latency740", "buffer740 queue740", "worker740"],
    ),
    (
        ("storage740 network740 latency740 buffer740 queue740 worker740", 28),
        ["storage740 network740", "latency740 buffer740", "queue740 worker740"],
    ),
    (
        ("network740 latency740 buffer740 queue740 worker740 kernel740", 6),
        ["network740", "latency740", "buffer740", "queue740", "worker740", "kernel740"],
    ),
    (
        ("network740 latency740 buffer740 queue740 worker740 kernel740", 10),
        ["network740", "latency740", "buffer740", "queue740", "worker740", "kernel740"],
    ),
    (
        ("network740 latency740 buffer740 queue740 worker740 kernel740", 18),
        ["network740", "latency740", "buffer740 queue740", "worker740", "kernel740"],
    ),
    (
        ("network740 latency740 buffer740 queue740 worker740 kernel740", 28),
        ["network740 latency740", "buffer740 queue740 worker740", "kernel740"],
    ),
    (
        ("latency740 buffer740 queue740 worker740 kernel740 signal740", 6),
        ["latency740", "buffer740", "queue740", "worker740", "kernel740", "signal740"],
    ),
    (
        ("latency740 buffer740 queue740 worker740 kernel740 signal740", 10),
        ["latency740", "buffer740", "queue740", "worker740", "kernel740", "signal740"],
    ),
    (
        ("latency740 buffer740 queue740 worker740 kernel740 signal740", 18),
        ["latency740", "buffer740 queue740", "worker740", "kernel740", "signal740"],
    ),
    (
        ("latency740 buffer740 queue740 worker740 kernel740 signal740", 28),
        ["latency740 buffer740", "queue740 worker740 kernel740", "signal740"],
    ),
    (
        ("buffer740 queue740 worker740 kernel740 signal740 packet740", 6),
        ["buffer740", "queue740", "worker740", "kernel740", "signal740", "packet740"],
    ),
    (
        ("buffer740 queue740 worker740 kernel740 signal740 packet740", 10),
        ["buffer740", "queue740", "worker740", "kernel740", "signal740", "packet740"],
    ),
    (
        ("buffer740 queue740 worker740 kernel740 signal740 packet740", 18),
        ["buffer740 queue740", "worker740", "kernel740", "signal740", "packet740"],
    ),
    (
        ("buffer740 queue740 worker740 kernel740 signal740 packet740", 28),
        ["buffer740 queue740 worker740", "kernel740 signal740", "packet740"],
    ),
    (
        ("queue740 worker740 kernel740 signal740 packet740 router740", 6),
        ["queue740", "worker740", "kernel740", "signal740", "packet740", "router740"],
    ),
    (
        ("queue740 worker740 kernel740 signal740 packet740 router740", 10),
        ["queue740", "worker740", "kernel740", "signal740", "packet740", "router740"],
    ),
    (
        ("queue740 worker740 kernel740 signal740 packet740 router740", 18),
        ["queue740 worker740", "kernel740", "signal740", "packet740", "router740"],
    ),
    (
        ("queue740 worker740 kernel740 signal740 packet740 router740", 28),
        ["queue740 worker740 kernel740", "signal740 packet740", "router740"],
    ),
    (
        ("worker740 kernel740 signal740 packet740 router740 cluster740", 6),
        ["worker740", "kernel740", "signal740", "packet740", "router740", "cluster740"],
    ),
    (
        ("worker740 kernel740 signal740 packet740 router740 cluster740", 10),
        ["worker740", "kernel740", "signal740", "packet740", "router740", "cluster740"],
    ),
    (
        ("worker740 kernel740 signal740 packet740 router740 cluster740", 18),
        ["worker740", "kernel740", "signal740", "packet740", "router740", "cluster740"],
    ),
    (
        ("worker740 kernel740 signal740 packet740 router740 cluster740", 28),
        ["worker740 kernel740", "signal740 packet740", "router740 cluster740"],
    ),
    (
        ("kernel740 signal740 packet740 router740 cluster740 mirror740", 6),
        ["kernel740", "signal740", "packet740", "router740", "cluster740", "mirror740"],
    ),
    (
        ("kernel740 signal740 packet740 router740 cluster740 mirror740", 10),
        ["kernel740", "signal740", "packet740", "router740", "cluster740", "mirror740"],
    ),
    (
        ("kernel740 signal740 packet740 router740 cluster740 mirror740", 18),
        ["kernel740", "signal740", "packet740", "router740", "cluster740", "mirror740"],
    ),
    (
        ("kernel740 signal740 packet740 router740 cluster740 mirror740", 28),
        ["kernel740 signal740", "packet740 router740", "cluster740 mirror740"],
    ),
    (
        ("signal740 packet740 router740 cluster740 mirror740 filter740", 6),
        ["signal740", "packet740", "router740", "cluster740", "mirror740", "filter740"],
    ),
    (
        ("signal740 packet740 router740 cluster740 mirror740 filter740", 10),
        ["signal740", "packet740", "router740", "cluster740", "mirror740", "filter740"],
    ),
    (
        ("signal740 packet740 router740 cluster740 mirror740 filter740", 18),
        ["signal740", "packet740", "router740", "cluster740", "mirror740", "filter740"],
    ),
    (
        ("signal740 packet740 router740 cluster740 mirror740 filter740", 28),
        ["signal740 packet740", "router740 cluster740", "mirror740 filter740"],
    ),
    (
        ("packet740 router740 cluster740 mirror740 filter740 ranking740", 6),
        ["packet740", "router740", "cluster740", "mirror740", "filter740", "ranking740"],
    ),
    (
        ("packet740 router740 cluster740 mirror740 filter740 ranking740", 10),
        ["packet740", "router740", "cluster740", "mirror740", "filter740", "ranking740"],
    ),
    (
        ("packet740 router740 cluster740 mirror740 filter740 ranking740", 18),
        ["packet740", "router740", "cluster740", "mirror740", "filter740", "ranking740"],
    ),
    (
        ("packet740 router740 cluster740 mirror740 filter740 ranking740", 28),
        ["packet740 router740", "cluster740 mirror740", "filter740 ranking740"],
    ),
    (
        ("router740 cluster740 mirror740 filter740 ranking740 encoding740", 6),
        ["router740", "cluster740", "mirror740", "filter740", "ranking740", "encoding740"],
    ),
    (
        ("router740 cluster740 mirror740 filter740 ranking740 encoding740", 10),
        ["router740", "cluster740", "mirror740", "filter740", "ranking740", "encoding740"],
    ),
    (
        ("router740 cluster740 mirror740 filter740 ranking740 encoding740", 18),
        ["router740", "cluster740", "mirror740", "filter740", "ranking740", "encoding740"],
    ),
    (
        ("router740 cluster740 mirror740 filter740 ranking740 encoding740", 28),
        ["router740 cluster740", "mirror740 filter740", "ranking740 encoding740"],
    ),
    (
        ("cluster740 mirror740 filter740 ranking740 encoding740 mapping740", 6),
        ["cluster740", "mirror740", "filter740", "ranking740", "encoding740", "mapping740"],
    ),
    (
        ("cluster740 mirror740 filter740 ranking740 encoding740 mapping740", 10),
        ["cluster740", "mirror740", "filter740", "ranking740", "encoding740", "mapping740"],
    ),
    (
        ("cluster740 mirror740 filter740 ranking740 encoding740 mapping740", 18),
        ["cluster740", "mirror740", "filter740", "ranking740", "encoding740", "mapping740"],
    ),
    (
        ("cluster740 mirror740 filter740 ranking740 encoding740 mapping740", 28),
        ["cluster740 mirror740", "filter740 ranking740", "encoding740 mapping740"],
    ),
    (
        ("mirror740 filter740 ranking740 encoding740 mapping740 record740", 6),
        ["mirror740", "filter740", "ranking740", "encoding740", "mapping740", "record740"],
    ),
    (
        ("mirror740 filter740 ranking740 encoding740 mapping740 record740", 10),
        ["mirror740", "filter740", "ranking740", "encoding740", "mapping740", "record740"],
    ),
    (
        ("mirror740 filter740 ranking740 encoding740 mapping740 record740", 18),
        ["mirror740", "filter740", "ranking740", "encoding740", "mapping740", "record740"],
    ),
    (
        ("mirror740 filter740 ranking740 encoding740 mapping740 record740", 28),
        ["mirror740 filter740", "ranking740 encoding740", "mapping740 record740"],
    ),
    (
        ("filter740 ranking740 encoding740 mapping740 record740 candle740", 6),
        ["filter740", "ranking740", "encoding740", "mapping740", "record740", "candle740"],
    ),
    (
        ("filter740 ranking740 encoding740 mapping740 record740 candle740", 10),
        ["filter740", "ranking740", "encoding740", "mapping740", "record740", "candle740"],
    ),
    (
        ("filter740 ranking740 encoding740 mapping740 record740 candle740", 18),
        ["filter740", "ranking740", "encoding740", "mapping740", "record740", "candle740"],
    ),
    (
        ("filter740 ranking740 encoding740 mapping740 record740 candle740", 28),
        ["filter740 ranking740", "encoding740 mapping740", "record740 candle740"],
    ),
    (
        ("ranking740 encoding740 mapping740 record740 candle740 thread740", 6),
        ["ranking740", "encoding740", "mapping740", "record740", "candle740", "thread740"],
    ),
    (
        ("ranking740 encoding740 mapping740 record740 candle740 thread740", 10),
        ["ranking740", "encoding740", "mapping740", "record740", "candle740", "thread740"],
    ),
    (
        ("ranking740 encoding740 mapping740 record740 candle740 thread740", 18),
        ["ranking740", "encoding740", "mapping740", "record740", "candle740", "thread740"],
    ),
    (
        ("ranking740 encoding740 mapping740 record740 candle740 thread740", 28),
        ["ranking740 encoding740", "mapping740 record740", "candle740 thread740"],
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
