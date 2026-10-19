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
        ("round 200: the quick brown fox jumps over the lazy dog", 4),
        ["round", "200:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 200: the quick brown fox jumps over the lazy dog", 8),
        ["round", "200: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 200: the quick brown fox jumps over the lazy dog", 12),
        ["round 200:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 200: the quick brown fox jumps over the lazy dog", 16),
        ["round 200: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 200: the quick brown fox jumps over the lazy dog", 24),
        ["round 200: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 200: the quick brown fox jumps over the lazy dog", 32),
        ["round 200: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 200: agentuniverse is a framework for multi agents", 4),
        ["round", "200:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 200: agentuniverse is a framework for multi agents", 8),
        ["round", "200:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 200: agentuniverse is a framework for multi agents", 12),
        ["round 200:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 200: agentuniverse is a framework for multi agents", 16),
        ["round 200:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 200: agentuniverse is a framework for multi agents", 24),
        ["round 200: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 200: agentuniverse is a framework for multi agents", 32),
        ["round 200: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 200: knowledge stored as vectors enables retrieval", 4),
        ["round", "200:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 200: knowledge stored as vectors enables retrieval", 8),
        ["round", "200:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 200: knowledge stored as vectors enables retrieval", 12),
        ["round 200:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 200: knowledge stored as vectors enables retrieval", 16),
        ["round 200:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 200: knowledge stored as vectors enables retrieval", 24),
        ["round 200: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 200: knowledge stored as vectors enables retrieval", 32),
        ["round 200: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 200: the processor reads the record then stops", 4),
        ["round", "200:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 200: the processor reads the record then stops", 8),
        ["round", "200: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 200: the processor reads the record then stops", 12),
        ["round 200:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 200: the processor reads the record then stops", 16),
        ["round 200: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 200: the processor reads the record then stops", 24),
        ["round 200: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 200: the processor reads the record then stops", 32),
        ["round 200: the processor reads", "the record then stops"],
    ),
    (
        ("round 200: a worker pulls the next task from the queue", 4),
        ["round", "200:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 200: a worker pulls the next task from the queue", 8),
        ["round", "200: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 200: a worker pulls the next task from the queue", 12),
        ["round 200: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 200: a worker pulls the next task from the queue", 16),
        ["round 200: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 200: a worker pulls the next task from the queue", 24),
        ["round 200: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 200: a worker pulls the next task from the queue", 32),
        ["round 200: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 200: signals travel through the network layer", 4),
        ["round", "200:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 200: signals travel through the network layer", 8),
        ["round", "200:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 200: signals travel through the network layer", 12),
        ["round 200:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 200: signals travel through the network layer", 16),
        ["round 200:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 200: signals travel through the network layer", 24),
        ["round 200: signals", "travel through the", "network layer"],
    ),
    (
        ("round 200: signals travel through the network layer", 32),
        ["round 200: signals travel", "through the network layer"],
    ),
    (
        ("round 200: the gateway routes each request by policy", 4),
        ["round", "200:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 200: the gateway routes each request by policy", 8),
        ["round", "200: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 200: the gateway routes each request by policy", 12),
        ["round 200:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 200: the gateway routes each request by policy", 16),
        ["round 200: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 200: the gateway routes each request by policy", 24),
        ["round 200: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 200: the gateway routes each request by policy", 32),
        ["round 200: the gateway routes", "each request by policy"],
    ),
    (
        ("round 200: memory grows until the buffer is full", 4),
        ["round", "200:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 200: memory grows until the buffer is full", 8),
        ["round", "200:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 200: memory grows until the buffer is full", 12),
        ["round 200:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 200: memory grows until the buffer is full", 16),
        ["round 200:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 200: memory grows until the buffer is full", 24), ["round 200: memory grows", "until the buffer is full"]),
    (("round 200: memory grows until the buffer is full", 32), ["round 200: memory grows until", "the buffer is full"]),
    (
        ("round 200: the cluster mirrors every packet twice", 4),
        ["round", "200:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 200: the cluster mirrors every packet twice", 8),
        ["round", "200: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 200: the cluster mirrors every packet twice", 12),
        ["round 200:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 200: the cluster mirrors every packet twice", 16),
        ["round 200: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 200: the cluster mirrors every packet twice", 24),
        ["round 200: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 200: the cluster mirrors every packet twice", 32),
        ["round 200: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 200: ranking uses tokens learned from the corpus", 4),
        ["round", "200:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 200: ranking uses tokens learned from the corpus", 8),
        ["round", "200:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 200: ranking uses tokens learned from the corpus", 12),
        ["round 200:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 200: ranking uses tokens learned from the corpus", 16),
        ["round 200:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 200: ranking uses tokens learned from the corpus", 24),
        ["round 200: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 200: ranking uses tokens learned from the corpus", 32),
        ["round 200: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 200: a long session ends when the candle dies", 4),
        ["round", "200:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 200: a long session ends when the candle dies", 8),
        ["round", "200: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 200: a long session ends when the candle dies", 12),
        ["round 200: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 200: a long session ends when the candle dies", 16),
        ["round 200: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 200: a long session ends when the candle dies", 24),
        ["round 200: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 200: a long session ends when the candle dies", 32),
        ["round 200: a long session ends", "when the candle dies"],
    ),
    (
        ("round 200: encode the prompt then map the result", 4),
        ["round", "200:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 200: encode the prompt then map the result", 8),
        ["round", "200:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 200: encode the prompt then map the result", 12),
        ["round 200:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 200: encode the prompt then map the result", 16),
        ["round 200:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 200: encode the prompt then map the result", 24),
        ["round 200: encode the", "prompt then map the", "result"],
    ),
    (("round 200: encode the prompt then map the result", 32), ["round 200: encode the prompt", "then map the result"]),
    (
        ("round 200: the kernel wakes the worker at dawn", 4),
        ["round", "200:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 200: the kernel wakes the worker at dawn", 8),
        ["round", "200: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 200: the kernel wakes the worker at dawn", 12),
        ["round 200:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 200: the kernel wakes the worker at dawn", 16), ["round 200: the", "kernel wakes the", "worker at dawn"]),
    (("round 200: the kernel wakes the worker at dawn", 24), ["round 200: the kernel", "wakes the worker at dawn"]),
    (("round 200: the kernel wakes the worker at dawn", 32), ["round 200: the kernel wakes the", "worker at dawn"]),
    (
        ("round 200: service latency drops after the patch", 4),
        ["round", "200:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 200: service latency drops after the patch", 8),
        ["round", "200:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 200: service latency drops after the patch", 12),
        ["round 200:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 200: service latency drops after the patch", 16),
        ["round 200:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 200: service latency drops after the patch", 24),
        ["round 200: service", "latency drops after the", "patch"],
    ),
    (("round 200: service latency drops after the patch", 32), ["round 200: service latency drops", "after the patch"]),
    (
        ("round 200: the library caches every vector it sees", 4),
        ["round", "200:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 200: the library caches every vector it sees", 8),
        ["round", "200: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 200: the library caches every vector it sees", 12),
        ["round 200:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 200: the library caches every vector it sees", 16),
        ["round 200: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 200: the library caches every vector it sees", 24),
        ["round 200: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 200: the library caches every vector it sees", 32),
        ["round 200: the library caches", "every vector it sees"],
    ),
    (
        ("round 200: agents argue then the debate resolves", 4),
        ["round", "200:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 200: agents argue then the debate resolves", 8),
        ["round", "200:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 200: agents argue then the debate resolves", 12),
        ["round 200:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 200: agents argue then the debate resolves", 16),
        ["round 200:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 200: agents argue then the debate resolves", 24), ["round 200: agents argue", "then the debate resolves"]),
    (("round 200: agents argue then the debate resolves", 32), ["round 200: agents argue then the", "debate resolves"]),
    (
        ("round 200: the filter keeps only strong matches", 4),
        ["round", "200:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 200: the filter keeps only strong matches", 8),
        ["round", "200: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 200: the filter keeps only strong matches", 12),
        ["round 200:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 200: the filter keeps only strong matches", 16),
        ["round 200: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 200: the filter keeps only strong matches", 24),
        ["round 200: the filter", "keeps only strong", "matches"],
    ),
    (("round 200: the filter keeps only strong matches", 32), ["round 200: the filter keeps only", "strong matches"]),
    (
        ("round 200: the model answers with a short reply", 4),
        ["round", "200:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 200: the model answers with a short reply", 8),
        ["round", "200: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 200: the model answers with a short reply", 12),
        ["round 200:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 200: the model answers with a short reply", 16),
        ["round 200: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 200: the model answers with a short reply", 24),
        ["round 200: the model", "answers with a short", "reply"],
    ),
    (("round 200: the model answers with a short reply", 32), ["round 200: the model answers", "with a short reply"]),
    (
        ("round 200: the recorder stores the reasoning trace", 4),
        ["round", "200:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 200: the recorder stores the reasoning trace", 8),
        ["round", "200: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 200: the recorder stores the reasoning trace", 12),
        ["round 200:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 200: the recorder stores the reasoning trace", 16),
        ["round 200: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 200: the recorder stores the reasoning trace", 24),
        ["round 200: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 200: the recorder stores the reasoning trace", 32),
        ["round 200: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 200: the angel watches the processor run", 4),
        ["round", "200:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 200: the angel watches the processor run", 8),
        ["round", "200: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 200: the angel watches the processor run", 12),
        ["round 200:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 200: the angel watches the processor run", 16),
        ["round 200: the", "angel watches", "the processor", "run"],
    ),
    (("round 200: the angel watches the processor run", 24), ["round 200: the angel", "watches the processor", "run"]),
    (("round 200: the angel watches the processor run", 32), ["round 200: the angel watches the", "processor run"]),
    (
        ("round 200: angle of the vector decides the match", 4),
        ["round", "200:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 200: angle of the vector decides the match", 8),
        ["round", "200:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 200: angle of the vector decides the match", 12),
        ["round 200:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 200: angle of the vector decides the match", 16),
        ["round 200: angle", "of the vector", "decides the", "match"],
    ),
    (("round 200: angle of the vector decides the match", 24), ["round 200: angle of the", "vector decides the match"]),
    (("round 200: angle of the vector decides the match", 32), ["round 200: angle of the vector", "decides the match"]),
    (
        ("round 200: the candle burns twice as long at night", 4),
        ["round", "200:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 200: the candle burns twice as long at night", 8),
        ["round", "200: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 200: the candle burns twice as long at night", 12),
        ["round 200:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 200: the candle burns twice as long at night", 16),
        ["round 200: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 200: the candle burns twice as long at night", 24),
        ["round 200: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 200: the candle burns twice as long at night", 32),
        ["round 200: the candle burns", "twice as long at night"],
    ),
    (
        ("round 200: a mirror of the universe in one line", 4),
        ["round", "200:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 200: a mirror of the universe in one line", 8),
        ["round", "200: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 200: a mirror of the universe in one line", 12),
        ["round 200: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 200: a mirror of the universe in one line", 16),
        ["round 200: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 200: a mirror of the universe in one line", 24), ["round 200: a mirror of", "the universe in one line"]),
    (("round 200: a mirror of the universe in one line", 32), ["round 200: a mirror of the", "universe in one line"]),
    (
        ("round 200: the queue drains before the storm", 4),
        ["round", "200:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 200: the queue drains before the storm", 8),
        ["round", "200: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 200: the queue drains before the storm", 12),
        ["round 200:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 200: the queue drains before the storm", 16), ["round 200: the", "queue drains", "before the storm"]),
    (("round 200: the queue drains before the storm", 24), ["round 200: the queue", "drains before the storm"]),
    (("round 200: the queue drains before the storm", 32), ["round 200: the queue drains", "before the storm"]),
    (
        ("kitten200 sitting200 agent200 angle200 universe200 memory200", 6),
        ["kitten200", "sitting200", "agent200", "angle200", "universe200", "memory200"],
    ),
    (
        ("kitten200 sitting200 agent200 angle200 universe200 memory200", 10),
        ["kitten200", "sitting200", "agent200", "angle200", "universe200", "memory200"],
    ),
    (
        ("kitten200 sitting200 agent200 angle200 universe200 memory200", 18),
        ["kitten200", "sitting200", "agent200 angle200", "universe200", "memory200"],
    ),
    (
        ("kitten200 sitting200 agent200 angle200 universe200 memory200", 28),
        ["kitten200 sitting200", "agent200 angle200", "universe200 memory200"],
    ),
    (
        ("sitting200 agent200 angle200 universe200 memory200 stream200", 6),
        ["sitting200", "agent200", "angle200", "universe200", "memory200", "stream200"],
    ),
    (
        ("sitting200 agent200 angle200 universe200 memory200 stream200", 10),
        ["sitting200", "agent200", "angle200", "universe200", "memory200", "stream200"],
    ),
    (
        ("sitting200 agent200 angle200 universe200 memory200 stream200", 18),
        ["sitting200", "agent200 angle200", "universe200", "memory200", "stream200"],
    ),
    (
        ("sitting200 agent200 angle200 universe200 memory200 stream200", 28),
        ["sitting200 agent200 angle200", "universe200 memory200", "stream200"],
    ),
    (
        ("agent200 angle200 universe200 memory200 stream200 context200", 6),
        ["agent200", "angle200", "universe200", "memory200", "stream200", "context200"],
    ),
    (
        ("agent200 angle200 universe200 memory200 stream200 context200", 10),
        ["agent200", "angle200", "universe200", "memory200", "stream200", "context200"],
    ),
    (
        ("agent200 angle200 universe200 memory200 stream200 context200", 18),
        ["agent200 angle200", "universe200", "memory200", "stream200", "context200"],
    ),
    (
        ("agent200 angle200 universe200 memory200 stream200 context200", 28),
        ["agent200 angle200", "universe200 memory200", "stream200 context200"],
    ),
    (
        ("angle200 universe200 memory200 stream200 context200 knowledge200", 6),
        ["angle200", "universe200", "memory200", "stream200", "context200", "knowledge200"],
    ),
    (
        ("angle200 universe200 memory200 stream200 context200 knowledge200", 10),
        ["angle200", "universe200", "memory200", "stream200", "context200", "knowledge200"],
    ),
    (
        ("angle200 universe200 memory200 stream200 context200 knowledge200", 18),
        ["angle200", "universe200", "memory200", "stream200", "context200", "knowledge200"],
    ),
    (
        ("angle200 universe200 memory200 stream200 context200 knowledge200", 28),
        ["angle200 universe200", "memory200 stream200", "context200 knowledge200"],
    ),
    (
        ("universe200 memory200 stream200 context200 knowledge200 vector200", 6),
        ["universe200", "memory200", "stream200", "context200", "knowledge200", "vector200"],
    ),
    (
        ("universe200 memory200 stream200 context200 knowledge200 vector200", 10),
        ["universe200", "memory200", "stream200", "context200", "knowledge200", "vector200"],
    ),
    (
        ("universe200 memory200 stream200 context200 knowledge200 vector200", 18),
        ["universe200", "memory200", "stream200", "context200", "knowledge200", "vector200"],
    ),
    (
        ("universe200 memory200 stream200 context200 knowledge200 vector200", 28),
        ["universe200 memory200", "stream200 context200", "knowledge200 vector200"],
    ),
    (
        ("memory200 stream200 context200 knowledge200 vector200 processor200", 6),
        ["memory200", "stream200", "context200", "knowledge200", "vector200", "processor200"],
    ),
    (
        ("memory200 stream200 context200 knowledge200 vector200 processor200", 10),
        ["memory200", "stream200", "context200", "knowledge200", "vector200", "processor200"],
    ),
    (
        ("memory200 stream200 context200 knowledge200 vector200 processor200", 18),
        ["memory200", "stream200", "context200", "knowledge200", "vector200", "processor200"],
    ),
    (
        ("memory200 stream200 context200 knowledge200 vector200 processor200", 28),
        ["memory200 stream200", "context200 knowledge200", "vector200 processor200"],
    ),
    (
        ("stream200 context200 knowledge200 vector200 processor200 reasoning200", 6),
        ["stream200", "context200", "knowledge200", "vector200", "processor200", "reasoning200"],
    ),
    (
        ("stream200 context200 knowledge200 vector200 processor200 reasoning200", 10),
        ["stream200", "context200", "knowledge200", "vector200", "processor200", "reasoning200"],
    ),
    (
        ("stream200 context200 knowledge200 vector200 processor200 reasoning200", 18),
        ["stream200", "context200", "knowledge200", "vector200", "processor200", "reasoning200"],
    ),
    (
        ("stream200 context200 knowledge200 vector200 processor200 reasoning200", 28),
        ["stream200 context200", "knowledge200 vector200", "processor200 reasoning200"],
    ),
    (
        ("context200 knowledge200 vector200 processor200 reasoning200 machine200", 6),
        ["context200", "knowledge200", "vector200", "processor200", "reasoning200", "machine200"],
    ),
    (
        ("context200 knowledge200 vector200 processor200 reasoning200 machine200", 10),
        ["context200", "knowledge200", "vector200", "processor200", "reasoning200", "machine200"],
    ),
    (
        ("context200 knowledge200 vector200 processor200 reasoning200 machine200", 18),
        ["context200", "knowledge200", "vector200", "processor200", "reasoning200", "machine200"],
    ),
    (
        ("context200 knowledge200 vector200 processor200 reasoning200 machine200", 28),
        ["context200 knowledge200", "vector200 processor200", "reasoning200 machine200"],
    ),
    (
        ("knowledge200 vector200 processor200 reasoning200 machine200 learning200", 6),
        ["knowledge200", "vector200", "processor200", "reasoning200", "machine200", "learning200"],
    ),
    (
        ("knowledge200 vector200 processor200 reasoning200 machine200 learning200", 10),
        ["knowledge200", "vector200", "processor200", "reasoning200", "machine200", "learning200"],
    ),
    (
        ("knowledge200 vector200 processor200 reasoning200 machine200 learning200", 18),
        ["knowledge200", "vector200", "processor200", "reasoning200", "machine200", "learning200"],
    ),
    (
        ("knowledge200 vector200 processor200 reasoning200 machine200 learning200", 28),
        ["knowledge200 vector200", "processor200 reasoning200", "machine200 learning200"],
    ),
    (
        ("vector200 processor200 reasoning200 machine200 learning200 model200", 6),
        ["vector200", "processor200", "reasoning200", "machine200", "learning200", "model200"],
    ),
    (
        ("vector200 processor200 reasoning200 machine200 learning200 model200", 10),
        ["vector200", "processor200", "reasoning200", "machine200", "learning200", "model200"],
    ),
    (
        ("vector200 processor200 reasoning200 machine200 learning200 model200", 18),
        ["vector200", "processor200", "reasoning200", "machine200", "learning200", "model200"],
    ),
    (
        ("vector200 processor200 reasoning200 machine200 learning200 model200", 28),
        ["vector200 processor200", "reasoning200 machine200", "learning200 model200"],
    ),
    (
        ("processor200 reasoning200 machine200 learning200 model200 token200", 6),
        ["processor200", "reasoning200", "machine200", "learning200", "model200", "token200"],
    ),
    (
        ("processor200 reasoning200 machine200 learning200 model200 token200", 10),
        ["processor200", "reasoning200", "machine200", "learning200", "model200", "token200"],
    ),
    (
        ("processor200 reasoning200 machine200 learning200 model200 token200", 18),
        ["processor200", "reasoning200", "machine200", "learning200", "model200 token200"],
    ),
    (
        ("processor200 reasoning200 machine200 learning200 model200 token200", 28),
        ["processor200 reasoning200", "machine200 learning200", "model200 token200"],
    ),
    (
        ("reasoning200 machine200 learning200 model200 token200 prompt200", 6),
        ["reasoning200", "machine200", "learning200", "model200", "token200", "prompt200"],
    ),
    (
        ("reasoning200 machine200 learning200 model200 token200 prompt200", 10),
        ["reasoning200", "machine200", "learning200", "model200", "token200", "prompt200"],
    ),
    (
        ("reasoning200 machine200 learning200 model200 token200 prompt200", 18),
        ["reasoning200", "machine200", "learning200", "model200 token200", "prompt200"],
    ),
    (
        ("reasoning200 machine200 learning200 model200 token200 prompt200", 28),
        ["reasoning200 machine200", "learning200 model200", "token200 prompt200"],
    ),
    (
        ("machine200 learning200 model200 token200 prompt200 session200", 6),
        ["machine200", "learning200", "model200", "token200", "prompt200", "session200"],
    ),
    (
        ("machine200 learning200 model200 token200 prompt200 session200", 10),
        ["machine200", "learning200", "model200", "token200", "prompt200", "session200"],
    ),
    (
        ("machine200 learning200 model200 token200 prompt200 session200", 18),
        ["machine200", "learning200", "model200 token200", "prompt200", "session200"],
    ),
    (
        ("machine200 learning200 model200 token200 prompt200 session200", 28),
        ["machine200 learning200", "model200 token200 prompt200", "session200"],
    ),
    (
        ("learning200 model200 token200 prompt200 session200 library200", 6),
        ["learning200", "model200", "token200", "prompt200", "session200", "library200"],
    ),
    (
        ("learning200 model200 token200 prompt200 session200 library200", 10),
        ["learning200", "model200", "token200", "prompt200", "session200", "library200"],
    ),
    (
        ("learning200 model200 token200 prompt200 session200 library200", 18),
        ["learning200", "model200 token200", "prompt200", "session200", "library200"],
    ),
    (
        ("learning200 model200 token200 prompt200 session200 library200", 28),
        ["learning200 model200", "token200 prompt200", "session200 library200"],
    ),
    (
        ("model200 token200 prompt200 session200 library200 service200", 6),
        ["model200", "token200", "prompt200", "session200", "library200", "service200"],
    ),
    (
        ("model200 token200 prompt200 session200 library200 service200", 10),
        ["model200", "token200", "prompt200", "session200", "library200", "service200"],
    ),
    (
        ("model200 token200 prompt200 session200 library200 service200", 18),
        ["model200 token200", "prompt200", "session200", "library200", "service200"],
    ),
    (
        ("model200 token200 prompt200 session200 library200 service200", 28),
        ["model200 token200 prompt200", "session200 library200", "service200"],
    ),
    (
        ("token200 prompt200 session200 library200 service200 gateway200", 6),
        ["token200", "prompt200", "session200", "library200", "service200", "gateway200"],
    ),
    (
        ("token200 prompt200 session200 library200 service200 gateway200", 10),
        ["token200", "prompt200", "session200", "library200", "service200", "gateway200"],
    ),
    (
        ("token200 prompt200 session200 library200 service200 gateway200", 18),
        ["token200 prompt200", "session200", "library200", "service200", "gateway200"],
    ),
    (
        ("token200 prompt200 session200 library200 service200 gateway200", 28),
        ["token200 prompt200", "session200 library200", "service200 gateway200"],
    ),
    (
        ("prompt200 session200 library200 service200 gateway200 storage200", 6),
        ["prompt200", "session200", "library200", "service200", "gateway200", "storage200"],
    ),
    (
        ("prompt200 session200 library200 service200 gateway200 storage200", 10),
        ["prompt200", "session200", "library200", "service200", "gateway200", "storage200"],
    ),
    (
        ("prompt200 session200 library200 service200 gateway200 storage200", 18),
        ["prompt200", "session200", "library200", "service200", "gateway200", "storage200"],
    ),
    (
        ("prompt200 session200 library200 service200 gateway200 storage200", 28),
        ["prompt200 session200", "library200 service200", "gateway200 storage200"],
    ),
    (
        ("session200 library200 service200 gateway200 storage200 network200", 6),
        ["session200", "library200", "service200", "gateway200", "storage200", "network200"],
    ),
    (
        ("session200 library200 service200 gateway200 storage200 network200", 10),
        ["session200", "library200", "service200", "gateway200", "storage200", "network200"],
    ),
    (
        ("session200 library200 service200 gateway200 storage200 network200", 18),
        ["session200", "library200", "service200", "gateway200", "storage200", "network200"],
    ),
    (
        ("session200 library200 service200 gateway200 storage200 network200", 28),
        ["session200 library200", "service200 gateway200", "storage200 network200"],
    ),
    (
        ("library200 service200 gateway200 storage200 network200 latency200", 6),
        ["library200", "service200", "gateway200", "storage200", "network200", "latency200"],
    ),
    (
        ("library200 service200 gateway200 storage200 network200 latency200", 10),
        ["library200", "service200", "gateway200", "storage200", "network200", "latency200"],
    ),
    (
        ("library200 service200 gateway200 storage200 network200 latency200", 18),
        ["library200", "service200", "gateway200", "storage200", "network200", "latency200"],
    ),
    (
        ("library200 service200 gateway200 storage200 network200 latency200", 28),
        ["library200 service200", "gateway200 storage200", "network200 latency200"],
    ),
    (
        ("service200 gateway200 storage200 network200 latency200 buffer200", 6),
        ["service200", "gateway200", "storage200", "network200", "latency200", "buffer200"],
    ),
    (
        ("service200 gateway200 storage200 network200 latency200 buffer200", 10),
        ["service200", "gateway200", "storage200", "network200", "latency200", "buffer200"],
    ),
    (
        ("service200 gateway200 storage200 network200 latency200 buffer200", 18),
        ["service200", "gateway200", "storage200", "network200", "latency200", "buffer200"],
    ),
    (
        ("service200 gateway200 storage200 network200 latency200 buffer200", 28),
        ["service200 gateway200", "storage200 network200", "latency200 buffer200"],
    ),
    (
        ("gateway200 storage200 network200 latency200 buffer200 queue200", 6),
        ["gateway200", "storage200", "network200", "latency200", "buffer200", "queue200"],
    ),
    (
        ("gateway200 storage200 network200 latency200 buffer200 queue200", 10),
        ["gateway200", "storage200", "network200", "latency200", "buffer200", "queue200"],
    ),
    (
        ("gateway200 storage200 network200 latency200 buffer200 queue200", 18),
        ["gateway200", "storage200", "network200", "latency200", "buffer200 queue200"],
    ),
    (
        ("gateway200 storage200 network200 latency200 buffer200 queue200", 28),
        ["gateway200 storage200", "network200 latency200", "buffer200 queue200"],
    ),
    (
        ("storage200 network200 latency200 buffer200 queue200 worker200", 6),
        ["storage200", "network200", "latency200", "buffer200", "queue200", "worker200"],
    ),
    (
        ("storage200 network200 latency200 buffer200 queue200 worker200", 10),
        ["storage200", "network200", "latency200", "buffer200", "queue200", "worker200"],
    ),
    (
        ("storage200 network200 latency200 buffer200 queue200 worker200", 18),
        ["storage200", "network200", "latency200", "buffer200 queue200", "worker200"],
    ),
    (
        ("storage200 network200 latency200 buffer200 queue200 worker200", 28),
        ["storage200 network200", "latency200 buffer200", "queue200 worker200"],
    ),
    (
        ("network200 latency200 buffer200 queue200 worker200 kernel200", 6),
        ["network200", "latency200", "buffer200", "queue200", "worker200", "kernel200"],
    ),
    (
        ("network200 latency200 buffer200 queue200 worker200 kernel200", 10),
        ["network200", "latency200", "buffer200", "queue200", "worker200", "kernel200"],
    ),
    (
        ("network200 latency200 buffer200 queue200 worker200 kernel200", 18),
        ["network200", "latency200", "buffer200 queue200", "worker200", "kernel200"],
    ),
    (
        ("network200 latency200 buffer200 queue200 worker200 kernel200", 28),
        ["network200 latency200", "buffer200 queue200 worker200", "kernel200"],
    ),
    (
        ("latency200 buffer200 queue200 worker200 kernel200 signal200", 6),
        ["latency200", "buffer200", "queue200", "worker200", "kernel200", "signal200"],
    ),
    (
        ("latency200 buffer200 queue200 worker200 kernel200 signal200", 10),
        ["latency200", "buffer200", "queue200", "worker200", "kernel200", "signal200"],
    ),
    (
        ("latency200 buffer200 queue200 worker200 kernel200 signal200", 18),
        ["latency200", "buffer200 queue200", "worker200", "kernel200", "signal200"],
    ),
    (
        ("latency200 buffer200 queue200 worker200 kernel200 signal200", 28),
        ["latency200 buffer200", "queue200 worker200 kernel200", "signal200"],
    ),
    (
        ("buffer200 queue200 worker200 kernel200 signal200 packet200", 6),
        ["buffer200", "queue200", "worker200", "kernel200", "signal200", "packet200"],
    ),
    (
        ("buffer200 queue200 worker200 kernel200 signal200 packet200", 10),
        ["buffer200", "queue200", "worker200", "kernel200", "signal200", "packet200"],
    ),
    (
        ("buffer200 queue200 worker200 kernel200 signal200 packet200", 18),
        ["buffer200 queue200", "worker200", "kernel200", "signal200", "packet200"],
    ),
    (
        ("buffer200 queue200 worker200 kernel200 signal200 packet200", 28),
        ["buffer200 queue200 worker200", "kernel200 signal200", "packet200"],
    ),
    (
        ("queue200 worker200 kernel200 signal200 packet200 router200", 6),
        ["queue200", "worker200", "kernel200", "signal200", "packet200", "router200"],
    ),
    (
        ("queue200 worker200 kernel200 signal200 packet200 router200", 10),
        ["queue200", "worker200", "kernel200", "signal200", "packet200", "router200"],
    ),
    (
        ("queue200 worker200 kernel200 signal200 packet200 router200", 18),
        ["queue200 worker200", "kernel200", "signal200", "packet200", "router200"],
    ),
    (
        ("queue200 worker200 kernel200 signal200 packet200 router200", 28),
        ["queue200 worker200 kernel200", "signal200 packet200", "router200"],
    ),
    (
        ("worker200 kernel200 signal200 packet200 router200 cluster200", 6),
        ["worker200", "kernel200", "signal200", "packet200", "router200", "cluster200"],
    ),
    (
        ("worker200 kernel200 signal200 packet200 router200 cluster200", 10),
        ["worker200", "kernel200", "signal200", "packet200", "router200", "cluster200"],
    ),
    (
        ("worker200 kernel200 signal200 packet200 router200 cluster200", 18),
        ["worker200", "kernel200", "signal200", "packet200", "router200", "cluster200"],
    ),
    (
        ("worker200 kernel200 signal200 packet200 router200 cluster200", 28),
        ["worker200 kernel200", "signal200 packet200", "router200 cluster200"],
    ),
    (
        ("kernel200 signal200 packet200 router200 cluster200 mirror200", 6),
        ["kernel200", "signal200", "packet200", "router200", "cluster200", "mirror200"],
    ),
    (
        ("kernel200 signal200 packet200 router200 cluster200 mirror200", 10),
        ["kernel200", "signal200", "packet200", "router200", "cluster200", "mirror200"],
    ),
    (
        ("kernel200 signal200 packet200 router200 cluster200 mirror200", 18),
        ["kernel200", "signal200", "packet200", "router200", "cluster200", "mirror200"],
    ),
    (
        ("kernel200 signal200 packet200 router200 cluster200 mirror200", 28),
        ["kernel200 signal200", "packet200 router200", "cluster200 mirror200"],
    ),
    (
        ("signal200 packet200 router200 cluster200 mirror200 filter200", 6),
        ["signal200", "packet200", "router200", "cluster200", "mirror200", "filter200"],
    ),
    (
        ("signal200 packet200 router200 cluster200 mirror200 filter200", 10),
        ["signal200", "packet200", "router200", "cluster200", "mirror200", "filter200"],
    ),
    (
        ("signal200 packet200 router200 cluster200 mirror200 filter200", 18),
        ["signal200", "packet200", "router200", "cluster200", "mirror200", "filter200"],
    ),
    (
        ("signal200 packet200 router200 cluster200 mirror200 filter200", 28),
        ["signal200 packet200", "router200 cluster200", "mirror200 filter200"],
    ),
    (
        ("packet200 router200 cluster200 mirror200 filter200 ranking200", 6),
        ["packet200", "router200", "cluster200", "mirror200", "filter200", "ranking200"],
    ),
    (
        ("packet200 router200 cluster200 mirror200 filter200 ranking200", 10),
        ["packet200", "router200", "cluster200", "mirror200", "filter200", "ranking200"],
    ),
    (
        ("packet200 router200 cluster200 mirror200 filter200 ranking200", 18),
        ["packet200", "router200", "cluster200", "mirror200", "filter200", "ranking200"],
    ),
    (
        ("packet200 router200 cluster200 mirror200 filter200 ranking200", 28),
        ["packet200 router200", "cluster200 mirror200", "filter200 ranking200"],
    ),
    (
        ("router200 cluster200 mirror200 filter200 ranking200 encoding200", 6),
        ["router200", "cluster200", "mirror200", "filter200", "ranking200", "encoding200"],
    ),
    (
        ("router200 cluster200 mirror200 filter200 ranking200 encoding200", 10),
        ["router200", "cluster200", "mirror200", "filter200", "ranking200", "encoding200"],
    ),
    (
        ("router200 cluster200 mirror200 filter200 ranking200 encoding200", 18),
        ["router200", "cluster200", "mirror200", "filter200", "ranking200", "encoding200"],
    ),
    (
        ("router200 cluster200 mirror200 filter200 ranking200 encoding200", 28),
        ["router200 cluster200", "mirror200 filter200", "ranking200 encoding200"],
    ),
    (
        ("cluster200 mirror200 filter200 ranking200 encoding200 mapping200", 6),
        ["cluster200", "mirror200", "filter200", "ranking200", "encoding200", "mapping200"],
    ),
    (
        ("cluster200 mirror200 filter200 ranking200 encoding200 mapping200", 10),
        ["cluster200", "mirror200", "filter200", "ranking200", "encoding200", "mapping200"],
    ),
    (
        ("cluster200 mirror200 filter200 ranking200 encoding200 mapping200", 18),
        ["cluster200", "mirror200", "filter200", "ranking200", "encoding200", "mapping200"],
    ),
    (
        ("cluster200 mirror200 filter200 ranking200 encoding200 mapping200", 28),
        ["cluster200 mirror200", "filter200 ranking200", "encoding200 mapping200"],
    ),
    (
        ("mirror200 filter200 ranking200 encoding200 mapping200 record200", 6),
        ["mirror200", "filter200", "ranking200", "encoding200", "mapping200", "record200"],
    ),
    (
        ("mirror200 filter200 ranking200 encoding200 mapping200 record200", 10),
        ["mirror200", "filter200", "ranking200", "encoding200", "mapping200", "record200"],
    ),
    (
        ("mirror200 filter200 ranking200 encoding200 mapping200 record200", 18),
        ["mirror200", "filter200", "ranking200", "encoding200", "mapping200", "record200"],
    ),
    (
        ("mirror200 filter200 ranking200 encoding200 mapping200 record200", 28),
        ["mirror200 filter200", "ranking200 encoding200", "mapping200 record200"],
    ),
    (
        ("filter200 ranking200 encoding200 mapping200 record200 candle200", 6),
        ["filter200", "ranking200", "encoding200", "mapping200", "record200", "candle200"],
    ),
    (
        ("filter200 ranking200 encoding200 mapping200 record200 candle200", 10),
        ["filter200", "ranking200", "encoding200", "mapping200", "record200", "candle200"],
    ),
    (
        ("filter200 ranking200 encoding200 mapping200 record200 candle200", 18),
        ["filter200", "ranking200", "encoding200", "mapping200", "record200", "candle200"],
    ),
    (
        ("filter200 ranking200 encoding200 mapping200 record200 candle200", 28),
        ["filter200 ranking200", "encoding200 mapping200", "record200 candle200"],
    ),
    (
        ("ranking200 encoding200 mapping200 record200 candle200 thread200", 6),
        ["ranking200", "encoding200", "mapping200", "record200", "candle200", "thread200"],
    ),
    (
        ("ranking200 encoding200 mapping200 record200 candle200 thread200", 10),
        ["ranking200", "encoding200", "mapping200", "record200", "candle200", "thread200"],
    ),
    (
        ("ranking200 encoding200 mapping200 record200 candle200 thread200", 18),
        ["ranking200", "encoding200", "mapping200", "record200", "candle200", "thread200"],
    ),
    (
        ("ranking200 encoding200 mapping200 record200 candle200 thread200", 28),
        ["ranking200 encoding200", "mapping200 record200", "candle200 thread200"],
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
