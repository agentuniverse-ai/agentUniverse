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
        ("round 734: the quick brown fox jumps over the lazy dog", 4),
        ["round", "734:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 734: the quick brown fox jumps over the lazy dog", 8),
        ["round", "734: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 734: the quick brown fox jumps over the lazy dog", 12),
        ["round 734:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 734: the quick brown fox jumps over the lazy dog", 16),
        ["round 734: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 734: the quick brown fox jumps over the lazy dog", 24),
        ["round 734: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 734: the quick brown fox jumps over the lazy dog", 32),
        ["round 734: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 734: agentuniverse is a framework for multi agents", 4),
        ["round", "734:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 734: agentuniverse is a framework for multi agents", 8),
        ["round", "734:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 734: agentuniverse is a framework for multi agents", 12),
        ["round 734:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 734: agentuniverse is a framework for multi agents", 16),
        ["round 734:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 734: agentuniverse is a framework for multi agents", 24),
        ["round 734: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 734: agentuniverse is a framework for multi agents", 32),
        ["round 734: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 734: knowledge stored as vectors enables retrieval", 4),
        ["round", "734:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 734: knowledge stored as vectors enables retrieval", 8),
        ["round", "734:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 734: knowledge stored as vectors enables retrieval", 12),
        ["round 734:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 734: knowledge stored as vectors enables retrieval", 16),
        ["round 734:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 734: knowledge stored as vectors enables retrieval", 24),
        ["round 734: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 734: knowledge stored as vectors enables retrieval", 32),
        ["round 734: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 734: the processor reads the record then stops", 4),
        ["round", "734:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 734: the processor reads the record then stops", 8),
        ["round", "734: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 734: the processor reads the record then stops", 12),
        ["round 734:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 734: the processor reads the record then stops", 16),
        ["round 734: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 734: the processor reads the record then stops", 24),
        ["round 734: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 734: the processor reads the record then stops", 32),
        ["round 734: the processor reads", "the record then stops"],
    ),
    (
        ("round 734: a worker pulls the next task from the queue", 4),
        ["round", "734:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 734: a worker pulls the next task from the queue", 8),
        ["round", "734: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 734: a worker pulls the next task from the queue", 12),
        ["round 734: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 734: a worker pulls the next task from the queue", 16),
        ["round 734: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 734: a worker pulls the next task from the queue", 24),
        ["round 734: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 734: a worker pulls the next task from the queue", 32),
        ["round 734: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 734: signals travel through the network layer", 4),
        ["round", "734:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 734: signals travel through the network layer", 8),
        ["round", "734:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 734: signals travel through the network layer", 12),
        ["round 734:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 734: signals travel through the network layer", 16),
        ["round 734:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 734: signals travel through the network layer", 24),
        ["round 734: signals", "travel through the", "network layer"],
    ),
    (
        ("round 734: signals travel through the network layer", 32),
        ["round 734: signals travel", "through the network layer"],
    ),
    (
        ("round 734: the gateway routes each request by policy", 4),
        ["round", "734:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 734: the gateway routes each request by policy", 8),
        ["round", "734: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 734: the gateway routes each request by policy", 12),
        ["round 734:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 734: the gateway routes each request by policy", 16),
        ["round 734: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 734: the gateway routes each request by policy", 24),
        ["round 734: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 734: the gateway routes each request by policy", 32),
        ["round 734: the gateway routes", "each request by policy"],
    ),
    (
        ("round 734: memory grows until the buffer is full", 4),
        ["round", "734:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 734: memory grows until the buffer is full", 8),
        ["round", "734:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 734: memory grows until the buffer is full", 12),
        ["round 734:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 734: memory grows until the buffer is full", 16),
        ["round 734:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 734: memory grows until the buffer is full", 24), ["round 734: memory grows", "until the buffer is full"]),
    (("round 734: memory grows until the buffer is full", 32), ["round 734: memory grows until", "the buffer is full"]),
    (
        ("round 734: the cluster mirrors every packet twice", 4),
        ["round", "734:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 734: the cluster mirrors every packet twice", 8),
        ["round", "734: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 734: the cluster mirrors every packet twice", 12),
        ["round 734:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 734: the cluster mirrors every packet twice", 16),
        ["round 734: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 734: the cluster mirrors every packet twice", 24),
        ["round 734: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 734: the cluster mirrors every packet twice", 32),
        ["round 734: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 734: ranking uses tokens learned from the corpus", 4),
        ["round", "734:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 734: ranking uses tokens learned from the corpus", 8),
        ["round", "734:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 734: ranking uses tokens learned from the corpus", 12),
        ["round 734:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 734: ranking uses tokens learned from the corpus", 16),
        ["round 734:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 734: ranking uses tokens learned from the corpus", 24),
        ["round 734: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 734: ranking uses tokens learned from the corpus", 32),
        ["round 734: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 734: a long session ends when the candle dies", 4),
        ["round", "734:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 734: a long session ends when the candle dies", 8),
        ["round", "734: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 734: a long session ends when the candle dies", 12),
        ["round 734: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 734: a long session ends when the candle dies", 16),
        ["round 734: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 734: a long session ends when the candle dies", 24),
        ["round 734: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 734: a long session ends when the candle dies", 32),
        ["round 734: a long session ends", "when the candle dies"],
    ),
    (
        ("round 734: encode the prompt then map the result", 4),
        ["round", "734:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 734: encode the prompt then map the result", 8),
        ["round", "734:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 734: encode the prompt then map the result", 12),
        ["round 734:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 734: encode the prompt then map the result", 16),
        ["round 734:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 734: encode the prompt then map the result", 24),
        ["round 734: encode the", "prompt then map the", "result"],
    ),
    (("round 734: encode the prompt then map the result", 32), ["round 734: encode the prompt", "then map the result"]),
    (
        ("round 734: the kernel wakes the worker at dawn", 4),
        ["round", "734:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 734: the kernel wakes the worker at dawn", 8),
        ["round", "734: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 734: the kernel wakes the worker at dawn", 12),
        ["round 734:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 734: the kernel wakes the worker at dawn", 16), ["round 734: the", "kernel wakes the", "worker at dawn"]),
    (("round 734: the kernel wakes the worker at dawn", 24), ["round 734: the kernel", "wakes the worker at dawn"]),
    (("round 734: the kernel wakes the worker at dawn", 32), ["round 734: the kernel wakes the", "worker at dawn"]),
    (
        ("round 734: service latency drops after the patch", 4),
        ["round", "734:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 734: service latency drops after the patch", 8),
        ["round", "734:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 734: service latency drops after the patch", 12),
        ["round 734:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 734: service latency drops after the patch", 16),
        ["round 734:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 734: service latency drops after the patch", 24),
        ["round 734: service", "latency drops after the", "patch"],
    ),
    (("round 734: service latency drops after the patch", 32), ["round 734: service latency drops", "after the patch"]),
    (
        ("round 734: the library caches every vector it sees", 4),
        ["round", "734:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 734: the library caches every vector it sees", 8),
        ["round", "734: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 734: the library caches every vector it sees", 12),
        ["round 734:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 734: the library caches every vector it sees", 16),
        ["round 734: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 734: the library caches every vector it sees", 24),
        ["round 734: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 734: the library caches every vector it sees", 32),
        ["round 734: the library caches", "every vector it sees"],
    ),
    (
        ("round 734: agents argue then the debate resolves", 4),
        ["round", "734:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 734: agents argue then the debate resolves", 8),
        ["round", "734:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 734: agents argue then the debate resolves", 12),
        ["round 734:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 734: agents argue then the debate resolves", 16),
        ["round 734:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 734: agents argue then the debate resolves", 24), ["round 734: agents argue", "then the debate resolves"]),
    (("round 734: agents argue then the debate resolves", 32), ["round 734: agents argue then the", "debate resolves"]),
    (
        ("round 734: the filter keeps only strong matches", 4),
        ["round", "734:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 734: the filter keeps only strong matches", 8),
        ["round", "734: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 734: the filter keeps only strong matches", 12),
        ["round 734:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 734: the filter keeps only strong matches", 16),
        ["round 734: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 734: the filter keeps only strong matches", 24),
        ["round 734: the filter", "keeps only strong", "matches"],
    ),
    (("round 734: the filter keeps only strong matches", 32), ["round 734: the filter keeps only", "strong matches"]),
    (
        ("round 734: the model answers with a short reply", 4),
        ["round", "734:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 734: the model answers with a short reply", 8),
        ["round", "734: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 734: the model answers with a short reply", 12),
        ["round 734:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 734: the model answers with a short reply", 16),
        ["round 734: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 734: the model answers with a short reply", 24),
        ["round 734: the model", "answers with a short", "reply"],
    ),
    (("round 734: the model answers with a short reply", 32), ["round 734: the model answers", "with a short reply"]),
    (
        ("round 734: the recorder stores the reasoning trace", 4),
        ["round", "734:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 734: the recorder stores the reasoning trace", 8),
        ["round", "734: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 734: the recorder stores the reasoning trace", 12),
        ["round 734:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 734: the recorder stores the reasoning trace", 16),
        ["round 734: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 734: the recorder stores the reasoning trace", 24),
        ["round 734: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 734: the recorder stores the reasoning trace", 32),
        ["round 734: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 734: the angel watches the processor run", 4),
        ["round", "734:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 734: the angel watches the processor run", 8),
        ["round", "734: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 734: the angel watches the processor run", 12),
        ["round 734:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 734: the angel watches the processor run", 16),
        ["round 734: the", "angel watches", "the processor", "run"],
    ),
    (("round 734: the angel watches the processor run", 24), ["round 734: the angel", "watches the processor", "run"]),
    (("round 734: the angel watches the processor run", 32), ["round 734: the angel watches the", "processor run"]),
    (
        ("round 734: angle of the vector decides the match", 4),
        ["round", "734:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 734: angle of the vector decides the match", 8),
        ["round", "734:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 734: angle of the vector decides the match", 12),
        ["round 734:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 734: angle of the vector decides the match", 16),
        ["round 734: angle", "of the vector", "decides the", "match"],
    ),
    (("round 734: angle of the vector decides the match", 24), ["round 734: angle of the", "vector decides the match"]),
    (("round 734: angle of the vector decides the match", 32), ["round 734: angle of the vector", "decides the match"]),
    (
        ("round 734: the candle burns twice as long at night", 4),
        ["round", "734:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 734: the candle burns twice as long at night", 8),
        ["round", "734: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 734: the candle burns twice as long at night", 12),
        ["round 734:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 734: the candle burns twice as long at night", 16),
        ["round 734: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 734: the candle burns twice as long at night", 24),
        ["round 734: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 734: the candle burns twice as long at night", 32),
        ["round 734: the candle burns", "twice as long at night"],
    ),
    (
        ("round 734: a mirror of the universe in one line", 4),
        ["round", "734:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 734: a mirror of the universe in one line", 8),
        ["round", "734: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 734: a mirror of the universe in one line", 12),
        ["round 734: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 734: a mirror of the universe in one line", 16),
        ["round 734: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 734: a mirror of the universe in one line", 24), ["round 734: a mirror of", "the universe in one line"]),
    (("round 734: a mirror of the universe in one line", 32), ["round 734: a mirror of the", "universe in one line"]),
    (
        ("round 734: the queue drains before the storm", 4),
        ["round", "734:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 734: the queue drains before the storm", 8),
        ["round", "734: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 734: the queue drains before the storm", 12),
        ["round 734:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 734: the queue drains before the storm", 16), ["round 734: the", "queue drains", "before the storm"]),
    (("round 734: the queue drains before the storm", 24), ["round 734: the queue", "drains before the storm"]),
    (("round 734: the queue drains before the storm", 32), ["round 734: the queue drains", "before the storm"]),
    (
        ("kitten734 sitting734 agent734 angle734 universe734 memory734", 6),
        ["kitten734", "sitting734", "agent734", "angle734", "universe734", "memory734"],
    ),
    (
        ("kitten734 sitting734 agent734 angle734 universe734 memory734", 10),
        ["kitten734", "sitting734", "agent734", "angle734", "universe734", "memory734"],
    ),
    (
        ("kitten734 sitting734 agent734 angle734 universe734 memory734", 18),
        ["kitten734", "sitting734", "agent734 angle734", "universe734", "memory734"],
    ),
    (
        ("kitten734 sitting734 agent734 angle734 universe734 memory734", 28),
        ["kitten734 sitting734", "agent734 angle734", "universe734 memory734"],
    ),
    (
        ("sitting734 agent734 angle734 universe734 memory734 stream734", 6),
        ["sitting734", "agent734", "angle734", "universe734", "memory734", "stream734"],
    ),
    (
        ("sitting734 agent734 angle734 universe734 memory734 stream734", 10),
        ["sitting734", "agent734", "angle734", "universe734", "memory734", "stream734"],
    ),
    (
        ("sitting734 agent734 angle734 universe734 memory734 stream734", 18),
        ["sitting734", "agent734 angle734", "universe734", "memory734", "stream734"],
    ),
    (
        ("sitting734 agent734 angle734 universe734 memory734 stream734", 28),
        ["sitting734 agent734 angle734", "universe734 memory734", "stream734"],
    ),
    (
        ("agent734 angle734 universe734 memory734 stream734 context734", 6),
        ["agent734", "angle734", "universe734", "memory734", "stream734", "context734"],
    ),
    (
        ("agent734 angle734 universe734 memory734 stream734 context734", 10),
        ["agent734", "angle734", "universe734", "memory734", "stream734", "context734"],
    ),
    (
        ("agent734 angle734 universe734 memory734 stream734 context734", 18),
        ["agent734 angle734", "universe734", "memory734", "stream734", "context734"],
    ),
    (
        ("agent734 angle734 universe734 memory734 stream734 context734", 28),
        ["agent734 angle734", "universe734 memory734", "stream734 context734"],
    ),
    (
        ("angle734 universe734 memory734 stream734 context734 knowledge734", 6),
        ["angle734", "universe734", "memory734", "stream734", "context734", "knowledge734"],
    ),
    (
        ("angle734 universe734 memory734 stream734 context734 knowledge734", 10),
        ["angle734", "universe734", "memory734", "stream734", "context734", "knowledge734"],
    ),
    (
        ("angle734 universe734 memory734 stream734 context734 knowledge734", 18),
        ["angle734", "universe734", "memory734", "stream734", "context734", "knowledge734"],
    ),
    (
        ("angle734 universe734 memory734 stream734 context734 knowledge734", 28),
        ["angle734 universe734", "memory734 stream734", "context734 knowledge734"],
    ),
    (
        ("universe734 memory734 stream734 context734 knowledge734 vector734", 6),
        ["universe734", "memory734", "stream734", "context734", "knowledge734", "vector734"],
    ),
    (
        ("universe734 memory734 stream734 context734 knowledge734 vector734", 10),
        ["universe734", "memory734", "stream734", "context734", "knowledge734", "vector734"],
    ),
    (
        ("universe734 memory734 stream734 context734 knowledge734 vector734", 18),
        ["universe734", "memory734", "stream734", "context734", "knowledge734", "vector734"],
    ),
    (
        ("universe734 memory734 stream734 context734 knowledge734 vector734", 28),
        ["universe734 memory734", "stream734 context734", "knowledge734 vector734"],
    ),
    (
        ("memory734 stream734 context734 knowledge734 vector734 processor734", 6),
        ["memory734", "stream734", "context734", "knowledge734", "vector734", "processor734"],
    ),
    (
        ("memory734 stream734 context734 knowledge734 vector734 processor734", 10),
        ["memory734", "stream734", "context734", "knowledge734", "vector734", "processor734"],
    ),
    (
        ("memory734 stream734 context734 knowledge734 vector734 processor734", 18),
        ["memory734", "stream734", "context734", "knowledge734", "vector734", "processor734"],
    ),
    (
        ("memory734 stream734 context734 knowledge734 vector734 processor734", 28),
        ["memory734 stream734", "context734 knowledge734", "vector734 processor734"],
    ),
    (
        ("stream734 context734 knowledge734 vector734 processor734 reasoning734", 6),
        ["stream734", "context734", "knowledge734", "vector734", "processor734", "reasoning734"],
    ),
    (
        ("stream734 context734 knowledge734 vector734 processor734 reasoning734", 10),
        ["stream734", "context734", "knowledge734", "vector734", "processor734", "reasoning734"],
    ),
    (
        ("stream734 context734 knowledge734 vector734 processor734 reasoning734", 18),
        ["stream734", "context734", "knowledge734", "vector734", "processor734", "reasoning734"],
    ),
    (
        ("stream734 context734 knowledge734 vector734 processor734 reasoning734", 28),
        ["stream734 context734", "knowledge734 vector734", "processor734 reasoning734"],
    ),
    (
        ("context734 knowledge734 vector734 processor734 reasoning734 machine734", 6),
        ["context734", "knowledge734", "vector734", "processor734", "reasoning734", "machine734"],
    ),
    (
        ("context734 knowledge734 vector734 processor734 reasoning734 machine734", 10),
        ["context734", "knowledge734", "vector734", "processor734", "reasoning734", "machine734"],
    ),
    (
        ("context734 knowledge734 vector734 processor734 reasoning734 machine734", 18),
        ["context734", "knowledge734", "vector734", "processor734", "reasoning734", "machine734"],
    ),
    (
        ("context734 knowledge734 vector734 processor734 reasoning734 machine734", 28),
        ["context734 knowledge734", "vector734 processor734", "reasoning734 machine734"],
    ),
    (
        ("knowledge734 vector734 processor734 reasoning734 machine734 learning734", 6),
        ["knowledge734", "vector734", "processor734", "reasoning734", "machine734", "learning734"],
    ),
    (
        ("knowledge734 vector734 processor734 reasoning734 machine734 learning734", 10),
        ["knowledge734", "vector734", "processor734", "reasoning734", "machine734", "learning734"],
    ),
    (
        ("knowledge734 vector734 processor734 reasoning734 machine734 learning734", 18),
        ["knowledge734", "vector734", "processor734", "reasoning734", "machine734", "learning734"],
    ),
    (
        ("knowledge734 vector734 processor734 reasoning734 machine734 learning734", 28),
        ["knowledge734 vector734", "processor734 reasoning734", "machine734 learning734"],
    ),
    (
        ("vector734 processor734 reasoning734 machine734 learning734 model734", 6),
        ["vector734", "processor734", "reasoning734", "machine734", "learning734", "model734"],
    ),
    (
        ("vector734 processor734 reasoning734 machine734 learning734 model734", 10),
        ["vector734", "processor734", "reasoning734", "machine734", "learning734", "model734"],
    ),
    (
        ("vector734 processor734 reasoning734 machine734 learning734 model734", 18),
        ["vector734", "processor734", "reasoning734", "machine734", "learning734", "model734"],
    ),
    (
        ("vector734 processor734 reasoning734 machine734 learning734 model734", 28),
        ["vector734 processor734", "reasoning734 machine734", "learning734 model734"],
    ),
    (
        ("processor734 reasoning734 machine734 learning734 model734 token734", 6),
        ["processor734", "reasoning734", "machine734", "learning734", "model734", "token734"],
    ),
    (
        ("processor734 reasoning734 machine734 learning734 model734 token734", 10),
        ["processor734", "reasoning734", "machine734", "learning734", "model734", "token734"],
    ),
    (
        ("processor734 reasoning734 machine734 learning734 model734 token734", 18),
        ["processor734", "reasoning734", "machine734", "learning734", "model734 token734"],
    ),
    (
        ("processor734 reasoning734 machine734 learning734 model734 token734", 28),
        ["processor734 reasoning734", "machine734 learning734", "model734 token734"],
    ),
    (
        ("reasoning734 machine734 learning734 model734 token734 prompt734", 6),
        ["reasoning734", "machine734", "learning734", "model734", "token734", "prompt734"],
    ),
    (
        ("reasoning734 machine734 learning734 model734 token734 prompt734", 10),
        ["reasoning734", "machine734", "learning734", "model734", "token734", "prompt734"],
    ),
    (
        ("reasoning734 machine734 learning734 model734 token734 prompt734", 18),
        ["reasoning734", "machine734", "learning734", "model734 token734", "prompt734"],
    ),
    (
        ("reasoning734 machine734 learning734 model734 token734 prompt734", 28),
        ["reasoning734 machine734", "learning734 model734", "token734 prompt734"],
    ),
    (
        ("machine734 learning734 model734 token734 prompt734 session734", 6),
        ["machine734", "learning734", "model734", "token734", "prompt734", "session734"],
    ),
    (
        ("machine734 learning734 model734 token734 prompt734 session734", 10),
        ["machine734", "learning734", "model734", "token734", "prompt734", "session734"],
    ),
    (
        ("machine734 learning734 model734 token734 prompt734 session734", 18),
        ["machine734", "learning734", "model734 token734", "prompt734", "session734"],
    ),
    (
        ("machine734 learning734 model734 token734 prompt734 session734", 28),
        ["machine734 learning734", "model734 token734 prompt734", "session734"],
    ),
    (
        ("learning734 model734 token734 prompt734 session734 library734", 6),
        ["learning734", "model734", "token734", "prompt734", "session734", "library734"],
    ),
    (
        ("learning734 model734 token734 prompt734 session734 library734", 10),
        ["learning734", "model734", "token734", "prompt734", "session734", "library734"],
    ),
    (
        ("learning734 model734 token734 prompt734 session734 library734", 18),
        ["learning734", "model734 token734", "prompt734", "session734", "library734"],
    ),
    (
        ("learning734 model734 token734 prompt734 session734 library734", 28),
        ["learning734 model734", "token734 prompt734", "session734 library734"],
    ),
    (
        ("model734 token734 prompt734 session734 library734 service734", 6),
        ["model734", "token734", "prompt734", "session734", "library734", "service734"],
    ),
    (
        ("model734 token734 prompt734 session734 library734 service734", 10),
        ["model734", "token734", "prompt734", "session734", "library734", "service734"],
    ),
    (
        ("model734 token734 prompt734 session734 library734 service734", 18),
        ["model734 token734", "prompt734", "session734", "library734", "service734"],
    ),
    (
        ("model734 token734 prompt734 session734 library734 service734", 28),
        ["model734 token734 prompt734", "session734 library734", "service734"],
    ),
    (
        ("token734 prompt734 session734 library734 service734 gateway734", 6),
        ["token734", "prompt734", "session734", "library734", "service734", "gateway734"],
    ),
    (
        ("token734 prompt734 session734 library734 service734 gateway734", 10),
        ["token734", "prompt734", "session734", "library734", "service734", "gateway734"],
    ),
    (
        ("token734 prompt734 session734 library734 service734 gateway734", 18),
        ["token734 prompt734", "session734", "library734", "service734", "gateway734"],
    ),
    (
        ("token734 prompt734 session734 library734 service734 gateway734", 28),
        ["token734 prompt734", "session734 library734", "service734 gateway734"],
    ),
    (
        ("prompt734 session734 library734 service734 gateway734 storage734", 6),
        ["prompt734", "session734", "library734", "service734", "gateway734", "storage734"],
    ),
    (
        ("prompt734 session734 library734 service734 gateway734 storage734", 10),
        ["prompt734", "session734", "library734", "service734", "gateway734", "storage734"],
    ),
    (
        ("prompt734 session734 library734 service734 gateway734 storage734", 18),
        ["prompt734", "session734", "library734", "service734", "gateway734", "storage734"],
    ),
    (
        ("prompt734 session734 library734 service734 gateway734 storage734", 28),
        ["prompt734 session734", "library734 service734", "gateway734 storage734"],
    ),
    (
        ("session734 library734 service734 gateway734 storage734 network734", 6),
        ["session734", "library734", "service734", "gateway734", "storage734", "network734"],
    ),
    (
        ("session734 library734 service734 gateway734 storage734 network734", 10),
        ["session734", "library734", "service734", "gateway734", "storage734", "network734"],
    ),
    (
        ("session734 library734 service734 gateway734 storage734 network734", 18),
        ["session734", "library734", "service734", "gateway734", "storage734", "network734"],
    ),
    (
        ("session734 library734 service734 gateway734 storage734 network734", 28),
        ["session734 library734", "service734 gateway734", "storage734 network734"],
    ),
    (
        ("library734 service734 gateway734 storage734 network734 latency734", 6),
        ["library734", "service734", "gateway734", "storage734", "network734", "latency734"],
    ),
    (
        ("library734 service734 gateway734 storage734 network734 latency734", 10),
        ["library734", "service734", "gateway734", "storage734", "network734", "latency734"],
    ),
    (
        ("library734 service734 gateway734 storage734 network734 latency734", 18),
        ["library734", "service734", "gateway734", "storage734", "network734", "latency734"],
    ),
    (
        ("library734 service734 gateway734 storage734 network734 latency734", 28),
        ["library734 service734", "gateway734 storage734", "network734 latency734"],
    ),
    (
        ("service734 gateway734 storage734 network734 latency734 buffer734", 6),
        ["service734", "gateway734", "storage734", "network734", "latency734", "buffer734"],
    ),
    (
        ("service734 gateway734 storage734 network734 latency734 buffer734", 10),
        ["service734", "gateway734", "storage734", "network734", "latency734", "buffer734"],
    ),
    (
        ("service734 gateway734 storage734 network734 latency734 buffer734", 18),
        ["service734", "gateway734", "storage734", "network734", "latency734", "buffer734"],
    ),
    (
        ("service734 gateway734 storage734 network734 latency734 buffer734", 28),
        ["service734 gateway734", "storage734 network734", "latency734 buffer734"],
    ),
    (
        ("gateway734 storage734 network734 latency734 buffer734 queue734", 6),
        ["gateway734", "storage734", "network734", "latency734", "buffer734", "queue734"],
    ),
    (
        ("gateway734 storage734 network734 latency734 buffer734 queue734", 10),
        ["gateway734", "storage734", "network734", "latency734", "buffer734", "queue734"],
    ),
    (
        ("gateway734 storage734 network734 latency734 buffer734 queue734", 18),
        ["gateway734", "storage734", "network734", "latency734", "buffer734 queue734"],
    ),
    (
        ("gateway734 storage734 network734 latency734 buffer734 queue734", 28),
        ["gateway734 storage734", "network734 latency734", "buffer734 queue734"],
    ),
    (
        ("storage734 network734 latency734 buffer734 queue734 worker734", 6),
        ["storage734", "network734", "latency734", "buffer734", "queue734", "worker734"],
    ),
    (
        ("storage734 network734 latency734 buffer734 queue734 worker734", 10),
        ["storage734", "network734", "latency734", "buffer734", "queue734", "worker734"],
    ),
    (
        ("storage734 network734 latency734 buffer734 queue734 worker734", 18),
        ["storage734", "network734", "latency734", "buffer734 queue734", "worker734"],
    ),
    (
        ("storage734 network734 latency734 buffer734 queue734 worker734", 28),
        ["storage734 network734", "latency734 buffer734", "queue734 worker734"],
    ),
    (
        ("network734 latency734 buffer734 queue734 worker734 kernel734", 6),
        ["network734", "latency734", "buffer734", "queue734", "worker734", "kernel734"],
    ),
    (
        ("network734 latency734 buffer734 queue734 worker734 kernel734", 10),
        ["network734", "latency734", "buffer734", "queue734", "worker734", "kernel734"],
    ),
    (
        ("network734 latency734 buffer734 queue734 worker734 kernel734", 18),
        ["network734", "latency734", "buffer734 queue734", "worker734", "kernel734"],
    ),
    (
        ("network734 latency734 buffer734 queue734 worker734 kernel734", 28),
        ["network734 latency734", "buffer734 queue734 worker734", "kernel734"],
    ),
    (
        ("latency734 buffer734 queue734 worker734 kernel734 signal734", 6),
        ["latency734", "buffer734", "queue734", "worker734", "kernel734", "signal734"],
    ),
    (
        ("latency734 buffer734 queue734 worker734 kernel734 signal734", 10),
        ["latency734", "buffer734", "queue734", "worker734", "kernel734", "signal734"],
    ),
    (
        ("latency734 buffer734 queue734 worker734 kernel734 signal734", 18),
        ["latency734", "buffer734 queue734", "worker734", "kernel734", "signal734"],
    ),
    (
        ("latency734 buffer734 queue734 worker734 kernel734 signal734", 28),
        ["latency734 buffer734", "queue734 worker734 kernel734", "signal734"],
    ),
    (
        ("buffer734 queue734 worker734 kernel734 signal734 packet734", 6),
        ["buffer734", "queue734", "worker734", "kernel734", "signal734", "packet734"],
    ),
    (
        ("buffer734 queue734 worker734 kernel734 signal734 packet734", 10),
        ["buffer734", "queue734", "worker734", "kernel734", "signal734", "packet734"],
    ),
    (
        ("buffer734 queue734 worker734 kernel734 signal734 packet734", 18),
        ["buffer734 queue734", "worker734", "kernel734", "signal734", "packet734"],
    ),
    (
        ("buffer734 queue734 worker734 kernel734 signal734 packet734", 28),
        ["buffer734 queue734 worker734", "kernel734 signal734", "packet734"],
    ),
    (
        ("queue734 worker734 kernel734 signal734 packet734 router734", 6),
        ["queue734", "worker734", "kernel734", "signal734", "packet734", "router734"],
    ),
    (
        ("queue734 worker734 kernel734 signal734 packet734 router734", 10),
        ["queue734", "worker734", "kernel734", "signal734", "packet734", "router734"],
    ),
    (
        ("queue734 worker734 kernel734 signal734 packet734 router734", 18),
        ["queue734 worker734", "kernel734", "signal734", "packet734", "router734"],
    ),
    (
        ("queue734 worker734 kernel734 signal734 packet734 router734", 28),
        ["queue734 worker734 kernel734", "signal734 packet734", "router734"],
    ),
    (
        ("worker734 kernel734 signal734 packet734 router734 cluster734", 6),
        ["worker734", "kernel734", "signal734", "packet734", "router734", "cluster734"],
    ),
    (
        ("worker734 kernel734 signal734 packet734 router734 cluster734", 10),
        ["worker734", "kernel734", "signal734", "packet734", "router734", "cluster734"],
    ),
    (
        ("worker734 kernel734 signal734 packet734 router734 cluster734", 18),
        ["worker734", "kernel734", "signal734", "packet734", "router734", "cluster734"],
    ),
    (
        ("worker734 kernel734 signal734 packet734 router734 cluster734", 28),
        ["worker734 kernel734", "signal734 packet734", "router734 cluster734"],
    ),
    (
        ("kernel734 signal734 packet734 router734 cluster734 mirror734", 6),
        ["kernel734", "signal734", "packet734", "router734", "cluster734", "mirror734"],
    ),
    (
        ("kernel734 signal734 packet734 router734 cluster734 mirror734", 10),
        ["kernel734", "signal734", "packet734", "router734", "cluster734", "mirror734"],
    ),
    (
        ("kernel734 signal734 packet734 router734 cluster734 mirror734", 18),
        ["kernel734", "signal734", "packet734", "router734", "cluster734", "mirror734"],
    ),
    (
        ("kernel734 signal734 packet734 router734 cluster734 mirror734", 28),
        ["kernel734 signal734", "packet734 router734", "cluster734 mirror734"],
    ),
    (
        ("signal734 packet734 router734 cluster734 mirror734 filter734", 6),
        ["signal734", "packet734", "router734", "cluster734", "mirror734", "filter734"],
    ),
    (
        ("signal734 packet734 router734 cluster734 mirror734 filter734", 10),
        ["signal734", "packet734", "router734", "cluster734", "mirror734", "filter734"],
    ),
    (
        ("signal734 packet734 router734 cluster734 mirror734 filter734", 18),
        ["signal734", "packet734", "router734", "cluster734", "mirror734", "filter734"],
    ),
    (
        ("signal734 packet734 router734 cluster734 mirror734 filter734", 28),
        ["signal734 packet734", "router734 cluster734", "mirror734 filter734"],
    ),
    (
        ("packet734 router734 cluster734 mirror734 filter734 ranking734", 6),
        ["packet734", "router734", "cluster734", "mirror734", "filter734", "ranking734"],
    ),
    (
        ("packet734 router734 cluster734 mirror734 filter734 ranking734", 10),
        ["packet734", "router734", "cluster734", "mirror734", "filter734", "ranking734"],
    ),
    (
        ("packet734 router734 cluster734 mirror734 filter734 ranking734", 18),
        ["packet734", "router734", "cluster734", "mirror734", "filter734", "ranking734"],
    ),
    (
        ("packet734 router734 cluster734 mirror734 filter734 ranking734", 28),
        ["packet734 router734", "cluster734 mirror734", "filter734 ranking734"],
    ),
    (
        ("router734 cluster734 mirror734 filter734 ranking734 encoding734", 6),
        ["router734", "cluster734", "mirror734", "filter734", "ranking734", "encoding734"],
    ),
    (
        ("router734 cluster734 mirror734 filter734 ranking734 encoding734", 10),
        ["router734", "cluster734", "mirror734", "filter734", "ranking734", "encoding734"],
    ),
    (
        ("router734 cluster734 mirror734 filter734 ranking734 encoding734", 18),
        ["router734", "cluster734", "mirror734", "filter734", "ranking734", "encoding734"],
    ),
    (
        ("router734 cluster734 mirror734 filter734 ranking734 encoding734", 28),
        ["router734 cluster734", "mirror734 filter734", "ranking734 encoding734"],
    ),
    (
        ("cluster734 mirror734 filter734 ranking734 encoding734 mapping734", 6),
        ["cluster734", "mirror734", "filter734", "ranking734", "encoding734", "mapping734"],
    ),
    (
        ("cluster734 mirror734 filter734 ranking734 encoding734 mapping734", 10),
        ["cluster734", "mirror734", "filter734", "ranking734", "encoding734", "mapping734"],
    ),
    (
        ("cluster734 mirror734 filter734 ranking734 encoding734 mapping734", 18),
        ["cluster734", "mirror734", "filter734", "ranking734", "encoding734", "mapping734"],
    ),
    (
        ("cluster734 mirror734 filter734 ranking734 encoding734 mapping734", 28),
        ["cluster734 mirror734", "filter734 ranking734", "encoding734 mapping734"],
    ),
    (
        ("mirror734 filter734 ranking734 encoding734 mapping734 record734", 6),
        ["mirror734", "filter734", "ranking734", "encoding734", "mapping734", "record734"],
    ),
    (
        ("mirror734 filter734 ranking734 encoding734 mapping734 record734", 10),
        ["mirror734", "filter734", "ranking734", "encoding734", "mapping734", "record734"],
    ),
    (
        ("mirror734 filter734 ranking734 encoding734 mapping734 record734", 18),
        ["mirror734", "filter734", "ranking734", "encoding734", "mapping734", "record734"],
    ),
    (
        ("mirror734 filter734 ranking734 encoding734 mapping734 record734", 28),
        ["mirror734 filter734", "ranking734 encoding734", "mapping734 record734"],
    ),
    (
        ("filter734 ranking734 encoding734 mapping734 record734 candle734", 6),
        ["filter734", "ranking734", "encoding734", "mapping734", "record734", "candle734"],
    ),
    (
        ("filter734 ranking734 encoding734 mapping734 record734 candle734", 10),
        ["filter734", "ranking734", "encoding734", "mapping734", "record734", "candle734"],
    ),
    (
        ("filter734 ranking734 encoding734 mapping734 record734 candle734", 18),
        ["filter734", "ranking734", "encoding734", "mapping734", "record734", "candle734"],
    ),
    (
        ("filter734 ranking734 encoding734 mapping734 record734 candle734", 28),
        ["filter734 ranking734", "encoding734 mapping734", "record734 candle734"],
    ),
    (
        ("ranking734 encoding734 mapping734 record734 candle734 thread734", 6),
        ["ranking734", "encoding734", "mapping734", "record734", "candle734", "thread734"],
    ),
    (
        ("ranking734 encoding734 mapping734 record734 candle734 thread734", 10),
        ["ranking734", "encoding734", "mapping734", "record734", "candle734", "thread734"],
    ),
    (
        ("ranking734 encoding734 mapping734 record734 candle734 thread734", 18),
        ["ranking734", "encoding734", "mapping734", "record734", "candle734", "thread734"],
    ),
    (
        ("ranking734 encoding734 mapping734 record734 candle734 thread734", 28),
        ["ranking734 encoding734", "mapping734 record734", "candle734 thread734"],
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
