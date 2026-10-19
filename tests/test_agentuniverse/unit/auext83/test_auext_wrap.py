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
        ("round 83: the quick brown fox jumps over the lazy dog", 4),
        ["round", "83:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 83: the quick brown fox jumps over the lazy dog", 8),
        ["round", "83: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 83: the quick brown fox jumps over the lazy dog", 12),
        ["round 83:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 83: the quick brown fox jumps over the lazy dog", 16),
        ["round 83: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 83: the quick brown fox jumps over the lazy dog", 24),
        ["round 83: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 83: the quick brown fox jumps over the lazy dog", 32),
        ["round 83: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 83: agentuniverse is a framework for multi agents", 4),
        ["round", "83:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 83: agentuniverse is a framework for multi agents", 8),
        ["round", "83:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 83: agentuniverse is a framework for multi agents", 12),
        ["round 83:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 83: agentuniverse is a framework for multi agents", 16),
        ["round 83:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 83: agentuniverse is a framework for multi agents", 24),
        ["round 83: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 83: agentuniverse is a framework for multi agents", 32),
        ["round 83: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 83: knowledge stored as vectors enables retrieval", 4),
        ["round", "83:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 83: knowledge stored as vectors enables retrieval", 8),
        ["round", "83:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 83: knowledge stored as vectors enables retrieval", 12),
        ["round 83:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 83: knowledge stored as vectors enables retrieval", 16),
        ["round 83:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 83: knowledge stored as vectors enables retrieval", 24),
        ["round 83: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 83: knowledge stored as vectors enables retrieval", 32),
        ["round 83: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 83: the processor reads the record then stops", 4),
        ["round", "83:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 83: the processor reads the record then stops", 8),
        ["round", "83: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 83: the processor reads the record then stops", 12),
        ["round 83:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 83: the processor reads the record then stops", 16),
        ["round 83: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 83: the processor reads the record then stops", 24),
        ["round 83: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 83: the processor reads the record then stops", 32),
        ["round 83: the processor reads", "the record then stops"],
    ),
    (
        ("round 83: a worker pulls the next task from the queue", 4),
        ["round", "83:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 83: a worker pulls the next task from the queue", 8),
        ["round", "83: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 83: a worker pulls the next task from the queue", 12),
        ["round 83: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 83: a worker pulls the next task from the queue", 16),
        ["round 83: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 83: a worker pulls the next task from the queue", 24),
        ["round 83: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 83: a worker pulls the next task from the queue", 32),
        ["round 83: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 83: signals travel through the network layer", 4),
        ["round", "83:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 83: signals travel through the network layer", 8),
        ["round", "83:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 83: signals travel through the network layer", 12),
        ["round 83:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 83: signals travel through the network layer", 16),
        ["round 83:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 83: signals travel through the network layer", 24),
        ["round 83: signals travel", "through the network", "layer"],
    ),
    (
        ("round 83: signals travel through the network layer", 32),
        ["round 83: signals travel through", "the network layer"],
    ),
    (
        ("round 83: the gateway routes each request by policy", 4),
        ["round", "83:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 83: the gateway routes each request by policy", 8),
        ["round", "83: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 83: the gateway routes each request by policy", 12),
        ["round 83:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 83: the gateway routes each request by policy", 16),
        ["round 83: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 83: the gateway routes each request by policy", 24),
        ["round 83: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 83: the gateway routes each request by policy", 32),
        ["round 83: the gateway routes", "each request by policy"],
    ),
    (
        ("round 83: memory grows until the buffer is full", 4),
        ["round", "83:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 83: memory grows until the buffer is full", 8),
        ["round", "83:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 83: memory grows until the buffer is full", 12),
        ["round 83:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 83: memory grows until the buffer is full", 16),
        ["round 83: memory", "grows until the", "buffer is full"],
    ),
    (("round 83: memory grows until the buffer is full", 24), ["round 83: memory grows", "until the buffer is full"]),
    (("round 83: memory grows until the buffer is full", 32), ["round 83: memory grows until the", "buffer is full"]),
    (
        ("round 83: the cluster mirrors every packet twice", 4),
        ["round", "83:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 83: the cluster mirrors every packet twice", 8),
        ["round", "83: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 83: the cluster mirrors every packet twice", 12),
        ["round 83:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 83: the cluster mirrors every packet twice", 16),
        ["round 83: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 83: the cluster mirrors every packet twice", 24),
        ["round 83: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 83: the cluster mirrors every packet twice", 32), ["round 83: the cluster mirrors", "every packet twice"]),
    (
        ("round 83: ranking uses tokens learned from the corpus", 4),
        ["round", "83:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 83: ranking uses tokens learned from the corpus", 8),
        ["round", "83:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 83: ranking uses tokens learned from the corpus", 12),
        ["round 83:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 83: ranking uses tokens learned from the corpus", 16),
        ["round 83:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 83: ranking uses tokens learned from the corpus", 24),
        ["round 83: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 83: ranking uses tokens learned from the corpus", 32),
        ["round 83: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 83: a long session ends when the candle dies", 4),
        ["round", "83:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 83: a long session ends when the candle dies", 8),
        ["round", "83: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 83: a long session ends when the candle dies", 12),
        ["round 83: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 83: a long session ends when the candle dies", 16),
        ["round 83: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 83: a long session ends when the candle dies", 24),
        ["round 83: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 83: a long session ends when the candle dies", 32),
        ["round 83: a long session ends", "when the candle dies"],
    ),
    (
        ("round 83: encode the prompt then map the result", 4),
        ["round", "83:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 83: encode the prompt then map the result", 8),
        ["round", "83:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 83: encode the prompt then map the result", 12),
        ["round 83:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 83: encode the prompt then map the result", 16),
        ["round 83: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 83: encode the prompt then map the result", 24),
        ["round 83: encode the", "prompt then map the", "result"],
    ),
    (("round 83: encode the prompt then map the result", 32), ["round 83: encode the prompt then", "map the result"]),
    (
        ("round 83: the kernel wakes the worker at dawn", 4),
        ["round", "83:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 83: the kernel wakes the worker at dawn", 8),
        ["round", "83: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 83: the kernel wakes the worker at dawn", 12),
        ["round 83:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 83: the kernel wakes the worker at dawn", 16), ["round 83: the", "kernel wakes the", "worker at dawn"]),
    (("round 83: the kernel wakes the worker at dawn", 24), ["round 83: the kernel", "wakes the worker at dawn"]),
    (("round 83: the kernel wakes the worker at dawn", 32), ["round 83: the kernel wakes the", "worker at dawn"]),
    (
        ("round 83: service latency drops after the patch", 4),
        ["round", "83:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 83: service latency drops after the patch", 8),
        ["round", "83:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 83: service latency drops after the patch", 12),
        ["round 83:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 83: service latency drops after the patch", 16),
        ["round 83:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 83: service latency drops after the patch", 24),
        ["round 83: service", "latency drops after the", "patch"],
    ),
    (("round 83: service latency drops after the patch", 32), ["round 83: service latency drops", "after the patch"]),
    (
        ("round 83: the library caches every vector it sees", 4),
        ["round", "83:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 83: the library caches every vector it sees", 8),
        ["round", "83: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 83: the library caches every vector it sees", 12),
        ["round 83:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 83: the library caches every vector it sees", 16),
        ["round 83: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 83: the library caches every vector it sees", 24),
        ["round 83: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 83: the library caches every vector it sees", 32),
        ["round 83: the library caches", "every vector it sees"],
    ),
    (
        ("round 83: agents argue then the debate resolves", 4),
        ["round", "83:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 83: agents argue then the debate resolves", 8),
        ["round", "83:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 83: agents argue then the debate resolves", 12),
        ["round 83:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 83: agents argue then the debate resolves", 16),
        ["round 83: agents", "argue then the", "debate resolves"],
    ),
    (("round 83: agents argue then the debate resolves", 24), ["round 83: agents argue", "then the debate resolves"]),
    (("round 83: agents argue then the debate resolves", 32), ["round 83: agents argue then the", "debate resolves"]),
    (
        ("round 83: the filter keeps only strong matches", 4),
        ["round", "83:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 83: the filter keeps only strong matches", 8),
        ["round", "83: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 83: the filter keeps only strong matches", 12),
        ["round 83:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 83: the filter keeps only strong matches", 16),
        ["round 83: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 83: the filter keeps only strong matches", 24), ["round 83: the filter", "keeps only strong", "matches"]),
    (("round 83: the filter keeps only strong matches", 32), ["round 83: the filter keeps only", "strong matches"]),
    (
        ("round 83: the model answers with a short reply", 4),
        ["round", "83:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 83: the model answers with a short reply", 8),
        ["round", "83: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 83: the model answers with a short reply", 12),
        ["round 83:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 83: the model answers with a short reply", 16),
        ["round 83: the", "model answers", "with a short", "reply"],
    ),
    (("round 83: the model answers with a short reply", 24), ["round 83: the model", "answers with a short", "reply"]),
    (("round 83: the model answers with a short reply", 32), ["round 83: the model answers with", "a short reply"]),
    (
        ("round 83: the recorder stores the reasoning trace", 4),
        ["round", "83:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 83: the recorder stores the reasoning trace", 8),
        ["round", "83: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 83: the recorder stores the reasoning trace", 12),
        ["round 83:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 83: the recorder stores the reasoning trace", 16),
        ["round 83: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 83: the recorder stores the reasoning trace", 24),
        ["round 83: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 83: the recorder stores the reasoning trace", 32),
        ["round 83: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 83: the angel watches the processor run", 4),
        ["round", "83:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 83: the angel watches the processor run", 8),
        ["round", "83: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 83: the angel watches the processor run", 12),
        ["round 83:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 83: the angel watches the processor run", 16), ["round 83: the", "angel watches", "the processor", "run"]),
    (("round 83: the angel watches the processor run", 24), ["round 83: the angel", "watches the processor", "run"]),
    (("round 83: the angel watches the processor run", 32), ["round 83: the angel watches the", "processor run"]),
    (
        ("round 83: angle of the vector decides the match", 4),
        ["round", "83:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 83: angle of the vector decides the match", 8),
        ["round", "83:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 83: angle of the vector decides the match", 12),
        ["round 83:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 83: angle of the vector decides the match", 16),
        ["round 83: angle", "of the vector", "decides the", "match"],
    ),
    (("round 83: angle of the vector decides the match", 24), ["round 83: angle of the", "vector decides the match"]),
    (("round 83: angle of the vector decides the match", 32), ["round 83: angle of the vector", "decides the match"]),
    (
        ("round 83: the candle burns twice as long at night", 4),
        ["round", "83:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 83: the candle burns twice as long at night", 8),
        ["round", "83: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 83: the candle burns twice as long at night", 12),
        ["round 83:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 83: the candle burns twice as long at night", 16),
        ["round 83: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 83: the candle burns twice as long at night", 24),
        ["round 83: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 83: the candle burns twice as long at night", 32),
        ["round 83: the candle burns twice", "as long at night"],
    ),
    (
        ("round 83: a mirror of the universe in one line", 4),
        ["round", "83:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 83: a mirror of the universe in one line", 8),
        ["round", "83: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 83: a mirror of the universe in one line", 12),
        ["round 83: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 83: a mirror of the universe in one line", 16),
        ["round 83: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 83: a mirror of the universe in one line", 24), ["round 83: a mirror of", "the universe in one line"]),
    (("round 83: a mirror of the universe in one line", 32), ["round 83: a mirror of the", "universe in one line"]),
    (
        ("round 83: the queue drains before the storm", 4),
        ["round", "83:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 83: the queue drains before the storm", 8),
        ["round", "83: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 83: the queue drains before the storm", 12), ["round 83:", "the queue", "drains", "before the", "storm"]),
    (("round 83: the queue drains before the storm", 16), ["round 83: the", "queue drains", "before the storm"]),
    (("round 83: the queue drains before the storm", 24), ["round 83: the queue", "drains before the storm"]),
    (("round 83: the queue drains before the storm", 32), ["round 83: the queue drains", "before the storm"]),
    (
        ("kitten83 sitting83 agent83 angle83 universe83 memory83", 6),
        ["kitten83", "sitting83", "agent83", "angle83", "universe83", "memory83"],
    ),
    (
        ("kitten83 sitting83 agent83 angle83 universe83 memory83", 10),
        ["kitten83", "sitting83", "agent83", "angle83", "universe83", "memory83"],
    ),
    (
        ("kitten83 sitting83 agent83 angle83 universe83 memory83", 18),
        ["kitten83 sitting83", "agent83 angle83", "universe83", "memory83"],
    ),
    (
        ("kitten83 sitting83 agent83 angle83 universe83 memory83", 28),
        ["kitten83 sitting83 agent83", "angle83 universe83 memory83"],
    ),
    (
        ("sitting83 agent83 angle83 universe83 memory83 stream83", 6),
        ["sitting83", "agent83", "angle83", "universe83", "memory83", "stream83"],
    ),
    (
        ("sitting83 agent83 angle83 universe83 memory83 stream83", 10),
        ["sitting83", "agent83", "angle83", "universe83", "memory83", "stream83"],
    ),
    (
        ("sitting83 agent83 angle83 universe83 memory83 stream83", 18),
        ["sitting83 agent83", "angle83 universe83", "memory83 stream83"],
    ),
    (
        ("sitting83 agent83 angle83 universe83 memory83 stream83", 28),
        ["sitting83 agent83 angle83", "universe83 memory83 stream83"],
    ),
    (
        ("agent83 angle83 universe83 memory83 stream83 context83", 6),
        ["agent83", "angle83", "universe83", "memory83", "stream83", "context83"],
    ),
    (
        ("agent83 angle83 universe83 memory83 stream83 context83", 10),
        ["agent83", "angle83", "universe83", "memory83", "stream83", "context83"],
    ),
    (
        ("agent83 angle83 universe83 memory83 stream83 context83", 18),
        ["agent83 angle83", "universe83", "memory83 stream83", "context83"],
    ),
    (
        ("agent83 angle83 universe83 memory83 stream83 context83", 28),
        ["agent83 angle83 universe83", "memory83 stream83 context83"],
    ),
    (
        ("angle83 universe83 memory83 stream83 context83 knowledge83", 6),
        ["angle83", "universe83", "memory83", "stream83", "context83", "knowledge83"],
    ),
    (
        ("angle83 universe83 memory83 stream83 context83 knowledge83", 10),
        ["angle83", "universe83", "memory83", "stream83", "context83", "knowledge83"],
    ),
    (
        ("angle83 universe83 memory83 stream83 context83 knowledge83", 18),
        ["angle83 universe83", "memory83 stream83", "context83", "knowledge83"],
    ),
    (
        ("angle83 universe83 memory83 stream83 context83 knowledge83", 28),
        ["angle83 universe83 memory83", "stream83 context83", "knowledge83"],
    ),
    (
        ("universe83 memory83 stream83 context83 knowledge83 vector83", 6),
        ["universe83", "memory83", "stream83", "context83", "knowledge83", "vector83"],
    ),
    (
        ("universe83 memory83 stream83 context83 knowledge83 vector83", 10),
        ["universe83", "memory83", "stream83", "context83", "knowledge83", "vector83"],
    ),
    (
        ("universe83 memory83 stream83 context83 knowledge83 vector83", 18),
        ["universe83", "memory83 stream83", "context83", "knowledge83", "vector83"],
    ),
    (
        ("universe83 memory83 stream83 context83 knowledge83 vector83", 28),
        ["universe83 memory83 stream83", "context83 knowledge83", "vector83"],
    ),
    (
        ("memory83 stream83 context83 knowledge83 vector83 processor83", 6),
        ["memory83", "stream83", "context83", "knowledge83", "vector83", "processor83"],
    ),
    (
        ("memory83 stream83 context83 knowledge83 vector83 processor83", 10),
        ["memory83", "stream83", "context83", "knowledge83", "vector83", "processor83"],
    ),
    (
        ("memory83 stream83 context83 knowledge83 vector83 processor83", 18),
        ["memory83 stream83", "context83", "knowledge83", "vector83", "processor83"],
    ),
    (
        ("memory83 stream83 context83 knowledge83 vector83 processor83", 28),
        ["memory83 stream83 context83", "knowledge83 vector83", "processor83"],
    ),
    (
        ("stream83 context83 knowledge83 vector83 processor83 reasoning83", 6),
        ["stream83", "context83", "knowledge83", "vector83", "processor83", "reasoning83"],
    ),
    (
        ("stream83 context83 knowledge83 vector83 processor83 reasoning83", 10),
        ["stream83", "context83", "knowledge83", "vector83", "processor83", "reasoning83"],
    ),
    (
        ("stream83 context83 knowledge83 vector83 processor83 reasoning83", 18),
        ["stream83 context83", "knowledge83", "vector83", "processor83", "reasoning83"],
    ),
    (
        ("stream83 context83 knowledge83 vector83 processor83 reasoning83", 28),
        ["stream83 context83", "knowledge83 vector83", "processor83 reasoning83"],
    ),
    (
        ("context83 knowledge83 vector83 processor83 reasoning83 machine83", 6),
        ["context83", "knowledge83", "vector83", "processor83", "reasoning83", "machine83"],
    ),
    (
        ("context83 knowledge83 vector83 processor83 reasoning83 machine83", 10),
        ["context83", "knowledge83", "vector83", "processor83", "reasoning83", "machine83"],
    ),
    (
        ("context83 knowledge83 vector83 processor83 reasoning83 machine83", 18),
        ["context83", "knowledge83", "vector83", "processor83", "reasoning83", "machine83"],
    ),
    (
        ("context83 knowledge83 vector83 processor83 reasoning83 machine83", 28),
        ["context83 knowledge83", "vector83 processor83", "reasoning83 machine83"],
    ),
    (
        ("knowledge83 vector83 processor83 reasoning83 machine83 learning83", 6),
        ["knowledge83", "vector83", "processor83", "reasoning83", "machine83", "learning83"],
    ),
    (
        ("knowledge83 vector83 processor83 reasoning83 machine83 learning83", 10),
        ["knowledge83", "vector83", "processor83", "reasoning83", "machine83", "learning83"],
    ),
    (
        ("knowledge83 vector83 processor83 reasoning83 machine83 learning83", 18),
        ["knowledge83", "vector83", "processor83", "reasoning83", "machine83", "learning83"],
    ),
    (
        ("knowledge83 vector83 processor83 reasoning83 machine83 learning83", 28),
        ["knowledge83 vector83", "processor83 reasoning83", "machine83 learning83"],
    ),
    (
        ("vector83 processor83 reasoning83 machine83 learning83 model83", 6),
        ["vector83", "processor83", "reasoning83", "machine83", "learning83", "model83"],
    ),
    (
        ("vector83 processor83 reasoning83 machine83 learning83 model83", 10),
        ["vector83", "processor83", "reasoning83", "machine83", "learning83", "model83"],
    ),
    (
        ("vector83 processor83 reasoning83 machine83 learning83 model83", 18),
        ["vector83", "processor83", "reasoning83", "machine83", "learning83 model83"],
    ),
    (
        ("vector83 processor83 reasoning83 machine83 learning83 model83", 28),
        ["vector83 processor83", "reasoning83 machine83", "learning83 model83"],
    ),
    (
        ("processor83 reasoning83 machine83 learning83 model83 token83", 6),
        ["processor83", "reasoning83", "machine83", "learning83", "model83", "token83"],
    ),
    (
        ("processor83 reasoning83 machine83 learning83 model83 token83", 10),
        ["processor83", "reasoning83", "machine83", "learning83", "model83", "token83"],
    ),
    (
        ("processor83 reasoning83 machine83 learning83 model83 token83", 18),
        ["processor83", "reasoning83", "machine83", "learning83 model83", "token83"],
    ),
    (
        ("processor83 reasoning83 machine83 learning83 model83 token83", 28),
        ["processor83 reasoning83", "machine83 learning83 model83", "token83"],
    ),
    (
        ("reasoning83 machine83 learning83 model83 token83 prompt83", 6),
        ["reasoning83", "machine83", "learning83", "model83", "token83", "prompt83"],
    ),
    (
        ("reasoning83 machine83 learning83 model83 token83 prompt83", 10),
        ["reasoning83", "machine83", "learning83", "model83", "token83", "prompt83"],
    ),
    (
        ("reasoning83 machine83 learning83 model83 token83 prompt83", 18),
        ["reasoning83", "machine83", "learning83 model83", "token83 prompt83"],
    ),
    (
        ("reasoning83 machine83 learning83 model83 token83 prompt83", 28),
        ["reasoning83 machine83", "learning83 model83 token83", "prompt83"],
    ),
    (
        ("machine83 learning83 model83 token83 prompt83 session83", 6),
        ["machine83", "learning83", "model83", "token83", "prompt83", "session83"],
    ),
    (
        ("machine83 learning83 model83 token83 prompt83 session83", 10),
        ["machine83", "learning83", "model83", "token83", "prompt83", "session83"],
    ),
    (
        ("machine83 learning83 model83 token83 prompt83 session83", 18),
        ["machine83", "learning83 model83", "token83 prompt83", "session83"],
    ),
    (
        ("machine83 learning83 model83 token83 prompt83 session83", 28),
        ["machine83 learning83 model83", "token83 prompt83 session83"],
    ),
    (
        ("learning83 model83 token83 prompt83 session83 library83", 6),
        ["learning83", "model83", "token83", "prompt83", "session83", "library83"],
    ),
    (
        ("learning83 model83 token83 prompt83 session83 library83", 10),
        ["learning83", "model83", "token83", "prompt83", "session83", "library83"],
    ),
    (
        ("learning83 model83 token83 prompt83 session83 library83", 18),
        ["learning83 model83", "token83 prompt83", "session83", "library83"],
    ),
    (
        ("learning83 model83 token83 prompt83 session83 library83", 28),
        ["learning83 model83 token83", "prompt83 session83 library83"],
    ),
    (
        ("model83 token83 prompt83 session83 library83 service83", 6),
        ["model83", "token83", "prompt83", "session83", "library83", "service83"],
    ),
    (
        ("model83 token83 prompt83 session83 library83 service83", 10),
        ["model83", "token83", "prompt83", "session83", "library83", "service83"],
    ),
    (
        ("model83 token83 prompt83 session83 library83 service83", 18),
        ["model83 token83", "prompt83 session83", "library83", "service83"],
    ),
    (
        ("model83 token83 prompt83 session83 library83 service83", 28),
        ["model83 token83 prompt83", "session83 library83", "service83"],
    ),
    (
        ("token83 prompt83 session83 library83 service83 gateway83", 6),
        ["token83", "prompt83", "session83", "library83", "service83", "gateway83"],
    ),
    (
        ("token83 prompt83 session83 library83 service83 gateway83", 10),
        ["token83", "prompt83", "session83", "library83", "service83", "gateway83"],
    ),
    (
        ("token83 prompt83 session83 library83 service83 gateway83", 18),
        ["token83 prompt83", "session83", "library83", "service83", "gateway83"],
    ),
    (
        ("token83 prompt83 session83 library83 service83 gateway83", 28),
        ["token83 prompt83 session83", "library83 service83", "gateway83"],
    ),
    (
        ("prompt83 session83 library83 service83 gateway83 storage83", 6),
        ["prompt83", "session83", "library83", "service83", "gateway83", "storage83"],
    ),
    (
        ("prompt83 session83 library83 service83 gateway83 storage83", 10),
        ["prompt83", "session83", "library83", "service83", "gateway83", "storage83"],
    ),
    (
        ("prompt83 session83 library83 service83 gateway83 storage83", 18),
        ["prompt83 session83", "library83", "service83", "gateway83", "storage83"],
    ),
    (
        ("prompt83 session83 library83 service83 gateway83 storage83", 28),
        ["prompt83 session83 library83", "service83 gateway83", "storage83"],
    ),
    (
        ("session83 library83 service83 gateway83 storage83 network83", 6),
        ["session83", "library83", "service83", "gateway83", "storage83", "network83"],
    ),
    (
        ("session83 library83 service83 gateway83 storage83 network83", 10),
        ["session83", "library83", "service83", "gateway83", "storage83", "network83"],
    ),
    (
        ("session83 library83 service83 gateway83 storage83 network83", 18),
        ["session83", "library83", "service83", "gateway83", "storage83", "network83"],
    ),
    (
        ("session83 library83 service83 gateway83 storage83 network83", 28),
        ["session83 library83", "service83 gateway83", "storage83 network83"],
    ),
    (
        ("library83 service83 gateway83 storage83 network83 latency83", 6),
        ["library83", "service83", "gateway83", "storage83", "network83", "latency83"],
    ),
    (
        ("library83 service83 gateway83 storage83 network83 latency83", 10),
        ["library83", "service83", "gateway83", "storage83", "network83", "latency83"],
    ),
    (
        ("library83 service83 gateway83 storage83 network83 latency83", 18),
        ["library83", "service83", "gateway83", "storage83", "network83", "latency83"],
    ),
    (
        ("library83 service83 gateway83 storage83 network83 latency83", 28),
        ["library83 service83", "gateway83 storage83", "network83 latency83"],
    ),
    (
        ("service83 gateway83 storage83 network83 latency83 buffer83", 6),
        ["service83", "gateway83", "storage83", "network83", "latency83", "buffer83"],
    ),
    (
        ("service83 gateway83 storage83 network83 latency83 buffer83", 10),
        ["service83", "gateway83", "storage83", "network83", "latency83", "buffer83"],
    ),
    (
        ("service83 gateway83 storage83 network83 latency83 buffer83", 18),
        ["service83", "gateway83", "storage83", "network83", "latency83 buffer83"],
    ),
    (
        ("service83 gateway83 storage83 network83 latency83 buffer83", 28),
        ["service83 gateway83", "storage83 network83", "latency83 buffer83"],
    ),
    (
        ("gateway83 storage83 network83 latency83 buffer83 queue83", 6),
        ["gateway83", "storage83", "network83", "latency83", "buffer83", "queue83"],
    ),
    (
        ("gateway83 storage83 network83 latency83 buffer83 queue83", 10),
        ["gateway83", "storage83", "network83", "latency83", "buffer83", "queue83"],
    ),
    (
        ("gateway83 storage83 network83 latency83 buffer83 queue83", 18),
        ["gateway83", "storage83", "network83", "latency83 buffer83", "queue83"],
    ),
    (
        ("gateway83 storage83 network83 latency83 buffer83 queue83", 28),
        ["gateway83 storage83", "network83 latency83 buffer83", "queue83"],
    ),
    (
        ("storage83 network83 latency83 buffer83 queue83 worker83", 6),
        ["storage83", "network83", "latency83", "buffer83", "queue83", "worker83"],
    ),
    (
        ("storage83 network83 latency83 buffer83 queue83 worker83", 10),
        ["storage83", "network83", "latency83", "buffer83", "queue83", "worker83"],
    ),
    (
        ("storage83 network83 latency83 buffer83 queue83 worker83", 18),
        ["storage83", "network83", "latency83 buffer83", "queue83 worker83"],
    ),
    (
        ("storage83 network83 latency83 buffer83 queue83 worker83", 28),
        ["storage83 network83", "latency83 buffer83 queue83", "worker83"],
    ),
    (
        ("network83 latency83 buffer83 queue83 worker83 kernel83", 6),
        ["network83", "latency83", "buffer83", "queue83", "worker83", "kernel83"],
    ),
    (
        ("network83 latency83 buffer83 queue83 worker83 kernel83", 10),
        ["network83", "latency83", "buffer83", "queue83", "worker83", "kernel83"],
    ),
    (
        ("network83 latency83 buffer83 queue83 worker83 kernel83", 18),
        ["network83", "latency83 buffer83", "queue83 worker83", "kernel83"],
    ),
    (
        ("network83 latency83 buffer83 queue83 worker83 kernel83", 28),
        ["network83 latency83 buffer83", "queue83 worker83 kernel83"],
    ),
    (
        ("latency83 buffer83 queue83 worker83 kernel83 signal83", 6),
        ["latency83", "buffer83", "queue83", "worker83", "kernel83", "signal83"],
    ),
    (
        ("latency83 buffer83 queue83 worker83 kernel83 signal83", 10),
        ["latency83", "buffer83", "queue83", "worker83", "kernel83", "signal83"],
    ),
    (
        ("latency83 buffer83 queue83 worker83 kernel83 signal83", 18),
        ["latency83 buffer83", "queue83 worker83", "kernel83 signal83"],
    ),
    (
        ("latency83 buffer83 queue83 worker83 kernel83 signal83", 28),
        ["latency83 buffer83 queue83", "worker83 kernel83 signal83"],
    ),
    (
        ("buffer83 queue83 worker83 kernel83 signal83 packet83", 6),
        ["buffer83", "queue83", "worker83", "kernel83", "signal83", "packet83"],
    ),
    (
        ("buffer83 queue83 worker83 kernel83 signal83 packet83", 10),
        ["buffer83", "queue83", "worker83", "kernel83", "signal83", "packet83"],
    ),
    (
        ("buffer83 queue83 worker83 kernel83 signal83 packet83", 18),
        ["buffer83 queue83", "worker83 kernel83", "signal83 packet83"],
    ),
    (
        ("buffer83 queue83 worker83 kernel83 signal83 packet83", 28),
        ["buffer83 queue83 worker83", "kernel83 signal83 packet83"],
    ),
    (
        ("queue83 worker83 kernel83 signal83 packet83 router83", 6),
        ["queue83", "worker83", "kernel83", "signal83", "packet83", "router83"],
    ),
    (
        ("queue83 worker83 kernel83 signal83 packet83 router83", 10),
        ["queue83", "worker83", "kernel83", "signal83", "packet83", "router83"],
    ),
    (
        ("queue83 worker83 kernel83 signal83 packet83 router83", 18),
        ["queue83 worker83", "kernel83 signal83", "packet83 router83"],
    ),
    (
        ("queue83 worker83 kernel83 signal83 packet83 router83", 28),
        ["queue83 worker83 kernel83", "signal83 packet83 router83"],
    ),
    (
        ("worker83 kernel83 signal83 packet83 router83 cluster83", 6),
        ["worker83", "kernel83", "signal83", "packet83", "router83", "cluster83"],
    ),
    (
        ("worker83 kernel83 signal83 packet83 router83 cluster83", 10),
        ["worker83", "kernel83", "signal83", "packet83", "router83", "cluster83"],
    ),
    (
        ("worker83 kernel83 signal83 packet83 router83 cluster83", 18),
        ["worker83 kernel83", "signal83 packet83", "router83 cluster83"],
    ),
    (
        ("worker83 kernel83 signal83 packet83 router83 cluster83", 28),
        ["worker83 kernel83 signal83", "packet83 router83 cluster83"],
    ),
    (
        ("kernel83 signal83 packet83 router83 cluster83 mirror83", 6),
        ["kernel83", "signal83", "packet83", "router83", "cluster83", "mirror83"],
    ),
    (
        ("kernel83 signal83 packet83 router83 cluster83 mirror83", 10),
        ["kernel83", "signal83", "packet83", "router83", "cluster83", "mirror83"],
    ),
    (
        ("kernel83 signal83 packet83 router83 cluster83 mirror83", 18),
        ["kernel83 signal83", "packet83 router83", "cluster83 mirror83"],
    ),
    (
        ("kernel83 signal83 packet83 router83 cluster83 mirror83", 28),
        ["kernel83 signal83 packet83", "router83 cluster83 mirror83"],
    ),
    (
        ("signal83 packet83 router83 cluster83 mirror83 filter83", 6),
        ["signal83", "packet83", "router83", "cluster83", "mirror83", "filter83"],
    ),
    (
        ("signal83 packet83 router83 cluster83 mirror83 filter83", 10),
        ["signal83", "packet83", "router83", "cluster83", "mirror83", "filter83"],
    ),
    (
        ("signal83 packet83 router83 cluster83 mirror83 filter83", 18),
        ["signal83 packet83", "router83 cluster83", "mirror83 filter83"],
    ),
    (
        ("signal83 packet83 router83 cluster83 mirror83 filter83", 28),
        ["signal83 packet83 router83", "cluster83 mirror83 filter83"],
    ),
    (
        ("packet83 router83 cluster83 mirror83 filter83 ranking83", 6),
        ["packet83", "router83", "cluster83", "mirror83", "filter83", "ranking83"],
    ),
    (
        ("packet83 router83 cluster83 mirror83 filter83 ranking83", 10),
        ["packet83", "router83", "cluster83", "mirror83", "filter83", "ranking83"],
    ),
    (
        ("packet83 router83 cluster83 mirror83 filter83 ranking83", 18),
        ["packet83 router83", "cluster83 mirror83", "filter83 ranking83"],
    ),
    (
        ("packet83 router83 cluster83 mirror83 filter83 ranking83", 28),
        ["packet83 router83 cluster83", "mirror83 filter83 ranking83"],
    ),
    (
        ("router83 cluster83 mirror83 filter83 ranking83 encoding83", 6),
        ["router83", "cluster83", "mirror83", "filter83", "ranking83", "encoding83"],
    ),
    (
        ("router83 cluster83 mirror83 filter83 ranking83 encoding83", 10),
        ["router83", "cluster83", "mirror83", "filter83", "ranking83", "encoding83"],
    ),
    (
        ("router83 cluster83 mirror83 filter83 ranking83 encoding83", 18),
        ["router83 cluster83", "mirror83 filter83", "ranking83", "encoding83"],
    ),
    (
        ("router83 cluster83 mirror83 filter83 ranking83 encoding83", 28),
        ["router83 cluster83 mirror83", "filter83 ranking83", "encoding83"],
    ),
    (
        ("cluster83 mirror83 filter83 ranking83 encoding83 mapping83", 6),
        ["cluster83", "mirror83", "filter83", "ranking83", "encoding83", "mapping83"],
    ),
    (
        ("cluster83 mirror83 filter83 ranking83 encoding83 mapping83", 10),
        ["cluster83", "mirror83", "filter83", "ranking83", "encoding83", "mapping83"],
    ),
    (
        ("cluster83 mirror83 filter83 ranking83 encoding83 mapping83", 18),
        ["cluster83 mirror83", "filter83 ranking83", "encoding83", "mapping83"],
    ),
    (
        ("cluster83 mirror83 filter83 ranking83 encoding83 mapping83", 28),
        ["cluster83 mirror83 filter83", "ranking83 encoding83", "mapping83"],
    ),
    (
        ("mirror83 filter83 ranking83 encoding83 mapping83 record83", 6),
        ["mirror83", "filter83", "ranking83", "encoding83", "mapping83", "record83"],
    ),
    (
        ("mirror83 filter83 ranking83 encoding83 mapping83 record83", 10),
        ["mirror83", "filter83", "ranking83", "encoding83", "mapping83", "record83"],
    ),
    (
        ("mirror83 filter83 ranking83 encoding83 mapping83 record83", 18),
        ["mirror83 filter83", "ranking83", "encoding83", "mapping83 record83"],
    ),
    (
        ("mirror83 filter83 ranking83 encoding83 mapping83 record83", 28),
        ["mirror83 filter83 ranking83", "encoding83 mapping83", "record83"],
    ),
    (
        ("filter83 ranking83 encoding83 mapping83 record83 candle83", 6),
        ["filter83", "ranking83", "encoding83", "mapping83", "record83", "candle83"],
    ),
    (
        ("filter83 ranking83 encoding83 mapping83 record83 candle83", 10),
        ["filter83", "ranking83", "encoding83", "mapping83", "record83", "candle83"],
    ),
    (
        ("filter83 ranking83 encoding83 mapping83 record83 candle83", 18),
        ["filter83 ranking83", "encoding83", "mapping83 record83", "candle83"],
    ),
    (
        ("filter83 ranking83 encoding83 mapping83 record83 candle83", 28),
        ["filter83 ranking83", "encoding83 mapping83", "record83 candle83"],
    ),
    (
        ("ranking83 encoding83 mapping83 record83 candle83 thread83", 6),
        ["ranking83", "encoding83", "mapping83", "record83", "candle83", "thread83"],
    ),
    (
        ("ranking83 encoding83 mapping83 record83 candle83 thread83", 10),
        ["ranking83", "encoding83", "mapping83", "record83", "candle83", "thread83"],
    ),
    (
        ("ranking83 encoding83 mapping83 record83 candle83 thread83", 18),
        ["ranking83", "encoding83", "mapping83 record83", "candle83 thread83"],
    ),
    (
        ("ranking83 encoding83 mapping83 record83 candle83 thread83", 28),
        ["ranking83 encoding83", "mapping83 record83 candle83", "thread83"],
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
