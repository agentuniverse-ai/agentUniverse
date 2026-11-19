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
        ("round 74: the quick brown fox jumps over the lazy dog", 4),
        ["round", "74:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 74: the quick brown fox jumps over the lazy dog", 8),
        ["round", "74: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 74: the quick brown fox jumps over the lazy dog", 12),
        ["round 74:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 74: the quick brown fox jumps over the lazy dog", 16),
        ["round 74: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 74: the quick brown fox jumps over the lazy dog", 24),
        ["round 74: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 74: the quick brown fox jumps over the lazy dog", 32),
        ["round 74: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 74: agentuniverse is a framework for multi agents", 4),
        ["round", "74:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 74: agentuniverse is a framework for multi agents", 8),
        ["round", "74:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 74: agentuniverse is a framework for multi agents", 12),
        ["round 74:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 74: agentuniverse is a framework for multi agents", 16),
        ["round 74:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 74: agentuniverse is a framework for multi agents", 24),
        ["round 74: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 74: agentuniverse is a framework for multi agents", 32),
        ["round 74: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 74: knowledge stored as vectors enables retrieval", 4),
        ["round", "74:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 74: knowledge stored as vectors enables retrieval", 8),
        ["round", "74:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 74: knowledge stored as vectors enables retrieval", 12),
        ["round 74:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 74: knowledge stored as vectors enables retrieval", 16),
        ["round 74:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 74: knowledge stored as vectors enables retrieval", 24),
        ["round 74: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 74: knowledge stored as vectors enables retrieval", 32),
        ["round 74: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 74: the processor reads the record then stops", 4),
        ["round", "74:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 74: the processor reads the record then stops", 8),
        ["round", "74: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 74: the processor reads the record then stops", 12),
        ["round 74:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 74: the processor reads the record then stops", 16),
        ["round 74: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 74: the processor reads the record then stops", 24),
        ["round 74: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 74: the processor reads the record then stops", 32),
        ["round 74: the processor reads", "the record then stops"],
    ),
    (
        ("round 74: a worker pulls the next task from the queue", 4),
        ["round", "74:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 74: a worker pulls the next task from the queue", 8),
        ["round", "74: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 74: a worker pulls the next task from the queue", 12),
        ["round 74: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 74: a worker pulls the next task from the queue", 16),
        ["round 74: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 74: a worker pulls the next task from the queue", 24),
        ["round 74: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 74: a worker pulls the next task from the queue", 32),
        ["round 74: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 74: signals travel through the network layer", 4),
        ["round", "74:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 74: signals travel through the network layer", 8),
        ["round", "74:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 74: signals travel through the network layer", 12),
        ["round 74:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 74: signals travel through the network layer", 16),
        ["round 74:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 74: signals travel through the network layer", 24),
        ["round 74: signals travel", "through the network", "layer"],
    ),
    (
        ("round 74: signals travel through the network layer", 32),
        ["round 74: signals travel through", "the network layer"],
    ),
    (
        ("round 74: the gateway routes each request by policy", 4),
        ["round", "74:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 74: the gateway routes each request by policy", 8),
        ["round", "74: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 74: the gateway routes each request by policy", 12),
        ["round 74:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 74: the gateway routes each request by policy", 16),
        ["round 74: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 74: the gateway routes each request by policy", 24),
        ["round 74: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 74: the gateway routes each request by policy", 32),
        ["round 74: the gateway routes", "each request by policy"],
    ),
    (
        ("round 74: memory grows until the buffer is full", 4),
        ["round", "74:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 74: memory grows until the buffer is full", 8),
        ["round", "74:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 74: memory grows until the buffer is full", 12),
        ["round 74:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 74: memory grows until the buffer is full", 16),
        ["round 74: memory", "grows until the", "buffer is full"],
    ),
    (("round 74: memory grows until the buffer is full", 24), ["round 74: memory grows", "until the buffer is full"]),
    (("round 74: memory grows until the buffer is full", 32), ["round 74: memory grows until the", "buffer is full"]),
    (
        ("round 74: the cluster mirrors every packet twice", 4),
        ["round", "74:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 74: the cluster mirrors every packet twice", 8),
        ["round", "74: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 74: the cluster mirrors every packet twice", 12),
        ["round 74:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 74: the cluster mirrors every packet twice", 16),
        ["round 74: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 74: the cluster mirrors every packet twice", 24),
        ["round 74: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 74: the cluster mirrors every packet twice", 32), ["round 74: the cluster mirrors", "every packet twice"]),
    (
        ("round 74: ranking uses tokens learned from the corpus", 4),
        ["round", "74:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 74: ranking uses tokens learned from the corpus", 8),
        ["round", "74:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 74: ranking uses tokens learned from the corpus", 12),
        ["round 74:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 74: ranking uses tokens learned from the corpus", 16),
        ["round 74:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 74: ranking uses tokens learned from the corpus", 24),
        ["round 74: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 74: ranking uses tokens learned from the corpus", 32),
        ["round 74: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 74: a long session ends when the candle dies", 4),
        ["round", "74:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 74: a long session ends when the candle dies", 8),
        ["round", "74: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 74: a long session ends when the candle dies", 12),
        ["round 74: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 74: a long session ends when the candle dies", 16),
        ["round 74: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 74: a long session ends when the candle dies", 24),
        ["round 74: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 74: a long session ends when the candle dies", 32),
        ["round 74: a long session ends", "when the candle dies"],
    ),
    (
        ("round 74: encode the prompt then map the result", 4),
        ["round", "74:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 74: encode the prompt then map the result", 8),
        ["round", "74:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 74: encode the prompt then map the result", 12),
        ["round 74:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 74: encode the prompt then map the result", 16),
        ["round 74: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 74: encode the prompt then map the result", 24),
        ["round 74: encode the", "prompt then map the", "result"],
    ),
    (("round 74: encode the prompt then map the result", 32), ["round 74: encode the prompt then", "map the result"]),
    (
        ("round 74: the kernel wakes the worker at dawn", 4),
        ["round", "74:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 74: the kernel wakes the worker at dawn", 8),
        ["round", "74: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 74: the kernel wakes the worker at dawn", 12),
        ["round 74:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 74: the kernel wakes the worker at dawn", 16), ["round 74: the", "kernel wakes the", "worker at dawn"]),
    (("round 74: the kernel wakes the worker at dawn", 24), ["round 74: the kernel", "wakes the worker at dawn"]),
    (("round 74: the kernel wakes the worker at dawn", 32), ["round 74: the kernel wakes the", "worker at dawn"]),
    (
        ("round 74: service latency drops after the patch", 4),
        ["round", "74:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 74: service latency drops after the patch", 8),
        ["round", "74:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 74: service latency drops after the patch", 12),
        ["round 74:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 74: service latency drops after the patch", 16),
        ["round 74:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 74: service latency drops after the patch", 24),
        ["round 74: service", "latency drops after the", "patch"],
    ),
    (("round 74: service latency drops after the patch", 32), ["round 74: service latency drops", "after the patch"]),
    (
        ("round 74: the library caches every vector it sees", 4),
        ["round", "74:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 74: the library caches every vector it sees", 8),
        ["round", "74: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 74: the library caches every vector it sees", 12),
        ["round 74:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 74: the library caches every vector it sees", 16),
        ["round 74: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 74: the library caches every vector it sees", 24),
        ["round 74: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 74: the library caches every vector it sees", 32),
        ["round 74: the library caches", "every vector it sees"],
    ),
    (
        ("round 74: agents argue then the debate resolves", 4),
        ["round", "74:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 74: agents argue then the debate resolves", 8),
        ["round", "74:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 74: agents argue then the debate resolves", 12),
        ["round 74:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 74: agents argue then the debate resolves", 16),
        ["round 74: agents", "argue then the", "debate resolves"],
    ),
    (("round 74: agents argue then the debate resolves", 24), ["round 74: agents argue", "then the debate resolves"]),
    (("round 74: agents argue then the debate resolves", 32), ["round 74: agents argue then the", "debate resolves"]),
    (
        ("round 74: the filter keeps only strong matches", 4),
        ["round", "74:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 74: the filter keeps only strong matches", 8),
        ["round", "74: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 74: the filter keeps only strong matches", 12),
        ["round 74:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 74: the filter keeps only strong matches", 16),
        ["round 74: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 74: the filter keeps only strong matches", 24), ["round 74: the filter", "keeps only strong", "matches"]),
    (("round 74: the filter keeps only strong matches", 32), ["round 74: the filter keeps only", "strong matches"]),
    (
        ("round 74: the model answers with a short reply", 4),
        ["round", "74:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 74: the model answers with a short reply", 8),
        ["round", "74: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 74: the model answers with a short reply", 12),
        ["round 74:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 74: the model answers with a short reply", 16),
        ["round 74: the", "model answers", "with a short", "reply"],
    ),
    (("round 74: the model answers with a short reply", 24), ["round 74: the model", "answers with a short", "reply"]),
    (("round 74: the model answers with a short reply", 32), ["round 74: the model answers with", "a short reply"]),
    (
        ("round 74: the recorder stores the reasoning trace", 4),
        ["round", "74:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 74: the recorder stores the reasoning trace", 8),
        ["round", "74: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 74: the recorder stores the reasoning trace", 12),
        ["round 74:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 74: the recorder stores the reasoning trace", 16),
        ["round 74: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 74: the recorder stores the reasoning trace", 24),
        ["round 74: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 74: the recorder stores the reasoning trace", 32),
        ["round 74: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 74: the angel watches the processor run", 4),
        ["round", "74:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 74: the angel watches the processor run", 8),
        ["round", "74: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 74: the angel watches the processor run", 12),
        ["round 74:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 74: the angel watches the processor run", 16), ["round 74: the", "angel watches", "the processor", "run"]),
    (("round 74: the angel watches the processor run", 24), ["round 74: the angel", "watches the processor", "run"]),
    (("round 74: the angel watches the processor run", 32), ["round 74: the angel watches the", "processor run"]),
    (
        ("round 74: angle of the vector decides the match", 4),
        ["round", "74:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 74: angle of the vector decides the match", 8),
        ["round", "74:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 74: angle of the vector decides the match", 12),
        ["round 74:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 74: angle of the vector decides the match", 16),
        ["round 74: angle", "of the vector", "decides the", "match"],
    ),
    (("round 74: angle of the vector decides the match", 24), ["round 74: angle of the", "vector decides the match"]),
    (("round 74: angle of the vector decides the match", 32), ["round 74: angle of the vector", "decides the match"]),
    (
        ("round 74: the candle burns twice as long at night", 4),
        ["round", "74:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 74: the candle burns twice as long at night", 8),
        ["round", "74: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 74: the candle burns twice as long at night", 12),
        ["round 74:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 74: the candle burns twice as long at night", 16),
        ["round 74: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 74: the candle burns twice as long at night", 24),
        ["round 74: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 74: the candle burns twice as long at night", 32),
        ["round 74: the candle burns twice", "as long at night"],
    ),
    (
        ("round 74: a mirror of the universe in one line", 4),
        ["round", "74:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 74: a mirror of the universe in one line", 8),
        ["round", "74: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 74: a mirror of the universe in one line", 12),
        ["round 74: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 74: a mirror of the universe in one line", 16),
        ["round 74: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 74: a mirror of the universe in one line", 24), ["round 74: a mirror of", "the universe in one line"]),
    (("round 74: a mirror of the universe in one line", 32), ["round 74: a mirror of the", "universe in one line"]),
    (
        ("round 74: the queue drains before the storm", 4),
        ["round", "74:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 74: the queue drains before the storm", 8),
        ["round", "74: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 74: the queue drains before the storm", 12), ["round 74:", "the queue", "drains", "before the", "storm"]),
    (("round 74: the queue drains before the storm", 16), ["round 74: the", "queue drains", "before the storm"]),
    (("round 74: the queue drains before the storm", 24), ["round 74: the queue", "drains before the storm"]),
    (("round 74: the queue drains before the storm", 32), ["round 74: the queue drains", "before the storm"]),
    (
        ("kitten74 sitting74 agent74 angle74 universe74 memory74", 6),
        ["kitten74", "sitting74", "agent74", "angle74", "universe74", "memory74"],
    ),
    (
        ("kitten74 sitting74 agent74 angle74 universe74 memory74", 10),
        ["kitten74", "sitting74", "agent74", "angle74", "universe74", "memory74"],
    ),
    (
        ("kitten74 sitting74 agent74 angle74 universe74 memory74", 18),
        ["kitten74 sitting74", "agent74 angle74", "universe74", "memory74"],
    ),
    (
        ("kitten74 sitting74 agent74 angle74 universe74 memory74", 28),
        ["kitten74 sitting74 agent74", "angle74 universe74 memory74"],
    ),
    (
        ("sitting74 agent74 angle74 universe74 memory74 stream74", 6),
        ["sitting74", "agent74", "angle74", "universe74", "memory74", "stream74"],
    ),
    (
        ("sitting74 agent74 angle74 universe74 memory74 stream74", 10),
        ["sitting74", "agent74", "angle74", "universe74", "memory74", "stream74"],
    ),
    (
        ("sitting74 agent74 angle74 universe74 memory74 stream74", 18),
        ["sitting74 agent74", "angle74 universe74", "memory74 stream74"],
    ),
    (
        ("sitting74 agent74 angle74 universe74 memory74 stream74", 28),
        ["sitting74 agent74 angle74", "universe74 memory74 stream74"],
    ),
    (
        ("agent74 angle74 universe74 memory74 stream74 context74", 6),
        ["agent74", "angle74", "universe74", "memory74", "stream74", "context74"],
    ),
    (
        ("agent74 angle74 universe74 memory74 stream74 context74", 10),
        ["agent74", "angle74", "universe74", "memory74", "stream74", "context74"],
    ),
    (
        ("agent74 angle74 universe74 memory74 stream74 context74", 18),
        ["agent74 angle74", "universe74", "memory74 stream74", "context74"],
    ),
    (
        ("agent74 angle74 universe74 memory74 stream74 context74", 28),
        ["agent74 angle74 universe74", "memory74 stream74 context74"],
    ),
    (
        ("angle74 universe74 memory74 stream74 context74 knowledge74", 6),
        ["angle74", "universe74", "memory74", "stream74", "context74", "knowledge74"],
    ),
    (
        ("angle74 universe74 memory74 stream74 context74 knowledge74", 10),
        ["angle74", "universe74", "memory74", "stream74", "context74", "knowledge74"],
    ),
    (
        ("angle74 universe74 memory74 stream74 context74 knowledge74", 18),
        ["angle74 universe74", "memory74 stream74", "context74", "knowledge74"],
    ),
    (
        ("angle74 universe74 memory74 stream74 context74 knowledge74", 28),
        ["angle74 universe74 memory74", "stream74 context74", "knowledge74"],
    ),
    (
        ("universe74 memory74 stream74 context74 knowledge74 vector74", 6),
        ["universe74", "memory74", "stream74", "context74", "knowledge74", "vector74"],
    ),
    (
        ("universe74 memory74 stream74 context74 knowledge74 vector74", 10),
        ["universe74", "memory74", "stream74", "context74", "knowledge74", "vector74"],
    ),
    (
        ("universe74 memory74 stream74 context74 knowledge74 vector74", 18),
        ["universe74", "memory74 stream74", "context74", "knowledge74", "vector74"],
    ),
    (
        ("universe74 memory74 stream74 context74 knowledge74 vector74", 28),
        ["universe74 memory74 stream74", "context74 knowledge74", "vector74"],
    ),
    (
        ("memory74 stream74 context74 knowledge74 vector74 processor74", 6),
        ["memory74", "stream74", "context74", "knowledge74", "vector74", "processor74"],
    ),
    (
        ("memory74 stream74 context74 knowledge74 vector74 processor74", 10),
        ["memory74", "stream74", "context74", "knowledge74", "vector74", "processor74"],
    ),
    (
        ("memory74 stream74 context74 knowledge74 vector74 processor74", 18),
        ["memory74 stream74", "context74", "knowledge74", "vector74", "processor74"],
    ),
    (
        ("memory74 stream74 context74 knowledge74 vector74 processor74", 28),
        ["memory74 stream74 context74", "knowledge74 vector74", "processor74"],
    ),
    (
        ("stream74 context74 knowledge74 vector74 processor74 reasoning74", 6),
        ["stream74", "context74", "knowledge74", "vector74", "processor74", "reasoning74"],
    ),
    (
        ("stream74 context74 knowledge74 vector74 processor74 reasoning74", 10),
        ["stream74", "context74", "knowledge74", "vector74", "processor74", "reasoning74"],
    ),
    (
        ("stream74 context74 knowledge74 vector74 processor74 reasoning74", 18),
        ["stream74 context74", "knowledge74", "vector74", "processor74", "reasoning74"],
    ),
    (
        ("stream74 context74 knowledge74 vector74 processor74 reasoning74", 28),
        ["stream74 context74", "knowledge74 vector74", "processor74 reasoning74"],
    ),
    (
        ("context74 knowledge74 vector74 processor74 reasoning74 machine74", 6),
        ["context74", "knowledge74", "vector74", "processor74", "reasoning74", "machine74"],
    ),
    (
        ("context74 knowledge74 vector74 processor74 reasoning74 machine74", 10),
        ["context74", "knowledge74", "vector74", "processor74", "reasoning74", "machine74"],
    ),
    (
        ("context74 knowledge74 vector74 processor74 reasoning74 machine74", 18),
        ["context74", "knowledge74", "vector74", "processor74", "reasoning74", "machine74"],
    ),
    (
        ("context74 knowledge74 vector74 processor74 reasoning74 machine74", 28),
        ["context74 knowledge74", "vector74 processor74", "reasoning74 machine74"],
    ),
    (
        ("knowledge74 vector74 processor74 reasoning74 machine74 learning74", 6),
        ["knowledge74", "vector74", "processor74", "reasoning74", "machine74", "learning74"],
    ),
    (
        ("knowledge74 vector74 processor74 reasoning74 machine74 learning74", 10),
        ["knowledge74", "vector74", "processor74", "reasoning74", "machine74", "learning74"],
    ),
    (
        ("knowledge74 vector74 processor74 reasoning74 machine74 learning74", 18),
        ["knowledge74", "vector74", "processor74", "reasoning74", "machine74", "learning74"],
    ),
    (
        ("knowledge74 vector74 processor74 reasoning74 machine74 learning74", 28),
        ["knowledge74 vector74", "processor74 reasoning74", "machine74 learning74"],
    ),
    (
        ("vector74 processor74 reasoning74 machine74 learning74 model74", 6),
        ["vector74", "processor74", "reasoning74", "machine74", "learning74", "model74"],
    ),
    (
        ("vector74 processor74 reasoning74 machine74 learning74 model74", 10),
        ["vector74", "processor74", "reasoning74", "machine74", "learning74", "model74"],
    ),
    (
        ("vector74 processor74 reasoning74 machine74 learning74 model74", 18),
        ["vector74", "processor74", "reasoning74", "machine74", "learning74 model74"],
    ),
    (
        ("vector74 processor74 reasoning74 machine74 learning74 model74", 28),
        ["vector74 processor74", "reasoning74 machine74", "learning74 model74"],
    ),
    (
        ("processor74 reasoning74 machine74 learning74 model74 token74", 6),
        ["processor74", "reasoning74", "machine74", "learning74", "model74", "token74"],
    ),
    (
        ("processor74 reasoning74 machine74 learning74 model74 token74", 10),
        ["processor74", "reasoning74", "machine74", "learning74", "model74", "token74"],
    ),
    (
        ("processor74 reasoning74 machine74 learning74 model74 token74", 18),
        ["processor74", "reasoning74", "machine74", "learning74 model74", "token74"],
    ),
    (
        ("processor74 reasoning74 machine74 learning74 model74 token74", 28),
        ["processor74 reasoning74", "machine74 learning74 model74", "token74"],
    ),
    (
        ("reasoning74 machine74 learning74 model74 token74 prompt74", 6),
        ["reasoning74", "machine74", "learning74", "model74", "token74", "prompt74"],
    ),
    (
        ("reasoning74 machine74 learning74 model74 token74 prompt74", 10),
        ["reasoning74", "machine74", "learning74", "model74", "token74", "prompt74"],
    ),
    (
        ("reasoning74 machine74 learning74 model74 token74 prompt74", 18),
        ["reasoning74", "machine74", "learning74 model74", "token74 prompt74"],
    ),
    (
        ("reasoning74 machine74 learning74 model74 token74 prompt74", 28),
        ["reasoning74 machine74", "learning74 model74 token74", "prompt74"],
    ),
    (
        ("machine74 learning74 model74 token74 prompt74 session74", 6),
        ["machine74", "learning74", "model74", "token74", "prompt74", "session74"],
    ),
    (
        ("machine74 learning74 model74 token74 prompt74 session74", 10),
        ["machine74", "learning74", "model74", "token74", "prompt74", "session74"],
    ),
    (
        ("machine74 learning74 model74 token74 prompt74 session74", 18),
        ["machine74", "learning74 model74", "token74 prompt74", "session74"],
    ),
    (
        ("machine74 learning74 model74 token74 prompt74 session74", 28),
        ["machine74 learning74 model74", "token74 prompt74 session74"],
    ),
    (
        ("learning74 model74 token74 prompt74 session74 library74", 6),
        ["learning74", "model74", "token74", "prompt74", "session74", "library74"],
    ),
    (
        ("learning74 model74 token74 prompt74 session74 library74", 10),
        ["learning74", "model74", "token74", "prompt74", "session74", "library74"],
    ),
    (
        ("learning74 model74 token74 prompt74 session74 library74", 18),
        ["learning74 model74", "token74 prompt74", "session74", "library74"],
    ),
    (
        ("learning74 model74 token74 prompt74 session74 library74", 28),
        ["learning74 model74 token74", "prompt74 session74 library74"],
    ),
    (
        ("model74 token74 prompt74 session74 library74 service74", 6),
        ["model74", "token74", "prompt74", "session74", "library74", "service74"],
    ),
    (
        ("model74 token74 prompt74 session74 library74 service74", 10),
        ["model74", "token74", "prompt74", "session74", "library74", "service74"],
    ),
    (
        ("model74 token74 prompt74 session74 library74 service74", 18),
        ["model74 token74", "prompt74 session74", "library74", "service74"],
    ),
    (
        ("model74 token74 prompt74 session74 library74 service74", 28),
        ["model74 token74 prompt74", "session74 library74", "service74"],
    ),
    (
        ("token74 prompt74 session74 library74 service74 gateway74", 6),
        ["token74", "prompt74", "session74", "library74", "service74", "gateway74"],
    ),
    (
        ("token74 prompt74 session74 library74 service74 gateway74", 10),
        ["token74", "prompt74", "session74", "library74", "service74", "gateway74"],
    ),
    (
        ("token74 prompt74 session74 library74 service74 gateway74", 18),
        ["token74 prompt74", "session74", "library74", "service74", "gateway74"],
    ),
    (
        ("token74 prompt74 session74 library74 service74 gateway74", 28),
        ["token74 prompt74 session74", "library74 service74", "gateway74"],
    ),
    (
        ("prompt74 session74 library74 service74 gateway74 storage74", 6),
        ["prompt74", "session74", "library74", "service74", "gateway74", "storage74"],
    ),
    (
        ("prompt74 session74 library74 service74 gateway74 storage74", 10),
        ["prompt74", "session74", "library74", "service74", "gateway74", "storage74"],
    ),
    (
        ("prompt74 session74 library74 service74 gateway74 storage74", 18),
        ["prompt74 session74", "library74", "service74", "gateway74", "storage74"],
    ),
    (
        ("prompt74 session74 library74 service74 gateway74 storage74", 28),
        ["prompt74 session74 library74", "service74 gateway74", "storage74"],
    ),
    (
        ("session74 library74 service74 gateway74 storage74 network74", 6),
        ["session74", "library74", "service74", "gateway74", "storage74", "network74"],
    ),
    (
        ("session74 library74 service74 gateway74 storage74 network74", 10),
        ["session74", "library74", "service74", "gateway74", "storage74", "network74"],
    ),
    (
        ("session74 library74 service74 gateway74 storage74 network74", 18),
        ["session74", "library74", "service74", "gateway74", "storage74", "network74"],
    ),
    (
        ("session74 library74 service74 gateway74 storage74 network74", 28),
        ["session74 library74", "service74 gateway74", "storage74 network74"],
    ),
    (
        ("library74 service74 gateway74 storage74 network74 latency74", 6),
        ["library74", "service74", "gateway74", "storage74", "network74", "latency74"],
    ),
    (
        ("library74 service74 gateway74 storage74 network74 latency74", 10),
        ["library74", "service74", "gateway74", "storage74", "network74", "latency74"],
    ),
    (
        ("library74 service74 gateway74 storage74 network74 latency74", 18),
        ["library74", "service74", "gateway74", "storage74", "network74", "latency74"],
    ),
    (
        ("library74 service74 gateway74 storage74 network74 latency74", 28),
        ["library74 service74", "gateway74 storage74", "network74 latency74"],
    ),
    (
        ("service74 gateway74 storage74 network74 latency74 buffer74", 6),
        ["service74", "gateway74", "storage74", "network74", "latency74", "buffer74"],
    ),
    (
        ("service74 gateway74 storage74 network74 latency74 buffer74", 10),
        ["service74", "gateway74", "storage74", "network74", "latency74", "buffer74"],
    ),
    (
        ("service74 gateway74 storage74 network74 latency74 buffer74", 18),
        ["service74", "gateway74", "storage74", "network74", "latency74 buffer74"],
    ),
    (
        ("service74 gateway74 storage74 network74 latency74 buffer74", 28),
        ["service74 gateway74", "storage74 network74", "latency74 buffer74"],
    ),
    (
        ("gateway74 storage74 network74 latency74 buffer74 queue74", 6),
        ["gateway74", "storage74", "network74", "latency74", "buffer74", "queue74"],
    ),
    (
        ("gateway74 storage74 network74 latency74 buffer74 queue74", 10),
        ["gateway74", "storage74", "network74", "latency74", "buffer74", "queue74"],
    ),
    (
        ("gateway74 storage74 network74 latency74 buffer74 queue74", 18),
        ["gateway74", "storage74", "network74", "latency74 buffer74", "queue74"],
    ),
    (
        ("gateway74 storage74 network74 latency74 buffer74 queue74", 28),
        ["gateway74 storage74", "network74 latency74 buffer74", "queue74"],
    ),
    (
        ("storage74 network74 latency74 buffer74 queue74 worker74", 6),
        ["storage74", "network74", "latency74", "buffer74", "queue74", "worker74"],
    ),
    (
        ("storage74 network74 latency74 buffer74 queue74 worker74", 10),
        ["storage74", "network74", "latency74", "buffer74", "queue74", "worker74"],
    ),
    (
        ("storage74 network74 latency74 buffer74 queue74 worker74", 18),
        ["storage74", "network74", "latency74 buffer74", "queue74 worker74"],
    ),
    (
        ("storage74 network74 latency74 buffer74 queue74 worker74", 28),
        ["storage74 network74", "latency74 buffer74 queue74", "worker74"],
    ),
    (
        ("network74 latency74 buffer74 queue74 worker74 kernel74", 6),
        ["network74", "latency74", "buffer74", "queue74", "worker74", "kernel74"],
    ),
    (
        ("network74 latency74 buffer74 queue74 worker74 kernel74", 10),
        ["network74", "latency74", "buffer74", "queue74", "worker74", "kernel74"],
    ),
    (
        ("network74 latency74 buffer74 queue74 worker74 kernel74", 18),
        ["network74", "latency74 buffer74", "queue74 worker74", "kernel74"],
    ),
    (
        ("network74 latency74 buffer74 queue74 worker74 kernel74", 28),
        ["network74 latency74 buffer74", "queue74 worker74 kernel74"],
    ),
    (
        ("latency74 buffer74 queue74 worker74 kernel74 signal74", 6),
        ["latency74", "buffer74", "queue74", "worker74", "kernel74", "signal74"],
    ),
    (
        ("latency74 buffer74 queue74 worker74 kernel74 signal74", 10),
        ["latency74", "buffer74", "queue74", "worker74", "kernel74", "signal74"],
    ),
    (
        ("latency74 buffer74 queue74 worker74 kernel74 signal74", 18),
        ["latency74 buffer74", "queue74 worker74", "kernel74 signal74"],
    ),
    (
        ("latency74 buffer74 queue74 worker74 kernel74 signal74", 28),
        ["latency74 buffer74 queue74", "worker74 kernel74 signal74"],
    ),
    (
        ("buffer74 queue74 worker74 kernel74 signal74 packet74", 6),
        ["buffer74", "queue74", "worker74", "kernel74", "signal74", "packet74"],
    ),
    (
        ("buffer74 queue74 worker74 kernel74 signal74 packet74", 10),
        ["buffer74", "queue74", "worker74", "kernel74", "signal74", "packet74"],
    ),
    (
        ("buffer74 queue74 worker74 kernel74 signal74 packet74", 18),
        ["buffer74 queue74", "worker74 kernel74", "signal74 packet74"],
    ),
    (
        ("buffer74 queue74 worker74 kernel74 signal74 packet74", 28),
        ["buffer74 queue74 worker74", "kernel74 signal74 packet74"],
    ),
    (
        ("queue74 worker74 kernel74 signal74 packet74 router74", 6),
        ["queue74", "worker74", "kernel74", "signal74", "packet74", "router74"],
    ),
    (
        ("queue74 worker74 kernel74 signal74 packet74 router74", 10),
        ["queue74", "worker74", "kernel74", "signal74", "packet74", "router74"],
    ),
    (
        ("queue74 worker74 kernel74 signal74 packet74 router74", 18),
        ["queue74 worker74", "kernel74 signal74", "packet74 router74"],
    ),
    (
        ("queue74 worker74 kernel74 signal74 packet74 router74", 28),
        ["queue74 worker74 kernel74", "signal74 packet74 router74"],
    ),
    (
        ("worker74 kernel74 signal74 packet74 router74 cluster74", 6),
        ["worker74", "kernel74", "signal74", "packet74", "router74", "cluster74"],
    ),
    (
        ("worker74 kernel74 signal74 packet74 router74 cluster74", 10),
        ["worker74", "kernel74", "signal74", "packet74", "router74", "cluster74"],
    ),
    (
        ("worker74 kernel74 signal74 packet74 router74 cluster74", 18),
        ["worker74 kernel74", "signal74 packet74", "router74 cluster74"],
    ),
    (
        ("worker74 kernel74 signal74 packet74 router74 cluster74", 28),
        ["worker74 kernel74 signal74", "packet74 router74 cluster74"],
    ),
    (
        ("kernel74 signal74 packet74 router74 cluster74 mirror74", 6),
        ["kernel74", "signal74", "packet74", "router74", "cluster74", "mirror74"],
    ),
    (
        ("kernel74 signal74 packet74 router74 cluster74 mirror74", 10),
        ["kernel74", "signal74", "packet74", "router74", "cluster74", "mirror74"],
    ),
    (
        ("kernel74 signal74 packet74 router74 cluster74 mirror74", 18),
        ["kernel74 signal74", "packet74 router74", "cluster74 mirror74"],
    ),
    (
        ("kernel74 signal74 packet74 router74 cluster74 mirror74", 28),
        ["kernel74 signal74 packet74", "router74 cluster74 mirror74"],
    ),
    (
        ("signal74 packet74 router74 cluster74 mirror74 filter74", 6),
        ["signal74", "packet74", "router74", "cluster74", "mirror74", "filter74"],
    ),
    (
        ("signal74 packet74 router74 cluster74 mirror74 filter74", 10),
        ["signal74", "packet74", "router74", "cluster74", "mirror74", "filter74"],
    ),
    (
        ("signal74 packet74 router74 cluster74 mirror74 filter74", 18),
        ["signal74 packet74", "router74 cluster74", "mirror74 filter74"],
    ),
    (
        ("signal74 packet74 router74 cluster74 mirror74 filter74", 28),
        ["signal74 packet74 router74", "cluster74 mirror74 filter74"],
    ),
    (
        ("packet74 router74 cluster74 mirror74 filter74 ranking74", 6),
        ["packet74", "router74", "cluster74", "mirror74", "filter74", "ranking74"],
    ),
    (
        ("packet74 router74 cluster74 mirror74 filter74 ranking74", 10),
        ["packet74", "router74", "cluster74", "mirror74", "filter74", "ranking74"],
    ),
    (
        ("packet74 router74 cluster74 mirror74 filter74 ranking74", 18),
        ["packet74 router74", "cluster74 mirror74", "filter74 ranking74"],
    ),
    (
        ("packet74 router74 cluster74 mirror74 filter74 ranking74", 28),
        ["packet74 router74 cluster74", "mirror74 filter74 ranking74"],
    ),
    (
        ("router74 cluster74 mirror74 filter74 ranking74 encoding74", 6),
        ["router74", "cluster74", "mirror74", "filter74", "ranking74", "encoding74"],
    ),
    (
        ("router74 cluster74 mirror74 filter74 ranking74 encoding74", 10),
        ["router74", "cluster74", "mirror74", "filter74", "ranking74", "encoding74"],
    ),
    (
        ("router74 cluster74 mirror74 filter74 ranking74 encoding74", 18),
        ["router74 cluster74", "mirror74 filter74", "ranking74", "encoding74"],
    ),
    (
        ("router74 cluster74 mirror74 filter74 ranking74 encoding74", 28),
        ["router74 cluster74 mirror74", "filter74 ranking74", "encoding74"],
    ),
    (
        ("cluster74 mirror74 filter74 ranking74 encoding74 mapping74", 6),
        ["cluster74", "mirror74", "filter74", "ranking74", "encoding74", "mapping74"],
    ),
    (
        ("cluster74 mirror74 filter74 ranking74 encoding74 mapping74", 10),
        ["cluster74", "mirror74", "filter74", "ranking74", "encoding74", "mapping74"],
    ),
    (
        ("cluster74 mirror74 filter74 ranking74 encoding74 mapping74", 18),
        ["cluster74 mirror74", "filter74 ranking74", "encoding74", "mapping74"],
    ),
    (
        ("cluster74 mirror74 filter74 ranking74 encoding74 mapping74", 28),
        ["cluster74 mirror74 filter74", "ranking74 encoding74", "mapping74"],
    ),
    (
        ("mirror74 filter74 ranking74 encoding74 mapping74 record74", 6),
        ["mirror74", "filter74", "ranking74", "encoding74", "mapping74", "record74"],
    ),
    (
        ("mirror74 filter74 ranking74 encoding74 mapping74 record74", 10),
        ["mirror74", "filter74", "ranking74", "encoding74", "mapping74", "record74"],
    ),
    (
        ("mirror74 filter74 ranking74 encoding74 mapping74 record74", 18),
        ["mirror74 filter74", "ranking74", "encoding74", "mapping74 record74"],
    ),
    (
        ("mirror74 filter74 ranking74 encoding74 mapping74 record74", 28),
        ["mirror74 filter74 ranking74", "encoding74 mapping74", "record74"],
    ),
    (
        ("filter74 ranking74 encoding74 mapping74 record74 candle74", 6),
        ["filter74", "ranking74", "encoding74", "mapping74", "record74", "candle74"],
    ),
    (
        ("filter74 ranking74 encoding74 mapping74 record74 candle74", 10),
        ["filter74", "ranking74", "encoding74", "mapping74", "record74", "candle74"],
    ),
    (
        ("filter74 ranking74 encoding74 mapping74 record74 candle74", 18),
        ["filter74 ranking74", "encoding74", "mapping74 record74", "candle74"],
    ),
    (
        ("filter74 ranking74 encoding74 mapping74 record74 candle74", 28),
        ["filter74 ranking74", "encoding74 mapping74", "record74 candle74"],
    ),
    (
        ("ranking74 encoding74 mapping74 record74 candle74 thread74", 6),
        ["ranking74", "encoding74", "mapping74", "record74", "candle74", "thread74"],
    ),
    (
        ("ranking74 encoding74 mapping74 record74 candle74 thread74", 10),
        ["ranking74", "encoding74", "mapping74", "record74", "candle74", "thread74"],
    ),
    (
        ("ranking74 encoding74 mapping74 record74 candle74 thread74", 18),
        ["ranking74", "encoding74", "mapping74 record74", "candle74 thread74"],
    ),
    (
        ("ranking74 encoding74 mapping74 record74 candle74 thread74", 28),
        ["ranking74 encoding74", "mapping74 record74 candle74", "thread74"],
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
