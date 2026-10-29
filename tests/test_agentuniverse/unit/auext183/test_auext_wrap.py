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
        ("round 183: the quick brown fox jumps over the lazy dog", 4),
        ["round", "183:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 183: the quick brown fox jumps over the lazy dog", 8),
        ["round", "183: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 183: the quick brown fox jumps over the lazy dog", 12),
        ["round 183:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 183: the quick brown fox jumps over the lazy dog", 16),
        ["round 183: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 183: the quick brown fox jumps over the lazy dog", 24),
        ["round 183: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 183: the quick brown fox jumps over the lazy dog", 32),
        ["round 183: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 183: agentuniverse is a framework for multi agents", 4),
        ["round", "183:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 183: agentuniverse is a framework for multi agents", 8),
        ["round", "183:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 183: agentuniverse is a framework for multi agents", 12),
        ["round 183:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 183: agentuniverse is a framework for multi agents", 16),
        ["round 183:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 183: agentuniverse is a framework for multi agents", 24),
        ["round 183: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 183: agentuniverse is a framework for multi agents", 32),
        ["round 183: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 183: knowledge stored as vectors enables retrieval", 4),
        ["round", "183:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 183: knowledge stored as vectors enables retrieval", 8),
        ["round", "183:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 183: knowledge stored as vectors enables retrieval", 12),
        ["round 183:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 183: knowledge stored as vectors enables retrieval", 16),
        ["round 183:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 183: knowledge stored as vectors enables retrieval", 24),
        ["round 183: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 183: knowledge stored as vectors enables retrieval", 32),
        ["round 183: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 183: the processor reads the record then stops", 4),
        ["round", "183:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 183: the processor reads the record then stops", 8),
        ["round", "183: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 183: the processor reads the record then stops", 12),
        ["round 183:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 183: the processor reads the record then stops", 16),
        ["round 183: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 183: the processor reads the record then stops", 24),
        ["round 183: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 183: the processor reads the record then stops", 32),
        ["round 183: the processor reads", "the record then stops"],
    ),
    (
        ("round 183: a worker pulls the next task from the queue", 4),
        ["round", "183:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 183: a worker pulls the next task from the queue", 8),
        ["round", "183: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 183: a worker pulls the next task from the queue", 12),
        ["round 183: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 183: a worker pulls the next task from the queue", 16),
        ["round 183: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 183: a worker pulls the next task from the queue", 24),
        ["round 183: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 183: a worker pulls the next task from the queue", 32),
        ["round 183: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 183: signals travel through the network layer", 4),
        ["round", "183:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 183: signals travel through the network layer", 8),
        ["round", "183:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 183: signals travel through the network layer", 12),
        ["round 183:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 183: signals travel through the network layer", 16),
        ["round 183:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 183: signals travel through the network layer", 24),
        ["round 183: signals", "travel through the", "network layer"],
    ),
    (
        ("round 183: signals travel through the network layer", 32),
        ["round 183: signals travel", "through the network layer"],
    ),
    (
        ("round 183: the gateway routes each request by policy", 4),
        ["round", "183:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 183: the gateway routes each request by policy", 8),
        ["round", "183: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 183: the gateway routes each request by policy", 12),
        ["round 183:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 183: the gateway routes each request by policy", 16),
        ["round 183: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 183: the gateway routes each request by policy", 24),
        ["round 183: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 183: the gateway routes each request by policy", 32),
        ["round 183: the gateway routes", "each request by policy"],
    ),
    (
        ("round 183: memory grows until the buffer is full", 4),
        ["round", "183:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 183: memory grows until the buffer is full", 8),
        ["round", "183:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 183: memory grows until the buffer is full", 12),
        ["round 183:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 183: memory grows until the buffer is full", 16),
        ["round 183:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 183: memory grows until the buffer is full", 24), ["round 183: memory grows", "until the buffer is full"]),
    (("round 183: memory grows until the buffer is full", 32), ["round 183: memory grows until", "the buffer is full"]),
    (
        ("round 183: the cluster mirrors every packet twice", 4),
        ["round", "183:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 183: the cluster mirrors every packet twice", 8),
        ["round", "183: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 183: the cluster mirrors every packet twice", 12),
        ["round 183:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 183: the cluster mirrors every packet twice", 16),
        ["round 183: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 183: the cluster mirrors every packet twice", 24),
        ["round 183: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 183: the cluster mirrors every packet twice", 32),
        ["round 183: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 183: ranking uses tokens learned from the corpus", 4),
        ["round", "183:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 183: ranking uses tokens learned from the corpus", 8),
        ["round", "183:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 183: ranking uses tokens learned from the corpus", 12),
        ["round 183:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 183: ranking uses tokens learned from the corpus", 16),
        ["round 183:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 183: ranking uses tokens learned from the corpus", 24),
        ["round 183: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 183: ranking uses tokens learned from the corpus", 32),
        ["round 183: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 183: a long session ends when the candle dies", 4),
        ["round", "183:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 183: a long session ends when the candle dies", 8),
        ["round", "183: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 183: a long session ends when the candle dies", 12),
        ["round 183: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 183: a long session ends when the candle dies", 16),
        ["round 183: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 183: a long session ends when the candle dies", 24),
        ["round 183: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 183: a long session ends when the candle dies", 32),
        ["round 183: a long session ends", "when the candle dies"],
    ),
    (
        ("round 183: encode the prompt then map the result", 4),
        ["round", "183:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 183: encode the prompt then map the result", 8),
        ["round", "183:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 183: encode the prompt then map the result", 12),
        ["round 183:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 183: encode the prompt then map the result", 16),
        ["round 183:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 183: encode the prompt then map the result", 24),
        ["round 183: encode the", "prompt then map the", "result"],
    ),
    (("round 183: encode the prompt then map the result", 32), ["round 183: encode the prompt", "then map the result"]),
    (
        ("round 183: the kernel wakes the worker at dawn", 4),
        ["round", "183:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 183: the kernel wakes the worker at dawn", 8),
        ["round", "183: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 183: the kernel wakes the worker at dawn", 12),
        ["round 183:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 183: the kernel wakes the worker at dawn", 16), ["round 183: the", "kernel wakes the", "worker at dawn"]),
    (("round 183: the kernel wakes the worker at dawn", 24), ["round 183: the kernel", "wakes the worker at dawn"]),
    (("round 183: the kernel wakes the worker at dawn", 32), ["round 183: the kernel wakes the", "worker at dawn"]),
    (
        ("round 183: service latency drops after the patch", 4),
        ["round", "183:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 183: service latency drops after the patch", 8),
        ["round", "183:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 183: service latency drops after the patch", 12),
        ["round 183:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 183: service latency drops after the patch", 16),
        ["round 183:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 183: service latency drops after the patch", 24),
        ["round 183: service", "latency drops after the", "patch"],
    ),
    (("round 183: service latency drops after the patch", 32), ["round 183: service latency drops", "after the patch"]),
    (
        ("round 183: the library caches every vector it sees", 4),
        ["round", "183:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 183: the library caches every vector it sees", 8),
        ["round", "183: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 183: the library caches every vector it sees", 12),
        ["round 183:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 183: the library caches every vector it sees", 16),
        ["round 183: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 183: the library caches every vector it sees", 24),
        ["round 183: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 183: the library caches every vector it sees", 32),
        ["round 183: the library caches", "every vector it sees"],
    ),
    (
        ("round 183: agents argue then the debate resolves", 4),
        ["round", "183:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 183: agents argue then the debate resolves", 8),
        ["round", "183:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 183: agents argue then the debate resolves", 12),
        ["round 183:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 183: agents argue then the debate resolves", 16),
        ["round 183:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 183: agents argue then the debate resolves", 24), ["round 183: agents argue", "then the debate resolves"]),
    (("round 183: agents argue then the debate resolves", 32), ["round 183: agents argue then the", "debate resolves"]),
    (
        ("round 183: the filter keeps only strong matches", 4),
        ["round", "183:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 183: the filter keeps only strong matches", 8),
        ["round", "183: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 183: the filter keeps only strong matches", 12),
        ["round 183:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 183: the filter keeps only strong matches", 16),
        ["round 183: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 183: the filter keeps only strong matches", 24),
        ["round 183: the filter", "keeps only strong", "matches"],
    ),
    (("round 183: the filter keeps only strong matches", 32), ["round 183: the filter keeps only", "strong matches"]),
    (
        ("round 183: the model answers with a short reply", 4),
        ["round", "183:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 183: the model answers with a short reply", 8),
        ["round", "183: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 183: the model answers with a short reply", 12),
        ["round 183:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 183: the model answers with a short reply", 16),
        ["round 183: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 183: the model answers with a short reply", 24),
        ["round 183: the model", "answers with a short", "reply"],
    ),
    (("round 183: the model answers with a short reply", 32), ["round 183: the model answers", "with a short reply"]),
    (
        ("round 183: the recorder stores the reasoning trace", 4),
        ["round", "183:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 183: the recorder stores the reasoning trace", 8),
        ["round", "183: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 183: the recorder stores the reasoning trace", 12),
        ["round 183:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 183: the recorder stores the reasoning trace", 16),
        ["round 183: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 183: the recorder stores the reasoning trace", 24),
        ["round 183: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 183: the recorder stores the reasoning trace", 32),
        ["round 183: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 183: the angel watches the processor run", 4),
        ["round", "183:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 183: the angel watches the processor run", 8),
        ["round", "183: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 183: the angel watches the processor run", 12),
        ["round 183:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 183: the angel watches the processor run", 16),
        ["round 183: the", "angel watches", "the processor", "run"],
    ),
    (("round 183: the angel watches the processor run", 24), ["round 183: the angel", "watches the processor", "run"]),
    (("round 183: the angel watches the processor run", 32), ["round 183: the angel watches the", "processor run"]),
    (
        ("round 183: angle of the vector decides the match", 4),
        ["round", "183:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 183: angle of the vector decides the match", 8),
        ["round", "183:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 183: angle of the vector decides the match", 12),
        ["round 183:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 183: angle of the vector decides the match", 16),
        ["round 183: angle", "of the vector", "decides the", "match"],
    ),
    (("round 183: angle of the vector decides the match", 24), ["round 183: angle of the", "vector decides the match"]),
    (("round 183: angle of the vector decides the match", 32), ["round 183: angle of the vector", "decides the match"]),
    (
        ("round 183: the candle burns twice as long at night", 4),
        ["round", "183:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 183: the candle burns twice as long at night", 8),
        ["round", "183: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 183: the candle burns twice as long at night", 12),
        ["round 183:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 183: the candle burns twice as long at night", 16),
        ["round 183: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 183: the candle burns twice as long at night", 24),
        ["round 183: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 183: the candle burns twice as long at night", 32),
        ["round 183: the candle burns", "twice as long at night"],
    ),
    (
        ("round 183: a mirror of the universe in one line", 4),
        ["round", "183:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 183: a mirror of the universe in one line", 8),
        ["round", "183: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 183: a mirror of the universe in one line", 12),
        ["round 183: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 183: a mirror of the universe in one line", 16),
        ["round 183: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 183: a mirror of the universe in one line", 24), ["round 183: a mirror of", "the universe in one line"]),
    (("round 183: a mirror of the universe in one line", 32), ["round 183: a mirror of the", "universe in one line"]),
    (
        ("round 183: the queue drains before the storm", 4),
        ["round", "183:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 183: the queue drains before the storm", 8),
        ["round", "183: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 183: the queue drains before the storm", 12),
        ["round 183:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 183: the queue drains before the storm", 16), ["round 183: the", "queue drains", "before the storm"]),
    (("round 183: the queue drains before the storm", 24), ["round 183: the queue", "drains before the storm"]),
    (("round 183: the queue drains before the storm", 32), ["round 183: the queue drains", "before the storm"]),
    (
        ("kitten183 sitting183 agent183 angle183 universe183 memory183", 6),
        ["kitten183", "sitting183", "agent183", "angle183", "universe183", "memory183"],
    ),
    (
        ("kitten183 sitting183 agent183 angle183 universe183 memory183", 10),
        ["kitten183", "sitting183", "agent183", "angle183", "universe183", "memory183"],
    ),
    (
        ("kitten183 sitting183 agent183 angle183 universe183 memory183", 18),
        ["kitten183", "sitting183", "agent183 angle183", "universe183", "memory183"],
    ),
    (
        ("kitten183 sitting183 agent183 angle183 universe183 memory183", 28),
        ["kitten183 sitting183", "agent183 angle183", "universe183 memory183"],
    ),
    (
        ("sitting183 agent183 angle183 universe183 memory183 stream183", 6),
        ["sitting183", "agent183", "angle183", "universe183", "memory183", "stream183"],
    ),
    (
        ("sitting183 agent183 angle183 universe183 memory183 stream183", 10),
        ["sitting183", "agent183", "angle183", "universe183", "memory183", "stream183"],
    ),
    (
        ("sitting183 agent183 angle183 universe183 memory183 stream183", 18),
        ["sitting183", "agent183 angle183", "universe183", "memory183", "stream183"],
    ),
    (
        ("sitting183 agent183 angle183 universe183 memory183 stream183", 28),
        ["sitting183 agent183 angle183", "universe183 memory183", "stream183"],
    ),
    (
        ("agent183 angle183 universe183 memory183 stream183 context183", 6),
        ["agent183", "angle183", "universe183", "memory183", "stream183", "context183"],
    ),
    (
        ("agent183 angle183 universe183 memory183 stream183 context183", 10),
        ["agent183", "angle183", "universe183", "memory183", "stream183", "context183"],
    ),
    (
        ("agent183 angle183 universe183 memory183 stream183 context183", 18),
        ["agent183 angle183", "universe183", "memory183", "stream183", "context183"],
    ),
    (
        ("agent183 angle183 universe183 memory183 stream183 context183", 28),
        ["agent183 angle183", "universe183 memory183", "stream183 context183"],
    ),
    (
        ("angle183 universe183 memory183 stream183 context183 knowledge183", 6),
        ["angle183", "universe183", "memory183", "stream183", "context183", "knowledge183"],
    ),
    (
        ("angle183 universe183 memory183 stream183 context183 knowledge183", 10),
        ["angle183", "universe183", "memory183", "stream183", "context183", "knowledge183"],
    ),
    (
        ("angle183 universe183 memory183 stream183 context183 knowledge183", 18),
        ["angle183", "universe183", "memory183", "stream183", "context183", "knowledge183"],
    ),
    (
        ("angle183 universe183 memory183 stream183 context183 knowledge183", 28),
        ["angle183 universe183", "memory183 stream183", "context183 knowledge183"],
    ),
    (
        ("universe183 memory183 stream183 context183 knowledge183 vector183", 6),
        ["universe183", "memory183", "stream183", "context183", "knowledge183", "vector183"],
    ),
    (
        ("universe183 memory183 stream183 context183 knowledge183 vector183", 10),
        ["universe183", "memory183", "stream183", "context183", "knowledge183", "vector183"],
    ),
    (
        ("universe183 memory183 stream183 context183 knowledge183 vector183", 18),
        ["universe183", "memory183", "stream183", "context183", "knowledge183", "vector183"],
    ),
    (
        ("universe183 memory183 stream183 context183 knowledge183 vector183", 28),
        ["universe183 memory183", "stream183 context183", "knowledge183 vector183"],
    ),
    (
        ("memory183 stream183 context183 knowledge183 vector183 processor183", 6),
        ["memory183", "stream183", "context183", "knowledge183", "vector183", "processor183"],
    ),
    (
        ("memory183 stream183 context183 knowledge183 vector183 processor183", 10),
        ["memory183", "stream183", "context183", "knowledge183", "vector183", "processor183"],
    ),
    (
        ("memory183 stream183 context183 knowledge183 vector183 processor183", 18),
        ["memory183", "stream183", "context183", "knowledge183", "vector183", "processor183"],
    ),
    (
        ("memory183 stream183 context183 knowledge183 vector183 processor183", 28),
        ["memory183 stream183", "context183 knowledge183", "vector183 processor183"],
    ),
    (
        ("stream183 context183 knowledge183 vector183 processor183 reasoning183", 6),
        ["stream183", "context183", "knowledge183", "vector183", "processor183", "reasoning183"],
    ),
    (
        ("stream183 context183 knowledge183 vector183 processor183 reasoning183", 10),
        ["stream183", "context183", "knowledge183", "vector183", "processor183", "reasoning183"],
    ),
    (
        ("stream183 context183 knowledge183 vector183 processor183 reasoning183", 18),
        ["stream183", "context183", "knowledge183", "vector183", "processor183", "reasoning183"],
    ),
    (
        ("stream183 context183 knowledge183 vector183 processor183 reasoning183", 28),
        ["stream183 context183", "knowledge183 vector183", "processor183 reasoning183"],
    ),
    (
        ("context183 knowledge183 vector183 processor183 reasoning183 machine183", 6),
        ["context183", "knowledge183", "vector183", "processor183", "reasoning183", "machine183"],
    ),
    (
        ("context183 knowledge183 vector183 processor183 reasoning183 machine183", 10),
        ["context183", "knowledge183", "vector183", "processor183", "reasoning183", "machine183"],
    ),
    (
        ("context183 knowledge183 vector183 processor183 reasoning183 machine183", 18),
        ["context183", "knowledge183", "vector183", "processor183", "reasoning183", "machine183"],
    ),
    (
        ("context183 knowledge183 vector183 processor183 reasoning183 machine183", 28),
        ["context183 knowledge183", "vector183 processor183", "reasoning183 machine183"],
    ),
    (
        ("knowledge183 vector183 processor183 reasoning183 machine183 learning183", 6),
        ["knowledge183", "vector183", "processor183", "reasoning183", "machine183", "learning183"],
    ),
    (
        ("knowledge183 vector183 processor183 reasoning183 machine183 learning183", 10),
        ["knowledge183", "vector183", "processor183", "reasoning183", "machine183", "learning183"],
    ),
    (
        ("knowledge183 vector183 processor183 reasoning183 machine183 learning183", 18),
        ["knowledge183", "vector183", "processor183", "reasoning183", "machine183", "learning183"],
    ),
    (
        ("knowledge183 vector183 processor183 reasoning183 machine183 learning183", 28),
        ["knowledge183 vector183", "processor183 reasoning183", "machine183 learning183"],
    ),
    (
        ("vector183 processor183 reasoning183 machine183 learning183 model183", 6),
        ["vector183", "processor183", "reasoning183", "machine183", "learning183", "model183"],
    ),
    (
        ("vector183 processor183 reasoning183 machine183 learning183 model183", 10),
        ["vector183", "processor183", "reasoning183", "machine183", "learning183", "model183"],
    ),
    (
        ("vector183 processor183 reasoning183 machine183 learning183 model183", 18),
        ["vector183", "processor183", "reasoning183", "machine183", "learning183", "model183"],
    ),
    (
        ("vector183 processor183 reasoning183 machine183 learning183 model183", 28),
        ["vector183 processor183", "reasoning183 machine183", "learning183 model183"],
    ),
    (
        ("processor183 reasoning183 machine183 learning183 model183 token183", 6),
        ["processor183", "reasoning183", "machine183", "learning183", "model183", "token183"],
    ),
    (
        ("processor183 reasoning183 machine183 learning183 model183 token183", 10),
        ["processor183", "reasoning183", "machine183", "learning183", "model183", "token183"],
    ),
    (
        ("processor183 reasoning183 machine183 learning183 model183 token183", 18),
        ["processor183", "reasoning183", "machine183", "learning183", "model183 token183"],
    ),
    (
        ("processor183 reasoning183 machine183 learning183 model183 token183", 28),
        ["processor183 reasoning183", "machine183 learning183", "model183 token183"],
    ),
    (
        ("reasoning183 machine183 learning183 model183 token183 prompt183", 6),
        ["reasoning183", "machine183", "learning183", "model183", "token183", "prompt183"],
    ),
    (
        ("reasoning183 machine183 learning183 model183 token183 prompt183", 10),
        ["reasoning183", "machine183", "learning183", "model183", "token183", "prompt183"],
    ),
    (
        ("reasoning183 machine183 learning183 model183 token183 prompt183", 18),
        ["reasoning183", "machine183", "learning183", "model183 token183", "prompt183"],
    ),
    (
        ("reasoning183 machine183 learning183 model183 token183 prompt183", 28),
        ["reasoning183 machine183", "learning183 model183", "token183 prompt183"],
    ),
    (
        ("machine183 learning183 model183 token183 prompt183 session183", 6),
        ["machine183", "learning183", "model183", "token183", "prompt183", "session183"],
    ),
    (
        ("machine183 learning183 model183 token183 prompt183 session183", 10),
        ["machine183", "learning183", "model183", "token183", "prompt183", "session183"],
    ),
    (
        ("machine183 learning183 model183 token183 prompt183 session183", 18),
        ["machine183", "learning183", "model183 token183", "prompt183", "session183"],
    ),
    (
        ("machine183 learning183 model183 token183 prompt183 session183", 28),
        ["machine183 learning183", "model183 token183 prompt183", "session183"],
    ),
    (
        ("learning183 model183 token183 prompt183 session183 library183", 6),
        ["learning183", "model183", "token183", "prompt183", "session183", "library183"],
    ),
    (
        ("learning183 model183 token183 prompt183 session183 library183", 10),
        ["learning183", "model183", "token183", "prompt183", "session183", "library183"],
    ),
    (
        ("learning183 model183 token183 prompt183 session183 library183", 18),
        ["learning183", "model183 token183", "prompt183", "session183", "library183"],
    ),
    (
        ("learning183 model183 token183 prompt183 session183 library183", 28),
        ["learning183 model183", "token183 prompt183", "session183 library183"],
    ),
    (
        ("model183 token183 prompt183 session183 library183 service183", 6),
        ["model183", "token183", "prompt183", "session183", "library183", "service183"],
    ),
    (
        ("model183 token183 prompt183 session183 library183 service183", 10),
        ["model183", "token183", "prompt183", "session183", "library183", "service183"],
    ),
    (
        ("model183 token183 prompt183 session183 library183 service183", 18),
        ["model183 token183", "prompt183", "session183", "library183", "service183"],
    ),
    (
        ("model183 token183 prompt183 session183 library183 service183", 28),
        ["model183 token183 prompt183", "session183 library183", "service183"],
    ),
    (
        ("token183 prompt183 session183 library183 service183 gateway183", 6),
        ["token183", "prompt183", "session183", "library183", "service183", "gateway183"],
    ),
    (
        ("token183 prompt183 session183 library183 service183 gateway183", 10),
        ["token183", "prompt183", "session183", "library183", "service183", "gateway183"],
    ),
    (
        ("token183 prompt183 session183 library183 service183 gateway183", 18),
        ["token183 prompt183", "session183", "library183", "service183", "gateway183"],
    ),
    (
        ("token183 prompt183 session183 library183 service183 gateway183", 28),
        ["token183 prompt183", "session183 library183", "service183 gateway183"],
    ),
    (
        ("prompt183 session183 library183 service183 gateway183 storage183", 6),
        ["prompt183", "session183", "library183", "service183", "gateway183", "storage183"],
    ),
    (
        ("prompt183 session183 library183 service183 gateway183 storage183", 10),
        ["prompt183", "session183", "library183", "service183", "gateway183", "storage183"],
    ),
    (
        ("prompt183 session183 library183 service183 gateway183 storage183", 18),
        ["prompt183", "session183", "library183", "service183", "gateway183", "storage183"],
    ),
    (
        ("prompt183 session183 library183 service183 gateway183 storage183", 28),
        ["prompt183 session183", "library183 service183", "gateway183 storage183"],
    ),
    (
        ("session183 library183 service183 gateway183 storage183 network183", 6),
        ["session183", "library183", "service183", "gateway183", "storage183", "network183"],
    ),
    (
        ("session183 library183 service183 gateway183 storage183 network183", 10),
        ["session183", "library183", "service183", "gateway183", "storage183", "network183"],
    ),
    (
        ("session183 library183 service183 gateway183 storage183 network183", 18),
        ["session183", "library183", "service183", "gateway183", "storage183", "network183"],
    ),
    (
        ("session183 library183 service183 gateway183 storage183 network183", 28),
        ["session183 library183", "service183 gateway183", "storage183 network183"],
    ),
    (
        ("library183 service183 gateway183 storage183 network183 latency183", 6),
        ["library183", "service183", "gateway183", "storage183", "network183", "latency183"],
    ),
    (
        ("library183 service183 gateway183 storage183 network183 latency183", 10),
        ["library183", "service183", "gateway183", "storage183", "network183", "latency183"],
    ),
    (
        ("library183 service183 gateway183 storage183 network183 latency183", 18),
        ["library183", "service183", "gateway183", "storage183", "network183", "latency183"],
    ),
    (
        ("library183 service183 gateway183 storage183 network183 latency183", 28),
        ["library183 service183", "gateway183 storage183", "network183 latency183"],
    ),
    (
        ("service183 gateway183 storage183 network183 latency183 buffer183", 6),
        ["service183", "gateway183", "storage183", "network183", "latency183", "buffer183"],
    ),
    (
        ("service183 gateway183 storage183 network183 latency183 buffer183", 10),
        ["service183", "gateway183", "storage183", "network183", "latency183", "buffer183"],
    ),
    (
        ("service183 gateway183 storage183 network183 latency183 buffer183", 18),
        ["service183", "gateway183", "storage183", "network183", "latency183", "buffer183"],
    ),
    (
        ("service183 gateway183 storage183 network183 latency183 buffer183", 28),
        ["service183 gateway183", "storage183 network183", "latency183 buffer183"],
    ),
    (
        ("gateway183 storage183 network183 latency183 buffer183 queue183", 6),
        ["gateway183", "storage183", "network183", "latency183", "buffer183", "queue183"],
    ),
    (
        ("gateway183 storage183 network183 latency183 buffer183 queue183", 10),
        ["gateway183", "storage183", "network183", "latency183", "buffer183", "queue183"],
    ),
    (
        ("gateway183 storage183 network183 latency183 buffer183 queue183", 18),
        ["gateway183", "storage183", "network183", "latency183", "buffer183 queue183"],
    ),
    (
        ("gateway183 storage183 network183 latency183 buffer183 queue183", 28),
        ["gateway183 storage183", "network183 latency183", "buffer183 queue183"],
    ),
    (
        ("storage183 network183 latency183 buffer183 queue183 worker183", 6),
        ["storage183", "network183", "latency183", "buffer183", "queue183", "worker183"],
    ),
    (
        ("storage183 network183 latency183 buffer183 queue183 worker183", 10),
        ["storage183", "network183", "latency183", "buffer183", "queue183", "worker183"],
    ),
    (
        ("storage183 network183 latency183 buffer183 queue183 worker183", 18),
        ["storage183", "network183", "latency183", "buffer183 queue183", "worker183"],
    ),
    (
        ("storage183 network183 latency183 buffer183 queue183 worker183", 28),
        ["storage183 network183", "latency183 buffer183", "queue183 worker183"],
    ),
    (
        ("network183 latency183 buffer183 queue183 worker183 kernel183", 6),
        ["network183", "latency183", "buffer183", "queue183", "worker183", "kernel183"],
    ),
    (
        ("network183 latency183 buffer183 queue183 worker183 kernel183", 10),
        ["network183", "latency183", "buffer183", "queue183", "worker183", "kernel183"],
    ),
    (
        ("network183 latency183 buffer183 queue183 worker183 kernel183", 18),
        ["network183", "latency183", "buffer183 queue183", "worker183", "kernel183"],
    ),
    (
        ("network183 latency183 buffer183 queue183 worker183 kernel183", 28),
        ["network183 latency183", "buffer183 queue183 worker183", "kernel183"],
    ),
    (
        ("latency183 buffer183 queue183 worker183 kernel183 signal183", 6),
        ["latency183", "buffer183", "queue183", "worker183", "kernel183", "signal183"],
    ),
    (
        ("latency183 buffer183 queue183 worker183 kernel183 signal183", 10),
        ["latency183", "buffer183", "queue183", "worker183", "kernel183", "signal183"],
    ),
    (
        ("latency183 buffer183 queue183 worker183 kernel183 signal183", 18),
        ["latency183", "buffer183 queue183", "worker183", "kernel183", "signal183"],
    ),
    (
        ("latency183 buffer183 queue183 worker183 kernel183 signal183", 28),
        ["latency183 buffer183", "queue183 worker183 kernel183", "signal183"],
    ),
    (
        ("buffer183 queue183 worker183 kernel183 signal183 packet183", 6),
        ["buffer183", "queue183", "worker183", "kernel183", "signal183", "packet183"],
    ),
    (
        ("buffer183 queue183 worker183 kernel183 signal183 packet183", 10),
        ["buffer183", "queue183", "worker183", "kernel183", "signal183", "packet183"],
    ),
    (
        ("buffer183 queue183 worker183 kernel183 signal183 packet183", 18),
        ["buffer183 queue183", "worker183", "kernel183", "signal183", "packet183"],
    ),
    (
        ("buffer183 queue183 worker183 kernel183 signal183 packet183", 28),
        ["buffer183 queue183 worker183", "kernel183 signal183", "packet183"],
    ),
    (
        ("queue183 worker183 kernel183 signal183 packet183 router183", 6),
        ["queue183", "worker183", "kernel183", "signal183", "packet183", "router183"],
    ),
    (
        ("queue183 worker183 kernel183 signal183 packet183 router183", 10),
        ["queue183", "worker183", "kernel183", "signal183", "packet183", "router183"],
    ),
    (
        ("queue183 worker183 kernel183 signal183 packet183 router183", 18),
        ["queue183 worker183", "kernel183", "signal183", "packet183", "router183"],
    ),
    (
        ("queue183 worker183 kernel183 signal183 packet183 router183", 28),
        ["queue183 worker183 kernel183", "signal183 packet183", "router183"],
    ),
    (
        ("worker183 kernel183 signal183 packet183 router183 cluster183", 6),
        ["worker183", "kernel183", "signal183", "packet183", "router183", "cluster183"],
    ),
    (
        ("worker183 kernel183 signal183 packet183 router183 cluster183", 10),
        ["worker183", "kernel183", "signal183", "packet183", "router183", "cluster183"],
    ),
    (
        ("worker183 kernel183 signal183 packet183 router183 cluster183", 18),
        ["worker183", "kernel183", "signal183", "packet183", "router183", "cluster183"],
    ),
    (
        ("worker183 kernel183 signal183 packet183 router183 cluster183", 28),
        ["worker183 kernel183", "signal183 packet183", "router183 cluster183"],
    ),
    (
        ("kernel183 signal183 packet183 router183 cluster183 mirror183", 6),
        ["kernel183", "signal183", "packet183", "router183", "cluster183", "mirror183"],
    ),
    (
        ("kernel183 signal183 packet183 router183 cluster183 mirror183", 10),
        ["kernel183", "signal183", "packet183", "router183", "cluster183", "mirror183"],
    ),
    (
        ("kernel183 signal183 packet183 router183 cluster183 mirror183", 18),
        ["kernel183", "signal183", "packet183", "router183", "cluster183", "mirror183"],
    ),
    (
        ("kernel183 signal183 packet183 router183 cluster183 mirror183", 28),
        ["kernel183 signal183", "packet183 router183", "cluster183 mirror183"],
    ),
    (
        ("signal183 packet183 router183 cluster183 mirror183 filter183", 6),
        ["signal183", "packet183", "router183", "cluster183", "mirror183", "filter183"],
    ),
    (
        ("signal183 packet183 router183 cluster183 mirror183 filter183", 10),
        ["signal183", "packet183", "router183", "cluster183", "mirror183", "filter183"],
    ),
    (
        ("signal183 packet183 router183 cluster183 mirror183 filter183", 18),
        ["signal183", "packet183", "router183", "cluster183", "mirror183", "filter183"],
    ),
    (
        ("signal183 packet183 router183 cluster183 mirror183 filter183", 28),
        ["signal183 packet183", "router183 cluster183", "mirror183 filter183"],
    ),
    (
        ("packet183 router183 cluster183 mirror183 filter183 ranking183", 6),
        ["packet183", "router183", "cluster183", "mirror183", "filter183", "ranking183"],
    ),
    (
        ("packet183 router183 cluster183 mirror183 filter183 ranking183", 10),
        ["packet183", "router183", "cluster183", "mirror183", "filter183", "ranking183"],
    ),
    (
        ("packet183 router183 cluster183 mirror183 filter183 ranking183", 18),
        ["packet183", "router183", "cluster183", "mirror183", "filter183", "ranking183"],
    ),
    (
        ("packet183 router183 cluster183 mirror183 filter183 ranking183", 28),
        ["packet183 router183", "cluster183 mirror183", "filter183 ranking183"],
    ),
    (
        ("router183 cluster183 mirror183 filter183 ranking183 encoding183", 6),
        ["router183", "cluster183", "mirror183", "filter183", "ranking183", "encoding183"],
    ),
    (
        ("router183 cluster183 mirror183 filter183 ranking183 encoding183", 10),
        ["router183", "cluster183", "mirror183", "filter183", "ranking183", "encoding183"],
    ),
    (
        ("router183 cluster183 mirror183 filter183 ranking183 encoding183", 18),
        ["router183", "cluster183", "mirror183", "filter183", "ranking183", "encoding183"],
    ),
    (
        ("router183 cluster183 mirror183 filter183 ranking183 encoding183", 28),
        ["router183 cluster183", "mirror183 filter183", "ranking183 encoding183"],
    ),
    (
        ("cluster183 mirror183 filter183 ranking183 encoding183 mapping183", 6),
        ["cluster183", "mirror183", "filter183", "ranking183", "encoding183", "mapping183"],
    ),
    (
        ("cluster183 mirror183 filter183 ranking183 encoding183 mapping183", 10),
        ["cluster183", "mirror183", "filter183", "ranking183", "encoding183", "mapping183"],
    ),
    (
        ("cluster183 mirror183 filter183 ranking183 encoding183 mapping183", 18),
        ["cluster183", "mirror183", "filter183", "ranking183", "encoding183", "mapping183"],
    ),
    (
        ("cluster183 mirror183 filter183 ranking183 encoding183 mapping183", 28),
        ["cluster183 mirror183", "filter183 ranking183", "encoding183 mapping183"],
    ),
    (
        ("mirror183 filter183 ranking183 encoding183 mapping183 record183", 6),
        ["mirror183", "filter183", "ranking183", "encoding183", "mapping183", "record183"],
    ),
    (
        ("mirror183 filter183 ranking183 encoding183 mapping183 record183", 10),
        ["mirror183", "filter183", "ranking183", "encoding183", "mapping183", "record183"],
    ),
    (
        ("mirror183 filter183 ranking183 encoding183 mapping183 record183", 18),
        ["mirror183", "filter183", "ranking183", "encoding183", "mapping183", "record183"],
    ),
    (
        ("mirror183 filter183 ranking183 encoding183 mapping183 record183", 28),
        ["mirror183 filter183", "ranking183 encoding183", "mapping183 record183"],
    ),
    (
        ("filter183 ranking183 encoding183 mapping183 record183 candle183", 6),
        ["filter183", "ranking183", "encoding183", "mapping183", "record183", "candle183"],
    ),
    (
        ("filter183 ranking183 encoding183 mapping183 record183 candle183", 10),
        ["filter183", "ranking183", "encoding183", "mapping183", "record183", "candle183"],
    ),
    (
        ("filter183 ranking183 encoding183 mapping183 record183 candle183", 18),
        ["filter183", "ranking183", "encoding183", "mapping183", "record183", "candle183"],
    ),
    (
        ("filter183 ranking183 encoding183 mapping183 record183 candle183", 28),
        ["filter183 ranking183", "encoding183 mapping183", "record183 candle183"],
    ),
    (
        ("ranking183 encoding183 mapping183 record183 candle183 thread183", 6),
        ["ranking183", "encoding183", "mapping183", "record183", "candle183", "thread183"],
    ),
    (
        ("ranking183 encoding183 mapping183 record183 candle183 thread183", 10),
        ["ranking183", "encoding183", "mapping183", "record183", "candle183", "thread183"],
    ),
    (
        ("ranking183 encoding183 mapping183 record183 candle183 thread183", 18),
        ["ranking183", "encoding183", "mapping183", "record183", "candle183", "thread183"],
    ),
    (
        ("ranking183 encoding183 mapping183 record183 candle183 thread183", 28),
        ["ranking183 encoding183", "mapping183 record183", "candle183 thread183"],
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
