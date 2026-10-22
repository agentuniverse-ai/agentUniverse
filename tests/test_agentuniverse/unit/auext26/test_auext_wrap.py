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
        ("round 26: the quick brown fox jumps over the lazy dog", 4),
        ["round", "26:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 26: the quick brown fox jumps over the lazy dog", 8),
        ["round", "26: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 26: the quick brown fox jumps over the lazy dog", 12),
        ["round 26:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 26: the quick brown fox jumps over the lazy dog", 16),
        ["round 26: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 26: the quick brown fox jumps over the lazy dog", 24),
        ["round 26: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 26: the quick brown fox jumps over the lazy dog", 32),
        ["round 26: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 26: agentuniverse is a framework for multi agents", 4),
        ["round", "26:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 26: agentuniverse is a framework for multi agents", 8),
        ["round", "26:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 26: agentuniverse is a framework for multi agents", 12),
        ["round 26:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 26: agentuniverse is a framework for multi agents", 16),
        ["round 26:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 26: agentuniverse is a framework for multi agents", 24),
        ["round 26: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 26: agentuniverse is a framework for multi agents", 32),
        ["round 26: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 26: knowledge stored as vectors enables retrieval", 4),
        ["round", "26:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 26: knowledge stored as vectors enables retrieval", 8),
        ["round", "26:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 26: knowledge stored as vectors enables retrieval", 12),
        ["round 26:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 26: knowledge stored as vectors enables retrieval", 16),
        ["round 26:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 26: knowledge stored as vectors enables retrieval", 24),
        ["round 26: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 26: knowledge stored as vectors enables retrieval", 32),
        ["round 26: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 26: the processor reads the record then stops", 4),
        ["round", "26:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 26: the processor reads the record then stops", 8),
        ["round", "26: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 26: the processor reads the record then stops", 12),
        ["round 26:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 26: the processor reads the record then stops", 16),
        ["round 26: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 26: the processor reads the record then stops", 24),
        ["round 26: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 26: the processor reads the record then stops", 32),
        ["round 26: the processor reads", "the record then stops"],
    ),
    (
        ("round 26: a worker pulls the next task from the queue", 4),
        ["round", "26:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 26: a worker pulls the next task from the queue", 8),
        ["round", "26: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 26: a worker pulls the next task from the queue", 12),
        ["round 26: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 26: a worker pulls the next task from the queue", 16),
        ["round 26: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 26: a worker pulls the next task from the queue", 24),
        ["round 26: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 26: a worker pulls the next task from the queue", 32),
        ["round 26: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 26: signals travel through the network layer", 4),
        ["round", "26:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 26: signals travel through the network layer", 8),
        ["round", "26:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 26: signals travel through the network layer", 12),
        ["round 26:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 26: signals travel through the network layer", 16),
        ["round 26:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 26: signals travel through the network layer", 24),
        ["round 26: signals travel", "through the network", "layer"],
    ),
    (
        ("round 26: signals travel through the network layer", 32),
        ["round 26: signals travel through", "the network layer"],
    ),
    (
        ("round 26: the gateway routes each request by policy", 4),
        ["round", "26:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 26: the gateway routes each request by policy", 8),
        ["round", "26: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 26: the gateway routes each request by policy", 12),
        ["round 26:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 26: the gateway routes each request by policy", 16),
        ["round 26: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 26: the gateway routes each request by policy", 24),
        ["round 26: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 26: the gateway routes each request by policy", 32),
        ["round 26: the gateway routes", "each request by policy"],
    ),
    (
        ("round 26: memory grows until the buffer is full", 4),
        ["round", "26:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 26: memory grows until the buffer is full", 8),
        ["round", "26:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 26: memory grows until the buffer is full", 12),
        ["round 26:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 26: memory grows until the buffer is full", 16),
        ["round 26: memory", "grows until the", "buffer is full"],
    ),
    (("round 26: memory grows until the buffer is full", 24), ["round 26: memory grows", "until the buffer is full"]),
    (("round 26: memory grows until the buffer is full", 32), ["round 26: memory grows until the", "buffer is full"]),
    (
        ("round 26: the cluster mirrors every packet twice", 4),
        ["round", "26:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 26: the cluster mirrors every packet twice", 8),
        ["round", "26: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 26: the cluster mirrors every packet twice", 12),
        ["round 26:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 26: the cluster mirrors every packet twice", 16),
        ["round 26: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 26: the cluster mirrors every packet twice", 24),
        ["round 26: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 26: the cluster mirrors every packet twice", 32), ["round 26: the cluster mirrors", "every packet twice"]),
    (
        ("round 26: ranking uses tokens learned from the corpus", 4),
        ["round", "26:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 26: ranking uses tokens learned from the corpus", 8),
        ["round", "26:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 26: ranking uses tokens learned from the corpus", 12),
        ["round 26:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 26: ranking uses tokens learned from the corpus", 16),
        ["round 26:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 26: ranking uses tokens learned from the corpus", 24),
        ["round 26: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 26: ranking uses tokens learned from the corpus", 32),
        ["round 26: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 26: a long session ends when the candle dies", 4),
        ["round", "26:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 26: a long session ends when the candle dies", 8),
        ["round", "26: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 26: a long session ends when the candle dies", 12),
        ["round 26: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 26: a long session ends when the candle dies", 16),
        ["round 26: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 26: a long session ends when the candle dies", 24),
        ["round 26: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 26: a long session ends when the candle dies", 32),
        ["round 26: a long session ends", "when the candle dies"],
    ),
    (
        ("round 26: encode the prompt then map the result", 4),
        ["round", "26:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 26: encode the prompt then map the result", 8),
        ["round", "26:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 26: encode the prompt then map the result", 12),
        ["round 26:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 26: encode the prompt then map the result", 16),
        ["round 26: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 26: encode the prompt then map the result", 24),
        ["round 26: encode the", "prompt then map the", "result"],
    ),
    (("round 26: encode the prompt then map the result", 32), ["round 26: encode the prompt then", "map the result"]),
    (
        ("round 26: the kernel wakes the worker at dawn", 4),
        ["round", "26:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 26: the kernel wakes the worker at dawn", 8),
        ["round", "26: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 26: the kernel wakes the worker at dawn", 12),
        ["round 26:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 26: the kernel wakes the worker at dawn", 16), ["round 26: the", "kernel wakes the", "worker at dawn"]),
    (("round 26: the kernel wakes the worker at dawn", 24), ["round 26: the kernel", "wakes the worker at dawn"]),
    (("round 26: the kernel wakes the worker at dawn", 32), ["round 26: the kernel wakes the", "worker at dawn"]),
    (
        ("round 26: service latency drops after the patch", 4),
        ["round", "26:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 26: service latency drops after the patch", 8),
        ["round", "26:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 26: service latency drops after the patch", 12),
        ["round 26:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 26: service latency drops after the patch", 16),
        ["round 26:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 26: service latency drops after the patch", 24),
        ["round 26: service", "latency drops after the", "patch"],
    ),
    (("round 26: service latency drops after the patch", 32), ["round 26: service latency drops", "after the patch"]),
    (
        ("round 26: the library caches every vector it sees", 4),
        ["round", "26:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 26: the library caches every vector it sees", 8),
        ["round", "26: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 26: the library caches every vector it sees", 12),
        ["round 26:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 26: the library caches every vector it sees", 16),
        ["round 26: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 26: the library caches every vector it sees", 24),
        ["round 26: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 26: the library caches every vector it sees", 32),
        ["round 26: the library caches", "every vector it sees"],
    ),
    (
        ("round 26: agents argue then the debate resolves", 4),
        ["round", "26:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 26: agents argue then the debate resolves", 8),
        ["round", "26:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 26: agents argue then the debate resolves", 12),
        ["round 26:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 26: agents argue then the debate resolves", 16),
        ["round 26: agents", "argue then the", "debate resolves"],
    ),
    (("round 26: agents argue then the debate resolves", 24), ["round 26: agents argue", "then the debate resolves"]),
    (("round 26: agents argue then the debate resolves", 32), ["round 26: agents argue then the", "debate resolves"]),
    (
        ("round 26: the filter keeps only strong matches", 4),
        ["round", "26:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 26: the filter keeps only strong matches", 8),
        ["round", "26: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 26: the filter keeps only strong matches", 12),
        ["round 26:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 26: the filter keeps only strong matches", 16),
        ["round 26: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 26: the filter keeps only strong matches", 24), ["round 26: the filter", "keeps only strong", "matches"]),
    (("round 26: the filter keeps only strong matches", 32), ["round 26: the filter keeps only", "strong matches"]),
    (
        ("round 26: the model answers with a short reply", 4),
        ["round", "26:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 26: the model answers with a short reply", 8),
        ["round", "26: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 26: the model answers with a short reply", 12),
        ["round 26:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 26: the model answers with a short reply", 16),
        ["round 26: the", "model answers", "with a short", "reply"],
    ),
    (("round 26: the model answers with a short reply", 24), ["round 26: the model", "answers with a short", "reply"]),
    (("round 26: the model answers with a short reply", 32), ["round 26: the model answers with", "a short reply"]),
    (
        ("round 26: the recorder stores the reasoning trace", 4),
        ["round", "26:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 26: the recorder stores the reasoning trace", 8),
        ["round", "26: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 26: the recorder stores the reasoning trace", 12),
        ["round 26:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 26: the recorder stores the reasoning trace", 16),
        ["round 26: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 26: the recorder stores the reasoning trace", 24),
        ["round 26: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 26: the recorder stores the reasoning trace", 32),
        ["round 26: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 26: the angel watches the processor run", 4),
        ["round", "26:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 26: the angel watches the processor run", 8),
        ["round", "26: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 26: the angel watches the processor run", 12),
        ["round 26:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 26: the angel watches the processor run", 16), ["round 26: the", "angel watches", "the processor", "run"]),
    (("round 26: the angel watches the processor run", 24), ["round 26: the angel", "watches the processor", "run"]),
    (("round 26: the angel watches the processor run", 32), ["round 26: the angel watches the", "processor run"]),
    (
        ("round 26: angle of the vector decides the match", 4),
        ["round", "26:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 26: angle of the vector decides the match", 8),
        ["round", "26:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 26: angle of the vector decides the match", 12),
        ["round 26:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 26: angle of the vector decides the match", 16),
        ["round 26: angle", "of the vector", "decides the", "match"],
    ),
    (("round 26: angle of the vector decides the match", 24), ["round 26: angle of the", "vector decides the match"]),
    (("round 26: angle of the vector decides the match", 32), ["round 26: angle of the vector", "decides the match"]),
    (
        ("round 26: the candle burns twice as long at night", 4),
        ["round", "26:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 26: the candle burns twice as long at night", 8),
        ["round", "26: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 26: the candle burns twice as long at night", 12),
        ["round 26:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 26: the candle burns twice as long at night", 16),
        ["round 26: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 26: the candle burns twice as long at night", 24),
        ["round 26: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 26: the candle burns twice as long at night", 32),
        ["round 26: the candle burns twice", "as long at night"],
    ),
    (
        ("round 26: a mirror of the universe in one line", 4),
        ["round", "26:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 26: a mirror of the universe in one line", 8),
        ["round", "26: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 26: a mirror of the universe in one line", 12),
        ["round 26: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 26: a mirror of the universe in one line", 16),
        ["round 26: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 26: a mirror of the universe in one line", 24), ["round 26: a mirror of", "the universe in one line"]),
    (("round 26: a mirror of the universe in one line", 32), ["round 26: a mirror of the", "universe in one line"]),
    (
        ("round 26: the queue drains before the storm", 4),
        ["round", "26:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 26: the queue drains before the storm", 8),
        ["round", "26: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 26: the queue drains before the storm", 12), ["round 26:", "the queue", "drains", "before the", "storm"]),
    (("round 26: the queue drains before the storm", 16), ["round 26: the", "queue drains", "before the storm"]),
    (("round 26: the queue drains before the storm", 24), ["round 26: the queue", "drains before the storm"]),
    (("round 26: the queue drains before the storm", 32), ["round 26: the queue drains", "before the storm"]),
    (
        ("kitten26 sitting26 agent26 angle26 universe26 memory26", 6),
        ["kitten26", "sitting26", "agent26", "angle26", "universe26", "memory26"],
    ),
    (
        ("kitten26 sitting26 agent26 angle26 universe26 memory26", 10),
        ["kitten26", "sitting26", "agent26", "angle26", "universe26", "memory26"],
    ),
    (
        ("kitten26 sitting26 agent26 angle26 universe26 memory26", 18),
        ["kitten26 sitting26", "agent26 angle26", "universe26", "memory26"],
    ),
    (
        ("kitten26 sitting26 agent26 angle26 universe26 memory26", 28),
        ["kitten26 sitting26 agent26", "angle26 universe26 memory26"],
    ),
    (
        ("sitting26 agent26 angle26 universe26 memory26 stream26", 6),
        ["sitting26", "agent26", "angle26", "universe26", "memory26", "stream26"],
    ),
    (
        ("sitting26 agent26 angle26 universe26 memory26 stream26", 10),
        ["sitting26", "agent26", "angle26", "universe26", "memory26", "stream26"],
    ),
    (
        ("sitting26 agent26 angle26 universe26 memory26 stream26", 18),
        ["sitting26 agent26", "angle26 universe26", "memory26 stream26"],
    ),
    (
        ("sitting26 agent26 angle26 universe26 memory26 stream26", 28),
        ["sitting26 agent26 angle26", "universe26 memory26 stream26"],
    ),
    (
        ("agent26 angle26 universe26 memory26 stream26 context26", 6),
        ["agent26", "angle26", "universe26", "memory26", "stream26", "context26"],
    ),
    (
        ("agent26 angle26 universe26 memory26 stream26 context26", 10),
        ["agent26", "angle26", "universe26", "memory26", "stream26", "context26"],
    ),
    (
        ("agent26 angle26 universe26 memory26 stream26 context26", 18),
        ["agent26 angle26", "universe26", "memory26 stream26", "context26"],
    ),
    (
        ("agent26 angle26 universe26 memory26 stream26 context26", 28),
        ["agent26 angle26 universe26", "memory26 stream26 context26"],
    ),
    (
        ("angle26 universe26 memory26 stream26 context26 knowledge26", 6),
        ["angle26", "universe26", "memory26", "stream26", "context26", "knowledge26"],
    ),
    (
        ("angle26 universe26 memory26 stream26 context26 knowledge26", 10),
        ["angle26", "universe26", "memory26", "stream26", "context26", "knowledge26"],
    ),
    (
        ("angle26 universe26 memory26 stream26 context26 knowledge26", 18),
        ["angle26 universe26", "memory26 stream26", "context26", "knowledge26"],
    ),
    (
        ("angle26 universe26 memory26 stream26 context26 knowledge26", 28),
        ["angle26 universe26 memory26", "stream26 context26", "knowledge26"],
    ),
    (
        ("universe26 memory26 stream26 context26 knowledge26 vector26", 6),
        ["universe26", "memory26", "stream26", "context26", "knowledge26", "vector26"],
    ),
    (
        ("universe26 memory26 stream26 context26 knowledge26 vector26", 10),
        ["universe26", "memory26", "stream26", "context26", "knowledge26", "vector26"],
    ),
    (
        ("universe26 memory26 stream26 context26 knowledge26 vector26", 18),
        ["universe26", "memory26 stream26", "context26", "knowledge26", "vector26"],
    ),
    (
        ("universe26 memory26 stream26 context26 knowledge26 vector26", 28),
        ["universe26 memory26 stream26", "context26 knowledge26", "vector26"],
    ),
    (
        ("memory26 stream26 context26 knowledge26 vector26 processor26", 6),
        ["memory26", "stream26", "context26", "knowledge26", "vector26", "processor26"],
    ),
    (
        ("memory26 stream26 context26 knowledge26 vector26 processor26", 10),
        ["memory26", "stream26", "context26", "knowledge26", "vector26", "processor26"],
    ),
    (
        ("memory26 stream26 context26 knowledge26 vector26 processor26", 18),
        ["memory26 stream26", "context26", "knowledge26", "vector26", "processor26"],
    ),
    (
        ("memory26 stream26 context26 knowledge26 vector26 processor26", 28),
        ["memory26 stream26 context26", "knowledge26 vector26", "processor26"],
    ),
    (
        ("stream26 context26 knowledge26 vector26 processor26 reasoning26", 6),
        ["stream26", "context26", "knowledge26", "vector26", "processor26", "reasoning26"],
    ),
    (
        ("stream26 context26 knowledge26 vector26 processor26 reasoning26", 10),
        ["stream26", "context26", "knowledge26", "vector26", "processor26", "reasoning26"],
    ),
    (
        ("stream26 context26 knowledge26 vector26 processor26 reasoning26", 18),
        ["stream26 context26", "knowledge26", "vector26", "processor26", "reasoning26"],
    ),
    (
        ("stream26 context26 knowledge26 vector26 processor26 reasoning26", 28),
        ["stream26 context26", "knowledge26 vector26", "processor26 reasoning26"],
    ),
    (
        ("context26 knowledge26 vector26 processor26 reasoning26 machine26", 6),
        ["context26", "knowledge26", "vector26", "processor26", "reasoning26", "machine26"],
    ),
    (
        ("context26 knowledge26 vector26 processor26 reasoning26 machine26", 10),
        ["context26", "knowledge26", "vector26", "processor26", "reasoning26", "machine26"],
    ),
    (
        ("context26 knowledge26 vector26 processor26 reasoning26 machine26", 18),
        ["context26", "knowledge26", "vector26", "processor26", "reasoning26", "machine26"],
    ),
    (
        ("context26 knowledge26 vector26 processor26 reasoning26 machine26", 28),
        ["context26 knowledge26", "vector26 processor26", "reasoning26 machine26"],
    ),
    (
        ("knowledge26 vector26 processor26 reasoning26 machine26 learning26", 6),
        ["knowledge26", "vector26", "processor26", "reasoning26", "machine26", "learning26"],
    ),
    (
        ("knowledge26 vector26 processor26 reasoning26 machine26 learning26", 10),
        ["knowledge26", "vector26", "processor26", "reasoning26", "machine26", "learning26"],
    ),
    (
        ("knowledge26 vector26 processor26 reasoning26 machine26 learning26", 18),
        ["knowledge26", "vector26", "processor26", "reasoning26", "machine26", "learning26"],
    ),
    (
        ("knowledge26 vector26 processor26 reasoning26 machine26 learning26", 28),
        ["knowledge26 vector26", "processor26 reasoning26", "machine26 learning26"],
    ),
    (
        ("vector26 processor26 reasoning26 machine26 learning26 model26", 6),
        ["vector26", "processor26", "reasoning26", "machine26", "learning26", "model26"],
    ),
    (
        ("vector26 processor26 reasoning26 machine26 learning26 model26", 10),
        ["vector26", "processor26", "reasoning26", "machine26", "learning26", "model26"],
    ),
    (
        ("vector26 processor26 reasoning26 machine26 learning26 model26", 18),
        ["vector26", "processor26", "reasoning26", "machine26", "learning26 model26"],
    ),
    (
        ("vector26 processor26 reasoning26 machine26 learning26 model26", 28),
        ["vector26 processor26", "reasoning26 machine26", "learning26 model26"],
    ),
    (
        ("processor26 reasoning26 machine26 learning26 model26 token26", 6),
        ["processor26", "reasoning26", "machine26", "learning26", "model26", "token26"],
    ),
    (
        ("processor26 reasoning26 machine26 learning26 model26 token26", 10),
        ["processor26", "reasoning26", "machine26", "learning26", "model26", "token26"],
    ),
    (
        ("processor26 reasoning26 machine26 learning26 model26 token26", 18),
        ["processor26", "reasoning26", "machine26", "learning26 model26", "token26"],
    ),
    (
        ("processor26 reasoning26 machine26 learning26 model26 token26", 28),
        ["processor26 reasoning26", "machine26 learning26 model26", "token26"],
    ),
    (
        ("reasoning26 machine26 learning26 model26 token26 prompt26", 6),
        ["reasoning26", "machine26", "learning26", "model26", "token26", "prompt26"],
    ),
    (
        ("reasoning26 machine26 learning26 model26 token26 prompt26", 10),
        ["reasoning26", "machine26", "learning26", "model26", "token26", "prompt26"],
    ),
    (
        ("reasoning26 machine26 learning26 model26 token26 prompt26", 18),
        ["reasoning26", "machine26", "learning26 model26", "token26 prompt26"],
    ),
    (
        ("reasoning26 machine26 learning26 model26 token26 prompt26", 28),
        ["reasoning26 machine26", "learning26 model26 token26", "prompt26"],
    ),
    (
        ("machine26 learning26 model26 token26 prompt26 session26", 6),
        ["machine26", "learning26", "model26", "token26", "prompt26", "session26"],
    ),
    (
        ("machine26 learning26 model26 token26 prompt26 session26", 10),
        ["machine26", "learning26", "model26", "token26", "prompt26", "session26"],
    ),
    (
        ("machine26 learning26 model26 token26 prompt26 session26", 18),
        ["machine26", "learning26 model26", "token26 prompt26", "session26"],
    ),
    (
        ("machine26 learning26 model26 token26 prompt26 session26", 28),
        ["machine26 learning26 model26", "token26 prompt26 session26"],
    ),
    (
        ("learning26 model26 token26 prompt26 session26 library26", 6),
        ["learning26", "model26", "token26", "prompt26", "session26", "library26"],
    ),
    (
        ("learning26 model26 token26 prompt26 session26 library26", 10),
        ["learning26", "model26", "token26", "prompt26", "session26", "library26"],
    ),
    (
        ("learning26 model26 token26 prompt26 session26 library26", 18),
        ["learning26 model26", "token26 prompt26", "session26", "library26"],
    ),
    (
        ("learning26 model26 token26 prompt26 session26 library26", 28),
        ["learning26 model26 token26", "prompt26 session26 library26"],
    ),
    (
        ("model26 token26 prompt26 session26 library26 service26", 6),
        ["model26", "token26", "prompt26", "session26", "library26", "service26"],
    ),
    (
        ("model26 token26 prompt26 session26 library26 service26", 10),
        ["model26", "token26", "prompt26", "session26", "library26", "service26"],
    ),
    (
        ("model26 token26 prompt26 session26 library26 service26", 18),
        ["model26 token26", "prompt26 session26", "library26", "service26"],
    ),
    (
        ("model26 token26 prompt26 session26 library26 service26", 28),
        ["model26 token26 prompt26", "session26 library26", "service26"],
    ),
    (
        ("token26 prompt26 session26 library26 service26 gateway26", 6),
        ["token26", "prompt26", "session26", "library26", "service26", "gateway26"],
    ),
    (
        ("token26 prompt26 session26 library26 service26 gateway26", 10),
        ["token26", "prompt26", "session26", "library26", "service26", "gateway26"],
    ),
    (
        ("token26 prompt26 session26 library26 service26 gateway26", 18),
        ["token26 prompt26", "session26", "library26", "service26", "gateway26"],
    ),
    (
        ("token26 prompt26 session26 library26 service26 gateway26", 28),
        ["token26 prompt26 session26", "library26 service26", "gateway26"],
    ),
    (
        ("prompt26 session26 library26 service26 gateway26 storage26", 6),
        ["prompt26", "session26", "library26", "service26", "gateway26", "storage26"],
    ),
    (
        ("prompt26 session26 library26 service26 gateway26 storage26", 10),
        ["prompt26", "session26", "library26", "service26", "gateway26", "storage26"],
    ),
    (
        ("prompt26 session26 library26 service26 gateway26 storage26", 18),
        ["prompt26 session26", "library26", "service26", "gateway26", "storage26"],
    ),
    (
        ("prompt26 session26 library26 service26 gateway26 storage26", 28),
        ["prompt26 session26 library26", "service26 gateway26", "storage26"],
    ),
    (
        ("session26 library26 service26 gateway26 storage26 network26", 6),
        ["session26", "library26", "service26", "gateway26", "storage26", "network26"],
    ),
    (
        ("session26 library26 service26 gateway26 storage26 network26", 10),
        ["session26", "library26", "service26", "gateway26", "storage26", "network26"],
    ),
    (
        ("session26 library26 service26 gateway26 storage26 network26", 18),
        ["session26", "library26", "service26", "gateway26", "storage26", "network26"],
    ),
    (
        ("session26 library26 service26 gateway26 storage26 network26", 28),
        ["session26 library26", "service26 gateway26", "storage26 network26"],
    ),
    (
        ("library26 service26 gateway26 storage26 network26 latency26", 6),
        ["library26", "service26", "gateway26", "storage26", "network26", "latency26"],
    ),
    (
        ("library26 service26 gateway26 storage26 network26 latency26", 10),
        ["library26", "service26", "gateway26", "storage26", "network26", "latency26"],
    ),
    (
        ("library26 service26 gateway26 storage26 network26 latency26", 18),
        ["library26", "service26", "gateway26", "storage26", "network26", "latency26"],
    ),
    (
        ("library26 service26 gateway26 storage26 network26 latency26", 28),
        ["library26 service26", "gateway26 storage26", "network26 latency26"],
    ),
    (
        ("service26 gateway26 storage26 network26 latency26 buffer26", 6),
        ["service26", "gateway26", "storage26", "network26", "latency26", "buffer26"],
    ),
    (
        ("service26 gateway26 storage26 network26 latency26 buffer26", 10),
        ["service26", "gateway26", "storage26", "network26", "latency26", "buffer26"],
    ),
    (
        ("service26 gateway26 storage26 network26 latency26 buffer26", 18),
        ["service26", "gateway26", "storage26", "network26", "latency26 buffer26"],
    ),
    (
        ("service26 gateway26 storage26 network26 latency26 buffer26", 28),
        ["service26 gateway26", "storage26 network26", "latency26 buffer26"],
    ),
    (
        ("gateway26 storage26 network26 latency26 buffer26 queue26", 6),
        ["gateway26", "storage26", "network26", "latency26", "buffer26", "queue26"],
    ),
    (
        ("gateway26 storage26 network26 latency26 buffer26 queue26", 10),
        ["gateway26", "storage26", "network26", "latency26", "buffer26", "queue26"],
    ),
    (
        ("gateway26 storage26 network26 latency26 buffer26 queue26", 18),
        ["gateway26", "storage26", "network26", "latency26 buffer26", "queue26"],
    ),
    (
        ("gateway26 storage26 network26 latency26 buffer26 queue26", 28),
        ["gateway26 storage26", "network26 latency26 buffer26", "queue26"],
    ),
    (
        ("storage26 network26 latency26 buffer26 queue26 worker26", 6),
        ["storage26", "network26", "latency26", "buffer26", "queue26", "worker26"],
    ),
    (
        ("storage26 network26 latency26 buffer26 queue26 worker26", 10),
        ["storage26", "network26", "latency26", "buffer26", "queue26", "worker26"],
    ),
    (
        ("storage26 network26 latency26 buffer26 queue26 worker26", 18),
        ["storage26", "network26", "latency26 buffer26", "queue26 worker26"],
    ),
    (
        ("storage26 network26 latency26 buffer26 queue26 worker26", 28),
        ["storage26 network26", "latency26 buffer26 queue26", "worker26"],
    ),
    (
        ("network26 latency26 buffer26 queue26 worker26 kernel26", 6),
        ["network26", "latency26", "buffer26", "queue26", "worker26", "kernel26"],
    ),
    (
        ("network26 latency26 buffer26 queue26 worker26 kernel26", 10),
        ["network26", "latency26", "buffer26", "queue26", "worker26", "kernel26"],
    ),
    (
        ("network26 latency26 buffer26 queue26 worker26 kernel26", 18),
        ["network26", "latency26 buffer26", "queue26 worker26", "kernel26"],
    ),
    (
        ("network26 latency26 buffer26 queue26 worker26 kernel26", 28),
        ["network26 latency26 buffer26", "queue26 worker26 kernel26"],
    ),
    (
        ("latency26 buffer26 queue26 worker26 kernel26 signal26", 6),
        ["latency26", "buffer26", "queue26", "worker26", "kernel26", "signal26"],
    ),
    (
        ("latency26 buffer26 queue26 worker26 kernel26 signal26", 10),
        ["latency26", "buffer26", "queue26", "worker26", "kernel26", "signal26"],
    ),
    (
        ("latency26 buffer26 queue26 worker26 kernel26 signal26", 18),
        ["latency26 buffer26", "queue26 worker26", "kernel26 signal26"],
    ),
    (
        ("latency26 buffer26 queue26 worker26 kernel26 signal26", 28),
        ["latency26 buffer26 queue26", "worker26 kernel26 signal26"],
    ),
    (
        ("buffer26 queue26 worker26 kernel26 signal26 packet26", 6),
        ["buffer26", "queue26", "worker26", "kernel26", "signal26", "packet26"],
    ),
    (
        ("buffer26 queue26 worker26 kernel26 signal26 packet26", 10),
        ["buffer26", "queue26", "worker26", "kernel26", "signal26", "packet26"],
    ),
    (
        ("buffer26 queue26 worker26 kernel26 signal26 packet26", 18),
        ["buffer26 queue26", "worker26 kernel26", "signal26 packet26"],
    ),
    (
        ("buffer26 queue26 worker26 kernel26 signal26 packet26", 28),
        ["buffer26 queue26 worker26", "kernel26 signal26 packet26"],
    ),
    (
        ("queue26 worker26 kernel26 signal26 packet26 router26", 6),
        ["queue26", "worker26", "kernel26", "signal26", "packet26", "router26"],
    ),
    (
        ("queue26 worker26 kernel26 signal26 packet26 router26", 10),
        ["queue26", "worker26", "kernel26", "signal26", "packet26", "router26"],
    ),
    (
        ("queue26 worker26 kernel26 signal26 packet26 router26", 18),
        ["queue26 worker26", "kernel26 signal26", "packet26 router26"],
    ),
    (
        ("queue26 worker26 kernel26 signal26 packet26 router26", 28),
        ["queue26 worker26 kernel26", "signal26 packet26 router26"],
    ),
    (
        ("worker26 kernel26 signal26 packet26 router26 cluster26", 6),
        ["worker26", "kernel26", "signal26", "packet26", "router26", "cluster26"],
    ),
    (
        ("worker26 kernel26 signal26 packet26 router26 cluster26", 10),
        ["worker26", "kernel26", "signal26", "packet26", "router26", "cluster26"],
    ),
    (
        ("worker26 kernel26 signal26 packet26 router26 cluster26", 18),
        ["worker26 kernel26", "signal26 packet26", "router26 cluster26"],
    ),
    (
        ("worker26 kernel26 signal26 packet26 router26 cluster26", 28),
        ["worker26 kernel26 signal26", "packet26 router26 cluster26"],
    ),
    (
        ("kernel26 signal26 packet26 router26 cluster26 mirror26", 6),
        ["kernel26", "signal26", "packet26", "router26", "cluster26", "mirror26"],
    ),
    (
        ("kernel26 signal26 packet26 router26 cluster26 mirror26", 10),
        ["kernel26", "signal26", "packet26", "router26", "cluster26", "mirror26"],
    ),
    (
        ("kernel26 signal26 packet26 router26 cluster26 mirror26", 18),
        ["kernel26 signal26", "packet26 router26", "cluster26 mirror26"],
    ),
    (
        ("kernel26 signal26 packet26 router26 cluster26 mirror26", 28),
        ["kernel26 signal26 packet26", "router26 cluster26 mirror26"],
    ),
    (
        ("signal26 packet26 router26 cluster26 mirror26 filter26", 6),
        ["signal26", "packet26", "router26", "cluster26", "mirror26", "filter26"],
    ),
    (
        ("signal26 packet26 router26 cluster26 mirror26 filter26", 10),
        ["signal26", "packet26", "router26", "cluster26", "mirror26", "filter26"],
    ),
    (
        ("signal26 packet26 router26 cluster26 mirror26 filter26", 18),
        ["signal26 packet26", "router26 cluster26", "mirror26 filter26"],
    ),
    (
        ("signal26 packet26 router26 cluster26 mirror26 filter26", 28),
        ["signal26 packet26 router26", "cluster26 mirror26 filter26"],
    ),
    (
        ("packet26 router26 cluster26 mirror26 filter26 ranking26", 6),
        ["packet26", "router26", "cluster26", "mirror26", "filter26", "ranking26"],
    ),
    (
        ("packet26 router26 cluster26 mirror26 filter26 ranking26", 10),
        ["packet26", "router26", "cluster26", "mirror26", "filter26", "ranking26"],
    ),
    (
        ("packet26 router26 cluster26 mirror26 filter26 ranking26", 18),
        ["packet26 router26", "cluster26 mirror26", "filter26 ranking26"],
    ),
    (
        ("packet26 router26 cluster26 mirror26 filter26 ranking26", 28),
        ["packet26 router26 cluster26", "mirror26 filter26 ranking26"],
    ),
    (
        ("router26 cluster26 mirror26 filter26 ranking26 encoding26", 6),
        ["router26", "cluster26", "mirror26", "filter26", "ranking26", "encoding26"],
    ),
    (
        ("router26 cluster26 mirror26 filter26 ranking26 encoding26", 10),
        ["router26", "cluster26", "mirror26", "filter26", "ranking26", "encoding26"],
    ),
    (
        ("router26 cluster26 mirror26 filter26 ranking26 encoding26", 18),
        ["router26 cluster26", "mirror26 filter26", "ranking26", "encoding26"],
    ),
    (
        ("router26 cluster26 mirror26 filter26 ranking26 encoding26", 28),
        ["router26 cluster26 mirror26", "filter26 ranking26", "encoding26"],
    ),
    (
        ("cluster26 mirror26 filter26 ranking26 encoding26 mapping26", 6),
        ["cluster26", "mirror26", "filter26", "ranking26", "encoding26", "mapping26"],
    ),
    (
        ("cluster26 mirror26 filter26 ranking26 encoding26 mapping26", 10),
        ["cluster26", "mirror26", "filter26", "ranking26", "encoding26", "mapping26"],
    ),
    (
        ("cluster26 mirror26 filter26 ranking26 encoding26 mapping26", 18),
        ["cluster26 mirror26", "filter26 ranking26", "encoding26", "mapping26"],
    ),
    (
        ("cluster26 mirror26 filter26 ranking26 encoding26 mapping26", 28),
        ["cluster26 mirror26 filter26", "ranking26 encoding26", "mapping26"],
    ),
    (
        ("mirror26 filter26 ranking26 encoding26 mapping26 record26", 6),
        ["mirror26", "filter26", "ranking26", "encoding26", "mapping26", "record26"],
    ),
    (
        ("mirror26 filter26 ranking26 encoding26 mapping26 record26", 10),
        ["mirror26", "filter26", "ranking26", "encoding26", "mapping26", "record26"],
    ),
    (
        ("mirror26 filter26 ranking26 encoding26 mapping26 record26", 18),
        ["mirror26 filter26", "ranking26", "encoding26", "mapping26 record26"],
    ),
    (
        ("mirror26 filter26 ranking26 encoding26 mapping26 record26", 28),
        ["mirror26 filter26 ranking26", "encoding26 mapping26", "record26"],
    ),
    (
        ("filter26 ranking26 encoding26 mapping26 record26 candle26", 6),
        ["filter26", "ranking26", "encoding26", "mapping26", "record26", "candle26"],
    ),
    (
        ("filter26 ranking26 encoding26 mapping26 record26 candle26", 10),
        ["filter26", "ranking26", "encoding26", "mapping26", "record26", "candle26"],
    ),
    (
        ("filter26 ranking26 encoding26 mapping26 record26 candle26", 18),
        ["filter26 ranking26", "encoding26", "mapping26 record26", "candle26"],
    ),
    (
        ("filter26 ranking26 encoding26 mapping26 record26 candle26", 28),
        ["filter26 ranking26", "encoding26 mapping26", "record26 candle26"],
    ),
    (
        ("ranking26 encoding26 mapping26 record26 candle26 thread26", 6),
        ["ranking26", "encoding26", "mapping26", "record26", "candle26", "thread26"],
    ),
    (
        ("ranking26 encoding26 mapping26 record26 candle26 thread26", 10),
        ["ranking26", "encoding26", "mapping26", "record26", "candle26", "thread26"],
    ),
    (
        ("ranking26 encoding26 mapping26 record26 candle26 thread26", 18),
        ["ranking26", "encoding26", "mapping26 record26", "candle26 thread26"],
    ),
    (
        ("ranking26 encoding26 mapping26 record26 candle26 thread26", 28),
        ["ranking26 encoding26", "mapping26 record26 candle26", "thread26"],
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
