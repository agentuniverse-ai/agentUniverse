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
        ("round 173: the quick brown fox jumps over the lazy dog", 4),
        ["round", "173:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 173: the quick brown fox jumps over the lazy dog", 8),
        ["round", "173: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 173: the quick brown fox jumps over the lazy dog", 12),
        ["round 173:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 173: the quick brown fox jumps over the lazy dog", 16),
        ["round 173: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 173: the quick brown fox jumps over the lazy dog", 24),
        ["round 173: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 173: the quick brown fox jumps over the lazy dog", 32),
        ["round 173: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 173: agentuniverse is a framework for multi agents", 4),
        ["round", "173:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 173: agentuniverse is a framework for multi agents", 8),
        ["round", "173:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 173: agentuniverse is a framework for multi agents", 12),
        ["round 173:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 173: agentuniverse is a framework for multi agents", 16),
        ["round 173:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 173: agentuniverse is a framework for multi agents", 24),
        ["round 173: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 173: agentuniverse is a framework for multi agents", 32),
        ["round 173: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 173: knowledge stored as vectors enables retrieval", 4),
        ["round", "173:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 173: knowledge stored as vectors enables retrieval", 8),
        ["round", "173:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 173: knowledge stored as vectors enables retrieval", 12),
        ["round 173:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 173: knowledge stored as vectors enables retrieval", 16),
        ["round 173:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 173: knowledge stored as vectors enables retrieval", 24),
        ["round 173: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 173: knowledge stored as vectors enables retrieval", 32),
        ["round 173: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 173: the processor reads the record then stops", 4),
        ["round", "173:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 173: the processor reads the record then stops", 8),
        ["round", "173: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 173: the processor reads the record then stops", 12),
        ["round 173:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 173: the processor reads the record then stops", 16),
        ["round 173: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 173: the processor reads the record then stops", 24),
        ["round 173: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 173: the processor reads the record then stops", 32),
        ["round 173: the processor reads", "the record then stops"],
    ),
    (
        ("round 173: a worker pulls the next task from the queue", 4),
        ["round", "173:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 173: a worker pulls the next task from the queue", 8),
        ["round", "173: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 173: a worker pulls the next task from the queue", 12),
        ["round 173: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 173: a worker pulls the next task from the queue", 16),
        ["round 173: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 173: a worker pulls the next task from the queue", 24),
        ["round 173: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 173: a worker pulls the next task from the queue", 32),
        ["round 173: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 173: signals travel through the network layer", 4),
        ["round", "173:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 173: signals travel through the network layer", 8),
        ["round", "173:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 173: signals travel through the network layer", 12),
        ["round 173:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 173: signals travel through the network layer", 16),
        ["round 173:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 173: signals travel through the network layer", 24),
        ["round 173: signals", "travel through the", "network layer"],
    ),
    (
        ("round 173: signals travel through the network layer", 32),
        ["round 173: signals travel", "through the network layer"],
    ),
    (
        ("round 173: the gateway routes each request by policy", 4),
        ["round", "173:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 173: the gateway routes each request by policy", 8),
        ["round", "173: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 173: the gateway routes each request by policy", 12),
        ["round 173:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 173: the gateway routes each request by policy", 16),
        ["round 173: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 173: the gateway routes each request by policy", 24),
        ["round 173: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 173: the gateway routes each request by policy", 32),
        ["round 173: the gateway routes", "each request by policy"],
    ),
    (
        ("round 173: memory grows until the buffer is full", 4),
        ["round", "173:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 173: memory grows until the buffer is full", 8),
        ["round", "173:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 173: memory grows until the buffer is full", 12),
        ["round 173:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 173: memory grows until the buffer is full", 16),
        ["round 173:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 173: memory grows until the buffer is full", 24), ["round 173: memory grows", "until the buffer is full"]),
    (("round 173: memory grows until the buffer is full", 32), ["round 173: memory grows until", "the buffer is full"]),
    (
        ("round 173: the cluster mirrors every packet twice", 4),
        ["round", "173:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 173: the cluster mirrors every packet twice", 8),
        ["round", "173: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 173: the cluster mirrors every packet twice", 12),
        ["round 173:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 173: the cluster mirrors every packet twice", 16),
        ["round 173: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 173: the cluster mirrors every packet twice", 24),
        ["round 173: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 173: the cluster mirrors every packet twice", 32),
        ["round 173: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 173: ranking uses tokens learned from the corpus", 4),
        ["round", "173:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 173: ranking uses tokens learned from the corpus", 8),
        ["round", "173:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 173: ranking uses tokens learned from the corpus", 12),
        ["round 173:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 173: ranking uses tokens learned from the corpus", 16),
        ["round 173:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 173: ranking uses tokens learned from the corpus", 24),
        ["round 173: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 173: ranking uses tokens learned from the corpus", 32),
        ["round 173: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 173: a long session ends when the candle dies", 4),
        ["round", "173:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 173: a long session ends when the candle dies", 8),
        ["round", "173: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 173: a long session ends when the candle dies", 12),
        ["round 173: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 173: a long session ends when the candle dies", 16),
        ["round 173: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 173: a long session ends when the candle dies", 24),
        ["round 173: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 173: a long session ends when the candle dies", 32),
        ["round 173: a long session ends", "when the candle dies"],
    ),
    (
        ("round 173: encode the prompt then map the result", 4),
        ["round", "173:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 173: encode the prompt then map the result", 8),
        ["round", "173:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 173: encode the prompt then map the result", 12),
        ["round 173:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 173: encode the prompt then map the result", 16),
        ["round 173:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 173: encode the prompt then map the result", 24),
        ["round 173: encode the", "prompt then map the", "result"],
    ),
    (("round 173: encode the prompt then map the result", 32), ["round 173: encode the prompt", "then map the result"]),
    (
        ("round 173: the kernel wakes the worker at dawn", 4),
        ["round", "173:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 173: the kernel wakes the worker at dawn", 8),
        ["round", "173: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 173: the kernel wakes the worker at dawn", 12),
        ["round 173:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 173: the kernel wakes the worker at dawn", 16), ["round 173: the", "kernel wakes the", "worker at dawn"]),
    (("round 173: the kernel wakes the worker at dawn", 24), ["round 173: the kernel", "wakes the worker at dawn"]),
    (("round 173: the kernel wakes the worker at dawn", 32), ["round 173: the kernel wakes the", "worker at dawn"]),
    (
        ("round 173: service latency drops after the patch", 4),
        ["round", "173:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 173: service latency drops after the patch", 8),
        ["round", "173:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 173: service latency drops after the patch", 12),
        ["round 173:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 173: service latency drops after the patch", 16),
        ["round 173:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 173: service latency drops after the patch", 24),
        ["round 173: service", "latency drops after the", "patch"],
    ),
    (("round 173: service latency drops after the patch", 32), ["round 173: service latency drops", "after the patch"]),
    (
        ("round 173: the library caches every vector it sees", 4),
        ["round", "173:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 173: the library caches every vector it sees", 8),
        ["round", "173: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 173: the library caches every vector it sees", 12),
        ["round 173:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 173: the library caches every vector it sees", 16),
        ["round 173: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 173: the library caches every vector it sees", 24),
        ["round 173: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 173: the library caches every vector it sees", 32),
        ["round 173: the library caches", "every vector it sees"],
    ),
    (
        ("round 173: agents argue then the debate resolves", 4),
        ["round", "173:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 173: agents argue then the debate resolves", 8),
        ["round", "173:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 173: agents argue then the debate resolves", 12),
        ["round 173:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 173: agents argue then the debate resolves", 16),
        ["round 173:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 173: agents argue then the debate resolves", 24), ["round 173: agents argue", "then the debate resolves"]),
    (("round 173: agents argue then the debate resolves", 32), ["round 173: agents argue then the", "debate resolves"]),
    (
        ("round 173: the filter keeps only strong matches", 4),
        ["round", "173:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 173: the filter keeps only strong matches", 8),
        ["round", "173: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 173: the filter keeps only strong matches", 12),
        ["round 173:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 173: the filter keeps only strong matches", 16),
        ["round 173: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 173: the filter keeps only strong matches", 24),
        ["round 173: the filter", "keeps only strong", "matches"],
    ),
    (("round 173: the filter keeps only strong matches", 32), ["round 173: the filter keeps only", "strong matches"]),
    (
        ("round 173: the model answers with a short reply", 4),
        ["round", "173:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 173: the model answers with a short reply", 8),
        ["round", "173: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 173: the model answers with a short reply", 12),
        ["round 173:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 173: the model answers with a short reply", 16),
        ["round 173: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 173: the model answers with a short reply", 24),
        ["round 173: the model", "answers with a short", "reply"],
    ),
    (("round 173: the model answers with a short reply", 32), ["round 173: the model answers", "with a short reply"]),
    (
        ("round 173: the recorder stores the reasoning trace", 4),
        ["round", "173:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 173: the recorder stores the reasoning trace", 8),
        ["round", "173: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 173: the recorder stores the reasoning trace", 12),
        ["round 173:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 173: the recorder stores the reasoning trace", 16),
        ["round 173: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 173: the recorder stores the reasoning trace", 24),
        ["round 173: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 173: the recorder stores the reasoning trace", 32),
        ["round 173: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 173: the angel watches the processor run", 4),
        ["round", "173:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 173: the angel watches the processor run", 8),
        ["round", "173: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 173: the angel watches the processor run", 12),
        ["round 173:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 173: the angel watches the processor run", 16),
        ["round 173: the", "angel watches", "the processor", "run"],
    ),
    (("round 173: the angel watches the processor run", 24), ["round 173: the angel", "watches the processor", "run"]),
    (("round 173: the angel watches the processor run", 32), ["round 173: the angel watches the", "processor run"]),
    (
        ("round 173: angle of the vector decides the match", 4),
        ["round", "173:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 173: angle of the vector decides the match", 8),
        ["round", "173:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 173: angle of the vector decides the match", 12),
        ["round 173:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 173: angle of the vector decides the match", 16),
        ["round 173: angle", "of the vector", "decides the", "match"],
    ),
    (("round 173: angle of the vector decides the match", 24), ["round 173: angle of the", "vector decides the match"]),
    (("round 173: angle of the vector decides the match", 32), ["round 173: angle of the vector", "decides the match"]),
    (
        ("round 173: the candle burns twice as long at night", 4),
        ["round", "173:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 173: the candle burns twice as long at night", 8),
        ["round", "173: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 173: the candle burns twice as long at night", 12),
        ["round 173:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 173: the candle burns twice as long at night", 16),
        ["round 173: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 173: the candle burns twice as long at night", 24),
        ["round 173: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 173: the candle burns twice as long at night", 32),
        ["round 173: the candle burns", "twice as long at night"],
    ),
    (
        ("round 173: a mirror of the universe in one line", 4),
        ["round", "173:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 173: a mirror of the universe in one line", 8),
        ["round", "173: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 173: a mirror of the universe in one line", 12),
        ["round 173: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 173: a mirror of the universe in one line", 16),
        ["round 173: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 173: a mirror of the universe in one line", 24), ["round 173: a mirror of", "the universe in one line"]),
    (("round 173: a mirror of the universe in one line", 32), ["round 173: a mirror of the", "universe in one line"]),
    (
        ("round 173: the queue drains before the storm", 4),
        ["round", "173:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 173: the queue drains before the storm", 8),
        ["round", "173: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 173: the queue drains before the storm", 12),
        ["round 173:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 173: the queue drains before the storm", 16), ["round 173: the", "queue drains", "before the storm"]),
    (("round 173: the queue drains before the storm", 24), ["round 173: the queue", "drains before the storm"]),
    (("round 173: the queue drains before the storm", 32), ["round 173: the queue drains", "before the storm"]),
    (
        ("kitten173 sitting173 agent173 angle173 universe173 memory173", 6),
        ["kitten173", "sitting173", "agent173", "angle173", "universe173", "memory173"],
    ),
    (
        ("kitten173 sitting173 agent173 angle173 universe173 memory173", 10),
        ["kitten173", "sitting173", "agent173", "angle173", "universe173", "memory173"],
    ),
    (
        ("kitten173 sitting173 agent173 angle173 universe173 memory173", 18),
        ["kitten173", "sitting173", "agent173 angle173", "universe173", "memory173"],
    ),
    (
        ("kitten173 sitting173 agent173 angle173 universe173 memory173", 28),
        ["kitten173 sitting173", "agent173 angle173", "universe173 memory173"],
    ),
    (
        ("sitting173 agent173 angle173 universe173 memory173 stream173", 6),
        ["sitting173", "agent173", "angle173", "universe173", "memory173", "stream173"],
    ),
    (
        ("sitting173 agent173 angle173 universe173 memory173 stream173", 10),
        ["sitting173", "agent173", "angle173", "universe173", "memory173", "stream173"],
    ),
    (
        ("sitting173 agent173 angle173 universe173 memory173 stream173", 18),
        ["sitting173", "agent173 angle173", "universe173", "memory173", "stream173"],
    ),
    (
        ("sitting173 agent173 angle173 universe173 memory173 stream173", 28),
        ["sitting173 agent173 angle173", "universe173 memory173", "stream173"],
    ),
    (
        ("agent173 angle173 universe173 memory173 stream173 context173", 6),
        ["agent173", "angle173", "universe173", "memory173", "stream173", "context173"],
    ),
    (
        ("agent173 angle173 universe173 memory173 stream173 context173", 10),
        ["agent173", "angle173", "universe173", "memory173", "stream173", "context173"],
    ),
    (
        ("agent173 angle173 universe173 memory173 stream173 context173", 18),
        ["agent173 angle173", "universe173", "memory173", "stream173", "context173"],
    ),
    (
        ("agent173 angle173 universe173 memory173 stream173 context173", 28),
        ["agent173 angle173", "universe173 memory173", "stream173 context173"],
    ),
    (
        ("angle173 universe173 memory173 stream173 context173 knowledge173", 6),
        ["angle173", "universe173", "memory173", "stream173", "context173", "knowledge173"],
    ),
    (
        ("angle173 universe173 memory173 stream173 context173 knowledge173", 10),
        ["angle173", "universe173", "memory173", "stream173", "context173", "knowledge173"],
    ),
    (
        ("angle173 universe173 memory173 stream173 context173 knowledge173", 18),
        ["angle173", "universe173", "memory173", "stream173", "context173", "knowledge173"],
    ),
    (
        ("angle173 universe173 memory173 stream173 context173 knowledge173", 28),
        ["angle173 universe173", "memory173 stream173", "context173 knowledge173"],
    ),
    (
        ("universe173 memory173 stream173 context173 knowledge173 vector173", 6),
        ["universe173", "memory173", "stream173", "context173", "knowledge173", "vector173"],
    ),
    (
        ("universe173 memory173 stream173 context173 knowledge173 vector173", 10),
        ["universe173", "memory173", "stream173", "context173", "knowledge173", "vector173"],
    ),
    (
        ("universe173 memory173 stream173 context173 knowledge173 vector173", 18),
        ["universe173", "memory173", "stream173", "context173", "knowledge173", "vector173"],
    ),
    (
        ("universe173 memory173 stream173 context173 knowledge173 vector173", 28),
        ["universe173 memory173", "stream173 context173", "knowledge173 vector173"],
    ),
    (
        ("memory173 stream173 context173 knowledge173 vector173 processor173", 6),
        ["memory173", "stream173", "context173", "knowledge173", "vector173", "processor173"],
    ),
    (
        ("memory173 stream173 context173 knowledge173 vector173 processor173", 10),
        ["memory173", "stream173", "context173", "knowledge173", "vector173", "processor173"],
    ),
    (
        ("memory173 stream173 context173 knowledge173 vector173 processor173", 18),
        ["memory173", "stream173", "context173", "knowledge173", "vector173", "processor173"],
    ),
    (
        ("memory173 stream173 context173 knowledge173 vector173 processor173", 28),
        ["memory173 stream173", "context173 knowledge173", "vector173 processor173"],
    ),
    (
        ("stream173 context173 knowledge173 vector173 processor173 reasoning173", 6),
        ["stream173", "context173", "knowledge173", "vector173", "processor173", "reasoning173"],
    ),
    (
        ("stream173 context173 knowledge173 vector173 processor173 reasoning173", 10),
        ["stream173", "context173", "knowledge173", "vector173", "processor173", "reasoning173"],
    ),
    (
        ("stream173 context173 knowledge173 vector173 processor173 reasoning173", 18),
        ["stream173", "context173", "knowledge173", "vector173", "processor173", "reasoning173"],
    ),
    (
        ("stream173 context173 knowledge173 vector173 processor173 reasoning173", 28),
        ["stream173 context173", "knowledge173 vector173", "processor173 reasoning173"],
    ),
    (
        ("context173 knowledge173 vector173 processor173 reasoning173 machine173", 6),
        ["context173", "knowledge173", "vector173", "processor173", "reasoning173", "machine173"],
    ),
    (
        ("context173 knowledge173 vector173 processor173 reasoning173 machine173", 10),
        ["context173", "knowledge173", "vector173", "processor173", "reasoning173", "machine173"],
    ),
    (
        ("context173 knowledge173 vector173 processor173 reasoning173 machine173", 18),
        ["context173", "knowledge173", "vector173", "processor173", "reasoning173", "machine173"],
    ),
    (
        ("context173 knowledge173 vector173 processor173 reasoning173 machine173", 28),
        ["context173 knowledge173", "vector173 processor173", "reasoning173 machine173"],
    ),
    (
        ("knowledge173 vector173 processor173 reasoning173 machine173 learning173", 6),
        ["knowledge173", "vector173", "processor173", "reasoning173", "machine173", "learning173"],
    ),
    (
        ("knowledge173 vector173 processor173 reasoning173 machine173 learning173", 10),
        ["knowledge173", "vector173", "processor173", "reasoning173", "machine173", "learning173"],
    ),
    (
        ("knowledge173 vector173 processor173 reasoning173 machine173 learning173", 18),
        ["knowledge173", "vector173", "processor173", "reasoning173", "machine173", "learning173"],
    ),
    (
        ("knowledge173 vector173 processor173 reasoning173 machine173 learning173", 28),
        ["knowledge173 vector173", "processor173 reasoning173", "machine173 learning173"],
    ),
    (
        ("vector173 processor173 reasoning173 machine173 learning173 model173", 6),
        ["vector173", "processor173", "reasoning173", "machine173", "learning173", "model173"],
    ),
    (
        ("vector173 processor173 reasoning173 machine173 learning173 model173", 10),
        ["vector173", "processor173", "reasoning173", "machine173", "learning173", "model173"],
    ),
    (
        ("vector173 processor173 reasoning173 machine173 learning173 model173", 18),
        ["vector173", "processor173", "reasoning173", "machine173", "learning173", "model173"],
    ),
    (
        ("vector173 processor173 reasoning173 machine173 learning173 model173", 28),
        ["vector173 processor173", "reasoning173 machine173", "learning173 model173"],
    ),
    (
        ("processor173 reasoning173 machine173 learning173 model173 token173", 6),
        ["processor173", "reasoning173", "machine173", "learning173", "model173", "token173"],
    ),
    (
        ("processor173 reasoning173 machine173 learning173 model173 token173", 10),
        ["processor173", "reasoning173", "machine173", "learning173", "model173", "token173"],
    ),
    (
        ("processor173 reasoning173 machine173 learning173 model173 token173", 18),
        ["processor173", "reasoning173", "machine173", "learning173", "model173 token173"],
    ),
    (
        ("processor173 reasoning173 machine173 learning173 model173 token173", 28),
        ["processor173 reasoning173", "machine173 learning173", "model173 token173"],
    ),
    (
        ("reasoning173 machine173 learning173 model173 token173 prompt173", 6),
        ["reasoning173", "machine173", "learning173", "model173", "token173", "prompt173"],
    ),
    (
        ("reasoning173 machine173 learning173 model173 token173 prompt173", 10),
        ["reasoning173", "machine173", "learning173", "model173", "token173", "prompt173"],
    ),
    (
        ("reasoning173 machine173 learning173 model173 token173 prompt173", 18),
        ["reasoning173", "machine173", "learning173", "model173 token173", "prompt173"],
    ),
    (
        ("reasoning173 machine173 learning173 model173 token173 prompt173", 28),
        ["reasoning173 machine173", "learning173 model173", "token173 prompt173"],
    ),
    (
        ("machine173 learning173 model173 token173 prompt173 session173", 6),
        ["machine173", "learning173", "model173", "token173", "prompt173", "session173"],
    ),
    (
        ("machine173 learning173 model173 token173 prompt173 session173", 10),
        ["machine173", "learning173", "model173", "token173", "prompt173", "session173"],
    ),
    (
        ("machine173 learning173 model173 token173 prompt173 session173", 18),
        ["machine173", "learning173", "model173 token173", "prompt173", "session173"],
    ),
    (
        ("machine173 learning173 model173 token173 prompt173 session173", 28),
        ["machine173 learning173", "model173 token173 prompt173", "session173"],
    ),
    (
        ("learning173 model173 token173 prompt173 session173 library173", 6),
        ["learning173", "model173", "token173", "prompt173", "session173", "library173"],
    ),
    (
        ("learning173 model173 token173 prompt173 session173 library173", 10),
        ["learning173", "model173", "token173", "prompt173", "session173", "library173"],
    ),
    (
        ("learning173 model173 token173 prompt173 session173 library173", 18),
        ["learning173", "model173 token173", "prompt173", "session173", "library173"],
    ),
    (
        ("learning173 model173 token173 prompt173 session173 library173", 28),
        ["learning173 model173", "token173 prompt173", "session173 library173"],
    ),
    (
        ("model173 token173 prompt173 session173 library173 service173", 6),
        ["model173", "token173", "prompt173", "session173", "library173", "service173"],
    ),
    (
        ("model173 token173 prompt173 session173 library173 service173", 10),
        ["model173", "token173", "prompt173", "session173", "library173", "service173"],
    ),
    (
        ("model173 token173 prompt173 session173 library173 service173", 18),
        ["model173 token173", "prompt173", "session173", "library173", "service173"],
    ),
    (
        ("model173 token173 prompt173 session173 library173 service173", 28),
        ["model173 token173 prompt173", "session173 library173", "service173"],
    ),
    (
        ("token173 prompt173 session173 library173 service173 gateway173", 6),
        ["token173", "prompt173", "session173", "library173", "service173", "gateway173"],
    ),
    (
        ("token173 prompt173 session173 library173 service173 gateway173", 10),
        ["token173", "prompt173", "session173", "library173", "service173", "gateway173"],
    ),
    (
        ("token173 prompt173 session173 library173 service173 gateway173", 18),
        ["token173 prompt173", "session173", "library173", "service173", "gateway173"],
    ),
    (
        ("token173 prompt173 session173 library173 service173 gateway173", 28),
        ["token173 prompt173", "session173 library173", "service173 gateway173"],
    ),
    (
        ("prompt173 session173 library173 service173 gateway173 storage173", 6),
        ["prompt173", "session173", "library173", "service173", "gateway173", "storage173"],
    ),
    (
        ("prompt173 session173 library173 service173 gateway173 storage173", 10),
        ["prompt173", "session173", "library173", "service173", "gateway173", "storage173"],
    ),
    (
        ("prompt173 session173 library173 service173 gateway173 storage173", 18),
        ["prompt173", "session173", "library173", "service173", "gateway173", "storage173"],
    ),
    (
        ("prompt173 session173 library173 service173 gateway173 storage173", 28),
        ["prompt173 session173", "library173 service173", "gateway173 storage173"],
    ),
    (
        ("session173 library173 service173 gateway173 storage173 network173", 6),
        ["session173", "library173", "service173", "gateway173", "storage173", "network173"],
    ),
    (
        ("session173 library173 service173 gateway173 storage173 network173", 10),
        ["session173", "library173", "service173", "gateway173", "storage173", "network173"],
    ),
    (
        ("session173 library173 service173 gateway173 storage173 network173", 18),
        ["session173", "library173", "service173", "gateway173", "storage173", "network173"],
    ),
    (
        ("session173 library173 service173 gateway173 storage173 network173", 28),
        ["session173 library173", "service173 gateway173", "storage173 network173"],
    ),
    (
        ("library173 service173 gateway173 storage173 network173 latency173", 6),
        ["library173", "service173", "gateway173", "storage173", "network173", "latency173"],
    ),
    (
        ("library173 service173 gateway173 storage173 network173 latency173", 10),
        ["library173", "service173", "gateway173", "storage173", "network173", "latency173"],
    ),
    (
        ("library173 service173 gateway173 storage173 network173 latency173", 18),
        ["library173", "service173", "gateway173", "storage173", "network173", "latency173"],
    ),
    (
        ("library173 service173 gateway173 storage173 network173 latency173", 28),
        ["library173 service173", "gateway173 storage173", "network173 latency173"],
    ),
    (
        ("service173 gateway173 storage173 network173 latency173 buffer173", 6),
        ["service173", "gateway173", "storage173", "network173", "latency173", "buffer173"],
    ),
    (
        ("service173 gateway173 storage173 network173 latency173 buffer173", 10),
        ["service173", "gateway173", "storage173", "network173", "latency173", "buffer173"],
    ),
    (
        ("service173 gateway173 storage173 network173 latency173 buffer173", 18),
        ["service173", "gateway173", "storage173", "network173", "latency173", "buffer173"],
    ),
    (
        ("service173 gateway173 storage173 network173 latency173 buffer173", 28),
        ["service173 gateway173", "storage173 network173", "latency173 buffer173"],
    ),
    (
        ("gateway173 storage173 network173 latency173 buffer173 queue173", 6),
        ["gateway173", "storage173", "network173", "latency173", "buffer173", "queue173"],
    ),
    (
        ("gateway173 storage173 network173 latency173 buffer173 queue173", 10),
        ["gateway173", "storage173", "network173", "latency173", "buffer173", "queue173"],
    ),
    (
        ("gateway173 storage173 network173 latency173 buffer173 queue173", 18),
        ["gateway173", "storage173", "network173", "latency173", "buffer173 queue173"],
    ),
    (
        ("gateway173 storage173 network173 latency173 buffer173 queue173", 28),
        ["gateway173 storage173", "network173 latency173", "buffer173 queue173"],
    ),
    (
        ("storage173 network173 latency173 buffer173 queue173 worker173", 6),
        ["storage173", "network173", "latency173", "buffer173", "queue173", "worker173"],
    ),
    (
        ("storage173 network173 latency173 buffer173 queue173 worker173", 10),
        ["storage173", "network173", "latency173", "buffer173", "queue173", "worker173"],
    ),
    (
        ("storage173 network173 latency173 buffer173 queue173 worker173", 18),
        ["storage173", "network173", "latency173", "buffer173 queue173", "worker173"],
    ),
    (
        ("storage173 network173 latency173 buffer173 queue173 worker173", 28),
        ["storage173 network173", "latency173 buffer173", "queue173 worker173"],
    ),
    (
        ("network173 latency173 buffer173 queue173 worker173 kernel173", 6),
        ["network173", "latency173", "buffer173", "queue173", "worker173", "kernel173"],
    ),
    (
        ("network173 latency173 buffer173 queue173 worker173 kernel173", 10),
        ["network173", "latency173", "buffer173", "queue173", "worker173", "kernel173"],
    ),
    (
        ("network173 latency173 buffer173 queue173 worker173 kernel173", 18),
        ["network173", "latency173", "buffer173 queue173", "worker173", "kernel173"],
    ),
    (
        ("network173 latency173 buffer173 queue173 worker173 kernel173", 28),
        ["network173 latency173", "buffer173 queue173 worker173", "kernel173"],
    ),
    (
        ("latency173 buffer173 queue173 worker173 kernel173 signal173", 6),
        ["latency173", "buffer173", "queue173", "worker173", "kernel173", "signal173"],
    ),
    (
        ("latency173 buffer173 queue173 worker173 kernel173 signal173", 10),
        ["latency173", "buffer173", "queue173", "worker173", "kernel173", "signal173"],
    ),
    (
        ("latency173 buffer173 queue173 worker173 kernel173 signal173", 18),
        ["latency173", "buffer173 queue173", "worker173", "kernel173", "signal173"],
    ),
    (
        ("latency173 buffer173 queue173 worker173 kernel173 signal173", 28),
        ["latency173 buffer173", "queue173 worker173 kernel173", "signal173"],
    ),
    (
        ("buffer173 queue173 worker173 kernel173 signal173 packet173", 6),
        ["buffer173", "queue173", "worker173", "kernel173", "signal173", "packet173"],
    ),
    (
        ("buffer173 queue173 worker173 kernel173 signal173 packet173", 10),
        ["buffer173", "queue173", "worker173", "kernel173", "signal173", "packet173"],
    ),
    (
        ("buffer173 queue173 worker173 kernel173 signal173 packet173", 18),
        ["buffer173 queue173", "worker173", "kernel173", "signal173", "packet173"],
    ),
    (
        ("buffer173 queue173 worker173 kernel173 signal173 packet173", 28),
        ["buffer173 queue173 worker173", "kernel173 signal173", "packet173"],
    ),
    (
        ("queue173 worker173 kernel173 signal173 packet173 router173", 6),
        ["queue173", "worker173", "kernel173", "signal173", "packet173", "router173"],
    ),
    (
        ("queue173 worker173 kernel173 signal173 packet173 router173", 10),
        ["queue173", "worker173", "kernel173", "signal173", "packet173", "router173"],
    ),
    (
        ("queue173 worker173 kernel173 signal173 packet173 router173", 18),
        ["queue173 worker173", "kernel173", "signal173", "packet173", "router173"],
    ),
    (
        ("queue173 worker173 kernel173 signal173 packet173 router173", 28),
        ["queue173 worker173 kernel173", "signal173 packet173", "router173"],
    ),
    (
        ("worker173 kernel173 signal173 packet173 router173 cluster173", 6),
        ["worker173", "kernel173", "signal173", "packet173", "router173", "cluster173"],
    ),
    (
        ("worker173 kernel173 signal173 packet173 router173 cluster173", 10),
        ["worker173", "kernel173", "signal173", "packet173", "router173", "cluster173"],
    ),
    (
        ("worker173 kernel173 signal173 packet173 router173 cluster173", 18),
        ["worker173", "kernel173", "signal173", "packet173", "router173", "cluster173"],
    ),
    (
        ("worker173 kernel173 signal173 packet173 router173 cluster173", 28),
        ["worker173 kernel173", "signal173 packet173", "router173 cluster173"],
    ),
    (
        ("kernel173 signal173 packet173 router173 cluster173 mirror173", 6),
        ["kernel173", "signal173", "packet173", "router173", "cluster173", "mirror173"],
    ),
    (
        ("kernel173 signal173 packet173 router173 cluster173 mirror173", 10),
        ["kernel173", "signal173", "packet173", "router173", "cluster173", "mirror173"],
    ),
    (
        ("kernel173 signal173 packet173 router173 cluster173 mirror173", 18),
        ["kernel173", "signal173", "packet173", "router173", "cluster173", "mirror173"],
    ),
    (
        ("kernel173 signal173 packet173 router173 cluster173 mirror173", 28),
        ["kernel173 signal173", "packet173 router173", "cluster173 mirror173"],
    ),
    (
        ("signal173 packet173 router173 cluster173 mirror173 filter173", 6),
        ["signal173", "packet173", "router173", "cluster173", "mirror173", "filter173"],
    ),
    (
        ("signal173 packet173 router173 cluster173 mirror173 filter173", 10),
        ["signal173", "packet173", "router173", "cluster173", "mirror173", "filter173"],
    ),
    (
        ("signal173 packet173 router173 cluster173 mirror173 filter173", 18),
        ["signal173", "packet173", "router173", "cluster173", "mirror173", "filter173"],
    ),
    (
        ("signal173 packet173 router173 cluster173 mirror173 filter173", 28),
        ["signal173 packet173", "router173 cluster173", "mirror173 filter173"],
    ),
    (
        ("packet173 router173 cluster173 mirror173 filter173 ranking173", 6),
        ["packet173", "router173", "cluster173", "mirror173", "filter173", "ranking173"],
    ),
    (
        ("packet173 router173 cluster173 mirror173 filter173 ranking173", 10),
        ["packet173", "router173", "cluster173", "mirror173", "filter173", "ranking173"],
    ),
    (
        ("packet173 router173 cluster173 mirror173 filter173 ranking173", 18),
        ["packet173", "router173", "cluster173", "mirror173", "filter173", "ranking173"],
    ),
    (
        ("packet173 router173 cluster173 mirror173 filter173 ranking173", 28),
        ["packet173 router173", "cluster173 mirror173", "filter173 ranking173"],
    ),
    (
        ("router173 cluster173 mirror173 filter173 ranking173 encoding173", 6),
        ["router173", "cluster173", "mirror173", "filter173", "ranking173", "encoding173"],
    ),
    (
        ("router173 cluster173 mirror173 filter173 ranking173 encoding173", 10),
        ["router173", "cluster173", "mirror173", "filter173", "ranking173", "encoding173"],
    ),
    (
        ("router173 cluster173 mirror173 filter173 ranking173 encoding173", 18),
        ["router173", "cluster173", "mirror173", "filter173", "ranking173", "encoding173"],
    ),
    (
        ("router173 cluster173 mirror173 filter173 ranking173 encoding173", 28),
        ["router173 cluster173", "mirror173 filter173", "ranking173 encoding173"],
    ),
    (
        ("cluster173 mirror173 filter173 ranking173 encoding173 mapping173", 6),
        ["cluster173", "mirror173", "filter173", "ranking173", "encoding173", "mapping173"],
    ),
    (
        ("cluster173 mirror173 filter173 ranking173 encoding173 mapping173", 10),
        ["cluster173", "mirror173", "filter173", "ranking173", "encoding173", "mapping173"],
    ),
    (
        ("cluster173 mirror173 filter173 ranking173 encoding173 mapping173", 18),
        ["cluster173", "mirror173", "filter173", "ranking173", "encoding173", "mapping173"],
    ),
    (
        ("cluster173 mirror173 filter173 ranking173 encoding173 mapping173", 28),
        ["cluster173 mirror173", "filter173 ranking173", "encoding173 mapping173"],
    ),
    (
        ("mirror173 filter173 ranking173 encoding173 mapping173 record173", 6),
        ["mirror173", "filter173", "ranking173", "encoding173", "mapping173", "record173"],
    ),
    (
        ("mirror173 filter173 ranking173 encoding173 mapping173 record173", 10),
        ["mirror173", "filter173", "ranking173", "encoding173", "mapping173", "record173"],
    ),
    (
        ("mirror173 filter173 ranking173 encoding173 mapping173 record173", 18),
        ["mirror173", "filter173", "ranking173", "encoding173", "mapping173", "record173"],
    ),
    (
        ("mirror173 filter173 ranking173 encoding173 mapping173 record173", 28),
        ["mirror173 filter173", "ranking173 encoding173", "mapping173 record173"],
    ),
    (
        ("filter173 ranking173 encoding173 mapping173 record173 candle173", 6),
        ["filter173", "ranking173", "encoding173", "mapping173", "record173", "candle173"],
    ),
    (
        ("filter173 ranking173 encoding173 mapping173 record173 candle173", 10),
        ["filter173", "ranking173", "encoding173", "mapping173", "record173", "candle173"],
    ),
    (
        ("filter173 ranking173 encoding173 mapping173 record173 candle173", 18),
        ["filter173", "ranking173", "encoding173", "mapping173", "record173", "candle173"],
    ),
    (
        ("filter173 ranking173 encoding173 mapping173 record173 candle173", 28),
        ["filter173 ranking173", "encoding173 mapping173", "record173 candle173"],
    ),
    (
        ("ranking173 encoding173 mapping173 record173 candle173 thread173", 6),
        ["ranking173", "encoding173", "mapping173", "record173", "candle173", "thread173"],
    ),
    (
        ("ranking173 encoding173 mapping173 record173 candle173 thread173", 10),
        ["ranking173", "encoding173", "mapping173", "record173", "candle173", "thread173"],
    ),
    (
        ("ranking173 encoding173 mapping173 record173 candle173 thread173", 18),
        ["ranking173", "encoding173", "mapping173", "record173", "candle173", "thread173"],
    ),
    (
        ("ranking173 encoding173 mapping173 record173 candle173 thread173", 28),
        ["ranking173 encoding173", "mapping173 record173", "candle173 thread173"],
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
