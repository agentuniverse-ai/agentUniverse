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
        ("round 82: the quick brown fox jumps over the lazy dog", 4),
        ["round", "82:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 82: the quick brown fox jumps over the lazy dog", 8),
        ["round", "82: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 82: the quick brown fox jumps over the lazy dog", 12),
        ["round 82:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 82: the quick brown fox jumps over the lazy dog", 16),
        ["round 82: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 82: the quick brown fox jumps over the lazy dog", 24),
        ["round 82: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 82: the quick brown fox jumps over the lazy dog", 32),
        ["round 82: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 82: agentuniverse is a framework for multi agents", 4),
        ["round", "82:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 82: agentuniverse is a framework for multi agents", 8),
        ["round", "82:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 82: agentuniverse is a framework for multi agents", 12),
        ["round 82:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 82: agentuniverse is a framework for multi agents", 16),
        ["round 82:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 82: agentuniverse is a framework for multi agents", 24),
        ["round 82: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 82: agentuniverse is a framework for multi agents", 32),
        ["round 82: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 82: knowledge stored as vectors enables retrieval", 4),
        ["round", "82:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 82: knowledge stored as vectors enables retrieval", 8),
        ["round", "82:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 82: knowledge stored as vectors enables retrieval", 12),
        ["round 82:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 82: knowledge stored as vectors enables retrieval", 16),
        ["round 82:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 82: knowledge stored as vectors enables retrieval", 24),
        ["round 82: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 82: knowledge stored as vectors enables retrieval", 32),
        ["round 82: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 82: the processor reads the record then stops", 4),
        ["round", "82:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 82: the processor reads the record then stops", 8),
        ["round", "82: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 82: the processor reads the record then stops", 12),
        ["round 82:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 82: the processor reads the record then stops", 16),
        ["round 82: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 82: the processor reads the record then stops", 24),
        ["round 82: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 82: the processor reads the record then stops", 32),
        ["round 82: the processor reads", "the record then stops"],
    ),
    (
        ("round 82: a worker pulls the next task from the queue", 4),
        ["round", "82:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 82: a worker pulls the next task from the queue", 8),
        ["round", "82: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 82: a worker pulls the next task from the queue", 12),
        ["round 82: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 82: a worker pulls the next task from the queue", 16),
        ["round 82: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 82: a worker pulls the next task from the queue", 24),
        ["round 82: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 82: a worker pulls the next task from the queue", 32),
        ["round 82: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 82: signals travel through the network layer", 4),
        ["round", "82:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 82: signals travel through the network layer", 8),
        ["round", "82:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 82: signals travel through the network layer", 12),
        ["round 82:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 82: signals travel through the network layer", 16),
        ["round 82:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 82: signals travel through the network layer", 24),
        ["round 82: signals travel", "through the network", "layer"],
    ),
    (
        ("round 82: signals travel through the network layer", 32),
        ["round 82: signals travel through", "the network layer"],
    ),
    (
        ("round 82: the gateway routes each request by policy", 4),
        ["round", "82:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 82: the gateway routes each request by policy", 8),
        ["round", "82: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 82: the gateway routes each request by policy", 12),
        ["round 82:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 82: the gateway routes each request by policy", 16),
        ["round 82: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 82: the gateway routes each request by policy", 24),
        ["round 82: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 82: the gateway routes each request by policy", 32),
        ["round 82: the gateway routes", "each request by policy"],
    ),
    (
        ("round 82: memory grows until the buffer is full", 4),
        ["round", "82:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 82: memory grows until the buffer is full", 8),
        ["round", "82:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 82: memory grows until the buffer is full", 12),
        ["round 82:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 82: memory grows until the buffer is full", 16),
        ["round 82: memory", "grows until the", "buffer is full"],
    ),
    (("round 82: memory grows until the buffer is full", 24), ["round 82: memory grows", "until the buffer is full"]),
    (("round 82: memory grows until the buffer is full", 32), ["round 82: memory grows until the", "buffer is full"]),
    (
        ("round 82: the cluster mirrors every packet twice", 4),
        ["round", "82:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 82: the cluster mirrors every packet twice", 8),
        ["round", "82: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 82: the cluster mirrors every packet twice", 12),
        ["round 82:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 82: the cluster mirrors every packet twice", 16),
        ["round 82: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 82: the cluster mirrors every packet twice", 24),
        ["round 82: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 82: the cluster mirrors every packet twice", 32), ["round 82: the cluster mirrors", "every packet twice"]),
    (
        ("round 82: ranking uses tokens learned from the corpus", 4),
        ["round", "82:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 82: ranking uses tokens learned from the corpus", 8),
        ["round", "82:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 82: ranking uses tokens learned from the corpus", 12),
        ["round 82:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 82: ranking uses tokens learned from the corpus", 16),
        ["round 82:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 82: ranking uses tokens learned from the corpus", 24),
        ["round 82: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 82: ranking uses tokens learned from the corpus", 32),
        ["round 82: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 82: a long session ends when the candle dies", 4),
        ["round", "82:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 82: a long session ends when the candle dies", 8),
        ["round", "82: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 82: a long session ends when the candle dies", 12),
        ["round 82: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 82: a long session ends when the candle dies", 16),
        ["round 82: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 82: a long session ends when the candle dies", 24),
        ["round 82: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 82: a long session ends when the candle dies", 32),
        ["round 82: a long session ends", "when the candle dies"],
    ),
    (
        ("round 82: encode the prompt then map the result", 4),
        ["round", "82:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 82: encode the prompt then map the result", 8),
        ["round", "82:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 82: encode the prompt then map the result", 12),
        ["round 82:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 82: encode the prompt then map the result", 16),
        ["round 82: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 82: encode the prompt then map the result", 24),
        ["round 82: encode the", "prompt then map the", "result"],
    ),
    (("round 82: encode the prompt then map the result", 32), ["round 82: encode the prompt then", "map the result"]),
    (
        ("round 82: the kernel wakes the worker at dawn", 4),
        ["round", "82:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 82: the kernel wakes the worker at dawn", 8),
        ["round", "82: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 82: the kernel wakes the worker at dawn", 12),
        ["round 82:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 82: the kernel wakes the worker at dawn", 16), ["round 82: the", "kernel wakes the", "worker at dawn"]),
    (("round 82: the kernel wakes the worker at dawn", 24), ["round 82: the kernel", "wakes the worker at dawn"]),
    (("round 82: the kernel wakes the worker at dawn", 32), ["round 82: the kernel wakes the", "worker at dawn"]),
    (
        ("round 82: service latency drops after the patch", 4),
        ["round", "82:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 82: service latency drops after the patch", 8),
        ["round", "82:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 82: service latency drops after the patch", 12),
        ["round 82:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 82: service latency drops after the patch", 16),
        ["round 82:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 82: service latency drops after the patch", 24),
        ["round 82: service", "latency drops after the", "patch"],
    ),
    (("round 82: service latency drops after the patch", 32), ["round 82: service latency drops", "after the patch"]),
    (
        ("round 82: the library caches every vector it sees", 4),
        ["round", "82:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 82: the library caches every vector it sees", 8),
        ["round", "82: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 82: the library caches every vector it sees", 12),
        ["round 82:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 82: the library caches every vector it sees", 16),
        ["round 82: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 82: the library caches every vector it sees", 24),
        ["round 82: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 82: the library caches every vector it sees", 32),
        ["round 82: the library caches", "every vector it sees"],
    ),
    (
        ("round 82: agents argue then the debate resolves", 4),
        ["round", "82:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 82: agents argue then the debate resolves", 8),
        ["round", "82:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 82: agents argue then the debate resolves", 12),
        ["round 82:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 82: agents argue then the debate resolves", 16),
        ["round 82: agents", "argue then the", "debate resolves"],
    ),
    (("round 82: agents argue then the debate resolves", 24), ["round 82: agents argue", "then the debate resolves"]),
    (("round 82: agents argue then the debate resolves", 32), ["round 82: agents argue then the", "debate resolves"]),
    (
        ("round 82: the filter keeps only strong matches", 4),
        ["round", "82:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 82: the filter keeps only strong matches", 8),
        ["round", "82: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 82: the filter keeps only strong matches", 12),
        ["round 82:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 82: the filter keeps only strong matches", 16),
        ["round 82: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 82: the filter keeps only strong matches", 24), ["round 82: the filter", "keeps only strong", "matches"]),
    (("round 82: the filter keeps only strong matches", 32), ["round 82: the filter keeps only", "strong matches"]),
    (
        ("round 82: the model answers with a short reply", 4),
        ["round", "82:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 82: the model answers with a short reply", 8),
        ["round", "82: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 82: the model answers with a short reply", 12),
        ["round 82:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 82: the model answers with a short reply", 16),
        ["round 82: the", "model answers", "with a short", "reply"],
    ),
    (("round 82: the model answers with a short reply", 24), ["round 82: the model", "answers with a short", "reply"]),
    (("round 82: the model answers with a short reply", 32), ["round 82: the model answers with", "a short reply"]),
    (
        ("round 82: the recorder stores the reasoning trace", 4),
        ["round", "82:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 82: the recorder stores the reasoning trace", 8),
        ["round", "82: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 82: the recorder stores the reasoning trace", 12),
        ["round 82:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 82: the recorder stores the reasoning trace", 16),
        ["round 82: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 82: the recorder stores the reasoning trace", 24),
        ["round 82: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 82: the recorder stores the reasoning trace", 32),
        ["round 82: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 82: the angel watches the processor run", 4),
        ["round", "82:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 82: the angel watches the processor run", 8),
        ["round", "82: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 82: the angel watches the processor run", 12),
        ["round 82:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 82: the angel watches the processor run", 16), ["round 82: the", "angel watches", "the processor", "run"]),
    (("round 82: the angel watches the processor run", 24), ["round 82: the angel", "watches the processor", "run"]),
    (("round 82: the angel watches the processor run", 32), ["round 82: the angel watches the", "processor run"]),
    (
        ("round 82: angle of the vector decides the match", 4),
        ["round", "82:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 82: angle of the vector decides the match", 8),
        ["round", "82:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 82: angle of the vector decides the match", 12),
        ["round 82:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 82: angle of the vector decides the match", 16),
        ["round 82: angle", "of the vector", "decides the", "match"],
    ),
    (("round 82: angle of the vector decides the match", 24), ["round 82: angle of the", "vector decides the match"]),
    (("round 82: angle of the vector decides the match", 32), ["round 82: angle of the vector", "decides the match"]),
    (
        ("round 82: the candle burns twice as long at night", 4),
        ["round", "82:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 82: the candle burns twice as long at night", 8),
        ["round", "82: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 82: the candle burns twice as long at night", 12),
        ["round 82:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 82: the candle burns twice as long at night", 16),
        ["round 82: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 82: the candle burns twice as long at night", 24),
        ["round 82: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 82: the candle burns twice as long at night", 32),
        ["round 82: the candle burns twice", "as long at night"],
    ),
    (
        ("round 82: a mirror of the universe in one line", 4),
        ["round", "82:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 82: a mirror of the universe in one line", 8),
        ["round", "82: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 82: a mirror of the universe in one line", 12),
        ["round 82: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 82: a mirror of the universe in one line", 16),
        ["round 82: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 82: a mirror of the universe in one line", 24), ["round 82: a mirror of", "the universe in one line"]),
    (("round 82: a mirror of the universe in one line", 32), ["round 82: a mirror of the", "universe in one line"]),
    (
        ("round 82: the queue drains before the storm", 4),
        ["round", "82:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 82: the queue drains before the storm", 8),
        ["round", "82: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 82: the queue drains before the storm", 12), ["round 82:", "the queue", "drains", "before the", "storm"]),
    (("round 82: the queue drains before the storm", 16), ["round 82: the", "queue drains", "before the storm"]),
    (("round 82: the queue drains before the storm", 24), ["round 82: the queue", "drains before the storm"]),
    (("round 82: the queue drains before the storm", 32), ["round 82: the queue drains", "before the storm"]),
    (
        ("kitten82 sitting82 agent82 angle82 universe82 memory82", 6),
        ["kitten82", "sitting82", "agent82", "angle82", "universe82", "memory82"],
    ),
    (
        ("kitten82 sitting82 agent82 angle82 universe82 memory82", 10),
        ["kitten82", "sitting82", "agent82", "angle82", "universe82", "memory82"],
    ),
    (
        ("kitten82 sitting82 agent82 angle82 universe82 memory82", 18),
        ["kitten82 sitting82", "agent82 angle82", "universe82", "memory82"],
    ),
    (
        ("kitten82 sitting82 agent82 angle82 universe82 memory82", 28),
        ["kitten82 sitting82 agent82", "angle82 universe82 memory82"],
    ),
    (
        ("sitting82 agent82 angle82 universe82 memory82 stream82", 6),
        ["sitting82", "agent82", "angle82", "universe82", "memory82", "stream82"],
    ),
    (
        ("sitting82 agent82 angle82 universe82 memory82 stream82", 10),
        ["sitting82", "agent82", "angle82", "universe82", "memory82", "stream82"],
    ),
    (
        ("sitting82 agent82 angle82 universe82 memory82 stream82", 18),
        ["sitting82 agent82", "angle82 universe82", "memory82 stream82"],
    ),
    (
        ("sitting82 agent82 angle82 universe82 memory82 stream82", 28),
        ["sitting82 agent82 angle82", "universe82 memory82 stream82"],
    ),
    (
        ("agent82 angle82 universe82 memory82 stream82 context82", 6),
        ["agent82", "angle82", "universe82", "memory82", "stream82", "context82"],
    ),
    (
        ("agent82 angle82 universe82 memory82 stream82 context82", 10),
        ["agent82", "angle82", "universe82", "memory82", "stream82", "context82"],
    ),
    (
        ("agent82 angle82 universe82 memory82 stream82 context82", 18),
        ["agent82 angle82", "universe82", "memory82 stream82", "context82"],
    ),
    (
        ("agent82 angle82 universe82 memory82 stream82 context82", 28),
        ["agent82 angle82 universe82", "memory82 stream82 context82"],
    ),
    (
        ("angle82 universe82 memory82 stream82 context82 knowledge82", 6),
        ["angle82", "universe82", "memory82", "stream82", "context82", "knowledge82"],
    ),
    (
        ("angle82 universe82 memory82 stream82 context82 knowledge82", 10),
        ["angle82", "universe82", "memory82", "stream82", "context82", "knowledge82"],
    ),
    (
        ("angle82 universe82 memory82 stream82 context82 knowledge82", 18),
        ["angle82 universe82", "memory82 stream82", "context82", "knowledge82"],
    ),
    (
        ("angle82 universe82 memory82 stream82 context82 knowledge82", 28),
        ["angle82 universe82 memory82", "stream82 context82", "knowledge82"],
    ),
    (
        ("universe82 memory82 stream82 context82 knowledge82 vector82", 6),
        ["universe82", "memory82", "stream82", "context82", "knowledge82", "vector82"],
    ),
    (
        ("universe82 memory82 stream82 context82 knowledge82 vector82", 10),
        ["universe82", "memory82", "stream82", "context82", "knowledge82", "vector82"],
    ),
    (
        ("universe82 memory82 stream82 context82 knowledge82 vector82", 18),
        ["universe82", "memory82 stream82", "context82", "knowledge82", "vector82"],
    ),
    (
        ("universe82 memory82 stream82 context82 knowledge82 vector82", 28),
        ["universe82 memory82 stream82", "context82 knowledge82", "vector82"],
    ),
    (
        ("memory82 stream82 context82 knowledge82 vector82 processor82", 6),
        ["memory82", "stream82", "context82", "knowledge82", "vector82", "processor82"],
    ),
    (
        ("memory82 stream82 context82 knowledge82 vector82 processor82", 10),
        ["memory82", "stream82", "context82", "knowledge82", "vector82", "processor82"],
    ),
    (
        ("memory82 stream82 context82 knowledge82 vector82 processor82", 18),
        ["memory82 stream82", "context82", "knowledge82", "vector82", "processor82"],
    ),
    (
        ("memory82 stream82 context82 knowledge82 vector82 processor82", 28),
        ["memory82 stream82 context82", "knowledge82 vector82", "processor82"],
    ),
    (
        ("stream82 context82 knowledge82 vector82 processor82 reasoning82", 6),
        ["stream82", "context82", "knowledge82", "vector82", "processor82", "reasoning82"],
    ),
    (
        ("stream82 context82 knowledge82 vector82 processor82 reasoning82", 10),
        ["stream82", "context82", "knowledge82", "vector82", "processor82", "reasoning82"],
    ),
    (
        ("stream82 context82 knowledge82 vector82 processor82 reasoning82", 18),
        ["stream82 context82", "knowledge82", "vector82", "processor82", "reasoning82"],
    ),
    (
        ("stream82 context82 knowledge82 vector82 processor82 reasoning82", 28),
        ["stream82 context82", "knowledge82 vector82", "processor82 reasoning82"],
    ),
    (
        ("context82 knowledge82 vector82 processor82 reasoning82 machine82", 6),
        ["context82", "knowledge82", "vector82", "processor82", "reasoning82", "machine82"],
    ),
    (
        ("context82 knowledge82 vector82 processor82 reasoning82 machine82", 10),
        ["context82", "knowledge82", "vector82", "processor82", "reasoning82", "machine82"],
    ),
    (
        ("context82 knowledge82 vector82 processor82 reasoning82 machine82", 18),
        ["context82", "knowledge82", "vector82", "processor82", "reasoning82", "machine82"],
    ),
    (
        ("context82 knowledge82 vector82 processor82 reasoning82 machine82", 28),
        ["context82 knowledge82", "vector82 processor82", "reasoning82 machine82"],
    ),
    (
        ("knowledge82 vector82 processor82 reasoning82 machine82 learning82", 6),
        ["knowledge82", "vector82", "processor82", "reasoning82", "machine82", "learning82"],
    ),
    (
        ("knowledge82 vector82 processor82 reasoning82 machine82 learning82", 10),
        ["knowledge82", "vector82", "processor82", "reasoning82", "machine82", "learning82"],
    ),
    (
        ("knowledge82 vector82 processor82 reasoning82 machine82 learning82", 18),
        ["knowledge82", "vector82", "processor82", "reasoning82", "machine82", "learning82"],
    ),
    (
        ("knowledge82 vector82 processor82 reasoning82 machine82 learning82", 28),
        ["knowledge82 vector82", "processor82 reasoning82", "machine82 learning82"],
    ),
    (
        ("vector82 processor82 reasoning82 machine82 learning82 model82", 6),
        ["vector82", "processor82", "reasoning82", "machine82", "learning82", "model82"],
    ),
    (
        ("vector82 processor82 reasoning82 machine82 learning82 model82", 10),
        ["vector82", "processor82", "reasoning82", "machine82", "learning82", "model82"],
    ),
    (
        ("vector82 processor82 reasoning82 machine82 learning82 model82", 18),
        ["vector82", "processor82", "reasoning82", "machine82", "learning82 model82"],
    ),
    (
        ("vector82 processor82 reasoning82 machine82 learning82 model82", 28),
        ["vector82 processor82", "reasoning82 machine82", "learning82 model82"],
    ),
    (
        ("processor82 reasoning82 machine82 learning82 model82 token82", 6),
        ["processor82", "reasoning82", "machine82", "learning82", "model82", "token82"],
    ),
    (
        ("processor82 reasoning82 machine82 learning82 model82 token82", 10),
        ["processor82", "reasoning82", "machine82", "learning82", "model82", "token82"],
    ),
    (
        ("processor82 reasoning82 machine82 learning82 model82 token82", 18),
        ["processor82", "reasoning82", "machine82", "learning82 model82", "token82"],
    ),
    (
        ("processor82 reasoning82 machine82 learning82 model82 token82", 28),
        ["processor82 reasoning82", "machine82 learning82 model82", "token82"],
    ),
    (
        ("reasoning82 machine82 learning82 model82 token82 prompt82", 6),
        ["reasoning82", "machine82", "learning82", "model82", "token82", "prompt82"],
    ),
    (
        ("reasoning82 machine82 learning82 model82 token82 prompt82", 10),
        ["reasoning82", "machine82", "learning82", "model82", "token82", "prompt82"],
    ),
    (
        ("reasoning82 machine82 learning82 model82 token82 prompt82", 18),
        ["reasoning82", "machine82", "learning82 model82", "token82 prompt82"],
    ),
    (
        ("reasoning82 machine82 learning82 model82 token82 prompt82", 28),
        ["reasoning82 machine82", "learning82 model82 token82", "prompt82"],
    ),
    (
        ("machine82 learning82 model82 token82 prompt82 session82", 6),
        ["machine82", "learning82", "model82", "token82", "prompt82", "session82"],
    ),
    (
        ("machine82 learning82 model82 token82 prompt82 session82", 10),
        ["machine82", "learning82", "model82", "token82", "prompt82", "session82"],
    ),
    (
        ("machine82 learning82 model82 token82 prompt82 session82", 18),
        ["machine82", "learning82 model82", "token82 prompt82", "session82"],
    ),
    (
        ("machine82 learning82 model82 token82 prompt82 session82", 28),
        ["machine82 learning82 model82", "token82 prompt82 session82"],
    ),
    (
        ("learning82 model82 token82 prompt82 session82 library82", 6),
        ["learning82", "model82", "token82", "prompt82", "session82", "library82"],
    ),
    (
        ("learning82 model82 token82 prompt82 session82 library82", 10),
        ["learning82", "model82", "token82", "prompt82", "session82", "library82"],
    ),
    (
        ("learning82 model82 token82 prompt82 session82 library82", 18),
        ["learning82 model82", "token82 prompt82", "session82", "library82"],
    ),
    (
        ("learning82 model82 token82 prompt82 session82 library82", 28),
        ["learning82 model82 token82", "prompt82 session82 library82"],
    ),
    (
        ("model82 token82 prompt82 session82 library82 service82", 6),
        ["model82", "token82", "prompt82", "session82", "library82", "service82"],
    ),
    (
        ("model82 token82 prompt82 session82 library82 service82", 10),
        ["model82", "token82", "prompt82", "session82", "library82", "service82"],
    ),
    (
        ("model82 token82 prompt82 session82 library82 service82", 18),
        ["model82 token82", "prompt82 session82", "library82", "service82"],
    ),
    (
        ("model82 token82 prompt82 session82 library82 service82", 28),
        ["model82 token82 prompt82", "session82 library82", "service82"],
    ),
    (
        ("token82 prompt82 session82 library82 service82 gateway82", 6),
        ["token82", "prompt82", "session82", "library82", "service82", "gateway82"],
    ),
    (
        ("token82 prompt82 session82 library82 service82 gateway82", 10),
        ["token82", "prompt82", "session82", "library82", "service82", "gateway82"],
    ),
    (
        ("token82 prompt82 session82 library82 service82 gateway82", 18),
        ["token82 prompt82", "session82", "library82", "service82", "gateway82"],
    ),
    (
        ("token82 prompt82 session82 library82 service82 gateway82", 28),
        ["token82 prompt82 session82", "library82 service82", "gateway82"],
    ),
    (
        ("prompt82 session82 library82 service82 gateway82 storage82", 6),
        ["prompt82", "session82", "library82", "service82", "gateway82", "storage82"],
    ),
    (
        ("prompt82 session82 library82 service82 gateway82 storage82", 10),
        ["prompt82", "session82", "library82", "service82", "gateway82", "storage82"],
    ),
    (
        ("prompt82 session82 library82 service82 gateway82 storage82", 18),
        ["prompt82 session82", "library82", "service82", "gateway82", "storage82"],
    ),
    (
        ("prompt82 session82 library82 service82 gateway82 storage82", 28),
        ["prompt82 session82 library82", "service82 gateway82", "storage82"],
    ),
    (
        ("session82 library82 service82 gateway82 storage82 network82", 6),
        ["session82", "library82", "service82", "gateway82", "storage82", "network82"],
    ),
    (
        ("session82 library82 service82 gateway82 storage82 network82", 10),
        ["session82", "library82", "service82", "gateway82", "storage82", "network82"],
    ),
    (
        ("session82 library82 service82 gateway82 storage82 network82", 18),
        ["session82", "library82", "service82", "gateway82", "storage82", "network82"],
    ),
    (
        ("session82 library82 service82 gateway82 storage82 network82", 28),
        ["session82 library82", "service82 gateway82", "storage82 network82"],
    ),
    (
        ("library82 service82 gateway82 storage82 network82 latency82", 6),
        ["library82", "service82", "gateway82", "storage82", "network82", "latency82"],
    ),
    (
        ("library82 service82 gateway82 storage82 network82 latency82", 10),
        ["library82", "service82", "gateway82", "storage82", "network82", "latency82"],
    ),
    (
        ("library82 service82 gateway82 storage82 network82 latency82", 18),
        ["library82", "service82", "gateway82", "storage82", "network82", "latency82"],
    ),
    (
        ("library82 service82 gateway82 storage82 network82 latency82", 28),
        ["library82 service82", "gateway82 storage82", "network82 latency82"],
    ),
    (
        ("service82 gateway82 storage82 network82 latency82 buffer82", 6),
        ["service82", "gateway82", "storage82", "network82", "latency82", "buffer82"],
    ),
    (
        ("service82 gateway82 storage82 network82 latency82 buffer82", 10),
        ["service82", "gateway82", "storage82", "network82", "latency82", "buffer82"],
    ),
    (
        ("service82 gateway82 storage82 network82 latency82 buffer82", 18),
        ["service82", "gateway82", "storage82", "network82", "latency82 buffer82"],
    ),
    (
        ("service82 gateway82 storage82 network82 latency82 buffer82", 28),
        ["service82 gateway82", "storage82 network82", "latency82 buffer82"],
    ),
    (
        ("gateway82 storage82 network82 latency82 buffer82 queue82", 6),
        ["gateway82", "storage82", "network82", "latency82", "buffer82", "queue82"],
    ),
    (
        ("gateway82 storage82 network82 latency82 buffer82 queue82", 10),
        ["gateway82", "storage82", "network82", "latency82", "buffer82", "queue82"],
    ),
    (
        ("gateway82 storage82 network82 latency82 buffer82 queue82", 18),
        ["gateway82", "storage82", "network82", "latency82 buffer82", "queue82"],
    ),
    (
        ("gateway82 storage82 network82 latency82 buffer82 queue82", 28),
        ["gateway82 storage82", "network82 latency82 buffer82", "queue82"],
    ),
    (
        ("storage82 network82 latency82 buffer82 queue82 worker82", 6),
        ["storage82", "network82", "latency82", "buffer82", "queue82", "worker82"],
    ),
    (
        ("storage82 network82 latency82 buffer82 queue82 worker82", 10),
        ["storage82", "network82", "latency82", "buffer82", "queue82", "worker82"],
    ),
    (
        ("storage82 network82 latency82 buffer82 queue82 worker82", 18),
        ["storage82", "network82", "latency82 buffer82", "queue82 worker82"],
    ),
    (
        ("storage82 network82 latency82 buffer82 queue82 worker82", 28),
        ["storage82 network82", "latency82 buffer82 queue82", "worker82"],
    ),
    (
        ("network82 latency82 buffer82 queue82 worker82 kernel82", 6),
        ["network82", "latency82", "buffer82", "queue82", "worker82", "kernel82"],
    ),
    (
        ("network82 latency82 buffer82 queue82 worker82 kernel82", 10),
        ["network82", "latency82", "buffer82", "queue82", "worker82", "kernel82"],
    ),
    (
        ("network82 latency82 buffer82 queue82 worker82 kernel82", 18),
        ["network82", "latency82 buffer82", "queue82 worker82", "kernel82"],
    ),
    (
        ("network82 latency82 buffer82 queue82 worker82 kernel82", 28),
        ["network82 latency82 buffer82", "queue82 worker82 kernel82"],
    ),
    (
        ("latency82 buffer82 queue82 worker82 kernel82 signal82", 6),
        ["latency82", "buffer82", "queue82", "worker82", "kernel82", "signal82"],
    ),
    (
        ("latency82 buffer82 queue82 worker82 kernel82 signal82", 10),
        ["latency82", "buffer82", "queue82", "worker82", "kernel82", "signal82"],
    ),
    (
        ("latency82 buffer82 queue82 worker82 kernel82 signal82", 18),
        ["latency82 buffer82", "queue82 worker82", "kernel82 signal82"],
    ),
    (
        ("latency82 buffer82 queue82 worker82 kernel82 signal82", 28),
        ["latency82 buffer82 queue82", "worker82 kernel82 signal82"],
    ),
    (
        ("buffer82 queue82 worker82 kernel82 signal82 packet82", 6),
        ["buffer82", "queue82", "worker82", "kernel82", "signal82", "packet82"],
    ),
    (
        ("buffer82 queue82 worker82 kernel82 signal82 packet82", 10),
        ["buffer82", "queue82", "worker82", "kernel82", "signal82", "packet82"],
    ),
    (
        ("buffer82 queue82 worker82 kernel82 signal82 packet82", 18),
        ["buffer82 queue82", "worker82 kernel82", "signal82 packet82"],
    ),
    (
        ("buffer82 queue82 worker82 kernel82 signal82 packet82", 28),
        ["buffer82 queue82 worker82", "kernel82 signal82 packet82"],
    ),
    (
        ("queue82 worker82 kernel82 signal82 packet82 router82", 6),
        ["queue82", "worker82", "kernel82", "signal82", "packet82", "router82"],
    ),
    (
        ("queue82 worker82 kernel82 signal82 packet82 router82", 10),
        ["queue82", "worker82", "kernel82", "signal82", "packet82", "router82"],
    ),
    (
        ("queue82 worker82 kernel82 signal82 packet82 router82", 18),
        ["queue82 worker82", "kernel82 signal82", "packet82 router82"],
    ),
    (
        ("queue82 worker82 kernel82 signal82 packet82 router82", 28),
        ["queue82 worker82 kernel82", "signal82 packet82 router82"],
    ),
    (
        ("worker82 kernel82 signal82 packet82 router82 cluster82", 6),
        ["worker82", "kernel82", "signal82", "packet82", "router82", "cluster82"],
    ),
    (
        ("worker82 kernel82 signal82 packet82 router82 cluster82", 10),
        ["worker82", "kernel82", "signal82", "packet82", "router82", "cluster82"],
    ),
    (
        ("worker82 kernel82 signal82 packet82 router82 cluster82", 18),
        ["worker82 kernel82", "signal82 packet82", "router82 cluster82"],
    ),
    (
        ("worker82 kernel82 signal82 packet82 router82 cluster82", 28),
        ["worker82 kernel82 signal82", "packet82 router82 cluster82"],
    ),
    (
        ("kernel82 signal82 packet82 router82 cluster82 mirror82", 6),
        ["kernel82", "signal82", "packet82", "router82", "cluster82", "mirror82"],
    ),
    (
        ("kernel82 signal82 packet82 router82 cluster82 mirror82", 10),
        ["kernel82", "signal82", "packet82", "router82", "cluster82", "mirror82"],
    ),
    (
        ("kernel82 signal82 packet82 router82 cluster82 mirror82", 18),
        ["kernel82 signal82", "packet82 router82", "cluster82 mirror82"],
    ),
    (
        ("kernel82 signal82 packet82 router82 cluster82 mirror82", 28),
        ["kernel82 signal82 packet82", "router82 cluster82 mirror82"],
    ),
    (
        ("signal82 packet82 router82 cluster82 mirror82 filter82", 6),
        ["signal82", "packet82", "router82", "cluster82", "mirror82", "filter82"],
    ),
    (
        ("signal82 packet82 router82 cluster82 mirror82 filter82", 10),
        ["signal82", "packet82", "router82", "cluster82", "mirror82", "filter82"],
    ),
    (
        ("signal82 packet82 router82 cluster82 mirror82 filter82", 18),
        ["signal82 packet82", "router82 cluster82", "mirror82 filter82"],
    ),
    (
        ("signal82 packet82 router82 cluster82 mirror82 filter82", 28),
        ["signal82 packet82 router82", "cluster82 mirror82 filter82"],
    ),
    (
        ("packet82 router82 cluster82 mirror82 filter82 ranking82", 6),
        ["packet82", "router82", "cluster82", "mirror82", "filter82", "ranking82"],
    ),
    (
        ("packet82 router82 cluster82 mirror82 filter82 ranking82", 10),
        ["packet82", "router82", "cluster82", "mirror82", "filter82", "ranking82"],
    ),
    (
        ("packet82 router82 cluster82 mirror82 filter82 ranking82", 18),
        ["packet82 router82", "cluster82 mirror82", "filter82 ranking82"],
    ),
    (
        ("packet82 router82 cluster82 mirror82 filter82 ranking82", 28),
        ["packet82 router82 cluster82", "mirror82 filter82 ranking82"],
    ),
    (
        ("router82 cluster82 mirror82 filter82 ranking82 encoding82", 6),
        ["router82", "cluster82", "mirror82", "filter82", "ranking82", "encoding82"],
    ),
    (
        ("router82 cluster82 mirror82 filter82 ranking82 encoding82", 10),
        ["router82", "cluster82", "mirror82", "filter82", "ranking82", "encoding82"],
    ),
    (
        ("router82 cluster82 mirror82 filter82 ranking82 encoding82", 18),
        ["router82 cluster82", "mirror82 filter82", "ranking82", "encoding82"],
    ),
    (
        ("router82 cluster82 mirror82 filter82 ranking82 encoding82", 28),
        ["router82 cluster82 mirror82", "filter82 ranking82", "encoding82"],
    ),
    (
        ("cluster82 mirror82 filter82 ranking82 encoding82 mapping82", 6),
        ["cluster82", "mirror82", "filter82", "ranking82", "encoding82", "mapping82"],
    ),
    (
        ("cluster82 mirror82 filter82 ranking82 encoding82 mapping82", 10),
        ["cluster82", "mirror82", "filter82", "ranking82", "encoding82", "mapping82"],
    ),
    (
        ("cluster82 mirror82 filter82 ranking82 encoding82 mapping82", 18),
        ["cluster82 mirror82", "filter82 ranking82", "encoding82", "mapping82"],
    ),
    (
        ("cluster82 mirror82 filter82 ranking82 encoding82 mapping82", 28),
        ["cluster82 mirror82 filter82", "ranking82 encoding82", "mapping82"],
    ),
    (
        ("mirror82 filter82 ranking82 encoding82 mapping82 record82", 6),
        ["mirror82", "filter82", "ranking82", "encoding82", "mapping82", "record82"],
    ),
    (
        ("mirror82 filter82 ranking82 encoding82 mapping82 record82", 10),
        ["mirror82", "filter82", "ranking82", "encoding82", "mapping82", "record82"],
    ),
    (
        ("mirror82 filter82 ranking82 encoding82 mapping82 record82", 18),
        ["mirror82 filter82", "ranking82", "encoding82", "mapping82 record82"],
    ),
    (
        ("mirror82 filter82 ranking82 encoding82 mapping82 record82", 28),
        ["mirror82 filter82 ranking82", "encoding82 mapping82", "record82"],
    ),
    (
        ("filter82 ranking82 encoding82 mapping82 record82 candle82", 6),
        ["filter82", "ranking82", "encoding82", "mapping82", "record82", "candle82"],
    ),
    (
        ("filter82 ranking82 encoding82 mapping82 record82 candle82", 10),
        ["filter82", "ranking82", "encoding82", "mapping82", "record82", "candle82"],
    ),
    (
        ("filter82 ranking82 encoding82 mapping82 record82 candle82", 18),
        ["filter82 ranking82", "encoding82", "mapping82 record82", "candle82"],
    ),
    (
        ("filter82 ranking82 encoding82 mapping82 record82 candle82", 28),
        ["filter82 ranking82", "encoding82 mapping82", "record82 candle82"],
    ),
    (
        ("ranking82 encoding82 mapping82 record82 candle82 thread82", 6),
        ["ranking82", "encoding82", "mapping82", "record82", "candle82", "thread82"],
    ),
    (
        ("ranking82 encoding82 mapping82 record82 candle82 thread82", 10),
        ["ranking82", "encoding82", "mapping82", "record82", "candle82", "thread82"],
    ),
    (
        ("ranking82 encoding82 mapping82 record82 candle82 thread82", 18),
        ["ranking82", "encoding82", "mapping82 record82", "candle82 thread82"],
    ),
    (
        ("ranking82 encoding82 mapping82 record82 candle82 thread82", 28),
        ["ranking82 encoding82", "mapping82 record82 candle82", "thread82"],
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
