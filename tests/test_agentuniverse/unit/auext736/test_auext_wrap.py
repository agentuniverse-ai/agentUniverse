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
        ("round 736: the quick brown fox jumps over the lazy dog", 4),
        ["round", "736:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 736: the quick brown fox jumps over the lazy dog", 8),
        ["round", "736: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 736: the quick brown fox jumps over the lazy dog", 12),
        ["round 736:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 736: the quick brown fox jumps over the lazy dog", 16),
        ["round 736: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 736: the quick brown fox jumps over the lazy dog", 24),
        ["round 736: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 736: the quick brown fox jumps over the lazy dog", 32),
        ["round 736: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 736: agentuniverse is a framework for multi agents", 4),
        ["round", "736:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 736: agentuniverse is a framework for multi agents", 8),
        ["round", "736:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 736: agentuniverse is a framework for multi agents", 12),
        ["round 736:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 736: agentuniverse is a framework for multi agents", 16),
        ["round 736:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 736: agentuniverse is a framework for multi agents", 24),
        ["round 736: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 736: agentuniverse is a framework for multi agents", 32),
        ["round 736: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 736: knowledge stored as vectors enables retrieval", 4),
        ["round", "736:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 736: knowledge stored as vectors enables retrieval", 8),
        ["round", "736:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 736: knowledge stored as vectors enables retrieval", 12),
        ["round 736:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 736: knowledge stored as vectors enables retrieval", 16),
        ["round 736:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 736: knowledge stored as vectors enables retrieval", 24),
        ["round 736: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 736: knowledge stored as vectors enables retrieval", 32),
        ["round 736: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 736: the processor reads the record then stops", 4),
        ["round", "736:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 736: the processor reads the record then stops", 8),
        ["round", "736: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 736: the processor reads the record then stops", 12),
        ["round 736:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 736: the processor reads the record then stops", 16),
        ["round 736: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 736: the processor reads the record then stops", 24),
        ["round 736: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 736: the processor reads the record then stops", 32),
        ["round 736: the processor reads", "the record then stops"],
    ),
    (
        ("round 736: a worker pulls the next task from the queue", 4),
        ["round", "736:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 736: a worker pulls the next task from the queue", 8),
        ["round", "736: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 736: a worker pulls the next task from the queue", 12),
        ["round 736: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 736: a worker pulls the next task from the queue", 16),
        ["round 736: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 736: a worker pulls the next task from the queue", 24),
        ["round 736: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 736: a worker pulls the next task from the queue", 32),
        ["round 736: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 736: signals travel through the network layer", 4),
        ["round", "736:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 736: signals travel through the network layer", 8),
        ["round", "736:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 736: signals travel through the network layer", 12),
        ["round 736:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 736: signals travel through the network layer", 16),
        ["round 736:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 736: signals travel through the network layer", 24),
        ["round 736: signals", "travel through the", "network layer"],
    ),
    (
        ("round 736: signals travel through the network layer", 32),
        ["round 736: signals travel", "through the network layer"],
    ),
    (
        ("round 736: the gateway routes each request by policy", 4),
        ["round", "736:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 736: the gateway routes each request by policy", 8),
        ["round", "736: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 736: the gateway routes each request by policy", 12),
        ["round 736:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 736: the gateway routes each request by policy", 16),
        ["round 736: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 736: the gateway routes each request by policy", 24),
        ["round 736: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 736: the gateway routes each request by policy", 32),
        ["round 736: the gateway routes", "each request by policy"],
    ),
    (
        ("round 736: memory grows until the buffer is full", 4),
        ["round", "736:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 736: memory grows until the buffer is full", 8),
        ["round", "736:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 736: memory grows until the buffer is full", 12),
        ["round 736:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 736: memory grows until the buffer is full", 16),
        ["round 736:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 736: memory grows until the buffer is full", 24), ["round 736: memory grows", "until the buffer is full"]),
    (("round 736: memory grows until the buffer is full", 32), ["round 736: memory grows until", "the buffer is full"]),
    (
        ("round 736: the cluster mirrors every packet twice", 4),
        ["round", "736:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 736: the cluster mirrors every packet twice", 8),
        ["round", "736: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 736: the cluster mirrors every packet twice", 12),
        ["round 736:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 736: the cluster mirrors every packet twice", 16),
        ["round 736: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 736: the cluster mirrors every packet twice", 24),
        ["round 736: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 736: the cluster mirrors every packet twice", 32),
        ["round 736: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 736: ranking uses tokens learned from the corpus", 4),
        ["round", "736:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 736: ranking uses tokens learned from the corpus", 8),
        ["round", "736:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 736: ranking uses tokens learned from the corpus", 12),
        ["round 736:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 736: ranking uses tokens learned from the corpus", 16),
        ["round 736:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 736: ranking uses tokens learned from the corpus", 24),
        ["round 736: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 736: ranking uses tokens learned from the corpus", 32),
        ["round 736: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 736: a long session ends when the candle dies", 4),
        ["round", "736:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 736: a long session ends when the candle dies", 8),
        ["round", "736: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 736: a long session ends when the candle dies", 12),
        ["round 736: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 736: a long session ends when the candle dies", 16),
        ["round 736: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 736: a long session ends when the candle dies", 24),
        ["round 736: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 736: a long session ends when the candle dies", 32),
        ["round 736: a long session ends", "when the candle dies"],
    ),
    (
        ("round 736: encode the prompt then map the result", 4),
        ["round", "736:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 736: encode the prompt then map the result", 8),
        ["round", "736:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 736: encode the prompt then map the result", 12),
        ["round 736:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 736: encode the prompt then map the result", 16),
        ["round 736:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 736: encode the prompt then map the result", 24),
        ["round 736: encode the", "prompt then map the", "result"],
    ),
    (("round 736: encode the prompt then map the result", 32), ["round 736: encode the prompt", "then map the result"]),
    (
        ("round 736: the kernel wakes the worker at dawn", 4),
        ["round", "736:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 736: the kernel wakes the worker at dawn", 8),
        ["round", "736: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 736: the kernel wakes the worker at dawn", 12),
        ["round 736:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 736: the kernel wakes the worker at dawn", 16), ["round 736: the", "kernel wakes the", "worker at dawn"]),
    (("round 736: the kernel wakes the worker at dawn", 24), ["round 736: the kernel", "wakes the worker at dawn"]),
    (("round 736: the kernel wakes the worker at dawn", 32), ["round 736: the kernel wakes the", "worker at dawn"]),
    (
        ("round 736: service latency drops after the patch", 4),
        ["round", "736:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 736: service latency drops after the patch", 8),
        ["round", "736:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 736: service latency drops after the patch", 12),
        ["round 736:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 736: service latency drops after the patch", 16),
        ["round 736:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 736: service latency drops after the patch", 24),
        ["round 736: service", "latency drops after the", "patch"],
    ),
    (("round 736: service latency drops after the patch", 32), ["round 736: service latency drops", "after the patch"]),
    (
        ("round 736: the library caches every vector it sees", 4),
        ["round", "736:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 736: the library caches every vector it sees", 8),
        ["round", "736: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 736: the library caches every vector it sees", 12),
        ["round 736:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 736: the library caches every vector it sees", 16),
        ["round 736: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 736: the library caches every vector it sees", 24),
        ["round 736: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 736: the library caches every vector it sees", 32),
        ["round 736: the library caches", "every vector it sees"],
    ),
    (
        ("round 736: agents argue then the debate resolves", 4),
        ["round", "736:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 736: agents argue then the debate resolves", 8),
        ["round", "736:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 736: agents argue then the debate resolves", 12),
        ["round 736:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 736: agents argue then the debate resolves", 16),
        ["round 736:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 736: agents argue then the debate resolves", 24), ["round 736: agents argue", "then the debate resolves"]),
    (("round 736: agents argue then the debate resolves", 32), ["round 736: agents argue then the", "debate resolves"]),
    (
        ("round 736: the filter keeps only strong matches", 4),
        ["round", "736:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 736: the filter keeps only strong matches", 8),
        ["round", "736: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 736: the filter keeps only strong matches", 12),
        ["round 736:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 736: the filter keeps only strong matches", 16),
        ["round 736: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 736: the filter keeps only strong matches", 24),
        ["round 736: the filter", "keeps only strong", "matches"],
    ),
    (("round 736: the filter keeps only strong matches", 32), ["round 736: the filter keeps only", "strong matches"]),
    (
        ("round 736: the model answers with a short reply", 4),
        ["round", "736:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 736: the model answers with a short reply", 8),
        ["round", "736: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 736: the model answers with a short reply", 12),
        ["round 736:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 736: the model answers with a short reply", 16),
        ["round 736: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 736: the model answers with a short reply", 24),
        ["round 736: the model", "answers with a short", "reply"],
    ),
    (("round 736: the model answers with a short reply", 32), ["round 736: the model answers", "with a short reply"]),
    (
        ("round 736: the recorder stores the reasoning trace", 4),
        ["round", "736:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 736: the recorder stores the reasoning trace", 8),
        ["round", "736: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 736: the recorder stores the reasoning trace", 12),
        ["round 736:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 736: the recorder stores the reasoning trace", 16),
        ["round 736: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 736: the recorder stores the reasoning trace", 24),
        ["round 736: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 736: the recorder stores the reasoning trace", 32),
        ["round 736: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 736: the angel watches the processor run", 4),
        ["round", "736:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 736: the angel watches the processor run", 8),
        ["round", "736: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 736: the angel watches the processor run", 12),
        ["round 736:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 736: the angel watches the processor run", 16),
        ["round 736: the", "angel watches", "the processor", "run"],
    ),
    (("round 736: the angel watches the processor run", 24), ["round 736: the angel", "watches the processor", "run"]),
    (("round 736: the angel watches the processor run", 32), ["round 736: the angel watches the", "processor run"]),
    (
        ("round 736: angle of the vector decides the match", 4),
        ["round", "736:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 736: angle of the vector decides the match", 8),
        ["round", "736:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 736: angle of the vector decides the match", 12),
        ["round 736:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 736: angle of the vector decides the match", 16),
        ["round 736: angle", "of the vector", "decides the", "match"],
    ),
    (("round 736: angle of the vector decides the match", 24), ["round 736: angle of the", "vector decides the match"]),
    (("round 736: angle of the vector decides the match", 32), ["round 736: angle of the vector", "decides the match"]),
    (
        ("round 736: the candle burns twice as long at night", 4),
        ["round", "736:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 736: the candle burns twice as long at night", 8),
        ["round", "736: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 736: the candle burns twice as long at night", 12),
        ["round 736:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 736: the candle burns twice as long at night", 16),
        ["round 736: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 736: the candle burns twice as long at night", 24),
        ["round 736: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 736: the candle burns twice as long at night", 32),
        ["round 736: the candle burns", "twice as long at night"],
    ),
    (
        ("round 736: a mirror of the universe in one line", 4),
        ["round", "736:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 736: a mirror of the universe in one line", 8),
        ["round", "736: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 736: a mirror of the universe in one line", 12),
        ["round 736: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 736: a mirror of the universe in one line", 16),
        ["round 736: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 736: a mirror of the universe in one line", 24), ["round 736: a mirror of", "the universe in one line"]),
    (("round 736: a mirror of the universe in one line", 32), ["round 736: a mirror of the", "universe in one line"]),
    (
        ("round 736: the queue drains before the storm", 4),
        ["round", "736:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 736: the queue drains before the storm", 8),
        ["round", "736: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 736: the queue drains before the storm", 12),
        ["round 736:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 736: the queue drains before the storm", 16), ["round 736: the", "queue drains", "before the storm"]),
    (("round 736: the queue drains before the storm", 24), ["round 736: the queue", "drains before the storm"]),
    (("round 736: the queue drains before the storm", 32), ["round 736: the queue drains", "before the storm"]),
    (
        ("kitten736 sitting736 agent736 angle736 universe736 memory736", 6),
        ["kitten736", "sitting736", "agent736", "angle736", "universe736", "memory736"],
    ),
    (
        ("kitten736 sitting736 agent736 angle736 universe736 memory736", 10),
        ["kitten736", "sitting736", "agent736", "angle736", "universe736", "memory736"],
    ),
    (
        ("kitten736 sitting736 agent736 angle736 universe736 memory736", 18),
        ["kitten736", "sitting736", "agent736 angle736", "universe736", "memory736"],
    ),
    (
        ("kitten736 sitting736 agent736 angle736 universe736 memory736", 28),
        ["kitten736 sitting736", "agent736 angle736", "universe736 memory736"],
    ),
    (
        ("sitting736 agent736 angle736 universe736 memory736 stream736", 6),
        ["sitting736", "agent736", "angle736", "universe736", "memory736", "stream736"],
    ),
    (
        ("sitting736 agent736 angle736 universe736 memory736 stream736", 10),
        ["sitting736", "agent736", "angle736", "universe736", "memory736", "stream736"],
    ),
    (
        ("sitting736 agent736 angle736 universe736 memory736 stream736", 18),
        ["sitting736", "agent736 angle736", "universe736", "memory736", "stream736"],
    ),
    (
        ("sitting736 agent736 angle736 universe736 memory736 stream736", 28),
        ["sitting736 agent736 angle736", "universe736 memory736", "stream736"],
    ),
    (
        ("agent736 angle736 universe736 memory736 stream736 context736", 6),
        ["agent736", "angle736", "universe736", "memory736", "stream736", "context736"],
    ),
    (
        ("agent736 angle736 universe736 memory736 stream736 context736", 10),
        ["agent736", "angle736", "universe736", "memory736", "stream736", "context736"],
    ),
    (
        ("agent736 angle736 universe736 memory736 stream736 context736", 18),
        ["agent736 angle736", "universe736", "memory736", "stream736", "context736"],
    ),
    (
        ("agent736 angle736 universe736 memory736 stream736 context736", 28),
        ["agent736 angle736", "universe736 memory736", "stream736 context736"],
    ),
    (
        ("angle736 universe736 memory736 stream736 context736 knowledge736", 6),
        ["angle736", "universe736", "memory736", "stream736", "context736", "knowledge736"],
    ),
    (
        ("angle736 universe736 memory736 stream736 context736 knowledge736", 10),
        ["angle736", "universe736", "memory736", "stream736", "context736", "knowledge736"],
    ),
    (
        ("angle736 universe736 memory736 stream736 context736 knowledge736", 18),
        ["angle736", "universe736", "memory736", "stream736", "context736", "knowledge736"],
    ),
    (
        ("angle736 universe736 memory736 stream736 context736 knowledge736", 28),
        ["angle736 universe736", "memory736 stream736", "context736 knowledge736"],
    ),
    (
        ("universe736 memory736 stream736 context736 knowledge736 vector736", 6),
        ["universe736", "memory736", "stream736", "context736", "knowledge736", "vector736"],
    ),
    (
        ("universe736 memory736 stream736 context736 knowledge736 vector736", 10),
        ["universe736", "memory736", "stream736", "context736", "knowledge736", "vector736"],
    ),
    (
        ("universe736 memory736 stream736 context736 knowledge736 vector736", 18),
        ["universe736", "memory736", "stream736", "context736", "knowledge736", "vector736"],
    ),
    (
        ("universe736 memory736 stream736 context736 knowledge736 vector736", 28),
        ["universe736 memory736", "stream736 context736", "knowledge736 vector736"],
    ),
    (
        ("memory736 stream736 context736 knowledge736 vector736 processor736", 6),
        ["memory736", "stream736", "context736", "knowledge736", "vector736", "processor736"],
    ),
    (
        ("memory736 stream736 context736 knowledge736 vector736 processor736", 10),
        ["memory736", "stream736", "context736", "knowledge736", "vector736", "processor736"],
    ),
    (
        ("memory736 stream736 context736 knowledge736 vector736 processor736", 18),
        ["memory736", "stream736", "context736", "knowledge736", "vector736", "processor736"],
    ),
    (
        ("memory736 stream736 context736 knowledge736 vector736 processor736", 28),
        ["memory736 stream736", "context736 knowledge736", "vector736 processor736"],
    ),
    (
        ("stream736 context736 knowledge736 vector736 processor736 reasoning736", 6),
        ["stream736", "context736", "knowledge736", "vector736", "processor736", "reasoning736"],
    ),
    (
        ("stream736 context736 knowledge736 vector736 processor736 reasoning736", 10),
        ["stream736", "context736", "knowledge736", "vector736", "processor736", "reasoning736"],
    ),
    (
        ("stream736 context736 knowledge736 vector736 processor736 reasoning736", 18),
        ["stream736", "context736", "knowledge736", "vector736", "processor736", "reasoning736"],
    ),
    (
        ("stream736 context736 knowledge736 vector736 processor736 reasoning736", 28),
        ["stream736 context736", "knowledge736 vector736", "processor736 reasoning736"],
    ),
    (
        ("context736 knowledge736 vector736 processor736 reasoning736 machine736", 6),
        ["context736", "knowledge736", "vector736", "processor736", "reasoning736", "machine736"],
    ),
    (
        ("context736 knowledge736 vector736 processor736 reasoning736 machine736", 10),
        ["context736", "knowledge736", "vector736", "processor736", "reasoning736", "machine736"],
    ),
    (
        ("context736 knowledge736 vector736 processor736 reasoning736 machine736", 18),
        ["context736", "knowledge736", "vector736", "processor736", "reasoning736", "machine736"],
    ),
    (
        ("context736 knowledge736 vector736 processor736 reasoning736 machine736", 28),
        ["context736 knowledge736", "vector736 processor736", "reasoning736 machine736"],
    ),
    (
        ("knowledge736 vector736 processor736 reasoning736 machine736 learning736", 6),
        ["knowledge736", "vector736", "processor736", "reasoning736", "machine736", "learning736"],
    ),
    (
        ("knowledge736 vector736 processor736 reasoning736 machine736 learning736", 10),
        ["knowledge736", "vector736", "processor736", "reasoning736", "machine736", "learning736"],
    ),
    (
        ("knowledge736 vector736 processor736 reasoning736 machine736 learning736", 18),
        ["knowledge736", "vector736", "processor736", "reasoning736", "machine736", "learning736"],
    ),
    (
        ("knowledge736 vector736 processor736 reasoning736 machine736 learning736", 28),
        ["knowledge736 vector736", "processor736 reasoning736", "machine736 learning736"],
    ),
    (
        ("vector736 processor736 reasoning736 machine736 learning736 model736", 6),
        ["vector736", "processor736", "reasoning736", "machine736", "learning736", "model736"],
    ),
    (
        ("vector736 processor736 reasoning736 machine736 learning736 model736", 10),
        ["vector736", "processor736", "reasoning736", "machine736", "learning736", "model736"],
    ),
    (
        ("vector736 processor736 reasoning736 machine736 learning736 model736", 18),
        ["vector736", "processor736", "reasoning736", "machine736", "learning736", "model736"],
    ),
    (
        ("vector736 processor736 reasoning736 machine736 learning736 model736", 28),
        ["vector736 processor736", "reasoning736 machine736", "learning736 model736"],
    ),
    (
        ("processor736 reasoning736 machine736 learning736 model736 token736", 6),
        ["processor736", "reasoning736", "machine736", "learning736", "model736", "token736"],
    ),
    (
        ("processor736 reasoning736 machine736 learning736 model736 token736", 10),
        ["processor736", "reasoning736", "machine736", "learning736", "model736", "token736"],
    ),
    (
        ("processor736 reasoning736 machine736 learning736 model736 token736", 18),
        ["processor736", "reasoning736", "machine736", "learning736", "model736 token736"],
    ),
    (
        ("processor736 reasoning736 machine736 learning736 model736 token736", 28),
        ["processor736 reasoning736", "machine736 learning736", "model736 token736"],
    ),
    (
        ("reasoning736 machine736 learning736 model736 token736 prompt736", 6),
        ["reasoning736", "machine736", "learning736", "model736", "token736", "prompt736"],
    ),
    (
        ("reasoning736 machine736 learning736 model736 token736 prompt736", 10),
        ["reasoning736", "machine736", "learning736", "model736", "token736", "prompt736"],
    ),
    (
        ("reasoning736 machine736 learning736 model736 token736 prompt736", 18),
        ["reasoning736", "machine736", "learning736", "model736 token736", "prompt736"],
    ),
    (
        ("reasoning736 machine736 learning736 model736 token736 prompt736", 28),
        ["reasoning736 machine736", "learning736 model736", "token736 prompt736"],
    ),
    (
        ("machine736 learning736 model736 token736 prompt736 session736", 6),
        ["machine736", "learning736", "model736", "token736", "prompt736", "session736"],
    ),
    (
        ("machine736 learning736 model736 token736 prompt736 session736", 10),
        ["machine736", "learning736", "model736", "token736", "prompt736", "session736"],
    ),
    (
        ("machine736 learning736 model736 token736 prompt736 session736", 18),
        ["machine736", "learning736", "model736 token736", "prompt736", "session736"],
    ),
    (
        ("machine736 learning736 model736 token736 prompt736 session736", 28),
        ["machine736 learning736", "model736 token736 prompt736", "session736"],
    ),
    (
        ("learning736 model736 token736 prompt736 session736 library736", 6),
        ["learning736", "model736", "token736", "prompt736", "session736", "library736"],
    ),
    (
        ("learning736 model736 token736 prompt736 session736 library736", 10),
        ["learning736", "model736", "token736", "prompt736", "session736", "library736"],
    ),
    (
        ("learning736 model736 token736 prompt736 session736 library736", 18),
        ["learning736", "model736 token736", "prompt736", "session736", "library736"],
    ),
    (
        ("learning736 model736 token736 prompt736 session736 library736", 28),
        ["learning736 model736", "token736 prompt736", "session736 library736"],
    ),
    (
        ("model736 token736 prompt736 session736 library736 service736", 6),
        ["model736", "token736", "prompt736", "session736", "library736", "service736"],
    ),
    (
        ("model736 token736 prompt736 session736 library736 service736", 10),
        ["model736", "token736", "prompt736", "session736", "library736", "service736"],
    ),
    (
        ("model736 token736 prompt736 session736 library736 service736", 18),
        ["model736 token736", "prompt736", "session736", "library736", "service736"],
    ),
    (
        ("model736 token736 prompt736 session736 library736 service736", 28),
        ["model736 token736 prompt736", "session736 library736", "service736"],
    ),
    (
        ("token736 prompt736 session736 library736 service736 gateway736", 6),
        ["token736", "prompt736", "session736", "library736", "service736", "gateway736"],
    ),
    (
        ("token736 prompt736 session736 library736 service736 gateway736", 10),
        ["token736", "prompt736", "session736", "library736", "service736", "gateway736"],
    ),
    (
        ("token736 prompt736 session736 library736 service736 gateway736", 18),
        ["token736 prompt736", "session736", "library736", "service736", "gateway736"],
    ),
    (
        ("token736 prompt736 session736 library736 service736 gateway736", 28),
        ["token736 prompt736", "session736 library736", "service736 gateway736"],
    ),
    (
        ("prompt736 session736 library736 service736 gateway736 storage736", 6),
        ["prompt736", "session736", "library736", "service736", "gateway736", "storage736"],
    ),
    (
        ("prompt736 session736 library736 service736 gateway736 storage736", 10),
        ["prompt736", "session736", "library736", "service736", "gateway736", "storage736"],
    ),
    (
        ("prompt736 session736 library736 service736 gateway736 storage736", 18),
        ["prompt736", "session736", "library736", "service736", "gateway736", "storage736"],
    ),
    (
        ("prompt736 session736 library736 service736 gateway736 storage736", 28),
        ["prompt736 session736", "library736 service736", "gateway736 storage736"],
    ),
    (
        ("session736 library736 service736 gateway736 storage736 network736", 6),
        ["session736", "library736", "service736", "gateway736", "storage736", "network736"],
    ),
    (
        ("session736 library736 service736 gateway736 storage736 network736", 10),
        ["session736", "library736", "service736", "gateway736", "storage736", "network736"],
    ),
    (
        ("session736 library736 service736 gateway736 storage736 network736", 18),
        ["session736", "library736", "service736", "gateway736", "storage736", "network736"],
    ),
    (
        ("session736 library736 service736 gateway736 storage736 network736", 28),
        ["session736 library736", "service736 gateway736", "storage736 network736"],
    ),
    (
        ("library736 service736 gateway736 storage736 network736 latency736", 6),
        ["library736", "service736", "gateway736", "storage736", "network736", "latency736"],
    ),
    (
        ("library736 service736 gateway736 storage736 network736 latency736", 10),
        ["library736", "service736", "gateway736", "storage736", "network736", "latency736"],
    ),
    (
        ("library736 service736 gateway736 storage736 network736 latency736", 18),
        ["library736", "service736", "gateway736", "storage736", "network736", "latency736"],
    ),
    (
        ("library736 service736 gateway736 storage736 network736 latency736", 28),
        ["library736 service736", "gateway736 storage736", "network736 latency736"],
    ),
    (
        ("service736 gateway736 storage736 network736 latency736 buffer736", 6),
        ["service736", "gateway736", "storage736", "network736", "latency736", "buffer736"],
    ),
    (
        ("service736 gateway736 storage736 network736 latency736 buffer736", 10),
        ["service736", "gateway736", "storage736", "network736", "latency736", "buffer736"],
    ),
    (
        ("service736 gateway736 storage736 network736 latency736 buffer736", 18),
        ["service736", "gateway736", "storage736", "network736", "latency736", "buffer736"],
    ),
    (
        ("service736 gateway736 storage736 network736 latency736 buffer736", 28),
        ["service736 gateway736", "storage736 network736", "latency736 buffer736"],
    ),
    (
        ("gateway736 storage736 network736 latency736 buffer736 queue736", 6),
        ["gateway736", "storage736", "network736", "latency736", "buffer736", "queue736"],
    ),
    (
        ("gateway736 storage736 network736 latency736 buffer736 queue736", 10),
        ["gateway736", "storage736", "network736", "latency736", "buffer736", "queue736"],
    ),
    (
        ("gateway736 storage736 network736 latency736 buffer736 queue736", 18),
        ["gateway736", "storage736", "network736", "latency736", "buffer736 queue736"],
    ),
    (
        ("gateway736 storage736 network736 latency736 buffer736 queue736", 28),
        ["gateway736 storage736", "network736 latency736", "buffer736 queue736"],
    ),
    (
        ("storage736 network736 latency736 buffer736 queue736 worker736", 6),
        ["storage736", "network736", "latency736", "buffer736", "queue736", "worker736"],
    ),
    (
        ("storage736 network736 latency736 buffer736 queue736 worker736", 10),
        ["storage736", "network736", "latency736", "buffer736", "queue736", "worker736"],
    ),
    (
        ("storage736 network736 latency736 buffer736 queue736 worker736", 18),
        ["storage736", "network736", "latency736", "buffer736 queue736", "worker736"],
    ),
    (
        ("storage736 network736 latency736 buffer736 queue736 worker736", 28),
        ["storage736 network736", "latency736 buffer736", "queue736 worker736"],
    ),
    (
        ("network736 latency736 buffer736 queue736 worker736 kernel736", 6),
        ["network736", "latency736", "buffer736", "queue736", "worker736", "kernel736"],
    ),
    (
        ("network736 latency736 buffer736 queue736 worker736 kernel736", 10),
        ["network736", "latency736", "buffer736", "queue736", "worker736", "kernel736"],
    ),
    (
        ("network736 latency736 buffer736 queue736 worker736 kernel736", 18),
        ["network736", "latency736", "buffer736 queue736", "worker736", "kernel736"],
    ),
    (
        ("network736 latency736 buffer736 queue736 worker736 kernel736", 28),
        ["network736 latency736", "buffer736 queue736 worker736", "kernel736"],
    ),
    (
        ("latency736 buffer736 queue736 worker736 kernel736 signal736", 6),
        ["latency736", "buffer736", "queue736", "worker736", "kernel736", "signal736"],
    ),
    (
        ("latency736 buffer736 queue736 worker736 kernel736 signal736", 10),
        ["latency736", "buffer736", "queue736", "worker736", "kernel736", "signal736"],
    ),
    (
        ("latency736 buffer736 queue736 worker736 kernel736 signal736", 18),
        ["latency736", "buffer736 queue736", "worker736", "kernel736", "signal736"],
    ),
    (
        ("latency736 buffer736 queue736 worker736 kernel736 signal736", 28),
        ["latency736 buffer736", "queue736 worker736 kernel736", "signal736"],
    ),
    (
        ("buffer736 queue736 worker736 kernel736 signal736 packet736", 6),
        ["buffer736", "queue736", "worker736", "kernel736", "signal736", "packet736"],
    ),
    (
        ("buffer736 queue736 worker736 kernel736 signal736 packet736", 10),
        ["buffer736", "queue736", "worker736", "kernel736", "signal736", "packet736"],
    ),
    (
        ("buffer736 queue736 worker736 kernel736 signal736 packet736", 18),
        ["buffer736 queue736", "worker736", "kernel736", "signal736", "packet736"],
    ),
    (
        ("buffer736 queue736 worker736 kernel736 signal736 packet736", 28),
        ["buffer736 queue736 worker736", "kernel736 signal736", "packet736"],
    ),
    (
        ("queue736 worker736 kernel736 signal736 packet736 router736", 6),
        ["queue736", "worker736", "kernel736", "signal736", "packet736", "router736"],
    ),
    (
        ("queue736 worker736 kernel736 signal736 packet736 router736", 10),
        ["queue736", "worker736", "kernel736", "signal736", "packet736", "router736"],
    ),
    (
        ("queue736 worker736 kernel736 signal736 packet736 router736", 18),
        ["queue736 worker736", "kernel736", "signal736", "packet736", "router736"],
    ),
    (
        ("queue736 worker736 kernel736 signal736 packet736 router736", 28),
        ["queue736 worker736 kernel736", "signal736 packet736", "router736"],
    ),
    (
        ("worker736 kernel736 signal736 packet736 router736 cluster736", 6),
        ["worker736", "kernel736", "signal736", "packet736", "router736", "cluster736"],
    ),
    (
        ("worker736 kernel736 signal736 packet736 router736 cluster736", 10),
        ["worker736", "kernel736", "signal736", "packet736", "router736", "cluster736"],
    ),
    (
        ("worker736 kernel736 signal736 packet736 router736 cluster736", 18),
        ["worker736", "kernel736", "signal736", "packet736", "router736", "cluster736"],
    ),
    (
        ("worker736 kernel736 signal736 packet736 router736 cluster736", 28),
        ["worker736 kernel736", "signal736 packet736", "router736 cluster736"],
    ),
    (
        ("kernel736 signal736 packet736 router736 cluster736 mirror736", 6),
        ["kernel736", "signal736", "packet736", "router736", "cluster736", "mirror736"],
    ),
    (
        ("kernel736 signal736 packet736 router736 cluster736 mirror736", 10),
        ["kernel736", "signal736", "packet736", "router736", "cluster736", "mirror736"],
    ),
    (
        ("kernel736 signal736 packet736 router736 cluster736 mirror736", 18),
        ["kernel736", "signal736", "packet736", "router736", "cluster736", "mirror736"],
    ),
    (
        ("kernel736 signal736 packet736 router736 cluster736 mirror736", 28),
        ["kernel736 signal736", "packet736 router736", "cluster736 mirror736"],
    ),
    (
        ("signal736 packet736 router736 cluster736 mirror736 filter736", 6),
        ["signal736", "packet736", "router736", "cluster736", "mirror736", "filter736"],
    ),
    (
        ("signal736 packet736 router736 cluster736 mirror736 filter736", 10),
        ["signal736", "packet736", "router736", "cluster736", "mirror736", "filter736"],
    ),
    (
        ("signal736 packet736 router736 cluster736 mirror736 filter736", 18),
        ["signal736", "packet736", "router736", "cluster736", "mirror736", "filter736"],
    ),
    (
        ("signal736 packet736 router736 cluster736 mirror736 filter736", 28),
        ["signal736 packet736", "router736 cluster736", "mirror736 filter736"],
    ),
    (
        ("packet736 router736 cluster736 mirror736 filter736 ranking736", 6),
        ["packet736", "router736", "cluster736", "mirror736", "filter736", "ranking736"],
    ),
    (
        ("packet736 router736 cluster736 mirror736 filter736 ranking736", 10),
        ["packet736", "router736", "cluster736", "mirror736", "filter736", "ranking736"],
    ),
    (
        ("packet736 router736 cluster736 mirror736 filter736 ranking736", 18),
        ["packet736", "router736", "cluster736", "mirror736", "filter736", "ranking736"],
    ),
    (
        ("packet736 router736 cluster736 mirror736 filter736 ranking736", 28),
        ["packet736 router736", "cluster736 mirror736", "filter736 ranking736"],
    ),
    (
        ("router736 cluster736 mirror736 filter736 ranking736 encoding736", 6),
        ["router736", "cluster736", "mirror736", "filter736", "ranking736", "encoding736"],
    ),
    (
        ("router736 cluster736 mirror736 filter736 ranking736 encoding736", 10),
        ["router736", "cluster736", "mirror736", "filter736", "ranking736", "encoding736"],
    ),
    (
        ("router736 cluster736 mirror736 filter736 ranking736 encoding736", 18),
        ["router736", "cluster736", "mirror736", "filter736", "ranking736", "encoding736"],
    ),
    (
        ("router736 cluster736 mirror736 filter736 ranking736 encoding736", 28),
        ["router736 cluster736", "mirror736 filter736", "ranking736 encoding736"],
    ),
    (
        ("cluster736 mirror736 filter736 ranking736 encoding736 mapping736", 6),
        ["cluster736", "mirror736", "filter736", "ranking736", "encoding736", "mapping736"],
    ),
    (
        ("cluster736 mirror736 filter736 ranking736 encoding736 mapping736", 10),
        ["cluster736", "mirror736", "filter736", "ranking736", "encoding736", "mapping736"],
    ),
    (
        ("cluster736 mirror736 filter736 ranking736 encoding736 mapping736", 18),
        ["cluster736", "mirror736", "filter736", "ranking736", "encoding736", "mapping736"],
    ),
    (
        ("cluster736 mirror736 filter736 ranking736 encoding736 mapping736", 28),
        ["cluster736 mirror736", "filter736 ranking736", "encoding736 mapping736"],
    ),
    (
        ("mirror736 filter736 ranking736 encoding736 mapping736 record736", 6),
        ["mirror736", "filter736", "ranking736", "encoding736", "mapping736", "record736"],
    ),
    (
        ("mirror736 filter736 ranking736 encoding736 mapping736 record736", 10),
        ["mirror736", "filter736", "ranking736", "encoding736", "mapping736", "record736"],
    ),
    (
        ("mirror736 filter736 ranking736 encoding736 mapping736 record736", 18),
        ["mirror736", "filter736", "ranking736", "encoding736", "mapping736", "record736"],
    ),
    (
        ("mirror736 filter736 ranking736 encoding736 mapping736 record736", 28),
        ["mirror736 filter736", "ranking736 encoding736", "mapping736 record736"],
    ),
    (
        ("filter736 ranking736 encoding736 mapping736 record736 candle736", 6),
        ["filter736", "ranking736", "encoding736", "mapping736", "record736", "candle736"],
    ),
    (
        ("filter736 ranking736 encoding736 mapping736 record736 candle736", 10),
        ["filter736", "ranking736", "encoding736", "mapping736", "record736", "candle736"],
    ),
    (
        ("filter736 ranking736 encoding736 mapping736 record736 candle736", 18),
        ["filter736", "ranking736", "encoding736", "mapping736", "record736", "candle736"],
    ),
    (
        ("filter736 ranking736 encoding736 mapping736 record736 candle736", 28),
        ["filter736 ranking736", "encoding736 mapping736", "record736 candle736"],
    ),
    (
        ("ranking736 encoding736 mapping736 record736 candle736 thread736", 6),
        ["ranking736", "encoding736", "mapping736", "record736", "candle736", "thread736"],
    ),
    (
        ("ranking736 encoding736 mapping736 record736 candle736 thread736", 10),
        ["ranking736", "encoding736", "mapping736", "record736", "candle736", "thread736"],
    ),
    (
        ("ranking736 encoding736 mapping736 record736 candle736 thread736", 18),
        ["ranking736", "encoding736", "mapping736", "record736", "candle736", "thread736"],
    ),
    (
        ("ranking736 encoding736 mapping736 record736 candle736 thread736", 28),
        ["ranking736 encoding736", "mapping736 record736", "candle736 thread736"],
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
