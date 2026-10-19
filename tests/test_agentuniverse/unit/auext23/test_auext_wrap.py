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
        ("round 23: the quick brown fox jumps over the lazy dog", 4),
        ["round", "23:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 23: the quick brown fox jumps over the lazy dog", 8),
        ["round", "23: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 23: the quick brown fox jumps over the lazy dog", 12),
        ["round 23:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 23: the quick brown fox jumps over the lazy dog", 16),
        ["round 23: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 23: the quick brown fox jumps over the lazy dog", 24),
        ["round 23: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 23: the quick brown fox jumps over the lazy dog", 32),
        ["round 23: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 23: agentuniverse is a framework for multi agents", 4),
        ["round", "23:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 23: agentuniverse is a framework for multi agents", 8),
        ["round", "23:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 23: agentuniverse is a framework for multi agents", 12),
        ["round 23:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 23: agentuniverse is a framework for multi agents", 16),
        ["round 23:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 23: agentuniverse is a framework for multi agents", 24),
        ["round 23: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 23: agentuniverse is a framework for multi agents", 32),
        ["round 23: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 23: knowledge stored as vectors enables retrieval", 4),
        ["round", "23:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 23: knowledge stored as vectors enables retrieval", 8),
        ["round", "23:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 23: knowledge stored as vectors enables retrieval", 12),
        ["round 23:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 23: knowledge stored as vectors enables retrieval", 16),
        ["round 23:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 23: knowledge stored as vectors enables retrieval", 24),
        ["round 23: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 23: knowledge stored as vectors enables retrieval", 32),
        ["round 23: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 23: the processor reads the record then stops", 4),
        ["round", "23:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 23: the processor reads the record then stops", 8),
        ["round", "23: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 23: the processor reads the record then stops", 12),
        ["round 23:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 23: the processor reads the record then stops", 16),
        ["round 23: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 23: the processor reads the record then stops", 24),
        ["round 23: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 23: the processor reads the record then stops", 32),
        ["round 23: the processor reads", "the record then stops"],
    ),
    (
        ("round 23: a worker pulls the next task from the queue", 4),
        ["round", "23:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 23: a worker pulls the next task from the queue", 8),
        ["round", "23: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 23: a worker pulls the next task from the queue", 12),
        ["round 23: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 23: a worker pulls the next task from the queue", 16),
        ["round 23: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 23: a worker pulls the next task from the queue", 24),
        ["round 23: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 23: a worker pulls the next task from the queue", 32),
        ["round 23: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 23: signals travel through the network layer", 4),
        ["round", "23:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 23: signals travel through the network layer", 8),
        ["round", "23:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 23: signals travel through the network layer", 12),
        ["round 23:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 23: signals travel through the network layer", 16),
        ["round 23:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 23: signals travel through the network layer", 24),
        ["round 23: signals travel", "through the network", "layer"],
    ),
    (
        ("round 23: signals travel through the network layer", 32),
        ["round 23: signals travel through", "the network layer"],
    ),
    (
        ("round 23: the gateway routes each request by policy", 4),
        ["round", "23:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 23: the gateway routes each request by policy", 8),
        ["round", "23: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 23: the gateway routes each request by policy", 12),
        ["round 23:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 23: the gateway routes each request by policy", 16),
        ["round 23: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 23: the gateway routes each request by policy", 24),
        ["round 23: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 23: the gateway routes each request by policy", 32),
        ["round 23: the gateway routes", "each request by policy"],
    ),
    (
        ("round 23: memory grows until the buffer is full", 4),
        ["round", "23:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 23: memory grows until the buffer is full", 8),
        ["round", "23:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 23: memory grows until the buffer is full", 12),
        ["round 23:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 23: memory grows until the buffer is full", 16),
        ["round 23: memory", "grows until the", "buffer is full"],
    ),
    (("round 23: memory grows until the buffer is full", 24), ["round 23: memory grows", "until the buffer is full"]),
    (("round 23: memory grows until the buffer is full", 32), ["round 23: memory grows until the", "buffer is full"]),
    (
        ("round 23: the cluster mirrors every packet twice", 4),
        ["round", "23:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 23: the cluster mirrors every packet twice", 8),
        ["round", "23: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 23: the cluster mirrors every packet twice", 12),
        ["round 23:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 23: the cluster mirrors every packet twice", 16),
        ["round 23: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 23: the cluster mirrors every packet twice", 24),
        ["round 23: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 23: the cluster mirrors every packet twice", 32), ["round 23: the cluster mirrors", "every packet twice"]),
    (
        ("round 23: ranking uses tokens learned from the corpus", 4),
        ["round", "23:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 23: ranking uses tokens learned from the corpus", 8),
        ["round", "23:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 23: ranking uses tokens learned from the corpus", 12),
        ["round 23:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 23: ranking uses tokens learned from the corpus", 16),
        ["round 23:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 23: ranking uses tokens learned from the corpus", 24),
        ["round 23: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 23: ranking uses tokens learned from the corpus", 32),
        ["round 23: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 23: a long session ends when the candle dies", 4),
        ["round", "23:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 23: a long session ends when the candle dies", 8),
        ["round", "23: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 23: a long session ends when the candle dies", 12),
        ["round 23: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 23: a long session ends when the candle dies", 16),
        ["round 23: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 23: a long session ends when the candle dies", 24),
        ["round 23: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 23: a long session ends when the candle dies", 32),
        ["round 23: a long session ends", "when the candle dies"],
    ),
    (
        ("round 23: encode the prompt then map the result", 4),
        ["round", "23:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 23: encode the prompt then map the result", 8),
        ["round", "23:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 23: encode the prompt then map the result", 12),
        ["round 23:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 23: encode the prompt then map the result", 16),
        ["round 23: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 23: encode the prompt then map the result", 24),
        ["round 23: encode the", "prompt then map the", "result"],
    ),
    (("round 23: encode the prompt then map the result", 32), ["round 23: encode the prompt then", "map the result"]),
    (
        ("round 23: the kernel wakes the worker at dawn", 4),
        ["round", "23:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 23: the kernel wakes the worker at dawn", 8),
        ["round", "23: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 23: the kernel wakes the worker at dawn", 12),
        ["round 23:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 23: the kernel wakes the worker at dawn", 16), ["round 23: the", "kernel wakes the", "worker at dawn"]),
    (("round 23: the kernel wakes the worker at dawn", 24), ["round 23: the kernel", "wakes the worker at dawn"]),
    (("round 23: the kernel wakes the worker at dawn", 32), ["round 23: the kernel wakes the", "worker at dawn"]),
    (
        ("round 23: service latency drops after the patch", 4),
        ["round", "23:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 23: service latency drops after the patch", 8),
        ["round", "23:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 23: service latency drops after the patch", 12),
        ["round 23:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 23: service latency drops after the patch", 16),
        ["round 23:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 23: service latency drops after the patch", 24),
        ["round 23: service", "latency drops after the", "patch"],
    ),
    (("round 23: service latency drops after the patch", 32), ["round 23: service latency drops", "after the patch"]),
    (
        ("round 23: the library caches every vector it sees", 4),
        ["round", "23:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 23: the library caches every vector it sees", 8),
        ["round", "23: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 23: the library caches every vector it sees", 12),
        ["round 23:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 23: the library caches every vector it sees", 16),
        ["round 23: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 23: the library caches every vector it sees", 24),
        ["round 23: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 23: the library caches every vector it sees", 32),
        ["round 23: the library caches", "every vector it sees"],
    ),
    (
        ("round 23: agents argue then the debate resolves", 4),
        ["round", "23:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 23: agents argue then the debate resolves", 8),
        ["round", "23:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 23: agents argue then the debate resolves", 12),
        ["round 23:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 23: agents argue then the debate resolves", 16),
        ["round 23: agents", "argue then the", "debate resolves"],
    ),
    (("round 23: agents argue then the debate resolves", 24), ["round 23: agents argue", "then the debate resolves"]),
    (("round 23: agents argue then the debate resolves", 32), ["round 23: agents argue then the", "debate resolves"]),
    (
        ("round 23: the filter keeps only strong matches", 4),
        ["round", "23:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 23: the filter keeps only strong matches", 8),
        ["round", "23: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 23: the filter keeps only strong matches", 12),
        ["round 23:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 23: the filter keeps only strong matches", 16),
        ["round 23: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 23: the filter keeps only strong matches", 24), ["round 23: the filter", "keeps only strong", "matches"]),
    (("round 23: the filter keeps only strong matches", 32), ["round 23: the filter keeps only", "strong matches"]),
    (
        ("round 23: the model answers with a short reply", 4),
        ["round", "23:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 23: the model answers with a short reply", 8),
        ["round", "23: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 23: the model answers with a short reply", 12),
        ["round 23:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 23: the model answers with a short reply", 16),
        ["round 23: the", "model answers", "with a short", "reply"],
    ),
    (("round 23: the model answers with a short reply", 24), ["round 23: the model", "answers with a short", "reply"]),
    (("round 23: the model answers with a short reply", 32), ["round 23: the model answers with", "a short reply"]),
    (
        ("round 23: the recorder stores the reasoning trace", 4),
        ["round", "23:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 23: the recorder stores the reasoning trace", 8),
        ["round", "23: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 23: the recorder stores the reasoning trace", 12),
        ["round 23:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 23: the recorder stores the reasoning trace", 16),
        ["round 23: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 23: the recorder stores the reasoning trace", 24),
        ["round 23: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 23: the recorder stores the reasoning trace", 32),
        ["round 23: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 23: the angel watches the processor run", 4),
        ["round", "23:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 23: the angel watches the processor run", 8),
        ["round", "23: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 23: the angel watches the processor run", 12),
        ["round 23:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 23: the angel watches the processor run", 16), ["round 23: the", "angel watches", "the processor", "run"]),
    (("round 23: the angel watches the processor run", 24), ["round 23: the angel", "watches the processor", "run"]),
    (("round 23: the angel watches the processor run", 32), ["round 23: the angel watches the", "processor run"]),
    (
        ("round 23: angle of the vector decides the match", 4),
        ["round", "23:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 23: angle of the vector decides the match", 8),
        ["round", "23:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 23: angle of the vector decides the match", 12),
        ["round 23:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 23: angle of the vector decides the match", 16),
        ["round 23: angle", "of the vector", "decides the", "match"],
    ),
    (("round 23: angle of the vector decides the match", 24), ["round 23: angle of the", "vector decides the match"]),
    (("round 23: angle of the vector decides the match", 32), ["round 23: angle of the vector", "decides the match"]),
    (
        ("round 23: the candle burns twice as long at night", 4),
        ["round", "23:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 23: the candle burns twice as long at night", 8),
        ["round", "23: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 23: the candle burns twice as long at night", 12),
        ["round 23:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 23: the candle burns twice as long at night", 16),
        ["round 23: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 23: the candle burns twice as long at night", 24),
        ["round 23: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 23: the candle burns twice as long at night", 32),
        ["round 23: the candle burns twice", "as long at night"],
    ),
    (
        ("round 23: a mirror of the universe in one line", 4),
        ["round", "23:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 23: a mirror of the universe in one line", 8),
        ["round", "23: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 23: a mirror of the universe in one line", 12),
        ["round 23: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 23: a mirror of the universe in one line", 16),
        ["round 23: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 23: a mirror of the universe in one line", 24), ["round 23: a mirror of", "the universe in one line"]),
    (("round 23: a mirror of the universe in one line", 32), ["round 23: a mirror of the", "universe in one line"]),
    (
        ("round 23: the queue drains before the storm", 4),
        ["round", "23:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 23: the queue drains before the storm", 8),
        ["round", "23: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 23: the queue drains before the storm", 12), ["round 23:", "the queue", "drains", "before the", "storm"]),
    (("round 23: the queue drains before the storm", 16), ["round 23: the", "queue drains", "before the storm"]),
    (("round 23: the queue drains before the storm", 24), ["round 23: the queue", "drains before the storm"]),
    (("round 23: the queue drains before the storm", 32), ["round 23: the queue drains", "before the storm"]),
    (
        ("kitten23 sitting23 agent23 angle23 universe23 memory23", 6),
        ["kitten23", "sitting23", "agent23", "angle23", "universe23", "memory23"],
    ),
    (
        ("kitten23 sitting23 agent23 angle23 universe23 memory23", 10),
        ["kitten23", "sitting23", "agent23", "angle23", "universe23", "memory23"],
    ),
    (
        ("kitten23 sitting23 agent23 angle23 universe23 memory23", 18),
        ["kitten23 sitting23", "agent23 angle23", "universe23", "memory23"],
    ),
    (
        ("kitten23 sitting23 agent23 angle23 universe23 memory23", 28),
        ["kitten23 sitting23 agent23", "angle23 universe23 memory23"],
    ),
    (
        ("sitting23 agent23 angle23 universe23 memory23 stream23", 6),
        ["sitting23", "agent23", "angle23", "universe23", "memory23", "stream23"],
    ),
    (
        ("sitting23 agent23 angle23 universe23 memory23 stream23", 10),
        ["sitting23", "agent23", "angle23", "universe23", "memory23", "stream23"],
    ),
    (
        ("sitting23 agent23 angle23 universe23 memory23 stream23", 18),
        ["sitting23 agent23", "angle23 universe23", "memory23 stream23"],
    ),
    (
        ("sitting23 agent23 angle23 universe23 memory23 stream23", 28),
        ["sitting23 agent23 angle23", "universe23 memory23 stream23"],
    ),
    (
        ("agent23 angle23 universe23 memory23 stream23 context23", 6),
        ["agent23", "angle23", "universe23", "memory23", "stream23", "context23"],
    ),
    (
        ("agent23 angle23 universe23 memory23 stream23 context23", 10),
        ["agent23", "angle23", "universe23", "memory23", "stream23", "context23"],
    ),
    (
        ("agent23 angle23 universe23 memory23 stream23 context23", 18),
        ["agent23 angle23", "universe23", "memory23 stream23", "context23"],
    ),
    (
        ("agent23 angle23 universe23 memory23 stream23 context23", 28),
        ["agent23 angle23 universe23", "memory23 stream23 context23"],
    ),
    (
        ("angle23 universe23 memory23 stream23 context23 knowledge23", 6),
        ["angle23", "universe23", "memory23", "stream23", "context23", "knowledge23"],
    ),
    (
        ("angle23 universe23 memory23 stream23 context23 knowledge23", 10),
        ["angle23", "universe23", "memory23", "stream23", "context23", "knowledge23"],
    ),
    (
        ("angle23 universe23 memory23 stream23 context23 knowledge23", 18),
        ["angle23 universe23", "memory23 stream23", "context23", "knowledge23"],
    ),
    (
        ("angle23 universe23 memory23 stream23 context23 knowledge23", 28),
        ["angle23 universe23 memory23", "stream23 context23", "knowledge23"],
    ),
    (
        ("universe23 memory23 stream23 context23 knowledge23 vector23", 6),
        ["universe23", "memory23", "stream23", "context23", "knowledge23", "vector23"],
    ),
    (
        ("universe23 memory23 stream23 context23 knowledge23 vector23", 10),
        ["universe23", "memory23", "stream23", "context23", "knowledge23", "vector23"],
    ),
    (
        ("universe23 memory23 stream23 context23 knowledge23 vector23", 18),
        ["universe23", "memory23 stream23", "context23", "knowledge23", "vector23"],
    ),
    (
        ("universe23 memory23 stream23 context23 knowledge23 vector23", 28),
        ["universe23 memory23 stream23", "context23 knowledge23", "vector23"],
    ),
    (
        ("memory23 stream23 context23 knowledge23 vector23 processor23", 6),
        ["memory23", "stream23", "context23", "knowledge23", "vector23", "processor23"],
    ),
    (
        ("memory23 stream23 context23 knowledge23 vector23 processor23", 10),
        ["memory23", "stream23", "context23", "knowledge23", "vector23", "processor23"],
    ),
    (
        ("memory23 stream23 context23 knowledge23 vector23 processor23", 18),
        ["memory23 stream23", "context23", "knowledge23", "vector23", "processor23"],
    ),
    (
        ("memory23 stream23 context23 knowledge23 vector23 processor23", 28),
        ["memory23 stream23 context23", "knowledge23 vector23", "processor23"],
    ),
    (
        ("stream23 context23 knowledge23 vector23 processor23 reasoning23", 6),
        ["stream23", "context23", "knowledge23", "vector23", "processor23", "reasoning23"],
    ),
    (
        ("stream23 context23 knowledge23 vector23 processor23 reasoning23", 10),
        ["stream23", "context23", "knowledge23", "vector23", "processor23", "reasoning23"],
    ),
    (
        ("stream23 context23 knowledge23 vector23 processor23 reasoning23", 18),
        ["stream23 context23", "knowledge23", "vector23", "processor23", "reasoning23"],
    ),
    (
        ("stream23 context23 knowledge23 vector23 processor23 reasoning23", 28),
        ["stream23 context23", "knowledge23 vector23", "processor23 reasoning23"],
    ),
    (
        ("context23 knowledge23 vector23 processor23 reasoning23 machine23", 6),
        ["context23", "knowledge23", "vector23", "processor23", "reasoning23", "machine23"],
    ),
    (
        ("context23 knowledge23 vector23 processor23 reasoning23 machine23", 10),
        ["context23", "knowledge23", "vector23", "processor23", "reasoning23", "machine23"],
    ),
    (
        ("context23 knowledge23 vector23 processor23 reasoning23 machine23", 18),
        ["context23", "knowledge23", "vector23", "processor23", "reasoning23", "machine23"],
    ),
    (
        ("context23 knowledge23 vector23 processor23 reasoning23 machine23", 28),
        ["context23 knowledge23", "vector23 processor23", "reasoning23 machine23"],
    ),
    (
        ("knowledge23 vector23 processor23 reasoning23 machine23 learning23", 6),
        ["knowledge23", "vector23", "processor23", "reasoning23", "machine23", "learning23"],
    ),
    (
        ("knowledge23 vector23 processor23 reasoning23 machine23 learning23", 10),
        ["knowledge23", "vector23", "processor23", "reasoning23", "machine23", "learning23"],
    ),
    (
        ("knowledge23 vector23 processor23 reasoning23 machine23 learning23", 18),
        ["knowledge23", "vector23", "processor23", "reasoning23", "machine23", "learning23"],
    ),
    (
        ("knowledge23 vector23 processor23 reasoning23 machine23 learning23", 28),
        ["knowledge23 vector23", "processor23 reasoning23", "machine23 learning23"],
    ),
    (
        ("vector23 processor23 reasoning23 machine23 learning23 model23", 6),
        ["vector23", "processor23", "reasoning23", "machine23", "learning23", "model23"],
    ),
    (
        ("vector23 processor23 reasoning23 machine23 learning23 model23", 10),
        ["vector23", "processor23", "reasoning23", "machine23", "learning23", "model23"],
    ),
    (
        ("vector23 processor23 reasoning23 machine23 learning23 model23", 18),
        ["vector23", "processor23", "reasoning23", "machine23", "learning23 model23"],
    ),
    (
        ("vector23 processor23 reasoning23 machine23 learning23 model23", 28),
        ["vector23 processor23", "reasoning23 machine23", "learning23 model23"],
    ),
    (
        ("processor23 reasoning23 machine23 learning23 model23 token23", 6),
        ["processor23", "reasoning23", "machine23", "learning23", "model23", "token23"],
    ),
    (
        ("processor23 reasoning23 machine23 learning23 model23 token23", 10),
        ["processor23", "reasoning23", "machine23", "learning23", "model23", "token23"],
    ),
    (
        ("processor23 reasoning23 machine23 learning23 model23 token23", 18),
        ["processor23", "reasoning23", "machine23", "learning23 model23", "token23"],
    ),
    (
        ("processor23 reasoning23 machine23 learning23 model23 token23", 28),
        ["processor23 reasoning23", "machine23 learning23 model23", "token23"],
    ),
    (
        ("reasoning23 machine23 learning23 model23 token23 prompt23", 6),
        ["reasoning23", "machine23", "learning23", "model23", "token23", "prompt23"],
    ),
    (
        ("reasoning23 machine23 learning23 model23 token23 prompt23", 10),
        ["reasoning23", "machine23", "learning23", "model23", "token23", "prompt23"],
    ),
    (
        ("reasoning23 machine23 learning23 model23 token23 prompt23", 18),
        ["reasoning23", "machine23", "learning23 model23", "token23 prompt23"],
    ),
    (
        ("reasoning23 machine23 learning23 model23 token23 prompt23", 28),
        ["reasoning23 machine23", "learning23 model23 token23", "prompt23"],
    ),
    (
        ("machine23 learning23 model23 token23 prompt23 session23", 6),
        ["machine23", "learning23", "model23", "token23", "prompt23", "session23"],
    ),
    (
        ("machine23 learning23 model23 token23 prompt23 session23", 10),
        ["machine23", "learning23", "model23", "token23", "prompt23", "session23"],
    ),
    (
        ("machine23 learning23 model23 token23 prompt23 session23", 18),
        ["machine23", "learning23 model23", "token23 prompt23", "session23"],
    ),
    (
        ("machine23 learning23 model23 token23 prompt23 session23", 28),
        ["machine23 learning23 model23", "token23 prompt23 session23"],
    ),
    (
        ("learning23 model23 token23 prompt23 session23 library23", 6),
        ["learning23", "model23", "token23", "prompt23", "session23", "library23"],
    ),
    (
        ("learning23 model23 token23 prompt23 session23 library23", 10),
        ["learning23", "model23", "token23", "prompt23", "session23", "library23"],
    ),
    (
        ("learning23 model23 token23 prompt23 session23 library23", 18),
        ["learning23 model23", "token23 prompt23", "session23", "library23"],
    ),
    (
        ("learning23 model23 token23 prompt23 session23 library23", 28),
        ["learning23 model23 token23", "prompt23 session23 library23"],
    ),
    (
        ("model23 token23 prompt23 session23 library23 service23", 6),
        ["model23", "token23", "prompt23", "session23", "library23", "service23"],
    ),
    (
        ("model23 token23 prompt23 session23 library23 service23", 10),
        ["model23", "token23", "prompt23", "session23", "library23", "service23"],
    ),
    (
        ("model23 token23 prompt23 session23 library23 service23", 18),
        ["model23 token23", "prompt23 session23", "library23", "service23"],
    ),
    (
        ("model23 token23 prompt23 session23 library23 service23", 28),
        ["model23 token23 prompt23", "session23 library23", "service23"],
    ),
    (
        ("token23 prompt23 session23 library23 service23 gateway23", 6),
        ["token23", "prompt23", "session23", "library23", "service23", "gateway23"],
    ),
    (
        ("token23 prompt23 session23 library23 service23 gateway23", 10),
        ["token23", "prompt23", "session23", "library23", "service23", "gateway23"],
    ),
    (
        ("token23 prompt23 session23 library23 service23 gateway23", 18),
        ["token23 prompt23", "session23", "library23", "service23", "gateway23"],
    ),
    (
        ("token23 prompt23 session23 library23 service23 gateway23", 28),
        ["token23 prompt23 session23", "library23 service23", "gateway23"],
    ),
    (
        ("prompt23 session23 library23 service23 gateway23 storage23", 6),
        ["prompt23", "session23", "library23", "service23", "gateway23", "storage23"],
    ),
    (
        ("prompt23 session23 library23 service23 gateway23 storage23", 10),
        ["prompt23", "session23", "library23", "service23", "gateway23", "storage23"],
    ),
    (
        ("prompt23 session23 library23 service23 gateway23 storage23", 18),
        ["prompt23 session23", "library23", "service23", "gateway23", "storage23"],
    ),
    (
        ("prompt23 session23 library23 service23 gateway23 storage23", 28),
        ["prompt23 session23 library23", "service23 gateway23", "storage23"],
    ),
    (
        ("session23 library23 service23 gateway23 storage23 network23", 6),
        ["session23", "library23", "service23", "gateway23", "storage23", "network23"],
    ),
    (
        ("session23 library23 service23 gateway23 storage23 network23", 10),
        ["session23", "library23", "service23", "gateway23", "storage23", "network23"],
    ),
    (
        ("session23 library23 service23 gateway23 storage23 network23", 18),
        ["session23", "library23", "service23", "gateway23", "storage23", "network23"],
    ),
    (
        ("session23 library23 service23 gateway23 storage23 network23", 28),
        ["session23 library23", "service23 gateway23", "storage23 network23"],
    ),
    (
        ("library23 service23 gateway23 storage23 network23 latency23", 6),
        ["library23", "service23", "gateway23", "storage23", "network23", "latency23"],
    ),
    (
        ("library23 service23 gateway23 storage23 network23 latency23", 10),
        ["library23", "service23", "gateway23", "storage23", "network23", "latency23"],
    ),
    (
        ("library23 service23 gateway23 storage23 network23 latency23", 18),
        ["library23", "service23", "gateway23", "storage23", "network23", "latency23"],
    ),
    (
        ("library23 service23 gateway23 storage23 network23 latency23", 28),
        ["library23 service23", "gateway23 storage23", "network23 latency23"],
    ),
    (
        ("service23 gateway23 storage23 network23 latency23 buffer23", 6),
        ["service23", "gateway23", "storage23", "network23", "latency23", "buffer23"],
    ),
    (
        ("service23 gateway23 storage23 network23 latency23 buffer23", 10),
        ["service23", "gateway23", "storage23", "network23", "latency23", "buffer23"],
    ),
    (
        ("service23 gateway23 storage23 network23 latency23 buffer23", 18),
        ["service23", "gateway23", "storage23", "network23", "latency23 buffer23"],
    ),
    (
        ("service23 gateway23 storage23 network23 latency23 buffer23", 28),
        ["service23 gateway23", "storage23 network23", "latency23 buffer23"],
    ),
    (
        ("gateway23 storage23 network23 latency23 buffer23 queue23", 6),
        ["gateway23", "storage23", "network23", "latency23", "buffer23", "queue23"],
    ),
    (
        ("gateway23 storage23 network23 latency23 buffer23 queue23", 10),
        ["gateway23", "storage23", "network23", "latency23", "buffer23", "queue23"],
    ),
    (
        ("gateway23 storage23 network23 latency23 buffer23 queue23", 18),
        ["gateway23", "storage23", "network23", "latency23 buffer23", "queue23"],
    ),
    (
        ("gateway23 storage23 network23 latency23 buffer23 queue23", 28),
        ["gateway23 storage23", "network23 latency23 buffer23", "queue23"],
    ),
    (
        ("storage23 network23 latency23 buffer23 queue23 worker23", 6),
        ["storage23", "network23", "latency23", "buffer23", "queue23", "worker23"],
    ),
    (
        ("storage23 network23 latency23 buffer23 queue23 worker23", 10),
        ["storage23", "network23", "latency23", "buffer23", "queue23", "worker23"],
    ),
    (
        ("storage23 network23 latency23 buffer23 queue23 worker23", 18),
        ["storage23", "network23", "latency23 buffer23", "queue23 worker23"],
    ),
    (
        ("storage23 network23 latency23 buffer23 queue23 worker23", 28),
        ["storage23 network23", "latency23 buffer23 queue23", "worker23"],
    ),
    (
        ("network23 latency23 buffer23 queue23 worker23 kernel23", 6),
        ["network23", "latency23", "buffer23", "queue23", "worker23", "kernel23"],
    ),
    (
        ("network23 latency23 buffer23 queue23 worker23 kernel23", 10),
        ["network23", "latency23", "buffer23", "queue23", "worker23", "kernel23"],
    ),
    (
        ("network23 latency23 buffer23 queue23 worker23 kernel23", 18),
        ["network23", "latency23 buffer23", "queue23 worker23", "kernel23"],
    ),
    (
        ("network23 latency23 buffer23 queue23 worker23 kernel23", 28),
        ["network23 latency23 buffer23", "queue23 worker23 kernel23"],
    ),
    (
        ("latency23 buffer23 queue23 worker23 kernel23 signal23", 6),
        ["latency23", "buffer23", "queue23", "worker23", "kernel23", "signal23"],
    ),
    (
        ("latency23 buffer23 queue23 worker23 kernel23 signal23", 10),
        ["latency23", "buffer23", "queue23", "worker23", "kernel23", "signal23"],
    ),
    (
        ("latency23 buffer23 queue23 worker23 kernel23 signal23", 18),
        ["latency23 buffer23", "queue23 worker23", "kernel23 signal23"],
    ),
    (
        ("latency23 buffer23 queue23 worker23 kernel23 signal23", 28),
        ["latency23 buffer23 queue23", "worker23 kernel23 signal23"],
    ),
    (
        ("buffer23 queue23 worker23 kernel23 signal23 packet23", 6),
        ["buffer23", "queue23", "worker23", "kernel23", "signal23", "packet23"],
    ),
    (
        ("buffer23 queue23 worker23 kernel23 signal23 packet23", 10),
        ["buffer23", "queue23", "worker23", "kernel23", "signal23", "packet23"],
    ),
    (
        ("buffer23 queue23 worker23 kernel23 signal23 packet23", 18),
        ["buffer23 queue23", "worker23 kernel23", "signal23 packet23"],
    ),
    (
        ("buffer23 queue23 worker23 kernel23 signal23 packet23", 28),
        ["buffer23 queue23 worker23", "kernel23 signal23 packet23"],
    ),
    (
        ("queue23 worker23 kernel23 signal23 packet23 router23", 6),
        ["queue23", "worker23", "kernel23", "signal23", "packet23", "router23"],
    ),
    (
        ("queue23 worker23 kernel23 signal23 packet23 router23", 10),
        ["queue23", "worker23", "kernel23", "signal23", "packet23", "router23"],
    ),
    (
        ("queue23 worker23 kernel23 signal23 packet23 router23", 18),
        ["queue23 worker23", "kernel23 signal23", "packet23 router23"],
    ),
    (
        ("queue23 worker23 kernel23 signal23 packet23 router23", 28),
        ["queue23 worker23 kernel23", "signal23 packet23 router23"],
    ),
    (
        ("worker23 kernel23 signal23 packet23 router23 cluster23", 6),
        ["worker23", "kernel23", "signal23", "packet23", "router23", "cluster23"],
    ),
    (
        ("worker23 kernel23 signal23 packet23 router23 cluster23", 10),
        ["worker23", "kernel23", "signal23", "packet23", "router23", "cluster23"],
    ),
    (
        ("worker23 kernel23 signal23 packet23 router23 cluster23", 18),
        ["worker23 kernel23", "signal23 packet23", "router23 cluster23"],
    ),
    (
        ("worker23 kernel23 signal23 packet23 router23 cluster23", 28),
        ["worker23 kernel23 signal23", "packet23 router23 cluster23"],
    ),
    (
        ("kernel23 signal23 packet23 router23 cluster23 mirror23", 6),
        ["kernel23", "signal23", "packet23", "router23", "cluster23", "mirror23"],
    ),
    (
        ("kernel23 signal23 packet23 router23 cluster23 mirror23", 10),
        ["kernel23", "signal23", "packet23", "router23", "cluster23", "mirror23"],
    ),
    (
        ("kernel23 signal23 packet23 router23 cluster23 mirror23", 18),
        ["kernel23 signal23", "packet23 router23", "cluster23 mirror23"],
    ),
    (
        ("kernel23 signal23 packet23 router23 cluster23 mirror23", 28),
        ["kernel23 signal23 packet23", "router23 cluster23 mirror23"],
    ),
    (
        ("signal23 packet23 router23 cluster23 mirror23 filter23", 6),
        ["signal23", "packet23", "router23", "cluster23", "mirror23", "filter23"],
    ),
    (
        ("signal23 packet23 router23 cluster23 mirror23 filter23", 10),
        ["signal23", "packet23", "router23", "cluster23", "mirror23", "filter23"],
    ),
    (
        ("signal23 packet23 router23 cluster23 mirror23 filter23", 18),
        ["signal23 packet23", "router23 cluster23", "mirror23 filter23"],
    ),
    (
        ("signal23 packet23 router23 cluster23 mirror23 filter23", 28),
        ["signal23 packet23 router23", "cluster23 mirror23 filter23"],
    ),
    (
        ("packet23 router23 cluster23 mirror23 filter23 ranking23", 6),
        ["packet23", "router23", "cluster23", "mirror23", "filter23", "ranking23"],
    ),
    (
        ("packet23 router23 cluster23 mirror23 filter23 ranking23", 10),
        ["packet23", "router23", "cluster23", "mirror23", "filter23", "ranking23"],
    ),
    (
        ("packet23 router23 cluster23 mirror23 filter23 ranking23", 18),
        ["packet23 router23", "cluster23 mirror23", "filter23 ranking23"],
    ),
    (
        ("packet23 router23 cluster23 mirror23 filter23 ranking23", 28),
        ["packet23 router23 cluster23", "mirror23 filter23 ranking23"],
    ),
    (
        ("router23 cluster23 mirror23 filter23 ranking23 encoding23", 6),
        ["router23", "cluster23", "mirror23", "filter23", "ranking23", "encoding23"],
    ),
    (
        ("router23 cluster23 mirror23 filter23 ranking23 encoding23", 10),
        ["router23", "cluster23", "mirror23", "filter23", "ranking23", "encoding23"],
    ),
    (
        ("router23 cluster23 mirror23 filter23 ranking23 encoding23", 18),
        ["router23 cluster23", "mirror23 filter23", "ranking23", "encoding23"],
    ),
    (
        ("router23 cluster23 mirror23 filter23 ranking23 encoding23", 28),
        ["router23 cluster23 mirror23", "filter23 ranking23", "encoding23"],
    ),
    (
        ("cluster23 mirror23 filter23 ranking23 encoding23 mapping23", 6),
        ["cluster23", "mirror23", "filter23", "ranking23", "encoding23", "mapping23"],
    ),
    (
        ("cluster23 mirror23 filter23 ranking23 encoding23 mapping23", 10),
        ["cluster23", "mirror23", "filter23", "ranking23", "encoding23", "mapping23"],
    ),
    (
        ("cluster23 mirror23 filter23 ranking23 encoding23 mapping23", 18),
        ["cluster23 mirror23", "filter23 ranking23", "encoding23", "mapping23"],
    ),
    (
        ("cluster23 mirror23 filter23 ranking23 encoding23 mapping23", 28),
        ["cluster23 mirror23 filter23", "ranking23 encoding23", "mapping23"],
    ),
    (
        ("mirror23 filter23 ranking23 encoding23 mapping23 record23", 6),
        ["mirror23", "filter23", "ranking23", "encoding23", "mapping23", "record23"],
    ),
    (
        ("mirror23 filter23 ranking23 encoding23 mapping23 record23", 10),
        ["mirror23", "filter23", "ranking23", "encoding23", "mapping23", "record23"],
    ),
    (
        ("mirror23 filter23 ranking23 encoding23 mapping23 record23", 18),
        ["mirror23 filter23", "ranking23", "encoding23", "mapping23 record23"],
    ),
    (
        ("mirror23 filter23 ranking23 encoding23 mapping23 record23", 28),
        ["mirror23 filter23 ranking23", "encoding23 mapping23", "record23"],
    ),
    (
        ("filter23 ranking23 encoding23 mapping23 record23 candle23", 6),
        ["filter23", "ranking23", "encoding23", "mapping23", "record23", "candle23"],
    ),
    (
        ("filter23 ranking23 encoding23 mapping23 record23 candle23", 10),
        ["filter23", "ranking23", "encoding23", "mapping23", "record23", "candle23"],
    ),
    (
        ("filter23 ranking23 encoding23 mapping23 record23 candle23", 18),
        ["filter23 ranking23", "encoding23", "mapping23 record23", "candle23"],
    ),
    (
        ("filter23 ranking23 encoding23 mapping23 record23 candle23", 28),
        ["filter23 ranking23", "encoding23 mapping23", "record23 candle23"],
    ),
    (
        ("ranking23 encoding23 mapping23 record23 candle23 thread23", 6),
        ["ranking23", "encoding23", "mapping23", "record23", "candle23", "thread23"],
    ),
    (
        ("ranking23 encoding23 mapping23 record23 candle23 thread23", 10),
        ["ranking23", "encoding23", "mapping23", "record23", "candle23", "thread23"],
    ),
    (
        ("ranking23 encoding23 mapping23 record23 candle23 thread23", 18),
        ["ranking23", "encoding23", "mapping23 record23", "candle23 thread23"],
    ),
    (
        ("ranking23 encoding23 mapping23 record23 candle23 thread23", 28),
        ["ranking23 encoding23", "mapping23 record23 candle23", "thread23"],
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
