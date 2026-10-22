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
        ("round 40: the quick brown fox jumps over the lazy dog", 4),
        ["round", "40:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 40: the quick brown fox jumps over the lazy dog", 8),
        ["round", "40: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 40: the quick brown fox jumps over the lazy dog", 12),
        ["round 40:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 40: the quick brown fox jumps over the lazy dog", 16),
        ["round 40: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 40: the quick brown fox jumps over the lazy dog", 24),
        ["round 40: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 40: the quick brown fox jumps over the lazy dog", 32),
        ["round 40: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 40: agentuniverse is a framework for multi agents", 4),
        ["round", "40:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 40: agentuniverse is a framework for multi agents", 8),
        ["round", "40:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 40: agentuniverse is a framework for multi agents", 12),
        ["round 40:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 40: agentuniverse is a framework for multi agents", 16),
        ["round 40:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 40: agentuniverse is a framework for multi agents", 24),
        ["round 40: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 40: agentuniverse is a framework for multi agents", 32),
        ["round 40: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 40: knowledge stored as vectors enables retrieval", 4),
        ["round", "40:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 40: knowledge stored as vectors enables retrieval", 8),
        ["round", "40:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 40: knowledge stored as vectors enables retrieval", 12),
        ["round 40:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 40: knowledge stored as vectors enables retrieval", 16),
        ["round 40:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 40: knowledge stored as vectors enables retrieval", 24),
        ["round 40: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 40: knowledge stored as vectors enables retrieval", 32),
        ["round 40: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 40: the processor reads the record then stops", 4),
        ["round", "40:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 40: the processor reads the record then stops", 8),
        ["round", "40: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 40: the processor reads the record then stops", 12),
        ["round 40:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 40: the processor reads the record then stops", 16),
        ["round 40: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 40: the processor reads the record then stops", 24),
        ["round 40: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 40: the processor reads the record then stops", 32),
        ["round 40: the processor reads", "the record then stops"],
    ),
    (
        ("round 40: a worker pulls the next task from the queue", 4),
        ["round", "40:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 40: a worker pulls the next task from the queue", 8),
        ["round", "40: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 40: a worker pulls the next task from the queue", 12),
        ["round 40: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 40: a worker pulls the next task from the queue", 16),
        ["round 40: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 40: a worker pulls the next task from the queue", 24),
        ["round 40: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 40: a worker pulls the next task from the queue", 32),
        ["round 40: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 40: signals travel through the network layer", 4),
        ["round", "40:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 40: signals travel through the network layer", 8),
        ["round", "40:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 40: signals travel through the network layer", 12),
        ["round 40:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 40: signals travel through the network layer", 16),
        ["round 40:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 40: signals travel through the network layer", 24),
        ["round 40: signals travel", "through the network", "layer"],
    ),
    (
        ("round 40: signals travel through the network layer", 32),
        ["round 40: signals travel through", "the network layer"],
    ),
    (
        ("round 40: the gateway routes each request by policy", 4),
        ["round", "40:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 40: the gateway routes each request by policy", 8),
        ["round", "40: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 40: the gateway routes each request by policy", 12),
        ["round 40:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 40: the gateway routes each request by policy", 16),
        ["round 40: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 40: the gateway routes each request by policy", 24),
        ["round 40: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 40: the gateway routes each request by policy", 32),
        ["round 40: the gateway routes", "each request by policy"],
    ),
    (
        ("round 40: memory grows until the buffer is full", 4),
        ["round", "40:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 40: memory grows until the buffer is full", 8),
        ["round", "40:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 40: memory grows until the buffer is full", 12),
        ["round 40:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 40: memory grows until the buffer is full", 16),
        ["round 40: memory", "grows until the", "buffer is full"],
    ),
    (("round 40: memory grows until the buffer is full", 24), ["round 40: memory grows", "until the buffer is full"]),
    (("round 40: memory grows until the buffer is full", 32), ["round 40: memory grows until the", "buffer is full"]),
    (
        ("round 40: the cluster mirrors every packet twice", 4),
        ["round", "40:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 40: the cluster mirrors every packet twice", 8),
        ["round", "40: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 40: the cluster mirrors every packet twice", 12),
        ["round 40:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 40: the cluster mirrors every packet twice", 16),
        ["round 40: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 40: the cluster mirrors every packet twice", 24),
        ["round 40: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 40: the cluster mirrors every packet twice", 32), ["round 40: the cluster mirrors", "every packet twice"]),
    (
        ("round 40: ranking uses tokens learned from the corpus", 4),
        ["round", "40:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 40: ranking uses tokens learned from the corpus", 8),
        ["round", "40:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 40: ranking uses tokens learned from the corpus", 12),
        ["round 40:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 40: ranking uses tokens learned from the corpus", 16),
        ["round 40:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 40: ranking uses tokens learned from the corpus", 24),
        ["round 40: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 40: ranking uses tokens learned from the corpus", 32),
        ["round 40: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 40: a long session ends when the candle dies", 4),
        ["round", "40:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 40: a long session ends when the candle dies", 8),
        ["round", "40: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 40: a long session ends when the candle dies", 12),
        ["round 40: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 40: a long session ends when the candle dies", 16),
        ["round 40: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 40: a long session ends when the candle dies", 24),
        ["round 40: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 40: a long session ends when the candle dies", 32),
        ["round 40: a long session ends", "when the candle dies"],
    ),
    (
        ("round 40: encode the prompt then map the result", 4),
        ["round", "40:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 40: encode the prompt then map the result", 8),
        ["round", "40:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 40: encode the prompt then map the result", 12),
        ["round 40:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 40: encode the prompt then map the result", 16),
        ["round 40: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 40: encode the prompt then map the result", 24),
        ["round 40: encode the", "prompt then map the", "result"],
    ),
    (("round 40: encode the prompt then map the result", 32), ["round 40: encode the prompt then", "map the result"]),
    (
        ("round 40: the kernel wakes the worker at dawn", 4),
        ["round", "40:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 40: the kernel wakes the worker at dawn", 8),
        ["round", "40: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 40: the kernel wakes the worker at dawn", 12),
        ["round 40:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 40: the kernel wakes the worker at dawn", 16), ["round 40: the", "kernel wakes the", "worker at dawn"]),
    (("round 40: the kernel wakes the worker at dawn", 24), ["round 40: the kernel", "wakes the worker at dawn"]),
    (("round 40: the kernel wakes the worker at dawn", 32), ["round 40: the kernel wakes the", "worker at dawn"]),
    (
        ("round 40: service latency drops after the patch", 4),
        ["round", "40:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 40: service latency drops after the patch", 8),
        ["round", "40:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 40: service latency drops after the patch", 12),
        ["round 40:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 40: service latency drops after the patch", 16),
        ["round 40:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 40: service latency drops after the patch", 24),
        ["round 40: service", "latency drops after the", "patch"],
    ),
    (("round 40: service latency drops after the patch", 32), ["round 40: service latency drops", "after the patch"]),
    (
        ("round 40: the library caches every vector it sees", 4),
        ["round", "40:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 40: the library caches every vector it sees", 8),
        ["round", "40: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 40: the library caches every vector it sees", 12),
        ["round 40:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 40: the library caches every vector it sees", 16),
        ["round 40: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 40: the library caches every vector it sees", 24),
        ["round 40: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 40: the library caches every vector it sees", 32),
        ["round 40: the library caches", "every vector it sees"],
    ),
    (
        ("round 40: agents argue then the debate resolves", 4),
        ["round", "40:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 40: agents argue then the debate resolves", 8),
        ["round", "40:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 40: agents argue then the debate resolves", 12),
        ["round 40:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 40: agents argue then the debate resolves", 16),
        ["round 40: agents", "argue then the", "debate resolves"],
    ),
    (("round 40: agents argue then the debate resolves", 24), ["round 40: agents argue", "then the debate resolves"]),
    (("round 40: agents argue then the debate resolves", 32), ["round 40: agents argue then the", "debate resolves"]),
    (
        ("round 40: the filter keeps only strong matches", 4),
        ["round", "40:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 40: the filter keeps only strong matches", 8),
        ["round", "40: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 40: the filter keeps only strong matches", 12),
        ["round 40:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 40: the filter keeps only strong matches", 16),
        ["round 40: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 40: the filter keeps only strong matches", 24), ["round 40: the filter", "keeps only strong", "matches"]),
    (("round 40: the filter keeps only strong matches", 32), ["round 40: the filter keeps only", "strong matches"]),
    (
        ("round 40: the model answers with a short reply", 4),
        ["round", "40:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 40: the model answers with a short reply", 8),
        ["round", "40: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 40: the model answers with a short reply", 12),
        ["round 40:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 40: the model answers with a short reply", 16),
        ["round 40: the", "model answers", "with a short", "reply"],
    ),
    (("round 40: the model answers with a short reply", 24), ["round 40: the model", "answers with a short", "reply"]),
    (("round 40: the model answers with a short reply", 32), ["round 40: the model answers with", "a short reply"]),
    (
        ("round 40: the recorder stores the reasoning trace", 4),
        ["round", "40:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 40: the recorder stores the reasoning trace", 8),
        ["round", "40: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 40: the recorder stores the reasoning trace", 12),
        ["round 40:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 40: the recorder stores the reasoning trace", 16),
        ["round 40: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 40: the recorder stores the reasoning trace", 24),
        ["round 40: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 40: the recorder stores the reasoning trace", 32),
        ["round 40: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 40: the angel watches the processor run", 4),
        ["round", "40:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 40: the angel watches the processor run", 8),
        ["round", "40: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 40: the angel watches the processor run", 12),
        ["round 40:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 40: the angel watches the processor run", 16), ["round 40: the", "angel watches", "the processor", "run"]),
    (("round 40: the angel watches the processor run", 24), ["round 40: the angel", "watches the processor", "run"]),
    (("round 40: the angel watches the processor run", 32), ["round 40: the angel watches the", "processor run"]),
    (
        ("round 40: angle of the vector decides the match", 4),
        ["round", "40:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 40: angle of the vector decides the match", 8),
        ["round", "40:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 40: angle of the vector decides the match", 12),
        ["round 40:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 40: angle of the vector decides the match", 16),
        ["round 40: angle", "of the vector", "decides the", "match"],
    ),
    (("round 40: angle of the vector decides the match", 24), ["round 40: angle of the", "vector decides the match"]),
    (("round 40: angle of the vector decides the match", 32), ["round 40: angle of the vector", "decides the match"]),
    (
        ("round 40: the candle burns twice as long at night", 4),
        ["round", "40:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 40: the candle burns twice as long at night", 8),
        ["round", "40: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 40: the candle burns twice as long at night", 12),
        ["round 40:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 40: the candle burns twice as long at night", 16),
        ["round 40: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 40: the candle burns twice as long at night", 24),
        ["round 40: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 40: the candle burns twice as long at night", 32),
        ["round 40: the candle burns twice", "as long at night"],
    ),
    (
        ("round 40: a mirror of the universe in one line", 4),
        ["round", "40:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 40: a mirror of the universe in one line", 8),
        ["round", "40: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 40: a mirror of the universe in one line", 12),
        ["round 40: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 40: a mirror of the universe in one line", 16),
        ["round 40: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 40: a mirror of the universe in one line", 24), ["round 40: a mirror of", "the universe in one line"]),
    (("round 40: a mirror of the universe in one line", 32), ["round 40: a mirror of the", "universe in one line"]),
    (
        ("round 40: the queue drains before the storm", 4),
        ["round", "40:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 40: the queue drains before the storm", 8),
        ["round", "40: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 40: the queue drains before the storm", 12), ["round 40:", "the queue", "drains", "before the", "storm"]),
    (("round 40: the queue drains before the storm", 16), ["round 40: the", "queue drains", "before the storm"]),
    (("round 40: the queue drains before the storm", 24), ["round 40: the queue", "drains before the storm"]),
    (("round 40: the queue drains before the storm", 32), ["round 40: the queue drains", "before the storm"]),
    (
        ("kitten40 sitting40 agent40 angle40 universe40 memory40", 6),
        ["kitten40", "sitting40", "agent40", "angle40", "universe40", "memory40"],
    ),
    (
        ("kitten40 sitting40 agent40 angle40 universe40 memory40", 10),
        ["kitten40", "sitting40", "agent40", "angle40", "universe40", "memory40"],
    ),
    (
        ("kitten40 sitting40 agent40 angle40 universe40 memory40", 18),
        ["kitten40 sitting40", "agent40 angle40", "universe40", "memory40"],
    ),
    (
        ("kitten40 sitting40 agent40 angle40 universe40 memory40", 28),
        ["kitten40 sitting40 agent40", "angle40 universe40 memory40"],
    ),
    (
        ("sitting40 agent40 angle40 universe40 memory40 stream40", 6),
        ["sitting40", "agent40", "angle40", "universe40", "memory40", "stream40"],
    ),
    (
        ("sitting40 agent40 angle40 universe40 memory40 stream40", 10),
        ["sitting40", "agent40", "angle40", "universe40", "memory40", "stream40"],
    ),
    (
        ("sitting40 agent40 angle40 universe40 memory40 stream40", 18),
        ["sitting40 agent40", "angle40 universe40", "memory40 stream40"],
    ),
    (
        ("sitting40 agent40 angle40 universe40 memory40 stream40", 28),
        ["sitting40 agent40 angle40", "universe40 memory40 stream40"],
    ),
    (
        ("agent40 angle40 universe40 memory40 stream40 context40", 6),
        ["agent40", "angle40", "universe40", "memory40", "stream40", "context40"],
    ),
    (
        ("agent40 angle40 universe40 memory40 stream40 context40", 10),
        ["agent40", "angle40", "universe40", "memory40", "stream40", "context40"],
    ),
    (
        ("agent40 angle40 universe40 memory40 stream40 context40", 18),
        ["agent40 angle40", "universe40", "memory40 stream40", "context40"],
    ),
    (
        ("agent40 angle40 universe40 memory40 stream40 context40", 28),
        ["agent40 angle40 universe40", "memory40 stream40 context40"],
    ),
    (
        ("angle40 universe40 memory40 stream40 context40 knowledge40", 6),
        ["angle40", "universe40", "memory40", "stream40", "context40", "knowledge40"],
    ),
    (
        ("angle40 universe40 memory40 stream40 context40 knowledge40", 10),
        ["angle40", "universe40", "memory40", "stream40", "context40", "knowledge40"],
    ),
    (
        ("angle40 universe40 memory40 stream40 context40 knowledge40", 18),
        ["angle40 universe40", "memory40 stream40", "context40", "knowledge40"],
    ),
    (
        ("angle40 universe40 memory40 stream40 context40 knowledge40", 28),
        ["angle40 universe40 memory40", "stream40 context40", "knowledge40"],
    ),
    (
        ("universe40 memory40 stream40 context40 knowledge40 vector40", 6),
        ["universe40", "memory40", "stream40", "context40", "knowledge40", "vector40"],
    ),
    (
        ("universe40 memory40 stream40 context40 knowledge40 vector40", 10),
        ["universe40", "memory40", "stream40", "context40", "knowledge40", "vector40"],
    ),
    (
        ("universe40 memory40 stream40 context40 knowledge40 vector40", 18),
        ["universe40", "memory40 stream40", "context40", "knowledge40", "vector40"],
    ),
    (
        ("universe40 memory40 stream40 context40 knowledge40 vector40", 28),
        ["universe40 memory40 stream40", "context40 knowledge40", "vector40"],
    ),
    (
        ("memory40 stream40 context40 knowledge40 vector40 processor40", 6),
        ["memory40", "stream40", "context40", "knowledge40", "vector40", "processor40"],
    ),
    (
        ("memory40 stream40 context40 knowledge40 vector40 processor40", 10),
        ["memory40", "stream40", "context40", "knowledge40", "vector40", "processor40"],
    ),
    (
        ("memory40 stream40 context40 knowledge40 vector40 processor40", 18),
        ["memory40 stream40", "context40", "knowledge40", "vector40", "processor40"],
    ),
    (
        ("memory40 stream40 context40 knowledge40 vector40 processor40", 28),
        ["memory40 stream40 context40", "knowledge40 vector40", "processor40"],
    ),
    (
        ("stream40 context40 knowledge40 vector40 processor40 reasoning40", 6),
        ["stream40", "context40", "knowledge40", "vector40", "processor40", "reasoning40"],
    ),
    (
        ("stream40 context40 knowledge40 vector40 processor40 reasoning40", 10),
        ["stream40", "context40", "knowledge40", "vector40", "processor40", "reasoning40"],
    ),
    (
        ("stream40 context40 knowledge40 vector40 processor40 reasoning40", 18),
        ["stream40 context40", "knowledge40", "vector40", "processor40", "reasoning40"],
    ),
    (
        ("stream40 context40 knowledge40 vector40 processor40 reasoning40", 28),
        ["stream40 context40", "knowledge40 vector40", "processor40 reasoning40"],
    ),
    (
        ("context40 knowledge40 vector40 processor40 reasoning40 machine40", 6),
        ["context40", "knowledge40", "vector40", "processor40", "reasoning40", "machine40"],
    ),
    (
        ("context40 knowledge40 vector40 processor40 reasoning40 machine40", 10),
        ["context40", "knowledge40", "vector40", "processor40", "reasoning40", "machine40"],
    ),
    (
        ("context40 knowledge40 vector40 processor40 reasoning40 machine40", 18),
        ["context40", "knowledge40", "vector40", "processor40", "reasoning40", "machine40"],
    ),
    (
        ("context40 knowledge40 vector40 processor40 reasoning40 machine40", 28),
        ["context40 knowledge40", "vector40 processor40", "reasoning40 machine40"],
    ),
    (
        ("knowledge40 vector40 processor40 reasoning40 machine40 learning40", 6),
        ["knowledge40", "vector40", "processor40", "reasoning40", "machine40", "learning40"],
    ),
    (
        ("knowledge40 vector40 processor40 reasoning40 machine40 learning40", 10),
        ["knowledge40", "vector40", "processor40", "reasoning40", "machine40", "learning40"],
    ),
    (
        ("knowledge40 vector40 processor40 reasoning40 machine40 learning40", 18),
        ["knowledge40", "vector40", "processor40", "reasoning40", "machine40", "learning40"],
    ),
    (
        ("knowledge40 vector40 processor40 reasoning40 machine40 learning40", 28),
        ["knowledge40 vector40", "processor40 reasoning40", "machine40 learning40"],
    ),
    (
        ("vector40 processor40 reasoning40 machine40 learning40 model40", 6),
        ["vector40", "processor40", "reasoning40", "machine40", "learning40", "model40"],
    ),
    (
        ("vector40 processor40 reasoning40 machine40 learning40 model40", 10),
        ["vector40", "processor40", "reasoning40", "machine40", "learning40", "model40"],
    ),
    (
        ("vector40 processor40 reasoning40 machine40 learning40 model40", 18),
        ["vector40", "processor40", "reasoning40", "machine40", "learning40 model40"],
    ),
    (
        ("vector40 processor40 reasoning40 machine40 learning40 model40", 28),
        ["vector40 processor40", "reasoning40 machine40", "learning40 model40"],
    ),
    (
        ("processor40 reasoning40 machine40 learning40 model40 token40", 6),
        ["processor40", "reasoning40", "machine40", "learning40", "model40", "token40"],
    ),
    (
        ("processor40 reasoning40 machine40 learning40 model40 token40", 10),
        ["processor40", "reasoning40", "machine40", "learning40", "model40", "token40"],
    ),
    (
        ("processor40 reasoning40 machine40 learning40 model40 token40", 18),
        ["processor40", "reasoning40", "machine40", "learning40 model40", "token40"],
    ),
    (
        ("processor40 reasoning40 machine40 learning40 model40 token40", 28),
        ["processor40 reasoning40", "machine40 learning40 model40", "token40"],
    ),
    (
        ("reasoning40 machine40 learning40 model40 token40 prompt40", 6),
        ["reasoning40", "machine40", "learning40", "model40", "token40", "prompt40"],
    ),
    (
        ("reasoning40 machine40 learning40 model40 token40 prompt40", 10),
        ["reasoning40", "machine40", "learning40", "model40", "token40", "prompt40"],
    ),
    (
        ("reasoning40 machine40 learning40 model40 token40 prompt40", 18),
        ["reasoning40", "machine40", "learning40 model40", "token40 prompt40"],
    ),
    (
        ("reasoning40 machine40 learning40 model40 token40 prompt40", 28),
        ["reasoning40 machine40", "learning40 model40 token40", "prompt40"],
    ),
    (
        ("machine40 learning40 model40 token40 prompt40 session40", 6),
        ["machine40", "learning40", "model40", "token40", "prompt40", "session40"],
    ),
    (
        ("machine40 learning40 model40 token40 prompt40 session40", 10),
        ["machine40", "learning40", "model40", "token40", "prompt40", "session40"],
    ),
    (
        ("machine40 learning40 model40 token40 prompt40 session40", 18),
        ["machine40", "learning40 model40", "token40 prompt40", "session40"],
    ),
    (
        ("machine40 learning40 model40 token40 prompt40 session40", 28),
        ["machine40 learning40 model40", "token40 prompt40 session40"],
    ),
    (
        ("learning40 model40 token40 prompt40 session40 library40", 6),
        ["learning40", "model40", "token40", "prompt40", "session40", "library40"],
    ),
    (
        ("learning40 model40 token40 prompt40 session40 library40", 10),
        ["learning40", "model40", "token40", "prompt40", "session40", "library40"],
    ),
    (
        ("learning40 model40 token40 prompt40 session40 library40", 18),
        ["learning40 model40", "token40 prompt40", "session40", "library40"],
    ),
    (
        ("learning40 model40 token40 prompt40 session40 library40", 28),
        ["learning40 model40 token40", "prompt40 session40 library40"],
    ),
    (
        ("model40 token40 prompt40 session40 library40 service40", 6),
        ["model40", "token40", "prompt40", "session40", "library40", "service40"],
    ),
    (
        ("model40 token40 prompt40 session40 library40 service40", 10),
        ["model40", "token40", "prompt40", "session40", "library40", "service40"],
    ),
    (
        ("model40 token40 prompt40 session40 library40 service40", 18),
        ["model40 token40", "prompt40 session40", "library40", "service40"],
    ),
    (
        ("model40 token40 prompt40 session40 library40 service40", 28),
        ["model40 token40 prompt40", "session40 library40", "service40"],
    ),
    (
        ("token40 prompt40 session40 library40 service40 gateway40", 6),
        ["token40", "prompt40", "session40", "library40", "service40", "gateway40"],
    ),
    (
        ("token40 prompt40 session40 library40 service40 gateway40", 10),
        ["token40", "prompt40", "session40", "library40", "service40", "gateway40"],
    ),
    (
        ("token40 prompt40 session40 library40 service40 gateway40", 18),
        ["token40 prompt40", "session40", "library40", "service40", "gateway40"],
    ),
    (
        ("token40 prompt40 session40 library40 service40 gateway40", 28),
        ["token40 prompt40 session40", "library40 service40", "gateway40"],
    ),
    (
        ("prompt40 session40 library40 service40 gateway40 storage40", 6),
        ["prompt40", "session40", "library40", "service40", "gateway40", "storage40"],
    ),
    (
        ("prompt40 session40 library40 service40 gateway40 storage40", 10),
        ["prompt40", "session40", "library40", "service40", "gateway40", "storage40"],
    ),
    (
        ("prompt40 session40 library40 service40 gateway40 storage40", 18),
        ["prompt40 session40", "library40", "service40", "gateway40", "storage40"],
    ),
    (
        ("prompt40 session40 library40 service40 gateway40 storage40", 28),
        ["prompt40 session40 library40", "service40 gateway40", "storage40"],
    ),
    (
        ("session40 library40 service40 gateway40 storage40 network40", 6),
        ["session40", "library40", "service40", "gateway40", "storage40", "network40"],
    ),
    (
        ("session40 library40 service40 gateway40 storage40 network40", 10),
        ["session40", "library40", "service40", "gateway40", "storage40", "network40"],
    ),
    (
        ("session40 library40 service40 gateway40 storage40 network40", 18),
        ["session40", "library40", "service40", "gateway40", "storage40", "network40"],
    ),
    (
        ("session40 library40 service40 gateway40 storage40 network40", 28),
        ["session40 library40", "service40 gateway40", "storage40 network40"],
    ),
    (
        ("library40 service40 gateway40 storage40 network40 latency40", 6),
        ["library40", "service40", "gateway40", "storage40", "network40", "latency40"],
    ),
    (
        ("library40 service40 gateway40 storage40 network40 latency40", 10),
        ["library40", "service40", "gateway40", "storage40", "network40", "latency40"],
    ),
    (
        ("library40 service40 gateway40 storage40 network40 latency40", 18),
        ["library40", "service40", "gateway40", "storage40", "network40", "latency40"],
    ),
    (
        ("library40 service40 gateway40 storage40 network40 latency40", 28),
        ["library40 service40", "gateway40 storage40", "network40 latency40"],
    ),
    (
        ("service40 gateway40 storage40 network40 latency40 buffer40", 6),
        ["service40", "gateway40", "storage40", "network40", "latency40", "buffer40"],
    ),
    (
        ("service40 gateway40 storage40 network40 latency40 buffer40", 10),
        ["service40", "gateway40", "storage40", "network40", "latency40", "buffer40"],
    ),
    (
        ("service40 gateway40 storage40 network40 latency40 buffer40", 18),
        ["service40", "gateway40", "storage40", "network40", "latency40 buffer40"],
    ),
    (
        ("service40 gateway40 storage40 network40 latency40 buffer40", 28),
        ["service40 gateway40", "storage40 network40", "latency40 buffer40"],
    ),
    (
        ("gateway40 storage40 network40 latency40 buffer40 queue40", 6),
        ["gateway40", "storage40", "network40", "latency40", "buffer40", "queue40"],
    ),
    (
        ("gateway40 storage40 network40 latency40 buffer40 queue40", 10),
        ["gateway40", "storage40", "network40", "latency40", "buffer40", "queue40"],
    ),
    (
        ("gateway40 storage40 network40 latency40 buffer40 queue40", 18),
        ["gateway40", "storage40", "network40", "latency40 buffer40", "queue40"],
    ),
    (
        ("gateway40 storage40 network40 latency40 buffer40 queue40", 28),
        ["gateway40 storage40", "network40 latency40 buffer40", "queue40"],
    ),
    (
        ("storage40 network40 latency40 buffer40 queue40 worker40", 6),
        ["storage40", "network40", "latency40", "buffer40", "queue40", "worker40"],
    ),
    (
        ("storage40 network40 latency40 buffer40 queue40 worker40", 10),
        ["storage40", "network40", "latency40", "buffer40", "queue40", "worker40"],
    ),
    (
        ("storage40 network40 latency40 buffer40 queue40 worker40", 18),
        ["storage40", "network40", "latency40 buffer40", "queue40 worker40"],
    ),
    (
        ("storage40 network40 latency40 buffer40 queue40 worker40", 28),
        ["storage40 network40", "latency40 buffer40 queue40", "worker40"],
    ),
    (
        ("network40 latency40 buffer40 queue40 worker40 kernel40", 6),
        ["network40", "latency40", "buffer40", "queue40", "worker40", "kernel40"],
    ),
    (
        ("network40 latency40 buffer40 queue40 worker40 kernel40", 10),
        ["network40", "latency40", "buffer40", "queue40", "worker40", "kernel40"],
    ),
    (
        ("network40 latency40 buffer40 queue40 worker40 kernel40", 18),
        ["network40", "latency40 buffer40", "queue40 worker40", "kernel40"],
    ),
    (
        ("network40 latency40 buffer40 queue40 worker40 kernel40", 28),
        ["network40 latency40 buffer40", "queue40 worker40 kernel40"],
    ),
    (
        ("latency40 buffer40 queue40 worker40 kernel40 signal40", 6),
        ["latency40", "buffer40", "queue40", "worker40", "kernel40", "signal40"],
    ),
    (
        ("latency40 buffer40 queue40 worker40 kernel40 signal40", 10),
        ["latency40", "buffer40", "queue40", "worker40", "kernel40", "signal40"],
    ),
    (
        ("latency40 buffer40 queue40 worker40 kernel40 signal40", 18),
        ["latency40 buffer40", "queue40 worker40", "kernel40 signal40"],
    ),
    (
        ("latency40 buffer40 queue40 worker40 kernel40 signal40", 28),
        ["latency40 buffer40 queue40", "worker40 kernel40 signal40"],
    ),
    (
        ("buffer40 queue40 worker40 kernel40 signal40 packet40", 6),
        ["buffer40", "queue40", "worker40", "kernel40", "signal40", "packet40"],
    ),
    (
        ("buffer40 queue40 worker40 kernel40 signal40 packet40", 10),
        ["buffer40", "queue40", "worker40", "kernel40", "signal40", "packet40"],
    ),
    (
        ("buffer40 queue40 worker40 kernel40 signal40 packet40", 18),
        ["buffer40 queue40", "worker40 kernel40", "signal40 packet40"],
    ),
    (
        ("buffer40 queue40 worker40 kernel40 signal40 packet40", 28),
        ["buffer40 queue40 worker40", "kernel40 signal40 packet40"],
    ),
    (
        ("queue40 worker40 kernel40 signal40 packet40 router40", 6),
        ["queue40", "worker40", "kernel40", "signal40", "packet40", "router40"],
    ),
    (
        ("queue40 worker40 kernel40 signal40 packet40 router40", 10),
        ["queue40", "worker40", "kernel40", "signal40", "packet40", "router40"],
    ),
    (
        ("queue40 worker40 kernel40 signal40 packet40 router40", 18),
        ["queue40 worker40", "kernel40 signal40", "packet40 router40"],
    ),
    (
        ("queue40 worker40 kernel40 signal40 packet40 router40", 28),
        ["queue40 worker40 kernel40", "signal40 packet40 router40"],
    ),
    (
        ("worker40 kernel40 signal40 packet40 router40 cluster40", 6),
        ["worker40", "kernel40", "signal40", "packet40", "router40", "cluster40"],
    ),
    (
        ("worker40 kernel40 signal40 packet40 router40 cluster40", 10),
        ["worker40", "kernel40", "signal40", "packet40", "router40", "cluster40"],
    ),
    (
        ("worker40 kernel40 signal40 packet40 router40 cluster40", 18),
        ["worker40 kernel40", "signal40 packet40", "router40 cluster40"],
    ),
    (
        ("worker40 kernel40 signal40 packet40 router40 cluster40", 28),
        ["worker40 kernel40 signal40", "packet40 router40 cluster40"],
    ),
    (
        ("kernel40 signal40 packet40 router40 cluster40 mirror40", 6),
        ["kernel40", "signal40", "packet40", "router40", "cluster40", "mirror40"],
    ),
    (
        ("kernel40 signal40 packet40 router40 cluster40 mirror40", 10),
        ["kernel40", "signal40", "packet40", "router40", "cluster40", "mirror40"],
    ),
    (
        ("kernel40 signal40 packet40 router40 cluster40 mirror40", 18),
        ["kernel40 signal40", "packet40 router40", "cluster40 mirror40"],
    ),
    (
        ("kernel40 signal40 packet40 router40 cluster40 mirror40", 28),
        ["kernel40 signal40 packet40", "router40 cluster40 mirror40"],
    ),
    (
        ("signal40 packet40 router40 cluster40 mirror40 filter40", 6),
        ["signal40", "packet40", "router40", "cluster40", "mirror40", "filter40"],
    ),
    (
        ("signal40 packet40 router40 cluster40 mirror40 filter40", 10),
        ["signal40", "packet40", "router40", "cluster40", "mirror40", "filter40"],
    ),
    (
        ("signal40 packet40 router40 cluster40 mirror40 filter40", 18),
        ["signal40 packet40", "router40 cluster40", "mirror40 filter40"],
    ),
    (
        ("signal40 packet40 router40 cluster40 mirror40 filter40", 28),
        ["signal40 packet40 router40", "cluster40 mirror40 filter40"],
    ),
    (
        ("packet40 router40 cluster40 mirror40 filter40 ranking40", 6),
        ["packet40", "router40", "cluster40", "mirror40", "filter40", "ranking40"],
    ),
    (
        ("packet40 router40 cluster40 mirror40 filter40 ranking40", 10),
        ["packet40", "router40", "cluster40", "mirror40", "filter40", "ranking40"],
    ),
    (
        ("packet40 router40 cluster40 mirror40 filter40 ranking40", 18),
        ["packet40 router40", "cluster40 mirror40", "filter40 ranking40"],
    ),
    (
        ("packet40 router40 cluster40 mirror40 filter40 ranking40", 28),
        ["packet40 router40 cluster40", "mirror40 filter40 ranking40"],
    ),
    (
        ("router40 cluster40 mirror40 filter40 ranking40 encoding40", 6),
        ["router40", "cluster40", "mirror40", "filter40", "ranking40", "encoding40"],
    ),
    (
        ("router40 cluster40 mirror40 filter40 ranking40 encoding40", 10),
        ["router40", "cluster40", "mirror40", "filter40", "ranking40", "encoding40"],
    ),
    (
        ("router40 cluster40 mirror40 filter40 ranking40 encoding40", 18),
        ["router40 cluster40", "mirror40 filter40", "ranking40", "encoding40"],
    ),
    (
        ("router40 cluster40 mirror40 filter40 ranking40 encoding40", 28),
        ["router40 cluster40 mirror40", "filter40 ranking40", "encoding40"],
    ),
    (
        ("cluster40 mirror40 filter40 ranking40 encoding40 mapping40", 6),
        ["cluster40", "mirror40", "filter40", "ranking40", "encoding40", "mapping40"],
    ),
    (
        ("cluster40 mirror40 filter40 ranking40 encoding40 mapping40", 10),
        ["cluster40", "mirror40", "filter40", "ranking40", "encoding40", "mapping40"],
    ),
    (
        ("cluster40 mirror40 filter40 ranking40 encoding40 mapping40", 18),
        ["cluster40 mirror40", "filter40 ranking40", "encoding40", "mapping40"],
    ),
    (
        ("cluster40 mirror40 filter40 ranking40 encoding40 mapping40", 28),
        ["cluster40 mirror40 filter40", "ranking40 encoding40", "mapping40"],
    ),
    (
        ("mirror40 filter40 ranking40 encoding40 mapping40 record40", 6),
        ["mirror40", "filter40", "ranking40", "encoding40", "mapping40", "record40"],
    ),
    (
        ("mirror40 filter40 ranking40 encoding40 mapping40 record40", 10),
        ["mirror40", "filter40", "ranking40", "encoding40", "mapping40", "record40"],
    ),
    (
        ("mirror40 filter40 ranking40 encoding40 mapping40 record40", 18),
        ["mirror40 filter40", "ranking40", "encoding40", "mapping40 record40"],
    ),
    (
        ("mirror40 filter40 ranking40 encoding40 mapping40 record40", 28),
        ["mirror40 filter40 ranking40", "encoding40 mapping40", "record40"],
    ),
    (
        ("filter40 ranking40 encoding40 mapping40 record40 candle40", 6),
        ["filter40", "ranking40", "encoding40", "mapping40", "record40", "candle40"],
    ),
    (
        ("filter40 ranking40 encoding40 mapping40 record40 candle40", 10),
        ["filter40", "ranking40", "encoding40", "mapping40", "record40", "candle40"],
    ),
    (
        ("filter40 ranking40 encoding40 mapping40 record40 candle40", 18),
        ["filter40 ranking40", "encoding40", "mapping40 record40", "candle40"],
    ),
    (
        ("filter40 ranking40 encoding40 mapping40 record40 candle40", 28),
        ["filter40 ranking40", "encoding40 mapping40", "record40 candle40"],
    ),
    (
        ("ranking40 encoding40 mapping40 record40 candle40 thread40", 6),
        ["ranking40", "encoding40", "mapping40", "record40", "candle40", "thread40"],
    ),
    (
        ("ranking40 encoding40 mapping40 record40 candle40 thread40", 10),
        ["ranking40", "encoding40", "mapping40", "record40", "candle40", "thread40"],
    ),
    (
        ("ranking40 encoding40 mapping40 record40 candle40 thread40", 18),
        ["ranking40", "encoding40", "mapping40 record40", "candle40 thread40"],
    ),
    (
        ("ranking40 encoding40 mapping40 record40 candle40 thread40", 28),
        ["ranking40 encoding40", "mapping40 record40 candle40", "thread40"],
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
