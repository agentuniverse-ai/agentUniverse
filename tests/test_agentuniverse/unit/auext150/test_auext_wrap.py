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
        ("round 150: the quick brown fox jumps over the lazy dog", 4),
        ["round", "150:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 150: the quick brown fox jumps over the lazy dog", 8),
        ["round", "150: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 150: the quick brown fox jumps over the lazy dog", 12),
        ["round 150:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 150: the quick brown fox jumps over the lazy dog", 16),
        ["round 150: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 150: the quick brown fox jumps over the lazy dog", 24),
        ["round 150: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 150: the quick brown fox jumps over the lazy dog", 32),
        ["round 150: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 150: agentuniverse is a framework for multi agents", 4),
        ["round", "150:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 150: agentuniverse is a framework for multi agents", 8),
        ["round", "150:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 150: agentuniverse is a framework for multi agents", 12),
        ["round 150:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 150: agentuniverse is a framework for multi agents", 16),
        ["round 150:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 150: agentuniverse is a framework for multi agents", 24),
        ["round 150: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 150: agentuniverse is a framework for multi agents", 32),
        ["round 150: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 150: knowledge stored as vectors enables retrieval", 4),
        ["round", "150:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 150: knowledge stored as vectors enables retrieval", 8),
        ["round", "150:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 150: knowledge stored as vectors enables retrieval", 12),
        ["round 150:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 150: knowledge stored as vectors enables retrieval", 16),
        ["round 150:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 150: knowledge stored as vectors enables retrieval", 24),
        ["round 150: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 150: knowledge stored as vectors enables retrieval", 32),
        ["round 150: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 150: the processor reads the record then stops", 4),
        ["round", "150:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 150: the processor reads the record then stops", 8),
        ["round", "150: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 150: the processor reads the record then stops", 12),
        ["round 150:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 150: the processor reads the record then stops", 16),
        ["round 150: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 150: the processor reads the record then stops", 24),
        ["round 150: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 150: the processor reads the record then stops", 32),
        ["round 150: the processor reads", "the record then stops"],
    ),
    (
        ("round 150: a worker pulls the next task from the queue", 4),
        ["round", "150:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 150: a worker pulls the next task from the queue", 8),
        ["round", "150: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 150: a worker pulls the next task from the queue", 12),
        ["round 150: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 150: a worker pulls the next task from the queue", 16),
        ["round 150: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 150: a worker pulls the next task from the queue", 24),
        ["round 150: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 150: a worker pulls the next task from the queue", 32),
        ["round 150: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 150: signals travel through the network layer", 4),
        ["round", "150:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 150: signals travel through the network layer", 8),
        ["round", "150:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 150: signals travel through the network layer", 12),
        ["round 150:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 150: signals travel through the network layer", 16),
        ["round 150:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 150: signals travel through the network layer", 24),
        ["round 150: signals", "travel through the", "network layer"],
    ),
    (
        ("round 150: signals travel through the network layer", 32),
        ["round 150: signals travel", "through the network layer"],
    ),
    (
        ("round 150: the gateway routes each request by policy", 4),
        ["round", "150:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 150: the gateway routes each request by policy", 8),
        ["round", "150: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 150: the gateway routes each request by policy", 12),
        ["round 150:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 150: the gateway routes each request by policy", 16),
        ["round 150: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 150: the gateway routes each request by policy", 24),
        ["round 150: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 150: the gateway routes each request by policy", 32),
        ["round 150: the gateway routes", "each request by policy"],
    ),
    (
        ("round 150: memory grows until the buffer is full", 4),
        ["round", "150:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 150: memory grows until the buffer is full", 8),
        ["round", "150:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 150: memory grows until the buffer is full", 12),
        ["round 150:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 150: memory grows until the buffer is full", 16),
        ["round 150:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 150: memory grows until the buffer is full", 24), ["round 150: memory grows", "until the buffer is full"]),
    (("round 150: memory grows until the buffer is full", 32), ["round 150: memory grows until", "the buffer is full"]),
    (
        ("round 150: the cluster mirrors every packet twice", 4),
        ["round", "150:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 150: the cluster mirrors every packet twice", 8),
        ["round", "150: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 150: the cluster mirrors every packet twice", 12),
        ["round 150:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 150: the cluster mirrors every packet twice", 16),
        ["round 150: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 150: the cluster mirrors every packet twice", 24),
        ["round 150: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 150: the cluster mirrors every packet twice", 32),
        ["round 150: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 150: ranking uses tokens learned from the corpus", 4),
        ["round", "150:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 150: ranking uses tokens learned from the corpus", 8),
        ["round", "150:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 150: ranking uses tokens learned from the corpus", 12),
        ["round 150:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 150: ranking uses tokens learned from the corpus", 16),
        ["round 150:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 150: ranking uses tokens learned from the corpus", 24),
        ["round 150: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 150: ranking uses tokens learned from the corpus", 32),
        ["round 150: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 150: a long session ends when the candle dies", 4),
        ["round", "150:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 150: a long session ends when the candle dies", 8),
        ["round", "150: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 150: a long session ends when the candle dies", 12),
        ["round 150: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 150: a long session ends when the candle dies", 16),
        ["round 150: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 150: a long session ends when the candle dies", 24),
        ["round 150: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 150: a long session ends when the candle dies", 32),
        ["round 150: a long session ends", "when the candle dies"],
    ),
    (
        ("round 150: encode the prompt then map the result", 4),
        ["round", "150:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 150: encode the prompt then map the result", 8),
        ["round", "150:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 150: encode the prompt then map the result", 12),
        ["round 150:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 150: encode the prompt then map the result", 16),
        ["round 150:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 150: encode the prompt then map the result", 24),
        ["round 150: encode the", "prompt then map the", "result"],
    ),
    (("round 150: encode the prompt then map the result", 32), ["round 150: encode the prompt", "then map the result"]),
    (
        ("round 150: the kernel wakes the worker at dawn", 4),
        ["round", "150:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 150: the kernel wakes the worker at dawn", 8),
        ["round", "150: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 150: the kernel wakes the worker at dawn", 12),
        ["round 150:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 150: the kernel wakes the worker at dawn", 16), ["round 150: the", "kernel wakes the", "worker at dawn"]),
    (("round 150: the kernel wakes the worker at dawn", 24), ["round 150: the kernel", "wakes the worker at dawn"]),
    (("round 150: the kernel wakes the worker at dawn", 32), ["round 150: the kernel wakes the", "worker at dawn"]),
    (
        ("round 150: service latency drops after the patch", 4),
        ["round", "150:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 150: service latency drops after the patch", 8),
        ["round", "150:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 150: service latency drops after the patch", 12),
        ["round 150:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 150: service latency drops after the patch", 16),
        ["round 150:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 150: service latency drops after the patch", 24),
        ["round 150: service", "latency drops after the", "patch"],
    ),
    (("round 150: service latency drops after the patch", 32), ["round 150: service latency drops", "after the patch"]),
    (
        ("round 150: the library caches every vector it sees", 4),
        ["round", "150:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 150: the library caches every vector it sees", 8),
        ["round", "150: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 150: the library caches every vector it sees", 12),
        ["round 150:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 150: the library caches every vector it sees", 16),
        ["round 150: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 150: the library caches every vector it sees", 24),
        ["round 150: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 150: the library caches every vector it sees", 32),
        ["round 150: the library caches", "every vector it sees"],
    ),
    (
        ("round 150: agents argue then the debate resolves", 4),
        ["round", "150:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 150: agents argue then the debate resolves", 8),
        ["round", "150:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 150: agents argue then the debate resolves", 12),
        ["round 150:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 150: agents argue then the debate resolves", 16),
        ["round 150:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 150: agents argue then the debate resolves", 24), ["round 150: agents argue", "then the debate resolves"]),
    (("round 150: agents argue then the debate resolves", 32), ["round 150: agents argue then the", "debate resolves"]),
    (
        ("round 150: the filter keeps only strong matches", 4),
        ["round", "150:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 150: the filter keeps only strong matches", 8),
        ["round", "150: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 150: the filter keeps only strong matches", 12),
        ["round 150:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 150: the filter keeps only strong matches", 16),
        ["round 150: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 150: the filter keeps only strong matches", 24),
        ["round 150: the filter", "keeps only strong", "matches"],
    ),
    (("round 150: the filter keeps only strong matches", 32), ["round 150: the filter keeps only", "strong matches"]),
    (
        ("round 150: the model answers with a short reply", 4),
        ["round", "150:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 150: the model answers with a short reply", 8),
        ["round", "150: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 150: the model answers with a short reply", 12),
        ["round 150:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 150: the model answers with a short reply", 16),
        ["round 150: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 150: the model answers with a short reply", 24),
        ["round 150: the model", "answers with a short", "reply"],
    ),
    (("round 150: the model answers with a short reply", 32), ["round 150: the model answers", "with a short reply"]),
    (
        ("round 150: the recorder stores the reasoning trace", 4),
        ["round", "150:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 150: the recorder stores the reasoning trace", 8),
        ["round", "150: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 150: the recorder stores the reasoning trace", 12),
        ["round 150:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 150: the recorder stores the reasoning trace", 16),
        ["round 150: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 150: the recorder stores the reasoning trace", 24),
        ["round 150: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 150: the recorder stores the reasoning trace", 32),
        ["round 150: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 150: the angel watches the processor run", 4),
        ["round", "150:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 150: the angel watches the processor run", 8),
        ["round", "150: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 150: the angel watches the processor run", 12),
        ["round 150:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 150: the angel watches the processor run", 16),
        ["round 150: the", "angel watches", "the processor", "run"],
    ),
    (("round 150: the angel watches the processor run", 24), ["round 150: the angel", "watches the processor", "run"]),
    (("round 150: the angel watches the processor run", 32), ["round 150: the angel watches the", "processor run"]),
    (
        ("round 150: angle of the vector decides the match", 4),
        ["round", "150:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 150: angle of the vector decides the match", 8),
        ["round", "150:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 150: angle of the vector decides the match", 12),
        ["round 150:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 150: angle of the vector decides the match", 16),
        ["round 150: angle", "of the vector", "decides the", "match"],
    ),
    (("round 150: angle of the vector decides the match", 24), ["round 150: angle of the", "vector decides the match"]),
    (("round 150: angle of the vector decides the match", 32), ["round 150: angle of the vector", "decides the match"]),
    (
        ("round 150: the candle burns twice as long at night", 4),
        ["round", "150:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 150: the candle burns twice as long at night", 8),
        ["round", "150: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 150: the candle burns twice as long at night", 12),
        ["round 150:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 150: the candle burns twice as long at night", 16),
        ["round 150: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 150: the candle burns twice as long at night", 24),
        ["round 150: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 150: the candle burns twice as long at night", 32),
        ["round 150: the candle burns", "twice as long at night"],
    ),
    (
        ("round 150: a mirror of the universe in one line", 4),
        ["round", "150:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 150: a mirror of the universe in one line", 8),
        ["round", "150: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 150: a mirror of the universe in one line", 12),
        ["round 150: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 150: a mirror of the universe in one line", 16),
        ["round 150: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 150: a mirror of the universe in one line", 24), ["round 150: a mirror of", "the universe in one line"]),
    (("round 150: a mirror of the universe in one line", 32), ["round 150: a mirror of the", "universe in one line"]),
    (
        ("round 150: the queue drains before the storm", 4),
        ["round", "150:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 150: the queue drains before the storm", 8),
        ["round", "150: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 150: the queue drains before the storm", 12),
        ["round 150:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 150: the queue drains before the storm", 16), ["round 150: the", "queue drains", "before the storm"]),
    (("round 150: the queue drains before the storm", 24), ["round 150: the queue", "drains before the storm"]),
    (("round 150: the queue drains before the storm", 32), ["round 150: the queue drains", "before the storm"]),
    (
        ("kitten150 sitting150 agent150 angle150 universe150 memory150", 6),
        ["kitten150", "sitting150", "agent150", "angle150", "universe150", "memory150"],
    ),
    (
        ("kitten150 sitting150 agent150 angle150 universe150 memory150", 10),
        ["kitten150", "sitting150", "agent150", "angle150", "universe150", "memory150"],
    ),
    (
        ("kitten150 sitting150 agent150 angle150 universe150 memory150", 18),
        ["kitten150", "sitting150", "agent150 angle150", "universe150", "memory150"],
    ),
    (
        ("kitten150 sitting150 agent150 angle150 universe150 memory150", 28),
        ["kitten150 sitting150", "agent150 angle150", "universe150 memory150"],
    ),
    (
        ("sitting150 agent150 angle150 universe150 memory150 stream150", 6),
        ["sitting150", "agent150", "angle150", "universe150", "memory150", "stream150"],
    ),
    (
        ("sitting150 agent150 angle150 universe150 memory150 stream150", 10),
        ["sitting150", "agent150", "angle150", "universe150", "memory150", "stream150"],
    ),
    (
        ("sitting150 agent150 angle150 universe150 memory150 stream150", 18),
        ["sitting150", "agent150 angle150", "universe150", "memory150", "stream150"],
    ),
    (
        ("sitting150 agent150 angle150 universe150 memory150 stream150", 28),
        ["sitting150 agent150 angle150", "universe150 memory150", "stream150"],
    ),
    (
        ("agent150 angle150 universe150 memory150 stream150 context150", 6),
        ["agent150", "angle150", "universe150", "memory150", "stream150", "context150"],
    ),
    (
        ("agent150 angle150 universe150 memory150 stream150 context150", 10),
        ["agent150", "angle150", "universe150", "memory150", "stream150", "context150"],
    ),
    (
        ("agent150 angle150 universe150 memory150 stream150 context150", 18),
        ["agent150 angle150", "universe150", "memory150", "stream150", "context150"],
    ),
    (
        ("agent150 angle150 universe150 memory150 stream150 context150", 28),
        ["agent150 angle150", "universe150 memory150", "stream150 context150"],
    ),
    (
        ("angle150 universe150 memory150 stream150 context150 knowledge150", 6),
        ["angle150", "universe150", "memory150", "stream150", "context150", "knowledge150"],
    ),
    (
        ("angle150 universe150 memory150 stream150 context150 knowledge150", 10),
        ["angle150", "universe150", "memory150", "stream150", "context150", "knowledge150"],
    ),
    (
        ("angle150 universe150 memory150 stream150 context150 knowledge150", 18),
        ["angle150", "universe150", "memory150", "stream150", "context150", "knowledge150"],
    ),
    (
        ("angle150 universe150 memory150 stream150 context150 knowledge150", 28),
        ["angle150 universe150", "memory150 stream150", "context150 knowledge150"],
    ),
    (
        ("universe150 memory150 stream150 context150 knowledge150 vector150", 6),
        ["universe150", "memory150", "stream150", "context150", "knowledge150", "vector150"],
    ),
    (
        ("universe150 memory150 stream150 context150 knowledge150 vector150", 10),
        ["universe150", "memory150", "stream150", "context150", "knowledge150", "vector150"],
    ),
    (
        ("universe150 memory150 stream150 context150 knowledge150 vector150", 18),
        ["universe150", "memory150", "stream150", "context150", "knowledge150", "vector150"],
    ),
    (
        ("universe150 memory150 stream150 context150 knowledge150 vector150", 28),
        ["universe150 memory150", "stream150 context150", "knowledge150 vector150"],
    ),
    (
        ("memory150 stream150 context150 knowledge150 vector150 processor150", 6),
        ["memory150", "stream150", "context150", "knowledge150", "vector150", "processor150"],
    ),
    (
        ("memory150 stream150 context150 knowledge150 vector150 processor150", 10),
        ["memory150", "stream150", "context150", "knowledge150", "vector150", "processor150"],
    ),
    (
        ("memory150 stream150 context150 knowledge150 vector150 processor150", 18),
        ["memory150", "stream150", "context150", "knowledge150", "vector150", "processor150"],
    ),
    (
        ("memory150 stream150 context150 knowledge150 vector150 processor150", 28),
        ["memory150 stream150", "context150 knowledge150", "vector150 processor150"],
    ),
    (
        ("stream150 context150 knowledge150 vector150 processor150 reasoning150", 6),
        ["stream150", "context150", "knowledge150", "vector150", "processor150", "reasoning150"],
    ),
    (
        ("stream150 context150 knowledge150 vector150 processor150 reasoning150", 10),
        ["stream150", "context150", "knowledge150", "vector150", "processor150", "reasoning150"],
    ),
    (
        ("stream150 context150 knowledge150 vector150 processor150 reasoning150", 18),
        ["stream150", "context150", "knowledge150", "vector150", "processor150", "reasoning150"],
    ),
    (
        ("stream150 context150 knowledge150 vector150 processor150 reasoning150", 28),
        ["stream150 context150", "knowledge150 vector150", "processor150 reasoning150"],
    ),
    (
        ("context150 knowledge150 vector150 processor150 reasoning150 machine150", 6),
        ["context150", "knowledge150", "vector150", "processor150", "reasoning150", "machine150"],
    ),
    (
        ("context150 knowledge150 vector150 processor150 reasoning150 machine150", 10),
        ["context150", "knowledge150", "vector150", "processor150", "reasoning150", "machine150"],
    ),
    (
        ("context150 knowledge150 vector150 processor150 reasoning150 machine150", 18),
        ["context150", "knowledge150", "vector150", "processor150", "reasoning150", "machine150"],
    ),
    (
        ("context150 knowledge150 vector150 processor150 reasoning150 machine150", 28),
        ["context150 knowledge150", "vector150 processor150", "reasoning150 machine150"],
    ),
    (
        ("knowledge150 vector150 processor150 reasoning150 machine150 learning150", 6),
        ["knowledge150", "vector150", "processor150", "reasoning150", "machine150", "learning150"],
    ),
    (
        ("knowledge150 vector150 processor150 reasoning150 machine150 learning150", 10),
        ["knowledge150", "vector150", "processor150", "reasoning150", "machine150", "learning150"],
    ),
    (
        ("knowledge150 vector150 processor150 reasoning150 machine150 learning150", 18),
        ["knowledge150", "vector150", "processor150", "reasoning150", "machine150", "learning150"],
    ),
    (
        ("knowledge150 vector150 processor150 reasoning150 machine150 learning150", 28),
        ["knowledge150 vector150", "processor150 reasoning150", "machine150 learning150"],
    ),
    (
        ("vector150 processor150 reasoning150 machine150 learning150 model150", 6),
        ["vector150", "processor150", "reasoning150", "machine150", "learning150", "model150"],
    ),
    (
        ("vector150 processor150 reasoning150 machine150 learning150 model150", 10),
        ["vector150", "processor150", "reasoning150", "machine150", "learning150", "model150"],
    ),
    (
        ("vector150 processor150 reasoning150 machine150 learning150 model150", 18),
        ["vector150", "processor150", "reasoning150", "machine150", "learning150", "model150"],
    ),
    (
        ("vector150 processor150 reasoning150 machine150 learning150 model150", 28),
        ["vector150 processor150", "reasoning150 machine150", "learning150 model150"],
    ),
    (
        ("processor150 reasoning150 machine150 learning150 model150 token150", 6),
        ["processor150", "reasoning150", "machine150", "learning150", "model150", "token150"],
    ),
    (
        ("processor150 reasoning150 machine150 learning150 model150 token150", 10),
        ["processor150", "reasoning150", "machine150", "learning150", "model150", "token150"],
    ),
    (
        ("processor150 reasoning150 machine150 learning150 model150 token150", 18),
        ["processor150", "reasoning150", "machine150", "learning150", "model150 token150"],
    ),
    (
        ("processor150 reasoning150 machine150 learning150 model150 token150", 28),
        ["processor150 reasoning150", "machine150 learning150", "model150 token150"],
    ),
    (
        ("reasoning150 machine150 learning150 model150 token150 prompt150", 6),
        ["reasoning150", "machine150", "learning150", "model150", "token150", "prompt150"],
    ),
    (
        ("reasoning150 machine150 learning150 model150 token150 prompt150", 10),
        ["reasoning150", "machine150", "learning150", "model150", "token150", "prompt150"],
    ),
    (
        ("reasoning150 machine150 learning150 model150 token150 prompt150", 18),
        ["reasoning150", "machine150", "learning150", "model150 token150", "prompt150"],
    ),
    (
        ("reasoning150 machine150 learning150 model150 token150 prompt150", 28),
        ["reasoning150 machine150", "learning150 model150", "token150 prompt150"],
    ),
    (
        ("machine150 learning150 model150 token150 prompt150 session150", 6),
        ["machine150", "learning150", "model150", "token150", "prompt150", "session150"],
    ),
    (
        ("machine150 learning150 model150 token150 prompt150 session150", 10),
        ["machine150", "learning150", "model150", "token150", "prompt150", "session150"],
    ),
    (
        ("machine150 learning150 model150 token150 prompt150 session150", 18),
        ["machine150", "learning150", "model150 token150", "prompt150", "session150"],
    ),
    (
        ("machine150 learning150 model150 token150 prompt150 session150", 28),
        ["machine150 learning150", "model150 token150 prompt150", "session150"],
    ),
    (
        ("learning150 model150 token150 prompt150 session150 library150", 6),
        ["learning150", "model150", "token150", "prompt150", "session150", "library150"],
    ),
    (
        ("learning150 model150 token150 prompt150 session150 library150", 10),
        ["learning150", "model150", "token150", "prompt150", "session150", "library150"],
    ),
    (
        ("learning150 model150 token150 prompt150 session150 library150", 18),
        ["learning150", "model150 token150", "prompt150", "session150", "library150"],
    ),
    (
        ("learning150 model150 token150 prompt150 session150 library150", 28),
        ["learning150 model150", "token150 prompt150", "session150 library150"],
    ),
    (
        ("model150 token150 prompt150 session150 library150 service150", 6),
        ["model150", "token150", "prompt150", "session150", "library150", "service150"],
    ),
    (
        ("model150 token150 prompt150 session150 library150 service150", 10),
        ["model150", "token150", "prompt150", "session150", "library150", "service150"],
    ),
    (
        ("model150 token150 prompt150 session150 library150 service150", 18),
        ["model150 token150", "prompt150", "session150", "library150", "service150"],
    ),
    (
        ("model150 token150 prompt150 session150 library150 service150", 28),
        ["model150 token150 prompt150", "session150 library150", "service150"],
    ),
    (
        ("token150 prompt150 session150 library150 service150 gateway150", 6),
        ["token150", "prompt150", "session150", "library150", "service150", "gateway150"],
    ),
    (
        ("token150 prompt150 session150 library150 service150 gateway150", 10),
        ["token150", "prompt150", "session150", "library150", "service150", "gateway150"],
    ),
    (
        ("token150 prompt150 session150 library150 service150 gateway150", 18),
        ["token150 prompt150", "session150", "library150", "service150", "gateway150"],
    ),
    (
        ("token150 prompt150 session150 library150 service150 gateway150", 28),
        ["token150 prompt150", "session150 library150", "service150 gateway150"],
    ),
    (
        ("prompt150 session150 library150 service150 gateway150 storage150", 6),
        ["prompt150", "session150", "library150", "service150", "gateway150", "storage150"],
    ),
    (
        ("prompt150 session150 library150 service150 gateway150 storage150", 10),
        ["prompt150", "session150", "library150", "service150", "gateway150", "storage150"],
    ),
    (
        ("prompt150 session150 library150 service150 gateway150 storage150", 18),
        ["prompt150", "session150", "library150", "service150", "gateway150", "storage150"],
    ),
    (
        ("prompt150 session150 library150 service150 gateway150 storage150", 28),
        ["prompt150 session150", "library150 service150", "gateway150 storage150"],
    ),
    (
        ("session150 library150 service150 gateway150 storage150 network150", 6),
        ["session150", "library150", "service150", "gateway150", "storage150", "network150"],
    ),
    (
        ("session150 library150 service150 gateway150 storage150 network150", 10),
        ["session150", "library150", "service150", "gateway150", "storage150", "network150"],
    ),
    (
        ("session150 library150 service150 gateway150 storage150 network150", 18),
        ["session150", "library150", "service150", "gateway150", "storage150", "network150"],
    ),
    (
        ("session150 library150 service150 gateway150 storage150 network150", 28),
        ["session150 library150", "service150 gateway150", "storage150 network150"],
    ),
    (
        ("library150 service150 gateway150 storage150 network150 latency150", 6),
        ["library150", "service150", "gateway150", "storage150", "network150", "latency150"],
    ),
    (
        ("library150 service150 gateway150 storage150 network150 latency150", 10),
        ["library150", "service150", "gateway150", "storage150", "network150", "latency150"],
    ),
    (
        ("library150 service150 gateway150 storage150 network150 latency150", 18),
        ["library150", "service150", "gateway150", "storage150", "network150", "latency150"],
    ),
    (
        ("library150 service150 gateway150 storage150 network150 latency150", 28),
        ["library150 service150", "gateway150 storage150", "network150 latency150"],
    ),
    (
        ("service150 gateway150 storage150 network150 latency150 buffer150", 6),
        ["service150", "gateway150", "storage150", "network150", "latency150", "buffer150"],
    ),
    (
        ("service150 gateway150 storage150 network150 latency150 buffer150", 10),
        ["service150", "gateway150", "storage150", "network150", "latency150", "buffer150"],
    ),
    (
        ("service150 gateway150 storage150 network150 latency150 buffer150", 18),
        ["service150", "gateway150", "storage150", "network150", "latency150", "buffer150"],
    ),
    (
        ("service150 gateway150 storage150 network150 latency150 buffer150", 28),
        ["service150 gateway150", "storage150 network150", "latency150 buffer150"],
    ),
    (
        ("gateway150 storage150 network150 latency150 buffer150 queue150", 6),
        ["gateway150", "storage150", "network150", "latency150", "buffer150", "queue150"],
    ),
    (
        ("gateway150 storage150 network150 latency150 buffer150 queue150", 10),
        ["gateway150", "storage150", "network150", "latency150", "buffer150", "queue150"],
    ),
    (
        ("gateway150 storage150 network150 latency150 buffer150 queue150", 18),
        ["gateway150", "storage150", "network150", "latency150", "buffer150 queue150"],
    ),
    (
        ("gateway150 storage150 network150 latency150 buffer150 queue150", 28),
        ["gateway150 storage150", "network150 latency150", "buffer150 queue150"],
    ),
    (
        ("storage150 network150 latency150 buffer150 queue150 worker150", 6),
        ["storage150", "network150", "latency150", "buffer150", "queue150", "worker150"],
    ),
    (
        ("storage150 network150 latency150 buffer150 queue150 worker150", 10),
        ["storage150", "network150", "latency150", "buffer150", "queue150", "worker150"],
    ),
    (
        ("storage150 network150 latency150 buffer150 queue150 worker150", 18),
        ["storage150", "network150", "latency150", "buffer150 queue150", "worker150"],
    ),
    (
        ("storage150 network150 latency150 buffer150 queue150 worker150", 28),
        ["storage150 network150", "latency150 buffer150", "queue150 worker150"],
    ),
    (
        ("network150 latency150 buffer150 queue150 worker150 kernel150", 6),
        ["network150", "latency150", "buffer150", "queue150", "worker150", "kernel150"],
    ),
    (
        ("network150 latency150 buffer150 queue150 worker150 kernel150", 10),
        ["network150", "latency150", "buffer150", "queue150", "worker150", "kernel150"],
    ),
    (
        ("network150 latency150 buffer150 queue150 worker150 kernel150", 18),
        ["network150", "latency150", "buffer150 queue150", "worker150", "kernel150"],
    ),
    (
        ("network150 latency150 buffer150 queue150 worker150 kernel150", 28),
        ["network150 latency150", "buffer150 queue150 worker150", "kernel150"],
    ),
    (
        ("latency150 buffer150 queue150 worker150 kernel150 signal150", 6),
        ["latency150", "buffer150", "queue150", "worker150", "kernel150", "signal150"],
    ),
    (
        ("latency150 buffer150 queue150 worker150 kernel150 signal150", 10),
        ["latency150", "buffer150", "queue150", "worker150", "kernel150", "signal150"],
    ),
    (
        ("latency150 buffer150 queue150 worker150 kernel150 signal150", 18),
        ["latency150", "buffer150 queue150", "worker150", "kernel150", "signal150"],
    ),
    (
        ("latency150 buffer150 queue150 worker150 kernel150 signal150", 28),
        ["latency150 buffer150", "queue150 worker150 kernel150", "signal150"],
    ),
    (
        ("buffer150 queue150 worker150 kernel150 signal150 packet150", 6),
        ["buffer150", "queue150", "worker150", "kernel150", "signal150", "packet150"],
    ),
    (
        ("buffer150 queue150 worker150 kernel150 signal150 packet150", 10),
        ["buffer150", "queue150", "worker150", "kernel150", "signal150", "packet150"],
    ),
    (
        ("buffer150 queue150 worker150 kernel150 signal150 packet150", 18),
        ["buffer150 queue150", "worker150", "kernel150", "signal150", "packet150"],
    ),
    (
        ("buffer150 queue150 worker150 kernel150 signal150 packet150", 28),
        ["buffer150 queue150 worker150", "kernel150 signal150", "packet150"],
    ),
    (
        ("queue150 worker150 kernel150 signal150 packet150 router150", 6),
        ["queue150", "worker150", "kernel150", "signal150", "packet150", "router150"],
    ),
    (
        ("queue150 worker150 kernel150 signal150 packet150 router150", 10),
        ["queue150", "worker150", "kernel150", "signal150", "packet150", "router150"],
    ),
    (
        ("queue150 worker150 kernel150 signal150 packet150 router150", 18),
        ["queue150 worker150", "kernel150", "signal150", "packet150", "router150"],
    ),
    (
        ("queue150 worker150 kernel150 signal150 packet150 router150", 28),
        ["queue150 worker150 kernel150", "signal150 packet150", "router150"],
    ),
    (
        ("worker150 kernel150 signal150 packet150 router150 cluster150", 6),
        ["worker150", "kernel150", "signal150", "packet150", "router150", "cluster150"],
    ),
    (
        ("worker150 kernel150 signal150 packet150 router150 cluster150", 10),
        ["worker150", "kernel150", "signal150", "packet150", "router150", "cluster150"],
    ),
    (
        ("worker150 kernel150 signal150 packet150 router150 cluster150", 18),
        ["worker150", "kernel150", "signal150", "packet150", "router150", "cluster150"],
    ),
    (
        ("worker150 kernel150 signal150 packet150 router150 cluster150", 28),
        ["worker150 kernel150", "signal150 packet150", "router150 cluster150"],
    ),
    (
        ("kernel150 signal150 packet150 router150 cluster150 mirror150", 6),
        ["kernel150", "signal150", "packet150", "router150", "cluster150", "mirror150"],
    ),
    (
        ("kernel150 signal150 packet150 router150 cluster150 mirror150", 10),
        ["kernel150", "signal150", "packet150", "router150", "cluster150", "mirror150"],
    ),
    (
        ("kernel150 signal150 packet150 router150 cluster150 mirror150", 18),
        ["kernel150", "signal150", "packet150", "router150", "cluster150", "mirror150"],
    ),
    (
        ("kernel150 signal150 packet150 router150 cluster150 mirror150", 28),
        ["kernel150 signal150", "packet150 router150", "cluster150 mirror150"],
    ),
    (
        ("signal150 packet150 router150 cluster150 mirror150 filter150", 6),
        ["signal150", "packet150", "router150", "cluster150", "mirror150", "filter150"],
    ),
    (
        ("signal150 packet150 router150 cluster150 mirror150 filter150", 10),
        ["signal150", "packet150", "router150", "cluster150", "mirror150", "filter150"],
    ),
    (
        ("signal150 packet150 router150 cluster150 mirror150 filter150", 18),
        ["signal150", "packet150", "router150", "cluster150", "mirror150", "filter150"],
    ),
    (
        ("signal150 packet150 router150 cluster150 mirror150 filter150", 28),
        ["signal150 packet150", "router150 cluster150", "mirror150 filter150"],
    ),
    (
        ("packet150 router150 cluster150 mirror150 filter150 ranking150", 6),
        ["packet150", "router150", "cluster150", "mirror150", "filter150", "ranking150"],
    ),
    (
        ("packet150 router150 cluster150 mirror150 filter150 ranking150", 10),
        ["packet150", "router150", "cluster150", "mirror150", "filter150", "ranking150"],
    ),
    (
        ("packet150 router150 cluster150 mirror150 filter150 ranking150", 18),
        ["packet150", "router150", "cluster150", "mirror150", "filter150", "ranking150"],
    ),
    (
        ("packet150 router150 cluster150 mirror150 filter150 ranking150", 28),
        ["packet150 router150", "cluster150 mirror150", "filter150 ranking150"],
    ),
    (
        ("router150 cluster150 mirror150 filter150 ranking150 encoding150", 6),
        ["router150", "cluster150", "mirror150", "filter150", "ranking150", "encoding150"],
    ),
    (
        ("router150 cluster150 mirror150 filter150 ranking150 encoding150", 10),
        ["router150", "cluster150", "mirror150", "filter150", "ranking150", "encoding150"],
    ),
    (
        ("router150 cluster150 mirror150 filter150 ranking150 encoding150", 18),
        ["router150", "cluster150", "mirror150", "filter150", "ranking150", "encoding150"],
    ),
    (
        ("router150 cluster150 mirror150 filter150 ranking150 encoding150", 28),
        ["router150 cluster150", "mirror150 filter150", "ranking150 encoding150"],
    ),
    (
        ("cluster150 mirror150 filter150 ranking150 encoding150 mapping150", 6),
        ["cluster150", "mirror150", "filter150", "ranking150", "encoding150", "mapping150"],
    ),
    (
        ("cluster150 mirror150 filter150 ranking150 encoding150 mapping150", 10),
        ["cluster150", "mirror150", "filter150", "ranking150", "encoding150", "mapping150"],
    ),
    (
        ("cluster150 mirror150 filter150 ranking150 encoding150 mapping150", 18),
        ["cluster150", "mirror150", "filter150", "ranking150", "encoding150", "mapping150"],
    ),
    (
        ("cluster150 mirror150 filter150 ranking150 encoding150 mapping150", 28),
        ["cluster150 mirror150", "filter150 ranking150", "encoding150 mapping150"],
    ),
    (
        ("mirror150 filter150 ranking150 encoding150 mapping150 record150", 6),
        ["mirror150", "filter150", "ranking150", "encoding150", "mapping150", "record150"],
    ),
    (
        ("mirror150 filter150 ranking150 encoding150 mapping150 record150", 10),
        ["mirror150", "filter150", "ranking150", "encoding150", "mapping150", "record150"],
    ),
    (
        ("mirror150 filter150 ranking150 encoding150 mapping150 record150", 18),
        ["mirror150", "filter150", "ranking150", "encoding150", "mapping150", "record150"],
    ),
    (
        ("mirror150 filter150 ranking150 encoding150 mapping150 record150", 28),
        ["mirror150 filter150", "ranking150 encoding150", "mapping150 record150"],
    ),
    (
        ("filter150 ranking150 encoding150 mapping150 record150 candle150", 6),
        ["filter150", "ranking150", "encoding150", "mapping150", "record150", "candle150"],
    ),
    (
        ("filter150 ranking150 encoding150 mapping150 record150 candle150", 10),
        ["filter150", "ranking150", "encoding150", "mapping150", "record150", "candle150"],
    ),
    (
        ("filter150 ranking150 encoding150 mapping150 record150 candle150", 18),
        ["filter150", "ranking150", "encoding150", "mapping150", "record150", "candle150"],
    ),
    (
        ("filter150 ranking150 encoding150 mapping150 record150 candle150", 28),
        ["filter150 ranking150", "encoding150 mapping150", "record150 candle150"],
    ),
    (
        ("ranking150 encoding150 mapping150 record150 candle150 thread150", 6),
        ["ranking150", "encoding150", "mapping150", "record150", "candle150", "thread150"],
    ),
    (
        ("ranking150 encoding150 mapping150 record150 candle150 thread150", 10),
        ["ranking150", "encoding150", "mapping150", "record150", "candle150", "thread150"],
    ),
    (
        ("ranking150 encoding150 mapping150 record150 candle150 thread150", 18),
        ["ranking150", "encoding150", "mapping150", "record150", "candle150", "thread150"],
    ),
    (
        ("ranking150 encoding150 mapping150 record150 candle150 thread150", 28),
        ["ranking150 encoding150", "mapping150 record150", "candle150 thread150"],
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
