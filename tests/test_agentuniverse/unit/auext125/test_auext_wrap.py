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
        ("round 125: the quick brown fox jumps over the lazy dog", 4),
        ["round", "125:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 125: the quick brown fox jumps over the lazy dog", 8),
        ["round", "125: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 125: the quick brown fox jumps over the lazy dog", 12),
        ["round 125:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 125: the quick brown fox jumps over the lazy dog", 16),
        ["round 125: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 125: the quick brown fox jumps over the lazy dog", 24),
        ["round 125: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 125: the quick brown fox jumps over the lazy dog", 32),
        ["round 125: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 125: agentuniverse is a framework for multi agents", 4),
        ["round", "125:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 125: agentuniverse is a framework for multi agents", 8),
        ["round", "125:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 125: agentuniverse is a framework for multi agents", 12),
        ["round 125:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 125: agentuniverse is a framework for multi agents", 16),
        ["round 125:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 125: agentuniverse is a framework for multi agents", 24),
        ["round 125: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 125: agentuniverse is a framework for multi agents", 32),
        ["round 125: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 125: knowledge stored as vectors enables retrieval", 4),
        ["round", "125:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 125: knowledge stored as vectors enables retrieval", 8),
        ["round", "125:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 125: knowledge stored as vectors enables retrieval", 12),
        ["round 125:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 125: knowledge stored as vectors enables retrieval", 16),
        ["round 125:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 125: knowledge stored as vectors enables retrieval", 24),
        ["round 125: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 125: knowledge stored as vectors enables retrieval", 32),
        ["round 125: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 125: the processor reads the record then stops", 4),
        ["round", "125:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 125: the processor reads the record then stops", 8),
        ["round", "125: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 125: the processor reads the record then stops", 12),
        ["round 125:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 125: the processor reads the record then stops", 16),
        ["round 125: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 125: the processor reads the record then stops", 24),
        ["round 125: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 125: the processor reads the record then stops", 32),
        ["round 125: the processor reads", "the record then stops"],
    ),
    (
        ("round 125: a worker pulls the next task from the queue", 4),
        ["round", "125:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 125: a worker pulls the next task from the queue", 8),
        ["round", "125: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 125: a worker pulls the next task from the queue", 12),
        ["round 125: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 125: a worker pulls the next task from the queue", 16),
        ["round 125: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 125: a worker pulls the next task from the queue", 24),
        ["round 125: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 125: a worker pulls the next task from the queue", 32),
        ["round 125: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 125: signals travel through the network layer", 4),
        ["round", "125:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 125: signals travel through the network layer", 8),
        ["round", "125:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 125: signals travel through the network layer", 12),
        ["round 125:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 125: signals travel through the network layer", 16),
        ["round 125:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 125: signals travel through the network layer", 24),
        ["round 125: signals", "travel through the", "network layer"],
    ),
    (
        ("round 125: signals travel through the network layer", 32),
        ["round 125: signals travel", "through the network layer"],
    ),
    (
        ("round 125: the gateway routes each request by policy", 4),
        ["round", "125:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 125: the gateway routes each request by policy", 8),
        ["round", "125: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 125: the gateway routes each request by policy", 12),
        ["round 125:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 125: the gateway routes each request by policy", 16),
        ["round 125: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 125: the gateway routes each request by policy", 24),
        ["round 125: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 125: the gateway routes each request by policy", 32),
        ["round 125: the gateway routes", "each request by policy"],
    ),
    (
        ("round 125: memory grows until the buffer is full", 4),
        ["round", "125:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 125: memory grows until the buffer is full", 8),
        ["round", "125:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 125: memory grows until the buffer is full", 12),
        ["round 125:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 125: memory grows until the buffer is full", 16),
        ["round 125:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 125: memory grows until the buffer is full", 24), ["round 125: memory grows", "until the buffer is full"]),
    (("round 125: memory grows until the buffer is full", 32), ["round 125: memory grows until", "the buffer is full"]),
    (
        ("round 125: the cluster mirrors every packet twice", 4),
        ["round", "125:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 125: the cluster mirrors every packet twice", 8),
        ["round", "125: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 125: the cluster mirrors every packet twice", 12),
        ["round 125:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 125: the cluster mirrors every packet twice", 16),
        ["round 125: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 125: the cluster mirrors every packet twice", 24),
        ["round 125: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 125: the cluster mirrors every packet twice", 32),
        ["round 125: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 125: ranking uses tokens learned from the corpus", 4),
        ["round", "125:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 125: ranking uses tokens learned from the corpus", 8),
        ["round", "125:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 125: ranking uses tokens learned from the corpus", 12),
        ["round 125:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 125: ranking uses tokens learned from the corpus", 16),
        ["round 125:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 125: ranking uses tokens learned from the corpus", 24),
        ["round 125: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 125: ranking uses tokens learned from the corpus", 32),
        ["round 125: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 125: a long session ends when the candle dies", 4),
        ["round", "125:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 125: a long session ends when the candle dies", 8),
        ["round", "125: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 125: a long session ends when the candle dies", 12),
        ["round 125: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 125: a long session ends when the candle dies", 16),
        ["round 125: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 125: a long session ends when the candle dies", 24),
        ["round 125: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 125: a long session ends when the candle dies", 32),
        ["round 125: a long session ends", "when the candle dies"],
    ),
    (
        ("round 125: encode the prompt then map the result", 4),
        ["round", "125:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 125: encode the prompt then map the result", 8),
        ["round", "125:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 125: encode the prompt then map the result", 12),
        ["round 125:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 125: encode the prompt then map the result", 16),
        ["round 125:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 125: encode the prompt then map the result", 24),
        ["round 125: encode the", "prompt then map the", "result"],
    ),
    (("round 125: encode the prompt then map the result", 32), ["round 125: encode the prompt", "then map the result"]),
    (
        ("round 125: the kernel wakes the worker at dawn", 4),
        ["round", "125:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 125: the kernel wakes the worker at dawn", 8),
        ["round", "125: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 125: the kernel wakes the worker at dawn", 12),
        ["round 125:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 125: the kernel wakes the worker at dawn", 16), ["round 125: the", "kernel wakes the", "worker at dawn"]),
    (("round 125: the kernel wakes the worker at dawn", 24), ["round 125: the kernel", "wakes the worker at dawn"]),
    (("round 125: the kernel wakes the worker at dawn", 32), ["round 125: the kernel wakes the", "worker at dawn"]),
    (
        ("round 125: service latency drops after the patch", 4),
        ["round", "125:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 125: service latency drops after the patch", 8),
        ["round", "125:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 125: service latency drops after the patch", 12),
        ["round 125:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 125: service latency drops after the patch", 16),
        ["round 125:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 125: service latency drops after the patch", 24),
        ["round 125: service", "latency drops after the", "patch"],
    ),
    (("round 125: service latency drops after the patch", 32), ["round 125: service latency drops", "after the patch"]),
    (
        ("round 125: the library caches every vector it sees", 4),
        ["round", "125:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 125: the library caches every vector it sees", 8),
        ["round", "125: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 125: the library caches every vector it sees", 12),
        ["round 125:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 125: the library caches every vector it sees", 16),
        ["round 125: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 125: the library caches every vector it sees", 24),
        ["round 125: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 125: the library caches every vector it sees", 32),
        ["round 125: the library caches", "every vector it sees"],
    ),
    (
        ("round 125: agents argue then the debate resolves", 4),
        ["round", "125:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 125: agents argue then the debate resolves", 8),
        ["round", "125:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 125: agents argue then the debate resolves", 12),
        ["round 125:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 125: agents argue then the debate resolves", 16),
        ["round 125:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 125: agents argue then the debate resolves", 24), ["round 125: agents argue", "then the debate resolves"]),
    (("round 125: agents argue then the debate resolves", 32), ["round 125: agents argue then the", "debate resolves"]),
    (
        ("round 125: the filter keeps only strong matches", 4),
        ["round", "125:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 125: the filter keeps only strong matches", 8),
        ["round", "125: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 125: the filter keeps only strong matches", 12),
        ["round 125:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 125: the filter keeps only strong matches", 16),
        ["round 125: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 125: the filter keeps only strong matches", 24),
        ["round 125: the filter", "keeps only strong", "matches"],
    ),
    (("round 125: the filter keeps only strong matches", 32), ["round 125: the filter keeps only", "strong matches"]),
    (
        ("round 125: the model answers with a short reply", 4),
        ["round", "125:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 125: the model answers with a short reply", 8),
        ["round", "125: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 125: the model answers with a short reply", 12),
        ["round 125:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 125: the model answers with a short reply", 16),
        ["round 125: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 125: the model answers with a short reply", 24),
        ["round 125: the model", "answers with a short", "reply"],
    ),
    (("round 125: the model answers with a short reply", 32), ["round 125: the model answers", "with a short reply"]),
    (
        ("round 125: the recorder stores the reasoning trace", 4),
        ["round", "125:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 125: the recorder stores the reasoning trace", 8),
        ["round", "125: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 125: the recorder stores the reasoning trace", 12),
        ["round 125:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 125: the recorder stores the reasoning trace", 16),
        ["round 125: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 125: the recorder stores the reasoning trace", 24),
        ["round 125: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 125: the recorder stores the reasoning trace", 32),
        ["round 125: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 125: the angel watches the processor run", 4),
        ["round", "125:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 125: the angel watches the processor run", 8),
        ["round", "125: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 125: the angel watches the processor run", 12),
        ["round 125:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 125: the angel watches the processor run", 16),
        ["round 125: the", "angel watches", "the processor", "run"],
    ),
    (("round 125: the angel watches the processor run", 24), ["round 125: the angel", "watches the processor", "run"]),
    (("round 125: the angel watches the processor run", 32), ["round 125: the angel watches the", "processor run"]),
    (
        ("round 125: angle of the vector decides the match", 4),
        ["round", "125:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 125: angle of the vector decides the match", 8),
        ["round", "125:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 125: angle of the vector decides the match", 12),
        ["round 125:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 125: angle of the vector decides the match", 16),
        ["round 125: angle", "of the vector", "decides the", "match"],
    ),
    (("round 125: angle of the vector decides the match", 24), ["round 125: angle of the", "vector decides the match"]),
    (("round 125: angle of the vector decides the match", 32), ["round 125: angle of the vector", "decides the match"]),
    (
        ("round 125: the candle burns twice as long at night", 4),
        ["round", "125:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 125: the candle burns twice as long at night", 8),
        ["round", "125: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 125: the candle burns twice as long at night", 12),
        ["round 125:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 125: the candle burns twice as long at night", 16),
        ["round 125: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 125: the candle burns twice as long at night", 24),
        ["round 125: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 125: the candle burns twice as long at night", 32),
        ["round 125: the candle burns", "twice as long at night"],
    ),
    (
        ("round 125: a mirror of the universe in one line", 4),
        ["round", "125:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 125: a mirror of the universe in one line", 8),
        ["round", "125: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 125: a mirror of the universe in one line", 12),
        ["round 125: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 125: a mirror of the universe in one line", 16),
        ["round 125: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 125: a mirror of the universe in one line", 24), ["round 125: a mirror of", "the universe in one line"]),
    (("round 125: a mirror of the universe in one line", 32), ["round 125: a mirror of the", "universe in one line"]),
    (
        ("round 125: the queue drains before the storm", 4),
        ["round", "125:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 125: the queue drains before the storm", 8),
        ["round", "125: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 125: the queue drains before the storm", 12),
        ["round 125:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 125: the queue drains before the storm", 16), ["round 125: the", "queue drains", "before the storm"]),
    (("round 125: the queue drains before the storm", 24), ["round 125: the queue", "drains before the storm"]),
    (("round 125: the queue drains before the storm", 32), ["round 125: the queue drains", "before the storm"]),
    (
        ("kitten125 sitting125 agent125 angle125 universe125 memory125", 6),
        ["kitten125", "sitting125", "agent125", "angle125", "universe125", "memory125"],
    ),
    (
        ("kitten125 sitting125 agent125 angle125 universe125 memory125", 10),
        ["kitten125", "sitting125", "agent125", "angle125", "universe125", "memory125"],
    ),
    (
        ("kitten125 sitting125 agent125 angle125 universe125 memory125", 18),
        ["kitten125", "sitting125", "agent125 angle125", "universe125", "memory125"],
    ),
    (
        ("kitten125 sitting125 agent125 angle125 universe125 memory125", 28),
        ["kitten125 sitting125", "agent125 angle125", "universe125 memory125"],
    ),
    (
        ("sitting125 agent125 angle125 universe125 memory125 stream125", 6),
        ["sitting125", "agent125", "angle125", "universe125", "memory125", "stream125"],
    ),
    (
        ("sitting125 agent125 angle125 universe125 memory125 stream125", 10),
        ["sitting125", "agent125", "angle125", "universe125", "memory125", "stream125"],
    ),
    (
        ("sitting125 agent125 angle125 universe125 memory125 stream125", 18),
        ["sitting125", "agent125 angle125", "universe125", "memory125", "stream125"],
    ),
    (
        ("sitting125 agent125 angle125 universe125 memory125 stream125", 28),
        ["sitting125 agent125 angle125", "universe125 memory125", "stream125"],
    ),
    (
        ("agent125 angle125 universe125 memory125 stream125 context125", 6),
        ["agent125", "angle125", "universe125", "memory125", "stream125", "context125"],
    ),
    (
        ("agent125 angle125 universe125 memory125 stream125 context125", 10),
        ["agent125", "angle125", "universe125", "memory125", "stream125", "context125"],
    ),
    (
        ("agent125 angle125 universe125 memory125 stream125 context125", 18),
        ["agent125 angle125", "universe125", "memory125", "stream125", "context125"],
    ),
    (
        ("agent125 angle125 universe125 memory125 stream125 context125", 28),
        ["agent125 angle125", "universe125 memory125", "stream125 context125"],
    ),
    (
        ("angle125 universe125 memory125 stream125 context125 knowledge125", 6),
        ["angle125", "universe125", "memory125", "stream125", "context125", "knowledge125"],
    ),
    (
        ("angle125 universe125 memory125 stream125 context125 knowledge125", 10),
        ["angle125", "universe125", "memory125", "stream125", "context125", "knowledge125"],
    ),
    (
        ("angle125 universe125 memory125 stream125 context125 knowledge125", 18),
        ["angle125", "universe125", "memory125", "stream125", "context125", "knowledge125"],
    ),
    (
        ("angle125 universe125 memory125 stream125 context125 knowledge125", 28),
        ["angle125 universe125", "memory125 stream125", "context125 knowledge125"],
    ),
    (
        ("universe125 memory125 stream125 context125 knowledge125 vector125", 6),
        ["universe125", "memory125", "stream125", "context125", "knowledge125", "vector125"],
    ),
    (
        ("universe125 memory125 stream125 context125 knowledge125 vector125", 10),
        ["universe125", "memory125", "stream125", "context125", "knowledge125", "vector125"],
    ),
    (
        ("universe125 memory125 stream125 context125 knowledge125 vector125", 18),
        ["universe125", "memory125", "stream125", "context125", "knowledge125", "vector125"],
    ),
    (
        ("universe125 memory125 stream125 context125 knowledge125 vector125", 28),
        ["universe125 memory125", "stream125 context125", "knowledge125 vector125"],
    ),
    (
        ("memory125 stream125 context125 knowledge125 vector125 processor125", 6),
        ["memory125", "stream125", "context125", "knowledge125", "vector125", "processor125"],
    ),
    (
        ("memory125 stream125 context125 knowledge125 vector125 processor125", 10),
        ["memory125", "stream125", "context125", "knowledge125", "vector125", "processor125"],
    ),
    (
        ("memory125 stream125 context125 knowledge125 vector125 processor125", 18),
        ["memory125", "stream125", "context125", "knowledge125", "vector125", "processor125"],
    ),
    (
        ("memory125 stream125 context125 knowledge125 vector125 processor125", 28),
        ["memory125 stream125", "context125 knowledge125", "vector125 processor125"],
    ),
    (
        ("stream125 context125 knowledge125 vector125 processor125 reasoning125", 6),
        ["stream125", "context125", "knowledge125", "vector125", "processor125", "reasoning125"],
    ),
    (
        ("stream125 context125 knowledge125 vector125 processor125 reasoning125", 10),
        ["stream125", "context125", "knowledge125", "vector125", "processor125", "reasoning125"],
    ),
    (
        ("stream125 context125 knowledge125 vector125 processor125 reasoning125", 18),
        ["stream125", "context125", "knowledge125", "vector125", "processor125", "reasoning125"],
    ),
    (
        ("stream125 context125 knowledge125 vector125 processor125 reasoning125", 28),
        ["stream125 context125", "knowledge125 vector125", "processor125 reasoning125"],
    ),
    (
        ("context125 knowledge125 vector125 processor125 reasoning125 machine125", 6),
        ["context125", "knowledge125", "vector125", "processor125", "reasoning125", "machine125"],
    ),
    (
        ("context125 knowledge125 vector125 processor125 reasoning125 machine125", 10),
        ["context125", "knowledge125", "vector125", "processor125", "reasoning125", "machine125"],
    ),
    (
        ("context125 knowledge125 vector125 processor125 reasoning125 machine125", 18),
        ["context125", "knowledge125", "vector125", "processor125", "reasoning125", "machine125"],
    ),
    (
        ("context125 knowledge125 vector125 processor125 reasoning125 machine125", 28),
        ["context125 knowledge125", "vector125 processor125", "reasoning125 machine125"],
    ),
    (
        ("knowledge125 vector125 processor125 reasoning125 machine125 learning125", 6),
        ["knowledge125", "vector125", "processor125", "reasoning125", "machine125", "learning125"],
    ),
    (
        ("knowledge125 vector125 processor125 reasoning125 machine125 learning125", 10),
        ["knowledge125", "vector125", "processor125", "reasoning125", "machine125", "learning125"],
    ),
    (
        ("knowledge125 vector125 processor125 reasoning125 machine125 learning125", 18),
        ["knowledge125", "vector125", "processor125", "reasoning125", "machine125", "learning125"],
    ),
    (
        ("knowledge125 vector125 processor125 reasoning125 machine125 learning125", 28),
        ["knowledge125 vector125", "processor125 reasoning125", "machine125 learning125"],
    ),
    (
        ("vector125 processor125 reasoning125 machine125 learning125 model125", 6),
        ["vector125", "processor125", "reasoning125", "machine125", "learning125", "model125"],
    ),
    (
        ("vector125 processor125 reasoning125 machine125 learning125 model125", 10),
        ["vector125", "processor125", "reasoning125", "machine125", "learning125", "model125"],
    ),
    (
        ("vector125 processor125 reasoning125 machine125 learning125 model125", 18),
        ["vector125", "processor125", "reasoning125", "machine125", "learning125", "model125"],
    ),
    (
        ("vector125 processor125 reasoning125 machine125 learning125 model125", 28),
        ["vector125 processor125", "reasoning125 machine125", "learning125 model125"],
    ),
    (
        ("processor125 reasoning125 machine125 learning125 model125 token125", 6),
        ["processor125", "reasoning125", "machine125", "learning125", "model125", "token125"],
    ),
    (
        ("processor125 reasoning125 machine125 learning125 model125 token125", 10),
        ["processor125", "reasoning125", "machine125", "learning125", "model125", "token125"],
    ),
    (
        ("processor125 reasoning125 machine125 learning125 model125 token125", 18),
        ["processor125", "reasoning125", "machine125", "learning125", "model125 token125"],
    ),
    (
        ("processor125 reasoning125 machine125 learning125 model125 token125", 28),
        ["processor125 reasoning125", "machine125 learning125", "model125 token125"],
    ),
    (
        ("reasoning125 machine125 learning125 model125 token125 prompt125", 6),
        ["reasoning125", "machine125", "learning125", "model125", "token125", "prompt125"],
    ),
    (
        ("reasoning125 machine125 learning125 model125 token125 prompt125", 10),
        ["reasoning125", "machine125", "learning125", "model125", "token125", "prompt125"],
    ),
    (
        ("reasoning125 machine125 learning125 model125 token125 prompt125", 18),
        ["reasoning125", "machine125", "learning125", "model125 token125", "prompt125"],
    ),
    (
        ("reasoning125 machine125 learning125 model125 token125 prompt125", 28),
        ["reasoning125 machine125", "learning125 model125", "token125 prompt125"],
    ),
    (
        ("machine125 learning125 model125 token125 prompt125 session125", 6),
        ["machine125", "learning125", "model125", "token125", "prompt125", "session125"],
    ),
    (
        ("machine125 learning125 model125 token125 prompt125 session125", 10),
        ["machine125", "learning125", "model125", "token125", "prompt125", "session125"],
    ),
    (
        ("machine125 learning125 model125 token125 prompt125 session125", 18),
        ["machine125", "learning125", "model125 token125", "prompt125", "session125"],
    ),
    (
        ("machine125 learning125 model125 token125 prompt125 session125", 28),
        ["machine125 learning125", "model125 token125 prompt125", "session125"],
    ),
    (
        ("learning125 model125 token125 prompt125 session125 library125", 6),
        ["learning125", "model125", "token125", "prompt125", "session125", "library125"],
    ),
    (
        ("learning125 model125 token125 prompt125 session125 library125", 10),
        ["learning125", "model125", "token125", "prompt125", "session125", "library125"],
    ),
    (
        ("learning125 model125 token125 prompt125 session125 library125", 18),
        ["learning125", "model125 token125", "prompt125", "session125", "library125"],
    ),
    (
        ("learning125 model125 token125 prompt125 session125 library125", 28),
        ["learning125 model125", "token125 prompt125", "session125 library125"],
    ),
    (
        ("model125 token125 prompt125 session125 library125 service125", 6),
        ["model125", "token125", "prompt125", "session125", "library125", "service125"],
    ),
    (
        ("model125 token125 prompt125 session125 library125 service125", 10),
        ["model125", "token125", "prompt125", "session125", "library125", "service125"],
    ),
    (
        ("model125 token125 prompt125 session125 library125 service125", 18),
        ["model125 token125", "prompt125", "session125", "library125", "service125"],
    ),
    (
        ("model125 token125 prompt125 session125 library125 service125", 28),
        ["model125 token125 prompt125", "session125 library125", "service125"],
    ),
    (
        ("token125 prompt125 session125 library125 service125 gateway125", 6),
        ["token125", "prompt125", "session125", "library125", "service125", "gateway125"],
    ),
    (
        ("token125 prompt125 session125 library125 service125 gateway125", 10),
        ["token125", "prompt125", "session125", "library125", "service125", "gateway125"],
    ),
    (
        ("token125 prompt125 session125 library125 service125 gateway125", 18),
        ["token125 prompt125", "session125", "library125", "service125", "gateway125"],
    ),
    (
        ("token125 prompt125 session125 library125 service125 gateway125", 28),
        ["token125 prompt125", "session125 library125", "service125 gateway125"],
    ),
    (
        ("prompt125 session125 library125 service125 gateway125 storage125", 6),
        ["prompt125", "session125", "library125", "service125", "gateway125", "storage125"],
    ),
    (
        ("prompt125 session125 library125 service125 gateway125 storage125", 10),
        ["prompt125", "session125", "library125", "service125", "gateway125", "storage125"],
    ),
    (
        ("prompt125 session125 library125 service125 gateway125 storage125", 18),
        ["prompt125", "session125", "library125", "service125", "gateway125", "storage125"],
    ),
    (
        ("prompt125 session125 library125 service125 gateway125 storage125", 28),
        ["prompt125 session125", "library125 service125", "gateway125 storage125"],
    ),
    (
        ("session125 library125 service125 gateway125 storage125 network125", 6),
        ["session125", "library125", "service125", "gateway125", "storage125", "network125"],
    ),
    (
        ("session125 library125 service125 gateway125 storage125 network125", 10),
        ["session125", "library125", "service125", "gateway125", "storage125", "network125"],
    ),
    (
        ("session125 library125 service125 gateway125 storage125 network125", 18),
        ["session125", "library125", "service125", "gateway125", "storage125", "network125"],
    ),
    (
        ("session125 library125 service125 gateway125 storage125 network125", 28),
        ["session125 library125", "service125 gateway125", "storage125 network125"],
    ),
    (
        ("library125 service125 gateway125 storage125 network125 latency125", 6),
        ["library125", "service125", "gateway125", "storage125", "network125", "latency125"],
    ),
    (
        ("library125 service125 gateway125 storage125 network125 latency125", 10),
        ["library125", "service125", "gateway125", "storage125", "network125", "latency125"],
    ),
    (
        ("library125 service125 gateway125 storage125 network125 latency125", 18),
        ["library125", "service125", "gateway125", "storage125", "network125", "latency125"],
    ),
    (
        ("library125 service125 gateway125 storage125 network125 latency125", 28),
        ["library125 service125", "gateway125 storage125", "network125 latency125"],
    ),
    (
        ("service125 gateway125 storage125 network125 latency125 buffer125", 6),
        ["service125", "gateway125", "storage125", "network125", "latency125", "buffer125"],
    ),
    (
        ("service125 gateway125 storage125 network125 latency125 buffer125", 10),
        ["service125", "gateway125", "storage125", "network125", "latency125", "buffer125"],
    ),
    (
        ("service125 gateway125 storage125 network125 latency125 buffer125", 18),
        ["service125", "gateway125", "storage125", "network125", "latency125", "buffer125"],
    ),
    (
        ("service125 gateway125 storage125 network125 latency125 buffer125", 28),
        ["service125 gateway125", "storage125 network125", "latency125 buffer125"],
    ),
    (
        ("gateway125 storage125 network125 latency125 buffer125 queue125", 6),
        ["gateway125", "storage125", "network125", "latency125", "buffer125", "queue125"],
    ),
    (
        ("gateway125 storage125 network125 latency125 buffer125 queue125", 10),
        ["gateway125", "storage125", "network125", "latency125", "buffer125", "queue125"],
    ),
    (
        ("gateway125 storage125 network125 latency125 buffer125 queue125", 18),
        ["gateway125", "storage125", "network125", "latency125", "buffer125 queue125"],
    ),
    (
        ("gateway125 storage125 network125 latency125 buffer125 queue125", 28),
        ["gateway125 storage125", "network125 latency125", "buffer125 queue125"],
    ),
    (
        ("storage125 network125 latency125 buffer125 queue125 worker125", 6),
        ["storage125", "network125", "latency125", "buffer125", "queue125", "worker125"],
    ),
    (
        ("storage125 network125 latency125 buffer125 queue125 worker125", 10),
        ["storage125", "network125", "latency125", "buffer125", "queue125", "worker125"],
    ),
    (
        ("storage125 network125 latency125 buffer125 queue125 worker125", 18),
        ["storage125", "network125", "latency125", "buffer125 queue125", "worker125"],
    ),
    (
        ("storage125 network125 latency125 buffer125 queue125 worker125", 28),
        ["storage125 network125", "latency125 buffer125", "queue125 worker125"],
    ),
    (
        ("network125 latency125 buffer125 queue125 worker125 kernel125", 6),
        ["network125", "latency125", "buffer125", "queue125", "worker125", "kernel125"],
    ),
    (
        ("network125 latency125 buffer125 queue125 worker125 kernel125", 10),
        ["network125", "latency125", "buffer125", "queue125", "worker125", "kernel125"],
    ),
    (
        ("network125 latency125 buffer125 queue125 worker125 kernel125", 18),
        ["network125", "latency125", "buffer125 queue125", "worker125", "kernel125"],
    ),
    (
        ("network125 latency125 buffer125 queue125 worker125 kernel125", 28),
        ["network125 latency125", "buffer125 queue125 worker125", "kernel125"],
    ),
    (
        ("latency125 buffer125 queue125 worker125 kernel125 signal125", 6),
        ["latency125", "buffer125", "queue125", "worker125", "kernel125", "signal125"],
    ),
    (
        ("latency125 buffer125 queue125 worker125 kernel125 signal125", 10),
        ["latency125", "buffer125", "queue125", "worker125", "kernel125", "signal125"],
    ),
    (
        ("latency125 buffer125 queue125 worker125 kernel125 signal125", 18),
        ["latency125", "buffer125 queue125", "worker125", "kernel125", "signal125"],
    ),
    (
        ("latency125 buffer125 queue125 worker125 kernel125 signal125", 28),
        ["latency125 buffer125", "queue125 worker125 kernel125", "signal125"],
    ),
    (
        ("buffer125 queue125 worker125 kernel125 signal125 packet125", 6),
        ["buffer125", "queue125", "worker125", "kernel125", "signal125", "packet125"],
    ),
    (
        ("buffer125 queue125 worker125 kernel125 signal125 packet125", 10),
        ["buffer125", "queue125", "worker125", "kernel125", "signal125", "packet125"],
    ),
    (
        ("buffer125 queue125 worker125 kernel125 signal125 packet125", 18),
        ["buffer125 queue125", "worker125", "kernel125", "signal125", "packet125"],
    ),
    (
        ("buffer125 queue125 worker125 kernel125 signal125 packet125", 28),
        ["buffer125 queue125 worker125", "kernel125 signal125", "packet125"],
    ),
    (
        ("queue125 worker125 kernel125 signal125 packet125 router125", 6),
        ["queue125", "worker125", "kernel125", "signal125", "packet125", "router125"],
    ),
    (
        ("queue125 worker125 kernel125 signal125 packet125 router125", 10),
        ["queue125", "worker125", "kernel125", "signal125", "packet125", "router125"],
    ),
    (
        ("queue125 worker125 kernel125 signal125 packet125 router125", 18),
        ["queue125 worker125", "kernel125", "signal125", "packet125", "router125"],
    ),
    (
        ("queue125 worker125 kernel125 signal125 packet125 router125", 28),
        ["queue125 worker125 kernel125", "signal125 packet125", "router125"],
    ),
    (
        ("worker125 kernel125 signal125 packet125 router125 cluster125", 6),
        ["worker125", "kernel125", "signal125", "packet125", "router125", "cluster125"],
    ),
    (
        ("worker125 kernel125 signal125 packet125 router125 cluster125", 10),
        ["worker125", "kernel125", "signal125", "packet125", "router125", "cluster125"],
    ),
    (
        ("worker125 kernel125 signal125 packet125 router125 cluster125", 18),
        ["worker125", "kernel125", "signal125", "packet125", "router125", "cluster125"],
    ),
    (
        ("worker125 kernel125 signal125 packet125 router125 cluster125", 28),
        ["worker125 kernel125", "signal125 packet125", "router125 cluster125"],
    ),
    (
        ("kernel125 signal125 packet125 router125 cluster125 mirror125", 6),
        ["kernel125", "signal125", "packet125", "router125", "cluster125", "mirror125"],
    ),
    (
        ("kernel125 signal125 packet125 router125 cluster125 mirror125", 10),
        ["kernel125", "signal125", "packet125", "router125", "cluster125", "mirror125"],
    ),
    (
        ("kernel125 signal125 packet125 router125 cluster125 mirror125", 18),
        ["kernel125", "signal125", "packet125", "router125", "cluster125", "mirror125"],
    ),
    (
        ("kernel125 signal125 packet125 router125 cluster125 mirror125", 28),
        ["kernel125 signal125", "packet125 router125", "cluster125 mirror125"],
    ),
    (
        ("signal125 packet125 router125 cluster125 mirror125 filter125", 6),
        ["signal125", "packet125", "router125", "cluster125", "mirror125", "filter125"],
    ),
    (
        ("signal125 packet125 router125 cluster125 mirror125 filter125", 10),
        ["signal125", "packet125", "router125", "cluster125", "mirror125", "filter125"],
    ),
    (
        ("signal125 packet125 router125 cluster125 mirror125 filter125", 18),
        ["signal125", "packet125", "router125", "cluster125", "mirror125", "filter125"],
    ),
    (
        ("signal125 packet125 router125 cluster125 mirror125 filter125", 28),
        ["signal125 packet125", "router125 cluster125", "mirror125 filter125"],
    ),
    (
        ("packet125 router125 cluster125 mirror125 filter125 ranking125", 6),
        ["packet125", "router125", "cluster125", "mirror125", "filter125", "ranking125"],
    ),
    (
        ("packet125 router125 cluster125 mirror125 filter125 ranking125", 10),
        ["packet125", "router125", "cluster125", "mirror125", "filter125", "ranking125"],
    ),
    (
        ("packet125 router125 cluster125 mirror125 filter125 ranking125", 18),
        ["packet125", "router125", "cluster125", "mirror125", "filter125", "ranking125"],
    ),
    (
        ("packet125 router125 cluster125 mirror125 filter125 ranking125", 28),
        ["packet125 router125", "cluster125 mirror125", "filter125 ranking125"],
    ),
    (
        ("router125 cluster125 mirror125 filter125 ranking125 encoding125", 6),
        ["router125", "cluster125", "mirror125", "filter125", "ranking125", "encoding125"],
    ),
    (
        ("router125 cluster125 mirror125 filter125 ranking125 encoding125", 10),
        ["router125", "cluster125", "mirror125", "filter125", "ranking125", "encoding125"],
    ),
    (
        ("router125 cluster125 mirror125 filter125 ranking125 encoding125", 18),
        ["router125", "cluster125", "mirror125", "filter125", "ranking125", "encoding125"],
    ),
    (
        ("router125 cluster125 mirror125 filter125 ranking125 encoding125", 28),
        ["router125 cluster125", "mirror125 filter125", "ranking125 encoding125"],
    ),
    (
        ("cluster125 mirror125 filter125 ranking125 encoding125 mapping125", 6),
        ["cluster125", "mirror125", "filter125", "ranking125", "encoding125", "mapping125"],
    ),
    (
        ("cluster125 mirror125 filter125 ranking125 encoding125 mapping125", 10),
        ["cluster125", "mirror125", "filter125", "ranking125", "encoding125", "mapping125"],
    ),
    (
        ("cluster125 mirror125 filter125 ranking125 encoding125 mapping125", 18),
        ["cluster125", "mirror125", "filter125", "ranking125", "encoding125", "mapping125"],
    ),
    (
        ("cluster125 mirror125 filter125 ranking125 encoding125 mapping125", 28),
        ["cluster125 mirror125", "filter125 ranking125", "encoding125 mapping125"],
    ),
    (
        ("mirror125 filter125 ranking125 encoding125 mapping125 record125", 6),
        ["mirror125", "filter125", "ranking125", "encoding125", "mapping125", "record125"],
    ),
    (
        ("mirror125 filter125 ranking125 encoding125 mapping125 record125", 10),
        ["mirror125", "filter125", "ranking125", "encoding125", "mapping125", "record125"],
    ),
    (
        ("mirror125 filter125 ranking125 encoding125 mapping125 record125", 18),
        ["mirror125", "filter125", "ranking125", "encoding125", "mapping125", "record125"],
    ),
    (
        ("mirror125 filter125 ranking125 encoding125 mapping125 record125", 28),
        ["mirror125 filter125", "ranking125 encoding125", "mapping125 record125"],
    ),
    (
        ("filter125 ranking125 encoding125 mapping125 record125 candle125", 6),
        ["filter125", "ranking125", "encoding125", "mapping125", "record125", "candle125"],
    ),
    (
        ("filter125 ranking125 encoding125 mapping125 record125 candle125", 10),
        ["filter125", "ranking125", "encoding125", "mapping125", "record125", "candle125"],
    ),
    (
        ("filter125 ranking125 encoding125 mapping125 record125 candle125", 18),
        ["filter125", "ranking125", "encoding125", "mapping125", "record125", "candle125"],
    ),
    (
        ("filter125 ranking125 encoding125 mapping125 record125 candle125", 28),
        ["filter125 ranking125", "encoding125 mapping125", "record125 candle125"],
    ),
    (
        ("ranking125 encoding125 mapping125 record125 candle125 thread125", 6),
        ["ranking125", "encoding125", "mapping125", "record125", "candle125", "thread125"],
    ),
    (
        ("ranking125 encoding125 mapping125 record125 candle125 thread125", 10),
        ["ranking125", "encoding125", "mapping125", "record125", "candle125", "thread125"],
    ),
    (
        ("ranking125 encoding125 mapping125 record125 candle125 thread125", 18),
        ["ranking125", "encoding125", "mapping125", "record125", "candle125", "thread125"],
    ),
    (
        ("ranking125 encoding125 mapping125 record125 candle125 thread125", 28),
        ["ranking125 encoding125", "mapping125 record125", "candle125 thread125"],
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
