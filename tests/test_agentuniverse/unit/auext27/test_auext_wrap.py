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
        ("round 27: the quick brown fox jumps over the lazy dog", 4),
        ["round", "27:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 27: the quick brown fox jumps over the lazy dog", 8),
        ["round", "27: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 27: the quick brown fox jumps over the lazy dog", 12),
        ["round 27:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 27: the quick brown fox jumps over the lazy dog", 16),
        ["round 27: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 27: the quick brown fox jumps over the lazy dog", 24),
        ["round 27: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 27: the quick brown fox jumps over the lazy dog", 32),
        ["round 27: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 27: agentuniverse is a framework for multi agents", 4),
        ["round", "27:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 27: agentuniverse is a framework for multi agents", 8),
        ["round", "27:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 27: agentuniverse is a framework for multi agents", 12),
        ["round 27:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 27: agentuniverse is a framework for multi agents", 16),
        ["round 27:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 27: agentuniverse is a framework for multi agents", 24),
        ["round 27: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 27: agentuniverse is a framework for multi agents", 32),
        ["round 27: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 27: knowledge stored as vectors enables retrieval", 4),
        ["round", "27:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 27: knowledge stored as vectors enables retrieval", 8),
        ["round", "27:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 27: knowledge stored as vectors enables retrieval", 12),
        ["round 27:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 27: knowledge stored as vectors enables retrieval", 16),
        ["round 27:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 27: knowledge stored as vectors enables retrieval", 24),
        ["round 27: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 27: knowledge stored as vectors enables retrieval", 32),
        ["round 27: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 27: the processor reads the record then stops", 4),
        ["round", "27:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 27: the processor reads the record then stops", 8),
        ["round", "27: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 27: the processor reads the record then stops", 12),
        ["round 27:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 27: the processor reads the record then stops", 16),
        ["round 27: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 27: the processor reads the record then stops", 24),
        ["round 27: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 27: the processor reads the record then stops", 32),
        ["round 27: the processor reads", "the record then stops"],
    ),
    (
        ("round 27: a worker pulls the next task from the queue", 4),
        ["round", "27:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 27: a worker pulls the next task from the queue", 8),
        ["round", "27: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 27: a worker pulls the next task from the queue", 12),
        ["round 27: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 27: a worker pulls the next task from the queue", 16),
        ["round 27: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 27: a worker pulls the next task from the queue", 24),
        ["round 27: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 27: a worker pulls the next task from the queue", 32),
        ["round 27: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 27: signals travel through the network layer", 4),
        ["round", "27:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 27: signals travel through the network layer", 8),
        ["round", "27:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 27: signals travel through the network layer", 12),
        ["round 27:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 27: signals travel through the network layer", 16),
        ["round 27:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 27: signals travel through the network layer", 24),
        ["round 27: signals travel", "through the network", "layer"],
    ),
    (
        ("round 27: signals travel through the network layer", 32),
        ["round 27: signals travel through", "the network layer"],
    ),
    (
        ("round 27: the gateway routes each request by policy", 4),
        ["round", "27:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 27: the gateway routes each request by policy", 8),
        ["round", "27: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 27: the gateway routes each request by policy", 12),
        ["round 27:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 27: the gateway routes each request by policy", 16),
        ["round 27: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 27: the gateway routes each request by policy", 24),
        ["round 27: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 27: the gateway routes each request by policy", 32),
        ["round 27: the gateway routes", "each request by policy"],
    ),
    (
        ("round 27: memory grows until the buffer is full", 4),
        ["round", "27:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 27: memory grows until the buffer is full", 8),
        ["round", "27:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 27: memory grows until the buffer is full", 12),
        ["round 27:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 27: memory grows until the buffer is full", 16),
        ["round 27: memory", "grows until the", "buffer is full"],
    ),
    (("round 27: memory grows until the buffer is full", 24), ["round 27: memory grows", "until the buffer is full"]),
    (("round 27: memory grows until the buffer is full", 32), ["round 27: memory grows until the", "buffer is full"]),
    (
        ("round 27: the cluster mirrors every packet twice", 4),
        ["round", "27:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 27: the cluster mirrors every packet twice", 8),
        ["round", "27: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 27: the cluster mirrors every packet twice", 12),
        ["round 27:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 27: the cluster mirrors every packet twice", 16),
        ["round 27: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 27: the cluster mirrors every packet twice", 24),
        ["round 27: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 27: the cluster mirrors every packet twice", 32), ["round 27: the cluster mirrors", "every packet twice"]),
    (
        ("round 27: ranking uses tokens learned from the corpus", 4),
        ["round", "27:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 27: ranking uses tokens learned from the corpus", 8),
        ["round", "27:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 27: ranking uses tokens learned from the corpus", 12),
        ["round 27:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 27: ranking uses tokens learned from the corpus", 16),
        ["round 27:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 27: ranking uses tokens learned from the corpus", 24),
        ["round 27: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 27: ranking uses tokens learned from the corpus", 32),
        ["round 27: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 27: a long session ends when the candle dies", 4),
        ["round", "27:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 27: a long session ends when the candle dies", 8),
        ["round", "27: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 27: a long session ends when the candle dies", 12),
        ["round 27: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 27: a long session ends when the candle dies", 16),
        ["round 27: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 27: a long session ends when the candle dies", 24),
        ["round 27: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 27: a long session ends when the candle dies", 32),
        ["round 27: a long session ends", "when the candle dies"],
    ),
    (
        ("round 27: encode the prompt then map the result", 4),
        ["round", "27:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 27: encode the prompt then map the result", 8),
        ["round", "27:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 27: encode the prompt then map the result", 12),
        ["round 27:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 27: encode the prompt then map the result", 16),
        ["round 27: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 27: encode the prompt then map the result", 24),
        ["round 27: encode the", "prompt then map the", "result"],
    ),
    (("round 27: encode the prompt then map the result", 32), ["round 27: encode the prompt then", "map the result"]),
    (
        ("round 27: the kernel wakes the worker at dawn", 4),
        ["round", "27:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 27: the kernel wakes the worker at dawn", 8),
        ["round", "27: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 27: the kernel wakes the worker at dawn", 12),
        ["round 27:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 27: the kernel wakes the worker at dawn", 16), ["round 27: the", "kernel wakes the", "worker at dawn"]),
    (("round 27: the kernel wakes the worker at dawn", 24), ["round 27: the kernel", "wakes the worker at dawn"]),
    (("round 27: the kernel wakes the worker at dawn", 32), ["round 27: the kernel wakes the", "worker at dawn"]),
    (
        ("round 27: service latency drops after the patch", 4),
        ["round", "27:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 27: service latency drops after the patch", 8),
        ["round", "27:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 27: service latency drops after the patch", 12),
        ["round 27:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 27: service latency drops after the patch", 16),
        ["round 27:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 27: service latency drops after the patch", 24),
        ["round 27: service", "latency drops after the", "patch"],
    ),
    (("round 27: service latency drops after the patch", 32), ["round 27: service latency drops", "after the patch"]),
    (
        ("round 27: the library caches every vector it sees", 4),
        ["round", "27:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 27: the library caches every vector it sees", 8),
        ["round", "27: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 27: the library caches every vector it sees", 12),
        ["round 27:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 27: the library caches every vector it sees", 16),
        ["round 27: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 27: the library caches every vector it sees", 24),
        ["round 27: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 27: the library caches every vector it sees", 32),
        ["round 27: the library caches", "every vector it sees"],
    ),
    (
        ("round 27: agents argue then the debate resolves", 4),
        ["round", "27:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 27: agents argue then the debate resolves", 8),
        ["round", "27:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 27: agents argue then the debate resolves", 12),
        ["round 27:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 27: agents argue then the debate resolves", 16),
        ["round 27: agents", "argue then the", "debate resolves"],
    ),
    (("round 27: agents argue then the debate resolves", 24), ["round 27: agents argue", "then the debate resolves"]),
    (("round 27: agents argue then the debate resolves", 32), ["round 27: agents argue then the", "debate resolves"]),
    (
        ("round 27: the filter keeps only strong matches", 4),
        ["round", "27:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 27: the filter keeps only strong matches", 8),
        ["round", "27: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 27: the filter keeps only strong matches", 12),
        ["round 27:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 27: the filter keeps only strong matches", 16),
        ["round 27: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 27: the filter keeps only strong matches", 24), ["round 27: the filter", "keeps only strong", "matches"]),
    (("round 27: the filter keeps only strong matches", 32), ["round 27: the filter keeps only", "strong matches"]),
    (
        ("round 27: the model answers with a short reply", 4),
        ["round", "27:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 27: the model answers with a short reply", 8),
        ["round", "27: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 27: the model answers with a short reply", 12),
        ["round 27:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 27: the model answers with a short reply", 16),
        ["round 27: the", "model answers", "with a short", "reply"],
    ),
    (("round 27: the model answers with a short reply", 24), ["round 27: the model", "answers with a short", "reply"]),
    (("round 27: the model answers with a short reply", 32), ["round 27: the model answers with", "a short reply"]),
    (
        ("round 27: the recorder stores the reasoning trace", 4),
        ["round", "27:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 27: the recorder stores the reasoning trace", 8),
        ["round", "27: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 27: the recorder stores the reasoning trace", 12),
        ["round 27:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 27: the recorder stores the reasoning trace", 16),
        ["round 27: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 27: the recorder stores the reasoning trace", 24),
        ["round 27: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 27: the recorder stores the reasoning trace", 32),
        ["round 27: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 27: the angel watches the processor run", 4),
        ["round", "27:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 27: the angel watches the processor run", 8),
        ["round", "27: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 27: the angel watches the processor run", 12),
        ["round 27:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 27: the angel watches the processor run", 16), ["round 27: the", "angel watches", "the processor", "run"]),
    (("round 27: the angel watches the processor run", 24), ["round 27: the angel", "watches the processor", "run"]),
    (("round 27: the angel watches the processor run", 32), ["round 27: the angel watches the", "processor run"]),
    (
        ("round 27: angle of the vector decides the match", 4),
        ["round", "27:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 27: angle of the vector decides the match", 8),
        ["round", "27:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 27: angle of the vector decides the match", 12),
        ["round 27:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 27: angle of the vector decides the match", 16),
        ["round 27: angle", "of the vector", "decides the", "match"],
    ),
    (("round 27: angle of the vector decides the match", 24), ["round 27: angle of the", "vector decides the match"]),
    (("round 27: angle of the vector decides the match", 32), ["round 27: angle of the vector", "decides the match"]),
    (
        ("round 27: the candle burns twice as long at night", 4),
        ["round", "27:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 27: the candle burns twice as long at night", 8),
        ["round", "27: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 27: the candle burns twice as long at night", 12),
        ["round 27:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 27: the candle burns twice as long at night", 16),
        ["round 27: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 27: the candle burns twice as long at night", 24),
        ["round 27: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 27: the candle burns twice as long at night", 32),
        ["round 27: the candle burns twice", "as long at night"],
    ),
    (
        ("round 27: a mirror of the universe in one line", 4),
        ["round", "27:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 27: a mirror of the universe in one line", 8),
        ["round", "27: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 27: a mirror of the universe in one line", 12),
        ["round 27: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 27: a mirror of the universe in one line", 16),
        ["round 27: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 27: a mirror of the universe in one line", 24), ["round 27: a mirror of", "the universe in one line"]),
    (("round 27: a mirror of the universe in one line", 32), ["round 27: a mirror of the", "universe in one line"]),
    (
        ("round 27: the queue drains before the storm", 4),
        ["round", "27:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 27: the queue drains before the storm", 8),
        ["round", "27: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 27: the queue drains before the storm", 12), ["round 27:", "the queue", "drains", "before the", "storm"]),
    (("round 27: the queue drains before the storm", 16), ["round 27: the", "queue drains", "before the storm"]),
    (("round 27: the queue drains before the storm", 24), ["round 27: the queue", "drains before the storm"]),
    (("round 27: the queue drains before the storm", 32), ["round 27: the queue drains", "before the storm"]),
    (
        ("kitten27 sitting27 agent27 angle27 universe27 memory27", 6),
        ["kitten27", "sitting27", "agent27", "angle27", "universe27", "memory27"],
    ),
    (
        ("kitten27 sitting27 agent27 angle27 universe27 memory27", 10),
        ["kitten27", "sitting27", "agent27", "angle27", "universe27", "memory27"],
    ),
    (
        ("kitten27 sitting27 agent27 angle27 universe27 memory27", 18),
        ["kitten27 sitting27", "agent27 angle27", "universe27", "memory27"],
    ),
    (
        ("kitten27 sitting27 agent27 angle27 universe27 memory27", 28),
        ["kitten27 sitting27 agent27", "angle27 universe27 memory27"],
    ),
    (
        ("sitting27 agent27 angle27 universe27 memory27 stream27", 6),
        ["sitting27", "agent27", "angle27", "universe27", "memory27", "stream27"],
    ),
    (
        ("sitting27 agent27 angle27 universe27 memory27 stream27", 10),
        ["sitting27", "agent27", "angle27", "universe27", "memory27", "stream27"],
    ),
    (
        ("sitting27 agent27 angle27 universe27 memory27 stream27", 18),
        ["sitting27 agent27", "angle27 universe27", "memory27 stream27"],
    ),
    (
        ("sitting27 agent27 angle27 universe27 memory27 stream27", 28),
        ["sitting27 agent27 angle27", "universe27 memory27 stream27"],
    ),
    (
        ("agent27 angle27 universe27 memory27 stream27 context27", 6),
        ["agent27", "angle27", "universe27", "memory27", "stream27", "context27"],
    ),
    (
        ("agent27 angle27 universe27 memory27 stream27 context27", 10),
        ["agent27", "angle27", "universe27", "memory27", "stream27", "context27"],
    ),
    (
        ("agent27 angle27 universe27 memory27 stream27 context27", 18),
        ["agent27 angle27", "universe27", "memory27 stream27", "context27"],
    ),
    (
        ("agent27 angle27 universe27 memory27 stream27 context27", 28),
        ["agent27 angle27 universe27", "memory27 stream27 context27"],
    ),
    (
        ("angle27 universe27 memory27 stream27 context27 knowledge27", 6),
        ["angle27", "universe27", "memory27", "stream27", "context27", "knowledge27"],
    ),
    (
        ("angle27 universe27 memory27 stream27 context27 knowledge27", 10),
        ["angle27", "universe27", "memory27", "stream27", "context27", "knowledge27"],
    ),
    (
        ("angle27 universe27 memory27 stream27 context27 knowledge27", 18),
        ["angle27 universe27", "memory27 stream27", "context27", "knowledge27"],
    ),
    (
        ("angle27 universe27 memory27 stream27 context27 knowledge27", 28),
        ["angle27 universe27 memory27", "stream27 context27", "knowledge27"],
    ),
    (
        ("universe27 memory27 stream27 context27 knowledge27 vector27", 6),
        ["universe27", "memory27", "stream27", "context27", "knowledge27", "vector27"],
    ),
    (
        ("universe27 memory27 stream27 context27 knowledge27 vector27", 10),
        ["universe27", "memory27", "stream27", "context27", "knowledge27", "vector27"],
    ),
    (
        ("universe27 memory27 stream27 context27 knowledge27 vector27", 18),
        ["universe27", "memory27 stream27", "context27", "knowledge27", "vector27"],
    ),
    (
        ("universe27 memory27 stream27 context27 knowledge27 vector27", 28),
        ["universe27 memory27 stream27", "context27 knowledge27", "vector27"],
    ),
    (
        ("memory27 stream27 context27 knowledge27 vector27 processor27", 6),
        ["memory27", "stream27", "context27", "knowledge27", "vector27", "processor27"],
    ),
    (
        ("memory27 stream27 context27 knowledge27 vector27 processor27", 10),
        ["memory27", "stream27", "context27", "knowledge27", "vector27", "processor27"],
    ),
    (
        ("memory27 stream27 context27 knowledge27 vector27 processor27", 18),
        ["memory27 stream27", "context27", "knowledge27", "vector27", "processor27"],
    ),
    (
        ("memory27 stream27 context27 knowledge27 vector27 processor27", 28),
        ["memory27 stream27 context27", "knowledge27 vector27", "processor27"],
    ),
    (
        ("stream27 context27 knowledge27 vector27 processor27 reasoning27", 6),
        ["stream27", "context27", "knowledge27", "vector27", "processor27", "reasoning27"],
    ),
    (
        ("stream27 context27 knowledge27 vector27 processor27 reasoning27", 10),
        ["stream27", "context27", "knowledge27", "vector27", "processor27", "reasoning27"],
    ),
    (
        ("stream27 context27 knowledge27 vector27 processor27 reasoning27", 18),
        ["stream27 context27", "knowledge27", "vector27", "processor27", "reasoning27"],
    ),
    (
        ("stream27 context27 knowledge27 vector27 processor27 reasoning27", 28),
        ["stream27 context27", "knowledge27 vector27", "processor27 reasoning27"],
    ),
    (
        ("context27 knowledge27 vector27 processor27 reasoning27 machine27", 6),
        ["context27", "knowledge27", "vector27", "processor27", "reasoning27", "machine27"],
    ),
    (
        ("context27 knowledge27 vector27 processor27 reasoning27 machine27", 10),
        ["context27", "knowledge27", "vector27", "processor27", "reasoning27", "machine27"],
    ),
    (
        ("context27 knowledge27 vector27 processor27 reasoning27 machine27", 18),
        ["context27", "knowledge27", "vector27", "processor27", "reasoning27", "machine27"],
    ),
    (
        ("context27 knowledge27 vector27 processor27 reasoning27 machine27", 28),
        ["context27 knowledge27", "vector27 processor27", "reasoning27 machine27"],
    ),
    (
        ("knowledge27 vector27 processor27 reasoning27 machine27 learning27", 6),
        ["knowledge27", "vector27", "processor27", "reasoning27", "machine27", "learning27"],
    ),
    (
        ("knowledge27 vector27 processor27 reasoning27 machine27 learning27", 10),
        ["knowledge27", "vector27", "processor27", "reasoning27", "machine27", "learning27"],
    ),
    (
        ("knowledge27 vector27 processor27 reasoning27 machine27 learning27", 18),
        ["knowledge27", "vector27", "processor27", "reasoning27", "machine27", "learning27"],
    ),
    (
        ("knowledge27 vector27 processor27 reasoning27 machine27 learning27", 28),
        ["knowledge27 vector27", "processor27 reasoning27", "machine27 learning27"],
    ),
    (
        ("vector27 processor27 reasoning27 machine27 learning27 model27", 6),
        ["vector27", "processor27", "reasoning27", "machine27", "learning27", "model27"],
    ),
    (
        ("vector27 processor27 reasoning27 machine27 learning27 model27", 10),
        ["vector27", "processor27", "reasoning27", "machine27", "learning27", "model27"],
    ),
    (
        ("vector27 processor27 reasoning27 machine27 learning27 model27", 18),
        ["vector27", "processor27", "reasoning27", "machine27", "learning27 model27"],
    ),
    (
        ("vector27 processor27 reasoning27 machine27 learning27 model27", 28),
        ["vector27 processor27", "reasoning27 machine27", "learning27 model27"],
    ),
    (
        ("processor27 reasoning27 machine27 learning27 model27 token27", 6),
        ["processor27", "reasoning27", "machine27", "learning27", "model27", "token27"],
    ),
    (
        ("processor27 reasoning27 machine27 learning27 model27 token27", 10),
        ["processor27", "reasoning27", "machine27", "learning27", "model27", "token27"],
    ),
    (
        ("processor27 reasoning27 machine27 learning27 model27 token27", 18),
        ["processor27", "reasoning27", "machine27", "learning27 model27", "token27"],
    ),
    (
        ("processor27 reasoning27 machine27 learning27 model27 token27", 28),
        ["processor27 reasoning27", "machine27 learning27 model27", "token27"],
    ),
    (
        ("reasoning27 machine27 learning27 model27 token27 prompt27", 6),
        ["reasoning27", "machine27", "learning27", "model27", "token27", "prompt27"],
    ),
    (
        ("reasoning27 machine27 learning27 model27 token27 prompt27", 10),
        ["reasoning27", "machine27", "learning27", "model27", "token27", "prompt27"],
    ),
    (
        ("reasoning27 machine27 learning27 model27 token27 prompt27", 18),
        ["reasoning27", "machine27", "learning27 model27", "token27 prompt27"],
    ),
    (
        ("reasoning27 machine27 learning27 model27 token27 prompt27", 28),
        ["reasoning27 machine27", "learning27 model27 token27", "prompt27"],
    ),
    (
        ("machine27 learning27 model27 token27 prompt27 session27", 6),
        ["machine27", "learning27", "model27", "token27", "prompt27", "session27"],
    ),
    (
        ("machine27 learning27 model27 token27 prompt27 session27", 10),
        ["machine27", "learning27", "model27", "token27", "prompt27", "session27"],
    ),
    (
        ("machine27 learning27 model27 token27 prompt27 session27", 18),
        ["machine27", "learning27 model27", "token27 prompt27", "session27"],
    ),
    (
        ("machine27 learning27 model27 token27 prompt27 session27", 28),
        ["machine27 learning27 model27", "token27 prompt27 session27"],
    ),
    (
        ("learning27 model27 token27 prompt27 session27 library27", 6),
        ["learning27", "model27", "token27", "prompt27", "session27", "library27"],
    ),
    (
        ("learning27 model27 token27 prompt27 session27 library27", 10),
        ["learning27", "model27", "token27", "prompt27", "session27", "library27"],
    ),
    (
        ("learning27 model27 token27 prompt27 session27 library27", 18),
        ["learning27 model27", "token27 prompt27", "session27", "library27"],
    ),
    (
        ("learning27 model27 token27 prompt27 session27 library27", 28),
        ["learning27 model27 token27", "prompt27 session27 library27"],
    ),
    (
        ("model27 token27 prompt27 session27 library27 service27", 6),
        ["model27", "token27", "prompt27", "session27", "library27", "service27"],
    ),
    (
        ("model27 token27 prompt27 session27 library27 service27", 10),
        ["model27", "token27", "prompt27", "session27", "library27", "service27"],
    ),
    (
        ("model27 token27 prompt27 session27 library27 service27", 18),
        ["model27 token27", "prompt27 session27", "library27", "service27"],
    ),
    (
        ("model27 token27 prompt27 session27 library27 service27", 28),
        ["model27 token27 prompt27", "session27 library27", "service27"],
    ),
    (
        ("token27 prompt27 session27 library27 service27 gateway27", 6),
        ["token27", "prompt27", "session27", "library27", "service27", "gateway27"],
    ),
    (
        ("token27 prompt27 session27 library27 service27 gateway27", 10),
        ["token27", "prompt27", "session27", "library27", "service27", "gateway27"],
    ),
    (
        ("token27 prompt27 session27 library27 service27 gateway27", 18),
        ["token27 prompt27", "session27", "library27", "service27", "gateway27"],
    ),
    (
        ("token27 prompt27 session27 library27 service27 gateway27", 28),
        ["token27 prompt27 session27", "library27 service27", "gateway27"],
    ),
    (
        ("prompt27 session27 library27 service27 gateway27 storage27", 6),
        ["prompt27", "session27", "library27", "service27", "gateway27", "storage27"],
    ),
    (
        ("prompt27 session27 library27 service27 gateway27 storage27", 10),
        ["prompt27", "session27", "library27", "service27", "gateway27", "storage27"],
    ),
    (
        ("prompt27 session27 library27 service27 gateway27 storage27", 18),
        ["prompt27 session27", "library27", "service27", "gateway27", "storage27"],
    ),
    (
        ("prompt27 session27 library27 service27 gateway27 storage27", 28),
        ["prompt27 session27 library27", "service27 gateway27", "storage27"],
    ),
    (
        ("session27 library27 service27 gateway27 storage27 network27", 6),
        ["session27", "library27", "service27", "gateway27", "storage27", "network27"],
    ),
    (
        ("session27 library27 service27 gateway27 storage27 network27", 10),
        ["session27", "library27", "service27", "gateway27", "storage27", "network27"],
    ),
    (
        ("session27 library27 service27 gateway27 storage27 network27", 18),
        ["session27", "library27", "service27", "gateway27", "storage27", "network27"],
    ),
    (
        ("session27 library27 service27 gateway27 storage27 network27", 28),
        ["session27 library27", "service27 gateway27", "storage27 network27"],
    ),
    (
        ("library27 service27 gateway27 storage27 network27 latency27", 6),
        ["library27", "service27", "gateway27", "storage27", "network27", "latency27"],
    ),
    (
        ("library27 service27 gateway27 storage27 network27 latency27", 10),
        ["library27", "service27", "gateway27", "storage27", "network27", "latency27"],
    ),
    (
        ("library27 service27 gateway27 storage27 network27 latency27", 18),
        ["library27", "service27", "gateway27", "storage27", "network27", "latency27"],
    ),
    (
        ("library27 service27 gateway27 storage27 network27 latency27", 28),
        ["library27 service27", "gateway27 storage27", "network27 latency27"],
    ),
    (
        ("service27 gateway27 storage27 network27 latency27 buffer27", 6),
        ["service27", "gateway27", "storage27", "network27", "latency27", "buffer27"],
    ),
    (
        ("service27 gateway27 storage27 network27 latency27 buffer27", 10),
        ["service27", "gateway27", "storage27", "network27", "latency27", "buffer27"],
    ),
    (
        ("service27 gateway27 storage27 network27 latency27 buffer27", 18),
        ["service27", "gateway27", "storage27", "network27", "latency27 buffer27"],
    ),
    (
        ("service27 gateway27 storage27 network27 latency27 buffer27", 28),
        ["service27 gateway27", "storage27 network27", "latency27 buffer27"],
    ),
    (
        ("gateway27 storage27 network27 latency27 buffer27 queue27", 6),
        ["gateway27", "storage27", "network27", "latency27", "buffer27", "queue27"],
    ),
    (
        ("gateway27 storage27 network27 latency27 buffer27 queue27", 10),
        ["gateway27", "storage27", "network27", "latency27", "buffer27", "queue27"],
    ),
    (
        ("gateway27 storage27 network27 latency27 buffer27 queue27", 18),
        ["gateway27", "storage27", "network27", "latency27 buffer27", "queue27"],
    ),
    (
        ("gateway27 storage27 network27 latency27 buffer27 queue27", 28),
        ["gateway27 storage27", "network27 latency27 buffer27", "queue27"],
    ),
    (
        ("storage27 network27 latency27 buffer27 queue27 worker27", 6),
        ["storage27", "network27", "latency27", "buffer27", "queue27", "worker27"],
    ),
    (
        ("storage27 network27 latency27 buffer27 queue27 worker27", 10),
        ["storage27", "network27", "latency27", "buffer27", "queue27", "worker27"],
    ),
    (
        ("storage27 network27 latency27 buffer27 queue27 worker27", 18),
        ["storage27", "network27", "latency27 buffer27", "queue27 worker27"],
    ),
    (
        ("storage27 network27 latency27 buffer27 queue27 worker27", 28),
        ["storage27 network27", "latency27 buffer27 queue27", "worker27"],
    ),
    (
        ("network27 latency27 buffer27 queue27 worker27 kernel27", 6),
        ["network27", "latency27", "buffer27", "queue27", "worker27", "kernel27"],
    ),
    (
        ("network27 latency27 buffer27 queue27 worker27 kernel27", 10),
        ["network27", "latency27", "buffer27", "queue27", "worker27", "kernel27"],
    ),
    (
        ("network27 latency27 buffer27 queue27 worker27 kernel27", 18),
        ["network27", "latency27 buffer27", "queue27 worker27", "kernel27"],
    ),
    (
        ("network27 latency27 buffer27 queue27 worker27 kernel27", 28),
        ["network27 latency27 buffer27", "queue27 worker27 kernel27"],
    ),
    (
        ("latency27 buffer27 queue27 worker27 kernel27 signal27", 6),
        ["latency27", "buffer27", "queue27", "worker27", "kernel27", "signal27"],
    ),
    (
        ("latency27 buffer27 queue27 worker27 kernel27 signal27", 10),
        ["latency27", "buffer27", "queue27", "worker27", "kernel27", "signal27"],
    ),
    (
        ("latency27 buffer27 queue27 worker27 kernel27 signal27", 18),
        ["latency27 buffer27", "queue27 worker27", "kernel27 signal27"],
    ),
    (
        ("latency27 buffer27 queue27 worker27 kernel27 signal27", 28),
        ["latency27 buffer27 queue27", "worker27 kernel27 signal27"],
    ),
    (
        ("buffer27 queue27 worker27 kernel27 signal27 packet27", 6),
        ["buffer27", "queue27", "worker27", "kernel27", "signal27", "packet27"],
    ),
    (
        ("buffer27 queue27 worker27 kernel27 signal27 packet27", 10),
        ["buffer27", "queue27", "worker27", "kernel27", "signal27", "packet27"],
    ),
    (
        ("buffer27 queue27 worker27 kernel27 signal27 packet27", 18),
        ["buffer27 queue27", "worker27 kernel27", "signal27 packet27"],
    ),
    (
        ("buffer27 queue27 worker27 kernel27 signal27 packet27", 28),
        ["buffer27 queue27 worker27", "kernel27 signal27 packet27"],
    ),
    (
        ("queue27 worker27 kernel27 signal27 packet27 router27", 6),
        ["queue27", "worker27", "kernel27", "signal27", "packet27", "router27"],
    ),
    (
        ("queue27 worker27 kernel27 signal27 packet27 router27", 10),
        ["queue27", "worker27", "kernel27", "signal27", "packet27", "router27"],
    ),
    (
        ("queue27 worker27 kernel27 signal27 packet27 router27", 18),
        ["queue27 worker27", "kernel27 signal27", "packet27 router27"],
    ),
    (
        ("queue27 worker27 kernel27 signal27 packet27 router27", 28),
        ["queue27 worker27 kernel27", "signal27 packet27 router27"],
    ),
    (
        ("worker27 kernel27 signal27 packet27 router27 cluster27", 6),
        ["worker27", "kernel27", "signal27", "packet27", "router27", "cluster27"],
    ),
    (
        ("worker27 kernel27 signal27 packet27 router27 cluster27", 10),
        ["worker27", "kernel27", "signal27", "packet27", "router27", "cluster27"],
    ),
    (
        ("worker27 kernel27 signal27 packet27 router27 cluster27", 18),
        ["worker27 kernel27", "signal27 packet27", "router27 cluster27"],
    ),
    (
        ("worker27 kernel27 signal27 packet27 router27 cluster27", 28),
        ["worker27 kernel27 signal27", "packet27 router27 cluster27"],
    ),
    (
        ("kernel27 signal27 packet27 router27 cluster27 mirror27", 6),
        ["kernel27", "signal27", "packet27", "router27", "cluster27", "mirror27"],
    ),
    (
        ("kernel27 signal27 packet27 router27 cluster27 mirror27", 10),
        ["kernel27", "signal27", "packet27", "router27", "cluster27", "mirror27"],
    ),
    (
        ("kernel27 signal27 packet27 router27 cluster27 mirror27", 18),
        ["kernel27 signal27", "packet27 router27", "cluster27 mirror27"],
    ),
    (
        ("kernel27 signal27 packet27 router27 cluster27 mirror27", 28),
        ["kernel27 signal27 packet27", "router27 cluster27 mirror27"],
    ),
    (
        ("signal27 packet27 router27 cluster27 mirror27 filter27", 6),
        ["signal27", "packet27", "router27", "cluster27", "mirror27", "filter27"],
    ),
    (
        ("signal27 packet27 router27 cluster27 mirror27 filter27", 10),
        ["signal27", "packet27", "router27", "cluster27", "mirror27", "filter27"],
    ),
    (
        ("signal27 packet27 router27 cluster27 mirror27 filter27", 18),
        ["signal27 packet27", "router27 cluster27", "mirror27 filter27"],
    ),
    (
        ("signal27 packet27 router27 cluster27 mirror27 filter27", 28),
        ["signal27 packet27 router27", "cluster27 mirror27 filter27"],
    ),
    (
        ("packet27 router27 cluster27 mirror27 filter27 ranking27", 6),
        ["packet27", "router27", "cluster27", "mirror27", "filter27", "ranking27"],
    ),
    (
        ("packet27 router27 cluster27 mirror27 filter27 ranking27", 10),
        ["packet27", "router27", "cluster27", "mirror27", "filter27", "ranking27"],
    ),
    (
        ("packet27 router27 cluster27 mirror27 filter27 ranking27", 18),
        ["packet27 router27", "cluster27 mirror27", "filter27 ranking27"],
    ),
    (
        ("packet27 router27 cluster27 mirror27 filter27 ranking27", 28),
        ["packet27 router27 cluster27", "mirror27 filter27 ranking27"],
    ),
    (
        ("router27 cluster27 mirror27 filter27 ranking27 encoding27", 6),
        ["router27", "cluster27", "mirror27", "filter27", "ranking27", "encoding27"],
    ),
    (
        ("router27 cluster27 mirror27 filter27 ranking27 encoding27", 10),
        ["router27", "cluster27", "mirror27", "filter27", "ranking27", "encoding27"],
    ),
    (
        ("router27 cluster27 mirror27 filter27 ranking27 encoding27", 18),
        ["router27 cluster27", "mirror27 filter27", "ranking27", "encoding27"],
    ),
    (
        ("router27 cluster27 mirror27 filter27 ranking27 encoding27", 28),
        ["router27 cluster27 mirror27", "filter27 ranking27", "encoding27"],
    ),
    (
        ("cluster27 mirror27 filter27 ranking27 encoding27 mapping27", 6),
        ["cluster27", "mirror27", "filter27", "ranking27", "encoding27", "mapping27"],
    ),
    (
        ("cluster27 mirror27 filter27 ranking27 encoding27 mapping27", 10),
        ["cluster27", "mirror27", "filter27", "ranking27", "encoding27", "mapping27"],
    ),
    (
        ("cluster27 mirror27 filter27 ranking27 encoding27 mapping27", 18),
        ["cluster27 mirror27", "filter27 ranking27", "encoding27", "mapping27"],
    ),
    (
        ("cluster27 mirror27 filter27 ranking27 encoding27 mapping27", 28),
        ["cluster27 mirror27 filter27", "ranking27 encoding27", "mapping27"],
    ),
    (
        ("mirror27 filter27 ranking27 encoding27 mapping27 record27", 6),
        ["mirror27", "filter27", "ranking27", "encoding27", "mapping27", "record27"],
    ),
    (
        ("mirror27 filter27 ranking27 encoding27 mapping27 record27", 10),
        ["mirror27", "filter27", "ranking27", "encoding27", "mapping27", "record27"],
    ),
    (
        ("mirror27 filter27 ranking27 encoding27 mapping27 record27", 18),
        ["mirror27 filter27", "ranking27", "encoding27", "mapping27 record27"],
    ),
    (
        ("mirror27 filter27 ranking27 encoding27 mapping27 record27", 28),
        ["mirror27 filter27 ranking27", "encoding27 mapping27", "record27"],
    ),
    (
        ("filter27 ranking27 encoding27 mapping27 record27 candle27", 6),
        ["filter27", "ranking27", "encoding27", "mapping27", "record27", "candle27"],
    ),
    (
        ("filter27 ranking27 encoding27 mapping27 record27 candle27", 10),
        ["filter27", "ranking27", "encoding27", "mapping27", "record27", "candle27"],
    ),
    (
        ("filter27 ranking27 encoding27 mapping27 record27 candle27", 18),
        ["filter27 ranking27", "encoding27", "mapping27 record27", "candle27"],
    ),
    (
        ("filter27 ranking27 encoding27 mapping27 record27 candle27", 28),
        ["filter27 ranking27", "encoding27 mapping27", "record27 candle27"],
    ),
    (
        ("ranking27 encoding27 mapping27 record27 candle27 thread27", 6),
        ["ranking27", "encoding27", "mapping27", "record27", "candle27", "thread27"],
    ),
    (
        ("ranking27 encoding27 mapping27 record27 candle27 thread27", 10),
        ["ranking27", "encoding27", "mapping27", "record27", "candle27", "thread27"],
    ),
    (
        ("ranking27 encoding27 mapping27 record27 candle27 thread27", 18),
        ["ranking27", "encoding27", "mapping27 record27", "candle27 thread27"],
    ),
    (
        ("ranking27 encoding27 mapping27 record27 candle27 thread27", 28),
        ["ranking27 encoding27", "mapping27 record27 candle27", "thread27"],
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
