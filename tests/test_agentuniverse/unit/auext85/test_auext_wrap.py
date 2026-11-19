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
        ("round 85: the quick brown fox jumps over the lazy dog", 4),
        ["round", "85:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 85: the quick brown fox jumps over the lazy dog", 8),
        ["round", "85: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 85: the quick brown fox jumps over the lazy dog", 12),
        ["round 85:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 85: the quick brown fox jumps over the lazy dog", 16),
        ["round 85: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 85: the quick brown fox jumps over the lazy dog", 24),
        ["round 85: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 85: the quick brown fox jumps over the lazy dog", 32),
        ["round 85: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 85: agentuniverse is a framework for multi agents", 4),
        ["round", "85:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 85: agentuniverse is a framework for multi agents", 8),
        ["round", "85:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 85: agentuniverse is a framework for multi agents", 12),
        ["round 85:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 85: agentuniverse is a framework for multi agents", 16),
        ["round 85:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 85: agentuniverse is a framework for multi agents", 24),
        ["round 85: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 85: agentuniverse is a framework for multi agents", 32),
        ["round 85: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 85: knowledge stored as vectors enables retrieval", 4),
        ["round", "85:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 85: knowledge stored as vectors enables retrieval", 8),
        ["round", "85:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 85: knowledge stored as vectors enables retrieval", 12),
        ["round 85:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 85: knowledge stored as vectors enables retrieval", 16),
        ["round 85:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 85: knowledge stored as vectors enables retrieval", 24),
        ["round 85: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 85: knowledge stored as vectors enables retrieval", 32),
        ["round 85: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 85: the processor reads the record then stops", 4),
        ["round", "85:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 85: the processor reads the record then stops", 8),
        ["round", "85: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 85: the processor reads the record then stops", 12),
        ["round 85:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 85: the processor reads the record then stops", 16),
        ["round 85: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 85: the processor reads the record then stops", 24),
        ["round 85: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 85: the processor reads the record then stops", 32),
        ["round 85: the processor reads", "the record then stops"],
    ),
    (
        ("round 85: a worker pulls the next task from the queue", 4),
        ["round", "85:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 85: a worker pulls the next task from the queue", 8),
        ["round", "85: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 85: a worker pulls the next task from the queue", 12),
        ["round 85: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 85: a worker pulls the next task from the queue", 16),
        ["round 85: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 85: a worker pulls the next task from the queue", 24),
        ["round 85: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 85: a worker pulls the next task from the queue", 32),
        ["round 85: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 85: signals travel through the network layer", 4),
        ["round", "85:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 85: signals travel through the network layer", 8),
        ["round", "85:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 85: signals travel through the network layer", 12),
        ["round 85:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 85: signals travel through the network layer", 16),
        ["round 85:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 85: signals travel through the network layer", 24),
        ["round 85: signals travel", "through the network", "layer"],
    ),
    (
        ("round 85: signals travel through the network layer", 32),
        ["round 85: signals travel through", "the network layer"],
    ),
    (
        ("round 85: the gateway routes each request by policy", 4),
        ["round", "85:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 85: the gateway routes each request by policy", 8),
        ["round", "85: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 85: the gateway routes each request by policy", 12),
        ["round 85:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 85: the gateway routes each request by policy", 16),
        ["round 85: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 85: the gateway routes each request by policy", 24),
        ["round 85: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 85: the gateway routes each request by policy", 32),
        ["round 85: the gateway routes", "each request by policy"],
    ),
    (
        ("round 85: memory grows until the buffer is full", 4),
        ["round", "85:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 85: memory grows until the buffer is full", 8),
        ["round", "85:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 85: memory grows until the buffer is full", 12),
        ["round 85:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 85: memory grows until the buffer is full", 16),
        ["round 85: memory", "grows until the", "buffer is full"],
    ),
    (("round 85: memory grows until the buffer is full", 24), ["round 85: memory grows", "until the buffer is full"]),
    (("round 85: memory grows until the buffer is full", 32), ["round 85: memory grows until the", "buffer is full"]),
    (
        ("round 85: the cluster mirrors every packet twice", 4),
        ["round", "85:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 85: the cluster mirrors every packet twice", 8),
        ["round", "85: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 85: the cluster mirrors every packet twice", 12),
        ["round 85:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 85: the cluster mirrors every packet twice", 16),
        ["round 85: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 85: the cluster mirrors every packet twice", 24),
        ["round 85: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 85: the cluster mirrors every packet twice", 32), ["round 85: the cluster mirrors", "every packet twice"]),
    (
        ("round 85: ranking uses tokens learned from the corpus", 4),
        ["round", "85:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 85: ranking uses tokens learned from the corpus", 8),
        ["round", "85:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 85: ranking uses tokens learned from the corpus", 12),
        ["round 85:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 85: ranking uses tokens learned from the corpus", 16),
        ["round 85:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 85: ranking uses tokens learned from the corpus", 24),
        ["round 85: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 85: ranking uses tokens learned from the corpus", 32),
        ["round 85: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 85: a long session ends when the candle dies", 4),
        ["round", "85:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 85: a long session ends when the candle dies", 8),
        ["round", "85: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 85: a long session ends when the candle dies", 12),
        ["round 85: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 85: a long session ends when the candle dies", 16),
        ["round 85: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 85: a long session ends when the candle dies", 24),
        ["round 85: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 85: a long session ends when the candle dies", 32),
        ["round 85: a long session ends", "when the candle dies"],
    ),
    (
        ("round 85: encode the prompt then map the result", 4),
        ["round", "85:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 85: encode the prompt then map the result", 8),
        ["round", "85:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 85: encode the prompt then map the result", 12),
        ["round 85:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 85: encode the prompt then map the result", 16),
        ["round 85: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 85: encode the prompt then map the result", 24),
        ["round 85: encode the", "prompt then map the", "result"],
    ),
    (("round 85: encode the prompt then map the result", 32), ["round 85: encode the prompt then", "map the result"]),
    (
        ("round 85: the kernel wakes the worker at dawn", 4),
        ["round", "85:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 85: the kernel wakes the worker at dawn", 8),
        ["round", "85: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 85: the kernel wakes the worker at dawn", 12),
        ["round 85:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 85: the kernel wakes the worker at dawn", 16), ["round 85: the", "kernel wakes the", "worker at dawn"]),
    (("round 85: the kernel wakes the worker at dawn", 24), ["round 85: the kernel", "wakes the worker at dawn"]),
    (("round 85: the kernel wakes the worker at dawn", 32), ["round 85: the kernel wakes the", "worker at dawn"]),
    (
        ("round 85: service latency drops after the patch", 4),
        ["round", "85:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 85: service latency drops after the patch", 8),
        ["round", "85:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 85: service latency drops after the patch", 12),
        ["round 85:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 85: service latency drops after the patch", 16),
        ["round 85:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 85: service latency drops after the patch", 24),
        ["round 85: service", "latency drops after the", "patch"],
    ),
    (("round 85: service latency drops after the patch", 32), ["round 85: service latency drops", "after the patch"]),
    (
        ("round 85: the library caches every vector it sees", 4),
        ["round", "85:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 85: the library caches every vector it sees", 8),
        ["round", "85: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 85: the library caches every vector it sees", 12),
        ["round 85:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 85: the library caches every vector it sees", 16),
        ["round 85: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 85: the library caches every vector it sees", 24),
        ["round 85: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 85: the library caches every vector it sees", 32),
        ["round 85: the library caches", "every vector it sees"],
    ),
    (
        ("round 85: agents argue then the debate resolves", 4),
        ["round", "85:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 85: agents argue then the debate resolves", 8),
        ["round", "85:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 85: agents argue then the debate resolves", 12),
        ["round 85:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 85: agents argue then the debate resolves", 16),
        ["round 85: agents", "argue then the", "debate resolves"],
    ),
    (("round 85: agents argue then the debate resolves", 24), ["round 85: agents argue", "then the debate resolves"]),
    (("round 85: agents argue then the debate resolves", 32), ["round 85: agents argue then the", "debate resolves"]),
    (
        ("round 85: the filter keeps only strong matches", 4),
        ["round", "85:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 85: the filter keeps only strong matches", 8),
        ["round", "85: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 85: the filter keeps only strong matches", 12),
        ["round 85:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 85: the filter keeps only strong matches", 16),
        ["round 85: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 85: the filter keeps only strong matches", 24), ["round 85: the filter", "keeps only strong", "matches"]),
    (("round 85: the filter keeps only strong matches", 32), ["round 85: the filter keeps only", "strong matches"]),
    (
        ("round 85: the model answers with a short reply", 4),
        ["round", "85:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 85: the model answers with a short reply", 8),
        ["round", "85: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 85: the model answers with a short reply", 12),
        ["round 85:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 85: the model answers with a short reply", 16),
        ["round 85: the", "model answers", "with a short", "reply"],
    ),
    (("round 85: the model answers with a short reply", 24), ["round 85: the model", "answers with a short", "reply"]),
    (("round 85: the model answers with a short reply", 32), ["round 85: the model answers with", "a short reply"]),
    (
        ("round 85: the recorder stores the reasoning trace", 4),
        ["round", "85:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 85: the recorder stores the reasoning trace", 8),
        ["round", "85: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 85: the recorder stores the reasoning trace", 12),
        ["round 85:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 85: the recorder stores the reasoning trace", 16),
        ["round 85: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 85: the recorder stores the reasoning trace", 24),
        ["round 85: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 85: the recorder stores the reasoning trace", 32),
        ["round 85: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 85: the angel watches the processor run", 4),
        ["round", "85:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 85: the angel watches the processor run", 8),
        ["round", "85: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 85: the angel watches the processor run", 12),
        ["round 85:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 85: the angel watches the processor run", 16), ["round 85: the", "angel watches", "the processor", "run"]),
    (("round 85: the angel watches the processor run", 24), ["round 85: the angel", "watches the processor", "run"]),
    (("round 85: the angel watches the processor run", 32), ["round 85: the angel watches the", "processor run"]),
    (
        ("round 85: angle of the vector decides the match", 4),
        ["round", "85:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 85: angle of the vector decides the match", 8),
        ["round", "85:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 85: angle of the vector decides the match", 12),
        ["round 85:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 85: angle of the vector decides the match", 16),
        ["round 85: angle", "of the vector", "decides the", "match"],
    ),
    (("round 85: angle of the vector decides the match", 24), ["round 85: angle of the", "vector decides the match"]),
    (("round 85: angle of the vector decides the match", 32), ["round 85: angle of the vector", "decides the match"]),
    (
        ("round 85: the candle burns twice as long at night", 4),
        ["round", "85:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 85: the candle burns twice as long at night", 8),
        ["round", "85: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 85: the candle burns twice as long at night", 12),
        ["round 85:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 85: the candle burns twice as long at night", 16),
        ["round 85: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 85: the candle burns twice as long at night", 24),
        ["round 85: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 85: the candle burns twice as long at night", 32),
        ["round 85: the candle burns twice", "as long at night"],
    ),
    (
        ("round 85: a mirror of the universe in one line", 4),
        ["round", "85:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 85: a mirror of the universe in one line", 8),
        ["round", "85: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 85: a mirror of the universe in one line", 12),
        ["round 85: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 85: a mirror of the universe in one line", 16),
        ["round 85: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 85: a mirror of the universe in one line", 24), ["round 85: a mirror of", "the universe in one line"]),
    (("round 85: a mirror of the universe in one line", 32), ["round 85: a mirror of the", "universe in one line"]),
    (
        ("round 85: the queue drains before the storm", 4),
        ["round", "85:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 85: the queue drains before the storm", 8),
        ["round", "85: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 85: the queue drains before the storm", 12), ["round 85:", "the queue", "drains", "before the", "storm"]),
    (("round 85: the queue drains before the storm", 16), ["round 85: the", "queue drains", "before the storm"]),
    (("round 85: the queue drains before the storm", 24), ["round 85: the queue", "drains before the storm"]),
    (("round 85: the queue drains before the storm", 32), ["round 85: the queue drains", "before the storm"]),
    (
        ("kitten85 sitting85 agent85 angle85 universe85 memory85", 6),
        ["kitten85", "sitting85", "agent85", "angle85", "universe85", "memory85"],
    ),
    (
        ("kitten85 sitting85 agent85 angle85 universe85 memory85", 10),
        ["kitten85", "sitting85", "agent85", "angle85", "universe85", "memory85"],
    ),
    (
        ("kitten85 sitting85 agent85 angle85 universe85 memory85", 18),
        ["kitten85 sitting85", "agent85 angle85", "universe85", "memory85"],
    ),
    (
        ("kitten85 sitting85 agent85 angle85 universe85 memory85", 28),
        ["kitten85 sitting85 agent85", "angle85 universe85 memory85"],
    ),
    (
        ("sitting85 agent85 angle85 universe85 memory85 stream85", 6),
        ["sitting85", "agent85", "angle85", "universe85", "memory85", "stream85"],
    ),
    (
        ("sitting85 agent85 angle85 universe85 memory85 stream85", 10),
        ["sitting85", "agent85", "angle85", "universe85", "memory85", "stream85"],
    ),
    (
        ("sitting85 agent85 angle85 universe85 memory85 stream85", 18),
        ["sitting85 agent85", "angle85 universe85", "memory85 stream85"],
    ),
    (
        ("sitting85 agent85 angle85 universe85 memory85 stream85", 28),
        ["sitting85 agent85 angle85", "universe85 memory85 stream85"],
    ),
    (
        ("agent85 angle85 universe85 memory85 stream85 context85", 6),
        ["agent85", "angle85", "universe85", "memory85", "stream85", "context85"],
    ),
    (
        ("agent85 angle85 universe85 memory85 stream85 context85", 10),
        ["agent85", "angle85", "universe85", "memory85", "stream85", "context85"],
    ),
    (
        ("agent85 angle85 universe85 memory85 stream85 context85", 18),
        ["agent85 angle85", "universe85", "memory85 stream85", "context85"],
    ),
    (
        ("agent85 angle85 universe85 memory85 stream85 context85", 28),
        ["agent85 angle85 universe85", "memory85 stream85 context85"],
    ),
    (
        ("angle85 universe85 memory85 stream85 context85 knowledge85", 6),
        ["angle85", "universe85", "memory85", "stream85", "context85", "knowledge85"],
    ),
    (
        ("angle85 universe85 memory85 stream85 context85 knowledge85", 10),
        ["angle85", "universe85", "memory85", "stream85", "context85", "knowledge85"],
    ),
    (
        ("angle85 universe85 memory85 stream85 context85 knowledge85", 18),
        ["angle85 universe85", "memory85 stream85", "context85", "knowledge85"],
    ),
    (
        ("angle85 universe85 memory85 stream85 context85 knowledge85", 28),
        ["angle85 universe85 memory85", "stream85 context85", "knowledge85"],
    ),
    (
        ("universe85 memory85 stream85 context85 knowledge85 vector85", 6),
        ["universe85", "memory85", "stream85", "context85", "knowledge85", "vector85"],
    ),
    (
        ("universe85 memory85 stream85 context85 knowledge85 vector85", 10),
        ["universe85", "memory85", "stream85", "context85", "knowledge85", "vector85"],
    ),
    (
        ("universe85 memory85 stream85 context85 knowledge85 vector85", 18),
        ["universe85", "memory85 stream85", "context85", "knowledge85", "vector85"],
    ),
    (
        ("universe85 memory85 stream85 context85 knowledge85 vector85", 28),
        ["universe85 memory85 stream85", "context85 knowledge85", "vector85"],
    ),
    (
        ("memory85 stream85 context85 knowledge85 vector85 processor85", 6),
        ["memory85", "stream85", "context85", "knowledge85", "vector85", "processor85"],
    ),
    (
        ("memory85 stream85 context85 knowledge85 vector85 processor85", 10),
        ["memory85", "stream85", "context85", "knowledge85", "vector85", "processor85"],
    ),
    (
        ("memory85 stream85 context85 knowledge85 vector85 processor85", 18),
        ["memory85 stream85", "context85", "knowledge85", "vector85", "processor85"],
    ),
    (
        ("memory85 stream85 context85 knowledge85 vector85 processor85", 28),
        ["memory85 stream85 context85", "knowledge85 vector85", "processor85"],
    ),
    (
        ("stream85 context85 knowledge85 vector85 processor85 reasoning85", 6),
        ["stream85", "context85", "knowledge85", "vector85", "processor85", "reasoning85"],
    ),
    (
        ("stream85 context85 knowledge85 vector85 processor85 reasoning85", 10),
        ["stream85", "context85", "knowledge85", "vector85", "processor85", "reasoning85"],
    ),
    (
        ("stream85 context85 knowledge85 vector85 processor85 reasoning85", 18),
        ["stream85 context85", "knowledge85", "vector85", "processor85", "reasoning85"],
    ),
    (
        ("stream85 context85 knowledge85 vector85 processor85 reasoning85", 28),
        ["stream85 context85", "knowledge85 vector85", "processor85 reasoning85"],
    ),
    (
        ("context85 knowledge85 vector85 processor85 reasoning85 machine85", 6),
        ["context85", "knowledge85", "vector85", "processor85", "reasoning85", "machine85"],
    ),
    (
        ("context85 knowledge85 vector85 processor85 reasoning85 machine85", 10),
        ["context85", "knowledge85", "vector85", "processor85", "reasoning85", "machine85"],
    ),
    (
        ("context85 knowledge85 vector85 processor85 reasoning85 machine85", 18),
        ["context85", "knowledge85", "vector85", "processor85", "reasoning85", "machine85"],
    ),
    (
        ("context85 knowledge85 vector85 processor85 reasoning85 machine85", 28),
        ["context85 knowledge85", "vector85 processor85", "reasoning85 machine85"],
    ),
    (
        ("knowledge85 vector85 processor85 reasoning85 machine85 learning85", 6),
        ["knowledge85", "vector85", "processor85", "reasoning85", "machine85", "learning85"],
    ),
    (
        ("knowledge85 vector85 processor85 reasoning85 machine85 learning85", 10),
        ["knowledge85", "vector85", "processor85", "reasoning85", "machine85", "learning85"],
    ),
    (
        ("knowledge85 vector85 processor85 reasoning85 machine85 learning85", 18),
        ["knowledge85", "vector85", "processor85", "reasoning85", "machine85", "learning85"],
    ),
    (
        ("knowledge85 vector85 processor85 reasoning85 machine85 learning85", 28),
        ["knowledge85 vector85", "processor85 reasoning85", "machine85 learning85"],
    ),
    (
        ("vector85 processor85 reasoning85 machine85 learning85 model85", 6),
        ["vector85", "processor85", "reasoning85", "machine85", "learning85", "model85"],
    ),
    (
        ("vector85 processor85 reasoning85 machine85 learning85 model85", 10),
        ["vector85", "processor85", "reasoning85", "machine85", "learning85", "model85"],
    ),
    (
        ("vector85 processor85 reasoning85 machine85 learning85 model85", 18),
        ["vector85", "processor85", "reasoning85", "machine85", "learning85 model85"],
    ),
    (
        ("vector85 processor85 reasoning85 machine85 learning85 model85", 28),
        ["vector85 processor85", "reasoning85 machine85", "learning85 model85"],
    ),
    (
        ("processor85 reasoning85 machine85 learning85 model85 token85", 6),
        ["processor85", "reasoning85", "machine85", "learning85", "model85", "token85"],
    ),
    (
        ("processor85 reasoning85 machine85 learning85 model85 token85", 10),
        ["processor85", "reasoning85", "machine85", "learning85", "model85", "token85"],
    ),
    (
        ("processor85 reasoning85 machine85 learning85 model85 token85", 18),
        ["processor85", "reasoning85", "machine85", "learning85 model85", "token85"],
    ),
    (
        ("processor85 reasoning85 machine85 learning85 model85 token85", 28),
        ["processor85 reasoning85", "machine85 learning85 model85", "token85"],
    ),
    (
        ("reasoning85 machine85 learning85 model85 token85 prompt85", 6),
        ["reasoning85", "machine85", "learning85", "model85", "token85", "prompt85"],
    ),
    (
        ("reasoning85 machine85 learning85 model85 token85 prompt85", 10),
        ["reasoning85", "machine85", "learning85", "model85", "token85", "prompt85"],
    ),
    (
        ("reasoning85 machine85 learning85 model85 token85 prompt85", 18),
        ["reasoning85", "machine85", "learning85 model85", "token85 prompt85"],
    ),
    (
        ("reasoning85 machine85 learning85 model85 token85 prompt85", 28),
        ["reasoning85 machine85", "learning85 model85 token85", "prompt85"],
    ),
    (
        ("machine85 learning85 model85 token85 prompt85 session85", 6),
        ["machine85", "learning85", "model85", "token85", "prompt85", "session85"],
    ),
    (
        ("machine85 learning85 model85 token85 prompt85 session85", 10),
        ["machine85", "learning85", "model85", "token85", "prompt85", "session85"],
    ),
    (
        ("machine85 learning85 model85 token85 prompt85 session85", 18),
        ["machine85", "learning85 model85", "token85 prompt85", "session85"],
    ),
    (
        ("machine85 learning85 model85 token85 prompt85 session85", 28),
        ["machine85 learning85 model85", "token85 prompt85 session85"],
    ),
    (
        ("learning85 model85 token85 prompt85 session85 library85", 6),
        ["learning85", "model85", "token85", "prompt85", "session85", "library85"],
    ),
    (
        ("learning85 model85 token85 prompt85 session85 library85", 10),
        ["learning85", "model85", "token85", "prompt85", "session85", "library85"],
    ),
    (
        ("learning85 model85 token85 prompt85 session85 library85", 18),
        ["learning85 model85", "token85 prompt85", "session85", "library85"],
    ),
    (
        ("learning85 model85 token85 prompt85 session85 library85", 28),
        ["learning85 model85 token85", "prompt85 session85 library85"],
    ),
    (
        ("model85 token85 prompt85 session85 library85 service85", 6),
        ["model85", "token85", "prompt85", "session85", "library85", "service85"],
    ),
    (
        ("model85 token85 prompt85 session85 library85 service85", 10),
        ["model85", "token85", "prompt85", "session85", "library85", "service85"],
    ),
    (
        ("model85 token85 prompt85 session85 library85 service85", 18),
        ["model85 token85", "prompt85 session85", "library85", "service85"],
    ),
    (
        ("model85 token85 prompt85 session85 library85 service85", 28),
        ["model85 token85 prompt85", "session85 library85", "service85"],
    ),
    (
        ("token85 prompt85 session85 library85 service85 gateway85", 6),
        ["token85", "prompt85", "session85", "library85", "service85", "gateway85"],
    ),
    (
        ("token85 prompt85 session85 library85 service85 gateway85", 10),
        ["token85", "prompt85", "session85", "library85", "service85", "gateway85"],
    ),
    (
        ("token85 prompt85 session85 library85 service85 gateway85", 18),
        ["token85 prompt85", "session85", "library85", "service85", "gateway85"],
    ),
    (
        ("token85 prompt85 session85 library85 service85 gateway85", 28),
        ["token85 prompt85 session85", "library85 service85", "gateway85"],
    ),
    (
        ("prompt85 session85 library85 service85 gateway85 storage85", 6),
        ["prompt85", "session85", "library85", "service85", "gateway85", "storage85"],
    ),
    (
        ("prompt85 session85 library85 service85 gateway85 storage85", 10),
        ["prompt85", "session85", "library85", "service85", "gateway85", "storage85"],
    ),
    (
        ("prompt85 session85 library85 service85 gateway85 storage85", 18),
        ["prompt85 session85", "library85", "service85", "gateway85", "storage85"],
    ),
    (
        ("prompt85 session85 library85 service85 gateway85 storage85", 28),
        ["prompt85 session85 library85", "service85 gateway85", "storage85"],
    ),
    (
        ("session85 library85 service85 gateway85 storage85 network85", 6),
        ["session85", "library85", "service85", "gateway85", "storage85", "network85"],
    ),
    (
        ("session85 library85 service85 gateway85 storage85 network85", 10),
        ["session85", "library85", "service85", "gateway85", "storage85", "network85"],
    ),
    (
        ("session85 library85 service85 gateway85 storage85 network85", 18),
        ["session85", "library85", "service85", "gateway85", "storage85", "network85"],
    ),
    (
        ("session85 library85 service85 gateway85 storage85 network85", 28),
        ["session85 library85", "service85 gateway85", "storage85 network85"],
    ),
    (
        ("library85 service85 gateway85 storage85 network85 latency85", 6),
        ["library85", "service85", "gateway85", "storage85", "network85", "latency85"],
    ),
    (
        ("library85 service85 gateway85 storage85 network85 latency85", 10),
        ["library85", "service85", "gateway85", "storage85", "network85", "latency85"],
    ),
    (
        ("library85 service85 gateway85 storage85 network85 latency85", 18),
        ["library85", "service85", "gateway85", "storage85", "network85", "latency85"],
    ),
    (
        ("library85 service85 gateway85 storage85 network85 latency85", 28),
        ["library85 service85", "gateway85 storage85", "network85 latency85"],
    ),
    (
        ("service85 gateway85 storage85 network85 latency85 buffer85", 6),
        ["service85", "gateway85", "storage85", "network85", "latency85", "buffer85"],
    ),
    (
        ("service85 gateway85 storage85 network85 latency85 buffer85", 10),
        ["service85", "gateway85", "storage85", "network85", "latency85", "buffer85"],
    ),
    (
        ("service85 gateway85 storage85 network85 latency85 buffer85", 18),
        ["service85", "gateway85", "storage85", "network85", "latency85 buffer85"],
    ),
    (
        ("service85 gateway85 storage85 network85 latency85 buffer85", 28),
        ["service85 gateway85", "storage85 network85", "latency85 buffer85"],
    ),
    (
        ("gateway85 storage85 network85 latency85 buffer85 queue85", 6),
        ["gateway85", "storage85", "network85", "latency85", "buffer85", "queue85"],
    ),
    (
        ("gateway85 storage85 network85 latency85 buffer85 queue85", 10),
        ["gateway85", "storage85", "network85", "latency85", "buffer85", "queue85"],
    ),
    (
        ("gateway85 storage85 network85 latency85 buffer85 queue85", 18),
        ["gateway85", "storage85", "network85", "latency85 buffer85", "queue85"],
    ),
    (
        ("gateway85 storage85 network85 latency85 buffer85 queue85", 28),
        ["gateway85 storage85", "network85 latency85 buffer85", "queue85"],
    ),
    (
        ("storage85 network85 latency85 buffer85 queue85 worker85", 6),
        ["storage85", "network85", "latency85", "buffer85", "queue85", "worker85"],
    ),
    (
        ("storage85 network85 latency85 buffer85 queue85 worker85", 10),
        ["storage85", "network85", "latency85", "buffer85", "queue85", "worker85"],
    ),
    (
        ("storage85 network85 latency85 buffer85 queue85 worker85", 18),
        ["storage85", "network85", "latency85 buffer85", "queue85 worker85"],
    ),
    (
        ("storage85 network85 latency85 buffer85 queue85 worker85", 28),
        ["storage85 network85", "latency85 buffer85 queue85", "worker85"],
    ),
    (
        ("network85 latency85 buffer85 queue85 worker85 kernel85", 6),
        ["network85", "latency85", "buffer85", "queue85", "worker85", "kernel85"],
    ),
    (
        ("network85 latency85 buffer85 queue85 worker85 kernel85", 10),
        ["network85", "latency85", "buffer85", "queue85", "worker85", "kernel85"],
    ),
    (
        ("network85 latency85 buffer85 queue85 worker85 kernel85", 18),
        ["network85", "latency85 buffer85", "queue85 worker85", "kernel85"],
    ),
    (
        ("network85 latency85 buffer85 queue85 worker85 kernel85", 28),
        ["network85 latency85 buffer85", "queue85 worker85 kernel85"],
    ),
    (
        ("latency85 buffer85 queue85 worker85 kernel85 signal85", 6),
        ["latency85", "buffer85", "queue85", "worker85", "kernel85", "signal85"],
    ),
    (
        ("latency85 buffer85 queue85 worker85 kernel85 signal85", 10),
        ["latency85", "buffer85", "queue85", "worker85", "kernel85", "signal85"],
    ),
    (
        ("latency85 buffer85 queue85 worker85 kernel85 signal85", 18),
        ["latency85 buffer85", "queue85 worker85", "kernel85 signal85"],
    ),
    (
        ("latency85 buffer85 queue85 worker85 kernel85 signal85", 28),
        ["latency85 buffer85 queue85", "worker85 kernel85 signal85"],
    ),
    (
        ("buffer85 queue85 worker85 kernel85 signal85 packet85", 6),
        ["buffer85", "queue85", "worker85", "kernel85", "signal85", "packet85"],
    ),
    (
        ("buffer85 queue85 worker85 kernel85 signal85 packet85", 10),
        ["buffer85", "queue85", "worker85", "kernel85", "signal85", "packet85"],
    ),
    (
        ("buffer85 queue85 worker85 kernel85 signal85 packet85", 18),
        ["buffer85 queue85", "worker85 kernel85", "signal85 packet85"],
    ),
    (
        ("buffer85 queue85 worker85 kernel85 signal85 packet85", 28),
        ["buffer85 queue85 worker85", "kernel85 signal85 packet85"],
    ),
    (
        ("queue85 worker85 kernel85 signal85 packet85 router85", 6),
        ["queue85", "worker85", "kernel85", "signal85", "packet85", "router85"],
    ),
    (
        ("queue85 worker85 kernel85 signal85 packet85 router85", 10),
        ["queue85", "worker85", "kernel85", "signal85", "packet85", "router85"],
    ),
    (
        ("queue85 worker85 kernel85 signal85 packet85 router85", 18),
        ["queue85 worker85", "kernel85 signal85", "packet85 router85"],
    ),
    (
        ("queue85 worker85 kernel85 signal85 packet85 router85", 28),
        ["queue85 worker85 kernel85", "signal85 packet85 router85"],
    ),
    (
        ("worker85 kernel85 signal85 packet85 router85 cluster85", 6),
        ["worker85", "kernel85", "signal85", "packet85", "router85", "cluster85"],
    ),
    (
        ("worker85 kernel85 signal85 packet85 router85 cluster85", 10),
        ["worker85", "kernel85", "signal85", "packet85", "router85", "cluster85"],
    ),
    (
        ("worker85 kernel85 signal85 packet85 router85 cluster85", 18),
        ["worker85 kernel85", "signal85 packet85", "router85 cluster85"],
    ),
    (
        ("worker85 kernel85 signal85 packet85 router85 cluster85", 28),
        ["worker85 kernel85 signal85", "packet85 router85 cluster85"],
    ),
    (
        ("kernel85 signal85 packet85 router85 cluster85 mirror85", 6),
        ["kernel85", "signal85", "packet85", "router85", "cluster85", "mirror85"],
    ),
    (
        ("kernel85 signal85 packet85 router85 cluster85 mirror85", 10),
        ["kernel85", "signal85", "packet85", "router85", "cluster85", "mirror85"],
    ),
    (
        ("kernel85 signal85 packet85 router85 cluster85 mirror85", 18),
        ["kernel85 signal85", "packet85 router85", "cluster85 mirror85"],
    ),
    (
        ("kernel85 signal85 packet85 router85 cluster85 mirror85", 28),
        ["kernel85 signal85 packet85", "router85 cluster85 mirror85"],
    ),
    (
        ("signal85 packet85 router85 cluster85 mirror85 filter85", 6),
        ["signal85", "packet85", "router85", "cluster85", "mirror85", "filter85"],
    ),
    (
        ("signal85 packet85 router85 cluster85 mirror85 filter85", 10),
        ["signal85", "packet85", "router85", "cluster85", "mirror85", "filter85"],
    ),
    (
        ("signal85 packet85 router85 cluster85 mirror85 filter85", 18),
        ["signal85 packet85", "router85 cluster85", "mirror85 filter85"],
    ),
    (
        ("signal85 packet85 router85 cluster85 mirror85 filter85", 28),
        ["signal85 packet85 router85", "cluster85 mirror85 filter85"],
    ),
    (
        ("packet85 router85 cluster85 mirror85 filter85 ranking85", 6),
        ["packet85", "router85", "cluster85", "mirror85", "filter85", "ranking85"],
    ),
    (
        ("packet85 router85 cluster85 mirror85 filter85 ranking85", 10),
        ["packet85", "router85", "cluster85", "mirror85", "filter85", "ranking85"],
    ),
    (
        ("packet85 router85 cluster85 mirror85 filter85 ranking85", 18),
        ["packet85 router85", "cluster85 mirror85", "filter85 ranking85"],
    ),
    (
        ("packet85 router85 cluster85 mirror85 filter85 ranking85", 28),
        ["packet85 router85 cluster85", "mirror85 filter85 ranking85"],
    ),
    (
        ("router85 cluster85 mirror85 filter85 ranking85 encoding85", 6),
        ["router85", "cluster85", "mirror85", "filter85", "ranking85", "encoding85"],
    ),
    (
        ("router85 cluster85 mirror85 filter85 ranking85 encoding85", 10),
        ["router85", "cluster85", "mirror85", "filter85", "ranking85", "encoding85"],
    ),
    (
        ("router85 cluster85 mirror85 filter85 ranking85 encoding85", 18),
        ["router85 cluster85", "mirror85 filter85", "ranking85", "encoding85"],
    ),
    (
        ("router85 cluster85 mirror85 filter85 ranking85 encoding85", 28),
        ["router85 cluster85 mirror85", "filter85 ranking85", "encoding85"],
    ),
    (
        ("cluster85 mirror85 filter85 ranking85 encoding85 mapping85", 6),
        ["cluster85", "mirror85", "filter85", "ranking85", "encoding85", "mapping85"],
    ),
    (
        ("cluster85 mirror85 filter85 ranking85 encoding85 mapping85", 10),
        ["cluster85", "mirror85", "filter85", "ranking85", "encoding85", "mapping85"],
    ),
    (
        ("cluster85 mirror85 filter85 ranking85 encoding85 mapping85", 18),
        ["cluster85 mirror85", "filter85 ranking85", "encoding85", "mapping85"],
    ),
    (
        ("cluster85 mirror85 filter85 ranking85 encoding85 mapping85", 28),
        ["cluster85 mirror85 filter85", "ranking85 encoding85", "mapping85"],
    ),
    (
        ("mirror85 filter85 ranking85 encoding85 mapping85 record85", 6),
        ["mirror85", "filter85", "ranking85", "encoding85", "mapping85", "record85"],
    ),
    (
        ("mirror85 filter85 ranking85 encoding85 mapping85 record85", 10),
        ["mirror85", "filter85", "ranking85", "encoding85", "mapping85", "record85"],
    ),
    (
        ("mirror85 filter85 ranking85 encoding85 mapping85 record85", 18),
        ["mirror85 filter85", "ranking85", "encoding85", "mapping85 record85"],
    ),
    (
        ("mirror85 filter85 ranking85 encoding85 mapping85 record85", 28),
        ["mirror85 filter85 ranking85", "encoding85 mapping85", "record85"],
    ),
    (
        ("filter85 ranking85 encoding85 mapping85 record85 candle85", 6),
        ["filter85", "ranking85", "encoding85", "mapping85", "record85", "candle85"],
    ),
    (
        ("filter85 ranking85 encoding85 mapping85 record85 candle85", 10),
        ["filter85", "ranking85", "encoding85", "mapping85", "record85", "candle85"],
    ),
    (
        ("filter85 ranking85 encoding85 mapping85 record85 candle85", 18),
        ["filter85 ranking85", "encoding85", "mapping85 record85", "candle85"],
    ),
    (
        ("filter85 ranking85 encoding85 mapping85 record85 candle85", 28),
        ["filter85 ranking85", "encoding85 mapping85", "record85 candle85"],
    ),
    (
        ("ranking85 encoding85 mapping85 record85 candle85 thread85", 6),
        ["ranking85", "encoding85", "mapping85", "record85", "candle85", "thread85"],
    ),
    (
        ("ranking85 encoding85 mapping85 record85 candle85 thread85", 10),
        ["ranking85", "encoding85", "mapping85", "record85", "candle85", "thread85"],
    ),
    (
        ("ranking85 encoding85 mapping85 record85 candle85 thread85", 18),
        ["ranking85", "encoding85", "mapping85 record85", "candle85 thread85"],
    ),
    (
        ("ranking85 encoding85 mapping85 record85 candle85 thread85", 28),
        ["ranking85 encoding85", "mapping85 record85 candle85", "thread85"],
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
