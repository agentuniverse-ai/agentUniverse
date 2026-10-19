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
        ("round 178: the quick brown fox jumps over the lazy dog", 4),
        ["round", "178:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 178: the quick brown fox jumps over the lazy dog", 8),
        ["round", "178: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 178: the quick brown fox jumps over the lazy dog", 12),
        ["round 178:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 178: the quick brown fox jumps over the lazy dog", 16),
        ["round 178: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 178: the quick brown fox jumps over the lazy dog", 24),
        ["round 178: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 178: the quick brown fox jumps over the lazy dog", 32),
        ["round 178: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 178: agentuniverse is a framework for multi agents", 4),
        ["round", "178:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 178: agentuniverse is a framework for multi agents", 8),
        ["round", "178:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 178: agentuniverse is a framework for multi agents", 12),
        ["round 178:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 178: agentuniverse is a framework for multi agents", 16),
        ["round 178:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 178: agentuniverse is a framework for multi agents", 24),
        ["round 178: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 178: agentuniverse is a framework for multi agents", 32),
        ["round 178: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 178: knowledge stored as vectors enables retrieval", 4),
        ["round", "178:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 178: knowledge stored as vectors enables retrieval", 8),
        ["round", "178:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 178: knowledge stored as vectors enables retrieval", 12),
        ["round 178:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 178: knowledge stored as vectors enables retrieval", 16),
        ["round 178:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 178: knowledge stored as vectors enables retrieval", 24),
        ["round 178: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 178: knowledge stored as vectors enables retrieval", 32),
        ["round 178: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 178: the processor reads the record then stops", 4),
        ["round", "178:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 178: the processor reads the record then stops", 8),
        ["round", "178: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 178: the processor reads the record then stops", 12),
        ["round 178:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 178: the processor reads the record then stops", 16),
        ["round 178: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 178: the processor reads the record then stops", 24),
        ["round 178: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 178: the processor reads the record then stops", 32),
        ["round 178: the processor reads", "the record then stops"],
    ),
    (
        ("round 178: a worker pulls the next task from the queue", 4),
        ["round", "178:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 178: a worker pulls the next task from the queue", 8),
        ["round", "178: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 178: a worker pulls the next task from the queue", 12),
        ["round 178: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 178: a worker pulls the next task from the queue", 16),
        ["round 178: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 178: a worker pulls the next task from the queue", 24),
        ["round 178: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 178: a worker pulls the next task from the queue", 32),
        ["round 178: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 178: signals travel through the network layer", 4),
        ["round", "178:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 178: signals travel through the network layer", 8),
        ["round", "178:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 178: signals travel through the network layer", 12),
        ["round 178:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 178: signals travel through the network layer", 16),
        ["round 178:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 178: signals travel through the network layer", 24),
        ["round 178: signals", "travel through the", "network layer"],
    ),
    (
        ("round 178: signals travel through the network layer", 32),
        ["round 178: signals travel", "through the network layer"],
    ),
    (
        ("round 178: the gateway routes each request by policy", 4),
        ["round", "178:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 178: the gateway routes each request by policy", 8),
        ["round", "178: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 178: the gateway routes each request by policy", 12),
        ["round 178:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 178: the gateway routes each request by policy", 16),
        ["round 178: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 178: the gateway routes each request by policy", 24),
        ["round 178: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 178: the gateway routes each request by policy", 32),
        ["round 178: the gateway routes", "each request by policy"],
    ),
    (
        ("round 178: memory grows until the buffer is full", 4),
        ["round", "178:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 178: memory grows until the buffer is full", 8),
        ["round", "178:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 178: memory grows until the buffer is full", 12),
        ["round 178:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 178: memory grows until the buffer is full", 16),
        ["round 178:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 178: memory grows until the buffer is full", 24), ["round 178: memory grows", "until the buffer is full"]),
    (("round 178: memory grows until the buffer is full", 32), ["round 178: memory grows until", "the buffer is full"]),
    (
        ("round 178: the cluster mirrors every packet twice", 4),
        ["round", "178:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 178: the cluster mirrors every packet twice", 8),
        ["round", "178: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 178: the cluster mirrors every packet twice", 12),
        ["round 178:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 178: the cluster mirrors every packet twice", 16),
        ["round 178: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 178: the cluster mirrors every packet twice", 24),
        ["round 178: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 178: the cluster mirrors every packet twice", 32),
        ["round 178: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 178: ranking uses tokens learned from the corpus", 4),
        ["round", "178:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 178: ranking uses tokens learned from the corpus", 8),
        ["round", "178:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 178: ranking uses tokens learned from the corpus", 12),
        ["round 178:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 178: ranking uses tokens learned from the corpus", 16),
        ["round 178:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 178: ranking uses tokens learned from the corpus", 24),
        ["round 178: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 178: ranking uses tokens learned from the corpus", 32),
        ["round 178: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 178: a long session ends when the candle dies", 4),
        ["round", "178:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 178: a long session ends when the candle dies", 8),
        ["round", "178: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 178: a long session ends when the candle dies", 12),
        ["round 178: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 178: a long session ends when the candle dies", 16),
        ["round 178: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 178: a long session ends when the candle dies", 24),
        ["round 178: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 178: a long session ends when the candle dies", 32),
        ["round 178: a long session ends", "when the candle dies"],
    ),
    (
        ("round 178: encode the prompt then map the result", 4),
        ["round", "178:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 178: encode the prompt then map the result", 8),
        ["round", "178:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 178: encode the prompt then map the result", 12),
        ["round 178:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 178: encode the prompt then map the result", 16),
        ["round 178:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 178: encode the prompt then map the result", 24),
        ["round 178: encode the", "prompt then map the", "result"],
    ),
    (("round 178: encode the prompt then map the result", 32), ["round 178: encode the prompt", "then map the result"]),
    (
        ("round 178: the kernel wakes the worker at dawn", 4),
        ["round", "178:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 178: the kernel wakes the worker at dawn", 8),
        ["round", "178: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 178: the kernel wakes the worker at dawn", 12),
        ["round 178:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 178: the kernel wakes the worker at dawn", 16), ["round 178: the", "kernel wakes the", "worker at dawn"]),
    (("round 178: the kernel wakes the worker at dawn", 24), ["round 178: the kernel", "wakes the worker at dawn"]),
    (("round 178: the kernel wakes the worker at dawn", 32), ["round 178: the kernel wakes the", "worker at dawn"]),
    (
        ("round 178: service latency drops after the patch", 4),
        ["round", "178:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 178: service latency drops after the patch", 8),
        ["round", "178:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 178: service latency drops after the patch", 12),
        ["round 178:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 178: service latency drops after the patch", 16),
        ["round 178:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 178: service latency drops after the patch", 24),
        ["round 178: service", "latency drops after the", "patch"],
    ),
    (("round 178: service latency drops after the patch", 32), ["round 178: service latency drops", "after the patch"]),
    (
        ("round 178: the library caches every vector it sees", 4),
        ["round", "178:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 178: the library caches every vector it sees", 8),
        ["round", "178: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 178: the library caches every vector it sees", 12),
        ["round 178:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 178: the library caches every vector it sees", 16),
        ["round 178: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 178: the library caches every vector it sees", 24),
        ["round 178: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 178: the library caches every vector it sees", 32),
        ["round 178: the library caches", "every vector it sees"],
    ),
    (
        ("round 178: agents argue then the debate resolves", 4),
        ["round", "178:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 178: agents argue then the debate resolves", 8),
        ["round", "178:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 178: agents argue then the debate resolves", 12),
        ["round 178:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 178: agents argue then the debate resolves", 16),
        ["round 178:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 178: agents argue then the debate resolves", 24), ["round 178: agents argue", "then the debate resolves"]),
    (("round 178: agents argue then the debate resolves", 32), ["round 178: agents argue then the", "debate resolves"]),
    (
        ("round 178: the filter keeps only strong matches", 4),
        ["round", "178:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 178: the filter keeps only strong matches", 8),
        ["round", "178: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 178: the filter keeps only strong matches", 12),
        ["round 178:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 178: the filter keeps only strong matches", 16),
        ["round 178: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 178: the filter keeps only strong matches", 24),
        ["round 178: the filter", "keeps only strong", "matches"],
    ),
    (("round 178: the filter keeps only strong matches", 32), ["round 178: the filter keeps only", "strong matches"]),
    (
        ("round 178: the model answers with a short reply", 4),
        ["round", "178:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 178: the model answers with a short reply", 8),
        ["round", "178: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 178: the model answers with a short reply", 12),
        ["round 178:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 178: the model answers with a short reply", 16),
        ["round 178: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 178: the model answers with a short reply", 24),
        ["round 178: the model", "answers with a short", "reply"],
    ),
    (("round 178: the model answers with a short reply", 32), ["round 178: the model answers", "with a short reply"]),
    (
        ("round 178: the recorder stores the reasoning trace", 4),
        ["round", "178:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 178: the recorder stores the reasoning trace", 8),
        ["round", "178: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 178: the recorder stores the reasoning trace", 12),
        ["round 178:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 178: the recorder stores the reasoning trace", 16),
        ["round 178: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 178: the recorder stores the reasoning trace", 24),
        ["round 178: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 178: the recorder stores the reasoning trace", 32),
        ["round 178: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 178: the angel watches the processor run", 4),
        ["round", "178:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 178: the angel watches the processor run", 8),
        ["round", "178: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 178: the angel watches the processor run", 12),
        ["round 178:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 178: the angel watches the processor run", 16),
        ["round 178: the", "angel watches", "the processor", "run"],
    ),
    (("round 178: the angel watches the processor run", 24), ["round 178: the angel", "watches the processor", "run"]),
    (("round 178: the angel watches the processor run", 32), ["round 178: the angel watches the", "processor run"]),
    (
        ("round 178: angle of the vector decides the match", 4),
        ["round", "178:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 178: angle of the vector decides the match", 8),
        ["round", "178:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 178: angle of the vector decides the match", 12),
        ["round 178:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 178: angle of the vector decides the match", 16),
        ["round 178: angle", "of the vector", "decides the", "match"],
    ),
    (("round 178: angle of the vector decides the match", 24), ["round 178: angle of the", "vector decides the match"]),
    (("round 178: angle of the vector decides the match", 32), ["round 178: angle of the vector", "decides the match"]),
    (
        ("round 178: the candle burns twice as long at night", 4),
        ["round", "178:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 178: the candle burns twice as long at night", 8),
        ["round", "178: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 178: the candle burns twice as long at night", 12),
        ["round 178:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 178: the candle burns twice as long at night", 16),
        ["round 178: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 178: the candle burns twice as long at night", 24),
        ["round 178: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 178: the candle burns twice as long at night", 32),
        ["round 178: the candle burns", "twice as long at night"],
    ),
    (
        ("round 178: a mirror of the universe in one line", 4),
        ["round", "178:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 178: a mirror of the universe in one line", 8),
        ["round", "178: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 178: a mirror of the universe in one line", 12),
        ["round 178: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 178: a mirror of the universe in one line", 16),
        ["round 178: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 178: a mirror of the universe in one line", 24), ["round 178: a mirror of", "the universe in one line"]),
    (("round 178: a mirror of the universe in one line", 32), ["round 178: a mirror of the", "universe in one line"]),
    (
        ("round 178: the queue drains before the storm", 4),
        ["round", "178:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 178: the queue drains before the storm", 8),
        ["round", "178: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 178: the queue drains before the storm", 12),
        ["round 178:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 178: the queue drains before the storm", 16), ["round 178: the", "queue drains", "before the storm"]),
    (("round 178: the queue drains before the storm", 24), ["round 178: the queue", "drains before the storm"]),
    (("round 178: the queue drains before the storm", 32), ["round 178: the queue drains", "before the storm"]),
    (
        ("kitten178 sitting178 agent178 angle178 universe178 memory178", 6),
        ["kitten178", "sitting178", "agent178", "angle178", "universe178", "memory178"],
    ),
    (
        ("kitten178 sitting178 agent178 angle178 universe178 memory178", 10),
        ["kitten178", "sitting178", "agent178", "angle178", "universe178", "memory178"],
    ),
    (
        ("kitten178 sitting178 agent178 angle178 universe178 memory178", 18),
        ["kitten178", "sitting178", "agent178 angle178", "universe178", "memory178"],
    ),
    (
        ("kitten178 sitting178 agent178 angle178 universe178 memory178", 28),
        ["kitten178 sitting178", "agent178 angle178", "universe178 memory178"],
    ),
    (
        ("sitting178 agent178 angle178 universe178 memory178 stream178", 6),
        ["sitting178", "agent178", "angle178", "universe178", "memory178", "stream178"],
    ),
    (
        ("sitting178 agent178 angle178 universe178 memory178 stream178", 10),
        ["sitting178", "agent178", "angle178", "universe178", "memory178", "stream178"],
    ),
    (
        ("sitting178 agent178 angle178 universe178 memory178 stream178", 18),
        ["sitting178", "agent178 angle178", "universe178", "memory178", "stream178"],
    ),
    (
        ("sitting178 agent178 angle178 universe178 memory178 stream178", 28),
        ["sitting178 agent178 angle178", "universe178 memory178", "stream178"],
    ),
    (
        ("agent178 angle178 universe178 memory178 stream178 context178", 6),
        ["agent178", "angle178", "universe178", "memory178", "stream178", "context178"],
    ),
    (
        ("agent178 angle178 universe178 memory178 stream178 context178", 10),
        ["agent178", "angle178", "universe178", "memory178", "stream178", "context178"],
    ),
    (
        ("agent178 angle178 universe178 memory178 stream178 context178", 18),
        ["agent178 angle178", "universe178", "memory178", "stream178", "context178"],
    ),
    (
        ("agent178 angle178 universe178 memory178 stream178 context178", 28),
        ["agent178 angle178", "universe178 memory178", "stream178 context178"],
    ),
    (
        ("angle178 universe178 memory178 stream178 context178 knowledge178", 6),
        ["angle178", "universe178", "memory178", "stream178", "context178", "knowledge178"],
    ),
    (
        ("angle178 universe178 memory178 stream178 context178 knowledge178", 10),
        ["angle178", "universe178", "memory178", "stream178", "context178", "knowledge178"],
    ),
    (
        ("angle178 universe178 memory178 stream178 context178 knowledge178", 18),
        ["angle178", "universe178", "memory178", "stream178", "context178", "knowledge178"],
    ),
    (
        ("angle178 universe178 memory178 stream178 context178 knowledge178", 28),
        ["angle178 universe178", "memory178 stream178", "context178 knowledge178"],
    ),
    (
        ("universe178 memory178 stream178 context178 knowledge178 vector178", 6),
        ["universe178", "memory178", "stream178", "context178", "knowledge178", "vector178"],
    ),
    (
        ("universe178 memory178 stream178 context178 knowledge178 vector178", 10),
        ["universe178", "memory178", "stream178", "context178", "knowledge178", "vector178"],
    ),
    (
        ("universe178 memory178 stream178 context178 knowledge178 vector178", 18),
        ["universe178", "memory178", "stream178", "context178", "knowledge178", "vector178"],
    ),
    (
        ("universe178 memory178 stream178 context178 knowledge178 vector178", 28),
        ["universe178 memory178", "stream178 context178", "knowledge178 vector178"],
    ),
    (
        ("memory178 stream178 context178 knowledge178 vector178 processor178", 6),
        ["memory178", "stream178", "context178", "knowledge178", "vector178", "processor178"],
    ),
    (
        ("memory178 stream178 context178 knowledge178 vector178 processor178", 10),
        ["memory178", "stream178", "context178", "knowledge178", "vector178", "processor178"],
    ),
    (
        ("memory178 stream178 context178 knowledge178 vector178 processor178", 18),
        ["memory178", "stream178", "context178", "knowledge178", "vector178", "processor178"],
    ),
    (
        ("memory178 stream178 context178 knowledge178 vector178 processor178", 28),
        ["memory178 stream178", "context178 knowledge178", "vector178 processor178"],
    ),
    (
        ("stream178 context178 knowledge178 vector178 processor178 reasoning178", 6),
        ["stream178", "context178", "knowledge178", "vector178", "processor178", "reasoning178"],
    ),
    (
        ("stream178 context178 knowledge178 vector178 processor178 reasoning178", 10),
        ["stream178", "context178", "knowledge178", "vector178", "processor178", "reasoning178"],
    ),
    (
        ("stream178 context178 knowledge178 vector178 processor178 reasoning178", 18),
        ["stream178", "context178", "knowledge178", "vector178", "processor178", "reasoning178"],
    ),
    (
        ("stream178 context178 knowledge178 vector178 processor178 reasoning178", 28),
        ["stream178 context178", "knowledge178 vector178", "processor178 reasoning178"],
    ),
    (
        ("context178 knowledge178 vector178 processor178 reasoning178 machine178", 6),
        ["context178", "knowledge178", "vector178", "processor178", "reasoning178", "machine178"],
    ),
    (
        ("context178 knowledge178 vector178 processor178 reasoning178 machine178", 10),
        ["context178", "knowledge178", "vector178", "processor178", "reasoning178", "machine178"],
    ),
    (
        ("context178 knowledge178 vector178 processor178 reasoning178 machine178", 18),
        ["context178", "knowledge178", "vector178", "processor178", "reasoning178", "machine178"],
    ),
    (
        ("context178 knowledge178 vector178 processor178 reasoning178 machine178", 28),
        ["context178 knowledge178", "vector178 processor178", "reasoning178 machine178"],
    ),
    (
        ("knowledge178 vector178 processor178 reasoning178 machine178 learning178", 6),
        ["knowledge178", "vector178", "processor178", "reasoning178", "machine178", "learning178"],
    ),
    (
        ("knowledge178 vector178 processor178 reasoning178 machine178 learning178", 10),
        ["knowledge178", "vector178", "processor178", "reasoning178", "machine178", "learning178"],
    ),
    (
        ("knowledge178 vector178 processor178 reasoning178 machine178 learning178", 18),
        ["knowledge178", "vector178", "processor178", "reasoning178", "machine178", "learning178"],
    ),
    (
        ("knowledge178 vector178 processor178 reasoning178 machine178 learning178", 28),
        ["knowledge178 vector178", "processor178 reasoning178", "machine178 learning178"],
    ),
    (
        ("vector178 processor178 reasoning178 machine178 learning178 model178", 6),
        ["vector178", "processor178", "reasoning178", "machine178", "learning178", "model178"],
    ),
    (
        ("vector178 processor178 reasoning178 machine178 learning178 model178", 10),
        ["vector178", "processor178", "reasoning178", "machine178", "learning178", "model178"],
    ),
    (
        ("vector178 processor178 reasoning178 machine178 learning178 model178", 18),
        ["vector178", "processor178", "reasoning178", "machine178", "learning178", "model178"],
    ),
    (
        ("vector178 processor178 reasoning178 machine178 learning178 model178", 28),
        ["vector178 processor178", "reasoning178 machine178", "learning178 model178"],
    ),
    (
        ("processor178 reasoning178 machine178 learning178 model178 token178", 6),
        ["processor178", "reasoning178", "machine178", "learning178", "model178", "token178"],
    ),
    (
        ("processor178 reasoning178 machine178 learning178 model178 token178", 10),
        ["processor178", "reasoning178", "machine178", "learning178", "model178", "token178"],
    ),
    (
        ("processor178 reasoning178 machine178 learning178 model178 token178", 18),
        ["processor178", "reasoning178", "machine178", "learning178", "model178 token178"],
    ),
    (
        ("processor178 reasoning178 machine178 learning178 model178 token178", 28),
        ["processor178 reasoning178", "machine178 learning178", "model178 token178"],
    ),
    (
        ("reasoning178 machine178 learning178 model178 token178 prompt178", 6),
        ["reasoning178", "machine178", "learning178", "model178", "token178", "prompt178"],
    ),
    (
        ("reasoning178 machine178 learning178 model178 token178 prompt178", 10),
        ["reasoning178", "machine178", "learning178", "model178", "token178", "prompt178"],
    ),
    (
        ("reasoning178 machine178 learning178 model178 token178 prompt178", 18),
        ["reasoning178", "machine178", "learning178", "model178 token178", "prompt178"],
    ),
    (
        ("reasoning178 machine178 learning178 model178 token178 prompt178", 28),
        ["reasoning178 machine178", "learning178 model178", "token178 prompt178"],
    ),
    (
        ("machine178 learning178 model178 token178 prompt178 session178", 6),
        ["machine178", "learning178", "model178", "token178", "prompt178", "session178"],
    ),
    (
        ("machine178 learning178 model178 token178 prompt178 session178", 10),
        ["machine178", "learning178", "model178", "token178", "prompt178", "session178"],
    ),
    (
        ("machine178 learning178 model178 token178 prompt178 session178", 18),
        ["machine178", "learning178", "model178 token178", "prompt178", "session178"],
    ),
    (
        ("machine178 learning178 model178 token178 prompt178 session178", 28),
        ["machine178 learning178", "model178 token178 prompt178", "session178"],
    ),
    (
        ("learning178 model178 token178 prompt178 session178 library178", 6),
        ["learning178", "model178", "token178", "prompt178", "session178", "library178"],
    ),
    (
        ("learning178 model178 token178 prompt178 session178 library178", 10),
        ["learning178", "model178", "token178", "prompt178", "session178", "library178"],
    ),
    (
        ("learning178 model178 token178 prompt178 session178 library178", 18),
        ["learning178", "model178 token178", "prompt178", "session178", "library178"],
    ),
    (
        ("learning178 model178 token178 prompt178 session178 library178", 28),
        ["learning178 model178", "token178 prompt178", "session178 library178"],
    ),
    (
        ("model178 token178 prompt178 session178 library178 service178", 6),
        ["model178", "token178", "prompt178", "session178", "library178", "service178"],
    ),
    (
        ("model178 token178 prompt178 session178 library178 service178", 10),
        ["model178", "token178", "prompt178", "session178", "library178", "service178"],
    ),
    (
        ("model178 token178 prompt178 session178 library178 service178", 18),
        ["model178 token178", "prompt178", "session178", "library178", "service178"],
    ),
    (
        ("model178 token178 prompt178 session178 library178 service178", 28),
        ["model178 token178 prompt178", "session178 library178", "service178"],
    ),
    (
        ("token178 prompt178 session178 library178 service178 gateway178", 6),
        ["token178", "prompt178", "session178", "library178", "service178", "gateway178"],
    ),
    (
        ("token178 prompt178 session178 library178 service178 gateway178", 10),
        ["token178", "prompt178", "session178", "library178", "service178", "gateway178"],
    ),
    (
        ("token178 prompt178 session178 library178 service178 gateway178", 18),
        ["token178 prompt178", "session178", "library178", "service178", "gateway178"],
    ),
    (
        ("token178 prompt178 session178 library178 service178 gateway178", 28),
        ["token178 prompt178", "session178 library178", "service178 gateway178"],
    ),
    (
        ("prompt178 session178 library178 service178 gateway178 storage178", 6),
        ["prompt178", "session178", "library178", "service178", "gateway178", "storage178"],
    ),
    (
        ("prompt178 session178 library178 service178 gateway178 storage178", 10),
        ["prompt178", "session178", "library178", "service178", "gateway178", "storage178"],
    ),
    (
        ("prompt178 session178 library178 service178 gateway178 storage178", 18),
        ["prompt178", "session178", "library178", "service178", "gateway178", "storage178"],
    ),
    (
        ("prompt178 session178 library178 service178 gateway178 storage178", 28),
        ["prompt178 session178", "library178 service178", "gateway178 storage178"],
    ),
    (
        ("session178 library178 service178 gateway178 storage178 network178", 6),
        ["session178", "library178", "service178", "gateway178", "storage178", "network178"],
    ),
    (
        ("session178 library178 service178 gateway178 storage178 network178", 10),
        ["session178", "library178", "service178", "gateway178", "storage178", "network178"],
    ),
    (
        ("session178 library178 service178 gateway178 storage178 network178", 18),
        ["session178", "library178", "service178", "gateway178", "storage178", "network178"],
    ),
    (
        ("session178 library178 service178 gateway178 storage178 network178", 28),
        ["session178 library178", "service178 gateway178", "storage178 network178"],
    ),
    (
        ("library178 service178 gateway178 storage178 network178 latency178", 6),
        ["library178", "service178", "gateway178", "storage178", "network178", "latency178"],
    ),
    (
        ("library178 service178 gateway178 storage178 network178 latency178", 10),
        ["library178", "service178", "gateway178", "storage178", "network178", "latency178"],
    ),
    (
        ("library178 service178 gateway178 storage178 network178 latency178", 18),
        ["library178", "service178", "gateway178", "storage178", "network178", "latency178"],
    ),
    (
        ("library178 service178 gateway178 storage178 network178 latency178", 28),
        ["library178 service178", "gateway178 storage178", "network178 latency178"],
    ),
    (
        ("service178 gateway178 storage178 network178 latency178 buffer178", 6),
        ["service178", "gateway178", "storage178", "network178", "latency178", "buffer178"],
    ),
    (
        ("service178 gateway178 storage178 network178 latency178 buffer178", 10),
        ["service178", "gateway178", "storage178", "network178", "latency178", "buffer178"],
    ),
    (
        ("service178 gateway178 storage178 network178 latency178 buffer178", 18),
        ["service178", "gateway178", "storage178", "network178", "latency178", "buffer178"],
    ),
    (
        ("service178 gateway178 storage178 network178 latency178 buffer178", 28),
        ["service178 gateway178", "storage178 network178", "latency178 buffer178"],
    ),
    (
        ("gateway178 storage178 network178 latency178 buffer178 queue178", 6),
        ["gateway178", "storage178", "network178", "latency178", "buffer178", "queue178"],
    ),
    (
        ("gateway178 storage178 network178 latency178 buffer178 queue178", 10),
        ["gateway178", "storage178", "network178", "latency178", "buffer178", "queue178"],
    ),
    (
        ("gateway178 storage178 network178 latency178 buffer178 queue178", 18),
        ["gateway178", "storage178", "network178", "latency178", "buffer178 queue178"],
    ),
    (
        ("gateway178 storage178 network178 latency178 buffer178 queue178", 28),
        ["gateway178 storage178", "network178 latency178", "buffer178 queue178"],
    ),
    (
        ("storage178 network178 latency178 buffer178 queue178 worker178", 6),
        ["storage178", "network178", "latency178", "buffer178", "queue178", "worker178"],
    ),
    (
        ("storage178 network178 latency178 buffer178 queue178 worker178", 10),
        ["storage178", "network178", "latency178", "buffer178", "queue178", "worker178"],
    ),
    (
        ("storage178 network178 latency178 buffer178 queue178 worker178", 18),
        ["storage178", "network178", "latency178", "buffer178 queue178", "worker178"],
    ),
    (
        ("storage178 network178 latency178 buffer178 queue178 worker178", 28),
        ["storage178 network178", "latency178 buffer178", "queue178 worker178"],
    ),
    (
        ("network178 latency178 buffer178 queue178 worker178 kernel178", 6),
        ["network178", "latency178", "buffer178", "queue178", "worker178", "kernel178"],
    ),
    (
        ("network178 latency178 buffer178 queue178 worker178 kernel178", 10),
        ["network178", "latency178", "buffer178", "queue178", "worker178", "kernel178"],
    ),
    (
        ("network178 latency178 buffer178 queue178 worker178 kernel178", 18),
        ["network178", "latency178", "buffer178 queue178", "worker178", "kernel178"],
    ),
    (
        ("network178 latency178 buffer178 queue178 worker178 kernel178", 28),
        ["network178 latency178", "buffer178 queue178 worker178", "kernel178"],
    ),
    (
        ("latency178 buffer178 queue178 worker178 kernel178 signal178", 6),
        ["latency178", "buffer178", "queue178", "worker178", "kernel178", "signal178"],
    ),
    (
        ("latency178 buffer178 queue178 worker178 kernel178 signal178", 10),
        ["latency178", "buffer178", "queue178", "worker178", "kernel178", "signal178"],
    ),
    (
        ("latency178 buffer178 queue178 worker178 kernel178 signal178", 18),
        ["latency178", "buffer178 queue178", "worker178", "kernel178", "signal178"],
    ),
    (
        ("latency178 buffer178 queue178 worker178 kernel178 signal178", 28),
        ["latency178 buffer178", "queue178 worker178 kernel178", "signal178"],
    ),
    (
        ("buffer178 queue178 worker178 kernel178 signal178 packet178", 6),
        ["buffer178", "queue178", "worker178", "kernel178", "signal178", "packet178"],
    ),
    (
        ("buffer178 queue178 worker178 kernel178 signal178 packet178", 10),
        ["buffer178", "queue178", "worker178", "kernel178", "signal178", "packet178"],
    ),
    (
        ("buffer178 queue178 worker178 kernel178 signal178 packet178", 18),
        ["buffer178 queue178", "worker178", "kernel178", "signal178", "packet178"],
    ),
    (
        ("buffer178 queue178 worker178 kernel178 signal178 packet178", 28),
        ["buffer178 queue178 worker178", "kernel178 signal178", "packet178"],
    ),
    (
        ("queue178 worker178 kernel178 signal178 packet178 router178", 6),
        ["queue178", "worker178", "kernel178", "signal178", "packet178", "router178"],
    ),
    (
        ("queue178 worker178 kernel178 signal178 packet178 router178", 10),
        ["queue178", "worker178", "kernel178", "signal178", "packet178", "router178"],
    ),
    (
        ("queue178 worker178 kernel178 signal178 packet178 router178", 18),
        ["queue178 worker178", "kernel178", "signal178", "packet178", "router178"],
    ),
    (
        ("queue178 worker178 kernel178 signal178 packet178 router178", 28),
        ["queue178 worker178 kernel178", "signal178 packet178", "router178"],
    ),
    (
        ("worker178 kernel178 signal178 packet178 router178 cluster178", 6),
        ["worker178", "kernel178", "signal178", "packet178", "router178", "cluster178"],
    ),
    (
        ("worker178 kernel178 signal178 packet178 router178 cluster178", 10),
        ["worker178", "kernel178", "signal178", "packet178", "router178", "cluster178"],
    ),
    (
        ("worker178 kernel178 signal178 packet178 router178 cluster178", 18),
        ["worker178", "kernel178", "signal178", "packet178", "router178", "cluster178"],
    ),
    (
        ("worker178 kernel178 signal178 packet178 router178 cluster178", 28),
        ["worker178 kernel178", "signal178 packet178", "router178 cluster178"],
    ),
    (
        ("kernel178 signal178 packet178 router178 cluster178 mirror178", 6),
        ["kernel178", "signal178", "packet178", "router178", "cluster178", "mirror178"],
    ),
    (
        ("kernel178 signal178 packet178 router178 cluster178 mirror178", 10),
        ["kernel178", "signal178", "packet178", "router178", "cluster178", "mirror178"],
    ),
    (
        ("kernel178 signal178 packet178 router178 cluster178 mirror178", 18),
        ["kernel178", "signal178", "packet178", "router178", "cluster178", "mirror178"],
    ),
    (
        ("kernel178 signal178 packet178 router178 cluster178 mirror178", 28),
        ["kernel178 signal178", "packet178 router178", "cluster178 mirror178"],
    ),
    (
        ("signal178 packet178 router178 cluster178 mirror178 filter178", 6),
        ["signal178", "packet178", "router178", "cluster178", "mirror178", "filter178"],
    ),
    (
        ("signal178 packet178 router178 cluster178 mirror178 filter178", 10),
        ["signal178", "packet178", "router178", "cluster178", "mirror178", "filter178"],
    ),
    (
        ("signal178 packet178 router178 cluster178 mirror178 filter178", 18),
        ["signal178", "packet178", "router178", "cluster178", "mirror178", "filter178"],
    ),
    (
        ("signal178 packet178 router178 cluster178 mirror178 filter178", 28),
        ["signal178 packet178", "router178 cluster178", "mirror178 filter178"],
    ),
    (
        ("packet178 router178 cluster178 mirror178 filter178 ranking178", 6),
        ["packet178", "router178", "cluster178", "mirror178", "filter178", "ranking178"],
    ),
    (
        ("packet178 router178 cluster178 mirror178 filter178 ranking178", 10),
        ["packet178", "router178", "cluster178", "mirror178", "filter178", "ranking178"],
    ),
    (
        ("packet178 router178 cluster178 mirror178 filter178 ranking178", 18),
        ["packet178", "router178", "cluster178", "mirror178", "filter178", "ranking178"],
    ),
    (
        ("packet178 router178 cluster178 mirror178 filter178 ranking178", 28),
        ["packet178 router178", "cluster178 mirror178", "filter178 ranking178"],
    ),
    (
        ("router178 cluster178 mirror178 filter178 ranking178 encoding178", 6),
        ["router178", "cluster178", "mirror178", "filter178", "ranking178", "encoding178"],
    ),
    (
        ("router178 cluster178 mirror178 filter178 ranking178 encoding178", 10),
        ["router178", "cluster178", "mirror178", "filter178", "ranking178", "encoding178"],
    ),
    (
        ("router178 cluster178 mirror178 filter178 ranking178 encoding178", 18),
        ["router178", "cluster178", "mirror178", "filter178", "ranking178", "encoding178"],
    ),
    (
        ("router178 cluster178 mirror178 filter178 ranking178 encoding178", 28),
        ["router178 cluster178", "mirror178 filter178", "ranking178 encoding178"],
    ),
    (
        ("cluster178 mirror178 filter178 ranking178 encoding178 mapping178", 6),
        ["cluster178", "mirror178", "filter178", "ranking178", "encoding178", "mapping178"],
    ),
    (
        ("cluster178 mirror178 filter178 ranking178 encoding178 mapping178", 10),
        ["cluster178", "mirror178", "filter178", "ranking178", "encoding178", "mapping178"],
    ),
    (
        ("cluster178 mirror178 filter178 ranking178 encoding178 mapping178", 18),
        ["cluster178", "mirror178", "filter178", "ranking178", "encoding178", "mapping178"],
    ),
    (
        ("cluster178 mirror178 filter178 ranking178 encoding178 mapping178", 28),
        ["cluster178 mirror178", "filter178 ranking178", "encoding178 mapping178"],
    ),
    (
        ("mirror178 filter178 ranking178 encoding178 mapping178 record178", 6),
        ["mirror178", "filter178", "ranking178", "encoding178", "mapping178", "record178"],
    ),
    (
        ("mirror178 filter178 ranking178 encoding178 mapping178 record178", 10),
        ["mirror178", "filter178", "ranking178", "encoding178", "mapping178", "record178"],
    ),
    (
        ("mirror178 filter178 ranking178 encoding178 mapping178 record178", 18),
        ["mirror178", "filter178", "ranking178", "encoding178", "mapping178", "record178"],
    ),
    (
        ("mirror178 filter178 ranking178 encoding178 mapping178 record178", 28),
        ["mirror178 filter178", "ranking178 encoding178", "mapping178 record178"],
    ),
    (
        ("filter178 ranking178 encoding178 mapping178 record178 candle178", 6),
        ["filter178", "ranking178", "encoding178", "mapping178", "record178", "candle178"],
    ),
    (
        ("filter178 ranking178 encoding178 mapping178 record178 candle178", 10),
        ["filter178", "ranking178", "encoding178", "mapping178", "record178", "candle178"],
    ),
    (
        ("filter178 ranking178 encoding178 mapping178 record178 candle178", 18),
        ["filter178", "ranking178", "encoding178", "mapping178", "record178", "candle178"],
    ),
    (
        ("filter178 ranking178 encoding178 mapping178 record178 candle178", 28),
        ["filter178 ranking178", "encoding178 mapping178", "record178 candle178"],
    ),
    (
        ("ranking178 encoding178 mapping178 record178 candle178 thread178", 6),
        ["ranking178", "encoding178", "mapping178", "record178", "candle178", "thread178"],
    ),
    (
        ("ranking178 encoding178 mapping178 record178 candle178 thread178", 10),
        ["ranking178", "encoding178", "mapping178", "record178", "candle178", "thread178"],
    ),
    (
        ("ranking178 encoding178 mapping178 record178 candle178 thread178", 18),
        ["ranking178", "encoding178", "mapping178", "record178", "candle178", "thread178"],
    ),
    (
        ("ranking178 encoding178 mapping178 record178 candle178 thread178", 28),
        ["ranking178 encoding178", "mapping178 record178", "candle178 thread178"],
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
