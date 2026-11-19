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
        ("round 72: the quick brown fox jumps over the lazy dog", 4),
        ["round", "72:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 72: the quick brown fox jumps over the lazy dog", 8),
        ["round", "72: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 72: the quick brown fox jumps over the lazy dog", 12),
        ["round 72:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 72: the quick brown fox jumps over the lazy dog", 16),
        ["round 72: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 72: the quick brown fox jumps over the lazy dog", 24),
        ["round 72: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 72: the quick brown fox jumps over the lazy dog", 32),
        ["round 72: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 72: agentuniverse is a framework for multi agents", 4),
        ["round", "72:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 72: agentuniverse is a framework for multi agents", 8),
        ["round", "72:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 72: agentuniverse is a framework for multi agents", 12),
        ["round 72:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 72: agentuniverse is a framework for multi agents", 16),
        ["round 72:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 72: agentuniverse is a framework for multi agents", 24),
        ["round 72: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 72: agentuniverse is a framework for multi agents", 32),
        ["round 72: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 72: knowledge stored as vectors enables retrieval", 4),
        ["round", "72:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 72: knowledge stored as vectors enables retrieval", 8),
        ["round", "72:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 72: knowledge stored as vectors enables retrieval", 12),
        ["round 72:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 72: knowledge stored as vectors enables retrieval", 16),
        ["round 72:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 72: knowledge stored as vectors enables retrieval", 24),
        ["round 72: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 72: knowledge stored as vectors enables retrieval", 32),
        ["round 72: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 72: the processor reads the record then stops", 4),
        ["round", "72:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 72: the processor reads the record then stops", 8),
        ["round", "72: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 72: the processor reads the record then stops", 12),
        ["round 72:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 72: the processor reads the record then stops", 16),
        ["round 72: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 72: the processor reads the record then stops", 24),
        ["round 72: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 72: the processor reads the record then stops", 32),
        ["round 72: the processor reads", "the record then stops"],
    ),
    (
        ("round 72: a worker pulls the next task from the queue", 4),
        ["round", "72:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 72: a worker pulls the next task from the queue", 8),
        ["round", "72: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 72: a worker pulls the next task from the queue", 12),
        ["round 72: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 72: a worker pulls the next task from the queue", 16),
        ["round 72: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 72: a worker pulls the next task from the queue", 24),
        ["round 72: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 72: a worker pulls the next task from the queue", 32),
        ["round 72: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 72: signals travel through the network layer", 4),
        ["round", "72:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 72: signals travel through the network layer", 8),
        ["round", "72:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 72: signals travel through the network layer", 12),
        ["round 72:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 72: signals travel through the network layer", 16),
        ["round 72:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 72: signals travel through the network layer", 24),
        ["round 72: signals travel", "through the network", "layer"],
    ),
    (
        ("round 72: signals travel through the network layer", 32),
        ["round 72: signals travel through", "the network layer"],
    ),
    (
        ("round 72: the gateway routes each request by policy", 4),
        ["round", "72:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 72: the gateway routes each request by policy", 8),
        ["round", "72: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 72: the gateway routes each request by policy", 12),
        ["round 72:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 72: the gateway routes each request by policy", 16),
        ["round 72: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 72: the gateway routes each request by policy", 24),
        ["round 72: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 72: the gateway routes each request by policy", 32),
        ["round 72: the gateway routes", "each request by policy"],
    ),
    (
        ("round 72: memory grows until the buffer is full", 4),
        ["round", "72:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 72: memory grows until the buffer is full", 8),
        ["round", "72:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 72: memory grows until the buffer is full", 12),
        ["round 72:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 72: memory grows until the buffer is full", 16),
        ["round 72: memory", "grows until the", "buffer is full"],
    ),
    (("round 72: memory grows until the buffer is full", 24), ["round 72: memory grows", "until the buffer is full"]),
    (("round 72: memory grows until the buffer is full", 32), ["round 72: memory grows until the", "buffer is full"]),
    (
        ("round 72: the cluster mirrors every packet twice", 4),
        ["round", "72:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 72: the cluster mirrors every packet twice", 8),
        ["round", "72: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 72: the cluster mirrors every packet twice", 12),
        ["round 72:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 72: the cluster mirrors every packet twice", 16),
        ["round 72: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 72: the cluster mirrors every packet twice", 24),
        ["round 72: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 72: the cluster mirrors every packet twice", 32), ["round 72: the cluster mirrors", "every packet twice"]),
    (
        ("round 72: ranking uses tokens learned from the corpus", 4),
        ["round", "72:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 72: ranking uses tokens learned from the corpus", 8),
        ["round", "72:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 72: ranking uses tokens learned from the corpus", 12),
        ["round 72:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 72: ranking uses tokens learned from the corpus", 16),
        ["round 72:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 72: ranking uses tokens learned from the corpus", 24),
        ["round 72: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 72: ranking uses tokens learned from the corpus", 32),
        ["round 72: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 72: a long session ends when the candle dies", 4),
        ["round", "72:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 72: a long session ends when the candle dies", 8),
        ["round", "72: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 72: a long session ends when the candle dies", 12),
        ["round 72: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 72: a long session ends when the candle dies", 16),
        ["round 72: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 72: a long session ends when the candle dies", 24),
        ["round 72: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 72: a long session ends when the candle dies", 32),
        ["round 72: a long session ends", "when the candle dies"],
    ),
    (
        ("round 72: encode the prompt then map the result", 4),
        ["round", "72:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 72: encode the prompt then map the result", 8),
        ["round", "72:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 72: encode the prompt then map the result", 12),
        ["round 72:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 72: encode the prompt then map the result", 16),
        ["round 72: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 72: encode the prompt then map the result", 24),
        ["round 72: encode the", "prompt then map the", "result"],
    ),
    (("round 72: encode the prompt then map the result", 32), ["round 72: encode the prompt then", "map the result"]),
    (
        ("round 72: the kernel wakes the worker at dawn", 4),
        ["round", "72:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 72: the kernel wakes the worker at dawn", 8),
        ["round", "72: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 72: the kernel wakes the worker at dawn", 12),
        ["round 72:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 72: the kernel wakes the worker at dawn", 16), ["round 72: the", "kernel wakes the", "worker at dawn"]),
    (("round 72: the kernel wakes the worker at dawn", 24), ["round 72: the kernel", "wakes the worker at dawn"]),
    (("round 72: the kernel wakes the worker at dawn", 32), ["round 72: the kernel wakes the", "worker at dawn"]),
    (
        ("round 72: service latency drops after the patch", 4),
        ["round", "72:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 72: service latency drops after the patch", 8),
        ["round", "72:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 72: service latency drops after the patch", 12),
        ["round 72:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 72: service latency drops after the patch", 16),
        ["round 72:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 72: service latency drops after the patch", 24),
        ["round 72: service", "latency drops after the", "patch"],
    ),
    (("round 72: service latency drops after the patch", 32), ["round 72: service latency drops", "after the patch"]),
    (
        ("round 72: the library caches every vector it sees", 4),
        ["round", "72:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 72: the library caches every vector it sees", 8),
        ["round", "72: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 72: the library caches every vector it sees", 12),
        ["round 72:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 72: the library caches every vector it sees", 16),
        ["round 72: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 72: the library caches every vector it sees", 24),
        ["round 72: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 72: the library caches every vector it sees", 32),
        ["round 72: the library caches", "every vector it sees"],
    ),
    (
        ("round 72: agents argue then the debate resolves", 4),
        ["round", "72:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 72: agents argue then the debate resolves", 8),
        ["round", "72:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 72: agents argue then the debate resolves", 12),
        ["round 72:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 72: agents argue then the debate resolves", 16),
        ["round 72: agents", "argue then the", "debate resolves"],
    ),
    (("round 72: agents argue then the debate resolves", 24), ["round 72: agents argue", "then the debate resolves"]),
    (("round 72: agents argue then the debate resolves", 32), ["round 72: agents argue then the", "debate resolves"]),
    (
        ("round 72: the filter keeps only strong matches", 4),
        ["round", "72:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 72: the filter keeps only strong matches", 8),
        ["round", "72: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 72: the filter keeps only strong matches", 12),
        ["round 72:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 72: the filter keeps only strong matches", 16),
        ["round 72: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 72: the filter keeps only strong matches", 24), ["round 72: the filter", "keeps only strong", "matches"]),
    (("round 72: the filter keeps only strong matches", 32), ["round 72: the filter keeps only", "strong matches"]),
    (
        ("round 72: the model answers with a short reply", 4),
        ["round", "72:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 72: the model answers with a short reply", 8),
        ["round", "72: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 72: the model answers with a short reply", 12),
        ["round 72:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 72: the model answers with a short reply", 16),
        ["round 72: the", "model answers", "with a short", "reply"],
    ),
    (("round 72: the model answers with a short reply", 24), ["round 72: the model", "answers with a short", "reply"]),
    (("round 72: the model answers with a short reply", 32), ["round 72: the model answers with", "a short reply"]),
    (
        ("round 72: the recorder stores the reasoning trace", 4),
        ["round", "72:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 72: the recorder stores the reasoning trace", 8),
        ["round", "72: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 72: the recorder stores the reasoning trace", 12),
        ["round 72:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 72: the recorder stores the reasoning trace", 16),
        ["round 72: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 72: the recorder stores the reasoning trace", 24),
        ["round 72: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 72: the recorder stores the reasoning trace", 32),
        ["round 72: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 72: the angel watches the processor run", 4),
        ["round", "72:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 72: the angel watches the processor run", 8),
        ["round", "72: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 72: the angel watches the processor run", 12),
        ["round 72:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 72: the angel watches the processor run", 16), ["round 72: the", "angel watches", "the processor", "run"]),
    (("round 72: the angel watches the processor run", 24), ["round 72: the angel", "watches the processor", "run"]),
    (("round 72: the angel watches the processor run", 32), ["round 72: the angel watches the", "processor run"]),
    (
        ("round 72: angle of the vector decides the match", 4),
        ["round", "72:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 72: angle of the vector decides the match", 8),
        ["round", "72:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 72: angle of the vector decides the match", 12),
        ["round 72:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 72: angle of the vector decides the match", 16),
        ["round 72: angle", "of the vector", "decides the", "match"],
    ),
    (("round 72: angle of the vector decides the match", 24), ["round 72: angle of the", "vector decides the match"]),
    (("round 72: angle of the vector decides the match", 32), ["round 72: angle of the vector", "decides the match"]),
    (
        ("round 72: the candle burns twice as long at night", 4),
        ["round", "72:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 72: the candle burns twice as long at night", 8),
        ["round", "72: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 72: the candle burns twice as long at night", 12),
        ["round 72:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 72: the candle burns twice as long at night", 16),
        ["round 72: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 72: the candle burns twice as long at night", 24),
        ["round 72: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 72: the candle burns twice as long at night", 32),
        ["round 72: the candle burns twice", "as long at night"],
    ),
    (
        ("round 72: a mirror of the universe in one line", 4),
        ["round", "72:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 72: a mirror of the universe in one line", 8),
        ["round", "72: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 72: a mirror of the universe in one line", 12),
        ["round 72: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 72: a mirror of the universe in one line", 16),
        ["round 72: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 72: a mirror of the universe in one line", 24), ["round 72: a mirror of", "the universe in one line"]),
    (("round 72: a mirror of the universe in one line", 32), ["round 72: a mirror of the", "universe in one line"]),
    (
        ("round 72: the queue drains before the storm", 4),
        ["round", "72:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 72: the queue drains before the storm", 8),
        ["round", "72: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 72: the queue drains before the storm", 12), ["round 72:", "the queue", "drains", "before the", "storm"]),
    (("round 72: the queue drains before the storm", 16), ["round 72: the", "queue drains", "before the storm"]),
    (("round 72: the queue drains before the storm", 24), ["round 72: the queue", "drains before the storm"]),
    (("round 72: the queue drains before the storm", 32), ["round 72: the queue drains", "before the storm"]),
    (
        ("kitten72 sitting72 agent72 angle72 universe72 memory72", 6),
        ["kitten72", "sitting72", "agent72", "angle72", "universe72", "memory72"],
    ),
    (
        ("kitten72 sitting72 agent72 angle72 universe72 memory72", 10),
        ["kitten72", "sitting72", "agent72", "angle72", "universe72", "memory72"],
    ),
    (
        ("kitten72 sitting72 agent72 angle72 universe72 memory72", 18),
        ["kitten72 sitting72", "agent72 angle72", "universe72", "memory72"],
    ),
    (
        ("kitten72 sitting72 agent72 angle72 universe72 memory72", 28),
        ["kitten72 sitting72 agent72", "angle72 universe72 memory72"],
    ),
    (
        ("sitting72 agent72 angle72 universe72 memory72 stream72", 6),
        ["sitting72", "agent72", "angle72", "universe72", "memory72", "stream72"],
    ),
    (
        ("sitting72 agent72 angle72 universe72 memory72 stream72", 10),
        ["sitting72", "agent72", "angle72", "universe72", "memory72", "stream72"],
    ),
    (
        ("sitting72 agent72 angle72 universe72 memory72 stream72", 18),
        ["sitting72 agent72", "angle72 universe72", "memory72 stream72"],
    ),
    (
        ("sitting72 agent72 angle72 universe72 memory72 stream72", 28),
        ["sitting72 agent72 angle72", "universe72 memory72 stream72"],
    ),
    (
        ("agent72 angle72 universe72 memory72 stream72 context72", 6),
        ["agent72", "angle72", "universe72", "memory72", "stream72", "context72"],
    ),
    (
        ("agent72 angle72 universe72 memory72 stream72 context72", 10),
        ["agent72", "angle72", "universe72", "memory72", "stream72", "context72"],
    ),
    (
        ("agent72 angle72 universe72 memory72 stream72 context72", 18),
        ["agent72 angle72", "universe72", "memory72 stream72", "context72"],
    ),
    (
        ("agent72 angle72 universe72 memory72 stream72 context72", 28),
        ["agent72 angle72 universe72", "memory72 stream72 context72"],
    ),
    (
        ("angle72 universe72 memory72 stream72 context72 knowledge72", 6),
        ["angle72", "universe72", "memory72", "stream72", "context72", "knowledge72"],
    ),
    (
        ("angle72 universe72 memory72 stream72 context72 knowledge72", 10),
        ["angle72", "universe72", "memory72", "stream72", "context72", "knowledge72"],
    ),
    (
        ("angle72 universe72 memory72 stream72 context72 knowledge72", 18),
        ["angle72 universe72", "memory72 stream72", "context72", "knowledge72"],
    ),
    (
        ("angle72 universe72 memory72 stream72 context72 knowledge72", 28),
        ["angle72 universe72 memory72", "stream72 context72", "knowledge72"],
    ),
    (
        ("universe72 memory72 stream72 context72 knowledge72 vector72", 6),
        ["universe72", "memory72", "stream72", "context72", "knowledge72", "vector72"],
    ),
    (
        ("universe72 memory72 stream72 context72 knowledge72 vector72", 10),
        ["universe72", "memory72", "stream72", "context72", "knowledge72", "vector72"],
    ),
    (
        ("universe72 memory72 stream72 context72 knowledge72 vector72", 18),
        ["universe72", "memory72 stream72", "context72", "knowledge72", "vector72"],
    ),
    (
        ("universe72 memory72 stream72 context72 knowledge72 vector72", 28),
        ["universe72 memory72 stream72", "context72 knowledge72", "vector72"],
    ),
    (
        ("memory72 stream72 context72 knowledge72 vector72 processor72", 6),
        ["memory72", "stream72", "context72", "knowledge72", "vector72", "processor72"],
    ),
    (
        ("memory72 stream72 context72 knowledge72 vector72 processor72", 10),
        ["memory72", "stream72", "context72", "knowledge72", "vector72", "processor72"],
    ),
    (
        ("memory72 stream72 context72 knowledge72 vector72 processor72", 18),
        ["memory72 stream72", "context72", "knowledge72", "vector72", "processor72"],
    ),
    (
        ("memory72 stream72 context72 knowledge72 vector72 processor72", 28),
        ["memory72 stream72 context72", "knowledge72 vector72", "processor72"],
    ),
    (
        ("stream72 context72 knowledge72 vector72 processor72 reasoning72", 6),
        ["stream72", "context72", "knowledge72", "vector72", "processor72", "reasoning72"],
    ),
    (
        ("stream72 context72 knowledge72 vector72 processor72 reasoning72", 10),
        ["stream72", "context72", "knowledge72", "vector72", "processor72", "reasoning72"],
    ),
    (
        ("stream72 context72 knowledge72 vector72 processor72 reasoning72", 18),
        ["stream72 context72", "knowledge72", "vector72", "processor72", "reasoning72"],
    ),
    (
        ("stream72 context72 knowledge72 vector72 processor72 reasoning72", 28),
        ["stream72 context72", "knowledge72 vector72", "processor72 reasoning72"],
    ),
    (
        ("context72 knowledge72 vector72 processor72 reasoning72 machine72", 6),
        ["context72", "knowledge72", "vector72", "processor72", "reasoning72", "machine72"],
    ),
    (
        ("context72 knowledge72 vector72 processor72 reasoning72 machine72", 10),
        ["context72", "knowledge72", "vector72", "processor72", "reasoning72", "machine72"],
    ),
    (
        ("context72 knowledge72 vector72 processor72 reasoning72 machine72", 18),
        ["context72", "knowledge72", "vector72", "processor72", "reasoning72", "machine72"],
    ),
    (
        ("context72 knowledge72 vector72 processor72 reasoning72 machine72", 28),
        ["context72 knowledge72", "vector72 processor72", "reasoning72 machine72"],
    ),
    (
        ("knowledge72 vector72 processor72 reasoning72 machine72 learning72", 6),
        ["knowledge72", "vector72", "processor72", "reasoning72", "machine72", "learning72"],
    ),
    (
        ("knowledge72 vector72 processor72 reasoning72 machine72 learning72", 10),
        ["knowledge72", "vector72", "processor72", "reasoning72", "machine72", "learning72"],
    ),
    (
        ("knowledge72 vector72 processor72 reasoning72 machine72 learning72", 18),
        ["knowledge72", "vector72", "processor72", "reasoning72", "machine72", "learning72"],
    ),
    (
        ("knowledge72 vector72 processor72 reasoning72 machine72 learning72", 28),
        ["knowledge72 vector72", "processor72 reasoning72", "machine72 learning72"],
    ),
    (
        ("vector72 processor72 reasoning72 machine72 learning72 model72", 6),
        ["vector72", "processor72", "reasoning72", "machine72", "learning72", "model72"],
    ),
    (
        ("vector72 processor72 reasoning72 machine72 learning72 model72", 10),
        ["vector72", "processor72", "reasoning72", "machine72", "learning72", "model72"],
    ),
    (
        ("vector72 processor72 reasoning72 machine72 learning72 model72", 18),
        ["vector72", "processor72", "reasoning72", "machine72", "learning72 model72"],
    ),
    (
        ("vector72 processor72 reasoning72 machine72 learning72 model72", 28),
        ["vector72 processor72", "reasoning72 machine72", "learning72 model72"],
    ),
    (
        ("processor72 reasoning72 machine72 learning72 model72 token72", 6),
        ["processor72", "reasoning72", "machine72", "learning72", "model72", "token72"],
    ),
    (
        ("processor72 reasoning72 machine72 learning72 model72 token72", 10),
        ["processor72", "reasoning72", "machine72", "learning72", "model72", "token72"],
    ),
    (
        ("processor72 reasoning72 machine72 learning72 model72 token72", 18),
        ["processor72", "reasoning72", "machine72", "learning72 model72", "token72"],
    ),
    (
        ("processor72 reasoning72 machine72 learning72 model72 token72", 28),
        ["processor72 reasoning72", "machine72 learning72 model72", "token72"],
    ),
    (
        ("reasoning72 machine72 learning72 model72 token72 prompt72", 6),
        ["reasoning72", "machine72", "learning72", "model72", "token72", "prompt72"],
    ),
    (
        ("reasoning72 machine72 learning72 model72 token72 prompt72", 10),
        ["reasoning72", "machine72", "learning72", "model72", "token72", "prompt72"],
    ),
    (
        ("reasoning72 machine72 learning72 model72 token72 prompt72", 18),
        ["reasoning72", "machine72", "learning72 model72", "token72 prompt72"],
    ),
    (
        ("reasoning72 machine72 learning72 model72 token72 prompt72", 28),
        ["reasoning72 machine72", "learning72 model72 token72", "prompt72"],
    ),
    (
        ("machine72 learning72 model72 token72 prompt72 session72", 6),
        ["machine72", "learning72", "model72", "token72", "prompt72", "session72"],
    ),
    (
        ("machine72 learning72 model72 token72 prompt72 session72", 10),
        ["machine72", "learning72", "model72", "token72", "prompt72", "session72"],
    ),
    (
        ("machine72 learning72 model72 token72 prompt72 session72", 18),
        ["machine72", "learning72 model72", "token72 prompt72", "session72"],
    ),
    (
        ("machine72 learning72 model72 token72 prompt72 session72", 28),
        ["machine72 learning72 model72", "token72 prompt72 session72"],
    ),
    (
        ("learning72 model72 token72 prompt72 session72 library72", 6),
        ["learning72", "model72", "token72", "prompt72", "session72", "library72"],
    ),
    (
        ("learning72 model72 token72 prompt72 session72 library72", 10),
        ["learning72", "model72", "token72", "prompt72", "session72", "library72"],
    ),
    (
        ("learning72 model72 token72 prompt72 session72 library72", 18),
        ["learning72 model72", "token72 prompt72", "session72", "library72"],
    ),
    (
        ("learning72 model72 token72 prompt72 session72 library72", 28),
        ["learning72 model72 token72", "prompt72 session72 library72"],
    ),
    (
        ("model72 token72 prompt72 session72 library72 service72", 6),
        ["model72", "token72", "prompt72", "session72", "library72", "service72"],
    ),
    (
        ("model72 token72 prompt72 session72 library72 service72", 10),
        ["model72", "token72", "prompt72", "session72", "library72", "service72"],
    ),
    (
        ("model72 token72 prompt72 session72 library72 service72", 18),
        ["model72 token72", "prompt72 session72", "library72", "service72"],
    ),
    (
        ("model72 token72 prompt72 session72 library72 service72", 28),
        ["model72 token72 prompt72", "session72 library72", "service72"],
    ),
    (
        ("token72 prompt72 session72 library72 service72 gateway72", 6),
        ["token72", "prompt72", "session72", "library72", "service72", "gateway72"],
    ),
    (
        ("token72 prompt72 session72 library72 service72 gateway72", 10),
        ["token72", "prompt72", "session72", "library72", "service72", "gateway72"],
    ),
    (
        ("token72 prompt72 session72 library72 service72 gateway72", 18),
        ["token72 prompt72", "session72", "library72", "service72", "gateway72"],
    ),
    (
        ("token72 prompt72 session72 library72 service72 gateway72", 28),
        ["token72 prompt72 session72", "library72 service72", "gateway72"],
    ),
    (
        ("prompt72 session72 library72 service72 gateway72 storage72", 6),
        ["prompt72", "session72", "library72", "service72", "gateway72", "storage72"],
    ),
    (
        ("prompt72 session72 library72 service72 gateway72 storage72", 10),
        ["prompt72", "session72", "library72", "service72", "gateway72", "storage72"],
    ),
    (
        ("prompt72 session72 library72 service72 gateway72 storage72", 18),
        ["prompt72 session72", "library72", "service72", "gateway72", "storage72"],
    ),
    (
        ("prompt72 session72 library72 service72 gateway72 storage72", 28),
        ["prompt72 session72 library72", "service72 gateway72", "storage72"],
    ),
    (
        ("session72 library72 service72 gateway72 storage72 network72", 6),
        ["session72", "library72", "service72", "gateway72", "storage72", "network72"],
    ),
    (
        ("session72 library72 service72 gateway72 storage72 network72", 10),
        ["session72", "library72", "service72", "gateway72", "storage72", "network72"],
    ),
    (
        ("session72 library72 service72 gateway72 storage72 network72", 18),
        ["session72", "library72", "service72", "gateway72", "storage72", "network72"],
    ),
    (
        ("session72 library72 service72 gateway72 storage72 network72", 28),
        ["session72 library72", "service72 gateway72", "storage72 network72"],
    ),
    (
        ("library72 service72 gateway72 storage72 network72 latency72", 6),
        ["library72", "service72", "gateway72", "storage72", "network72", "latency72"],
    ),
    (
        ("library72 service72 gateway72 storage72 network72 latency72", 10),
        ["library72", "service72", "gateway72", "storage72", "network72", "latency72"],
    ),
    (
        ("library72 service72 gateway72 storage72 network72 latency72", 18),
        ["library72", "service72", "gateway72", "storage72", "network72", "latency72"],
    ),
    (
        ("library72 service72 gateway72 storage72 network72 latency72", 28),
        ["library72 service72", "gateway72 storage72", "network72 latency72"],
    ),
    (
        ("service72 gateway72 storage72 network72 latency72 buffer72", 6),
        ["service72", "gateway72", "storage72", "network72", "latency72", "buffer72"],
    ),
    (
        ("service72 gateway72 storage72 network72 latency72 buffer72", 10),
        ["service72", "gateway72", "storage72", "network72", "latency72", "buffer72"],
    ),
    (
        ("service72 gateway72 storage72 network72 latency72 buffer72", 18),
        ["service72", "gateway72", "storage72", "network72", "latency72 buffer72"],
    ),
    (
        ("service72 gateway72 storage72 network72 latency72 buffer72", 28),
        ["service72 gateway72", "storage72 network72", "latency72 buffer72"],
    ),
    (
        ("gateway72 storage72 network72 latency72 buffer72 queue72", 6),
        ["gateway72", "storage72", "network72", "latency72", "buffer72", "queue72"],
    ),
    (
        ("gateway72 storage72 network72 latency72 buffer72 queue72", 10),
        ["gateway72", "storage72", "network72", "latency72", "buffer72", "queue72"],
    ),
    (
        ("gateway72 storage72 network72 latency72 buffer72 queue72", 18),
        ["gateway72", "storage72", "network72", "latency72 buffer72", "queue72"],
    ),
    (
        ("gateway72 storage72 network72 latency72 buffer72 queue72", 28),
        ["gateway72 storage72", "network72 latency72 buffer72", "queue72"],
    ),
    (
        ("storage72 network72 latency72 buffer72 queue72 worker72", 6),
        ["storage72", "network72", "latency72", "buffer72", "queue72", "worker72"],
    ),
    (
        ("storage72 network72 latency72 buffer72 queue72 worker72", 10),
        ["storage72", "network72", "latency72", "buffer72", "queue72", "worker72"],
    ),
    (
        ("storage72 network72 latency72 buffer72 queue72 worker72", 18),
        ["storage72", "network72", "latency72 buffer72", "queue72 worker72"],
    ),
    (
        ("storage72 network72 latency72 buffer72 queue72 worker72", 28),
        ["storage72 network72", "latency72 buffer72 queue72", "worker72"],
    ),
    (
        ("network72 latency72 buffer72 queue72 worker72 kernel72", 6),
        ["network72", "latency72", "buffer72", "queue72", "worker72", "kernel72"],
    ),
    (
        ("network72 latency72 buffer72 queue72 worker72 kernel72", 10),
        ["network72", "latency72", "buffer72", "queue72", "worker72", "kernel72"],
    ),
    (
        ("network72 latency72 buffer72 queue72 worker72 kernel72", 18),
        ["network72", "latency72 buffer72", "queue72 worker72", "kernel72"],
    ),
    (
        ("network72 latency72 buffer72 queue72 worker72 kernel72", 28),
        ["network72 latency72 buffer72", "queue72 worker72 kernel72"],
    ),
    (
        ("latency72 buffer72 queue72 worker72 kernel72 signal72", 6),
        ["latency72", "buffer72", "queue72", "worker72", "kernel72", "signal72"],
    ),
    (
        ("latency72 buffer72 queue72 worker72 kernel72 signal72", 10),
        ["latency72", "buffer72", "queue72", "worker72", "kernel72", "signal72"],
    ),
    (
        ("latency72 buffer72 queue72 worker72 kernel72 signal72", 18),
        ["latency72 buffer72", "queue72 worker72", "kernel72 signal72"],
    ),
    (
        ("latency72 buffer72 queue72 worker72 kernel72 signal72", 28),
        ["latency72 buffer72 queue72", "worker72 kernel72 signal72"],
    ),
    (
        ("buffer72 queue72 worker72 kernel72 signal72 packet72", 6),
        ["buffer72", "queue72", "worker72", "kernel72", "signal72", "packet72"],
    ),
    (
        ("buffer72 queue72 worker72 kernel72 signal72 packet72", 10),
        ["buffer72", "queue72", "worker72", "kernel72", "signal72", "packet72"],
    ),
    (
        ("buffer72 queue72 worker72 kernel72 signal72 packet72", 18),
        ["buffer72 queue72", "worker72 kernel72", "signal72 packet72"],
    ),
    (
        ("buffer72 queue72 worker72 kernel72 signal72 packet72", 28),
        ["buffer72 queue72 worker72", "kernel72 signal72 packet72"],
    ),
    (
        ("queue72 worker72 kernel72 signal72 packet72 router72", 6),
        ["queue72", "worker72", "kernel72", "signal72", "packet72", "router72"],
    ),
    (
        ("queue72 worker72 kernel72 signal72 packet72 router72", 10),
        ["queue72", "worker72", "kernel72", "signal72", "packet72", "router72"],
    ),
    (
        ("queue72 worker72 kernel72 signal72 packet72 router72", 18),
        ["queue72 worker72", "kernel72 signal72", "packet72 router72"],
    ),
    (
        ("queue72 worker72 kernel72 signal72 packet72 router72", 28),
        ["queue72 worker72 kernel72", "signal72 packet72 router72"],
    ),
    (
        ("worker72 kernel72 signal72 packet72 router72 cluster72", 6),
        ["worker72", "kernel72", "signal72", "packet72", "router72", "cluster72"],
    ),
    (
        ("worker72 kernel72 signal72 packet72 router72 cluster72", 10),
        ["worker72", "kernel72", "signal72", "packet72", "router72", "cluster72"],
    ),
    (
        ("worker72 kernel72 signal72 packet72 router72 cluster72", 18),
        ["worker72 kernel72", "signal72 packet72", "router72 cluster72"],
    ),
    (
        ("worker72 kernel72 signal72 packet72 router72 cluster72", 28),
        ["worker72 kernel72 signal72", "packet72 router72 cluster72"],
    ),
    (
        ("kernel72 signal72 packet72 router72 cluster72 mirror72", 6),
        ["kernel72", "signal72", "packet72", "router72", "cluster72", "mirror72"],
    ),
    (
        ("kernel72 signal72 packet72 router72 cluster72 mirror72", 10),
        ["kernel72", "signal72", "packet72", "router72", "cluster72", "mirror72"],
    ),
    (
        ("kernel72 signal72 packet72 router72 cluster72 mirror72", 18),
        ["kernel72 signal72", "packet72 router72", "cluster72 mirror72"],
    ),
    (
        ("kernel72 signal72 packet72 router72 cluster72 mirror72", 28),
        ["kernel72 signal72 packet72", "router72 cluster72 mirror72"],
    ),
    (
        ("signal72 packet72 router72 cluster72 mirror72 filter72", 6),
        ["signal72", "packet72", "router72", "cluster72", "mirror72", "filter72"],
    ),
    (
        ("signal72 packet72 router72 cluster72 mirror72 filter72", 10),
        ["signal72", "packet72", "router72", "cluster72", "mirror72", "filter72"],
    ),
    (
        ("signal72 packet72 router72 cluster72 mirror72 filter72", 18),
        ["signal72 packet72", "router72 cluster72", "mirror72 filter72"],
    ),
    (
        ("signal72 packet72 router72 cluster72 mirror72 filter72", 28),
        ["signal72 packet72 router72", "cluster72 mirror72 filter72"],
    ),
    (
        ("packet72 router72 cluster72 mirror72 filter72 ranking72", 6),
        ["packet72", "router72", "cluster72", "mirror72", "filter72", "ranking72"],
    ),
    (
        ("packet72 router72 cluster72 mirror72 filter72 ranking72", 10),
        ["packet72", "router72", "cluster72", "mirror72", "filter72", "ranking72"],
    ),
    (
        ("packet72 router72 cluster72 mirror72 filter72 ranking72", 18),
        ["packet72 router72", "cluster72 mirror72", "filter72 ranking72"],
    ),
    (
        ("packet72 router72 cluster72 mirror72 filter72 ranking72", 28),
        ["packet72 router72 cluster72", "mirror72 filter72 ranking72"],
    ),
    (
        ("router72 cluster72 mirror72 filter72 ranking72 encoding72", 6),
        ["router72", "cluster72", "mirror72", "filter72", "ranking72", "encoding72"],
    ),
    (
        ("router72 cluster72 mirror72 filter72 ranking72 encoding72", 10),
        ["router72", "cluster72", "mirror72", "filter72", "ranking72", "encoding72"],
    ),
    (
        ("router72 cluster72 mirror72 filter72 ranking72 encoding72", 18),
        ["router72 cluster72", "mirror72 filter72", "ranking72", "encoding72"],
    ),
    (
        ("router72 cluster72 mirror72 filter72 ranking72 encoding72", 28),
        ["router72 cluster72 mirror72", "filter72 ranking72", "encoding72"],
    ),
    (
        ("cluster72 mirror72 filter72 ranking72 encoding72 mapping72", 6),
        ["cluster72", "mirror72", "filter72", "ranking72", "encoding72", "mapping72"],
    ),
    (
        ("cluster72 mirror72 filter72 ranking72 encoding72 mapping72", 10),
        ["cluster72", "mirror72", "filter72", "ranking72", "encoding72", "mapping72"],
    ),
    (
        ("cluster72 mirror72 filter72 ranking72 encoding72 mapping72", 18),
        ["cluster72 mirror72", "filter72 ranking72", "encoding72", "mapping72"],
    ),
    (
        ("cluster72 mirror72 filter72 ranking72 encoding72 mapping72", 28),
        ["cluster72 mirror72 filter72", "ranking72 encoding72", "mapping72"],
    ),
    (
        ("mirror72 filter72 ranking72 encoding72 mapping72 record72", 6),
        ["mirror72", "filter72", "ranking72", "encoding72", "mapping72", "record72"],
    ),
    (
        ("mirror72 filter72 ranking72 encoding72 mapping72 record72", 10),
        ["mirror72", "filter72", "ranking72", "encoding72", "mapping72", "record72"],
    ),
    (
        ("mirror72 filter72 ranking72 encoding72 mapping72 record72", 18),
        ["mirror72 filter72", "ranking72", "encoding72", "mapping72 record72"],
    ),
    (
        ("mirror72 filter72 ranking72 encoding72 mapping72 record72", 28),
        ["mirror72 filter72 ranking72", "encoding72 mapping72", "record72"],
    ),
    (
        ("filter72 ranking72 encoding72 mapping72 record72 candle72", 6),
        ["filter72", "ranking72", "encoding72", "mapping72", "record72", "candle72"],
    ),
    (
        ("filter72 ranking72 encoding72 mapping72 record72 candle72", 10),
        ["filter72", "ranking72", "encoding72", "mapping72", "record72", "candle72"],
    ),
    (
        ("filter72 ranking72 encoding72 mapping72 record72 candle72", 18),
        ["filter72 ranking72", "encoding72", "mapping72 record72", "candle72"],
    ),
    (
        ("filter72 ranking72 encoding72 mapping72 record72 candle72", 28),
        ["filter72 ranking72", "encoding72 mapping72", "record72 candle72"],
    ),
    (
        ("ranking72 encoding72 mapping72 record72 candle72 thread72", 6),
        ["ranking72", "encoding72", "mapping72", "record72", "candle72", "thread72"],
    ),
    (
        ("ranking72 encoding72 mapping72 record72 candle72 thread72", 10),
        ["ranking72", "encoding72", "mapping72", "record72", "candle72", "thread72"],
    ),
    (
        ("ranking72 encoding72 mapping72 record72 candle72 thread72", 18),
        ["ranking72", "encoding72", "mapping72 record72", "candle72 thread72"],
    ),
    (
        ("ranking72 encoding72 mapping72 record72 candle72 thread72", 28),
        ["ranking72 encoding72", "mapping72 record72 candle72", "thread72"],
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
