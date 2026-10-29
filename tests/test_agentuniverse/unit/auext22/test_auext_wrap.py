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
        ("round 22: the quick brown fox jumps over the lazy dog", 4),
        ["round", "22:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 22: the quick brown fox jumps over the lazy dog", 8),
        ["round", "22: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 22: the quick brown fox jumps over the lazy dog", 12),
        ["round 22:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 22: the quick brown fox jumps over the lazy dog", 16),
        ["round 22: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 22: the quick brown fox jumps over the lazy dog", 24),
        ["round 22: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 22: the quick brown fox jumps over the lazy dog", 32),
        ["round 22: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 22: agentuniverse is a framework for multi agents", 4),
        ["round", "22:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 22: agentuniverse is a framework for multi agents", 8),
        ["round", "22:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 22: agentuniverse is a framework for multi agents", 12),
        ["round 22:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 22: agentuniverse is a framework for multi agents", 16),
        ["round 22:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 22: agentuniverse is a framework for multi agents", 24),
        ["round 22: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 22: agentuniverse is a framework for multi agents", 32),
        ["round 22: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 22: knowledge stored as vectors enables retrieval", 4),
        ["round", "22:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 22: knowledge stored as vectors enables retrieval", 8),
        ["round", "22:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 22: knowledge stored as vectors enables retrieval", 12),
        ["round 22:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 22: knowledge stored as vectors enables retrieval", 16),
        ["round 22:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 22: knowledge stored as vectors enables retrieval", 24),
        ["round 22: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 22: knowledge stored as vectors enables retrieval", 32),
        ["round 22: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 22: the processor reads the record then stops", 4),
        ["round", "22:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 22: the processor reads the record then stops", 8),
        ["round", "22: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 22: the processor reads the record then stops", 12),
        ["round 22:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 22: the processor reads the record then stops", 16),
        ["round 22: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 22: the processor reads the record then stops", 24),
        ["round 22: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 22: the processor reads the record then stops", 32),
        ["round 22: the processor reads", "the record then stops"],
    ),
    (
        ("round 22: a worker pulls the next task from the queue", 4),
        ["round", "22:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 22: a worker pulls the next task from the queue", 8),
        ["round", "22: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 22: a worker pulls the next task from the queue", 12),
        ["round 22: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 22: a worker pulls the next task from the queue", 16),
        ["round 22: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 22: a worker pulls the next task from the queue", 24),
        ["round 22: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 22: a worker pulls the next task from the queue", 32),
        ["round 22: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 22: signals travel through the network layer", 4),
        ["round", "22:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 22: signals travel through the network layer", 8),
        ["round", "22:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 22: signals travel through the network layer", 12),
        ["round 22:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 22: signals travel through the network layer", 16),
        ["round 22:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 22: signals travel through the network layer", 24),
        ["round 22: signals travel", "through the network", "layer"],
    ),
    (
        ("round 22: signals travel through the network layer", 32),
        ["round 22: signals travel through", "the network layer"],
    ),
    (
        ("round 22: the gateway routes each request by policy", 4),
        ["round", "22:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 22: the gateway routes each request by policy", 8),
        ["round", "22: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 22: the gateway routes each request by policy", 12),
        ["round 22:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 22: the gateway routes each request by policy", 16),
        ["round 22: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 22: the gateway routes each request by policy", 24),
        ["round 22: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 22: the gateway routes each request by policy", 32),
        ["round 22: the gateway routes", "each request by policy"],
    ),
    (
        ("round 22: memory grows until the buffer is full", 4),
        ["round", "22:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 22: memory grows until the buffer is full", 8),
        ["round", "22:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 22: memory grows until the buffer is full", 12),
        ["round 22:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 22: memory grows until the buffer is full", 16),
        ["round 22: memory", "grows until the", "buffer is full"],
    ),
    (("round 22: memory grows until the buffer is full", 24), ["round 22: memory grows", "until the buffer is full"]),
    (("round 22: memory grows until the buffer is full", 32), ["round 22: memory grows until the", "buffer is full"]),
    (
        ("round 22: the cluster mirrors every packet twice", 4),
        ["round", "22:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 22: the cluster mirrors every packet twice", 8),
        ["round", "22: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 22: the cluster mirrors every packet twice", 12),
        ["round 22:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 22: the cluster mirrors every packet twice", 16),
        ["round 22: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 22: the cluster mirrors every packet twice", 24),
        ["round 22: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 22: the cluster mirrors every packet twice", 32), ["round 22: the cluster mirrors", "every packet twice"]),
    (
        ("round 22: ranking uses tokens learned from the corpus", 4),
        ["round", "22:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 22: ranking uses tokens learned from the corpus", 8),
        ["round", "22:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 22: ranking uses tokens learned from the corpus", 12),
        ["round 22:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 22: ranking uses tokens learned from the corpus", 16),
        ["round 22:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 22: ranking uses tokens learned from the corpus", 24),
        ["round 22: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 22: ranking uses tokens learned from the corpus", 32),
        ["round 22: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 22: a long session ends when the candle dies", 4),
        ["round", "22:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 22: a long session ends when the candle dies", 8),
        ["round", "22: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 22: a long session ends when the candle dies", 12),
        ["round 22: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 22: a long session ends when the candle dies", 16),
        ["round 22: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 22: a long session ends when the candle dies", 24),
        ["round 22: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 22: a long session ends when the candle dies", 32),
        ["round 22: a long session ends", "when the candle dies"],
    ),
    (
        ("round 22: encode the prompt then map the result", 4),
        ["round", "22:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 22: encode the prompt then map the result", 8),
        ["round", "22:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 22: encode the prompt then map the result", 12),
        ["round 22:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 22: encode the prompt then map the result", 16),
        ["round 22: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 22: encode the prompt then map the result", 24),
        ["round 22: encode the", "prompt then map the", "result"],
    ),
    (("round 22: encode the prompt then map the result", 32), ["round 22: encode the prompt then", "map the result"]),
    (
        ("round 22: the kernel wakes the worker at dawn", 4),
        ["round", "22:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 22: the kernel wakes the worker at dawn", 8),
        ["round", "22: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 22: the kernel wakes the worker at dawn", 12),
        ["round 22:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 22: the kernel wakes the worker at dawn", 16), ["round 22: the", "kernel wakes the", "worker at dawn"]),
    (("round 22: the kernel wakes the worker at dawn", 24), ["round 22: the kernel", "wakes the worker at dawn"]),
    (("round 22: the kernel wakes the worker at dawn", 32), ["round 22: the kernel wakes the", "worker at dawn"]),
    (
        ("round 22: service latency drops after the patch", 4),
        ["round", "22:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 22: service latency drops after the patch", 8),
        ["round", "22:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 22: service latency drops after the patch", 12),
        ["round 22:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 22: service latency drops after the patch", 16),
        ["round 22:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 22: service latency drops after the patch", 24),
        ["round 22: service", "latency drops after the", "patch"],
    ),
    (("round 22: service latency drops after the patch", 32), ["round 22: service latency drops", "after the patch"]),
    (
        ("round 22: the library caches every vector it sees", 4),
        ["round", "22:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 22: the library caches every vector it sees", 8),
        ["round", "22: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 22: the library caches every vector it sees", 12),
        ["round 22:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 22: the library caches every vector it sees", 16),
        ["round 22: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 22: the library caches every vector it sees", 24),
        ["round 22: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 22: the library caches every vector it sees", 32),
        ["round 22: the library caches", "every vector it sees"],
    ),
    (
        ("round 22: agents argue then the debate resolves", 4),
        ["round", "22:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 22: agents argue then the debate resolves", 8),
        ["round", "22:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 22: agents argue then the debate resolves", 12),
        ["round 22:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 22: agents argue then the debate resolves", 16),
        ["round 22: agents", "argue then the", "debate resolves"],
    ),
    (("round 22: agents argue then the debate resolves", 24), ["round 22: agents argue", "then the debate resolves"]),
    (("round 22: agents argue then the debate resolves", 32), ["round 22: agents argue then the", "debate resolves"]),
    (
        ("round 22: the filter keeps only strong matches", 4),
        ["round", "22:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 22: the filter keeps only strong matches", 8),
        ["round", "22: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 22: the filter keeps only strong matches", 12),
        ["round 22:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 22: the filter keeps only strong matches", 16),
        ["round 22: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 22: the filter keeps only strong matches", 24), ["round 22: the filter", "keeps only strong", "matches"]),
    (("round 22: the filter keeps only strong matches", 32), ["round 22: the filter keeps only", "strong matches"]),
    (
        ("round 22: the model answers with a short reply", 4),
        ["round", "22:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 22: the model answers with a short reply", 8),
        ["round", "22: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 22: the model answers with a short reply", 12),
        ["round 22:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 22: the model answers with a short reply", 16),
        ["round 22: the", "model answers", "with a short", "reply"],
    ),
    (("round 22: the model answers with a short reply", 24), ["round 22: the model", "answers with a short", "reply"]),
    (("round 22: the model answers with a short reply", 32), ["round 22: the model answers with", "a short reply"]),
    (
        ("round 22: the recorder stores the reasoning trace", 4),
        ["round", "22:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 22: the recorder stores the reasoning trace", 8),
        ["round", "22: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 22: the recorder stores the reasoning trace", 12),
        ["round 22:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 22: the recorder stores the reasoning trace", 16),
        ["round 22: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 22: the recorder stores the reasoning trace", 24),
        ["round 22: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 22: the recorder stores the reasoning trace", 32),
        ["round 22: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 22: the angel watches the processor run", 4),
        ["round", "22:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 22: the angel watches the processor run", 8),
        ["round", "22: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 22: the angel watches the processor run", 12),
        ["round 22:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 22: the angel watches the processor run", 16), ["round 22: the", "angel watches", "the processor", "run"]),
    (("round 22: the angel watches the processor run", 24), ["round 22: the angel", "watches the processor", "run"]),
    (("round 22: the angel watches the processor run", 32), ["round 22: the angel watches the", "processor run"]),
    (
        ("round 22: angle of the vector decides the match", 4),
        ["round", "22:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 22: angle of the vector decides the match", 8),
        ["round", "22:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 22: angle of the vector decides the match", 12),
        ["round 22:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 22: angle of the vector decides the match", 16),
        ["round 22: angle", "of the vector", "decides the", "match"],
    ),
    (("round 22: angle of the vector decides the match", 24), ["round 22: angle of the", "vector decides the match"]),
    (("round 22: angle of the vector decides the match", 32), ["round 22: angle of the vector", "decides the match"]),
    (
        ("round 22: the candle burns twice as long at night", 4),
        ["round", "22:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 22: the candle burns twice as long at night", 8),
        ["round", "22: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 22: the candle burns twice as long at night", 12),
        ["round 22:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 22: the candle burns twice as long at night", 16),
        ["round 22: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 22: the candle burns twice as long at night", 24),
        ["round 22: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 22: the candle burns twice as long at night", 32),
        ["round 22: the candle burns twice", "as long at night"],
    ),
    (
        ("round 22: a mirror of the universe in one line", 4),
        ["round", "22:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 22: a mirror of the universe in one line", 8),
        ["round", "22: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 22: a mirror of the universe in one line", 12),
        ["round 22: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 22: a mirror of the universe in one line", 16),
        ["round 22: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 22: a mirror of the universe in one line", 24), ["round 22: a mirror of", "the universe in one line"]),
    (("round 22: a mirror of the universe in one line", 32), ["round 22: a mirror of the", "universe in one line"]),
    (
        ("round 22: the queue drains before the storm", 4),
        ["round", "22:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 22: the queue drains before the storm", 8),
        ["round", "22: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 22: the queue drains before the storm", 12), ["round 22:", "the queue", "drains", "before the", "storm"]),
    (("round 22: the queue drains before the storm", 16), ["round 22: the", "queue drains", "before the storm"]),
    (("round 22: the queue drains before the storm", 24), ["round 22: the queue", "drains before the storm"]),
    (("round 22: the queue drains before the storm", 32), ["round 22: the queue drains", "before the storm"]),
    (
        ("kitten22 sitting22 agent22 angle22 universe22 memory22", 6),
        ["kitten22", "sitting22", "agent22", "angle22", "universe22", "memory22"],
    ),
    (
        ("kitten22 sitting22 agent22 angle22 universe22 memory22", 10),
        ["kitten22", "sitting22", "agent22", "angle22", "universe22", "memory22"],
    ),
    (
        ("kitten22 sitting22 agent22 angle22 universe22 memory22", 18),
        ["kitten22 sitting22", "agent22 angle22", "universe22", "memory22"],
    ),
    (
        ("kitten22 sitting22 agent22 angle22 universe22 memory22", 28),
        ["kitten22 sitting22 agent22", "angle22 universe22 memory22"],
    ),
    (
        ("sitting22 agent22 angle22 universe22 memory22 stream22", 6),
        ["sitting22", "agent22", "angle22", "universe22", "memory22", "stream22"],
    ),
    (
        ("sitting22 agent22 angle22 universe22 memory22 stream22", 10),
        ["sitting22", "agent22", "angle22", "universe22", "memory22", "stream22"],
    ),
    (
        ("sitting22 agent22 angle22 universe22 memory22 stream22", 18),
        ["sitting22 agent22", "angle22 universe22", "memory22 stream22"],
    ),
    (
        ("sitting22 agent22 angle22 universe22 memory22 stream22", 28),
        ["sitting22 agent22 angle22", "universe22 memory22 stream22"],
    ),
    (
        ("agent22 angle22 universe22 memory22 stream22 context22", 6),
        ["agent22", "angle22", "universe22", "memory22", "stream22", "context22"],
    ),
    (
        ("agent22 angle22 universe22 memory22 stream22 context22", 10),
        ["agent22", "angle22", "universe22", "memory22", "stream22", "context22"],
    ),
    (
        ("agent22 angle22 universe22 memory22 stream22 context22", 18),
        ["agent22 angle22", "universe22", "memory22 stream22", "context22"],
    ),
    (
        ("agent22 angle22 universe22 memory22 stream22 context22", 28),
        ["agent22 angle22 universe22", "memory22 stream22 context22"],
    ),
    (
        ("angle22 universe22 memory22 stream22 context22 knowledge22", 6),
        ["angle22", "universe22", "memory22", "stream22", "context22", "knowledge22"],
    ),
    (
        ("angle22 universe22 memory22 stream22 context22 knowledge22", 10),
        ["angle22", "universe22", "memory22", "stream22", "context22", "knowledge22"],
    ),
    (
        ("angle22 universe22 memory22 stream22 context22 knowledge22", 18),
        ["angle22 universe22", "memory22 stream22", "context22", "knowledge22"],
    ),
    (
        ("angle22 universe22 memory22 stream22 context22 knowledge22", 28),
        ["angle22 universe22 memory22", "stream22 context22", "knowledge22"],
    ),
    (
        ("universe22 memory22 stream22 context22 knowledge22 vector22", 6),
        ["universe22", "memory22", "stream22", "context22", "knowledge22", "vector22"],
    ),
    (
        ("universe22 memory22 stream22 context22 knowledge22 vector22", 10),
        ["universe22", "memory22", "stream22", "context22", "knowledge22", "vector22"],
    ),
    (
        ("universe22 memory22 stream22 context22 knowledge22 vector22", 18),
        ["universe22", "memory22 stream22", "context22", "knowledge22", "vector22"],
    ),
    (
        ("universe22 memory22 stream22 context22 knowledge22 vector22", 28),
        ["universe22 memory22 stream22", "context22 knowledge22", "vector22"],
    ),
    (
        ("memory22 stream22 context22 knowledge22 vector22 processor22", 6),
        ["memory22", "stream22", "context22", "knowledge22", "vector22", "processor22"],
    ),
    (
        ("memory22 stream22 context22 knowledge22 vector22 processor22", 10),
        ["memory22", "stream22", "context22", "knowledge22", "vector22", "processor22"],
    ),
    (
        ("memory22 stream22 context22 knowledge22 vector22 processor22", 18),
        ["memory22 stream22", "context22", "knowledge22", "vector22", "processor22"],
    ),
    (
        ("memory22 stream22 context22 knowledge22 vector22 processor22", 28),
        ["memory22 stream22 context22", "knowledge22 vector22", "processor22"],
    ),
    (
        ("stream22 context22 knowledge22 vector22 processor22 reasoning22", 6),
        ["stream22", "context22", "knowledge22", "vector22", "processor22", "reasoning22"],
    ),
    (
        ("stream22 context22 knowledge22 vector22 processor22 reasoning22", 10),
        ["stream22", "context22", "knowledge22", "vector22", "processor22", "reasoning22"],
    ),
    (
        ("stream22 context22 knowledge22 vector22 processor22 reasoning22", 18),
        ["stream22 context22", "knowledge22", "vector22", "processor22", "reasoning22"],
    ),
    (
        ("stream22 context22 knowledge22 vector22 processor22 reasoning22", 28),
        ["stream22 context22", "knowledge22 vector22", "processor22 reasoning22"],
    ),
    (
        ("context22 knowledge22 vector22 processor22 reasoning22 machine22", 6),
        ["context22", "knowledge22", "vector22", "processor22", "reasoning22", "machine22"],
    ),
    (
        ("context22 knowledge22 vector22 processor22 reasoning22 machine22", 10),
        ["context22", "knowledge22", "vector22", "processor22", "reasoning22", "machine22"],
    ),
    (
        ("context22 knowledge22 vector22 processor22 reasoning22 machine22", 18),
        ["context22", "knowledge22", "vector22", "processor22", "reasoning22", "machine22"],
    ),
    (
        ("context22 knowledge22 vector22 processor22 reasoning22 machine22", 28),
        ["context22 knowledge22", "vector22 processor22", "reasoning22 machine22"],
    ),
    (
        ("knowledge22 vector22 processor22 reasoning22 machine22 learning22", 6),
        ["knowledge22", "vector22", "processor22", "reasoning22", "machine22", "learning22"],
    ),
    (
        ("knowledge22 vector22 processor22 reasoning22 machine22 learning22", 10),
        ["knowledge22", "vector22", "processor22", "reasoning22", "machine22", "learning22"],
    ),
    (
        ("knowledge22 vector22 processor22 reasoning22 machine22 learning22", 18),
        ["knowledge22", "vector22", "processor22", "reasoning22", "machine22", "learning22"],
    ),
    (
        ("knowledge22 vector22 processor22 reasoning22 machine22 learning22", 28),
        ["knowledge22 vector22", "processor22 reasoning22", "machine22 learning22"],
    ),
    (
        ("vector22 processor22 reasoning22 machine22 learning22 model22", 6),
        ["vector22", "processor22", "reasoning22", "machine22", "learning22", "model22"],
    ),
    (
        ("vector22 processor22 reasoning22 machine22 learning22 model22", 10),
        ["vector22", "processor22", "reasoning22", "machine22", "learning22", "model22"],
    ),
    (
        ("vector22 processor22 reasoning22 machine22 learning22 model22", 18),
        ["vector22", "processor22", "reasoning22", "machine22", "learning22 model22"],
    ),
    (
        ("vector22 processor22 reasoning22 machine22 learning22 model22", 28),
        ["vector22 processor22", "reasoning22 machine22", "learning22 model22"],
    ),
    (
        ("processor22 reasoning22 machine22 learning22 model22 token22", 6),
        ["processor22", "reasoning22", "machine22", "learning22", "model22", "token22"],
    ),
    (
        ("processor22 reasoning22 machine22 learning22 model22 token22", 10),
        ["processor22", "reasoning22", "machine22", "learning22", "model22", "token22"],
    ),
    (
        ("processor22 reasoning22 machine22 learning22 model22 token22", 18),
        ["processor22", "reasoning22", "machine22", "learning22 model22", "token22"],
    ),
    (
        ("processor22 reasoning22 machine22 learning22 model22 token22", 28),
        ["processor22 reasoning22", "machine22 learning22 model22", "token22"],
    ),
    (
        ("reasoning22 machine22 learning22 model22 token22 prompt22", 6),
        ["reasoning22", "machine22", "learning22", "model22", "token22", "prompt22"],
    ),
    (
        ("reasoning22 machine22 learning22 model22 token22 prompt22", 10),
        ["reasoning22", "machine22", "learning22", "model22", "token22", "prompt22"],
    ),
    (
        ("reasoning22 machine22 learning22 model22 token22 prompt22", 18),
        ["reasoning22", "machine22", "learning22 model22", "token22 prompt22"],
    ),
    (
        ("reasoning22 machine22 learning22 model22 token22 prompt22", 28),
        ["reasoning22 machine22", "learning22 model22 token22", "prompt22"],
    ),
    (
        ("machine22 learning22 model22 token22 prompt22 session22", 6),
        ["machine22", "learning22", "model22", "token22", "prompt22", "session22"],
    ),
    (
        ("machine22 learning22 model22 token22 prompt22 session22", 10),
        ["machine22", "learning22", "model22", "token22", "prompt22", "session22"],
    ),
    (
        ("machine22 learning22 model22 token22 prompt22 session22", 18),
        ["machine22", "learning22 model22", "token22 prompt22", "session22"],
    ),
    (
        ("machine22 learning22 model22 token22 prompt22 session22", 28),
        ["machine22 learning22 model22", "token22 prompt22 session22"],
    ),
    (
        ("learning22 model22 token22 prompt22 session22 library22", 6),
        ["learning22", "model22", "token22", "prompt22", "session22", "library22"],
    ),
    (
        ("learning22 model22 token22 prompt22 session22 library22", 10),
        ["learning22", "model22", "token22", "prompt22", "session22", "library22"],
    ),
    (
        ("learning22 model22 token22 prompt22 session22 library22", 18),
        ["learning22 model22", "token22 prompt22", "session22", "library22"],
    ),
    (
        ("learning22 model22 token22 prompt22 session22 library22", 28),
        ["learning22 model22 token22", "prompt22 session22 library22"],
    ),
    (
        ("model22 token22 prompt22 session22 library22 service22", 6),
        ["model22", "token22", "prompt22", "session22", "library22", "service22"],
    ),
    (
        ("model22 token22 prompt22 session22 library22 service22", 10),
        ["model22", "token22", "prompt22", "session22", "library22", "service22"],
    ),
    (
        ("model22 token22 prompt22 session22 library22 service22", 18),
        ["model22 token22", "prompt22 session22", "library22", "service22"],
    ),
    (
        ("model22 token22 prompt22 session22 library22 service22", 28),
        ["model22 token22 prompt22", "session22 library22", "service22"],
    ),
    (
        ("token22 prompt22 session22 library22 service22 gateway22", 6),
        ["token22", "prompt22", "session22", "library22", "service22", "gateway22"],
    ),
    (
        ("token22 prompt22 session22 library22 service22 gateway22", 10),
        ["token22", "prompt22", "session22", "library22", "service22", "gateway22"],
    ),
    (
        ("token22 prompt22 session22 library22 service22 gateway22", 18),
        ["token22 prompt22", "session22", "library22", "service22", "gateway22"],
    ),
    (
        ("token22 prompt22 session22 library22 service22 gateway22", 28),
        ["token22 prompt22 session22", "library22 service22", "gateway22"],
    ),
    (
        ("prompt22 session22 library22 service22 gateway22 storage22", 6),
        ["prompt22", "session22", "library22", "service22", "gateway22", "storage22"],
    ),
    (
        ("prompt22 session22 library22 service22 gateway22 storage22", 10),
        ["prompt22", "session22", "library22", "service22", "gateway22", "storage22"],
    ),
    (
        ("prompt22 session22 library22 service22 gateway22 storage22", 18),
        ["prompt22 session22", "library22", "service22", "gateway22", "storage22"],
    ),
    (
        ("prompt22 session22 library22 service22 gateway22 storage22", 28),
        ["prompt22 session22 library22", "service22 gateway22", "storage22"],
    ),
    (
        ("session22 library22 service22 gateway22 storage22 network22", 6),
        ["session22", "library22", "service22", "gateway22", "storage22", "network22"],
    ),
    (
        ("session22 library22 service22 gateway22 storage22 network22", 10),
        ["session22", "library22", "service22", "gateway22", "storage22", "network22"],
    ),
    (
        ("session22 library22 service22 gateway22 storage22 network22", 18),
        ["session22", "library22", "service22", "gateway22", "storage22", "network22"],
    ),
    (
        ("session22 library22 service22 gateway22 storage22 network22", 28),
        ["session22 library22", "service22 gateway22", "storage22 network22"],
    ),
    (
        ("library22 service22 gateway22 storage22 network22 latency22", 6),
        ["library22", "service22", "gateway22", "storage22", "network22", "latency22"],
    ),
    (
        ("library22 service22 gateway22 storage22 network22 latency22", 10),
        ["library22", "service22", "gateway22", "storage22", "network22", "latency22"],
    ),
    (
        ("library22 service22 gateway22 storage22 network22 latency22", 18),
        ["library22", "service22", "gateway22", "storage22", "network22", "latency22"],
    ),
    (
        ("library22 service22 gateway22 storage22 network22 latency22", 28),
        ["library22 service22", "gateway22 storage22", "network22 latency22"],
    ),
    (
        ("service22 gateway22 storage22 network22 latency22 buffer22", 6),
        ["service22", "gateway22", "storage22", "network22", "latency22", "buffer22"],
    ),
    (
        ("service22 gateway22 storage22 network22 latency22 buffer22", 10),
        ["service22", "gateway22", "storage22", "network22", "latency22", "buffer22"],
    ),
    (
        ("service22 gateway22 storage22 network22 latency22 buffer22", 18),
        ["service22", "gateway22", "storage22", "network22", "latency22 buffer22"],
    ),
    (
        ("service22 gateway22 storage22 network22 latency22 buffer22", 28),
        ["service22 gateway22", "storage22 network22", "latency22 buffer22"],
    ),
    (
        ("gateway22 storage22 network22 latency22 buffer22 queue22", 6),
        ["gateway22", "storage22", "network22", "latency22", "buffer22", "queue22"],
    ),
    (
        ("gateway22 storage22 network22 latency22 buffer22 queue22", 10),
        ["gateway22", "storage22", "network22", "latency22", "buffer22", "queue22"],
    ),
    (
        ("gateway22 storage22 network22 latency22 buffer22 queue22", 18),
        ["gateway22", "storage22", "network22", "latency22 buffer22", "queue22"],
    ),
    (
        ("gateway22 storage22 network22 latency22 buffer22 queue22", 28),
        ["gateway22 storage22", "network22 latency22 buffer22", "queue22"],
    ),
    (
        ("storage22 network22 latency22 buffer22 queue22 worker22", 6),
        ["storage22", "network22", "latency22", "buffer22", "queue22", "worker22"],
    ),
    (
        ("storage22 network22 latency22 buffer22 queue22 worker22", 10),
        ["storage22", "network22", "latency22", "buffer22", "queue22", "worker22"],
    ),
    (
        ("storage22 network22 latency22 buffer22 queue22 worker22", 18),
        ["storage22", "network22", "latency22 buffer22", "queue22 worker22"],
    ),
    (
        ("storage22 network22 latency22 buffer22 queue22 worker22", 28),
        ["storage22 network22", "latency22 buffer22 queue22", "worker22"],
    ),
    (
        ("network22 latency22 buffer22 queue22 worker22 kernel22", 6),
        ["network22", "latency22", "buffer22", "queue22", "worker22", "kernel22"],
    ),
    (
        ("network22 latency22 buffer22 queue22 worker22 kernel22", 10),
        ["network22", "latency22", "buffer22", "queue22", "worker22", "kernel22"],
    ),
    (
        ("network22 latency22 buffer22 queue22 worker22 kernel22", 18),
        ["network22", "latency22 buffer22", "queue22 worker22", "kernel22"],
    ),
    (
        ("network22 latency22 buffer22 queue22 worker22 kernel22", 28),
        ["network22 latency22 buffer22", "queue22 worker22 kernel22"],
    ),
    (
        ("latency22 buffer22 queue22 worker22 kernel22 signal22", 6),
        ["latency22", "buffer22", "queue22", "worker22", "kernel22", "signal22"],
    ),
    (
        ("latency22 buffer22 queue22 worker22 kernel22 signal22", 10),
        ["latency22", "buffer22", "queue22", "worker22", "kernel22", "signal22"],
    ),
    (
        ("latency22 buffer22 queue22 worker22 kernel22 signal22", 18),
        ["latency22 buffer22", "queue22 worker22", "kernel22 signal22"],
    ),
    (
        ("latency22 buffer22 queue22 worker22 kernel22 signal22", 28),
        ["latency22 buffer22 queue22", "worker22 kernel22 signal22"],
    ),
    (
        ("buffer22 queue22 worker22 kernel22 signal22 packet22", 6),
        ["buffer22", "queue22", "worker22", "kernel22", "signal22", "packet22"],
    ),
    (
        ("buffer22 queue22 worker22 kernel22 signal22 packet22", 10),
        ["buffer22", "queue22", "worker22", "kernel22", "signal22", "packet22"],
    ),
    (
        ("buffer22 queue22 worker22 kernel22 signal22 packet22", 18),
        ["buffer22 queue22", "worker22 kernel22", "signal22 packet22"],
    ),
    (
        ("buffer22 queue22 worker22 kernel22 signal22 packet22", 28),
        ["buffer22 queue22 worker22", "kernel22 signal22 packet22"],
    ),
    (
        ("queue22 worker22 kernel22 signal22 packet22 router22", 6),
        ["queue22", "worker22", "kernel22", "signal22", "packet22", "router22"],
    ),
    (
        ("queue22 worker22 kernel22 signal22 packet22 router22", 10),
        ["queue22", "worker22", "kernel22", "signal22", "packet22", "router22"],
    ),
    (
        ("queue22 worker22 kernel22 signal22 packet22 router22", 18),
        ["queue22 worker22", "kernel22 signal22", "packet22 router22"],
    ),
    (
        ("queue22 worker22 kernel22 signal22 packet22 router22", 28),
        ["queue22 worker22 kernel22", "signal22 packet22 router22"],
    ),
    (
        ("worker22 kernel22 signal22 packet22 router22 cluster22", 6),
        ["worker22", "kernel22", "signal22", "packet22", "router22", "cluster22"],
    ),
    (
        ("worker22 kernel22 signal22 packet22 router22 cluster22", 10),
        ["worker22", "kernel22", "signal22", "packet22", "router22", "cluster22"],
    ),
    (
        ("worker22 kernel22 signal22 packet22 router22 cluster22", 18),
        ["worker22 kernel22", "signal22 packet22", "router22 cluster22"],
    ),
    (
        ("worker22 kernel22 signal22 packet22 router22 cluster22", 28),
        ["worker22 kernel22 signal22", "packet22 router22 cluster22"],
    ),
    (
        ("kernel22 signal22 packet22 router22 cluster22 mirror22", 6),
        ["kernel22", "signal22", "packet22", "router22", "cluster22", "mirror22"],
    ),
    (
        ("kernel22 signal22 packet22 router22 cluster22 mirror22", 10),
        ["kernel22", "signal22", "packet22", "router22", "cluster22", "mirror22"],
    ),
    (
        ("kernel22 signal22 packet22 router22 cluster22 mirror22", 18),
        ["kernel22 signal22", "packet22 router22", "cluster22 mirror22"],
    ),
    (
        ("kernel22 signal22 packet22 router22 cluster22 mirror22", 28),
        ["kernel22 signal22 packet22", "router22 cluster22 mirror22"],
    ),
    (
        ("signal22 packet22 router22 cluster22 mirror22 filter22", 6),
        ["signal22", "packet22", "router22", "cluster22", "mirror22", "filter22"],
    ),
    (
        ("signal22 packet22 router22 cluster22 mirror22 filter22", 10),
        ["signal22", "packet22", "router22", "cluster22", "mirror22", "filter22"],
    ),
    (
        ("signal22 packet22 router22 cluster22 mirror22 filter22", 18),
        ["signal22 packet22", "router22 cluster22", "mirror22 filter22"],
    ),
    (
        ("signal22 packet22 router22 cluster22 mirror22 filter22", 28),
        ["signal22 packet22 router22", "cluster22 mirror22 filter22"],
    ),
    (
        ("packet22 router22 cluster22 mirror22 filter22 ranking22", 6),
        ["packet22", "router22", "cluster22", "mirror22", "filter22", "ranking22"],
    ),
    (
        ("packet22 router22 cluster22 mirror22 filter22 ranking22", 10),
        ["packet22", "router22", "cluster22", "mirror22", "filter22", "ranking22"],
    ),
    (
        ("packet22 router22 cluster22 mirror22 filter22 ranking22", 18),
        ["packet22 router22", "cluster22 mirror22", "filter22 ranking22"],
    ),
    (
        ("packet22 router22 cluster22 mirror22 filter22 ranking22", 28),
        ["packet22 router22 cluster22", "mirror22 filter22 ranking22"],
    ),
    (
        ("router22 cluster22 mirror22 filter22 ranking22 encoding22", 6),
        ["router22", "cluster22", "mirror22", "filter22", "ranking22", "encoding22"],
    ),
    (
        ("router22 cluster22 mirror22 filter22 ranking22 encoding22", 10),
        ["router22", "cluster22", "mirror22", "filter22", "ranking22", "encoding22"],
    ),
    (
        ("router22 cluster22 mirror22 filter22 ranking22 encoding22", 18),
        ["router22 cluster22", "mirror22 filter22", "ranking22", "encoding22"],
    ),
    (
        ("router22 cluster22 mirror22 filter22 ranking22 encoding22", 28),
        ["router22 cluster22 mirror22", "filter22 ranking22", "encoding22"],
    ),
    (
        ("cluster22 mirror22 filter22 ranking22 encoding22 mapping22", 6),
        ["cluster22", "mirror22", "filter22", "ranking22", "encoding22", "mapping22"],
    ),
    (
        ("cluster22 mirror22 filter22 ranking22 encoding22 mapping22", 10),
        ["cluster22", "mirror22", "filter22", "ranking22", "encoding22", "mapping22"],
    ),
    (
        ("cluster22 mirror22 filter22 ranking22 encoding22 mapping22", 18),
        ["cluster22 mirror22", "filter22 ranking22", "encoding22", "mapping22"],
    ),
    (
        ("cluster22 mirror22 filter22 ranking22 encoding22 mapping22", 28),
        ["cluster22 mirror22 filter22", "ranking22 encoding22", "mapping22"],
    ),
    (
        ("mirror22 filter22 ranking22 encoding22 mapping22 record22", 6),
        ["mirror22", "filter22", "ranking22", "encoding22", "mapping22", "record22"],
    ),
    (
        ("mirror22 filter22 ranking22 encoding22 mapping22 record22", 10),
        ["mirror22", "filter22", "ranking22", "encoding22", "mapping22", "record22"],
    ),
    (
        ("mirror22 filter22 ranking22 encoding22 mapping22 record22", 18),
        ["mirror22 filter22", "ranking22", "encoding22", "mapping22 record22"],
    ),
    (
        ("mirror22 filter22 ranking22 encoding22 mapping22 record22", 28),
        ["mirror22 filter22 ranking22", "encoding22 mapping22", "record22"],
    ),
    (
        ("filter22 ranking22 encoding22 mapping22 record22 candle22", 6),
        ["filter22", "ranking22", "encoding22", "mapping22", "record22", "candle22"],
    ),
    (
        ("filter22 ranking22 encoding22 mapping22 record22 candle22", 10),
        ["filter22", "ranking22", "encoding22", "mapping22", "record22", "candle22"],
    ),
    (
        ("filter22 ranking22 encoding22 mapping22 record22 candle22", 18),
        ["filter22 ranking22", "encoding22", "mapping22 record22", "candle22"],
    ),
    (
        ("filter22 ranking22 encoding22 mapping22 record22 candle22", 28),
        ["filter22 ranking22", "encoding22 mapping22", "record22 candle22"],
    ),
    (
        ("ranking22 encoding22 mapping22 record22 candle22 thread22", 6),
        ["ranking22", "encoding22", "mapping22", "record22", "candle22", "thread22"],
    ),
    (
        ("ranking22 encoding22 mapping22 record22 candle22 thread22", 10),
        ["ranking22", "encoding22", "mapping22", "record22", "candle22", "thread22"],
    ),
    (
        ("ranking22 encoding22 mapping22 record22 candle22 thread22", 18),
        ["ranking22", "encoding22", "mapping22 record22", "candle22 thread22"],
    ),
    (
        ("ranking22 encoding22 mapping22 record22 candle22 thread22", 28),
        ["ranking22 encoding22", "mapping22 record22 candle22", "thread22"],
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
