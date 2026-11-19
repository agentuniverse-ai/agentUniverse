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
        ("round 98: the quick brown fox jumps over the lazy dog", 4),
        ["round", "98:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 98: the quick brown fox jumps over the lazy dog", 8),
        ["round", "98: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 98: the quick brown fox jumps over the lazy dog", 12),
        ["round 98:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 98: the quick brown fox jumps over the lazy dog", 16),
        ["round 98: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 98: the quick brown fox jumps over the lazy dog", 24),
        ["round 98: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 98: the quick brown fox jumps over the lazy dog", 32),
        ["round 98: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 98: agentuniverse is a framework for multi agents", 4),
        ["round", "98:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 98: agentuniverse is a framework for multi agents", 8),
        ["round", "98:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 98: agentuniverse is a framework for multi agents", 12),
        ["round 98:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 98: agentuniverse is a framework for multi agents", 16),
        ["round 98:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 98: agentuniverse is a framework for multi agents", 24),
        ["round 98: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 98: agentuniverse is a framework for multi agents", 32),
        ["round 98: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 98: knowledge stored as vectors enables retrieval", 4),
        ["round", "98:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 98: knowledge stored as vectors enables retrieval", 8),
        ["round", "98:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 98: knowledge stored as vectors enables retrieval", 12),
        ["round 98:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 98: knowledge stored as vectors enables retrieval", 16),
        ["round 98:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 98: knowledge stored as vectors enables retrieval", 24),
        ["round 98: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 98: knowledge stored as vectors enables retrieval", 32),
        ["round 98: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 98: the processor reads the record then stops", 4),
        ["round", "98:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 98: the processor reads the record then stops", 8),
        ["round", "98: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 98: the processor reads the record then stops", 12),
        ["round 98:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 98: the processor reads the record then stops", 16),
        ["round 98: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 98: the processor reads the record then stops", 24),
        ["round 98: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 98: the processor reads the record then stops", 32),
        ["round 98: the processor reads", "the record then stops"],
    ),
    (
        ("round 98: a worker pulls the next task from the queue", 4),
        ["round", "98:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 98: a worker pulls the next task from the queue", 8),
        ["round", "98: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 98: a worker pulls the next task from the queue", 12),
        ["round 98: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 98: a worker pulls the next task from the queue", 16),
        ["round 98: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 98: a worker pulls the next task from the queue", 24),
        ["round 98: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 98: a worker pulls the next task from the queue", 32),
        ["round 98: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 98: signals travel through the network layer", 4),
        ["round", "98:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 98: signals travel through the network layer", 8),
        ["round", "98:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 98: signals travel through the network layer", 12),
        ["round 98:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 98: signals travel through the network layer", 16),
        ["round 98:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 98: signals travel through the network layer", 24),
        ["round 98: signals travel", "through the network", "layer"],
    ),
    (
        ("round 98: signals travel through the network layer", 32),
        ["round 98: signals travel through", "the network layer"],
    ),
    (
        ("round 98: the gateway routes each request by policy", 4),
        ["round", "98:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 98: the gateway routes each request by policy", 8),
        ["round", "98: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 98: the gateway routes each request by policy", 12),
        ["round 98:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 98: the gateway routes each request by policy", 16),
        ["round 98: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 98: the gateway routes each request by policy", 24),
        ["round 98: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 98: the gateway routes each request by policy", 32),
        ["round 98: the gateway routes", "each request by policy"],
    ),
    (
        ("round 98: memory grows until the buffer is full", 4),
        ["round", "98:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 98: memory grows until the buffer is full", 8),
        ["round", "98:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 98: memory grows until the buffer is full", 12),
        ["round 98:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 98: memory grows until the buffer is full", 16),
        ["round 98: memory", "grows until the", "buffer is full"],
    ),
    (("round 98: memory grows until the buffer is full", 24), ["round 98: memory grows", "until the buffer is full"]),
    (("round 98: memory grows until the buffer is full", 32), ["round 98: memory grows until the", "buffer is full"]),
    (
        ("round 98: the cluster mirrors every packet twice", 4),
        ["round", "98:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 98: the cluster mirrors every packet twice", 8),
        ["round", "98: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 98: the cluster mirrors every packet twice", 12),
        ["round 98:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 98: the cluster mirrors every packet twice", 16),
        ["round 98: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 98: the cluster mirrors every packet twice", 24),
        ["round 98: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 98: the cluster mirrors every packet twice", 32), ["round 98: the cluster mirrors", "every packet twice"]),
    (
        ("round 98: ranking uses tokens learned from the corpus", 4),
        ["round", "98:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 98: ranking uses tokens learned from the corpus", 8),
        ["round", "98:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 98: ranking uses tokens learned from the corpus", 12),
        ["round 98:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 98: ranking uses tokens learned from the corpus", 16),
        ["round 98:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 98: ranking uses tokens learned from the corpus", 24),
        ["round 98: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 98: ranking uses tokens learned from the corpus", 32),
        ["round 98: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 98: a long session ends when the candle dies", 4),
        ["round", "98:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 98: a long session ends when the candle dies", 8),
        ["round", "98: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 98: a long session ends when the candle dies", 12),
        ["round 98: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 98: a long session ends when the candle dies", 16),
        ["round 98: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 98: a long session ends when the candle dies", 24),
        ["round 98: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 98: a long session ends when the candle dies", 32),
        ["round 98: a long session ends", "when the candle dies"],
    ),
    (
        ("round 98: encode the prompt then map the result", 4),
        ["round", "98:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 98: encode the prompt then map the result", 8),
        ["round", "98:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 98: encode the prompt then map the result", 12),
        ["round 98:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 98: encode the prompt then map the result", 16),
        ["round 98: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 98: encode the prompt then map the result", 24),
        ["round 98: encode the", "prompt then map the", "result"],
    ),
    (("round 98: encode the prompt then map the result", 32), ["round 98: encode the prompt then", "map the result"]),
    (
        ("round 98: the kernel wakes the worker at dawn", 4),
        ["round", "98:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 98: the kernel wakes the worker at dawn", 8),
        ["round", "98: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 98: the kernel wakes the worker at dawn", 12),
        ["round 98:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 98: the kernel wakes the worker at dawn", 16), ["round 98: the", "kernel wakes the", "worker at dawn"]),
    (("round 98: the kernel wakes the worker at dawn", 24), ["round 98: the kernel", "wakes the worker at dawn"]),
    (("round 98: the kernel wakes the worker at dawn", 32), ["round 98: the kernel wakes the", "worker at dawn"]),
    (
        ("round 98: service latency drops after the patch", 4),
        ["round", "98:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 98: service latency drops after the patch", 8),
        ["round", "98:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 98: service latency drops after the patch", 12),
        ["round 98:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 98: service latency drops after the patch", 16),
        ["round 98:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 98: service latency drops after the patch", 24),
        ["round 98: service", "latency drops after the", "patch"],
    ),
    (("round 98: service latency drops after the patch", 32), ["round 98: service latency drops", "after the patch"]),
    (
        ("round 98: the library caches every vector it sees", 4),
        ["round", "98:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 98: the library caches every vector it sees", 8),
        ["round", "98: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 98: the library caches every vector it sees", 12),
        ["round 98:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 98: the library caches every vector it sees", 16),
        ["round 98: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 98: the library caches every vector it sees", 24),
        ["round 98: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 98: the library caches every vector it sees", 32),
        ["round 98: the library caches", "every vector it sees"],
    ),
    (
        ("round 98: agents argue then the debate resolves", 4),
        ["round", "98:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 98: agents argue then the debate resolves", 8),
        ["round", "98:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 98: agents argue then the debate resolves", 12),
        ["round 98:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 98: agents argue then the debate resolves", 16),
        ["round 98: agents", "argue then the", "debate resolves"],
    ),
    (("round 98: agents argue then the debate resolves", 24), ["round 98: agents argue", "then the debate resolves"]),
    (("round 98: agents argue then the debate resolves", 32), ["round 98: agents argue then the", "debate resolves"]),
    (
        ("round 98: the filter keeps only strong matches", 4),
        ["round", "98:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 98: the filter keeps only strong matches", 8),
        ["round", "98: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 98: the filter keeps only strong matches", 12),
        ["round 98:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 98: the filter keeps only strong matches", 16),
        ["round 98: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 98: the filter keeps only strong matches", 24), ["round 98: the filter", "keeps only strong", "matches"]),
    (("round 98: the filter keeps only strong matches", 32), ["round 98: the filter keeps only", "strong matches"]),
    (
        ("round 98: the model answers with a short reply", 4),
        ["round", "98:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 98: the model answers with a short reply", 8),
        ["round", "98: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 98: the model answers with a short reply", 12),
        ["round 98:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 98: the model answers with a short reply", 16),
        ["round 98: the", "model answers", "with a short", "reply"],
    ),
    (("round 98: the model answers with a short reply", 24), ["round 98: the model", "answers with a short", "reply"]),
    (("round 98: the model answers with a short reply", 32), ["round 98: the model answers with", "a short reply"]),
    (
        ("round 98: the recorder stores the reasoning trace", 4),
        ["round", "98:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 98: the recorder stores the reasoning trace", 8),
        ["round", "98: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 98: the recorder stores the reasoning trace", 12),
        ["round 98:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 98: the recorder stores the reasoning trace", 16),
        ["round 98: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 98: the recorder stores the reasoning trace", 24),
        ["round 98: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 98: the recorder stores the reasoning trace", 32),
        ["round 98: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 98: the angel watches the processor run", 4),
        ["round", "98:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 98: the angel watches the processor run", 8),
        ["round", "98: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 98: the angel watches the processor run", 12),
        ["round 98:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 98: the angel watches the processor run", 16), ["round 98: the", "angel watches", "the processor", "run"]),
    (("round 98: the angel watches the processor run", 24), ["round 98: the angel", "watches the processor", "run"]),
    (("round 98: the angel watches the processor run", 32), ["round 98: the angel watches the", "processor run"]),
    (
        ("round 98: angle of the vector decides the match", 4),
        ["round", "98:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 98: angle of the vector decides the match", 8),
        ["round", "98:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 98: angle of the vector decides the match", 12),
        ["round 98:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 98: angle of the vector decides the match", 16),
        ["round 98: angle", "of the vector", "decides the", "match"],
    ),
    (("round 98: angle of the vector decides the match", 24), ["round 98: angle of the", "vector decides the match"]),
    (("round 98: angle of the vector decides the match", 32), ["round 98: angle of the vector", "decides the match"]),
    (
        ("round 98: the candle burns twice as long at night", 4),
        ["round", "98:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 98: the candle burns twice as long at night", 8),
        ["round", "98: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 98: the candle burns twice as long at night", 12),
        ["round 98:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 98: the candle burns twice as long at night", 16),
        ["round 98: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 98: the candle burns twice as long at night", 24),
        ["round 98: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 98: the candle burns twice as long at night", 32),
        ["round 98: the candle burns twice", "as long at night"],
    ),
    (
        ("round 98: a mirror of the universe in one line", 4),
        ["round", "98:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 98: a mirror of the universe in one line", 8),
        ["round", "98: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 98: a mirror of the universe in one line", 12),
        ["round 98: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 98: a mirror of the universe in one line", 16),
        ["round 98: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 98: a mirror of the universe in one line", 24), ["round 98: a mirror of", "the universe in one line"]),
    (("round 98: a mirror of the universe in one line", 32), ["round 98: a mirror of the", "universe in one line"]),
    (
        ("round 98: the queue drains before the storm", 4),
        ["round", "98:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 98: the queue drains before the storm", 8),
        ["round", "98: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 98: the queue drains before the storm", 12), ["round 98:", "the queue", "drains", "before the", "storm"]),
    (("round 98: the queue drains before the storm", 16), ["round 98: the", "queue drains", "before the storm"]),
    (("round 98: the queue drains before the storm", 24), ["round 98: the queue", "drains before the storm"]),
    (("round 98: the queue drains before the storm", 32), ["round 98: the queue drains", "before the storm"]),
    (
        ("kitten98 sitting98 agent98 angle98 universe98 memory98", 6),
        ["kitten98", "sitting98", "agent98", "angle98", "universe98", "memory98"],
    ),
    (
        ("kitten98 sitting98 agent98 angle98 universe98 memory98", 10),
        ["kitten98", "sitting98", "agent98", "angle98", "universe98", "memory98"],
    ),
    (
        ("kitten98 sitting98 agent98 angle98 universe98 memory98", 18),
        ["kitten98 sitting98", "agent98 angle98", "universe98", "memory98"],
    ),
    (
        ("kitten98 sitting98 agent98 angle98 universe98 memory98", 28),
        ["kitten98 sitting98 agent98", "angle98 universe98 memory98"],
    ),
    (
        ("sitting98 agent98 angle98 universe98 memory98 stream98", 6),
        ["sitting98", "agent98", "angle98", "universe98", "memory98", "stream98"],
    ),
    (
        ("sitting98 agent98 angle98 universe98 memory98 stream98", 10),
        ["sitting98", "agent98", "angle98", "universe98", "memory98", "stream98"],
    ),
    (
        ("sitting98 agent98 angle98 universe98 memory98 stream98", 18),
        ["sitting98 agent98", "angle98 universe98", "memory98 stream98"],
    ),
    (
        ("sitting98 agent98 angle98 universe98 memory98 stream98", 28),
        ["sitting98 agent98 angle98", "universe98 memory98 stream98"],
    ),
    (
        ("agent98 angle98 universe98 memory98 stream98 context98", 6),
        ["agent98", "angle98", "universe98", "memory98", "stream98", "context98"],
    ),
    (
        ("agent98 angle98 universe98 memory98 stream98 context98", 10),
        ["agent98", "angle98", "universe98", "memory98", "stream98", "context98"],
    ),
    (
        ("agent98 angle98 universe98 memory98 stream98 context98", 18),
        ["agent98 angle98", "universe98", "memory98 stream98", "context98"],
    ),
    (
        ("agent98 angle98 universe98 memory98 stream98 context98", 28),
        ["agent98 angle98 universe98", "memory98 stream98 context98"],
    ),
    (
        ("angle98 universe98 memory98 stream98 context98 knowledge98", 6),
        ["angle98", "universe98", "memory98", "stream98", "context98", "knowledge98"],
    ),
    (
        ("angle98 universe98 memory98 stream98 context98 knowledge98", 10),
        ["angle98", "universe98", "memory98", "stream98", "context98", "knowledge98"],
    ),
    (
        ("angle98 universe98 memory98 stream98 context98 knowledge98", 18),
        ["angle98 universe98", "memory98 stream98", "context98", "knowledge98"],
    ),
    (
        ("angle98 universe98 memory98 stream98 context98 knowledge98", 28),
        ["angle98 universe98 memory98", "stream98 context98", "knowledge98"],
    ),
    (
        ("universe98 memory98 stream98 context98 knowledge98 vector98", 6),
        ["universe98", "memory98", "stream98", "context98", "knowledge98", "vector98"],
    ),
    (
        ("universe98 memory98 stream98 context98 knowledge98 vector98", 10),
        ["universe98", "memory98", "stream98", "context98", "knowledge98", "vector98"],
    ),
    (
        ("universe98 memory98 stream98 context98 knowledge98 vector98", 18),
        ["universe98", "memory98 stream98", "context98", "knowledge98", "vector98"],
    ),
    (
        ("universe98 memory98 stream98 context98 knowledge98 vector98", 28),
        ["universe98 memory98 stream98", "context98 knowledge98", "vector98"],
    ),
    (
        ("memory98 stream98 context98 knowledge98 vector98 processor98", 6),
        ["memory98", "stream98", "context98", "knowledge98", "vector98", "processor98"],
    ),
    (
        ("memory98 stream98 context98 knowledge98 vector98 processor98", 10),
        ["memory98", "stream98", "context98", "knowledge98", "vector98", "processor98"],
    ),
    (
        ("memory98 stream98 context98 knowledge98 vector98 processor98", 18),
        ["memory98 stream98", "context98", "knowledge98", "vector98", "processor98"],
    ),
    (
        ("memory98 stream98 context98 knowledge98 vector98 processor98", 28),
        ["memory98 stream98 context98", "knowledge98 vector98", "processor98"],
    ),
    (
        ("stream98 context98 knowledge98 vector98 processor98 reasoning98", 6),
        ["stream98", "context98", "knowledge98", "vector98", "processor98", "reasoning98"],
    ),
    (
        ("stream98 context98 knowledge98 vector98 processor98 reasoning98", 10),
        ["stream98", "context98", "knowledge98", "vector98", "processor98", "reasoning98"],
    ),
    (
        ("stream98 context98 knowledge98 vector98 processor98 reasoning98", 18),
        ["stream98 context98", "knowledge98", "vector98", "processor98", "reasoning98"],
    ),
    (
        ("stream98 context98 knowledge98 vector98 processor98 reasoning98", 28),
        ["stream98 context98", "knowledge98 vector98", "processor98 reasoning98"],
    ),
    (
        ("context98 knowledge98 vector98 processor98 reasoning98 machine98", 6),
        ["context98", "knowledge98", "vector98", "processor98", "reasoning98", "machine98"],
    ),
    (
        ("context98 knowledge98 vector98 processor98 reasoning98 machine98", 10),
        ["context98", "knowledge98", "vector98", "processor98", "reasoning98", "machine98"],
    ),
    (
        ("context98 knowledge98 vector98 processor98 reasoning98 machine98", 18),
        ["context98", "knowledge98", "vector98", "processor98", "reasoning98", "machine98"],
    ),
    (
        ("context98 knowledge98 vector98 processor98 reasoning98 machine98", 28),
        ["context98 knowledge98", "vector98 processor98", "reasoning98 machine98"],
    ),
    (
        ("knowledge98 vector98 processor98 reasoning98 machine98 learning98", 6),
        ["knowledge98", "vector98", "processor98", "reasoning98", "machine98", "learning98"],
    ),
    (
        ("knowledge98 vector98 processor98 reasoning98 machine98 learning98", 10),
        ["knowledge98", "vector98", "processor98", "reasoning98", "machine98", "learning98"],
    ),
    (
        ("knowledge98 vector98 processor98 reasoning98 machine98 learning98", 18),
        ["knowledge98", "vector98", "processor98", "reasoning98", "machine98", "learning98"],
    ),
    (
        ("knowledge98 vector98 processor98 reasoning98 machine98 learning98", 28),
        ["knowledge98 vector98", "processor98 reasoning98", "machine98 learning98"],
    ),
    (
        ("vector98 processor98 reasoning98 machine98 learning98 model98", 6),
        ["vector98", "processor98", "reasoning98", "machine98", "learning98", "model98"],
    ),
    (
        ("vector98 processor98 reasoning98 machine98 learning98 model98", 10),
        ["vector98", "processor98", "reasoning98", "machine98", "learning98", "model98"],
    ),
    (
        ("vector98 processor98 reasoning98 machine98 learning98 model98", 18),
        ["vector98", "processor98", "reasoning98", "machine98", "learning98 model98"],
    ),
    (
        ("vector98 processor98 reasoning98 machine98 learning98 model98", 28),
        ["vector98 processor98", "reasoning98 machine98", "learning98 model98"],
    ),
    (
        ("processor98 reasoning98 machine98 learning98 model98 token98", 6),
        ["processor98", "reasoning98", "machine98", "learning98", "model98", "token98"],
    ),
    (
        ("processor98 reasoning98 machine98 learning98 model98 token98", 10),
        ["processor98", "reasoning98", "machine98", "learning98", "model98", "token98"],
    ),
    (
        ("processor98 reasoning98 machine98 learning98 model98 token98", 18),
        ["processor98", "reasoning98", "machine98", "learning98 model98", "token98"],
    ),
    (
        ("processor98 reasoning98 machine98 learning98 model98 token98", 28),
        ["processor98 reasoning98", "machine98 learning98 model98", "token98"],
    ),
    (
        ("reasoning98 machine98 learning98 model98 token98 prompt98", 6),
        ["reasoning98", "machine98", "learning98", "model98", "token98", "prompt98"],
    ),
    (
        ("reasoning98 machine98 learning98 model98 token98 prompt98", 10),
        ["reasoning98", "machine98", "learning98", "model98", "token98", "prompt98"],
    ),
    (
        ("reasoning98 machine98 learning98 model98 token98 prompt98", 18),
        ["reasoning98", "machine98", "learning98 model98", "token98 prompt98"],
    ),
    (
        ("reasoning98 machine98 learning98 model98 token98 prompt98", 28),
        ["reasoning98 machine98", "learning98 model98 token98", "prompt98"],
    ),
    (
        ("machine98 learning98 model98 token98 prompt98 session98", 6),
        ["machine98", "learning98", "model98", "token98", "prompt98", "session98"],
    ),
    (
        ("machine98 learning98 model98 token98 prompt98 session98", 10),
        ["machine98", "learning98", "model98", "token98", "prompt98", "session98"],
    ),
    (
        ("machine98 learning98 model98 token98 prompt98 session98", 18),
        ["machine98", "learning98 model98", "token98 prompt98", "session98"],
    ),
    (
        ("machine98 learning98 model98 token98 prompt98 session98", 28),
        ["machine98 learning98 model98", "token98 prompt98 session98"],
    ),
    (
        ("learning98 model98 token98 prompt98 session98 library98", 6),
        ["learning98", "model98", "token98", "prompt98", "session98", "library98"],
    ),
    (
        ("learning98 model98 token98 prompt98 session98 library98", 10),
        ["learning98", "model98", "token98", "prompt98", "session98", "library98"],
    ),
    (
        ("learning98 model98 token98 prompt98 session98 library98", 18),
        ["learning98 model98", "token98 prompt98", "session98", "library98"],
    ),
    (
        ("learning98 model98 token98 prompt98 session98 library98", 28),
        ["learning98 model98 token98", "prompt98 session98 library98"],
    ),
    (
        ("model98 token98 prompt98 session98 library98 service98", 6),
        ["model98", "token98", "prompt98", "session98", "library98", "service98"],
    ),
    (
        ("model98 token98 prompt98 session98 library98 service98", 10),
        ["model98", "token98", "prompt98", "session98", "library98", "service98"],
    ),
    (
        ("model98 token98 prompt98 session98 library98 service98", 18),
        ["model98 token98", "prompt98 session98", "library98", "service98"],
    ),
    (
        ("model98 token98 prompt98 session98 library98 service98", 28),
        ["model98 token98 prompt98", "session98 library98", "service98"],
    ),
    (
        ("token98 prompt98 session98 library98 service98 gateway98", 6),
        ["token98", "prompt98", "session98", "library98", "service98", "gateway98"],
    ),
    (
        ("token98 prompt98 session98 library98 service98 gateway98", 10),
        ["token98", "prompt98", "session98", "library98", "service98", "gateway98"],
    ),
    (
        ("token98 prompt98 session98 library98 service98 gateway98", 18),
        ["token98 prompt98", "session98", "library98", "service98", "gateway98"],
    ),
    (
        ("token98 prompt98 session98 library98 service98 gateway98", 28),
        ["token98 prompt98 session98", "library98 service98", "gateway98"],
    ),
    (
        ("prompt98 session98 library98 service98 gateway98 storage98", 6),
        ["prompt98", "session98", "library98", "service98", "gateway98", "storage98"],
    ),
    (
        ("prompt98 session98 library98 service98 gateway98 storage98", 10),
        ["prompt98", "session98", "library98", "service98", "gateway98", "storage98"],
    ),
    (
        ("prompt98 session98 library98 service98 gateway98 storage98", 18),
        ["prompt98 session98", "library98", "service98", "gateway98", "storage98"],
    ),
    (
        ("prompt98 session98 library98 service98 gateway98 storage98", 28),
        ["prompt98 session98 library98", "service98 gateway98", "storage98"],
    ),
    (
        ("session98 library98 service98 gateway98 storage98 network98", 6),
        ["session98", "library98", "service98", "gateway98", "storage98", "network98"],
    ),
    (
        ("session98 library98 service98 gateway98 storage98 network98", 10),
        ["session98", "library98", "service98", "gateway98", "storage98", "network98"],
    ),
    (
        ("session98 library98 service98 gateway98 storage98 network98", 18),
        ["session98", "library98", "service98", "gateway98", "storage98", "network98"],
    ),
    (
        ("session98 library98 service98 gateway98 storage98 network98", 28),
        ["session98 library98", "service98 gateway98", "storage98 network98"],
    ),
    (
        ("library98 service98 gateway98 storage98 network98 latency98", 6),
        ["library98", "service98", "gateway98", "storage98", "network98", "latency98"],
    ),
    (
        ("library98 service98 gateway98 storage98 network98 latency98", 10),
        ["library98", "service98", "gateway98", "storage98", "network98", "latency98"],
    ),
    (
        ("library98 service98 gateway98 storage98 network98 latency98", 18),
        ["library98", "service98", "gateway98", "storage98", "network98", "latency98"],
    ),
    (
        ("library98 service98 gateway98 storage98 network98 latency98", 28),
        ["library98 service98", "gateway98 storage98", "network98 latency98"],
    ),
    (
        ("service98 gateway98 storage98 network98 latency98 buffer98", 6),
        ["service98", "gateway98", "storage98", "network98", "latency98", "buffer98"],
    ),
    (
        ("service98 gateway98 storage98 network98 latency98 buffer98", 10),
        ["service98", "gateway98", "storage98", "network98", "latency98", "buffer98"],
    ),
    (
        ("service98 gateway98 storage98 network98 latency98 buffer98", 18),
        ["service98", "gateway98", "storage98", "network98", "latency98 buffer98"],
    ),
    (
        ("service98 gateway98 storage98 network98 latency98 buffer98", 28),
        ["service98 gateway98", "storage98 network98", "latency98 buffer98"],
    ),
    (
        ("gateway98 storage98 network98 latency98 buffer98 queue98", 6),
        ["gateway98", "storage98", "network98", "latency98", "buffer98", "queue98"],
    ),
    (
        ("gateway98 storage98 network98 latency98 buffer98 queue98", 10),
        ["gateway98", "storage98", "network98", "latency98", "buffer98", "queue98"],
    ),
    (
        ("gateway98 storage98 network98 latency98 buffer98 queue98", 18),
        ["gateway98", "storage98", "network98", "latency98 buffer98", "queue98"],
    ),
    (
        ("gateway98 storage98 network98 latency98 buffer98 queue98", 28),
        ["gateway98 storage98", "network98 latency98 buffer98", "queue98"],
    ),
    (
        ("storage98 network98 latency98 buffer98 queue98 worker98", 6),
        ["storage98", "network98", "latency98", "buffer98", "queue98", "worker98"],
    ),
    (
        ("storage98 network98 latency98 buffer98 queue98 worker98", 10),
        ["storage98", "network98", "latency98", "buffer98", "queue98", "worker98"],
    ),
    (
        ("storage98 network98 latency98 buffer98 queue98 worker98", 18),
        ["storage98", "network98", "latency98 buffer98", "queue98 worker98"],
    ),
    (
        ("storage98 network98 latency98 buffer98 queue98 worker98", 28),
        ["storage98 network98", "latency98 buffer98 queue98", "worker98"],
    ),
    (
        ("network98 latency98 buffer98 queue98 worker98 kernel98", 6),
        ["network98", "latency98", "buffer98", "queue98", "worker98", "kernel98"],
    ),
    (
        ("network98 latency98 buffer98 queue98 worker98 kernel98", 10),
        ["network98", "latency98", "buffer98", "queue98", "worker98", "kernel98"],
    ),
    (
        ("network98 latency98 buffer98 queue98 worker98 kernel98", 18),
        ["network98", "latency98 buffer98", "queue98 worker98", "kernel98"],
    ),
    (
        ("network98 latency98 buffer98 queue98 worker98 kernel98", 28),
        ["network98 latency98 buffer98", "queue98 worker98 kernel98"],
    ),
    (
        ("latency98 buffer98 queue98 worker98 kernel98 signal98", 6),
        ["latency98", "buffer98", "queue98", "worker98", "kernel98", "signal98"],
    ),
    (
        ("latency98 buffer98 queue98 worker98 kernel98 signal98", 10),
        ["latency98", "buffer98", "queue98", "worker98", "kernel98", "signal98"],
    ),
    (
        ("latency98 buffer98 queue98 worker98 kernel98 signal98", 18),
        ["latency98 buffer98", "queue98 worker98", "kernel98 signal98"],
    ),
    (
        ("latency98 buffer98 queue98 worker98 kernel98 signal98", 28),
        ["latency98 buffer98 queue98", "worker98 kernel98 signal98"],
    ),
    (
        ("buffer98 queue98 worker98 kernel98 signal98 packet98", 6),
        ["buffer98", "queue98", "worker98", "kernel98", "signal98", "packet98"],
    ),
    (
        ("buffer98 queue98 worker98 kernel98 signal98 packet98", 10),
        ["buffer98", "queue98", "worker98", "kernel98", "signal98", "packet98"],
    ),
    (
        ("buffer98 queue98 worker98 kernel98 signal98 packet98", 18),
        ["buffer98 queue98", "worker98 kernel98", "signal98 packet98"],
    ),
    (
        ("buffer98 queue98 worker98 kernel98 signal98 packet98", 28),
        ["buffer98 queue98 worker98", "kernel98 signal98 packet98"],
    ),
    (
        ("queue98 worker98 kernel98 signal98 packet98 router98", 6),
        ["queue98", "worker98", "kernel98", "signal98", "packet98", "router98"],
    ),
    (
        ("queue98 worker98 kernel98 signal98 packet98 router98", 10),
        ["queue98", "worker98", "kernel98", "signal98", "packet98", "router98"],
    ),
    (
        ("queue98 worker98 kernel98 signal98 packet98 router98", 18),
        ["queue98 worker98", "kernel98 signal98", "packet98 router98"],
    ),
    (
        ("queue98 worker98 kernel98 signal98 packet98 router98", 28),
        ["queue98 worker98 kernel98", "signal98 packet98 router98"],
    ),
    (
        ("worker98 kernel98 signal98 packet98 router98 cluster98", 6),
        ["worker98", "kernel98", "signal98", "packet98", "router98", "cluster98"],
    ),
    (
        ("worker98 kernel98 signal98 packet98 router98 cluster98", 10),
        ["worker98", "kernel98", "signal98", "packet98", "router98", "cluster98"],
    ),
    (
        ("worker98 kernel98 signal98 packet98 router98 cluster98", 18),
        ["worker98 kernel98", "signal98 packet98", "router98 cluster98"],
    ),
    (
        ("worker98 kernel98 signal98 packet98 router98 cluster98", 28),
        ["worker98 kernel98 signal98", "packet98 router98 cluster98"],
    ),
    (
        ("kernel98 signal98 packet98 router98 cluster98 mirror98", 6),
        ["kernel98", "signal98", "packet98", "router98", "cluster98", "mirror98"],
    ),
    (
        ("kernel98 signal98 packet98 router98 cluster98 mirror98", 10),
        ["kernel98", "signal98", "packet98", "router98", "cluster98", "mirror98"],
    ),
    (
        ("kernel98 signal98 packet98 router98 cluster98 mirror98", 18),
        ["kernel98 signal98", "packet98 router98", "cluster98 mirror98"],
    ),
    (
        ("kernel98 signal98 packet98 router98 cluster98 mirror98", 28),
        ["kernel98 signal98 packet98", "router98 cluster98 mirror98"],
    ),
    (
        ("signal98 packet98 router98 cluster98 mirror98 filter98", 6),
        ["signal98", "packet98", "router98", "cluster98", "mirror98", "filter98"],
    ),
    (
        ("signal98 packet98 router98 cluster98 mirror98 filter98", 10),
        ["signal98", "packet98", "router98", "cluster98", "mirror98", "filter98"],
    ),
    (
        ("signal98 packet98 router98 cluster98 mirror98 filter98", 18),
        ["signal98 packet98", "router98 cluster98", "mirror98 filter98"],
    ),
    (
        ("signal98 packet98 router98 cluster98 mirror98 filter98", 28),
        ["signal98 packet98 router98", "cluster98 mirror98 filter98"],
    ),
    (
        ("packet98 router98 cluster98 mirror98 filter98 ranking98", 6),
        ["packet98", "router98", "cluster98", "mirror98", "filter98", "ranking98"],
    ),
    (
        ("packet98 router98 cluster98 mirror98 filter98 ranking98", 10),
        ["packet98", "router98", "cluster98", "mirror98", "filter98", "ranking98"],
    ),
    (
        ("packet98 router98 cluster98 mirror98 filter98 ranking98", 18),
        ["packet98 router98", "cluster98 mirror98", "filter98 ranking98"],
    ),
    (
        ("packet98 router98 cluster98 mirror98 filter98 ranking98", 28),
        ["packet98 router98 cluster98", "mirror98 filter98 ranking98"],
    ),
    (
        ("router98 cluster98 mirror98 filter98 ranking98 encoding98", 6),
        ["router98", "cluster98", "mirror98", "filter98", "ranking98", "encoding98"],
    ),
    (
        ("router98 cluster98 mirror98 filter98 ranking98 encoding98", 10),
        ["router98", "cluster98", "mirror98", "filter98", "ranking98", "encoding98"],
    ),
    (
        ("router98 cluster98 mirror98 filter98 ranking98 encoding98", 18),
        ["router98 cluster98", "mirror98 filter98", "ranking98", "encoding98"],
    ),
    (
        ("router98 cluster98 mirror98 filter98 ranking98 encoding98", 28),
        ["router98 cluster98 mirror98", "filter98 ranking98", "encoding98"],
    ),
    (
        ("cluster98 mirror98 filter98 ranking98 encoding98 mapping98", 6),
        ["cluster98", "mirror98", "filter98", "ranking98", "encoding98", "mapping98"],
    ),
    (
        ("cluster98 mirror98 filter98 ranking98 encoding98 mapping98", 10),
        ["cluster98", "mirror98", "filter98", "ranking98", "encoding98", "mapping98"],
    ),
    (
        ("cluster98 mirror98 filter98 ranking98 encoding98 mapping98", 18),
        ["cluster98 mirror98", "filter98 ranking98", "encoding98", "mapping98"],
    ),
    (
        ("cluster98 mirror98 filter98 ranking98 encoding98 mapping98", 28),
        ["cluster98 mirror98 filter98", "ranking98 encoding98", "mapping98"],
    ),
    (
        ("mirror98 filter98 ranking98 encoding98 mapping98 record98", 6),
        ["mirror98", "filter98", "ranking98", "encoding98", "mapping98", "record98"],
    ),
    (
        ("mirror98 filter98 ranking98 encoding98 mapping98 record98", 10),
        ["mirror98", "filter98", "ranking98", "encoding98", "mapping98", "record98"],
    ),
    (
        ("mirror98 filter98 ranking98 encoding98 mapping98 record98", 18),
        ["mirror98 filter98", "ranking98", "encoding98", "mapping98 record98"],
    ),
    (
        ("mirror98 filter98 ranking98 encoding98 mapping98 record98", 28),
        ["mirror98 filter98 ranking98", "encoding98 mapping98", "record98"],
    ),
    (
        ("filter98 ranking98 encoding98 mapping98 record98 candle98", 6),
        ["filter98", "ranking98", "encoding98", "mapping98", "record98", "candle98"],
    ),
    (
        ("filter98 ranking98 encoding98 mapping98 record98 candle98", 10),
        ["filter98", "ranking98", "encoding98", "mapping98", "record98", "candle98"],
    ),
    (
        ("filter98 ranking98 encoding98 mapping98 record98 candle98", 18),
        ["filter98 ranking98", "encoding98", "mapping98 record98", "candle98"],
    ),
    (
        ("filter98 ranking98 encoding98 mapping98 record98 candle98", 28),
        ["filter98 ranking98", "encoding98 mapping98", "record98 candle98"],
    ),
    (
        ("ranking98 encoding98 mapping98 record98 candle98 thread98", 6),
        ["ranking98", "encoding98", "mapping98", "record98", "candle98", "thread98"],
    ),
    (
        ("ranking98 encoding98 mapping98 record98 candle98 thread98", 10),
        ["ranking98", "encoding98", "mapping98", "record98", "candle98", "thread98"],
    ),
    (
        ("ranking98 encoding98 mapping98 record98 candle98 thread98", 18),
        ["ranking98", "encoding98", "mapping98 record98", "candle98 thread98"],
    ),
    (
        ("ranking98 encoding98 mapping98 record98 candle98 thread98", 28),
        ["ranking98 encoding98", "mapping98 record98 candle98", "thread98"],
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
