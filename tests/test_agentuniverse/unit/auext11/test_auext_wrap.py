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
        ("round 11: the quick brown fox jumps over the lazy dog", 4),
        ["round", "11:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 11: the quick brown fox jumps over the lazy dog", 8),
        ["round", "11: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 11: the quick brown fox jumps over the lazy dog", 12),
        ["round 11:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 11: the quick brown fox jumps over the lazy dog", 16),
        ["round 11: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 11: the quick brown fox jumps over the lazy dog", 24),
        ["round 11: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 11: the quick brown fox jumps over the lazy dog", 32),
        ["round 11: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 11: agentuniverse is a framework for multi agents", 4),
        ["round", "11:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 11: agentuniverse is a framework for multi agents", 8),
        ["round", "11:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 11: agentuniverse is a framework for multi agents", 12),
        ["round 11:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 11: agentuniverse is a framework for multi agents", 16),
        ["round 11:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 11: agentuniverse is a framework for multi agents", 24),
        ["round 11: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 11: agentuniverse is a framework for multi agents", 32),
        ["round 11: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 11: knowledge stored as vectors enables retrieval", 4),
        ["round", "11:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 11: knowledge stored as vectors enables retrieval", 8),
        ["round", "11:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 11: knowledge stored as vectors enables retrieval", 12),
        ["round 11:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 11: knowledge stored as vectors enables retrieval", 16),
        ["round 11:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 11: knowledge stored as vectors enables retrieval", 24),
        ["round 11: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 11: knowledge stored as vectors enables retrieval", 32),
        ["round 11: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 11: the processor reads the record then stops", 4),
        ["round", "11:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 11: the processor reads the record then stops", 8),
        ["round", "11: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 11: the processor reads the record then stops", 12),
        ["round 11:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 11: the processor reads the record then stops", 16),
        ["round 11: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 11: the processor reads the record then stops", 24),
        ["round 11: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 11: the processor reads the record then stops", 32),
        ["round 11: the processor reads", "the record then stops"],
    ),
    (
        ("round 11: a worker pulls the next task from the queue", 4),
        ["round", "11:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 11: a worker pulls the next task from the queue", 8),
        ["round", "11: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 11: a worker pulls the next task from the queue", 12),
        ["round 11: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 11: a worker pulls the next task from the queue", 16),
        ["round 11: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 11: a worker pulls the next task from the queue", 24),
        ["round 11: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 11: a worker pulls the next task from the queue", 32),
        ["round 11: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 11: signals travel through the network layer", 4),
        ["round", "11:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 11: signals travel through the network layer", 8),
        ["round", "11:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 11: signals travel through the network layer", 12),
        ["round 11:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 11: signals travel through the network layer", 16),
        ["round 11:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 11: signals travel through the network layer", 24),
        ["round 11: signals travel", "through the network", "layer"],
    ),
    (
        ("round 11: signals travel through the network layer", 32),
        ["round 11: signals travel through", "the network layer"],
    ),
    (
        ("round 11: the gateway routes each request by policy", 4),
        ["round", "11:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 11: the gateway routes each request by policy", 8),
        ["round", "11: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 11: the gateway routes each request by policy", 12),
        ["round 11:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 11: the gateway routes each request by policy", 16),
        ["round 11: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 11: the gateway routes each request by policy", 24),
        ["round 11: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 11: the gateway routes each request by policy", 32),
        ["round 11: the gateway routes", "each request by policy"],
    ),
    (
        ("round 11: memory grows until the buffer is full", 4),
        ["round", "11:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 11: memory grows until the buffer is full", 8),
        ["round", "11:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 11: memory grows until the buffer is full", 12),
        ["round 11:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 11: memory grows until the buffer is full", 16),
        ["round 11: memory", "grows until the", "buffer is full"],
    ),
    (("round 11: memory grows until the buffer is full", 24), ["round 11: memory grows", "until the buffer is full"]),
    (("round 11: memory grows until the buffer is full", 32), ["round 11: memory grows until the", "buffer is full"]),
    (
        ("round 11: the cluster mirrors every packet twice", 4),
        ["round", "11:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 11: the cluster mirrors every packet twice", 8),
        ["round", "11: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 11: the cluster mirrors every packet twice", 12),
        ["round 11:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 11: the cluster mirrors every packet twice", 16),
        ["round 11: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 11: the cluster mirrors every packet twice", 24),
        ["round 11: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 11: the cluster mirrors every packet twice", 32), ["round 11: the cluster mirrors", "every packet twice"]),
    (
        ("round 11: ranking uses tokens learned from the corpus", 4),
        ["round", "11:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 11: ranking uses tokens learned from the corpus", 8),
        ["round", "11:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 11: ranking uses tokens learned from the corpus", 12),
        ["round 11:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 11: ranking uses tokens learned from the corpus", 16),
        ["round 11:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 11: ranking uses tokens learned from the corpus", 24),
        ["round 11: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 11: ranking uses tokens learned from the corpus", 32),
        ["round 11: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 11: a long session ends when the candle dies", 4),
        ["round", "11:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 11: a long session ends when the candle dies", 8),
        ["round", "11: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 11: a long session ends when the candle dies", 12),
        ["round 11: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 11: a long session ends when the candle dies", 16),
        ["round 11: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 11: a long session ends when the candle dies", 24),
        ["round 11: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 11: a long session ends when the candle dies", 32),
        ["round 11: a long session ends", "when the candle dies"],
    ),
    (
        ("round 11: encode the prompt then map the result", 4),
        ["round", "11:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 11: encode the prompt then map the result", 8),
        ["round", "11:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 11: encode the prompt then map the result", 12),
        ["round 11:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 11: encode the prompt then map the result", 16),
        ["round 11: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 11: encode the prompt then map the result", 24),
        ["round 11: encode the", "prompt then map the", "result"],
    ),
    (("round 11: encode the prompt then map the result", 32), ["round 11: encode the prompt then", "map the result"]),
    (
        ("round 11: the kernel wakes the worker at dawn", 4),
        ["round", "11:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 11: the kernel wakes the worker at dawn", 8),
        ["round", "11: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 11: the kernel wakes the worker at dawn", 12),
        ["round 11:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 11: the kernel wakes the worker at dawn", 16), ["round 11: the", "kernel wakes the", "worker at dawn"]),
    (("round 11: the kernel wakes the worker at dawn", 24), ["round 11: the kernel", "wakes the worker at dawn"]),
    (("round 11: the kernel wakes the worker at dawn", 32), ["round 11: the kernel wakes the", "worker at dawn"]),
    (
        ("round 11: service latency drops after the patch", 4),
        ["round", "11:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 11: service latency drops after the patch", 8),
        ["round", "11:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 11: service latency drops after the patch", 12),
        ["round 11:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 11: service latency drops after the patch", 16),
        ["round 11:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 11: service latency drops after the patch", 24),
        ["round 11: service", "latency drops after the", "patch"],
    ),
    (("round 11: service latency drops after the patch", 32), ["round 11: service latency drops", "after the patch"]),
    (
        ("round 11: the library caches every vector it sees", 4),
        ["round", "11:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 11: the library caches every vector it sees", 8),
        ["round", "11: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 11: the library caches every vector it sees", 12),
        ["round 11:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 11: the library caches every vector it sees", 16),
        ["round 11: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 11: the library caches every vector it sees", 24),
        ["round 11: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 11: the library caches every vector it sees", 32),
        ["round 11: the library caches", "every vector it sees"],
    ),
    (
        ("round 11: agents argue then the debate resolves", 4),
        ["round", "11:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 11: agents argue then the debate resolves", 8),
        ["round", "11:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 11: agents argue then the debate resolves", 12),
        ["round 11:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 11: agents argue then the debate resolves", 16),
        ["round 11: agents", "argue then the", "debate resolves"],
    ),
    (("round 11: agents argue then the debate resolves", 24), ["round 11: agents argue", "then the debate resolves"]),
    (("round 11: agents argue then the debate resolves", 32), ["round 11: agents argue then the", "debate resolves"]),
    (
        ("round 11: the filter keeps only strong matches", 4),
        ["round", "11:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 11: the filter keeps only strong matches", 8),
        ["round", "11: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 11: the filter keeps only strong matches", 12),
        ["round 11:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 11: the filter keeps only strong matches", 16),
        ["round 11: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 11: the filter keeps only strong matches", 24), ["round 11: the filter", "keeps only strong", "matches"]),
    (("round 11: the filter keeps only strong matches", 32), ["round 11: the filter keeps only", "strong matches"]),
    (
        ("round 11: the model answers with a short reply", 4),
        ["round", "11:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 11: the model answers with a short reply", 8),
        ["round", "11: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 11: the model answers with a short reply", 12),
        ["round 11:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 11: the model answers with a short reply", 16),
        ["round 11: the", "model answers", "with a short", "reply"],
    ),
    (("round 11: the model answers with a short reply", 24), ["round 11: the model", "answers with a short", "reply"]),
    (("round 11: the model answers with a short reply", 32), ["round 11: the model answers with", "a short reply"]),
    (
        ("round 11: the recorder stores the reasoning trace", 4),
        ["round", "11:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 11: the recorder stores the reasoning trace", 8),
        ["round", "11: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 11: the recorder stores the reasoning trace", 12),
        ["round 11:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 11: the recorder stores the reasoning trace", 16),
        ["round 11: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 11: the recorder stores the reasoning trace", 24),
        ["round 11: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 11: the recorder stores the reasoning trace", 32),
        ["round 11: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 11: the angel watches the processor run", 4),
        ["round", "11:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 11: the angel watches the processor run", 8),
        ["round", "11: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 11: the angel watches the processor run", 12),
        ["round 11:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 11: the angel watches the processor run", 16), ["round 11: the", "angel watches", "the processor", "run"]),
    (("round 11: the angel watches the processor run", 24), ["round 11: the angel", "watches the processor", "run"]),
    (("round 11: the angel watches the processor run", 32), ["round 11: the angel watches the", "processor run"]),
    (
        ("round 11: angle of the vector decides the match", 4),
        ["round", "11:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 11: angle of the vector decides the match", 8),
        ["round", "11:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 11: angle of the vector decides the match", 12),
        ["round 11:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 11: angle of the vector decides the match", 16),
        ["round 11: angle", "of the vector", "decides the", "match"],
    ),
    (("round 11: angle of the vector decides the match", 24), ["round 11: angle of the", "vector decides the match"]),
    (("round 11: angle of the vector decides the match", 32), ["round 11: angle of the vector", "decides the match"]),
    (
        ("round 11: the candle burns twice as long at night", 4),
        ["round", "11:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 11: the candle burns twice as long at night", 8),
        ["round", "11: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 11: the candle burns twice as long at night", 12),
        ["round 11:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 11: the candle burns twice as long at night", 16),
        ["round 11: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 11: the candle burns twice as long at night", 24),
        ["round 11: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 11: the candle burns twice as long at night", 32),
        ["round 11: the candle burns twice", "as long at night"],
    ),
    (
        ("round 11: a mirror of the universe in one line", 4),
        ["round", "11:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 11: a mirror of the universe in one line", 8),
        ["round", "11: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 11: a mirror of the universe in one line", 12),
        ["round 11: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 11: a mirror of the universe in one line", 16),
        ["round 11: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 11: a mirror of the universe in one line", 24), ["round 11: a mirror of", "the universe in one line"]),
    (("round 11: a mirror of the universe in one line", 32), ["round 11: a mirror of the", "universe in one line"]),
    (
        ("round 11: the queue drains before the storm", 4),
        ["round", "11:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 11: the queue drains before the storm", 8),
        ["round", "11: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 11: the queue drains before the storm", 12), ["round 11:", "the queue", "drains", "before the", "storm"]),
    (("round 11: the queue drains before the storm", 16), ["round 11: the", "queue drains", "before the storm"]),
    (("round 11: the queue drains before the storm", 24), ["round 11: the queue", "drains before the storm"]),
    (("round 11: the queue drains before the storm", 32), ["round 11: the queue drains", "before the storm"]),
    (
        ("kitten11 sitting11 agent11 angle11 universe11 memory11", 6),
        ["kitten11", "sitting11", "agent11", "angle11", "universe11", "memory11"],
    ),
    (
        ("kitten11 sitting11 agent11 angle11 universe11 memory11", 10),
        ["kitten11", "sitting11", "agent11", "angle11", "universe11", "memory11"],
    ),
    (
        ("kitten11 sitting11 agent11 angle11 universe11 memory11", 18),
        ["kitten11 sitting11", "agent11 angle11", "universe11", "memory11"],
    ),
    (
        ("kitten11 sitting11 agent11 angle11 universe11 memory11", 28),
        ["kitten11 sitting11 agent11", "angle11 universe11 memory11"],
    ),
    (
        ("sitting11 agent11 angle11 universe11 memory11 stream11", 6),
        ["sitting11", "agent11", "angle11", "universe11", "memory11", "stream11"],
    ),
    (
        ("sitting11 agent11 angle11 universe11 memory11 stream11", 10),
        ["sitting11", "agent11", "angle11", "universe11", "memory11", "stream11"],
    ),
    (
        ("sitting11 agent11 angle11 universe11 memory11 stream11", 18),
        ["sitting11 agent11", "angle11 universe11", "memory11 stream11"],
    ),
    (
        ("sitting11 agent11 angle11 universe11 memory11 stream11", 28),
        ["sitting11 agent11 angle11", "universe11 memory11 stream11"],
    ),
    (
        ("agent11 angle11 universe11 memory11 stream11 context11", 6),
        ["agent11", "angle11", "universe11", "memory11", "stream11", "context11"],
    ),
    (
        ("agent11 angle11 universe11 memory11 stream11 context11", 10),
        ["agent11", "angle11", "universe11", "memory11", "stream11", "context11"],
    ),
    (
        ("agent11 angle11 universe11 memory11 stream11 context11", 18),
        ["agent11 angle11", "universe11", "memory11 stream11", "context11"],
    ),
    (
        ("agent11 angle11 universe11 memory11 stream11 context11", 28),
        ["agent11 angle11 universe11", "memory11 stream11 context11"],
    ),
    (
        ("angle11 universe11 memory11 stream11 context11 knowledge11", 6),
        ["angle11", "universe11", "memory11", "stream11", "context11", "knowledge11"],
    ),
    (
        ("angle11 universe11 memory11 stream11 context11 knowledge11", 10),
        ["angle11", "universe11", "memory11", "stream11", "context11", "knowledge11"],
    ),
    (
        ("angle11 universe11 memory11 stream11 context11 knowledge11", 18),
        ["angle11 universe11", "memory11 stream11", "context11", "knowledge11"],
    ),
    (
        ("angle11 universe11 memory11 stream11 context11 knowledge11", 28),
        ["angle11 universe11 memory11", "stream11 context11", "knowledge11"],
    ),
    (
        ("universe11 memory11 stream11 context11 knowledge11 vector11", 6),
        ["universe11", "memory11", "stream11", "context11", "knowledge11", "vector11"],
    ),
    (
        ("universe11 memory11 stream11 context11 knowledge11 vector11", 10),
        ["universe11", "memory11", "stream11", "context11", "knowledge11", "vector11"],
    ),
    (
        ("universe11 memory11 stream11 context11 knowledge11 vector11", 18),
        ["universe11", "memory11 stream11", "context11", "knowledge11", "vector11"],
    ),
    (
        ("universe11 memory11 stream11 context11 knowledge11 vector11", 28),
        ["universe11 memory11 stream11", "context11 knowledge11", "vector11"],
    ),
    (
        ("memory11 stream11 context11 knowledge11 vector11 processor11", 6),
        ["memory11", "stream11", "context11", "knowledge11", "vector11", "processor11"],
    ),
    (
        ("memory11 stream11 context11 knowledge11 vector11 processor11", 10),
        ["memory11", "stream11", "context11", "knowledge11", "vector11", "processor11"],
    ),
    (
        ("memory11 stream11 context11 knowledge11 vector11 processor11", 18),
        ["memory11 stream11", "context11", "knowledge11", "vector11", "processor11"],
    ),
    (
        ("memory11 stream11 context11 knowledge11 vector11 processor11", 28),
        ["memory11 stream11 context11", "knowledge11 vector11", "processor11"],
    ),
    (
        ("stream11 context11 knowledge11 vector11 processor11 reasoning11", 6),
        ["stream11", "context11", "knowledge11", "vector11", "processor11", "reasoning11"],
    ),
    (
        ("stream11 context11 knowledge11 vector11 processor11 reasoning11", 10),
        ["stream11", "context11", "knowledge11", "vector11", "processor11", "reasoning11"],
    ),
    (
        ("stream11 context11 knowledge11 vector11 processor11 reasoning11", 18),
        ["stream11 context11", "knowledge11", "vector11", "processor11", "reasoning11"],
    ),
    (
        ("stream11 context11 knowledge11 vector11 processor11 reasoning11", 28),
        ["stream11 context11", "knowledge11 vector11", "processor11 reasoning11"],
    ),
    (
        ("context11 knowledge11 vector11 processor11 reasoning11 machine11", 6),
        ["context11", "knowledge11", "vector11", "processor11", "reasoning11", "machine11"],
    ),
    (
        ("context11 knowledge11 vector11 processor11 reasoning11 machine11", 10),
        ["context11", "knowledge11", "vector11", "processor11", "reasoning11", "machine11"],
    ),
    (
        ("context11 knowledge11 vector11 processor11 reasoning11 machine11", 18),
        ["context11", "knowledge11", "vector11", "processor11", "reasoning11", "machine11"],
    ),
    (
        ("context11 knowledge11 vector11 processor11 reasoning11 machine11", 28),
        ["context11 knowledge11", "vector11 processor11", "reasoning11 machine11"],
    ),
    (
        ("knowledge11 vector11 processor11 reasoning11 machine11 learning11", 6),
        ["knowledge11", "vector11", "processor11", "reasoning11", "machine11", "learning11"],
    ),
    (
        ("knowledge11 vector11 processor11 reasoning11 machine11 learning11", 10),
        ["knowledge11", "vector11", "processor11", "reasoning11", "machine11", "learning11"],
    ),
    (
        ("knowledge11 vector11 processor11 reasoning11 machine11 learning11", 18),
        ["knowledge11", "vector11", "processor11", "reasoning11", "machine11", "learning11"],
    ),
    (
        ("knowledge11 vector11 processor11 reasoning11 machine11 learning11", 28),
        ["knowledge11 vector11", "processor11 reasoning11", "machine11 learning11"],
    ),
    (
        ("vector11 processor11 reasoning11 machine11 learning11 model11", 6),
        ["vector11", "processor11", "reasoning11", "machine11", "learning11", "model11"],
    ),
    (
        ("vector11 processor11 reasoning11 machine11 learning11 model11", 10),
        ["vector11", "processor11", "reasoning11", "machine11", "learning11", "model11"],
    ),
    (
        ("vector11 processor11 reasoning11 machine11 learning11 model11", 18),
        ["vector11", "processor11", "reasoning11", "machine11", "learning11 model11"],
    ),
    (
        ("vector11 processor11 reasoning11 machine11 learning11 model11", 28),
        ["vector11 processor11", "reasoning11 machine11", "learning11 model11"],
    ),
    (
        ("processor11 reasoning11 machine11 learning11 model11 token11", 6),
        ["processor11", "reasoning11", "machine11", "learning11", "model11", "token11"],
    ),
    (
        ("processor11 reasoning11 machine11 learning11 model11 token11", 10),
        ["processor11", "reasoning11", "machine11", "learning11", "model11", "token11"],
    ),
    (
        ("processor11 reasoning11 machine11 learning11 model11 token11", 18),
        ["processor11", "reasoning11", "machine11", "learning11 model11", "token11"],
    ),
    (
        ("processor11 reasoning11 machine11 learning11 model11 token11", 28),
        ["processor11 reasoning11", "machine11 learning11 model11", "token11"],
    ),
    (
        ("reasoning11 machine11 learning11 model11 token11 prompt11", 6),
        ["reasoning11", "machine11", "learning11", "model11", "token11", "prompt11"],
    ),
    (
        ("reasoning11 machine11 learning11 model11 token11 prompt11", 10),
        ["reasoning11", "machine11", "learning11", "model11", "token11", "prompt11"],
    ),
    (
        ("reasoning11 machine11 learning11 model11 token11 prompt11", 18),
        ["reasoning11", "machine11", "learning11 model11", "token11 prompt11"],
    ),
    (
        ("reasoning11 machine11 learning11 model11 token11 prompt11", 28),
        ["reasoning11 machine11", "learning11 model11 token11", "prompt11"],
    ),
    (
        ("machine11 learning11 model11 token11 prompt11 session11", 6),
        ["machine11", "learning11", "model11", "token11", "prompt11", "session11"],
    ),
    (
        ("machine11 learning11 model11 token11 prompt11 session11", 10),
        ["machine11", "learning11", "model11", "token11", "prompt11", "session11"],
    ),
    (
        ("machine11 learning11 model11 token11 prompt11 session11", 18),
        ["machine11", "learning11 model11", "token11 prompt11", "session11"],
    ),
    (
        ("machine11 learning11 model11 token11 prompt11 session11", 28),
        ["machine11 learning11 model11", "token11 prompt11 session11"],
    ),
    (
        ("learning11 model11 token11 prompt11 session11 library11", 6),
        ["learning11", "model11", "token11", "prompt11", "session11", "library11"],
    ),
    (
        ("learning11 model11 token11 prompt11 session11 library11", 10),
        ["learning11", "model11", "token11", "prompt11", "session11", "library11"],
    ),
    (
        ("learning11 model11 token11 prompt11 session11 library11", 18),
        ["learning11 model11", "token11 prompt11", "session11", "library11"],
    ),
    (
        ("learning11 model11 token11 prompt11 session11 library11", 28),
        ["learning11 model11 token11", "prompt11 session11 library11"],
    ),
    (
        ("model11 token11 prompt11 session11 library11 service11", 6),
        ["model11", "token11", "prompt11", "session11", "library11", "service11"],
    ),
    (
        ("model11 token11 prompt11 session11 library11 service11", 10),
        ["model11", "token11", "prompt11", "session11", "library11", "service11"],
    ),
    (
        ("model11 token11 prompt11 session11 library11 service11", 18),
        ["model11 token11", "prompt11 session11", "library11", "service11"],
    ),
    (
        ("model11 token11 prompt11 session11 library11 service11", 28),
        ["model11 token11 prompt11", "session11 library11", "service11"],
    ),
    (
        ("token11 prompt11 session11 library11 service11 gateway11", 6),
        ["token11", "prompt11", "session11", "library11", "service11", "gateway11"],
    ),
    (
        ("token11 prompt11 session11 library11 service11 gateway11", 10),
        ["token11", "prompt11", "session11", "library11", "service11", "gateway11"],
    ),
    (
        ("token11 prompt11 session11 library11 service11 gateway11", 18),
        ["token11 prompt11", "session11", "library11", "service11", "gateway11"],
    ),
    (
        ("token11 prompt11 session11 library11 service11 gateway11", 28),
        ["token11 prompt11 session11", "library11 service11", "gateway11"],
    ),
    (
        ("prompt11 session11 library11 service11 gateway11 storage11", 6),
        ["prompt11", "session11", "library11", "service11", "gateway11", "storage11"],
    ),
    (
        ("prompt11 session11 library11 service11 gateway11 storage11", 10),
        ["prompt11", "session11", "library11", "service11", "gateway11", "storage11"],
    ),
    (
        ("prompt11 session11 library11 service11 gateway11 storage11", 18),
        ["prompt11 session11", "library11", "service11", "gateway11", "storage11"],
    ),
    (
        ("prompt11 session11 library11 service11 gateway11 storage11", 28),
        ["prompt11 session11 library11", "service11 gateway11", "storage11"],
    ),
    (
        ("session11 library11 service11 gateway11 storage11 network11", 6),
        ["session11", "library11", "service11", "gateway11", "storage11", "network11"],
    ),
    (
        ("session11 library11 service11 gateway11 storage11 network11", 10),
        ["session11", "library11", "service11", "gateway11", "storage11", "network11"],
    ),
    (
        ("session11 library11 service11 gateway11 storage11 network11", 18),
        ["session11", "library11", "service11", "gateway11", "storage11", "network11"],
    ),
    (
        ("session11 library11 service11 gateway11 storage11 network11", 28),
        ["session11 library11", "service11 gateway11", "storage11 network11"],
    ),
    (
        ("library11 service11 gateway11 storage11 network11 latency11", 6),
        ["library11", "service11", "gateway11", "storage11", "network11", "latency11"],
    ),
    (
        ("library11 service11 gateway11 storage11 network11 latency11", 10),
        ["library11", "service11", "gateway11", "storage11", "network11", "latency11"],
    ),
    (
        ("library11 service11 gateway11 storage11 network11 latency11", 18),
        ["library11", "service11", "gateway11", "storage11", "network11", "latency11"],
    ),
    (
        ("library11 service11 gateway11 storage11 network11 latency11", 28),
        ["library11 service11", "gateway11 storage11", "network11 latency11"],
    ),
    (
        ("service11 gateway11 storage11 network11 latency11 buffer11", 6),
        ["service11", "gateway11", "storage11", "network11", "latency11", "buffer11"],
    ),
    (
        ("service11 gateway11 storage11 network11 latency11 buffer11", 10),
        ["service11", "gateway11", "storage11", "network11", "latency11", "buffer11"],
    ),
    (
        ("service11 gateway11 storage11 network11 latency11 buffer11", 18),
        ["service11", "gateway11", "storage11", "network11", "latency11 buffer11"],
    ),
    (
        ("service11 gateway11 storage11 network11 latency11 buffer11", 28),
        ["service11 gateway11", "storage11 network11", "latency11 buffer11"],
    ),
    (
        ("gateway11 storage11 network11 latency11 buffer11 queue11", 6),
        ["gateway11", "storage11", "network11", "latency11", "buffer11", "queue11"],
    ),
    (
        ("gateway11 storage11 network11 latency11 buffer11 queue11", 10),
        ["gateway11", "storage11", "network11", "latency11", "buffer11", "queue11"],
    ),
    (
        ("gateway11 storage11 network11 latency11 buffer11 queue11", 18),
        ["gateway11", "storage11", "network11", "latency11 buffer11", "queue11"],
    ),
    (
        ("gateway11 storage11 network11 latency11 buffer11 queue11", 28),
        ["gateway11 storage11", "network11 latency11 buffer11", "queue11"],
    ),
    (
        ("storage11 network11 latency11 buffer11 queue11 worker11", 6),
        ["storage11", "network11", "latency11", "buffer11", "queue11", "worker11"],
    ),
    (
        ("storage11 network11 latency11 buffer11 queue11 worker11", 10),
        ["storage11", "network11", "latency11", "buffer11", "queue11", "worker11"],
    ),
    (
        ("storage11 network11 latency11 buffer11 queue11 worker11", 18),
        ["storage11", "network11", "latency11 buffer11", "queue11 worker11"],
    ),
    (
        ("storage11 network11 latency11 buffer11 queue11 worker11", 28),
        ["storage11 network11", "latency11 buffer11 queue11", "worker11"],
    ),
    (
        ("network11 latency11 buffer11 queue11 worker11 kernel11", 6),
        ["network11", "latency11", "buffer11", "queue11", "worker11", "kernel11"],
    ),
    (
        ("network11 latency11 buffer11 queue11 worker11 kernel11", 10),
        ["network11", "latency11", "buffer11", "queue11", "worker11", "kernel11"],
    ),
    (
        ("network11 latency11 buffer11 queue11 worker11 kernel11", 18),
        ["network11", "latency11 buffer11", "queue11 worker11", "kernel11"],
    ),
    (
        ("network11 latency11 buffer11 queue11 worker11 kernel11", 28),
        ["network11 latency11 buffer11", "queue11 worker11 kernel11"],
    ),
    (
        ("latency11 buffer11 queue11 worker11 kernel11 signal11", 6),
        ["latency11", "buffer11", "queue11", "worker11", "kernel11", "signal11"],
    ),
    (
        ("latency11 buffer11 queue11 worker11 kernel11 signal11", 10),
        ["latency11", "buffer11", "queue11", "worker11", "kernel11", "signal11"],
    ),
    (
        ("latency11 buffer11 queue11 worker11 kernel11 signal11", 18),
        ["latency11 buffer11", "queue11 worker11", "kernel11 signal11"],
    ),
    (
        ("latency11 buffer11 queue11 worker11 kernel11 signal11", 28),
        ["latency11 buffer11 queue11", "worker11 kernel11 signal11"],
    ),
    (
        ("buffer11 queue11 worker11 kernel11 signal11 packet11", 6),
        ["buffer11", "queue11", "worker11", "kernel11", "signal11", "packet11"],
    ),
    (
        ("buffer11 queue11 worker11 kernel11 signal11 packet11", 10),
        ["buffer11", "queue11", "worker11", "kernel11", "signal11", "packet11"],
    ),
    (
        ("buffer11 queue11 worker11 kernel11 signal11 packet11", 18),
        ["buffer11 queue11", "worker11 kernel11", "signal11 packet11"],
    ),
    (
        ("buffer11 queue11 worker11 kernel11 signal11 packet11", 28),
        ["buffer11 queue11 worker11", "kernel11 signal11 packet11"],
    ),
    (
        ("queue11 worker11 kernel11 signal11 packet11 router11", 6),
        ["queue11", "worker11", "kernel11", "signal11", "packet11", "router11"],
    ),
    (
        ("queue11 worker11 kernel11 signal11 packet11 router11", 10),
        ["queue11", "worker11", "kernel11", "signal11", "packet11", "router11"],
    ),
    (
        ("queue11 worker11 kernel11 signal11 packet11 router11", 18),
        ["queue11 worker11", "kernel11 signal11", "packet11 router11"],
    ),
    (
        ("queue11 worker11 kernel11 signal11 packet11 router11", 28),
        ["queue11 worker11 kernel11", "signal11 packet11 router11"],
    ),
    (
        ("worker11 kernel11 signal11 packet11 router11 cluster11", 6),
        ["worker11", "kernel11", "signal11", "packet11", "router11", "cluster11"],
    ),
    (
        ("worker11 kernel11 signal11 packet11 router11 cluster11", 10),
        ["worker11", "kernel11", "signal11", "packet11", "router11", "cluster11"],
    ),
    (
        ("worker11 kernel11 signal11 packet11 router11 cluster11", 18),
        ["worker11 kernel11", "signal11 packet11", "router11 cluster11"],
    ),
    (
        ("worker11 kernel11 signal11 packet11 router11 cluster11", 28),
        ["worker11 kernel11 signal11", "packet11 router11 cluster11"],
    ),
    (
        ("kernel11 signal11 packet11 router11 cluster11 mirror11", 6),
        ["kernel11", "signal11", "packet11", "router11", "cluster11", "mirror11"],
    ),
    (
        ("kernel11 signal11 packet11 router11 cluster11 mirror11", 10),
        ["kernel11", "signal11", "packet11", "router11", "cluster11", "mirror11"],
    ),
    (
        ("kernel11 signal11 packet11 router11 cluster11 mirror11", 18),
        ["kernel11 signal11", "packet11 router11", "cluster11 mirror11"],
    ),
    (
        ("kernel11 signal11 packet11 router11 cluster11 mirror11", 28),
        ["kernel11 signal11 packet11", "router11 cluster11 mirror11"],
    ),
    (
        ("signal11 packet11 router11 cluster11 mirror11 filter11", 6),
        ["signal11", "packet11", "router11", "cluster11", "mirror11", "filter11"],
    ),
    (
        ("signal11 packet11 router11 cluster11 mirror11 filter11", 10),
        ["signal11", "packet11", "router11", "cluster11", "mirror11", "filter11"],
    ),
    (
        ("signal11 packet11 router11 cluster11 mirror11 filter11", 18),
        ["signal11 packet11", "router11 cluster11", "mirror11 filter11"],
    ),
    (
        ("signal11 packet11 router11 cluster11 mirror11 filter11", 28),
        ["signal11 packet11 router11", "cluster11 mirror11 filter11"],
    ),
    (
        ("packet11 router11 cluster11 mirror11 filter11 ranking11", 6),
        ["packet11", "router11", "cluster11", "mirror11", "filter11", "ranking11"],
    ),
    (
        ("packet11 router11 cluster11 mirror11 filter11 ranking11", 10),
        ["packet11", "router11", "cluster11", "mirror11", "filter11", "ranking11"],
    ),
    (
        ("packet11 router11 cluster11 mirror11 filter11 ranking11", 18),
        ["packet11 router11", "cluster11 mirror11", "filter11 ranking11"],
    ),
    (
        ("packet11 router11 cluster11 mirror11 filter11 ranking11", 28),
        ["packet11 router11 cluster11", "mirror11 filter11 ranking11"],
    ),
    (
        ("router11 cluster11 mirror11 filter11 ranking11 encoding11", 6),
        ["router11", "cluster11", "mirror11", "filter11", "ranking11", "encoding11"],
    ),
    (
        ("router11 cluster11 mirror11 filter11 ranking11 encoding11", 10),
        ["router11", "cluster11", "mirror11", "filter11", "ranking11", "encoding11"],
    ),
    (
        ("router11 cluster11 mirror11 filter11 ranking11 encoding11", 18),
        ["router11 cluster11", "mirror11 filter11", "ranking11", "encoding11"],
    ),
    (
        ("router11 cluster11 mirror11 filter11 ranking11 encoding11", 28),
        ["router11 cluster11 mirror11", "filter11 ranking11", "encoding11"],
    ),
    (
        ("cluster11 mirror11 filter11 ranking11 encoding11 mapping11", 6),
        ["cluster11", "mirror11", "filter11", "ranking11", "encoding11", "mapping11"],
    ),
    (
        ("cluster11 mirror11 filter11 ranking11 encoding11 mapping11", 10),
        ["cluster11", "mirror11", "filter11", "ranking11", "encoding11", "mapping11"],
    ),
    (
        ("cluster11 mirror11 filter11 ranking11 encoding11 mapping11", 18),
        ["cluster11 mirror11", "filter11 ranking11", "encoding11", "mapping11"],
    ),
    (
        ("cluster11 mirror11 filter11 ranking11 encoding11 mapping11", 28),
        ["cluster11 mirror11 filter11", "ranking11 encoding11", "mapping11"],
    ),
    (
        ("mirror11 filter11 ranking11 encoding11 mapping11 record11", 6),
        ["mirror11", "filter11", "ranking11", "encoding11", "mapping11", "record11"],
    ),
    (
        ("mirror11 filter11 ranking11 encoding11 mapping11 record11", 10),
        ["mirror11", "filter11", "ranking11", "encoding11", "mapping11", "record11"],
    ),
    (
        ("mirror11 filter11 ranking11 encoding11 mapping11 record11", 18),
        ["mirror11 filter11", "ranking11", "encoding11", "mapping11 record11"],
    ),
    (
        ("mirror11 filter11 ranking11 encoding11 mapping11 record11", 28),
        ["mirror11 filter11 ranking11", "encoding11 mapping11", "record11"],
    ),
    (
        ("filter11 ranking11 encoding11 mapping11 record11 candle11", 6),
        ["filter11", "ranking11", "encoding11", "mapping11", "record11", "candle11"],
    ),
    (
        ("filter11 ranking11 encoding11 mapping11 record11 candle11", 10),
        ["filter11", "ranking11", "encoding11", "mapping11", "record11", "candle11"],
    ),
    (
        ("filter11 ranking11 encoding11 mapping11 record11 candle11", 18),
        ["filter11 ranking11", "encoding11", "mapping11 record11", "candle11"],
    ),
    (
        ("filter11 ranking11 encoding11 mapping11 record11 candle11", 28),
        ["filter11 ranking11", "encoding11 mapping11", "record11 candle11"],
    ),
    (
        ("ranking11 encoding11 mapping11 record11 candle11 thread11", 6),
        ["ranking11", "encoding11", "mapping11", "record11", "candle11", "thread11"],
    ),
    (
        ("ranking11 encoding11 mapping11 record11 candle11 thread11", 10),
        ["ranking11", "encoding11", "mapping11", "record11", "candle11", "thread11"],
    ),
    (
        ("ranking11 encoding11 mapping11 record11 candle11 thread11", 18),
        ["ranking11", "encoding11", "mapping11 record11", "candle11 thread11"],
    ),
    (
        ("ranking11 encoding11 mapping11 record11 candle11 thread11", 28),
        ["ranking11 encoding11", "mapping11 record11 candle11", "thread11"],
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
