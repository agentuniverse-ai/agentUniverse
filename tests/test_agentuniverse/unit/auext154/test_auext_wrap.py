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
        ("round 154: the quick brown fox jumps over the lazy dog", 4),
        ["round", "154:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 154: the quick brown fox jumps over the lazy dog", 8),
        ["round", "154: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 154: the quick brown fox jumps over the lazy dog", 12),
        ["round 154:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 154: the quick brown fox jumps over the lazy dog", 16),
        ["round 154: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 154: the quick brown fox jumps over the lazy dog", 24),
        ["round 154: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 154: the quick brown fox jumps over the lazy dog", 32),
        ["round 154: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 154: agentuniverse is a framework for multi agents", 4),
        ["round", "154:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 154: agentuniverse is a framework for multi agents", 8),
        ["round", "154:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 154: agentuniverse is a framework for multi agents", 12),
        ["round 154:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 154: agentuniverse is a framework for multi agents", 16),
        ["round 154:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 154: agentuniverse is a framework for multi agents", 24),
        ["round 154: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 154: agentuniverse is a framework for multi agents", 32),
        ["round 154: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 154: knowledge stored as vectors enables retrieval", 4),
        ["round", "154:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 154: knowledge stored as vectors enables retrieval", 8),
        ["round", "154:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 154: knowledge stored as vectors enables retrieval", 12),
        ["round 154:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 154: knowledge stored as vectors enables retrieval", 16),
        ["round 154:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 154: knowledge stored as vectors enables retrieval", 24),
        ["round 154: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 154: knowledge stored as vectors enables retrieval", 32),
        ["round 154: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 154: the processor reads the record then stops", 4),
        ["round", "154:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 154: the processor reads the record then stops", 8),
        ["round", "154: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 154: the processor reads the record then stops", 12),
        ["round 154:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 154: the processor reads the record then stops", 16),
        ["round 154: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 154: the processor reads the record then stops", 24),
        ["round 154: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 154: the processor reads the record then stops", 32),
        ["round 154: the processor reads", "the record then stops"],
    ),
    (
        ("round 154: a worker pulls the next task from the queue", 4),
        ["round", "154:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 154: a worker pulls the next task from the queue", 8),
        ["round", "154: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 154: a worker pulls the next task from the queue", 12),
        ["round 154: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 154: a worker pulls the next task from the queue", 16),
        ["round 154: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 154: a worker pulls the next task from the queue", 24),
        ["round 154: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 154: a worker pulls the next task from the queue", 32),
        ["round 154: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 154: signals travel through the network layer", 4),
        ["round", "154:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 154: signals travel through the network layer", 8),
        ["round", "154:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 154: signals travel through the network layer", 12),
        ["round 154:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 154: signals travel through the network layer", 16),
        ["round 154:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 154: signals travel through the network layer", 24),
        ["round 154: signals", "travel through the", "network layer"],
    ),
    (
        ("round 154: signals travel through the network layer", 32),
        ["round 154: signals travel", "through the network layer"],
    ),
    (
        ("round 154: the gateway routes each request by policy", 4),
        ["round", "154:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 154: the gateway routes each request by policy", 8),
        ["round", "154: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 154: the gateway routes each request by policy", 12),
        ["round 154:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 154: the gateway routes each request by policy", 16),
        ["round 154: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 154: the gateway routes each request by policy", 24),
        ["round 154: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 154: the gateway routes each request by policy", 32),
        ["round 154: the gateway routes", "each request by policy"],
    ),
    (
        ("round 154: memory grows until the buffer is full", 4),
        ["round", "154:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 154: memory grows until the buffer is full", 8),
        ["round", "154:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 154: memory grows until the buffer is full", 12),
        ["round 154:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 154: memory grows until the buffer is full", 16),
        ["round 154:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 154: memory grows until the buffer is full", 24), ["round 154: memory grows", "until the buffer is full"]),
    (("round 154: memory grows until the buffer is full", 32), ["round 154: memory grows until", "the buffer is full"]),
    (
        ("round 154: the cluster mirrors every packet twice", 4),
        ["round", "154:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 154: the cluster mirrors every packet twice", 8),
        ["round", "154: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 154: the cluster mirrors every packet twice", 12),
        ["round 154:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 154: the cluster mirrors every packet twice", 16),
        ["round 154: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 154: the cluster mirrors every packet twice", 24),
        ["round 154: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 154: the cluster mirrors every packet twice", 32),
        ["round 154: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 154: ranking uses tokens learned from the corpus", 4),
        ["round", "154:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 154: ranking uses tokens learned from the corpus", 8),
        ["round", "154:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 154: ranking uses tokens learned from the corpus", 12),
        ["round 154:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 154: ranking uses tokens learned from the corpus", 16),
        ["round 154:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 154: ranking uses tokens learned from the corpus", 24),
        ["round 154: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 154: ranking uses tokens learned from the corpus", 32),
        ["round 154: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 154: a long session ends when the candle dies", 4),
        ["round", "154:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 154: a long session ends when the candle dies", 8),
        ["round", "154: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 154: a long session ends when the candle dies", 12),
        ["round 154: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 154: a long session ends when the candle dies", 16),
        ["round 154: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 154: a long session ends when the candle dies", 24),
        ["round 154: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 154: a long session ends when the candle dies", 32),
        ["round 154: a long session ends", "when the candle dies"],
    ),
    (
        ("round 154: encode the prompt then map the result", 4),
        ["round", "154:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 154: encode the prompt then map the result", 8),
        ["round", "154:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 154: encode the prompt then map the result", 12),
        ["round 154:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 154: encode the prompt then map the result", 16),
        ["round 154:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 154: encode the prompt then map the result", 24),
        ["round 154: encode the", "prompt then map the", "result"],
    ),
    (("round 154: encode the prompt then map the result", 32), ["round 154: encode the prompt", "then map the result"]),
    (
        ("round 154: the kernel wakes the worker at dawn", 4),
        ["round", "154:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 154: the kernel wakes the worker at dawn", 8),
        ["round", "154: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 154: the kernel wakes the worker at dawn", 12),
        ["round 154:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 154: the kernel wakes the worker at dawn", 16), ["round 154: the", "kernel wakes the", "worker at dawn"]),
    (("round 154: the kernel wakes the worker at dawn", 24), ["round 154: the kernel", "wakes the worker at dawn"]),
    (("round 154: the kernel wakes the worker at dawn", 32), ["round 154: the kernel wakes the", "worker at dawn"]),
    (
        ("round 154: service latency drops after the patch", 4),
        ["round", "154:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 154: service latency drops after the patch", 8),
        ["round", "154:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 154: service latency drops after the patch", 12),
        ["round 154:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 154: service latency drops after the patch", 16),
        ["round 154:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 154: service latency drops after the patch", 24),
        ["round 154: service", "latency drops after the", "patch"],
    ),
    (("round 154: service latency drops after the patch", 32), ["round 154: service latency drops", "after the patch"]),
    (
        ("round 154: the library caches every vector it sees", 4),
        ["round", "154:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 154: the library caches every vector it sees", 8),
        ["round", "154: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 154: the library caches every vector it sees", 12),
        ["round 154:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 154: the library caches every vector it sees", 16),
        ["round 154: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 154: the library caches every vector it sees", 24),
        ["round 154: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 154: the library caches every vector it sees", 32),
        ["round 154: the library caches", "every vector it sees"],
    ),
    (
        ("round 154: agents argue then the debate resolves", 4),
        ["round", "154:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 154: agents argue then the debate resolves", 8),
        ["round", "154:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 154: agents argue then the debate resolves", 12),
        ["round 154:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 154: agents argue then the debate resolves", 16),
        ["round 154:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 154: agents argue then the debate resolves", 24), ["round 154: agents argue", "then the debate resolves"]),
    (("round 154: agents argue then the debate resolves", 32), ["round 154: agents argue then the", "debate resolves"]),
    (
        ("round 154: the filter keeps only strong matches", 4),
        ["round", "154:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 154: the filter keeps only strong matches", 8),
        ["round", "154: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 154: the filter keeps only strong matches", 12),
        ["round 154:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 154: the filter keeps only strong matches", 16),
        ["round 154: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 154: the filter keeps only strong matches", 24),
        ["round 154: the filter", "keeps only strong", "matches"],
    ),
    (("round 154: the filter keeps only strong matches", 32), ["round 154: the filter keeps only", "strong matches"]),
    (
        ("round 154: the model answers with a short reply", 4),
        ["round", "154:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 154: the model answers with a short reply", 8),
        ["round", "154: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 154: the model answers with a short reply", 12),
        ["round 154:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 154: the model answers with a short reply", 16),
        ["round 154: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 154: the model answers with a short reply", 24),
        ["round 154: the model", "answers with a short", "reply"],
    ),
    (("round 154: the model answers with a short reply", 32), ["round 154: the model answers", "with a short reply"]),
    (
        ("round 154: the recorder stores the reasoning trace", 4),
        ["round", "154:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 154: the recorder stores the reasoning trace", 8),
        ["round", "154: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 154: the recorder stores the reasoning trace", 12),
        ["round 154:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 154: the recorder stores the reasoning trace", 16),
        ["round 154: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 154: the recorder stores the reasoning trace", 24),
        ["round 154: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 154: the recorder stores the reasoning trace", 32),
        ["round 154: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 154: the angel watches the processor run", 4),
        ["round", "154:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 154: the angel watches the processor run", 8),
        ["round", "154: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 154: the angel watches the processor run", 12),
        ["round 154:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 154: the angel watches the processor run", 16),
        ["round 154: the", "angel watches", "the processor", "run"],
    ),
    (("round 154: the angel watches the processor run", 24), ["round 154: the angel", "watches the processor", "run"]),
    (("round 154: the angel watches the processor run", 32), ["round 154: the angel watches the", "processor run"]),
    (
        ("round 154: angle of the vector decides the match", 4),
        ["round", "154:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 154: angle of the vector decides the match", 8),
        ["round", "154:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 154: angle of the vector decides the match", 12),
        ["round 154:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 154: angle of the vector decides the match", 16),
        ["round 154: angle", "of the vector", "decides the", "match"],
    ),
    (("round 154: angle of the vector decides the match", 24), ["round 154: angle of the", "vector decides the match"]),
    (("round 154: angle of the vector decides the match", 32), ["round 154: angle of the vector", "decides the match"]),
    (
        ("round 154: the candle burns twice as long at night", 4),
        ["round", "154:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 154: the candle burns twice as long at night", 8),
        ["round", "154: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 154: the candle burns twice as long at night", 12),
        ["round 154:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 154: the candle burns twice as long at night", 16),
        ["round 154: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 154: the candle burns twice as long at night", 24),
        ["round 154: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 154: the candle burns twice as long at night", 32),
        ["round 154: the candle burns", "twice as long at night"],
    ),
    (
        ("round 154: a mirror of the universe in one line", 4),
        ["round", "154:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 154: a mirror of the universe in one line", 8),
        ["round", "154: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 154: a mirror of the universe in one line", 12),
        ["round 154: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 154: a mirror of the universe in one line", 16),
        ["round 154: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 154: a mirror of the universe in one line", 24), ["round 154: a mirror of", "the universe in one line"]),
    (("round 154: a mirror of the universe in one line", 32), ["round 154: a mirror of the", "universe in one line"]),
    (
        ("round 154: the queue drains before the storm", 4),
        ["round", "154:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 154: the queue drains before the storm", 8),
        ["round", "154: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 154: the queue drains before the storm", 12),
        ["round 154:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 154: the queue drains before the storm", 16), ["round 154: the", "queue drains", "before the storm"]),
    (("round 154: the queue drains before the storm", 24), ["round 154: the queue", "drains before the storm"]),
    (("round 154: the queue drains before the storm", 32), ["round 154: the queue drains", "before the storm"]),
    (
        ("kitten154 sitting154 agent154 angle154 universe154 memory154", 6),
        ["kitten154", "sitting154", "agent154", "angle154", "universe154", "memory154"],
    ),
    (
        ("kitten154 sitting154 agent154 angle154 universe154 memory154", 10),
        ["kitten154", "sitting154", "agent154", "angle154", "universe154", "memory154"],
    ),
    (
        ("kitten154 sitting154 agent154 angle154 universe154 memory154", 18),
        ["kitten154", "sitting154", "agent154 angle154", "universe154", "memory154"],
    ),
    (
        ("kitten154 sitting154 agent154 angle154 universe154 memory154", 28),
        ["kitten154 sitting154", "agent154 angle154", "universe154 memory154"],
    ),
    (
        ("sitting154 agent154 angle154 universe154 memory154 stream154", 6),
        ["sitting154", "agent154", "angle154", "universe154", "memory154", "stream154"],
    ),
    (
        ("sitting154 agent154 angle154 universe154 memory154 stream154", 10),
        ["sitting154", "agent154", "angle154", "universe154", "memory154", "stream154"],
    ),
    (
        ("sitting154 agent154 angle154 universe154 memory154 stream154", 18),
        ["sitting154", "agent154 angle154", "universe154", "memory154", "stream154"],
    ),
    (
        ("sitting154 agent154 angle154 universe154 memory154 stream154", 28),
        ["sitting154 agent154 angle154", "universe154 memory154", "stream154"],
    ),
    (
        ("agent154 angle154 universe154 memory154 stream154 context154", 6),
        ["agent154", "angle154", "universe154", "memory154", "stream154", "context154"],
    ),
    (
        ("agent154 angle154 universe154 memory154 stream154 context154", 10),
        ["agent154", "angle154", "universe154", "memory154", "stream154", "context154"],
    ),
    (
        ("agent154 angle154 universe154 memory154 stream154 context154", 18),
        ["agent154 angle154", "universe154", "memory154", "stream154", "context154"],
    ),
    (
        ("agent154 angle154 universe154 memory154 stream154 context154", 28),
        ["agent154 angle154", "universe154 memory154", "stream154 context154"],
    ),
    (
        ("angle154 universe154 memory154 stream154 context154 knowledge154", 6),
        ["angle154", "universe154", "memory154", "stream154", "context154", "knowledge154"],
    ),
    (
        ("angle154 universe154 memory154 stream154 context154 knowledge154", 10),
        ["angle154", "universe154", "memory154", "stream154", "context154", "knowledge154"],
    ),
    (
        ("angle154 universe154 memory154 stream154 context154 knowledge154", 18),
        ["angle154", "universe154", "memory154", "stream154", "context154", "knowledge154"],
    ),
    (
        ("angle154 universe154 memory154 stream154 context154 knowledge154", 28),
        ["angle154 universe154", "memory154 stream154", "context154 knowledge154"],
    ),
    (
        ("universe154 memory154 stream154 context154 knowledge154 vector154", 6),
        ["universe154", "memory154", "stream154", "context154", "knowledge154", "vector154"],
    ),
    (
        ("universe154 memory154 stream154 context154 knowledge154 vector154", 10),
        ["universe154", "memory154", "stream154", "context154", "knowledge154", "vector154"],
    ),
    (
        ("universe154 memory154 stream154 context154 knowledge154 vector154", 18),
        ["universe154", "memory154", "stream154", "context154", "knowledge154", "vector154"],
    ),
    (
        ("universe154 memory154 stream154 context154 knowledge154 vector154", 28),
        ["universe154 memory154", "stream154 context154", "knowledge154 vector154"],
    ),
    (
        ("memory154 stream154 context154 knowledge154 vector154 processor154", 6),
        ["memory154", "stream154", "context154", "knowledge154", "vector154", "processor154"],
    ),
    (
        ("memory154 stream154 context154 knowledge154 vector154 processor154", 10),
        ["memory154", "stream154", "context154", "knowledge154", "vector154", "processor154"],
    ),
    (
        ("memory154 stream154 context154 knowledge154 vector154 processor154", 18),
        ["memory154", "stream154", "context154", "knowledge154", "vector154", "processor154"],
    ),
    (
        ("memory154 stream154 context154 knowledge154 vector154 processor154", 28),
        ["memory154 stream154", "context154 knowledge154", "vector154 processor154"],
    ),
    (
        ("stream154 context154 knowledge154 vector154 processor154 reasoning154", 6),
        ["stream154", "context154", "knowledge154", "vector154", "processor154", "reasoning154"],
    ),
    (
        ("stream154 context154 knowledge154 vector154 processor154 reasoning154", 10),
        ["stream154", "context154", "knowledge154", "vector154", "processor154", "reasoning154"],
    ),
    (
        ("stream154 context154 knowledge154 vector154 processor154 reasoning154", 18),
        ["stream154", "context154", "knowledge154", "vector154", "processor154", "reasoning154"],
    ),
    (
        ("stream154 context154 knowledge154 vector154 processor154 reasoning154", 28),
        ["stream154 context154", "knowledge154 vector154", "processor154 reasoning154"],
    ),
    (
        ("context154 knowledge154 vector154 processor154 reasoning154 machine154", 6),
        ["context154", "knowledge154", "vector154", "processor154", "reasoning154", "machine154"],
    ),
    (
        ("context154 knowledge154 vector154 processor154 reasoning154 machine154", 10),
        ["context154", "knowledge154", "vector154", "processor154", "reasoning154", "machine154"],
    ),
    (
        ("context154 knowledge154 vector154 processor154 reasoning154 machine154", 18),
        ["context154", "knowledge154", "vector154", "processor154", "reasoning154", "machine154"],
    ),
    (
        ("context154 knowledge154 vector154 processor154 reasoning154 machine154", 28),
        ["context154 knowledge154", "vector154 processor154", "reasoning154 machine154"],
    ),
    (
        ("knowledge154 vector154 processor154 reasoning154 machine154 learning154", 6),
        ["knowledge154", "vector154", "processor154", "reasoning154", "machine154", "learning154"],
    ),
    (
        ("knowledge154 vector154 processor154 reasoning154 machine154 learning154", 10),
        ["knowledge154", "vector154", "processor154", "reasoning154", "machine154", "learning154"],
    ),
    (
        ("knowledge154 vector154 processor154 reasoning154 machine154 learning154", 18),
        ["knowledge154", "vector154", "processor154", "reasoning154", "machine154", "learning154"],
    ),
    (
        ("knowledge154 vector154 processor154 reasoning154 machine154 learning154", 28),
        ["knowledge154 vector154", "processor154 reasoning154", "machine154 learning154"],
    ),
    (
        ("vector154 processor154 reasoning154 machine154 learning154 model154", 6),
        ["vector154", "processor154", "reasoning154", "machine154", "learning154", "model154"],
    ),
    (
        ("vector154 processor154 reasoning154 machine154 learning154 model154", 10),
        ["vector154", "processor154", "reasoning154", "machine154", "learning154", "model154"],
    ),
    (
        ("vector154 processor154 reasoning154 machine154 learning154 model154", 18),
        ["vector154", "processor154", "reasoning154", "machine154", "learning154", "model154"],
    ),
    (
        ("vector154 processor154 reasoning154 machine154 learning154 model154", 28),
        ["vector154 processor154", "reasoning154 machine154", "learning154 model154"],
    ),
    (
        ("processor154 reasoning154 machine154 learning154 model154 token154", 6),
        ["processor154", "reasoning154", "machine154", "learning154", "model154", "token154"],
    ),
    (
        ("processor154 reasoning154 machine154 learning154 model154 token154", 10),
        ["processor154", "reasoning154", "machine154", "learning154", "model154", "token154"],
    ),
    (
        ("processor154 reasoning154 machine154 learning154 model154 token154", 18),
        ["processor154", "reasoning154", "machine154", "learning154", "model154 token154"],
    ),
    (
        ("processor154 reasoning154 machine154 learning154 model154 token154", 28),
        ["processor154 reasoning154", "machine154 learning154", "model154 token154"],
    ),
    (
        ("reasoning154 machine154 learning154 model154 token154 prompt154", 6),
        ["reasoning154", "machine154", "learning154", "model154", "token154", "prompt154"],
    ),
    (
        ("reasoning154 machine154 learning154 model154 token154 prompt154", 10),
        ["reasoning154", "machine154", "learning154", "model154", "token154", "prompt154"],
    ),
    (
        ("reasoning154 machine154 learning154 model154 token154 prompt154", 18),
        ["reasoning154", "machine154", "learning154", "model154 token154", "prompt154"],
    ),
    (
        ("reasoning154 machine154 learning154 model154 token154 prompt154", 28),
        ["reasoning154 machine154", "learning154 model154", "token154 prompt154"],
    ),
    (
        ("machine154 learning154 model154 token154 prompt154 session154", 6),
        ["machine154", "learning154", "model154", "token154", "prompt154", "session154"],
    ),
    (
        ("machine154 learning154 model154 token154 prompt154 session154", 10),
        ["machine154", "learning154", "model154", "token154", "prompt154", "session154"],
    ),
    (
        ("machine154 learning154 model154 token154 prompt154 session154", 18),
        ["machine154", "learning154", "model154 token154", "prompt154", "session154"],
    ),
    (
        ("machine154 learning154 model154 token154 prompt154 session154", 28),
        ["machine154 learning154", "model154 token154 prompt154", "session154"],
    ),
    (
        ("learning154 model154 token154 prompt154 session154 library154", 6),
        ["learning154", "model154", "token154", "prompt154", "session154", "library154"],
    ),
    (
        ("learning154 model154 token154 prompt154 session154 library154", 10),
        ["learning154", "model154", "token154", "prompt154", "session154", "library154"],
    ),
    (
        ("learning154 model154 token154 prompt154 session154 library154", 18),
        ["learning154", "model154 token154", "prompt154", "session154", "library154"],
    ),
    (
        ("learning154 model154 token154 prompt154 session154 library154", 28),
        ["learning154 model154", "token154 prompt154", "session154 library154"],
    ),
    (
        ("model154 token154 prompt154 session154 library154 service154", 6),
        ["model154", "token154", "prompt154", "session154", "library154", "service154"],
    ),
    (
        ("model154 token154 prompt154 session154 library154 service154", 10),
        ["model154", "token154", "prompt154", "session154", "library154", "service154"],
    ),
    (
        ("model154 token154 prompt154 session154 library154 service154", 18),
        ["model154 token154", "prompt154", "session154", "library154", "service154"],
    ),
    (
        ("model154 token154 prompt154 session154 library154 service154", 28),
        ["model154 token154 prompt154", "session154 library154", "service154"],
    ),
    (
        ("token154 prompt154 session154 library154 service154 gateway154", 6),
        ["token154", "prompt154", "session154", "library154", "service154", "gateway154"],
    ),
    (
        ("token154 prompt154 session154 library154 service154 gateway154", 10),
        ["token154", "prompt154", "session154", "library154", "service154", "gateway154"],
    ),
    (
        ("token154 prompt154 session154 library154 service154 gateway154", 18),
        ["token154 prompt154", "session154", "library154", "service154", "gateway154"],
    ),
    (
        ("token154 prompt154 session154 library154 service154 gateway154", 28),
        ["token154 prompt154", "session154 library154", "service154 gateway154"],
    ),
    (
        ("prompt154 session154 library154 service154 gateway154 storage154", 6),
        ["prompt154", "session154", "library154", "service154", "gateway154", "storage154"],
    ),
    (
        ("prompt154 session154 library154 service154 gateway154 storage154", 10),
        ["prompt154", "session154", "library154", "service154", "gateway154", "storage154"],
    ),
    (
        ("prompt154 session154 library154 service154 gateway154 storage154", 18),
        ["prompt154", "session154", "library154", "service154", "gateway154", "storage154"],
    ),
    (
        ("prompt154 session154 library154 service154 gateway154 storage154", 28),
        ["prompt154 session154", "library154 service154", "gateway154 storage154"],
    ),
    (
        ("session154 library154 service154 gateway154 storage154 network154", 6),
        ["session154", "library154", "service154", "gateway154", "storage154", "network154"],
    ),
    (
        ("session154 library154 service154 gateway154 storage154 network154", 10),
        ["session154", "library154", "service154", "gateway154", "storage154", "network154"],
    ),
    (
        ("session154 library154 service154 gateway154 storage154 network154", 18),
        ["session154", "library154", "service154", "gateway154", "storage154", "network154"],
    ),
    (
        ("session154 library154 service154 gateway154 storage154 network154", 28),
        ["session154 library154", "service154 gateway154", "storage154 network154"],
    ),
    (
        ("library154 service154 gateway154 storage154 network154 latency154", 6),
        ["library154", "service154", "gateway154", "storage154", "network154", "latency154"],
    ),
    (
        ("library154 service154 gateway154 storage154 network154 latency154", 10),
        ["library154", "service154", "gateway154", "storage154", "network154", "latency154"],
    ),
    (
        ("library154 service154 gateway154 storage154 network154 latency154", 18),
        ["library154", "service154", "gateway154", "storage154", "network154", "latency154"],
    ),
    (
        ("library154 service154 gateway154 storage154 network154 latency154", 28),
        ["library154 service154", "gateway154 storage154", "network154 latency154"],
    ),
    (
        ("service154 gateway154 storage154 network154 latency154 buffer154", 6),
        ["service154", "gateway154", "storage154", "network154", "latency154", "buffer154"],
    ),
    (
        ("service154 gateway154 storage154 network154 latency154 buffer154", 10),
        ["service154", "gateway154", "storage154", "network154", "latency154", "buffer154"],
    ),
    (
        ("service154 gateway154 storage154 network154 latency154 buffer154", 18),
        ["service154", "gateway154", "storage154", "network154", "latency154", "buffer154"],
    ),
    (
        ("service154 gateway154 storage154 network154 latency154 buffer154", 28),
        ["service154 gateway154", "storage154 network154", "latency154 buffer154"],
    ),
    (
        ("gateway154 storage154 network154 latency154 buffer154 queue154", 6),
        ["gateway154", "storage154", "network154", "latency154", "buffer154", "queue154"],
    ),
    (
        ("gateway154 storage154 network154 latency154 buffer154 queue154", 10),
        ["gateway154", "storage154", "network154", "latency154", "buffer154", "queue154"],
    ),
    (
        ("gateway154 storage154 network154 latency154 buffer154 queue154", 18),
        ["gateway154", "storage154", "network154", "latency154", "buffer154 queue154"],
    ),
    (
        ("gateway154 storage154 network154 latency154 buffer154 queue154", 28),
        ["gateway154 storage154", "network154 latency154", "buffer154 queue154"],
    ),
    (
        ("storage154 network154 latency154 buffer154 queue154 worker154", 6),
        ["storage154", "network154", "latency154", "buffer154", "queue154", "worker154"],
    ),
    (
        ("storage154 network154 latency154 buffer154 queue154 worker154", 10),
        ["storage154", "network154", "latency154", "buffer154", "queue154", "worker154"],
    ),
    (
        ("storage154 network154 latency154 buffer154 queue154 worker154", 18),
        ["storage154", "network154", "latency154", "buffer154 queue154", "worker154"],
    ),
    (
        ("storage154 network154 latency154 buffer154 queue154 worker154", 28),
        ["storage154 network154", "latency154 buffer154", "queue154 worker154"],
    ),
    (
        ("network154 latency154 buffer154 queue154 worker154 kernel154", 6),
        ["network154", "latency154", "buffer154", "queue154", "worker154", "kernel154"],
    ),
    (
        ("network154 latency154 buffer154 queue154 worker154 kernel154", 10),
        ["network154", "latency154", "buffer154", "queue154", "worker154", "kernel154"],
    ),
    (
        ("network154 latency154 buffer154 queue154 worker154 kernel154", 18),
        ["network154", "latency154", "buffer154 queue154", "worker154", "kernel154"],
    ),
    (
        ("network154 latency154 buffer154 queue154 worker154 kernel154", 28),
        ["network154 latency154", "buffer154 queue154 worker154", "kernel154"],
    ),
    (
        ("latency154 buffer154 queue154 worker154 kernel154 signal154", 6),
        ["latency154", "buffer154", "queue154", "worker154", "kernel154", "signal154"],
    ),
    (
        ("latency154 buffer154 queue154 worker154 kernel154 signal154", 10),
        ["latency154", "buffer154", "queue154", "worker154", "kernel154", "signal154"],
    ),
    (
        ("latency154 buffer154 queue154 worker154 kernel154 signal154", 18),
        ["latency154", "buffer154 queue154", "worker154", "kernel154", "signal154"],
    ),
    (
        ("latency154 buffer154 queue154 worker154 kernel154 signal154", 28),
        ["latency154 buffer154", "queue154 worker154 kernel154", "signal154"],
    ),
    (
        ("buffer154 queue154 worker154 kernel154 signal154 packet154", 6),
        ["buffer154", "queue154", "worker154", "kernel154", "signal154", "packet154"],
    ),
    (
        ("buffer154 queue154 worker154 kernel154 signal154 packet154", 10),
        ["buffer154", "queue154", "worker154", "kernel154", "signal154", "packet154"],
    ),
    (
        ("buffer154 queue154 worker154 kernel154 signal154 packet154", 18),
        ["buffer154 queue154", "worker154", "kernel154", "signal154", "packet154"],
    ),
    (
        ("buffer154 queue154 worker154 kernel154 signal154 packet154", 28),
        ["buffer154 queue154 worker154", "kernel154 signal154", "packet154"],
    ),
    (
        ("queue154 worker154 kernel154 signal154 packet154 router154", 6),
        ["queue154", "worker154", "kernel154", "signal154", "packet154", "router154"],
    ),
    (
        ("queue154 worker154 kernel154 signal154 packet154 router154", 10),
        ["queue154", "worker154", "kernel154", "signal154", "packet154", "router154"],
    ),
    (
        ("queue154 worker154 kernel154 signal154 packet154 router154", 18),
        ["queue154 worker154", "kernel154", "signal154", "packet154", "router154"],
    ),
    (
        ("queue154 worker154 kernel154 signal154 packet154 router154", 28),
        ["queue154 worker154 kernel154", "signal154 packet154", "router154"],
    ),
    (
        ("worker154 kernel154 signal154 packet154 router154 cluster154", 6),
        ["worker154", "kernel154", "signal154", "packet154", "router154", "cluster154"],
    ),
    (
        ("worker154 kernel154 signal154 packet154 router154 cluster154", 10),
        ["worker154", "kernel154", "signal154", "packet154", "router154", "cluster154"],
    ),
    (
        ("worker154 kernel154 signal154 packet154 router154 cluster154", 18),
        ["worker154", "kernel154", "signal154", "packet154", "router154", "cluster154"],
    ),
    (
        ("worker154 kernel154 signal154 packet154 router154 cluster154", 28),
        ["worker154 kernel154", "signal154 packet154", "router154 cluster154"],
    ),
    (
        ("kernel154 signal154 packet154 router154 cluster154 mirror154", 6),
        ["kernel154", "signal154", "packet154", "router154", "cluster154", "mirror154"],
    ),
    (
        ("kernel154 signal154 packet154 router154 cluster154 mirror154", 10),
        ["kernel154", "signal154", "packet154", "router154", "cluster154", "mirror154"],
    ),
    (
        ("kernel154 signal154 packet154 router154 cluster154 mirror154", 18),
        ["kernel154", "signal154", "packet154", "router154", "cluster154", "mirror154"],
    ),
    (
        ("kernel154 signal154 packet154 router154 cluster154 mirror154", 28),
        ["kernel154 signal154", "packet154 router154", "cluster154 mirror154"],
    ),
    (
        ("signal154 packet154 router154 cluster154 mirror154 filter154", 6),
        ["signal154", "packet154", "router154", "cluster154", "mirror154", "filter154"],
    ),
    (
        ("signal154 packet154 router154 cluster154 mirror154 filter154", 10),
        ["signal154", "packet154", "router154", "cluster154", "mirror154", "filter154"],
    ),
    (
        ("signal154 packet154 router154 cluster154 mirror154 filter154", 18),
        ["signal154", "packet154", "router154", "cluster154", "mirror154", "filter154"],
    ),
    (
        ("signal154 packet154 router154 cluster154 mirror154 filter154", 28),
        ["signal154 packet154", "router154 cluster154", "mirror154 filter154"],
    ),
    (
        ("packet154 router154 cluster154 mirror154 filter154 ranking154", 6),
        ["packet154", "router154", "cluster154", "mirror154", "filter154", "ranking154"],
    ),
    (
        ("packet154 router154 cluster154 mirror154 filter154 ranking154", 10),
        ["packet154", "router154", "cluster154", "mirror154", "filter154", "ranking154"],
    ),
    (
        ("packet154 router154 cluster154 mirror154 filter154 ranking154", 18),
        ["packet154", "router154", "cluster154", "mirror154", "filter154", "ranking154"],
    ),
    (
        ("packet154 router154 cluster154 mirror154 filter154 ranking154", 28),
        ["packet154 router154", "cluster154 mirror154", "filter154 ranking154"],
    ),
    (
        ("router154 cluster154 mirror154 filter154 ranking154 encoding154", 6),
        ["router154", "cluster154", "mirror154", "filter154", "ranking154", "encoding154"],
    ),
    (
        ("router154 cluster154 mirror154 filter154 ranking154 encoding154", 10),
        ["router154", "cluster154", "mirror154", "filter154", "ranking154", "encoding154"],
    ),
    (
        ("router154 cluster154 mirror154 filter154 ranking154 encoding154", 18),
        ["router154", "cluster154", "mirror154", "filter154", "ranking154", "encoding154"],
    ),
    (
        ("router154 cluster154 mirror154 filter154 ranking154 encoding154", 28),
        ["router154 cluster154", "mirror154 filter154", "ranking154 encoding154"],
    ),
    (
        ("cluster154 mirror154 filter154 ranking154 encoding154 mapping154", 6),
        ["cluster154", "mirror154", "filter154", "ranking154", "encoding154", "mapping154"],
    ),
    (
        ("cluster154 mirror154 filter154 ranking154 encoding154 mapping154", 10),
        ["cluster154", "mirror154", "filter154", "ranking154", "encoding154", "mapping154"],
    ),
    (
        ("cluster154 mirror154 filter154 ranking154 encoding154 mapping154", 18),
        ["cluster154", "mirror154", "filter154", "ranking154", "encoding154", "mapping154"],
    ),
    (
        ("cluster154 mirror154 filter154 ranking154 encoding154 mapping154", 28),
        ["cluster154 mirror154", "filter154 ranking154", "encoding154 mapping154"],
    ),
    (
        ("mirror154 filter154 ranking154 encoding154 mapping154 record154", 6),
        ["mirror154", "filter154", "ranking154", "encoding154", "mapping154", "record154"],
    ),
    (
        ("mirror154 filter154 ranking154 encoding154 mapping154 record154", 10),
        ["mirror154", "filter154", "ranking154", "encoding154", "mapping154", "record154"],
    ),
    (
        ("mirror154 filter154 ranking154 encoding154 mapping154 record154", 18),
        ["mirror154", "filter154", "ranking154", "encoding154", "mapping154", "record154"],
    ),
    (
        ("mirror154 filter154 ranking154 encoding154 mapping154 record154", 28),
        ["mirror154 filter154", "ranking154 encoding154", "mapping154 record154"],
    ),
    (
        ("filter154 ranking154 encoding154 mapping154 record154 candle154", 6),
        ["filter154", "ranking154", "encoding154", "mapping154", "record154", "candle154"],
    ),
    (
        ("filter154 ranking154 encoding154 mapping154 record154 candle154", 10),
        ["filter154", "ranking154", "encoding154", "mapping154", "record154", "candle154"],
    ),
    (
        ("filter154 ranking154 encoding154 mapping154 record154 candle154", 18),
        ["filter154", "ranking154", "encoding154", "mapping154", "record154", "candle154"],
    ),
    (
        ("filter154 ranking154 encoding154 mapping154 record154 candle154", 28),
        ["filter154 ranking154", "encoding154 mapping154", "record154 candle154"],
    ),
    (
        ("ranking154 encoding154 mapping154 record154 candle154 thread154", 6),
        ["ranking154", "encoding154", "mapping154", "record154", "candle154", "thread154"],
    ),
    (
        ("ranking154 encoding154 mapping154 record154 candle154 thread154", 10),
        ["ranking154", "encoding154", "mapping154", "record154", "candle154", "thread154"],
    ),
    (
        ("ranking154 encoding154 mapping154 record154 candle154 thread154", 18),
        ["ranking154", "encoding154", "mapping154", "record154", "candle154", "thread154"],
    ),
    (
        ("ranking154 encoding154 mapping154 record154 candle154 thread154", 28),
        ["ranking154 encoding154", "mapping154 record154", "candle154 thread154"],
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
