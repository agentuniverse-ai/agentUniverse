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
        ("round 733: the quick brown fox jumps over the lazy dog", 4),
        ["round", "733:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 733: the quick brown fox jumps over the lazy dog", 8),
        ["round", "733: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 733: the quick brown fox jumps over the lazy dog", 12),
        ["round 733:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 733: the quick brown fox jumps over the lazy dog", 16),
        ["round 733: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 733: the quick brown fox jumps over the lazy dog", 24),
        ["round 733: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 733: the quick brown fox jumps over the lazy dog", 32),
        ["round 733: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 733: agentuniverse is a framework for multi agents", 4),
        ["round", "733:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 733: agentuniverse is a framework for multi agents", 8),
        ["round", "733:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 733: agentuniverse is a framework for multi agents", 12),
        ["round 733:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 733: agentuniverse is a framework for multi agents", 16),
        ["round 733:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 733: agentuniverse is a framework for multi agents", 24),
        ["round 733: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 733: agentuniverse is a framework for multi agents", 32),
        ["round 733: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 733: knowledge stored as vectors enables retrieval", 4),
        ["round", "733:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 733: knowledge stored as vectors enables retrieval", 8),
        ["round", "733:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 733: knowledge stored as vectors enables retrieval", 12),
        ["round 733:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 733: knowledge stored as vectors enables retrieval", 16),
        ["round 733:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 733: knowledge stored as vectors enables retrieval", 24),
        ["round 733: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 733: knowledge stored as vectors enables retrieval", 32),
        ["round 733: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 733: the processor reads the record then stops", 4),
        ["round", "733:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 733: the processor reads the record then stops", 8),
        ["round", "733: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 733: the processor reads the record then stops", 12),
        ["round 733:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 733: the processor reads the record then stops", 16),
        ["round 733: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 733: the processor reads the record then stops", 24),
        ["round 733: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 733: the processor reads the record then stops", 32),
        ["round 733: the processor reads", "the record then stops"],
    ),
    (
        ("round 733: a worker pulls the next task from the queue", 4),
        ["round", "733:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 733: a worker pulls the next task from the queue", 8),
        ["round", "733: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 733: a worker pulls the next task from the queue", 12),
        ["round 733: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 733: a worker pulls the next task from the queue", 16),
        ["round 733: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 733: a worker pulls the next task from the queue", 24),
        ["round 733: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 733: a worker pulls the next task from the queue", 32),
        ["round 733: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 733: signals travel through the network layer", 4),
        ["round", "733:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 733: signals travel through the network layer", 8),
        ["round", "733:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 733: signals travel through the network layer", 12),
        ["round 733:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 733: signals travel through the network layer", 16),
        ["round 733:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 733: signals travel through the network layer", 24),
        ["round 733: signals", "travel through the", "network layer"],
    ),
    (
        ("round 733: signals travel through the network layer", 32),
        ["round 733: signals travel", "through the network layer"],
    ),
    (
        ("round 733: the gateway routes each request by policy", 4),
        ["round", "733:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 733: the gateway routes each request by policy", 8),
        ["round", "733: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 733: the gateway routes each request by policy", 12),
        ["round 733:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 733: the gateway routes each request by policy", 16),
        ["round 733: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 733: the gateway routes each request by policy", 24),
        ["round 733: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 733: the gateway routes each request by policy", 32),
        ["round 733: the gateway routes", "each request by policy"],
    ),
    (
        ("round 733: memory grows until the buffer is full", 4),
        ["round", "733:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 733: memory grows until the buffer is full", 8),
        ["round", "733:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 733: memory grows until the buffer is full", 12),
        ["round 733:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 733: memory grows until the buffer is full", 16),
        ["round 733:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 733: memory grows until the buffer is full", 24), ["round 733: memory grows", "until the buffer is full"]),
    (("round 733: memory grows until the buffer is full", 32), ["round 733: memory grows until", "the buffer is full"]),
    (
        ("round 733: the cluster mirrors every packet twice", 4),
        ["round", "733:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 733: the cluster mirrors every packet twice", 8),
        ["round", "733: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 733: the cluster mirrors every packet twice", 12),
        ["round 733:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 733: the cluster mirrors every packet twice", 16),
        ["round 733: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 733: the cluster mirrors every packet twice", 24),
        ["round 733: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 733: the cluster mirrors every packet twice", 32),
        ["round 733: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 733: ranking uses tokens learned from the corpus", 4),
        ["round", "733:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 733: ranking uses tokens learned from the corpus", 8),
        ["round", "733:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 733: ranking uses tokens learned from the corpus", 12),
        ["round 733:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 733: ranking uses tokens learned from the corpus", 16),
        ["round 733:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 733: ranking uses tokens learned from the corpus", 24),
        ["round 733: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 733: ranking uses tokens learned from the corpus", 32),
        ["round 733: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 733: a long session ends when the candle dies", 4),
        ["round", "733:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 733: a long session ends when the candle dies", 8),
        ["round", "733: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 733: a long session ends when the candle dies", 12),
        ["round 733: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 733: a long session ends when the candle dies", 16),
        ["round 733: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 733: a long session ends when the candle dies", 24),
        ["round 733: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 733: a long session ends when the candle dies", 32),
        ["round 733: a long session ends", "when the candle dies"],
    ),
    (
        ("round 733: encode the prompt then map the result", 4),
        ["round", "733:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 733: encode the prompt then map the result", 8),
        ["round", "733:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 733: encode the prompt then map the result", 12),
        ["round 733:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 733: encode the prompt then map the result", 16),
        ["round 733:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 733: encode the prompt then map the result", 24),
        ["round 733: encode the", "prompt then map the", "result"],
    ),
    (("round 733: encode the prompt then map the result", 32), ["round 733: encode the prompt", "then map the result"]),
    (
        ("round 733: the kernel wakes the worker at dawn", 4),
        ["round", "733:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 733: the kernel wakes the worker at dawn", 8),
        ["round", "733: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 733: the kernel wakes the worker at dawn", 12),
        ["round 733:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 733: the kernel wakes the worker at dawn", 16), ["round 733: the", "kernel wakes the", "worker at dawn"]),
    (("round 733: the kernel wakes the worker at dawn", 24), ["round 733: the kernel", "wakes the worker at dawn"]),
    (("round 733: the kernel wakes the worker at dawn", 32), ["round 733: the kernel wakes the", "worker at dawn"]),
    (
        ("round 733: service latency drops after the patch", 4),
        ["round", "733:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 733: service latency drops after the patch", 8),
        ["round", "733:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 733: service latency drops after the patch", 12),
        ["round 733:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 733: service latency drops after the patch", 16),
        ["round 733:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 733: service latency drops after the patch", 24),
        ["round 733: service", "latency drops after the", "patch"],
    ),
    (("round 733: service latency drops after the patch", 32), ["round 733: service latency drops", "after the patch"]),
    (
        ("round 733: the library caches every vector it sees", 4),
        ["round", "733:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 733: the library caches every vector it sees", 8),
        ["round", "733: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 733: the library caches every vector it sees", 12),
        ["round 733:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 733: the library caches every vector it sees", 16),
        ["round 733: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 733: the library caches every vector it sees", 24),
        ["round 733: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 733: the library caches every vector it sees", 32),
        ["round 733: the library caches", "every vector it sees"],
    ),
    (
        ("round 733: agents argue then the debate resolves", 4),
        ["round", "733:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 733: agents argue then the debate resolves", 8),
        ["round", "733:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 733: agents argue then the debate resolves", 12),
        ["round 733:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 733: agents argue then the debate resolves", 16),
        ["round 733:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 733: agents argue then the debate resolves", 24), ["round 733: agents argue", "then the debate resolves"]),
    (("round 733: agents argue then the debate resolves", 32), ["round 733: agents argue then the", "debate resolves"]),
    (
        ("round 733: the filter keeps only strong matches", 4),
        ["round", "733:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 733: the filter keeps only strong matches", 8),
        ["round", "733: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 733: the filter keeps only strong matches", 12),
        ["round 733:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 733: the filter keeps only strong matches", 16),
        ["round 733: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 733: the filter keeps only strong matches", 24),
        ["round 733: the filter", "keeps only strong", "matches"],
    ),
    (("round 733: the filter keeps only strong matches", 32), ["round 733: the filter keeps only", "strong matches"]),
    (
        ("round 733: the model answers with a short reply", 4),
        ["round", "733:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 733: the model answers with a short reply", 8),
        ["round", "733: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 733: the model answers with a short reply", 12),
        ["round 733:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 733: the model answers with a short reply", 16),
        ["round 733: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 733: the model answers with a short reply", 24),
        ["round 733: the model", "answers with a short", "reply"],
    ),
    (("round 733: the model answers with a short reply", 32), ["round 733: the model answers", "with a short reply"]),
    (
        ("round 733: the recorder stores the reasoning trace", 4),
        ["round", "733:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 733: the recorder stores the reasoning trace", 8),
        ["round", "733: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 733: the recorder stores the reasoning trace", 12),
        ["round 733:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 733: the recorder stores the reasoning trace", 16),
        ["round 733: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 733: the recorder stores the reasoning trace", 24),
        ["round 733: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 733: the recorder stores the reasoning trace", 32),
        ["round 733: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 733: the angel watches the processor run", 4),
        ["round", "733:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 733: the angel watches the processor run", 8),
        ["round", "733: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 733: the angel watches the processor run", 12),
        ["round 733:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 733: the angel watches the processor run", 16),
        ["round 733: the", "angel watches", "the processor", "run"],
    ),
    (("round 733: the angel watches the processor run", 24), ["round 733: the angel", "watches the processor", "run"]),
    (("round 733: the angel watches the processor run", 32), ["round 733: the angel watches the", "processor run"]),
    (
        ("round 733: angle of the vector decides the match", 4),
        ["round", "733:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 733: angle of the vector decides the match", 8),
        ["round", "733:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 733: angle of the vector decides the match", 12),
        ["round 733:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 733: angle of the vector decides the match", 16),
        ["round 733: angle", "of the vector", "decides the", "match"],
    ),
    (("round 733: angle of the vector decides the match", 24), ["round 733: angle of the", "vector decides the match"]),
    (("round 733: angle of the vector decides the match", 32), ["round 733: angle of the vector", "decides the match"]),
    (
        ("round 733: the candle burns twice as long at night", 4),
        ["round", "733:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 733: the candle burns twice as long at night", 8),
        ["round", "733: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 733: the candle burns twice as long at night", 12),
        ["round 733:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 733: the candle burns twice as long at night", 16),
        ["round 733: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 733: the candle burns twice as long at night", 24),
        ["round 733: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 733: the candle burns twice as long at night", 32),
        ["round 733: the candle burns", "twice as long at night"],
    ),
    (
        ("round 733: a mirror of the universe in one line", 4),
        ["round", "733:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 733: a mirror of the universe in one line", 8),
        ["round", "733: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 733: a mirror of the universe in one line", 12),
        ["round 733: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 733: a mirror of the universe in one line", 16),
        ["round 733: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 733: a mirror of the universe in one line", 24), ["round 733: a mirror of", "the universe in one line"]),
    (("round 733: a mirror of the universe in one line", 32), ["round 733: a mirror of the", "universe in one line"]),
    (
        ("round 733: the queue drains before the storm", 4),
        ["round", "733:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 733: the queue drains before the storm", 8),
        ["round", "733: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 733: the queue drains before the storm", 12),
        ["round 733:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 733: the queue drains before the storm", 16), ["round 733: the", "queue drains", "before the storm"]),
    (("round 733: the queue drains before the storm", 24), ["round 733: the queue", "drains before the storm"]),
    (("round 733: the queue drains before the storm", 32), ["round 733: the queue drains", "before the storm"]),
    (
        ("kitten733 sitting733 agent733 angle733 universe733 memory733", 6),
        ["kitten733", "sitting733", "agent733", "angle733", "universe733", "memory733"],
    ),
    (
        ("kitten733 sitting733 agent733 angle733 universe733 memory733", 10),
        ["kitten733", "sitting733", "agent733", "angle733", "universe733", "memory733"],
    ),
    (
        ("kitten733 sitting733 agent733 angle733 universe733 memory733", 18),
        ["kitten733", "sitting733", "agent733 angle733", "universe733", "memory733"],
    ),
    (
        ("kitten733 sitting733 agent733 angle733 universe733 memory733", 28),
        ["kitten733 sitting733", "agent733 angle733", "universe733 memory733"],
    ),
    (
        ("sitting733 agent733 angle733 universe733 memory733 stream733", 6),
        ["sitting733", "agent733", "angle733", "universe733", "memory733", "stream733"],
    ),
    (
        ("sitting733 agent733 angle733 universe733 memory733 stream733", 10),
        ["sitting733", "agent733", "angle733", "universe733", "memory733", "stream733"],
    ),
    (
        ("sitting733 agent733 angle733 universe733 memory733 stream733", 18),
        ["sitting733", "agent733 angle733", "universe733", "memory733", "stream733"],
    ),
    (
        ("sitting733 agent733 angle733 universe733 memory733 stream733", 28),
        ["sitting733 agent733 angle733", "universe733 memory733", "stream733"],
    ),
    (
        ("agent733 angle733 universe733 memory733 stream733 context733", 6),
        ["agent733", "angle733", "universe733", "memory733", "stream733", "context733"],
    ),
    (
        ("agent733 angle733 universe733 memory733 stream733 context733", 10),
        ["agent733", "angle733", "universe733", "memory733", "stream733", "context733"],
    ),
    (
        ("agent733 angle733 universe733 memory733 stream733 context733", 18),
        ["agent733 angle733", "universe733", "memory733", "stream733", "context733"],
    ),
    (
        ("agent733 angle733 universe733 memory733 stream733 context733", 28),
        ["agent733 angle733", "universe733 memory733", "stream733 context733"],
    ),
    (
        ("angle733 universe733 memory733 stream733 context733 knowledge733", 6),
        ["angle733", "universe733", "memory733", "stream733", "context733", "knowledge733"],
    ),
    (
        ("angle733 universe733 memory733 stream733 context733 knowledge733", 10),
        ["angle733", "universe733", "memory733", "stream733", "context733", "knowledge733"],
    ),
    (
        ("angle733 universe733 memory733 stream733 context733 knowledge733", 18),
        ["angle733", "universe733", "memory733", "stream733", "context733", "knowledge733"],
    ),
    (
        ("angle733 universe733 memory733 stream733 context733 knowledge733", 28),
        ["angle733 universe733", "memory733 stream733", "context733 knowledge733"],
    ),
    (
        ("universe733 memory733 stream733 context733 knowledge733 vector733", 6),
        ["universe733", "memory733", "stream733", "context733", "knowledge733", "vector733"],
    ),
    (
        ("universe733 memory733 stream733 context733 knowledge733 vector733", 10),
        ["universe733", "memory733", "stream733", "context733", "knowledge733", "vector733"],
    ),
    (
        ("universe733 memory733 stream733 context733 knowledge733 vector733", 18),
        ["universe733", "memory733", "stream733", "context733", "knowledge733", "vector733"],
    ),
    (
        ("universe733 memory733 stream733 context733 knowledge733 vector733", 28),
        ["universe733 memory733", "stream733 context733", "knowledge733 vector733"],
    ),
    (
        ("memory733 stream733 context733 knowledge733 vector733 processor733", 6),
        ["memory733", "stream733", "context733", "knowledge733", "vector733", "processor733"],
    ),
    (
        ("memory733 stream733 context733 knowledge733 vector733 processor733", 10),
        ["memory733", "stream733", "context733", "knowledge733", "vector733", "processor733"],
    ),
    (
        ("memory733 stream733 context733 knowledge733 vector733 processor733", 18),
        ["memory733", "stream733", "context733", "knowledge733", "vector733", "processor733"],
    ),
    (
        ("memory733 stream733 context733 knowledge733 vector733 processor733", 28),
        ["memory733 stream733", "context733 knowledge733", "vector733 processor733"],
    ),
    (
        ("stream733 context733 knowledge733 vector733 processor733 reasoning733", 6),
        ["stream733", "context733", "knowledge733", "vector733", "processor733", "reasoning733"],
    ),
    (
        ("stream733 context733 knowledge733 vector733 processor733 reasoning733", 10),
        ["stream733", "context733", "knowledge733", "vector733", "processor733", "reasoning733"],
    ),
    (
        ("stream733 context733 knowledge733 vector733 processor733 reasoning733", 18),
        ["stream733", "context733", "knowledge733", "vector733", "processor733", "reasoning733"],
    ),
    (
        ("stream733 context733 knowledge733 vector733 processor733 reasoning733", 28),
        ["stream733 context733", "knowledge733 vector733", "processor733 reasoning733"],
    ),
    (
        ("context733 knowledge733 vector733 processor733 reasoning733 machine733", 6),
        ["context733", "knowledge733", "vector733", "processor733", "reasoning733", "machine733"],
    ),
    (
        ("context733 knowledge733 vector733 processor733 reasoning733 machine733", 10),
        ["context733", "knowledge733", "vector733", "processor733", "reasoning733", "machine733"],
    ),
    (
        ("context733 knowledge733 vector733 processor733 reasoning733 machine733", 18),
        ["context733", "knowledge733", "vector733", "processor733", "reasoning733", "machine733"],
    ),
    (
        ("context733 knowledge733 vector733 processor733 reasoning733 machine733", 28),
        ["context733 knowledge733", "vector733 processor733", "reasoning733 machine733"],
    ),
    (
        ("knowledge733 vector733 processor733 reasoning733 machine733 learning733", 6),
        ["knowledge733", "vector733", "processor733", "reasoning733", "machine733", "learning733"],
    ),
    (
        ("knowledge733 vector733 processor733 reasoning733 machine733 learning733", 10),
        ["knowledge733", "vector733", "processor733", "reasoning733", "machine733", "learning733"],
    ),
    (
        ("knowledge733 vector733 processor733 reasoning733 machine733 learning733", 18),
        ["knowledge733", "vector733", "processor733", "reasoning733", "machine733", "learning733"],
    ),
    (
        ("knowledge733 vector733 processor733 reasoning733 machine733 learning733", 28),
        ["knowledge733 vector733", "processor733 reasoning733", "machine733 learning733"],
    ),
    (
        ("vector733 processor733 reasoning733 machine733 learning733 model733", 6),
        ["vector733", "processor733", "reasoning733", "machine733", "learning733", "model733"],
    ),
    (
        ("vector733 processor733 reasoning733 machine733 learning733 model733", 10),
        ["vector733", "processor733", "reasoning733", "machine733", "learning733", "model733"],
    ),
    (
        ("vector733 processor733 reasoning733 machine733 learning733 model733", 18),
        ["vector733", "processor733", "reasoning733", "machine733", "learning733", "model733"],
    ),
    (
        ("vector733 processor733 reasoning733 machine733 learning733 model733", 28),
        ["vector733 processor733", "reasoning733 machine733", "learning733 model733"],
    ),
    (
        ("processor733 reasoning733 machine733 learning733 model733 token733", 6),
        ["processor733", "reasoning733", "machine733", "learning733", "model733", "token733"],
    ),
    (
        ("processor733 reasoning733 machine733 learning733 model733 token733", 10),
        ["processor733", "reasoning733", "machine733", "learning733", "model733", "token733"],
    ),
    (
        ("processor733 reasoning733 machine733 learning733 model733 token733", 18),
        ["processor733", "reasoning733", "machine733", "learning733", "model733 token733"],
    ),
    (
        ("processor733 reasoning733 machine733 learning733 model733 token733", 28),
        ["processor733 reasoning733", "machine733 learning733", "model733 token733"],
    ),
    (
        ("reasoning733 machine733 learning733 model733 token733 prompt733", 6),
        ["reasoning733", "machine733", "learning733", "model733", "token733", "prompt733"],
    ),
    (
        ("reasoning733 machine733 learning733 model733 token733 prompt733", 10),
        ["reasoning733", "machine733", "learning733", "model733", "token733", "prompt733"],
    ),
    (
        ("reasoning733 machine733 learning733 model733 token733 prompt733", 18),
        ["reasoning733", "machine733", "learning733", "model733 token733", "prompt733"],
    ),
    (
        ("reasoning733 machine733 learning733 model733 token733 prompt733", 28),
        ["reasoning733 machine733", "learning733 model733", "token733 prompt733"],
    ),
    (
        ("machine733 learning733 model733 token733 prompt733 session733", 6),
        ["machine733", "learning733", "model733", "token733", "prompt733", "session733"],
    ),
    (
        ("machine733 learning733 model733 token733 prompt733 session733", 10),
        ["machine733", "learning733", "model733", "token733", "prompt733", "session733"],
    ),
    (
        ("machine733 learning733 model733 token733 prompt733 session733", 18),
        ["machine733", "learning733", "model733 token733", "prompt733", "session733"],
    ),
    (
        ("machine733 learning733 model733 token733 prompt733 session733", 28),
        ["machine733 learning733", "model733 token733 prompt733", "session733"],
    ),
    (
        ("learning733 model733 token733 prompt733 session733 library733", 6),
        ["learning733", "model733", "token733", "prompt733", "session733", "library733"],
    ),
    (
        ("learning733 model733 token733 prompt733 session733 library733", 10),
        ["learning733", "model733", "token733", "prompt733", "session733", "library733"],
    ),
    (
        ("learning733 model733 token733 prompt733 session733 library733", 18),
        ["learning733", "model733 token733", "prompt733", "session733", "library733"],
    ),
    (
        ("learning733 model733 token733 prompt733 session733 library733", 28),
        ["learning733 model733", "token733 prompt733", "session733 library733"],
    ),
    (
        ("model733 token733 prompt733 session733 library733 service733", 6),
        ["model733", "token733", "prompt733", "session733", "library733", "service733"],
    ),
    (
        ("model733 token733 prompt733 session733 library733 service733", 10),
        ["model733", "token733", "prompt733", "session733", "library733", "service733"],
    ),
    (
        ("model733 token733 prompt733 session733 library733 service733", 18),
        ["model733 token733", "prompt733", "session733", "library733", "service733"],
    ),
    (
        ("model733 token733 prompt733 session733 library733 service733", 28),
        ["model733 token733 prompt733", "session733 library733", "service733"],
    ),
    (
        ("token733 prompt733 session733 library733 service733 gateway733", 6),
        ["token733", "prompt733", "session733", "library733", "service733", "gateway733"],
    ),
    (
        ("token733 prompt733 session733 library733 service733 gateway733", 10),
        ["token733", "prompt733", "session733", "library733", "service733", "gateway733"],
    ),
    (
        ("token733 prompt733 session733 library733 service733 gateway733", 18),
        ["token733 prompt733", "session733", "library733", "service733", "gateway733"],
    ),
    (
        ("token733 prompt733 session733 library733 service733 gateway733", 28),
        ["token733 prompt733", "session733 library733", "service733 gateway733"],
    ),
    (
        ("prompt733 session733 library733 service733 gateway733 storage733", 6),
        ["prompt733", "session733", "library733", "service733", "gateway733", "storage733"],
    ),
    (
        ("prompt733 session733 library733 service733 gateway733 storage733", 10),
        ["prompt733", "session733", "library733", "service733", "gateway733", "storage733"],
    ),
    (
        ("prompt733 session733 library733 service733 gateway733 storage733", 18),
        ["prompt733", "session733", "library733", "service733", "gateway733", "storage733"],
    ),
    (
        ("prompt733 session733 library733 service733 gateway733 storage733", 28),
        ["prompt733 session733", "library733 service733", "gateway733 storage733"],
    ),
    (
        ("session733 library733 service733 gateway733 storage733 network733", 6),
        ["session733", "library733", "service733", "gateway733", "storage733", "network733"],
    ),
    (
        ("session733 library733 service733 gateway733 storage733 network733", 10),
        ["session733", "library733", "service733", "gateway733", "storage733", "network733"],
    ),
    (
        ("session733 library733 service733 gateway733 storage733 network733", 18),
        ["session733", "library733", "service733", "gateway733", "storage733", "network733"],
    ),
    (
        ("session733 library733 service733 gateway733 storage733 network733", 28),
        ["session733 library733", "service733 gateway733", "storage733 network733"],
    ),
    (
        ("library733 service733 gateway733 storage733 network733 latency733", 6),
        ["library733", "service733", "gateway733", "storage733", "network733", "latency733"],
    ),
    (
        ("library733 service733 gateway733 storage733 network733 latency733", 10),
        ["library733", "service733", "gateway733", "storage733", "network733", "latency733"],
    ),
    (
        ("library733 service733 gateway733 storage733 network733 latency733", 18),
        ["library733", "service733", "gateway733", "storage733", "network733", "latency733"],
    ),
    (
        ("library733 service733 gateway733 storage733 network733 latency733", 28),
        ["library733 service733", "gateway733 storage733", "network733 latency733"],
    ),
    (
        ("service733 gateway733 storage733 network733 latency733 buffer733", 6),
        ["service733", "gateway733", "storage733", "network733", "latency733", "buffer733"],
    ),
    (
        ("service733 gateway733 storage733 network733 latency733 buffer733", 10),
        ["service733", "gateway733", "storage733", "network733", "latency733", "buffer733"],
    ),
    (
        ("service733 gateway733 storage733 network733 latency733 buffer733", 18),
        ["service733", "gateway733", "storage733", "network733", "latency733", "buffer733"],
    ),
    (
        ("service733 gateway733 storage733 network733 latency733 buffer733", 28),
        ["service733 gateway733", "storage733 network733", "latency733 buffer733"],
    ),
    (
        ("gateway733 storage733 network733 latency733 buffer733 queue733", 6),
        ["gateway733", "storage733", "network733", "latency733", "buffer733", "queue733"],
    ),
    (
        ("gateway733 storage733 network733 latency733 buffer733 queue733", 10),
        ["gateway733", "storage733", "network733", "latency733", "buffer733", "queue733"],
    ),
    (
        ("gateway733 storage733 network733 latency733 buffer733 queue733", 18),
        ["gateway733", "storage733", "network733", "latency733", "buffer733 queue733"],
    ),
    (
        ("gateway733 storage733 network733 latency733 buffer733 queue733", 28),
        ["gateway733 storage733", "network733 latency733", "buffer733 queue733"],
    ),
    (
        ("storage733 network733 latency733 buffer733 queue733 worker733", 6),
        ["storage733", "network733", "latency733", "buffer733", "queue733", "worker733"],
    ),
    (
        ("storage733 network733 latency733 buffer733 queue733 worker733", 10),
        ["storage733", "network733", "latency733", "buffer733", "queue733", "worker733"],
    ),
    (
        ("storage733 network733 latency733 buffer733 queue733 worker733", 18),
        ["storage733", "network733", "latency733", "buffer733 queue733", "worker733"],
    ),
    (
        ("storage733 network733 latency733 buffer733 queue733 worker733", 28),
        ["storage733 network733", "latency733 buffer733", "queue733 worker733"],
    ),
    (
        ("network733 latency733 buffer733 queue733 worker733 kernel733", 6),
        ["network733", "latency733", "buffer733", "queue733", "worker733", "kernel733"],
    ),
    (
        ("network733 latency733 buffer733 queue733 worker733 kernel733", 10),
        ["network733", "latency733", "buffer733", "queue733", "worker733", "kernel733"],
    ),
    (
        ("network733 latency733 buffer733 queue733 worker733 kernel733", 18),
        ["network733", "latency733", "buffer733 queue733", "worker733", "kernel733"],
    ),
    (
        ("network733 latency733 buffer733 queue733 worker733 kernel733", 28),
        ["network733 latency733", "buffer733 queue733 worker733", "kernel733"],
    ),
    (
        ("latency733 buffer733 queue733 worker733 kernel733 signal733", 6),
        ["latency733", "buffer733", "queue733", "worker733", "kernel733", "signal733"],
    ),
    (
        ("latency733 buffer733 queue733 worker733 kernel733 signal733", 10),
        ["latency733", "buffer733", "queue733", "worker733", "kernel733", "signal733"],
    ),
    (
        ("latency733 buffer733 queue733 worker733 kernel733 signal733", 18),
        ["latency733", "buffer733 queue733", "worker733", "kernel733", "signal733"],
    ),
    (
        ("latency733 buffer733 queue733 worker733 kernel733 signal733", 28),
        ["latency733 buffer733", "queue733 worker733 kernel733", "signal733"],
    ),
    (
        ("buffer733 queue733 worker733 kernel733 signal733 packet733", 6),
        ["buffer733", "queue733", "worker733", "kernel733", "signal733", "packet733"],
    ),
    (
        ("buffer733 queue733 worker733 kernel733 signal733 packet733", 10),
        ["buffer733", "queue733", "worker733", "kernel733", "signal733", "packet733"],
    ),
    (
        ("buffer733 queue733 worker733 kernel733 signal733 packet733", 18),
        ["buffer733 queue733", "worker733", "kernel733", "signal733", "packet733"],
    ),
    (
        ("buffer733 queue733 worker733 kernel733 signal733 packet733", 28),
        ["buffer733 queue733 worker733", "kernel733 signal733", "packet733"],
    ),
    (
        ("queue733 worker733 kernel733 signal733 packet733 router733", 6),
        ["queue733", "worker733", "kernel733", "signal733", "packet733", "router733"],
    ),
    (
        ("queue733 worker733 kernel733 signal733 packet733 router733", 10),
        ["queue733", "worker733", "kernel733", "signal733", "packet733", "router733"],
    ),
    (
        ("queue733 worker733 kernel733 signal733 packet733 router733", 18),
        ["queue733 worker733", "kernel733", "signal733", "packet733", "router733"],
    ),
    (
        ("queue733 worker733 kernel733 signal733 packet733 router733", 28),
        ["queue733 worker733 kernel733", "signal733 packet733", "router733"],
    ),
    (
        ("worker733 kernel733 signal733 packet733 router733 cluster733", 6),
        ["worker733", "kernel733", "signal733", "packet733", "router733", "cluster733"],
    ),
    (
        ("worker733 kernel733 signal733 packet733 router733 cluster733", 10),
        ["worker733", "kernel733", "signal733", "packet733", "router733", "cluster733"],
    ),
    (
        ("worker733 kernel733 signal733 packet733 router733 cluster733", 18),
        ["worker733", "kernel733", "signal733", "packet733", "router733", "cluster733"],
    ),
    (
        ("worker733 kernel733 signal733 packet733 router733 cluster733", 28),
        ["worker733 kernel733", "signal733 packet733", "router733 cluster733"],
    ),
    (
        ("kernel733 signal733 packet733 router733 cluster733 mirror733", 6),
        ["kernel733", "signal733", "packet733", "router733", "cluster733", "mirror733"],
    ),
    (
        ("kernel733 signal733 packet733 router733 cluster733 mirror733", 10),
        ["kernel733", "signal733", "packet733", "router733", "cluster733", "mirror733"],
    ),
    (
        ("kernel733 signal733 packet733 router733 cluster733 mirror733", 18),
        ["kernel733", "signal733", "packet733", "router733", "cluster733", "mirror733"],
    ),
    (
        ("kernel733 signal733 packet733 router733 cluster733 mirror733", 28),
        ["kernel733 signal733", "packet733 router733", "cluster733 mirror733"],
    ),
    (
        ("signal733 packet733 router733 cluster733 mirror733 filter733", 6),
        ["signal733", "packet733", "router733", "cluster733", "mirror733", "filter733"],
    ),
    (
        ("signal733 packet733 router733 cluster733 mirror733 filter733", 10),
        ["signal733", "packet733", "router733", "cluster733", "mirror733", "filter733"],
    ),
    (
        ("signal733 packet733 router733 cluster733 mirror733 filter733", 18),
        ["signal733", "packet733", "router733", "cluster733", "mirror733", "filter733"],
    ),
    (
        ("signal733 packet733 router733 cluster733 mirror733 filter733", 28),
        ["signal733 packet733", "router733 cluster733", "mirror733 filter733"],
    ),
    (
        ("packet733 router733 cluster733 mirror733 filter733 ranking733", 6),
        ["packet733", "router733", "cluster733", "mirror733", "filter733", "ranking733"],
    ),
    (
        ("packet733 router733 cluster733 mirror733 filter733 ranking733", 10),
        ["packet733", "router733", "cluster733", "mirror733", "filter733", "ranking733"],
    ),
    (
        ("packet733 router733 cluster733 mirror733 filter733 ranking733", 18),
        ["packet733", "router733", "cluster733", "mirror733", "filter733", "ranking733"],
    ),
    (
        ("packet733 router733 cluster733 mirror733 filter733 ranking733", 28),
        ["packet733 router733", "cluster733 mirror733", "filter733 ranking733"],
    ),
    (
        ("router733 cluster733 mirror733 filter733 ranking733 encoding733", 6),
        ["router733", "cluster733", "mirror733", "filter733", "ranking733", "encoding733"],
    ),
    (
        ("router733 cluster733 mirror733 filter733 ranking733 encoding733", 10),
        ["router733", "cluster733", "mirror733", "filter733", "ranking733", "encoding733"],
    ),
    (
        ("router733 cluster733 mirror733 filter733 ranking733 encoding733", 18),
        ["router733", "cluster733", "mirror733", "filter733", "ranking733", "encoding733"],
    ),
    (
        ("router733 cluster733 mirror733 filter733 ranking733 encoding733", 28),
        ["router733 cluster733", "mirror733 filter733", "ranking733 encoding733"],
    ),
    (
        ("cluster733 mirror733 filter733 ranking733 encoding733 mapping733", 6),
        ["cluster733", "mirror733", "filter733", "ranking733", "encoding733", "mapping733"],
    ),
    (
        ("cluster733 mirror733 filter733 ranking733 encoding733 mapping733", 10),
        ["cluster733", "mirror733", "filter733", "ranking733", "encoding733", "mapping733"],
    ),
    (
        ("cluster733 mirror733 filter733 ranking733 encoding733 mapping733", 18),
        ["cluster733", "mirror733", "filter733", "ranking733", "encoding733", "mapping733"],
    ),
    (
        ("cluster733 mirror733 filter733 ranking733 encoding733 mapping733", 28),
        ["cluster733 mirror733", "filter733 ranking733", "encoding733 mapping733"],
    ),
    (
        ("mirror733 filter733 ranking733 encoding733 mapping733 record733", 6),
        ["mirror733", "filter733", "ranking733", "encoding733", "mapping733", "record733"],
    ),
    (
        ("mirror733 filter733 ranking733 encoding733 mapping733 record733", 10),
        ["mirror733", "filter733", "ranking733", "encoding733", "mapping733", "record733"],
    ),
    (
        ("mirror733 filter733 ranking733 encoding733 mapping733 record733", 18),
        ["mirror733", "filter733", "ranking733", "encoding733", "mapping733", "record733"],
    ),
    (
        ("mirror733 filter733 ranking733 encoding733 mapping733 record733", 28),
        ["mirror733 filter733", "ranking733 encoding733", "mapping733 record733"],
    ),
    (
        ("filter733 ranking733 encoding733 mapping733 record733 candle733", 6),
        ["filter733", "ranking733", "encoding733", "mapping733", "record733", "candle733"],
    ),
    (
        ("filter733 ranking733 encoding733 mapping733 record733 candle733", 10),
        ["filter733", "ranking733", "encoding733", "mapping733", "record733", "candle733"],
    ),
    (
        ("filter733 ranking733 encoding733 mapping733 record733 candle733", 18),
        ["filter733", "ranking733", "encoding733", "mapping733", "record733", "candle733"],
    ),
    (
        ("filter733 ranking733 encoding733 mapping733 record733 candle733", 28),
        ["filter733 ranking733", "encoding733 mapping733", "record733 candle733"],
    ),
    (
        ("ranking733 encoding733 mapping733 record733 candle733 thread733", 6),
        ["ranking733", "encoding733", "mapping733", "record733", "candle733", "thread733"],
    ),
    (
        ("ranking733 encoding733 mapping733 record733 candle733 thread733", 10),
        ["ranking733", "encoding733", "mapping733", "record733", "candle733", "thread733"],
    ),
    (
        ("ranking733 encoding733 mapping733 record733 candle733 thread733", 18),
        ["ranking733", "encoding733", "mapping733", "record733", "candle733", "thread733"],
    ),
    (
        ("ranking733 encoding733 mapping733 record733 candle733 thread733", 28),
        ["ranking733 encoding733", "mapping733 record733", "candle733 thread733"],
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
