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
        ("round 127: the quick brown fox jumps over the lazy dog", 4),
        ["round", "127:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 127: the quick brown fox jumps over the lazy dog", 8),
        ["round", "127: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 127: the quick brown fox jumps over the lazy dog", 12),
        ["round 127:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 127: the quick brown fox jumps over the lazy dog", 16),
        ["round 127: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 127: the quick brown fox jumps over the lazy dog", 24),
        ["round 127: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 127: the quick brown fox jumps over the lazy dog", 32),
        ["round 127: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 127: agentuniverse is a framework for multi agents", 4),
        ["round", "127:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 127: agentuniverse is a framework for multi agents", 8),
        ["round", "127:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 127: agentuniverse is a framework for multi agents", 12),
        ["round 127:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 127: agentuniverse is a framework for multi agents", 16),
        ["round 127:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 127: agentuniverse is a framework for multi agents", 24),
        ["round 127: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 127: agentuniverse is a framework for multi agents", 32),
        ["round 127: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 127: knowledge stored as vectors enables retrieval", 4),
        ["round", "127:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 127: knowledge stored as vectors enables retrieval", 8),
        ["round", "127:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 127: knowledge stored as vectors enables retrieval", 12),
        ["round 127:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 127: knowledge stored as vectors enables retrieval", 16),
        ["round 127:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 127: knowledge stored as vectors enables retrieval", 24),
        ["round 127: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 127: knowledge stored as vectors enables retrieval", 32),
        ["round 127: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 127: the processor reads the record then stops", 4),
        ["round", "127:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 127: the processor reads the record then stops", 8),
        ["round", "127: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 127: the processor reads the record then stops", 12),
        ["round 127:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 127: the processor reads the record then stops", 16),
        ["round 127: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 127: the processor reads the record then stops", 24),
        ["round 127: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 127: the processor reads the record then stops", 32),
        ["round 127: the processor reads", "the record then stops"],
    ),
    (
        ("round 127: a worker pulls the next task from the queue", 4),
        ["round", "127:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 127: a worker pulls the next task from the queue", 8),
        ["round", "127: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 127: a worker pulls the next task from the queue", 12),
        ["round 127: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 127: a worker pulls the next task from the queue", 16),
        ["round 127: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 127: a worker pulls the next task from the queue", 24),
        ["round 127: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 127: a worker pulls the next task from the queue", 32),
        ["round 127: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 127: signals travel through the network layer", 4),
        ["round", "127:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 127: signals travel through the network layer", 8),
        ["round", "127:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 127: signals travel through the network layer", 12),
        ["round 127:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 127: signals travel through the network layer", 16),
        ["round 127:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 127: signals travel through the network layer", 24),
        ["round 127: signals", "travel through the", "network layer"],
    ),
    (
        ("round 127: signals travel through the network layer", 32),
        ["round 127: signals travel", "through the network layer"],
    ),
    (
        ("round 127: the gateway routes each request by policy", 4),
        ["round", "127:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 127: the gateway routes each request by policy", 8),
        ["round", "127: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 127: the gateway routes each request by policy", 12),
        ["round 127:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 127: the gateway routes each request by policy", 16),
        ["round 127: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 127: the gateway routes each request by policy", 24),
        ["round 127: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 127: the gateway routes each request by policy", 32),
        ["round 127: the gateway routes", "each request by policy"],
    ),
    (
        ("round 127: memory grows until the buffer is full", 4),
        ["round", "127:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 127: memory grows until the buffer is full", 8),
        ["round", "127:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 127: memory grows until the buffer is full", 12),
        ["round 127:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 127: memory grows until the buffer is full", 16),
        ["round 127:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 127: memory grows until the buffer is full", 24), ["round 127: memory grows", "until the buffer is full"]),
    (("round 127: memory grows until the buffer is full", 32), ["round 127: memory grows until", "the buffer is full"]),
    (
        ("round 127: the cluster mirrors every packet twice", 4),
        ["round", "127:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 127: the cluster mirrors every packet twice", 8),
        ["round", "127: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 127: the cluster mirrors every packet twice", 12),
        ["round 127:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 127: the cluster mirrors every packet twice", 16),
        ["round 127: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 127: the cluster mirrors every packet twice", 24),
        ["round 127: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 127: the cluster mirrors every packet twice", 32),
        ["round 127: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 127: ranking uses tokens learned from the corpus", 4),
        ["round", "127:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 127: ranking uses tokens learned from the corpus", 8),
        ["round", "127:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 127: ranking uses tokens learned from the corpus", 12),
        ["round 127:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 127: ranking uses tokens learned from the corpus", 16),
        ["round 127:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 127: ranking uses tokens learned from the corpus", 24),
        ["round 127: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 127: ranking uses tokens learned from the corpus", 32),
        ["round 127: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 127: a long session ends when the candle dies", 4),
        ["round", "127:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 127: a long session ends when the candle dies", 8),
        ["round", "127: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 127: a long session ends when the candle dies", 12),
        ["round 127: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 127: a long session ends when the candle dies", 16),
        ["round 127: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 127: a long session ends when the candle dies", 24),
        ["round 127: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 127: a long session ends when the candle dies", 32),
        ["round 127: a long session ends", "when the candle dies"],
    ),
    (
        ("round 127: encode the prompt then map the result", 4),
        ["round", "127:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 127: encode the prompt then map the result", 8),
        ["round", "127:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 127: encode the prompt then map the result", 12),
        ["round 127:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 127: encode the prompt then map the result", 16),
        ["round 127:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 127: encode the prompt then map the result", 24),
        ["round 127: encode the", "prompt then map the", "result"],
    ),
    (("round 127: encode the prompt then map the result", 32), ["round 127: encode the prompt", "then map the result"]),
    (
        ("round 127: the kernel wakes the worker at dawn", 4),
        ["round", "127:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 127: the kernel wakes the worker at dawn", 8),
        ["round", "127: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 127: the kernel wakes the worker at dawn", 12),
        ["round 127:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 127: the kernel wakes the worker at dawn", 16), ["round 127: the", "kernel wakes the", "worker at dawn"]),
    (("round 127: the kernel wakes the worker at dawn", 24), ["round 127: the kernel", "wakes the worker at dawn"]),
    (("round 127: the kernel wakes the worker at dawn", 32), ["round 127: the kernel wakes the", "worker at dawn"]),
    (
        ("round 127: service latency drops after the patch", 4),
        ["round", "127:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 127: service latency drops after the patch", 8),
        ["round", "127:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 127: service latency drops after the patch", 12),
        ["round 127:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 127: service latency drops after the patch", 16),
        ["round 127:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 127: service latency drops after the patch", 24),
        ["round 127: service", "latency drops after the", "patch"],
    ),
    (("round 127: service latency drops after the patch", 32), ["round 127: service latency drops", "after the patch"]),
    (
        ("round 127: the library caches every vector it sees", 4),
        ["round", "127:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 127: the library caches every vector it sees", 8),
        ["round", "127: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 127: the library caches every vector it sees", 12),
        ["round 127:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 127: the library caches every vector it sees", 16),
        ["round 127: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 127: the library caches every vector it sees", 24),
        ["round 127: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 127: the library caches every vector it sees", 32),
        ["round 127: the library caches", "every vector it sees"],
    ),
    (
        ("round 127: agents argue then the debate resolves", 4),
        ["round", "127:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 127: agents argue then the debate resolves", 8),
        ["round", "127:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 127: agents argue then the debate resolves", 12),
        ["round 127:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 127: agents argue then the debate resolves", 16),
        ["round 127:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 127: agents argue then the debate resolves", 24), ["round 127: agents argue", "then the debate resolves"]),
    (("round 127: agents argue then the debate resolves", 32), ["round 127: agents argue then the", "debate resolves"]),
    (
        ("round 127: the filter keeps only strong matches", 4),
        ["round", "127:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 127: the filter keeps only strong matches", 8),
        ["round", "127: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 127: the filter keeps only strong matches", 12),
        ["round 127:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 127: the filter keeps only strong matches", 16),
        ["round 127: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 127: the filter keeps only strong matches", 24),
        ["round 127: the filter", "keeps only strong", "matches"],
    ),
    (("round 127: the filter keeps only strong matches", 32), ["round 127: the filter keeps only", "strong matches"]),
    (
        ("round 127: the model answers with a short reply", 4),
        ["round", "127:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 127: the model answers with a short reply", 8),
        ["round", "127: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 127: the model answers with a short reply", 12),
        ["round 127:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 127: the model answers with a short reply", 16),
        ["round 127: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 127: the model answers with a short reply", 24),
        ["round 127: the model", "answers with a short", "reply"],
    ),
    (("round 127: the model answers with a short reply", 32), ["round 127: the model answers", "with a short reply"]),
    (
        ("round 127: the recorder stores the reasoning trace", 4),
        ["round", "127:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 127: the recorder stores the reasoning trace", 8),
        ["round", "127: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 127: the recorder stores the reasoning trace", 12),
        ["round 127:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 127: the recorder stores the reasoning trace", 16),
        ["round 127: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 127: the recorder stores the reasoning trace", 24),
        ["round 127: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 127: the recorder stores the reasoning trace", 32),
        ["round 127: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 127: the angel watches the processor run", 4),
        ["round", "127:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 127: the angel watches the processor run", 8),
        ["round", "127: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 127: the angel watches the processor run", 12),
        ["round 127:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 127: the angel watches the processor run", 16),
        ["round 127: the", "angel watches", "the processor", "run"],
    ),
    (("round 127: the angel watches the processor run", 24), ["round 127: the angel", "watches the processor", "run"]),
    (("round 127: the angel watches the processor run", 32), ["round 127: the angel watches the", "processor run"]),
    (
        ("round 127: angle of the vector decides the match", 4),
        ["round", "127:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 127: angle of the vector decides the match", 8),
        ["round", "127:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 127: angle of the vector decides the match", 12),
        ["round 127:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 127: angle of the vector decides the match", 16),
        ["round 127: angle", "of the vector", "decides the", "match"],
    ),
    (("round 127: angle of the vector decides the match", 24), ["round 127: angle of the", "vector decides the match"]),
    (("round 127: angle of the vector decides the match", 32), ["round 127: angle of the vector", "decides the match"]),
    (
        ("round 127: the candle burns twice as long at night", 4),
        ["round", "127:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 127: the candle burns twice as long at night", 8),
        ["round", "127: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 127: the candle burns twice as long at night", 12),
        ["round 127:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 127: the candle burns twice as long at night", 16),
        ["round 127: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 127: the candle burns twice as long at night", 24),
        ["round 127: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 127: the candle burns twice as long at night", 32),
        ["round 127: the candle burns", "twice as long at night"],
    ),
    (
        ("round 127: a mirror of the universe in one line", 4),
        ["round", "127:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 127: a mirror of the universe in one line", 8),
        ["round", "127: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 127: a mirror of the universe in one line", 12),
        ["round 127: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 127: a mirror of the universe in one line", 16),
        ["round 127: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 127: a mirror of the universe in one line", 24), ["round 127: a mirror of", "the universe in one line"]),
    (("round 127: a mirror of the universe in one line", 32), ["round 127: a mirror of the", "universe in one line"]),
    (
        ("round 127: the queue drains before the storm", 4),
        ["round", "127:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 127: the queue drains before the storm", 8),
        ["round", "127: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 127: the queue drains before the storm", 12),
        ["round 127:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 127: the queue drains before the storm", 16), ["round 127: the", "queue drains", "before the storm"]),
    (("round 127: the queue drains before the storm", 24), ["round 127: the queue", "drains before the storm"]),
    (("round 127: the queue drains before the storm", 32), ["round 127: the queue drains", "before the storm"]),
    (
        ("kitten127 sitting127 agent127 angle127 universe127 memory127", 6),
        ["kitten127", "sitting127", "agent127", "angle127", "universe127", "memory127"],
    ),
    (
        ("kitten127 sitting127 agent127 angle127 universe127 memory127", 10),
        ["kitten127", "sitting127", "agent127", "angle127", "universe127", "memory127"],
    ),
    (
        ("kitten127 sitting127 agent127 angle127 universe127 memory127", 18),
        ["kitten127", "sitting127", "agent127 angle127", "universe127", "memory127"],
    ),
    (
        ("kitten127 sitting127 agent127 angle127 universe127 memory127", 28),
        ["kitten127 sitting127", "agent127 angle127", "universe127 memory127"],
    ),
    (
        ("sitting127 agent127 angle127 universe127 memory127 stream127", 6),
        ["sitting127", "agent127", "angle127", "universe127", "memory127", "stream127"],
    ),
    (
        ("sitting127 agent127 angle127 universe127 memory127 stream127", 10),
        ["sitting127", "agent127", "angle127", "universe127", "memory127", "stream127"],
    ),
    (
        ("sitting127 agent127 angle127 universe127 memory127 stream127", 18),
        ["sitting127", "agent127 angle127", "universe127", "memory127", "stream127"],
    ),
    (
        ("sitting127 agent127 angle127 universe127 memory127 stream127", 28),
        ["sitting127 agent127 angle127", "universe127 memory127", "stream127"],
    ),
    (
        ("agent127 angle127 universe127 memory127 stream127 context127", 6),
        ["agent127", "angle127", "universe127", "memory127", "stream127", "context127"],
    ),
    (
        ("agent127 angle127 universe127 memory127 stream127 context127", 10),
        ["agent127", "angle127", "universe127", "memory127", "stream127", "context127"],
    ),
    (
        ("agent127 angle127 universe127 memory127 stream127 context127", 18),
        ["agent127 angle127", "universe127", "memory127", "stream127", "context127"],
    ),
    (
        ("agent127 angle127 universe127 memory127 stream127 context127", 28),
        ["agent127 angle127", "universe127 memory127", "stream127 context127"],
    ),
    (
        ("angle127 universe127 memory127 stream127 context127 knowledge127", 6),
        ["angle127", "universe127", "memory127", "stream127", "context127", "knowledge127"],
    ),
    (
        ("angle127 universe127 memory127 stream127 context127 knowledge127", 10),
        ["angle127", "universe127", "memory127", "stream127", "context127", "knowledge127"],
    ),
    (
        ("angle127 universe127 memory127 stream127 context127 knowledge127", 18),
        ["angle127", "universe127", "memory127", "stream127", "context127", "knowledge127"],
    ),
    (
        ("angle127 universe127 memory127 stream127 context127 knowledge127", 28),
        ["angle127 universe127", "memory127 stream127", "context127 knowledge127"],
    ),
    (
        ("universe127 memory127 stream127 context127 knowledge127 vector127", 6),
        ["universe127", "memory127", "stream127", "context127", "knowledge127", "vector127"],
    ),
    (
        ("universe127 memory127 stream127 context127 knowledge127 vector127", 10),
        ["universe127", "memory127", "stream127", "context127", "knowledge127", "vector127"],
    ),
    (
        ("universe127 memory127 stream127 context127 knowledge127 vector127", 18),
        ["universe127", "memory127", "stream127", "context127", "knowledge127", "vector127"],
    ),
    (
        ("universe127 memory127 stream127 context127 knowledge127 vector127", 28),
        ["universe127 memory127", "stream127 context127", "knowledge127 vector127"],
    ),
    (
        ("memory127 stream127 context127 knowledge127 vector127 processor127", 6),
        ["memory127", "stream127", "context127", "knowledge127", "vector127", "processor127"],
    ),
    (
        ("memory127 stream127 context127 knowledge127 vector127 processor127", 10),
        ["memory127", "stream127", "context127", "knowledge127", "vector127", "processor127"],
    ),
    (
        ("memory127 stream127 context127 knowledge127 vector127 processor127", 18),
        ["memory127", "stream127", "context127", "knowledge127", "vector127", "processor127"],
    ),
    (
        ("memory127 stream127 context127 knowledge127 vector127 processor127", 28),
        ["memory127 stream127", "context127 knowledge127", "vector127 processor127"],
    ),
    (
        ("stream127 context127 knowledge127 vector127 processor127 reasoning127", 6),
        ["stream127", "context127", "knowledge127", "vector127", "processor127", "reasoning127"],
    ),
    (
        ("stream127 context127 knowledge127 vector127 processor127 reasoning127", 10),
        ["stream127", "context127", "knowledge127", "vector127", "processor127", "reasoning127"],
    ),
    (
        ("stream127 context127 knowledge127 vector127 processor127 reasoning127", 18),
        ["stream127", "context127", "knowledge127", "vector127", "processor127", "reasoning127"],
    ),
    (
        ("stream127 context127 knowledge127 vector127 processor127 reasoning127", 28),
        ["stream127 context127", "knowledge127 vector127", "processor127 reasoning127"],
    ),
    (
        ("context127 knowledge127 vector127 processor127 reasoning127 machine127", 6),
        ["context127", "knowledge127", "vector127", "processor127", "reasoning127", "machine127"],
    ),
    (
        ("context127 knowledge127 vector127 processor127 reasoning127 machine127", 10),
        ["context127", "knowledge127", "vector127", "processor127", "reasoning127", "machine127"],
    ),
    (
        ("context127 knowledge127 vector127 processor127 reasoning127 machine127", 18),
        ["context127", "knowledge127", "vector127", "processor127", "reasoning127", "machine127"],
    ),
    (
        ("context127 knowledge127 vector127 processor127 reasoning127 machine127", 28),
        ["context127 knowledge127", "vector127 processor127", "reasoning127 machine127"],
    ),
    (
        ("knowledge127 vector127 processor127 reasoning127 machine127 learning127", 6),
        ["knowledge127", "vector127", "processor127", "reasoning127", "machine127", "learning127"],
    ),
    (
        ("knowledge127 vector127 processor127 reasoning127 machine127 learning127", 10),
        ["knowledge127", "vector127", "processor127", "reasoning127", "machine127", "learning127"],
    ),
    (
        ("knowledge127 vector127 processor127 reasoning127 machine127 learning127", 18),
        ["knowledge127", "vector127", "processor127", "reasoning127", "machine127", "learning127"],
    ),
    (
        ("knowledge127 vector127 processor127 reasoning127 machine127 learning127", 28),
        ["knowledge127 vector127", "processor127 reasoning127", "machine127 learning127"],
    ),
    (
        ("vector127 processor127 reasoning127 machine127 learning127 model127", 6),
        ["vector127", "processor127", "reasoning127", "machine127", "learning127", "model127"],
    ),
    (
        ("vector127 processor127 reasoning127 machine127 learning127 model127", 10),
        ["vector127", "processor127", "reasoning127", "machine127", "learning127", "model127"],
    ),
    (
        ("vector127 processor127 reasoning127 machine127 learning127 model127", 18),
        ["vector127", "processor127", "reasoning127", "machine127", "learning127", "model127"],
    ),
    (
        ("vector127 processor127 reasoning127 machine127 learning127 model127", 28),
        ["vector127 processor127", "reasoning127 machine127", "learning127 model127"],
    ),
    (
        ("processor127 reasoning127 machine127 learning127 model127 token127", 6),
        ["processor127", "reasoning127", "machine127", "learning127", "model127", "token127"],
    ),
    (
        ("processor127 reasoning127 machine127 learning127 model127 token127", 10),
        ["processor127", "reasoning127", "machine127", "learning127", "model127", "token127"],
    ),
    (
        ("processor127 reasoning127 machine127 learning127 model127 token127", 18),
        ["processor127", "reasoning127", "machine127", "learning127", "model127 token127"],
    ),
    (
        ("processor127 reasoning127 machine127 learning127 model127 token127", 28),
        ["processor127 reasoning127", "machine127 learning127", "model127 token127"],
    ),
    (
        ("reasoning127 machine127 learning127 model127 token127 prompt127", 6),
        ["reasoning127", "machine127", "learning127", "model127", "token127", "prompt127"],
    ),
    (
        ("reasoning127 machine127 learning127 model127 token127 prompt127", 10),
        ["reasoning127", "machine127", "learning127", "model127", "token127", "prompt127"],
    ),
    (
        ("reasoning127 machine127 learning127 model127 token127 prompt127", 18),
        ["reasoning127", "machine127", "learning127", "model127 token127", "prompt127"],
    ),
    (
        ("reasoning127 machine127 learning127 model127 token127 prompt127", 28),
        ["reasoning127 machine127", "learning127 model127", "token127 prompt127"],
    ),
    (
        ("machine127 learning127 model127 token127 prompt127 session127", 6),
        ["machine127", "learning127", "model127", "token127", "prompt127", "session127"],
    ),
    (
        ("machine127 learning127 model127 token127 prompt127 session127", 10),
        ["machine127", "learning127", "model127", "token127", "prompt127", "session127"],
    ),
    (
        ("machine127 learning127 model127 token127 prompt127 session127", 18),
        ["machine127", "learning127", "model127 token127", "prompt127", "session127"],
    ),
    (
        ("machine127 learning127 model127 token127 prompt127 session127", 28),
        ["machine127 learning127", "model127 token127 prompt127", "session127"],
    ),
    (
        ("learning127 model127 token127 prompt127 session127 library127", 6),
        ["learning127", "model127", "token127", "prompt127", "session127", "library127"],
    ),
    (
        ("learning127 model127 token127 prompt127 session127 library127", 10),
        ["learning127", "model127", "token127", "prompt127", "session127", "library127"],
    ),
    (
        ("learning127 model127 token127 prompt127 session127 library127", 18),
        ["learning127", "model127 token127", "prompt127", "session127", "library127"],
    ),
    (
        ("learning127 model127 token127 prompt127 session127 library127", 28),
        ["learning127 model127", "token127 prompt127", "session127 library127"],
    ),
    (
        ("model127 token127 prompt127 session127 library127 service127", 6),
        ["model127", "token127", "prompt127", "session127", "library127", "service127"],
    ),
    (
        ("model127 token127 prompt127 session127 library127 service127", 10),
        ["model127", "token127", "prompt127", "session127", "library127", "service127"],
    ),
    (
        ("model127 token127 prompt127 session127 library127 service127", 18),
        ["model127 token127", "prompt127", "session127", "library127", "service127"],
    ),
    (
        ("model127 token127 prompt127 session127 library127 service127", 28),
        ["model127 token127 prompt127", "session127 library127", "service127"],
    ),
    (
        ("token127 prompt127 session127 library127 service127 gateway127", 6),
        ["token127", "prompt127", "session127", "library127", "service127", "gateway127"],
    ),
    (
        ("token127 prompt127 session127 library127 service127 gateway127", 10),
        ["token127", "prompt127", "session127", "library127", "service127", "gateway127"],
    ),
    (
        ("token127 prompt127 session127 library127 service127 gateway127", 18),
        ["token127 prompt127", "session127", "library127", "service127", "gateway127"],
    ),
    (
        ("token127 prompt127 session127 library127 service127 gateway127", 28),
        ["token127 prompt127", "session127 library127", "service127 gateway127"],
    ),
    (
        ("prompt127 session127 library127 service127 gateway127 storage127", 6),
        ["prompt127", "session127", "library127", "service127", "gateway127", "storage127"],
    ),
    (
        ("prompt127 session127 library127 service127 gateway127 storage127", 10),
        ["prompt127", "session127", "library127", "service127", "gateway127", "storage127"],
    ),
    (
        ("prompt127 session127 library127 service127 gateway127 storage127", 18),
        ["prompt127", "session127", "library127", "service127", "gateway127", "storage127"],
    ),
    (
        ("prompt127 session127 library127 service127 gateway127 storage127", 28),
        ["prompt127 session127", "library127 service127", "gateway127 storage127"],
    ),
    (
        ("session127 library127 service127 gateway127 storage127 network127", 6),
        ["session127", "library127", "service127", "gateway127", "storage127", "network127"],
    ),
    (
        ("session127 library127 service127 gateway127 storage127 network127", 10),
        ["session127", "library127", "service127", "gateway127", "storage127", "network127"],
    ),
    (
        ("session127 library127 service127 gateway127 storage127 network127", 18),
        ["session127", "library127", "service127", "gateway127", "storage127", "network127"],
    ),
    (
        ("session127 library127 service127 gateway127 storage127 network127", 28),
        ["session127 library127", "service127 gateway127", "storage127 network127"],
    ),
    (
        ("library127 service127 gateway127 storage127 network127 latency127", 6),
        ["library127", "service127", "gateway127", "storage127", "network127", "latency127"],
    ),
    (
        ("library127 service127 gateway127 storage127 network127 latency127", 10),
        ["library127", "service127", "gateway127", "storage127", "network127", "latency127"],
    ),
    (
        ("library127 service127 gateway127 storage127 network127 latency127", 18),
        ["library127", "service127", "gateway127", "storage127", "network127", "latency127"],
    ),
    (
        ("library127 service127 gateway127 storage127 network127 latency127", 28),
        ["library127 service127", "gateway127 storage127", "network127 latency127"],
    ),
    (
        ("service127 gateway127 storage127 network127 latency127 buffer127", 6),
        ["service127", "gateway127", "storage127", "network127", "latency127", "buffer127"],
    ),
    (
        ("service127 gateway127 storage127 network127 latency127 buffer127", 10),
        ["service127", "gateway127", "storage127", "network127", "latency127", "buffer127"],
    ),
    (
        ("service127 gateway127 storage127 network127 latency127 buffer127", 18),
        ["service127", "gateway127", "storage127", "network127", "latency127", "buffer127"],
    ),
    (
        ("service127 gateway127 storage127 network127 latency127 buffer127", 28),
        ["service127 gateway127", "storage127 network127", "latency127 buffer127"],
    ),
    (
        ("gateway127 storage127 network127 latency127 buffer127 queue127", 6),
        ["gateway127", "storage127", "network127", "latency127", "buffer127", "queue127"],
    ),
    (
        ("gateway127 storage127 network127 latency127 buffer127 queue127", 10),
        ["gateway127", "storage127", "network127", "latency127", "buffer127", "queue127"],
    ),
    (
        ("gateway127 storage127 network127 latency127 buffer127 queue127", 18),
        ["gateway127", "storage127", "network127", "latency127", "buffer127 queue127"],
    ),
    (
        ("gateway127 storage127 network127 latency127 buffer127 queue127", 28),
        ["gateway127 storage127", "network127 latency127", "buffer127 queue127"],
    ),
    (
        ("storage127 network127 latency127 buffer127 queue127 worker127", 6),
        ["storage127", "network127", "latency127", "buffer127", "queue127", "worker127"],
    ),
    (
        ("storage127 network127 latency127 buffer127 queue127 worker127", 10),
        ["storage127", "network127", "latency127", "buffer127", "queue127", "worker127"],
    ),
    (
        ("storage127 network127 latency127 buffer127 queue127 worker127", 18),
        ["storage127", "network127", "latency127", "buffer127 queue127", "worker127"],
    ),
    (
        ("storage127 network127 latency127 buffer127 queue127 worker127", 28),
        ["storage127 network127", "latency127 buffer127", "queue127 worker127"],
    ),
    (
        ("network127 latency127 buffer127 queue127 worker127 kernel127", 6),
        ["network127", "latency127", "buffer127", "queue127", "worker127", "kernel127"],
    ),
    (
        ("network127 latency127 buffer127 queue127 worker127 kernel127", 10),
        ["network127", "latency127", "buffer127", "queue127", "worker127", "kernel127"],
    ),
    (
        ("network127 latency127 buffer127 queue127 worker127 kernel127", 18),
        ["network127", "latency127", "buffer127 queue127", "worker127", "kernel127"],
    ),
    (
        ("network127 latency127 buffer127 queue127 worker127 kernel127", 28),
        ["network127 latency127", "buffer127 queue127 worker127", "kernel127"],
    ),
    (
        ("latency127 buffer127 queue127 worker127 kernel127 signal127", 6),
        ["latency127", "buffer127", "queue127", "worker127", "kernel127", "signal127"],
    ),
    (
        ("latency127 buffer127 queue127 worker127 kernel127 signal127", 10),
        ["latency127", "buffer127", "queue127", "worker127", "kernel127", "signal127"],
    ),
    (
        ("latency127 buffer127 queue127 worker127 kernel127 signal127", 18),
        ["latency127", "buffer127 queue127", "worker127", "kernel127", "signal127"],
    ),
    (
        ("latency127 buffer127 queue127 worker127 kernel127 signal127", 28),
        ["latency127 buffer127", "queue127 worker127 kernel127", "signal127"],
    ),
    (
        ("buffer127 queue127 worker127 kernel127 signal127 packet127", 6),
        ["buffer127", "queue127", "worker127", "kernel127", "signal127", "packet127"],
    ),
    (
        ("buffer127 queue127 worker127 kernel127 signal127 packet127", 10),
        ["buffer127", "queue127", "worker127", "kernel127", "signal127", "packet127"],
    ),
    (
        ("buffer127 queue127 worker127 kernel127 signal127 packet127", 18),
        ["buffer127 queue127", "worker127", "kernel127", "signal127", "packet127"],
    ),
    (
        ("buffer127 queue127 worker127 kernel127 signal127 packet127", 28),
        ["buffer127 queue127 worker127", "kernel127 signal127", "packet127"],
    ),
    (
        ("queue127 worker127 kernel127 signal127 packet127 router127", 6),
        ["queue127", "worker127", "kernel127", "signal127", "packet127", "router127"],
    ),
    (
        ("queue127 worker127 kernel127 signal127 packet127 router127", 10),
        ["queue127", "worker127", "kernel127", "signal127", "packet127", "router127"],
    ),
    (
        ("queue127 worker127 kernel127 signal127 packet127 router127", 18),
        ["queue127 worker127", "kernel127", "signal127", "packet127", "router127"],
    ),
    (
        ("queue127 worker127 kernel127 signal127 packet127 router127", 28),
        ["queue127 worker127 kernel127", "signal127 packet127", "router127"],
    ),
    (
        ("worker127 kernel127 signal127 packet127 router127 cluster127", 6),
        ["worker127", "kernel127", "signal127", "packet127", "router127", "cluster127"],
    ),
    (
        ("worker127 kernel127 signal127 packet127 router127 cluster127", 10),
        ["worker127", "kernel127", "signal127", "packet127", "router127", "cluster127"],
    ),
    (
        ("worker127 kernel127 signal127 packet127 router127 cluster127", 18),
        ["worker127", "kernel127", "signal127", "packet127", "router127", "cluster127"],
    ),
    (
        ("worker127 kernel127 signal127 packet127 router127 cluster127", 28),
        ["worker127 kernel127", "signal127 packet127", "router127 cluster127"],
    ),
    (
        ("kernel127 signal127 packet127 router127 cluster127 mirror127", 6),
        ["kernel127", "signal127", "packet127", "router127", "cluster127", "mirror127"],
    ),
    (
        ("kernel127 signal127 packet127 router127 cluster127 mirror127", 10),
        ["kernel127", "signal127", "packet127", "router127", "cluster127", "mirror127"],
    ),
    (
        ("kernel127 signal127 packet127 router127 cluster127 mirror127", 18),
        ["kernel127", "signal127", "packet127", "router127", "cluster127", "mirror127"],
    ),
    (
        ("kernel127 signal127 packet127 router127 cluster127 mirror127", 28),
        ["kernel127 signal127", "packet127 router127", "cluster127 mirror127"],
    ),
    (
        ("signal127 packet127 router127 cluster127 mirror127 filter127", 6),
        ["signal127", "packet127", "router127", "cluster127", "mirror127", "filter127"],
    ),
    (
        ("signal127 packet127 router127 cluster127 mirror127 filter127", 10),
        ["signal127", "packet127", "router127", "cluster127", "mirror127", "filter127"],
    ),
    (
        ("signal127 packet127 router127 cluster127 mirror127 filter127", 18),
        ["signal127", "packet127", "router127", "cluster127", "mirror127", "filter127"],
    ),
    (
        ("signal127 packet127 router127 cluster127 mirror127 filter127", 28),
        ["signal127 packet127", "router127 cluster127", "mirror127 filter127"],
    ),
    (
        ("packet127 router127 cluster127 mirror127 filter127 ranking127", 6),
        ["packet127", "router127", "cluster127", "mirror127", "filter127", "ranking127"],
    ),
    (
        ("packet127 router127 cluster127 mirror127 filter127 ranking127", 10),
        ["packet127", "router127", "cluster127", "mirror127", "filter127", "ranking127"],
    ),
    (
        ("packet127 router127 cluster127 mirror127 filter127 ranking127", 18),
        ["packet127", "router127", "cluster127", "mirror127", "filter127", "ranking127"],
    ),
    (
        ("packet127 router127 cluster127 mirror127 filter127 ranking127", 28),
        ["packet127 router127", "cluster127 mirror127", "filter127 ranking127"],
    ),
    (
        ("router127 cluster127 mirror127 filter127 ranking127 encoding127", 6),
        ["router127", "cluster127", "mirror127", "filter127", "ranking127", "encoding127"],
    ),
    (
        ("router127 cluster127 mirror127 filter127 ranking127 encoding127", 10),
        ["router127", "cluster127", "mirror127", "filter127", "ranking127", "encoding127"],
    ),
    (
        ("router127 cluster127 mirror127 filter127 ranking127 encoding127", 18),
        ["router127", "cluster127", "mirror127", "filter127", "ranking127", "encoding127"],
    ),
    (
        ("router127 cluster127 mirror127 filter127 ranking127 encoding127", 28),
        ["router127 cluster127", "mirror127 filter127", "ranking127 encoding127"],
    ),
    (
        ("cluster127 mirror127 filter127 ranking127 encoding127 mapping127", 6),
        ["cluster127", "mirror127", "filter127", "ranking127", "encoding127", "mapping127"],
    ),
    (
        ("cluster127 mirror127 filter127 ranking127 encoding127 mapping127", 10),
        ["cluster127", "mirror127", "filter127", "ranking127", "encoding127", "mapping127"],
    ),
    (
        ("cluster127 mirror127 filter127 ranking127 encoding127 mapping127", 18),
        ["cluster127", "mirror127", "filter127", "ranking127", "encoding127", "mapping127"],
    ),
    (
        ("cluster127 mirror127 filter127 ranking127 encoding127 mapping127", 28),
        ["cluster127 mirror127", "filter127 ranking127", "encoding127 mapping127"],
    ),
    (
        ("mirror127 filter127 ranking127 encoding127 mapping127 record127", 6),
        ["mirror127", "filter127", "ranking127", "encoding127", "mapping127", "record127"],
    ),
    (
        ("mirror127 filter127 ranking127 encoding127 mapping127 record127", 10),
        ["mirror127", "filter127", "ranking127", "encoding127", "mapping127", "record127"],
    ),
    (
        ("mirror127 filter127 ranking127 encoding127 mapping127 record127", 18),
        ["mirror127", "filter127", "ranking127", "encoding127", "mapping127", "record127"],
    ),
    (
        ("mirror127 filter127 ranking127 encoding127 mapping127 record127", 28),
        ["mirror127 filter127", "ranking127 encoding127", "mapping127 record127"],
    ),
    (
        ("filter127 ranking127 encoding127 mapping127 record127 candle127", 6),
        ["filter127", "ranking127", "encoding127", "mapping127", "record127", "candle127"],
    ),
    (
        ("filter127 ranking127 encoding127 mapping127 record127 candle127", 10),
        ["filter127", "ranking127", "encoding127", "mapping127", "record127", "candle127"],
    ),
    (
        ("filter127 ranking127 encoding127 mapping127 record127 candle127", 18),
        ["filter127", "ranking127", "encoding127", "mapping127", "record127", "candle127"],
    ),
    (
        ("filter127 ranking127 encoding127 mapping127 record127 candle127", 28),
        ["filter127 ranking127", "encoding127 mapping127", "record127 candle127"],
    ),
    (
        ("ranking127 encoding127 mapping127 record127 candle127 thread127", 6),
        ["ranking127", "encoding127", "mapping127", "record127", "candle127", "thread127"],
    ),
    (
        ("ranking127 encoding127 mapping127 record127 candle127 thread127", 10),
        ["ranking127", "encoding127", "mapping127", "record127", "candle127", "thread127"],
    ),
    (
        ("ranking127 encoding127 mapping127 record127 candle127 thread127", 18),
        ["ranking127", "encoding127", "mapping127", "record127", "candle127", "thread127"],
    ),
    (
        ("ranking127 encoding127 mapping127 record127 candle127 thread127", 28),
        ["ranking127 encoding127", "mapping127 record127", "candle127 thread127"],
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
