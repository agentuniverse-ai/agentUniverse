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
        ("round 50: the quick brown fox jumps over the lazy dog", 4),
        ["round", "50:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 50: the quick brown fox jumps over the lazy dog", 8),
        ["round", "50: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 50: the quick brown fox jumps over the lazy dog", 12),
        ["round 50:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 50: the quick brown fox jumps over the lazy dog", 16),
        ["round 50: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 50: the quick brown fox jumps over the lazy dog", 24),
        ["round 50: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 50: the quick brown fox jumps over the lazy dog", 32),
        ["round 50: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 50: agentuniverse is a framework for multi agents", 4),
        ["round", "50:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 50: agentuniverse is a framework for multi agents", 8),
        ["round", "50:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 50: agentuniverse is a framework for multi agents", 12),
        ["round 50:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 50: agentuniverse is a framework for multi agents", 16),
        ["round 50:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 50: agentuniverse is a framework for multi agents", 24),
        ["round 50: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 50: agentuniverse is a framework for multi agents", 32),
        ["round 50: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 50: knowledge stored as vectors enables retrieval", 4),
        ["round", "50:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 50: knowledge stored as vectors enables retrieval", 8),
        ["round", "50:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 50: knowledge stored as vectors enables retrieval", 12),
        ["round 50:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 50: knowledge stored as vectors enables retrieval", 16),
        ["round 50:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 50: knowledge stored as vectors enables retrieval", 24),
        ["round 50: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 50: knowledge stored as vectors enables retrieval", 32),
        ["round 50: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 50: the processor reads the record then stops", 4),
        ["round", "50:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 50: the processor reads the record then stops", 8),
        ["round", "50: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 50: the processor reads the record then stops", 12),
        ["round 50:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 50: the processor reads the record then stops", 16),
        ["round 50: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 50: the processor reads the record then stops", 24),
        ["round 50: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 50: the processor reads the record then stops", 32),
        ["round 50: the processor reads", "the record then stops"],
    ),
    (
        ("round 50: a worker pulls the next task from the queue", 4),
        ["round", "50:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 50: a worker pulls the next task from the queue", 8),
        ["round", "50: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 50: a worker pulls the next task from the queue", 12),
        ["round 50: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 50: a worker pulls the next task from the queue", 16),
        ["round 50: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 50: a worker pulls the next task from the queue", 24),
        ["round 50: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 50: a worker pulls the next task from the queue", 32),
        ["round 50: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 50: signals travel through the network layer", 4),
        ["round", "50:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 50: signals travel through the network layer", 8),
        ["round", "50:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 50: signals travel through the network layer", 12),
        ["round 50:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 50: signals travel through the network layer", 16),
        ["round 50:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 50: signals travel through the network layer", 24),
        ["round 50: signals travel", "through the network", "layer"],
    ),
    (
        ("round 50: signals travel through the network layer", 32),
        ["round 50: signals travel through", "the network layer"],
    ),
    (
        ("round 50: the gateway routes each request by policy", 4),
        ["round", "50:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 50: the gateway routes each request by policy", 8),
        ["round", "50: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 50: the gateway routes each request by policy", 12),
        ["round 50:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 50: the gateway routes each request by policy", 16),
        ["round 50: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 50: the gateway routes each request by policy", 24),
        ["round 50: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 50: the gateway routes each request by policy", 32),
        ["round 50: the gateway routes", "each request by policy"],
    ),
    (
        ("round 50: memory grows until the buffer is full", 4),
        ["round", "50:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 50: memory grows until the buffer is full", 8),
        ["round", "50:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 50: memory grows until the buffer is full", 12),
        ["round 50:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 50: memory grows until the buffer is full", 16),
        ["round 50: memory", "grows until the", "buffer is full"],
    ),
    (("round 50: memory grows until the buffer is full", 24), ["round 50: memory grows", "until the buffer is full"]),
    (("round 50: memory grows until the buffer is full", 32), ["round 50: memory grows until the", "buffer is full"]),
    (
        ("round 50: the cluster mirrors every packet twice", 4),
        ["round", "50:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 50: the cluster mirrors every packet twice", 8),
        ["round", "50: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 50: the cluster mirrors every packet twice", 12),
        ["round 50:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 50: the cluster mirrors every packet twice", 16),
        ["round 50: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 50: the cluster mirrors every packet twice", 24),
        ["round 50: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 50: the cluster mirrors every packet twice", 32), ["round 50: the cluster mirrors", "every packet twice"]),
    (
        ("round 50: ranking uses tokens learned from the corpus", 4),
        ["round", "50:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 50: ranking uses tokens learned from the corpus", 8),
        ["round", "50:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 50: ranking uses tokens learned from the corpus", 12),
        ["round 50:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 50: ranking uses tokens learned from the corpus", 16),
        ["round 50:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 50: ranking uses tokens learned from the corpus", 24),
        ["round 50: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 50: ranking uses tokens learned from the corpus", 32),
        ["round 50: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 50: a long session ends when the candle dies", 4),
        ["round", "50:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 50: a long session ends when the candle dies", 8),
        ["round", "50: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 50: a long session ends when the candle dies", 12),
        ["round 50: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 50: a long session ends when the candle dies", 16),
        ["round 50: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 50: a long session ends when the candle dies", 24),
        ["round 50: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 50: a long session ends when the candle dies", 32),
        ["round 50: a long session ends", "when the candle dies"],
    ),
    (
        ("round 50: encode the prompt then map the result", 4),
        ["round", "50:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 50: encode the prompt then map the result", 8),
        ["round", "50:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 50: encode the prompt then map the result", 12),
        ["round 50:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 50: encode the prompt then map the result", 16),
        ["round 50: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 50: encode the prompt then map the result", 24),
        ["round 50: encode the", "prompt then map the", "result"],
    ),
    (("round 50: encode the prompt then map the result", 32), ["round 50: encode the prompt then", "map the result"]),
    (
        ("round 50: the kernel wakes the worker at dawn", 4),
        ["round", "50:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 50: the kernel wakes the worker at dawn", 8),
        ["round", "50: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 50: the kernel wakes the worker at dawn", 12),
        ["round 50:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 50: the kernel wakes the worker at dawn", 16), ["round 50: the", "kernel wakes the", "worker at dawn"]),
    (("round 50: the kernel wakes the worker at dawn", 24), ["round 50: the kernel", "wakes the worker at dawn"]),
    (("round 50: the kernel wakes the worker at dawn", 32), ["round 50: the kernel wakes the", "worker at dawn"]),
    (
        ("round 50: service latency drops after the patch", 4),
        ["round", "50:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 50: service latency drops after the patch", 8),
        ["round", "50:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 50: service latency drops after the patch", 12),
        ["round 50:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 50: service latency drops after the patch", 16),
        ["round 50:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 50: service latency drops after the patch", 24),
        ["round 50: service", "latency drops after the", "patch"],
    ),
    (("round 50: service latency drops after the patch", 32), ["round 50: service latency drops", "after the patch"]),
    (
        ("round 50: the library caches every vector it sees", 4),
        ["round", "50:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 50: the library caches every vector it sees", 8),
        ["round", "50: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 50: the library caches every vector it sees", 12),
        ["round 50:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 50: the library caches every vector it sees", 16),
        ["round 50: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 50: the library caches every vector it sees", 24),
        ["round 50: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 50: the library caches every vector it sees", 32),
        ["round 50: the library caches", "every vector it sees"],
    ),
    (
        ("round 50: agents argue then the debate resolves", 4),
        ["round", "50:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 50: agents argue then the debate resolves", 8),
        ["round", "50:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 50: agents argue then the debate resolves", 12),
        ["round 50:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 50: agents argue then the debate resolves", 16),
        ["round 50: agents", "argue then the", "debate resolves"],
    ),
    (("round 50: agents argue then the debate resolves", 24), ["round 50: agents argue", "then the debate resolves"]),
    (("round 50: agents argue then the debate resolves", 32), ["round 50: agents argue then the", "debate resolves"]),
    (
        ("round 50: the filter keeps only strong matches", 4),
        ["round", "50:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 50: the filter keeps only strong matches", 8),
        ["round", "50: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 50: the filter keeps only strong matches", 12),
        ["round 50:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 50: the filter keeps only strong matches", 16),
        ["round 50: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 50: the filter keeps only strong matches", 24), ["round 50: the filter", "keeps only strong", "matches"]),
    (("round 50: the filter keeps only strong matches", 32), ["round 50: the filter keeps only", "strong matches"]),
    (
        ("round 50: the model answers with a short reply", 4),
        ["round", "50:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 50: the model answers with a short reply", 8),
        ["round", "50: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 50: the model answers with a short reply", 12),
        ["round 50:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 50: the model answers with a short reply", 16),
        ["round 50: the", "model answers", "with a short", "reply"],
    ),
    (("round 50: the model answers with a short reply", 24), ["round 50: the model", "answers with a short", "reply"]),
    (("round 50: the model answers with a short reply", 32), ["round 50: the model answers with", "a short reply"]),
    (
        ("round 50: the recorder stores the reasoning trace", 4),
        ["round", "50:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 50: the recorder stores the reasoning trace", 8),
        ["round", "50: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 50: the recorder stores the reasoning trace", 12),
        ["round 50:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 50: the recorder stores the reasoning trace", 16),
        ["round 50: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 50: the recorder stores the reasoning trace", 24),
        ["round 50: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 50: the recorder stores the reasoning trace", 32),
        ["round 50: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 50: the angel watches the processor run", 4),
        ["round", "50:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 50: the angel watches the processor run", 8),
        ["round", "50: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 50: the angel watches the processor run", 12),
        ["round 50:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 50: the angel watches the processor run", 16), ["round 50: the", "angel watches", "the processor", "run"]),
    (("round 50: the angel watches the processor run", 24), ["round 50: the angel", "watches the processor", "run"]),
    (("round 50: the angel watches the processor run", 32), ["round 50: the angel watches the", "processor run"]),
    (
        ("round 50: angle of the vector decides the match", 4),
        ["round", "50:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 50: angle of the vector decides the match", 8),
        ["round", "50:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 50: angle of the vector decides the match", 12),
        ["round 50:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 50: angle of the vector decides the match", 16),
        ["round 50: angle", "of the vector", "decides the", "match"],
    ),
    (("round 50: angle of the vector decides the match", 24), ["round 50: angle of the", "vector decides the match"]),
    (("round 50: angle of the vector decides the match", 32), ["round 50: angle of the vector", "decides the match"]),
    (
        ("round 50: the candle burns twice as long at night", 4),
        ["round", "50:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 50: the candle burns twice as long at night", 8),
        ["round", "50: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 50: the candle burns twice as long at night", 12),
        ["round 50:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 50: the candle burns twice as long at night", 16),
        ["round 50: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 50: the candle burns twice as long at night", 24),
        ["round 50: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 50: the candle burns twice as long at night", 32),
        ["round 50: the candle burns twice", "as long at night"],
    ),
    (
        ("round 50: a mirror of the universe in one line", 4),
        ["round", "50:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 50: a mirror of the universe in one line", 8),
        ["round", "50: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 50: a mirror of the universe in one line", 12),
        ["round 50: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 50: a mirror of the universe in one line", 16),
        ["round 50: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 50: a mirror of the universe in one line", 24), ["round 50: a mirror of", "the universe in one line"]),
    (("round 50: a mirror of the universe in one line", 32), ["round 50: a mirror of the", "universe in one line"]),
    (
        ("round 50: the queue drains before the storm", 4),
        ["round", "50:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 50: the queue drains before the storm", 8),
        ["round", "50: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 50: the queue drains before the storm", 12), ["round 50:", "the queue", "drains", "before the", "storm"]),
    (("round 50: the queue drains before the storm", 16), ["round 50: the", "queue drains", "before the storm"]),
    (("round 50: the queue drains before the storm", 24), ["round 50: the queue", "drains before the storm"]),
    (("round 50: the queue drains before the storm", 32), ["round 50: the queue drains", "before the storm"]),
    (
        ("kitten50 sitting50 agent50 angle50 universe50 memory50", 6),
        ["kitten50", "sitting50", "agent50", "angle50", "universe50", "memory50"],
    ),
    (
        ("kitten50 sitting50 agent50 angle50 universe50 memory50", 10),
        ["kitten50", "sitting50", "agent50", "angle50", "universe50", "memory50"],
    ),
    (
        ("kitten50 sitting50 agent50 angle50 universe50 memory50", 18),
        ["kitten50 sitting50", "agent50 angle50", "universe50", "memory50"],
    ),
    (
        ("kitten50 sitting50 agent50 angle50 universe50 memory50", 28),
        ["kitten50 sitting50 agent50", "angle50 universe50 memory50"],
    ),
    (
        ("sitting50 agent50 angle50 universe50 memory50 stream50", 6),
        ["sitting50", "agent50", "angle50", "universe50", "memory50", "stream50"],
    ),
    (
        ("sitting50 agent50 angle50 universe50 memory50 stream50", 10),
        ["sitting50", "agent50", "angle50", "universe50", "memory50", "stream50"],
    ),
    (
        ("sitting50 agent50 angle50 universe50 memory50 stream50", 18),
        ["sitting50 agent50", "angle50 universe50", "memory50 stream50"],
    ),
    (
        ("sitting50 agent50 angle50 universe50 memory50 stream50", 28),
        ["sitting50 agent50 angle50", "universe50 memory50 stream50"],
    ),
    (
        ("agent50 angle50 universe50 memory50 stream50 context50", 6),
        ["agent50", "angle50", "universe50", "memory50", "stream50", "context50"],
    ),
    (
        ("agent50 angle50 universe50 memory50 stream50 context50", 10),
        ["agent50", "angle50", "universe50", "memory50", "stream50", "context50"],
    ),
    (
        ("agent50 angle50 universe50 memory50 stream50 context50", 18),
        ["agent50 angle50", "universe50", "memory50 stream50", "context50"],
    ),
    (
        ("agent50 angle50 universe50 memory50 stream50 context50", 28),
        ["agent50 angle50 universe50", "memory50 stream50 context50"],
    ),
    (
        ("angle50 universe50 memory50 stream50 context50 knowledge50", 6),
        ["angle50", "universe50", "memory50", "stream50", "context50", "knowledge50"],
    ),
    (
        ("angle50 universe50 memory50 stream50 context50 knowledge50", 10),
        ["angle50", "universe50", "memory50", "stream50", "context50", "knowledge50"],
    ),
    (
        ("angle50 universe50 memory50 stream50 context50 knowledge50", 18),
        ["angle50 universe50", "memory50 stream50", "context50", "knowledge50"],
    ),
    (
        ("angle50 universe50 memory50 stream50 context50 knowledge50", 28),
        ["angle50 universe50 memory50", "stream50 context50", "knowledge50"],
    ),
    (
        ("universe50 memory50 stream50 context50 knowledge50 vector50", 6),
        ["universe50", "memory50", "stream50", "context50", "knowledge50", "vector50"],
    ),
    (
        ("universe50 memory50 stream50 context50 knowledge50 vector50", 10),
        ["universe50", "memory50", "stream50", "context50", "knowledge50", "vector50"],
    ),
    (
        ("universe50 memory50 stream50 context50 knowledge50 vector50", 18),
        ["universe50", "memory50 stream50", "context50", "knowledge50", "vector50"],
    ),
    (
        ("universe50 memory50 stream50 context50 knowledge50 vector50", 28),
        ["universe50 memory50 stream50", "context50 knowledge50", "vector50"],
    ),
    (
        ("memory50 stream50 context50 knowledge50 vector50 processor50", 6),
        ["memory50", "stream50", "context50", "knowledge50", "vector50", "processor50"],
    ),
    (
        ("memory50 stream50 context50 knowledge50 vector50 processor50", 10),
        ["memory50", "stream50", "context50", "knowledge50", "vector50", "processor50"],
    ),
    (
        ("memory50 stream50 context50 knowledge50 vector50 processor50", 18),
        ["memory50 stream50", "context50", "knowledge50", "vector50", "processor50"],
    ),
    (
        ("memory50 stream50 context50 knowledge50 vector50 processor50", 28),
        ["memory50 stream50 context50", "knowledge50 vector50", "processor50"],
    ),
    (
        ("stream50 context50 knowledge50 vector50 processor50 reasoning50", 6),
        ["stream50", "context50", "knowledge50", "vector50", "processor50", "reasoning50"],
    ),
    (
        ("stream50 context50 knowledge50 vector50 processor50 reasoning50", 10),
        ["stream50", "context50", "knowledge50", "vector50", "processor50", "reasoning50"],
    ),
    (
        ("stream50 context50 knowledge50 vector50 processor50 reasoning50", 18),
        ["stream50 context50", "knowledge50", "vector50", "processor50", "reasoning50"],
    ),
    (
        ("stream50 context50 knowledge50 vector50 processor50 reasoning50", 28),
        ["stream50 context50", "knowledge50 vector50", "processor50 reasoning50"],
    ),
    (
        ("context50 knowledge50 vector50 processor50 reasoning50 machine50", 6),
        ["context50", "knowledge50", "vector50", "processor50", "reasoning50", "machine50"],
    ),
    (
        ("context50 knowledge50 vector50 processor50 reasoning50 machine50", 10),
        ["context50", "knowledge50", "vector50", "processor50", "reasoning50", "machine50"],
    ),
    (
        ("context50 knowledge50 vector50 processor50 reasoning50 machine50", 18),
        ["context50", "knowledge50", "vector50", "processor50", "reasoning50", "machine50"],
    ),
    (
        ("context50 knowledge50 vector50 processor50 reasoning50 machine50", 28),
        ["context50 knowledge50", "vector50 processor50", "reasoning50 machine50"],
    ),
    (
        ("knowledge50 vector50 processor50 reasoning50 machine50 learning50", 6),
        ["knowledge50", "vector50", "processor50", "reasoning50", "machine50", "learning50"],
    ),
    (
        ("knowledge50 vector50 processor50 reasoning50 machine50 learning50", 10),
        ["knowledge50", "vector50", "processor50", "reasoning50", "machine50", "learning50"],
    ),
    (
        ("knowledge50 vector50 processor50 reasoning50 machine50 learning50", 18),
        ["knowledge50", "vector50", "processor50", "reasoning50", "machine50", "learning50"],
    ),
    (
        ("knowledge50 vector50 processor50 reasoning50 machine50 learning50", 28),
        ["knowledge50 vector50", "processor50 reasoning50", "machine50 learning50"],
    ),
    (
        ("vector50 processor50 reasoning50 machine50 learning50 model50", 6),
        ["vector50", "processor50", "reasoning50", "machine50", "learning50", "model50"],
    ),
    (
        ("vector50 processor50 reasoning50 machine50 learning50 model50", 10),
        ["vector50", "processor50", "reasoning50", "machine50", "learning50", "model50"],
    ),
    (
        ("vector50 processor50 reasoning50 machine50 learning50 model50", 18),
        ["vector50", "processor50", "reasoning50", "machine50", "learning50 model50"],
    ),
    (
        ("vector50 processor50 reasoning50 machine50 learning50 model50", 28),
        ["vector50 processor50", "reasoning50 machine50", "learning50 model50"],
    ),
    (
        ("processor50 reasoning50 machine50 learning50 model50 token50", 6),
        ["processor50", "reasoning50", "machine50", "learning50", "model50", "token50"],
    ),
    (
        ("processor50 reasoning50 machine50 learning50 model50 token50", 10),
        ["processor50", "reasoning50", "machine50", "learning50", "model50", "token50"],
    ),
    (
        ("processor50 reasoning50 machine50 learning50 model50 token50", 18),
        ["processor50", "reasoning50", "machine50", "learning50 model50", "token50"],
    ),
    (
        ("processor50 reasoning50 machine50 learning50 model50 token50", 28),
        ["processor50 reasoning50", "machine50 learning50 model50", "token50"],
    ),
    (
        ("reasoning50 machine50 learning50 model50 token50 prompt50", 6),
        ["reasoning50", "machine50", "learning50", "model50", "token50", "prompt50"],
    ),
    (
        ("reasoning50 machine50 learning50 model50 token50 prompt50", 10),
        ["reasoning50", "machine50", "learning50", "model50", "token50", "prompt50"],
    ),
    (
        ("reasoning50 machine50 learning50 model50 token50 prompt50", 18),
        ["reasoning50", "machine50", "learning50 model50", "token50 prompt50"],
    ),
    (
        ("reasoning50 machine50 learning50 model50 token50 prompt50", 28),
        ["reasoning50 machine50", "learning50 model50 token50", "prompt50"],
    ),
    (
        ("machine50 learning50 model50 token50 prompt50 session50", 6),
        ["machine50", "learning50", "model50", "token50", "prompt50", "session50"],
    ),
    (
        ("machine50 learning50 model50 token50 prompt50 session50", 10),
        ["machine50", "learning50", "model50", "token50", "prompt50", "session50"],
    ),
    (
        ("machine50 learning50 model50 token50 prompt50 session50", 18),
        ["machine50", "learning50 model50", "token50 prompt50", "session50"],
    ),
    (
        ("machine50 learning50 model50 token50 prompt50 session50", 28),
        ["machine50 learning50 model50", "token50 prompt50 session50"],
    ),
    (
        ("learning50 model50 token50 prompt50 session50 library50", 6),
        ["learning50", "model50", "token50", "prompt50", "session50", "library50"],
    ),
    (
        ("learning50 model50 token50 prompt50 session50 library50", 10),
        ["learning50", "model50", "token50", "prompt50", "session50", "library50"],
    ),
    (
        ("learning50 model50 token50 prompt50 session50 library50", 18),
        ["learning50 model50", "token50 prompt50", "session50", "library50"],
    ),
    (
        ("learning50 model50 token50 prompt50 session50 library50", 28),
        ["learning50 model50 token50", "prompt50 session50 library50"],
    ),
    (
        ("model50 token50 prompt50 session50 library50 service50", 6),
        ["model50", "token50", "prompt50", "session50", "library50", "service50"],
    ),
    (
        ("model50 token50 prompt50 session50 library50 service50", 10),
        ["model50", "token50", "prompt50", "session50", "library50", "service50"],
    ),
    (
        ("model50 token50 prompt50 session50 library50 service50", 18),
        ["model50 token50", "prompt50 session50", "library50", "service50"],
    ),
    (
        ("model50 token50 prompt50 session50 library50 service50", 28),
        ["model50 token50 prompt50", "session50 library50", "service50"],
    ),
    (
        ("token50 prompt50 session50 library50 service50 gateway50", 6),
        ["token50", "prompt50", "session50", "library50", "service50", "gateway50"],
    ),
    (
        ("token50 prompt50 session50 library50 service50 gateway50", 10),
        ["token50", "prompt50", "session50", "library50", "service50", "gateway50"],
    ),
    (
        ("token50 prompt50 session50 library50 service50 gateway50", 18),
        ["token50 prompt50", "session50", "library50", "service50", "gateway50"],
    ),
    (
        ("token50 prompt50 session50 library50 service50 gateway50", 28),
        ["token50 prompt50 session50", "library50 service50", "gateway50"],
    ),
    (
        ("prompt50 session50 library50 service50 gateway50 storage50", 6),
        ["prompt50", "session50", "library50", "service50", "gateway50", "storage50"],
    ),
    (
        ("prompt50 session50 library50 service50 gateway50 storage50", 10),
        ["prompt50", "session50", "library50", "service50", "gateway50", "storage50"],
    ),
    (
        ("prompt50 session50 library50 service50 gateway50 storage50", 18),
        ["prompt50 session50", "library50", "service50", "gateway50", "storage50"],
    ),
    (
        ("prompt50 session50 library50 service50 gateway50 storage50", 28),
        ["prompt50 session50 library50", "service50 gateway50", "storage50"],
    ),
    (
        ("session50 library50 service50 gateway50 storage50 network50", 6),
        ["session50", "library50", "service50", "gateway50", "storage50", "network50"],
    ),
    (
        ("session50 library50 service50 gateway50 storage50 network50", 10),
        ["session50", "library50", "service50", "gateway50", "storage50", "network50"],
    ),
    (
        ("session50 library50 service50 gateway50 storage50 network50", 18),
        ["session50", "library50", "service50", "gateway50", "storage50", "network50"],
    ),
    (
        ("session50 library50 service50 gateway50 storage50 network50", 28),
        ["session50 library50", "service50 gateway50", "storage50 network50"],
    ),
    (
        ("library50 service50 gateway50 storage50 network50 latency50", 6),
        ["library50", "service50", "gateway50", "storage50", "network50", "latency50"],
    ),
    (
        ("library50 service50 gateway50 storage50 network50 latency50", 10),
        ["library50", "service50", "gateway50", "storage50", "network50", "latency50"],
    ),
    (
        ("library50 service50 gateway50 storage50 network50 latency50", 18),
        ["library50", "service50", "gateway50", "storage50", "network50", "latency50"],
    ),
    (
        ("library50 service50 gateway50 storage50 network50 latency50", 28),
        ["library50 service50", "gateway50 storage50", "network50 latency50"],
    ),
    (
        ("service50 gateway50 storage50 network50 latency50 buffer50", 6),
        ["service50", "gateway50", "storage50", "network50", "latency50", "buffer50"],
    ),
    (
        ("service50 gateway50 storage50 network50 latency50 buffer50", 10),
        ["service50", "gateway50", "storage50", "network50", "latency50", "buffer50"],
    ),
    (
        ("service50 gateway50 storage50 network50 latency50 buffer50", 18),
        ["service50", "gateway50", "storage50", "network50", "latency50 buffer50"],
    ),
    (
        ("service50 gateway50 storage50 network50 latency50 buffer50", 28),
        ["service50 gateway50", "storage50 network50", "latency50 buffer50"],
    ),
    (
        ("gateway50 storage50 network50 latency50 buffer50 queue50", 6),
        ["gateway50", "storage50", "network50", "latency50", "buffer50", "queue50"],
    ),
    (
        ("gateway50 storage50 network50 latency50 buffer50 queue50", 10),
        ["gateway50", "storage50", "network50", "latency50", "buffer50", "queue50"],
    ),
    (
        ("gateway50 storage50 network50 latency50 buffer50 queue50", 18),
        ["gateway50", "storage50", "network50", "latency50 buffer50", "queue50"],
    ),
    (
        ("gateway50 storage50 network50 latency50 buffer50 queue50", 28),
        ["gateway50 storage50", "network50 latency50 buffer50", "queue50"],
    ),
    (
        ("storage50 network50 latency50 buffer50 queue50 worker50", 6),
        ["storage50", "network50", "latency50", "buffer50", "queue50", "worker50"],
    ),
    (
        ("storage50 network50 latency50 buffer50 queue50 worker50", 10),
        ["storage50", "network50", "latency50", "buffer50", "queue50", "worker50"],
    ),
    (
        ("storage50 network50 latency50 buffer50 queue50 worker50", 18),
        ["storage50", "network50", "latency50 buffer50", "queue50 worker50"],
    ),
    (
        ("storage50 network50 latency50 buffer50 queue50 worker50", 28),
        ["storage50 network50", "latency50 buffer50 queue50", "worker50"],
    ),
    (
        ("network50 latency50 buffer50 queue50 worker50 kernel50", 6),
        ["network50", "latency50", "buffer50", "queue50", "worker50", "kernel50"],
    ),
    (
        ("network50 latency50 buffer50 queue50 worker50 kernel50", 10),
        ["network50", "latency50", "buffer50", "queue50", "worker50", "kernel50"],
    ),
    (
        ("network50 latency50 buffer50 queue50 worker50 kernel50", 18),
        ["network50", "latency50 buffer50", "queue50 worker50", "kernel50"],
    ),
    (
        ("network50 latency50 buffer50 queue50 worker50 kernel50", 28),
        ["network50 latency50 buffer50", "queue50 worker50 kernel50"],
    ),
    (
        ("latency50 buffer50 queue50 worker50 kernel50 signal50", 6),
        ["latency50", "buffer50", "queue50", "worker50", "kernel50", "signal50"],
    ),
    (
        ("latency50 buffer50 queue50 worker50 kernel50 signal50", 10),
        ["latency50", "buffer50", "queue50", "worker50", "kernel50", "signal50"],
    ),
    (
        ("latency50 buffer50 queue50 worker50 kernel50 signal50", 18),
        ["latency50 buffer50", "queue50 worker50", "kernel50 signal50"],
    ),
    (
        ("latency50 buffer50 queue50 worker50 kernel50 signal50", 28),
        ["latency50 buffer50 queue50", "worker50 kernel50 signal50"],
    ),
    (
        ("buffer50 queue50 worker50 kernel50 signal50 packet50", 6),
        ["buffer50", "queue50", "worker50", "kernel50", "signal50", "packet50"],
    ),
    (
        ("buffer50 queue50 worker50 kernel50 signal50 packet50", 10),
        ["buffer50", "queue50", "worker50", "kernel50", "signal50", "packet50"],
    ),
    (
        ("buffer50 queue50 worker50 kernel50 signal50 packet50", 18),
        ["buffer50 queue50", "worker50 kernel50", "signal50 packet50"],
    ),
    (
        ("buffer50 queue50 worker50 kernel50 signal50 packet50", 28),
        ["buffer50 queue50 worker50", "kernel50 signal50 packet50"],
    ),
    (
        ("queue50 worker50 kernel50 signal50 packet50 router50", 6),
        ["queue50", "worker50", "kernel50", "signal50", "packet50", "router50"],
    ),
    (
        ("queue50 worker50 kernel50 signal50 packet50 router50", 10),
        ["queue50", "worker50", "kernel50", "signal50", "packet50", "router50"],
    ),
    (
        ("queue50 worker50 kernel50 signal50 packet50 router50", 18),
        ["queue50 worker50", "kernel50 signal50", "packet50 router50"],
    ),
    (
        ("queue50 worker50 kernel50 signal50 packet50 router50", 28),
        ["queue50 worker50 kernel50", "signal50 packet50 router50"],
    ),
    (
        ("worker50 kernel50 signal50 packet50 router50 cluster50", 6),
        ["worker50", "kernel50", "signal50", "packet50", "router50", "cluster50"],
    ),
    (
        ("worker50 kernel50 signal50 packet50 router50 cluster50", 10),
        ["worker50", "kernel50", "signal50", "packet50", "router50", "cluster50"],
    ),
    (
        ("worker50 kernel50 signal50 packet50 router50 cluster50", 18),
        ["worker50 kernel50", "signal50 packet50", "router50 cluster50"],
    ),
    (
        ("worker50 kernel50 signal50 packet50 router50 cluster50", 28),
        ["worker50 kernel50 signal50", "packet50 router50 cluster50"],
    ),
    (
        ("kernel50 signal50 packet50 router50 cluster50 mirror50", 6),
        ["kernel50", "signal50", "packet50", "router50", "cluster50", "mirror50"],
    ),
    (
        ("kernel50 signal50 packet50 router50 cluster50 mirror50", 10),
        ["kernel50", "signal50", "packet50", "router50", "cluster50", "mirror50"],
    ),
    (
        ("kernel50 signal50 packet50 router50 cluster50 mirror50", 18),
        ["kernel50 signal50", "packet50 router50", "cluster50 mirror50"],
    ),
    (
        ("kernel50 signal50 packet50 router50 cluster50 mirror50", 28),
        ["kernel50 signal50 packet50", "router50 cluster50 mirror50"],
    ),
    (
        ("signal50 packet50 router50 cluster50 mirror50 filter50", 6),
        ["signal50", "packet50", "router50", "cluster50", "mirror50", "filter50"],
    ),
    (
        ("signal50 packet50 router50 cluster50 mirror50 filter50", 10),
        ["signal50", "packet50", "router50", "cluster50", "mirror50", "filter50"],
    ),
    (
        ("signal50 packet50 router50 cluster50 mirror50 filter50", 18),
        ["signal50 packet50", "router50 cluster50", "mirror50 filter50"],
    ),
    (
        ("signal50 packet50 router50 cluster50 mirror50 filter50", 28),
        ["signal50 packet50 router50", "cluster50 mirror50 filter50"],
    ),
    (
        ("packet50 router50 cluster50 mirror50 filter50 ranking50", 6),
        ["packet50", "router50", "cluster50", "mirror50", "filter50", "ranking50"],
    ),
    (
        ("packet50 router50 cluster50 mirror50 filter50 ranking50", 10),
        ["packet50", "router50", "cluster50", "mirror50", "filter50", "ranking50"],
    ),
    (
        ("packet50 router50 cluster50 mirror50 filter50 ranking50", 18),
        ["packet50 router50", "cluster50 mirror50", "filter50 ranking50"],
    ),
    (
        ("packet50 router50 cluster50 mirror50 filter50 ranking50", 28),
        ["packet50 router50 cluster50", "mirror50 filter50 ranking50"],
    ),
    (
        ("router50 cluster50 mirror50 filter50 ranking50 encoding50", 6),
        ["router50", "cluster50", "mirror50", "filter50", "ranking50", "encoding50"],
    ),
    (
        ("router50 cluster50 mirror50 filter50 ranking50 encoding50", 10),
        ["router50", "cluster50", "mirror50", "filter50", "ranking50", "encoding50"],
    ),
    (
        ("router50 cluster50 mirror50 filter50 ranking50 encoding50", 18),
        ["router50 cluster50", "mirror50 filter50", "ranking50", "encoding50"],
    ),
    (
        ("router50 cluster50 mirror50 filter50 ranking50 encoding50", 28),
        ["router50 cluster50 mirror50", "filter50 ranking50", "encoding50"],
    ),
    (
        ("cluster50 mirror50 filter50 ranking50 encoding50 mapping50", 6),
        ["cluster50", "mirror50", "filter50", "ranking50", "encoding50", "mapping50"],
    ),
    (
        ("cluster50 mirror50 filter50 ranking50 encoding50 mapping50", 10),
        ["cluster50", "mirror50", "filter50", "ranking50", "encoding50", "mapping50"],
    ),
    (
        ("cluster50 mirror50 filter50 ranking50 encoding50 mapping50", 18),
        ["cluster50 mirror50", "filter50 ranking50", "encoding50", "mapping50"],
    ),
    (
        ("cluster50 mirror50 filter50 ranking50 encoding50 mapping50", 28),
        ["cluster50 mirror50 filter50", "ranking50 encoding50", "mapping50"],
    ),
    (
        ("mirror50 filter50 ranking50 encoding50 mapping50 record50", 6),
        ["mirror50", "filter50", "ranking50", "encoding50", "mapping50", "record50"],
    ),
    (
        ("mirror50 filter50 ranking50 encoding50 mapping50 record50", 10),
        ["mirror50", "filter50", "ranking50", "encoding50", "mapping50", "record50"],
    ),
    (
        ("mirror50 filter50 ranking50 encoding50 mapping50 record50", 18),
        ["mirror50 filter50", "ranking50", "encoding50", "mapping50 record50"],
    ),
    (
        ("mirror50 filter50 ranking50 encoding50 mapping50 record50", 28),
        ["mirror50 filter50 ranking50", "encoding50 mapping50", "record50"],
    ),
    (
        ("filter50 ranking50 encoding50 mapping50 record50 candle50", 6),
        ["filter50", "ranking50", "encoding50", "mapping50", "record50", "candle50"],
    ),
    (
        ("filter50 ranking50 encoding50 mapping50 record50 candle50", 10),
        ["filter50", "ranking50", "encoding50", "mapping50", "record50", "candle50"],
    ),
    (
        ("filter50 ranking50 encoding50 mapping50 record50 candle50", 18),
        ["filter50 ranking50", "encoding50", "mapping50 record50", "candle50"],
    ),
    (
        ("filter50 ranking50 encoding50 mapping50 record50 candle50", 28),
        ["filter50 ranking50", "encoding50 mapping50", "record50 candle50"],
    ),
    (
        ("ranking50 encoding50 mapping50 record50 candle50 thread50", 6),
        ["ranking50", "encoding50", "mapping50", "record50", "candle50", "thread50"],
    ),
    (
        ("ranking50 encoding50 mapping50 record50 candle50 thread50", 10),
        ["ranking50", "encoding50", "mapping50", "record50", "candle50", "thread50"],
    ),
    (
        ("ranking50 encoding50 mapping50 record50 candle50 thread50", 18),
        ["ranking50", "encoding50", "mapping50 record50", "candle50 thread50"],
    ),
    (
        ("ranking50 encoding50 mapping50 record50 candle50 thread50", 28),
        ["ranking50 encoding50", "mapping50 record50 candle50", "thread50"],
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
