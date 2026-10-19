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
        ("round 61: the quick brown fox jumps over the lazy dog", 4),
        ["round", "61:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 61: the quick brown fox jumps over the lazy dog", 8),
        ["round", "61: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 61: the quick brown fox jumps over the lazy dog", 12),
        ["round 61:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 61: the quick brown fox jumps over the lazy dog", 16),
        ["round 61: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 61: the quick brown fox jumps over the lazy dog", 24),
        ["round 61: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 61: the quick brown fox jumps over the lazy dog", 32),
        ["round 61: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 61: agentuniverse is a framework for multi agents", 4),
        ["round", "61:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 61: agentuniverse is a framework for multi agents", 8),
        ["round", "61:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 61: agentuniverse is a framework for multi agents", 12),
        ["round 61:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 61: agentuniverse is a framework for multi agents", 16),
        ["round 61:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 61: agentuniverse is a framework for multi agents", 24),
        ["round 61: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 61: agentuniverse is a framework for multi agents", 32),
        ["round 61: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 61: knowledge stored as vectors enables retrieval", 4),
        ["round", "61:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 61: knowledge stored as vectors enables retrieval", 8),
        ["round", "61:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 61: knowledge stored as vectors enables retrieval", 12),
        ["round 61:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 61: knowledge stored as vectors enables retrieval", 16),
        ["round 61:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 61: knowledge stored as vectors enables retrieval", 24),
        ["round 61: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 61: knowledge stored as vectors enables retrieval", 32),
        ["round 61: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 61: the processor reads the record then stops", 4),
        ["round", "61:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 61: the processor reads the record then stops", 8),
        ["round", "61: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 61: the processor reads the record then stops", 12),
        ["round 61:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 61: the processor reads the record then stops", 16),
        ["round 61: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 61: the processor reads the record then stops", 24),
        ["round 61: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 61: the processor reads the record then stops", 32),
        ["round 61: the processor reads", "the record then stops"],
    ),
    (
        ("round 61: a worker pulls the next task from the queue", 4),
        ["round", "61:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 61: a worker pulls the next task from the queue", 8),
        ["round", "61: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 61: a worker pulls the next task from the queue", 12),
        ["round 61: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 61: a worker pulls the next task from the queue", 16),
        ["round 61: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 61: a worker pulls the next task from the queue", 24),
        ["round 61: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 61: a worker pulls the next task from the queue", 32),
        ["round 61: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 61: signals travel through the network layer", 4),
        ["round", "61:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 61: signals travel through the network layer", 8),
        ["round", "61:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 61: signals travel through the network layer", 12),
        ["round 61:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 61: signals travel through the network layer", 16),
        ["round 61:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 61: signals travel through the network layer", 24),
        ["round 61: signals travel", "through the network", "layer"],
    ),
    (
        ("round 61: signals travel through the network layer", 32),
        ["round 61: signals travel through", "the network layer"],
    ),
    (
        ("round 61: the gateway routes each request by policy", 4),
        ["round", "61:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 61: the gateway routes each request by policy", 8),
        ["round", "61: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 61: the gateway routes each request by policy", 12),
        ["round 61:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 61: the gateway routes each request by policy", 16),
        ["round 61: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 61: the gateway routes each request by policy", 24),
        ["round 61: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 61: the gateway routes each request by policy", 32),
        ["round 61: the gateway routes", "each request by policy"],
    ),
    (
        ("round 61: memory grows until the buffer is full", 4),
        ["round", "61:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 61: memory grows until the buffer is full", 8),
        ["round", "61:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 61: memory grows until the buffer is full", 12),
        ["round 61:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 61: memory grows until the buffer is full", 16),
        ["round 61: memory", "grows until the", "buffer is full"],
    ),
    (("round 61: memory grows until the buffer is full", 24), ["round 61: memory grows", "until the buffer is full"]),
    (("round 61: memory grows until the buffer is full", 32), ["round 61: memory grows until the", "buffer is full"]),
    (
        ("round 61: the cluster mirrors every packet twice", 4),
        ["round", "61:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 61: the cluster mirrors every packet twice", 8),
        ["round", "61: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 61: the cluster mirrors every packet twice", 12),
        ["round 61:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 61: the cluster mirrors every packet twice", 16),
        ["round 61: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 61: the cluster mirrors every packet twice", 24),
        ["round 61: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 61: the cluster mirrors every packet twice", 32), ["round 61: the cluster mirrors", "every packet twice"]),
    (
        ("round 61: ranking uses tokens learned from the corpus", 4),
        ["round", "61:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 61: ranking uses tokens learned from the corpus", 8),
        ["round", "61:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 61: ranking uses tokens learned from the corpus", 12),
        ["round 61:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 61: ranking uses tokens learned from the corpus", 16),
        ["round 61:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 61: ranking uses tokens learned from the corpus", 24),
        ["round 61: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 61: ranking uses tokens learned from the corpus", 32),
        ["round 61: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 61: a long session ends when the candle dies", 4),
        ["round", "61:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 61: a long session ends when the candle dies", 8),
        ["round", "61: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 61: a long session ends when the candle dies", 12),
        ["round 61: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 61: a long session ends when the candle dies", 16),
        ["round 61: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 61: a long session ends when the candle dies", 24),
        ["round 61: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 61: a long session ends when the candle dies", 32),
        ["round 61: a long session ends", "when the candle dies"],
    ),
    (
        ("round 61: encode the prompt then map the result", 4),
        ["round", "61:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 61: encode the prompt then map the result", 8),
        ["round", "61:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 61: encode the prompt then map the result", 12),
        ["round 61:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 61: encode the prompt then map the result", 16),
        ["round 61: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 61: encode the prompt then map the result", 24),
        ["round 61: encode the", "prompt then map the", "result"],
    ),
    (("round 61: encode the prompt then map the result", 32), ["round 61: encode the prompt then", "map the result"]),
    (
        ("round 61: the kernel wakes the worker at dawn", 4),
        ["round", "61:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 61: the kernel wakes the worker at dawn", 8),
        ["round", "61: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 61: the kernel wakes the worker at dawn", 12),
        ["round 61:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 61: the kernel wakes the worker at dawn", 16), ["round 61: the", "kernel wakes the", "worker at dawn"]),
    (("round 61: the kernel wakes the worker at dawn", 24), ["round 61: the kernel", "wakes the worker at dawn"]),
    (("round 61: the kernel wakes the worker at dawn", 32), ["round 61: the kernel wakes the", "worker at dawn"]),
    (
        ("round 61: service latency drops after the patch", 4),
        ["round", "61:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 61: service latency drops after the patch", 8),
        ["round", "61:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 61: service latency drops after the patch", 12),
        ["round 61:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 61: service latency drops after the patch", 16),
        ["round 61:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 61: service latency drops after the patch", 24),
        ["round 61: service", "latency drops after the", "patch"],
    ),
    (("round 61: service latency drops after the patch", 32), ["round 61: service latency drops", "after the patch"]),
    (
        ("round 61: the library caches every vector it sees", 4),
        ["round", "61:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 61: the library caches every vector it sees", 8),
        ["round", "61: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 61: the library caches every vector it sees", 12),
        ["round 61:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 61: the library caches every vector it sees", 16),
        ["round 61: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 61: the library caches every vector it sees", 24),
        ["round 61: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 61: the library caches every vector it sees", 32),
        ["round 61: the library caches", "every vector it sees"],
    ),
    (
        ("round 61: agents argue then the debate resolves", 4),
        ["round", "61:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 61: agents argue then the debate resolves", 8),
        ["round", "61:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 61: agents argue then the debate resolves", 12),
        ["round 61:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 61: agents argue then the debate resolves", 16),
        ["round 61: agents", "argue then the", "debate resolves"],
    ),
    (("round 61: agents argue then the debate resolves", 24), ["round 61: agents argue", "then the debate resolves"]),
    (("round 61: agents argue then the debate resolves", 32), ["round 61: agents argue then the", "debate resolves"]),
    (
        ("round 61: the filter keeps only strong matches", 4),
        ["round", "61:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 61: the filter keeps only strong matches", 8),
        ["round", "61: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 61: the filter keeps only strong matches", 12),
        ["round 61:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 61: the filter keeps only strong matches", 16),
        ["round 61: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 61: the filter keeps only strong matches", 24), ["round 61: the filter", "keeps only strong", "matches"]),
    (("round 61: the filter keeps only strong matches", 32), ["round 61: the filter keeps only", "strong matches"]),
    (
        ("round 61: the model answers with a short reply", 4),
        ["round", "61:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 61: the model answers with a short reply", 8),
        ["round", "61: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 61: the model answers with a short reply", 12),
        ["round 61:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 61: the model answers with a short reply", 16),
        ["round 61: the", "model answers", "with a short", "reply"],
    ),
    (("round 61: the model answers with a short reply", 24), ["round 61: the model", "answers with a short", "reply"]),
    (("round 61: the model answers with a short reply", 32), ["round 61: the model answers with", "a short reply"]),
    (
        ("round 61: the recorder stores the reasoning trace", 4),
        ["round", "61:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 61: the recorder stores the reasoning trace", 8),
        ["round", "61: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 61: the recorder stores the reasoning trace", 12),
        ["round 61:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 61: the recorder stores the reasoning trace", 16),
        ["round 61: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 61: the recorder stores the reasoning trace", 24),
        ["round 61: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 61: the recorder stores the reasoning trace", 32),
        ["round 61: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 61: the angel watches the processor run", 4),
        ["round", "61:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 61: the angel watches the processor run", 8),
        ["round", "61: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 61: the angel watches the processor run", 12),
        ["round 61:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 61: the angel watches the processor run", 16), ["round 61: the", "angel watches", "the processor", "run"]),
    (("round 61: the angel watches the processor run", 24), ["round 61: the angel", "watches the processor", "run"]),
    (("round 61: the angel watches the processor run", 32), ["round 61: the angel watches the", "processor run"]),
    (
        ("round 61: angle of the vector decides the match", 4),
        ["round", "61:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 61: angle of the vector decides the match", 8),
        ["round", "61:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 61: angle of the vector decides the match", 12),
        ["round 61:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 61: angle of the vector decides the match", 16),
        ["round 61: angle", "of the vector", "decides the", "match"],
    ),
    (("round 61: angle of the vector decides the match", 24), ["round 61: angle of the", "vector decides the match"]),
    (("round 61: angle of the vector decides the match", 32), ["round 61: angle of the vector", "decides the match"]),
    (
        ("round 61: the candle burns twice as long at night", 4),
        ["round", "61:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 61: the candle burns twice as long at night", 8),
        ["round", "61: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 61: the candle burns twice as long at night", 12),
        ["round 61:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 61: the candle burns twice as long at night", 16),
        ["round 61: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 61: the candle burns twice as long at night", 24),
        ["round 61: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 61: the candle burns twice as long at night", 32),
        ["round 61: the candle burns twice", "as long at night"],
    ),
    (
        ("round 61: a mirror of the universe in one line", 4),
        ["round", "61:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 61: a mirror of the universe in one line", 8),
        ["round", "61: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 61: a mirror of the universe in one line", 12),
        ["round 61: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 61: a mirror of the universe in one line", 16),
        ["round 61: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 61: a mirror of the universe in one line", 24), ["round 61: a mirror of", "the universe in one line"]),
    (("round 61: a mirror of the universe in one line", 32), ["round 61: a mirror of the", "universe in one line"]),
    (
        ("round 61: the queue drains before the storm", 4),
        ["round", "61:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 61: the queue drains before the storm", 8),
        ["round", "61: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 61: the queue drains before the storm", 12), ["round 61:", "the queue", "drains", "before the", "storm"]),
    (("round 61: the queue drains before the storm", 16), ["round 61: the", "queue drains", "before the storm"]),
    (("round 61: the queue drains before the storm", 24), ["round 61: the queue", "drains before the storm"]),
    (("round 61: the queue drains before the storm", 32), ["round 61: the queue drains", "before the storm"]),
    (
        ("kitten61 sitting61 agent61 angle61 universe61 memory61", 6),
        ["kitten61", "sitting61", "agent61", "angle61", "universe61", "memory61"],
    ),
    (
        ("kitten61 sitting61 agent61 angle61 universe61 memory61", 10),
        ["kitten61", "sitting61", "agent61", "angle61", "universe61", "memory61"],
    ),
    (
        ("kitten61 sitting61 agent61 angle61 universe61 memory61", 18),
        ["kitten61 sitting61", "agent61 angle61", "universe61", "memory61"],
    ),
    (
        ("kitten61 sitting61 agent61 angle61 universe61 memory61", 28),
        ["kitten61 sitting61 agent61", "angle61 universe61 memory61"],
    ),
    (
        ("sitting61 agent61 angle61 universe61 memory61 stream61", 6),
        ["sitting61", "agent61", "angle61", "universe61", "memory61", "stream61"],
    ),
    (
        ("sitting61 agent61 angle61 universe61 memory61 stream61", 10),
        ["sitting61", "agent61", "angle61", "universe61", "memory61", "stream61"],
    ),
    (
        ("sitting61 agent61 angle61 universe61 memory61 stream61", 18),
        ["sitting61 agent61", "angle61 universe61", "memory61 stream61"],
    ),
    (
        ("sitting61 agent61 angle61 universe61 memory61 stream61", 28),
        ["sitting61 agent61 angle61", "universe61 memory61 stream61"],
    ),
    (
        ("agent61 angle61 universe61 memory61 stream61 context61", 6),
        ["agent61", "angle61", "universe61", "memory61", "stream61", "context61"],
    ),
    (
        ("agent61 angle61 universe61 memory61 stream61 context61", 10),
        ["agent61", "angle61", "universe61", "memory61", "stream61", "context61"],
    ),
    (
        ("agent61 angle61 universe61 memory61 stream61 context61", 18),
        ["agent61 angle61", "universe61", "memory61 stream61", "context61"],
    ),
    (
        ("agent61 angle61 universe61 memory61 stream61 context61", 28),
        ["agent61 angle61 universe61", "memory61 stream61 context61"],
    ),
    (
        ("angle61 universe61 memory61 stream61 context61 knowledge61", 6),
        ["angle61", "universe61", "memory61", "stream61", "context61", "knowledge61"],
    ),
    (
        ("angle61 universe61 memory61 stream61 context61 knowledge61", 10),
        ["angle61", "universe61", "memory61", "stream61", "context61", "knowledge61"],
    ),
    (
        ("angle61 universe61 memory61 stream61 context61 knowledge61", 18),
        ["angle61 universe61", "memory61 stream61", "context61", "knowledge61"],
    ),
    (
        ("angle61 universe61 memory61 stream61 context61 knowledge61", 28),
        ["angle61 universe61 memory61", "stream61 context61", "knowledge61"],
    ),
    (
        ("universe61 memory61 stream61 context61 knowledge61 vector61", 6),
        ["universe61", "memory61", "stream61", "context61", "knowledge61", "vector61"],
    ),
    (
        ("universe61 memory61 stream61 context61 knowledge61 vector61", 10),
        ["universe61", "memory61", "stream61", "context61", "knowledge61", "vector61"],
    ),
    (
        ("universe61 memory61 stream61 context61 knowledge61 vector61", 18),
        ["universe61", "memory61 stream61", "context61", "knowledge61", "vector61"],
    ),
    (
        ("universe61 memory61 stream61 context61 knowledge61 vector61", 28),
        ["universe61 memory61 stream61", "context61 knowledge61", "vector61"],
    ),
    (
        ("memory61 stream61 context61 knowledge61 vector61 processor61", 6),
        ["memory61", "stream61", "context61", "knowledge61", "vector61", "processor61"],
    ),
    (
        ("memory61 stream61 context61 knowledge61 vector61 processor61", 10),
        ["memory61", "stream61", "context61", "knowledge61", "vector61", "processor61"],
    ),
    (
        ("memory61 stream61 context61 knowledge61 vector61 processor61", 18),
        ["memory61 stream61", "context61", "knowledge61", "vector61", "processor61"],
    ),
    (
        ("memory61 stream61 context61 knowledge61 vector61 processor61", 28),
        ["memory61 stream61 context61", "knowledge61 vector61", "processor61"],
    ),
    (
        ("stream61 context61 knowledge61 vector61 processor61 reasoning61", 6),
        ["stream61", "context61", "knowledge61", "vector61", "processor61", "reasoning61"],
    ),
    (
        ("stream61 context61 knowledge61 vector61 processor61 reasoning61", 10),
        ["stream61", "context61", "knowledge61", "vector61", "processor61", "reasoning61"],
    ),
    (
        ("stream61 context61 knowledge61 vector61 processor61 reasoning61", 18),
        ["stream61 context61", "knowledge61", "vector61", "processor61", "reasoning61"],
    ),
    (
        ("stream61 context61 knowledge61 vector61 processor61 reasoning61", 28),
        ["stream61 context61", "knowledge61 vector61", "processor61 reasoning61"],
    ),
    (
        ("context61 knowledge61 vector61 processor61 reasoning61 machine61", 6),
        ["context61", "knowledge61", "vector61", "processor61", "reasoning61", "machine61"],
    ),
    (
        ("context61 knowledge61 vector61 processor61 reasoning61 machine61", 10),
        ["context61", "knowledge61", "vector61", "processor61", "reasoning61", "machine61"],
    ),
    (
        ("context61 knowledge61 vector61 processor61 reasoning61 machine61", 18),
        ["context61", "knowledge61", "vector61", "processor61", "reasoning61", "machine61"],
    ),
    (
        ("context61 knowledge61 vector61 processor61 reasoning61 machine61", 28),
        ["context61 knowledge61", "vector61 processor61", "reasoning61 machine61"],
    ),
    (
        ("knowledge61 vector61 processor61 reasoning61 machine61 learning61", 6),
        ["knowledge61", "vector61", "processor61", "reasoning61", "machine61", "learning61"],
    ),
    (
        ("knowledge61 vector61 processor61 reasoning61 machine61 learning61", 10),
        ["knowledge61", "vector61", "processor61", "reasoning61", "machine61", "learning61"],
    ),
    (
        ("knowledge61 vector61 processor61 reasoning61 machine61 learning61", 18),
        ["knowledge61", "vector61", "processor61", "reasoning61", "machine61", "learning61"],
    ),
    (
        ("knowledge61 vector61 processor61 reasoning61 machine61 learning61", 28),
        ["knowledge61 vector61", "processor61 reasoning61", "machine61 learning61"],
    ),
    (
        ("vector61 processor61 reasoning61 machine61 learning61 model61", 6),
        ["vector61", "processor61", "reasoning61", "machine61", "learning61", "model61"],
    ),
    (
        ("vector61 processor61 reasoning61 machine61 learning61 model61", 10),
        ["vector61", "processor61", "reasoning61", "machine61", "learning61", "model61"],
    ),
    (
        ("vector61 processor61 reasoning61 machine61 learning61 model61", 18),
        ["vector61", "processor61", "reasoning61", "machine61", "learning61 model61"],
    ),
    (
        ("vector61 processor61 reasoning61 machine61 learning61 model61", 28),
        ["vector61 processor61", "reasoning61 machine61", "learning61 model61"],
    ),
    (
        ("processor61 reasoning61 machine61 learning61 model61 token61", 6),
        ["processor61", "reasoning61", "machine61", "learning61", "model61", "token61"],
    ),
    (
        ("processor61 reasoning61 machine61 learning61 model61 token61", 10),
        ["processor61", "reasoning61", "machine61", "learning61", "model61", "token61"],
    ),
    (
        ("processor61 reasoning61 machine61 learning61 model61 token61", 18),
        ["processor61", "reasoning61", "machine61", "learning61 model61", "token61"],
    ),
    (
        ("processor61 reasoning61 machine61 learning61 model61 token61", 28),
        ["processor61 reasoning61", "machine61 learning61 model61", "token61"],
    ),
    (
        ("reasoning61 machine61 learning61 model61 token61 prompt61", 6),
        ["reasoning61", "machine61", "learning61", "model61", "token61", "prompt61"],
    ),
    (
        ("reasoning61 machine61 learning61 model61 token61 prompt61", 10),
        ["reasoning61", "machine61", "learning61", "model61", "token61", "prompt61"],
    ),
    (
        ("reasoning61 machine61 learning61 model61 token61 prompt61", 18),
        ["reasoning61", "machine61", "learning61 model61", "token61 prompt61"],
    ),
    (
        ("reasoning61 machine61 learning61 model61 token61 prompt61", 28),
        ["reasoning61 machine61", "learning61 model61 token61", "prompt61"],
    ),
    (
        ("machine61 learning61 model61 token61 prompt61 session61", 6),
        ["machine61", "learning61", "model61", "token61", "prompt61", "session61"],
    ),
    (
        ("machine61 learning61 model61 token61 prompt61 session61", 10),
        ["machine61", "learning61", "model61", "token61", "prompt61", "session61"],
    ),
    (
        ("machine61 learning61 model61 token61 prompt61 session61", 18),
        ["machine61", "learning61 model61", "token61 prompt61", "session61"],
    ),
    (
        ("machine61 learning61 model61 token61 prompt61 session61", 28),
        ["machine61 learning61 model61", "token61 prompt61 session61"],
    ),
    (
        ("learning61 model61 token61 prompt61 session61 library61", 6),
        ["learning61", "model61", "token61", "prompt61", "session61", "library61"],
    ),
    (
        ("learning61 model61 token61 prompt61 session61 library61", 10),
        ["learning61", "model61", "token61", "prompt61", "session61", "library61"],
    ),
    (
        ("learning61 model61 token61 prompt61 session61 library61", 18),
        ["learning61 model61", "token61 prompt61", "session61", "library61"],
    ),
    (
        ("learning61 model61 token61 prompt61 session61 library61", 28),
        ["learning61 model61 token61", "prompt61 session61 library61"],
    ),
    (
        ("model61 token61 prompt61 session61 library61 service61", 6),
        ["model61", "token61", "prompt61", "session61", "library61", "service61"],
    ),
    (
        ("model61 token61 prompt61 session61 library61 service61", 10),
        ["model61", "token61", "prompt61", "session61", "library61", "service61"],
    ),
    (
        ("model61 token61 prompt61 session61 library61 service61", 18),
        ["model61 token61", "prompt61 session61", "library61", "service61"],
    ),
    (
        ("model61 token61 prompt61 session61 library61 service61", 28),
        ["model61 token61 prompt61", "session61 library61", "service61"],
    ),
    (
        ("token61 prompt61 session61 library61 service61 gateway61", 6),
        ["token61", "prompt61", "session61", "library61", "service61", "gateway61"],
    ),
    (
        ("token61 prompt61 session61 library61 service61 gateway61", 10),
        ["token61", "prompt61", "session61", "library61", "service61", "gateway61"],
    ),
    (
        ("token61 prompt61 session61 library61 service61 gateway61", 18),
        ["token61 prompt61", "session61", "library61", "service61", "gateway61"],
    ),
    (
        ("token61 prompt61 session61 library61 service61 gateway61", 28),
        ["token61 prompt61 session61", "library61 service61", "gateway61"],
    ),
    (
        ("prompt61 session61 library61 service61 gateway61 storage61", 6),
        ["prompt61", "session61", "library61", "service61", "gateway61", "storage61"],
    ),
    (
        ("prompt61 session61 library61 service61 gateway61 storage61", 10),
        ["prompt61", "session61", "library61", "service61", "gateway61", "storage61"],
    ),
    (
        ("prompt61 session61 library61 service61 gateway61 storage61", 18),
        ["prompt61 session61", "library61", "service61", "gateway61", "storage61"],
    ),
    (
        ("prompt61 session61 library61 service61 gateway61 storage61", 28),
        ["prompt61 session61 library61", "service61 gateway61", "storage61"],
    ),
    (
        ("session61 library61 service61 gateway61 storage61 network61", 6),
        ["session61", "library61", "service61", "gateway61", "storage61", "network61"],
    ),
    (
        ("session61 library61 service61 gateway61 storage61 network61", 10),
        ["session61", "library61", "service61", "gateway61", "storage61", "network61"],
    ),
    (
        ("session61 library61 service61 gateway61 storage61 network61", 18),
        ["session61", "library61", "service61", "gateway61", "storage61", "network61"],
    ),
    (
        ("session61 library61 service61 gateway61 storage61 network61", 28),
        ["session61 library61", "service61 gateway61", "storage61 network61"],
    ),
    (
        ("library61 service61 gateway61 storage61 network61 latency61", 6),
        ["library61", "service61", "gateway61", "storage61", "network61", "latency61"],
    ),
    (
        ("library61 service61 gateway61 storage61 network61 latency61", 10),
        ["library61", "service61", "gateway61", "storage61", "network61", "latency61"],
    ),
    (
        ("library61 service61 gateway61 storage61 network61 latency61", 18),
        ["library61", "service61", "gateway61", "storage61", "network61", "latency61"],
    ),
    (
        ("library61 service61 gateway61 storage61 network61 latency61", 28),
        ["library61 service61", "gateway61 storage61", "network61 latency61"],
    ),
    (
        ("service61 gateway61 storage61 network61 latency61 buffer61", 6),
        ["service61", "gateway61", "storage61", "network61", "latency61", "buffer61"],
    ),
    (
        ("service61 gateway61 storage61 network61 latency61 buffer61", 10),
        ["service61", "gateway61", "storage61", "network61", "latency61", "buffer61"],
    ),
    (
        ("service61 gateway61 storage61 network61 latency61 buffer61", 18),
        ["service61", "gateway61", "storage61", "network61", "latency61 buffer61"],
    ),
    (
        ("service61 gateway61 storage61 network61 latency61 buffer61", 28),
        ["service61 gateway61", "storage61 network61", "latency61 buffer61"],
    ),
    (
        ("gateway61 storage61 network61 latency61 buffer61 queue61", 6),
        ["gateway61", "storage61", "network61", "latency61", "buffer61", "queue61"],
    ),
    (
        ("gateway61 storage61 network61 latency61 buffer61 queue61", 10),
        ["gateway61", "storage61", "network61", "latency61", "buffer61", "queue61"],
    ),
    (
        ("gateway61 storage61 network61 latency61 buffer61 queue61", 18),
        ["gateway61", "storage61", "network61", "latency61 buffer61", "queue61"],
    ),
    (
        ("gateway61 storage61 network61 latency61 buffer61 queue61", 28),
        ["gateway61 storage61", "network61 latency61 buffer61", "queue61"],
    ),
    (
        ("storage61 network61 latency61 buffer61 queue61 worker61", 6),
        ["storage61", "network61", "latency61", "buffer61", "queue61", "worker61"],
    ),
    (
        ("storage61 network61 latency61 buffer61 queue61 worker61", 10),
        ["storage61", "network61", "latency61", "buffer61", "queue61", "worker61"],
    ),
    (
        ("storage61 network61 latency61 buffer61 queue61 worker61", 18),
        ["storage61", "network61", "latency61 buffer61", "queue61 worker61"],
    ),
    (
        ("storage61 network61 latency61 buffer61 queue61 worker61", 28),
        ["storage61 network61", "latency61 buffer61 queue61", "worker61"],
    ),
    (
        ("network61 latency61 buffer61 queue61 worker61 kernel61", 6),
        ["network61", "latency61", "buffer61", "queue61", "worker61", "kernel61"],
    ),
    (
        ("network61 latency61 buffer61 queue61 worker61 kernel61", 10),
        ["network61", "latency61", "buffer61", "queue61", "worker61", "kernel61"],
    ),
    (
        ("network61 latency61 buffer61 queue61 worker61 kernel61", 18),
        ["network61", "latency61 buffer61", "queue61 worker61", "kernel61"],
    ),
    (
        ("network61 latency61 buffer61 queue61 worker61 kernel61", 28),
        ["network61 latency61 buffer61", "queue61 worker61 kernel61"],
    ),
    (
        ("latency61 buffer61 queue61 worker61 kernel61 signal61", 6),
        ["latency61", "buffer61", "queue61", "worker61", "kernel61", "signal61"],
    ),
    (
        ("latency61 buffer61 queue61 worker61 kernel61 signal61", 10),
        ["latency61", "buffer61", "queue61", "worker61", "kernel61", "signal61"],
    ),
    (
        ("latency61 buffer61 queue61 worker61 kernel61 signal61", 18),
        ["latency61 buffer61", "queue61 worker61", "kernel61 signal61"],
    ),
    (
        ("latency61 buffer61 queue61 worker61 kernel61 signal61", 28),
        ["latency61 buffer61 queue61", "worker61 kernel61 signal61"],
    ),
    (
        ("buffer61 queue61 worker61 kernel61 signal61 packet61", 6),
        ["buffer61", "queue61", "worker61", "kernel61", "signal61", "packet61"],
    ),
    (
        ("buffer61 queue61 worker61 kernel61 signal61 packet61", 10),
        ["buffer61", "queue61", "worker61", "kernel61", "signal61", "packet61"],
    ),
    (
        ("buffer61 queue61 worker61 kernel61 signal61 packet61", 18),
        ["buffer61 queue61", "worker61 kernel61", "signal61 packet61"],
    ),
    (
        ("buffer61 queue61 worker61 kernel61 signal61 packet61", 28),
        ["buffer61 queue61 worker61", "kernel61 signal61 packet61"],
    ),
    (
        ("queue61 worker61 kernel61 signal61 packet61 router61", 6),
        ["queue61", "worker61", "kernel61", "signal61", "packet61", "router61"],
    ),
    (
        ("queue61 worker61 kernel61 signal61 packet61 router61", 10),
        ["queue61", "worker61", "kernel61", "signal61", "packet61", "router61"],
    ),
    (
        ("queue61 worker61 kernel61 signal61 packet61 router61", 18),
        ["queue61 worker61", "kernel61 signal61", "packet61 router61"],
    ),
    (
        ("queue61 worker61 kernel61 signal61 packet61 router61", 28),
        ["queue61 worker61 kernel61", "signal61 packet61 router61"],
    ),
    (
        ("worker61 kernel61 signal61 packet61 router61 cluster61", 6),
        ["worker61", "kernel61", "signal61", "packet61", "router61", "cluster61"],
    ),
    (
        ("worker61 kernel61 signal61 packet61 router61 cluster61", 10),
        ["worker61", "kernel61", "signal61", "packet61", "router61", "cluster61"],
    ),
    (
        ("worker61 kernel61 signal61 packet61 router61 cluster61", 18),
        ["worker61 kernel61", "signal61 packet61", "router61 cluster61"],
    ),
    (
        ("worker61 kernel61 signal61 packet61 router61 cluster61", 28),
        ["worker61 kernel61 signal61", "packet61 router61 cluster61"],
    ),
    (
        ("kernel61 signal61 packet61 router61 cluster61 mirror61", 6),
        ["kernel61", "signal61", "packet61", "router61", "cluster61", "mirror61"],
    ),
    (
        ("kernel61 signal61 packet61 router61 cluster61 mirror61", 10),
        ["kernel61", "signal61", "packet61", "router61", "cluster61", "mirror61"],
    ),
    (
        ("kernel61 signal61 packet61 router61 cluster61 mirror61", 18),
        ["kernel61 signal61", "packet61 router61", "cluster61 mirror61"],
    ),
    (
        ("kernel61 signal61 packet61 router61 cluster61 mirror61", 28),
        ["kernel61 signal61 packet61", "router61 cluster61 mirror61"],
    ),
    (
        ("signal61 packet61 router61 cluster61 mirror61 filter61", 6),
        ["signal61", "packet61", "router61", "cluster61", "mirror61", "filter61"],
    ),
    (
        ("signal61 packet61 router61 cluster61 mirror61 filter61", 10),
        ["signal61", "packet61", "router61", "cluster61", "mirror61", "filter61"],
    ),
    (
        ("signal61 packet61 router61 cluster61 mirror61 filter61", 18),
        ["signal61 packet61", "router61 cluster61", "mirror61 filter61"],
    ),
    (
        ("signal61 packet61 router61 cluster61 mirror61 filter61", 28),
        ["signal61 packet61 router61", "cluster61 mirror61 filter61"],
    ),
    (
        ("packet61 router61 cluster61 mirror61 filter61 ranking61", 6),
        ["packet61", "router61", "cluster61", "mirror61", "filter61", "ranking61"],
    ),
    (
        ("packet61 router61 cluster61 mirror61 filter61 ranking61", 10),
        ["packet61", "router61", "cluster61", "mirror61", "filter61", "ranking61"],
    ),
    (
        ("packet61 router61 cluster61 mirror61 filter61 ranking61", 18),
        ["packet61 router61", "cluster61 mirror61", "filter61 ranking61"],
    ),
    (
        ("packet61 router61 cluster61 mirror61 filter61 ranking61", 28),
        ["packet61 router61 cluster61", "mirror61 filter61 ranking61"],
    ),
    (
        ("router61 cluster61 mirror61 filter61 ranking61 encoding61", 6),
        ["router61", "cluster61", "mirror61", "filter61", "ranking61", "encoding61"],
    ),
    (
        ("router61 cluster61 mirror61 filter61 ranking61 encoding61", 10),
        ["router61", "cluster61", "mirror61", "filter61", "ranking61", "encoding61"],
    ),
    (
        ("router61 cluster61 mirror61 filter61 ranking61 encoding61", 18),
        ["router61 cluster61", "mirror61 filter61", "ranking61", "encoding61"],
    ),
    (
        ("router61 cluster61 mirror61 filter61 ranking61 encoding61", 28),
        ["router61 cluster61 mirror61", "filter61 ranking61", "encoding61"],
    ),
    (
        ("cluster61 mirror61 filter61 ranking61 encoding61 mapping61", 6),
        ["cluster61", "mirror61", "filter61", "ranking61", "encoding61", "mapping61"],
    ),
    (
        ("cluster61 mirror61 filter61 ranking61 encoding61 mapping61", 10),
        ["cluster61", "mirror61", "filter61", "ranking61", "encoding61", "mapping61"],
    ),
    (
        ("cluster61 mirror61 filter61 ranking61 encoding61 mapping61", 18),
        ["cluster61 mirror61", "filter61 ranking61", "encoding61", "mapping61"],
    ),
    (
        ("cluster61 mirror61 filter61 ranking61 encoding61 mapping61", 28),
        ["cluster61 mirror61 filter61", "ranking61 encoding61", "mapping61"],
    ),
    (
        ("mirror61 filter61 ranking61 encoding61 mapping61 record61", 6),
        ["mirror61", "filter61", "ranking61", "encoding61", "mapping61", "record61"],
    ),
    (
        ("mirror61 filter61 ranking61 encoding61 mapping61 record61", 10),
        ["mirror61", "filter61", "ranking61", "encoding61", "mapping61", "record61"],
    ),
    (
        ("mirror61 filter61 ranking61 encoding61 mapping61 record61", 18),
        ["mirror61 filter61", "ranking61", "encoding61", "mapping61 record61"],
    ),
    (
        ("mirror61 filter61 ranking61 encoding61 mapping61 record61", 28),
        ["mirror61 filter61 ranking61", "encoding61 mapping61", "record61"],
    ),
    (
        ("filter61 ranking61 encoding61 mapping61 record61 candle61", 6),
        ["filter61", "ranking61", "encoding61", "mapping61", "record61", "candle61"],
    ),
    (
        ("filter61 ranking61 encoding61 mapping61 record61 candle61", 10),
        ["filter61", "ranking61", "encoding61", "mapping61", "record61", "candle61"],
    ),
    (
        ("filter61 ranking61 encoding61 mapping61 record61 candle61", 18),
        ["filter61 ranking61", "encoding61", "mapping61 record61", "candle61"],
    ),
    (
        ("filter61 ranking61 encoding61 mapping61 record61 candle61", 28),
        ["filter61 ranking61", "encoding61 mapping61", "record61 candle61"],
    ),
    (
        ("ranking61 encoding61 mapping61 record61 candle61 thread61", 6),
        ["ranking61", "encoding61", "mapping61", "record61", "candle61", "thread61"],
    ),
    (
        ("ranking61 encoding61 mapping61 record61 candle61 thread61", 10),
        ["ranking61", "encoding61", "mapping61", "record61", "candle61", "thread61"],
    ),
    (
        ("ranking61 encoding61 mapping61 record61 candle61 thread61", 18),
        ["ranking61", "encoding61", "mapping61 record61", "candle61 thread61"],
    ),
    (
        ("ranking61 encoding61 mapping61 record61 candle61 thread61", 28),
        ["ranking61 encoding61", "mapping61 record61 candle61", "thread61"],
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
