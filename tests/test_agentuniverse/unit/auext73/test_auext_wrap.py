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
        ("round 73: the quick brown fox jumps over the lazy dog", 4),
        ["round", "73:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 73: the quick brown fox jumps over the lazy dog", 8),
        ["round", "73: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 73: the quick brown fox jumps over the lazy dog", 12),
        ["round 73:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 73: the quick brown fox jumps over the lazy dog", 16),
        ["round 73: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 73: the quick brown fox jumps over the lazy dog", 24),
        ["round 73: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 73: the quick brown fox jumps over the lazy dog", 32),
        ["round 73: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 73: agentuniverse is a framework for multi agents", 4),
        ["round", "73:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 73: agentuniverse is a framework for multi agents", 8),
        ["round", "73:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 73: agentuniverse is a framework for multi agents", 12),
        ["round 73:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 73: agentuniverse is a framework for multi agents", 16),
        ["round 73:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 73: agentuniverse is a framework for multi agents", 24),
        ["round 73: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 73: agentuniverse is a framework for multi agents", 32),
        ["round 73: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 73: knowledge stored as vectors enables retrieval", 4),
        ["round", "73:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 73: knowledge stored as vectors enables retrieval", 8),
        ["round", "73:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 73: knowledge stored as vectors enables retrieval", 12),
        ["round 73:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 73: knowledge stored as vectors enables retrieval", 16),
        ["round 73:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 73: knowledge stored as vectors enables retrieval", 24),
        ["round 73: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 73: knowledge stored as vectors enables retrieval", 32),
        ["round 73: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 73: the processor reads the record then stops", 4),
        ["round", "73:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 73: the processor reads the record then stops", 8),
        ["round", "73: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 73: the processor reads the record then stops", 12),
        ["round 73:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 73: the processor reads the record then stops", 16),
        ["round 73: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 73: the processor reads the record then stops", 24),
        ["round 73: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 73: the processor reads the record then stops", 32),
        ["round 73: the processor reads", "the record then stops"],
    ),
    (
        ("round 73: a worker pulls the next task from the queue", 4),
        ["round", "73:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 73: a worker pulls the next task from the queue", 8),
        ["round", "73: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 73: a worker pulls the next task from the queue", 12),
        ["round 73: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 73: a worker pulls the next task from the queue", 16),
        ["round 73: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 73: a worker pulls the next task from the queue", 24),
        ["round 73: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 73: a worker pulls the next task from the queue", 32),
        ["round 73: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 73: signals travel through the network layer", 4),
        ["round", "73:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 73: signals travel through the network layer", 8),
        ["round", "73:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 73: signals travel through the network layer", 12),
        ["round 73:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 73: signals travel through the network layer", 16),
        ["round 73:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 73: signals travel through the network layer", 24),
        ["round 73: signals travel", "through the network", "layer"],
    ),
    (
        ("round 73: signals travel through the network layer", 32),
        ["round 73: signals travel through", "the network layer"],
    ),
    (
        ("round 73: the gateway routes each request by policy", 4),
        ["round", "73:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 73: the gateway routes each request by policy", 8),
        ["round", "73: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 73: the gateway routes each request by policy", 12),
        ["round 73:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 73: the gateway routes each request by policy", 16),
        ["round 73: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 73: the gateway routes each request by policy", 24),
        ["round 73: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 73: the gateway routes each request by policy", 32),
        ["round 73: the gateway routes", "each request by policy"],
    ),
    (
        ("round 73: memory grows until the buffer is full", 4),
        ["round", "73:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 73: memory grows until the buffer is full", 8),
        ["round", "73:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 73: memory grows until the buffer is full", 12),
        ["round 73:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 73: memory grows until the buffer is full", 16),
        ["round 73: memory", "grows until the", "buffer is full"],
    ),
    (("round 73: memory grows until the buffer is full", 24), ["round 73: memory grows", "until the buffer is full"]),
    (("round 73: memory grows until the buffer is full", 32), ["round 73: memory grows until the", "buffer is full"]),
    (
        ("round 73: the cluster mirrors every packet twice", 4),
        ["round", "73:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 73: the cluster mirrors every packet twice", 8),
        ["round", "73: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 73: the cluster mirrors every packet twice", 12),
        ["round 73:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 73: the cluster mirrors every packet twice", 16),
        ["round 73: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 73: the cluster mirrors every packet twice", 24),
        ["round 73: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 73: the cluster mirrors every packet twice", 32), ["round 73: the cluster mirrors", "every packet twice"]),
    (
        ("round 73: ranking uses tokens learned from the corpus", 4),
        ["round", "73:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 73: ranking uses tokens learned from the corpus", 8),
        ["round", "73:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 73: ranking uses tokens learned from the corpus", 12),
        ["round 73:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 73: ranking uses tokens learned from the corpus", 16),
        ["round 73:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 73: ranking uses tokens learned from the corpus", 24),
        ["round 73: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 73: ranking uses tokens learned from the corpus", 32),
        ["round 73: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 73: a long session ends when the candle dies", 4),
        ["round", "73:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 73: a long session ends when the candle dies", 8),
        ["round", "73: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 73: a long session ends when the candle dies", 12),
        ["round 73: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 73: a long session ends when the candle dies", 16),
        ["round 73: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 73: a long session ends when the candle dies", 24),
        ["round 73: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 73: a long session ends when the candle dies", 32),
        ["round 73: a long session ends", "when the candle dies"],
    ),
    (
        ("round 73: encode the prompt then map the result", 4),
        ["round", "73:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 73: encode the prompt then map the result", 8),
        ["round", "73:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 73: encode the prompt then map the result", 12),
        ["round 73:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 73: encode the prompt then map the result", 16),
        ["round 73: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 73: encode the prompt then map the result", 24),
        ["round 73: encode the", "prompt then map the", "result"],
    ),
    (("round 73: encode the prompt then map the result", 32), ["round 73: encode the prompt then", "map the result"]),
    (
        ("round 73: the kernel wakes the worker at dawn", 4),
        ["round", "73:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 73: the kernel wakes the worker at dawn", 8),
        ["round", "73: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 73: the kernel wakes the worker at dawn", 12),
        ["round 73:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 73: the kernel wakes the worker at dawn", 16), ["round 73: the", "kernel wakes the", "worker at dawn"]),
    (("round 73: the kernel wakes the worker at dawn", 24), ["round 73: the kernel", "wakes the worker at dawn"]),
    (("round 73: the kernel wakes the worker at dawn", 32), ["round 73: the kernel wakes the", "worker at dawn"]),
    (
        ("round 73: service latency drops after the patch", 4),
        ["round", "73:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 73: service latency drops after the patch", 8),
        ["round", "73:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 73: service latency drops after the patch", 12),
        ["round 73:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 73: service latency drops after the patch", 16),
        ["round 73:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 73: service latency drops after the patch", 24),
        ["round 73: service", "latency drops after the", "patch"],
    ),
    (("round 73: service latency drops after the patch", 32), ["round 73: service latency drops", "after the patch"]),
    (
        ("round 73: the library caches every vector it sees", 4),
        ["round", "73:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 73: the library caches every vector it sees", 8),
        ["round", "73: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 73: the library caches every vector it sees", 12),
        ["round 73:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 73: the library caches every vector it sees", 16),
        ["round 73: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 73: the library caches every vector it sees", 24),
        ["round 73: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 73: the library caches every vector it sees", 32),
        ["round 73: the library caches", "every vector it sees"],
    ),
    (
        ("round 73: agents argue then the debate resolves", 4),
        ["round", "73:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 73: agents argue then the debate resolves", 8),
        ["round", "73:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 73: agents argue then the debate resolves", 12),
        ["round 73:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 73: agents argue then the debate resolves", 16),
        ["round 73: agents", "argue then the", "debate resolves"],
    ),
    (("round 73: agents argue then the debate resolves", 24), ["round 73: agents argue", "then the debate resolves"]),
    (("round 73: agents argue then the debate resolves", 32), ["round 73: agents argue then the", "debate resolves"]),
    (
        ("round 73: the filter keeps only strong matches", 4),
        ["round", "73:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 73: the filter keeps only strong matches", 8),
        ["round", "73: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 73: the filter keeps only strong matches", 12),
        ["round 73:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 73: the filter keeps only strong matches", 16),
        ["round 73: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 73: the filter keeps only strong matches", 24), ["round 73: the filter", "keeps only strong", "matches"]),
    (("round 73: the filter keeps only strong matches", 32), ["round 73: the filter keeps only", "strong matches"]),
    (
        ("round 73: the model answers with a short reply", 4),
        ["round", "73:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 73: the model answers with a short reply", 8),
        ["round", "73: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 73: the model answers with a short reply", 12),
        ["round 73:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 73: the model answers with a short reply", 16),
        ["round 73: the", "model answers", "with a short", "reply"],
    ),
    (("round 73: the model answers with a short reply", 24), ["round 73: the model", "answers with a short", "reply"]),
    (("round 73: the model answers with a short reply", 32), ["round 73: the model answers with", "a short reply"]),
    (
        ("round 73: the recorder stores the reasoning trace", 4),
        ["round", "73:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 73: the recorder stores the reasoning trace", 8),
        ["round", "73: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 73: the recorder stores the reasoning trace", 12),
        ["round 73:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 73: the recorder stores the reasoning trace", 16),
        ["round 73: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 73: the recorder stores the reasoning trace", 24),
        ["round 73: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 73: the recorder stores the reasoning trace", 32),
        ["round 73: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 73: the angel watches the processor run", 4),
        ["round", "73:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 73: the angel watches the processor run", 8),
        ["round", "73: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 73: the angel watches the processor run", 12),
        ["round 73:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 73: the angel watches the processor run", 16), ["round 73: the", "angel watches", "the processor", "run"]),
    (("round 73: the angel watches the processor run", 24), ["round 73: the angel", "watches the processor", "run"]),
    (("round 73: the angel watches the processor run", 32), ["round 73: the angel watches the", "processor run"]),
    (
        ("round 73: angle of the vector decides the match", 4),
        ["round", "73:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 73: angle of the vector decides the match", 8),
        ["round", "73:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 73: angle of the vector decides the match", 12),
        ["round 73:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 73: angle of the vector decides the match", 16),
        ["round 73: angle", "of the vector", "decides the", "match"],
    ),
    (("round 73: angle of the vector decides the match", 24), ["round 73: angle of the", "vector decides the match"]),
    (("round 73: angle of the vector decides the match", 32), ["round 73: angle of the vector", "decides the match"]),
    (
        ("round 73: the candle burns twice as long at night", 4),
        ["round", "73:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 73: the candle burns twice as long at night", 8),
        ["round", "73: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 73: the candle burns twice as long at night", 12),
        ["round 73:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 73: the candle burns twice as long at night", 16),
        ["round 73: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 73: the candle burns twice as long at night", 24),
        ["round 73: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 73: the candle burns twice as long at night", 32),
        ["round 73: the candle burns twice", "as long at night"],
    ),
    (
        ("round 73: a mirror of the universe in one line", 4),
        ["round", "73:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 73: a mirror of the universe in one line", 8),
        ["round", "73: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 73: a mirror of the universe in one line", 12),
        ["round 73: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 73: a mirror of the universe in one line", 16),
        ["round 73: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 73: a mirror of the universe in one line", 24), ["round 73: a mirror of", "the universe in one line"]),
    (("round 73: a mirror of the universe in one line", 32), ["round 73: a mirror of the", "universe in one line"]),
    (
        ("round 73: the queue drains before the storm", 4),
        ["round", "73:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 73: the queue drains before the storm", 8),
        ["round", "73: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 73: the queue drains before the storm", 12), ["round 73:", "the queue", "drains", "before the", "storm"]),
    (("round 73: the queue drains before the storm", 16), ["round 73: the", "queue drains", "before the storm"]),
    (("round 73: the queue drains before the storm", 24), ["round 73: the queue", "drains before the storm"]),
    (("round 73: the queue drains before the storm", 32), ["round 73: the queue drains", "before the storm"]),
    (
        ("kitten73 sitting73 agent73 angle73 universe73 memory73", 6),
        ["kitten73", "sitting73", "agent73", "angle73", "universe73", "memory73"],
    ),
    (
        ("kitten73 sitting73 agent73 angle73 universe73 memory73", 10),
        ["kitten73", "sitting73", "agent73", "angle73", "universe73", "memory73"],
    ),
    (
        ("kitten73 sitting73 agent73 angle73 universe73 memory73", 18),
        ["kitten73 sitting73", "agent73 angle73", "universe73", "memory73"],
    ),
    (
        ("kitten73 sitting73 agent73 angle73 universe73 memory73", 28),
        ["kitten73 sitting73 agent73", "angle73 universe73 memory73"],
    ),
    (
        ("sitting73 agent73 angle73 universe73 memory73 stream73", 6),
        ["sitting73", "agent73", "angle73", "universe73", "memory73", "stream73"],
    ),
    (
        ("sitting73 agent73 angle73 universe73 memory73 stream73", 10),
        ["sitting73", "agent73", "angle73", "universe73", "memory73", "stream73"],
    ),
    (
        ("sitting73 agent73 angle73 universe73 memory73 stream73", 18),
        ["sitting73 agent73", "angle73 universe73", "memory73 stream73"],
    ),
    (
        ("sitting73 agent73 angle73 universe73 memory73 stream73", 28),
        ["sitting73 agent73 angle73", "universe73 memory73 stream73"],
    ),
    (
        ("agent73 angle73 universe73 memory73 stream73 context73", 6),
        ["agent73", "angle73", "universe73", "memory73", "stream73", "context73"],
    ),
    (
        ("agent73 angle73 universe73 memory73 stream73 context73", 10),
        ["agent73", "angle73", "universe73", "memory73", "stream73", "context73"],
    ),
    (
        ("agent73 angle73 universe73 memory73 stream73 context73", 18),
        ["agent73 angle73", "universe73", "memory73 stream73", "context73"],
    ),
    (
        ("agent73 angle73 universe73 memory73 stream73 context73", 28),
        ["agent73 angle73 universe73", "memory73 stream73 context73"],
    ),
    (
        ("angle73 universe73 memory73 stream73 context73 knowledge73", 6),
        ["angle73", "universe73", "memory73", "stream73", "context73", "knowledge73"],
    ),
    (
        ("angle73 universe73 memory73 stream73 context73 knowledge73", 10),
        ["angle73", "universe73", "memory73", "stream73", "context73", "knowledge73"],
    ),
    (
        ("angle73 universe73 memory73 stream73 context73 knowledge73", 18),
        ["angle73 universe73", "memory73 stream73", "context73", "knowledge73"],
    ),
    (
        ("angle73 universe73 memory73 stream73 context73 knowledge73", 28),
        ["angle73 universe73 memory73", "stream73 context73", "knowledge73"],
    ),
    (
        ("universe73 memory73 stream73 context73 knowledge73 vector73", 6),
        ["universe73", "memory73", "stream73", "context73", "knowledge73", "vector73"],
    ),
    (
        ("universe73 memory73 stream73 context73 knowledge73 vector73", 10),
        ["universe73", "memory73", "stream73", "context73", "knowledge73", "vector73"],
    ),
    (
        ("universe73 memory73 stream73 context73 knowledge73 vector73", 18),
        ["universe73", "memory73 stream73", "context73", "knowledge73", "vector73"],
    ),
    (
        ("universe73 memory73 stream73 context73 knowledge73 vector73", 28),
        ["universe73 memory73 stream73", "context73 knowledge73", "vector73"],
    ),
    (
        ("memory73 stream73 context73 knowledge73 vector73 processor73", 6),
        ["memory73", "stream73", "context73", "knowledge73", "vector73", "processor73"],
    ),
    (
        ("memory73 stream73 context73 knowledge73 vector73 processor73", 10),
        ["memory73", "stream73", "context73", "knowledge73", "vector73", "processor73"],
    ),
    (
        ("memory73 stream73 context73 knowledge73 vector73 processor73", 18),
        ["memory73 stream73", "context73", "knowledge73", "vector73", "processor73"],
    ),
    (
        ("memory73 stream73 context73 knowledge73 vector73 processor73", 28),
        ["memory73 stream73 context73", "knowledge73 vector73", "processor73"],
    ),
    (
        ("stream73 context73 knowledge73 vector73 processor73 reasoning73", 6),
        ["stream73", "context73", "knowledge73", "vector73", "processor73", "reasoning73"],
    ),
    (
        ("stream73 context73 knowledge73 vector73 processor73 reasoning73", 10),
        ["stream73", "context73", "knowledge73", "vector73", "processor73", "reasoning73"],
    ),
    (
        ("stream73 context73 knowledge73 vector73 processor73 reasoning73", 18),
        ["stream73 context73", "knowledge73", "vector73", "processor73", "reasoning73"],
    ),
    (
        ("stream73 context73 knowledge73 vector73 processor73 reasoning73", 28),
        ["stream73 context73", "knowledge73 vector73", "processor73 reasoning73"],
    ),
    (
        ("context73 knowledge73 vector73 processor73 reasoning73 machine73", 6),
        ["context73", "knowledge73", "vector73", "processor73", "reasoning73", "machine73"],
    ),
    (
        ("context73 knowledge73 vector73 processor73 reasoning73 machine73", 10),
        ["context73", "knowledge73", "vector73", "processor73", "reasoning73", "machine73"],
    ),
    (
        ("context73 knowledge73 vector73 processor73 reasoning73 machine73", 18),
        ["context73", "knowledge73", "vector73", "processor73", "reasoning73", "machine73"],
    ),
    (
        ("context73 knowledge73 vector73 processor73 reasoning73 machine73", 28),
        ["context73 knowledge73", "vector73 processor73", "reasoning73 machine73"],
    ),
    (
        ("knowledge73 vector73 processor73 reasoning73 machine73 learning73", 6),
        ["knowledge73", "vector73", "processor73", "reasoning73", "machine73", "learning73"],
    ),
    (
        ("knowledge73 vector73 processor73 reasoning73 machine73 learning73", 10),
        ["knowledge73", "vector73", "processor73", "reasoning73", "machine73", "learning73"],
    ),
    (
        ("knowledge73 vector73 processor73 reasoning73 machine73 learning73", 18),
        ["knowledge73", "vector73", "processor73", "reasoning73", "machine73", "learning73"],
    ),
    (
        ("knowledge73 vector73 processor73 reasoning73 machine73 learning73", 28),
        ["knowledge73 vector73", "processor73 reasoning73", "machine73 learning73"],
    ),
    (
        ("vector73 processor73 reasoning73 machine73 learning73 model73", 6),
        ["vector73", "processor73", "reasoning73", "machine73", "learning73", "model73"],
    ),
    (
        ("vector73 processor73 reasoning73 machine73 learning73 model73", 10),
        ["vector73", "processor73", "reasoning73", "machine73", "learning73", "model73"],
    ),
    (
        ("vector73 processor73 reasoning73 machine73 learning73 model73", 18),
        ["vector73", "processor73", "reasoning73", "machine73", "learning73 model73"],
    ),
    (
        ("vector73 processor73 reasoning73 machine73 learning73 model73", 28),
        ["vector73 processor73", "reasoning73 machine73", "learning73 model73"],
    ),
    (
        ("processor73 reasoning73 machine73 learning73 model73 token73", 6),
        ["processor73", "reasoning73", "machine73", "learning73", "model73", "token73"],
    ),
    (
        ("processor73 reasoning73 machine73 learning73 model73 token73", 10),
        ["processor73", "reasoning73", "machine73", "learning73", "model73", "token73"],
    ),
    (
        ("processor73 reasoning73 machine73 learning73 model73 token73", 18),
        ["processor73", "reasoning73", "machine73", "learning73 model73", "token73"],
    ),
    (
        ("processor73 reasoning73 machine73 learning73 model73 token73", 28),
        ["processor73 reasoning73", "machine73 learning73 model73", "token73"],
    ),
    (
        ("reasoning73 machine73 learning73 model73 token73 prompt73", 6),
        ["reasoning73", "machine73", "learning73", "model73", "token73", "prompt73"],
    ),
    (
        ("reasoning73 machine73 learning73 model73 token73 prompt73", 10),
        ["reasoning73", "machine73", "learning73", "model73", "token73", "prompt73"],
    ),
    (
        ("reasoning73 machine73 learning73 model73 token73 prompt73", 18),
        ["reasoning73", "machine73", "learning73 model73", "token73 prompt73"],
    ),
    (
        ("reasoning73 machine73 learning73 model73 token73 prompt73", 28),
        ["reasoning73 machine73", "learning73 model73 token73", "prompt73"],
    ),
    (
        ("machine73 learning73 model73 token73 prompt73 session73", 6),
        ["machine73", "learning73", "model73", "token73", "prompt73", "session73"],
    ),
    (
        ("machine73 learning73 model73 token73 prompt73 session73", 10),
        ["machine73", "learning73", "model73", "token73", "prompt73", "session73"],
    ),
    (
        ("machine73 learning73 model73 token73 prompt73 session73", 18),
        ["machine73", "learning73 model73", "token73 prompt73", "session73"],
    ),
    (
        ("machine73 learning73 model73 token73 prompt73 session73", 28),
        ["machine73 learning73 model73", "token73 prompt73 session73"],
    ),
    (
        ("learning73 model73 token73 prompt73 session73 library73", 6),
        ["learning73", "model73", "token73", "prompt73", "session73", "library73"],
    ),
    (
        ("learning73 model73 token73 prompt73 session73 library73", 10),
        ["learning73", "model73", "token73", "prompt73", "session73", "library73"],
    ),
    (
        ("learning73 model73 token73 prompt73 session73 library73", 18),
        ["learning73 model73", "token73 prompt73", "session73", "library73"],
    ),
    (
        ("learning73 model73 token73 prompt73 session73 library73", 28),
        ["learning73 model73 token73", "prompt73 session73 library73"],
    ),
    (
        ("model73 token73 prompt73 session73 library73 service73", 6),
        ["model73", "token73", "prompt73", "session73", "library73", "service73"],
    ),
    (
        ("model73 token73 prompt73 session73 library73 service73", 10),
        ["model73", "token73", "prompt73", "session73", "library73", "service73"],
    ),
    (
        ("model73 token73 prompt73 session73 library73 service73", 18),
        ["model73 token73", "prompt73 session73", "library73", "service73"],
    ),
    (
        ("model73 token73 prompt73 session73 library73 service73", 28),
        ["model73 token73 prompt73", "session73 library73", "service73"],
    ),
    (
        ("token73 prompt73 session73 library73 service73 gateway73", 6),
        ["token73", "prompt73", "session73", "library73", "service73", "gateway73"],
    ),
    (
        ("token73 prompt73 session73 library73 service73 gateway73", 10),
        ["token73", "prompt73", "session73", "library73", "service73", "gateway73"],
    ),
    (
        ("token73 prompt73 session73 library73 service73 gateway73", 18),
        ["token73 prompt73", "session73", "library73", "service73", "gateway73"],
    ),
    (
        ("token73 prompt73 session73 library73 service73 gateway73", 28),
        ["token73 prompt73 session73", "library73 service73", "gateway73"],
    ),
    (
        ("prompt73 session73 library73 service73 gateway73 storage73", 6),
        ["prompt73", "session73", "library73", "service73", "gateway73", "storage73"],
    ),
    (
        ("prompt73 session73 library73 service73 gateway73 storage73", 10),
        ["prompt73", "session73", "library73", "service73", "gateway73", "storage73"],
    ),
    (
        ("prompt73 session73 library73 service73 gateway73 storage73", 18),
        ["prompt73 session73", "library73", "service73", "gateway73", "storage73"],
    ),
    (
        ("prompt73 session73 library73 service73 gateway73 storage73", 28),
        ["prompt73 session73 library73", "service73 gateway73", "storage73"],
    ),
    (
        ("session73 library73 service73 gateway73 storage73 network73", 6),
        ["session73", "library73", "service73", "gateway73", "storage73", "network73"],
    ),
    (
        ("session73 library73 service73 gateway73 storage73 network73", 10),
        ["session73", "library73", "service73", "gateway73", "storage73", "network73"],
    ),
    (
        ("session73 library73 service73 gateway73 storage73 network73", 18),
        ["session73", "library73", "service73", "gateway73", "storage73", "network73"],
    ),
    (
        ("session73 library73 service73 gateway73 storage73 network73", 28),
        ["session73 library73", "service73 gateway73", "storage73 network73"],
    ),
    (
        ("library73 service73 gateway73 storage73 network73 latency73", 6),
        ["library73", "service73", "gateway73", "storage73", "network73", "latency73"],
    ),
    (
        ("library73 service73 gateway73 storage73 network73 latency73", 10),
        ["library73", "service73", "gateway73", "storage73", "network73", "latency73"],
    ),
    (
        ("library73 service73 gateway73 storage73 network73 latency73", 18),
        ["library73", "service73", "gateway73", "storage73", "network73", "latency73"],
    ),
    (
        ("library73 service73 gateway73 storage73 network73 latency73", 28),
        ["library73 service73", "gateway73 storage73", "network73 latency73"],
    ),
    (
        ("service73 gateway73 storage73 network73 latency73 buffer73", 6),
        ["service73", "gateway73", "storage73", "network73", "latency73", "buffer73"],
    ),
    (
        ("service73 gateway73 storage73 network73 latency73 buffer73", 10),
        ["service73", "gateway73", "storage73", "network73", "latency73", "buffer73"],
    ),
    (
        ("service73 gateway73 storage73 network73 latency73 buffer73", 18),
        ["service73", "gateway73", "storage73", "network73", "latency73 buffer73"],
    ),
    (
        ("service73 gateway73 storage73 network73 latency73 buffer73", 28),
        ["service73 gateway73", "storage73 network73", "latency73 buffer73"],
    ),
    (
        ("gateway73 storage73 network73 latency73 buffer73 queue73", 6),
        ["gateway73", "storage73", "network73", "latency73", "buffer73", "queue73"],
    ),
    (
        ("gateway73 storage73 network73 latency73 buffer73 queue73", 10),
        ["gateway73", "storage73", "network73", "latency73", "buffer73", "queue73"],
    ),
    (
        ("gateway73 storage73 network73 latency73 buffer73 queue73", 18),
        ["gateway73", "storage73", "network73", "latency73 buffer73", "queue73"],
    ),
    (
        ("gateway73 storage73 network73 latency73 buffer73 queue73", 28),
        ["gateway73 storage73", "network73 latency73 buffer73", "queue73"],
    ),
    (
        ("storage73 network73 latency73 buffer73 queue73 worker73", 6),
        ["storage73", "network73", "latency73", "buffer73", "queue73", "worker73"],
    ),
    (
        ("storage73 network73 latency73 buffer73 queue73 worker73", 10),
        ["storage73", "network73", "latency73", "buffer73", "queue73", "worker73"],
    ),
    (
        ("storage73 network73 latency73 buffer73 queue73 worker73", 18),
        ["storage73", "network73", "latency73 buffer73", "queue73 worker73"],
    ),
    (
        ("storage73 network73 latency73 buffer73 queue73 worker73", 28),
        ["storage73 network73", "latency73 buffer73 queue73", "worker73"],
    ),
    (
        ("network73 latency73 buffer73 queue73 worker73 kernel73", 6),
        ["network73", "latency73", "buffer73", "queue73", "worker73", "kernel73"],
    ),
    (
        ("network73 latency73 buffer73 queue73 worker73 kernel73", 10),
        ["network73", "latency73", "buffer73", "queue73", "worker73", "kernel73"],
    ),
    (
        ("network73 latency73 buffer73 queue73 worker73 kernel73", 18),
        ["network73", "latency73 buffer73", "queue73 worker73", "kernel73"],
    ),
    (
        ("network73 latency73 buffer73 queue73 worker73 kernel73", 28),
        ["network73 latency73 buffer73", "queue73 worker73 kernel73"],
    ),
    (
        ("latency73 buffer73 queue73 worker73 kernel73 signal73", 6),
        ["latency73", "buffer73", "queue73", "worker73", "kernel73", "signal73"],
    ),
    (
        ("latency73 buffer73 queue73 worker73 kernel73 signal73", 10),
        ["latency73", "buffer73", "queue73", "worker73", "kernel73", "signal73"],
    ),
    (
        ("latency73 buffer73 queue73 worker73 kernel73 signal73", 18),
        ["latency73 buffer73", "queue73 worker73", "kernel73 signal73"],
    ),
    (
        ("latency73 buffer73 queue73 worker73 kernel73 signal73", 28),
        ["latency73 buffer73 queue73", "worker73 kernel73 signal73"],
    ),
    (
        ("buffer73 queue73 worker73 kernel73 signal73 packet73", 6),
        ["buffer73", "queue73", "worker73", "kernel73", "signal73", "packet73"],
    ),
    (
        ("buffer73 queue73 worker73 kernel73 signal73 packet73", 10),
        ["buffer73", "queue73", "worker73", "kernel73", "signal73", "packet73"],
    ),
    (
        ("buffer73 queue73 worker73 kernel73 signal73 packet73", 18),
        ["buffer73 queue73", "worker73 kernel73", "signal73 packet73"],
    ),
    (
        ("buffer73 queue73 worker73 kernel73 signal73 packet73", 28),
        ["buffer73 queue73 worker73", "kernel73 signal73 packet73"],
    ),
    (
        ("queue73 worker73 kernel73 signal73 packet73 router73", 6),
        ["queue73", "worker73", "kernel73", "signal73", "packet73", "router73"],
    ),
    (
        ("queue73 worker73 kernel73 signal73 packet73 router73", 10),
        ["queue73", "worker73", "kernel73", "signal73", "packet73", "router73"],
    ),
    (
        ("queue73 worker73 kernel73 signal73 packet73 router73", 18),
        ["queue73 worker73", "kernel73 signal73", "packet73 router73"],
    ),
    (
        ("queue73 worker73 kernel73 signal73 packet73 router73", 28),
        ["queue73 worker73 kernel73", "signal73 packet73 router73"],
    ),
    (
        ("worker73 kernel73 signal73 packet73 router73 cluster73", 6),
        ["worker73", "kernel73", "signal73", "packet73", "router73", "cluster73"],
    ),
    (
        ("worker73 kernel73 signal73 packet73 router73 cluster73", 10),
        ["worker73", "kernel73", "signal73", "packet73", "router73", "cluster73"],
    ),
    (
        ("worker73 kernel73 signal73 packet73 router73 cluster73", 18),
        ["worker73 kernel73", "signal73 packet73", "router73 cluster73"],
    ),
    (
        ("worker73 kernel73 signal73 packet73 router73 cluster73", 28),
        ["worker73 kernel73 signal73", "packet73 router73 cluster73"],
    ),
    (
        ("kernel73 signal73 packet73 router73 cluster73 mirror73", 6),
        ["kernel73", "signal73", "packet73", "router73", "cluster73", "mirror73"],
    ),
    (
        ("kernel73 signal73 packet73 router73 cluster73 mirror73", 10),
        ["kernel73", "signal73", "packet73", "router73", "cluster73", "mirror73"],
    ),
    (
        ("kernel73 signal73 packet73 router73 cluster73 mirror73", 18),
        ["kernel73 signal73", "packet73 router73", "cluster73 mirror73"],
    ),
    (
        ("kernel73 signal73 packet73 router73 cluster73 mirror73", 28),
        ["kernel73 signal73 packet73", "router73 cluster73 mirror73"],
    ),
    (
        ("signal73 packet73 router73 cluster73 mirror73 filter73", 6),
        ["signal73", "packet73", "router73", "cluster73", "mirror73", "filter73"],
    ),
    (
        ("signal73 packet73 router73 cluster73 mirror73 filter73", 10),
        ["signal73", "packet73", "router73", "cluster73", "mirror73", "filter73"],
    ),
    (
        ("signal73 packet73 router73 cluster73 mirror73 filter73", 18),
        ["signal73 packet73", "router73 cluster73", "mirror73 filter73"],
    ),
    (
        ("signal73 packet73 router73 cluster73 mirror73 filter73", 28),
        ["signal73 packet73 router73", "cluster73 mirror73 filter73"],
    ),
    (
        ("packet73 router73 cluster73 mirror73 filter73 ranking73", 6),
        ["packet73", "router73", "cluster73", "mirror73", "filter73", "ranking73"],
    ),
    (
        ("packet73 router73 cluster73 mirror73 filter73 ranking73", 10),
        ["packet73", "router73", "cluster73", "mirror73", "filter73", "ranking73"],
    ),
    (
        ("packet73 router73 cluster73 mirror73 filter73 ranking73", 18),
        ["packet73 router73", "cluster73 mirror73", "filter73 ranking73"],
    ),
    (
        ("packet73 router73 cluster73 mirror73 filter73 ranking73", 28),
        ["packet73 router73 cluster73", "mirror73 filter73 ranking73"],
    ),
    (
        ("router73 cluster73 mirror73 filter73 ranking73 encoding73", 6),
        ["router73", "cluster73", "mirror73", "filter73", "ranking73", "encoding73"],
    ),
    (
        ("router73 cluster73 mirror73 filter73 ranking73 encoding73", 10),
        ["router73", "cluster73", "mirror73", "filter73", "ranking73", "encoding73"],
    ),
    (
        ("router73 cluster73 mirror73 filter73 ranking73 encoding73", 18),
        ["router73 cluster73", "mirror73 filter73", "ranking73", "encoding73"],
    ),
    (
        ("router73 cluster73 mirror73 filter73 ranking73 encoding73", 28),
        ["router73 cluster73 mirror73", "filter73 ranking73", "encoding73"],
    ),
    (
        ("cluster73 mirror73 filter73 ranking73 encoding73 mapping73", 6),
        ["cluster73", "mirror73", "filter73", "ranking73", "encoding73", "mapping73"],
    ),
    (
        ("cluster73 mirror73 filter73 ranking73 encoding73 mapping73", 10),
        ["cluster73", "mirror73", "filter73", "ranking73", "encoding73", "mapping73"],
    ),
    (
        ("cluster73 mirror73 filter73 ranking73 encoding73 mapping73", 18),
        ["cluster73 mirror73", "filter73 ranking73", "encoding73", "mapping73"],
    ),
    (
        ("cluster73 mirror73 filter73 ranking73 encoding73 mapping73", 28),
        ["cluster73 mirror73 filter73", "ranking73 encoding73", "mapping73"],
    ),
    (
        ("mirror73 filter73 ranking73 encoding73 mapping73 record73", 6),
        ["mirror73", "filter73", "ranking73", "encoding73", "mapping73", "record73"],
    ),
    (
        ("mirror73 filter73 ranking73 encoding73 mapping73 record73", 10),
        ["mirror73", "filter73", "ranking73", "encoding73", "mapping73", "record73"],
    ),
    (
        ("mirror73 filter73 ranking73 encoding73 mapping73 record73", 18),
        ["mirror73 filter73", "ranking73", "encoding73", "mapping73 record73"],
    ),
    (
        ("mirror73 filter73 ranking73 encoding73 mapping73 record73", 28),
        ["mirror73 filter73 ranking73", "encoding73 mapping73", "record73"],
    ),
    (
        ("filter73 ranking73 encoding73 mapping73 record73 candle73", 6),
        ["filter73", "ranking73", "encoding73", "mapping73", "record73", "candle73"],
    ),
    (
        ("filter73 ranking73 encoding73 mapping73 record73 candle73", 10),
        ["filter73", "ranking73", "encoding73", "mapping73", "record73", "candle73"],
    ),
    (
        ("filter73 ranking73 encoding73 mapping73 record73 candle73", 18),
        ["filter73 ranking73", "encoding73", "mapping73 record73", "candle73"],
    ),
    (
        ("filter73 ranking73 encoding73 mapping73 record73 candle73", 28),
        ["filter73 ranking73", "encoding73 mapping73", "record73 candle73"],
    ),
    (
        ("ranking73 encoding73 mapping73 record73 candle73 thread73", 6),
        ["ranking73", "encoding73", "mapping73", "record73", "candle73", "thread73"],
    ),
    (
        ("ranking73 encoding73 mapping73 record73 candle73 thread73", 10),
        ["ranking73", "encoding73", "mapping73", "record73", "candle73", "thread73"],
    ),
    (
        ("ranking73 encoding73 mapping73 record73 candle73 thread73", 18),
        ["ranking73", "encoding73", "mapping73 record73", "candle73 thread73"],
    ),
    (
        ("ranking73 encoding73 mapping73 record73 candle73 thread73", 28),
        ["ranking73 encoding73", "mapping73 record73 candle73", "thread73"],
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
