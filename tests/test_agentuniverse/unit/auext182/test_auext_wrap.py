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
        ("round 182: the quick brown fox jumps over the lazy dog", 4),
        ["round", "182:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 182: the quick brown fox jumps over the lazy dog", 8),
        ["round", "182: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 182: the quick brown fox jumps over the lazy dog", 12),
        ["round 182:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 182: the quick brown fox jumps over the lazy dog", 16),
        ["round 182: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 182: the quick brown fox jumps over the lazy dog", 24),
        ["round 182: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 182: the quick brown fox jumps over the lazy dog", 32),
        ["round 182: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 182: agentuniverse is a framework for multi agents", 4),
        ["round", "182:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 182: agentuniverse is a framework for multi agents", 8),
        ["round", "182:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 182: agentuniverse is a framework for multi agents", 12),
        ["round 182:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 182: agentuniverse is a framework for multi agents", 16),
        ["round 182:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 182: agentuniverse is a framework for multi agents", 24),
        ["round 182: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 182: agentuniverse is a framework for multi agents", 32),
        ["round 182: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 182: knowledge stored as vectors enables retrieval", 4),
        ["round", "182:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 182: knowledge stored as vectors enables retrieval", 8),
        ["round", "182:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 182: knowledge stored as vectors enables retrieval", 12),
        ["round 182:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 182: knowledge stored as vectors enables retrieval", 16),
        ["round 182:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 182: knowledge stored as vectors enables retrieval", 24),
        ["round 182: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 182: knowledge stored as vectors enables retrieval", 32),
        ["round 182: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 182: the processor reads the record then stops", 4),
        ["round", "182:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 182: the processor reads the record then stops", 8),
        ["round", "182: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 182: the processor reads the record then stops", 12),
        ["round 182:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 182: the processor reads the record then stops", 16),
        ["round 182: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 182: the processor reads the record then stops", 24),
        ["round 182: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 182: the processor reads the record then stops", 32),
        ["round 182: the processor reads", "the record then stops"],
    ),
    (
        ("round 182: a worker pulls the next task from the queue", 4),
        ["round", "182:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 182: a worker pulls the next task from the queue", 8),
        ["round", "182: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 182: a worker pulls the next task from the queue", 12),
        ["round 182: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 182: a worker pulls the next task from the queue", 16),
        ["round 182: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 182: a worker pulls the next task from the queue", 24),
        ["round 182: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 182: a worker pulls the next task from the queue", 32),
        ["round 182: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 182: signals travel through the network layer", 4),
        ["round", "182:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 182: signals travel through the network layer", 8),
        ["round", "182:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 182: signals travel through the network layer", 12),
        ["round 182:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 182: signals travel through the network layer", 16),
        ["round 182:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 182: signals travel through the network layer", 24),
        ["round 182: signals", "travel through the", "network layer"],
    ),
    (
        ("round 182: signals travel through the network layer", 32),
        ["round 182: signals travel", "through the network layer"],
    ),
    (
        ("round 182: the gateway routes each request by policy", 4),
        ["round", "182:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 182: the gateway routes each request by policy", 8),
        ["round", "182: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 182: the gateway routes each request by policy", 12),
        ["round 182:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 182: the gateway routes each request by policy", 16),
        ["round 182: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 182: the gateway routes each request by policy", 24),
        ["round 182: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 182: the gateway routes each request by policy", 32),
        ["round 182: the gateway routes", "each request by policy"],
    ),
    (
        ("round 182: memory grows until the buffer is full", 4),
        ["round", "182:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 182: memory grows until the buffer is full", 8),
        ["round", "182:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 182: memory grows until the buffer is full", 12),
        ["round 182:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 182: memory grows until the buffer is full", 16),
        ["round 182:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 182: memory grows until the buffer is full", 24), ["round 182: memory grows", "until the buffer is full"]),
    (("round 182: memory grows until the buffer is full", 32), ["round 182: memory grows until", "the buffer is full"]),
    (
        ("round 182: the cluster mirrors every packet twice", 4),
        ["round", "182:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 182: the cluster mirrors every packet twice", 8),
        ["round", "182: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 182: the cluster mirrors every packet twice", 12),
        ["round 182:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 182: the cluster mirrors every packet twice", 16),
        ["round 182: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 182: the cluster mirrors every packet twice", 24),
        ["round 182: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 182: the cluster mirrors every packet twice", 32),
        ["round 182: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 182: ranking uses tokens learned from the corpus", 4),
        ["round", "182:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 182: ranking uses tokens learned from the corpus", 8),
        ["round", "182:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 182: ranking uses tokens learned from the corpus", 12),
        ["round 182:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 182: ranking uses tokens learned from the corpus", 16),
        ["round 182:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 182: ranking uses tokens learned from the corpus", 24),
        ["round 182: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 182: ranking uses tokens learned from the corpus", 32),
        ["round 182: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 182: a long session ends when the candle dies", 4),
        ["round", "182:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 182: a long session ends when the candle dies", 8),
        ["round", "182: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 182: a long session ends when the candle dies", 12),
        ["round 182: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 182: a long session ends when the candle dies", 16),
        ["round 182: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 182: a long session ends when the candle dies", 24),
        ["round 182: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 182: a long session ends when the candle dies", 32),
        ["round 182: a long session ends", "when the candle dies"],
    ),
    (
        ("round 182: encode the prompt then map the result", 4),
        ["round", "182:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 182: encode the prompt then map the result", 8),
        ["round", "182:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 182: encode the prompt then map the result", 12),
        ["round 182:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 182: encode the prompt then map the result", 16),
        ["round 182:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 182: encode the prompt then map the result", 24),
        ["round 182: encode the", "prompt then map the", "result"],
    ),
    (("round 182: encode the prompt then map the result", 32), ["round 182: encode the prompt", "then map the result"]),
    (
        ("round 182: the kernel wakes the worker at dawn", 4),
        ["round", "182:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 182: the kernel wakes the worker at dawn", 8),
        ["round", "182: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 182: the kernel wakes the worker at dawn", 12),
        ["round 182:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 182: the kernel wakes the worker at dawn", 16), ["round 182: the", "kernel wakes the", "worker at dawn"]),
    (("round 182: the kernel wakes the worker at dawn", 24), ["round 182: the kernel", "wakes the worker at dawn"]),
    (("round 182: the kernel wakes the worker at dawn", 32), ["round 182: the kernel wakes the", "worker at dawn"]),
    (
        ("round 182: service latency drops after the patch", 4),
        ["round", "182:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 182: service latency drops after the patch", 8),
        ["round", "182:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 182: service latency drops after the patch", 12),
        ["round 182:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 182: service latency drops after the patch", 16),
        ["round 182:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 182: service latency drops after the patch", 24),
        ["round 182: service", "latency drops after the", "patch"],
    ),
    (("round 182: service latency drops after the patch", 32), ["round 182: service latency drops", "after the patch"]),
    (
        ("round 182: the library caches every vector it sees", 4),
        ["round", "182:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 182: the library caches every vector it sees", 8),
        ["round", "182: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 182: the library caches every vector it sees", 12),
        ["round 182:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 182: the library caches every vector it sees", 16),
        ["round 182: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 182: the library caches every vector it sees", 24),
        ["round 182: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 182: the library caches every vector it sees", 32),
        ["round 182: the library caches", "every vector it sees"],
    ),
    (
        ("round 182: agents argue then the debate resolves", 4),
        ["round", "182:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 182: agents argue then the debate resolves", 8),
        ["round", "182:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 182: agents argue then the debate resolves", 12),
        ["round 182:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 182: agents argue then the debate resolves", 16),
        ["round 182:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 182: agents argue then the debate resolves", 24), ["round 182: agents argue", "then the debate resolves"]),
    (("round 182: agents argue then the debate resolves", 32), ["round 182: agents argue then the", "debate resolves"]),
    (
        ("round 182: the filter keeps only strong matches", 4),
        ["round", "182:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 182: the filter keeps only strong matches", 8),
        ["round", "182: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 182: the filter keeps only strong matches", 12),
        ["round 182:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 182: the filter keeps only strong matches", 16),
        ["round 182: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 182: the filter keeps only strong matches", 24),
        ["round 182: the filter", "keeps only strong", "matches"],
    ),
    (("round 182: the filter keeps only strong matches", 32), ["round 182: the filter keeps only", "strong matches"]),
    (
        ("round 182: the model answers with a short reply", 4),
        ["round", "182:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 182: the model answers with a short reply", 8),
        ["round", "182: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 182: the model answers with a short reply", 12),
        ["round 182:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 182: the model answers with a short reply", 16),
        ["round 182: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 182: the model answers with a short reply", 24),
        ["round 182: the model", "answers with a short", "reply"],
    ),
    (("round 182: the model answers with a short reply", 32), ["round 182: the model answers", "with a short reply"]),
    (
        ("round 182: the recorder stores the reasoning trace", 4),
        ["round", "182:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 182: the recorder stores the reasoning trace", 8),
        ["round", "182: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 182: the recorder stores the reasoning trace", 12),
        ["round 182:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 182: the recorder stores the reasoning trace", 16),
        ["round 182: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 182: the recorder stores the reasoning trace", 24),
        ["round 182: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 182: the recorder stores the reasoning trace", 32),
        ["round 182: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 182: the angel watches the processor run", 4),
        ["round", "182:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 182: the angel watches the processor run", 8),
        ["round", "182: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 182: the angel watches the processor run", 12),
        ["round 182:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 182: the angel watches the processor run", 16),
        ["round 182: the", "angel watches", "the processor", "run"],
    ),
    (("round 182: the angel watches the processor run", 24), ["round 182: the angel", "watches the processor", "run"]),
    (("round 182: the angel watches the processor run", 32), ["round 182: the angel watches the", "processor run"]),
    (
        ("round 182: angle of the vector decides the match", 4),
        ["round", "182:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 182: angle of the vector decides the match", 8),
        ["round", "182:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 182: angle of the vector decides the match", 12),
        ["round 182:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 182: angle of the vector decides the match", 16),
        ["round 182: angle", "of the vector", "decides the", "match"],
    ),
    (("round 182: angle of the vector decides the match", 24), ["round 182: angle of the", "vector decides the match"]),
    (("round 182: angle of the vector decides the match", 32), ["round 182: angle of the vector", "decides the match"]),
    (
        ("round 182: the candle burns twice as long at night", 4),
        ["round", "182:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 182: the candle burns twice as long at night", 8),
        ["round", "182: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 182: the candle burns twice as long at night", 12),
        ["round 182:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 182: the candle burns twice as long at night", 16),
        ["round 182: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 182: the candle burns twice as long at night", 24),
        ["round 182: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 182: the candle burns twice as long at night", 32),
        ["round 182: the candle burns", "twice as long at night"],
    ),
    (
        ("round 182: a mirror of the universe in one line", 4),
        ["round", "182:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 182: a mirror of the universe in one line", 8),
        ["round", "182: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 182: a mirror of the universe in one line", 12),
        ["round 182: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 182: a mirror of the universe in one line", 16),
        ["round 182: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 182: a mirror of the universe in one line", 24), ["round 182: a mirror of", "the universe in one line"]),
    (("round 182: a mirror of the universe in one line", 32), ["round 182: a mirror of the", "universe in one line"]),
    (
        ("round 182: the queue drains before the storm", 4),
        ["round", "182:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 182: the queue drains before the storm", 8),
        ["round", "182: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 182: the queue drains before the storm", 12),
        ["round 182:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 182: the queue drains before the storm", 16), ["round 182: the", "queue drains", "before the storm"]),
    (("round 182: the queue drains before the storm", 24), ["round 182: the queue", "drains before the storm"]),
    (("round 182: the queue drains before the storm", 32), ["round 182: the queue drains", "before the storm"]),
    (
        ("kitten182 sitting182 agent182 angle182 universe182 memory182", 6),
        ["kitten182", "sitting182", "agent182", "angle182", "universe182", "memory182"],
    ),
    (
        ("kitten182 sitting182 agent182 angle182 universe182 memory182", 10),
        ["kitten182", "sitting182", "agent182", "angle182", "universe182", "memory182"],
    ),
    (
        ("kitten182 sitting182 agent182 angle182 universe182 memory182", 18),
        ["kitten182", "sitting182", "agent182 angle182", "universe182", "memory182"],
    ),
    (
        ("kitten182 sitting182 agent182 angle182 universe182 memory182", 28),
        ["kitten182 sitting182", "agent182 angle182", "universe182 memory182"],
    ),
    (
        ("sitting182 agent182 angle182 universe182 memory182 stream182", 6),
        ["sitting182", "agent182", "angle182", "universe182", "memory182", "stream182"],
    ),
    (
        ("sitting182 agent182 angle182 universe182 memory182 stream182", 10),
        ["sitting182", "agent182", "angle182", "universe182", "memory182", "stream182"],
    ),
    (
        ("sitting182 agent182 angle182 universe182 memory182 stream182", 18),
        ["sitting182", "agent182 angle182", "universe182", "memory182", "stream182"],
    ),
    (
        ("sitting182 agent182 angle182 universe182 memory182 stream182", 28),
        ["sitting182 agent182 angle182", "universe182 memory182", "stream182"],
    ),
    (
        ("agent182 angle182 universe182 memory182 stream182 context182", 6),
        ["agent182", "angle182", "universe182", "memory182", "stream182", "context182"],
    ),
    (
        ("agent182 angle182 universe182 memory182 stream182 context182", 10),
        ["agent182", "angle182", "universe182", "memory182", "stream182", "context182"],
    ),
    (
        ("agent182 angle182 universe182 memory182 stream182 context182", 18),
        ["agent182 angle182", "universe182", "memory182", "stream182", "context182"],
    ),
    (
        ("agent182 angle182 universe182 memory182 stream182 context182", 28),
        ["agent182 angle182", "universe182 memory182", "stream182 context182"],
    ),
    (
        ("angle182 universe182 memory182 stream182 context182 knowledge182", 6),
        ["angle182", "universe182", "memory182", "stream182", "context182", "knowledge182"],
    ),
    (
        ("angle182 universe182 memory182 stream182 context182 knowledge182", 10),
        ["angle182", "universe182", "memory182", "stream182", "context182", "knowledge182"],
    ),
    (
        ("angle182 universe182 memory182 stream182 context182 knowledge182", 18),
        ["angle182", "universe182", "memory182", "stream182", "context182", "knowledge182"],
    ),
    (
        ("angle182 universe182 memory182 stream182 context182 knowledge182", 28),
        ["angle182 universe182", "memory182 stream182", "context182 knowledge182"],
    ),
    (
        ("universe182 memory182 stream182 context182 knowledge182 vector182", 6),
        ["universe182", "memory182", "stream182", "context182", "knowledge182", "vector182"],
    ),
    (
        ("universe182 memory182 stream182 context182 knowledge182 vector182", 10),
        ["universe182", "memory182", "stream182", "context182", "knowledge182", "vector182"],
    ),
    (
        ("universe182 memory182 stream182 context182 knowledge182 vector182", 18),
        ["universe182", "memory182", "stream182", "context182", "knowledge182", "vector182"],
    ),
    (
        ("universe182 memory182 stream182 context182 knowledge182 vector182", 28),
        ["universe182 memory182", "stream182 context182", "knowledge182 vector182"],
    ),
    (
        ("memory182 stream182 context182 knowledge182 vector182 processor182", 6),
        ["memory182", "stream182", "context182", "knowledge182", "vector182", "processor182"],
    ),
    (
        ("memory182 stream182 context182 knowledge182 vector182 processor182", 10),
        ["memory182", "stream182", "context182", "knowledge182", "vector182", "processor182"],
    ),
    (
        ("memory182 stream182 context182 knowledge182 vector182 processor182", 18),
        ["memory182", "stream182", "context182", "knowledge182", "vector182", "processor182"],
    ),
    (
        ("memory182 stream182 context182 knowledge182 vector182 processor182", 28),
        ["memory182 stream182", "context182 knowledge182", "vector182 processor182"],
    ),
    (
        ("stream182 context182 knowledge182 vector182 processor182 reasoning182", 6),
        ["stream182", "context182", "knowledge182", "vector182", "processor182", "reasoning182"],
    ),
    (
        ("stream182 context182 knowledge182 vector182 processor182 reasoning182", 10),
        ["stream182", "context182", "knowledge182", "vector182", "processor182", "reasoning182"],
    ),
    (
        ("stream182 context182 knowledge182 vector182 processor182 reasoning182", 18),
        ["stream182", "context182", "knowledge182", "vector182", "processor182", "reasoning182"],
    ),
    (
        ("stream182 context182 knowledge182 vector182 processor182 reasoning182", 28),
        ["stream182 context182", "knowledge182 vector182", "processor182 reasoning182"],
    ),
    (
        ("context182 knowledge182 vector182 processor182 reasoning182 machine182", 6),
        ["context182", "knowledge182", "vector182", "processor182", "reasoning182", "machine182"],
    ),
    (
        ("context182 knowledge182 vector182 processor182 reasoning182 machine182", 10),
        ["context182", "knowledge182", "vector182", "processor182", "reasoning182", "machine182"],
    ),
    (
        ("context182 knowledge182 vector182 processor182 reasoning182 machine182", 18),
        ["context182", "knowledge182", "vector182", "processor182", "reasoning182", "machine182"],
    ),
    (
        ("context182 knowledge182 vector182 processor182 reasoning182 machine182", 28),
        ["context182 knowledge182", "vector182 processor182", "reasoning182 machine182"],
    ),
    (
        ("knowledge182 vector182 processor182 reasoning182 machine182 learning182", 6),
        ["knowledge182", "vector182", "processor182", "reasoning182", "machine182", "learning182"],
    ),
    (
        ("knowledge182 vector182 processor182 reasoning182 machine182 learning182", 10),
        ["knowledge182", "vector182", "processor182", "reasoning182", "machine182", "learning182"],
    ),
    (
        ("knowledge182 vector182 processor182 reasoning182 machine182 learning182", 18),
        ["knowledge182", "vector182", "processor182", "reasoning182", "machine182", "learning182"],
    ),
    (
        ("knowledge182 vector182 processor182 reasoning182 machine182 learning182", 28),
        ["knowledge182 vector182", "processor182 reasoning182", "machine182 learning182"],
    ),
    (
        ("vector182 processor182 reasoning182 machine182 learning182 model182", 6),
        ["vector182", "processor182", "reasoning182", "machine182", "learning182", "model182"],
    ),
    (
        ("vector182 processor182 reasoning182 machine182 learning182 model182", 10),
        ["vector182", "processor182", "reasoning182", "machine182", "learning182", "model182"],
    ),
    (
        ("vector182 processor182 reasoning182 machine182 learning182 model182", 18),
        ["vector182", "processor182", "reasoning182", "machine182", "learning182", "model182"],
    ),
    (
        ("vector182 processor182 reasoning182 machine182 learning182 model182", 28),
        ["vector182 processor182", "reasoning182 machine182", "learning182 model182"],
    ),
    (
        ("processor182 reasoning182 machine182 learning182 model182 token182", 6),
        ["processor182", "reasoning182", "machine182", "learning182", "model182", "token182"],
    ),
    (
        ("processor182 reasoning182 machine182 learning182 model182 token182", 10),
        ["processor182", "reasoning182", "machine182", "learning182", "model182", "token182"],
    ),
    (
        ("processor182 reasoning182 machine182 learning182 model182 token182", 18),
        ["processor182", "reasoning182", "machine182", "learning182", "model182 token182"],
    ),
    (
        ("processor182 reasoning182 machine182 learning182 model182 token182", 28),
        ["processor182 reasoning182", "machine182 learning182", "model182 token182"],
    ),
    (
        ("reasoning182 machine182 learning182 model182 token182 prompt182", 6),
        ["reasoning182", "machine182", "learning182", "model182", "token182", "prompt182"],
    ),
    (
        ("reasoning182 machine182 learning182 model182 token182 prompt182", 10),
        ["reasoning182", "machine182", "learning182", "model182", "token182", "prompt182"],
    ),
    (
        ("reasoning182 machine182 learning182 model182 token182 prompt182", 18),
        ["reasoning182", "machine182", "learning182", "model182 token182", "prompt182"],
    ),
    (
        ("reasoning182 machine182 learning182 model182 token182 prompt182", 28),
        ["reasoning182 machine182", "learning182 model182", "token182 prompt182"],
    ),
    (
        ("machine182 learning182 model182 token182 prompt182 session182", 6),
        ["machine182", "learning182", "model182", "token182", "prompt182", "session182"],
    ),
    (
        ("machine182 learning182 model182 token182 prompt182 session182", 10),
        ["machine182", "learning182", "model182", "token182", "prompt182", "session182"],
    ),
    (
        ("machine182 learning182 model182 token182 prompt182 session182", 18),
        ["machine182", "learning182", "model182 token182", "prompt182", "session182"],
    ),
    (
        ("machine182 learning182 model182 token182 prompt182 session182", 28),
        ["machine182 learning182", "model182 token182 prompt182", "session182"],
    ),
    (
        ("learning182 model182 token182 prompt182 session182 library182", 6),
        ["learning182", "model182", "token182", "prompt182", "session182", "library182"],
    ),
    (
        ("learning182 model182 token182 prompt182 session182 library182", 10),
        ["learning182", "model182", "token182", "prompt182", "session182", "library182"],
    ),
    (
        ("learning182 model182 token182 prompt182 session182 library182", 18),
        ["learning182", "model182 token182", "prompt182", "session182", "library182"],
    ),
    (
        ("learning182 model182 token182 prompt182 session182 library182", 28),
        ["learning182 model182", "token182 prompt182", "session182 library182"],
    ),
    (
        ("model182 token182 prompt182 session182 library182 service182", 6),
        ["model182", "token182", "prompt182", "session182", "library182", "service182"],
    ),
    (
        ("model182 token182 prompt182 session182 library182 service182", 10),
        ["model182", "token182", "prompt182", "session182", "library182", "service182"],
    ),
    (
        ("model182 token182 prompt182 session182 library182 service182", 18),
        ["model182 token182", "prompt182", "session182", "library182", "service182"],
    ),
    (
        ("model182 token182 prompt182 session182 library182 service182", 28),
        ["model182 token182 prompt182", "session182 library182", "service182"],
    ),
    (
        ("token182 prompt182 session182 library182 service182 gateway182", 6),
        ["token182", "prompt182", "session182", "library182", "service182", "gateway182"],
    ),
    (
        ("token182 prompt182 session182 library182 service182 gateway182", 10),
        ["token182", "prompt182", "session182", "library182", "service182", "gateway182"],
    ),
    (
        ("token182 prompt182 session182 library182 service182 gateway182", 18),
        ["token182 prompt182", "session182", "library182", "service182", "gateway182"],
    ),
    (
        ("token182 prompt182 session182 library182 service182 gateway182", 28),
        ["token182 prompt182", "session182 library182", "service182 gateway182"],
    ),
    (
        ("prompt182 session182 library182 service182 gateway182 storage182", 6),
        ["prompt182", "session182", "library182", "service182", "gateway182", "storage182"],
    ),
    (
        ("prompt182 session182 library182 service182 gateway182 storage182", 10),
        ["prompt182", "session182", "library182", "service182", "gateway182", "storage182"],
    ),
    (
        ("prompt182 session182 library182 service182 gateway182 storage182", 18),
        ["prompt182", "session182", "library182", "service182", "gateway182", "storage182"],
    ),
    (
        ("prompt182 session182 library182 service182 gateway182 storage182", 28),
        ["prompt182 session182", "library182 service182", "gateway182 storage182"],
    ),
    (
        ("session182 library182 service182 gateway182 storage182 network182", 6),
        ["session182", "library182", "service182", "gateway182", "storage182", "network182"],
    ),
    (
        ("session182 library182 service182 gateway182 storage182 network182", 10),
        ["session182", "library182", "service182", "gateway182", "storage182", "network182"],
    ),
    (
        ("session182 library182 service182 gateway182 storage182 network182", 18),
        ["session182", "library182", "service182", "gateway182", "storage182", "network182"],
    ),
    (
        ("session182 library182 service182 gateway182 storage182 network182", 28),
        ["session182 library182", "service182 gateway182", "storage182 network182"],
    ),
    (
        ("library182 service182 gateway182 storage182 network182 latency182", 6),
        ["library182", "service182", "gateway182", "storage182", "network182", "latency182"],
    ),
    (
        ("library182 service182 gateway182 storage182 network182 latency182", 10),
        ["library182", "service182", "gateway182", "storage182", "network182", "latency182"],
    ),
    (
        ("library182 service182 gateway182 storage182 network182 latency182", 18),
        ["library182", "service182", "gateway182", "storage182", "network182", "latency182"],
    ),
    (
        ("library182 service182 gateway182 storage182 network182 latency182", 28),
        ["library182 service182", "gateway182 storage182", "network182 latency182"],
    ),
    (
        ("service182 gateway182 storage182 network182 latency182 buffer182", 6),
        ["service182", "gateway182", "storage182", "network182", "latency182", "buffer182"],
    ),
    (
        ("service182 gateway182 storage182 network182 latency182 buffer182", 10),
        ["service182", "gateway182", "storage182", "network182", "latency182", "buffer182"],
    ),
    (
        ("service182 gateway182 storage182 network182 latency182 buffer182", 18),
        ["service182", "gateway182", "storage182", "network182", "latency182", "buffer182"],
    ),
    (
        ("service182 gateway182 storage182 network182 latency182 buffer182", 28),
        ["service182 gateway182", "storage182 network182", "latency182 buffer182"],
    ),
    (
        ("gateway182 storage182 network182 latency182 buffer182 queue182", 6),
        ["gateway182", "storage182", "network182", "latency182", "buffer182", "queue182"],
    ),
    (
        ("gateway182 storage182 network182 latency182 buffer182 queue182", 10),
        ["gateway182", "storage182", "network182", "latency182", "buffer182", "queue182"],
    ),
    (
        ("gateway182 storage182 network182 latency182 buffer182 queue182", 18),
        ["gateway182", "storage182", "network182", "latency182", "buffer182 queue182"],
    ),
    (
        ("gateway182 storage182 network182 latency182 buffer182 queue182", 28),
        ["gateway182 storage182", "network182 latency182", "buffer182 queue182"],
    ),
    (
        ("storage182 network182 latency182 buffer182 queue182 worker182", 6),
        ["storage182", "network182", "latency182", "buffer182", "queue182", "worker182"],
    ),
    (
        ("storage182 network182 latency182 buffer182 queue182 worker182", 10),
        ["storage182", "network182", "latency182", "buffer182", "queue182", "worker182"],
    ),
    (
        ("storage182 network182 latency182 buffer182 queue182 worker182", 18),
        ["storage182", "network182", "latency182", "buffer182 queue182", "worker182"],
    ),
    (
        ("storage182 network182 latency182 buffer182 queue182 worker182", 28),
        ["storage182 network182", "latency182 buffer182", "queue182 worker182"],
    ),
    (
        ("network182 latency182 buffer182 queue182 worker182 kernel182", 6),
        ["network182", "latency182", "buffer182", "queue182", "worker182", "kernel182"],
    ),
    (
        ("network182 latency182 buffer182 queue182 worker182 kernel182", 10),
        ["network182", "latency182", "buffer182", "queue182", "worker182", "kernel182"],
    ),
    (
        ("network182 latency182 buffer182 queue182 worker182 kernel182", 18),
        ["network182", "latency182", "buffer182 queue182", "worker182", "kernel182"],
    ),
    (
        ("network182 latency182 buffer182 queue182 worker182 kernel182", 28),
        ["network182 latency182", "buffer182 queue182 worker182", "kernel182"],
    ),
    (
        ("latency182 buffer182 queue182 worker182 kernel182 signal182", 6),
        ["latency182", "buffer182", "queue182", "worker182", "kernel182", "signal182"],
    ),
    (
        ("latency182 buffer182 queue182 worker182 kernel182 signal182", 10),
        ["latency182", "buffer182", "queue182", "worker182", "kernel182", "signal182"],
    ),
    (
        ("latency182 buffer182 queue182 worker182 kernel182 signal182", 18),
        ["latency182", "buffer182 queue182", "worker182", "kernel182", "signal182"],
    ),
    (
        ("latency182 buffer182 queue182 worker182 kernel182 signal182", 28),
        ["latency182 buffer182", "queue182 worker182 kernel182", "signal182"],
    ),
    (
        ("buffer182 queue182 worker182 kernel182 signal182 packet182", 6),
        ["buffer182", "queue182", "worker182", "kernel182", "signal182", "packet182"],
    ),
    (
        ("buffer182 queue182 worker182 kernel182 signal182 packet182", 10),
        ["buffer182", "queue182", "worker182", "kernel182", "signal182", "packet182"],
    ),
    (
        ("buffer182 queue182 worker182 kernel182 signal182 packet182", 18),
        ["buffer182 queue182", "worker182", "kernel182", "signal182", "packet182"],
    ),
    (
        ("buffer182 queue182 worker182 kernel182 signal182 packet182", 28),
        ["buffer182 queue182 worker182", "kernel182 signal182", "packet182"],
    ),
    (
        ("queue182 worker182 kernel182 signal182 packet182 router182", 6),
        ["queue182", "worker182", "kernel182", "signal182", "packet182", "router182"],
    ),
    (
        ("queue182 worker182 kernel182 signal182 packet182 router182", 10),
        ["queue182", "worker182", "kernel182", "signal182", "packet182", "router182"],
    ),
    (
        ("queue182 worker182 kernel182 signal182 packet182 router182", 18),
        ["queue182 worker182", "kernel182", "signal182", "packet182", "router182"],
    ),
    (
        ("queue182 worker182 kernel182 signal182 packet182 router182", 28),
        ["queue182 worker182 kernel182", "signal182 packet182", "router182"],
    ),
    (
        ("worker182 kernel182 signal182 packet182 router182 cluster182", 6),
        ["worker182", "kernel182", "signal182", "packet182", "router182", "cluster182"],
    ),
    (
        ("worker182 kernel182 signal182 packet182 router182 cluster182", 10),
        ["worker182", "kernel182", "signal182", "packet182", "router182", "cluster182"],
    ),
    (
        ("worker182 kernel182 signal182 packet182 router182 cluster182", 18),
        ["worker182", "kernel182", "signal182", "packet182", "router182", "cluster182"],
    ),
    (
        ("worker182 kernel182 signal182 packet182 router182 cluster182", 28),
        ["worker182 kernel182", "signal182 packet182", "router182 cluster182"],
    ),
    (
        ("kernel182 signal182 packet182 router182 cluster182 mirror182", 6),
        ["kernel182", "signal182", "packet182", "router182", "cluster182", "mirror182"],
    ),
    (
        ("kernel182 signal182 packet182 router182 cluster182 mirror182", 10),
        ["kernel182", "signal182", "packet182", "router182", "cluster182", "mirror182"],
    ),
    (
        ("kernel182 signal182 packet182 router182 cluster182 mirror182", 18),
        ["kernel182", "signal182", "packet182", "router182", "cluster182", "mirror182"],
    ),
    (
        ("kernel182 signal182 packet182 router182 cluster182 mirror182", 28),
        ["kernel182 signal182", "packet182 router182", "cluster182 mirror182"],
    ),
    (
        ("signal182 packet182 router182 cluster182 mirror182 filter182", 6),
        ["signal182", "packet182", "router182", "cluster182", "mirror182", "filter182"],
    ),
    (
        ("signal182 packet182 router182 cluster182 mirror182 filter182", 10),
        ["signal182", "packet182", "router182", "cluster182", "mirror182", "filter182"],
    ),
    (
        ("signal182 packet182 router182 cluster182 mirror182 filter182", 18),
        ["signal182", "packet182", "router182", "cluster182", "mirror182", "filter182"],
    ),
    (
        ("signal182 packet182 router182 cluster182 mirror182 filter182", 28),
        ["signal182 packet182", "router182 cluster182", "mirror182 filter182"],
    ),
    (
        ("packet182 router182 cluster182 mirror182 filter182 ranking182", 6),
        ["packet182", "router182", "cluster182", "mirror182", "filter182", "ranking182"],
    ),
    (
        ("packet182 router182 cluster182 mirror182 filter182 ranking182", 10),
        ["packet182", "router182", "cluster182", "mirror182", "filter182", "ranking182"],
    ),
    (
        ("packet182 router182 cluster182 mirror182 filter182 ranking182", 18),
        ["packet182", "router182", "cluster182", "mirror182", "filter182", "ranking182"],
    ),
    (
        ("packet182 router182 cluster182 mirror182 filter182 ranking182", 28),
        ["packet182 router182", "cluster182 mirror182", "filter182 ranking182"],
    ),
    (
        ("router182 cluster182 mirror182 filter182 ranking182 encoding182", 6),
        ["router182", "cluster182", "mirror182", "filter182", "ranking182", "encoding182"],
    ),
    (
        ("router182 cluster182 mirror182 filter182 ranking182 encoding182", 10),
        ["router182", "cluster182", "mirror182", "filter182", "ranking182", "encoding182"],
    ),
    (
        ("router182 cluster182 mirror182 filter182 ranking182 encoding182", 18),
        ["router182", "cluster182", "mirror182", "filter182", "ranking182", "encoding182"],
    ),
    (
        ("router182 cluster182 mirror182 filter182 ranking182 encoding182", 28),
        ["router182 cluster182", "mirror182 filter182", "ranking182 encoding182"],
    ),
    (
        ("cluster182 mirror182 filter182 ranking182 encoding182 mapping182", 6),
        ["cluster182", "mirror182", "filter182", "ranking182", "encoding182", "mapping182"],
    ),
    (
        ("cluster182 mirror182 filter182 ranking182 encoding182 mapping182", 10),
        ["cluster182", "mirror182", "filter182", "ranking182", "encoding182", "mapping182"],
    ),
    (
        ("cluster182 mirror182 filter182 ranking182 encoding182 mapping182", 18),
        ["cluster182", "mirror182", "filter182", "ranking182", "encoding182", "mapping182"],
    ),
    (
        ("cluster182 mirror182 filter182 ranking182 encoding182 mapping182", 28),
        ["cluster182 mirror182", "filter182 ranking182", "encoding182 mapping182"],
    ),
    (
        ("mirror182 filter182 ranking182 encoding182 mapping182 record182", 6),
        ["mirror182", "filter182", "ranking182", "encoding182", "mapping182", "record182"],
    ),
    (
        ("mirror182 filter182 ranking182 encoding182 mapping182 record182", 10),
        ["mirror182", "filter182", "ranking182", "encoding182", "mapping182", "record182"],
    ),
    (
        ("mirror182 filter182 ranking182 encoding182 mapping182 record182", 18),
        ["mirror182", "filter182", "ranking182", "encoding182", "mapping182", "record182"],
    ),
    (
        ("mirror182 filter182 ranking182 encoding182 mapping182 record182", 28),
        ["mirror182 filter182", "ranking182 encoding182", "mapping182 record182"],
    ),
    (
        ("filter182 ranking182 encoding182 mapping182 record182 candle182", 6),
        ["filter182", "ranking182", "encoding182", "mapping182", "record182", "candle182"],
    ),
    (
        ("filter182 ranking182 encoding182 mapping182 record182 candle182", 10),
        ["filter182", "ranking182", "encoding182", "mapping182", "record182", "candle182"],
    ),
    (
        ("filter182 ranking182 encoding182 mapping182 record182 candle182", 18),
        ["filter182", "ranking182", "encoding182", "mapping182", "record182", "candle182"],
    ),
    (
        ("filter182 ranking182 encoding182 mapping182 record182 candle182", 28),
        ["filter182 ranking182", "encoding182 mapping182", "record182 candle182"],
    ),
    (
        ("ranking182 encoding182 mapping182 record182 candle182 thread182", 6),
        ["ranking182", "encoding182", "mapping182", "record182", "candle182", "thread182"],
    ),
    (
        ("ranking182 encoding182 mapping182 record182 candle182 thread182", 10),
        ["ranking182", "encoding182", "mapping182", "record182", "candle182", "thread182"],
    ),
    (
        ("ranking182 encoding182 mapping182 record182 candle182 thread182", 18),
        ["ranking182", "encoding182", "mapping182", "record182", "candle182", "thread182"],
    ),
    (
        ("ranking182 encoding182 mapping182 record182 candle182 thread182", 28),
        ["ranking182 encoding182", "mapping182 record182", "candle182 thread182"],
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
