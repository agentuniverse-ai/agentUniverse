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
        ("round 153: the quick brown fox jumps over the lazy dog", 4),
        ["round", "153:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 153: the quick brown fox jumps over the lazy dog", 8),
        ["round", "153: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 153: the quick brown fox jumps over the lazy dog", 12),
        ["round 153:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 153: the quick brown fox jumps over the lazy dog", 16),
        ["round 153: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 153: the quick brown fox jumps over the lazy dog", 24),
        ["round 153: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 153: the quick brown fox jumps over the lazy dog", 32),
        ["round 153: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 153: agentuniverse is a framework for multi agents", 4),
        ["round", "153:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 153: agentuniverse is a framework for multi agents", 8),
        ["round", "153:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 153: agentuniverse is a framework for multi agents", 12),
        ["round 153:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 153: agentuniverse is a framework for multi agents", 16),
        ["round 153:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 153: agentuniverse is a framework for multi agents", 24),
        ["round 153: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 153: agentuniverse is a framework for multi agents", 32),
        ["round 153: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 153: knowledge stored as vectors enables retrieval", 4),
        ["round", "153:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 153: knowledge stored as vectors enables retrieval", 8),
        ["round", "153:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 153: knowledge stored as vectors enables retrieval", 12),
        ["round 153:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 153: knowledge stored as vectors enables retrieval", 16),
        ["round 153:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 153: knowledge stored as vectors enables retrieval", 24),
        ["round 153: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 153: knowledge stored as vectors enables retrieval", 32),
        ["round 153: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 153: the processor reads the record then stops", 4),
        ["round", "153:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 153: the processor reads the record then stops", 8),
        ["round", "153: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 153: the processor reads the record then stops", 12),
        ["round 153:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 153: the processor reads the record then stops", 16),
        ["round 153: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 153: the processor reads the record then stops", 24),
        ["round 153: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 153: the processor reads the record then stops", 32),
        ["round 153: the processor reads", "the record then stops"],
    ),
    (
        ("round 153: a worker pulls the next task from the queue", 4),
        ["round", "153:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 153: a worker pulls the next task from the queue", 8),
        ["round", "153: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 153: a worker pulls the next task from the queue", 12),
        ["round 153: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 153: a worker pulls the next task from the queue", 16),
        ["round 153: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 153: a worker pulls the next task from the queue", 24),
        ["round 153: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 153: a worker pulls the next task from the queue", 32),
        ["round 153: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 153: signals travel through the network layer", 4),
        ["round", "153:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 153: signals travel through the network layer", 8),
        ["round", "153:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 153: signals travel through the network layer", 12),
        ["round 153:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 153: signals travel through the network layer", 16),
        ["round 153:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 153: signals travel through the network layer", 24),
        ["round 153: signals", "travel through the", "network layer"],
    ),
    (
        ("round 153: signals travel through the network layer", 32),
        ["round 153: signals travel", "through the network layer"],
    ),
    (
        ("round 153: the gateway routes each request by policy", 4),
        ["round", "153:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 153: the gateway routes each request by policy", 8),
        ["round", "153: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 153: the gateway routes each request by policy", 12),
        ["round 153:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 153: the gateway routes each request by policy", 16),
        ["round 153: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 153: the gateway routes each request by policy", 24),
        ["round 153: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 153: the gateway routes each request by policy", 32),
        ["round 153: the gateway routes", "each request by policy"],
    ),
    (
        ("round 153: memory grows until the buffer is full", 4),
        ["round", "153:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 153: memory grows until the buffer is full", 8),
        ["round", "153:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 153: memory grows until the buffer is full", 12),
        ["round 153:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 153: memory grows until the buffer is full", 16),
        ["round 153:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 153: memory grows until the buffer is full", 24), ["round 153: memory grows", "until the buffer is full"]),
    (("round 153: memory grows until the buffer is full", 32), ["round 153: memory grows until", "the buffer is full"]),
    (
        ("round 153: the cluster mirrors every packet twice", 4),
        ["round", "153:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 153: the cluster mirrors every packet twice", 8),
        ["round", "153: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 153: the cluster mirrors every packet twice", 12),
        ["round 153:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 153: the cluster mirrors every packet twice", 16),
        ["round 153: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 153: the cluster mirrors every packet twice", 24),
        ["round 153: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 153: the cluster mirrors every packet twice", 32),
        ["round 153: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 153: ranking uses tokens learned from the corpus", 4),
        ["round", "153:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 153: ranking uses tokens learned from the corpus", 8),
        ["round", "153:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 153: ranking uses tokens learned from the corpus", 12),
        ["round 153:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 153: ranking uses tokens learned from the corpus", 16),
        ["round 153:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 153: ranking uses tokens learned from the corpus", 24),
        ["round 153: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 153: ranking uses tokens learned from the corpus", 32),
        ["round 153: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 153: a long session ends when the candle dies", 4),
        ["round", "153:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 153: a long session ends when the candle dies", 8),
        ["round", "153: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 153: a long session ends when the candle dies", 12),
        ["round 153: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 153: a long session ends when the candle dies", 16),
        ["round 153: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 153: a long session ends when the candle dies", 24),
        ["round 153: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 153: a long session ends when the candle dies", 32),
        ["round 153: a long session ends", "when the candle dies"],
    ),
    (
        ("round 153: encode the prompt then map the result", 4),
        ["round", "153:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 153: encode the prompt then map the result", 8),
        ["round", "153:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 153: encode the prompt then map the result", 12),
        ["round 153:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 153: encode the prompt then map the result", 16),
        ["round 153:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 153: encode the prompt then map the result", 24),
        ["round 153: encode the", "prompt then map the", "result"],
    ),
    (("round 153: encode the prompt then map the result", 32), ["round 153: encode the prompt", "then map the result"]),
    (
        ("round 153: the kernel wakes the worker at dawn", 4),
        ["round", "153:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 153: the kernel wakes the worker at dawn", 8),
        ["round", "153: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 153: the kernel wakes the worker at dawn", 12),
        ["round 153:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 153: the kernel wakes the worker at dawn", 16), ["round 153: the", "kernel wakes the", "worker at dawn"]),
    (("round 153: the kernel wakes the worker at dawn", 24), ["round 153: the kernel", "wakes the worker at dawn"]),
    (("round 153: the kernel wakes the worker at dawn", 32), ["round 153: the kernel wakes the", "worker at dawn"]),
    (
        ("round 153: service latency drops after the patch", 4),
        ["round", "153:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 153: service latency drops after the patch", 8),
        ["round", "153:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 153: service latency drops after the patch", 12),
        ["round 153:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 153: service latency drops after the patch", 16),
        ["round 153:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 153: service latency drops after the patch", 24),
        ["round 153: service", "latency drops after the", "patch"],
    ),
    (("round 153: service latency drops after the patch", 32), ["round 153: service latency drops", "after the patch"]),
    (
        ("round 153: the library caches every vector it sees", 4),
        ["round", "153:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 153: the library caches every vector it sees", 8),
        ["round", "153: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 153: the library caches every vector it sees", 12),
        ["round 153:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 153: the library caches every vector it sees", 16),
        ["round 153: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 153: the library caches every vector it sees", 24),
        ["round 153: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 153: the library caches every vector it sees", 32),
        ["round 153: the library caches", "every vector it sees"],
    ),
    (
        ("round 153: agents argue then the debate resolves", 4),
        ["round", "153:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 153: agents argue then the debate resolves", 8),
        ["round", "153:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 153: agents argue then the debate resolves", 12),
        ["round 153:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 153: agents argue then the debate resolves", 16),
        ["round 153:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 153: agents argue then the debate resolves", 24), ["round 153: agents argue", "then the debate resolves"]),
    (("round 153: agents argue then the debate resolves", 32), ["round 153: agents argue then the", "debate resolves"]),
    (
        ("round 153: the filter keeps only strong matches", 4),
        ["round", "153:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 153: the filter keeps only strong matches", 8),
        ["round", "153: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 153: the filter keeps only strong matches", 12),
        ["round 153:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 153: the filter keeps only strong matches", 16),
        ["round 153: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 153: the filter keeps only strong matches", 24),
        ["round 153: the filter", "keeps only strong", "matches"],
    ),
    (("round 153: the filter keeps only strong matches", 32), ["round 153: the filter keeps only", "strong matches"]),
    (
        ("round 153: the model answers with a short reply", 4),
        ["round", "153:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 153: the model answers with a short reply", 8),
        ["round", "153: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 153: the model answers with a short reply", 12),
        ["round 153:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 153: the model answers with a short reply", 16),
        ["round 153: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 153: the model answers with a short reply", 24),
        ["round 153: the model", "answers with a short", "reply"],
    ),
    (("round 153: the model answers with a short reply", 32), ["round 153: the model answers", "with a short reply"]),
    (
        ("round 153: the recorder stores the reasoning trace", 4),
        ["round", "153:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 153: the recorder stores the reasoning trace", 8),
        ["round", "153: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 153: the recorder stores the reasoning trace", 12),
        ["round 153:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 153: the recorder stores the reasoning trace", 16),
        ["round 153: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 153: the recorder stores the reasoning trace", 24),
        ["round 153: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 153: the recorder stores the reasoning trace", 32),
        ["round 153: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 153: the angel watches the processor run", 4),
        ["round", "153:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 153: the angel watches the processor run", 8),
        ["round", "153: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 153: the angel watches the processor run", 12),
        ["round 153:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 153: the angel watches the processor run", 16),
        ["round 153: the", "angel watches", "the processor", "run"],
    ),
    (("round 153: the angel watches the processor run", 24), ["round 153: the angel", "watches the processor", "run"]),
    (("round 153: the angel watches the processor run", 32), ["round 153: the angel watches the", "processor run"]),
    (
        ("round 153: angle of the vector decides the match", 4),
        ["round", "153:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 153: angle of the vector decides the match", 8),
        ["round", "153:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 153: angle of the vector decides the match", 12),
        ["round 153:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 153: angle of the vector decides the match", 16),
        ["round 153: angle", "of the vector", "decides the", "match"],
    ),
    (("round 153: angle of the vector decides the match", 24), ["round 153: angle of the", "vector decides the match"]),
    (("round 153: angle of the vector decides the match", 32), ["round 153: angle of the vector", "decides the match"]),
    (
        ("round 153: the candle burns twice as long at night", 4),
        ["round", "153:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 153: the candle burns twice as long at night", 8),
        ["round", "153: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 153: the candle burns twice as long at night", 12),
        ["round 153:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 153: the candle burns twice as long at night", 16),
        ["round 153: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 153: the candle burns twice as long at night", 24),
        ["round 153: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 153: the candle burns twice as long at night", 32),
        ["round 153: the candle burns", "twice as long at night"],
    ),
    (
        ("round 153: a mirror of the universe in one line", 4),
        ["round", "153:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 153: a mirror of the universe in one line", 8),
        ["round", "153: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 153: a mirror of the universe in one line", 12),
        ["round 153: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 153: a mirror of the universe in one line", 16),
        ["round 153: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 153: a mirror of the universe in one line", 24), ["round 153: a mirror of", "the universe in one line"]),
    (("round 153: a mirror of the universe in one line", 32), ["round 153: a mirror of the", "universe in one line"]),
    (
        ("round 153: the queue drains before the storm", 4),
        ["round", "153:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 153: the queue drains before the storm", 8),
        ["round", "153: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 153: the queue drains before the storm", 12),
        ["round 153:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 153: the queue drains before the storm", 16), ["round 153: the", "queue drains", "before the storm"]),
    (("round 153: the queue drains before the storm", 24), ["round 153: the queue", "drains before the storm"]),
    (("round 153: the queue drains before the storm", 32), ["round 153: the queue drains", "before the storm"]),
    (
        ("kitten153 sitting153 agent153 angle153 universe153 memory153", 6),
        ["kitten153", "sitting153", "agent153", "angle153", "universe153", "memory153"],
    ),
    (
        ("kitten153 sitting153 agent153 angle153 universe153 memory153", 10),
        ["kitten153", "sitting153", "agent153", "angle153", "universe153", "memory153"],
    ),
    (
        ("kitten153 sitting153 agent153 angle153 universe153 memory153", 18),
        ["kitten153", "sitting153", "agent153 angle153", "universe153", "memory153"],
    ),
    (
        ("kitten153 sitting153 agent153 angle153 universe153 memory153", 28),
        ["kitten153 sitting153", "agent153 angle153", "universe153 memory153"],
    ),
    (
        ("sitting153 agent153 angle153 universe153 memory153 stream153", 6),
        ["sitting153", "agent153", "angle153", "universe153", "memory153", "stream153"],
    ),
    (
        ("sitting153 agent153 angle153 universe153 memory153 stream153", 10),
        ["sitting153", "agent153", "angle153", "universe153", "memory153", "stream153"],
    ),
    (
        ("sitting153 agent153 angle153 universe153 memory153 stream153", 18),
        ["sitting153", "agent153 angle153", "universe153", "memory153", "stream153"],
    ),
    (
        ("sitting153 agent153 angle153 universe153 memory153 stream153", 28),
        ["sitting153 agent153 angle153", "universe153 memory153", "stream153"],
    ),
    (
        ("agent153 angle153 universe153 memory153 stream153 context153", 6),
        ["agent153", "angle153", "universe153", "memory153", "stream153", "context153"],
    ),
    (
        ("agent153 angle153 universe153 memory153 stream153 context153", 10),
        ["agent153", "angle153", "universe153", "memory153", "stream153", "context153"],
    ),
    (
        ("agent153 angle153 universe153 memory153 stream153 context153", 18),
        ["agent153 angle153", "universe153", "memory153", "stream153", "context153"],
    ),
    (
        ("agent153 angle153 universe153 memory153 stream153 context153", 28),
        ["agent153 angle153", "universe153 memory153", "stream153 context153"],
    ),
    (
        ("angle153 universe153 memory153 stream153 context153 knowledge153", 6),
        ["angle153", "universe153", "memory153", "stream153", "context153", "knowledge153"],
    ),
    (
        ("angle153 universe153 memory153 stream153 context153 knowledge153", 10),
        ["angle153", "universe153", "memory153", "stream153", "context153", "knowledge153"],
    ),
    (
        ("angle153 universe153 memory153 stream153 context153 knowledge153", 18),
        ["angle153", "universe153", "memory153", "stream153", "context153", "knowledge153"],
    ),
    (
        ("angle153 universe153 memory153 stream153 context153 knowledge153", 28),
        ["angle153 universe153", "memory153 stream153", "context153 knowledge153"],
    ),
    (
        ("universe153 memory153 stream153 context153 knowledge153 vector153", 6),
        ["universe153", "memory153", "stream153", "context153", "knowledge153", "vector153"],
    ),
    (
        ("universe153 memory153 stream153 context153 knowledge153 vector153", 10),
        ["universe153", "memory153", "stream153", "context153", "knowledge153", "vector153"],
    ),
    (
        ("universe153 memory153 stream153 context153 knowledge153 vector153", 18),
        ["universe153", "memory153", "stream153", "context153", "knowledge153", "vector153"],
    ),
    (
        ("universe153 memory153 stream153 context153 knowledge153 vector153", 28),
        ["universe153 memory153", "stream153 context153", "knowledge153 vector153"],
    ),
    (
        ("memory153 stream153 context153 knowledge153 vector153 processor153", 6),
        ["memory153", "stream153", "context153", "knowledge153", "vector153", "processor153"],
    ),
    (
        ("memory153 stream153 context153 knowledge153 vector153 processor153", 10),
        ["memory153", "stream153", "context153", "knowledge153", "vector153", "processor153"],
    ),
    (
        ("memory153 stream153 context153 knowledge153 vector153 processor153", 18),
        ["memory153", "stream153", "context153", "knowledge153", "vector153", "processor153"],
    ),
    (
        ("memory153 stream153 context153 knowledge153 vector153 processor153", 28),
        ["memory153 stream153", "context153 knowledge153", "vector153 processor153"],
    ),
    (
        ("stream153 context153 knowledge153 vector153 processor153 reasoning153", 6),
        ["stream153", "context153", "knowledge153", "vector153", "processor153", "reasoning153"],
    ),
    (
        ("stream153 context153 knowledge153 vector153 processor153 reasoning153", 10),
        ["stream153", "context153", "knowledge153", "vector153", "processor153", "reasoning153"],
    ),
    (
        ("stream153 context153 knowledge153 vector153 processor153 reasoning153", 18),
        ["stream153", "context153", "knowledge153", "vector153", "processor153", "reasoning153"],
    ),
    (
        ("stream153 context153 knowledge153 vector153 processor153 reasoning153", 28),
        ["stream153 context153", "knowledge153 vector153", "processor153 reasoning153"],
    ),
    (
        ("context153 knowledge153 vector153 processor153 reasoning153 machine153", 6),
        ["context153", "knowledge153", "vector153", "processor153", "reasoning153", "machine153"],
    ),
    (
        ("context153 knowledge153 vector153 processor153 reasoning153 machine153", 10),
        ["context153", "knowledge153", "vector153", "processor153", "reasoning153", "machine153"],
    ),
    (
        ("context153 knowledge153 vector153 processor153 reasoning153 machine153", 18),
        ["context153", "knowledge153", "vector153", "processor153", "reasoning153", "machine153"],
    ),
    (
        ("context153 knowledge153 vector153 processor153 reasoning153 machine153", 28),
        ["context153 knowledge153", "vector153 processor153", "reasoning153 machine153"],
    ),
    (
        ("knowledge153 vector153 processor153 reasoning153 machine153 learning153", 6),
        ["knowledge153", "vector153", "processor153", "reasoning153", "machine153", "learning153"],
    ),
    (
        ("knowledge153 vector153 processor153 reasoning153 machine153 learning153", 10),
        ["knowledge153", "vector153", "processor153", "reasoning153", "machine153", "learning153"],
    ),
    (
        ("knowledge153 vector153 processor153 reasoning153 machine153 learning153", 18),
        ["knowledge153", "vector153", "processor153", "reasoning153", "machine153", "learning153"],
    ),
    (
        ("knowledge153 vector153 processor153 reasoning153 machine153 learning153", 28),
        ["knowledge153 vector153", "processor153 reasoning153", "machine153 learning153"],
    ),
    (
        ("vector153 processor153 reasoning153 machine153 learning153 model153", 6),
        ["vector153", "processor153", "reasoning153", "machine153", "learning153", "model153"],
    ),
    (
        ("vector153 processor153 reasoning153 machine153 learning153 model153", 10),
        ["vector153", "processor153", "reasoning153", "machine153", "learning153", "model153"],
    ),
    (
        ("vector153 processor153 reasoning153 machine153 learning153 model153", 18),
        ["vector153", "processor153", "reasoning153", "machine153", "learning153", "model153"],
    ),
    (
        ("vector153 processor153 reasoning153 machine153 learning153 model153", 28),
        ["vector153 processor153", "reasoning153 machine153", "learning153 model153"],
    ),
    (
        ("processor153 reasoning153 machine153 learning153 model153 token153", 6),
        ["processor153", "reasoning153", "machine153", "learning153", "model153", "token153"],
    ),
    (
        ("processor153 reasoning153 machine153 learning153 model153 token153", 10),
        ["processor153", "reasoning153", "machine153", "learning153", "model153", "token153"],
    ),
    (
        ("processor153 reasoning153 machine153 learning153 model153 token153", 18),
        ["processor153", "reasoning153", "machine153", "learning153", "model153 token153"],
    ),
    (
        ("processor153 reasoning153 machine153 learning153 model153 token153", 28),
        ["processor153 reasoning153", "machine153 learning153", "model153 token153"],
    ),
    (
        ("reasoning153 machine153 learning153 model153 token153 prompt153", 6),
        ["reasoning153", "machine153", "learning153", "model153", "token153", "prompt153"],
    ),
    (
        ("reasoning153 machine153 learning153 model153 token153 prompt153", 10),
        ["reasoning153", "machine153", "learning153", "model153", "token153", "prompt153"],
    ),
    (
        ("reasoning153 machine153 learning153 model153 token153 prompt153", 18),
        ["reasoning153", "machine153", "learning153", "model153 token153", "prompt153"],
    ),
    (
        ("reasoning153 machine153 learning153 model153 token153 prompt153", 28),
        ["reasoning153 machine153", "learning153 model153", "token153 prompt153"],
    ),
    (
        ("machine153 learning153 model153 token153 prompt153 session153", 6),
        ["machine153", "learning153", "model153", "token153", "prompt153", "session153"],
    ),
    (
        ("machine153 learning153 model153 token153 prompt153 session153", 10),
        ["machine153", "learning153", "model153", "token153", "prompt153", "session153"],
    ),
    (
        ("machine153 learning153 model153 token153 prompt153 session153", 18),
        ["machine153", "learning153", "model153 token153", "prompt153", "session153"],
    ),
    (
        ("machine153 learning153 model153 token153 prompt153 session153", 28),
        ["machine153 learning153", "model153 token153 prompt153", "session153"],
    ),
    (
        ("learning153 model153 token153 prompt153 session153 library153", 6),
        ["learning153", "model153", "token153", "prompt153", "session153", "library153"],
    ),
    (
        ("learning153 model153 token153 prompt153 session153 library153", 10),
        ["learning153", "model153", "token153", "prompt153", "session153", "library153"],
    ),
    (
        ("learning153 model153 token153 prompt153 session153 library153", 18),
        ["learning153", "model153 token153", "prompt153", "session153", "library153"],
    ),
    (
        ("learning153 model153 token153 prompt153 session153 library153", 28),
        ["learning153 model153", "token153 prompt153", "session153 library153"],
    ),
    (
        ("model153 token153 prompt153 session153 library153 service153", 6),
        ["model153", "token153", "prompt153", "session153", "library153", "service153"],
    ),
    (
        ("model153 token153 prompt153 session153 library153 service153", 10),
        ["model153", "token153", "prompt153", "session153", "library153", "service153"],
    ),
    (
        ("model153 token153 prompt153 session153 library153 service153", 18),
        ["model153 token153", "prompt153", "session153", "library153", "service153"],
    ),
    (
        ("model153 token153 prompt153 session153 library153 service153", 28),
        ["model153 token153 prompt153", "session153 library153", "service153"],
    ),
    (
        ("token153 prompt153 session153 library153 service153 gateway153", 6),
        ["token153", "prompt153", "session153", "library153", "service153", "gateway153"],
    ),
    (
        ("token153 prompt153 session153 library153 service153 gateway153", 10),
        ["token153", "prompt153", "session153", "library153", "service153", "gateway153"],
    ),
    (
        ("token153 prompt153 session153 library153 service153 gateway153", 18),
        ["token153 prompt153", "session153", "library153", "service153", "gateway153"],
    ),
    (
        ("token153 prompt153 session153 library153 service153 gateway153", 28),
        ["token153 prompt153", "session153 library153", "service153 gateway153"],
    ),
    (
        ("prompt153 session153 library153 service153 gateway153 storage153", 6),
        ["prompt153", "session153", "library153", "service153", "gateway153", "storage153"],
    ),
    (
        ("prompt153 session153 library153 service153 gateway153 storage153", 10),
        ["prompt153", "session153", "library153", "service153", "gateway153", "storage153"],
    ),
    (
        ("prompt153 session153 library153 service153 gateway153 storage153", 18),
        ["prompt153", "session153", "library153", "service153", "gateway153", "storage153"],
    ),
    (
        ("prompt153 session153 library153 service153 gateway153 storage153", 28),
        ["prompt153 session153", "library153 service153", "gateway153 storage153"],
    ),
    (
        ("session153 library153 service153 gateway153 storage153 network153", 6),
        ["session153", "library153", "service153", "gateway153", "storage153", "network153"],
    ),
    (
        ("session153 library153 service153 gateway153 storage153 network153", 10),
        ["session153", "library153", "service153", "gateway153", "storage153", "network153"],
    ),
    (
        ("session153 library153 service153 gateway153 storage153 network153", 18),
        ["session153", "library153", "service153", "gateway153", "storage153", "network153"],
    ),
    (
        ("session153 library153 service153 gateway153 storage153 network153", 28),
        ["session153 library153", "service153 gateway153", "storage153 network153"],
    ),
    (
        ("library153 service153 gateway153 storage153 network153 latency153", 6),
        ["library153", "service153", "gateway153", "storage153", "network153", "latency153"],
    ),
    (
        ("library153 service153 gateway153 storage153 network153 latency153", 10),
        ["library153", "service153", "gateway153", "storage153", "network153", "latency153"],
    ),
    (
        ("library153 service153 gateway153 storage153 network153 latency153", 18),
        ["library153", "service153", "gateway153", "storage153", "network153", "latency153"],
    ),
    (
        ("library153 service153 gateway153 storage153 network153 latency153", 28),
        ["library153 service153", "gateway153 storage153", "network153 latency153"],
    ),
    (
        ("service153 gateway153 storage153 network153 latency153 buffer153", 6),
        ["service153", "gateway153", "storage153", "network153", "latency153", "buffer153"],
    ),
    (
        ("service153 gateway153 storage153 network153 latency153 buffer153", 10),
        ["service153", "gateway153", "storage153", "network153", "latency153", "buffer153"],
    ),
    (
        ("service153 gateway153 storage153 network153 latency153 buffer153", 18),
        ["service153", "gateway153", "storage153", "network153", "latency153", "buffer153"],
    ),
    (
        ("service153 gateway153 storage153 network153 latency153 buffer153", 28),
        ["service153 gateway153", "storage153 network153", "latency153 buffer153"],
    ),
    (
        ("gateway153 storage153 network153 latency153 buffer153 queue153", 6),
        ["gateway153", "storage153", "network153", "latency153", "buffer153", "queue153"],
    ),
    (
        ("gateway153 storage153 network153 latency153 buffer153 queue153", 10),
        ["gateway153", "storage153", "network153", "latency153", "buffer153", "queue153"],
    ),
    (
        ("gateway153 storage153 network153 latency153 buffer153 queue153", 18),
        ["gateway153", "storage153", "network153", "latency153", "buffer153 queue153"],
    ),
    (
        ("gateway153 storage153 network153 latency153 buffer153 queue153", 28),
        ["gateway153 storage153", "network153 latency153", "buffer153 queue153"],
    ),
    (
        ("storage153 network153 latency153 buffer153 queue153 worker153", 6),
        ["storage153", "network153", "latency153", "buffer153", "queue153", "worker153"],
    ),
    (
        ("storage153 network153 latency153 buffer153 queue153 worker153", 10),
        ["storage153", "network153", "latency153", "buffer153", "queue153", "worker153"],
    ),
    (
        ("storage153 network153 latency153 buffer153 queue153 worker153", 18),
        ["storage153", "network153", "latency153", "buffer153 queue153", "worker153"],
    ),
    (
        ("storage153 network153 latency153 buffer153 queue153 worker153", 28),
        ["storage153 network153", "latency153 buffer153", "queue153 worker153"],
    ),
    (
        ("network153 latency153 buffer153 queue153 worker153 kernel153", 6),
        ["network153", "latency153", "buffer153", "queue153", "worker153", "kernel153"],
    ),
    (
        ("network153 latency153 buffer153 queue153 worker153 kernel153", 10),
        ["network153", "latency153", "buffer153", "queue153", "worker153", "kernel153"],
    ),
    (
        ("network153 latency153 buffer153 queue153 worker153 kernel153", 18),
        ["network153", "latency153", "buffer153 queue153", "worker153", "kernel153"],
    ),
    (
        ("network153 latency153 buffer153 queue153 worker153 kernel153", 28),
        ["network153 latency153", "buffer153 queue153 worker153", "kernel153"],
    ),
    (
        ("latency153 buffer153 queue153 worker153 kernel153 signal153", 6),
        ["latency153", "buffer153", "queue153", "worker153", "kernel153", "signal153"],
    ),
    (
        ("latency153 buffer153 queue153 worker153 kernel153 signal153", 10),
        ["latency153", "buffer153", "queue153", "worker153", "kernel153", "signal153"],
    ),
    (
        ("latency153 buffer153 queue153 worker153 kernel153 signal153", 18),
        ["latency153", "buffer153 queue153", "worker153", "kernel153", "signal153"],
    ),
    (
        ("latency153 buffer153 queue153 worker153 kernel153 signal153", 28),
        ["latency153 buffer153", "queue153 worker153 kernel153", "signal153"],
    ),
    (
        ("buffer153 queue153 worker153 kernel153 signal153 packet153", 6),
        ["buffer153", "queue153", "worker153", "kernel153", "signal153", "packet153"],
    ),
    (
        ("buffer153 queue153 worker153 kernel153 signal153 packet153", 10),
        ["buffer153", "queue153", "worker153", "kernel153", "signal153", "packet153"],
    ),
    (
        ("buffer153 queue153 worker153 kernel153 signal153 packet153", 18),
        ["buffer153 queue153", "worker153", "kernel153", "signal153", "packet153"],
    ),
    (
        ("buffer153 queue153 worker153 kernel153 signal153 packet153", 28),
        ["buffer153 queue153 worker153", "kernel153 signal153", "packet153"],
    ),
    (
        ("queue153 worker153 kernel153 signal153 packet153 router153", 6),
        ["queue153", "worker153", "kernel153", "signal153", "packet153", "router153"],
    ),
    (
        ("queue153 worker153 kernel153 signal153 packet153 router153", 10),
        ["queue153", "worker153", "kernel153", "signal153", "packet153", "router153"],
    ),
    (
        ("queue153 worker153 kernel153 signal153 packet153 router153", 18),
        ["queue153 worker153", "kernel153", "signal153", "packet153", "router153"],
    ),
    (
        ("queue153 worker153 kernel153 signal153 packet153 router153", 28),
        ["queue153 worker153 kernel153", "signal153 packet153", "router153"],
    ),
    (
        ("worker153 kernel153 signal153 packet153 router153 cluster153", 6),
        ["worker153", "kernel153", "signal153", "packet153", "router153", "cluster153"],
    ),
    (
        ("worker153 kernel153 signal153 packet153 router153 cluster153", 10),
        ["worker153", "kernel153", "signal153", "packet153", "router153", "cluster153"],
    ),
    (
        ("worker153 kernel153 signal153 packet153 router153 cluster153", 18),
        ["worker153", "kernel153", "signal153", "packet153", "router153", "cluster153"],
    ),
    (
        ("worker153 kernel153 signal153 packet153 router153 cluster153", 28),
        ["worker153 kernel153", "signal153 packet153", "router153 cluster153"],
    ),
    (
        ("kernel153 signal153 packet153 router153 cluster153 mirror153", 6),
        ["kernel153", "signal153", "packet153", "router153", "cluster153", "mirror153"],
    ),
    (
        ("kernel153 signal153 packet153 router153 cluster153 mirror153", 10),
        ["kernel153", "signal153", "packet153", "router153", "cluster153", "mirror153"],
    ),
    (
        ("kernel153 signal153 packet153 router153 cluster153 mirror153", 18),
        ["kernel153", "signal153", "packet153", "router153", "cluster153", "mirror153"],
    ),
    (
        ("kernel153 signal153 packet153 router153 cluster153 mirror153", 28),
        ["kernel153 signal153", "packet153 router153", "cluster153 mirror153"],
    ),
    (
        ("signal153 packet153 router153 cluster153 mirror153 filter153", 6),
        ["signal153", "packet153", "router153", "cluster153", "mirror153", "filter153"],
    ),
    (
        ("signal153 packet153 router153 cluster153 mirror153 filter153", 10),
        ["signal153", "packet153", "router153", "cluster153", "mirror153", "filter153"],
    ),
    (
        ("signal153 packet153 router153 cluster153 mirror153 filter153", 18),
        ["signal153", "packet153", "router153", "cluster153", "mirror153", "filter153"],
    ),
    (
        ("signal153 packet153 router153 cluster153 mirror153 filter153", 28),
        ["signal153 packet153", "router153 cluster153", "mirror153 filter153"],
    ),
    (
        ("packet153 router153 cluster153 mirror153 filter153 ranking153", 6),
        ["packet153", "router153", "cluster153", "mirror153", "filter153", "ranking153"],
    ),
    (
        ("packet153 router153 cluster153 mirror153 filter153 ranking153", 10),
        ["packet153", "router153", "cluster153", "mirror153", "filter153", "ranking153"],
    ),
    (
        ("packet153 router153 cluster153 mirror153 filter153 ranking153", 18),
        ["packet153", "router153", "cluster153", "mirror153", "filter153", "ranking153"],
    ),
    (
        ("packet153 router153 cluster153 mirror153 filter153 ranking153", 28),
        ["packet153 router153", "cluster153 mirror153", "filter153 ranking153"],
    ),
    (
        ("router153 cluster153 mirror153 filter153 ranking153 encoding153", 6),
        ["router153", "cluster153", "mirror153", "filter153", "ranking153", "encoding153"],
    ),
    (
        ("router153 cluster153 mirror153 filter153 ranking153 encoding153", 10),
        ["router153", "cluster153", "mirror153", "filter153", "ranking153", "encoding153"],
    ),
    (
        ("router153 cluster153 mirror153 filter153 ranking153 encoding153", 18),
        ["router153", "cluster153", "mirror153", "filter153", "ranking153", "encoding153"],
    ),
    (
        ("router153 cluster153 mirror153 filter153 ranking153 encoding153", 28),
        ["router153 cluster153", "mirror153 filter153", "ranking153 encoding153"],
    ),
    (
        ("cluster153 mirror153 filter153 ranking153 encoding153 mapping153", 6),
        ["cluster153", "mirror153", "filter153", "ranking153", "encoding153", "mapping153"],
    ),
    (
        ("cluster153 mirror153 filter153 ranking153 encoding153 mapping153", 10),
        ["cluster153", "mirror153", "filter153", "ranking153", "encoding153", "mapping153"],
    ),
    (
        ("cluster153 mirror153 filter153 ranking153 encoding153 mapping153", 18),
        ["cluster153", "mirror153", "filter153", "ranking153", "encoding153", "mapping153"],
    ),
    (
        ("cluster153 mirror153 filter153 ranking153 encoding153 mapping153", 28),
        ["cluster153 mirror153", "filter153 ranking153", "encoding153 mapping153"],
    ),
    (
        ("mirror153 filter153 ranking153 encoding153 mapping153 record153", 6),
        ["mirror153", "filter153", "ranking153", "encoding153", "mapping153", "record153"],
    ),
    (
        ("mirror153 filter153 ranking153 encoding153 mapping153 record153", 10),
        ["mirror153", "filter153", "ranking153", "encoding153", "mapping153", "record153"],
    ),
    (
        ("mirror153 filter153 ranking153 encoding153 mapping153 record153", 18),
        ["mirror153", "filter153", "ranking153", "encoding153", "mapping153", "record153"],
    ),
    (
        ("mirror153 filter153 ranking153 encoding153 mapping153 record153", 28),
        ["mirror153 filter153", "ranking153 encoding153", "mapping153 record153"],
    ),
    (
        ("filter153 ranking153 encoding153 mapping153 record153 candle153", 6),
        ["filter153", "ranking153", "encoding153", "mapping153", "record153", "candle153"],
    ),
    (
        ("filter153 ranking153 encoding153 mapping153 record153 candle153", 10),
        ["filter153", "ranking153", "encoding153", "mapping153", "record153", "candle153"],
    ),
    (
        ("filter153 ranking153 encoding153 mapping153 record153 candle153", 18),
        ["filter153", "ranking153", "encoding153", "mapping153", "record153", "candle153"],
    ),
    (
        ("filter153 ranking153 encoding153 mapping153 record153 candle153", 28),
        ["filter153 ranking153", "encoding153 mapping153", "record153 candle153"],
    ),
    (
        ("ranking153 encoding153 mapping153 record153 candle153 thread153", 6),
        ["ranking153", "encoding153", "mapping153", "record153", "candle153", "thread153"],
    ),
    (
        ("ranking153 encoding153 mapping153 record153 candle153 thread153", 10),
        ["ranking153", "encoding153", "mapping153", "record153", "candle153", "thread153"],
    ),
    (
        ("ranking153 encoding153 mapping153 record153 candle153 thread153", 18),
        ["ranking153", "encoding153", "mapping153", "record153", "candle153", "thread153"],
    ),
    (
        ("ranking153 encoding153 mapping153 record153 candle153 thread153", 28),
        ["ranking153 encoding153", "mapping153 record153", "candle153 thread153"],
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
