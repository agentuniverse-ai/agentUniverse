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
        ("round 189: the quick brown fox jumps over the lazy dog", 4),
        ["round", "189:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 189: the quick brown fox jumps over the lazy dog", 8),
        ["round", "189: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 189: the quick brown fox jumps over the lazy dog", 12),
        ["round 189:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 189: the quick brown fox jumps over the lazy dog", 16),
        ["round 189: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 189: the quick brown fox jumps over the lazy dog", 24),
        ["round 189: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 189: the quick brown fox jumps over the lazy dog", 32),
        ["round 189: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 189: agentuniverse is a framework for multi agents", 4),
        ["round", "189:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 189: agentuniverse is a framework for multi agents", 8),
        ["round", "189:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 189: agentuniverse is a framework for multi agents", 12),
        ["round 189:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 189: agentuniverse is a framework for multi agents", 16),
        ["round 189:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 189: agentuniverse is a framework for multi agents", 24),
        ["round 189: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 189: agentuniverse is a framework for multi agents", 32),
        ["round 189: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 189: knowledge stored as vectors enables retrieval", 4),
        ["round", "189:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 189: knowledge stored as vectors enables retrieval", 8),
        ["round", "189:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 189: knowledge stored as vectors enables retrieval", 12),
        ["round 189:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 189: knowledge stored as vectors enables retrieval", 16),
        ["round 189:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 189: knowledge stored as vectors enables retrieval", 24),
        ["round 189: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 189: knowledge stored as vectors enables retrieval", 32),
        ["round 189: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 189: the processor reads the record then stops", 4),
        ["round", "189:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 189: the processor reads the record then stops", 8),
        ["round", "189: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 189: the processor reads the record then stops", 12),
        ["round 189:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 189: the processor reads the record then stops", 16),
        ["round 189: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 189: the processor reads the record then stops", 24),
        ["round 189: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 189: the processor reads the record then stops", 32),
        ["round 189: the processor reads", "the record then stops"],
    ),
    (
        ("round 189: a worker pulls the next task from the queue", 4),
        ["round", "189:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 189: a worker pulls the next task from the queue", 8),
        ["round", "189: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 189: a worker pulls the next task from the queue", 12),
        ["round 189: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 189: a worker pulls the next task from the queue", 16),
        ["round 189: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 189: a worker pulls the next task from the queue", 24),
        ["round 189: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 189: a worker pulls the next task from the queue", 32),
        ["round 189: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 189: signals travel through the network layer", 4),
        ["round", "189:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 189: signals travel through the network layer", 8),
        ["round", "189:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 189: signals travel through the network layer", 12),
        ["round 189:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 189: signals travel through the network layer", 16),
        ["round 189:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 189: signals travel through the network layer", 24),
        ["round 189: signals", "travel through the", "network layer"],
    ),
    (
        ("round 189: signals travel through the network layer", 32),
        ["round 189: signals travel", "through the network layer"],
    ),
    (
        ("round 189: the gateway routes each request by policy", 4),
        ["round", "189:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 189: the gateway routes each request by policy", 8),
        ["round", "189: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 189: the gateway routes each request by policy", 12),
        ["round 189:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 189: the gateway routes each request by policy", 16),
        ["round 189: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 189: the gateway routes each request by policy", 24),
        ["round 189: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 189: the gateway routes each request by policy", 32),
        ["round 189: the gateway routes", "each request by policy"],
    ),
    (
        ("round 189: memory grows until the buffer is full", 4),
        ["round", "189:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 189: memory grows until the buffer is full", 8),
        ["round", "189:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 189: memory grows until the buffer is full", 12),
        ["round 189:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 189: memory grows until the buffer is full", 16),
        ["round 189:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 189: memory grows until the buffer is full", 24), ["round 189: memory grows", "until the buffer is full"]),
    (("round 189: memory grows until the buffer is full", 32), ["round 189: memory grows until", "the buffer is full"]),
    (
        ("round 189: the cluster mirrors every packet twice", 4),
        ["round", "189:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 189: the cluster mirrors every packet twice", 8),
        ["round", "189: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 189: the cluster mirrors every packet twice", 12),
        ["round 189:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 189: the cluster mirrors every packet twice", 16),
        ["round 189: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 189: the cluster mirrors every packet twice", 24),
        ["round 189: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 189: the cluster mirrors every packet twice", 32),
        ["round 189: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 189: ranking uses tokens learned from the corpus", 4),
        ["round", "189:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 189: ranking uses tokens learned from the corpus", 8),
        ["round", "189:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 189: ranking uses tokens learned from the corpus", 12),
        ["round 189:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 189: ranking uses tokens learned from the corpus", 16),
        ["round 189:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 189: ranking uses tokens learned from the corpus", 24),
        ["round 189: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 189: ranking uses tokens learned from the corpus", 32),
        ["round 189: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 189: a long session ends when the candle dies", 4),
        ["round", "189:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 189: a long session ends when the candle dies", 8),
        ["round", "189: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 189: a long session ends when the candle dies", 12),
        ["round 189: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 189: a long session ends when the candle dies", 16),
        ["round 189: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 189: a long session ends when the candle dies", 24),
        ["round 189: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 189: a long session ends when the candle dies", 32),
        ["round 189: a long session ends", "when the candle dies"],
    ),
    (
        ("round 189: encode the prompt then map the result", 4),
        ["round", "189:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 189: encode the prompt then map the result", 8),
        ["round", "189:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 189: encode the prompt then map the result", 12),
        ["round 189:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 189: encode the prompt then map the result", 16),
        ["round 189:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 189: encode the prompt then map the result", 24),
        ["round 189: encode the", "prompt then map the", "result"],
    ),
    (("round 189: encode the prompt then map the result", 32), ["round 189: encode the prompt", "then map the result"]),
    (
        ("round 189: the kernel wakes the worker at dawn", 4),
        ["round", "189:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 189: the kernel wakes the worker at dawn", 8),
        ["round", "189: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 189: the kernel wakes the worker at dawn", 12),
        ["round 189:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 189: the kernel wakes the worker at dawn", 16), ["round 189: the", "kernel wakes the", "worker at dawn"]),
    (("round 189: the kernel wakes the worker at dawn", 24), ["round 189: the kernel", "wakes the worker at dawn"]),
    (("round 189: the kernel wakes the worker at dawn", 32), ["round 189: the kernel wakes the", "worker at dawn"]),
    (
        ("round 189: service latency drops after the patch", 4),
        ["round", "189:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 189: service latency drops after the patch", 8),
        ["round", "189:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 189: service latency drops after the patch", 12),
        ["round 189:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 189: service latency drops after the patch", 16),
        ["round 189:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 189: service latency drops after the patch", 24),
        ["round 189: service", "latency drops after the", "patch"],
    ),
    (("round 189: service latency drops after the patch", 32), ["round 189: service latency drops", "after the patch"]),
    (
        ("round 189: the library caches every vector it sees", 4),
        ["round", "189:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 189: the library caches every vector it sees", 8),
        ["round", "189: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 189: the library caches every vector it sees", 12),
        ["round 189:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 189: the library caches every vector it sees", 16),
        ["round 189: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 189: the library caches every vector it sees", 24),
        ["round 189: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 189: the library caches every vector it sees", 32),
        ["round 189: the library caches", "every vector it sees"],
    ),
    (
        ("round 189: agents argue then the debate resolves", 4),
        ["round", "189:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 189: agents argue then the debate resolves", 8),
        ["round", "189:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 189: agents argue then the debate resolves", 12),
        ["round 189:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 189: agents argue then the debate resolves", 16),
        ["round 189:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 189: agents argue then the debate resolves", 24), ["round 189: agents argue", "then the debate resolves"]),
    (("round 189: agents argue then the debate resolves", 32), ["round 189: agents argue then the", "debate resolves"]),
    (
        ("round 189: the filter keeps only strong matches", 4),
        ["round", "189:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 189: the filter keeps only strong matches", 8),
        ["round", "189: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 189: the filter keeps only strong matches", 12),
        ["round 189:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 189: the filter keeps only strong matches", 16),
        ["round 189: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 189: the filter keeps only strong matches", 24),
        ["round 189: the filter", "keeps only strong", "matches"],
    ),
    (("round 189: the filter keeps only strong matches", 32), ["round 189: the filter keeps only", "strong matches"]),
    (
        ("round 189: the model answers with a short reply", 4),
        ["round", "189:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 189: the model answers with a short reply", 8),
        ["round", "189: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 189: the model answers with a short reply", 12),
        ["round 189:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 189: the model answers with a short reply", 16),
        ["round 189: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 189: the model answers with a short reply", 24),
        ["round 189: the model", "answers with a short", "reply"],
    ),
    (("round 189: the model answers with a short reply", 32), ["round 189: the model answers", "with a short reply"]),
    (
        ("round 189: the recorder stores the reasoning trace", 4),
        ["round", "189:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 189: the recorder stores the reasoning trace", 8),
        ["round", "189: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 189: the recorder stores the reasoning trace", 12),
        ["round 189:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 189: the recorder stores the reasoning trace", 16),
        ["round 189: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 189: the recorder stores the reasoning trace", 24),
        ["round 189: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 189: the recorder stores the reasoning trace", 32),
        ["round 189: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 189: the angel watches the processor run", 4),
        ["round", "189:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 189: the angel watches the processor run", 8),
        ["round", "189: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 189: the angel watches the processor run", 12),
        ["round 189:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 189: the angel watches the processor run", 16),
        ["round 189: the", "angel watches", "the processor", "run"],
    ),
    (("round 189: the angel watches the processor run", 24), ["round 189: the angel", "watches the processor", "run"]),
    (("round 189: the angel watches the processor run", 32), ["round 189: the angel watches the", "processor run"]),
    (
        ("round 189: angle of the vector decides the match", 4),
        ["round", "189:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 189: angle of the vector decides the match", 8),
        ["round", "189:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 189: angle of the vector decides the match", 12),
        ["round 189:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 189: angle of the vector decides the match", 16),
        ["round 189: angle", "of the vector", "decides the", "match"],
    ),
    (("round 189: angle of the vector decides the match", 24), ["round 189: angle of the", "vector decides the match"]),
    (("round 189: angle of the vector decides the match", 32), ["round 189: angle of the vector", "decides the match"]),
    (
        ("round 189: the candle burns twice as long at night", 4),
        ["round", "189:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 189: the candle burns twice as long at night", 8),
        ["round", "189: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 189: the candle burns twice as long at night", 12),
        ["round 189:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 189: the candle burns twice as long at night", 16),
        ["round 189: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 189: the candle burns twice as long at night", 24),
        ["round 189: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 189: the candle burns twice as long at night", 32),
        ["round 189: the candle burns", "twice as long at night"],
    ),
    (
        ("round 189: a mirror of the universe in one line", 4),
        ["round", "189:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 189: a mirror of the universe in one line", 8),
        ["round", "189: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 189: a mirror of the universe in one line", 12),
        ["round 189: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 189: a mirror of the universe in one line", 16),
        ["round 189: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 189: a mirror of the universe in one line", 24), ["round 189: a mirror of", "the universe in one line"]),
    (("round 189: a mirror of the universe in one line", 32), ["round 189: a mirror of the", "universe in one line"]),
    (
        ("round 189: the queue drains before the storm", 4),
        ["round", "189:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 189: the queue drains before the storm", 8),
        ["round", "189: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 189: the queue drains before the storm", 12),
        ["round 189:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 189: the queue drains before the storm", 16), ["round 189: the", "queue drains", "before the storm"]),
    (("round 189: the queue drains before the storm", 24), ["round 189: the queue", "drains before the storm"]),
    (("round 189: the queue drains before the storm", 32), ["round 189: the queue drains", "before the storm"]),
    (
        ("kitten189 sitting189 agent189 angle189 universe189 memory189", 6),
        ["kitten189", "sitting189", "agent189", "angle189", "universe189", "memory189"],
    ),
    (
        ("kitten189 sitting189 agent189 angle189 universe189 memory189", 10),
        ["kitten189", "sitting189", "agent189", "angle189", "universe189", "memory189"],
    ),
    (
        ("kitten189 sitting189 agent189 angle189 universe189 memory189", 18),
        ["kitten189", "sitting189", "agent189 angle189", "universe189", "memory189"],
    ),
    (
        ("kitten189 sitting189 agent189 angle189 universe189 memory189", 28),
        ["kitten189 sitting189", "agent189 angle189", "universe189 memory189"],
    ),
    (
        ("sitting189 agent189 angle189 universe189 memory189 stream189", 6),
        ["sitting189", "agent189", "angle189", "universe189", "memory189", "stream189"],
    ),
    (
        ("sitting189 agent189 angle189 universe189 memory189 stream189", 10),
        ["sitting189", "agent189", "angle189", "universe189", "memory189", "stream189"],
    ),
    (
        ("sitting189 agent189 angle189 universe189 memory189 stream189", 18),
        ["sitting189", "agent189 angle189", "universe189", "memory189", "stream189"],
    ),
    (
        ("sitting189 agent189 angle189 universe189 memory189 stream189", 28),
        ["sitting189 agent189 angle189", "universe189 memory189", "stream189"],
    ),
    (
        ("agent189 angle189 universe189 memory189 stream189 context189", 6),
        ["agent189", "angle189", "universe189", "memory189", "stream189", "context189"],
    ),
    (
        ("agent189 angle189 universe189 memory189 stream189 context189", 10),
        ["agent189", "angle189", "universe189", "memory189", "stream189", "context189"],
    ),
    (
        ("agent189 angle189 universe189 memory189 stream189 context189", 18),
        ["agent189 angle189", "universe189", "memory189", "stream189", "context189"],
    ),
    (
        ("agent189 angle189 universe189 memory189 stream189 context189", 28),
        ["agent189 angle189", "universe189 memory189", "stream189 context189"],
    ),
    (
        ("angle189 universe189 memory189 stream189 context189 knowledge189", 6),
        ["angle189", "universe189", "memory189", "stream189", "context189", "knowledge189"],
    ),
    (
        ("angle189 universe189 memory189 stream189 context189 knowledge189", 10),
        ["angle189", "universe189", "memory189", "stream189", "context189", "knowledge189"],
    ),
    (
        ("angle189 universe189 memory189 stream189 context189 knowledge189", 18),
        ["angle189", "universe189", "memory189", "stream189", "context189", "knowledge189"],
    ),
    (
        ("angle189 universe189 memory189 stream189 context189 knowledge189", 28),
        ["angle189 universe189", "memory189 stream189", "context189 knowledge189"],
    ),
    (
        ("universe189 memory189 stream189 context189 knowledge189 vector189", 6),
        ["universe189", "memory189", "stream189", "context189", "knowledge189", "vector189"],
    ),
    (
        ("universe189 memory189 stream189 context189 knowledge189 vector189", 10),
        ["universe189", "memory189", "stream189", "context189", "knowledge189", "vector189"],
    ),
    (
        ("universe189 memory189 stream189 context189 knowledge189 vector189", 18),
        ["universe189", "memory189", "stream189", "context189", "knowledge189", "vector189"],
    ),
    (
        ("universe189 memory189 stream189 context189 knowledge189 vector189", 28),
        ["universe189 memory189", "stream189 context189", "knowledge189 vector189"],
    ),
    (
        ("memory189 stream189 context189 knowledge189 vector189 processor189", 6),
        ["memory189", "stream189", "context189", "knowledge189", "vector189", "processor189"],
    ),
    (
        ("memory189 stream189 context189 knowledge189 vector189 processor189", 10),
        ["memory189", "stream189", "context189", "knowledge189", "vector189", "processor189"],
    ),
    (
        ("memory189 stream189 context189 knowledge189 vector189 processor189", 18),
        ["memory189", "stream189", "context189", "knowledge189", "vector189", "processor189"],
    ),
    (
        ("memory189 stream189 context189 knowledge189 vector189 processor189", 28),
        ["memory189 stream189", "context189 knowledge189", "vector189 processor189"],
    ),
    (
        ("stream189 context189 knowledge189 vector189 processor189 reasoning189", 6),
        ["stream189", "context189", "knowledge189", "vector189", "processor189", "reasoning189"],
    ),
    (
        ("stream189 context189 knowledge189 vector189 processor189 reasoning189", 10),
        ["stream189", "context189", "knowledge189", "vector189", "processor189", "reasoning189"],
    ),
    (
        ("stream189 context189 knowledge189 vector189 processor189 reasoning189", 18),
        ["stream189", "context189", "knowledge189", "vector189", "processor189", "reasoning189"],
    ),
    (
        ("stream189 context189 knowledge189 vector189 processor189 reasoning189", 28),
        ["stream189 context189", "knowledge189 vector189", "processor189 reasoning189"],
    ),
    (
        ("context189 knowledge189 vector189 processor189 reasoning189 machine189", 6),
        ["context189", "knowledge189", "vector189", "processor189", "reasoning189", "machine189"],
    ),
    (
        ("context189 knowledge189 vector189 processor189 reasoning189 machine189", 10),
        ["context189", "knowledge189", "vector189", "processor189", "reasoning189", "machine189"],
    ),
    (
        ("context189 knowledge189 vector189 processor189 reasoning189 machine189", 18),
        ["context189", "knowledge189", "vector189", "processor189", "reasoning189", "machine189"],
    ),
    (
        ("context189 knowledge189 vector189 processor189 reasoning189 machine189", 28),
        ["context189 knowledge189", "vector189 processor189", "reasoning189 machine189"],
    ),
    (
        ("knowledge189 vector189 processor189 reasoning189 machine189 learning189", 6),
        ["knowledge189", "vector189", "processor189", "reasoning189", "machine189", "learning189"],
    ),
    (
        ("knowledge189 vector189 processor189 reasoning189 machine189 learning189", 10),
        ["knowledge189", "vector189", "processor189", "reasoning189", "machine189", "learning189"],
    ),
    (
        ("knowledge189 vector189 processor189 reasoning189 machine189 learning189", 18),
        ["knowledge189", "vector189", "processor189", "reasoning189", "machine189", "learning189"],
    ),
    (
        ("knowledge189 vector189 processor189 reasoning189 machine189 learning189", 28),
        ["knowledge189 vector189", "processor189 reasoning189", "machine189 learning189"],
    ),
    (
        ("vector189 processor189 reasoning189 machine189 learning189 model189", 6),
        ["vector189", "processor189", "reasoning189", "machine189", "learning189", "model189"],
    ),
    (
        ("vector189 processor189 reasoning189 machine189 learning189 model189", 10),
        ["vector189", "processor189", "reasoning189", "machine189", "learning189", "model189"],
    ),
    (
        ("vector189 processor189 reasoning189 machine189 learning189 model189", 18),
        ["vector189", "processor189", "reasoning189", "machine189", "learning189", "model189"],
    ),
    (
        ("vector189 processor189 reasoning189 machine189 learning189 model189", 28),
        ["vector189 processor189", "reasoning189 machine189", "learning189 model189"],
    ),
    (
        ("processor189 reasoning189 machine189 learning189 model189 token189", 6),
        ["processor189", "reasoning189", "machine189", "learning189", "model189", "token189"],
    ),
    (
        ("processor189 reasoning189 machine189 learning189 model189 token189", 10),
        ["processor189", "reasoning189", "machine189", "learning189", "model189", "token189"],
    ),
    (
        ("processor189 reasoning189 machine189 learning189 model189 token189", 18),
        ["processor189", "reasoning189", "machine189", "learning189", "model189 token189"],
    ),
    (
        ("processor189 reasoning189 machine189 learning189 model189 token189", 28),
        ["processor189 reasoning189", "machine189 learning189", "model189 token189"],
    ),
    (
        ("reasoning189 machine189 learning189 model189 token189 prompt189", 6),
        ["reasoning189", "machine189", "learning189", "model189", "token189", "prompt189"],
    ),
    (
        ("reasoning189 machine189 learning189 model189 token189 prompt189", 10),
        ["reasoning189", "machine189", "learning189", "model189", "token189", "prompt189"],
    ),
    (
        ("reasoning189 machine189 learning189 model189 token189 prompt189", 18),
        ["reasoning189", "machine189", "learning189", "model189 token189", "prompt189"],
    ),
    (
        ("reasoning189 machine189 learning189 model189 token189 prompt189", 28),
        ["reasoning189 machine189", "learning189 model189", "token189 prompt189"],
    ),
    (
        ("machine189 learning189 model189 token189 prompt189 session189", 6),
        ["machine189", "learning189", "model189", "token189", "prompt189", "session189"],
    ),
    (
        ("machine189 learning189 model189 token189 prompt189 session189", 10),
        ["machine189", "learning189", "model189", "token189", "prompt189", "session189"],
    ),
    (
        ("machine189 learning189 model189 token189 prompt189 session189", 18),
        ["machine189", "learning189", "model189 token189", "prompt189", "session189"],
    ),
    (
        ("machine189 learning189 model189 token189 prompt189 session189", 28),
        ["machine189 learning189", "model189 token189 prompt189", "session189"],
    ),
    (
        ("learning189 model189 token189 prompt189 session189 library189", 6),
        ["learning189", "model189", "token189", "prompt189", "session189", "library189"],
    ),
    (
        ("learning189 model189 token189 prompt189 session189 library189", 10),
        ["learning189", "model189", "token189", "prompt189", "session189", "library189"],
    ),
    (
        ("learning189 model189 token189 prompt189 session189 library189", 18),
        ["learning189", "model189 token189", "prompt189", "session189", "library189"],
    ),
    (
        ("learning189 model189 token189 prompt189 session189 library189", 28),
        ["learning189 model189", "token189 prompt189", "session189 library189"],
    ),
    (
        ("model189 token189 prompt189 session189 library189 service189", 6),
        ["model189", "token189", "prompt189", "session189", "library189", "service189"],
    ),
    (
        ("model189 token189 prompt189 session189 library189 service189", 10),
        ["model189", "token189", "prompt189", "session189", "library189", "service189"],
    ),
    (
        ("model189 token189 prompt189 session189 library189 service189", 18),
        ["model189 token189", "prompt189", "session189", "library189", "service189"],
    ),
    (
        ("model189 token189 prompt189 session189 library189 service189", 28),
        ["model189 token189 prompt189", "session189 library189", "service189"],
    ),
    (
        ("token189 prompt189 session189 library189 service189 gateway189", 6),
        ["token189", "prompt189", "session189", "library189", "service189", "gateway189"],
    ),
    (
        ("token189 prompt189 session189 library189 service189 gateway189", 10),
        ["token189", "prompt189", "session189", "library189", "service189", "gateway189"],
    ),
    (
        ("token189 prompt189 session189 library189 service189 gateway189", 18),
        ["token189 prompt189", "session189", "library189", "service189", "gateway189"],
    ),
    (
        ("token189 prompt189 session189 library189 service189 gateway189", 28),
        ["token189 prompt189", "session189 library189", "service189 gateway189"],
    ),
    (
        ("prompt189 session189 library189 service189 gateway189 storage189", 6),
        ["prompt189", "session189", "library189", "service189", "gateway189", "storage189"],
    ),
    (
        ("prompt189 session189 library189 service189 gateway189 storage189", 10),
        ["prompt189", "session189", "library189", "service189", "gateway189", "storage189"],
    ),
    (
        ("prompt189 session189 library189 service189 gateway189 storage189", 18),
        ["prompt189", "session189", "library189", "service189", "gateway189", "storage189"],
    ),
    (
        ("prompt189 session189 library189 service189 gateway189 storage189", 28),
        ["prompt189 session189", "library189 service189", "gateway189 storage189"],
    ),
    (
        ("session189 library189 service189 gateway189 storage189 network189", 6),
        ["session189", "library189", "service189", "gateway189", "storage189", "network189"],
    ),
    (
        ("session189 library189 service189 gateway189 storage189 network189", 10),
        ["session189", "library189", "service189", "gateway189", "storage189", "network189"],
    ),
    (
        ("session189 library189 service189 gateway189 storage189 network189", 18),
        ["session189", "library189", "service189", "gateway189", "storage189", "network189"],
    ),
    (
        ("session189 library189 service189 gateway189 storage189 network189", 28),
        ["session189 library189", "service189 gateway189", "storage189 network189"],
    ),
    (
        ("library189 service189 gateway189 storage189 network189 latency189", 6),
        ["library189", "service189", "gateway189", "storage189", "network189", "latency189"],
    ),
    (
        ("library189 service189 gateway189 storage189 network189 latency189", 10),
        ["library189", "service189", "gateway189", "storage189", "network189", "latency189"],
    ),
    (
        ("library189 service189 gateway189 storage189 network189 latency189", 18),
        ["library189", "service189", "gateway189", "storage189", "network189", "latency189"],
    ),
    (
        ("library189 service189 gateway189 storage189 network189 latency189", 28),
        ["library189 service189", "gateway189 storage189", "network189 latency189"],
    ),
    (
        ("service189 gateway189 storage189 network189 latency189 buffer189", 6),
        ["service189", "gateway189", "storage189", "network189", "latency189", "buffer189"],
    ),
    (
        ("service189 gateway189 storage189 network189 latency189 buffer189", 10),
        ["service189", "gateway189", "storage189", "network189", "latency189", "buffer189"],
    ),
    (
        ("service189 gateway189 storage189 network189 latency189 buffer189", 18),
        ["service189", "gateway189", "storage189", "network189", "latency189", "buffer189"],
    ),
    (
        ("service189 gateway189 storage189 network189 latency189 buffer189", 28),
        ["service189 gateway189", "storage189 network189", "latency189 buffer189"],
    ),
    (
        ("gateway189 storage189 network189 latency189 buffer189 queue189", 6),
        ["gateway189", "storage189", "network189", "latency189", "buffer189", "queue189"],
    ),
    (
        ("gateway189 storage189 network189 latency189 buffer189 queue189", 10),
        ["gateway189", "storage189", "network189", "latency189", "buffer189", "queue189"],
    ),
    (
        ("gateway189 storage189 network189 latency189 buffer189 queue189", 18),
        ["gateway189", "storage189", "network189", "latency189", "buffer189 queue189"],
    ),
    (
        ("gateway189 storage189 network189 latency189 buffer189 queue189", 28),
        ["gateway189 storage189", "network189 latency189", "buffer189 queue189"],
    ),
    (
        ("storage189 network189 latency189 buffer189 queue189 worker189", 6),
        ["storage189", "network189", "latency189", "buffer189", "queue189", "worker189"],
    ),
    (
        ("storage189 network189 latency189 buffer189 queue189 worker189", 10),
        ["storage189", "network189", "latency189", "buffer189", "queue189", "worker189"],
    ),
    (
        ("storage189 network189 latency189 buffer189 queue189 worker189", 18),
        ["storage189", "network189", "latency189", "buffer189 queue189", "worker189"],
    ),
    (
        ("storage189 network189 latency189 buffer189 queue189 worker189", 28),
        ["storage189 network189", "latency189 buffer189", "queue189 worker189"],
    ),
    (
        ("network189 latency189 buffer189 queue189 worker189 kernel189", 6),
        ["network189", "latency189", "buffer189", "queue189", "worker189", "kernel189"],
    ),
    (
        ("network189 latency189 buffer189 queue189 worker189 kernel189", 10),
        ["network189", "latency189", "buffer189", "queue189", "worker189", "kernel189"],
    ),
    (
        ("network189 latency189 buffer189 queue189 worker189 kernel189", 18),
        ["network189", "latency189", "buffer189 queue189", "worker189", "kernel189"],
    ),
    (
        ("network189 latency189 buffer189 queue189 worker189 kernel189", 28),
        ["network189 latency189", "buffer189 queue189 worker189", "kernel189"],
    ),
    (
        ("latency189 buffer189 queue189 worker189 kernel189 signal189", 6),
        ["latency189", "buffer189", "queue189", "worker189", "kernel189", "signal189"],
    ),
    (
        ("latency189 buffer189 queue189 worker189 kernel189 signal189", 10),
        ["latency189", "buffer189", "queue189", "worker189", "kernel189", "signal189"],
    ),
    (
        ("latency189 buffer189 queue189 worker189 kernel189 signal189", 18),
        ["latency189", "buffer189 queue189", "worker189", "kernel189", "signal189"],
    ),
    (
        ("latency189 buffer189 queue189 worker189 kernel189 signal189", 28),
        ["latency189 buffer189", "queue189 worker189 kernel189", "signal189"],
    ),
    (
        ("buffer189 queue189 worker189 kernel189 signal189 packet189", 6),
        ["buffer189", "queue189", "worker189", "kernel189", "signal189", "packet189"],
    ),
    (
        ("buffer189 queue189 worker189 kernel189 signal189 packet189", 10),
        ["buffer189", "queue189", "worker189", "kernel189", "signal189", "packet189"],
    ),
    (
        ("buffer189 queue189 worker189 kernel189 signal189 packet189", 18),
        ["buffer189 queue189", "worker189", "kernel189", "signal189", "packet189"],
    ),
    (
        ("buffer189 queue189 worker189 kernel189 signal189 packet189", 28),
        ["buffer189 queue189 worker189", "kernel189 signal189", "packet189"],
    ),
    (
        ("queue189 worker189 kernel189 signal189 packet189 router189", 6),
        ["queue189", "worker189", "kernel189", "signal189", "packet189", "router189"],
    ),
    (
        ("queue189 worker189 kernel189 signal189 packet189 router189", 10),
        ["queue189", "worker189", "kernel189", "signal189", "packet189", "router189"],
    ),
    (
        ("queue189 worker189 kernel189 signal189 packet189 router189", 18),
        ["queue189 worker189", "kernel189", "signal189", "packet189", "router189"],
    ),
    (
        ("queue189 worker189 kernel189 signal189 packet189 router189", 28),
        ["queue189 worker189 kernel189", "signal189 packet189", "router189"],
    ),
    (
        ("worker189 kernel189 signal189 packet189 router189 cluster189", 6),
        ["worker189", "kernel189", "signal189", "packet189", "router189", "cluster189"],
    ),
    (
        ("worker189 kernel189 signal189 packet189 router189 cluster189", 10),
        ["worker189", "kernel189", "signal189", "packet189", "router189", "cluster189"],
    ),
    (
        ("worker189 kernel189 signal189 packet189 router189 cluster189", 18),
        ["worker189", "kernel189", "signal189", "packet189", "router189", "cluster189"],
    ),
    (
        ("worker189 kernel189 signal189 packet189 router189 cluster189", 28),
        ["worker189 kernel189", "signal189 packet189", "router189 cluster189"],
    ),
    (
        ("kernel189 signal189 packet189 router189 cluster189 mirror189", 6),
        ["kernel189", "signal189", "packet189", "router189", "cluster189", "mirror189"],
    ),
    (
        ("kernel189 signal189 packet189 router189 cluster189 mirror189", 10),
        ["kernel189", "signal189", "packet189", "router189", "cluster189", "mirror189"],
    ),
    (
        ("kernel189 signal189 packet189 router189 cluster189 mirror189", 18),
        ["kernel189", "signal189", "packet189", "router189", "cluster189", "mirror189"],
    ),
    (
        ("kernel189 signal189 packet189 router189 cluster189 mirror189", 28),
        ["kernel189 signal189", "packet189 router189", "cluster189 mirror189"],
    ),
    (
        ("signal189 packet189 router189 cluster189 mirror189 filter189", 6),
        ["signal189", "packet189", "router189", "cluster189", "mirror189", "filter189"],
    ),
    (
        ("signal189 packet189 router189 cluster189 mirror189 filter189", 10),
        ["signal189", "packet189", "router189", "cluster189", "mirror189", "filter189"],
    ),
    (
        ("signal189 packet189 router189 cluster189 mirror189 filter189", 18),
        ["signal189", "packet189", "router189", "cluster189", "mirror189", "filter189"],
    ),
    (
        ("signal189 packet189 router189 cluster189 mirror189 filter189", 28),
        ["signal189 packet189", "router189 cluster189", "mirror189 filter189"],
    ),
    (
        ("packet189 router189 cluster189 mirror189 filter189 ranking189", 6),
        ["packet189", "router189", "cluster189", "mirror189", "filter189", "ranking189"],
    ),
    (
        ("packet189 router189 cluster189 mirror189 filter189 ranking189", 10),
        ["packet189", "router189", "cluster189", "mirror189", "filter189", "ranking189"],
    ),
    (
        ("packet189 router189 cluster189 mirror189 filter189 ranking189", 18),
        ["packet189", "router189", "cluster189", "mirror189", "filter189", "ranking189"],
    ),
    (
        ("packet189 router189 cluster189 mirror189 filter189 ranking189", 28),
        ["packet189 router189", "cluster189 mirror189", "filter189 ranking189"],
    ),
    (
        ("router189 cluster189 mirror189 filter189 ranking189 encoding189", 6),
        ["router189", "cluster189", "mirror189", "filter189", "ranking189", "encoding189"],
    ),
    (
        ("router189 cluster189 mirror189 filter189 ranking189 encoding189", 10),
        ["router189", "cluster189", "mirror189", "filter189", "ranking189", "encoding189"],
    ),
    (
        ("router189 cluster189 mirror189 filter189 ranking189 encoding189", 18),
        ["router189", "cluster189", "mirror189", "filter189", "ranking189", "encoding189"],
    ),
    (
        ("router189 cluster189 mirror189 filter189 ranking189 encoding189", 28),
        ["router189 cluster189", "mirror189 filter189", "ranking189 encoding189"],
    ),
    (
        ("cluster189 mirror189 filter189 ranking189 encoding189 mapping189", 6),
        ["cluster189", "mirror189", "filter189", "ranking189", "encoding189", "mapping189"],
    ),
    (
        ("cluster189 mirror189 filter189 ranking189 encoding189 mapping189", 10),
        ["cluster189", "mirror189", "filter189", "ranking189", "encoding189", "mapping189"],
    ),
    (
        ("cluster189 mirror189 filter189 ranking189 encoding189 mapping189", 18),
        ["cluster189", "mirror189", "filter189", "ranking189", "encoding189", "mapping189"],
    ),
    (
        ("cluster189 mirror189 filter189 ranking189 encoding189 mapping189", 28),
        ["cluster189 mirror189", "filter189 ranking189", "encoding189 mapping189"],
    ),
    (
        ("mirror189 filter189 ranking189 encoding189 mapping189 record189", 6),
        ["mirror189", "filter189", "ranking189", "encoding189", "mapping189", "record189"],
    ),
    (
        ("mirror189 filter189 ranking189 encoding189 mapping189 record189", 10),
        ["mirror189", "filter189", "ranking189", "encoding189", "mapping189", "record189"],
    ),
    (
        ("mirror189 filter189 ranking189 encoding189 mapping189 record189", 18),
        ["mirror189", "filter189", "ranking189", "encoding189", "mapping189", "record189"],
    ),
    (
        ("mirror189 filter189 ranking189 encoding189 mapping189 record189", 28),
        ["mirror189 filter189", "ranking189 encoding189", "mapping189 record189"],
    ),
    (
        ("filter189 ranking189 encoding189 mapping189 record189 candle189", 6),
        ["filter189", "ranking189", "encoding189", "mapping189", "record189", "candle189"],
    ),
    (
        ("filter189 ranking189 encoding189 mapping189 record189 candle189", 10),
        ["filter189", "ranking189", "encoding189", "mapping189", "record189", "candle189"],
    ),
    (
        ("filter189 ranking189 encoding189 mapping189 record189 candle189", 18),
        ["filter189", "ranking189", "encoding189", "mapping189", "record189", "candle189"],
    ),
    (
        ("filter189 ranking189 encoding189 mapping189 record189 candle189", 28),
        ["filter189 ranking189", "encoding189 mapping189", "record189 candle189"],
    ),
    (
        ("ranking189 encoding189 mapping189 record189 candle189 thread189", 6),
        ["ranking189", "encoding189", "mapping189", "record189", "candle189", "thread189"],
    ),
    (
        ("ranking189 encoding189 mapping189 record189 candle189 thread189", 10),
        ["ranking189", "encoding189", "mapping189", "record189", "candle189", "thread189"],
    ),
    (
        ("ranking189 encoding189 mapping189 record189 candle189 thread189", 18),
        ["ranking189", "encoding189", "mapping189", "record189", "candle189", "thread189"],
    ),
    (
        ("ranking189 encoding189 mapping189 record189 candle189 thread189", 28),
        ["ranking189 encoding189", "mapping189 record189", "candle189 thread189"],
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
