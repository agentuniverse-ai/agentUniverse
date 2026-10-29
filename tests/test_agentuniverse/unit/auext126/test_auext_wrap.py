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
        ("round 126: the quick brown fox jumps over the lazy dog", 4),
        ["round", "126:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 126: the quick brown fox jumps over the lazy dog", 8),
        ["round", "126: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 126: the quick brown fox jumps over the lazy dog", 12),
        ["round 126:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 126: the quick brown fox jumps over the lazy dog", 16),
        ["round 126: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 126: the quick brown fox jumps over the lazy dog", 24),
        ["round 126: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 126: the quick brown fox jumps over the lazy dog", 32),
        ["round 126: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 126: agentuniverse is a framework for multi agents", 4),
        ["round", "126:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 126: agentuniverse is a framework for multi agents", 8),
        ["round", "126:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 126: agentuniverse is a framework for multi agents", 12),
        ["round 126:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 126: agentuniverse is a framework for multi agents", 16),
        ["round 126:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 126: agentuniverse is a framework for multi agents", 24),
        ["round 126: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 126: agentuniverse is a framework for multi agents", 32),
        ["round 126: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 126: knowledge stored as vectors enables retrieval", 4),
        ["round", "126:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 126: knowledge stored as vectors enables retrieval", 8),
        ["round", "126:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 126: knowledge stored as vectors enables retrieval", 12),
        ["round 126:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 126: knowledge stored as vectors enables retrieval", 16),
        ["round 126:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 126: knowledge stored as vectors enables retrieval", 24),
        ["round 126: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 126: knowledge stored as vectors enables retrieval", 32),
        ["round 126: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 126: the processor reads the record then stops", 4),
        ["round", "126:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 126: the processor reads the record then stops", 8),
        ["round", "126: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 126: the processor reads the record then stops", 12),
        ["round 126:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 126: the processor reads the record then stops", 16),
        ["round 126: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 126: the processor reads the record then stops", 24),
        ["round 126: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 126: the processor reads the record then stops", 32),
        ["round 126: the processor reads", "the record then stops"],
    ),
    (
        ("round 126: a worker pulls the next task from the queue", 4),
        ["round", "126:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 126: a worker pulls the next task from the queue", 8),
        ["round", "126: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 126: a worker pulls the next task from the queue", 12),
        ["round 126: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 126: a worker pulls the next task from the queue", 16),
        ["round 126: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 126: a worker pulls the next task from the queue", 24),
        ["round 126: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 126: a worker pulls the next task from the queue", 32),
        ["round 126: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 126: signals travel through the network layer", 4),
        ["round", "126:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 126: signals travel through the network layer", 8),
        ["round", "126:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 126: signals travel through the network layer", 12),
        ["round 126:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 126: signals travel through the network layer", 16),
        ["round 126:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 126: signals travel through the network layer", 24),
        ["round 126: signals", "travel through the", "network layer"],
    ),
    (
        ("round 126: signals travel through the network layer", 32),
        ["round 126: signals travel", "through the network layer"],
    ),
    (
        ("round 126: the gateway routes each request by policy", 4),
        ["round", "126:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 126: the gateway routes each request by policy", 8),
        ["round", "126: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 126: the gateway routes each request by policy", 12),
        ["round 126:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 126: the gateway routes each request by policy", 16),
        ["round 126: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 126: the gateway routes each request by policy", 24),
        ["round 126: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 126: the gateway routes each request by policy", 32),
        ["round 126: the gateway routes", "each request by policy"],
    ),
    (
        ("round 126: memory grows until the buffer is full", 4),
        ["round", "126:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 126: memory grows until the buffer is full", 8),
        ["round", "126:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 126: memory grows until the buffer is full", 12),
        ["round 126:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 126: memory grows until the buffer is full", 16),
        ["round 126:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 126: memory grows until the buffer is full", 24), ["round 126: memory grows", "until the buffer is full"]),
    (("round 126: memory grows until the buffer is full", 32), ["round 126: memory grows until", "the buffer is full"]),
    (
        ("round 126: the cluster mirrors every packet twice", 4),
        ["round", "126:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 126: the cluster mirrors every packet twice", 8),
        ["round", "126: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 126: the cluster mirrors every packet twice", 12),
        ["round 126:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 126: the cluster mirrors every packet twice", 16),
        ["round 126: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 126: the cluster mirrors every packet twice", 24),
        ["round 126: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 126: the cluster mirrors every packet twice", 32),
        ["round 126: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 126: ranking uses tokens learned from the corpus", 4),
        ["round", "126:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 126: ranking uses tokens learned from the corpus", 8),
        ["round", "126:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 126: ranking uses tokens learned from the corpus", 12),
        ["round 126:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 126: ranking uses tokens learned from the corpus", 16),
        ["round 126:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 126: ranking uses tokens learned from the corpus", 24),
        ["round 126: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 126: ranking uses tokens learned from the corpus", 32),
        ["round 126: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 126: a long session ends when the candle dies", 4),
        ["round", "126:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 126: a long session ends when the candle dies", 8),
        ["round", "126: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 126: a long session ends when the candle dies", 12),
        ["round 126: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 126: a long session ends when the candle dies", 16),
        ["round 126: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 126: a long session ends when the candle dies", 24),
        ["round 126: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 126: a long session ends when the candle dies", 32),
        ["round 126: a long session ends", "when the candle dies"],
    ),
    (
        ("round 126: encode the prompt then map the result", 4),
        ["round", "126:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 126: encode the prompt then map the result", 8),
        ["round", "126:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 126: encode the prompt then map the result", 12),
        ["round 126:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 126: encode the prompt then map the result", 16),
        ["round 126:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 126: encode the prompt then map the result", 24),
        ["round 126: encode the", "prompt then map the", "result"],
    ),
    (("round 126: encode the prompt then map the result", 32), ["round 126: encode the prompt", "then map the result"]),
    (
        ("round 126: the kernel wakes the worker at dawn", 4),
        ["round", "126:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 126: the kernel wakes the worker at dawn", 8),
        ["round", "126: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 126: the kernel wakes the worker at dawn", 12),
        ["round 126:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 126: the kernel wakes the worker at dawn", 16), ["round 126: the", "kernel wakes the", "worker at dawn"]),
    (("round 126: the kernel wakes the worker at dawn", 24), ["round 126: the kernel", "wakes the worker at dawn"]),
    (("round 126: the kernel wakes the worker at dawn", 32), ["round 126: the kernel wakes the", "worker at dawn"]),
    (
        ("round 126: service latency drops after the patch", 4),
        ["round", "126:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 126: service latency drops after the patch", 8),
        ["round", "126:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 126: service latency drops after the patch", 12),
        ["round 126:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 126: service latency drops after the patch", 16),
        ["round 126:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 126: service latency drops after the patch", 24),
        ["round 126: service", "latency drops after the", "patch"],
    ),
    (("round 126: service latency drops after the patch", 32), ["round 126: service latency drops", "after the patch"]),
    (
        ("round 126: the library caches every vector it sees", 4),
        ["round", "126:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 126: the library caches every vector it sees", 8),
        ["round", "126: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 126: the library caches every vector it sees", 12),
        ["round 126:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 126: the library caches every vector it sees", 16),
        ["round 126: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 126: the library caches every vector it sees", 24),
        ["round 126: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 126: the library caches every vector it sees", 32),
        ["round 126: the library caches", "every vector it sees"],
    ),
    (
        ("round 126: agents argue then the debate resolves", 4),
        ["round", "126:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 126: agents argue then the debate resolves", 8),
        ["round", "126:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 126: agents argue then the debate resolves", 12),
        ["round 126:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 126: agents argue then the debate resolves", 16),
        ["round 126:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 126: agents argue then the debate resolves", 24), ["round 126: agents argue", "then the debate resolves"]),
    (("round 126: agents argue then the debate resolves", 32), ["round 126: agents argue then the", "debate resolves"]),
    (
        ("round 126: the filter keeps only strong matches", 4),
        ["round", "126:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 126: the filter keeps only strong matches", 8),
        ["round", "126: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 126: the filter keeps only strong matches", 12),
        ["round 126:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 126: the filter keeps only strong matches", 16),
        ["round 126: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 126: the filter keeps only strong matches", 24),
        ["round 126: the filter", "keeps only strong", "matches"],
    ),
    (("round 126: the filter keeps only strong matches", 32), ["round 126: the filter keeps only", "strong matches"]),
    (
        ("round 126: the model answers with a short reply", 4),
        ["round", "126:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 126: the model answers with a short reply", 8),
        ["round", "126: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 126: the model answers with a short reply", 12),
        ["round 126:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 126: the model answers with a short reply", 16),
        ["round 126: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 126: the model answers with a short reply", 24),
        ["round 126: the model", "answers with a short", "reply"],
    ),
    (("round 126: the model answers with a short reply", 32), ["round 126: the model answers", "with a short reply"]),
    (
        ("round 126: the recorder stores the reasoning trace", 4),
        ["round", "126:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 126: the recorder stores the reasoning trace", 8),
        ["round", "126: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 126: the recorder stores the reasoning trace", 12),
        ["round 126:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 126: the recorder stores the reasoning trace", 16),
        ["round 126: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 126: the recorder stores the reasoning trace", 24),
        ["round 126: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 126: the recorder stores the reasoning trace", 32),
        ["round 126: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 126: the angel watches the processor run", 4),
        ["round", "126:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 126: the angel watches the processor run", 8),
        ["round", "126: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 126: the angel watches the processor run", 12),
        ["round 126:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 126: the angel watches the processor run", 16),
        ["round 126: the", "angel watches", "the processor", "run"],
    ),
    (("round 126: the angel watches the processor run", 24), ["round 126: the angel", "watches the processor", "run"]),
    (("round 126: the angel watches the processor run", 32), ["round 126: the angel watches the", "processor run"]),
    (
        ("round 126: angle of the vector decides the match", 4),
        ["round", "126:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 126: angle of the vector decides the match", 8),
        ["round", "126:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 126: angle of the vector decides the match", 12),
        ["round 126:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 126: angle of the vector decides the match", 16),
        ["round 126: angle", "of the vector", "decides the", "match"],
    ),
    (("round 126: angle of the vector decides the match", 24), ["round 126: angle of the", "vector decides the match"]),
    (("round 126: angle of the vector decides the match", 32), ["round 126: angle of the vector", "decides the match"]),
    (
        ("round 126: the candle burns twice as long at night", 4),
        ["round", "126:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 126: the candle burns twice as long at night", 8),
        ["round", "126: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 126: the candle burns twice as long at night", 12),
        ["round 126:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 126: the candle burns twice as long at night", 16),
        ["round 126: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 126: the candle burns twice as long at night", 24),
        ["round 126: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 126: the candle burns twice as long at night", 32),
        ["round 126: the candle burns", "twice as long at night"],
    ),
    (
        ("round 126: a mirror of the universe in one line", 4),
        ["round", "126:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 126: a mirror of the universe in one line", 8),
        ["round", "126: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 126: a mirror of the universe in one line", 12),
        ["round 126: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 126: a mirror of the universe in one line", 16),
        ["round 126: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 126: a mirror of the universe in one line", 24), ["round 126: a mirror of", "the universe in one line"]),
    (("round 126: a mirror of the universe in one line", 32), ["round 126: a mirror of the", "universe in one line"]),
    (
        ("round 126: the queue drains before the storm", 4),
        ["round", "126:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 126: the queue drains before the storm", 8),
        ["round", "126: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 126: the queue drains before the storm", 12),
        ["round 126:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 126: the queue drains before the storm", 16), ["round 126: the", "queue drains", "before the storm"]),
    (("round 126: the queue drains before the storm", 24), ["round 126: the queue", "drains before the storm"]),
    (("round 126: the queue drains before the storm", 32), ["round 126: the queue drains", "before the storm"]),
    (
        ("kitten126 sitting126 agent126 angle126 universe126 memory126", 6),
        ["kitten126", "sitting126", "agent126", "angle126", "universe126", "memory126"],
    ),
    (
        ("kitten126 sitting126 agent126 angle126 universe126 memory126", 10),
        ["kitten126", "sitting126", "agent126", "angle126", "universe126", "memory126"],
    ),
    (
        ("kitten126 sitting126 agent126 angle126 universe126 memory126", 18),
        ["kitten126", "sitting126", "agent126 angle126", "universe126", "memory126"],
    ),
    (
        ("kitten126 sitting126 agent126 angle126 universe126 memory126", 28),
        ["kitten126 sitting126", "agent126 angle126", "universe126 memory126"],
    ),
    (
        ("sitting126 agent126 angle126 universe126 memory126 stream126", 6),
        ["sitting126", "agent126", "angle126", "universe126", "memory126", "stream126"],
    ),
    (
        ("sitting126 agent126 angle126 universe126 memory126 stream126", 10),
        ["sitting126", "agent126", "angle126", "universe126", "memory126", "stream126"],
    ),
    (
        ("sitting126 agent126 angle126 universe126 memory126 stream126", 18),
        ["sitting126", "agent126 angle126", "universe126", "memory126", "stream126"],
    ),
    (
        ("sitting126 agent126 angle126 universe126 memory126 stream126", 28),
        ["sitting126 agent126 angle126", "universe126 memory126", "stream126"],
    ),
    (
        ("agent126 angle126 universe126 memory126 stream126 context126", 6),
        ["agent126", "angle126", "universe126", "memory126", "stream126", "context126"],
    ),
    (
        ("agent126 angle126 universe126 memory126 stream126 context126", 10),
        ["agent126", "angle126", "universe126", "memory126", "stream126", "context126"],
    ),
    (
        ("agent126 angle126 universe126 memory126 stream126 context126", 18),
        ["agent126 angle126", "universe126", "memory126", "stream126", "context126"],
    ),
    (
        ("agent126 angle126 universe126 memory126 stream126 context126", 28),
        ["agent126 angle126", "universe126 memory126", "stream126 context126"],
    ),
    (
        ("angle126 universe126 memory126 stream126 context126 knowledge126", 6),
        ["angle126", "universe126", "memory126", "stream126", "context126", "knowledge126"],
    ),
    (
        ("angle126 universe126 memory126 stream126 context126 knowledge126", 10),
        ["angle126", "universe126", "memory126", "stream126", "context126", "knowledge126"],
    ),
    (
        ("angle126 universe126 memory126 stream126 context126 knowledge126", 18),
        ["angle126", "universe126", "memory126", "stream126", "context126", "knowledge126"],
    ),
    (
        ("angle126 universe126 memory126 stream126 context126 knowledge126", 28),
        ["angle126 universe126", "memory126 stream126", "context126 knowledge126"],
    ),
    (
        ("universe126 memory126 stream126 context126 knowledge126 vector126", 6),
        ["universe126", "memory126", "stream126", "context126", "knowledge126", "vector126"],
    ),
    (
        ("universe126 memory126 stream126 context126 knowledge126 vector126", 10),
        ["universe126", "memory126", "stream126", "context126", "knowledge126", "vector126"],
    ),
    (
        ("universe126 memory126 stream126 context126 knowledge126 vector126", 18),
        ["universe126", "memory126", "stream126", "context126", "knowledge126", "vector126"],
    ),
    (
        ("universe126 memory126 stream126 context126 knowledge126 vector126", 28),
        ["universe126 memory126", "stream126 context126", "knowledge126 vector126"],
    ),
    (
        ("memory126 stream126 context126 knowledge126 vector126 processor126", 6),
        ["memory126", "stream126", "context126", "knowledge126", "vector126", "processor126"],
    ),
    (
        ("memory126 stream126 context126 knowledge126 vector126 processor126", 10),
        ["memory126", "stream126", "context126", "knowledge126", "vector126", "processor126"],
    ),
    (
        ("memory126 stream126 context126 knowledge126 vector126 processor126", 18),
        ["memory126", "stream126", "context126", "knowledge126", "vector126", "processor126"],
    ),
    (
        ("memory126 stream126 context126 knowledge126 vector126 processor126", 28),
        ["memory126 stream126", "context126 knowledge126", "vector126 processor126"],
    ),
    (
        ("stream126 context126 knowledge126 vector126 processor126 reasoning126", 6),
        ["stream126", "context126", "knowledge126", "vector126", "processor126", "reasoning126"],
    ),
    (
        ("stream126 context126 knowledge126 vector126 processor126 reasoning126", 10),
        ["stream126", "context126", "knowledge126", "vector126", "processor126", "reasoning126"],
    ),
    (
        ("stream126 context126 knowledge126 vector126 processor126 reasoning126", 18),
        ["stream126", "context126", "knowledge126", "vector126", "processor126", "reasoning126"],
    ),
    (
        ("stream126 context126 knowledge126 vector126 processor126 reasoning126", 28),
        ["stream126 context126", "knowledge126 vector126", "processor126 reasoning126"],
    ),
    (
        ("context126 knowledge126 vector126 processor126 reasoning126 machine126", 6),
        ["context126", "knowledge126", "vector126", "processor126", "reasoning126", "machine126"],
    ),
    (
        ("context126 knowledge126 vector126 processor126 reasoning126 machine126", 10),
        ["context126", "knowledge126", "vector126", "processor126", "reasoning126", "machine126"],
    ),
    (
        ("context126 knowledge126 vector126 processor126 reasoning126 machine126", 18),
        ["context126", "knowledge126", "vector126", "processor126", "reasoning126", "machine126"],
    ),
    (
        ("context126 knowledge126 vector126 processor126 reasoning126 machine126", 28),
        ["context126 knowledge126", "vector126 processor126", "reasoning126 machine126"],
    ),
    (
        ("knowledge126 vector126 processor126 reasoning126 machine126 learning126", 6),
        ["knowledge126", "vector126", "processor126", "reasoning126", "machine126", "learning126"],
    ),
    (
        ("knowledge126 vector126 processor126 reasoning126 machine126 learning126", 10),
        ["knowledge126", "vector126", "processor126", "reasoning126", "machine126", "learning126"],
    ),
    (
        ("knowledge126 vector126 processor126 reasoning126 machine126 learning126", 18),
        ["knowledge126", "vector126", "processor126", "reasoning126", "machine126", "learning126"],
    ),
    (
        ("knowledge126 vector126 processor126 reasoning126 machine126 learning126", 28),
        ["knowledge126 vector126", "processor126 reasoning126", "machine126 learning126"],
    ),
    (
        ("vector126 processor126 reasoning126 machine126 learning126 model126", 6),
        ["vector126", "processor126", "reasoning126", "machine126", "learning126", "model126"],
    ),
    (
        ("vector126 processor126 reasoning126 machine126 learning126 model126", 10),
        ["vector126", "processor126", "reasoning126", "machine126", "learning126", "model126"],
    ),
    (
        ("vector126 processor126 reasoning126 machine126 learning126 model126", 18),
        ["vector126", "processor126", "reasoning126", "machine126", "learning126", "model126"],
    ),
    (
        ("vector126 processor126 reasoning126 machine126 learning126 model126", 28),
        ["vector126 processor126", "reasoning126 machine126", "learning126 model126"],
    ),
    (
        ("processor126 reasoning126 machine126 learning126 model126 token126", 6),
        ["processor126", "reasoning126", "machine126", "learning126", "model126", "token126"],
    ),
    (
        ("processor126 reasoning126 machine126 learning126 model126 token126", 10),
        ["processor126", "reasoning126", "machine126", "learning126", "model126", "token126"],
    ),
    (
        ("processor126 reasoning126 machine126 learning126 model126 token126", 18),
        ["processor126", "reasoning126", "machine126", "learning126", "model126 token126"],
    ),
    (
        ("processor126 reasoning126 machine126 learning126 model126 token126", 28),
        ["processor126 reasoning126", "machine126 learning126", "model126 token126"],
    ),
    (
        ("reasoning126 machine126 learning126 model126 token126 prompt126", 6),
        ["reasoning126", "machine126", "learning126", "model126", "token126", "prompt126"],
    ),
    (
        ("reasoning126 machine126 learning126 model126 token126 prompt126", 10),
        ["reasoning126", "machine126", "learning126", "model126", "token126", "prompt126"],
    ),
    (
        ("reasoning126 machine126 learning126 model126 token126 prompt126", 18),
        ["reasoning126", "machine126", "learning126", "model126 token126", "prompt126"],
    ),
    (
        ("reasoning126 machine126 learning126 model126 token126 prompt126", 28),
        ["reasoning126 machine126", "learning126 model126", "token126 prompt126"],
    ),
    (
        ("machine126 learning126 model126 token126 prompt126 session126", 6),
        ["machine126", "learning126", "model126", "token126", "prompt126", "session126"],
    ),
    (
        ("machine126 learning126 model126 token126 prompt126 session126", 10),
        ["machine126", "learning126", "model126", "token126", "prompt126", "session126"],
    ),
    (
        ("machine126 learning126 model126 token126 prompt126 session126", 18),
        ["machine126", "learning126", "model126 token126", "prompt126", "session126"],
    ),
    (
        ("machine126 learning126 model126 token126 prompt126 session126", 28),
        ["machine126 learning126", "model126 token126 prompt126", "session126"],
    ),
    (
        ("learning126 model126 token126 prompt126 session126 library126", 6),
        ["learning126", "model126", "token126", "prompt126", "session126", "library126"],
    ),
    (
        ("learning126 model126 token126 prompt126 session126 library126", 10),
        ["learning126", "model126", "token126", "prompt126", "session126", "library126"],
    ),
    (
        ("learning126 model126 token126 prompt126 session126 library126", 18),
        ["learning126", "model126 token126", "prompt126", "session126", "library126"],
    ),
    (
        ("learning126 model126 token126 prompt126 session126 library126", 28),
        ["learning126 model126", "token126 prompt126", "session126 library126"],
    ),
    (
        ("model126 token126 prompt126 session126 library126 service126", 6),
        ["model126", "token126", "prompt126", "session126", "library126", "service126"],
    ),
    (
        ("model126 token126 prompt126 session126 library126 service126", 10),
        ["model126", "token126", "prompt126", "session126", "library126", "service126"],
    ),
    (
        ("model126 token126 prompt126 session126 library126 service126", 18),
        ["model126 token126", "prompt126", "session126", "library126", "service126"],
    ),
    (
        ("model126 token126 prompt126 session126 library126 service126", 28),
        ["model126 token126 prompt126", "session126 library126", "service126"],
    ),
    (
        ("token126 prompt126 session126 library126 service126 gateway126", 6),
        ["token126", "prompt126", "session126", "library126", "service126", "gateway126"],
    ),
    (
        ("token126 prompt126 session126 library126 service126 gateway126", 10),
        ["token126", "prompt126", "session126", "library126", "service126", "gateway126"],
    ),
    (
        ("token126 prompt126 session126 library126 service126 gateway126", 18),
        ["token126 prompt126", "session126", "library126", "service126", "gateway126"],
    ),
    (
        ("token126 prompt126 session126 library126 service126 gateway126", 28),
        ["token126 prompt126", "session126 library126", "service126 gateway126"],
    ),
    (
        ("prompt126 session126 library126 service126 gateway126 storage126", 6),
        ["prompt126", "session126", "library126", "service126", "gateway126", "storage126"],
    ),
    (
        ("prompt126 session126 library126 service126 gateway126 storage126", 10),
        ["prompt126", "session126", "library126", "service126", "gateway126", "storage126"],
    ),
    (
        ("prompt126 session126 library126 service126 gateway126 storage126", 18),
        ["prompt126", "session126", "library126", "service126", "gateway126", "storage126"],
    ),
    (
        ("prompt126 session126 library126 service126 gateway126 storage126", 28),
        ["prompt126 session126", "library126 service126", "gateway126 storage126"],
    ),
    (
        ("session126 library126 service126 gateway126 storage126 network126", 6),
        ["session126", "library126", "service126", "gateway126", "storage126", "network126"],
    ),
    (
        ("session126 library126 service126 gateway126 storage126 network126", 10),
        ["session126", "library126", "service126", "gateway126", "storage126", "network126"],
    ),
    (
        ("session126 library126 service126 gateway126 storage126 network126", 18),
        ["session126", "library126", "service126", "gateway126", "storage126", "network126"],
    ),
    (
        ("session126 library126 service126 gateway126 storage126 network126", 28),
        ["session126 library126", "service126 gateway126", "storage126 network126"],
    ),
    (
        ("library126 service126 gateway126 storage126 network126 latency126", 6),
        ["library126", "service126", "gateway126", "storage126", "network126", "latency126"],
    ),
    (
        ("library126 service126 gateway126 storage126 network126 latency126", 10),
        ["library126", "service126", "gateway126", "storage126", "network126", "latency126"],
    ),
    (
        ("library126 service126 gateway126 storage126 network126 latency126", 18),
        ["library126", "service126", "gateway126", "storage126", "network126", "latency126"],
    ),
    (
        ("library126 service126 gateway126 storage126 network126 latency126", 28),
        ["library126 service126", "gateway126 storage126", "network126 latency126"],
    ),
    (
        ("service126 gateway126 storage126 network126 latency126 buffer126", 6),
        ["service126", "gateway126", "storage126", "network126", "latency126", "buffer126"],
    ),
    (
        ("service126 gateway126 storage126 network126 latency126 buffer126", 10),
        ["service126", "gateway126", "storage126", "network126", "latency126", "buffer126"],
    ),
    (
        ("service126 gateway126 storage126 network126 latency126 buffer126", 18),
        ["service126", "gateway126", "storage126", "network126", "latency126", "buffer126"],
    ),
    (
        ("service126 gateway126 storage126 network126 latency126 buffer126", 28),
        ["service126 gateway126", "storage126 network126", "latency126 buffer126"],
    ),
    (
        ("gateway126 storage126 network126 latency126 buffer126 queue126", 6),
        ["gateway126", "storage126", "network126", "latency126", "buffer126", "queue126"],
    ),
    (
        ("gateway126 storage126 network126 latency126 buffer126 queue126", 10),
        ["gateway126", "storage126", "network126", "latency126", "buffer126", "queue126"],
    ),
    (
        ("gateway126 storage126 network126 latency126 buffer126 queue126", 18),
        ["gateway126", "storage126", "network126", "latency126", "buffer126 queue126"],
    ),
    (
        ("gateway126 storage126 network126 latency126 buffer126 queue126", 28),
        ["gateway126 storage126", "network126 latency126", "buffer126 queue126"],
    ),
    (
        ("storage126 network126 latency126 buffer126 queue126 worker126", 6),
        ["storage126", "network126", "latency126", "buffer126", "queue126", "worker126"],
    ),
    (
        ("storage126 network126 latency126 buffer126 queue126 worker126", 10),
        ["storage126", "network126", "latency126", "buffer126", "queue126", "worker126"],
    ),
    (
        ("storage126 network126 latency126 buffer126 queue126 worker126", 18),
        ["storage126", "network126", "latency126", "buffer126 queue126", "worker126"],
    ),
    (
        ("storage126 network126 latency126 buffer126 queue126 worker126", 28),
        ["storage126 network126", "latency126 buffer126", "queue126 worker126"],
    ),
    (
        ("network126 latency126 buffer126 queue126 worker126 kernel126", 6),
        ["network126", "latency126", "buffer126", "queue126", "worker126", "kernel126"],
    ),
    (
        ("network126 latency126 buffer126 queue126 worker126 kernel126", 10),
        ["network126", "latency126", "buffer126", "queue126", "worker126", "kernel126"],
    ),
    (
        ("network126 latency126 buffer126 queue126 worker126 kernel126", 18),
        ["network126", "latency126", "buffer126 queue126", "worker126", "kernel126"],
    ),
    (
        ("network126 latency126 buffer126 queue126 worker126 kernel126", 28),
        ["network126 latency126", "buffer126 queue126 worker126", "kernel126"],
    ),
    (
        ("latency126 buffer126 queue126 worker126 kernel126 signal126", 6),
        ["latency126", "buffer126", "queue126", "worker126", "kernel126", "signal126"],
    ),
    (
        ("latency126 buffer126 queue126 worker126 kernel126 signal126", 10),
        ["latency126", "buffer126", "queue126", "worker126", "kernel126", "signal126"],
    ),
    (
        ("latency126 buffer126 queue126 worker126 kernel126 signal126", 18),
        ["latency126", "buffer126 queue126", "worker126", "kernel126", "signal126"],
    ),
    (
        ("latency126 buffer126 queue126 worker126 kernel126 signal126", 28),
        ["latency126 buffer126", "queue126 worker126 kernel126", "signal126"],
    ),
    (
        ("buffer126 queue126 worker126 kernel126 signal126 packet126", 6),
        ["buffer126", "queue126", "worker126", "kernel126", "signal126", "packet126"],
    ),
    (
        ("buffer126 queue126 worker126 kernel126 signal126 packet126", 10),
        ["buffer126", "queue126", "worker126", "kernel126", "signal126", "packet126"],
    ),
    (
        ("buffer126 queue126 worker126 kernel126 signal126 packet126", 18),
        ["buffer126 queue126", "worker126", "kernel126", "signal126", "packet126"],
    ),
    (
        ("buffer126 queue126 worker126 kernel126 signal126 packet126", 28),
        ["buffer126 queue126 worker126", "kernel126 signal126", "packet126"],
    ),
    (
        ("queue126 worker126 kernel126 signal126 packet126 router126", 6),
        ["queue126", "worker126", "kernel126", "signal126", "packet126", "router126"],
    ),
    (
        ("queue126 worker126 kernel126 signal126 packet126 router126", 10),
        ["queue126", "worker126", "kernel126", "signal126", "packet126", "router126"],
    ),
    (
        ("queue126 worker126 kernel126 signal126 packet126 router126", 18),
        ["queue126 worker126", "kernel126", "signal126", "packet126", "router126"],
    ),
    (
        ("queue126 worker126 kernel126 signal126 packet126 router126", 28),
        ["queue126 worker126 kernel126", "signal126 packet126", "router126"],
    ),
    (
        ("worker126 kernel126 signal126 packet126 router126 cluster126", 6),
        ["worker126", "kernel126", "signal126", "packet126", "router126", "cluster126"],
    ),
    (
        ("worker126 kernel126 signal126 packet126 router126 cluster126", 10),
        ["worker126", "kernel126", "signal126", "packet126", "router126", "cluster126"],
    ),
    (
        ("worker126 kernel126 signal126 packet126 router126 cluster126", 18),
        ["worker126", "kernel126", "signal126", "packet126", "router126", "cluster126"],
    ),
    (
        ("worker126 kernel126 signal126 packet126 router126 cluster126", 28),
        ["worker126 kernel126", "signal126 packet126", "router126 cluster126"],
    ),
    (
        ("kernel126 signal126 packet126 router126 cluster126 mirror126", 6),
        ["kernel126", "signal126", "packet126", "router126", "cluster126", "mirror126"],
    ),
    (
        ("kernel126 signal126 packet126 router126 cluster126 mirror126", 10),
        ["kernel126", "signal126", "packet126", "router126", "cluster126", "mirror126"],
    ),
    (
        ("kernel126 signal126 packet126 router126 cluster126 mirror126", 18),
        ["kernel126", "signal126", "packet126", "router126", "cluster126", "mirror126"],
    ),
    (
        ("kernel126 signal126 packet126 router126 cluster126 mirror126", 28),
        ["kernel126 signal126", "packet126 router126", "cluster126 mirror126"],
    ),
    (
        ("signal126 packet126 router126 cluster126 mirror126 filter126", 6),
        ["signal126", "packet126", "router126", "cluster126", "mirror126", "filter126"],
    ),
    (
        ("signal126 packet126 router126 cluster126 mirror126 filter126", 10),
        ["signal126", "packet126", "router126", "cluster126", "mirror126", "filter126"],
    ),
    (
        ("signal126 packet126 router126 cluster126 mirror126 filter126", 18),
        ["signal126", "packet126", "router126", "cluster126", "mirror126", "filter126"],
    ),
    (
        ("signal126 packet126 router126 cluster126 mirror126 filter126", 28),
        ["signal126 packet126", "router126 cluster126", "mirror126 filter126"],
    ),
    (
        ("packet126 router126 cluster126 mirror126 filter126 ranking126", 6),
        ["packet126", "router126", "cluster126", "mirror126", "filter126", "ranking126"],
    ),
    (
        ("packet126 router126 cluster126 mirror126 filter126 ranking126", 10),
        ["packet126", "router126", "cluster126", "mirror126", "filter126", "ranking126"],
    ),
    (
        ("packet126 router126 cluster126 mirror126 filter126 ranking126", 18),
        ["packet126", "router126", "cluster126", "mirror126", "filter126", "ranking126"],
    ),
    (
        ("packet126 router126 cluster126 mirror126 filter126 ranking126", 28),
        ["packet126 router126", "cluster126 mirror126", "filter126 ranking126"],
    ),
    (
        ("router126 cluster126 mirror126 filter126 ranking126 encoding126", 6),
        ["router126", "cluster126", "mirror126", "filter126", "ranking126", "encoding126"],
    ),
    (
        ("router126 cluster126 mirror126 filter126 ranking126 encoding126", 10),
        ["router126", "cluster126", "mirror126", "filter126", "ranking126", "encoding126"],
    ),
    (
        ("router126 cluster126 mirror126 filter126 ranking126 encoding126", 18),
        ["router126", "cluster126", "mirror126", "filter126", "ranking126", "encoding126"],
    ),
    (
        ("router126 cluster126 mirror126 filter126 ranking126 encoding126", 28),
        ["router126 cluster126", "mirror126 filter126", "ranking126 encoding126"],
    ),
    (
        ("cluster126 mirror126 filter126 ranking126 encoding126 mapping126", 6),
        ["cluster126", "mirror126", "filter126", "ranking126", "encoding126", "mapping126"],
    ),
    (
        ("cluster126 mirror126 filter126 ranking126 encoding126 mapping126", 10),
        ["cluster126", "mirror126", "filter126", "ranking126", "encoding126", "mapping126"],
    ),
    (
        ("cluster126 mirror126 filter126 ranking126 encoding126 mapping126", 18),
        ["cluster126", "mirror126", "filter126", "ranking126", "encoding126", "mapping126"],
    ),
    (
        ("cluster126 mirror126 filter126 ranking126 encoding126 mapping126", 28),
        ["cluster126 mirror126", "filter126 ranking126", "encoding126 mapping126"],
    ),
    (
        ("mirror126 filter126 ranking126 encoding126 mapping126 record126", 6),
        ["mirror126", "filter126", "ranking126", "encoding126", "mapping126", "record126"],
    ),
    (
        ("mirror126 filter126 ranking126 encoding126 mapping126 record126", 10),
        ["mirror126", "filter126", "ranking126", "encoding126", "mapping126", "record126"],
    ),
    (
        ("mirror126 filter126 ranking126 encoding126 mapping126 record126", 18),
        ["mirror126", "filter126", "ranking126", "encoding126", "mapping126", "record126"],
    ),
    (
        ("mirror126 filter126 ranking126 encoding126 mapping126 record126", 28),
        ["mirror126 filter126", "ranking126 encoding126", "mapping126 record126"],
    ),
    (
        ("filter126 ranking126 encoding126 mapping126 record126 candle126", 6),
        ["filter126", "ranking126", "encoding126", "mapping126", "record126", "candle126"],
    ),
    (
        ("filter126 ranking126 encoding126 mapping126 record126 candle126", 10),
        ["filter126", "ranking126", "encoding126", "mapping126", "record126", "candle126"],
    ),
    (
        ("filter126 ranking126 encoding126 mapping126 record126 candle126", 18),
        ["filter126", "ranking126", "encoding126", "mapping126", "record126", "candle126"],
    ),
    (
        ("filter126 ranking126 encoding126 mapping126 record126 candle126", 28),
        ["filter126 ranking126", "encoding126 mapping126", "record126 candle126"],
    ),
    (
        ("ranking126 encoding126 mapping126 record126 candle126 thread126", 6),
        ["ranking126", "encoding126", "mapping126", "record126", "candle126", "thread126"],
    ),
    (
        ("ranking126 encoding126 mapping126 record126 candle126 thread126", 10),
        ["ranking126", "encoding126", "mapping126", "record126", "candle126", "thread126"],
    ),
    (
        ("ranking126 encoding126 mapping126 record126 candle126 thread126", 18),
        ["ranking126", "encoding126", "mapping126", "record126", "candle126", "thread126"],
    ),
    (
        ("ranking126 encoding126 mapping126 record126 candle126 thread126", 28),
        ["ranking126 encoding126", "mapping126 record126", "candle126 thread126"],
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
