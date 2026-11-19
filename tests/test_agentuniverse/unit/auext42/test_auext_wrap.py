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
        ("round 42: the quick brown fox jumps over the lazy dog", 4),
        ["round", "42:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 42: the quick brown fox jumps over the lazy dog", 8),
        ["round", "42: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 42: the quick brown fox jumps over the lazy dog", 12),
        ["round 42:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 42: the quick brown fox jumps over the lazy dog", 16),
        ["round 42: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 42: the quick brown fox jumps over the lazy dog", 24),
        ["round 42: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 42: the quick brown fox jumps over the lazy dog", 32),
        ["round 42: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 42: agentuniverse is a framework for multi agents", 4),
        ["round", "42:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 42: agentuniverse is a framework for multi agents", 8),
        ["round", "42:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 42: agentuniverse is a framework for multi agents", 12),
        ["round 42:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 42: agentuniverse is a framework for multi agents", 16),
        ["round 42:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 42: agentuniverse is a framework for multi agents", 24),
        ["round 42: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 42: agentuniverse is a framework for multi agents", 32),
        ["round 42: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 42: knowledge stored as vectors enables retrieval", 4),
        ["round", "42:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 42: knowledge stored as vectors enables retrieval", 8),
        ["round", "42:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 42: knowledge stored as vectors enables retrieval", 12),
        ["round 42:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 42: knowledge stored as vectors enables retrieval", 16),
        ["round 42:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 42: knowledge stored as vectors enables retrieval", 24),
        ["round 42: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 42: knowledge stored as vectors enables retrieval", 32),
        ["round 42: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 42: the processor reads the record then stops", 4),
        ["round", "42:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 42: the processor reads the record then stops", 8),
        ["round", "42: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 42: the processor reads the record then stops", 12),
        ["round 42:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 42: the processor reads the record then stops", 16),
        ["round 42: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 42: the processor reads the record then stops", 24),
        ["round 42: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 42: the processor reads the record then stops", 32),
        ["round 42: the processor reads", "the record then stops"],
    ),
    (
        ("round 42: a worker pulls the next task from the queue", 4),
        ["round", "42:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 42: a worker pulls the next task from the queue", 8),
        ["round", "42: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 42: a worker pulls the next task from the queue", 12),
        ["round 42: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 42: a worker pulls the next task from the queue", 16),
        ["round 42: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 42: a worker pulls the next task from the queue", 24),
        ["round 42: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 42: a worker pulls the next task from the queue", 32),
        ["round 42: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 42: signals travel through the network layer", 4),
        ["round", "42:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 42: signals travel through the network layer", 8),
        ["round", "42:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 42: signals travel through the network layer", 12),
        ["round 42:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 42: signals travel through the network layer", 16),
        ["round 42:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 42: signals travel through the network layer", 24),
        ["round 42: signals travel", "through the network", "layer"],
    ),
    (
        ("round 42: signals travel through the network layer", 32),
        ["round 42: signals travel through", "the network layer"],
    ),
    (
        ("round 42: the gateway routes each request by policy", 4),
        ["round", "42:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 42: the gateway routes each request by policy", 8),
        ["round", "42: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 42: the gateway routes each request by policy", 12),
        ["round 42:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 42: the gateway routes each request by policy", 16),
        ["round 42: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 42: the gateway routes each request by policy", 24),
        ["round 42: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 42: the gateway routes each request by policy", 32),
        ["round 42: the gateway routes", "each request by policy"],
    ),
    (
        ("round 42: memory grows until the buffer is full", 4),
        ["round", "42:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 42: memory grows until the buffer is full", 8),
        ["round", "42:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 42: memory grows until the buffer is full", 12),
        ["round 42:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 42: memory grows until the buffer is full", 16),
        ["round 42: memory", "grows until the", "buffer is full"],
    ),
    (("round 42: memory grows until the buffer is full", 24), ["round 42: memory grows", "until the buffer is full"]),
    (("round 42: memory grows until the buffer is full", 32), ["round 42: memory grows until the", "buffer is full"]),
    (
        ("round 42: the cluster mirrors every packet twice", 4),
        ["round", "42:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 42: the cluster mirrors every packet twice", 8),
        ["round", "42: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 42: the cluster mirrors every packet twice", 12),
        ["round 42:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 42: the cluster mirrors every packet twice", 16),
        ["round 42: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 42: the cluster mirrors every packet twice", 24),
        ["round 42: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 42: the cluster mirrors every packet twice", 32), ["round 42: the cluster mirrors", "every packet twice"]),
    (
        ("round 42: ranking uses tokens learned from the corpus", 4),
        ["round", "42:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 42: ranking uses tokens learned from the corpus", 8),
        ["round", "42:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 42: ranking uses tokens learned from the corpus", 12),
        ["round 42:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 42: ranking uses tokens learned from the corpus", 16),
        ["round 42:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 42: ranking uses tokens learned from the corpus", 24),
        ["round 42: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 42: ranking uses tokens learned from the corpus", 32),
        ["round 42: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 42: a long session ends when the candle dies", 4),
        ["round", "42:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 42: a long session ends when the candle dies", 8),
        ["round", "42: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 42: a long session ends when the candle dies", 12),
        ["round 42: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 42: a long session ends when the candle dies", 16),
        ["round 42: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 42: a long session ends when the candle dies", 24),
        ["round 42: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 42: a long session ends when the candle dies", 32),
        ["round 42: a long session ends", "when the candle dies"],
    ),
    (
        ("round 42: encode the prompt then map the result", 4),
        ["round", "42:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 42: encode the prompt then map the result", 8),
        ["round", "42:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 42: encode the prompt then map the result", 12),
        ["round 42:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 42: encode the prompt then map the result", 16),
        ["round 42: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 42: encode the prompt then map the result", 24),
        ["round 42: encode the", "prompt then map the", "result"],
    ),
    (("round 42: encode the prompt then map the result", 32), ["round 42: encode the prompt then", "map the result"]),
    (
        ("round 42: the kernel wakes the worker at dawn", 4),
        ["round", "42:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 42: the kernel wakes the worker at dawn", 8),
        ["round", "42: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 42: the kernel wakes the worker at dawn", 12),
        ["round 42:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 42: the kernel wakes the worker at dawn", 16), ["round 42: the", "kernel wakes the", "worker at dawn"]),
    (("round 42: the kernel wakes the worker at dawn", 24), ["round 42: the kernel", "wakes the worker at dawn"]),
    (("round 42: the kernel wakes the worker at dawn", 32), ["round 42: the kernel wakes the", "worker at dawn"]),
    (
        ("round 42: service latency drops after the patch", 4),
        ["round", "42:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 42: service latency drops after the patch", 8),
        ["round", "42:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 42: service latency drops after the patch", 12),
        ["round 42:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 42: service latency drops after the patch", 16),
        ["round 42:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 42: service latency drops after the patch", 24),
        ["round 42: service", "latency drops after the", "patch"],
    ),
    (("round 42: service latency drops after the patch", 32), ["round 42: service latency drops", "after the patch"]),
    (
        ("round 42: the library caches every vector it sees", 4),
        ["round", "42:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 42: the library caches every vector it sees", 8),
        ["round", "42: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 42: the library caches every vector it sees", 12),
        ["round 42:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 42: the library caches every vector it sees", 16),
        ["round 42: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 42: the library caches every vector it sees", 24),
        ["round 42: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 42: the library caches every vector it sees", 32),
        ["round 42: the library caches", "every vector it sees"],
    ),
    (
        ("round 42: agents argue then the debate resolves", 4),
        ["round", "42:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 42: agents argue then the debate resolves", 8),
        ["round", "42:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 42: agents argue then the debate resolves", 12),
        ["round 42:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 42: agents argue then the debate resolves", 16),
        ["round 42: agents", "argue then the", "debate resolves"],
    ),
    (("round 42: agents argue then the debate resolves", 24), ["round 42: agents argue", "then the debate resolves"]),
    (("round 42: agents argue then the debate resolves", 32), ["round 42: agents argue then the", "debate resolves"]),
    (
        ("round 42: the filter keeps only strong matches", 4),
        ["round", "42:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 42: the filter keeps only strong matches", 8),
        ["round", "42: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 42: the filter keeps only strong matches", 12),
        ["round 42:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 42: the filter keeps only strong matches", 16),
        ["round 42: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 42: the filter keeps only strong matches", 24), ["round 42: the filter", "keeps only strong", "matches"]),
    (("round 42: the filter keeps only strong matches", 32), ["round 42: the filter keeps only", "strong matches"]),
    (
        ("round 42: the model answers with a short reply", 4),
        ["round", "42:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 42: the model answers with a short reply", 8),
        ["round", "42: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 42: the model answers with a short reply", 12),
        ["round 42:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 42: the model answers with a short reply", 16),
        ["round 42: the", "model answers", "with a short", "reply"],
    ),
    (("round 42: the model answers with a short reply", 24), ["round 42: the model", "answers with a short", "reply"]),
    (("round 42: the model answers with a short reply", 32), ["round 42: the model answers with", "a short reply"]),
    (
        ("round 42: the recorder stores the reasoning trace", 4),
        ["round", "42:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 42: the recorder stores the reasoning trace", 8),
        ["round", "42: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 42: the recorder stores the reasoning trace", 12),
        ["round 42:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 42: the recorder stores the reasoning trace", 16),
        ["round 42: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 42: the recorder stores the reasoning trace", 24),
        ["round 42: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 42: the recorder stores the reasoning trace", 32),
        ["round 42: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 42: the angel watches the processor run", 4),
        ["round", "42:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 42: the angel watches the processor run", 8),
        ["round", "42: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 42: the angel watches the processor run", 12),
        ["round 42:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 42: the angel watches the processor run", 16), ["round 42: the", "angel watches", "the processor", "run"]),
    (("round 42: the angel watches the processor run", 24), ["round 42: the angel", "watches the processor", "run"]),
    (("round 42: the angel watches the processor run", 32), ["round 42: the angel watches the", "processor run"]),
    (
        ("round 42: angle of the vector decides the match", 4),
        ["round", "42:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 42: angle of the vector decides the match", 8),
        ["round", "42:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 42: angle of the vector decides the match", 12),
        ["round 42:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 42: angle of the vector decides the match", 16),
        ["round 42: angle", "of the vector", "decides the", "match"],
    ),
    (("round 42: angle of the vector decides the match", 24), ["round 42: angle of the", "vector decides the match"]),
    (("round 42: angle of the vector decides the match", 32), ["round 42: angle of the vector", "decides the match"]),
    (
        ("round 42: the candle burns twice as long at night", 4),
        ["round", "42:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 42: the candle burns twice as long at night", 8),
        ["round", "42: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 42: the candle burns twice as long at night", 12),
        ["round 42:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 42: the candle burns twice as long at night", 16),
        ["round 42: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 42: the candle burns twice as long at night", 24),
        ["round 42: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 42: the candle burns twice as long at night", 32),
        ["round 42: the candle burns twice", "as long at night"],
    ),
    (
        ("round 42: a mirror of the universe in one line", 4),
        ["round", "42:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 42: a mirror of the universe in one line", 8),
        ["round", "42: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 42: a mirror of the universe in one line", 12),
        ["round 42: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 42: a mirror of the universe in one line", 16),
        ["round 42: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 42: a mirror of the universe in one line", 24), ["round 42: a mirror of", "the universe in one line"]),
    (("round 42: a mirror of the universe in one line", 32), ["round 42: a mirror of the", "universe in one line"]),
    (
        ("round 42: the queue drains before the storm", 4),
        ["round", "42:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 42: the queue drains before the storm", 8),
        ["round", "42: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 42: the queue drains before the storm", 12), ["round 42:", "the queue", "drains", "before the", "storm"]),
    (("round 42: the queue drains before the storm", 16), ["round 42: the", "queue drains", "before the storm"]),
    (("round 42: the queue drains before the storm", 24), ["round 42: the queue", "drains before the storm"]),
    (("round 42: the queue drains before the storm", 32), ["round 42: the queue drains", "before the storm"]),
    (
        ("kitten42 sitting42 agent42 angle42 universe42 memory42", 6),
        ["kitten42", "sitting42", "agent42", "angle42", "universe42", "memory42"],
    ),
    (
        ("kitten42 sitting42 agent42 angle42 universe42 memory42", 10),
        ["kitten42", "sitting42", "agent42", "angle42", "universe42", "memory42"],
    ),
    (
        ("kitten42 sitting42 agent42 angle42 universe42 memory42", 18),
        ["kitten42 sitting42", "agent42 angle42", "universe42", "memory42"],
    ),
    (
        ("kitten42 sitting42 agent42 angle42 universe42 memory42", 28),
        ["kitten42 sitting42 agent42", "angle42 universe42 memory42"],
    ),
    (
        ("sitting42 agent42 angle42 universe42 memory42 stream42", 6),
        ["sitting42", "agent42", "angle42", "universe42", "memory42", "stream42"],
    ),
    (
        ("sitting42 agent42 angle42 universe42 memory42 stream42", 10),
        ["sitting42", "agent42", "angle42", "universe42", "memory42", "stream42"],
    ),
    (
        ("sitting42 agent42 angle42 universe42 memory42 stream42", 18),
        ["sitting42 agent42", "angle42 universe42", "memory42 stream42"],
    ),
    (
        ("sitting42 agent42 angle42 universe42 memory42 stream42", 28),
        ["sitting42 agent42 angle42", "universe42 memory42 stream42"],
    ),
    (
        ("agent42 angle42 universe42 memory42 stream42 context42", 6),
        ["agent42", "angle42", "universe42", "memory42", "stream42", "context42"],
    ),
    (
        ("agent42 angle42 universe42 memory42 stream42 context42", 10),
        ["agent42", "angle42", "universe42", "memory42", "stream42", "context42"],
    ),
    (
        ("agent42 angle42 universe42 memory42 stream42 context42", 18),
        ["agent42 angle42", "universe42", "memory42 stream42", "context42"],
    ),
    (
        ("agent42 angle42 universe42 memory42 stream42 context42", 28),
        ["agent42 angle42 universe42", "memory42 stream42 context42"],
    ),
    (
        ("angle42 universe42 memory42 stream42 context42 knowledge42", 6),
        ["angle42", "universe42", "memory42", "stream42", "context42", "knowledge42"],
    ),
    (
        ("angle42 universe42 memory42 stream42 context42 knowledge42", 10),
        ["angle42", "universe42", "memory42", "stream42", "context42", "knowledge42"],
    ),
    (
        ("angle42 universe42 memory42 stream42 context42 knowledge42", 18),
        ["angle42 universe42", "memory42 stream42", "context42", "knowledge42"],
    ),
    (
        ("angle42 universe42 memory42 stream42 context42 knowledge42", 28),
        ["angle42 universe42 memory42", "stream42 context42", "knowledge42"],
    ),
    (
        ("universe42 memory42 stream42 context42 knowledge42 vector42", 6),
        ["universe42", "memory42", "stream42", "context42", "knowledge42", "vector42"],
    ),
    (
        ("universe42 memory42 stream42 context42 knowledge42 vector42", 10),
        ["universe42", "memory42", "stream42", "context42", "knowledge42", "vector42"],
    ),
    (
        ("universe42 memory42 stream42 context42 knowledge42 vector42", 18),
        ["universe42", "memory42 stream42", "context42", "knowledge42", "vector42"],
    ),
    (
        ("universe42 memory42 stream42 context42 knowledge42 vector42", 28),
        ["universe42 memory42 stream42", "context42 knowledge42", "vector42"],
    ),
    (
        ("memory42 stream42 context42 knowledge42 vector42 processor42", 6),
        ["memory42", "stream42", "context42", "knowledge42", "vector42", "processor42"],
    ),
    (
        ("memory42 stream42 context42 knowledge42 vector42 processor42", 10),
        ["memory42", "stream42", "context42", "knowledge42", "vector42", "processor42"],
    ),
    (
        ("memory42 stream42 context42 knowledge42 vector42 processor42", 18),
        ["memory42 stream42", "context42", "knowledge42", "vector42", "processor42"],
    ),
    (
        ("memory42 stream42 context42 knowledge42 vector42 processor42", 28),
        ["memory42 stream42 context42", "knowledge42 vector42", "processor42"],
    ),
    (
        ("stream42 context42 knowledge42 vector42 processor42 reasoning42", 6),
        ["stream42", "context42", "knowledge42", "vector42", "processor42", "reasoning42"],
    ),
    (
        ("stream42 context42 knowledge42 vector42 processor42 reasoning42", 10),
        ["stream42", "context42", "knowledge42", "vector42", "processor42", "reasoning42"],
    ),
    (
        ("stream42 context42 knowledge42 vector42 processor42 reasoning42", 18),
        ["stream42 context42", "knowledge42", "vector42", "processor42", "reasoning42"],
    ),
    (
        ("stream42 context42 knowledge42 vector42 processor42 reasoning42", 28),
        ["stream42 context42", "knowledge42 vector42", "processor42 reasoning42"],
    ),
    (
        ("context42 knowledge42 vector42 processor42 reasoning42 machine42", 6),
        ["context42", "knowledge42", "vector42", "processor42", "reasoning42", "machine42"],
    ),
    (
        ("context42 knowledge42 vector42 processor42 reasoning42 machine42", 10),
        ["context42", "knowledge42", "vector42", "processor42", "reasoning42", "machine42"],
    ),
    (
        ("context42 knowledge42 vector42 processor42 reasoning42 machine42", 18),
        ["context42", "knowledge42", "vector42", "processor42", "reasoning42", "machine42"],
    ),
    (
        ("context42 knowledge42 vector42 processor42 reasoning42 machine42", 28),
        ["context42 knowledge42", "vector42 processor42", "reasoning42 machine42"],
    ),
    (
        ("knowledge42 vector42 processor42 reasoning42 machine42 learning42", 6),
        ["knowledge42", "vector42", "processor42", "reasoning42", "machine42", "learning42"],
    ),
    (
        ("knowledge42 vector42 processor42 reasoning42 machine42 learning42", 10),
        ["knowledge42", "vector42", "processor42", "reasoning42", "machine42", "learning42"],
    ),
    (
        ("knowledge42 vector42 processor42 reasoning42 machine42 learning42", 18),
        ["knowledge42", "vector42", "processor42", "reasoning42", "machine42", "learning42"],
    ),
    (
        ("knowledge42 vector42 processor42 reasoning42 machine42 learning42", 28),
        ["knowledge42 vector42", "processor42 reasoning42", "machine42 learning42"],
    ),
    (
        ("vector42 processor42 reasoning42 machine42 learning42 model42", 6),
        ["vector42", "processor42", "reasoning42", "machine42", "learning42", "model42"],
    ),
    (
        ("vector42 processor42 reasoning42 machine42 learning42 model42", 10),
        ["vector42", "processor42", "reasoning42", "machine42", "learning42", "model42"],
    ),
    (
        ("vector42 processor42 reasoning42 machine42 learning42 model42", 18),
        ["vector42", "processor42", "reasoning42", "machine42", "learning42 model42"],
    ),
    (
        ("vector42 processor42 reasoning42 machine42 learning42 model42", 28),
        ["vector42 processor42", "reasoning42 machine42", "learning42 model42"],
    ),
    (
        ("processor42 reasoning42 machine42 learning42 model42 token42", 6),
        ["processor42", "reasoning42", "machine42", "learning42", "model42", "token42"],
    ),
    (
        ("processor42 reasoning42 machine42 learning42 model42 token42", 10),
        ["processor42", "reasoning42", "machine42", "learning42", "model42", "token42"],
    ),
    (
        ("processor42 reasoning42 machine42 learning42 model42 token42", 18),
        ["processor42", "reasoning42", "machine42", "learning42 model42", "token42"],
    ),
    (
        ("processor42 reasoning42 machine42 learning42 model42 token42", 28),
        ["processor42 reasoning42", "machine42 learning42 model42", "token42"],
    ),
    (
        ("reasoning42 machine42 learning42 model42 token42 prompt42", 6),
        ["reasoning42", "machine42", "learning42", "model42", "token42", "prompt42"],
    ),
    (
        ("reasoning42 machine42 learning42 model42 token42 prompt42", 10),
        ["reasoning42", "machine42", "learning42", "model42", "token42", "prompt42"],
    ),
    (
        ("reasoning42 machine42 learning42 model42 token42 prompt42", 18),
        ["reasoning42", "machine42", "learning42 model42", "token42 prompt42"],
    ),
    (
        ("reasoning42 machine42 learning42 model42 token42 prompt42", 28),
        ["reasoning42 machine42", "learning42 model42 token42", "prompt42"],
    ),
    (
        ("machine42 learning42 model42 token42 prompt42 session42", 6),
        ["machine42", "learning42", "model42", "token42", "prompt42", "session42"],
    ),
    (
        ("machine42 learning42 model42 token42 prompt42 session42", 10),
        ["machine42", "learning42", "model42", "token42", "prompt42", "session42"],
    ),
    (
        ("machine42 learning42 model42 token42 prompt42 session42", 18),
        ["machine42", "learning42 model42", "token42 prompt42", "session42"],
    ),
    (
        ("machine42 learning42 model42 token42 prompt42 session42", 28),
        ["machine42 learning42 model42", "token42 prompt42 session42"],
    ),
    (
        ("learning42 model42 token42 prompt42 session42 library42", 6),
        ["learning42", "model42", "token42", "prompt42", "session42", "library42"],
    ),
    (
        ("learning42 model42 token42 prompt42 session42 library42", 10),
        ["learning42", "model42", "token42", "prompt42", "session42", "library42"],
    ),
    (
        ("learning42 model42 token42 prompt42 session42 library42", 18),
        ["learning42 model42", "token42 prompt42", "session42", "library42"],
    ),
    (
        ("learning42 model42 token42 prompt42 session42 library42", 28),
        ["learning42 model42 token42", "prompt42 session42 library42"],
    ),
    (
        ("model42 token42 prompt42 session42 library42 service42", 6),
        ["model42", "token42", "prompt42", "session42", "library42", "service42"],
    ),
    (
        ("model42 token42 prompt42 session42 library42 service42", 10),
        ["model42", "token42", "prompt42", "session42", "library42", "service42"],
    ),
    (
        ("model42 token42 prompt42 session42 library42 service42", 18),
        ["model42 token42", "prompt42 session42", "library42", "service42"],
    ),
    (
        ("model42 token42 prompt42 session42 library42 service42", 28),
        ["model42 token42 prompt42", "session42 library42", "service42"],
    ),
    (
        ("token42 prompt42 session42 library42 service42 gateway42", 6),
        ["token42", "prompt42", "session42", "library42", "service42", "gateway42"],
    ),
    (
        ("token42 prompt42 session42 library42 service42 gateway42", 10),
        ["token42", "prompt42", "session42", "library42", "service42", "gateway42"],
    ),
    (
        ("token42 prompt42 session42 library42 service42 gateway42", 18),
        ["token42 prompt42", "session42", "library42", "service42", "gateway42"],
    ),
    (
        ("token42 prompt42 session42 library42 service42 gateway42", 28),
        ["token42 prompt42 session42", "library42 service42", "gateway42"],
    ),
    (
        ("prompt42 session42 library42 service42 gateway42 storage42", 6),
        ["prompt42", "session42", "library42", "service42", "gateway42", "storage42"],
    ),
    (
        ("prompt42 session42 library42 service42 gateway42 storage42", 10),
        ["prompt42", "session42", "library42", "service42", "gateway42", "storage42"],
    ),
    (
        ("prompt42 session42 library42 service42 gateway42 storage42", 18),
        ["prompt42 session42", "library42", "service42", "gateway42", "storage42"],
    ),
    (
        ("prompt42 session42 library42 service42 gateway42 storage42", 28),
        ["prompt42 session42 library42", "service42 gateway42", "storage42"],
    ),
    (
        ("session42 library42 service42 gateway42 storage42 network42", 6),
        ["session42", "library42", "service42", "gateway42", "storage42", "network42"],
    ),
    (
        ("session42 library42 service42 gateway42 storage42 network42", 10),
        ["session42", "library42", "service42", "gateway42", "storage42", "network42"],
    ),
    (
        ("session42 library42 service42 gateway42 storage42 network42", 18),
        ["session42", "library42", "service42", "gateway42", "storage42", "network42"],
    ),
    (
        ("session42 library42 service42 gateway42 storage42 network42", 28),
        ["session42 library42", "service42 gateway42", "storage42 network42"],
    ),
    (
        ("library42 service42 gateway42 storage42 network42 latency42", 6),
        ["library42", "service42", "gateway42", "storage42", "network42", "latency42"],
    ),
    (
        ("library42 service42 gateway42 storage42 network42 latency42", 10),
        ["library42", "service42", "gateway42", "storage42", "network42", "latency42"],
    ),
    (
        ("library42 service42 gateway42 storage42 network42 latency42", 18),
        ["library42", "service42", "gateway42", "storage42", "network42", "latency42"],
    ),
    (
        ("library42 service42 gateway42 storage42 network42 latency42", 28),
        ["library42 service42", "gateway42 storage42", "network42 latency42"],
    ),
    (
        ("service42 gateway42 storage42 network42 latency42 buffer42", 6),
        ["service42", "gateway42", "storage42", "network42", "latency42", "buffer42"],
    ),
    (
        ("service42 gateway42 storage42 network42 latency42 buffer42", 10),
        ["service42", "gateway42", "storage42", "network42", "latency42", "buffer42"],
    ),
    (
        ("service42 gateway42 storage42 network42 latency42 buffer42", 18),
        ["service42", "gateway42", "storage42", "network42", "latency42 buffer42"],
    ),
    (
        ("service42 gateway42 storage42 network42 latency42 buffer42", 28),
        ["service42 gateway42", "storage42 network42", "latency42 buffer42"],
    ),
    (
        ("gateway42 storage42 network42 latency42 buffer42 queue42", 6),
        ["gateway42", "storage42", "network42", "latency42", "buffer42", "queue42"],
    ),
    (
        ("gateway42 storage42 network42 latency42 buffer42 queue42", 10),
        ["gateway42", "storage42", "network42", "latency42", "buffer42", "queue42"],
    ),
    (
        ("gateway42 storage42 network42 latency42 buffer42 queue42", 18),
        ["gateway42", "storage42", "network42", "latency42 buffer42", "queue42"],
    ),
    (
        ("gateway42 storage42 network42 latency42 buffer42 queue42", 28),
        ["gateway42 storage42", "network42 latency42 buffer42", "queue42"],
    ),
    (
        ("storage42 network42 latency42 buffer42 queue42 worker42", 6),
        ["storage42", "network42", "latency42", "buffer42", "queue42", "worker42"],
    ),
    (
        ("storage42 network42 latency42 buffer42 queue42 worker42", 10),
        ["storage42", "network42", "latency42", "buffer42", "queue42", "worker42"],
    ),
    (
        ("storage42 network42 latency42 buffer42 queue42 worker42", 18),
        ["storage42", "network42", "latency42 buffer42", "queue42 worker42"],
    ),
    (
        ("storage42 network42 latency42 buffer42 queue42 worker42", 28),
        ["storage42 network42", "latency42 buffer42 queue42", "worker42"],
    ),
    (
        ("network42 latency42 buffer42 queue42 worker42 kernel42", 6),
        ["network42", "latency42", "buffer42", "queue42", "worker42", "kernel42"],
    ),
    (
        ("network42 latency42 buffer42 queue42 worker42 kernel42", 10),
        ["network42", "latency42", "buffer42", "queue42", "worker42", "kernel42"],
    ),
    (
        ("network42 latency42 buffer42 queue42 worker42 kernel42", 18),
        ["network42", "latency42 buffer42", "queue42 worker42", "kernel42"],
    ),
    (
        ("network42 latency42 buffer42 queue42 worker42 kernel42", 28),
        ["network42 latency42 buffer42", "queue42 worker42 kernel42"],
    ),
    (
        ("latency42 buffer42 queue42 worker42 kernel42 signal42", 6),
        ["latency42", "buffer42", "queue42", "worker42", "kernel42", "signal42"],
    ),
    (
        ("latency42 buffer42 queue42 worker42 kernel42 signal42", 10),
        ["latency42", "buffer42", "queue42", "worker42", "kernel42", "signal42"],
    ),
    (
        ("latency42 buffer42 queue42 worker42 kernel42 signal42", 18),
        ["latency42 buffer42", "queue42 worker42", "kernel42 signal42"],
    ),
    (
        ("latency42 buffer42 queue42 worker42 kernel42 signal42", 28),
        ["latency42 buffer42 queue42", "worker42 kernel42 signal42"],
    ),
    (
        ("buffer42 queue42 worker42 kernel42 signal42 packet42", 6),
        ["buffer42", "queue42", "worker42", "kernel42", "signal42", "packet42"],
    ),
    (
        ("buffer42 queue42 worker42 kernel42 signal42 packet42", 10),
        ["buffer42", "queue42", "worker42", "kernel42", "signal42", "packet42"],
    ),
    (
        ("buffer42 queue42 worker42 kernel42 signal42 packet42", 18),
        ["buffer42 queue42", "worker42 kernel42", "signal42 packet42"],
    ),
    (
        ("buffer42 queue42 worker42 kernel42 signal42 packet42", 28),
        ["buffer42 queue42 worker42", "kernel42 signal42 packet42"],
    ),
    (
        ("queue42 worker42 kernel42 signal42 packet42 router42", 6),
        ["queue42", "worker42", "kernel42", "signal42", "packet42", "router42"],
    ),
    (
        ("queue42 worker42 kernel42 signal42 packet42 router42", 10),
        ["queue42", "worker42", "kernel42", "signal42", "packet42", "router42"],
    ),
    (
        ("queue42 worker42 kernel42 signal42 packet42 router42", 18),
        ["queue42 worker42", "kernel42 signal42", "packet42 router42"],
    ),
    (
        ("queue42 worker42 kernel42 signal42 packet42 router42", 28),
        ["queue42 worker42 kernel42", "signal42 packet42 router42"],
    ),
    (
        ("worker42 kernel42 signal42 packet42 router42 cluster42", 6),
        ["worker42", "kernel42", "signal42", "packet42", "router42", "cluster42"],
    ),
    (
        ("worker42 kernel42 signal42 packet42 router42 cluster42", 10),
        ["worker42", "kernel42", "signal42", "packet42", "router42", "cluster42"],
    ),
    (
        ("worker42 kernel42 signal42 packet42 router42 cluster42", 18),
        ["worker42 kernel42", "signal42 packet42", "router42 cluster42"],
    ),
    (
        ("worker42 kernel42 signal42 packet42 router42 cluster42", 28),
        ["worker42 kernel42 signal42", "packet42 router42 cluster42"],
    ),
    (
        ("kernel42 signal42 packet42 router42 cluster42 mirror42", 6),
        ["kernel42", "signal42", "packet42", "router42", "cluster42", "mirror42"],
    ),
    (
        ("kernel42 signal42 packet42 router42 cluster42 mirror42", 10),
        ["kernel42", "signal42", "packet42", "router42", "cluster42", "mirror42"],
    ),
    (
        ("kernel42 signal42 packet42 router42 cluster42 mirror42", 18),
        ["kernel42 signal42", "packet42 router42", "cluster42 mirror42"],
    ),
    (
        ("kernel42 signal42 packet42 router42 cluster42 mirror42", 28),
        ["kernel42 signal42 packet42", "router42 cluster42 mirror42"],
    ),
    (
        ("signal42 packet42 router42 cluster42 mirror42 filter42", 6),
        ["signal42", "packet42", "router42", "cluster42", "mirror42", "filter42"],
    ),
    (
        ("signal42 packet42 router42 cluster42 mirror42 filter42", 10),
        ["signal42", "packet42", "router42", "cluster42", "mirror42", "filter42"],
    ),
    (
        ("signal42 packet42 router42 cluster42 mirror42 filter42", 18),
        ["signal42 packet42", "router42 cluster42", "mirror42 filter42"],
    ),
    (
        ("signal42 packet42 router42 cluster42 mirror42 filter42", 28),
        ["signal42 packet42 router42", "cluster42 mirror42 filter42"],
    ),
    (
        ("packet42 router42 cluster42 mirror42 filter42 ranking42", 6),
        ["packet42", "router42", "cluster42", "mirror42", "filter42", "ranking42"],
    ),
    (
        ("packet42 router42 cluster42 mirror42 filter42 ranking42", 10),
        ["packet42", "router42", "cluster42", "mirror42", "filter42", "ranking42"],
    ),
    (
        ("packet42 router42 cluster42 mirror42 filter42 ranking42", 18),
        ["packet42 router42", "cluster42 mirror42", "filter42 ranking42"],
    ),
    (
        ("packet42 router42 cluster42 mirror42 filter42 ranking42", 28),
        ["packet42 router42 cluster42", "mirror42 filter42 ranking42"],
    ),
    (
        ("router42 cluster42 mirror42 filter42 ranking42 encoding42", 6),
        ["router42", "cluster42", "mirror42", "filter42", "ranking42", "encoding42"],
    ),
    (
        ("router42 cluster42 mirror42 filter42 ranking42 encoding42", 10),
        ["router42", "cluster42", "mirror42", "filter42", "ranking42", "encoding42"],
    ),
    (
        ("router42 cluster42 mirror42 filter42 ranking42 encoding42", 18),
        ["router42 cluster42", "mirror42 filter42", "ranking42", "encoding42"],
    ),
    (
        ("router42 cluster42 mirror42 filter42 ranking42 encoding42", 28),
        ["router42 cluster42 mirror42", "filter42 ranking42", "encoding42"],
    ),
    (
        ("cluster42 mirror42 filter42 ranking42 encoding42 mapping42", 6),
        ["cluster42", "mirror42", "filter42", "ranking42", "encoding42", "mapping42"],
    ),
    (
        ("cluster42 mirror42 filter42 ranking42 encoding42 mapping42", 10),
        ["cluster42", "mirror42", "filter42", "ranking42", "encoding42", "mapping42"],
    ),
    (
        ("cluster42 mirror42 filter42 ranking42 encoding42 mapping42", 18),
        ["cluster42 mirror42", "filter42 ranking42", "encoding42", "mapping42"],
    ),
    (
        ("cluster42 mirror42 filter42 ranking42 encoding42 mapping42", 28),
        ["cluster42 mirror42 filter42", "ranking42 encoding42", "mapping42"],
    ),
    (
        ("mirror42 filter42 ranking42 encoding42 mapping42 record42", 6),
        ["mirror42", "filter42", "ranking42", "encoding42", "mapping42", "record42"],
    ),
    (
        ("mirror42 filter42 ranking42 encoding42 mapping42 record42", 10),
        ["mirror42", "filter42", "ranking42", "encoding42", "mapping42", "record42"],
    ),
    (
        ("mirror42 filter42 ranking42 encoding42 mapping42 record42", 18),
        ["mirror42 filter42", "ranking42", "encoding42", "mapping42 record42"],
    ),
    (
        ("mirror42 filter42 ranking42 encoding42 mapping42 record42", 28),
        ["mirror42 filter42 ranking42", "encoding42 mapping42", "record42"],
    ),
    (
        ("filter42 ranking42 encoding42 mapping42 record42 candle42", 6),
        ["filter42", "ranking42", "encoding42", "mapping42", "record42", "candle42"],
    ),
    (
        ("filter42 ranking42 encoding42 mapping42 record42 candle42", 10),
        ["filter42", "ranking42", "encoding42", "mapping42", "record42", "candle42"],
    ),
    (
        ("filter42 ranking42 encoding42 mapping42 record42 candle42", 18),
        ["filter42 ranking42", "encoding42", "mapping42 record42", "candle42"],
    ),
    (
        ("filter42 ranking42 encoding42 mapping42 record42 candle42", 28),
        ["filter42 ranking42", "encoding42 mapping42", "record42 candle42"],
    ),
    (
        ("ranking42 encoding42 mapping42 record42 candle42 thread42", 6),
        ["ranking42", "encoding42", "mapping42", "record42", "candle42", "thread42"],
    ),
    (
        ("ranking42 encoding42 mapping42 record42 candle42 thread42", 10),
        ["ranking42", "encoding42", "mapping42", "record42", "candle42", "thread42"],
    ),
    (
        ("ranking42 encoding42 mapping42 record42 candle42 thread42", 18),
        ["ranking42", "encoding42", "mapping42 record42", "candle42 thread42"],
    ),
    (
        ("ranking42 encoding42 mapping42 record42 candle42 thread42", 28),
        ["ranking42 encoding42", "mapping42 record42 candle42", "thread42"],
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
