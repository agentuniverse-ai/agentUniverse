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
        ("round 123: the quick brown fox jumps over the lazy dog", 4),
        ["round", "123:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 123: the quick brown fox jumps over the lazy dog", 8),
        ["round", "123: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 123: the quick brown fox jumps over the lazy dog", 12),
        ["round 123:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 123: the quick brown fox jumps over the lazy dog", 16),
        ["round 123: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 123: the quick brown fox jumps over the lazy dog", 24),
        ["round 123: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 123: the quick brown fox jumps over the lazy dog", 32),
        ["round 123: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 123: agentuniverse is a framework for multi agents", 4),
        ["round", "123:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 123: agentuniverse is a framework for multi agents", 8),
        ["round", "123:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 123: agentuniverse is a framework for multi agents", 12),
        ["round 123:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 123: agentuniverse is a framework for multi agents", 16),
        ["round 123:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 123: agentuniverse is a framework for multi agents", 24),
        ["round 123: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 123: agentuniverse is a framework for multi agents", 32),
        ["round 123: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 123: knowledge stored as vectors enables retrieval", 4),
        ["round", "123:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 123: knowledge stored as vectors enables retrieval", 8),
        ["round", "123:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 123: knowledge stored as vectors enables retrieval", 12),
        ["round 123:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 123: knowledge stored as vectors enables retrieval", 16),
        ["round 123:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 123: knowledge stored as vectors enables retrieval", 24),
        ["round 123: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 123: knowledge stored as vectors enables retrieval", 32),
        ["round 123: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 123: the processor reads the record then stops", 4),
        ["round", "123:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 123: the processor reads the record then stops", 8),
        ["round", "123: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 123: the processor reads the record then stops", 12),
        ["round 123:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 123: the processor reads the record then stops", 16),
        ["round 123: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 123: the processor reads the record then stops", 24),
        ["round 123: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 123: the processor reads the record then stops", 32),
        ["round 123: the processor reads", "the record then stops"],
    ),
    (
        ("round 123: a worker pulls the next task from the queue", 4),
        ["round", "123:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 123: a worker pulls the next task from the queue", 8),
        ["round", "123: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 123: a worker pulls the next task from the queue", 12),
        ["round 123: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 123: a worker pulls the next task from the queue", 16),
        ["round 123: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 123: a worker pulls the next task from the queue", 24),
        ["round 123: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 123: a worker pulls the next task from the queue", 32),
        ["round 123: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 123: signals travel through the network layer", 4),
        ["round", "123:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 123: signals travel through the network layer", 8),
        ["round", "123:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 123: signals travel through the network layer", 12),
        ["round 123:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 123: signals travel through the network layer", 16),
        ["round 123:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 123: signals travel through the network layer", 24),
        ["round 123: signals", "travel through the", "network layer"],
    ),
    (
        ("round 123: signals travel through the network layer", 32),
        ["round 123: signals travel", "through the network layer"],
    ),
    (
        ("round 123: the gateway routes each request by policy", 4),
        ["round", "123:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 123: the gateway routes each request by policy", 8),
        ["round", "123: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 123: the gateway routes each request by policy", 12),
        ["round 123:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 123: the gateway routes each request by policy", 16),
        ["round 123: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 123: the gateway routes each request by policy", 24),
        ["round 123: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 123: the gateway routes each request by policy", 32),
        ["round 123: the gateway routes", "each request by policy"],
    ),
    (
        ("round 123: memory grows until the buffer is full", 4),
        ["round", "123:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 123: memory grows until the buffer is full", 8),
        ["round", "123:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 123: memory grows until the buffer is full", 12),
        ["round 123:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 123: memory grows until the buffer is full", 16),
        ["round 123:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 123: memory grows until the buffer is full", 24), ["round 123: memory grows", "until the buffer is full"]),
    (("round 123: memory grows until the buffer is full", 32), ["round 123: memory grows until", "the buffer is full"]),
    (
        ("round 123: the cluster mirrors every packet twice", 4),
        ["round", "123:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 123: the cluster mirrors every packet twice", 8),
        ["round", "123: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 123: the cluster mirrors every packet twice", 12),
        ["round 123:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 123: the cluster mirrors every packet twice", 16),
        ["round 123: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 123: the cluster mirrors every packet twice", 24),
        ["round 123: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 123: the cluster mirrors every packet twice", 32),
        ["round 123: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 123: ranking uses tokens learned from the corpus", 4),
        ["round", "123:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 123: ranking uses tokens learned from the corpus", 8),
        ["round", "123:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 123: ranking uses tokens learned from the corpus", 12),
        ["round 123:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 123: ranking uses tokens learned from the corpus", 16),
        ["round 123:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 123: ranking uses tokens learned from the corpus", 24),
        ["round 123: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 123: ranking uses tokens learned from the corpus", 32),
        ["round 123: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 123: a long session ends when the candle dies", 4),
        ["round", "123:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 123: a long session ends when the candle dies", 8),
        ["round", "123: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 123: a long session ends when the candle dies", 12),
        ["round 123: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 123: a long session ends when the candle dies", 16),
        ["round 123: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 123: a long session ends when the candle dies", 24),
        ["round 123: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 123: a long session ends when the candle dies", 32),
        ["round 123: a long session ends", "when the candle dies"],
    ),
    (
        ("round 123: encode the prompt then map the result", 4),
        ["round", "123:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 123: encode the prompt then map the result", 8),
        ["round", "123:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 123: encode the prompt then map the result", 12),
        ["round 123:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 123: encode the prompt then map the result", 16),
        ["round 123:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 123: encode the prompt then map the result", 24),
        ["round 123: encode the", "prompt then map the", "result"],
    ),
    (("round 123: encode the prompt then map the result", 32), ["round 123: encode the prompt", "then map the result"]),
    (
        ("round 123: the kernel wakes the worker at dawn", 4),
        ["round", "123:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 123: the kernel wakes the worker at dawn", 8),
        ["round", "123: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 123: the kernel wakes the worker at dawn", 12),
        ["round 123:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 123: the kernel wakes the worker at dawn", 16), ["round 123: the", "kernel wakes the", "worker at dawn"]),
    (("round 123: the kernel wakes the worker at dawn", 24), ["round 123: the kernel", "wakes the worker at dawn"]),
    (("round 123: the kernel wakes the worker at dawn", 32), ["round 123: the kernel wakes the", "worker at dawn"]),
    (
        ("round 123: service latency drops after the patch", 4),
        ["round", "123:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 123: service latency drops after the patch", 8),
        ["round", "123:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 123: service latency drops after the patch", 12),
        ["round 123:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 123: service latency drops after the patch", 16),
        ["round 123:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 123: service latency drops after the patch", 24),
        ["round 123: service", "latency drops after the", "patch"],
    ),
    (("round 123: service latency drops after the patch", 32), ["round 123: service latency drops", "after the patch"]),
    (
        ("round 123: the library caches every vector it sees", 4),
        ["round", "123:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 123: the library caches every vector it sees", 8),
        ["round", "123: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 123: the library caches every vector it sees", 12),
        ["round 123:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 123: the library caches every vector it sees", 16),
        ["round 123: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 123: the library caches every vector it sees", 24),
        ["round 123: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 123: the library caches every vector it sees", 32),
        ["round 123: the library caches", "every vector it sees"],
    ),
    (
        ("round 123: agents argue then the debate resolves", 4),
        ["round", "123:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 123: agents argue then the debate resolves", 8),
        ["round", "123:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 123: agents argue then the debate resolves", 12),
        ["round 123:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 123: agents argue then the debate resolves", 16),
        ["round 123:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 123: agents argue then the debate resolves", 24), ["round 123: agents argue", "then the debate resolves"]),
    (("round 123: agents argue then the debate resolves", 32), ["round 123: agents argue then the", "debate resolves"]),
    (
        ("round 123: the filter keeps only strong matches", 4),
        ["round", "123:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 123: the filter keeps only strong matches", 8),
        ["round", "123: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 123: the filter keeps only strong matches", 12),
        ["round 123:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 123: the filter keeps only strong matches", 16),
        ["round 123: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 123: the filter keeps only strong matches", 24),
        ["round 123: the filter", "keeps only strong", "matches"],
    ),
    (("round 123: the filter keeps only strong matches", 32), ["round 123: the filter keeps only", "strong matches"]),
    (
        ("round 123: the model answers with a short reply", 4),
        ["round", "123:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 123: the model answers with a short reply", 8),
        ["round", "123: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 123: the model answers with a short reply", 12),
        ["round 123:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 123: the model answers with a short reply", 16),
        ["round 123: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 123: the model answers with a short reply", 24),
        ["round 123: the model", "answers with a short", "reply"],
    ),
    (("round 123: the model answers with a short reply", 32), ["round 123: the model answers", "with a short reply"]),
    (
        ("round 123: the recorder stores the reasoning trace", 4),
        ["round", "123:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 123: the recorder stores the reasoning trace", 8),
        ["round", "123: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 123: the recorder stores the reasoning trace", 12),
        ["round 123:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 123: the recorder stores the reasoning trace", 16),
        ["round 123: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 123: the recorder stores the reasoning trace", 24),
        ["round 123: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 123: the recorder stores the reasoning trace", 32),
        ["round 123: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 123: the angel watches the processor run", 4),
        ["round", "123:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 123: the angel watches the processor run", 8),
        ["round", "123: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 123: the angel watches the processor run", 12),
        ["round 123:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 123: the angel watches the processor run", 16),
        ["round 123: the", "angel watches", "the processor", "run"],
    ),
    (("round 123: the angel watches the processor run", 24), ["round 123: the angel", "watches the processor", "run"]),
    (("round 123: the angel watches the processor run", 32), ["round 123: the angel watches the", "processor run"]),
    (
        ("round 123: angle of the vector decides the match", 4),
        ["round", "123:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 123: angle of the vector decides the match", 8),
        ["round", "123:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 123: angle of the vector decides the match", 12),
        ["round 123:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 123: angle of the vector decides the match", 16),
        ["round 123: angle", "of the vector", "decides the", "match"],
    ),
    (("round 123: angle of the vector decides the match", 24), ["round 123: angle of the", "vector decides the match"]),
    (("round 123: angle of the vector decides the match", 32), ["round 123: angle of the vector", "decides the match"]),
    (
        ("round 123: the candle burns twice as long at night", 4),
        ["round", "123:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 123: the candle burns twice as long at night", 8),
        ["round", "123: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 123: the candle burns twice as long at night", 12),
        ["round 123:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 123: the candle burns twice as long at night", 16),
        ["round 123: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 123: the candle burns twice as long at night", 24),
        ["round 123: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 123: the candle burns twice as long at night", 32),
        ["round 123: the candle burns", "twice as long at night"],
    ),
    (
        ("round 123: a mirror of the universe in one line", 4),
        ["round", "123:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 123: a mirror of the universe in one line", 8),
        ["round", "123: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 123: a mirror of the universe in one line", 12),
        ["round 123: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 123: a mirror of the universe in one line", 16),
        ["round 123: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 123: a mirror of the universe in one line", 24), ["round 123: a mirror of", "the universe in one line"]),
    (("round 123: a mirror of the universe in one line", 32), ["round 123: a mirror of the", "universe in one line"]),
    (
        ("round 123: the queue drains before the storm", 4),
        ["round", "123:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 123: the queue drains before the storm", 8),
        ["round", "123: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 123: the queue drains before the storm", 12),
        ["round 123:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 123: the queue drains before the storm", 16), ["round 123: the", "queue drains", "before the storm"]),
    (("round 123: the queue drains before the storm", 24), ["round 123: the queue", "drains before the storm"]),
    (("round 123: the queue drains before the storm", 32), ["round 123: the queue drains", "before the storm"]),
    (
        ("kitten123 sitting123 agent123 angle123 universe123 memory123", 6),
        ["kitten123", "sitting123", "agent123", "angle123", "universe123", "memory123"],
    ),
    (
        ("kitten123 sitting123 agent123 angle123 universe123 memory123", 10),
        ["kitten123", "sitting123", "agent123", "angle123", "universe123", "memory123"],
    ),
    (
        ("kitten123 sitting123 agent123 angle123 universe123 memory123", 18),
        ["kitten123", "sitting123", "agent123 angle123", "universe123", "memory123"],
    ),
    (
        ("kitten123 sitting123 agent123 angle123 universe123 memory123", 28),
        ["kitten123 sitting123", "agent123 angle123", "universe123 memory123"],
    ),
    (
        ("sitting123 agent123 angle123 universe123 memory123 stream123", 6),
        ["sitting123", "agent123", "angle123", "universe123", "memory123", "stream123"],
    ),
    (
        ("sitting123 agent123 angle123 universe123 memory123 stream123", 10),
        ["sitting123", "agent123", "angle123", "universe123", "memory123", "stream123"],
    ),
    (
        ("sitting123 agent123 angle123 universe123 memory123 stream123", 18),
        ["sitting123", "agent123 angle123", "universe123", "memory123", "stream123"],
    ),
    (
        ("sitting123 agent123 angle123 universe123 memory123 stream123", 28),
        ["sitting123 agent123 angle123", "universe123 memory123", "stream123"],
    ),
    (
        ("agent123 angle123 universe123 memory123 stream123 context123", 6),
        ["agent123", "angle123", "universe123", "memory123", "stream123", "context123"],
    ),
    (
        ("agent123 angle123 universe123 memory123 stream123 context123", 10),
        ["agent123", "angle123", "universe123", "memory123", "stream123", "context123"],
    ),
    (
        ("agent123 angle123 universe123 memory123 stream123 context123", 18),
        ["agent123 angle123", "universe123", "memory123", "stream123", "context123"],
    ),
    (
        ("agent123 angle123 universe123 memory123 stream123 context123", 28),
        ["agent123 angle123", "universe123 memory123", "stream123 context123"],
    ),
    (
        ("angle123 universe123 memory123 stream123 context123 knowledge123", 6),
        ["angle123", "universe123", "memory123", "stream123", "context123", "knowledge123"],
    ),
    (
        ("angle123 universe123 memory123 stream123 context123 knowledge123", 10),
        ["angle123", "universe123", "memory123", "stream123", "context123", "knowledge123"],
    ),
    (
        ("angle123 universe123 memory123 stream123 context123 knowledge123", 18),
        ["angle123", "universe123", "memory123", "stream123", "context123", "knowledge123"],
    ),
    (
        ("angle123 universe123 memory123 stream123 context123 knowledge123", 28),
        ["angle123 universe123", "memory123 stream123", "context123 knowledge123"],
    ),
    (
        ("universe123 memory123 stream123 context123 knowledge123 vector123", 6),
        ["universe123", "memory123", "stream123", "context123", "knowledge123", "vector123"],
    ),
    (
        ("universe123 memory123 stream123 context123 knowledge123 vector123", 10),
        ["universe123", "memory123", "stream123", "context123", "knowledge123", "vector123"],
    ),
    (
        ("universe123 memory123 stream123 context123 knowledge123 vector123", 18),
        ["universe123", "memory123", "stream123", "context123", "knowledge123", "vector123"],
    ),
    (
        ("universe123 memory123 stream123 context123 knowledge123 vector123", 28),
        ["universe123 memory123", "stream123 context123", "knowledge123 vector123"],
    ),
    (
        ("memory123 stream123 context123 knowledge123 vector123 processor123", 6),
        ["memory123", "stream123", "context123", "knowledge123", "vector123", "processor123"],
    ),
    (
        ("memory123 stream123 context123 knowledge123 vector123 processor123", 10),
        ["memory123", "stream123", "context123", "knowledge123", "vector123", "processor123"],
    ),
    (
        ("memory123 stream123 context123 knowledge123 vector123 processor123", 18),
        ["memory123", "stream123", "context123", "knowledge123", "vector123", "processor123"],
    ),
    (
        ("memory123 stream123 context123 knowledge123 vector123 processor123", 28),
        ["memory123 stream123", "context123 knowledge123", "vector123 processor123"],
    ),
    (
        ("stream123 context123 knowledge123 vector123 processor123 reasoning123", 6),
        ["stream123", "context123", "knowledge123", "vector123", "processor123", "reasoning123"],
    ),
    (
        ("stream123 context123 knowledge123 vector123 processor123 reasoning123", 10),
        ["stream123", "context123", "knowledge123", "vector123", "processor123", "reasoning123"],
    ),
    (
        ("stream123 context123 knowledge123 vector123 processor123 reasoning123", 18),
        ["stream123", "context123", "knowledge123", "vector123", "processor123", "reasoning123"],
    ),
    (
        ("stream123 context123 knowledge123 vector123 processor123 reasoning123", 28),
        ["stream123 context123", "knowledge123 vector123", "processor123 reasoning123"],
    ),
    (
        ("context123 knowledge123 vector123 processor123 reasoning123 machine123", 6),
        ["context123", "knowledge123", "vector123", "processor123", "reasoning123", "machine123"],
    ),
    (
        ("context123 knowledge123 vector123 processor123 reasoning123 machine123", 10),
        ["context123", "knowledge123", "vector123", "processor123", "reasoning123", "machine123"],
    ),
    (
        ("context123 knowledge123 vector123 processor123 reasoning123 machine123", 18),
        ["context123", "knowledge123", "vector123", "processor123", "reasoning123", "machine123"],
    ),
    (
        ("context123 knowledge123 vector123 processor123 reasoning123 machine123", 28),
        ["context123 knowledge123", "vector123 processor123", "reasoning123 machine123"],
    ),
    (
        ("knowledge123 vector123 processor123 reasoning123 machine123 learning123", 6),
        ["knowledge123", "vector123", "processor123", "reasoning123", "machine123", "learning123"],
    ),
    (
        ("knowledge123 vector123 processor123 reasoning123 machine123 learning123", 10),
        ["knowledge123", "vector123", "processor123", "reasoning123", "machine123", "learning123"],
    ),
    (
        ("knowledge123 vector123 processor123 reasoning123 machine123 learning123", 18),
        ["knowledge123", "vector123", "processor123", "reasoning123", "machine123", "learning123"],
    ),
    (
        ("knowledge123 vector123 processor123 reasoning123 machine123 learning123", 28),
        ["knowledge123 vector123", "processor123 reasoning123", "machine123 learning123"],
    ),
    (
        ("vector123 processor123 reasoning123 machine123 learning123 model123", 6),
        ["vector123", "processor123", "reasoning123", "machine123", "learning123", "model123"],
    ),
    (
        ("vector123 processor123 reasoning123 machine123 learning123 model123", 10),
        ["vector123", "processor123", "reasoning123", "machine123", "learning123", "model123"],
    ),
    (
        ("vector123 processor123 reasoning123 machine123 learning123 model123", 18),
        ["vector123", "processor123", "reasoning123", "machine123", "learning123", "model123"],
    ),
    (
        ("vector123 processor123 reasoning123 machine123 learning123 model123", 28),
        ["vector123 processor123", "reasoning123 machine123", "learning123 model123"],
    ),
    (
        ("processor123 reasoning123 machine123 learning123 model123 token123", 6),
        ["processor123", "reasoning123", "machine123", "learning123", "model123", "token123"],
    ),
    (
        ("processor123 reasoning123 machine123 learning123 model123 token123", 10),
        ["processor123", "reasoning123", "machine123", "learning123", "model123", "token123"],
    ),
    (
        ("processor123 reasoning123 machine123 learning123 model123 token123", 18),
        ["processor123", "reasoning123", "machine123", "learning123", "model123 token123"],
    ),
    (
        ("processor123 reasoning123 machine123 learning123 model123 token123", 28),
        ["processor123 reasoning123", "machine123 learning123", "model123 token123"],
    ),
    (
        ("reasoning123 machine123 learning123 model123 token123 prompt123", 6),
        ["reasoning123", "machine123", "learning123", "model123", "token123", "prompt123"],
    ),
    (
        ("reasoning123 machine123 learning123 model123 token123 prompt123", 10),
        ["reasoning123", "machine123", "learning123", "model123", "token123", "prompt123"],
    ),
    (
        ("reasoning123 machine123 learning123 model123 token123 prompt123", 18),
        ["reasoning123", "machine123", "learning123", "model123 token123", "prompt123"],
    ),
    (
        ("reasoning123 machine123 learning123 model123 token123 prompt123", 28),
        ["reasoning123 machine123", "learning123 model123", "token123 prompt123"],
    ),
    (
        ("machine123 learning123 model123 token123 prompt123 session123", 6),
        ["machine123", "learning123", "model123", "token123", "prompt123", "session123"],
    ),
    (
        ("machine123 learning123 model123 token123 prompt123 session123", 10),
        ["machine123", "learning123", "model123", "token123", "prompt123", "session123"],
    ),
    (
        ("machine123 learning123 model123 token123 prompt123 session123", 18),
        ["machine123", "learning123", "model123 token123", "prompt123", "session123"],
    ),
    (
        ("machine123 learning123 model123 token123 prompt123 session123", 28),
        ["machine123 learning123", "model123 token123 prompt123", "session123"],
    ),
    (
        ("learning123 model123 token123 prompt123 session123 library123", 6),
        ["learning123", "model123", "token123", "prompt123", "session123", "library123"],
    ),
    (
        ("learning123 model123 token123 prompt123 session123 library123", 10),
        ["learning123", "model123", "token123", "prompt123", "session123", "library123"],
    ),
    (
        ("learning123 model123 token123 prompt123 session123 library123", 18),
        ["learning123", "model123 token123", "prompt123", "session123", "library123"],
    ),
    (
        ("learning123 model123 token123 prompt123 session123 library123", 28),
        ["learning123 model123", "token123 prompt123", "session123 library123"],
    ),
    (
        ("model123 token123 prompt123 session123 library123 service123", 6),
        ["model123", "token123", "prompt123", "session123", "library123", "service123"],
    ),
    (
        ("model123 token123 prompt123 session123 library123 service123", 10),
        ["model123", "token123", "prompt123", "session123", "library123", "service123"],
    ),
    (
        ("model123 token123 prompt123 session123 library123 service123", 18),
        ["model123 token123", "prompt123", "session123", "library123", "service123"],
    ),
    (
        ("model123 token123 prompt123 session123 library123 service123", 28),
        ["model123 token123 prompt123", "session123 library123", "service123"],
    ),
    (
        ("token123 prompt123 session123 library123 service123 gateway123", 6),
        ["token123", "prompt123", "session123", "library123", "service123", "gateway123"],
    ),
    (
        ("token123 prompt123 session123 library123 service123 gateway123", 10),
        ["token123", "prompt123", "session123", "library123", "service123", "gateway123"],
    ),
    (
        ("token123 prompt123 session123 library123 service123 gateway123", 18),
        ["token123 prompt123", "session123", "library123", "service123", "gateway123"],
    ),
    (
        ("token123 prompt123 session123 library123 service123 gateway123", 28),
        ["token123 prompt123", "session123 library123", "service123 gateway123"],
    ),
    (
        ("prompt123 session123 library123 service123 gateway123 storage123", 6),
        ["prompt123", "session123", "library123", "service123", "gateway123", "storage123"],
    ),
    (
        ("prompt123 session123 library123 service123 gateway123 storage123", 10),
        ["prompt123", "session123", "library123", "service123", "gateway123", "storage123"],
    ),
    (
        ("prompt123 session123 library123 service123 gateway123 storage123", 18),
        ["prompt123", "session123", "library123", "service123", "gateway123", "storage123"],
    ),
    (
        ("prompt123 session123 library123 service123 gateway123 storage123", 28),
        ["prompt123 session123", "library123 service123", "gateway123 storage123"],
    ),
    (
        ("session123 library123 service123 gateway123 storage123 network123", 6),
        ["session123", "library123", "service123", "gateway123", "storage123", "network123"],
    ),
    (
        ("session123 library123 service123 gateway123 storage123 network123", 10),
        ["session123", "library123", "service123", "gateway123", "storage123", "network123"],
    ),
    (
        ("session123 library123 service123 gateway123 storage123 network123", 18),
        ["session123", "library123", "service123", "gateway123", "storage123", "network123"],
    ),
    (
        ("session123 library123 service123 gateway123 storage123 network123", 28),
        ["session123 library123", "service123 gateway123", "storage123 network123"],
    ),
    (
        ("library123 service123 gateway123 storage123 network123 latency123", 6),
        ["library123", "service123", "gateway123", "storage123", "network123", "latency123"],
    ),
    (
        ("library123 service123 gateway123 storage123 network123 latency123", 10),
        ["library123", "service123", "gateway123", "storage123", "network123", "latency123"],
    ),
    (
        ("library123 service123 gateway123 storage123 network123 latency123", 18),
        ["library123", "service123", "gateway123", "storage123", "network123", "latency123"],
    ),
    (
        ("library123 service123 gateway123 storage123 network123 latency123", 28),
        ["library123 service123", "gateway123 storage123", "network123 latency123"],
    ),
    (
        ("service123 gateway123 storage123 network123 latency123 buffer123", 6),
        ["service123", "gateway123", "storage123", "network123", "latency123", "buffer123"],
    ),
    (
        ("service123 gateway123 storage123 network123 latency123 buffer123", 10),
        ["service123", "gateway123", "storage123", "network123", "latency123", "buffer123"],
    ),
    (
        ("service123 gateway123 storage123 network123 latency123 buffer123", 18),
        ["service123", "gateway123", "storage123", "network123", "latency123", "buffer123"],
    ),
    (
        ("service123 gateway123 storage123 network123 latency123 buffer123", 28),
        ["service123 gateway123", "storage123 network123", "latency123 buffer123"],
    ),
    (
        ("gateway123 storage123 network123 latency123 buffer123 queue123", 6),
        ["gateway123", "storage123", "network123", "latency123", "buffer123", "queue123"],
    ),
    (
        ("gateway123 storage123 network123 latency123 buffer123 queue123", 10),
        ["gateway123", "storage123", "network123", "latency123", "buffer123", "queue123"],
    ),
    (
        ("gateway123 storage123 network123 latency123 buffer123 queue123", 18),
        ["gateway123", "storage123", "network123", "latency123", "buffer123 queue123"],
    ),
    (
        ("gateway123 storage123 network123 latency123 buffer123 queue123", 28),
        ["gateway123 storage123", "network123 latency123", "buffer123 queue123"],
    ),
    (
        ("storage123 network123 latency123 buffer123 queue123 worker123", 6),
        ["storage123", "network123", "latency123", "buffer123", "queue123", "worker123"],
    ),
    (
        ("storage123 network123 latency123 buffer123 queue123 worker123", 10),
        ["storage123", "network123", "latency123", "buffer123", "queue123", "worker123"],
    ),
    (
        ("storage123 network123 latency123 buffer123 queue123 worker123", 18),
        ["storage123", "network123", "latency123", "buffer123 queue123", "worker123"],
    ),
    (
        ("storage123 network123 latency123 buffer123 queue123 worker123", 28),
        ["storage123 network123", "latency123 buffer123", "queue123 worker123"],
    ),
    (
        ("network123 latency123 buffer123 queue123 worker123 kernel123", 6),
        ["network123", "latency123", "buffer123", "queue123", "worker123", "kernel123"],
    ),
    (
        ("network123 latency123 buffer123 queue123 worker123 kernel123", 10),
        ["network123", "latency123", "buffer123", "queue123", "worker123", "kernel123"],
    ),
    (
        ("network123 latency123 buffer123 queue123 worker123 kernel123", 18),
        ["network123", "latency123", "buffer123 queue123", "worker123", "kernel123"],
    ),
    (
        ("network123 latency123 buffer123 queue123 worker123 kernel123", 28),
        ["network123 latency123", "buffer123 queue123 worker123", "kernel123"],
    ),
    (
        ("latency123 buffer123 queue123 worker123 kernel123 signal123", 6),
        ["latency123", "buffer123", "queue123", "worker123", "kernel123", "signal123"],
    ),
    (
        ("latency123 buffer123 queue123 worker123 kernel123 signal123", 10),
        ["latency123", "buffer123", "queue123", "worker123", "kernel123", "signal123"],
    ),
    (
        ("latency123 buffer123 queue123 worker123 kernel123 signal123", 18),
        ["latency123", "buffer123 queue123", "worker123", "kernel123", "signal123"],
    ),
    (
        ("latency123 buffer123 queue123 worker123 kernel123 signal123", 28),
        ["latency123 buffer123", "queue123 worker123 kernel123", "signal123"],
    ),
    (
        ("buffer123 queue123 worker123 kernel123 signal123 packet123", 6),
        ["buffer123", "queue123", "worker123", "kernel123", "signal123", "packet123"],
    ),
    (
        ("buffer123 queue123 worker123 kernel123 signal123 packet123", 10),
        ["buffer123", "queue123", "worker123", "kernel123", "signal123", "packet123"],
    ),
    (
        ("buffer123 queue123 worker123 kernel123 signal123 packet123", 18),
        ["buffer123 queue123", "worker123", "kernel123", "signal123", "packet123"],
    ),
    (
        ("buffer123 queue123 worker123 kernel123 signal123 packet123", 28),
        ["buffer123 queue123 worker123", "kernel123 signal123", "packet123"],
    ),
    (
        ("queue123 worker123 kernel123 signal123 packet123 router123", 6),
        ["queue123", "worker123", "kernel123", "signal123", "packet123", "router123"],
    ),
    (
        ("queue123 worker123 kernel123 signal123 packet123 router123", 10),
        ["queue123", "worker123", "kernel123", "signal123", "packet123", "router123"],
    ),
    (
        ("queue123 worker123 kernel123 signal123 packet123 router123", 18),
        ["queue123 worker123", "kernel123", "signal123", "packet123", "router123"],
    ),
    (
        ("queue123 worker123 kernel123 signal123 packet123 router123", 28),
        ["queue123 worker123 kernel123", "signal123 packet123", "router123"],
    ),
    (
        ("worker123 kernel123 signal123 packet123 router123 cluster123", 6),
        ["worker123", "kernel123", "signal123", "packet123", "router123", "cluster123"],
    ),
    (
        ("worker123 kernel123 signal123 packet123 router123 cluster123", 10),
        ["worker123", "kernel123", "signal123", "packet123", "router123", "cluster123"],
    ),
    (
        ("worker123 kernel123 signal123 packet123 router123 cluster123", 18),
        ["worker123", "kernel123", "signal123", "packet123", "router123", "cluster123"],
    ),
    (
        ("worker123 kernel123 signal123 packet123 router123 cluster123", 28),
        ["worker123 kernel123", "signal123 packet123", "router123 cluster123"],
    ),
    (
        ("kernel123 signal123 packet123 router123 cluster123 mirror123", 6),
        ["kernel123", "signal123", "packet123", "router123", "cluster123", "mirror123"],
    ),
    (
        ("kernel123 signal123 packet123 router123 cluster123 mirror123", 10),
        ["kernel123", "signal123", "packet123", "router123", "cluster123", "mirror123"],
    ),
    (
        ("kernel123 signal123 packet123 router123 cluster123 mirror123", 18),
        ["kernel123", "signal123", "packet123", "router123", "cluster123", "mirror123"],
    ),
    (
        ("kernel123 signal123 packet123 router123 cluster123 mirror123", 28),
        ["kernel123 signal123", "packet123 router123", "cluster123 mirror123"],
    ),
    (
        ("signal123 packet123 router123 cluster123 mirror123 filter123", 6),
        ["signal123", "packet123", "router123", "cluster123", "mirror123", "filter123"],
    ),
    (
        ("signal123 packet123 router123 cluster123 mirror123 filter123", 10),
        ["signal123", "packet123", "router123", "cluster123", "mirror123", "filter123"],
    ),
    (
        ("signal123 packet123 router123 cluster123 mirror123 filter123", 18),
        ["signal123", "packet123", "router123", "cluster123", "mirror123", "filter123"],
    ),
    (
        ("signal123 packet123 router123 cluster123 mirror123 filter123", 28),
        ["signal123 packet123", "router123 cluster123", "mirror123 filter123"],
    ),
    (
        ("packet123 router123 cluster123 mirror123 filter123 ranking123", 6),
        ["packet123", "router123", "cluster123", "mirror123", "filter123", "ranking123"],
    ),
    (
        ("packet123 router123 cluster123 mirror123 filter123 ranking123", 10),
        ["packet123", "router123", "cluster123", "mirror123", "filter123", "ranking123"],
    ),
    (
        ("packet123 router123 cluster123 mirror123 filter123 ranking123", 18),
        ["packet123", "router123", "cluster123", "mirror123", "filter123", "ranking123"],
    ),
    (
        ("packet123 router123 cluster123 mirror123 filter123 ranking123", 28),
        ["packet123 router123", "cluster123 mirror123", "filter123 ranking123"],
    ),
    (
        ("router123 cluster123 mirror123 filter123 ranking123 encoding123", 6),
        ["router123", "cluster123", "mirror123", "filter123", "ranking123", "encoding123"],
    ),
    (
        ("router123 cluster123 mirror123 filter123 ranking123 encoding123", 10),
        ["router123", "cluster123", "mirror123", "filter123", "ranking123", "encoding123"],
    ),
    (
        ("router123 cluster123 mirror123 filter123 ranking123 encoding123", 18),
        ["router123", "cluster123", "mirror123", "filter123", "ranking123", "encoding123"],
    ),
    (
        ("router123 cluster123 mirror123 filter123 ranking123 encoding123", 28),
        ["router123 cluster123", "mirror123 filter123", "ranking123 encoding123"],
    ),
    (
        ("cluster123 mirror123 filter123 ranking123 encoding123 mapping123", 6),
        ["cluster123", "mirror123", "filter123", "ranking123", "encoding123", "mapping123"],
    ),
    (
        ("cluster123 mirror123 filter123 ranking123 encoding123 mapping123", 10),
        ["cluster123", "mirror123", "filter123", "ranking123", "encoding123", "mapping123"],
    ),
    (
        ("cluster123 mirror123 filter123 ranking123 encoding123 mapping123", 18),
        ["cluster123", "mirror123", "filter123", "ranking123", "encoding123", "mapping123"],
    ),
    (
        ("cluster123 mirror123 filter123 ranking123 encoding123 mapping123", 28),
        ["cluster123 mirror123", "filter123 ranking123", "encoding123 mapping123"],
    ),
    (
        ("mirror123 filter123 ranking123 encoding123 mapping123 record123", 6),
        ["mirror123", "filter123", "ranking123", "encoding123", "mapping123", "record123"],
    ),
    (
        ("mirror123 filter123 ranking123 encoding123 mapping123 record123", 10),
        ["mirror123", "filter123", "ranking123", "encoding123", "mapping123", "record123"],
    ),
    (
        ("mirror123 filter123 ranking123 encoding123 mapping123 record123", 18),
        ["mirror123", "filter123", "ranking123", "encoding123", "mapping123", "record123"],
    ),
    (
        ("mirror123 filter123 ranking123 encoding123 mapping123 record123", 28),
        ["mirror123 filter123", "ranking123 encoding123", "mapping123 record123"],
    ),
    (
        ("filter123 ranking123 encoding123 mapping123 record123 candle123", 6),
        ["filter123", "ranking123", "encoding123", "mapping123", "record123", "candle123"],
    ),
    (
        ("filter123 ranking123 encoding123 mapping123 record123 candle123", 10),
        ["filter123", "ranking123", "encoding123", "mapping123", "record123", "candle123"],
    ),
    (
        ("filter123 ranking123 encoding123 mapping123 record123 candle123", 18),
        ["filter123", "ranking123", "encoding123", "mapping123", "record123", "candle123"],
    ),
    (
        ("filter123 ranking123 encoding123 mapping123 record123 candle123", 28),
        ["filter123 ranking123", "encoding123 mapping123", "record123 candle123"],
    ),
    (
        ("ranking123 encoding123 mapping123 record123 candle123 thread123", 6),
        ["ranking123", "encoding123", "mapping123", "record123", "candle123", "thread123"],
    ),
    (
        ("ranking123 encoding123 mapping123 record123 candle123 thread123", 10),
        ["ranking123", "encoding123", "mapping123", "record123", "candle123", "thread123"],
    ),
    (
        ("ranking123 encoding123 mapping123 record123 candle123 thread123", 18),
        ["ranking123", "encoding123", "mapping123", "record123", "candle123", "thread123"],
    ),
    (
        ("ranking123 encoding123 mapping123 record123 candle123 thread123", 28),
        ["ranking123 encoding123", "mapping123 record123", "candle123 thread123"],
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
