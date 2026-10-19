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
        ("round 139: the quick brown fox jumps over the lazy dog", 4),
        ["round", "139:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 139: the quick brown fox jumps over the lazy dog", 8),
        ["round", "139: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 139: the quick brown fox jumps over the lazy dog", 12),
        ["round 139:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 139: the quick brown fox jumps over the lazy dog", 16),
        ["round 139: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 139: the quick brown fox jumps over the lazy dog", 24),
        ["round 139: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 139: the quick brown fox jumps over the lazy dog", 32),
        ["round 139: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 139: agentuniverse is a framework for multi agents", 4),
        ["round", "139:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 139: agentuniverse is a framework for multi agents", 8),
        ["round", "139:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 139: agentuniverse is a framework for multi agents", 12),
        ["round 139:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 139: agentuniverse is a framework for multi agents", 16),
        ["round 139:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 139: agentuniverse is a framework for multi agents", 24),
        ["round 139: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 139: agentuniverse is a framework for multi agents", 32),
        ["round 139: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 139: knowledge stored as vectors enables retrieval", 4),
        ["round", "139:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 139: knowledge stored as vectors enables retrieval", 8),
        ["round", "139:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 139: knowledge stored as vectors enables retrieval", 12),
        ["round 139:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 139: knowledge stored as vectors enables retrieval", 16),
        ["round 139:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 139: knowledge stored as vectors enables retrieval", 24),
        ["round 139: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 139: knowledge stored as vectors enables retrieval", 32),
        ["round 139: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 139: the processor reads the record then stops", 4),
        ["round", "139:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 139: the processor reads the record then stops", 8),
        ["round", "139: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 139: the processor reads the record then stops", 12),
        ["round 139:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 139: the processor reads the record then stops", 16),
        ["round 139: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 139: the processor reads the record then stops", 24),
        ["round 139: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 139: the processor reads the record then stops", 32),
        ["round 139: the processor reads", "the record then stops"],
    ),
    (
        ("round 139: a worker pulls the next task from the queue", 4),
        ["round", "139:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 139: a worker pulls the next task from the queue", 8),
        ["round", "139: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 139: a worker pulls the next task from the queue", 12),
        ["round 139: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 139: a worker pulls the next task from the queue", 16),
        ["round 139: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 139: a worker pulls the next task from the queue", 24),
        ["round 139: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 139: a worker pulls the next task from the queue", 32),
        ["round 139: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 139: signals travel through the network layer", 4),
        ["round", "139:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 139: signals travel through the network layer", 8),
        ["round", "139:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 139: signals travel through the network layer", 12),
        ["round 139:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 139: signals travel through the network layer", 16),
        ["round 139:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 139: signals travel through the network layer", 24),
        ["round 139: signals", "travel through the", "network layer"],
    ),
    (
        ("round 139: signals travel through the network layer", 32),
        ["round 139: signals travel", "through the network layer"],
    ),
    (
        ("round 139: the gateway routes each request by policy", 4),
        ["round", "139:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 139: the gateway routes each request by policy", 8),
        ["round", "139: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 139: the gateway routes each request by policy", 12),
        ["round 139:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 139: the gateway routes each request by policy", 16),
        ["round 139: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 139: the gateway routes each request by policy", 24),
        ["round 139: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 139: the gateway routes each request by policy", 32),
        ["round 139: the gateway routes", "each request by policy"],
    ),
    (
        ("round 139: memory grows until the buffer is full", 4),
        ["round", "139:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 139: memory grows until the buffer is full", 8),
        ["round", "139:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 139: memory grows until the buffer is full", 12),
        ["round 139:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 139: memory grows until the buffer is full", 16),
        ["round 139:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 139: memory grows until the buffer is full", 24), ["round 139: memory grows", "until the buffer is full"]),
    (("round 139: memory grows until the buffer is full", 32), ["round 139: memory grows until", "the buffer is full"]),
    (
        ("round 139: the cluster mirrors every packet twice", 4),
        ["round", "139:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 139: the cluster mirrors every packet twice", 8),
        ["round", "139: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 139: the cluster mirrors every packet twice", 12),
        ["round 139:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 139: the cluster mirrors every packet twice", 16),
        ["round 139: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 139: the cluster mirrors every packet twice", 24),
        ["round 139: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 139: the cluster mirrors every packet twice", 32),
        ["round 139: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 139: ranking uses tokens learned from the corpus", 4),
        ["round", "139:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 139: ranking uses tokens learned from the corpus", 8),
        ["round", "139:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 139: ranking uses tokens learned from the corpus", 12),
        ["round 139:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 139: ranking uses tokens learned from the corpus", 16),
        ["round 139:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 139: ranking uses tokens learned from the corpus", 24),
        ["round 139: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 139: ranking uses tokens learned from the corpus", 32),
        ["round 139: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 139: a long session ends when the candle dies", 4),
        ["round", "139:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 139: a long session ends when the candle dies", 8),
        ["round", "139: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 139: a long session ends when the candle dies", 12),
        ["round 139: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 139: a long session ends when the candle dies", 16),
        ["round 139: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 139: a long session ends when the candle dies", 24),
        ["round 139: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 139: a long session ends when the candle dies", 32),
        ["round 139: a long session ends", "when the candle dies"],
    ),
    (
        ("round 139: encode the prompt then map the result", 4),
        ["round", "139:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 139: encode the prompt then map the result", 8),
        ["round", "139:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 139: encode the prompt then map the result", 12),
        ["round 139:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 139: encode the prompt then map the result", 16),
        ["round 139:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 139: encode the prompt then map the result", 24),
        ["round 139: encode the", "prompt then map the", "result"],
    ),
    (("round 139: encode the prompt then map the result", 32), ["round 139: encode the prompt", "then map the result"]),
    (
        ("round 139: the kernel wakes the worker at dawn", 4),
        ["round", "139:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 139: the kernel wakes the worker at dawn", 8),
        ["round", "139: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 139: the kernel wakes the worker at dawn", 12),
        ["round 139:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 139: the kernel wakes the worker at dawn", 16), ["round 139: the", "kernel wakes the", "worker at dawn"]),
    (("round 139: the kernel wakes the worker at dawn", 24), ["round 139: the kernel", "wakes the worker at dawn"]),
    (("round 139: the kernel wakes the worker at dawn", 32), ["round 139: the kernel wakes the", "worker at dawn"]),
    (
        ("round 139: service latency drops after the patch", 4),
        ["round", "139:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 139: service latency drops after the patch", 8),
        ["round", "139:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 139: service latency drops after the patch", 12),
        ["round 139:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 139: service latency drops after the patch", 16),
        ["round 139:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 139: service latency drops after the patch", 24),
        ["round 139: service", "latency drops after the", "patch"],
    ),
    (("round 139: service latency drops after the patch", 32), ["round 139: service latency drops", "after the patch"]),
    (
        ("round 139: the library caches every vector it sees", 4),
        ["round", "139:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 139: the library caches every vector it sees", 8),
        ["round", "139: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 139: the library caches every vector it sees", 12),
        ["round 139:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 139: the library caches every vector it sees", 16),
        ["round 139: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 139: the library caches every vector it sees", 24),
        ["round 139: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 139: the library caches every vector it sees", 32),
        ["round 139: the library caches", "every vector it sees"],
    ),
    (
        ("round 139: agents argue then the debate resolves", 4),
        ["round", "139:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 139: agents argue then the debate resolves", 8),
        ["round", "139:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 139: agents argue then the debate resolves", 12),
        ["round 139:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 139: agents argue then the debate resolves", 16),
        ["round 139:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 139: agents argue then the debate resolves", 24), ["round 139: agents argue", "then the debate resolves"]),
    (("round 139: agents argue then the debate resolves", 32), ["round 139: agents argue then the", "debate resolves"]),
    (
        ("round 139: the filter keeps only strong matches", 4),
        ["round", "139:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 139: the filter keeps only strong matches", 8),
        ["round", "139: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 139: the filter keeps only strong matches", 12),
        ["round 139:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 139: the filter keeps only strong matches", 16),
        ["round 139: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 139: the filter keeps only strong matches", 24),
        ["round 139: the filter", "keeps only strong", "matches"],
    ),
    (("round 139: the filter keeps only strong matches", 32), ["round 139: the filter keeps only", "strong matches"]),
    (
        ("round 139: the model answers with a short reply", 4),
        ["round", "139:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 139: the model answers with a short reply", 8),
        ["round", "139: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 139: the model answers with a short reply", 12),
        ["round 139:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 139: the model answers with a short reply", 16),
        ["round 139: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 139: the model answers with a short reply", 24),
        ["round 139: the model", "answers with a short", "reply"],
    ),
    (("round 139: the model answers with a short reply", 32), ["round 139: the model answers", "with a short reply"]),
    (
        ("round 139: the recorder stores the reasoning trace", 4),
        ["round", "139:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 139: the recorder stores the reasoning trace", 8),
        ["round", "139: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 139: the recorder stores the reasoning trace", 12),
        ["round 139:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 139: the recorder stores the reasoning trace", 16),
        ["round 139: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 139: the recorder stores the reasoning trace", 24),
        ["round 139: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 139: the recorder stores the reasoning trace", 32),
        ["round 139: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 139: the angel watches the processor run", 4),
        ["round", "139:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 139: the angel watches the processor run", 8),
        ["round", "139: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 139: the angel watches the processor run", 12),
        ["round 139:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 139: the angel watches the processor run", 16),
        ["round 139: the", "angel watches", "the processor", "run"],
    ),
    (("round 139: the angel watches the processor run", 24), ["round 139: the angel", "watches the processor", "run"]),
    (("round 139: the angel watches the processor run", 32), ["round 139: the angel watches the", "processor run"]),
    (
        ("round 139: angle of the vector decides the match", 4),
        ["round", "139:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 139: angle of the vector decides the match", 8),
        ["round", "139:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 139: angle of the vector decides the match", 12),
        ["round 139:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 139: angle of the vector decides the match", 16),
        ["round 139: angle", "of the vector", "decides the", "match"],
    ),
    (("round 139: angle of the vector decides the match", 24), ["round 139: angle of the", "vector decides the match"]),
    (("round 139: angle of the vector decides the match", 32), ["round 139: angle of the vector", "decides the match"]),
    (
        ("round 139: the candle burns twice as long at night", 4),
        ["round", "139:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 139: the candle burns twice as long at night", 8),
        ["round", "139: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 139: the candle burns twice as long at night", 12),
        ["round 139:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 139: the candle burns twice as long at night", 16),
        ["round 139: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 139: the candle burns twice as long at night", 24),
        ["round 139: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 139: the candle burns twice as long at night", 32),
        ["round 139: the candle burns", "twice as long at night"],
    ),
    (
        ("round 139: a mirror of the universe in one line", 4),
        ["round", "139:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 139: a mirror of the universe in one line", 8),
        ["round", "139: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 139: a mirror of the universe in one line", 12),
        ["round 139: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 139: a mirror of the universe in one line", 16),
        ["round 139: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 139: a mirror of the universe in one line", 24), ["round 139: a mirror of", "the universe in one line"]),
    (("round 139: a mirror of the universe in one line", 32), ["round 139: a mirror of the", "universe in one line"]),
    (
        ("round 139: the queue drains before the storm", 4),
        ["round", "139:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 139: the queue drains before the storm", 8),
        ["round", "139: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 139: the queue drains before the storm", 12),
        ["round 139:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 139: the queue drains before the storm", 16), ["round 139: the", "queue drains", "before the storm"]),
    (("round 139: the queue drains before the storm", 24), ["round 139: the queue", "drains before the storm"]),
    (("round 139: the queue drains before the storm", 32), ["round 139: the queue drains", "before the storm"]),
    (
        ("kitten139 sitting139 agent139 angle139 universe139 memory139", 6),
        ["kitten139", "sitting139", "agent139", "angle139", "universe139", "memory139"],
    ),
    (
        ("kitten139 sitting139 agent139 angle139 universe139 memory139", 10),
        ["kitten139", "sitting139", "agent139", "angle139", "universe139", "memory139"],
    ),
    (
        ("kitten139 sitting139 agent139 angle139 universe139 memory139", 18),
        ["kitten139", "sitting139", "agent139 angle139", "universe139", "memory139"],
    ),
    (
        ("kitten139 sitting139 agent139 angle139 universe139 memory139", 28),
        ["kitten139 sitting139", "agent139 angle139", "universe139 memory139"],
    ),
    (
        ("sitting139 agent139 angle139 universe139 memory139 stream139", 6),
        ["sitting139", "agent139", "angle139", "universe139", "memory139", "stream139"],
    ),
    (
        ("sitting139 agent139 angle139 universe139 memory139 stream139", 10),
        ["sitting139", "agent139", "angle139", "universe139", "memory139", "stream139"],
    ),
    (
        ("sitting139 agent139 angle139 universe139 memory139 stream139", 18),
        ["sitting139", "agent139 angle139", "universe139", "memory139", "stream139"],
    ),
    (
        ("sitting139 agent139 angle139 universe139 memory139 stream139", 28),
        ["sitting139 agent139 angle139", "universe139 memory139", "stream139"],
    ),
    (
        ("agent139 angle139 universe139 memory139 stream139 context139", 6),
        ["agent139", "angle139", "universe139", "memory139", "stream139", "context139"],
    ),
    (
        ("agent139 angle139 universe139 memory139 stream139 context139", 10),
        ["agent139", "angle139", "universe139", "memory139", "stream139", "context139"],
    ),
    (
        ("agent139 angle139 universe139 memory139 stream139 context139", 18),
        ["agent139 angle139", "universe139", "memory139", "stream139", "context139"],
    ),
    (
        ("agent139 angle139 universe139 memory139 stream139 context139", 28),
        ["agent139 angle139", "universe139 memory139", "stream139 context139"],
    ),
    (
        ("angle139 universe139 memory139 stream139 context139 knowledge139", 6),
        ["angle139", "universe139", "memory139", "stream139", "context139", "knowledge139"],
    ),
    (
        ("angle139 universe139 memory139 stream139 context139 knowledge139", 10),
        ["angle139", "universe139", "memory139", "stream139", "context139", "knowledge139"],
    ),
    (
        ("angle139 universe139 memory139 stream139 context139 knowledge139", 18),
        ["angle139", "universe139", "memory139", "stream139", "context139", "knowledge139"],
    ),
    (
        ("angle139 universe139 memory139 stream139 context139 knowledge139", 28),
        ["angle139 universe139", "memory139 stream139", "context139 knowledge139"],
    ),
    (
        ("universe139 memory139 stream139 context139 knowledge139 vector139", 6),
        ["universe139", "memory139", "stream139", "context139", "knowledge139", "vector139"],
    ),
    (
        ("universe139 memory139 stream139 context139 knowledge139 vector139", 10),
        ["universe139", "memory139", "stream139", "context139", "knowledge139", "vector139"],
    ),
    (
        ("universe139 memory139 stream139 context139 knowledge139 vector139", 18),
        ["universe139", "memory139", "stream139", "context139", "knowledge139", "vector139"],
    ),
    (
        ("universe139 memory139 stream139 context139 knowledge139 vector139", 28),
        ["universe139 memory139", "stream139 context139", "knowledge139 vector139"],
    ),
    (
        ("memory139 stream139 context139 knowledge139 vector139 processor139", 6),
        ["memory139", "stream139", "context139", "knowledge139", "vector139", "processor139"],
    ),
    (
        ("memory139 stream139 context139 knowledge139 vector139 processor139", 10),
        ["memory139", "stream139", "context139", "knowledge139", "vector139", "processor139"],
    ),
    (
        ("memory139 stream139 context139 knowledge139 vector139 processor139", 18),
        ["memory139", "stream139", "context139", "knowledge139", "vector139", "processor139"],
    ),
    (
        ("memory139 stream139 context139 knowledge139 vector139 processor139", 28),
        ["memory139 stream139", "context139 knowledge139", "vector139 processor139"],
    ),
    (
        ("stream139 context139 knowledge139 vector139 processor139 reasoning139", 6),
        ["stream139", "context139", "knowledge139", "vector139", "processor139", "reasoning139"],
    ),
    (
        ("stream139 context139 knowledge139 vector139 processor139 reasoning139", 10),
        ["stream139", "context139", "knowledge139", "vector139", "processor139", "reasoning139"],
    ),
    (
        ("stream139 context139 knowledge139 vector139 processor139 reasoning139", 18),
        ["stream139", "context139", "knowledge139", "vector139", "processor139", "reasoning139"],
    ),
    (
        ("stream139 context139 knowledge139 vector139 processor139 reasoning139", 28),
        ["stream139 context139", "knowledge139 vector139", "processor139 reasoning139"],
    ),
    (
        ("context139 knowledge139 vector139 processor139 reasoning139 machine139", 6),
        ["context139", "knowledge139", "vector139", "processor139", "reasoning139", "machine139"],
    ),
    (
        ("context139 knowledge139 vector139 processor139 reasoning139 machine139", 10),
        ["context139", "knowledge139", "vector139", "processor139", "reasoning139", "machine139"],
    ),
    (
        ("context139 knowledge139 vector139 processor139 reasoning139 machine139", 18),
        ["context139", "knowledge139", "vector139", "processor139", "reasoning139", "machine139"],
    ),
    (
        ("context139 knowledge139 vector139 processor139 reasoning139 machine139", 28),
        ["context139 knowledge139", "vector139 processor139", "reasoning139 machine139"],
    ),
    (
        ("knowledge139 vector139 processor139 reasoning139 machine139 learning139", 6),
        ["knowledge139", "vector139", "processor139", "reasoning139", "machine139", "learning139"],
    ),
    (
        ("knowledge139 vector139 processor139 reasoning139 machine139 learning139", 10),
        ["knowledge139", "vector139", "processor139", "reasoning139", "machine139", "learning139"],
    ),
    (
        ("knowledge139 vector139 processor139 reasoning139 machine139 learning139", 18),
        ["knowledge139", "vector139", "processor139", "reasoning139", "machine139", "learning139"],
    ),
    (
        ("knowledge139 vector139 processor139 reasoning139 machine139 learning139", 28),
        ["knowledge139 vector139", "processor139 reasoning139", "machine139 learning139"],
    ),
    (
        ("vector139 processor139 reasoning139 machine139 learning139 model139", 6),
        ["vector139", "processor139", "reasoning139", "machine139", "learning139", "model139"],
    ),
    (
        ("vector139 processor139 reasoning139 machine139 learning139 model139", 10),
        ["vector139", "processor139", "reasoning139", "machine139", "learning139", "model139"],
    ),
    (
        ("vector139 processor139 reasoning139 machine139 learning139 model139", 18),
        ["vector139", "processor139", "reasoning139", "machine139", "learning139", "model139"],
    ),
    (
        ("vector139 processor139 reasoning139 machine139 learning139 model139", 28),
        ["vector139 processor139", "reasoning139 machine139", "learning139 model139"],
    ),
    (
        ("processor139 reasoning139 machine139 learning139 model139 token139", 6),
        ["processor139", "reasoning139", "machine139", "learning139", "model139", "token139"],
    ),
    (
        ("processor139 reasoning139 machine139 learning139 model139 token139", 10),
        ["processor139", "reasoning139", "machine139", "learning139", "model139", "token139"],
    ),
    (
        ("processor139 reasoning139 machine139 learning139 model139 token139", 18),
        ["processor139", "reasoning139", "machine139", "learning139", "model139 token139"],
    ),
    (
        ("processor139 reasoning139 machine139 learning139 model139 token139", 28),
        ["processor139 reasoning139", "machine139 learning139", "model139 token139"],
    ),
    (
        ("reasoning139 machine139 learning139 model139 token139 prompt139", 6),
        ["reasoning139", "machine139", "learning139", "model139", "token139", "prompt139"],
    ),
    (
        ("reasoning139 machine139 learning139 model139 token139 prompt139", 10),
        ["reasoning139", "machine139", "learning139", "model139", "token139", "prompt139"],
    ),
    (
        ("reasoning139 machine139 learning139 model139 token139 prompt139", 18),
        ["reasoning139", "machine139", "learning139", "model139 token139", "prompt139"],
    ),
    (
        ("reasoning139 machine139 learning139 model139 token139 prompt139", 28),
        ["reasoning139 machine139", "learning139 model139", "token139 prompt139"],
    ),
    (
        ("machine139 learning139 model139 token139 prompt139 session139", 6),
        ["machine139", "learning139", "model139", "token139", "prompt139", "session139"],
    ),
    (
        ("machine139 learning139 model139 token139 prompt139 session139", 10),
        ["machine139", "learning139", "model139", "token139", "prompt139", "session139"],
    ),
    (
        ("machine139 learning139 model139 token139 prompt139 session139", 18),
        ["machine139", "learning139", "model139 token139", "prompt139", "session139"],
    ),
    (
        ("machine139 learning139 model139 token139 prompt139 session139", 28),
        ["machine139 learning139", "model139 token139 prompt139", "session139"],
    ),
    (
        ("learning139 model139 token139 prompt139 session139 library139", 6),
        ["learning139", "model139", "token139", "prompt139", "session139", "library139"],
    ),
    (
        ("learning139 model139 token139 prompt139 session139 library139", 10),
        ["learning139", "model139", "token139", "prompt139", "session139", "library139"],
    ),
    (
        ("learning139 model139 token139 prompt139 session139 library139", 18),
        ["learning139", "model139 token139", "prompt139", "session139", "library139"],
    ),
    (
        ("learning139 model139 token139 prompt139 session139 library139", 28),
        ["learning139 model139", "token139 prompt139", "session139 library139"],
    ),
    (
        ("model139 token139 prompt139 session139 library139 service139", 6),
        ["model139", "token139", "prompt139", "session139", "library139", "service139"],
    ),
    (
        ("model139 token139 prompt139 session139 library139 service139", 10),
        ["model139", "token139", "prompt139", "session139", "library139", "service139"],
    ),
    (
        ("model139 token139 prompt139 session139 library139 service139", 18),
        ["model139 token139", "prompt139", "session139", "library139", "service139"],
    ),
    (
        ("model139 token139 prompt139 session139 library139 service139", 28),
        ["model139 token139 prompt139", "session139 library139", "service139"],
    ),
    (
        ("token139 prompt139 session139 library139 service139 gateway139", 6),
        ["token139", "prompt139", "session139", "library139", "service139", "gateway139"],
    ),
    (
        ("token139 prompt139 session139 library139 service139 gateway139", 10),
        ["token139", "prompt139", "session139", "library139", "service139", "gateway139"],
    ),
    (
        ("token139 prompt139 session139 library139 service139 gateway139", 18),
        ["token139 prompt139", "session139", "library139", "service139", "gateway139"],
    ),
    (
        ("token139 prompt139 session139 library139 service139 gateway139", 28),
        ["token139 prompt139", "session139 library139", "service139 gateway139"],
    ),
    (
        ("prompt139 session139 library139 service139 gateway139 storage139", 6),
        ["prompt139", "session139", "library139", "service139", "gateway139", "storage139"],
    ),
    (
        ("prompt139 session139 library139 service139 gateway139 storage139", 10),
        ["prompt139", "session139", "library139", "service139", "gateway139", "storage139"],
    ),
    (
        ("prompt139 session139 library139 service139 gateway139 storage139", 18),
        ["prompt139", "session139", "library139", "service139", "gateway139", "storage139"],
    ),
    (
        ("prompt139 session139 library139 service139 gateway139 storage139", 28),
        ["prompt139 session139", "library139 service139", "gateway139 storage139"],
    ),
    (
        ("session139 library139 service139 gateway139 storage139 network139", 6),
        ["session139", "library139", "service139", "gateway139", "storage139", "network139"],
    ),
    (
        ("session139 library139 service139 gateway139 storage139 network139", 10),
        ["session139", "library139", "service139", "gateway139", "storage139", "network139"],
    ),
    (
        ("session139 library139 service139 gateway139 storage139 network139", 18),
        ["session139", "library139", "service139", "gateway139", "storage139", "network139"],
    ),
    (
        ("session139 library139 service139 gateway139 storage139 network139", 28),
        ["session139 library139", "service139 gateway139", "storage139 network139"],
    ),
    (
        ("library139 service139 gateway139 storage139 network139 latency139", 6),
        ["library139", "service139", "gateway139", "storage139", "network139", "latency139"],
    ),
    (
        ("library139 service139 gateway139 storage139 network139 latency139", 10),
        ["library139", "service139", "gateway139", "storage139", "network139", "latency139"],
    ),
    (
        ("library139 service139 gateway139 storage139 network139 latency139", 18),
        ["library139", "service139", "gateway139", "storage139", "network139", "latency139"],
    ),
    (
        ("library139 service139 gateway139 storage139 network139 latency139", 28),
        ["library139 service139", "gateway139 storage139", "network139 latency139"],
    ),
    (
        ("service139 gateway139 storage139 network139 latency139 buffer139", 6),
        ["service139", "gateway139", "storage139", "network139", "latency139", "buffer139"],
    ),
    (
        ("service139 gateway139 storage139 network139 latency139 buffer139", 10),
        ["service139", "gateway139", "storage139", "network139", "latency139", "buffer139"],
    ),
    (
        ("service139 gateway139 storage139 network139 latency139 buffer139", 18),
        ["service139", "gateway139", "storage139", "network139", "latency139", "buffer139"],
    ),
    (
        ("service139 gateway139 storage139 network139 latency139 buffer139", 28),
        ["service139 gateway139", "storage139 network139", "latency139 buffer139"],
    ),
    (
        ("gateway139 storage139 network139 latency139 buffer139 queue139", 6),
        ["gateway139", "storage139", "network139", "latency139", "buffer139", "queue139"],
    ),
    (
        ("gateway139 storage139 network139 latency139 buffer139 queue139", 10),
        ["gateway139", "storage139", "network139", "latency139", "buffer139", "queue139"],
    ),
    (
        ("gateway139 storage139 network139 latency139 buffer139 queue139", 18),
        ["gateway139", "storage139", "network139", "latency139", "buffer139 queue139"],
    ),
    (
        ("gateway139 storage139 network139 latency139 buffer139 queue139", 28),
        ["gateway139 storage139", "network139 latency139", "buffer139 queue139"],
    ),
    (
        ("storage139 network139 latency139 buffer139 queue139 worker139", 6),
        ["storage139", "network139", "latency139", "buffer139", "queue139", "worker139"],
    ),
    (
        ("storage139 network139 latency139 buffer139 queue139 worker139", 10),
        ["storage139", "network139", "latency139", "buffer139", "queue139", "worker139"],
    ),
    (
        ("storage139 network139 latency139 buffer139 queue139 worker139", 18),
        ["storage139", "network139", "latency139", "buffer139 queue139", "worker139"],
    ),
    (
        ("storage139 network139 latency139 buffer139 queue139 worker139", 28),
        ["storage139 network139", "latency139 buffer139", "queue139 worker139"],
    ),
    (
        ("network139 latency139 buffer139 queue139 worker139 kernel139", 6),
        ["network139", "latency139", "buffer139", "queue139", "worker139", "kernel139"],
    ),
    (
        ("network139 latency139 buffer139 queue139 worker139 kernel139", 10),
        ["network139", "latency139", "buffer139", "queue139", "worker139", "kernel139"],
    ),
    (
        ("network139 latency139 buffer139 queue139 worker139 kernel139", 18),
        ["network139", "latency139", "buffer139 queue139", "worker139", "kernel139"],
    ),
    (
        ("network139 latency139 buffer139 queue139 worker139 kernel139", 28),
        ["network139 latency139", "buffer139 queue139 worker139", "kernel139"],
    ),
    (
        ("latency139 buffer139 queue139 worker139 kernel139 signal139", 6),
        ["latency139", "buffer139", "queue139", "worker139", "kernel139", "signal139"],
    ),
    (
        ("latency139 buffer139 queue139 worker139 kernel139 signal139", 10),
        ["latency139", "buffer139", "queue139", "worker139", "kernel139", "signal139"],
    ),
    (
        ("latency139 buffer139 queue139 worker139 kernel139 signal139", 18),
        ["latency139", "buffer139 queue139", "worker139", "kernel139", "signal139"],
    ),
    (
        ("latency139 buffer139 queue139 worker139 kernel139 signal139", 28),
        ["latency139 buffer139", "queue139 worker139 kernel139", "signal139"],
    ),
    (
        ("buffer139 queue139 worker139 kernel139 signal139 packet139", 6),
        ["buffer139", "queue139", "worker139", "kernel139", "signal139", "packet139"],
    ),
    (
        ("buffer139 queue139 worker139 kernel139 signal139 packet139", 10),
        ["buffer139", "queue139", "worker139", "kernel139", "signal139", "packet139"],
    ),
    (
        ("buffer139 queue139 worker139 kernel139 signal139 packet139", 18),
        ["buffer139 queue139", "worker139", "kernel139", "signal139", "packet139"],
    ),
    (
        ("buffer139 queue139 worker139 kernel139 signal139 packet139", 28),
        ["buffer139 queue139 worker139", "kernel139 signal139", "packet139"],
    ),
    (
        ("queue139 worker139 kernel139 signal139 packet139 router139", 6),
        ["queue139", "worker139", "kernel139", "signal139", "packet139", "router139"],
    ),
    (
        ("queue139 worker139 kernel139 signal139 packet139 router139", 10),
        ["queue139", "worker139", "kernel139", "signal139", "packet139", "router139"],
    ),
    (
        ("queue139 worker139 kernel139 signal139 packet139 router139", 18),
        ["queue139 worker139", "kernel139", "signal139", "packet139", "router139"],
    ),
    (
        ("queue139 worker139 kernel139 signal139 packet139 router139", 28),
        ["queue139 worker139 kernel139", "signal139 packet139", "router139"],
    ),
    (
        ("worker139 kernel139 signal139 packet139 router139 cluster139", 6),
        ["worker139", "kernel139", "signal139", "packet139", "router139", "cluster139"],
    ),
    (
        ("worker139 kernel139 signal139 packet139 router139 cluster139", 10),
        ["worker139", "kernel139", "signal139", "packet139", "router139", "cluster139"],
    ),
    (
        ("worker139 kernel139 signal139 packet139 router139 cluster139", 18),
        ["worker139", "kernel139", "signal139", "packet139", "router139", "cluster139"],
    ),
    (
        ("worker139 kernel139 signal139 packet139 router139 cluster139", 28),
        ["worker139 kernel139", "signal139 packet139", "router139 cluster139"],
    ),
    (
        ("kernel139 signal139 packet139 router139 cluster139 mirror139", 6),
        ["kernel139", "signal139", "packet139", "router139", "cluster139", "mirror139"],
    ),
    (
        ("kernel139 signal139 packet139 router139 cluster139 mirror139", 10),
        ["kernel139", "signal139", "packet139", "router139", "cluster139", "mirror139"],
    ),
    (
        ("kernel139 signal139 packet139 router139 cluster139 mirror139", 18),
        ["kernel139", "signal139", "packet139", "router139", "cluster139", "mirror139"],
    ),
    (
        ("kernel139 signal139 packet139 router139 cluster139 mirror139", 28),
        ["kernel139 signal139", "packet139 router139", "cluster139 mirror139"],
    ),
    (
        ("signal139 packet139 router139 cluster139 mirror139 filter139", 6),
        ["signal139", "packet139", "router139", "cluster139", "mirror139", "filter139"],
    ),
    (
        ("signal139 packet139 router139 cluster139 mirror139 filter139", 10),
        ["signal139", "packet139", "router139", "cluster139", "mirror139", "filter139"],
    ),
    (
        ("signal139 packet139 router139 cluster139 mirror139 filter139", 18),
        ["signal139", "packet139", "router139", "cluster139", "mirror139", "filter139"],
    ),
    (
        ("signal139 packet139 router139 cluster139 mirror139 filter139", 28),
        ["signal139 packet139", "router139 cluster139", "mirror139 filter139"],
    ),
    (
        ("packet139 router139 cluster139 mirror139 filter139 ranking139", 6),
        ["packet139", "router139", "cluster139", "mirror139", "filter139", "ranking139"],
    ),
    (
        ("packet139 router139 cluster139 mirror139 filter139 ranking139", 10),
        ["packet139", "router139", "cluster139", "mirror139", "filter139", "ranking139"],
    ),
    (
        ("packet139 router139 cluster139 mirror139 filter139 ranking139", 18),
        ["packet139", "router139", "cluster139", "mirror139", "filter139", "ranking139"],
    ),
    (
        ("packet139 router139 cluster139 mirror139 filter139 ranking139", 28),
        ["packet139 router139", "cluster139 mirror139", "filter139 ranking139"],
    ),
    (
        ("router139 cluster139 mirror139 filter139 ranking139 encoding139", 6),
        ["router139", "cluster139", "mirror139", "filter139", "ranking139", "encoding139"],
    ),
    (
        ("router139 cluster139 mirror139 filter139 ranking139 encoding139", 10),
        ["router139", "cluster139", "mirror139", "filter139", "ranking139", "encoding139"],
    ),
    (
        ("router139 cluster139 mirror139 filter139 ranking139 encoding139", 18),
        ["router139", "cluster139", "mirror139", "filter139", "ranking139", "encoding139"],
    ),
    (
        ("router139 cluster139 mirror139 filter139 ranking139 encoding139", 28),
        ["router139 cluster139", "mirror139 filter139", "ranking139 encoding139"],
    ),
    (
        ("cluster139 mirror139 filter139 ranking139 encoding139 mapping139", 6),
        ["cluster139", "mirror139", "filter139", "ranking139", "encoding139", "mapping139"],
    ),
    (
        ("cluster139 mirror139 filter139 ranking139 encoding139 mapping139", 10),
        ["cluster139", "mirror139", "filter139", "ranking139", "encoding139", "mapping139"],
    ),
    (
        ("cluster139 mirror139 filter139 ranking139 encoding139 mapping139", 18),
        ["cluster139", "mirror139", "filter139", "ranking139", "encoding139", "mapping139"],
    ),
    (
        ("cluster139 mirror139 filter139 ranking139 encoding139 mapping139", 28),
        ["cluster139 mirror139", "filter139 ranking139", "encoding139 mapping139"],
    ),
    (
        ("mirror139 filter139 ranking139 encoding139 mapping139 record139", 6),
        ["mirror139", "filter139", "ranking139", "encoding139", "mapping139", "record139"],
    ),
    (
        ("mirror139 filter139 ranking139 encoding139 mapping139 record139", 10),
        ["mirror139", "filter139", "ranking139", "encoding139", "mapping139", "record139"],
    ),
    (
        ("mirror139 filter139 ranking139 encoding139 mapping139 record139", 18),
        ["mirror139", "filter139", "ranking139", "encoding139", "mapping139", "record139"],
    ),
    (
        ("mirror139 filter139 ranking139 encoding139 mapping139 record139", 28),
        ["mirror139 filter139", "ranking139 encoding139", "mapping139 record139"],
    ),
    (
        ("filter139 ranking139 encoding139 mapping139 record139 candle139", 6),
        ["filter139", "ranking139", "encoding139", "mapping139", "record139", "candle139"],
    ),
    (
        ("filter139 ranking139 encoding139 mapping139 record139 candle139", 10),
        ["filter139", "ranking139", "encoding139", "mapping139", "record139", "candle139"],
    ),
    (
        ("filter139 ranking139 encoding139 mapping139 record139 candle139", 18),
        ["filter139", "ranking139", "encoding139", "mapping139", "record139", "candle139"],
    ),
    (
        ("filter139 ranking139 encoding139 mapping139 record139 candle139", 28),
        ["filter139 ranking139", "encoding139 mapping139", "record139 candle139"],
    ),
    (
        ("ranking139 encoding139 mapping139 record139 candle139 thread139", 6),
        ["ranking139", "encoding139", "mapping139", "record139", "candle139", "thread139"],
    ),
    (
        ("ranking139 encoding139 mapping139 record139 candle139 thread139", 10),
        ["ranking139", "encoding139", "mapping139", "record139", "candle139", "thread139"],
    ),
    (
        ("ranking139 encoding139 mapping139 record139 candle139 thread139", 18),
        ["ranking139", "encoding139", "mapping139", "record139", "candle139", "thread139"],
    ),
    (
        ("ranking139 encoding139 mapping139 record139 candle139 thread139", 28),
        ["ranking139 encoding139", "mapping139 record139", "candle139 thread139"],
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
