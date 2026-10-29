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
        ("round 134: the quick brown fox jumps over the lazy dog", 4),
        ["round", "134:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 134: the quick brown fox jumps over the lazy dog", 8),
        ["round", "134: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 134: the quick brown fox jumps over the lazy dog", 12),
        ["round 134:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 134: the quick brown fox jumps over the lazy dog", 16),
        ["round 134: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 134: the quick brown fox jumps over the lazy dog", 24),
        ["round 134: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 134: the quick brown fox jumps over the lazy dog", 32),
        ["round 134: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 134: agentuniverse is a framework for multi agents", 4),
        ["round", "134:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 134: agentuniverse is a framework for multi agents", 8),
        ["round", "134:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 134: agentuniverse is a framework for multi agents", 12),
        ["round 134:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 134: agentuniverse is a framework for multi agents", 16),
        ["round 134:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 134: agentuniverse is a framework for multi agents", 24),
        ["round 134: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 134: agentuniverse is a framework for multi agents", 32),
        ["round 134: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 134: knowledge stored as vectors enables retrieval", 4),
        ["round", "134:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 134: knowledge stored as vectors enables retrieval", 8),
        ["round", "134:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 134: knowledge stored as vectors enables retrieval", 12),
        ["round 134:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 134: knowledge stored as vectors enables retrieval", 16),
        ["round 134:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 134: knowledge stored as vectors enables retrieval", 24),
        ["round 134: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 134: knowledge stored as vectors enables retrieval", 32),
        ["round 134: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 134: the processor reads the record then stops", 4),
        ["round", "134:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 134: the processor reads the record then stops", 8),
        ["round", "134: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 134: the processor reads the record then stops", 12),
        ["round 134:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 134: the processor reads the record then stops", 16),
        ["round 134: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 134: the processor reads the record then stops", 24),
        ["round 134: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 134: the processor reads the record then stops", 32),
        ["round 134: the processor reads", "the record then stops"],
    ),
    (
        ("round 134: a worker pulls the next task from the queue", 4),
        ["round", "134:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 134: a worker pulls the next task from the queue", 8),
        ["round", "134: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 134: a worker pulls the next task from the queue", 12),
        ["round 134: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 134: a worker pulls the next task from the queue", 16),
        ["round 134: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 134: a worker pulls the next task from the queue", 24),
        ["round 134: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 134: a worker pulls the next task from the queue", 32),
        ["round 134: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 134: signals travel through the network layer", 4),
        ["round", "134:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 134: signals travel through the network layer", 8),
        ["round", "134:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 134: signals travel through the network layer", 12),
        ["round 134:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 134: signals travel through the network layer", 16),
        ["round 134:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 134: signals travel through the network layer", 24),
        ["round 134: signals", "travel through the", "network layer"],
    ),
    (
        ("round 134: signals travel through the network layer", 32),
        ["round 134: signals travel", "through the network layer"],
    ),
    (
        ("round 134: the gateway routes each request by policy", 4),
        ["round", "134:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 134: the gateway routes each request by policy", 8),
        ["round", "134: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 134: the gateway routes each request by policy", 12),
        ["round 134:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 134: the gateway routes each request by policy", 16),
        ["round 134: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 134: the gateway routes each request by policy", 24),
        ["round 134: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 134: the gateway routes each request by policy", 32),
        ["round 134: the gateway routes", "each request by policy"],
    ),
    (
        ("round 134: memory grows until the buffer is full", 4),
        ["round", "134:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 134: memory grows until the buffer is full", 8),
        ["round", "134:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 134: memory grows until the buffer is full", 12),
        ["round 134:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 134: memory grows until the buffer is full", 16),
        ["round 134:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 134: memory grows until the buffer is full", 24), ["round 134: memory grows", "until the buffer is full"]),
    (("round 134: memory grows until the buffer is full", 32), ["round 134: memory grows until", "the buffer is full"]),
    (
        ("round 134: the cluster mirrors every packet twice", 4),
        ["round", "134:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 134: the cluster mirrors every packet twice", 8),
        ["round", "134: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 134: the cluster mirrors every packet twice", 12),
        ["round 134:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 134: the cluster mirrors every packet twice", 16),
        ["round 134: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 134: the cluster mirrors every packet twice", 24),
        ["round 134: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 134: the cluster mirrors every packet twice", 32),
        ["round 134: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 134: ranking uses tokens learned from the corpus", 4),
        ["round", "134:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 134: ranking uses tokens learned from the corpus", 8),
        ["round", "134:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 134: ranking uses tokens learned from the corpus", 12),
        ["round 134:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 134: ranking uses tokens learned from the corpus", 16),
        ["round 134:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 134: ranking uses tokens learned from the corpus", 24),
        ["round 134: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 134: ranking uses tokens learned from the corpus", 32),
        ["round 134: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 134: a long session ends when the candle dies", 4),
        ["round", "134:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 134: a long session ends when the candle dies", 8),
        ["round", "134: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 134: a long session ends when the candle dies", 12),
        ["round 134: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 134: a long session ends when the candle dies", 16),
        ["round 134: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 134: a long session ends when the candle dies", 24),
        ["round 134: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 134: a long session ends when the candle dies", 32),
        ["round 134: a long session ends", "when the candle dies"],
    ),
    (
        ("round 134: encode the prompt then map the result", 4),
        ["round", "134:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 134: encode the prompt then map the result", 8),
        ["round", "134:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 134: encode the prompt then map the result", 12),
        ["round 134:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 134: encode the prompt then map the result", 16),
        ["round 134:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 134: encode the prompt then map the result", 24),
        ["round 134: encode the", "prompt then map the", "result"],
    ),
    (("round 134: encode the prompt then map the result", 32), ["round 134: encode the prompt", "then map the result"]),
    (
        ("round 134: the kernel wakes the worker at dawn", 4),
        ["round", "134:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 134: the kernel wakes the worker at dawn", 8),
        ["round", "134: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 134: the kernel wakes the worker at dawn", 12),
        ["round 134:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 134: the kernel wakes the worker at dawn", 16), ["round 134: the", "kernel wakes the", "worker at dawn"]),
    (("round 134: the kernel wakes the worker at dawn", 24), ["round 134: the kernel", "wakes the worker at dawn"]),
    (("round 134: the kernel wakes the worker at dawn", 32), ["round 134: the kernel wakes the", "worker at dawn"]),
    (
        ("round 134: service latency drops after the patch", 4),
        ["round", "134:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 134: service latency drops after the patch", 8),
        ["round", "134:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 134: service latency drops after the patch", 12),
        ["round 134:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 134: service latency drops after the patch", 16),
        ["round 134:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 134: service latency drops after the patch", 24),
        ["round 134: service", "latency drops after the", "patch"],
    ),
    (("round 134: service latency drops after the patch", 32), ["round 134: service latency drops", "after the patch"]),
    (
        ("round 134: the library caches every vector it sees", 4),
        ["round", "134:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 134: the library caches every vector it sees", 8),
        ["round", "134: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 134: the library caches every vector it sees", 12),
        ["round 134:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 134: the library caches every vector it sees", 16),
        ["round 134: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 134: the library caches every vector it sees", 24),
        ["round 134: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 134: the library caches every vector it sees", 32),
        ["round 134: the library caches", "every vector it sees"],
    ),
    (
        ("round 134: agents argue then the debate resolves", 4),
        ["round", "134:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 134: agents argue then the debate resolves", 8),
        ["round", "134:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 134: agents argue then the debate resolves", 12),
        ["round 134:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 134: agents argue then the debate resolves", 16),
        ["round 134:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 134: agents argue then the debate resolves", 24), ["round 134: agents argue", "then the debate resolves"]),
    (("round 134: agents argue then the debate resolves", 32), ["round 134: agents argue then the", "debate resolves"]),
    (
        ("round 134: the filter keeps only strong matches", 4),
        ["round", "134:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 134: the filter keeps only strong matches", 8),
        ["round", "134: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 134: the filter keeps only strong matches", 12),
        ["round 134:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 134: the filter keeps only strong matches", 16),
        ["round 134: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 134: the filter keeps only strong matches", 24),
        ["round 134: the filter", "keeps only strong", "matches"],
    ),
    (("round 134: the filter keeps only strong matches", 32), ["round 134: the filter keeps only", "strong matches"]),
    (
        ("round 134: the model answers with a short reply", 4),
        ["round", "134:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 134: the model answers with a short reply", 8),
        ["round", "134: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 134: the model answers with a short reply", 12),
        ["round 134:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 134: the model answers with a short reply", 16),
        ["round 134: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 134: the model answers with a short reply", 24),
        ["round 134: the model", "answers with a short", "reply"],
    ),
    (("round 134: the model answers with a short reply", 32), ["round 134: the model answers", "with a short reply"]),
    (
        ("round 134: the recorder stores the reasoning trace", 4),
        ["round", "134:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 134: the recorder stores the reasoning trace", 8),
        ["round", "134: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 134: the recorder stores the reasoning trace", 12),
        ["round 134:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 134: the recorder stores the reasoning trace", 16),
        ["round 134: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 134: the recorder stores the reasoning trace", 24),
        ["round 134: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 134: the recorder stores the reasoning trace", 32),
        ["round 134: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 134: the angel watches the processor run", 4),
        ["round", "134:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 134: the angel watches the processor run", 8),
        ["round", "134: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 134: the angel watches the processor run", 12),
        ["round 134:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 134: the angel watches the processor run", 16),
        ["round 134: the", "angel watches", "the processor", "run"],
    ),
    (("round 134: the angel watches the processor run", 24), ["round 134: the angel", "watches the processor", "run"]),
    (("round 134: the angel watches the processor run", 32), ["round 134: the angel watches the", "processor run"]),
    (
        ("round 134: angle of the vector decides the match", 4),
        ["round", "134:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 134: angle of the vector decides the match", 8),
        ["round", "134:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 134: angle of the vector decides the match", 12),
        ["round 134:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 134: angle of the vector decides the match", 16),
        ["round 134: angle", "of the vector", "decides the", "match"],
    ),
    (("round 134: angle of the vector decides the match", 24), ["round 134: angle of the", "vector decides the match"]),
    (("round 134: angle of the vector decides the match", 32), ["round 134: angle of the vector", "decides the match"]),
    (
        ("round 134: the candle burns twice as long at night", 4),
        ["round", "134:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 134: the candle burns twice as long at night", 8),
        ["round", "134: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 134: the candle burns twice as long at night", 12),
        ["round 134:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 134: the candle burns twice as long at night", 16),
        ["round 134: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 134: the candle burns twice as long at night", 24),
        ["round 134: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 134: the candle burns twice as long at night", 32),
        ["round 134: the candle burns", "twice as long at night"],
    ),
    (
        ("round 134: a mirror of the universe in one line", 4),
        ["round", "134:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 134: a mirror of the universe in one line", 8),
        ["round", "134: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 134: a mirror of the universe in one line", 12),
        ["round 134: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 134: a mirror of the universe in one line", 16),
        ["round 134: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 134: a mirror of the universe in one line", 24), ["round 134: a mirror of", "the universe in one line"]),
    (("round 134: a mirror of the universe in one line", 32), ["round 134: a mirror of the", "universe in one line"]),
    (
        ("round 134: the queue drains before the storm", 4),
        ["round", "134:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 134: the queue drains before the storm", 8),
        ["round", "134: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 134: the queue drains before the storm", 12),
        ["round 134:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 134: the queue drains before the storm", 16), ["round 134: the", "queue drains", "before the storm"]),
    (("round 134: the queue drains before the storm", 24), ["round 134: the queue", "drains before the storm"]),
    (("round 134: the queue drains before the storm", 32), ["round 134: the queue drains", "before the storm"]),
    (
        ("kitten134 sitting134 agent134 angle134 universe134 memory134", 6),
        ["kitten134", "sitting134", "agent134", "angle134", "universe134", "memory134"],
    ),
    (
        ("kitten134 sitting134 agent134 angle134 universe134 memory134", 10),
        ["kitten134", "sitting134", "agent134", "angle134", "universe134", "memory134"],
    ),
    (
        ("kitten134 sitting134 agent134 angle134 universe134 memory134", 18),
        ["kitten134", "sitting134", "agent134 angle134", "universe134", "memory134"],
    ),
    (
        ("kitten134 sitting134 agent134 angle134 universe134 memory134", 28),
        ["kitten134 sitting134", "agent134 angle134", "universe134 memory134"],
    ),
    (
        ("sitting134 agent134 angle134 universe134 memory134 stream134", 6),
        ["sitting134", "agent134", "angle134", "universe134", "memory134", "stream134"],
    ),
    (
        ("sitting134 agent134 angle134 universe134 memory134 stream134", 10),
        ["sitting134", "agent134", "angle134", "universe134", "memory134", "stream134"],
    ),
    (
        ("sitting134 agent134 angle134 universe134 memory134 stream134", 18),
        ["sitting134", "agent134 angle134", "universe134", "memory134", "stream134"],
    ),
    (
        ("sitting134 agent134 angle134 universe134 memory134 stream134", 28),
        ["sitting134 agent134 angle134", "universe134 memory134", "stream134"],
    ),
    (
        ("agent134 angle134 universe134 memory134 stream134 context134", 6),
        ["agent134", "angle134", "universe134", "memory134", "stream134", "context134"],
    ),
    (
        ("agent134 angle134 universe134 memory134 stream134 context134", 10),
        ["agent134", "angle134", "universe134", "memory134", "stream134", "context134"],
    ),
    (
        ("agent134 angle134 universe134 memory134 stream134 context134", 18),
        ["agent134 angle134", "universe134", "memory134", "stream134", "context134"],
    ),
    (
        ("agent134 angle134 universe134 memory134 stream134 context134", 28),
        ["agent134 angle134", "universe134 memory134", "stream134 context134"],
    ),
    (
        ("angle134 universe134 memory134 stream134 context134 knowledge134", 6),
        ["angle134", "universe134", "memory134", "stream134", "context134", "knowledge134"],
    ),
    (
        ("angle134 universe134 memory134 stream134 context134 knowledge134", 10),
        ["angle134", "universe134", "memory134", "stream134", "context134", "knowledge134"],
    ),
    (
        ("angle134 universe134 memory134 stream134 context134 knowledge134", 18),
        ["angle134", "universe134", "memory134", "stream134", "context134", "knowledge134"],
    ),
    (
        ("angle134 universe134 memory134 stream134 context134 knowledge134", 28),
        ["angle134 universe134", "memory134 stream134", "context134 knowledge134"],
    ),
    (
        ("universe134 memory134 stream134 context134 knowledge134 vector134", 6),
        ["universe134", "memory134", "stream134", "context134", "knowledge134", "vector134"],
    ),
    (
        ("universe134 memory134 stream134 context134 knowledge134 vector134", 10),
        ["universe134", "memory134", "stream134", "context134", "knowledge134", "vector134"],
    ),
    (
        ("universe134 memory134 stream134 context134 knowledge134 vector134", 18),
        ["universe134", "memory134", "stream134", "context134", "knowledge134", "vector134"],
    ),
    (
        ("universe134 memory134 stream134 context134 knowledge134 vector134", 28),
        ["universe134 memory134", "stream134 context134", "knowledge134 vector134"],
    ),
    (
        ("memory134 stream134 context134 knowledge134 vector134 processor134", 6),
        ["memory134", "stream134", "context134", "knowledge134", "vector134", "processor134"],
    ),
    (
        ("memory134 stream134 context134 knowledge134 vector134 processor134", 10),
        ["memory134", "stream134", "context134", "knowledge134", "vector134", "processor134"],
    ),
    (
        ("memory134 stream134 context134 knowledge134 vector134 processor134", 18),
        ["memory134", "stream134", "context134", "knowledge134", "vector134", "processor134"],
    ),
    (
        ("memory134 stream134 context134 knowledge134 vector134 processor134", 28),
        ["memory134 stream134", "context134 knowledge134", "vector134 processor134"],
    ),
    (
        ("stream134 context134 knowledge134 vector134 processor134 reasoning134", 6),
        ["stream134", "context134", "knowledge134", "vector134", "processor134", "reasoning134"],
    ),
    (
        ("stream134 context134 knowledge134 vector134 processor134 reasoning134", 10),
        ["stream134", "context134", "knowledge134", "vector134", "processor134", "reasoning134"],
    ),
    (
        ("stream134 context134 knowledge134 vector134 processor134 reasoning134", 18),
        ["stream134", "context134", "knowledge134", "vector134", "processor134", "reasoning134"],
    ),
    (
        ("stream134 context134 knowledge134 vector134 processor134 reasoning134", 28),
        ["stream134 context134", "knowledge134 vector134", "processor134 reasoning134"],
    ),
    (
        ("context134 knowledge134 vector134 processor134 reasoning134 machine134", 6),
        ["context134", "knowledge134", "vector134", "processor134", "reasoning134", "machine134"],
    ),
    (
        ("context134 knowledge134 vector134 processor134 reasoning134 machine134", 10),
        ["context134", "knowledge134", "vector134", "processor134", "reasoning134", "machine134"],
    ),
    (
        ("context134 knowledge134 vector134 processor134 reasoning134 machine134", 18),
        ["context134", "knowledge134", "vector134", "processor134", "reasoning134", "machine134"],
    ),
    (
        ("context134 knowledge134 vector134 processor134 reasoning134 machine134", 28),
        ["context134 knowledge134", "vector134 processor134", "reasoning134 machine134"],
    ),
    (
        ("knowledge134 vector134 processor134 reasoning134 machine134 learning134", 6),
        ["knowledge134", "vector134", "processor134", "reasoning134", "machine134", "learning134"],
    ),
    (
        ("knowledge134 vector134 processor134 reasoning134 machine134 learning134", 10),
        ["knowledge134", "vector134", "processor134", "reasoning134", "machine134", "learning134"],
    ),
    (
        ("knowledge134 vector134 processor134 reasoning134 machine134 learning134", 18),
        ["knowledge134", "vector134", "processor134", "reasoning134", "machine134", "learning134"],
    ),
    (
        ("knowledge134 vector134 processor134 reasoning134 machine134 learning134", 28),
        ["knowledge134 vector134", "processor134 reasoning134", "machine134 learning134"],
    ),
    (
        ("vector134 processor134 reasoning134 machine134 learning134 model134", 6),
        ["vector134", "processor134", "reasoning134", "machine134", "learning134", "model134"],
    ),
    (
        ("vector134 processor134 reasoning134 machine134 learning134 model134", 10),
        ["vector134", "processor134", "reasoning134", "machine134", "learning134", "model134"],
    ),
    (
        ("vector134 processor134 reasoning134 machine134 learning134 model134", 18),
        ["vector134", "processor134", "reasoning134", "machine134", "learning134", "model134"],
    ),
    (
        ("vector134 processor134 reasoning134 machine134 learning134 model134", 28),
        ["vector134 processor134", "reasoning134 machine134", "learning134 model134"],
    ),
    (
        ("processor134 reasoning134 machine134 learning134 model134 token134", 6),
        ["processor134", "reasoning134", "machine134", "learning134", "model134", "token134"],
    ),
    (
        ("processor134 reasoning134 machine134 learning134 model134 token134", 10),
        ["processor134", "reasoning134", "machine134", "learning134", "model134", "token134"],
    ),
    (
        ("processor134 reasoning134 machine134 learning134 model134 token134", 18),
        ["processor134", "reasoning134", "machine134", "learning134", "model134 token134"],
    ),
    (
        ("processor134 reasoning134 machine134 learning134 model134 token134", 28),
        ["processor134 reasoning134", "machine134 learning134", "model134 token134"],
    ),
    (
        ("reasoning134 machine134 learning134 model134 token134 prompt134", 6),
        ["reasoning134", "machine134", "learning134", "model134", "token134", "prompt134"],
    ),
    (
        ("reasoning134 machine134 learning134 model134 token134 prompt134", 10),
        ["reasoning134", "machine134", "learning134", "model134", "token134", "prompt134"],
    ),
    (
        ("reasoning134 machine134 learning134 model134 token134 prompt134", 18),
        ["reasoning134", "machine134", "learning134", "model134 token134", "prompt134"],
    ),
    (
        ("reasoning134 machine134 learning134 model134 token134 prompt134", 28),
        ["reasoning134 machine134", "learning134 model134", "token134 prompt134"],
    ),
    (
        ("machine134 learning134 model134 token134 prompt134 session134", 6),
        ["machine134", "learning134", "model134", "token134", "prompt134", "session134"],
    ),
    (
        ("machine134 learning134 model134 token134 prompt134 session134", 10),
        ["machine134", "learning134", "model134", "token134", "prompt134", "session134"],
    ),
    (
        ("machine134 learning134 model134 token134 prompt134 session134", 18),
        ["machine134", "learning134", "model134 token134", "prompt134", "session134"],
    ),
    (
        ("machine134 learning134 model134 token134 prompt134 session134", 28),
        ["machine134 learning134", "model134 token134 prompt134", "session134"],
    ),
    (
        ("learning134 model134 token134 prompt134 session134 library134", 6),
        ["learning134", "model134", "token134", "prompt134", "session134", "library134"],
    ),
    (
        ("learning134 model134 token134 prompt134 session134 library134", 10),
        ["learning134", "model134", "token134", "prompt134", "session134", "library134"],
    ),
    (
        ("learning134 model134 token134 prompt134 session134 library134", 18),
        ["learning134", "model134 token134", "prompt134", "session134", "library134"],
    ),
    (
        ("learning134 model134 token134 prompt134 session134 library134", 28),
        ["learning134 model134", "token134 prompt134", "session134 library134"],
    ),
    (
        ("model134 token134 prompt134 session134 library134 service134", 6),
        ["model134", "token134", "prompt134", "session134", "library134", "service134"],
    ),
    (
        ("model134 token134 prompt134 session134 library134 service134", 10),
        ["model134", "token134", "prompt134", "session134", "library134", "service134"],
    ),
    (
        ("model134 token134 prompt134 session134 library134 service134", 18),
        ["model134 token134", "prompt134", "session134", "library134", "service134"],
    ),
    (
        ("model134 token134 prompt134 session134 library134 service134", 28),
        ["model134 token134 prompt134", "session134 library134", "service134"],
    ),
    (
        ("token134 prompt134 session134 library134 service134 gateway134", 6),
        ["token134", "prompt134", "session134", "library134", "service134", "gateway134"],
    ),
    (
        ("token134 prompt134 session134 library134 service134 gateway134", 10),
        ["token134", "prompt134", "session134", "library134", "service134", "gateway134"],
    ),
    (
        ("token134 prompt134 session134 library134 service134 gateway134", 18),
        ["token134 prompt134", "session134", "library134", "service134", "gateway134"],
    ),
    (
        ("token134 prompt134 session134 library134 service134 gateway134", 28),
        ["token134 prompt134", "session134 library134", "service134 gateway134"],
    ),
    (
        ("prompt134 session134 library134 service134 gateway134 storage134", 6),
        ["prompt134", "session134", "library134", "service134", "gateway134", "storage134"],
    ),
    (
        ("prompt134 session134 library134 service134 gateway134 storage134", 10),
        ["prompt134", "session134", "library134", "service134", "gateway134", "storage134"],
    ),
    (
        ("prompt134 session134 library134 service134 gateway134 storage134", 18),
        ["prompt134", "session134", "library134", "service134", "gateway134", "storage134"],
    ),
    (
        ("prompt134 session134 library134 service134 gateway134 storage134", 28),
        ["prompt134 session134", "library134 service134", "gateway134 storage134"],
    ),
    (
        ("session134 library134 service134 gateway134 storage134 network134", 6),
        ["session134", "library134", "service134", "gateway134", "storage134", "network134"],
    ),
    (
        ("session134 library134 service134 gateway134 storage134 network134", 10),
        ["session134", "library134", "service134", "gateway134", "storage134", "network134"],
    ),
    (
        ("session134 library134 service134 gateway134 storage134 network134", 18),
        ["session134", "library134", "service134", "gateway134", "storage134", "network134"],
    ),
    (
        ("session134 library134 service134 gateway134 storage134 network134", 28),
        ["session134 library134", "service134 gateway134", "storage134 network134"],
    ),
    (
        ("library134 service134 gateway134 storage134 network134 latency134", 6),
        ["library134", "service134", "gateway134", "storage134", "network134", "latency134"],
    ),
    (
        ("library134 service134 gateway134 storage134 network134 latency134", 10),
        ["library134", "service134", "gateway134", "storage134", "network134", "latency134"],
    ),
    (
        ("library134 service134 gateway134 storage134 network134 latency134", 18),
        ["library134", "service134", "gateway134", "storage134", "network134", "latency134"],
    ),
    (
        ("library134 service134 gateway134 storage134 network134 latency134", 28),
        ["library134 service134", "gateway134 storage134", "network134 latency134"],
    ),
    (
        ("service134 gateway134 storage134 network134 latency134 buffer134", 6),
        ["service134", "gateway134", "storage134", "network134", "latency134", "buffer134"],
    ),
    (
        ("service134 gateway134 storage134 network134 latency134 buffer134", 10),
        ["service134", "gateway134", "storage134", "network134", "latency134", "buffer134"],
    ),
    (
        ("service134 gateway134 storage134 network134 latency134 buffer134", 18),
        ["service134", "gateway134", "storage134", "network134", "latency134", "buffer134"],
    ),
    (
        ("service134 gateway134 storage134 network134 latency134 buffer134", 28),
        ["service134 gateway134", "storage134 network134", "latency134 buffer134"],
    ),
    (
        ("gateway134 storage134 network134 latency134 buffer134 queue134", 6),
        ["gateway134", "storage134", "network134", "latency134", "buffer134", "queue134"],
    ),
    (
        ("gateway134 storage134 network134 latency134 buffer134 queue134", 10),
        ["gateway134", "storage134", "network134", "latency134", "buffer134", "queue134"],
    ),
    (
        ("gateway134 storage134 network134 latency134 buffer134 queue134", 18),
        ["gateway134", "storage134", "network134", "latency134", "buffer134 queue134"],
    ),
    (
        ("gateway134 storage134 network134 latency134 buffer134 queue134", 28),
        ["gateway134 storage134", "network134 latency134", "buffer134 queue134"],
    ),
    (
        ("storage134 network134 latency134 buffer134 queue134 worker134", 6),
        ["storage134", "network134", "latency134", "buffer134", "queue134", "worker134"],
    ),
    (
        ("storage134 network134 latency134 buffer134 queue134 worker134", 10),
        ["storage134", "network134", "latency134", "buffer134", "queue134", "worker134"],
    ),
    (
        ("storage134 network134 latency134 buffer134 queue134 worker134", 18),
        ["storage134", "network134", "latency134", "buffer134 queue134", "worker134"],
    ),
    (
        ("storage134 network134 latency134 buffer134 queue134 worker134", 28),
        ["storage134 network134", "latency134 buffer134", "queue134 worker134"],
    ),
    (
        ("network134 latency134 buffer134 queue134 worker134 kernel134", 6),
        ["network134", "latency134", "buffer134", "queue134", "worker134", "kernel134"],
    ),
    (
        ("network134 latency134 buffer134 queue134 worker134 kernel134", 10),
        ["network134", "latency134", "buffer134", "queue134", "worker134", "kernel134"],
    ),
    (
        ("network134 latency134 buffer134 queue134 worker134 kernel134", 18),
        ["network134", "latency134", "buffer134 queue134", "worker134", "kernel134"],
    ),
    (
        ("network134 latency134 buffer134 queue134 worker134 kernel134", 28),
        ["network134 latency134", "buffer134 queue134 worker134", "kernel134"],
    ),
    (
        ("latency134 buffer134 queue134 worker134 kernel134 signal134", 6),
        ["latency134", "buffer134", "queue134", "worker134", "kernel134", "signal134"],
    ),
    (
        ("latency134 buffer134 queue134 worker134 kernel134 signal134", 10),
        ["latency134", "buffer134", "queue134", "worker134", "kernel134", "signal134"],
    ),
    (
        ("latency134 buffer134 queue134 worker134 kernel134 signal134", 18),
        ["latency134", "buffer134 queue134", "worker134", "kernel134", "signal134"],
    ),
    (
        ("latency134 buffer134 queue134 worker134 kernel134 signal134", 28),
        ["latency134 buffer134", "queue134 worker134 kernel134", "signal134"],
    ),
    (
        ("buffer134 queue134 worker134 kernel134 signal134 packet134", 6),
        ["buffer134", "queue134", "worker134", "kernel134", "signal134", "packet134"],
    ),
    (
        ("buffer134 queue134 worker134 kernel134 signal134 packet134", 10),
        ["buffer134", "queue134", "worker134", "kernel134", "signal134", "packet134"],
    ),
    (
        ("buffer134 queue134 worker134 kernel134 signal134 packet134", 18),
        ["buffer134 queue134", "worker134", "kernel134", "signal134", "packet134"],
    ),
    (
        ("buffer134 queue134 worker134 kernel134 signal134 packet134", 28),
        ["buffer134 queue134 worker134", "kernel134 signal134", "packet134"],
    ),
    (
        ("queue134 worker134 kernel134 signal134 packet134 router134", 6),
        ["queue134", "worker134", "kernel134", "signal134", "packet134", "router134"],
    ),
    (
        ("queue134 worker134 kernel134 signal134 packet134 router134", 10),
        ["queue134", "worker134", "kernel134", "signal134", "packet134", "router134"],
    ),
    (
        ("queue134 worker134 kernel134 signal134 packet134 router134", 18),
        ["queue134 worker134", "kernel134", "signal134", "packet134", "router134"],
    ),
    (
        ("queue134 worker134 kernel134 signal134 packet134 router134", 28),
        ["queue134 worker134 kernel134", "signal134 packet134", "router134"],
    ),
    (
        ("worker134 kernel134 signal134 packet134 router134 cluster134", 6),
        ["worker134", "kernel134", "signal134", "packet134", "router134", "cluster134"],
    ),
    (
        ("worker134 kernel134 signal134 packet134 router134 cluster134", 10),
        ["worker134", "kernel134", "signal134", "packet134", "router134", "cluster134"],
    ),
    (
        ("worker134 kernel134 signal134 packet134 router134 cluster134", 18),
        ["worker134", "kernel134", "signal134", "packet134", "router134", "cluster134"],
    ),
    (
        ("worker134 kernel134 signal134 packet134 router134 cluster134", 28),
        ["worker134 kernel134", "signal134 packet134", "router134 cluster134"],
    ),
    (
        ("kernel134 signal134 packet134 router134 cluster134 mirror134", 6),
        ["kernel134", "signal134", "packet134", "router134", "cluster134", "mirror134"],
    ),
    (
        ("kernel134 signal134 packet134 router134 cluster134 mirror134", 10),
        ["kernel134", "signal134", "packet134", "router134", "cluster134", "mirror134"],
    ),
    (
        ("kernel134 signal134 packet134 router134 cluster134 mirror134", 18),
        ["kernel134", "signal134", "packet134", "router134", "cluster134", "mirror134"],
    ),
    (
        ("kernel134 signal134 packet134 router134 cluster134 mirror134", 28),
        ["kernel134 signal134", "packet134 router134", "cluster134 mirror134"],
    ),
    (
        ("signal134 packet134 router134 cluster134 mirror134 filter134", 6),
        ["signal134", "packet134", "router134", "cluster134", "mirror134", "filter134"],
    ),
    (
        ("signal134 packet134 router134 cluster134 mirror134 filter134", 10),
        ["signal134", "packet134", "router134", "cluster134", "mirror134", "filter134"],
    ),
    (
        ("signal134 packet134 router134 cluster134 mirror134 filter134", 18),
        ["signal134", "packet134", "router134", "cluster134", "mirror134", "filter134"],
    ),
    (
        ("signal134 packet134 router134 cluster134 mirror134 filter134", 28),
        ["signal134 packet134", "router134 cluster134", "mirror134 filter134"],
    ),
    (
        ("packet134 router134 cluster134 mirror134 filter134 ranking134", 6),
        ["packet134", "router134", "cluster134", "mirror134", "filter134", "ranking134"],
    ),
    (
        ("packet134 router134 cluster134 mirror134 filter134 ranking134", 10),
        ["packet134", "router134", "cluster134", "mirror134", "filter134", "ranking134"],
    ),
    (
        ("packet134 router134 cluster134 mirror134 filter134 ranking134", 18),
        ["packet134", "router134", "cluster134", "mirror134", "filter134", "ranking134"],
    ),
    (
        ("packet134 router134 cluster134 mirror134 filter134 ranking134", 28),
        ["packet134 router134", "cluster134 mirror134", "filter134 ranking134"],
    ),
    (
        ("router134 cluster134 mirror134 filter134 ranking134 encoding134", 6),
        ["router134", "cluster134", "mirror134", "filter134", "ranking134", "encoding134"],
    ),
    (
        ("router134 cluster134 mirror134 filter134 ranking134 encoding134", 10),
        ["router134", "cluster134", "mirror134", "filter134", "ranking134", "encoding134"],
    ),
    (
        ("router134 cluster134 mirror134 filter134 ranking134 encoding134", 18),
        ["router134", "cluster134", "mirror134", "filter134", "ranking134", "encoding134"],
    ),
    (
        ("router134 cluster134 mirror134 filter134 ranking134 encoding134", 28),
        ["router134 cluster134", "mirror134 filter134", "ranking134 encoding134"],
    ),
    (
        ("cluster134 mirror134 filter134 ranking134 encoding134 mapping134", 6),
        ["cluster134", "mirror134", "filter134", "ranking134", "encoding134", "mapping134"],
    ),
    (
        ("cluster134 mirror134 filter134 ranking134 encoding134 mapping134", 10),
        ["cluster134", "mirror134", "filter134", "ranking134", "encoding134", "mapping134"],
    ),
    (
        ("cluster134 mirror134 filter134 ranking134 encoding134 mapping134", 18),
        ["cluster134", "mirror134", "filter134", "ranking134", "encoding134", "mapping134"],
    ),
    (
        ("cluster134 mirror134 filter134 ranking134 encoding134 mapping134", 28),
        ["cluster134 mirror134", "filter134 ranking134", "encoding134 mapping134"],
    ),
    (
        ("mirror134 filter134 ranking134 encoding134 mapping134 record134", 6),
        ["mirror134", "filter134", "ranking134", "encoding134", "mapping134", "record134"],
    ),
    (
        ("mirror134 filter134 ranking134 encoding134 mapping134 record134", 10),
        ["mirror134", "filter134", "ranking134", "encoding134", "mapping134", "record134"],
    ),
    (
        ("mirror134 filter134 ranking134 encoding134 mapping134 record134", 18),
        ["mirror134", "filter134", "ranking134", "encoding134", "mapping134", "record134"],
    ),
    (
        ("mirror134 filter134 ranking134 encoding134 mapping134 record134", 28),
        ["mirror134 filter134", "ranking134 encoding134", "mapping134 record134"],
    ),
    (
        ("filter134 ranking134 encoding134 mapping134 record134 candle134", 6),
        ["filter134", "ranking134", "encoding134", "mapping134", "record134", "candle134"],
    ),
    (
        ("filter134 ranking134 encoding134 mapping134 record134 candle134", 10),
        ["filter134", "ranking134", "encoding134", "mapping134", "record134", "candle134"],
    ),
    (
        ("filter134 ranking134 encoding134 mapping134 record134 candle134", 18),
        ["filter134", "ranking134", "encoding134", "mapping134", "record134", "candle134"],
    ),
    (
        ("filter134 ranking134 encoding134 mapping134 record134 candle134", 28),
        ["filter134 ranking134", "encoding134 mapping134", "record134 candle134"],
    ),
    (
        ("ranking134 encoding134 mapping134 record134 candle134 thread134", 6),
        ["ranking134", "encoding134", "mapping134", "record134", "candle134", "thread134"],
    ),
    (
        ("ranking134 encoding134 mapping134 record134 candle134 thread134", 10),
        ["ranking134", "encoding134", "mapping134", "record134", "candle134", "thread134"],
    ),
    (
        ("ranking134 encoding134 mapping134 record134 candle134 thread134", 18),
        ["ranking134", "encoding134", "mapping134", "record134", "candle134", "thread134"],
    ),
    (
        ("ranking134 encoding134 mapping134 record134 candle134 thread134", 28),
        ["ranking134 encoding134", "mapping134 record134", "candle134 thread134"],
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
