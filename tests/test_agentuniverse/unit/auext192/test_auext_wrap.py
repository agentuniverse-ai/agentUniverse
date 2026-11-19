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
        ("round 192: the quick brown fox jumps over the lazy dog", 4),
        ["round", "192:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 192: the quick brown fox jumps over the lazy dog", 8),
        ["round", "192: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 192: the quick brown fox jumps over the lazy dog", 12),
        ["round 192:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 192: the quick brown fox jumps over the lazy dog", 16),
        ["round 192: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 192: the quick brown fox jumps over the lazy dog", 24),
        ["round 192: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 192: the quick brown fox jumps over the lazy dog", 32),
        ["round 192: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 192: agentuniverse is a framework for multi agents", 4),
        ["round", "192:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 192: agentuniverse is a framework for multi agents", 8),
        ["round", "192:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 192: agentuniverse is a framework for multi agents", 12),
        ["round 192:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 192: agentuniverse is a framework for multi agents", 16),
        ["round 192:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 192: agentuniverse is a framework for multi agents", 24),
        ["round 192: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 192: agentuniverse is a framework for multi agents", 32),
        ["round 192: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 192: knowledge stored as vectors enables retrieval", 4),
        ["round", "192:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 192: knowledge stored as vectors enables retrieval", 8),
        ["round", "192:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 192: knowledge stored as vectors enables retrieval", 12),
        ["round 192:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 192: knowledge stored as vectors enables retrieval", 16),
        ["round 192:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 192: knowledge stored as vectors enables retrieval", 24),
        ["round 192: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 192: knowledge stored as vectors enables retrieval", 32),
        ["round 192: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 192: the processor reads the record then stops", 4),
        ["round", "192:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 192: the processor reads the record then stops", 8),
        ["round", "192: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 192: the processor reads the record then stops", 12),
        ["round 192:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 192: the processor reads the record then stops", 16),
        ["round 192: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 192: the processor reads the record then stops", 24),
        ["round 192: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 192: the processor reads the record then stops", 32),
        ["round 192: the processor reads", "the record then stops"],
    ),
    (
        ("round 192: a worker pulls the next task from the queue", 4),
        ["round", "192:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 192: a worker pulls the next task from the queue", 8),
        ["round", "192: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 192: a worker pulls the next task from the queue", 12),
        ["round 192: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 192: a worker pulls the next task from the queue", 16),
        ["round 192: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 192: a worker pulls the next task from the queue", 24),
        ["round 192: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 192: a worker pulls the next task from the queue", 32),
        ["round 192: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 192: signals travel through the network layer", 4),
        ["round", "192:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 192: signals travel through the network layer", 8),
        ["round", "192:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 192: signals travel through the network layer", 12),
        ["round 192:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 192: signals travel through the network layer", 16),
        ["round 192:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 192: signals travel through the network layer", 24),
        ["round 192: signals", "travel through the", "network layer"],
    ),
    (
        ("round 192: signals travel through the network layer", 32),
        ["round 192: signals travel", "through the network layer"],
    ),
    (
        ("round 192: the gateway routes each request by policy", 4),
        ["round", "192:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 192: the gateway routes each request by policy", 8),
        ["round", "192: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 192: the gateway routes each request by policy", 12),
        ["round 192:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 192: the gateway routes each request by policy", 16),
        ["round 192: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 192: the gateway routes each request by policy", 24),
        ["round 192: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 192: the gateway routes each request by policy", 32),
        ["round 192: the gateway routes", "each request by policy"],
    ),
    (
        ("round 192: memory grows until the buffer is full", 4),
        ["round", "192:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 192: memory grows until the buffer is full", 8),
        ["round", "192:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 192: memory grows until the buffer is full", 12),
        ["round 192:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 192: memory grows until the buffer is full", 16),
        ["round 192:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 192: memory grows until the buffer is full", 24), ["round 192: memory grows", "until the buffer is full"]),
    (("round 192: memory grows until the buffer is full", 32), ["round 192: memory grows until", "the buffer is full"]),
    (
        ("round 192: the cluster mirrors every packet twice", 4),
        ["round", "192:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 192: the cluster mirrors every packet twice", 8),
        ["round", "192: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 192: the cluster mirrors every packet twice", 12),
        ["round 192:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 192: the cluster mirrors every packet twice", 16),
        ["round 192: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 192: the cluster mirrors every packet twice", 24),
        ["round 192: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 192: the cluster mirrors every packet twice", 32),
        ["round 192: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 192: ranking uses tokens learned from the corpus", 4),
        ["round", "192:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 192: ranking uses tokens learned from the corpus", 8),
        ["round", "192:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 192: ranking uses tokens learned from the corpus", 12),
        ["round 192:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 192: ranking uses tokens learned from the corpus", 16),
        ["round 192:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 192: ranking uses tokens learned from the corpus", 24),
        ["round 192: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 192: ranking uses tokens learned from the corpus", 32),
        ["round 192: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 192: a long session ends when the candle dies", 4),
        ["round", "192:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 192: a long session ends when the candle dies", 8),
        ["round", "192: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 192: a long session ends when the candle dies", 12),
        ["round 192: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 192: a long session ends when the candle dies", 16),
        ["round 192: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 192: a long session ends when the candle dies", 24),
        ["round 192: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 192: a long session ends when the candle dies", 32),
        ["round 192: a long session ends", "when the candle dies"],
    ),
    (
        ("round 192: encode the prompt then map the result", 4),
        ["round", "192:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 192: encode the prompt then map the result", 8),
        ["round", "192:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 192: encode the prompt then map the result", 12),
        ["round 192:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 192: encode the prompt then map the result", 16),
        ["round 192:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 192: encode the prompt then map the result", 24),
        ["round 192: encode the", "prompt then map the", "result"],
    ),
    (("round 192: encode the prompt then map the result", 32), ["round 192: encode the prompt", "then map the result"]),
    (
        ("round 192: the kernel wakes the worker at dawn", 4),
        ["round", "192:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 192: the kernel wakes the worker at dawn", 8),
        ["round", "192: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 192: the kernel wakes the worker at dawn", 12),
        ["round 192:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 192: the kernel wakes the worker at dawn", 16), ["round 192: the", "kernel wakes the", "worker at dawn"]),
    (("round 192: the kernel wakes the worker at dawn", 24), ["round 192: the kernel", "wakes the worker at dawn"]),
    (("round 192: the kernel wakes the worker at dawn", 32), ["round 192: the kernel wakes the", "worker at dawn"]),
    (
        ("round 192: service latency drops after the patch", 4),
        ["round", "192:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 192: service latency drops after the patch", 8),
        ["round", "192:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 192: service latency drops after the patch", 12),
        ["round 192:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 192: service latency drops after the patch", 16),
        ["round 192:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 192: service latency drops after the patch", 24),
        ["round 192: service", "latency drops after the", "patch"],
    ),
    (("round 192: service latency drops after the patch", 32), ["round 192: service latency drops", "after the patch"]),
    (
        ("round 192: the library caches every vector it sees", 4),
        ["round", "192:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 192: the library caches every vector it sees", 8),
        ["round", "192: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 192: the library caches every vector it sees", 12),
        ["round 192:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 192: the library caches every vector it sees", 16),
        ["round 192: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 192: the library caches every vector it sees", 24),
        ["round 192: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 192: the library caches every vector it sees", 32),
        ["round 192: the library caches", "every vector it sees"],
    ),
    (
        ("round 192: agents argue then the debate resolves", 4),
        ["round", "192:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 192: agents argue then the debate resolves", 8),
        ["round", "192:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 192: agents argue then the debate resolves", 12),
        ["round 192:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 192: agents argue then the debate resolves", 16),
        ["round 192:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 192: agents argue then the debate resolves", 24), ["round 192: agents argue", "then the debate resolves"]),
    (("round 192: agents argue then the debate resolves", 32), ["round 192: agents argue then the", "debate resolves"]),
    (
        ("round 192: the filter keeps only strong matches", 4),
        ["round", "192:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 192: the filter keeps only strong matches", 8),
        ["round", "192: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 192: the filter keeps only strong matches", 12),
        ["round 192:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 192: the filter keeps only strong matches", 16),
        ["round 192: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 192: the filter keeps only strong matches", 24),
        ["round 192: the filter", "keeps only strong", "matches"],
    ),
    (("round 192: the filter keeps only strong matches", 32), ["round 192: the filter keeps only", "strong matches"]),
    (
        ("round 192: the model answers with a short reply", 4),
        ["round", "192:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 192: the model answers with a short reply", 8),
        ["round", "192: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 192: the model answers with a short reply", 12),
        ["round 192:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 192: the model answers with a short reply", 16),
        ["round 192: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 192: the model answers with a short reply", 24),
        ["round 192: the model", "answers with a short", "reply"],
    ),
    (("round 192: the model answers with a short reply", 32), ["round 192: the model answers", "with a short reply"]),
    (
        ("round 192: the recorder stores the reasoning trace", 4),
        ["round", "192:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 192: the recorder stores the reasoning trace", 8),
        ["round", "192: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 192: the recorder stores the reasoning trace", 12),
        ["round 192:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 192: the recorder stores the reasoning trace", 16),
        ["round 192: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 192: the recorder stores the reasoning trace", 24),
        ["round 192: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 192: the recorder stores the reasoning trace", 32),
        ["round 192: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 192: the angel watches the processor run", 4),
        ["round", "192:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 192: the angel watches the processor run", 8),
        ["round", "192: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 192: the angel watches the processor run", 12),
        ["round 192:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 192: the angel watches the processor run", 16),
        ["round 192: the", "angel watches", "the processor", "run"],
    ),
    (("round 192: the angel watches the processor run", 24), ["round 192: the angel", "watches the processor", "run"]),
    (("round 192: the angel watches the processor run", 32), ["round 192: the angel watches the", "processor run"]),
    (
        ("round 192: angle of the vector decides the match", 4),
        ["round", "192:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 192: angle of the vector decides the match", 8),
        ["round", "192:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 192: angle of the vector decides the match", 12),
        ["round 192:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 192: angle of the vector decides the match", 16),
        ["round 192: angle", "of the vector", "decides the", "match"],
    ),
    (("round 192: angle of the vector decides the match", 24), ["round 192: angle of the", "vector decides the match"]),
    (("round 192: angle of the vector decides the match", 32), ["round 192: angle of the vector", "decides the match"]),
    (
        ("round 192: the candle burns twice as long at night", 4),
        ["round", "192:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 192: the candle burns twice as long at night", 8),
        ["round", "192: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 192: the candle burns twice as long at night", 12),
        ["round 192:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 192: the candle burns twice as long at night", 16),
        ["round 192: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 192: the candle burns twice as long at night", 24),
        ["round 192: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 192: the candle burns twice as long at night", 32),
        ["round 192: the candle burns", "twice as long at night"],
    ),
    (
        ("round 192: a mirror of the universe in one line", 4),
        ["round", "192:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 192: a mirror of the universe in one line", 8),
        ["round", "192: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 192: a mirror of the universe in one line", 12),
        ["round 192: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 192: a mirror of the universe in one line", 16),
        ["round 192: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 192: a mirror of the universe in one line", 24), ["round 192: a mirror of", "the universe in one line"]),
    (("round 192: a mirror of the universe in one line", 32), ["round 192: a mirror of the", "universe in one line"]),
    (
        ("round 192: the queue drains before the storm", 4),
        ["round", "192:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 192: the queue drains before the storm", 8),
        ["round", "192: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 192: the queue drains before the storm", 12),
        ["round 192:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 192: the queue drains before the storm", 16), ["round 192: the", "queue drains", "before the storm"]),
    (("round 192: the queue drains before the storm", 24), ["round 192: the queue", "drains before the storm"]),
    (("round 192: the queue drains before the storm", 32), ["round 192: the queue drains", "before the storm"]),
    (
        ("kitten192 sitting192 agent192 angle192 universe192 memory192", 6),
        ["kitten192", "sitting192", "agent192", "angle192", "universe192", "memory192"],
    ),
    (
        ("kitten192 sitting192 agent192 angle192 universe192 memory192", 10),
        ["kitten192", "sitting192", "agent192", "angle192", "universe192", "memory192"],
    ),
    (
        ("kitten192 sitting192 agent192 angle192 universe192 memory192", 18),
        ["kitten192", "sitting192", "agent192 angle192", "universe192", "memory192"],
    ),
    (
        ("kitten192 sitting192 agent192 angle192 universe192 memory192", 28),
        ["kitten192 sitting192", "agent192 angle192", "universe192 memory192"],
    ),
    (
        ("sitting192 agent192 angle192 universe192 memory192 stream192", 6),
        ["sitting192", "agent192", "angle192", "universe192", "memory192", "stream192"],
    ),
    (
        ("sitting192 agent192 angle192 universe192 memory192 stream192", 10),
        ["sitting192", "agent192", "angle192", "universe192", "memory192", "stream192"],
    ),
    (
        ("sitting192 agent192 angle192 universe192 memory192 stream192", 18),
        ["sitting192", "agent192 angle192", "universe192", "memory192", "stream192"],
    ),
    (
        ("sitting192 agent192 angle192 universe192 memory192 stream192", 28),
        ["sitting192 agent192 angle192", "universe192 memory192", "stream192"],
    ),
    (
        ("agent192 angle192 universe192 memory192 stream192 context192", 6),
        ["agent192", "angle192", "universe192", "memory192", "stream192", "context192"],
    ),
    (
        ("agent192 angle192 universe192 memory192 stream192 context192", 10),
        ["agent192", "angle192", "universe192", "memory192", "stream192", "context192"],
    ),
    (
        ("agent192 angle192 universe192 memory192 stream192 context192", 18),
        ["agent192 angle192", "universe192", "memory192", "stream192", "context192"],
    ),
    (
        ("agent192 angle192 universe192 memory192 stream192 context192", 28),
        ["agent192 angle192", "universe192 memory192", "stream192 context192"],
    ),
    (
        ("angle192 universe192 memory192 stream192 context192 knowledge192", 6),
        ["angle192", "universe192", "memory192", "stream192", "context192", "knowledge192"],
    ),
    (
        ("angle192 universe192 memory192 stream192 context192 knowledge192", 10),
        ["angle192", "universe192", "memory192", "stream192", "context192", "knowledge192"],
    ),
    (
        ("angle192 universe192 memory192 stream192 context192 knowledge192", 18),
        ["angle192", "universe192", "memory192", "stream192", "context192", "knowledge192"],
    ),
    (
        ("angle192 universe192 memory192 stream192 context192 knowledge192", 28),
        ["angle192 universe192", "memory192 stream192", "context192 knowledge192"],
    ),
    (
        ("universe192 memory192 stream192 context192 knowledge192 vector192", 6),
        ["universe192", "memory192", "stream192", "context192", "knowledge192", "vector192"],
    ),
    (
        ("universe192 memory192 stream192 context192 knowledge192 vector192", 10),
        ["universe192", "memory192", "stream192", "context192", "knowledge192", "vector192"],
    ),
    (
        ("universe192 memory192 stream192 context192 knowledge192 vector192", 18),
        ["universe192", "memory192", "stream192", "context192", "knowledge192", "vector192"],
    ),
    (
        ("universe192 memory192 stream192 context192 knowledge192 vector192", 28),
        ["universe192 memory192", "stream192 context192", "knowledge192 vector192"],
    ),
    (
        ("memory192 stream192 context192 knowledge192 vector192 processor192", 6),
        ["memory192", "stream192", "context192", "knowledge192", "vector192", "processor192"],
    ),
    (
        ("memory192 stream192 context192 knowledge192 vector192 processor192", 10),
        ["memory192", "stream192", "context192", "knowledge192", "vector192", "processor192"],
    ),
    (
        ("memory192 stream192 context192 knowledge192 vector192 processor192", 18),
        ["memory192", "stream192", "context192", "knowledge192", "vector192", "processor192"],
    ),
    (
        ("memory192 stream192 context192 knowledge192 vector192 processor192", 28),
        ["memory192 stream192", "context192 knowledge192", "vector192 processor192"],
    ),
    (
        ("stream192 context192 knowledge192 vector192 processor192 reasoning192", 6),
        ["stream192", "context192", "knowledge192", "vector192", "processor192", "reasoning192"],
    ),
    (
        ("stream192 context192 knowledge192 vector192 processor192 reasoning192", 10),
        ["stream192", "context192", "knowledge192", "vector192", "processor192", "reasoning192"],
    ),
    (
        ("stream192 context192 knowledge192 vector192 processor192 reasoning192", 18),
        ["stream192", "context192", "knowledge192", "vector192", "processor192", "reasoning192"],
    ),
    (
        ("stream192 context192 knowledge192 vector192 processor192 reasoning192", 28),
        ["stream192 context192", "knowledge192 vector192", "processor192 reasoning192"],
    ),
    (
        ("context192 knowledge192 vector192 processor192 reasoning192 machine192", 6),
        ["context192", "knowledge192", "vector192", "processor192", "reasoning192", "machine192"],
    ),
    (
        ("context192 knowledge192 vector192 processor192 reasoning192 machine192", 10),
        ["context192", "knowledge192", "vector192", "processor192", "reasoning192", "machine192"],
    ),
    (
        ("context192 knowledge192 vector192 processor192 reasoning192 machine192", 18),
        ["context192", "knowledge192", "vector192", "processor192", "reasoning192", "machine192"],
    ),
    (
        ("context192 knowledge192 vector192 processor192 reasoning192 machine192", 28),
        ["context192 knowledge192", "vector192 processor192", "reasoning192 machine192"],
    ),
    (
        ("knowledge192 vector192 processor192 reasoning192 machine192 learning192", 6),
        ["knowledge192", "vector192", "processor192", "reasoning192", "machine192", "learning192"],
    ),
    (
        ("knowledge192 vector192 processor192 reasoning192 machine192 learning192", 10),
        ["knowledge192", "vector192", "processor192", "reasoning192", "machine192", "learning192"],
    ),
    (
        ("knowledge192 vector192 processor192 reasoning192 machine192 learning192", 18),
        ["knowledge192", "vector192", "processor192", "reasoning192", "machine192", "learning192"],
    ),
    (
        ("knowledge192 vector192 processor192 reasoning192 machine192 learning192", 28),
        ["knowledge192 vector192", "processor192 reasoning192", "machine192 learning192"],
    ),
    (
        ("vector192 processor192 reasoning192 machine192 learning192 model192", 6),
        ["vector192", "processor192", "reasoning192", "machine192", "learning192", "model192"],
    ),
    (
        ("vector192 processor192 reasoning192 machine192 learning192 model192", 10),
        ["vector192", "processor192", "reasoning192", "machine192", "learning192", "model192"],
    ),
    (
        ("vector192 processor192 reasoning192 machine192 learning192 model192", 18),
        ["vector192", "processor192", "reasoning192", "machine192", "learning192", "model192"],
    ),
    (
        ("vector192 processor192 reasoning192 machine192 learning192 model192", 28),
        ["vector192 processor192", "reasoning192 machine192", "learning192 model192"],
    ),
    (
        ("processor192 reasoning192 machine192 learning192 model192 token192", 6),
        ["processor192", "reasoning192", "machine192", "learning192", "model192", "token192"],
    ),
    (
        ("processor192 reasoning192 machine192 learning192 model192 token192", 10),
        ["processor192", "reasoning192", "machine192", "learning192", "model192", "token192"],
    ),
    (
        ("processor192 reasoning192 machine192 learning192 model192 token192", 18),
        ["processor192", "reasoning192", "machine192", "learning192", "model192 token192"],
    ),
    (
        ("processor192 reasoning192 machine192 learning192 model192 token192", 28),
        ["processor192 reasoning192", "machine192 learning192", "model192 token192"],
    ),
    (
        ("reasoning192 machine192 learning192 model192 token192 prompt192", 6),
        ["reasoning192", "machine192", "learning192", "model192", "token192", "prompt192"],
    ),
    (
        ("reasoning192 machine192 learning192 model192 token192 prompt192", 10),
        ["reasoning192", "machine192", "learning192", "model192", "token192", "prompt192"],
    ),
    (
        ("reasoning192 machine192 learning192 model192 token192 prompt192", 18),
        ["reasoning192", "machine192", "learning192", "model192 token192", "prompt192"],
    ),
    (
        ("reasoning192 machine192 learning192 model192 token192 prompt192", 28),
        ["reasoning192 machine192", "learning192 model192", "token192 prompt192"],
    ),
    (
        ("machine192 learning192 model192 token192 prompt192 session192", 6),
        ["machine192", "learning192", "model192", "token192", "prompt192", "session192"],
    ),
    (
        ("machine192 learning192 model192 token192 prompt192 session192", 10),
        ["machine192", "learning192", "model192", "token192", "prompt192", "session192"],
    ),
    (
        ("machine192 learning192 model192 token192 prompt192 session192", 18),
        ["machine192", "learning192", "model192 token192", "prompt192", "session192"],
    ),
    (
        ("machine192 learning192 model192 token192 prompt192 session192", 28),
        ["machine192 learning192", "model192 token192 prompt192", "session192"],
    ),
    (
        ("learning192 model192 token192 prompt192 session192 library192", 6),
        ["learning192", "model192", "token192", "prompt192", "session192", "library192"],
    ),
    (
        ("learning192 model192 token192 prompt192 session192 library192", 10),
        ["learning192", "model192", "token192", "prompt192", "session192", "library192"],
    ),
    (
        ("learning192 model192 token192 prompt192 session192 library192", 18),
        ["learning192", "model192 token192", "prompt192", "session192", "library192"],
    ),
    (
        ("learning192 model192 token192 prompt192 session192 library192", 28),
        ["learning192 model192", "token192 prompt192", "session192 library192"],
    ),
    (
        ("model192 token192 prompt192 session192 library192 service192", 6),
        ["model192", "token192", "prompt192", "session192", "library192", "service192"],
    ),
    (
        ("model192 token192 prompt192 session192 library192 service192", 10),
        ["model192", "token192", "prompt192", "session192", "library192", "service192"],
    ),
    (
        ("model192 token192 prompt192 session192 library192 service192", 18),
        ["model192 token192", "prompt192", "session192", "library192", "service192"],
    ),
    (
        ("model192 token192 prompt192 session192 library192 service192", 28),
        ["model192 token192 prompt192", "session192 library192", "service192"],
    ),
    (
        ("token192 prompt192 session192 library192 service192 gateway192", 6),
        ["token192", "prompt192", "session192", "library192", "service192", "gateway192"],
    ),
    (
        ("token192 prompt192 session192 library192 service192 gateway192", 10),
        ["token192", "prompt192", "session192", "library192", "service192", "gateway192"],
    ),
    (
        ("token192 prompt192 session192 library192 service192 gateway192", 18),
        ["token192 prompt192", "session192", "library192", "service192", "gateway192"],
    ),
    (
        ("token192 prompt192 session192 library192 service192 gateway192", 28),
        ["token192 prompt192", "session192 library192", "service192 gateway192"],
    ),
    (
        ("prompt192 session192 library192 service192 gateway192 storage192", 6),
        ["prompt192", "session192", "library192", "service192", "gateway192", "storage192"],
    ),
    (
        ("prompt192 session192 library192 service192 gateway192 storage192", 10),
        ["prompt192", "session192", "library192", "service192", "gateway192", "storage192"],
    ),
    (
        ("prompt192 session192 library192 service192 gateway192 storage192", 18),
        ["prompt192", "session192", "library192", "service192", "gateway192", "storage192"],
    ),
    (
        ("prompt192 session192 library192 service192 gateway192 storage192", 28),
        ["prompt192 session192", "library192 service192", "gateway192 storage192"],
    ),
    (
        ("session192 library192 service192 gateway192 storage192 network192", 6),
        ["session192", "library192", "service192", "gateway192", "storage192", "network192"],
    ),
    (
        ("session192 library192 service192 gateway192 storage192 network192", 10),
        ["session192", "library192", "service192", "gateway192", "storage192", "network192"],
    ),
    (
        ("session192 library192 service192 gateway192 storage192 network192", 18),
        ["session192", "library192", "service192", "gateway192", "storage192", "network192"],
    ),
    (
        ("session192 library192 service192 gateway192 storage192 network192", 28),
        ["session192 library192", "service192 gateway192", "storage192 network192"],
    ),
    (
        ("library192 service192 gateway192 storage192 network192 latency192", 6),
        ["library192", "service192", "gateway192", "storage192", "network192", "latency192"],
    ),
    (
        ("library192 service192 gateway192 storage192 network192 latency192", 10),
        ["library192", "service192", "gateway192", "storage192", "network192", "latency192"],
    ),
    (
        ("library192 service192 gateway192 storage192 network192 latency192", 18),
        ["library192", "service192", "gateway192", "storage192", "network192", "latency192"],
    ),
    (
        ("library192 service192 gateway192 storage192 network192 latency192", 28),
        ["library192 service192", "gateway192 storage192", "network192 latency192"],
    ),
    (
        ("service192 gateway192 storage192 network192 latency192 buffer192", 6),
        ["service192", "gateway192", "storage192", "network192", "latency192", "buffer192"],
    ),
    (
        ("service192 gateway192 storage192 network192 latency192 buffer192", 10),
        ["service192", "gateway192", "storage192", "network192", "latency192", "buffer192"],
    ),
    (
        ("service192 gateway192 storage192 network192 latency192 buffer192", 18),
        ["service192", "gateway192", "storage192", "network192", "latency192", "buffer192"],
    ),
    (
        ("service192 gateway192 storage192 network192 latency192 buffer192", 28),
        ["service192 gateway192", "storage192 network192", "latency192 buffer192"],
    ),
    (
        ("gateway192 storage192 network192 latency192 buffer192 queue192", 6),
        ["gateway192", "storage192", "network192", "latency192", "buffer192", "queue192"],
    ),
    (
        ("gateway192 storage192 network192 latency192 buffer192 queue192", 10),
        ["gateway192", "storage192", "network192", "latency192", "buffer192", "queue192"],
    ),
    (
        ("gateway192 storage192 network192 latency192 buffer192 queue192", 18),
        ["gateway192", "storage192", "network192", "latency192", "buffer192 queue192"],
    ),
    (
        ("gateway192 storage192 network192 latency192 buffer192 queue192", 28),
        ["gateway192 storage192", "network192 latency192", "buffer192 queue192"],
    ),
    (
        ("storage192 network192 latency192 buffer192 queue192 worker192", 6),
        ["storage192", "network192", "latency192", "buffer192", "queue192", "worker192"],
    ),
    (
        ("storage192 network192 latency192 buffer192 queue192 worker192", 10),
        ["storage192", "network192", "latency192", "buffer192", "queue192", "worker192"],
    ),
    (
        ("storage192 network192 latency192 buffer192 queue192 worker192", 18),
        ["storage192", "network192", "latency192", "buffer192 queue192", "worker192"],
    ),
    (
        ("storage192 network192 latency192 buffer192 queue192 worker192", 28),
        ["storage192 network192", "latency192 buffer192", "queue192 worker192"],
    ),
    (
        ("network192 latency192 buffer192 queue192 worker192 kernel192", 6),
        ["network192", "latency192", "buffer192", "queue192", "worker192", "kernel192"],
    ),
    (
        ("network192 latency192 buffer192 queue192 worker192 kernel192", 10),
        ["network192", "latency192", "buffer192", "queue192", "worker192", "kernel192"],
    ),
    (
        ("network192 latency192 buffer192 queue192 worker192 kernel192", 18),
        ["network192", "latency192", "buffer192 queue192", "worker192", "kernel192"],
    ),
    (
        ("network192 latency192 buffer192 queue192 worker192 kernel192", 28),
        ["network192 latency192", "buffer192 queue192 worker192", "kernel192"],
    ),
    (
        ("latency192 buffer192 queue192 worker192 kernel192 signal192", 6),
        ["latency192", "buffer192", "queue192", "worker192", "kernel192", "signal192"],
    ),
    (
        ("latency192 buffer192 queue192 worker192 kernel192 signal192", 10),
        ["latency192", "buffer192", "queue192", "worker192", "kernel192", "signal192"],
    ),
    (
        ("latency192 buffer192 queue192 worker192 kernel192 signal192", 18),
        ["latency192", "buffer192 queue192", "worker192", "kernel192", "signal192"],
    ),
    (
        ("latency192 buffer192 queue192 worker192 kernel192 signal192", 28),
        ["latency192 buffer192", "queue192 worker192 kernel192", "signal192"],
    ),
    (
        ("buffer192 queue192 worker192 kernel192 signal192 packet192", 6),
        ["buffer192", "queue192", "worker192", "kernel192", "signal192", "packet192"],
    ),
    (
        ("buffer192 queue192 worker192 kernel192 signal192 packet192", 10),
        ["buffer192", "queue192", "worker192", "kernel192", "signal192", "packet192"],
    ),
    (
        ("buffer192 queue192 worker192 kernel192 signal192 packet192", 18),
        ["buffer192 queue192", "worker192", "kernel192", "signal192", "packet192"],
    ),
    (
        ("buffer192 queue192 worker192 kernel192 signal192 packet192", 28),
        ["buffer192 queue192 worker192", "kernel192 signal192", "packet192"],
    ),
    (
        ("queue192 worker192 kernel192 signal192 packet192 router192", 6),
        ["queue192", "worker192", "kernel192", "signal192", "packet192", "router192"],
    ),
    (
        ("queue192 worker192 kernel192 signal192 packet192 router192", 10),
        ["queue192", "worker192", "kernel192", "signal192", "packet192", "router192"],
    ),
    (
        ("queue192 worker192 kernel192 signal192 packet192 router192", 18),
        ["queue192 worker192", "kernel192", "signal192", "packet192", "router192"],
    ),
    (
        ("queue192 worker192 kernel192 signal192 packet192 router192", 28),
        ["queue192 worker192 kernel192", "signal192 packet192", "router192"],
    ),
    (
        ("worker192 kernel192 signal192 packet192 router192 cluster192", 6),
        ["worker192", "kernel192", "signal192", "packet192", "router192", "cluster192"],
    ),
    (
        ("worker192 kernel192 signal192 packet192 router192 cluster192", 10),
        ["worker192", "kernel192", "signal192", "packet192", "router192", "cluster192"],
    ),
    (
        ("worker192 kernel192 signal192 packet192 router192 cluster192", 18),
        ["worker192", "kernel192", "signal192", "packet192", "router192", "cluster192"],
    ),
    (
        ("worker192 kernel192 signal192 packet192 router192 cluster192", 28),
        ["worker192 kernel192", "signal192 packet192", "router192 cluster192"],
    ),
    (
        ("kernel192 signal192 packet192 router192 cluster192 mirror192", 6),
        ["kernel192", "signal192", "packet192", "router192", "cluster192", "mirror192"],
    ),
    (
        ("kernel192 signal192 packet192 router192 cluster192 mirror192", 10),
        ["kernel192", "signal192", "packet192", "router192", "cluster192", "mirror192"],
    ),
    (
        ("kernel192 signal192 packet192 router192 cluster192 mirror192", 18),
        ["kernel192", "signal192", "packet192", "router192", "cluster192", "mirror192"],
    ),
    (
        ("kernel192 signal192 packet192 router192 cluster192 mirror192", 28),
        ["kernel192 signal192", "packet192 router192", "cluster192 mirror192"],
    ),
    (
        ("signal192 packet192 router192 cluster192 mirror192 filter192", 6),
        ["signal192", "packet192", "router192", "cluster192", "mirror192", "filter192"],
    ),
    (
        ("signal192 packet192 router192 cluster192 mirror192 filter192", 10),
        ["signal192", "packet192", "router192", "cluster192", "mirror192", "filter192"],
    ),
    (
        ("signal192 packet192 router192 cluster192 mirror192 filter192", 18),
        ["signal192", "packet192", "router192", "cluster192", "mirror192", "filter192"],
    ),
    (
        ("signal192 packet192 router192 cluster192 mirror192 filter192", 28),
        ["signal192 packet192", "router192 cluster192", "mirror192 filter192"],
    ),
    (
        ("packet192 router192 cluster192 mirror192 filter192 ranking192", 6),
        ["packet192", "router192", "cluster192", "mirror192", "filter192", "ranking192"],
    ),
    (
        ("packet192 router192 cluster192 mirror192 filter192 ranking192", 10),
        ["packet192", "router192", "cluster192", "mirror192", "filter192", "ranking192"],
    ),
    (
        ("packet192 router192 cluster192 mirror192 filter192 ranking192", 18),
        ["packet192", "router192", "cluster192", "mirror192", "filter192", "ranking192"],
    ),
    (
        ("packet192 router192 cluster192 mirror192 filter192 ranking192", 28),
        ["packet192 router192", "cluster192 mirror192", "filter192 ranking192"],
    ),
    (
        ("router192 cluster192 mirror192 filter192 ranking192 encoding192", 6),
        ["router192", "cluster192", "mirror192", "filter192", "ranking192", "encoding192"],
    ),
    (
        ("router192 cluster192 mirror192 filter192 ranking192 encoding192", 10),
        ["router192", "cluster192", "mirror192", "filter192", "ranking192", "encoding192"],
    ),
    (
        ("router192 cluster192 mirror192 filter192 ranking192 encoding192", 18),
        ["router192", "cluster192", "mirror192", "filter192", "ranking192", "encoding192"],
    ),
    (
        ("router192 cluster192 mirror192 filter192 ranking192 encoding192", 28),
        ["router192 cluster192", "mirror192 filter192", "ranking192 encoding192"],
    ),
    (
        ("cluster192 mirror192 filter192 ranking192 encoding192 mapping192", 6),
        ["cluster192", "mirror192", "filter192", "ranking192", "encoding192", "mapping192"],
    ),
    (
        ("cluster192 mirror192 filter192 ranking192 encoding192 mapping192", 10),
        ["cluster192", "mirror192", "filter192", "ranking192", "encoding192", "mapping192"],
    ),
    (
        ("cluster192 mirror192 filter192 ranking192 encoding192 mapping192", 18),
        ["cluster192", "mirror192", "filter192", "ranking192", "encoding192", "mapping192"],
    ),
    (
        ("cluster192 mirror192 filter192 ranking192 encoding192 mapping192", 28),
        ["cluster192 mirror192", "filter192 ranking192", "encoding192 mapping192"],
    ),
    (
        ("mirror192 filter192 ranking192 encoding192 mapping192 record192", 6),
        ["mirror192", "filter192", "ranking192", "encoding192", "mapping192", "record192"],
    ),
    (
        ("mirror192 filter192 ranking192 encoding192 mapping192 record192", 10),
        ["mirror192", "filter192", "ranking192", "encoding192", "mapping192", "record192"],
    ),
    (
        ("mirror192 filter192 ranking192 encoding192 mapping192 record192", 18),
        ["mirror192", "filter192", "ranking192", "encoding192", "mapping192", "record192"],
    ),
    (
        ("mirror192 filter192 ranking192 encoding192 mapping192 record192", 28),
        ["mirror192 filter192", "ranking192 encoding192", "mapping192 record192"],
    ),
    (
        ("filter192 ranking192 encoding192 mapping192 record192 candle192", 6),
        ["filter192", "ranking192", "encoding192", "mapping192", "record192", "candle192"],
    ),
    (
        ("filter192 ranking192 encoding192 mapping192 record192 candle192", 10),
        ["filter192", "ranking192", "encoding192", "mapping192", "record192", "candle192"],
    ),
    (
        ("filter192 ranking192 encoding192 mapping192 record192 candle192", 18),
        ["filter192", "ranking192", "encoding192", "mapping192", "record192", "candle192"],
    ),
    (
        ("filter192 ranking192 encoding192 mapping192 record192 candle192", 28),
        ["filter192 ranking192", "encoding192 mapping192", "record192 candle192"],
    ),
    (
        ("ranking192 encoding192 mapping192 record192 candle192 thread192", 6),
        ["ranking192", "encoding192", "mapping192", "record192", "candle192", "thread192"],
    ),
    (
        ("ranking192 encoding192 mapping192 record192 candle192 thread192", 10),
        ["ranking192", "encoding192", "mapping192", "record192", "candle192", "thread192"],
    ),
    (
        ("ranking192 encoding192 mapping192 record192 candle192 thread192", 18),
        ["ranking192", "encoding192", "mapping192", "record192", "candle192", "thread192"],
    ),
    (
        ("ranking192 encoding192 mapping192 record192 candle192 thread192", 28),
        ["ranking192 encoding192", "mapping192 record192", "candle192 thread192"],
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
