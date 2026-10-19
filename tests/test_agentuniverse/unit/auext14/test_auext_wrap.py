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
        ("round 14: the quick brown fox jumps over the lazy dog", 4),
        ["round", "14:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 14: the quick brown fox jumps over the lazy dog", 8),
        ["round", "14: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 14: the quick brown fox jumps over the lazy dog", 12),
        ["round 14:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 14: the quick brown fox jumps over the lazy dog", 16),
        ["round 14: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 14: the quick brown fox jumps over the lazy dog", 24),
        ["round 14: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 14: the quick brown fox jumps over the lazy dog", 32),
        ["round 14: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 14: agentuniverse is a framework for multi agents", 4),
        ["round", "14:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 14: agentuniverse is a framework for multi agents", 8),
        ["round", "14:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 14: agentuniverse is a framework for multi agents", 12),
        ["round 14:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 14: agentuniverse is a framework for multi agents", 16),
        ["round 14:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 14: agentuniverse is a framework for multi agents", 24),
        ["round 14: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 14: agentuniverse is a framework for multi agents", 32),
        ["round 14: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 14: knowledge stored as vectors enables retrieval", 4),
        ["round", "14:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 14: knowledge stored as vectors enables retrieval", 8),
        ["round", "14:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 14: knowledge stored as vectors enables retrieval", 12),
        ["round 14:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 14: knowledge stored as vectors enables retrieval", 16),
        ["round 14:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 14: knowledge stored as vectors enables retrieval", 24),
        ["round 14: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 14: knowledge stored as vectors enables retrieval", 32),
        ["round 14: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 14: the processor reads the record then stops", 4),
        ["round", "14:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 14: the processor reads the record then stops", 8),
        ["round", "14: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 14: the processor reads the record then stops", 12),
        ["round 14:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 14: the processor reads the record then stops", 16),
        ["round 14: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 14: the processor reads the record then stops", 24),
        ["round 14: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 14: the processor reads the record then stops", 32),
        ["round 14: the processor reads", "the record then stops"],
    ),
    (
        ("round 14: a worker pulls the next task from the queue", 4),
        ["round", "14:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 14: a worker pulls the next task from the queue", 8),
        ["round", "14: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 14: a worker pulls the next task from the queue", 12),
        ["round 14: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 14: a worker pulls the next task from the queue", 16),
        ["round 14: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 14: a worker pulls the next task from the queue", 24),
        ["round 14: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 14: a worker pulls the next task from the queue", 32),
        ["round 14: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 14: signals travel through the network layer", 4),
        ["round", "14:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 14: signals travel through the network layer", 8),
        ["round", "14:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 14: signals travel through the network layer", 12),
        ["round 14:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 14: signals travel through the network layer", 16),
        ["round 14:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 14: signals travel through the network layer", 24),
        ["round 14: signals travel", "through the network", "layer"],
    ),
    (
        ("round 14: signals travel through the network layer", 32),
        ["round 14: signals travel through", "the network layer"],
    ),
    (
        ("round 14: the gateway routes each request by policy", 4),
        ["round", "14:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 14: the gateway routes each request by policy", 8),
        ["round", "14: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 14: the gateway routes each request by policy", 12),
        ["round 14:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 14: the gateway routes each request by policy", 16),
        ["round 14: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 14: the gateway routes each request by policy", 24),
        ["round 14: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 14: the gateway routes each request by policy", 32),
        ["round 14: the gateway routes", "each request by policy"],
    ),
    (
        ("round 14: memory grows until the buffer is full", 4),
        ["round", "14:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 14: memory grows until the buffer is full", 8),
        ["round", "14:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 14: memory grows until the buffer is full", 12),
        ["round 14:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 14: memory grows until the buffer is full", 16),
        ["round 14: memory", "grows until the", "buffer is full"],
    ),
    (("round 14: memory grows until the buffer is full", 24), ["round 14: memory grows", "until the buffer is full"]),
    (("round 14: memory grows until the buffer is full", 32), ["round 14: memory grows until the", "buffer is full"]),
    (
        ("round 14: the cluster mirrors every packet twice", 4),
        ["round", "14:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 14: the cluster mirrors every packet twice", 8),
        ["round", "14: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 14: the cluster mirrors every packet twice", 12),
        ["round 14:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 14: the cluster mirrors every packet twice", 16),
        ["round 14: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 14: the cluster mirrors every packet twice", 24),
        ["round 14: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 14: the cluster mirrors every packet twice", 32), ["round 14: the cluster mirrors", "every packet twice"]),
    (
        ("round 14: ranking uses tokens learned from the corpus", 4),
        ["round", "14:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 14: ranking uses tokens learned from the corpus", 8),
        ["round", "14:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 14: ranking uses tokens learned from the corpus", 12),
        ["round 14:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 14: ranking uses tokens learned from the corpus", 16),
        ["round 14:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 14: ranking uses tokens learned from the corpus", 24),
        ["round 14: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 14: ranking uses tokens learned from the corpus", 32),
        ["round 14: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 14: a long session ends when the candle dies", 4),
        ["round", "14:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 14: a long session ends when the candle dies", 8),
        ["round", "14: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 14: a long session ends when the candle dies", 12),
        ["round 14: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 14: a long session ends when the candle dies", 16),
        ["round 14: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 14: a long session ends when the candle dies", 24),
        ["round 14: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 14: a long session ends when the candle dies", 32),
        ["round 14: a long session ends", "when the candle dies"],
    ),
    (
        ("round 14: encode the prompt then map the result", 4),
        ["round", "14:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 14: encode the prompt then map the result", 8),
        ["round", "14:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 14: encode the prompt then map the result", 12),
        ["round 14:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 14: encode the prompt then map the result", 16),
        ["round 14: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 14: encode the prompt then map the result", 24),
        ["round 14: encode the", "prompt then map the", "result"],
    ),
    (("round 14: encode the prompt then map the result", 32), ["round 14: encode the prompt then", "map the result"]),
    (
        ("round 14: the kernel wakes the worker at dawn", 4),
        ["round", "14:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 14: the kernel wakes the worker at dawn", 8),
        ["round", "14: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 14: the kernel wakes the worker at dawn", 12),
        ["round 14:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 14: the kernel wakes the worker at dawn", 16), ["round 14: the", "kernel wakes the", "worker at dawn"]),
    (("round 14: the kernel wakes the worker at dawn", 24), ["round 14: the kernel", "wakes the worker at dawn"]),
    (("round 14: the kernel wakes the worker at dawn", 32), ["round 14: the kernel wakes the", "worker at dawn"]),
    (
        ("round 14: service latency drops after the patch", 4),
        ["round", "14:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 14: service latency drops after the patch", 8),
        ["round", "14:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 14: service latency drops after the patch", 12),
        ["round 14:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 14: service latency drops after the patch", 16),
        ["round 14:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 14: service latency drops after the patch", 24),
        ["round 14: service", "latency drops after the", "patch"],
    ),
    (("round 14: service latency drops after the patch", 32), ["round 14: service latency drops", "after the patch"]),
    (
        ("round 14: the library caches every vector it sees", 4),
        ["round", "14:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 14: the library caches every vector it sees", 8),
        ["round", "14: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 14: the library caches every vector it sees", 12),
        ["round 14:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 14: the library caches every vector it sees", 16),
        ["round 14: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 14: the library caches every vector it sees", 24),
        ["round 14: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 14: the library caches every vector it sees", 32),
        ["round 14: the library caches", "every vector it sees"],
    ),
    (
        ("round 14: agents argue then the debate resolves", 4),
        ["round", "14:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 14: agents argue then the debate resolves", 8),
        ["round", "14:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 14: agents argue then the debate resolves", 12),
        ["round 14:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 14: agents argue then the debate resolves", 16),
        ["round 14: agents", "argue then the", "debate resolves"],
    ),
    (("round 14: agents argue then the debate resolves", 24), ["round 14: agents argue", "then the debate resolves"]),
    (("round 14: agents argue then the debate resolves", 32), ["round 14: agents argue then the", "debate resolves"]),
    (
        ("round 14: the filter keeps only strong matches", 4),
        ["round", "14:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 14: the filter keeps only strong matches", 8),
        ["round", "14: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 14: the filter keeps only strong matches", 12),
        ["round 14:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 14: the filter keeps only strong matches", 16),
        ["round 14: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 14: the filter keeps only strong matches", 24), ["round 14: the filter", "keeps only strong", "matches"]),
    (("round 14: the filter keeps only strong matches", 32), ["round 14: the filter keeps only", "strong matches"]),
    (
        ("round 14: the model answers with a short reply", 4),
        ["round", "14:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 14: the model answers with a short reply", 8),
        ["round", "14: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 14: the model answers with a short reply", 12),
        ["round 14:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 14: the model answers with a short reply", 16),
        ["round 14: the", "model answers", "with a short", "reply"],
    ),
    (("round 14: the model answers with a short reply", 24), ["round 14: the model", "answers with a short", "reply"]),
    (("round 14: the model answers with a short reply", 32), ["round 14: the model answers with", "a short reply"]),
    (
        ("round 14: the recorder stores the reasoning trace", 4),
        ["round", "14:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 14: the recorder stores the reasoning trace", 8),
        ["round", "14: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 14: the recorder stores the reasoning trace", 12),
        ["round 14:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 14: the recorder stores the reasoning trace", 16),
        ["round 14: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 14: the recorder stores the reasoning trace", 24),
        ["round 14: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 14: the recorder stores the reasoning trace", 32),
        ["round 14: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 14: the angel watches the processor run", 4),
        ["round", "14:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 14: the angel watches the processor run", 8),
        ["round", "14: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 14: the angel watches the processor run", 12),
        ["round 14:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 14: the angel watches the processor run", 16), ["round 14: the", "angel watches", "the processor", "run"]),
    (("round 14: the angel watches the processor run", 24), ["round 14: the angel", "watches the processor", "run"]),
    (("round 14: the angel watches the processor run", 32), ["round 14: the angel watches the", "processor run"]),
    (
        ("round 14: angle of the vector decides the match", 4),
        ["round", "14:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 14: angle of the vector decides the match", 8),
        ["round", "14:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 14: angle of the vector decides the match", 12),
        ["round 14:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 14: angle of the vector decides the match", 16),
        ["round 14: angle", "of the vector", "decides the", "match"],
    ),
    (("round 14: angle of the vector decides the match", 24), ["round 14: angle of the", "vector decides the match"]),
    (("round 14: angle of the vector decides the match", 32), ["round 14: angle of the vector", "decides the match"]),
    (
        ("round 14: the candle burns twice as long at night", 4),
        ["round", "14:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 14: the candle burns twice as long at night", 8),
        ["round", "14: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 14: the candle burns twice as long at night", 12),
        ["round 14:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 14: the candle burns twice as long at night", 16),
        ["round 14: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 14: the candle burns twice as long at night", 24),
        ["round 14: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 14: the candle burns twice as long at night", 32),
        ["round 14: the candle burns twice", "as long at night"],
    ),
    (
        ("round 14: a mirror of the universe in one line", 4),
        ["round", "14:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 14: a mirror of the universe in one line", 8),
        ["round", "14: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 14: a mirror of the universe in one line", 12),
        ["round 14: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 14: a mirror of the universe in one line", 16),
        ["round 14: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 14: a mirror of the universe in one line", 24), ["round 14: a mirror of", "the universe in one line"]),
    (("round 14: a mirror of the universe in one line", 32), ["round 14: a mirror of the", "universe in one line"]),
    (
        ("round 14: the queue drains before the storm", 4),
        ["round", "14:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 14: the queue drains before the storm", 8),
        ["round", "14: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 14: the queue drains before the storm", 12), ["round 14:", "the queue", "drains", "before the", "storm"]),
    (("round 14: the queue drains before the storm", 16), ["round 14: the", "queue drains", "before the storm"]),
    (("round 14: the queue drains before the storm", 24), ["round 14: the queue", "drains before the storm"]),
    (("round 14: the queue drains before the storm", 32), ["round 14: the queue drains", "before the storm"]),
    (
        ("kitten14 sitting14 agent14 angle14 universe14 memory14", 6),
        ["kitten14", "sitting14", "agent14", "angle14", "universe14", "memory14"],
    ),
    (
        ("kitten14 sitting14 agent14 angle14 universe14 memory14", 10),
        ["kitten14", "sitting14", "agent14", "angle14", "universe14", "memory14"],
    ),
    (
        ("kitten14 sitting14 agent14 angle14 universe14 memory14", 18),
        ["kitten14 sitting14", "agent14 angle14", "universe14", "memory14"],
    ),
    (
        ("kitten14 sitting14 agent14 angle14 universe14 memory14", 28),
        ["kitten14 sitting14 agent14", "angle14 universe14 memory14"],
    ),
    (
        ("sitting14 agent14 angle14 universe14 memory14 stream14", 6),
        ["sitting14", "agent14", "angle14", "universe14", "memory14", "stream14"],
    ),
    (
        ("sitting14 agent14 angle14 universe14 memory14 stream14", 10),
        ["sitting14", "agent14", "angle14", "universe14", "memory14", "stream14"],
    ),
    (
        ("sitting14 agent14 angle14 universe14 memory14 stream14", 18),
        ["sitting14 agent14", "angle14 universe14", "memory14 stream14"],
    ),
    (
        ("sitting14 agent14 angle14 universe14 memory14 stream14", 28),
        ["sitting14 agent14 angle14", "universe14 memory14 stream14"],
    ),
    (
        ("agent14 angle14 universe14 memory14 stream14 context14", 6),
        ["agent14", "angle14", "universe14", "memory14", "stream14", "context14"],
    ),
    (
        ("agent14 angle14 universe14 memory14 stream14 context14", 10),
        ["agent14", "angle14", "universe14", "memory14", "stream14", "context14"],
    ),
    (
        ("agent14 angle14 universe14 memory14 stream14 context14", 18),
        ["agent14 angle14", "universe14", "memory14 stream14", "context14"],
    ),
    (
        ("agent14 angle14 universe14 memory14 stream14 context14", 28),
        ["agent14 angle14 universe14", "memory14 stream14 context14"],
    ),
    (
        ("angle14 universe14 memory14 stream14 context14 knowledge14", 6),
        ["angle14", "universe14", "memory14", "stream14", "context14", "knowledge14"],
    ),
    (
        ("angle14 universe14 memory14 stream14 context14 knowledge14", 10),
        ["angle14", "universe14", "memory14", "stream14", "context14", "knowledge14"],
    ),
    (
        ("angle14 universe14 memory14 stream14 context14 knowledge14", 18),
        ["angle14 universe14", "memory14 stream14", "context14", "knowledge14"],
    ),
    (
        ("angle14 universe14 memory14 stream14 context14 knowledge14", 28),
        ["angle14 universe14 memory14", "stream14 context14", "knowledge14"],
    ),
    (
        ("universe14 memory14 stream14 context14 knowledge14 vector14", 6),
        ["universe14", "memory14", "stream14", "context14", "knowledge14", "vector14"],
    ),
    (
        ("universe14 memory14 stream14 context14 knowledge14 vector14", 10),
        ["universe14", "memory14", "stream14", "context14", "knowledge14", "vector14"],
    ),
    (
        ("universe14 memory14 stream14 context14 knowledge14 vector14", 18),
        ["universe14", "memory14 stream14", "context14", "knowledge14", "vector14"],
    ),
    (
        ("universe14 memory14 stream14 context14 knowledge14 vector14", 28),
        ["universe14 memory14 stream14", "context14 knowledge14", "vector14"],
    ),
    (
        ("memory14 stream14 context14 knowledge14 vector14 processor14", 6),
        ["memory14", "stream14", "context14", "knowledge14", "vector14", "processor14"],
    ),
    (
        ("memory14 stream14 context14 knowledge14 vector14 processor14", 10),
        ["memory14", "stream14", "context14", "knowledge14", "vector14", "processor14"],
    ),
    (
        ("memory14 stream14 context14 knowledge14 vector14 processor14", 18),
        ["memory14 stream14", "context14", "knowledge14", "vector14", "processor14"],
    ),
    (
        ("memory14 stream14 context14 knowledge14 vector14 processor14", 28),
        ["memory14 stream14 context14", "knowledge14 vector14", "processor14"],
    ),
    (
        ("stream14 context14 knowledge14 vector14 processor14 reasoning14", 6),
        ["stream14", "context14", "knowledge14", "vector14", "processor14", "reasoning14"],
    ),
    (
        ("stream14 context14 knowledge14 vector14 processor14 reasoning14", 10),
        ["stream14", "context14", "knowledge14", "vector14", "processor14", "reasoning14"],
    ),
    (
        ("stream14 context14 knowledge14 vector14 processor14 reasoning14", 18),
        ["stream14 context14", "knowledge14", "vector14", "processor14", "reasoning14"],
    ),
    (
        ("stream14 context14 knowledge14 vector14 processor14 reasoning14", 28),
        ["stream14 context14", "knowledge14 vector14", "processor14 reasoning14"],
    ),
    (
        ("context14 knowledge14 vector14 processor14 reasoning14 machine14", 6),
        ["context14", "knowledge14", "vector14", "processor14", "reasoning14", "machine14"],
    ),
    (
        ("context14 knowledge14 vector14 processor14 reasoning14 machine14", 10),
        ["context14", "knowledge14", "vector14", "processor14", "reasoning14", "machine14"],
    ),
    (
        ("context14 knowledge14 vector14 processor14 reasoning14 machine14", 18),
        ["context14", "knowledge14", "vector14", "processor14", "reasoning14", "machine14"],
    ),
    (
        ("context14 knowledge14 vector14 processor14 reasoning14 machine14", 28),
        ["context14 knowledge14", "vector14 processor14", "reasoning14 machine14"],
    ),
    (
        ("knowledge14 vector14 processor14 reasoning14 machine14 learning14", 6),
        ["knowledge14", "vector14", "processor14", "reasoning14", "machine14", "learning14"],
    ),
    (
        ("knowledge14 vector14 processor14 reasoning14 machine14 learning14", 10),
        ["knowledge14", "vector14", "processor14", "reasoning14", "machine14", "learning14"],
    ),
    (
        ("knowledge14 vector14 processor14 reasoning14 machine14 learning14", 18),
        ["knowledge14", "vector14", "processor14", "reasoning14", "machine14", "learning14"],
    ),
    (
        ("knowledge14 vector14 processor14 reasoning14 machine14 learning14", 28),
        ["knowledge14 vector14", "processor14 reasoning14", "machine14 learning14"],
    ),
    (
        ("vector14 processor14 reasoning14 machine14 learning14 model14", 6),
        ["vector14", "processor14", "reasoning14", "machine14", "learning14", "model14"],
    ),
    (
        ("vector14 processor14 reasoning14 machine14 learning14 model14", 10),
        ["vector14", "processor14", "reasoning14", "machine14", "learning14", "model14"],
    ),
    (
        ("vector14 processor14 reasoning14 machine14 learning14 model14", 18),
        ["vector14", "processor14", "reasoning14", "machine14", "learning14 model14"],
    ),
    (
        ("vector14 processor14 reasoning14 machine14 learning14 model14", 28),
        ["vector14 processor14", "reasoning14 machine14", "learning14 model14"],
    ),
    (
        ("processor14 reasoning14 machine14 learning14 model14 token14", 6),
        ["processor14", "reasoning14", "machine14", "learning14", "model14", "token14"],
    ),
    (
        ("processor14 reasoning14 machine14 learning14 model14 token14", 10),
        ["processor14", "reasoning14", "machine14", "learning14", "model14", "token14"],
    ),
    (
        ("processor14 reasoning14 machine14 learning14 model14 token14", 18),
        ["processor14", "reasoning14", "machine14", "learning14 model14", "token14"],
    ),
    (
        ("processor14 reasoning14 machine14 learning14 model14 token14", 28),
        ["processor14 reasoning14", "machine14 learning14 model14", "token14"],
    ),
    (
        ("reasoning14 machine14 learning14 model14 token14 prompt14", 6),
        ["reasoning14", "machine14", "learning14", "model14", "token14", "prompt14"],
    ),
    (
        ("reasoning14 machine14 learning14 model14 token14 prompt14", 10),
        ["reasoning14", "machine14", "learning14", "model14", "token14", "prompt14"],
    ),
    (
        ("reasoning14 machine14 learning14 model14 token14 prompt14", 18),
        ["reasoning14", "machine14", "learning14 model14", "token14 prompt14"],
    ),
    (
        ("reasoning14 machine14 learning14 model14 token14 prompt14", 28),
        ["reasoning14 machine14", "learning14 model14 token14", "prompt14"],
    ),
    (
        ("machine14 learning14 model14 token14 prompt14 session14", 6),
        ["machine14", "learning14", "model14", "token14", "prompt14", "session14"],
    ),
    (
        ("machine14 learning14 model14 token14 prompt14 session14", 10),
        ["machine14", "learning14", "model14", "token14", "prompt14", "session14"],
    ),
    (
        ("machine14 learning14 model14 token14 prompt14 session14", 18),
        ["machine14", "learning14 model14", "token14 prompt14", "session14"],
    ),
    (
        ("machine14 learning14 model14 token14 prompt14 session14", 28),
        ["machine14 learning14 model14", "token14 prompt14 session14"],
    ),
    (
        ("learning14 model14 token14 prompt14 session14 library14", 6),
        ["learning14", "model14", "token14", "prompt14", "session14", "library14"],
    ),
    (
        ("learning14 model14 token14 prompt14 session14 library14", 10),
        ["learning14", "model14", "token14", "prompt14", "session14", "library14"],
    ),
    (
        ("learning14 model14 token14 prompt14 session14 library14", 18),
        ["learning14 model14", "token14 prompt14", "session14", "library14"],
    ),
    (
        ("learning14 model14 token14 prompt14 session14 library14", 28),
        ["learning14 model14 token14", "prompt14 session14 library14"],
    ),
    (
        ("model14 token14 prompt14 session14 library14 service14", 6),
        ["model14", "token14", "prompt14", "session14", "library14", "service14"],
    ),
    (
        ("model14 token14 prompt14 session14 library14 service14", 10),
        ["model14", "token14", "prompt14", "session14", "library14", "service14"],
    ),
    (
        ("model14 token14 prompt14 session14 library14 service14", 18),
        ["model14 token14", "prompt14 session14", "library14", "service14"],
    ),
    (
        ("model14 token14 prompt14 session14 library14 service14", 28),
        ["model14 token14 prompt14", "session14 library14", "service14"],
    ),
    (
        ("token14 prompt14 session14 library14 service14 gateway14", 6),
        ["token14", "prompt14", "session14", "library14", "service14", "gateway14"],
    ),
    (
        ("token14 prompt14 session14 library14 service14 gateway14", 10),
        ["token14", "prompt14", "session14", "library14", "service14", "gateway14"],
    ),
    (
        ("token14 prompt14 session14 library14 service14 gateway14", 18),
        ["token14 prompt14", "session14", "library14", "service14", "gateway14"],
    ),
    (
        ("token14 prompt14 session14 library14 service14 gateway14", 28),
        ["token14 prompt14 session14", "library14 service14", "gateway14"],
    ),
    (
        ("prompt14 session14 library14 service14 gateway14 storage14", 6),
        ["prompt14", "session14", "library14", "service14", "gateway14", "storage14"],
    ),
    (
        ("prompt14 session14 library14 service14 gateway14 storage14", 10),
        ["prompt14", "session14", "library14", "service14", "gateway14", "storage14"],
    ),
    (
        ("prompt14 session14 library14 service14 gateway14 storage14", 18),
        ["prompt14 session14", "library14", "service14", "gateway14", "storage14"],
    ),
    (
        ("prompt14 session14 library14 service14 gateway14 storage14", 28),
        ["prompt14 session14 library14", "service14 gateway14", "storage14"],
    ),
    (
        ("session14 library14 service14 gateway14 storage14 network14", 6),
        ["session14", "library14", "service14", "gateway14", "storage14", "network14"],
    ),
    (
        ("session14 library14 service14 gateway14 storage14 network14", 10),
        ["session14", "library14", "service14", "gateway14", "storage14", "network14"],
    ),
    (
        ("session14 library14 service14 gateway14 storage14 network14", 18),
        ["session14", "library14", "service14", "gateway14", "storage14", "network14"],
    ),
    (
        ("session14 library14 service14 gateway14 storage14 network14", 28),
        ["session14 library14", "service14 gateway14", "storage14 network14"],
    ),
    (
        ("library14 service14 gateway14 storage14 network14 latency14", 6),
        ["library14", "service14", "gateway14", "storage14", "network14", "latency14"],
    ),
    (
        ("library14 service14 gateway14 storage14 network14 latency14", 10),
        ["library14", "service14", "gateway14", "storage14", "network14", "latency14"],
    ),
    (
        ("library14 service14 gateway14 storage14 network14 latency14", 18),
        ["library14", "service14", "gateway14", "storage14", "network14", "latency14"],
    ),
    (
        ("library14 service14 gateway14 storage14 network14 latency14", 28),
        ["library14 service14", "gateway14 storage14", "network14 latency14"],
    ),
    (
        ("service14 gateway14 storage14 network14 latency14 buffer14", 6),
        ["service14", "gateway14", "storage14", "network14", "latency14", "buffer14"],
    ),
    (
        ("service14 gateway14 storage14 network14 latency14 buffer14", 10),
        ["service14", "gateway14", "storage14", "network14", "latency14", "buffer14"],
    ),
    (
        ("service14 gateway14 storage14 network14 latency14 buffer14", 18),
        ["service14", "gateway14", "storage14", "network14", "latency14 buffer14"],
    ),
    (
        ("service14 gateway14 storage14 network14 latency14 buffer14", 28),
        ["service14 gateway14", "storage14 network14", "latency14 buffer14"],
    ),
    (
        ("gateway14 storage14 network14 latency14 buffer14 queue14", 6),
        ["gateway14", "storage14", "network14", "latency14", "buffer14", "queue14"],
    ),
    (
        ("gateway14 storage14 network14 latency14 buffer14 queue14", 10),
        ["gateway14", "storage14", "network14", "latency14", "buffer14", "queue14"],
    ),
    (
        ("gateway14 storage14 network14 latency14 buffer14 queue14", 18),
        ["gateway14", "storage14", "network14", "latency14 buffer14", "queue14"],
    ),
    (
        ("gateway14 storage14 network14 latency14 buffer14 queue14", 28),
        ["gateway14 storage14", "network14 latency14 buffer14", "queue14"],
    ),
    (
        ("storage14 network14 latency14 buffer14 queue14 worker14", 6),
        ["storage14", "network14", "latency14", "buffer14", "queue14", "worker14"],
    ),
    (
        ("storage14 network14 latency14 buffer14 queue14 worker14", 10),
        ["storage14", "network14", "latency14", "buffer14", "queue14", "worker14"],
    ),
    (
        ("storage14 network14 latency14 buffer14 queue14 worker14", 18),
        ["storage14", "network14", "latency14 buffer14", "queue14 worker14"],
    ),
    (
        ("storage14 network14 latency14 buffer14 queue14 worker14", 28),
        ["storage14 network14", "latency14 buffer14 queue14", "worker14"],
    ),
    (
        ("network14 latency14 buffer14 queue14 worker14 kernel14", 6),
        ["network14", "latency14", "buffer14", "queue14", "worker14", "kernel14"],
    ),
    (
        ("network14 latency14 buffer14 queue14 worker14 kernel14", 10),
        ["network14", "latency14", "buffer14", "queue14", "worker14", "kernel14"],
    ),
    (
        ("network14 latency14 buffer14 queue14 worker14 kernel14", 18),
        ["network14", "latency14 buffer14", "queue14 worker14", "kernel14"],
    ),
    (
        ("network14 latency14 buffer14 queue14 worker14 kernel14", 28),
        ["network14 latency14 buffer14", "queue14 worker14 kernel14"],
    ),
    (
        ("latency14 buffer14 queue14 worker14 kernel14 signal14", 6),
        ["latency14", "buffer14", "queue14", "worker14", "kernel14", "signal14"],
    ),
    (
        ("latency14 buffer14 queue14 worker14 kernel14 signal14", 10),
        ["latency14", "buffer14", "queue14", "worker14", "kernel14", "signal14"],
    ),
    (
        ("latency14 buffer14 queue14 worker14 kernel14 signal14", 18),
        ["latency14 buffer14", "queue14 worker14", "kernel14 signal14"],
    ),
    (
        ("latency14 buffer14 queue14 worker14 kernel14 signal14", 28),
        ["latency14 buffer14 queue14", "worker14 kernel14 signal14"],
    ),
    (
        ("buffer14 queue14 worker14 kernel14 signal14 packet14", 6),
        ["buffer14", "queue14", "worker14", "kernel14", "signal14", "packet14"],
    ),
    (
        ("buffer14 queue14 worker14 kernel14 signal14 packet14", 10),
        ["buffer14", "queue14", "worker14", "kernel14", "signal14", "packet14"],
    ),
    (
        ("buffer14 queue14 worker14 kernel14 signal14 packet14", 18),
        ["buffer14 queue14", "worker14 kernel14", "signal14 packet14"],
    ),
    (
        ("buffer14 queue14 worker14 kernel14 signal14 packet14", 28),
        ["buffer14 queue14 worker14", "kernel14 signal14 packet14"],
    ),
    (
        ("queue14 worker14 kernel14 signal14 packet14 router14", 6),
        ["queue14", "worker14", "kernel14", "signal14", "packet14", "router14"],
    ),
    (
        ("queue14 worker14 kernel14 signal14 packet14 router14", 10),
        ["queue14", "worker14", "kernel14", "signal14", "packet14", "router14"],
    ),
    (
        ("queue14 worker14 kernel14 signal14 packet14 router14", 18),
        ["queue14 worker14", "kernel14 signal14", "packet14 router14"],
    ),
    (
        ("queue14 worker14 kernel14 signal14 packet14 router14", 28),
        ["queue14 worker14 kernel14", "signal14 packet14 router14"],
    ),
    (
        ("worker14 kernel14 signal14 packet14 router14 cluster14", 6),
        ["worker14", "kernel14", "signal14", "packet14", "router14", "cluster14"],
    ),
    (
        ("worker14 kernel14 signal14 packet14 router14 cluster14", 10),
        ["worker14", "kernel14", "signal14", "packet14", "router14", "cluster14"],
    ),
    (
        ("worker14 kernel14 signal14 packet14 router14 cluster14", 18),
        ["worker14 kernel14", "signal14 packet14", "router14 cluster14"],
    ),
    (
        ("worker14 kernel14 signal14 packet14 router14 cluster14", 28),
        ["worker14 kernel14 signal14", "packet14 router14 cluster14"],
    ),
    (
        ("kernel14 signal14 packet14 router14 cluster14 mirror14", 6),
        ["kernel14", "signal14", "packet14", "router14", "cluster14", "mirror14"],
    ),
    (
        ("kernel14 signal14 packet14 router14 cluster14 mirror14", 10),
        ["kernel14", "signal14", "packet14", "router14", "cluster14", "mirror14"],
    ),
    (
        ("kernel14 signal14 packet14 router14 cluster14 mirror14", 18),
        ["kernel14 signal14", "packet14 router14", "cluster14 mirror14"],
    ),
    (
        ("kernel14 signal14 packet14 router14 cluster14 mirror14", 28),
        ["kernel14 signal14 packet14", "router14 cluster14 mirror14"],
    ),
    (
        ("signal14 packet14 router14 cluster14 mirror14 filter14", 6),
        ["signal14", "packet14", "router14", "cluster14", "mirror14", "filter14"],
    ),
    (
        ("signal14 packet14 router14 cluster14 mirror14 filter14", 10),
        ["signal14", "packet14", "router14", "cluster14", "mirror14", "filter14"],
    ),
    (
        ("signal14 packet14 router14 cluster14 mirror14 filter14", 18),
        ["signal14 packet14", "router14 cluster14", "mirror14 filter14"],
    ),
    (
        ("signal14 packet14 router14 cluster14 mirror14 filter14", 28),
        ["signal14 packet14 router14", "cluster14 mirror14 filter14"],
    ),
    (
        ("packet14 router14 cluster14 mirror14 filter14 ranking14", 6),
        ["packet14", "router14", "cluster14", "mirror14", "filter14", "ranking14"],
    ),
    (
        ("packet14 router14 cluster14 mirror14 filter14 ranking14", 10),
        ["packet14", "router14", "cluster14", "mirror14", "filter14", "ranking14"],
    ),
    (
        ("packet14 router14 cluster14 mirror14 filter14 ranking14", 18),
        ["packet14 router14", "cluster14 mirror14", "filter14 ranking14"],
    ),
    (
        ("packet14 router14 cluster14 mirror14 filter14 ranking14", 28),
        ["packet14 router14 cluster14", "mirror14 filter14 ranking14"],
    ),
    (
        ("router14 cluster14 mirror14 filter14 ranking14 encoding14", 6),
        ["router14", "cluster14", "mirror14", "filter14", "ranking14", "encoding14"],
    ),
    (
        ("router14 cluster14 mirror14 filter14 ranking14 encoding14", 10),
        ["router14", "cluster14", "mirror14", "filter14", "ranking14", "encoding14"],
    ),
    (
        ("router14 cluster14 mirror14 filter14 ranking14 encoding14", 18),
        ["router14 cluster14", "mirror14 filter14", "ranking14", "encoding14"],
    ),
    (
        ("router14 cluster14 mirror14 filter14 ranking14 encoding14", 28),
        ["router14 cluster14 mirror14", "filter14 ranking14", "encoding14"],
    ),
    (
        ("cluster14 mirror14 filter14 ranking14 encoding14 mapping14", 6),
        ["cluster14", "mirror14", "filter14", "ranking14", "encoding14", "mapping14"],
    ),
    (
        ("cluster14 mirror14 filter14 ranking14 encoding14 mapping14", 10),
        ["cluster14", "mirror14", "filter14", "ranking14", "encoding14", "mapping14"],
    ),
    (
        ("cluster14 mirror14 filter14 ranking14 encoding14 mapping14", 18),
        ["cluster14 mirror14", "filter14 ranking14", "encoding14", "mapping14"],
    ),
    (
        ("cluster14 mirror14 filter14 ranking14 encoding14 mapping14", 28),
        ["cluster14 mirror14 filter14", "ranking14 encoding14", "mapping14"],
    ),
    (
        ("mirror14 filter14 ranking14 encoding14 mapping14 record14", 6),
        ["mirror14", "filter14", "ranking14", "encoding14", "mapping14", "record14"],
    ),
    (
        ("mirror14 filter14 ranking14 encoding14 mapping14 record14", 10),
        ["mirror14", "filter14", "ranking14", "encoding14", "mapping14", "record14"],
    ),
    (
        ("mirror14 filter14 ranking14 encoding14 mapping14 record14", 18),
        ["mirror14 filter14", "ranking14", "encoding14", "mapping14 record14"],
    ),
    (
        ("mirror14 filter14 ranking14 encoding14 mapping14 record14", 28),
        ["mirror14 filter14 ranking14", "encoding14 mapping14", "record14"],
    ),
    (
        ("filter14 ranking14 encoding14 mapping14 record14 candle14", 6),
        ["filter14", "ranking14", "encoding14", "mapping14", "record14", "candle14"],
    ),
    (
        ("filter14 ranking14 encoding14 mapping14 record14 candle14", 10),
        ["filter14", "ranking14", "encoding14", "mapping14", "record14", "candle14"],
    ),
    (
        ("filter14 ranking14 encoding14 mapping14 record14 candle14", 18),
        ["filter14 ranking14", "encoding14", "mapping14 record14", "candle14"],
    ),
    (
        ("filter14 ranking14 encoding14 mapping14 record14 candle14", 28),
        ["filter14 ranking14", "encoding14 mapping14", "record14 candle14"],
    ),
    (
        ("ranking14 encoding14 mapping14 record14 candle14 thread14", 6),
        ["ranking14", "encoding14", "mapping14", "record14", "candle14", "thread14"],
    ),
    (
        ("ranking14 encoding14 mapping14 record14 candle14 thread14", 10),
        ["ranking14", "encoding14", "mapping14", "record14", "candle14", "thread14"],
    ),
    (
        ("ranking14 encoding14 mapping14 record14 candle14 thread14", 18),
        ["ranking14", "encoding14", "mapping14 record14", "candle14 thread14"],
    ),
    (
        ("ranking14 encoding14 mapping14 record14 candle14 thread14", 28),
        ["ranking14 encoding14", "mapping14 record14 candle14", "thread14"],
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
