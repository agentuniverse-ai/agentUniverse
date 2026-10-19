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
        ("round 151: the quick brown fox jumps over the lazy dog", 4),
        ["round", "151:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 151: the quick brown fox jumps over the lazy dog", 8),
        ["round", "151: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 151: the quick brown fox jumps over the lazy dog", 12),
        ["round 151:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 151: the quick brown fox jumps over the lazy dog", 16),
        ["round 151: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 151: the quick brown fox jumps over the lazy dog", 24),
        ["round 151: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 151: the quick brown fox jumps over the lazy dog", 32),
        ["round 151: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 151: agentuniverse is a framework for multi agents", 4),
        ["round", "151:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 151: agentuniverse is a framework for multi agents", 8),
        ["round", "151:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 151: agentuniverse is a framework for multi agents", 12),
        ["round 151:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 151: agentuniverse is a framework for multi agents", 16),
        ["round 151:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 151: agentuniverse is a framework for multi agents", 24),
        ["round 151: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 151: agentuniverse is a framework for multi agents", 32),
        ["round 151: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 151: knowledge stored as vectors enables retrieval", 4),
        ["round", "151:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 151: knowledge stored as vectors enables retrieval", 8),
        ["round", "151:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 151: knowledge stored as vectors enables retrieval", 12),
        ["round 151:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 151: knowledge stored as vectors enables retrieval", 16),
        ["round 151:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 151: knowledge stored as vectors enables retrieval", 24),
        ["round 151: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 151: knowledge stored as vectors enables retrieval", 32),
        ["round 151: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 151: the processor reads the record then stops", 4),
        ["round", "151:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 151: the processor reads the record then stops", 8),
        ["round", "151: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 151: the processor reads the record then stops", 12),
        ["round 151:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 151: the processor reads the record then stops", 16),
        ["round 151: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 151: the processor reads the record then stops", 24),
        ["round 151: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 151: the processor reads the record then stops", 32),
        ["round 151: the processor reads", "the record then stops"],
    ),
    (
        ("round 151: a worker pulls the next task from the queue", 4),
        ["round", "151:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 151: a worker pulls the next task from the queue", 8),
        ["round", "151: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 151: a worker pulls the next task from the queue", 12),
        ["round 151: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 151: a worker pulls the next task from the queue", 16),
        ["round 151: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 151: a worker pulls the next task from the queue", 24),
        ["round 151: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 151: a worker pulls the next task from the queue", 32),
        ["round 151: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 151: signals travel through the network layer", 4),
        ["round", "151:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 151: signals travel through the network layer", 8),
        ["round", "151:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 151: signals travel through the network layer", 12),
        ["round 151:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 151: signals travel through the network layer", 16),
        ["round 151:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 151: signals travel through the network layer", 24),
        ["round 151: signals", "travel through the", "network layer"],
    ),
    (
        ("round 151: signals travel through the network layer", 32),
        ["round 151: signals travel", "through the network layer"],
    ),
    (
        ("round 151: the gateway routes each request by policy", 4),
        ["round", "151:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 151: the gateway routes each request by policy", 8),
        ["round", "151: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 151: the gateway routes each request by policy", 12),
        ["round 151:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 151: the gateway routes each request by policy", 16),
        ["round 151: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 151: the gateway routes each request by policy", 24),
        ["round 151: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 151: the gateway routes each request by policy", 32),
        ["round 151: the gateway routes", "each request by policy"],
    ),
    (
        ("round 151: memory grows until the buffer is full", 4),
        ["round", "151:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 151: memory grows until the buffer is full", 8),
        ["round", "151:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 151: memory grows until the buffer is full", 12),
        ["round 151:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 151: memory grows until the buffer is full", 16),
        ["round 151:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 151: memory grows until the buffer is full", 24), ["round 151: memory grows", "until the buffer is full"]),
    (("round 151: memory grows until the buffer is full", 32), ["round 151: memory grows until", "the buffer is full"]),
    (
        ("round 151: the cluster mirrors every packet twice", 4),
        ["round", "151:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 151: the cluster mirrors every packet twice", 8),
        ["round", "151: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 151: the cluster mirrors every packet twice", 12),
        ["round 151:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 151: the cluster mirrors every packet twice", 16),
        ["round 151: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 151: the cluster mirrors every packet twice", 24),
        ["round 151: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 151: the cluster mirrors every packet twice", 32),
        ["round 151: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 151: ranking uses tokens learned from the corpus", 4),
        ["round", "151:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 151: ranking uses tokens learned from the corpus", 8),
        ["round", "151:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 151: ranking uses tokens learned from the corpus", 12),
        ["round 151:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 151: ranking uses tokens learned from the corpus", 16),
        ["round 151:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 151: ranking uses tokens learned from the corpus", 24),
        ["round 151: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 151: ranking uses tokens learned from the corpus", 32),
        ["round 151: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 151: a long session ends when the candle dies", 4),
        ["round", "151:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 151: a long session ends when the candle dies", 8),
        ["round", "151: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 151: a long session ends when the candle dies", 12),
        ["round 151: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 151: a long session ends when the candle dies", 16),
        ["round 151: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 151: a long session ends when the candle dies", 24),
        ["round 151: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 151: a long session ends when the candle dies", 32),
        ["round 151: a long session ends", "when the candle dies"],
    ),
    (
        ("round 151: encode the prompt then map the result", 4),
        ["round", "151:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 151: encode the prompt then map the result", 8),
        ["round", "151:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 151: encode the prompt then map the result", 12),
        ["round 151:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 151: encode the prompt then map the result", 16),
        ["round 151:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 151: encode the prompt then map the result", 24),
        ["round 151: encode the", "prompt then map the", "result"],
    ),
    (("round 151: encode the prompt then map the result", 32), ["round 151: encode the prompt", "then map the result"]),
    (
        ("round 151: the kernel wakes the worker at dawn", 4),
        ["round", "151:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 151: the kernel wakes the worker at dawn", 8),
        ["round", "151: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 151: the kernel wakes the worker at dawn", 12),
        ["round 151:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 151: the kernel wakes the worker at dawn", 16), ["round 151: the", "kernel wakes the", "worker at dawn"]),
    (("round 151: the kernel wakes the worker at dawn", 24), ["round 151: the kernel", "wakes the worker at dawn"]),
    (("round 151: the kernel wakes the worker at dawn", 32), ["round 151: the kernel wakes the", "worker at dawn"]),
    (
        ("round 151: service latency drops after the patch", 4),
        ["round", "151:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 151: service latency drops after the patch", 8),
        ["round", "151:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 151: service latency drops after the patch", 12),
        ["round 151:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 151: service latency drops after the patch", 16),
        ["round 151:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 151: service latency drops after the patch", 24),
        ["round 151: service", "latency drops after the", "patch"],
    ),
    (("round 151: service latency drops after the patch", 32), ["round 151: service latency drops", "after the patch"]),
    (
        ("round 151: the library caches every vector it sees", 4),
        ["round", "151:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 151: the library caches every vector it sees", 8),
        ["round", "151: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 151: the library caches every vector it sees", 12),
        ["round 151:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 151: the library caches every vector it sees", 16),
        ["round 151: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 151: the library caches every vector it sees", 24),
        ["round 151: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 151: the library caches every vector it sees", 32),
        ["round 151: the library caches", "every vector it sees"],
    ),
    (
        ("round 151: agents argue then the debate resolves", 4),
        ["round", "151:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 151: agents argue then the debate resolves", 8),
        ["round", "151:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 151: agents argue then the debate resolves", 12),
        ["round 151:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 151: agents argue then the debate resolves", 16),
        ["round 151:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 151: agents argue then the debate resolves", 24), ["round 151: agents argue", "then the debate resolves"]),
    (("round 151: agents argue then the debate resolves", 32), ["round 151: agents argue then the", "debate resolves"]),
    (
        ("round 151: the filter keeps only strong matches", 4),
        ["round", "151:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 151: the filter keeps only strong matches", 8),
        ["round", "151: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 151: the filter keeps only strong matches", 12),
        ["round 151:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 151: the filter keeps only strong matches", 16),
        ["round 151: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 151: the filter keeps only strong matches", 24),
        ["round 151: the filter", "keeps only strong", "matches"],
    ),
    (("round 151: the filter keeps only strong matches", 32), ["round 151: the filter keeps only", "strong matches"]),
    (
        ("round 151: the model answers with a short reply", 4),
        ["round", "151:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 151: the model answers with a short reply", 8),
        ["round", "151: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 151: the model answers with a short reply", 12),
        ["round 151:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 151: the model answers with a short reply", 16),
        ["round 151: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 151: the model answers with a short reply", 24),
        ["round 151: the model", "answers with a short", "reply"],
    ),
    (("round 151: the model answers with a short reply", 32), ["round 151: the model answers", "with a short reply"]),
    (
        ("round 151: the recorder stores the reasoning trace", 4),
        ["round", "151:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 151: the recorder stores the reasoning trace", 8),
        ["round", "151: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 151: the recorder stores the reasoning trace", 12),
        ["round 151:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 151: the recorder stores the reasoning trace", 16),
        ["round 151: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 151: the recorder stores the reasoning trace", 24),
        ["round 151: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 151: the recorder stores the reasoning trace", 32),
        ["round 151: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 151: the angel watches the processor run", 4),
        ["round", "151:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 151: the angel watches the processor run", 8),
        ["round", "151: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 151: the angel watches the processor run", 12),
        ["round 151:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 151: the angel watches the processor run", 16),
        ["round 151: the", "angel watches", "the processor", "run"],
    ),
    (("round 151: the angel watches the processor run", 24), ["round 151: the angel", "watches the processor", "run"]),
    (("round 151: the angel watches the processor run", 32), ["round 151: the angel watches the", "processor run"]),
    (
        ("round 151: angle of the vector decides the match", 4),
        ["round", "151:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 151: angle of the vector decides the match", 8),
        ["round", "151:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 151: angle of the vector decides the match", 12),
        ["round 151:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 151: angle of the vector decides the match", 16),
        ["round 151: angle", "of the vector", "decides the", "match"],
    ),
    (("round 151: angle of the vector decides the match", 24), ["round 151: angle of the", "vector decides the match"]),
    (("round 151: angle of the vector decides the match", 32), ["round 151: angle of the vector", "decides the match"]),
    (
        ("round 151: the candle burns twice as long at night", 4),
        ["round", "151:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 151: the candle burns twice as long at night", 8),
        ["round", "151: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 151: the candle burns twice as long at night", 12),
        ["round 151:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 151: the candle burns twice as long at night", 16),
        ["round 151: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 151: the candle burns twice as long at night", 24),
        ["round 151: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 151: the candle burns twice as long at night", 32),
        ["round 151: the candle burns", "twice as long at night"],
    ),
    (
        ("round 151: a mirror of the universe in one line", 4),
        ["round", "151:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 151: a mirror of the universe in one line", 8),
        ["round", "151: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 151: a mirror of the universe in one line", 12),
        ["round 151: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 151: a mirror of the universe in one line", 16),
        ["round 151: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 151: a mirror of the universe in one line", 24), ["round 151: a mirror of", "the universe in one line"]),
    (("round 151: a mirror of the universe in one line", 32), ["round 151: a mirror of the", "universe in one line"]),
    (
        ("round 151: the queue drains before the storm", 4),
        ["round", "151:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 151: the queue drains before the storm", 8),
        ["round", "151: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 151: the queue drains before the storm", 12),
        ["round 151:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 151: the queue drains before the storm", 16), ["round 151: the", "queue drains", "before the storm"]),
    (("round 151: the queue drains before the storm", 24), ["round 151: the queue", "drains before the storm"]),
    (("round 151: the queue drains before the storm", 32), ["round 151: the queue drains", "before the storm"]),
    (
        ("kitten151 sitting151 agent151 angle151 universe151 memory151", 6),
        ["kitten151", "sitting151", "agent151", "angle151", "universe151", "memory151"],
    ),
    (
        ("kitten151 sitting151 agent151 angle151 universe151 memory151", 10),
        ["kitten151", "sitting151", "agent151", "angle151", "universe151", "memory151"],
    ),
    (
        ("kitten151 sitting151 agent151 angle151 universe151 memory151", 18),
        ["kitten151", "sitting151", "agent151 angle151", "universe151", "memory151"],
    ),
    (
        ("kitten151 sitting151 agent151 angle151 universe151 memory151", 28),
        ["kitten151 sitting151", "agent151 angle151", "universe151 memory151"],
    ),
    (
        ("sitting151 agent151 angle151 universe151 memory151 stream151", 6),
        ["sitting151", "agent151", "angle151", "universe151", "memory151", "stream151"],
    ),
    (
        ("sitting151 agent151 angle151 universe151 memory151 stream151", 10),
        ["sitting151", "agent151", "angle151", "universe151", "memory151", "stream151"],
    ),
    (
        ("sitting151 agent151 angle151 universe151 memory151 stream151", 18),
        ["sitting151", "agent151 angle151", "universe151", "memory151", "stream151"],
    ),
    (
        ("sitting151 agent151 angle151 universe151 memory151 stream151", 28),
        ["sitting151 agent151 angle151", "universe151 memory151", "stream151"],
    ),
    (
        ("agent151 angle151 universe151 memory151 stream151 context151", 6),
        ["agent151", "angle151", "universe151", "memory151", "stream151", "context151"],
    ),
    (
        ("agent151 angle151 universe151 memory151 stream151 context151", 10),
        ["agent151", "angle151", "universe151", "memory151", "stream151", "context151"],
    ),
    (
        ("agent151 angle151 universe151 memory151 stream151 context151", 18),
        ["agent151 angle151", "universe151", "memory151", "stream151", "context151"],
    ),
    (
        ("agent151 angle151 universe151 memory151 stream151 context151", 28),
        ["agent151 angle151", "universe151 memory151", "stream151 context151"],
    ),
    (
        ("angle151 universe151 memory151 stream151 context151 knowledge151", 6),
        ["angle151", "universe151", "memory151", "stream151", "context151", "knowledge151"],
    ),
    (
        ("angle151 universe151 memory151 stream151 context151 knowledge151", 10),
        ["angle151", "universe151", "memory151", "stream151", "context151", "knowledge151"],
    ),
    (
        ("angle151 universe151 memory151 stream151 context151 knowledge151", 18),
        ["angle151", "universe151", "memory151", "stream151", "context151", "knowledge151"],
    ),
    (
        ("angle151 universe151 memory151 stream151 context151 knowledge151", 28),
        ["angle151 universe151", "memory151 stream151", "context151 knowledge151"],
    ),
    (
        ("universe151 memory151 stream151 context151 knowledge151 vector151", 6),
        ["universe151", "memory151", "stream151", "context151", "knowledge151", "vector151"],
    ),
    (
        ("universe151 memory151 stream151 context151 knowledge151 vector151", 10),
        ["universe151", "memory151", "stream151", "context151", "knowledge151", "vector151"],
    ),
    (
        ("universe151 memory151 stream151 context151 knowledge151 vector151", 18),
        ["universe151", "memory151", "stream151", "context151", "knowledge151", "vector151"],
    ),
    (
        ("universe151 memory151 stream151 context151 knowledge151 vector151", 28),
        ["universe151 memory151", "stream151 context151", "knowledge151 vector151"],
    ),
    (
        ("memory151 stream151 context151 knowledge151 vector151 processor151", 6),
        ["memory151", "stream151", "context151", "knowledge151", "vector151", "processor151"],
    ),
    (
        ("memory151 stream151 context151 knowledge151 vector151 processor151", 10),
        ["memory151", "stream151", "context151", "knowledge151", "vector151", "processor151"],
    ),
    (
        ("memory151 stream151 context151 knowledge151 vector151 processor151", 18),
        ["memory151", "stream151", "context151", "knowledge151", "vector151", "processor151"],
    ),
    (
        ("memory151 stream151 context151 knowledge151 vector151 processor151", 28),
        ["memory151 stream151", "context151 knowledge151", "vector151 processor151"],
    ),
    (
        ("stream151 context151 knowledge151 vector151 processor151 reasoning151", 6),
        ["stream151", "context151", "knowledge151", "vector151", "processor151", "reasoning151"],
    ),
    (
        ("stream151 context151 knowledge151 vector151 processor151 reasoning151", 10),
        ["stream151", "context151", "knowledge151", "vector151", "processor151", "reasoning151"],
    ),
    (
        ("stream151 context151 knowledge151 vector151 processor151 reasoning151", 18),
        ["stream151", "context151", "knowledge151", "vector151", "processor151", "reasoning151"],
    ),
    (
        ("stream151 context151 knowledge151 vector151 processor151 reasoning151", 28),
        ["stream151 context151", "knowledge151 vector151", "processor151 reasoning151"],
    ),
    (
        ("context151 knowledge151 vector151 processor151 reasoning151 machine151", 6),
        ["context151", "knowledge151", "vector151", "processor151", "reasoning151", "machine151"],
    ),
    (
        ("context151 knowledge151 vector151 processor151 reasoning151 machine151", 10),
        ["context151", "knowledge151", "vector151", "processor151", "reasoning151", "machine151"],
    ),
    (
        ("context151 knowledge151 vector151 processor151 reasoning151 machine151", 18),
        ["context151", "knowledge151", "vector151", "processor151", "reasoning151", "machine151"],
    ),
    (
        ("context151 knowledge151 vector151 processor151 reasoning151 machine151", 28),
        ["context151 knowledge151", "vector151 processor151", "reasoning151 machine151"],
    ),
    (
        ("knowledge151 vector151 processor151 reasoning151 machine151 learning151", 6),
        ["knowledge151", "vector151", "processor151", "reasoning151", "machine151", "learning151"],
    ),
    (
        ("knowledge151 vector151 processor151 reasoning151 machine151 learning151", 10),
        ["knowledge151", "vector151", "processor151", "reasoning151", "machine151", "learning151"],
    ),
    (
        ("knowledge151 vector151 processor151 reasoning151 machine151 learning151", 18),
        ["knowledge151", "vector151", "processor151", "reasoning151", "machine151", "learning151"],
    ),
    (
        ("knowledge151 vector151 processor151 reasoning151 machine151 learning151", 28),
        ["knowledge151 vector151", "processor151 reasoning151", "machine151 learning151"],
    ),
    (
        ("vector151 processor151 reasoning151 machine151 learning151 model151", 6),
        ["vector151", "processor151", "reasoning151", "machine151", "learning151", "model151"],
    ),
    (
        ("vector151 processor151 reasoning151 machine151 learning151 model151", 10),
        ["vector151", "processor151", "reasoning151", "machine151", "learning151", "model151"],
    ),
    (
        ("vector151 processor151 reasoning151 machine151 learning151 model151", 18),
        ["vector151", "processor151", "reasoning151", "machine151", "learning151", "model151"],
    ),
    (
        ("vector151 processor151 reasoning151 machine151 learning151 model151", 28),
        ["vector151 processor151", "reasoning151 machine151", "learning151 model151"],
    ),
    (
        ("processor151 reasoning151 machine151 learning151 model151 token151", 6),
        ["processor151", "reasoning151", "machine151", "learning151", "model151", "token151"],
    ),
    (
        ("processor151 reasoning151 machine151 learning151 model151 token151", 10),
        ["processor151", "reasoning151", "machine151", "learning151", "model151", "token151"],
    ),
    (
        ("processor151 reasoning151 machine151 learning151 model151 token151", 18),
        ["processor151", "reasoning151", "machine151", "learning151", "model151 token151"],
    ),
    (
        ("processor151 reasoning151 machine151 learning151 model151 token151", 28),
        ["processor151 reasoning151", "machine151 learning151", "model151 token151"],
    ),
    (
        ("reasoning151 machine151 learning151 model151 token151 prompt151", 6),
        ["reasoning151", "machine151", "learning151", "model151", "token151", "prompt151"],
    ),
    (
        ("reasoning151 machine151 learning151 model151 token151 prompt151", 10),
        ["reasoning151", "machine151", "learning151", "model151", "token151", "prompt151"],
    ),
    (
        ("reasoning151 machine151 learning151 model151 token151 prompt151", 18),
        ["reasoning151", "machine151", "learning151", "model151 token151", "prompt151"],
    ),
    (
        ("reasoning151 machine151 learning151 model151 token151 prompt151", 28),
        ["reasoning151 machine151", "learning151 model151", "token151 prompt151"],
    ),
    (
        ("machine151 learning151 model151 token151 prompt151 session151", 6),
        ["machine151", "learning151", "model151", "token151", "prompt151", "session151"],
    ),
    (
        ("machine151 learning151 model151 token151 prompt151 session151", 10),
        ["machine151", "learning151", "model151", "token151", "prompt151", "session151"],
    ),
    (
        ("machine151 learning151 model151 token151 prompt151 session151", 18),
        ["machine151", "learning151", "model151 token151", "prompt151", "session151"],
    ),
    (
        ("machine151 learning151 model151 token151 prompt151 session151", 28),
        ["machine151 learning151", "model151 token151 prompt151", "session151"],
    ),
    (
        ("learning151 model151 token151 prompt151 session151 library151", 6),
        ["learning151", "model151", "token151", "prompt151", "session151", "library151"],
    ),
    (
        ("learning151 model151 token151 prompt151 session151 library151", 10),
        ["learning151", "model151", "token151", "prompt151", "session151", "library151"],
    ),
    (
        ("learning151 model151 token151 prompt151 session151 library151", 18),
        ["learning151", "model151 token151", "prompt151", "session151", "library151"],
    ),
    (
        ("learning151 model151 token151 prompt151 session151 library151", 28),
        ["learning151 model151", "token151 prompt151", "session151 library151"],
    ),
    (
        ("model151 token151 prompt151 session151 library151 service151", 6),
        ["model151", "token151", "prompt151", "session151", "library151", "service151"],
    ),
    (
        ("model151 token151 prompt151 session151 library151 service151", 10),
        ["model151", "token151", "prompt151", "session151", "library151", "service151"],
    ),
    (
        ("model151 token151 prompt151 session151 library151 service151", 18),
        ["model151 token151", "prompt151", "session151", "library151", "service151"],
    ),
    (
        ("model151 token151 prompt151 session151 library151 service151", 28),
        ["model151 token151 prompt151", "session151 library151", "service151"],
    ),
    (
        ("token151 prompt151 session151 library151 service151 gateway151", 6),
        ["token151", "prompt151", "session151", "library151", "service151", "gateway151"],
    ),
    (
        ("token151 prompt151 session151 library151 service151 gateway151", 10),
        ["token151", "prompt151", "session151", "library151", "service151", "gateway151"],
    ),
    (
        ("token151 prompt151 session151 library151 service151 gateway151", 18),
        ["token151 prompt151", "session151", "library151", "service151", "gateway151"],
    ),
    (
        ("token151 prompt151 session151 library151 service151 gateway151", 28),
        ["token151 prompt151", "session151 library151", "service151 gateway151"],
    ),
    (
        ("prompt151 session151 library151 service151 gateway151 storage151", 6),
        ["prompt151", "session151", "library151", "service151", "gateway151", "storage151"],
    ),
    (
        ("prompt151 session151 library151 service151 gateway151 storage151", 10),
        ["prompt151", "session151", "library151", "service151", "gateway151", "storage151"],
    ),
    (
        ("prompt151 session151 library151 service151 gateway151 storage151", 18),
        ["prompt151", "session151", "library151", "service151", "gateway151", "storage151"],
    ),
    (
        ("prompt151 session151 library151 service151 gateway151 storage151", 28),
        ["prompt151 session151", "library151 service151", "gateway151 storage151"],
    ),
    (
        ("session151 library151 service151 gateway151 storage151 network151", 6),
        ["session151", "library151", "service151", "gateway151", "storage151", "network151"],
    ),
    (
        ("session151 library151 service151 gateway151 storage151 network151", 10),
        ["session151", "library151", "service151", "gateway151", "storage151", "network151"],
    ),
    (
        ("session151 library151 service151 gateway151 storage151 network151", 18),
        ["session151", "library151", "service151", "gateway151", "storage151", "network151"],
    ),
    (
        ("session151 library151 service151 gateway151 storage151 network151", 28),
        ["session151 library151", "service151 gateway151", "storage151 network151"],
    ),
    (
        ("library151 service151 gateway151 storage151 network151 latency151", 6),
        ["library151", "service151", "gateway151", "storage151", "network151", "latency151"],
    ),
    (
        ("library151 service151 gateway151 storage151 network151 latency151", 10),
        ["library151", "service151", "gateway151", "storage151", "network151", "latency151"],
    ),
    (
        ("library151 service151 gateway151 storage151 network151 latency151", 18),
        ["library151", "service151", "gateway151", "storage151", "network151", "latency151"],
    ),
    (
        ("library151 service151 gateway151 storage151 network151 latency151", 28),
        ["library151 service151", "gateway151 storage151", "network151 latency151"],
    ),
    (
        ("service151 gateway151 storage151 network151 latency151 buffer151", 6),
        ["service151", "gateway151", "storage151", "network151", "latency151", "buffer151"],
    ),
    (
        ("service151 gateway151 storage151 network151 latency151 buffer151", 10),
        ["service151", "gateway151", "storage151", "network151", "latency151", "buffer151"],
    ),
    (
        ("service151 gateway151 storage151 network151 latency151 buffer151", 18),
        ["service151", "gateway151", "storage151", "network151", "latency151", "buffer151"],
    ),
    (
        ("service151 gateway151 storage151 network151 latency151 buffer151", 28),
        ["service151 gateway151", "storage151 network151", "latency151 buffer151"],
    ),
    (
        ("gateway151 storage151 network151 latency151 buffer151 queue151", 6),
        ["gateway151", "storage151", "network151", "latency151", "buffer151", "queue151"],
    ),
    (
        ("gateway151 storage151 network151 latency151 buffer151 queue151", 10),
        ["gateway151", "storage151", "network151", "latency151", "buffer151", "queue151"],
    ),
    (
        ("gateway151 storage151 network151 latency151 buffer151 queue151", 18),
        ["gateway151", "storage151", "network151", "latency151", "buffer151 queue151"],
    ),
    (
        ("gateway151 storage151 network151 latency151 buffer151 queue151", 28),
        ["gateway151 storage151", "network151 latency151", "buffer151 queue151"],
    ),
    (
        ("storage151 network151 latency151 buffer151 queue151 worker151", 6),
        ["storage151", "network151", "latency151", "buffer151", "queue151", "worker151"],
    ),
    (
        ("storage151 network151 latency151 buffer151 queue151 worker151", 10),
        ["storage151", "network151", "latency151", "buffer151", "queue151", "worker151"],
    ),
    (
        ("storage151 network151 latency151 buffer151 queue151 worker151", 18),
        ["storage151", "network151", "latency151", "buffer151 queue151", "worker151"],
    ),
    (
        ("storage151 network151 latency151 buffer151 queue151 worker151", 28),
        ["storage151 network151", "latency151 buffer151", "queue151 worker151"],
    ),
    (
        ("network151 latency151 buffer151 queue151 worker151 kernel151", 6),
        ["network151", "latency151", "buffer151", "queue151", "worker151", "kernel151"],
    ),
    (
        ("network151 latency151 buffer151 queue151 worker151 kernel151", 10),
        ["network151", "latency151", "buffer151", "queue151", "worker151", "kernel151"],
    ),
    (
        ("network151 latency151 buffer151 queue151 worker151 kernel151", 18),
        ["network151", "latency151", "buffer151 queue151", "worker151", "kernel151"],
    ),
    (
        ("network151 latency151 buffer151 queue151 worker151 kernel151", 28),
        ["network151 latency151", "buffer151 queue151 worker151", "kernel151"],
    ),
    (
        ("latency151 buffer151 queue151 worker151 kernel151 signal151", 6),
        ["latency151", "buffer151", "queue151", "worker151", "kernel151", "signal151"],
    ),
    (
        ("latency151 buffer151 queue151 worker151 kernel151 signal151", 10),
        ["latency151", "buffer151", "queue151", "worker151", "kernel151", "signal151"],
    ),
    (
        ("latency151 buffer151 queue151 worker151 kernel151 signal151", 18),
        ["latency151", "buffer151 queue151", "worker151", "kernel151", "signal151"],
    ),
    (
        ("latency151 buffer151 queue151 worker151 kernel151 signal151", 28),
        ["latency151 buffer151", "queue151 worker151 kernel151", "signal151"],
    ),
    (
        ("buffer151 queue151 worker151 kernel151 signal151 packet151", 6),
        ["buffer151", "queue151", "worker151", "kernel151", "signal151", "packet151"],
    ),
    (
        ("buffer151 queue151 worker151 kernel151 signal151 packet151", 10),
        ["buffer151", "queue151", "worker151", "kernel151", "signal151", "packet151"],
    ),
    (
        ("buffer151 queue151 worker151 kernel151 signal151 packet151", 18),
        ["buffer151 queue151", "worker151", "kernel151", "signal151", "packet151"],
    ),
    (
        ("buffer151 queue151 worker151 kernel151 signal151 packet151", 28),
        ["buffer151 queue151 worker151", "kernel151 signal151", "packet151"],
    ),
    (
        ("queue151 worker151 kernel151 signal151 packet151 router151", 6),
        ["queue151", "worker151", "kernel151", "signal151", "packet151", "router151"],
    ),
    (
        ("queue151 worker151 kernel151 signal151 packet151 router151", 10),
        ["queue151", "worker151", "kernel151", "signal151", "packet151", "router151"],
    ),
    (
        ("queue151 worker151 kernel151 signal151 packet151 router151", 18),
        ["queue151 worker151", "kernel151", "signal151", "packet151", "router151"],
    ),
    (
        ("queue151 worker151 kernel151 signal151 packet151 router151", 28),
        ["queue151 worker151 kernel151", "signal151 packet151", "router151"],
    ),
    (
        ("worker151 kernel151 signal151 packet151 router151 cluster151", 6),
        ["worker151", "kernel151", "signal151", "packet151", "router151", "cluster151"],
    ),
    (
        ("worker151 kernel151 signal151 packet151 router151 cluster151", 10),
        ["worker151", "kernel151", "signal151", "packet151", "router151", "cluster151"],
    ),
    (
        ("worker151 kernel151 signal151 packet151 router151 cluster151", 18),
        ["worker151", "kernel151", "signal151", "packet151", "router151", "cluster151"],
    ),
    (
        ("worker151 kernel151 signal151 packet151 router151 cluster151", 28),
        ["worker151 kernel151", "signal151 packet151", "router151 cluster151"],
    ),
    (
        ("kernel151 signal151 packet151 router151 cluster151 mirror151", 6),
        ["kernel151", "signal151", "packet151", "router151", "cluster151", "mirror151"],
    ),
    (
        ("kernel151 signal151 packet151 router151 cluster151 mirror151", 10),
        ["kernel151", "signal151", "packet151", "router151", "cluster151", "mirror151"],
    ),
    (
        ("kernel151 signal151 packet151 router151 cluster151 mirror151", 18),
        ["kernel151", "signal151", "packet151", "router151", "cluster151", "mirror151"],
    ),
    (
        ("kernel151 signal151 packet151 router151 cluster151 mirror151", 28),
        ["kernel151 signal151", "packet151 router151", "cluster151 mirror151"],
    ),
    (
        ("signal151 packet151 router151 cluster151 mirror151 filter151", 6),
        ["signal151", "packet151", "router151", "cluster151", "mirror151", "filter151"],
    ),
    (
        ("signal151 packet151 router151 cluster151 mirror151 filter151", 10),
        ["signal151", "packet151", "router151", "cluster151", "mirror151", "filter151"],
    ),
    (
        ("signal151 packet151 router151 cluster151 mirror151 filter151", 18),
        ["signal151", "packet151", "router151", "cluster151", "mirror151", "filter151"],
    ),
    (
        ("signal151 packet151 router151 cluster151 mirror151 filter151", 28),
        ["signal151 packet151", "router151 cluster151", "mirror151 filter151"],
    ),
    (
        ("packet151 router151 cluster151 mirror151 filter151 ranking151", 6),
        ["packet151", "router151", "cluster151", "mirror151", "filter151", "ranking151"],
    ),
    (
        ("packet151 router151 cluster151 mirror151 filter151 ranking151", 10),
        ["packet151", "router151", "cluster151", "mirror151", "filter151", "ranking151"],
    ),
    (
        ("packet151 router151 cluster151 mirror151 filter151 ranking151", 18),
        ["packet151", "router151", "cluster151", "mirror151", "filter151", "ranking151"],
    ),
    (
        ("packet151 router151 cluster151 mirror151 filter151 ranking151", 28),
        ["packet151 router151", "cluster151 mirror151", "filter151 ranking151"],
    ),
    (
        ("router151 cluster151 mirror151 filter151 ranking151 encoding151", 6),
        ["router151", "cluster151", "mirror151", "filter151", "ranking151", "encoding151"],
    ),
    (
        ("router151 cluster151 mirror151 filter151 ranking151 encoding151", 10),
        ["router151", "cluster151", "mirror151", "filter151", "ranking151", "encoding151"],
    ),
    (
        ("router151 cluster151 mirror151 filter151 ranking151 encoding151", 18),
        ["router151", "cluster151", "mirror151", "filter151", "ranking151", "encoding151"],
    ),
    (
        ("router151 cluster151 mirror151 filter151 ranking151 encoding151", 28),
        ["router151 cluster151", "mirror151 filter151", "ranking151 encoding151"],
    ),
    (
        ("cluster151 mirror151 filter151 ranking151 encoding151 mapping151", 6),
        ["cluster151", "mirror151", "filter151", "ranking151", "encoding151", "mapping151"],
    ),
    (
        ("cluster151 mirror151 filter151 ranking151 encoding151 mapping151", 10),
        ["cluster151", "mirror151", "filter151", "ranking151", "encoding151", "mapping151"],
    ),
    (
        ("cluster151 mirror151 filter151 ranking151 encoding151 mapping151", 18),
        ["cluster151", "mirror151", "filter151", "ranking151", "encoding151", "mapping151"],
    ),
    (
        ("cluster151 mirror151 filter151 ranking151 encoding151 mapping151", 28),
        ["cluster151 mirror151", "filter151 ranking151", "encoding151 mapping151"],
    ),
    (
        ("mirror151 filter151 ranking151 encoding151 mapping151 record151", 6),
        ["mirror151", "filter151", "ranking151", "encoding151", "mapping151", "record151"],
    ),
    (
        ("mirror151 filter151 ranking151 encoding151 mapping151 record151", 10),
        ["mirror151", "filter151", "ranking151", "encoding151", "mapping151", "record151"],
    ),
    (
        ("mirror151 filter151 ranking151 encoding151 mapping151 record151", 18),
        ["mirror151", "filter151", "ranking151", "encoding151", "mapping151", "record151"],
    ),
    (
        ("mirror151 filter151 ranking151 encoding151 mapping151 record151", 28),
        ["mirror151 filter151", "ranking151 encoding151", "mapping151 record151"],
    ),
    (
        ("filter151 ranking151 encoding151 mapping151 record151 candle151", 6),
        ["filter151", "ranking151", "encoding151", "mapping151", "record151", "candle151"],
    ),
    (
        ("filter151 ranking151 encoding151 mapping151 record151 candle151", 10),
        ["filter151", "ranking151", "encoding151", "mapping151", "record151", "candle151"],
    ),
    (
        ("filter151 ranking151 encoding151 mapping151 record151 candle151", 18),
        ["filter151", "ranking151", "encoding151", "mapping151", "record151", "candle151"],
    ),
    (
        ("filter151 ranking151 encoding151 mapping151 record151 candle151", 28),
        ["filter151 ranking151", "encoding151 mapping151", "record151 candle151"],
    ),
    (
        ("ranking151 encoding151 mapping151 record151 candle151 thread151", 6),
        ["ranking151", "encoding151", "mapping151", "record151", "candle151", "thread151"],
    ),
    (
        ("ranking151 encoding151 mapping151 record151 candle151 thread151", 10),
        ["ranking151", "encoding151", "mapping151", "record151", "candle151", "thread151"],
    ),
    (
        ("ranking151 encoding151 mapping151 record151 candle151 thread151", 18),
        ["ranking151", "encoding151", "mapping151", "record151", "candle151", "thread151"],
    ),
    (
        ("ranking151 encoding151 mapping151 record151 candle151 thread151", 28),
        ["ranking151 encoding151", "mapping151 record151", "candle151 thread151"],
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
