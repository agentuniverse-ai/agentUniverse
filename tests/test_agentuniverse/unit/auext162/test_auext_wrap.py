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
        ("round 162: the quick brown fox jumps over the lazy dog", 4),
        ["round", "162:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 162: the quick brown fox jumps over the lazy dog", 8),
        ["round", "162: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 162: the quick brown fox jumps over the lazy dog", 12),
        ["round 162:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 162: the quick brown fox jumps over the lazy dog", 16),
        ["round 162: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 162: the quick brown fox jumps over the lazy dog", 24),
        ["round 162: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 162: the quick brown fox jumps over the lazy dog", 32),
        ["round 162: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 162: agentuniverse is a framework for multi agents", 4),
        ["round", "162:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 162: agentuniverse is a framework for multi agents", 8),
        ["round", "162:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 162: agentuniverse is a framework for multi agents", 12),
        ["round 162:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 162: agentuniverse is a framework for multi agents", 16),
        ["round 162:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 162: agentuniverse is a framework for multi agents", 24),
        ["round 162: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 162: agentuniverse is a framework for multi agents", 32),
        ["round 162: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 162: knowledge stored as vectors enables retrieval", 4),
        ["round", "162:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 162: knowledge stored as vectors enables retrieval", 8),
        ["round", "162:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 162: knowledge stored as vectors enables retrieval", 12),
        ["round 162:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 162: knowledge stored as vectors enables retrieval", 16),
        ["round 162:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 162: knowledge stored as vectors enables retrieval", 24),
        ["round 162: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 162: knowledge stored as vectors enables retrieval", 32),
        ["round 162: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 162: the processor reads the record then stops", 4),
        ["round", "162:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 162: the processor reads the record then stops", 8),
        ["round", "162: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 162: the processor reads the record then stops", 12),
        ["round 162:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 162: the processor reads the record then stops", 16),
        ["round 162: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 162: the processor reads the record then stops", 24),
        ["round 162: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 162: the processor reads the record then stops", 32),
        ["round 162: the processor reads", "the record then stops"],
    ),
    (
        ("round 162: a worker pulls the next task from the queue", 4),
        ["round", "162:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 162: a worker pulls the next task from the queue", 8),
        ["round", "162: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 162: a worker pulls the next task from the queue", 12),
        ["round 162: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 162: a worker pulls the next task from the queue", 16),
        ["round 162: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 162: a worker pulls the next task from the queue", 24),
        ["round 162: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 162: a worker pulls the next task from the queue", 32),
        ["round 162: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 162: signals travel through the network layer", 4),
        ["round", "162:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 162: signals travel through the network layer", 8),
        ["round", "162:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 162: signals travel through the network layer", 12),
        ["round 162:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 162: signals travel through the network layer", 16),
        ["round 162:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 162: signals travel through the network layer", 24),
        ["round 162: signals", "travel through the", "network layer"],
    ),
    (
        ("round 162: signals travel through the network layer", 32),
        ["round 162: signals travel", "through the network layer"],
    ),
    (
        ("round 162: the gateway routes each request by policy", 4),
        ["round", "162:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 162: the gateway routes each request by policy", 8),
        ["round", "162: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 162: the gateway routes each request by policy", 12),
        ["round 162:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 162: the gateway routes each request by policy", 16),
        ["round 162: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 162: the gateway routes each request by policy", 24),
        ["round 162: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 162: the gateway routes each request by policy", 32),
        ["round 162: the gateway routes", "each request by policy"],
    ),
    (
        ("round 162: memory grows until the buffer is full", 4),
        ["round", "162:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 162: memory grows until the buffer is full", 8),
        ["round", "162:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 162: memory grows until the buffer is full", 12),
        ["round 162:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 162: memory grows until the buffer is full", 16),
        ["round 162:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 162: memory grows until the buffer is full", 24), ["round 162: memory grows", "until the buffer is full"]),
    (("round 162: memory grows until the buffer is full", 32), ["round 162: memory grows until", "the buffer is full"]),
    (
        ("round 162: the cluster mirrors every packet twice", 4),
        ["round", "162:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 162: the cluster mirrors every packet twice", 8),
        ["round", "162: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 162: the cluster mirrors every packet twice", 12),
        ["round 162:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 162: the cluster mirrors every packet twice", 16),
        ["round 162: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 162: the cluster mirrors every packet twice", 24),
        ["round 162: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 162: the cluster mirrors every packet twice", 32),
        ["round 162: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 162: ranking uses tokens learned from the corpus", 4),
        ["round", "162:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 162: ranking uses tokens learned from the corpus", 8),
        ["round", "162:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 162: ranking uses tokens learned from the corpus", 12),
        ["round 162:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 162: ranking uses tokens learned from the corpus", 16),
        ["round 162:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 162: ranking uses tokens learned from the corpus", 24),
        ["round 162: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 162: ranking uses tokens learned from the corpus", 32),
        ["round 162: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 162: a long session ends when the candle dies", 4),
        ["round", "162:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 162: a long session ends when the candle dies", 8),
        ["round", "162: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 162: a long session ends when the candle dies", 12),
        ["round 162: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 162: a long session ends when the candle dies", 16),
        ["round 162: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 162: a long session ends when the candle dies", 24),
        ["round 162: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 162: a long session ends when the candle dies", 32),
        ["round 162: a long session ends", "when the candle dies"],
    ),
    (
        ("round 162: encode the prompt then map the result", 4),
        ["round", "162:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 162: encode the prompt then map the result", 8),
        ["round", "162:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 162: encode the prompt then map the result", 12),
        ["round 162:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 162: encode the prompt then map the result", 16),
        ["round 162:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 162: encode the prompt then map the result", 24),
        ["round 162: encode the", "prompt then map the", "result"],
    ),
    (("round 162: encode the prompt then map the result", 32), ["round 162: encode the prompt", "then map the result"]),
    (
        ("round 162: the kernel wakes the worker at dawn", 4),
        ["round", "162:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 162: the kernel wakes the worker at dawn", 8),
        ["round", "162: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 162: the kernel wakes the worker at dawn", 12),
        ["round 162:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 162: the kernel wakes the worker at dawn", 16), ["round 162: the", "kernel wakes the", "worker at dawn"]),
    (("round 162: the kernel wakes the worker at dawn", 24), ["round 162: the kernel", "wakes the worker at dawn"]),
    (("round 162: the kernel wakes the worker at dawn", 32), ["round 162: the kernel wakes the", "worker at dawn"]),
    (
        ("round 162: service latency drops after the patch", 4),
        ["round", "162:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 162: service latency drops after the patch", 8),
        ["round", "162:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 162: service latency drops after the patch", 12),
        ["round 162:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 162: service latency drops after the patch", 16),
        ["round 162:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 162: service latency drops after the patch", 24),
        ["round 162: service", "latency drops after the", "patch"],
    ),
    (("round 162: service latency drops after the patch", 32), ["round 162: service latency drops", "after the patch"]),
    (
        ("round 162: the library caches every vector it sees", 4),
        ["round", "162:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 162: the library caches every vector it sees", 8),
        ["round", "162: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 162: the library caches every vector it sees", 12),
        ["round 162:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 162: the library caches every vector it sees", 16),
        ["round 162: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 162: the library caches every vector it sees", 24),
        ["round 162: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 162: the library caches every vector it sees", 32),
        ["round 162: the library caches", "every vector it sees"],
    ),
    (
        ("round 162: agents argue then the debate resolves", 4),
        ["round", "162:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 162: agents argue then the debate resolves", 8),
        ["round", "162:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 162: agents argue then the debate resolves", 12),
        ["round 162:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 162: agents argue then the debate resolves", 16),
        ["round 162:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 162: agents argue then the debate resolves", 24), ["round 162: agents argue", "then the debate resolves"]),
    (("round 162: agents argue then the debate resolves", 32), ["round 162: agents argue then the", "debate resolves"]),
    (
        ("round 162: the filter keeps only strong matches", 4),
        ["round", "162:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 162: the filter keeps only strong matches", 8),
        ["round", "162: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 162: the filter keeps only strong matches", 12),
        ["round 162:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 162: the filter keeps only strong matches", 16),
        ["round 162: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 162: the filter keeps only strong matches", 24),
        ["round 162: the filter", "keeps only strong", "matches"],
    ),
    (("round 162: the filter keeps only strong matches", 32), ["round 162: the filter keeps only", "strong matches"]),
    (
        ("round 162: the model answers with a short reply", 4),
        ["round", "162:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 162: the model answers with a short reply", 8),
        ["round", "162: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 162: the model answers with a short reply", 12),
        ["round 162:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 162: the model answers with a short reply", 16),
        ["round 162: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 162: the model answers with a short reply", 24),
        ["round 162: the model", "answers with a short", "reply"],
    ),
    (("round 162: the model answers with a short reply", 32), ["round 162: the model answers", "with a short reply"]),
    (
        ("round 162: the recorder stores the reasoning trace", 4),
        ["round", "162:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 162: the recorder stores the reasoning trace", 8),
        ["round", "162: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 162: the recorder stores the reasoning trace", 12),
        ["round 162:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 162: the recorder stores the reasoning trace", 16),
        ["round 162: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 162: the recorder stores the reasoning trace", 24),
        ["round 162: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 162: the recorder stores the reasoning trace", 32),
        ["round 162: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 162: the angel watches the processor run", 4),
        ["round", "162:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 162: the angel watches the processor run", 8),
        ["round", "162: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 162: the angel watches the processor run", 12),
        ["round 162:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 162: the angel watches the processor run", 16),
        ["round 162: the", "angel watches", "the processor", "run"],
    ),
    (("round 162: the angel watches the processor run", 24), ["round 162: the angel", "watches the processor", "run"]),
    (("round 162: the angel watches the processor run", 32), ["round 162: the angel watches the", "processor run"]),
    (
        ("round 162: angle of the vector decides the match", 4),
        ["round", "162:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 162: angle of the vector decides the match", 8),
        ["round", "162:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 162: angle of the vector decides the match", 12),
        ["round 162:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 162: angle of the vector decides the match", 16),
        ["round 162: angle", "of the vector", "decides the", "match"],
    ),
    (("round 162: angle of the vector decides the match", 24), ["round 162: angle of the", "vector decides the match"]),
    (("round 162: angle of the vector decides the match", 32), ["round 162: angle of the vector", "decides the match"]),
    (
        ("round 162: the candle burns twice as long at night", 4),
        ["round", "162:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 162: the candle burns twice as long at night", 8),
        ["round", "162: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 162: the candle burns twice as long at night", 12),
        ["round 162:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 162: the candle burns twice as long at night", 16),
        ["round 162: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 162: the candle burns twice as long at night", 24),
        ["round 162: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 162: the candle burns twice as long at night", 32),
        ["round 162: the candle burns", "twice as long at night"],
    ),
    (
        ("round 162: a mirror of the universe in one line", 4),
        ["round", "162:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 162: a mirror of the universe in one line", 8),
        ["round", "162: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 162: a mirror of the universe in one line", 12),
        ["round 162: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 162: a mirror of the universe in one line", 16),
        ["round 162: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 162: a mirror of the universe in one line", 24), ["round 162: a mirror of", "the universe in one line"]),
    (("round 162: a mirror of the universe in one line", 32), ["round 162: a mirror of the", "universe in one line"]),
    (
        ("round 162: the queue drains before the storm", 4),
        ["round", "162:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 162: the queue drains before the storm", 8),
        ["round", "162: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 162: the queue drains before the storm", 12),
        ["round 162:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 162: the queue drains before the storm", 16), ["round 162: the", "queue drains", "before the storm"]),
    (("round 162: the queue drains before the storm", 24), ["round 162: the queue", "drains before the storm"]),
    (("round 162: the queue drains before the storm", 32), ["round 162: the queue drains", "before the storm"]),
    (
        ("kitten162 sitting162 agent162 angle162 universe162 memory162", 6),
        ["kitten162", "sitting162", "agent162", "angle162", "universe162", "memory162"],
    ),
    (
        ("kitten162 sitting162 agent162 angle162 universe162 memory162", 10),
        ["kitten162", "sitting162", "agent162", "angle162", "universe162", "memory162"],
    ),
    (
        ("kitten162 sitting162 agent162 angle162 universe162 memory162", 18),
        ["kitten162", "sitting162", "agent162 angle162", "universe162", "memory162"],
    ),
    (
        ("kitten162 sitting162 agent162 angle162 universe162 memory162", 28),
        ["kitten162 sitting162", "agent162 angle162", "universe162 memory162"],
    ),
    (
        ("sitting162 agent162 angle162 universe162 memory162 stream162", 6),
        ["sitting162", "agent162", "angle162", "universe162", "memory162", "stream162"],
    ),
    (
        ("sitting162 agent162 angle162 universe162 memory162 stream162", 10),
        ["sitting162", "agent162", "angle162", "universe162", "memory162", "stream162"],
    ),
    (
        ("sitting162 agent162 angle162 universe162 memory162 stream162", 18),
        ["sitting162", "agent162 angle162", "universe162", "memory162", "stream162"],
    ),
    (
        ("sitting162 agent162 angle162 universe162 memory162 stream162", 28),
        ["sitting162 agent162 angle162", "universe162 memory162", "stream162"],
    ),
    (
        ("agent162 angle162 universe162 memory162 stream162 context162", 6),
        ["agent162", "angle162", "universe162", "memory162", "stream162", "context162"],
    ),
    (
        ("agent162 angle162 universe162 memory162 stream162 context162", 10),
        ["agent162", "angle162", "universe162", "memory162", "stream162", "context162"],
    ),
    (
        ("agent162 angle162 universe162 memory162 stream162 context162", 18),
        ["agent162 angle162", "universe162", "memory162", "stream162", "context162"],
    ),
    (
        ("agent162 angle162 universe162 memory162 stream162 context162", 28),
        ["agent162 angle162", "universe162 memory162", "stream162 context162"],
    ),
    (
        ("angle162 universe162 memory162 stream162 context162 knowledge162", 6),
        ["angle162", "universe162", "memory162", "stream162", "context162", "knowledge162"],
    ),
    (
        ("angle162 universe162 memory162 stream162 context162 knowledge162", 10),
        ["angle162", "universe162", "memory162", "stream162", "context162", "knowledge162"],
    ),
    (
        ("angle162 universe162 memory162 stream162 context162 knowledge162", 18),
        ["angle162", "universe162", "memory162", "stream162", "context162", "knowledge162"],
    ),
    (
        ("angle162 universe162 memory162 stream162 context162 knowledge162", 28),
        ["angle162 universe162", "memory162 stream162", "context162 knowledge162"],
    ),
    (
        ("universe162 memory162 stream162 context162 knowledge162 vector162", 6),
        ["universe162", "memory162", "stream162", "context162", "knowledge162", "vector162"],
    ),
    (
        ("universe162 memory162 stream162 context162 knowledge162 vector162", 10),
        ["universe162", "memory162", "stream162", "context162", "knowledge162", "vector162"],
    ),
    (
        ("universe162 memory162 stream162 context162 knowledge162 vector162", 18),
        ["universe162", "memory162", "stream162", "context162", "knowledge162", "vector162"],
    ),
    (
        ("universe162 memory162 stream162 context162 knowledge162 vector162", 28),
        ["universe162 memory162", "stream162 context162", "knowledge162 vector162"],
    ),
    (
        ("memory162 stream162 context162 knowledge162 vector162 processor162", 6),
        ["memory162", "stream162", "context162", "knowledge162", "vector162", "processor162"],
    ),
    (
        ("memory162 stream162 context162 knowledge162 vector162 processor162", 10),
        ["memory162", "stream162", "context162", "knowledge162", "vector162", "processor162"],
    ),
    (
        ("memory162 stream162 context162 knowledge162 vector162 processor162", 18),
        ["memory162", "stream162", "context162", "knowledge162", "vector162", "processor162"],
    ),
    (
        ("memory162 stream162 context162 knowledge162 vector162 processor162", 28),
        ["memory162 stream162", "context162 knowledge162", "vector162 processor162"],
    ),
    (
        ("stream162 context162 knowledge162 vector162 processor162 reasoning162", 6),
        ["stream162", "context162", "knowledge162", "vector162", "processor162", "reasoning162"],
    ),
    (
        ("stream162 context162 knowledge162 vector162 processor162 reasoning162", 10),
        ["stream162", "context162", "knowledge162", "vector162", "processor162", "reasoning162"],
    ),
    (
        ("stream162 context162 knowledge162 vector162 processor162 reasoning162", 18),
        ["stream162", "context162", "knowledge162", "vector162", "processor162", "reasoning162"],
    ),
    (
        ("stream162 context162 knowledge162 vector162 processor162 reasoning162", 28),
        ["stream162 context162", "knowledge162 vector162", "processor162 reasoning162"],
    ),
    (
        ("context162 knowledge162 vector162 processor162 reasoning162 machine162", 6),
        ["context162", "knowledge162", "vector162", "processor162", "reasoning162", "machine162"],
    ),
    (
        ("context162 knowledge162 vector162 processor162 reasoning162 machine162", 10),
        ["context162", "knowledge162", "vector162", "processor162", "reasoning162", "machine162"],
    ),
    (
        ("context162 knowledge162 vector162 processor162 reasoning162 machine162", 18),
        ["context162", "knowledge162", "vector162", "processor162", "reasoning162", "machine162"],
    ),
    (
        ("context162 knowledge162 vector162 processor162 reasoning162 machine162", 28),
        ["context162 knowledge162", "vector162 processor162", "reasoning162 machine162"],
    ),
    (
        ("knowledge162 vector162 processor162 reasoning162 machine162 learning162", 6),
        ["knowledge162", "vector162", "processor162", "reasoning162", "machine162", "learning162"],
    ),
    (
        ("knowledge162 vector162 processor162 reasoning162 machine162 learning162", 10),
        ["knowledge162", "vector162", "processor162", "reasoning162", "machine162", "learning162"],
    ),
    (
        ("knowledge162 vector162 processor162 reasoning162 machine162 learning162", 18),
        ["knowledge162", "vector162", "processor162", "reasoning162", "machine162", "learning162"],
    ),
    (
        ("knowledge162 vector162 processor162 reasoning162 machine162 learning162", 28),
        ["knowledge162 vector162", "processor162 reasoning162", "machine162 learning162"],
    ),
    (
        ("vector162 processor162 reasoning162 machine162 learning162 model162", 6),
        ["vector162", "processor162", "reasoning162", "machine162", "learning162", "model162"],
    ),
    (
        ("vector162 processor162 reasoning162 machine162 learning162 model162", 10),
        ["vector162", "processor162", "reasoning162", "machine162", "learning162", "model162"],
    ),
    (
        ("vector162 processor162 reasoning162 machine162 learning162 model162", 18),
        ["vector162", "processor162", "reasoning162", "machine162", "learning162", "model162"],
    ),
    (
        ("vector162 processor162 reasoning162 machine162 learning162 model162", 28),
        ["vector162 processor162", "reasoning162 machine162", "learning162 model162"],
    ),
    (
        ("processor162 reasoning162 machine162 learning162 model162 token162", 6),
        ["processor162", "reasoning162", "machine162", "learning162", "model162", "token162"],
    ),
    (
        ("processor162 reasoning162 machine162 learning162 model162 token162", 10),
        ["processor162", "reasoning162", "machine162", "learning162", "model162", "token162"],
    ),
    (
        ("processor162 reasoning162 machine162 learning162 model162 token162", 18),
        ["processor162", "reasoning162", "machine162", "learning162", "model162 token162"],
    ),
    (
        ("processor162 reasoning162 machine162 learning162 model162 token162", 28),
        ["processor162 reasoning162", "machine162 learning162", "model162 token162"],
    ),
    (
        ("reasoning162 machine162 learning162 model162 token162 prompt162", 6),
        ["reasoning162", "machine162", "learning162", "model162", "token162", "prompt162"],
    ),
    (
        ("reasoning162 machine162 learning162 model162 token162 prompt162", 10),
        ["reasoning162", "machine162", "learning162", "model162", "token162", "prompt162"],
    ),
    (
        ("reasoning162 machine162 learning162 model162 token162 prompt162", 18),
        ["reasoning162", "machine162", "learning162", "model162 token162", "prompt162"],
    ),
    (
        ("reasoning162 machine162 learning162 model162 token162 prompt162", 28),
        ["reasoning162 machine162", "learning162 model162", "token162 prompt162"],
    ),
    (
        ("machine162 learning162 model162 token162 prompt162 session162", 6),
        ["machine162", "learning162", "model162", "token162", "prompt162", "session162"],
    ),
    (
        ("machine162 learning162 model162 token162 prompt162 session162", 10),
        ["machine162", "learning162", "model162", "token162", "prompt162", "session162"],
    ),
    (
        ("machine162 learning162 model162 token162 prompt162 session162", 18),
        ["machine162", "learning162", "model162 token162", "prompt162", "session162"],
    ),
    (
        ("machine162 learning162 model162 token162 prompt162 session162", 28),
        ["machine162 learning162", "model162 token162 prompt162", "session162"],
    ),
    (
        ("learning162 model162 token162 prompt162 session162 library162", 6),
        ["learning162", "model162", "token162", "prompt162", "session162", "library162"],
    ),
    (
        ("learning162 model162 token162 prompt162 session162 library162", 10),
        ["learning162", "model162", "token162", "prompt162", "session162", "library162"],
    ),
    (
        ("learning162 model162 token162 prompt162 session162 library162", 18),
        ["learning162", "model162 token162", "prompt162", "session162", "library162"],
    ),
    (
        ("learning162 model162 token162 prompt162 session162 library162", 28),
        ["learning162 model162", "token162 prompt162", "session162 library162"],
    ),
    (
        ("model162 token162 prompt162 session162 library162 service162", 6),
        ["model162", "token162", "prompt162", "session162", "library162", "service162"],
    ),
    (
        ("model162 token162 prompt162 session162 library162 service162", 10),
        ["model162", "token162", "prompt162", "session162", "library162", "service162"],
    ),
    (
        ("model162 token162 prompt162 session162 library162 service162", 18),
        ["model162 token162", "prompt162", "session162", "library162", "service162"],
    ),
    (
        ("model162 token162 prompt162 session162 library162 service162", 28),
        ["model162 token162 prompt162", "session162 library162", "service162"],
    ),
    (
        ("token162 prompt162 session162 library162 service162 gateway162", 6),
        ["token162", "prompt162", "session162", "library162", "service162", "gateway162"],
    ),
    (
        ("token162 prompt162 session162 library162 service162 gateway162", 10),
        ["token162", "prompt162", "session162", "library162", "service162", "gateway162"],
    ),
    (
        ("token162 prompt162 session162 library162 service162 gateway162", 18),
        ["token162 prompt162", "session162", "library162", "service162", "gateway162"],
    ),
    (
        ("token162 prompt162 session162 library162 service162 gateway162", 28),
        ["token162 prompt162", "session162 library162", "service162 gateway162"],
    ),
    (
        ("prompt162 session162 library162 service162 gateway162 storage162", 6),
        ["prompt162", "session162", "library162", "service162", "gateway162", "storage162"],
    ),
    (
        ("prompt162 session162 library162 service162 gateway162 storage162", 10),
        ["prompt162", "session162", "library162", "service162", "gateway162", "storage162"],
    ),
    (
        ("prompt162 session162 library162 service162 gateway162 storage162", 18),
        ["prompt162", "session162", "library162", "service162", "gateway162", "storage162"],
    ),
    (
        ("prompt162 session162 library162 service162 gateway162 storage162", 28),
        ["prompt162 session162", "library162 service162", "gateway162 storage162"],
    ),
    (
        ("session162 library162 service162 gateway162 storage162 network162", 6),
        ["session162", "library162", "service162", "gateway162", "storage162", "network162"],
    ),
    (
        ("session162 library162 service162 gateway162 storage162 network162", 10),
        ["session162", "library162", "service162", "gateway162", "storage162", "network162"],
    ),
    (
        ("session162 library162 service162 gateway162 storage162 network162", 18),
        ["session162", "library162", "service162", "gateway162", "storage162", "network162"],
    ),
    (
        ("session162 library162 service162 gateway162 storage162 network162", 28),
        ["session162 library162", "service162 gateway162", "storage162 network162"],
    ),
    (
        ("library162 service162 gateway162 storage162 network162 latency162", 6),
        ["library162", "service162", "gateway162", "storage162", "network162", "latency162"],
    ),
    (
        ("library162 service162 gateway162 storage162 network162 latency162", 10),
        ["library162", "service162", "gateway162", "storage162", "network162", "latency162"],
    ),
    (
        ("library162 service162 gateway162 storage162 network162 latency162", 18),
        ["library162", "service162", "gateway162", "storage162", "network162", "latency162"],
    ),
    (
        ("library162 service162 gateway162 storage162 network162 latency162", 28),
        ["library162 service162", "gateway162 storage162", "network162 latency162"],
    ),
    (
        ("service162 gateway162 storage162 network162 latency162 buffer162", 6),
        ["service162", "gateway162", "storage162", "network162", "latency162", "buffer162"],
    ),
    (
        ("service162 gateway162 storage162 network162 latency162 buffer162", 10),
        ["service162", "gateway162", "storage162", "network162", "latency162", "buffer162"],
    ),
    (
        ("service162 gateway162 storage162 network162 latency162 buffer162", 18),
        ["service162", "gateway162", "storage162", "network162", "latency162", "buffer162"],
    ),
    (
        ("service162 gateway162 storage162 network162 latency162 buffer162", 28),
        ["service162 gateway162", "storage162 network162", "latency162 buffer162"],
    ),
    (
        ("gateway162 storage162 network162 latency162 buffer162 queue162", 6),
        ["gateway162", "storage162", "network162", "latency162", "buffer162", "queue162"],
    ),
    (
        ("gateway162 storage162 network162 latency162 buffer162 queue162", 10),
        ["gateway162", "storage162", "network162", "latency162", "buffer162", "queue162"],
    ),
    (
        ("gateway162 storage162 network162 latency162 buffer162 queue162", 18),
        ["gateway162", "storage162", "network162", "latency162", "buffer162 queue162"],
    ),
    (
        ("gateway162 storage162 network162 latency162 buffer162 queue162", 28),
        ["gateway162 storage162", "network162 latency162", "buffer162 queue162"],
    ),
    (
        ("storage162 network162 latency162 buffer162 queue162 worker162", 6),
        ["storage162", "network162", "latency162", "buffer162", "queue162", "worker162"],
    ),
    (
        ("storage162 network162 latency162 buffer162 queue162 worker162", 10),
        ["storage162", "network162", "latency162", "buffer162", "queue162", "worker162"],
    ),
    (
        ("storage162 network162 latency162 buffer162 queue162 worker162", 18),
        ["storage162", "network162", "latency162", "buffer162 queue162", "worker162"],
    ),
    (
        ("storage162 network162 latency162 buffer162 queue162 worker162", 28),
        ["storage162 network162", "latency162 buffer162", "queue162 worker162"],
    ),
    (
        ("network162 latency162 buffer162 queue162 worker162 kernel162", 6),
        ["network162", "latency162", "buffer162", "queue162", "worker162", "kernel162"],
    ),
    (
        ("network162 latency162 buffer162 queue162 worker162 kernel162", 10),
        ["network162", "latency162", "buffer162", "queue162", "worker162", "kernel162"],
    ),
    (
        ("network162 latency162 buffer162 queue162 worker162 kernel162", 18),
        ["network162", "latency162", "buffer162 queue162", "worker162", "kernel162"],
    ),
    (
        ("network162 latency162 buffer162 queue162 worker162 kernel162", 28),
        ["network162 latency162", "buffer162 queue162 worker162", "kernel162"],
    ),
    (
        ("latency162 buffer162 queue162 worker162 kernel162 signal162", 6),
        ["latency162", "buffer162", "queue162", "worker162", "kernel162", "signal162"],
    ),
    (
        ("latency162 buffer162 queue162 worker162 kernel162 signal162", 10),
        ["latency162", "buffer162", "queue162", "worker162", "kernel162", "signal162"],
    ),
    (
        ("latency162 buffer162 queue162 worker162 kernel162 signal162", 18),
        ["latency162", "buffer162 queue162", "worker162", "kernel162", "signal162"],
    ),
    (
        ("latency162 buffer162 queue162 worker162 kernel162 signal162", 28),
        ["latency162 buffer162", "queue162 worker162 kernel162", "signal162"],
    ),
    (
        ("buffer162 queue162 worker162 kernel162 signal162 packet162", 6),
        ["buffer162", "queue162", "worker162", "kernel162", "signal162", "packet162"],
    ),
    (
        ("buffer162 queue162 worker162 kernel162 signal162 packet162", 10),
        ["buffer162", "queue162", "worker162", "kernel162", "signal162", "packet162"],
    ),
    (
        ("buffer162 queue162 worker162 kernel162 signal162 packet162", 18),
        ["buffer162 queue162", "worker162", "kernel162", "signal162", "packet162"],
    ),
    (
        ("buffer162 queue162 worker162 kernel162 signal162 packet162", 28),
        ["buffer162 queue162 worker162", "kernel162 signal162", "packet162"],
    ),
    (
        ("queue162 worker162 kernel162 signal162 packet162 router162", 6),
        ["queue162", "worker162", "kernel162", "signal162", "packet162", "router162"],
    ),
    (
        ("queue162 worker162 kernel162 signal162 packet162 router162", 10),
        ["queue162", "worker162", "kernel162", "signal162", "packet162", "router162"],
    ),
    (
        ("queue162 worker162 kernel162 signal162 packet162 router162", 18),
        ["queue162 worker162", "kernel162", "signal162", "packet162", "router162"],
    ),
    (
        ("queue162 worker162 kernel162 signal162 packet162 router162", 28),
        ["queue162 worker162 kernel162", "signal162 packet162", "router162"],
    ),
    (
        ("worker162 kernel162 signal162 packet162 router162 cluster162", 6),
        ["worker162", "kernel162", "signal162", "packet162", "router162", "cluster162"],
    ),
    (
        ("worker162 kernel162 signal162 packet162 router162 cluster162", 10),
        ["worker162", "kernel162", "signal162", "packet162", "router162", "cluster162"],
    ),
    (
        ("worker162 kernel162 signal162 packet162 router162 cluster162", 18),
        ["worker162", "kernel162", "signal162", "packet162", "router162", "cluster162"],
    ),
    (
        ("worker162 kernel162 signal162 packet162 router162 cluster162", 28),
        ["worker162 kernel162", "signal162 packet162", "router162 cluster162"],
    ),
    (
        ("kernel162 signal162 packet162 router162 cluster162 mirror162", 6),
        ["kernel162", "signal162", "packet162", "router162", "cluster162", "mirror162"],
    ),
    (
        ("kernel162 signal162 packet162 router162 cluster162 mirror162", 10),
        ["kernel162", "signal162", "packet162", "router162", "cluster162", "mirror162"],
    ),
    (
        ("kernel162 signal162 packet162 router162 cluster162 mirror162", 18),
        ["kernel162", "signal162", "packet162", "router162", "cluster162", "mirror162"],
    ),
    (
        ("kernel162 signal162 packet162 router162 cluster162 mirror162", 28),
        ["kernel162 signal162", "packet162 router162", "cluster162 mirror162"],
    ),
    (
        ("signal162 packet162 router162 cluster162 mirror162 filter162", 6),
        ["signal162", "packet162", "router162", "cluster162", "mirror162", "filter162"],
    ),
    (
        ("signal162 packet162 router162 cluster162 mirror162 filter162", 10),
        ["signal162", "packet162", "router162", "cluster162", "mirror162", "filter162"],
    ),
    (
        ("signal162 packet162 router162 cluster162 mirror162 filter162", 18),
        ["signal162", "packet162", "router162", "cluster162", "mirror162", "filter162"],
    ),
    (
        ("signal162 packet162 router162 cluster162 mirror162 filter162", 28),
        ["signal162 packet162", "router162 cluster162", "mirror162 filter162"],
    ),
    (
        ("packet162 router162 cluster162 mirror162 filter162 ranking162", 6),
        ["packet162", "router162", "cluster162", "mirror162", "filter162", "ranking162"],
    ),
    (
        ("packet162 router162 cluster162 mirror162 filter162 ranking162", 10),
        ["packet162", "router162", "cluster162", "mirror162", "filter162", "ranking162"],
    ),
    (
        ("packet162 router162 cluster162 mirror162 filter162 ranking162", 18),
        ["packet162", "router162", "cluster162", "mirror162", "filter162", "ranking162"],
    ),
    (
        ("packet162 router162 cluster162 mirror162 filter162 ranking162", 28),
        ["packet162 router162", "cluster162 mirror162", "filter162 ranking162"],
    ),
    (
        ("router162 cluster162 mirror162 filter162 ranking162 encoding162", 6),
        ["router162", "cluster162", "mirror162", "filter162", "ranking162", "encoding162"],
    ),
    (
        ("router162 cluster162 mirror162 filter162 ranking162 encoding162", 10),
        ["router162", "cluster162", "mirror162", "filter162", "ranking162", "encoding162"],
    ),
    (
        ("router162 cluster162 mirror162 filter162 ranking162 encoding162", 18),
        ["router162", "cluster162", "mirror162", "filter162", "ranking162", "encoding162"],
    ),
    (
        ("router162 cluster162 mirror162 filter162 ranking162 encoding162", 28),
        ["router162 cluster162", "mirror162 filter162", "ranking162 encoding162"],
    ),
    (
        ("cluster162 mirror162 filter162 ranking162 encoding162 mapping162", 6),
        ["cluster162", "mirror162", "filter162", "ranking162", "encoding162", "mapping162"],
    ),
    (
        ("cluster162 mirror162 filter162 ranking162 encoding162 mapping162", 10),
        ["cluster162", "mirror162", "filter162", "ranking162", "encoding162", "mapping162"],
    ),
    (
        ("cluster162 mirror162 filter162 ranking162 encoding162 mapping162", 18),
        ["cluster162", "mirror162", "filter162", "ranking162", "encoding162", "mapping162"],
    ),
    (
        ("cluster162 mirror162 filter162 ranking162 encoding162 mapping162", 28),
        ["cluster162 mirror162", "filter162 ranking162", "encoding162 mapping162"],
    ),
    (
        ("mirror162 filter162 ranking162 encoding162 mapping162 record162", 6),
        ["mirror162", "filter162", "ranking162", "encoding162", "mapping162", "record162"],
    ),
    (
        ("mirror162 filter162 ranking162 encoding162 mapping162 record162", 10),
        ["mirror162", "filter162", "ranking162", "encoding162", "mapping162", "record162"],
    ),
    (
        ("mirror162 filter162 ranking162 encoding162 mapping162 record162", 18),
        ["mirror162", "filter162", "ranking162", "encoding162", "mapping162", "record162"],
    ),
    (
        ("mirror162 filter162 ranking162 encoding162 mapping162 record162", 28),
        ["mirror162 filter162", "ranking162 encoding162", "mapping162 record162"],
    ),
    (
        ("filter162 ranking162 encoding162 mapping162 record162 candle162", 6),
        ["filter162", "ranking162", "encoding162", "mapping162", "record162", "candle162"],
    ),
    (
        ("filter162 ranking162 encoding162 mapping162 record162 candle162", 10),
        ["filter162", "ranking162", "encoding162", "mapping162", "record162", "candle162"],
    ),
    (
        ("filter162 ranking162 encoding162 mapping162 record162 candle162", 18),
        ["filter162", "ranking162", "encoding162", "mapping162", "record162", "candle162"],
    ),
    (
        ("filter162 ranking162 encoding162 mapping162 record162 candle162", 28),
        ["filter162 ranking162", "encoding162 mapping162", "record162 candle162"],
    ),
    (
        ("ranking162 encoding162 mapping162 record162 candle162 thread162", 6),
        ["ranking162", "encoding162", "mapping162", "record162", "candle162", "thread162"],
    ),
    (
        ("ranking162 encoding162 mapping162 record162 candle162 thread162", 10),
        ["ranking162", "encoding162", "mapping162", "record162", "candle162", "thread162"],
    ),
    (
        ("ranking162 encoding162 mapping162 record162 candle162 thread162", 18),
        ["ranking162", "encoding162", "mapping162", "record162", "candle162", "thread162"],
    ),
    (
        ("ranking162 encoding162 mapping162 record162 candle162 thread162", 28),
        ["ranking162 encoding162", "mapping162 record162", "candle162 thread162"],
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
