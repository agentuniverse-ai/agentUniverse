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
        ("round 95: the quick brown fox jumps over the lazy dog", 4),
        ["round", "95:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 95: the quick brown fox jumps over the lazy dog", 8),
        ["round", "95: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 95: the quick brown fox jumps over the lazy dog", 12),
        ["round 95:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 95: the quick brown fox jumps over the lazy dog", 16),
        ["round 95: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 95: the quick brown fox jumps over the lazy dog", 24),
        ["round 95: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 95: the quick brown fox jumps over the lazy dog", 32),
        ["round 95: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 95: agentuniverse is a framework for multi agents", 4),
        ["round", "95:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 95: agentuniverse is a framework for multi agents", 8),
        ["round", "95:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 95: agentuniverse is a framework for multi agents", 12),
        ["round 95:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 95: agentuniverse is a framework for multi agents", 16),
        ["round 95:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 95: agentuniverse is a framework for multi agents", 24),
        ["round 95: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 95: agentuniverse is a framework for multi agents", 32),
        ["round 95: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 95: knowledge stored as vectors enables retrieval", 4),
        ["round", "95:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 95: knowledge stored as vectors enables retrieval", 8),
        ["round", "95:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 95: knowledge stored as vectors enables retrieval", 12),
        ["round 95:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 95: knowledge stored as vectors enables retrieval", 16),
        ["round 95:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 95: knowledge stored as vectors enables retrieval", 24),
        ["round 95: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 95: knowledge stored as vectors enables retrieval", 32),
        ["round 95: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 95: the processor reads the record then stops", 4),
        ["round", "95:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 95: the processor reads the record then stops", 8),
        ["round", "95: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 95: the processor reads the record then stops", 12),
        ["round 95:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 95: the processor reads the record then stops", 16),
        ["round 95: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 95: the processor reads the record then stops", 24),
        ["round 95: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 95: the processor reads the record then stops", 32),
        ["round 95: the processor reads", "the record then stops"],
    ),
    (
        ("round 95: a worker pulls the next task from the queue", 4),
        ["round", "95:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 95: a worker pulls the next task from the queue", 8),
        ["round", "95: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 95: a worker pulls the next task from the queue", 12),
        ["round 95: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 95: a worker pulls the next task from the queue", 16),
        ["round 95: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 95: a worker pulls the next task from the queue", 24),
        ["round 95: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 95: a worker pulls the next task from the queue", 32),
        ["round 95: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 95: signals travel through the network layer", 4),
        ["round", "95:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 95: signals travel through the network layer", 8),
        ["round", "95:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 95: signals travel through the network layer", 12),
        ["round 95:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 95: signals travel through the network layer", 16),
        ["round 95:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 95: signals travel through the network layer", 24),
        ["round 95: signals travel", "through the network", "layer"],
    ),
    (
        ("round 95: signals travel through the network layer", 32),
        ["round 95: signals travel through", "the network layer"],
    ),
    (
        ("round 95: the gateway routes each request by policy", 4),
        ["round", "95:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 95: the gateway routes each request by policy", 8),
        ["round", "95: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 95: the gateway routes each request by policy", 12),
        ["round 95:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 95: the gateway routes each request by policy", 16),
        ["round 95: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 95: the gateway routes each request by policy", 24),
        ["round 95: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 95: the gateway routes each request by policy", 32),
        ["round 95: the gateway routes", "each request by policy"],
    ),
    (
        ("round 95: memory grows until the buffer is full", 4),
        ["round", "95:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 95: memory grows until the buffer is full", 8),
        ["round", "95:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 95: memory grows until the buffer is full", 12),
        ["round 95:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 95: memory grows until the buffer is full", 16),
        ["round 95: memory", "grows until the", "buffer is full"],
    ),
    (("round 95: memory grows until the buffer is full", 24), ["round 95: memory grows", "until the buffer is full"]),
    (("round 95: memory grows until the buffer is full", 32), ["round 95: memory grows until the", "buffer is full"]),
    (
        ("round 95: the cluster mirrors every packet twice", 4),
        ["round", "95:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 95: the cluster mirrors every packet twice", 8),
        ["round", "95: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 95: the cluster mirrors every packet twice", 12),
        ["round 95:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 95: the cluster mirrors every packet twice", 16),
        ["round 95: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 95: the cluster mirrors every packet twice", 24),
        ["round 95: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 95: the cluster mirrors every packet twice", 32), ["round 95: the cluster mirrors", "every packet twice"]),
    (
        ("round 95: ranking uses tokens learned from the corpus", 4),
        ["round", "95:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 95: ranking uses tokens learned from the corpus", 8),
        ["round", "95:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 95: ranking uses tokens learned from the corpus", 12),
        ["round 95:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 95: ranking uses tokens learned from the corpus", 16),
        ["round 95:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 95: ranking uses tokens learned from the corpus", 24),
        ["round 95: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 95: ranking uses tokens learned from the corpus", 32),
        ["round 95: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 95: a long session ends when the candle dies", 4),
        ["round", "95:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 95: a long session ends when the candle dies", 8),
        ["round", "95: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 95: a long session ends when the candle dies", 12),
        ["round 95: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 95: a long session ends when the candle dies", 16),
        ["round 95: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 95: a long session ends when the candle dies", 24),
        ["round 95: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 95: a long session ends when the candle dies", 32),
        ["round 95: a long session ends", "when the candle dies"],
    ),
    (
        ("round 95: encode the prompt then map the result", 4),
        ["round", "95:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 95: encode the prompt then map the result", 8),
        ["round", "95:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 95: encode the prompt then map the result", 12),
        ["round 95:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 95: encode the prompt then map the result", 16),
        ["round 95: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 95: encode the prompt then map the result", 24),
        ["round 95: encode the", "prompt then map the", "result"],
    ),
    (("round 95: encode the prompt then map the result", 32), ["round 95: encode the prompt then", "map the result"]),
    (
        ("round 95: the kernel wakes the worker at dawn", 4),
        ["round", "95:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 95: the kernel wakes the worker at dawn", 8),
        ["round", "95: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 95: the kernel wakes the worker at dawn", 12),
        ["round 95:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 95: the kernel wakes the worker at dawn", 16), ["round 95: the", "kernel wakes the", "worker at dawn"]),
    (("round 95: the kernel wakes the worker at dawn", 24), ["round 95: the kernel", "wakes the worker at dawn"]),
    (("round 95: the kernel wakes the worker at dawn", 32), ["round 95: the kernel wakes the", "worker at dawn"]),
    (
        ("round 95: service latency drops after the patch", 4),
        ["round", "95:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 95: service latency drops after the patch", 8),
        ["round", "95:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 95: service latency drops after the patch", 12),
        ["round 95:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 95: service latency drops after the patch", 16),
        ["round 95:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 95: service latency drops after the patch", 24),
        ["round 95: service", "latency drops after the", "patch"],
    ),
    (("round 95: service latency drops after the patch", 32), ["round 95: service latency drops", "after the patch"]),
    (
        ("round 95: the library caches every vector it sees", 4),
        ["round", "95:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 95: the library caches every vector it sees", 8),
        ["round", "95: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 95: the library caches every vector it sees", 12),
        ["round 95:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 95: the library caches every vector it sees", 16),
        ["round 95: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 95: the library caches every vector it sees", 24),
        ["round 95: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 95: the library caches every vector it sees", 32),
        ["round 95: the library caches", "every vector it sees"],
    ),
    (
        ("round 95: agents argue then the debate resolves", 4),
        ["round", "95:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 95: agents argue then the debate resolves", 8),
        ["round", "95:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 95: agents argue then the debate resolves", 12),
        ["round 95:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 95: agents argue then the debate resolves", 16),
        ["round 95: agents", "argue then the", "debate resolves"],
    ),
    (("round 95: agents argue then the debate resolves", 24), ["round 95: agents argue", "then the debate resolves"]),
    (("round 95: agents argue then the debate resolves", 32), ["round 95: agents argue then the", "debate resolves"]),
    (
        ("round 95: the filter keeps only strong matches", 4),
        ["round", "95:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 95: the filter keeps only strong matches", 8),
        ["round", "95: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 95: the filter keeps only strong matches", 12),
        ["round 95:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 95: the filter keeps only strong matches", 16),
        ["round 95: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 95: the filter keeps only strong matches", 24), ["round 95: the filter", "keeps only strong", "matches"]),
    (("round 95: the filter keeps only strong matches", 32), ["round 95: the filter keeps only", "strong matches"]),
    (
        ("round 95: the model answers with a short reply", 4),
        ["round", "95:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 95: the model answers with a short reply", 8),
        ["round", "95: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 95: the model answers with a short reply", 12),
        ["round 95:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 95: the model answers with a short reply", 16),
        ["round 95: the", "model answers", "with a short", "reply"],
    ),
    (("round 95: the model answers with a short reply", 24), ["round 95: the model", "answers with a short", "reply"]),
    (("round 95: the model answers with a short reply", 32), ["round 95: the model answers with", "a short reply"]),
    (
        ("round 95: the recorder stores the reasoning trace", 4),
        ["round", "95:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 95: the recorder stores the reasoning trace", 8),
        ["round", "95: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 95: the recorder stores the reasoning trace", 12),
        ["round 95:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 95: the recorder stores the reasoning trace", 16),
        ["round 95: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 95: the recorder stores the reasoning trace", 24),
        ["round 95: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 95: the recorder stores the reasoning trace", 32),
        ["round 95: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 95: the angel watches the processor run", 4),
        ["round", "95:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 95: the angel watches the processor run", 8),
        ["round", "95: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 95: the angel watches the processor run", 12),
        ["round 95:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 95: the angel watches the processor run", 16), ["round 95: the", "angel watches", "the processor", "run"]),
    (("round 95: the angel watches the processor run", 24), ["round 95: the angel", "watches the processor", "run"]),
    (("round 95: the angel watches the processor run", 32), ["round 95: the angel watches the", "processor run"]),
    (
        ("round 95: angle of the vector decides the match", 4),
        ["round", "95:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 95: angle of the vector decides the match", 8),
        ["round", "95:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 95: angle of the vector decides the match", 12),
        ["round 95:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 95: angle of the vector decides the match", 16),
        ["round 95: angle", "of the vector", "decides the", "match"],
    ),
    (("round 95: angle of the vector decides the match", 24), ["round 95: angle of the", "vector decides the match"]),
    (("round 95: angle of the vector decides the match", 32), ["round 95: angle of the vector", "decides the match"]),
    (
        ("round 95: the candle burns twice as long at night", 4),
        ["round", "95:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 95: the candle burns twice as long at night", 8),
        ["round", "95: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 95: the candle burns twice as long at night", 12),
        ["round 95:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 95: the candle burns twice as long at night", 16),
        ["round 95: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 95: the candle burns twice as long at night", 24),
        ["round 95: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 95: the candle burns twice as long at night", 32),
        ["round 95: the candle burns twice", "as long at night"],
    ),
    (
        ("round 95: a mirror of the universe in one line", 4),
        ["round", "95:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 95: a mirror of the universe in one line", 8),
        ["round", "95: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 95: a mirror of the universe in one line", 12),
        ["round 95: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 95: a mirror of the universe in one line", 16),
        ["round 95: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 95: a mirror of the universe in one line", 24), ["round 95: a mirror of", "the universe in one line"]),
    (("round 95: a mirror of the universe in one line", 32), ["round 95: a mirror of the", "universe in one line"]),
    (
        ("round 95: the queue drains before the storm", 4),
        ["round", "95:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 95: the queue drains before the storm", 8),
        ["round", "95: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 95: the queue drains before the storm", 12), ["round 95:", "the queue", "drains", "before the", "storm"]),
    (("round 95: the queue drains before the storm", 16), ["round 95: the", "queue drains", "before the storm"]),
    (("round 95: the queue drains before the storm", 24), ["round 95: the queue", "drains before the storm"]),
    (("round 95: the queue drains before the storm", 32), ["round 95: the queue drains", "before the storm"]),
    (
        ("kitten95 sitting95 agent95 angle95 universe95 memory95", 6),
        ["kitten95", "sitting95", "agent95", "angle95", "universe95", "memory95"],
    ),
    (
        ("kitten95 sitting95 agent95 angle95 universe95 memory95", 10),
        ["kitten95", "sitting95", "agent95", "angle95", "universe95", "memory95"],
    ),
    (
        ("kitten95 sitting95 agent95 angle95 universe95 memory95", 18),
        ["kitten95 sitting95", "agent95 angle95", "universe95", "memory95"],
    ),
    (
        ("kitten95 sitting95 agent95 angle95 universe95 memory95", 28),
        ["kitten95 sitting95 agent95", "angle95 universe95 memory95"],
    ),
    (
        ("sitting95 agent95 angle95 universe95 memory95 stream95", 6),
        ["sitting95", "agent95", "angle95", "universe95", "memory95", "stream95"],
    ),
    (
        ("sitting95 agent95 angle95 universe95 memory95 stream95", 10),
        ["sitting95", "agent95", "angle95", "universe95", "memory95", "stream95"],
    ),
    (
        ("sitting95 agent95 angle95 universe95 memory95 stream95", 18),
        ["sitting95 agent95", "angle95 universe95", "memory95 stream95"],
    ),
    (
        ("sitting95 agent95 angle95 universe95 memory95 stream95", 28),
        ["sitting95 agent95 angle95", "universe95 memory95 stream95"],
    ),
    (
        ("agent95 angle95 universe95 memory95 stream95 context95", 6),
        ["agent95", "angle95", "universe95", "memory95", "stream95", "context95"],
    ),
    (
        ("agent95 angle95 universe95 memory95 stream95 context95", 10),
        ["agent95", "angle95", "universe95", "memory95", "stream95", "context95"],
    ),
    (
        ("agent95 angle95 universe95 memory95 stream95 context95", 18),
        ["agent95 angle95", "universe95", "memory95 stream95", "context95"],
    ),
    (
        ("agent95 angle95 universe95 memory95 stream95 context95", 28),
        ["agent95 angle95 universe95", "memory95 stream95 context95"],
    ),
    (
        ("angle95 universe95 memory95 stream95 context95 knowledge95", 6),
        ["angle95", "universe95", "memory95", "stream95", "context95", "knowledge95"],
    ),
    (
        ("angle95 universe95 memory95 stream95 context95 knowledge95", 10),
        ["angle95", "universe95", "memory95", "stream95", "context95", "knowledge95"],
    ),
    (
        ("angle95 universe95 memory95 stream95 context95 knowledge95", 18),
        ["angle95 universe95", "memory95 stream95", "context95", "knowledge95"],
    ),
    (
        ("angle95 universe95 memory95 stream95 context95 knowledge95", 28),
        ["angle95 universe95 memory95", "stream95 context95", "knowledge95"],
    ),
    (
        ("universe95 memory95 stream95 context95 knowledge95 vector95", 6),
        ["universe95", "memory95", "stream95", "context95", "knowledge95", "vector95"],
    ),
    (
        ("universe95 memory95 stream95 context95 knowledge95 vector95", 10),
        ["universe95", "memory95", "stream95", "context95", "knowledge95", "vector95"],
    ),
    (
        ("universe95 memory95 stream95 context95 knowledge95 vector95", 18),
        ["universe95", "memory95 stream95", "context95", "knowledge95", "vector95"],
    ),
    (
        ("universe95 memory95 stream95 context95 knowledge95 vector95", 28),
        ["universe95 memory95 stream95", "context95 knowledge95", "vector95"],
    ),
    (
        ("memory95 stream95 context95 knowledge95 vector95 processor95", 6),
        ["memory95", "stream95", "context95", "knowledge95", "vector95", "processor95"],
    ),
    (
        ("memory95 stream95 context95 knowledge95 vector95 processor95", 10),
        ["memory95", "stream95", "context95", "knowledge95", "vector95", "processor95"],
    ),
    (
        ("memory95 stream95 context95 knowledge95 vector95 processor95", 18),
        ["memory95 stream95", "context95", "knowledge95", "vector95", "processor95"],
    ),
    (
        ("memory95 stream95 context95 knowledge95 vector95 processor95", 28),
        ["memory95 stream95 context95", "knowledge95 vector95", "processor95"],
    ),
    (
        ("stream95 context95 knowledge95 vector95 processor95 reasoning95", 6),
        ["stream95", "context95", "knowledge95", "vector95", "processor95", "reasoning95"],
    ),
    (
        ("stream95 context95 knowledge95 vector95 processor95 reasoning95", 10),
        ["stream95", "context95", "knowledge95", "vector95", "processor95", "reasoning95"],
    ),
    (
        ("stream95 context95 knowledge95 vector95 processor95 reasoning95", 18),
        ["stream95 context95", "knowledge95", "vector95", "processor95", "reasoning95"],
    ),
    (
        ("stream95 context95 knowledge95 vector95 processor95 reasoning95", 28),
        ["stream95 context95", "knowledge95 vector95", "processor95 reasoning95"],
    ),
    (
        ("context95 knowledge95 vector95 processor95 reasoning95 machine95", 6),
        ["context95", "knowledge95", "vector95", "processor95", "reasoning95", "machine95"],
    ),
    (
        ("context95 knowledge95 vector95 processor95 reasoning95 machine95", 10),
        ["context95", "knowledge95", "vector95", "processor95", "reasoning95", "machine95"],
    ),
    (
        ("context95 knowledge95 vector95 processor95 reasoning95 machine95", 18),
        ["context95", "knowledge95", "vector95", "processor95", "reasoning95", "machine95"],
    ),
    (
        ("context95 knowledge95 vector95 processor95 reasoning95 machine95", 28),
        ["context95 knowledge95", "vector95 processor95", "reasoning95 machine95"],
    ),
    (
        ("knowledge95 vector95 processor95 reasoning95 machine95 learning95", 6),
        ["knowledge95", "vector95", "processor95", "reasoning95", "machine95", "learning95"],
    ),
    (
        ("knowledge95 vector95 processor95 reasoning95 machine95 learning95", 10),
        ["knowledge95", "vector95", "processor95", "reasoning95", "machine95", "learning95"],
    ),
    (
        ("knowledge95 vector95 processor95 reasoning95 machine95 learning95", 18),
        ["knowledge95", "vector95", "processor95", "reasoning95", "machine95", "learning95"],
    ),
    (
        ("knowledge95 vector95 processor95 reasoning95 machine95 learning95", 28),
        ["knowledge95 vector95", "processor95 reasoning95", "machine95 learning95"],
    ),
    (
        ("vector95 processor95 reasoning95 machine95 learning95 model95", 6),
        ["vector95", "processor95", "reasoning95", "machine95", "learning95", "model95"],
    ),
    (
        ("vector95 processor95 reasoning95 machine95 learning95 model95", 10),
        ["vector95", "processor95", "reasoning95", "machine95", "learning95", "model95"],
    ),
    (
        ("vector95 processor95 reasoning95 machine95 learning95 model95", 18),
        ["vector95", "processor95", "reasoning95", "machine95", "learning95 model95"],
    ),
    (
        ("vector95 processor95 reasoning95 machine95 learning95 model95", 28),
        ["vector95 processor95", "reasoning95 machine95", "learning95 model95"],
    ),
    (
        ("processor95 reasoning95 machine95 learning95 model95 token95", 6),
        ["processor95", "reasoning95", "machine95", "learning95", "model95", "token95"],
    ),
    (
        ("processor95 reasoning95 machine95 learning95 model95 token95", 10),
        ["processor95", "reasoning95", "machine95", "learning95", "model95", "token95"],
    ),
    (
        ("processor95 reasoning95 machine95 learning95 model95 token95", 18),
        ["processor95", "reasoning95", "machine95", "learning95 model95", "token95"],
    ),
    (
        ("processor95 reasoning95 machine95 learning95 model95 token95", 28),
        ["processor95 reasoning95", "machine95 learning95 model95", "token95"],
    ),
    (
        ("reasoning95 machine95 learning95 model95 token95 prompt95", 6),
        ["reasoning95", "machine95", "learning95", "model95", "token95", "prompt95"],
    ),
    (
        ("reasoning95 machine95 learning95 model95 token95 prompt95", 10),
        ["reasoning95", "machine95", "learning95", "model95", "token95", "prompt95"],
    ),
    (
        ("reasoning95 machine95 learning95 model95 token95 prompt95", 18),
        ["reasoning95", "machine95", "learning95 model95", "token95 prompt95"],
    ),
    (
        ("reasoning95 machine95 learning95 model95 token95 prompt95", 28),
        ["reasoning95 machine95", "learning95 model95 token95", "prompt95"],
    ),
    (
        ("machine95 learning95 model95 token95 prompt95 session95", 6),
        ["machine95", "learning95", "model95", "token95", "prompt95", "session95"],
    ),
    (
        ("machine95 learning95 model95 token95 prompt95 session95", 10),
        ["machine95", "learning95", "model95", "token95", "prompt95", "session95"],
    ),
    (
        ("machine95 learning95 model95 token95 prompt95 session95", 18),
        ["machine95", "learning95 model95", "token95 prompt95", "session95"],
    ),
    (
        ("machine95 learning95 model95 token95 prompt95 session95", 28),
        ["machine95 learning95 model95", "token95 prompt95 session95"],
    ),
    (
        ("learning95 model95 token95 prompt95 session95 library95", 6),
        ["learning95", "model95", "token95", "prompt95", "session95", "library95"],
    ),
    (
        ("learning95 model95 token95 prompt95 session95 library95", 10),
        ["learning95", "model95", "token95", "prompt95", "session95", "library95"],
    ),
    (
        ("learning95 model95 token95 prompt95 session95 library95", 18),
        ["learning95 model95", "token95 prompt95", "session95", "library95"],
    ),
    (
        ("learning95 model95 token95 prompt95 session95 library95", 28),
        ["learning95 model95 token95", "prompt95 session95 library95"],
    ),
    (
        ("model95 token95 prompt95 session95 library95 service95", 6),
        ["model95", "token95", "prompt95", "session95", "library95", "service95"],
    ),
    (
        ("model95 token95 prompt95 session95 library95 service95", 10),
        ["model95", "token95", "prompt95", "session95", "library95", "service95"],
    ),
    (
        ("model95 token95 prompt95 session95 library95 service95", 18),
        ["model95 token95", "prompt95 session95", "library95", "service95"],
    ),
    (
        ("model95 token95 prompt95 session95 library95 service95", 28),
        ["model95 token95 prompt95", "session95 library95", "service95"],
    ),
    (
        ("token95 prompt95 session95 library95 service95 gateway95", 6),
        ["token95", "prompt95", "session95", "library95", "service95", "gateway95"],
    ),
    (
        ("token95 prompt95 session95 library95 service95 gateway95", 10),
        ["token95", "prompt95", "session95", "library95", "service95", "gateway95"],
    ),
    (
        ("token95 prompt95 session95 library95 service95 gateway95", 18),
        ["token95 prompt95", "session95", "library95", "service95", "gateway95"],
    ),
    (
        ("token95 prompt95 session95 library95 service95 gateway95", 28),
        ["token95 prompt95 session95", "library95 service95", "gateway95"],
    ),
    (
        ("prompt95 session95 library95 service95 gateway95 storage95", 6),
        ["prompt95", "session95", "library95", "service95", "gateway95", "storage95"],
    ),
    (
        ("prompt95 session95 library95 service95 gateway95 storage95", 10),
        ["prompt95", "session95", "library95", "service95", "gateway95", "storage95"],
    ),
    (
        ("prompt95 session95 library95 service95 gateway95 storage95", 18),
        ["prompt95 session95", "library95", "service95", "gateway95", "storage95"],
    ),
    (
        ("prompt95 session95 library95 service95 gateway95 storage95", 28),
        ["prompt95 session95 library95", "service95 gateway95", "storage95"],
    ),
    (
        ("session95 library95 service95 gateway95 storage95 network95", 6),
        ["session95", "library95", "service95", "gateway95", "storage95", "network95"],
    ),
    (
        ("session95 library95 service95 gateway95 storage95 network95", 10),
        ["session95", "library95", "service95", "gateway95", "storage95", "network95"],
    ),
    (
        ("session95 library95 service95 gateway95 storage95 network95", 18),
        ["session95", "library95", "service95", "gateway95", "storage95", "network95"],
    ),
    (
        ("session95 library95 service95 gateway95 storage95 network95", 28),
        ["session95 library95", "service95 gateway95", "storage95 network95"],
    ),
    (
        ("library95 service95 gateway95 storage95 network95 latency95", 6),
        ["library95", "service95", "gateway95", "storage95", "network95", "latency95"],
    ),
    (
        ("library95 service95 gateway95 storage95 network95 latency95", 10),
        ["library95", "service95", "gateway95", "storage95", "network95", "latency95"],
    ),
    (
        ("library95 service95 gateway95 storage95 network95 latency95", 18),
        ["library95", "service95", "gateway95", "storage95", "network95", "latency95"],
    ),
    (
        ("library95 service95 gateway95 storage95 network95 latency95", 28),
        ["library95 service95", "gateway95 storage95", "network95 latency95"],
    ),
    (
        ("service95 gateway95 storage95 network95 latency95 buffer95", 6),
        ["service95", "gateway95", "storage95", "network95", "latency95", "buffer95"],
    ),
    (
        ("service95 gateway95 storage95 network95 latency95 buffer95", 10),
        ["service95", "gateway95", "storage95", "network95", "latency95", "buffer95"],
    ),
    (
        ("service95 gateway95 storage95 network95 latency95 buffer95", 18),
        ["service95", "gateway95", "storage95", "network95", "latency95 buffer95"],
    ),
    (
        ("service95 gateway95 storage95 network95 latency95 buffer95", 28),
        ["service95 gateway95", "storage95 network95", "latency95 buffer95"],
    ),
    (
        ("gateway95 storage95 network95 latency95 buffer95 queue95", 6),
        ["gateway95", "storage95", "network95", "latency95", "buffer95", "queue95"],
    ),
    (
        ("gateway95 storage95 network95 latency95 buffer95 queue95", 10),
        ["gateway95", "storage95", "network95", "latency95", "buffer95", "queue95"],
    ),
    (
        ("gateway95 storage95 network95 latency95 buffer95 queue95", 18),
        ["gateway95", "storage95", "network95", "latency95 buffer95", "queue95"],
    ),
    (
        ("gateway95 storage95 network95 latency95 buffer95 queue95", 28),
        ["gateway95 storage95", "network95 latency95 buffer95", "queue95"],
    ),
    (
        ("storage95 network95 latency95 buffer95 queue95 worker95", 6),
        ["storage95", "network95", "latency95", "buffer95", "queue95", "worker95"],
    ),
    (
        ("storage95 network95 latency95 buffer95 queue95 worker95", 10),
        ["storage95", "network95", "latency95", "buffer95", "queue95", "worker95"],
    ),
    (
        ("storage95 network95 latency95 buffer95 queue95 worker95", 18),
        ["storage95", "network95", "latency95 buffer95", "queue95 worker95"],
    ),
    (
        ("storage95 network95 latency95 buffer95 queue95 worker95", 28),
        ["storage95 network95", "latency95 buffer95 queue95", "worker95"],
    ),
    (
        ("network95 latency95 buffer95 queue95 worker95 kernel95", 6),
        ["network95", "latency95", "buffer95", "queue95", "worker95", "kernel95"],
    ),
    (
        ("network95 latency95 buffer95 queue95 worker95 kernel95", 10),
        ["network95", "latency95", "buffer95", "queue95", "worker95", "kernel95"],
    ),
    (
        ("network95 latency95 buffer95 queue95 worker95 kernel95", 18),
        ["network95", "latency95 buffer95", "queue95 worker95", "kernel95"],
    ),
    (
        ("network95 latency95 buffer95 queue95 worker95 kernel95", 28),
        ["network95 latency95 buffer95", "queue95 worker95 kernel95"],
    ),
    (
        ("latency95 buffer95 queue95 worker95 kernel95 signal95", 6),
        ["latency95", "buffer95", "queue95", "worker95", "kernel95", "signal95"],
    ),
    (
        ("latency95 buffer95 queue95 worker95 kernel95 signal95", 10),
        ["latency95", "buffer95", "queue95", "worker95", "kernel95", "signal95"],
    ),
    (
        ("latency95 buffer95 queue95 worker95 kernel95 signal95", 18),
        ["latency95 buffer95", "queue95 worker95", "kernel95 signal95"],
    ),
    (
        ("latency95 buffer95 queue95 worker95 kernel95 signal95", 28),
        ["latency95 buffer95 queue95", "worker95 kernel95 signal95"],
    ),
    (
        ("buffer95 queue95 worker95 kernel95 signal95 packet95", 6),
        ["buffer95", "queue95", "worker95", "kernel95", "signal95", "packet95"],
    ),
    (
        ("buffer95 queue95 worker95 kernel95 signal95 packet95", 10),
        ["buffer95", "queue95", "worker95", "kernel95", "signal95", "packet95"],
    ),
    (
        ("buffer95 queue95 worker95 kernel95 signal95 packet95", 18),
        ["buffer95 queue95", "worker95 kernel95", "signal95 packet95"],
    ),
    (
        ("buffer95 queue95 worker95 kernel95 signal95 packet95", 28),
        ["buffer95 queue95 worker95", "kernel95 signal95 packet95"],
    ),
    (
        ("queue95 worker95 kernel95 signal95 packet95 router95", 6),
        ["queue95", "worker95", "kernel95", "signal95", "packet95", "router95"],
    ),
    (
        ("queue95 worker95 kernel95 signal95 packet95 router95", 10),
        ["queue95", "worker95", "kernel95", "signal95", "packet95", "router95"],
    ),
    (
        ("queue95 worker95 kernel95 signal95 packet95 router95", 18),
        ["queue95 worker95", "kernel95 signal95", "packet95 router95"],
    ),
    (
        ("queue95 worker95 kernel95 signal95 packet95 router95", 28),
        ["queue95 worker95 kernel95", "signal95 packet95 router95"],
    ),
    (
        ("worker95 kernel95 signal95 packet95 router95 cluster95", 6),
        ["worker95", "kernel95", "signal95", "packet95", "router95", "cluster95"],
    ),
    (
        ("worker95 kernel95 signal95 packet95 router95 cluster95", 10),
        ["worker95", "kernel95", "signal95", "packet95", "router95", "cluster95"],
    ),
    (
        ("worker95 kernel95 signal95 packet95 router95 cluster95", 18),
        ["worker95 kernel95", "signal95 packet95", "router95 cluster95"],
    ),
    (
        ("worker95 kernel95 signal95 packet95 router95 cluster95", 28),
        ["worker95 kernel95 signal95", "packet95 router95 cluster95"],
    ),
    (
        ("kernel95 signal95 packet95 router95 cluster95 mirror95", 6),
        ["kernel95", "signal95", "packet95", "router95", "cluster95", "mirror95"],
    ),
    (
        ("kernel95 signal95 packet95 router95 cluster95 mirror95", 10),
        ["kernel95", "signal95", "packet95", "router95", "cluster95", "mirror95"],
    ),
    (
        ("kernel95 signal95 packet95 router95 cluster95 mirror95", 18),
        ["kernel95 signal95", "packet95 router95", "cluster95 mirror95"],
    ),
    (
        ("kernel95 signal95 packet95 router95 cluster95 mirror95", 28),
        ["kernel95 signal95 packet95", "router95 cluster95 mirror95"],
    ),
    (
        ("signal95 packet95 router95 cluster95 mirror95 filter95", 6),
        ["signal95", "packet95", "router95", "cluster95", "mirror95", "filter95"],
    ),
    (
        ("signal95 packet95 router95 cluster95 mirror95 filter95", 10),
        ["signal95", "packet95", "router95", "cluster95", "mirror95", "filter95"],
    ),
    (
        ("signal95 packet95 router95 cluster95 mirror95 filter95", 18),
        ["signal95 packet95", "router95 cluster95", "mirror95 filter95"],
    ),
    (
        ("signal95 packet95 router95 cluster95 mirror95 filter95", 28),
        ["signal95 packet95 router95", "cluster95 mirror95 filter95"],
    ),
    (
        ("packet95 router95 cluster95 mirror95 filter95 ranking95", 6),
        ["packet95", "router95", "cluster95", "mirror95", "filter95", "ranking95"],
    ),
    (
        ("packet95 router95 cluster95 mirror95 filter95 ranking95", 10),
        ["packet95", "router95", "cluster95", "mirror95", "filter95", "ranking95"],
    ),
    (
        ("packet95 router95 cluster95 mirror95 filter95 ranking95", 18),
        ["packet95 router95", "cluster95 mirror95", "filter95 ranking95"],
    ),
    (
        ("packet95 router95 cluster95 mirror95 filter95 ranking95", 28),
        ["packet95 router95 cluster95", "mirror95 filter95 ranking95"],
    ),
    (
        ("router95 cluster95 mirror95 filter95 ranking95 encoding95", 6),
        ["router95", "cluster95", "mirror95", "filter95", "ranking95", "encoding95"],
    ),
    (
        ("router95 cluster95 mirror95 filter95 ranking95 encoding95", 10),
        ["router95", "cluster95", "mirror95", "filter95", "ranking95", "encoding95"],
    ),
    (
        ("router95 cluster95 mirror95 filter95 ranking95 encoding95", 18),
        ["router95 cluster95", "mirror95 filter95", "ranking95", "encoding95"],
    ),
    (
        ("router95 cluster95 mirror95 filter95 ranking95 encoding95", 28),
        ["router95 cluster95 mirror95", "filter95 ranking95", "encoding95"],
    ),
    (
        ("cluster95 mirror95 filter95 ranking95 encoding95 mapping95", 6),
        ["cluster95", "mirror95", "filter95", "ranking95", "encoding95", "mapping95"],
    ),
    (
        ("cluster95 mirror95 filter95 ranking95 encoding95 mapping95", 10),
        ["cluster95", "mirror95", "filter95", "ranking95", "encoding95", "mapping95"],
    ),
    (
        ("cluster95 mirror95 filter95 ranking95 encoding95 mapping95", 18),
        ["cluster95 mirror95", "filter95 ranking95", "encoding95", "mapping95"],
    ),
    (
        ("cluster95 mirror95 filter95 ranking95 encoding95 mapping95", 28),
        ["cluster95 mirror95 filter95", "ranking95 encoding95", "mapping95"],
    ),
    (
        ("mirror95 filter95 ranking95 encoding95 mapping95 record95", 6),
        ["mirror95", "filter95", "ranking95", "encoding95", "mapping95", "record95"],
    ),
    (
        ("mirror95 filter95 ranking95 encoding95 mapping95 record95", 10),
        ["mirror95", "filter95", "ranking95", "encoding95", "mapping95", "record95"],
    ),
    (
        ("mirror95 filter95 ranking95 encoding95 mapping95 record95", 18),
        ["mirror95 filter95", "ranking95", "encoding95", "mapping95 record95"],
    ),
    (
        ("mirror95 filter95 ranking95 encoding95 mapping95 record95", 28),
        ["mirror95 filter95 ranking95", "encoding95 mapping95", "record95"],
    ),
    (
        ("filter95 ranking95 encoding95 mapping95 record95 candle95", 6),
        ["filter95", "ranking95", "encoding95", "mapping95", "record95", "candle95"],
    ),
    (
        ("filter95 ranking95 encoding95 mapping95 record95 candle95", 10),
        ["filter95", "ranking95", "encoding95", "mapping95", "record95", "candle95"],
    ),
    (
        ("filter95 ranking95 encoding95 mapping95 record95 candle95", 18),
        ["filter95 ranking95", "encoding95", "mapping95 record95", "candle95"],
    ),
    (
        ("filter95 ranking95 encoding95 mapping95 record95 candle95", 28),
        ["filter95 ranking95", "encoding95 mapping95", "record95 candle95"],
    ),
    (
        ("ranking95 encoding95 mapping95 record95 candle95 thread95", 6),
        ["ranking95", "encoding95", "mapping95", "record95", "candle95", "thread95"],
    ),
    (
        ("ranking95 encoding95 mapping95 record95 candle95 thread95", 10),
        ["ranking95", "encoding95", "mapping95", "record95", "candle95", "thread95"],
    ),
    (
        ("ranking95 encoding95 mapping95 record95 candle95 thread95", 18),
        ["ranking95", "encoding95", "mapping95 record95", "candle95 thread95"],
    ),
    (
        ("ranking95 encoding95 mapping95 record95 candle95 thread95", 28),
        ["ranking95 encoding95", "mapping95 record95 candle95", "thread95"],
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
