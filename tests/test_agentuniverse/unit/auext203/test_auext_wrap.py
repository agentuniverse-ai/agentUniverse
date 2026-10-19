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
        ("round 203: the quick brown fox jumps over the lazy dog", 4),
        ["round", "203:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 203: the quick brown fox jumps over the lazy dog", 8),
        ["round", "203: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 203: the quick brown fox jumps over the lazy dog", 12),
        ["round 203:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 203: the quick brown fox jumps over the lazy dog", 16),
        ["round 203: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 203: the quick brown fox jumps over the lazy dog", 24),
        ["round 203: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 203: the quick brown fox jumps over the lazy dog", 32),
        ["round 203: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 203: agentuniverse is a framework for multi agents", 4),
        ["round", "203:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 203: agentuniverse is a framework for multi agents", 8),
        ["round", "203:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 203: agentuniverse is a framework for multi agents", 12),
        ["round 203:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 203: agentuniverse is a framework for multi agents", 16),
        ["round 203:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 203: agentuniverse is a framework for multi agents", 24),
        ["round 203: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 203: agentuniverse is a framework for multi agents", 32),
        ["round 203: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 203: knowledge stored as vectors enables retrieval", 4),
        ["round", "203:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 203: knowledge stored as vectors enables retrieval", 8),
        ["round", "203:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 203: knowledge stored as vectors enables retrieval", 12),
        ["round 203:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 203: knowledge stored as vectors enables retrieval", 16),
        ["round 203:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 203: knowledge stored as vectors enables retrieval", 24),
        ["round 203: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 203: knowledge stored as vectors enables retrieval", 32),
        ["round 203: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 203: the processor reads the record then stops", 4),
        ["round", "203:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 203: the processor reads the record then stops", 8),
        ["round", "203: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 203: the processor reads the record then stops", 12),
        ["round 203:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 203: the processor reads the record then stops", 16),
        ["round 203: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 203: the processor reads the record then stops", 24),
        ["round 203: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 203: the processor reads the record then stops", 32),
        ["round 203: the processor reads", "the record then stops"],
    ),
    (
        ("round 203: a worker pulls the next task from the queue", 4),
        ["round", "203:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 203: a worker pulls the next task from the queue", 8),
        ["round", "203: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 203: a worker pulls the next task from the queue", 12),
        ["round 203: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 203: a worker pulls the next task from the queue", 16),
        ["round 203: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 203: a worker pulls the next task from the queue", 24),
        ["round 203: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 203: a worker pulls the next task from the queue", 32),
        ["round 203: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 203: signals travel through the network layer", 4),
        ["round", "203:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 203: signals travel through the network layer", 8),
        ["round", "203:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 203: signals travel through the network layer", 12),
        ["round 203:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 203: signals travel through the network layer", 16),
        ["round 203:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 203: signals travel through the network layer", 24),
        ["round 203: signals", "travel through the", "network layer"],
    ),
    (
        ("round 203: signals travel through the network layer", 32),
        ["round 203: signals travel", "through the network layer"],
    ),
    (
        ("round 203: the gateway routes each request by policy", 4),
        ["round", "203:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 203: the gateway routes each request by policy", 8),
        ["round", "203: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 203: the gateway routes each request by policy", 12),
        ["round 203:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 203: the gateway routes each request by policy", 16),
        ["round 203: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 203: the gateway routes each request by policy", 24),
        ["round 203: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 203: the gateway routes each request by policy", 32),
        ["round 203: the gateway routes", "each request by policy"],
    ),
    (
        ("round 203: memory grows until the buffer is full", 4),
        ["round", "203:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 203: memory grows until the buffer is full", 8),
        ["round", "203:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 203: memory grows until the buffer is full", 12),
        ["round 203:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 203: memory grows until the buffer is full", 16),
        ["round 203:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 203: memory grows until the buffer is full", 24), ["round 203: memory grows", "until the buffer is full"]),
    (("round 203: memory grows until the buffer is full", 32), ["round 203: memory grows until", "the buffer is full"]),
    (
        ("round 203: the cluster mirrors every packet twice", 4),
        ["round", "203:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 203: the cluster mirrors every packet twice", 8),
        ["round", "203: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 203: the cluster mirrors every packet twice", 12),
        ["round 203:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 203: the cluster mirrors every packet twice", 16),
        ["round 203: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 203: the cluster mirrors every packet twice", 24),
        ["round 203: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 203: the cluster mirrors every packet twice", 32),
        ["round 203: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 203: ranking uses tokens learned from the corpus", 4),
        ["round", "203:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 203: ranking uses tokens learned from the corpus", 8),
        ["round", "203:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 203: ranking uses tokens learned from the corpus", 12),
        ["round 203:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 203: ranking uses tokens learned from the corpus", 16),
        ["round 203:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 203: ranking uses tokens learned from the corpus", 24),
        ["round 203: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 203: ranking uses tokens learned from the corpus", 32),
        ["round 203: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 203: a long session ends when the candle dies", 4),
        ["round", "203:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 203: a long session ends when the candle dies", 8),
        ["round", "203: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 203: a long session ends when the candle dies", 12),
        ["round 203: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 203: a long session ends when the candle dies", 16),
        ["round 203: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 203: a long session ends when the candle dies", 24),
        ["round 203: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 203: a long session ends when the candle dies", 32),
        ["round 203: a long session ends", "when the candle dies"],
    ),
    (
        ("round 203: encode the prompt then map the result", 4),
        ["round", "203:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 203: encode the prompt then map the result", 8),
        ["round", "203:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 203: encode the prompt then map the result", 12),
        ["round 203:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 203: encode the prompt then map the result", 16),
        ["round 203:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 203: encode the prompt then map the result", 24),
        ["round 203: encode the", "prompt then map the", "result"],
    ),
    (("round 203: encode the prompt then map the result", 32), ["round 203: encode the prompt", "then map the result"]),
    (
        ("round 203: the kernel wakes the worker at dawn", 4),
        ["round", "203:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 203: the kernel wakes the worker at dawn", 8),
        ["round", "203: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 203: the kernel wakes the worker at dawn", 12),
        ["round 203:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 203: the kernel wakes the worker at dawn", 16), ["round 203: the", "kernel wakes the", "worker at dawn"]),
    (("round 203: the kernel wakes the worker at dawn", 24), ["round 203: the kernel", "wakes the worker at dawn"]),
    (("round 203: the kernel wakes the worker at dawn", 32), ["round 203: the kernel wakes the", "worker at dawn"]),
    (
        ("round 203: service latency drops after the patch", 4),
        ["round", "203:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 203: service latency drops after the patch", 8),
        ["round", "203:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 203: service latency drops after the patch", 12),
        ["round 203:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 203: service latency drops after the patch", 16),
        ["round 203:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 203: service latency drops after the patch", 24),
        ["round 203: service", "latency drops after the", "patch"],
    ),
    (("round 203: service latency drops after the patch", 32), ["round 203: service latency drops", "after the patch"]),
    (
        ("round 203: the library caches every vector it sees", 4),
        ["round", "203:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 203: the library caches every vector it sees", 8),
        ["round", "203: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 203: the library caches every vector it sees", 12),
        ["round 203:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 203: the library caches every vector it sees", 16),
        ["round 203: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 203: the library caches every vector it sees", 24),
        ["round 203: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 203: the library caches every vector it sees", 32),
        ["round 203: the library caches", "every vector it sees"],
    ),
    (
        ("round 203: agents argue then the debate resolves", 4),
        ["round", "203:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 203: agents argue then the debate resolves", 8),
        ["round", "203:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 203: agents argue then the debate resolves", 12),
        ["round 203:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 203: agents argue then the debate resolves", 16),
        ["round 203:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 203: agents argue then the debate resolves", 24), ["round 203: agents argue", "then the debate resolves"]),
    (("round 203: agents argue then the debate resolves", 32), ["round 203: agents argue then the", "debate resolves"]),
    (
        ("round 203: the filter keeps only strong matches", 4),
        ["round", "203:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 203: the filter keeps only strong matches", 8),
        ["round", "203: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 203: the filter keeps only strong matches", 12),
        ["round 203:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 203: the filter keeps only strong matches", 16),
        ["round 203: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 203: the filter keeps only strong matches", 24),
        ["round 203: the filter", "keeps only strong", "matches"],
    ),
    (("round 203: the filter keeps only strong matches", 32), ["round 203: the filter keeps only", "strong matches"]),
    (
        ("round 203: the model answers with a short reply", 4),
        ["round", "203:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 203: the model answers with a short reply", 8),
        ["round", "203: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 203: the model answers with a short reply", 12),
        ["round 203:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 203: the model answers with a short reply", 16),
        ["round 203: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 203: the model answers with a short reply", 24),
        ["round 203: the model", "answers with a short", "reply"],
    ),
    (("round 203: the model answers with a short reply", 32), ["round 203: the model answers", "with a short reply"]),
    (
        ("round 203: the recorder stores the reasoning trace", 4),
        ["round", "203:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 203: the recorder stores the reasoning trace", 8),
        ["round", "203: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 203: the recorder stores the reasoning trace", 12),
        ["round 203:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 203: the recorder stores the reasoning trace", 16),
        ["round 203: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 203: the recorder stores the reasoning trace", 24),
        ["round 203: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 203: the recorder stores the reasoning trace", 32),
        ["round 203: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 203: the angel watches the processor run", 4),
        ["round", "203:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 203: the angel watches the processor run", 8),
        ["round", "203: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 203: the angel watches the processor run", 12),
        ["round 203:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 203: the angel watches the processor run", 16),
        ["round 203: the", "angel watches", "the processor", "run"],
    ),
    (("round 203: the angel watches the processor run", 24), ["round 203: the angel", "watches the processor", "run"]),
    (("round 203: the angel watches the processor run", 32), ["round 203: the angel watches the", "processor run"]),
    (
        ("round 203: angle of the vector decides the match", 4),
        ["round", "203:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 203: angle of the vector decides the match", 8),
        ["round", "203:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 203: angle of the vector decides the match", 12),
        ["round 203:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 203: angle of the vector decides the match", 16),
        ["round 203: angle", "of the vector", "decides the", "match"],
    ),
    (("round 203: angle of the vector decides the match", 24), ["round 203: angle of the", "vector decides the match"]),
    (("round 203: angle of the vector decides the match", 32), ["round 203: angle of the vector", "decides the match"]),
    (
        ("round 203: the candle burns twice as long at night", 4),
        ["round", "203:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 203: the candle burns twice as long at night", 8),
        ["round", "203: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 203: the candle burns twice as long at night", 12),
        ["round 203:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 203: the candle burns twice as long at night", 16),
        ["round 203: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 203: the candle burns twice as long at night", 24),
        ["round 203: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 203: the candle burns twice as long at night", 32),
        ["round 203: the candle burns", "twice as long at night"],
    ),
    (
        ("round 203: a mirror of the universe in one line", 4),
        ["round", "203:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 203: a mirror of the universe in one line", 8),
        ["round", "203: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 203: a mirror of the universe in one line", 12),
        ["round 203: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 203: a mirror of the universe in one line", 16),
        ["round 203: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 203: a mirror of the universe in one line", 24), ["round 203: a mirror of", "the universe in one line"]),
    (("round 203: a mirror of the universe in one line", 32), ["round 203: a mirror of the", "universe in one line"]),
    (
        ("round 203: the queue drains before the storm", 4),
        ["round", "203:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 203: the queue drains before the storm", 8),
        ["round", "203: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 203: the queue drains before the storm", 12),
        ["round 203:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 203: the queue drains before the storm", 16), ["round 203: the", "queue drains", "before the storm"]),
    (("round 203: the queue drains before the storm", 24), ["round 203: the queue", "drains before the storm"]),
    (("round 203: the queue drains before the storm", 32), ["round 203: the queue drains", "before the storm"]),
    (
        ("kitten203 sitting203 agent203 angle203 universe203 memory203", 6),
        ["kitten203", "sitting203", "agent203", "angle203", "universe203", "memory203"],
    ),
    (
        ("kitten203 sitting203 agent203 angle203 universe203 memory203", 10),
        ["kitten203", "sitting203", "agent203", "angle203", "universe203", "memory203"],
    ),
    (
        ("kitten203 sitting203 agent203 angle203 universe203 memory203", 18),
        ["kitten203", "sitting203", "agent203 angle203", "universe203", "memory203"],
    ),
    (
        ("kitten203 sitting203 agent203 angle203 universe203 memory203", 28),
        ["kitten203 sitting203", "agent203 angle203", "universe203 memory203"],
    ),
    (
        ("sitting203 agent203 angle203 universe203 memory203 stream203", 6),
        ["sitting203", "agent203", "angle203", "universe203", "memory203", "stream203"],
    ),
    (
        ("sitting203 agent203 angle203 universe203 memory203 stream203", 10),
        ["sitting203", "agent203", "angle203", "universe203", "memory203", "stream203"],
    ),
    (
        ("sitting203 agent203 angle203 universe203 memory203 stream203", 18),
        ["sitting203", "agent203 angle203", "universe203", "memory203", "stream203"],
    ),
    (
        ("sitting203 agent203 angle203 universe203 memory203 stream203", 28),
        ["sitting203 agent203 angle203", "universe203 memory203", "stream203"],
    ),
    (
        ("agent203 angle203 universe203 memory203 stream203 context203", 6),
        ["agent203", "angle203", "universe203", "memory203", "stream203", "context203"],
    ),
    (
        ("agent203 angle203 universe203 memory203 stream203 context203", 10),
        ["agent203", "angle203", "universe203", "memory203", "stream203", "context203"],
    ),
    (
        ("agent203 angle203 universe203 memory203 stream203 context203", 18),
        ["agent203 angle203", "universe203", "memory203", "stream203", "context203"],
    ),
    (
        ("agent203 angle203 universe203 memory203 stream203 context203", 28),
        ["agent203 angle203", "universe203 memory203", "stream203 context203"],
    ),
    (
        ("angle203 universe203 memory203 stream203 context203 knowledge203", 6),
        ["angle203", "universe203", "memory203", "stream203", "context203", "knowledge203"],
    ),
    (
        ("angle203 universe203 memory203 stream203 context203 knowledge203", 10),
        ["angle203", "universe203", "memory203", "stream203", "context203", "knowledge203"],
    ),
    (
        ("angle203 universe203 memory203 stream203 context203 knowledge203", 18),
        ["angle203", "universe203", "memory203", "stream203", "context203", "knowledge203"],
    ),
    (
        ("angle203 universe203 memory203 stream203 context203 knowledge203", 28),
        ["angle203 universe203", "memory203 stream203", "context203 knowledge203"],
    ),
    (
        ("universe203 memory203 stream203 context203 knowledge203 vector203", 6),
        ["universe203", "memory203", "stream203", "context203", "knowledge203", "vector203"],
    ),
    (
        ("universe203 memory203 stream203 context203 knowledge203 vector203", 10),
        ["universe203", "memory203", "stream203", "context203", "knowledge203", "vector203"],
    ),
    (
        ("universe203 memory203 stream203 context203 knowledge203 vector203", 18),
        ["universe203", "memory203", "stream203", "context203", "knowledge203", "vector203"],
    ),
    (
        ("universe203 memory203 stream203 context203 knowledge203 vector203", 28),
        ["universe203 memory203", "stream203 context203", "knowledge203 vector203"],
    ),
    (
        ("memory203 stream203 context203 knowledge203 vector203 processor203", 6),
        ["memory203", "stream203", "context203", "knowledge203", "vector203", "processor203"],
    ),
    (
        ("memory203 stream203 context203 knowledge203 vector203 processor203", 10),
        ["memory203", "stream203", "context203", "knowledge203", "vector203", "processor203"],
    ),
    (
        ("memory203 stream203 context203 knowledge203 vector203 processor203", 18),
        ["memory203", "stream203", "context203", "knowledge203", "vector203", "processor203"],
    ),
    (
        ("memory203 stream203 context203 knowledge203 vector203 processor203", 28),
        ["memory203 stream203", "context203 knowledge203", "vector203 processor203"],
    ),
    (
        ("stream203 context203 knowledge203 vector203 processor203 reasoning203", 6),
        ["stream203", "context203", "knowledge203", "vector203", "processor203", "reasoning203"],
    ),
    (
        ("stream203 context203 knowledge203 vector203 processor203 reasoning203", 10),
        ["stream203", "context203", "knowledge203", "vector203", "processor203", "reasoning203"],
    ),
    (
        ("stream203 context203 knowledge203 vector203 processor203 reasoning203", 18),
        ["stream203", "context203", "knowledge203", "vector203", "processor203", "reasoning203"],
    ),
    (
        ("stream203 context203 knowledge203 vector203 processor203 reasoning203", 28),
        ["stream203 context203", "knowledge203 vector203", "processor203 reasoning203"],
    ),
    (
        ("context203 knowledge203 vector203 processor203 reasoning203 machine203", 6),
        ["context203", "knowledge203", "vector203", "processor203", "reasoning203", "machine203"],
    ),
    (
        ("context203 knowledge203 vector203 processor203 reasoning203 machine203", 10),
        ["context203", "knowledge203", "vector203", "processor203", "reasoning203", "machine203"],
    ),
    (
        ("context203 knowledge203 vector203 processor203 reasoning203 machine203", 18),
        ["context203", "knowledge203", "vector203", "processor203", "reasoning203", "machine203"],
    ),
    (
        ("context203 knowledge203 vector203 processor203 reasoning203 machine203", 28),
        ["context203 knowledge203", "vector203 processor203", "reasoning203 machine203"],
    ),
    (
        ("knowledge203 vector203 processor203 reasoning203 machine203 learning203", 6),
        ["knowledge203", "vector203", "processor203", "reasoning203", "machine203", "learning203"],
    ),
    (
        ("knowledge203 vector203 processor203 reasoning203 machine203 learning203", 10),
        ["knowledge203", "vector203", "processor203", "reasoning203", "machine203", "learning203"],
    ),
    (
        ("knowledge203 vector203 processor203 reasoning203 machine203 learning203", 18),
        ["knowledge203", "vector203", "processor203", "reasoning203", "machine203", "learning203"],
    ),
    (
        ("knowledge203 vector203 processor203 reasoning203 machine203 learning203", 28),
        ["knowledge203 vector203", "processor203 reasoning203", "machine203 learning203"],
    ),
    (
        ("vector203 processor203 reasoning203 machine203 learning203 model203", 6),
        ["vector203", "processor203", "reasoning203", "machine203", "learning203", "model203"],
    ),
    (
        ("vector203 processor203 reasoning203 machine203 learning203 model203", 10),
        ["vector203", "processor203", "reasoning203", "machine203", "learning203", "model203"],
    ),
    (
        ("vector203 processor203 reasoning203 machine203 learning203 model203", 18),
        ["vector203", "processor203", "reasoning203", "machine203", "learning203", "model203"],
    ),
    (
        ("vector203 processor203 reasoning203 machine203 learning203 model203", 28),
        ["vector203 processor203", "reasoning203 machine203", "learning203 model203"],
    ),
    (
        ("processor203 reasoning203 machine203 learning203 model203 token203", 6),
        ["processor203", "reasoning203", "machine203", "learning203", "model203", "token203"],
    ),
    (
        ("processor203 reasoning203 machine203 learning203 model203 token203", 10),
        ["processor203", "reasoning203", "machine203", "learning203", "model203", "token203"],
    ),
    (
        ("processor203 reasoning203 machine203 learning203 model203 token203", 18),
        ["processor203", "reasoning203", "machine203", "learning203", "model203 token203"],
    ),
    (
        ("processor203 reasoning203 machine203 learning203 model203 token203", 28),
        ["processor203 reasoning203", "machine203 learning203", "model203 token203"],
    ),
    (
        ("reasoning203 machine203 learning203 model203 token203 prompt203", 6),
        ["reasoning203", "machine203", "learning203", "model203", "token203", "prompt203"],
    ),
    (
        ("reasoning203 machine203 learning203 model203 token203 prompt203", 10),
        ["reasoning203", "machine203", "learning203", "model203", "token203", "prompt203"],
    ),
    (
        ("reasoning203 machine203 learning203 model203 token203 prompt203", 18),
        ["reasoning203", "machine203", "learning203", "model203 token203", "prompt203"],
    ),
    (
        ("reasoning203 machine203 learning203 model203 token203 prompt203", 28),
        ["reasoning203 machine203", "learning203 model203", "token203 prompt203"],
    ),
    (
        ("machine203 learning203 model203 token203 prompt203 session203", 6),
        ["machine203", "learning203", "model203", "token203", "prompt203", "session203"],
    ),
    (
        ("machine203 learning203 model203 token203 prompt203 session203", 10),
        ["machine203", "learning203", "model203", "token203", "prompt203", "session203"],
    ),
    (
        ("machine203 learning203 model203 token203 prompt203 session203", 18),
        ["machine203", "learning203", "model203 token203", "prompt203", "session203"],
    ),
    (
        ("machine203 learning203 model203 token203 prompt203 session203", 28),
        ["machine203 learning203", "model203 token203 prompt203", "session203"],
    ),
    (
        ("learning203 model203 token203 prompt203 session203 library203", 6),
        ["learning203", "model203", "token203", "prompt203", "session203", "library203"],
    ),
    (
        ("learning203 model203 token203 prompt203 session203 library203", 10),
        ["learning203", "model203", "token203", "prompt203", "session203", "library203"],
    ),
    (
        ("learning203 model203 token203 prompt203 session203 library203", 18),
        ["learning203", "model203 token203", "prompt203", "session203", "library203"],
    ),
    (
        ("learning203 model203 token203 prompt203 session203 library203", 28),
        ["learning203 model203", "token203 prompt203", "session203 library203"],
    ),
    (
        ("model203 token203 prompt203 session203 library203 service203", 6),
        ["model203", "token203", "prompt203", "session203", "library203", "service203"],
    ),
    (
        ("model203 token203 prompt203 session203 library203 service203", 10),
        ["model203", "token203", "prompt203", "session203", "library203", "service203"],
    ),
    (
        ("model203 token203 prompt203 session203 library203 service203", 18),
        ["model203 token203", "prompt203", "session203", "library203", "service203"],
    ),
    (
        ("model203 token203 prompt203 session203 library203 service203", 28),
        ["model203 token203 prompt203", "session203 library203", "service203"],
    ),
    (
        ("token203 prompt203 session203 library203 service203 gateway203", 6),
        ["token203", "prompt203", "session203", "library203", "service203", "gateway203"],
    ),
    (
        ("token203 prompt203 session203 library203 service203 gateway203", 10),
        ["token203", "prompt203", "session203", "library203", "service203", "gateway203"],
    ),
    (
        ("token203 prompt203 session203 library203 service203 gateway203", 18),
        ["token203 prompt203", "session203", "library203", "service203", "gateway203"],
    ),
    (
        ("token203 prompt203 session203 library203 service203 gateway203", 28),
        ["token203 prompt203", "session203 library203", "service203 gateway203"],
    ),
    (
        ("prompt203 session203 library203 service203 gateway203 storage203", 6),
        ["prompt203", "session203", "library203", "service203", "gateway203", "storage203"],
    ),
    (
        ("prompt203 session203 library203 service203 gateway203 storage203", 10),
        ["prompt203", "session203", "library203", "service203", "gateway203", "storage203"],
    ),
    (
        ("prompt203 session203 library203 service203 gateway203 storage203", 18),
        ["prompt203", "session203", "library203", "service203", "gateway203", "storage203"],
    ),
    (
        ("prompt203 session203 library203 service203 gateway203 storage203", 28),
        ["prompt203 session203", "library203 service203", "gateway203 storage203"],
    ),
    (
        ("session203 library203 service203 gateway203 storage203 network203", 6),
        ["session203", "library203", "service203", "gateway203", "storage203", "network203"],
    ),
    (
        ("session203 library203 service203 gateway203 storage203 network203", 10),
        ["session203", "library203", "service203", "gateway203", "storage203", "network203"],
    ),
    (
        ("session203 library203 service203 gateway203 storage203 network203", 18),
        ["session203", "library203", "service203", "gateway203", "storage203", "network203"],
    ),
    (
        ("session203 library203 service203 gateway203 storage203 network203", 28),
        ["session203 library203", "service203 gateway203", "storage203 network203"],
    ),
    (
        ("library203 service203 gateway203 storage203 network203 latency203", 6),
        ["library203", "service203", "gateway203", "storage203", "network203", "latency203"],
    ),
    (
        ("library203 service203 gateway203 storage203 network203 latency203", 10),
        ["library203", "service203", "gateway203", "storage203", "network203", "latency203"],
    ),
    (
        ("library203 service203 gateway203 storage203 network203 latency203", 18),
        ["library203", "service203", "gateway203", "storage203", "network203", "latency203"],
    ),
    (
        ("library203 service203 gateway203 storage203 network203 latency203", 28),
        ["library203 service203", "gateway203 storage203", "network203 latency203"],
    ),
    (
        ("service203 gateway203 storage203 network203 latency203 buffer203", 6),
        ["service203", "gateway203", "storage203", "network203", "latency203", "buffer203"],
    ),
    (
        ("service203 gateway203 storage203 network203 latency203 buffer203", 10),
        ["service203", "gateway203", "storage203", "network203", "latency203", "buffer203"],
    ),
    (
        ("service203 gateway203 storage203 network203 latency203 buffer203", 18),
        ["service203", "gateway203", "storage203", "network203", "latency203", "buffer203"],
    ),
    (
        ("service203 gateway203 storage203 network203 latency203 buffer203", 28),
        ["service203 gateway203", "storage203 network203", "latency203 buffer203"],
    ),
    (
        ("gateway203 storage203 network203 latency203 buffer203 queue203", 6),
        ["gateway203", "storage203", "network203", "latency203", "buffer203", "queue203"],
    ),
    (
        ("gateway203 storage203 network203 latency203 buffer203 queue203", 10),
        ["gateway203", "storage203", "network203", "latency203", "buffer203", "queue203"],
    ),
    (
        ("gateway203 storage203 network203 latency203 buffer203 queue203", 18),
        ["gateway203", "storage203", "network203", "latency203", "buffer203 queue203"],
    ),
    (
        ("gateway203 storage203 network203 latency203 buffer203 queue203", 28),
        ["gateway203 storage203", "network203 latency203", "buffer203 queue203"],
    ),
    (
        ("storage203 network203 latency203 buffer203 queue203 worker203", 6),
        ["storage203", "network203", "latency203", "buffer203", "queue203", "worker203"],
    ),
    (
        ("storage203 network203 latency203 buffer203 queue203 worker203", 10),
        ["storage203", "network203", "latency203", "buffer203", "queue203", "worker203"],
    ),
    (
        ("storage203 network203 latency203 buffer203 queue203 worker203", 18),
        ["storage203", "network203", "latency203", "buffer203 queue203", "worker203"],
    ),
    (
        ("storage203 network203 latency203 buffer203 queue203 worker203", 28),
        ["storage203 network203", "latency203 buffer203", "queue203 worker203"],
    ),
    (
        ("network203 latency203 buffer203 queue203 worker203 kernel203", 6),
        ["network203", "latency203", "buffer203", "queue203", "worker203", "kernel203"],
    ),
    (
        ("network203 latency203 buffer203 queue203 worker203 kernel203", 10),
        ["network203", "latency203", "buffer203", "queue203", "worker203", "kernel203"],
    ),
    (
        ("network203 latency203 buffer203 queue203 worker203 kernel203", 18),
        ["network203", "latency203", "buffer203 queue203", "worker203", "kernel203"],
    ),
    (
        ("network203 latency203 buffer203 queue203 worker203 kernel203", 28),
        ["network203 latency203", "buffer203 queue203 worker203", "kernel203"],
    ),
    (
        ("latency203 buffer203 queue203 worker203 kernel203 signal203", 6),
        ["latency203", "buffer203", "queue203", "worker203", "kernel203", "signal203"],
    ),
    (
        ("latency203 buffer203 queue203 worker203 kernel203 signal203", 10),
        ["latency203", "buffer203", "queue203", "worker203", "kernel203", "signal203"],
    ),
    (
        ("latency203 buffer203 queue203 worker203 kernel203 signal203", 18),
        ["latency203", "buffer203 queue203", "worker203", "kernel203", "signal203"],
    ),
    (
        ("latency203 buffer203 queue203 worker203 kernel203 signal203", 28),
        ["latency203 buffer203", "queue203 worker203 kernel203", "signal203"],
    ),
    (
        ("buffer203 queue203 worker203 kernel203 signal203 packet203", 6),
        ["buffer203", "queue203", "worker203", "kernel203", "signal203", "packet203"],
    ),
    (
        ("buffer203 queue203 worker203 kernel203 signal203 packet203", 10),
        ["buffer203", "queue203", "worker203", "kernel203", "signal203", "packet203"],
    ),
    (
        ("buffer203 queue203 worker203 kernel203 signal203 packet203", 18),
        ["buffer203 queue203", "worker203", "kernel203", "signal203", "packet203"],
    ),
    (
        ("buffer203 queue203 worker203 kernel203 signal203 packet203", 28),
        ["buffer203 queue203 worker203", "kernel203 signal203", "packet203"],
    ),
    (
        ("queue203 worker203 kernel203 signal203 packet203 router203", 6),
        ["queue203", "worker203", "kernel203", "signal203", "packet203", "router203"],
    ),
    (
        ("queue203 worker203 kernel203 signal203 packet203 router203", 10),
        ["queue203", "worker203", "kernel203", "signal203", "packet203", "router203"],
    ),
    (
        ("queue203 worker203 kernel203 signal203 packet203 router203", 18),
        ["queue203 worker203", "kernel203", "signal203", "packet203", "router203"],
    ),
    (
        ("queue203 worker203 kernel203 signal203 packet203 router203", 28),
        ["queue203 worker203 kernel203", "signal203 packet203", "router203"],
    ),
    (
        ("worker203 kernel203 signal203 packet203 router203 cluster203", 6),
        ["worker203", "kernel203", "signal203", "packet203", "router203", "cluster203"],
    ),
    (
        ("worker203 kernel203 signal203 packet203 router203 cluster203", 10),
        ["worker203", "kernel203", "signal203", "packet203", "router203", "cluster203"],
    ),
    (
        ("worker203 kernel203 signal203 packet203 router203 cluster203", 18),
        ["worker203", "kernel203", "signal203", "packet203", "router203", "cluster203"],
    ),
    (
        ("worker203 kernel203 signal203 packet203 router203 cluster203", 28),
        ["worker203 kernel203", "signal203 packet203", "router203 cluster203"],
    ),
    (
        ("kernel203 signal203 packet203 router203 cluster203 mirror203", 6),
        ["kernel203", "signal203", "packet203", "router203", "cluster203", "mirror203"],
    ),
    (
        ("kernel203 signal203 packet203 router203 cluster203 mirror203", 10),
        ["kernel203", "signal203", "packet203", "router203", "cluster203", "mirror203"],
    ),
    (
        ("kernel203 signal203 packet203 router203 cluster203 mirror203", 18),
        ["kernel203", "signal203", "packet203", "router203", "cluster203", "mirror203"],
    ),
    (
        ("kernel203 signal203 packet203 router203 cluster203 mirror203", 28),
        ["kernel203 signal203", "packet203 router203", "cluster203 mirror203"],
    ),
    (
        ("signal203 packet203 router203 cluster203 mirror203 filter203", 6),
        ["signal203", "packet203", "router203", "cluster203", "mirror203", "filter203"],
    ),
    (
        ("signal203 packet203 router203 cluster203 mirror203 filter203", 10),
        ["signal203", "packet203", "router203", "cluster203", "mirror203", "filter203"],
    ),
    (
        ("signal203 packet203 router203 cluster203 mirror203 filter203", 18),
        ["signal203", "packet203", "router203", "cluster203", "mirror203", "filter203"],
    ),
    (
        ("signal203 packet203 router203 cluster203 mirror203 filter203", 28),
        ["signal203 packet203", "router203 cluster203", "mirror203 filter203"],
    ),
    (
        ("packet203 router203 cluster203 mirror203 filter203 ranking203", 6),
        ["packet203", "router203", "cluster203", "mirror203", "filter203", "ranking203"],
    ),
    (
        ("packet203 router203 cluster203 mirror203 filter203 ranking203", 10),
        ["packet203", "router203", "cluster203", "mirror203", "filter203", "ranking203"],
    ),
    (
        ("packet203 router203 cluster203 mirror203 filter203 ranking203", 18),
        ["packet203", "router203", "cluster203", "mirror203", "filter203", "ranking203"],
    ),
    (
        ("packet203 router203 cluster203 mirror203 filter203 ranking203", 28),
        ["packet203 router203", "cluster203 mirror203", "filter203 ranking203"],
    ),
    (
        ("router203 cluster203 mirror203 filter203 ranking203 encoding203", 6),
        ["router203", "cluster203", "mirror203", "filter203", "ranking203", "encoding203"],
    ),
    (
        ("router203 cluster203 mirror203 filter203 ranking203 encoding203", 10),
        ["router203", "cluster203", "mirror203", "filter203", "ranking203", "encoding203"],
    ),
    (
        ("router203 cluster203 mirror203 filter203 ranking203 encoding203", 18),
        ["router203", "cluster203", "mirror203", "filter203", "ranking203", "encoding203"],
    ),
    (
        ("router203 cluster203 mirror203 filter203 ranking203 encoding203", 28),
        ["router203 cluster203", "mirror203 filter203", "ranking203 encoding203"],
    ),
    (
        ("cluster203 mirror203 filter203 ranking203 encoding203 mapping203", 6),
        ["cluster203", "mirror203", "filter203", "ranking203", "encoding203", "mapping203"],
    ),
    (
        ("cluster203 mirror203 filter203 ranking203 encoding203 mapping203", 10),
        ["cluster203", "mirror203", "filter203", "ranking203", "encoding203", "mapping203"],
    ),
    (
        ("cluster203 mirror203 filter203 ranking203 encoding203 mapping203", 18),
        ["cluster203", "mirror203", "filter203", "ranking203", "encoding203", "mapping203"],
    ),
    (
        ("cluster203 mirror203 filter203 ranking203 encoding203 mapping203", 28),
        ["cluster203 mirror203", "filter203 ranking203", "encoding203 mapping203"],
    ),
    (
        ("mirror203 filter203 ranking203 encoding203 mapping203 record203", 6),
        ["mirror203", "filter203", "ranking203", "encoding203", "mapping203", "record203"],
    ),
    (
        ("mirror203 filter203 ranking203 encoding203 mapping203 record203", 10),
        ["mirror203", "filter203", "ranking203", "encoding203", "mapping203", "record203"],
    ),
    (
        ("mirror203 filter203 ranking203 encoding203 mapping203 record203", 18),
        ["mirror203", "filter203", "ranking203", "encoding203", "mapping203", "record203"],
    ),
    (
        ("mirror203 filter203 ranking203 encoding203 mapping203 record203", 28),
        ["mirror203 filter203", "ranking203 encoding203", "mapping203 record203"],
    ),
    (
        ("filter203 ranking203 encoding203 mapping203 record203 candle203", 6),
        ["filter203", "ranking203", "encoding203", "mapping203", "record203", "candle203"],
    ),
    (
        ("filter203 ranking203 encoding203 mapping203 record203 candle203", 10),
        ["filter203", "ranking203", "encoding203", "mapping203", "record203", "candle203"],
    ),
    (
        ("filter203 ranking203 encoding203 mapping203 record203 candle203", 18),
        ["filter203", "ranking203", "encoding203", "mapping203", "record203", "candle203"],
    ),
    (
        ("filter203 ranking203 encoding203 mapping203 record203 candle203", 28),
        ["filter203 ranking203", "encoding203 mapping203", "record203 candle203"],
    ),
    (
        ("ranking203 encoding203 mapping203 record203 candle203 thread203", 6),
        ["ranking203", "encoding203", "mapping203", "record203", "candle203", "thread203"],
    ),
    (
        ("ranking203 encoding203 mapping203 record203 candle203 thread203", 10),
        ["ranking203", "encoding203", "mapping203", "record203", "candle203", "thread203"],
    ),
    (
        ("ranking203 encoding203 mapping203 record203 candle203 thread203", 18),
        ["ranking203", "encoding203", "mapping203", "record203", "candle203", "thread203"],
    ),
    (
        ("ranking203 encoding203 mapping203 record203 candle203 thread203", 28),
        ["ranking203 encoding203", "mapping203 record203", "candle203 thread203"],
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
