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
        ("round 171: the quick brown fox jumps over the lazy dog", 4),
        ["round", "171:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 171: the quick brown fox jumps over the lazy dog", 8),
        ["round", "171: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 171: the quick brown fox jumps over the lazy dog", 12),
        ["round 171:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 171: the quick brown fox jumps over the lazy dog", 16),
        ["round 171: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 171: the quick brown fox jumps over the lazy dog", 24),
        ["round 171: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 171: the quick brown fox jumps over the lazy dog", 32),
        ["round 171: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 171: agentuniverse is a framework for multi agents", 4),
        ["round", "171:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 171: agentuniverse is a framework for multi agents", 8),
        ["round", "171:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 171: agentuniverse is a framework for multi agents", 12),
        ["round 171:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 171: agentuniverse is a framework for multi agents", 16),
        ["round 171:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 171: agentuniverse is a framework for multi agents", 24),
        ["round 171: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 171: agentuniverse is a framework for multi agents", 32),
        ["round 171: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 171: knowledge stored as vectors enables retrieval", 4),
        ["round", "171:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 171: knowledge stored as vectors enables retrieval", 8),
        ["round", "171:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 171: knowledge stored as vectors enables retrieval", 12),
        ["round 171:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 171: knowledge stored as vectors enables retrieval", 16),
        ["round 171:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 171: knowledge stored as vectors enables retrieval", 24),
        ["round 171: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 171: knowledge stored as vectors enables retrieval", 32),
        ["round 171: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 171: the processor reads the record then stops", 4),
        ["round", "171:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 171: the processor reads the record then stops", 8),
        ["round", "171: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 171: the processor reads the record then stops", 12),
        ["round 171:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 171: the processor reads the record then stops", 16),
        ["round 171: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 171: the processor reads the record then stops", 24),
        ["round 171: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 171: the processor reads the record then stops", 32),
        ["round 171: the processor reads", "the record then stops"],
    ),
    (
        ("round 171: a worker pulls the next task from the queue", 4),
        ["round", "171:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 171: a worker pulls the next task from the queue", 8),
        ["round", "171: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 171: a worker pulls the next task from the queue", 12),
        ["round 171: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 171: a worker pulls the next task from the queue", 16),
        ["round 171: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 171: a worker pulls the next task from the queue", 24),
        ["round 171: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 171: a worker pulls the next task from the queue", 32),
        ["round 171: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 171: signals travel through the network layer", 4),
        ["round", "171:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 171: signals travel through the network layer", 8),
        ["round", "171:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 171: signals travel through the network layer", 12),
        ["round 171:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 171: signals travel through the network layer", 16),
        ["round 171:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 171: signals travel through the network layer", 24),
        ["round 171: signals", "travel through the", "network layer"],
    ),
    (
        ("round 171: signals travel through the network layer", 32),
        ["round 171: signals travel", "through the network layer"],
    ),
    (
        ("round 171: the gateway routes each request by policy", 4),
        ["round", "171:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 171: the gateway routes each request by policy", 8),
        ["round", "171: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 171: the gateway routes each request by policy", 12),
        ["round 171:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 171: the gateway routes each request by policy", 16),
        ["round 171: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 171: the gateway routes each request by policy", 24),
        ["round 171: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 171: the gateway routes each request by policy", 32),
        ["round 171: the gateway routes", "each request by policy"],
    ),
    (
        ("round 171: memory grows until the buffer is full", 4),
        ["round", "171:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 171: memory grows until the buffer is full", 8),
        ["round", "171:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 171: memory grows until the buffer is full", 12),
        ["round 171:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 171: memory grows until the buffer is full", 16),
        ["round 171:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 171: memory grows until the buffer is full", 24), ["round 171: memory grows", "until the buffer is full"]),
    (("round 171: memory grows until the buffer is full", 32), ["round 171: memory grows until", "the buffer is full"]),
    (
        ("round 171: the cluster mirrors every packet twice", 4),
        ["round", "171:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 171: the cluster mirrors every packet twice", 8),
        ["round", "171: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 171: the cluster mirrors every packet twice", 12),
        ["round 171:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 171: the cluster mirrors every packet twice", 16),
        ["round 171: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 171: the cluster mirrors every packet twice", 24),
        ["round 171: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 171: the cluster mirrors every packet twice", 32),
        ["round 171: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 171: ranking uses tokens learned from the corpus", 4),
        ["round", "171:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 171: ranking uses tokens learned from the corpus", 8),
        ["round", "171:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 171: ranking uses tokens learned from the corpus", 12),
        ["round 171:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 171: ranking uses tokens learned from the corpus", 16),
        ["round 171:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 171: ranking uses tokens learned from the corpus", 24),
        ["round 171: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 171: ranking uses tokens learned from the corpus", 32),
        ["round 171: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 171: a long session ends when the candle dies", 4),
        ["round", "171:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 171: a long session ends when the candle dies", 8),
        ["round", "171: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 171: a long session ends when the candle dies", 12),
        ["round 171: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 171: a long session ends when the candle dies", 16),
        ["round 171: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 171: a long session ends when the candle dies", 24),
        ["round 171: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 171: a long session ends when the candle dies", 32),
        ["round 171: a long session ends", "when the candle dies"],
    ),
    (
        ("round 171: encode the prompt then map the result", 4),
        ["round", "171:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 171: encode the prompt then map the result", 8),
        ["round", "171:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 171: encode the prompt then map the result", 12),
        ["round 171:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 171: encode the prompt then map the result", 16),
        ["round 171:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 171: encode the prompt then map the result", 24),
        ["round 171: encode the", "prompt then map the", "result"],
    ),
    (("round 171: encode the prompt then map the result", 32), ["round 171: encode the prompt", "then map the result"]),
    (
        ("round 171: the kernel wakes the worker at dawn", 4),
        ["round", "171:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 171: the kernel wakes the worker at dawn", 8),
        ["round", "171: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 171: the kernel wakes the worker at dawn", 12),
        ["round 171:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 171: the kernel wakes the worker at dawn", 16), ["round 171: the", "kernel wakes the", "worker at dawn"]),
    (("round 171: the kernel wakes the worker at dawn", 24), ["round 171: the kernel", "wakes the worker at dawn"]),
    (("round 171: the kernel wakes the worker at dawn", 32), ["round 171: the kernel wakes the", "worker at dawn"]),
    (
        ("round 171: service latency drops after the patch", 4),
        ["round", "171:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 171: service latency drops after the patch", 8),
        ["round", "171:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 171: service latency drops after the patch", 12),
        ["round 171:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 171: service latency drops after the patch", 16),
        ["round 171:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 171: service latency drops after the patch", 24),
        ["round 171: service", "latency drops after the", "patch"],
    ),
    (("round 171: service latency drops after the patch", 32), ["round 171: service latency drops", "after the patch"]),
    (
        ("round 171: the library caches every vector it sees", 4),
        ["round", "171:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 171: the library caches every vector it sees", 8),
        ["round", "171: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 171: the library caches every vector it sees", 12),
        ["round 171:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 171: the library caches every vector it sees", 16),
        ["round 171: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 171: the library caches every vector it sees", 24),
        ["round 171: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 171: the library caches every vector it sees", 32),
        ["round 171: the library caches", "every vector it sees"],
    ),
    (
        ("round 171: agents argue then the debate resolves", 4),
        ["round", "171:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 171: agents argue then the debate resolves", 8),
        ["round", "171:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 171: agents argue then the debate resolves", 12),
        ["round 171:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 171: agents argue then the debate resolves", 16),
        ["round 171:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 171: agents argue then the debate resolves", 24), ["round 171: agents argue", "then the debate resolves"]),
    (("round 171: agents argue then the debate resolves", 32), ["round 171: agents argue then the", "debate resolves"]),
    (
        ("round 171: the filter keeps only strong matches", 4),
        ["round", "171:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 171: the filter keeps only strong matches", 8),
        ["round", "171: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 171: the filter keeps only strong matches", 12),
        ["round 171:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 171: the filter keeps only strong matches", 16),
        ["round 171: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 171: the filter keeps only strong matches", 24),
        ["round 171: the filter", "keeps only strong", "matches"],
    ),
    (("round 171: the filter keeps only strong matches", 32), ["round 171: the filter keeps only", "strong matches"]),
    (
        ("round 171: the model answers with a short reply", 4),
        ["round", "171:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 171: the model answers with a short reply", 8),
        ["round", "171: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 171: the model answers with a short reply", 12),
        ["round 171:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 171: the model answers with a short reply", 16),
        ["round 171: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 171: the model answers with a short reply", 24),
        ["round 171: the model", "answers with a short", "reply"],
    ),
    (("round 171: the model answers with a short reply", 32), ["round 171: the model answers", "with a short reply"]),
    (
        ("round 171: the recorder stores the reasoning trace", 4),
        ["round", "171:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 171: the recorder stores the reasoning trace", 8),
        ["round", "171: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 171: the recorder stores the reasoning trace", 12),
        ["round 171:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 171: the recorder stores the reasoning trace", 16),
        ["round 171: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 171: the recorder stores the reasoning trace", 24),
        ["round 171: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 171: the recorder stores the reasoning trace", 32),
        ["round 171: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 171: the angel watches the processor run", 4),
        ["round", "171:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 171: the angel watches the processor run", 8),
        ["round", "171: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 171: the angel watches the processor run", 12),
        ["round 171:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 171: the angel watches the processor run", 16),
        ["round 171: the", "angel watches", "the processor", "run"],
    ),
    (("round 171: the angel watches the processor run", 24), ["round 171: the angel", "watches the processor", "run"]),
    (("round 171: the angel watches the processor run", 32), ["round 171: the angel watches the", "processor run"]),
    (
        ("round 171: angle of the vector decides the match", 4),
        ["round", "171:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 171: angle of the vector decides the match", 8),
        ["round", "171:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 171: angle of the vector decides the match", 12),
        ["round 171:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 171: angle of the vector decides the match", 16),
        ["round 171: angle", "of the vector", "decides the", "match"],
    ),
    (("round 171: angle of the vector decides the match", 24), ["round 171: angle of the", "vector decides the match"]),
    (("round 171: angle of the vector decides the match", 32), ["round 171: angle of the vector", "decides the match"]),
    (
        ("round 171: the candle burns twice as long at night", 4),
        ["round", "171:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 171: the candle burns twice as long at night", 8),
        ["round", "171: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 171: the candle burns twice as long at night", 12),
        ["round 171:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 171: the candle burns twice as long at night", 16),
        ["round 171: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 171: the candle burns twice as long at night", 24),
        ["round 171: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 171: the candle burns twice as long at night", 32),
        ["round 171: the candle burns", "twice as long at night"],
    ),
    (
        ("round 171: a mirror of the universe in one line", 4),
        ["round", "171:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 171: a mirror of the universe in one line", 8),
        ["round", "171: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 171: a mirror of the universe in one line", 12),
        ["round 171: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 171: a mirror of the universe in one line", 16),
        ["round 171: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 171: a mirror of the universe in one line", 24), ["round 171: a mirror of", "the universe in one line"]),
    (("round 171: a mirror of the universe in one line", 32), ["round 171: a mirror of the", "universe in one line"]),
    (
        ("round 171: the queue drains before the storm", 4),
        ["round", "171:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 171: the queue drains before the storm", 8),
        ["round", "171: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 171: the queue drains before the storm", 12),
        ["round 171:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 171: the queue drains before the storm", 16), ["round 171: the", "queue drains", "before the storm"]),
    (("round 171: the queue drains before the storm", 24), ["round 171: the queue", "drains before the storm"]),
    (("round 171: the queue drains before the storm", 32), ["round 171: the queue drains", "before the storm"]),
    (
        ("kitten171 sitting171 agent171 angle171 universe171 memory171", 6),
        ["kitten171", "sitting171", "agent171", "angle171", "universe171", "memory171"],
    ),
    (
        ("kitten171 sitting171 agent171 angle171 universe171 memory171", 10),
        ["kitten171", "sitting171", "agent171", "angle171", "universe171", "memory171"],
    ),
    (
        ("kitten171 sitting171 agent171 angle171 universe171 memory171", 18),
        ["kitten171", "sitting171", "agent171 angle171", "universe171", "memory171"],
    ),
    (
        ("kitten171 sitting171 agent171 angle171 universe171 memory171", 28),
        ["kitten171 sitting171", "agent171 angle171", "universe171 memory171"],
    ),
    (
        ("sitting171 agent171 angle171 universe171 memory171 stream171", 6),
        ["sitting171", "agent171", "angle171", "universe171", "memory171", "stream171"],
    ),
    (
        ("sitting171 agent171 angle171 universe171 memory171 stream171", 10),
        ["sitting171", "agent171", "angle171", "universe171", "memory171", "stream171"],
    ),
    (
        ("sitting171 agent171 angle171 universe171 memory171 stream171", 18),
        ["sitting171", "agent171 angle171", "universe171", "memory171", "stream171"],
    ),
    (
        ("sitting171 agent171 angle171 universe171 memory171 stream171", 28),
        ["sitting171 agent171 angle171", "universe171 memory171", "stream171"],
    ),
    (
        ("agent171 angle171 universe171 memory171 stream171 context171", 6),
        ["agent171", "angle171", "universe171", "memory171", "stream171", "context171"],
    ),
    (
        ("agent171 angle171 universe171 memory171 stream171 context171", 10),
        ["agent171", "angle171", "universe171", "memory171", "stream171", "context171"],
    ),
    (
        ("agent171 angle171 universe171 memory171 stream171 context171", 18),
        ["agent171 angle171", "universe171", "memory171", "stream171", "context171"],
    ),
    (
        ("agent171 angle171 universe171 memory171 stream171 context171", 28),
        ["agent171 angle171", "universe171 memory171", "stream171 context171"],
    ),
    (
        ("angle171 universe171 memory171 stream171 context171 knowledge171", 6),
        ["angle171", "universe171", "memory171", "stream171", "context171", "knowledge171"],
    ),
    (
        ("angle171 universe171 memory171 stream171 context171 knowledge171", 10),
        ["angle171", "universe171", "memory171", "stream171", "context171", "knowledge171"],
    ),
    (
        ("angle171 universe171 memory171 stream171 context171 knowledge171", 18),
        ["angle171", "universe171", "memory171", "stream171", "context171", "knowledge171"],
    ),
    (
        ("angle171 universe171 memory171 stream171 context171 knowledge171", 28),
        ["angle171 universe171", "memory171 stream171", "context171 knowledge171"],
    ),
    (
        ("universe171 memory171 stream171 context171 knowledge171 vector171", 6),
        ["universe171", "memory171", "stream171", "context171", "knowledge171", "vector171"],
    ),
    (
        ("universe171 memory171 stream171 context171 knowledge171 vector171", 10),
        ["universe171", "memory171", "stream171", "context171", "knowledge171", "vector171"],
    ),
    (
        ("universe171 memory171 stream171 context171 knowledge171 vector171", 18),
        ["universe171", "memory171", "stream171", "context171", "knowledge171", "vector171"],
    ),
    (
        ("universe171 memory171 stream171 context171 knowledge171 vector171", 28),
        ["universe171 memory171", "stream171 context171", "knowledge171 vector171"],
    ),
    (
        ("memory171 stream171 context171 knowledge171 vector171 processor171", 6),
        ["memory171", "stream171", "context171", "knowledge171", "vector171", "processor171"],
    ),
    (
        ("memory171 stream171 context171 knowledge171 vector171 processor171", 10),
        ["memory171", "stream171", "context171", "knowledge171", "vector171", "processor171"],
    ),
    (
        ("memory171 stream171 context171 knowledge171 vector171 processor171", 18),
        ["memory171", "stream171", "context171", "knowledge171", "vector171", "processor171"],
    ),
    (
        ("memory171 stream171 context171 knowledge171 vector171 processor171", 28),
        ["memory171 stream171", "context171 knowledge171", "vector171 processor171"],
    ),
    (
        ("stream171 context171 knowledge171 vector171 processor171 reasoning171", 6),
        ["stream171", "context171", "knowledge171", "vector171", "processor171", "reasoning171"],
    ),
    (
        ("stream171 context171 knowledge171 vector171 processor171 reasoning171", 10),
        ["stream171", "context171", "knowledge171", "vector171", "processor171", "reasoning171"],
    ),
    (
        ("stream171 context171 knowledge171 vector171 processor171 reasoning171", 18),
        ["stream171", "context171", "knowledge171", "vector171", "processor171", "reasoning171"],
    ),
    (
        ("stream171 context171 knowledge171 vector171 processor171 reasoning171", 28),
        ["stream171 context171", "knowledge171 vector171", "processor171 reasoning171"],
    ),
    (
        ("context171 knowledge171 vector171 processor171 reasoning171 machine171", 6),
        ["context171", "knowledge171", "vector171", "processor171", "reasoning171", "machine171"],
    ),
    (
        ("context171 knowledge171 vector171 processor171 reasoning171 machine171", 10),
        ["context171", "knowledge171", "vector171", "processor171", "reasoning171", "machine171"],
    ),
    (
        ("context171 knowledge171 vector171 processor171 reasoning171 machine171", 18),
        ["context171", "knowledge171", "vector171", "processor171", "reasoning171", "machine171"],
    ),
    (
        ("context171 knowledge171 vector171 processor171 reasoning171 machine171", 28),
        ["context171 knowledge171", "vector171 processor171", "reasoning171 machine171"],
    ),
    (
        ("knowledge171 vector171 processor171 reasoning171 machine171 learning171", 6),
        ["knowledge171", "vector171", "processor171", "reasoning171", "machine171", "learning171"],
    ),
    (
        ("knowledge171 vector171 processor171 reasoning171 machine171 learning171", 10),
        ["knowledge171", "vector171", "processor171", "reasoning171", "machine171", "learning171"],
    ),
    (
        ("knowledge171 vector171 processor171 reasoning171 machine171 learning171", 18),
        ["knowledge171", "vector171", "processor171", "reasoning171", "machine171", "learning171"],
    ),
    (
        ("knowledge171 vector171 processor171 reasoning171 machine171 learning171", 28),
        ["knowledge171 vector171", "processor171 reasoning171", "machine171 learning171"],
    ),
    (
        ("vector171 processor171 reasoning171 machine171 learning171 model171", 6),
        ["vector171", "processor171", "reasoning171", "machine171", "learning171", "model171"],
    ),
    (
        ("vector171 processor171 reasoning171 machine171 learning171 model171", 10),
        ["vector171", "processor171", "reasoning171", "machine171", "learning171", "model171"],
    ),
    (
        ("vector171 processor171 reasoning171 machine171 learning171 model171", 18),
        ["vector171", "processor171", "reasoning171", "machine171", "learning171", "model171"],
    ),
    (
        ("vector171 processor171 reasoning171 machine171 learning171 model171", 28),
        ["vector171 processor171", "reasoning171 machine171", "learning171 model171"],
    ),
    (
        ("processor171 reasoning171 machine171 learning171 model171 token171", 6),
        ["processor171", "reasoning171", "machine171", "learning171", "model171", "token171"],
    ),
    (
        ("processor171 reasoning171 machine171 learning171 model171 token171", 10),
        ["processor171", "reasoning171", "machine171", "learning171", "model171", "token171"],
    ),
    (
        ("processor171 reasoning171 machine171 learning171 model171 token171", 18),
        ["processor171", "reasoning171", "machine171", "learning171", "model171 token171"],
    ),
    (
        ("processor171 reasoning171 machine171 learning171 model171 token171", 28),
        ["processor171 reasoning171", "machine171 learning171", "model171 token171"],
    ),
    (
        ("reasoning171 machine171 learning171 model171 token171 prompt171", 6),
        ["reasoning171", "machine171", "learning171", "model171", "token171", "prompt171"],
    ),
    (
        ("reasoning171 machine171 learning171 model171 token171 prompt171", 10),
        ["reasoning171", "machine171", "learning171", "model171", "token171", "prompt171"],
    ),
    (
        ("reasoning171 machine171 learning171 model171 token171 prompt171", 18),
        ["reasoning171", "machine171", "learning171", "model171 token171", "prompt171"],
    ),
    (
        ("reasoning171 machine171 learning171 model171 token171 prompt171", 28),
        ["reasoning171 machine171", "learning171 model171", "token171 prompt171"],
    ),
    (
        ("machine171 learning171 model171 token171 prompt171 session171", 6),
        ["machine171", "learning171", "model171", "token171", "prompt171", "session171"],
    ),
    (
        ("machine171 learning171 model171 token171 prompt171 session171", 10),
        ["machine171", "learning171", "model171", "token171", "prompt171", "session171"],
    ),
    (
        ("machine171 learning171 model171 token171 prompt171 session171", 18),
        ["machine171", "learning171", "model171 token171", "prompt171", "session171"],
    ),
    (
        ("machine171 learning171 model171 token171 prompt171 session171", 28),
        ["machine171 learning171", "model171 token171 prompt171", "session171"],
    ),
    (
        ("learning171 model171 token171 prompt171 session171 library171", 6),
        ["learning171", "model171", "token171", "prompt171", "session171", "library171"],
    ),
    (
        ("learning171 model171 token171 prompt171 session171 library171", 10),
        ["learning171", "model171", "token171", "prompt171", "session171", "library171"],
    ),
    (
        ("learning171 model171 token171 prompt171 session171 library171", 18),
        ["learning171", "model171 token171", "prompt171", "session171", "library171"],
    ),
    (
        ("learning171 model171 token171 prompt171 session171 library171", 28),
        ["learning171 model171", "token171 prompt171", "session171 library171"],
    ),
    (
        ("model171 token171 prompt171 session171 library171 service171", 6),
        ["model171", "token171", "prompt171", "session171", "library171", "service171"],
    ),
    (
        ("model171 token171 prompt171 session171 library171 service171", 10),
        ["model171", "token171", "prompt171", "session171", "library171", "service171"],
    ),
    (
        ("model171 token171 prompt171 session171 library171 service171", 18),
        ["model171 token171", "prompt171", "session171", "library171", "service171"],
    ),
    (
        ("model171 token171 prompt171 session171 library171 service171", 28),
        ["model171 token171 prompt171", "session171 library171", "service171"],
    ),
    (
        ("token171 prompt171 session171 library171 service171 gateway171", 6),
        ["token171", "prompt171", "session171", "library171", "service171", "gateway171"],
    ),
    (
        ("token171 prompt171 session171 library171 service171 gateway171", 10),
        ["token171", "prompt171", "session171", "library171", "service171", "gateway171"],
    ),
    (
        ("token171 prompt171 session171 library171 service171 gateway171", 18),
        ["token171 prompt171", "session171", "library171", "service171", "gateway171"],
    ),
    (
        ("token171 prompt171 session171 library171 service171 gateway171", 28),
        ["token171 prompt171", "session171 library171", "service171 gateway171"],
    ),
    (
        ("prompt171 session171 library171 service171 gateway171 storage171", 6),
        ["prompt171", "session171", "library171", "service171", "gateway171", "storage171"],
    ),
    (
        ("prompt171 session171 library171 service171 gateway171 storage171", 10),
        ["prompt171", "session171", "library171", "service171", "gateway171", "storage171"],
    ),
    (
        ("prompt171 session171 library171 service171 gateway171 storage171", 18),
        ["prompt171", "session171", "library171", "service171", "gateway171", "storage171"],
    ),
    (
        ("prompt171 session171 library171 service171 gateway171 storage171", 28),
        ["prompt171 session171", "library171 service171", "gateway171 storage171"],
    ),
    (
        ("session171 library171 service171 gateway171 storage171 network171", 6),
        ["session171", "library171", "service171", "gateway171", "storage171", "network171"],
    ),
    (
        ("session171 library171 service171 gateway171 storage171 network171", 10),
        ["session171", "library171", "service171", "gateway171", "storage171", "network171"],
    ),
    (
        ("session171 library171 service171 gateway171 storage171 network171", 18),
        ["session171", "library171", "service171", "gateway171", "storage171", "network171"],
    ),
    (
        ("session171 library171 service171 gateway171 storage171 network171", 28),
        ["session171 library171", "service171 gateway171", "storage171 network171"],
    ),
    (
        ("library171 service171 gateway171 storage171 network171 latency171", 6),
        ["library171", "service171", "gateway171", "storage171", "network171", "latency171"],
    ),
    (
        ("library171 service171 gateway171 storage171 network171 latency171", 10),
        ["library171", "service171", "gateway171", "storage171", "network171", "latency171"],
    ),
    (
        ("library171 service171 gateway171 storage171 network171 latency171", 18),
        ["library171", "service171", "gateway171", "storage171", "network171", "latency171"],
    ),
    (
        ("library171 service171 gateway171 storage171 network171 latency171", 28),
        ["library171 service171", "gateway171 storage171", "network171 latency171"],
    ),
    (
        ("service171 gateway171 storage171 network171 latency171 buffer171", 6),
        ["service171", "gateway171", "storage171", "network171", "latency171", "buffer171"],
    ),
    (
        ("service171 gateway171 storage171 network171 latency171 buffer171", 10),
        ["service171", "gateway171", "storage171", "network171", "latency171", "buffer171"],
    ),
    (
        ("service171 gateway171 storage171 network171 latency171 buffer171", 18),
        ["service171", "gateway171", "storage171", "network171", "latency171", "buffer171"],
    ),
    (
        ("service171 gateway171 storage171 network171 latency171 buffer171", 28),
        ["service171 gateway171", "storage171 network171", "latency171 buffer171"],
    ),
    (
        ("gateway171 storage171 network171 latency171 buffer171 queue171", 6),
        ["gateway171", "storage171", "network171", "latency171", "buffer171", "queue171"],
    ),
    (
        ("gateway171 storage171 network171 latency171 buffer171 queue171", 10),
        ["gateway171", "storage171", "network171", "latency171", "buffer171", "queue171"],
    ),
    (
        ("gateway171 storage171 network171 latency171 buffer171 queue171", 18),
        ["gateway171", "storage171", "network171", "latency171", "buffer171 queue171"],
    ),
    (
        ("gateway171 storage171 network171 latency171 buffer171 queue171", 28),
        ["gateway171 storage171", "network171 latency171", "buffer171 queue171"],
    ),
    (
        ("storage171 network171 latency171 buffer171 queue171 worker171", 6),
        ["storage171", "network171", "latency171", "buffer171", "queue171", "worker171"],
    ),
    (
        ("storage171 network171 latency171 buffer171 queue171 worker171", 10),
        ["storage171", "network171", "latency171", "buffer171", "queue171", "worker171"],
    ),
    (
        ("storage171 network171 latency171 buffer171 queue171 worker171", 18),
        ["storage171", "network171", "latency171", "buffer171 queue171", "worker171"],
    ),
    (
        ("storage171 network171 latency171 buffer171 queue171 worker171", 28),
        ["storage171 network171", "latency171 buffer171", "queue171 worker171"],
    ),
    (
        ("network171 latency171 buffer171 queue171 worker171 kernel171", 6),
        ["network171", "latency171", "buffer171", "queue171", "worker171", "kernel171"],
    ),
    (
        ("network171 latency171 buffer171 queue171 worker171 kernel171", 10),
        ["network171", "latency171", "buffer171", "queue171", "worker171", "kernel171"],
    ),
    (
        ("network171 latency171 buffer171 queue171 worker171 kernel171", 18),
        ["network171", "latency171", "buffer171 queue171", "worker171", "kernel171"],
    ),
    (
        ("network171 latency171 buffer171 queue171 worker171 kernel171", 28),
        ["network171 latency171", "buffer171 queue171 worker171", "kernel171"],
    ),
    (
        ("latency171 buffer171 queue171 worker171 kernel171 signal171", 6),
        ["latency171", "buffer171", "queue171", "worker171", "kernel171", "signal171"],
    ),
    (
        ("latency171 buffer171 queue171 worker171 kernel171 signal171", 10),
        ["latency171", "buffer171", "queue171", "worker171", "kernel171", "signal171"],
    ),
    (
        ("latency171 buffer171 queue171 worker171 kernel171 signal171", 18),
        ["latency171", "buffer171 queue171", "worker171", "kernel171", "signal171"],
    ),
    (
        ("latency171 buffer171 queue171 worker171 kernel171 signal171", 28),
        ["latency171 buffer171", "queue171 worker171 kernel171", "signal171"],
    ),
    (
        ("buffer171 queue171 worker171 kernel171 signal171 packet171", 6),
        ["buffer171", "queue171", "worker171", "kernel171", "signal171", "packet171"],
    ),
    (
        ("buffer171 queue171 worker171 kernel171 signal171 packet171", 10),
        ["buffer171", "queue171", "worker171", "kernel171", "signal171", "packet171"],
    ),
    (
        ("buffer171 queue171 worker171 kernel171 signal171 packet171", 18),
        ["buffer171 queue171", "worker171", "kernel171", "signal171", "packet171"],
    ),
    (
        ("buffer171 queue171 worker171 kernel171 signal171 packet171", 28),
        ["buffer171 queue171 worker171", "kernel171 signal171", "packet171"],
    ),
    (
        ("queue171 worker171 kernel171 signal171 packet171 router171", 6),
        ["queue171", "worker171", "kernel171", "signal171", "packet171", "router171"],
    ),
    (
        ("queue171 worker171 kernel171 signal171 packet171 router171", 10),
        ["queue171", "worker171", "kernel171", "signal171", "packet171", "router171"],
    ),
    (
        ("queue171 worker171 kernel171 signal171 packet171 router171", 18),
        ["queue171 worker171", "kernel171", "signal171", "packet171", "router171"],
    ),
    (
        ("queue171 worker171 kernel171 signal171 packet171 router171", 28),
        ["queue171 worker171 kernel171", "signal171 packet171", "router171"],
    ),
    (
        ("worker171 kernel171 signal171 packet171 router171 cluster171", 6),
        ["worker171", "kernel171", "signal171", "packet171", "router171", "cluster171"],
    ),
    (
        ("worker171 kernel171 signal171 packet171 router171 cluster171", 10),
        ["worker171", "kernel171", "signal171", "packet171", "router171", "cluster171"],
    ),
    (
        ("worker171 kernel171 signal171 packet171 router171 cluster171", 18),
        ["worker171", "kernel171", "signal171", "packet171", "router171", "cluster171"],
    ),
    (
        ("worker171 kernel171 signal171 packet171 router171 cluster171", 28),
        ["worker171 kernel171", "signal171 packet171", "router171 cluster171"],
    ),
    (
        ("kernel171 signal171 packet171 router171 cluster171 mirror171", 6),
        ["kernel171", "signal171", "packet171", "router171", "cluster171", "mirror171"],
    ),
    (
        ("kernel171 signal171 packet171 router171 cluster171 mirror171", 10),
        ["kernel171", "signal171", "packet171", "router171", "cluster171", "mirror171"],
    ),
    (
        ("kernel171 signal171 packet171 router171 cluster171 mirror171", 18),
        ["kernel171", "signal171", "packet171", "router171", "cluster171", "mirror171"],
    ),
    (
        ("kernel171 signal171 packet171 router171 cluster171 mirror171", 28),
        ["kernel171 signal171", "packet171 router171", "cluster171 mirror171"],
    ),
    (
        ("signal171 packet171 router171 cluster171 mirror171 filter171", 6),
        ["signal171", "packet171", "router171", "cluster171", "mirror171", "filter171"],
    ),
    (
        ("signal171 packet171 router171 cluster171 mirror171 filter171", 10),
        ["signal171", "packet171", "router171", "cluster171", "mirror171", "filter171"],
    ),
    (
        ("signal171 packet171 router171 cluster171 mirror171 filter171", 18),
        ["signal171", "packet171", "router171", "cluster171", "mirror171", "filter171"],
    ),
    (
        ("signal171 packet171 router171 cluster171 mirror171 filter171", 28),
        ["signal171 packet171", "router171 cluster171", "mirror171 filter171"],
    ),
    (
        ("packet171 router171 cluster171 mirror171 filter171 ranking171", 6),
        ["packet171", "router171", "cluster171", "mirror171", "filter171", "ranking171"],
    ),
    (
        ("packet171 router171 cluster171 mirror171 filter171 ranking171", 10),
        ["packet171", "router171", "cluster171", "mirror171", "filter171", "ranking171"],
    ),
    (
        ("packet171 router171 cluster171 mirror171 filter171 ranking171", 18),
        ["packet171", "router171", "cluster171", "mirror171", "filter171", "ranking171"],
    ),
    (
        ("packet171 router171 cluster171 mirror171 filter171 ranking171", 28),
        ["packet171 router171", "cluster171 mirror171", "filter171 ranking171"],
    ),
    (
        ("router171 cluster171 mirror171 filter171 ranking171 encoding171", 6),
        ["router171", "cluster171", "mirror171", "filter171", "ranking171", "encoding171"],
    ),
    (
        ("router171 cluster171 mirror171 filter171 ranking171 encoding171", 10),
        ["router171", "cluster171", "mirror171", "filter171", "ranking171", "encoding171"],
    ),
    (
        ("router171 cluster171 mirror171 filter171 ranking171 encoding171", 18),
        ["router171", "cluster171", "mirror171", "filter171", "ranking171", "encoding171"],
    ),
    (
        ("router171 cluster171 mirror171 filter171 ranking171 encoding171", 28),
        ["router171 cluster171", "mirror171 filter171", "ranking171 encoding171"],
    ),
    (
        ("cluster171 mirror171 filter171 ranking171 encoding171 mapping171", 6),
        ["cluster171", "mirror171", "filter171", "ranking171", "encoding171", "mapping171"],
    ),
    (
        ("cluster171 mirror171 filter171 ranking171 encoding171 mapping171", 10),
        ["cluster171", "mirror171", "filter171", "ranking171", "encoding171", "mapping171"],
    ),
    (
        ("cluster171 mirror171 filter171 ranking171 encoding171 mapping171", 18),
        ["cluster171", "mirror171", "filter171", "ranking171", "encoding171", "mapping171"],
    ),
    (
        ("cluster171 mirror171 filter171 ranking171 encoding171 mapping171", 28),
        ["cluster171 mirror171", "filter171 ranking171", "encoding171 mapping171"],
    ),
    (
        ("mirror171 filter171 ranking171 encoding171 mapping171 record171", 6),
        ["mirror171", "filter171", "ranking171", "encoding171", "mapping171", "record171"],
    ),
    (
        ("mirror171 filter171 ranking171 encoding171 mapping171 record171", 10),
        ["mirror171", "filter171", "ranking171", "encoding171", "mapping171", "record171"],
    ),
    (
        ("mirror171 filter171 ranking171 encoding171 mapping171 record171", 18),
        ["mirror171", "filter171", "ranking171", "encoding171", "mapping171", "record171"],
    ),
    (
        ("mirror171 filter171 ranking171 encoding171 mapping171 record171", 28),
        ["mirror171 filter171", "ranking171 encoding171", "mapping171 record171"],
    ),
    (
        ("filter171 ranking171 encoding171 mapping171 record171 candle171", 6),
        ["filter171", "ranking171", "encoding171", "mapping171", "record171", "candle171"],
    ),
    (
        ("filter171 ranking171 encoding171 mapping171 record171 candle171", 10),
        ["filter171", "ranking171", "encoding171", "mapping171", "record171", "candle171"],
    ),
    (
        ("filter171 ranking171 encoding171 mapping171 record171 candle171", 18),
        ["filter171", "ranking171", "encoding171", "mapping171", "record171", "candle171"],
    ),
    (
        ("filter171 ranking171 encoding171 mapping171 record171 candle171", 28),
        ["filter171 ranking171", "encoding171 mapping171", "record171 candle171"],
    ),
    (
        ("ranking171 encoding171 mapping171 record171 candle171 thread171", 6),
        ["ranking171", "encoding171", "mapping171", "record171", "candle171", "thread171"],
    ),
    (
        ("ranking171 encoding171 mapping171 record171 candle171 thread171", 10),
        ["ranking171", "encoding171", "mapping171", "record171", "candle171", "thread171"],
    ),
    (
        ("ranking171 encoding171 mapping171 record171 candle171 thread171", 18),
        ["ranking171", "encoding171", "mapping171", "record171", "candle171", "thread171"],
    ),
    (
        ("ranking171 encoding171 mapping171 record171 candle171 thread171", 28),
        ["ranking171 encoding171", "mapping171 record171", "candle171 thread171"],
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
