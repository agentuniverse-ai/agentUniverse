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
        ("round 90: the quick brown fox jumps over the lazy dog", 4),
        ["round", "90:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 90: the quick brown fox jumps over the lazy dog", 8),
        ["round", "90: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 90: the quick brown fox jumps over the lazy dog", 12),
        ["round 90:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 90: the quick brown fox jumps over the lazy dog", 16),
        ["round 90: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 90: the quick brown fox jumps over the lazy dog", 24),
        ["round 90: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 90: the quick brown fox jumps over the lazy dog", 32),
        ["round 90: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 90: agentuniverse is a framework for multi agents", 4),
        ["round", "90:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 90: agentuniverse is a framework for multi agents", 8),
        ["round", "90:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 90: agentuniverse is a framework for multi agents", 12),
        ["round 90:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 90: agentuniverse is a framework for multi agents", 16),
        ["round 90:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 90: agentuniverse is a framework for multi agents", 24),
        ["round 90: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 90: agentuniverse is a framework for multi agents", 32),
        ["round 90: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 90: knowledge stored as vectors enables retrieval", 4),
        ["round", "90:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 90: knowledge stored as vectors enables retrieval", 8),
        ["round", "90:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 90: knowledge stored as vectors enables retrieval", 12),
        ["round 90:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 90: knowledge stored as vectors enables retrieval", 16),
        ["round 90:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 90: knowledge stored as vectors enables retrieval", 24),
        ["round 90: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 90: knowledge stored as vectors enables retrieval", 32),
        ["round 90: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 90: the processor reads the record then stops", 4),
        ["round", "90:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 90: the processor reads the record then stops", 8),
        ["round", "90: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 90: the processor reads the record then stops", 12),
        ["round 90:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 90: the processor reads the record then stops", 16),
        ["round 90: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 90: the processor reads the record then stops", 24),
        ["round 90: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 90: the processor reads the record then stops", 32),
        ["round 90: the processor reads", "the record then stops"],
    ),
    (
        ("round 90: a worker pulls the next task from the queue", 4),
        ["round", "90:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 90: a worker pulls the next task from the queue", 8),
        ["round", "90: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 90: a worker pulls the next task from the queue", 12),
        ["round 90: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 90: a worker pulls the next task from the queue", 16),
        ["round 90: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 90: a worker pulls the next task from the queue", 24),
        ["round 90: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 90: a worker pulls the next task from the queue", 32),
        ["round 90: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 90: signals travel through the network layer", 4),
        ["round", "90:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 90: signals travel through the network layer", 8),
        ["round", "90:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 90: signals travel through the network layer", 12),
        ["round 90:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 90: signals travel through the network layer", 16),
        ["round 90:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 90: signals travel through the network layer", 24),
        ["round 90: signals travel", "through the network", "layer"],
    ),
    (
        ("round 90: signals travel through the network layer", 32),
        ["round 90: signals travel through", "the network layer"],
    ),
    (
        ("round 90: the gateway routes each request by policy", 4),
        ["round", "90:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 90: the gateway routes each request by policy", 8),
        ["round", "90: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 90: the gateway routes each request by policy", 12),
        ["round 90:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 90: the gateway routes each request by policy", 16),
        ["round 90: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 90: the gateway routes each request by policy", 24),
        ["round 90: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 90: the gateway routes each request by policy", 32),
        ["round 90: the gateway routes", "each request by policy"],
    ),
    (
        ("round 90: memory grows until the buffer is full", 4),
        ["round", "90:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 90: memory grows until the buffer is full", 8),
        ["round", "90:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 90: memory grows until the buffer is full", 12),
        ["round 90:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 90: memory grows until the buffer is full", 16),
        ["round 90: memory", "grows until the", "buffer is full"],
    ),
    (("round 90: memory grows until the buffer is full", 24), ["round 90: memory grows", "until the buffer is full"]),
    (("round 90: memory grows until the buffer is full", 32), ["round 90: memory grows until the", "buffer is full"]),
    (
        ("round 90: the cluster mirrors every packet twice", 4),
        ["round", "90:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 90: the cluster mirrors every packet twice", 8),
        ["round", "90: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 90: the cluster mirrors every packet twice", 12),
        ["round 90:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 90: the cluster mirrors every packet twice", 16),
        ["round 90: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 90: the cluster mirrors every packet twice", 24),
        ["round 90: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 90: the cluster mirrors every packet twice", 32), ["round 90: the cluster mirrors", "every packet twice"]),
    (
        ("round 90: ranking uses tokens learned from the corpus", 4),
        ["round", "90:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 90: ranking uses tokens learned from the corpus", 8),
        ["round", "90:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 90: ranking uses tokens learned from the corpus", 12),
        ["round 90:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 90: ranking uses tokens learned from the corpus", 16),
        ["round 90:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 90: ranking uses tokens learned from the corpus", 24),
        ["round 90: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 90: ranking uses tokens learned from the corpus", 32),
        ["round 90: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 90: a long session ends when the candle dies", 4),
        ["round", "90:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 90: a long session ends when the candle dies", 8),
        ["round", "90: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 90: a long session ends when the candle dies", 12),
        ["round 90: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 90: a long session ends when the candle dies", 16),
        ["round 90: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 90: a long session ends when the candle dies", 24),
        ["round 90: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 90: a long session ends when the candle dies", 32),
        ["round 90: a long session ends", "when the candle dies"],
    ),
    (
        ("round 90: encode the prompt then map the result", 4),
        ["round", "90:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 90: encode the prompt then map the result", 8),
        ["round", "90:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 90: encode the prompt then map the result", 12),
        ["round 90:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 90: encode the prompt then map the result", 16),
        ["round 90: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 90: encode the prompt then map the result", 24),
        ["round 90: encode the", "prompt then map the", "result"],
    ),
    (("round 90: encode the prompt then map the result", 32), ["round 90: encode the prompt then", "map the result"]),
    (
        ("round 90: the kernel wakes the worker at dawn", 4),
        ["round", "90:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 90: the kernel wakes the worker at dawn", 8),
        ["round", "90: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 90: the kernel wakes the worker at dawn", 12),
        ["round 90:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 90: the kernel wakes the worker at dawn", 16), ["round 90: the", "kernel wakes the", "worker at dawn"]),
    (("round 90: the kernel wakes the worker at dawn", 24), ["round 90: the kernel", "wakes the worker at dawn"]),
    (("round 90: the kernel wakes the worker at dawn", 32), ["round 90: the kernel wakes the", "worker at dawn"]),
    (
        ("round 90: service latency drops after the patch", 4),
        ["round", "90:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 90: service latency drops after the patch", 8),
        ["round", "90:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 90: service latency drops after the patch", 12),
        ["round 90:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 90: service latency drops after the patch", 16),
        ["round 90:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 90: service latency drops after the patch", 24),
        ["round 90: service", "latency drops after the", "patch"],
    ),
    (("round 90: service latency drops after the patch", 32), ["round 90: service latency drops", "after the patch"]),
    (
        ("round 90: the library caches every vector it sees", 4),
        ["round", "90:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 90: the library caches every vector it sees", 8),
        ["round", "90: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 90: the library caches every vector it sees", 12),
        ["round 90:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 90: the library caches every vector it sees", 16),
        ["round 90: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 90: the library caches every vector it sees", 24),
        ["round 90: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 90: the library caches every vector it sees", 32),
        ["round 90: the library caches", "every vector it sees"],
    ),
    (
        ("round 90: agents argue then the debate resolves", 4),
        ["round", "90:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 90: agents argue then the debate resolves", 8),
        ["round", "90:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 90: agents argue then the debate resolves", 12),
        ["round 90:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 90: agents argue then the debate resolves", 16),
        ["round 90: agents", "argue then the", "debate resolves"],
    ),
    (("round 90: agents argue then the debate resolves", 24), ["round 90: agents argue", "then the debate resolves"]),
    (("round 90: agents argue then the debate resolves", 32), ["round 90: agents argue then the", "debate resolves"]),
    (
        ("round 90: the filter keeps only strong matches", 4),
        ["round", "90:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 90: the filter keeps only strong matches", 8),
        ["round", "90: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 90: the filter keeps only strong matches", 12),
        ["round 90:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 90: the filter keeps only strong matches", 16),
        ["round 90: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 90: the filter keeps only strong matches", 24), ["round 90: the filter", "keeps only strong", "matches"]),
    (("round 90: the filter keeps only strong matches", 32), ["round 90: the filter keeps only", "strong matches"]),
    (
        ("round 90: the model answers with a short reply", 4),
        ["round", "90:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 90: the model answers with a short reply", 8),
        ["round", "90: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 90: the model answers with a short reply", 12),
        ["round 90:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 90: the model answers with a short reply", 16),
        ["round 90: the", "model answers", "with a short", "reply"],
    ),
    (("round 90: the model answers with a short reply", 24), ["round 90: the model", "answers with a short", "reply"]),
    (("round 90: the model answers with a short reply", 32), ["round 90: the model answers with", "a short reply"]),
    (
        ("round 90: the recorder stores the reasoning trace", 4),
        ["round", "90:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 90: the recorder stores the reasoning trace", 8),
        ["round", "90: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 90: the recorder stores the reasoning trace", 12),
        ["round 90:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 90: the recorder stores the reasoning trace", 16),
        ["round 90: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 90: the recorder stores the reasoning trace", 24),
        ["round 90: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 90: the recorder stores the reasoning trace", 32),
        ["round 90: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 90: the angel watches the processor run", 4),
        ["round", "90:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 90: the angel watches the processor run", 8),
        ["round", "90: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 90: the angel watches the processor run", 12),
        ["round 90:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 90: the angel watches the processor run", 16), ["round 90: the", "angel watches", "the processor", "run"]),
    (("round 90: the angel watches the processor run", 24), ["round 90: the angel", "watches the processor", "run"]),
    (("round 90: the angel watches the processor run", 32), ["round 90: the angel watches the", "processor run"]),
    (
        ("round 90: angle of the vector decides the match", 4),
        ["round", "90:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 90: angle of the vector decides the match", 8),
        ["round", "90:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 90: angle of the vector decides the match", 12),
        ["round 90:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 90: angle of the vector decides the match", 16),
        ["round 90: angle", "of the vector", "decides the", "match"],
    ),
    (("round 90: angle of the vector decides the match", 24), ["round 90: angle of the", "vector decides the match"]),
    (("round 90: angle of the vector decides the match", 32), ["round 90: angle of the vector", "decides the match"]),
    (
        ("round 90: the candle burns twice as long at night", 4),
        ["round", "90:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 90: the candle burns twice as long at night", 8),
        ["round", "90: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 90: the candle burns twice as long at night", 12),
        ["round 90:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 90: the candle burns twice as long at night", 16),
        ["round 90: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 90: the candle burns twice as long at night", 24),
        ["round 90: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 90: the candle burns twice as long at night", 32),
        ["round 90: the candle burns twice", "as long at night"],
    ),
    (
        ("round 90: a mirror of the universe in one line", 4),
        ["round", "90:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 90: a mirror of the universe in one line", 8),
        ["round", "90: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 90: a mirror of the universe in one line", 12),
        ["round 90: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 90: a mirror of the universe in one line", 16),
        ["round 90: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 90: a mirror of the universe in one line", 24), ["round 90: a mirror of", "the universe in one line"]),
    (("round 90: a mirror of the universe in one line", 32), ["round 90: a mirror of the", "universe in one line"]),
    (
        ("round 90: the queue drains before the storm", 4),
        ["round", "90:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 90: the queue drains before the storm", 8),
        ["round", "90: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 90: the queue drains before the storm", 12), ["round 90:", "the queue", "drains", "before the", "storm"]),
    (("round 90: the queue drains before the storm", 16), ["round 90: the", "queue drains", "before the storm"]),
    (("round 90: the queue drains before the storm", 24), ["round 90: the queue", "drains before the storm"]),
    (("round 90: the queue drains before the storm", 32), ["round 90: the queue drains", "before the storm"]),
    (
        ("kitten90 sitting90 agent90 angle90 universe90 memory90", 6),
        ["kitten90", "sitting90", "agent90", "angle90", "universe90", "memory90"],
    ),
    (
        ("kitten90 sitting90 agent90 angle90 universe90 memory90", 10),
        ["kitten90", "sitting90", "agent90", "angle90", "universe90", "memory90"],
    ),
    (
        ("kitten90 sitting90 agent90 angle90 universe90 memory90", 18),
        ["kitten90 sitting90", "agent90 angle90", "universe90", "memory90"],
    ),
    (
        ("kitten90 sitting90 agent90 angle90 universe90 memory90", 28),
        ["kitten90 sitting90 agent90", "angle90 universe90 memory90"],
    ),
    (
        ("sitting90 agent90 angle90 universe90 memory90 stream90", 6),
        ["sitting90", "agent90", "angle90", "universe90", "memory90", "stream90"],
    ),
    (
        ("sitting90 agent90 angle90 universe90 memory90 stream90", 10),
        ["sitting90", "agent90", "angle90", "universe90", "memory90", "stream90"],
    ),
    (
        ("sitting90 agent90 angle90 universe90 memory90 stream90", 18),
        ["sitting90 agent90", "angle90 universe90", "memory90 stream90"],
    ),
    (
        ("sitting90 agent90 angle90 universe90 memory90 stream90", 28),
        ["sitting90 agent90 angle90", "universe90 memory90 stream90"],
    ),
    (
        ("agent90 angle90 universe90 memory90 stream90 context90", 6),
        ["agent90", "angle90", "universe90", "memory90", "stream90", "context90"],
    ),
    (
        ("agent90 angle90 universe90 memory90 stream90 context90", 10),
        ["agent90", "angle90", "universe90", "memory90", "stream90", "context90"],
    ),
    (
        ("agent90 angle90 universe90 memory90 stream90 context90", 18),
        ["agent90 angle90", "universe90", "memory90 stream90", "context90"],
    ),
    (
        ("agent90 angle90 universe90 memory90 stream90 context90", 28),
        ["agent90 angle90 universe90", "memory90 stream90 context90"],
    ),
    (
        ("angle90 universe90 memory90 stream90 context90 knowledge90", 6),
        ["angle90", "universe90", "memory90", "stream90", "context90", "knowledge90"],
    ),
    (
        ("angle90 universe90 memory90 stream90 context90 knowledge90", 10),
        ["angle90", "universe90", "memory90", "stream90", "context90", "knowledge90"],
    ),
    (
        ("angle90 universe90 memory90 stream90 context90 knowledge90", 18),
        ["angle90 universe90", "memory90 stream90", "context90", "knowledge90"],
    ),
    (
        ("angle90 universe90 memory90 stream90 context90 knowledge90", 28),
        ["angle90 universe90 memory90", "stream90 context90", "knowledge90"],
    ),
    (
        ("universe90 memory90 stream90 context90 knowledge90 vector90", 6),
        ["universe90", "memory90", "stream90", "context90", "knowledge90", "vector90"],
    ),
    (
        ("universe90 memory90 stream90 context90 knowledge90 vector90", 10),
        ["universe90", "memory90", "stream90", "context90", "knowledge90", "vector90"],
    ),
    (
        ("universe90 memory90 stream90 context90 knowledge90 vector90", 18),
        ["universe90", "memory90 stream90", "context90", "knowledge90", "vector90"],
    ),
    (
        ("universe90 memory90 stream90 context90 knowledge90 vector90", 28),
        ["universe90 memory90 stream90", "context90 knowledge90", "vector90"],
    ),
    (
        ("memory90 stream90 context90 knowledge90 vector90 processor90", 6),
        ["memory90", "stream90", "context90", "knowledge90", "vector90", "processor90"],
    ),
    (
        ("memory90 stream90 context90 knowledge90 vector90 processor90", 10),
        ["memory90", "stream90", "context90", "knowledge90", "vector90", "processor90"],
    ),
    (
        ("memory90 stream90 context90 knowledge90 vector90 processor90", 18),
        ["memory90 stream90", "context90", "knowledge90", "vector90", "processor90"],
    ),
    (
        ("memory90 stream90 context90 knowledge90 vector90 processor90", 28),
        ["memory90 stream90 context90", "knowledge90 vector90", "processor90"],
    ),
    (
        ("stream90 context90 knowledge90 vector90 processor90 reasoning90", 6),
        ["stream90", "context90", "knowledge90", "vector90", "processor90", "reasoning90"],
    ),
    (
        ("stream90 context90 knowledge90 vector90 processor90 reasoning90", 10),
        ["stream90", "context90", "knowledge90", "vector90", "processor90", "reasoning90"],
    ),
    (
        ("stream90 context90 knowledge90 vector90 processor90 reasoning90", 18),
        ["stream90 context90", "knowledge90", "vector90", "processor90", "reasoning90"],
    ),
    (
        ("stream90 context90 knowledge90 vector90 processor90 reasoning90", 28),
        ["stream90 context90", "knowledge90 vector90", "processor90 reasoning90"],
    ),
    (
        ("context90 knowledge90 vector90 processor90 reasoning90 machine90", 6),
        ["context90", "knowledge90", "vector90", "processor90", "reasoning90", "machine90"],
    ),
    (
        ("context90 knowledge90 vector90 processor90 reasoning90 machine90", 10),
        ["context90", "knowledge90", "vector90", "processor90", "reasoning90", "machine90"],
    ),
    (
        ("context90 knowledge90 vector90 processor90 reasoning90 machine90", 18),
        ["context90", "knowledge90", "vector90", "processor90", "reasoning90", "machine90"],
    ),
    (
        ("context90 knowledge90 vector90 processor90 reasoning90 machine90", 28),
        ["context90 knowledge90", "vector90 processor90", "reasoning90 machine90"],
    ),
    (
        ("knowledge90 vector90 processor90 reasoning90 machine90 learning90", 6),
        ["knowledge90", "vector90", "processor90", "reasoning90", "machine90", "learning90"],
    ),
    (
        ("knowledge90 vector90 processor90 reasoning90 machine90 learning90", 10),
        ["knowledge90", "vector90", "processor90", "reasoning90", "machine90", "learning90"],
    ),
    (
        ("knowledge90 vector90 processor90 reasoning90 machine90 learning90", 18),
        ["knowledge90", "vector90", "processor90", "reasoning90", "machine90", "learning90"],
    ),
    (
        ("knowledge90 vector90 processor90 reasoning90 machine90 learning90", 28),
        ["knowledge90 vector90", "processor90 reasoning90", "machine90 learning90"],
    ),
    (
        ("vector90 processor90 reasoning90 machine90 learning90 model90", 6),
        ["vector90", "processor90", "reasoning90", "machine90", "learning90", "model90"],
    ),
    (
        ("vector90 processor90 reasoning90 machine90 learning90 model90", 10),
        ["vector90", "processor90", "reasoning90", "machine90", "learning90", "model90"],
    ),
    (
        ("vector90 processor90 reasoning90 machine90 learning90 model90", 18),
        ["vector90", "processor90", "reasoning90", "machine90", "learning90 model90"],
    ),
    (
        ("vector90 processor90 reasoning90 machine90 learning90 model90", 28),
        ["vector90 processor90", "reasoning90 machine90", "learning90 model90"],
    ),
    (
        ("processor90 reasoning90 machine90 learning90 model90 token90", 6),
        ["processor90", "reasoning90", "machine90", "learning90", "model90", "token90"],
    ),
    (
        ("processor90 reasoning90 machine90 learning90 model90 token90", 10),
        ["processor90", "reasoning90", "machine90", "learning90", "model90", "token90"],
    ),
    (
        ("processor90 reasoning90 machine90 learning90 model90 token90", 18),
        ["processor90", "reasoning90", "machine90", "learning90 model90", "token90"],
    ),
    (
        ("processor90 reasoning90 machine90 learning90 model90 token90", 28),
        ["processor90 reasoning90", "machine90 learning90 model90", "token90"],
    ),
    (
        ("reasoning90 machine90 learning90 model90 token90 prompt90", 6),
        ["reasoning90", "machine90", "learning90", "model90", "token90", "prompt90"],
    ),
    (
        ("reasoning90 machine90 learning90 model90 token90 prompt90", 10),
        ["reasoning90", "machine90", "learning90", "model90", "token90", "prompt90"],
    ),
    (
        ("reasoning90 machine90 learning90 model90 token90 prompt90", 18),
        ["reasoning90", "machine90", "learning90 model90", "token90 prompt90"],
    ),
    (
        ("reasoning90 machine90 learning90 model90 token90 prompt90", 28),
        ["reasoning90 machine90", "learning90 model90 token90", "prompt90"],
    ),
    (
        ("machine90 learning90 model90 token90 prompt90 session90", 6),
        ["machine90", "learning90", "model90", "token90", "prompt90", "session90"],
    ),
    (
        ("machine90 learning90 model90 token90 prompt90 session90", 10),
        ["machine90", "learning90", "model90", "token90", "prompt90", "session90"],
    ),
    (
        ("machine90 learning90 model90 token90 prompt90 session90", 18),
        ["machine90", "learning90 model90", "token90 prompt90", "session90"],
    ),
    (
        ("machine90 learning90 model90 token90 prompt90 session90", 28),
        ["machine90 learning90 model90", "token90 prompt90 session90"],
    ),
    (
        ("learning90 model90 token90 prompt90 session90 library90", 6),
        ["learning90", "model90", "token90", "prompt90", "session90", "library90"],
    ),
    (
        ("learning90 model90 token90 prompt90 session90 library90", 10),
        ["learning90", "model90", "token90", "prompt90", "session90", "library90"],
    ),
    (
        ("learning90 model90 token90 prompt90 session90 library90", 18),
        ["learning90 model90", "token90 prompt90", "session90", "library90"],
    ),
    (
        ("learning90 model90 token90 prompt90 session90 library90", 28),
        ["learning90 model90 token90", "prompt90 session90 library90"],
    ),
    (
        ("model90 token90 prompt90 session90 library90 service90", 6),
        ["model90", "token90", "prompt90", "session90", "library90", "service90"],
    ),
    (
        ("model90 token90 prompt90 session90 library90 service90", 10),
        ["model90", "token90", "prompt90", "session90", "library90", "service90"],
    ),
    (
        ("model90 token90 prompt90 session90 library90 service90", 18),
        ["model90 token90", "prompt90 session90", "library90", "service90"],
    ),
    (
        ("model90 token90 prompt90 session90 library90 service90", 28),
        ["model90 token90 prompt90", "session90 library90", "service90"],
    ),
    (
        ("token90 prompt90 session90 library90 service90 gateway90", 6),
        ["token90", "prompt90", "session90", "library90", "service90", "gateway90"],
    ),
    (
        ("token90 prompt90 session90 library90 service90 gateway90", 10),
        ["token90", "prompt90", "session90", "library90", "service90", "gateway90"],
    ),
    (
        ("token90 prompt90 session90 library90 service90 gateway90", 18),
        ["token90 prompt90", "session90", "library90", "service90", "gateway90"],
    ),
    (
        ("token90 prompt90 session90 library90 service90 gateway90", 28),
        ["token90 prompt90 session90", "library90 service90", "gateway90"],
    ),
    (
        ("prompt90 session90 library90 service90 gateway90 storage90", 6),
        ["prompt90", "session90", "library90", "service90", "gateway90", "storage90"],
    ),
    (
        ("prompt90 session90 library90 service90 gateway90 storage90", 10),
        ["prompt90", "session90", "library90", "service90", "gateway90", "storage90"],
    ),
    (
        ("prompt90 session90 library90 service90 gateway90 storage90", 18),
        ["prompt90 session90", "library90", "service90", "gateway90", "storage90"],
    ),
    (
        ("prompt90 session90 library90 service90 gateway90 storage90", 28),
        ["prompt90 session90 library90", "service90 gateway90", "storage90"],
    ),
    (
        ("session90 library90 service90 gateway90 storage90 network90", 6),
        ["session90", "library90", "service90", "gateway90", "storage90", "network90"],
    ),
    (
        ("session90 library90 service90 gateway90 storage90 network90", 10),
        ["session90", "library90", "service90", "gateway90", "storage90", "network90"],
    ),
    (
        ("session90 library90 service90 gateway90 storage90 network90", 18),
        ["session90", "library90", "service90", "gateway90", "storage90", "network90"],
    ),
    (
        ("session90 library90 service90 gateway90 storage90 network90", 28),
        ["session90 library90", "service90 gateway90", "storage90 network90"],
    ),
    (
        ("library90 service90 gateway90 storage90 network90 latency90", 6),
        ["library90", "service90", "gateway90", "storage90", "network90", "latency90"],
    ),
    (
        ("library90 service90 gateway90 storage90 network90 latency90", 10),
        ["library90", "service90", "gateway90", "storage90", "network90", "latency90"],
    ),
    (
        ("library90 service90 gateway90 storage90 network90 latency90", 18),
        ["library90", "service90", "gateway90", "storage90", "network90", "latency90"],
    ),
    (
        ("library90 service90 gateway90 storage90 network90 latency90", 28),
        ["library90 service90", "gateway90 storage90", "network90 latency90"],
    ),
    (
        ("service90 gateway90 storage90 network90 latency90 buffer90", 6),
        ["service90", "gateway90", "storage90", "network90", "latency90", "buffer90"],
    ),
    (
        ("service90 gateway90 storage90 network90 latency90 buffer90", 10),
        ["service90", "gateway90", "storage90", "network90", "latency90", "buffer90"],
    ),
    (
        ("service90 gateway90 storage90 network90 latency90 buffer90", 18),
        ["service90", "gateway90", "storage90", "network90", "latency90 buffer90"],
    ),
    (
        ("service90 gateway90 storage90 network90 latency90 buffer90", 28),
        ["service90 gateway90", "storage90 network90", "latency90 buffer90"],
    ),
    (
        ("gateway90 storage90 network90 latency90 buffer90 queue90", 6),
        ["gateway90", "storage90", "network90", "latency90", "buffer90", "queue90"],
    ),
    (
        ("gateway90 storage90 network90 latency90 buffer90 queue90", 10),
        ["gateway90", "storage90", "network90", "latency90", "buffer90", "queue90"],
    ),
    (
        ("gateway90 storage90 network90 latency90 buffer90 queue90", 18),
        ["gateway90", "storage90", "network90", "latency90 buffer90", "queue90"],
    ),
    (
        ("gateway90 storage90 network90 latency90 buffer90 queue90", 28),
        ["gateway90 storage90", "network90 latency90 buffer90", "queue90"],
    ),
    (
        ("storage90 network90 latency90 buffer90 queue90 worker90", 6),
        ["storage90", "network90", "latency90", "buffer90", "queue90", "worker90"],
    ),
    (
        ("storage90 network90 latency90 buffer90 queue90 worker90", 10),
        ["storage90", "network90", "latency90", "buffer90", "queue90", "worker90"],
    ),
    (
        ("storage90 network90 latency90 buffer90 queue90 worker90", 18),
        ["storage90", "network90", "latency90 buffer90", "queue90 worker90"],
    ),
    (
        ("storage90 network90 latency90 buffer90 queue90 worker90", 28),
        ["storage90 network90", "latency90 buffer90 queue90", "worker90"],
    ),
    (
        ("network90 latency90 buffer90 queue90 worker90 kernel90", 6),
        ["network90", "latency90", "buffer90", "queue90", "worker90", "kernel90"],
    ),
    (
        ("network90 latency90 buffer90 queue90 worker90 kernel90", 10),
        ["network90", "latency90", "buffer90", "queue90", "worker90", "kernel90"],
    ),
    (
        ("network90 latency90 buffer90 queue90 worker90 kernel90", 18),
        ["network90", "latency90 buffer90", "queue90 worker90", "kernel90"],
    ),
    (
        ("network90 latency90 buffer90 queue90 worker90 kernel90", 28),
        ["network90 latency90 buffer90", "queue90 worker90 kernel90"],
    ),
    (
        ("latency90 buffer90 queue90 worker90 kernel90 signal90", 6),
        ["latency90", "buffer90", "queue90", "worker90", "kernel90", "signal90"],
    ),
    (
        ("latency90 buffer90 queue90 worker90 kernel90 signal90", 10),
        ["latency90", "buffer90", "queue90", "worker90", "kernel90", "signal90"],
    ),
    (
        ("latency90 buffer90 queue90 worker90 kernel90 signal90", 18),
        ["latency90 buffer90", "queue90 worker90", "kernel90 signal90"],
    ),
    (
        ("latency90 buffer90 queue90 worker90 kernel90 signal90", 28),
        ["latency90 buffer90 queue90", "worker90 kernel90 signal90"],
    ),
    (
        ("buffer90 queue90 worker90 kernel90 signal90 packet90", 6),
        ["buffer90", "queue90", "worker90", "kernel90", "signal90", "packet90"],
    ),
    (
        ("buffer90 queue90 worker90 kernel90 signal90 packet90", 10),
        ["buffer90", "queue90", "worker90", "kernel90", "signal90", "packet90"],
    ),
    (
        ("buffer90 queue90 worker90 kernel90 signal90 packet90", 18),
        ["buffer90 queue90", "worker90 kernel90", "signal90 packet90"],
    ),
    (
        ("buffer90 queue90 worker90 kernel90 signal90 packet90", 28),
        ["buffer90 queue90 worker90", "kernel90 signal90 packet90"],
    ),
    (
        ("queue90 worker90 kernel90 signal90 packet90 router90", 6),
        ["queue90", "worker90", "kernel90", "signal90", "packet90", "router90"],
    ),
    (
        ("queue90 worker90 kernel90 signal90 packet90 router90", 10),
        ["queue90", "worker90", "kernel90", "signal90", "packet90", "router90"],
    ),
    (
        ("queue90 worker90 kernel90 signal90 packet90 router90", 18),
        ["queue90 worker90", "kernel90 signal90", "packet90 router90"],
    ),
    (
        ("queue90 worker90 kernel90 signal90 packet90 router90", 28),
        ["queue90 worker90 kernel90", "signal90 packet90 router90"],
    ),
    (
        ("worker90 kernel90 signal90 packet90 router90 cluster90", 6),
        ["worker90", "kernel90", "signal90", "packet90", "router90", "cluster90"],
    ),
    (
        ("worker90 kernel90 signal90 packet90 router90 cluster90", 10),
        ["worker90", "kernel90", "signal90", "packet90", "router90", "cluster90"],
    ),
    (
        ("worker90 kernel90 signal90 packet90 router90 cluster90", 18),
        ["worker90 kernel90", "signal90 packet90", "router90 cluster90"],
    ),
    (
        ("worker90 kernel90 signal90 packet90 router90 cluster90", 28),
        ["worker90 kernel90 signal90", "packet90 router90 cluster90"],
    ),
    (
        ("kernel90 signal90 packet90 router90 cluster90 mirror90", 6),
        ["kernel90", "signal90", "packet90", "router90", "cluster90", "mirror90"],
    ),
    (
        ("kernel90 signal90 packet90 router90 cluster90 mirror90", 10),
        ["kernel90", "signal90", "packet90", "router90", "cluster90", "mirror90"],
    ),
    (
        ("kernel90 signal90 packet90 router90 cluster90 mirror90", 18),
        ["kernel90 signal90", "packet90 router90", "cluster90 mirror90"],
    ),
    (
        ("kernel90 signal90 packet90 router90 cluster90 mirror90", 28),
        ["kernel90 signal90 packet90", "router90 cluster90 mirror90"],
    ),
    (
        ("signal90 packet90 router90 cluster90 mirror90 filter90", 6),
        ["signal90", "packet90", "router90", "cluster90", "mirror90", "filter90"],
    ),
    (
        ("signal90 packet90 router90 cluster90 mirror90 filter90", 10),
        ["signal90", "packet90", "router90", "cluster90", "mirror90", "filter90"],
    ),
    (
        ("signal90 packet90 router90 cluster90 mirror90 filter90", 18),
        ["signal90 packet90", "router90 cluster90", "mirror90 filter90"],
    ),
    (
        ("signal90 packet90 router90 cluster90 mirror90 filter90", 28),
        ["signal90 packet90 router90", "cluster90 mirror90 filter90"],
    ),
    (
        ("packet90 router90 cluster90 mirror90 filter90 ranking90", 6),
        ["packet90", "router90", "cluster90", "mirror90", "filter90", "ranking90"],
    ),
    (
        ("packet90 router90 cluster90 mirror90 filter90 ranking90", 10),
        ["packet90", "router90", "cluster90", "mirror90", "filter90", "ranking90"],
    ),
    (
        ("packet90 router90 cluster90 mirror90 filter90 ranking90", 18),
        ["packet90 router90", "cluster90 mirror90", "filter90 ranking90"],
    ),
    (
        ("packet90 router90 cluster90 mirror90 filter90 ranking90", 28),
        ["packet90 router90 cluster90", "mirror90 filter90 ranking90"],
    ),
    (
        ("router90 cluster90 mirror90 filter90 ranking90 encoding90", 6),
        ["router90", "cluster90", "mirror90", "filter90", "ranking90", "encoding90"],
    ),
    (
        ("router90 cluster90 mirror90 filter90 ranking90 encoding90", 10),
        ["router90", "cluster90", "mirror90", "filter90", "ranking90", "encoding90"],
    ),
    (
        ("router90 cluster90 mirror90 filter90 ranking90 encoding90", 18),
        ["router90 cluster90", "mirror90 filter90", "ranking90", "encoding90"],
    ),
    (
        ("router90 cluster90 mirror90 filter90 ranking90 encoding90", 28),
        ["router90 cluster90 mirror90", "filter90 ranking90", "encoding90"],
    ),
    (
        ("cluster90 mirror90 filter90 ranking90 encoding90 mapping90", 6),
        ["cluster90", "mirror90", "filter90", "ranking90", "encoding90", "mapping90"],
    ),
    (
        ("cluster90 mirror90 filter90 ranking90 encoding90 mapping90", 10),
        ["cluster90", "mirror90", "filter90", "ranking90", "encoding90", "mapping90"],
    ),
    (
        ("cluster90 mirror90 filter90 ranking90 encoding90 mapping90", 18),
        ["cluster90 mirror90", "filter90 ranking90", "encoding90", "mapping90"],
    ),
    (
        ("cluster90 mirror90 filter90 ranking90 encoding90 mapping90", 28),
        ["cluster90 mirror90 filter90", "ranking90 encoding90", "mapping90"],
    ),
    (
        ("mirror90 filter90 ranking90 encoding90 mapping90 record90", 6),
        ["mirror90", "filter90", "ranking90", "encoding90", "mapping90", "record90"],
    ),
    (
        ("mirror90 filter90 ranking90 encoding90 mapping90 record90", 10),
        ["mirror90", "filter90", "ranking90", "encoding90", "mapping90", "record90"],
    ),
    (
        ("mirror90 filter90 ranking90 encoding90 mapping90 record90", 18),
        ["mirror90 filter90", "ranking90", "encoding90", "mapping90 record90"],
    ),
    (
        ("mirror90 filter90 ranking90 encoding90 mapping90 record90", 28),
        ["mirror90 filter90 ranking90", "encoding90 mapping90", "record90"],
    ),
    (
        ("filter90 ranking90 encoding90 mapping90 record90 candle90", 6),
        ["filter90", "ranking90", "encoding90", "mapping90", "record90", "candle90"],
    ),
    (
        ("filter90 ranking90 encoding90 mapping90 record90 candle90", 10),
        ["filter90", "ranking90", "encoding90", "mapping90", "record90", "candle90"],
    ),
    (
        ("filter90 ranking90 encoding90 mapping90 record90 candle90", 18),
        ["filter90 ranking90", "encoding90", "mapping90 record90", "candle90"],
    ),
    (
        ("filter90 ranking90 encoding90 mapping90 record90 candle90", 28),
        ["filter90 ranking90", "encoding90 mapping90", "record90 candle90"],
    ),
    (
        ("ranking90 encoding90 mapping90 record90 candle90 thread90", 6),
        ["ranking90", "encoding90", "mapping90", "record90", "candle90", "thread90"],
    ),
    (
        ("ranking90 encoding90 mapping90 record90 candle90 thread90", 10),
        ["ranking90", "encoding90", "mapping90", "record90", "candle90", "thread90"],
    ),
    (
        ("ranking90 encoding90 mapping90 record90 candle90 thread90", 18),
        ["ranking90", "encoding90", "mapping90 record90", "candle90 thread90"],
    ),
    (
        ("ranking90 encoding90 mapping90 record90 candle90 thread90", 28),
        ["ranking90 encoding90", "mapping90 record90 candle90", "thread90"],
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
