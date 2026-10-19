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
        ("round 64: the quick brown fox jumps over the lazy dog", 4),
        ["round", "64:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 64: the quick brown fox jumps over the lazy dog", 8),
        ["round", "64: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 64: the quick brown fox jumps over the lazy dog", 12),
        ["round 64:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 64: the quick brown fox jumps over the lazy dog", 16),
        ["round 64: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 64: the quick brown fox jumps over the lazy dog", 24),
        ["round 64: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 64: the quick brown fox jumps over the lazy dog", 32),
        ["round 64: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 64: agentuniverse is a framework for multi agents", 4),
        ["round", "64:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 64: agentuniverse is a framework for multi agents", 8),
        ["round", "64:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 64: agentuniverse is a framework for multi agents", 12),
        ["round 64:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 64: agentuniverse is a framework for multi agents", 16),
        ["round 64:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 64: agentuniverse is a framework for multi agents", 24),
        ["round 64: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 64: agentuniverse is a framework for multi agents", 32),
        ["round 64: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 64: knowledge stored as vectors enables retrieval", 4),
        ["round", "64:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 64: knowledge stored as vectors enables retrieval", 8),
        ["round", "64:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 64: knowledge stored as vectors enables retrieval", 12),
        ["round 64:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 64: knowledge stored as vectors enables retrieval", 16),
        ["round 64:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 64: knowledge stored as vectors enables retrieval", 24),
        ["round 64: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 64: knowledge stored as vectors enables retrieval", 32),
        ["round 64: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 64: the processor reads the record then stops", 4),
        ["round", "64:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 64: the processor reads the record then stops", 8),
        ["round", "64: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 64: the processor reads the record then stops", 12),
        ["round 64:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 64: the processor reads the record then stops", 16),
        ["round 64: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 64: the processor reads the record then stops", 24),
        ["round 64: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 64: the processor reads the record then stops", 32),
        ["round 64: the processor reads", "the record then stops"],
    ),
    (
        ("round 64: a worker pulls the next task from the queue", 4),
        ["round", "64:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 64: a worker pulls the next task from the queue", 8),
        ["round", "64: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 64: a worker pulls the next task from the queue", 12),
        ["round 64: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 64: a worker pulls the next task from the queue", 16),
        ["round 64: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 64: a worker pulls the next task from the queue", 24),
        ["round 64: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 64: a worker pulls the next task from the queue", 32),
        ["round 64: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 64: signals travel through the network layer", 4),
        ["round", "64:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 64: signals travel through the network layer", 8),
        ["round", "64:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 64: signals travel through the network layer", 12),
        ["round 64:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 64: signals travel through the network layer", 16),
        ["round 64:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 64: signals travel through the network layer", 24),
        ["round 64: signals travel", "through the network", "layer"],
    ),
    (
        ("round 64: signals travel through the network layer", 32),
        ["round 64: signals travel through", "the network layer"],
    ),
    (
        ("round 64: the gateway routes each request by policy", 4),
        ["round", "64:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 64: the gateway routes each request by policy", 8),
        ["round", "64: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 64: the gateway routes each request by policy", 12),
        ["round 64:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 64: the gateway routes each request by policy", 16),
        ["round 64: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 64: the gateway routes each request by policy", 24),
        ["round 64: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 64: the gateway routes each request by policy", 32),
        ["round 64: the gateway routes", "each request by policy"],
    ),
    (
        ("round 64: memory grows until the buffer is full", 4),
        ["round", "64:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 64: memory grows until the buffer is full", 8),
        ["round", "64:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 64: memory grows until the buffer is full", 12),
        ["round 64:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 64: memory grows until the buffer is full", 16),
        ["round 64: memory", "grows until the", "buffer is full"],
    ),
    (("round 64: memory grows until the buffer is full", 24), ["round 64: memory grows", "until the buffer is full"]),
    (("round 64: memory grows until the buffer is full", 32), ["round 64: memory grows until the", "buffer is full"]),
    (
        ("round 64: the cluster mirrors every packet twice", 4),
        ["round", "64:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 64: the cluster mirrors every packet twice", 8),
        ["round", "64: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 64: the cluster mirrors every packet twice", 12),
        ["round 64:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 64: the cluster mirrors every packet twice", 16),
        ["round 64: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 64: the cluster mirrors every packet twice", 24),
        ["round 64: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 64: the cluster mirrors every packet twice", 32), ["round 64: the cluster mirrors", "every packet twice"]),
    (
        ("round 64: ranking uses tokens learned from the corpus", 4),
        ["round", "64:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 64: ranking uses tokens learned from the corpus", 8),
        ["round", "64:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 64: ranking uses tokens learned from the corpus", 12),
        ["round 64:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 64: ranking uses tokens learned from the corpus", 16),
        ["round 64:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 64: ranking uses tokens learned from the corpus", 24),
        ["round 64: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 64: ranking uses tokens learned from the corpus", 32),
        ["round 64: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 64: a long session ends when the candle dies", 4),
        ["round", "64:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 64: a long session ends when the candle dies", 8),
        ["round", "64: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 64: a long session ends when the candle dies", 12),
        ["round 64: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 64: a long session ends when the candle dies", 16),
        ["round 64: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 64: a long session ends when the candle dies", 24),
        ["round 64: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 64: a long session ends when the candle dies", 32),
        ["round 64: a long session ends", "when the candle dies"],
    ),
    (
        ("round 64: encode the prompt then map the result", 4),
        ["round", "64:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 64: encode the prompt then map the result", 8),
        ["round", "64:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 64: encode the prompt then map the result", 12),
        ["round 64:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 64: encode the prompt then map the result", 16),
        ["round 64: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 64: encode the prompt then map the result", 24),
        ["round 64: encode the", "prompt then map the", "result"],
    ),
    (("round 64: encode the prompt then map the result", 32), ["round 64: encode the prompt then", "map the result"]),
    (
        ("round 64: the kernel wakes the worker at dawn", 4),
        ["round", "64:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 64: the kernel wakes the worker at dawn", 8),
        ["round", "64: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 64: the kernel wakes the worker at dawn", 12),
        ["round 64:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 64: the kernel wakes the worker at dawn", 16), ["round 64: the", "kernel wakes the", "worker at dawn"]),
    (("round 64: the kernel wakes the worker at dawn", 24), ["round 64: the kernel", "wakes the worker at dawn"]),
    (("round 64: the kernel wakes the worker at dawn", 32), ["round 64: the kernel wakes the", "worker at dawn"]),
    (
        ("round 64: service latency drops after the patch", 4),
        ["round", "64:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 64: service latency drops after the patch", 8),
        ["round", "64:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 64: service latency drops after the patch", 12),
        ["round 64:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 64: service latency drops after the patch", 16),
        ["round 64:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 64: service latency drops after the patch", 24),
        ["round 64: service", "latency drops after the", "patch"],
    ),
    (("round 64: service latency drops after the patch", 32), ["round 64: service latency drops", "after the patch"]),
    (
        ("round 64: the library caches every vector it sees", 4),
        ["round", "64:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 64: the library caches every vector it sees", 8),
        ["round", "64: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 64: the library caches every vector it sees", 12),
        ["round 64:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 64: the library caches every vector it sees", 16),
        ["round 64: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 64: the library caches every vector it sees", 24),
        ["round 64: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 64: the library caches every vector it sees", 32),
        ["round 64: the library caches", "every vector it sees"],
    ),
    (
        ("round 64: agents argue then the debate resolves", 4),
        ["round", "64:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 64: agents argue then the debate resolves", 8),
        ["round", "64:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 64: agents argue then the debate resolves", 12),
        ["round 64:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 64: agents argue then the debate resolves", 16),
        ["round 64: agents", "argue then the", "debate resolves"],
    ),
    (("round 64: agents argue then the debate resolves", 24), ["round 64: agents argue", "then the debate resolves"]),
    (("round 64: agents argue then the debate resolves", 32), ["round 64: agents argue then the", "debate resolves"]),
    (
        ("round 64: the filter keeps only strong matches", 4),
        ["round", "64:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 64: the filter keeps only strong matches", 8),
        ["round", "64: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 64: the filter keeps only strong matches", 12),
        ["round 64:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 64: the filter keeps only strong matches", 16),
        ["round 64: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 64: the filter keeps only strong matches", 24), ["round 64: the filter", "keeps only strong", "matches"]),
    (("round 64: the filter keeps only strong matches", 32), ["round 64: the filter keeps only", "strong matches"]),
    (
        ("round 64: the model answers with a short reply", 4),
        ["round", "64:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 64: the model answers with a short reply", 8),
        ["round", "64: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 64: the model answers with a short reply", 12),
        ["round 64:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 64: the model answers with a short reply", 16),
        ["round 64: the", "model answers", "with a short", "reply"],
    ),
    (("round 64: the model answers with a short reply", 24), ["round 64: the model", "answers with a short", "reply"]),
    (("round 64: the model answers with a short reply", 32), ["round 64: the model answers with", "a short reply"]),
    (
        ("round 64: the recorder stores the reasoning trace", 4),
        ["round", "64:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 64: the recorder stores the reasoning trace", 8),
        ["round", "64: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 64: the recorder stores the reasoning trace", 12),
        ["round 64:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 64: the recorder stores the reasoning trace", 16),
        ["round 64: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 64: the recorder stores the reasoning trace", 24),
        ["round 64: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 64: the recorder stores the reasoning trace", 32),
        ["round 64: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 64: the angel watches the processor run", 4),
        ["round", "64:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 64: the angel watches the processor run", 8),
        ["round", "64: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 64: the angel watches the processor run", 12),
        ["round 64:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 64: the angel watches the processor run", 16), ["round 64: the", "angel watches", "the processor", "run"]),
    (("round 64: the angel watches the processor run", 24), ["round 64: the angel", "watches the processor", "run"]),
    (("round 64: the angel watches the processor run", 32), ["round 64: the angel watches the", "processor run"]),
    (
        ("round 64: angle of the vector decides the match", 4),
        ["round", "64:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 64: angle of the vector decides the match", 8),
        ["round", "64:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 64: angle of the vector decides the match", 12),
        ["round 64:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 64: angle of the vector decides the match", 16),
        ["round 64: angle", "of the vector", "decides the", "match"],
    ),
    (("round 64: angle of the vector decides the match", 24), ["round 64: angle of the", "vector decides the match"]),
    (("round 64: angle of the vector decides the match", 32), ["round 64: angle of the vector", "decides the match"]),
    (
        ("round 64: the candle burns twice as long at night", 4),
        ["round", "64:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 64: the candle burns twice as long at night", 8),
        ["round", "64: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 64: the candle burns twice as long at night", 12),
        ["round 64:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 64: the candle burns twice as long at night", 16),
        ["round 64: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 64: the candle burns twice as long at night", 24),
        ["round 64: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 64: the candle burns twice as long at night", 32),
        ["round 64: the candle burns twice", "as long at night"],
    ),
    (
        ("round 64: a mirror of the universe in one line", 4),
        ["round", "64:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 64: a mirror of the universe in one line", 8),
        ["round", "64: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 64: a mirror of the universe in one line", 12),
        ["round 64: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 64: a mirror of the universe in one line", 16),
        ["round 64: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 64: a mirror of the universe in one line", 24), ["round 64: a mirror of", "the universe in one line"]),
    (("round 64: a mirror of the universe in one line", 32), ["round 64: a mirror of the", "universe in one line"]),
    (
        ("round 64: the queue drains before the storm", 4),
        ["round", "64:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 64: the queue drains before the storm", 8),
        ["round", "64: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 64: the queue drains before the storm", 12), ["round 64:", "the queue", "drains", "before the", "storm"]),
    (("round 64: the queue drains before the storm", 16), ["round 64: the", "queue drains", "before the storm"]),
    (("round 64: the queue drains before the storm", 24), ["round 64: the queue", "drains before the storm"]),
    (("round 64: the queue drains before the storm", 32), ["round 64: the queue drains", "before the storm"]),
    (
        ("kitten64 sitting64 agent64 angle64 universe64 memory64", 6),
        ["kitten64", "sitting64", "agent64", "angle64", "universe64", "memory64"],
    ),
    (
        ("kitten64 sitting64 agent64 angle64 universe64 memory64", 10),
        ["kitten64", "sitting64", "agent64", "angle64", "universe64", "memory64"],
    ),
    (
        ("kitten64 sitting64 agent64 angle64 universe64 memory64", 18),
        ["kitten64 sitting64", "agent64 angle64", "universe64", "memory64"],
    ),
    (
        ("kitten64 sitting64 agent64 angle64 universe64 memory64", 28),
        ["kitten64 sitting64 agent64", "angle64 universe64 memory64"],
    ),
    (
        ("sitting64 agent64 angle64 universe64 memory64 stream64", 6),
        ["sitting64", "agent64", "angle64", "universe64", "memory64", "stream64"],
    ),
    (
        ("sitting64 agent64 angle64 universe64 memory64 stream64", 10),
        ["sitting64", "agent64", "angle64", "universe64", "memory64", "stream64"],
    ),
    (
        ("sitting64 agent64 angle64 universe64 memory64 stream64", 18),
        ["sitting64 agent64", "angle64 universe64", "memory64 stream64"],
    ),
    (
        ("sitting64 agent64 angle64 universe64 memory64 stream64", 28),
        ["sitting64 agent64 angle64", "universe64 memory64 stream64"],
    ),
    (
        ("agent64 angle64 universe64 memory64 stream64 context64", 6),
        ["agent64", "angle64", "universe64", "memory64", "stream64", "context64"],
    ),
    (
        ("agent64 angle64 universe64 memory64 stream64 context64", 10),
        ["agent64", "angle64", "universe64", "memory64", "stream64", "context64"],
    ),
    (
        ("agent64 angle64 universe64 memory64 stream64 context64", 18),
        ["agent64 angle64", "universe64", "memory64 stream64", "context64"],
    ),
    (
        ("agent64 angle64 universe64 memory64 stream64 context64", 28),
        ["agent64 angle64 universe64", "memory64 stream64 context64"],
    ),
    (
        ("angle64 universe64 memory64 stream64 context64 knowledge64", 6),
        ["angle64", "universe64", "memory64", "stream64", "context64", "knowledge64"],
    ),
    (
        ("angle64 universe64 memory64 stream64 context64 knowledge64", 10),
        ["angle64", "universe64", "memory64", "stream64", "context64", "knowledge64"],
    ),
    (
        ("angle64 universe64 memory64 stream64 context64 knowledge64", 18),
        ["angle64 universe64", "memory64 stream64", "context64", "knowledge64"],
    ),
    (
        ("angle64 universe64 memory64 stream64 context64 knowledge64", 28),
        ["angle64 universe64 memory64", "stream64 context64", "knowledge64"],
    ),
    (
        ("universe64 memory64 stream64 context64 knowledge64 vector64", 6),
        ["universe64", "memory64", "stream64", "context64", "knowledge64", "vector64"],
    ),
    (
        ("universe64 memory64 stream64 context64 knowledge64 vector64", 10),
        ["universe64", "memory64", "stream64", "context64", "knowledge64", "vector64"],
    ),
    (
        ("universe64 memory64 stream64 context64 knowledge64 vector64", 18),
        ["universe64", "memory64 stream64", "context64", "knowledge64", "vector64"],
    ),
    (
        ("universe64 memory64 stream64 context64 knowledge64 vector64", 28),
        ["universe64 memory64 stream64", "context64 knowledge64", "vector64"],
    ),
    (
        ("memory64 stream64 context64 knowledge64 vector64 processor64", 6),
        ["memory64", "stream64", "context64", "knowledge64", "vector64", "processor64"],
    ),
    (
        ("memory64 stream64 context64 knowledge64 vector64 processor64", 10),
        ["memory64", "stream64", "context64", "knowledge64", "vector64", "processor64"],
    ),
    (
        ("memory64 stream64 context64 knowledge64 vector64 processor64", 18),
        ["memory64 stream64", "context64", "knowledge64", "vector64", "processor64"],
    ),
    (
        ("memory64 stream64 context64 knowledge64 vector64 processor64", 28),
        ["memory64 stream64 context64", "knowledge64 vector64", "processor64"],
    ),
    (
        ("stream64 context64 knowledge64 vector64 processor64 reasoning64", 6),
        ["stream64", "context64", "knowledge64", "vector64", "processor64", "reasoning64"],
    ),
    (
        ("stream64 context64 knowledge64 vector64 processor64 reasoning64", 10),
        ["stream64", "context64", "knowledge64", "vector64", "processor64", "reasoning64"],
    ),
    (
        ("stream64 context64 knowledge64 vector64 processor64 reasoning64", 18),
        ["stream64 context64", "knowledge64", "vector64", "processor64", "reasoning64"],
    ),
    (
        ("stream64 context64 knowledge64 vector64 processor64 reasoning64", 28),
        ["stream64 context64", "knowledge64 vector64", "processor64 reasoning64"],
    ),
    (
        ("context64 knowledge64 vector64 processor64 reasoning64 machine64", 6),
        ["context64", "knowledge64", "vector64", "processor64", "reasoning64", "machine64"],
    ),
    (
        ("context64 knowledge64 vector64 processor64 reasoning64 machine64", 10),
        ["context64", "knowledge64", "vector64", "processor64", "reasoning64", "machine64"],
    ),
    (
        ("context64 knowledge64 vector64 processor64 reasoning64 machine64", 18),
        ["context64", "knowledge64", "vector64", "processor64", "reasoning64", "machine64"],
    ),
    (
        ("context64 knowledge64 vector64 processor64 reasoning64 machine64", 28),
        ["context64 knowledge64", "vector64 processor64", "reasoning64 machine64"],
    ),
    (
        ("knowledge64 vector64 processor64 reasoning64 machine64 learning64", 6),
        ["knowledge64", "vector64", "processor64", "reasoning64", "machine64", "learning64"],
    ),
    (
        ("knowledge64 vector64 processor64 reasoning64 machine64 learning64", 10),
        ["knowledge64", "vector64", "processor64", "reasoning64", "machine64", "learning64"],
    ),
    (
        ("knowledge64 vector64 processor64 reasoning64 machine64 learning64", 18),
        ["knowledge64", "vector64", "processor64", "reasoning64", "machine64", "learning64"],
    ),
    (
        ("knowledge64 vector64 processor64 reasoning64 machine64 learning64", 28),
        ["knowledge64 vector64", "processor64 reasoning64", "machine64 learning64"],
    ),
    (
        ("vector64 processor64 reasoning64 machine64 learning64 model64", 6),
        ["vector64", "processor64", "reasoning64", "machine64", "learning64", "model64"],
    ),
    (
        ("vector64 processor64 reasoning64 machine64 learning64 model64", 10),
        ["vector64", "processor64", "reasoning64", "machine64", "learning64", "model64"],
    ),
    (
        ("vector64 processor64 reasoning64 machine64 learning64 model64", 18),
        ["vector64", "processor64", "reasoning64", "machine64", "learning64 model64"],
    ),
    (
        ("vector64 processor64 reasoning64 machine64 learning64 model64", 28),
        ["vector64 processor64", "reasoning64 machine64", "learning64 model64"],
    ),
    (
        ("processor64 reasoning64 machine64 learning64 model64 token64", 6),
        ["processor64", "reasoning64", "machine64", "learning64", "model64", "token64"],
    ),
    (
        ("processor64 reasoning64 machine64 learning64 model64 token64", 10),
        ["processor64", "reasoning64", "machine64", "learning64", "model64", "token64"],
    ),
    (
        ("processor64 reasoning64 machine64 learning64 model64 token64", 18),
        ["processor64", "reasoning64", "machine64", "learning64 model64", "token64"],
    ),
    (
        ("processor64 reasoning64 machine64 learning64 model64 token64", 28),
        ["processor64 reasoning64", "machine64 learning64 model64", "token64"],
    ),
    (
        ("reasoning64 machine64 learning64 model64 token64 prompt64", 6),
        ["reasoning64", "machine64", "learning64", "model64", "token64", "prompt64"],
    ),
    (
        ("reasoning64 machine64 learning64 model64 token64 prompt64", 10),
        ["reasoning64", "machine64", "learning64", "model64", "token64", "prompt64"],
    ),
    (
        ("reasoning64 machine64 learning64 model64 token64 prompt64", 18),
        ["reasoning64", "machine64", "learning64 model64", "token64 prompt64"],
    ),
    (
        ("reasoning64 machine64 learning64 model64 token64 prompt64", 28),
        ["reasoning64 machine64", "learning64 model64 token64", "prompt64"],
    ),
    (
        ("machine64 learning64 model64 token64 prompt64 session64", 6),
        ["machine64", "learning64", "model64", "token64", "prompt64", "session64"],
    ),
    (
        ("machine64 learning64 model64 token64 prompt64 session64", 10),
        ["machine64", "learning64", "model64", "token64", "prompt64", "session64"],
    ),
    (
        ("machine64 learning64 model64 token64 prompt64 session64", 18),
        ["machine64", "learning64 model64", "token64 prompt64", "session64"],
    ),
    (
        ("machine64 learning64 model64 token64 prompt64 session64", 28),
        ["machine64 learning64 model64", "token64 prompt64 session64"],
    ),
    (
        ("learning64 model64 token64 prompt64 session64 library64", 6),
        ["learning64", "model64", "token64", "prompt64", "session64", "library64"],
    ),
    (
        ("learning64 model64 token64 prompt64 session64 library64", 10),
        ["learning64", "model64", "token64", "prompt64", "session64", "library64"],
    ),
    (
        ("learning64 model64 token64 prompt64 session64 library64", 18),
        ["learning64 model64", "token64 prompt64", "session64", "library64"],
    ),
    (
        ("learning64 model64 token64 prompt64 session64 library64", 28),
        ["learning64 model64 token64", "prompt64 session64 library64"],
    ),
    (
        ("model64 token64 prompt64 session64 library64 service64", 6),
        ["model64", "token64", "prompt64", "session64", "library64", "service64"],
    ),
    (
        ("model64 token64 prompt64 session64 library64 service64", 10),
        ["model64", "token64", "prompt64", "session64", "library64", "service64"],
    ),
    (
        ("model64 token64 prompt64 session64 library64 service64", 18),
        ["model64 token64", "prompt64 session64", "library64", "service64"],
    ),
    (
        ("model64 token64 prompt64 session64 library64 service64", 28),
        ["model64 token64 prompt64", "session64 library64", "service64"],
    ),
    (
        ("token64 prompt64 session64 library64 service64 gateway64", 6),
        ["token64", "prompt64", "session64", "library64", "service64", "gateway64"],
    ),
    (
        ("token64 prompt64 session64 library64 service64 gateway64", 10),
        ["token64", "prompt64", "session64", "library64", "service64", "gateway64"],
    ),
    (
        ("token64 prompt64 session64 library64 service64 gateway64", 18),
        ["token64 prompt64", "session64", "library64", "service64", "gateway64"],
    ),
    (
        ("token64 prompt64 session64 library64 service64 gateway64", 28),
        ["token64 prompt64 session64", "library64 service64", "gateway64"],
    ),
    (
        ("prompt64 session64 library64 service64 gateway64 storage64", 6),
        ["prompt64", "session64", "library64", "service64", "gateway64", "storage64"],
    ),
    (
        ("prompt64 session64 library64 service64 gateway64 storage64", 10),
        ["prompt64", "session64", "library64", "service64", "gateway64", "storage64"],
    ),
    (
        ("prompt64 session64 library64 service64 gateway64 storage64", 18),
        ["prompt64 session64", "library64", "service64", "gateway64", "storage64"],
    ),
    (
        ("prompt64 session64 library64 service64 gateway64 storage64", 28),
        ["prompt64 session64 library64", "service64 gateway64", "storage64"],
    ),
    (
        ("session64 library64 service64 gateway64 storage64 network64", 6),
        ["session64", "library64", "service64", "gateway64", "storage64", "network64"],
    ),
    (
        ("session64 library64 service64 gateway64 storage64 network64", 10),
        ["session64", "library64", "service64", "gateway64", "storage64", "network64"],
    ),
    (
        ("session64 library64 service64 gateway64 storage64 network64", 18),
        ["session64", "library64", "service64", "gateway64", "storage64", "network64"],
    ),
    (
        ("session64 library64 service64 gateway64 storage64 network64", 28),
        ["session64 library64", "service64 gateway64", "storage64 network64"],
    ),
    (
        ("library64 service64 gateway64 storage64 network64 latency64", 6),
        ["library64", "service64", "gateway64", "storage64", "network64", "latency64"],
    ),
    (
        ("library64 service64 gateway64 storage64 network64 latency64", 10),
        ["library64", "service64", "gateway64", "storage64", "network64", "latency64"],
    ),
    (
        ("library64 service64 gateway64 storage64 network64 latency64", 18),
        ["library64", "service64", "gateway64", "storage64", "network64", "latency64"],
    ),
    (
        ("library64 service64 gateway64 storage64 network64 latency64", 28),
        ["library64 service64", "gateway64 storage64", "network64 latency64"],
    ),
    (
        ("service64 gateway64 storage64 network64 latency64 buffer64", 6),
        ["service64", "gateway64", "storage64", "network64", "latency64", "buffer64"],
    ),
    (
        ("service64 gateway64 storage64 network64 latency64 buffer64", 10),
        ["service64", "gateway64", "storage64", "network64", "latency64", "buffer64"],
    ),
    (
        ("service64 gateway64 storage64 network64 latency64 buffer64", 18),
        ["service64", "gateway64", "storage64", "network64", "latency64 buffer64"],
    ),
    (
        ("service64 gateway64 storage64 network64 latency64 buffer64", 28),
        ["service64 gateway64", "storage64 network64", "latency64 buffer64"],
    ),
    (
        ("gateway64 storage64 network64 latency64 buffer64 queue64", 6),
        ["gateway64", "storage64", "network64", "latency64", "buffer64", "queue64"],
    ),
    (
        ("gateway64 storage64 network64 latency64 buffer64 queue64", 10),
        ["gateway64", "storage64", "network64", "latency64", "buffer64", "queue64"],
    ),
    (
        ("gateway64 storage64 network64 latency64 buffer64 queue64", 18),
        ["gateway64", "storage64", "network64", "latency64 buffer64", "queue64"],
    ),
    (
        ("gateway64 storage64 network64 latency64 buffer64 queue64", 28),
        ["gateway64 storage64", "network64 latency64 buffer64", "queue64"],
    ),
    (
        ("storage64 network64 latency64 buffer64 queue64 worker64", 6),
        ["storage64", "network64", "latency64", "buffer64", "queue64", "worker64"],
    ),
    (
        ("storage64 network64 latency64 buffer64 queue64 worker64", 10),
        ["storage64", "network64", "latency64", "buffer64", "queue64", "worker64"],
    ),
    (
        ("storage64 network64 latency64 buffer64 queue64 worker64", 18),
        ["storage64", "network64", "latency64 buffer64", "queue64 worker64"],
    ),
    (
        ("storage64 network64 latency64 buffer64 queue64 worker64", 28),
        ["storage64 network64", "latency64 buffer64 queue64", "worker64"],
    ),
    (
        ("network64 latency64 buffer64 queue64 worker64 kernel64", 6),
        ["network64", "latency64", "buffer64", "queue64", "worker64", "kernel64"],
    ),
    (
        ("network64 latency64 buffer64 queue64 worker64 kernel64", 10),
        ["network64", "latency64", "buffer64", "queue64", "worker64", "kernel64"],
    ),
    (
        ("network64 latency64 buffer64 queue64 worker64 kernel64", 18),
        ["network64", "latency64 buffer64", "queue64 worker64", "kernel64"],
    ),
    (
        ("network64 latency64 buffer64 queue64 worker64 kernel64", 28),
        ["network64 latency64 buffer64", "queue64 worker64 kernel64"],
    ),
    (
        ("latency64 buffer64 queue64 worker64 kernel64 signal64", 6),
        ["latency64", "buffer64", "queue64", "worker64", "kernel64", "signal64"],
    ),
    (
        ("latency64 buffer64 queue64 worker64 kernel64 signal64", 10),
        ["latency64", "buffer64", "queue64", "worker64", "kernel64", "signal64"],
    ),
    (
        ("latency64 buffer64 queue64 worker64 kernel64 signal64", 18),
        ["latency64 buffer64", "queue64 worker64", "kernel64 signal64"],
    ),
    (
        ("latency64 buffer64 queue64 worker64 kernel64 signal64", 28),
        ["latency64 buffer64 queue64", "worker64 kernel64 signal64"],
    ),
    (
        ("buffer64 queue64 worker64 kernel64 signal64 packet64", 6),
        ["buffer64", "queue64", "worker64", "kernel64", "signal64", "packet64"],
    ),
    (
        ("buffer64 queue64 worker64 kernel64 signal64 packet64", 10),
        ["buffer64", "queue64", "worker64", "kernel64", "signal64", "packet64"],
    ),
    (
        ("buffer64 queue64 worker64 kernel64 signal64 packet64", 18),
        ["buffer64 queue64", "worker64 kernel64", "signal64 packet64"],
    ),
    (
        ("buffer64 queue64 worker64 kernel64 signal64 packet64", 28),
        ["buffer64 queue64 worker64", "kernel64 signal64 packet64"],
    ),
    (
        ("queue64 worker64 kernel64 signal64 packet64 router64", 6),
        ["queue64", "worker64", "kernel64", "signal64", "packet64", "router64"],
    ),
    (
        ("queue64 worker64 kernel64 signal64 packet64 router64", 10),
        ["queue64", "worker64", "kernel64", "signal64", "packet64", "router64"],
    ),
    (
        ("queue64 worker64 kernel64 signal64 packet64 router64", 18),
        ["queue64 worker64", "kernel64 signal64", "packet64 router64"],
    ),
    (
        ("queue64 worker64 kernel64 signal64 packet64 router64", 28),
        ["queue64 worker64 kernel64", "signal64 packet64 router64"],
    ),
    (
        ("worker64 kernel64 signal64 packet64 router64 cluster64", 6),
        ["worker64", "kernel64", "signal64", "packet64", "router64", "cluster64"],
    ),
    (
        ("worker64 kernel64 signal64 packet64 router64 cluster64", 10),
        ["worker64", "kernel64", "signal64", "packet64", "router64", "cluster64"],
    ),
    (
        ("worker64 kernel64 signal64 packet64 router64 cluster64", 18),
        ["worker64 kernel64", "signal64 packet64", "router64 cluster64"],
    ),
    (
        ("worker64 kernel64 signal64 packet64 router64 cluster64", 28),
        ["worker64 kernel64 signal64", "packet64 router64 cluster64"],
    ),
    (
        ("kernel64 signal64 packet64 router64 cluster64 mirror64", 6),
        ["kernel64", "signal64", "packet64", "router64", "cluster64", "mirror64"],
    ),
    (
        ("kernel64 signal64 packet64 router64 cluster64 mirror64", 10),
        ["kernel64", "signal64", "packet64", "router64", "cluster64", "mirror64"],
    ),
    (
        ("kernel64 signal64 packet64 router64 cluster64 mirror64", 18),
        ["kernel64 signal64", "packet64 router64", "cluster64 mirror64"],
    ),
    (
        ("kernel64 signal64 packet64 router64 cluster64 mirror64", 28),
        ["kernel64 signal64 packet64", "router64 cluster64 mirror64"],
    ),
    (
        ("signal64 packet64 router64 cluster64 mirror64 filter64", 6),
        ["signal64", "packet64", "router64", "cluster64", "mirror64", "filter64"],
    ),
    (
        ("signal64 packet64 router64 cluster64 mirror64 filter64", 10),
        ["signal64", "packet64", "router64", "cluster64", "mirror64", "filter64"],
    ),
    (
        ("signal64 packet64 router64 cluster64 mirror64 filter64", 18),
        ["signal64 packet64", "router64 cluster64", "mirror64 filter64"],
    ),
    (
        ("signal64 packet64 router64 cluster64 mirror64 filter64", 28),
        ["signal64 packet64 router64", "cluster64 mirror64 filter64"],
    ),
    (
        ("packet64 router64 cluster64 mirror64 filter64 ranking64", 6),
        ["packet64", "router64", "cluster64", "mirror64", "filter64", "ranking64"],
    ),
    (
        ("packet64 router64 cluster64 mirror64 filter64 ranking64", 10),
        ["packet64", "router64", "cluster64", "mirror64", "filter64", "ranking64"],
    ),
    (
        ("packet64 router64 cluster64 mirror64 filter64 ranking64", 18),
        ["packet64 router64", "cluster64 mirror64", "filter64 ranking64"],
    ),
    (
        ("packet64 router64 cluster64 mirror64 filter64 ranking64", 28),
        ["packet64 router64 cluster64", "mirror64 filter64 ranking64"],
    ),
    (
        ("router64 cluster64 mirror64 filter64 ranking64 encoding64", 6),
        ["router64", "cluster64", "mirror64", "filter64", "ranking64", "encoding64"],
    ),
    (
        ("router64 cluster64 mirror64 filter64 ranking64 encoding64", 10),
        ["router64", "cluster64", "mirror64", "filter64", "ranking64", "encoding64"],
    ),
    (
        ("router64 cluster64 mirror64 filter64 ranking64 encoding64", 18),
        ["router64 cluster64", "mirror64 filter64", "ranking64", "encoding64"],
    ),
    (
        ("router64 cluster64 mirror64 filter64 ranking64 encoding64", 28),
        ["router64 cluster64 mirror64", "filter64 ranking64", "encoding64"],
    ),
    (
        ("cluster64 mirror64 filter64 ranking64 encoding64 mapping64", 6),
        ["cluster64", "mirror64", "filter64", "ranking64", "encoding64", "mapping64"],
    ),
    (
        ("cluster64 mirror64 filter64 ranking64 encoding64 mapping64", 10),
        ["cluster64", "mirror64", "filter64", "ranking64", "encoding64", "mapping64"],
    ),
    (
        ("cluster64 mirror64 filter64 ranking64 encoding64 mapping64", 18),
        ["cluster64 mirror64", "filter64 ranking64", "encoding64", "mapping64"],
    ),
    (
        ("cluster64 mirror64 filter64 ranking64 encoding64 mapping64", 28),
        ["cluster64 mirror64 filter64", "ranking64 encoding64", "mapping64"],
    ),
    (
        ("mirror64 filter64 ranking64 encoding64 mapping64 record64", 6),
        ["mirror64", "filter64", "ranking64", "encoding64", "mapping64", "record64"],
    ),
    (
        ("mirror64 filter64 ranking64 encoding64 mapping64 record64", 10),
        ["mirror64", "filter64", "ranking64", "encoding64", "mapping64", "record64"],
    ),
    (
        ("mirror64 filter64 ranking64 encoding64 mapping64 record64", 18),
        ["mirror64 filter64", "ranking64", "encoding64", "mapping64 record64"],
    ),
    (
        ("mirror64 filter64 ranking64 encoding64 mapping64 record64", 28),
        ["mirror64 filter64 ranking64", "encoding64 mapping64", "record64"],
    ),
    (
        ("filter64 ranking64 encoding64 mapping64 record64 candle64", 6),
        ["filter64", "ranking64", "encoding64", "mapping64", "record64", "candle64"],
    ),
    (
        ("filter64 ranking64 encoding64 mapping64 record64 candle64", 10),
        ["filter64", "ranking64", "encoding64", "mapping64", "record64", "candle64"],
    ),
    (
        ("filter64 ranking64 encoding64 mapping64 record64 candle64", 18),
        ["filter64 ranking64", "encoding64", "mapping64 record64", "candle64"],
    ),
    (
        ("filter64 ranking64 encoding64 mapping64 record64 candle64", 28),
        ["filter64 ranking64", "encoding64 mapping64", "record64 candle64"],
    ),
    (
        ("ranking64 encoding64 mapping64 record64 candle64 thread64", 6),
        ["ranking64", "encoding64", "mapping64", "record64", "candle64", "thread64"],
    ),
    (
        ("ranking64 encoding64 mapping64 record64 candle64 thread64", 10),
        ["ranking64", "encoding64", "mapping64", "record64", "candle64", "thread64"],
    ),
    (
        ("ranking64 encoding64 mapping64 record64 candle64 thread64", 18),
        ["ranking64", "encoding64", "mapping64 record64", "candle64 thread64"],
    ),
    (
        ("ranking64 encoding64 mapping64 record64 candle64 thread64", 28),
        ["ranking64 encoding64", "mapping64 record64 candle64", "thread64"],
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
