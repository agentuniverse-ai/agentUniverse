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
        ("round 12: the quick brown fox jumps over the lazy dog", 4),
        ["round", "12:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 12: the quick brown fox jumps over the lazy dog", 8),
        ["round", "12: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 12: the quick brown fox jumps over the lazy dog", 12),
        ["round 12:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 12: the quick brown fox jumps over the lazy dog", 16),
        ["round 12: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 12: the quick brown fox jumps over the lazy dog", 24),
        ["round 12: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 12: the quick brown fox jumps over the lazy dog", 32),
        ["round 12: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 12: agentuniverse is a framework for multi agents", 4),
        ["round", "12:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 12: agentuniverse is a framework for multi agents", 8),
        ["round", "12:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 12: agentuniverse is a framework for multi agents", 12),
        ["round 12:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 12: agentuniverse is a framework for multi agents", 16),
        ["round 12:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 12: agentuniverse is a framework for multi agents", 24),
        ["round 12: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 12: agentuniverse is a framework for multi agents", 32),
        ["round 12: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 12: knowledge stored as vectors enables retrieval", 4),
        ["round", "12:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 12: knowledge stored as vectors enables retrieval", 8),
        ["round", "12:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 12: knowledge stored as vectors enables retrieval", 12),
        ["round 12:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 12: knowledge stored as vectors enables retrieval", 16),
        ["round 12:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 12: knowledge stored as vectors enables retrieval", 24),
        ["round 12: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 12: knowledge stored as vectors enables retrieval", 32),
        ["round 12: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 12: the processor reads the record then stops", 4),
        ["round", "12:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 12: the processor reads the record then stops", 8),
        ["round", "12: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 12: the processor reads the record then stops", 12),
        ["round 12:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 12: the processor reads the record then stops", 16),
        ["round 12: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 12: the processor reads the record then stops", 24),
        ["round 12: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 12: the processor reads the record then stops", 32),
        ["round 12: the processor reads", "the record then stops"],
    ),
    (
        ("round 12: a worker pulls the next task from the queue", 4),
        ["round", "12:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 12: a worker pulls the next task from the queue", 8),
        ["round", "12: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 12: a worker pulls the next task from the queue", 12),
        ["round 12: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 12: a worker pulls the next task from the queue", 16),
        ["round 12: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 12: a worker pulls the next task from the queue", 24),
        ["round 12: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 12: a worker pulls the next task from the queue", 32),
        ["round 12: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 12: signals travel through the network layer", 4),
        ["round", "12:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 12: signals travel through the network layer", 8),
        ["round", "12:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 12: signals travel through the network layer", 12),
        ["round 12:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 12: signals travel through the network layer", 16),
        ["round 12:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 12: signals travel through the network layer", 24),
        ["round 12: signals travel", "through the network", "layer"],
    ),
    (
        ("round 12: signals travel through the network layer", 32),
        ["round 12: signals travel through", "the network layer"],
    ),
    (
        ("round 12: the gateway routes each request by policy", 4),
        ["round", "12:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 12: the gateway routes each request by policy", 8),
        ["round", "12: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 12: the gateway routes each request by policy", 12),
        ["round 12:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 12: the gateway routes each request by policy", 16),
        ["round 12: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 12: the gateway routes each request by policy", 24),
        ["round 12: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 12: the gateway routes each request by policy", 32),
        ["round 12: the gateway routes", "each request by policy"],
    ),
    (
        ("round 12: memory grows until the buffer is full", 4),
        ["round", "12:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 12: memory grows until the buffer is full", 8),
        ["round", "12:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 12: memory grows until the buffer is full", 12),
        ["round 12:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 12: memory grows until the buffer is full", 16),
        ["round 12: memory", "grows until the", "buffer is full"],
    ),
    (("round 12: memory grows until the buffer is full", 24), ["round 12: memory grows", "until the buffer is full"]),
    (("round 12: memory grows until the buffer is full", 32), ["round 12: memory grows until the", "buffer is full"]),
    (
        ("round 12: the cluster mirrors every packet twice", 4),
        ["round", "12:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 12: the cluster mirrors every packet twice", 8),
        ["round", "12: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 12: the cluster mirrors every packet twice", 12),
        ["round 12:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 12: the cluster mirrors every packet twice", 16),
        ["round 12: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 12: the cluster mirrors every packet twice", 24),
        ["round 12: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 12: the cluster mirrors every packet twice", 32), ["round 12: the cluster mirrors", "every packet twice"]),
    (
        ("round 12: ranking uses tokens learned from the corpus", 4),
        ["round", "12:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 12: ranking uses tokens learned from the corpus", 8),
        ["round", "12:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 12: ranking uses tokens learned from the corpus", 12),
        ["round 12:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 12: ranking uses tokens learned from the corpus", 16),
        ["round 12:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 12: ranking uses tokens learned from the corpus", 24),
        ["round 12: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 12: ranking uses tokens learned from the corpus", 32),
        ["round 12: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 12: a long session ends when the candle dies", 4),
        ["round", "12:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 12: a long session ends when the candle dies", 8),
        ["round", "12: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 12: a long session ends when the candle dies", 12),
        ["round 12: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 12: a long session ends when the candle dies", 16),
        ["round 12: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 12: a long session ends when the candle dies", 24),
        ["round 12: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 12: a long session ends when the candle dies", 32),
        ["round 12: a long session ends", "when the candle dies"],
    ),
    (
        ("round 12: encode the prompt then map the result", 4),
        ["round", "12:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 12: encode the prompt then map the result", 8),
        ["round", "12:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 12: encode the prompt then map the result", 12),
        ["round 12:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 12: encode the prompt then map the result", 16),
        ["round 12: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 12: encode the prompt then map the result", 24),
        ["round 12: encode the", "prompt then map the", "result"],
    ),
    (("round 12: encode the prompt then map the result", 32), ["round 12: encode the prompt then", "map the result"]),
    (
        ("round 12: the kernel wakes the worker at dawn", 4),
        ["round", "12:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 12: the kernel wakes the worker at dawn", 8),
        ["round", "12: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 12: the kernel wakes the worker at dawn", 12),
        ["round 12:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 12: the kernel wakes the worker at dawn", 16), ["round 12: the", "kernel wakes the", "worker at dawn"]),
    (("round 12: the kernel wakes the worker at dawn", 24), ["round 12: the kernel", "wakes the worker at dawn"]),
    (("round 12: the kernel wakes the worker at dawn", 32), ["round 12: the kernel wakes the", "worker at dawn"]),
    (
        ("round 12: service latency drops after the patch", 4),
        ["round", "12:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 12: service latency drops after the patch", 8),
        ["round", "12:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 12: service latency drops after the patch", 12),
        ["round 12:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 12: service latency drops after the patch", 16),
        ["round 12:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 12: service latency drops after the patch", 24),
        ["round 12: service", "latency drops after the", "patch"],
    ),
    (("round 12: service latency drops after the patch", 32), ["round 12: service latency drops", "after the patch"]),
    (
        ("round 12: the library caches every vector it sees", 4),
        ["round", "12:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 12: the library caches every vector it sees", 8),
        ["round", "12: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 12: the library caches every vector it sees", 12),
        ["round 12:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 12: the library caches every vector it sees", 16),
        ["round 12: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 12: the library caches every vector it sees", 24),
        ["round 12: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 12: the library caches every vector it sees", 32),
        ["round 12: the library caches", "every vector it sees"],
    ),
    (
        ("round 12: agents argue then the debate resolves", 4),
        ["round", "12:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 12: agents argue then the debate resolves", 8),
        ["round", "12:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 12: agents argue then the debate resolves", 12),
        ["round 12:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 12: agents argue then the debate resolves", 16),
        ["round 12: agents", "argue then the", "debate resolves"],
    ),
    (("round 12: agents argue then the debate resolves", 24), ["round 12: agents argue", "then the debate resolves"]),
    (("round 12: agents argue then the debate resolves", 32), ["round 12: agents argue then the", "debate resolves"]),
    (
        ("round 12: the filter keeps only strong matches", 4),
        ["round", "12:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 12: the filter keeps only strong matches", 8),
        ["round", "12: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 12: the filter keeps only strong matches", 12),
        ["round 12:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 12: the filter keeps only strong matches", 16),
        ["round 12: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 12: the filter keeps only strong matches", 24), ["round 12: the filter", "keeps only strong", "matches"]),
    (("round 12: the filter keeps only strong matches", 32), ["round 12: the filter keeps only", "strong matches"]),
    (
        ("round 12: the model answers with a short reply", 4),
        ["round", "12:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 12: the model answers with a short reply", 8),
        ["round", "12: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 12: the model answers with a short reply", 12),
        ["round 12:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 12: the model answers with a short reply", 16),
        ["round 12: the", "model answers", "with a short", "reply"],
    ),
    (("round 12: the model answers with a short reply", 24), ["round 12: the model", "answers with a short", "reply"]),
    (("round 12: the model answers with a short reply", 32), ["round 12: the model answers with", "a short reply"]),
    (
        ("round 12: the recorder stores the reasoning trace", 4),
        ["round", "12:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 12: the recorder stores the reasoning trace", 8),
        ["round", "12: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 12: the recorder stores the reasoning trace", 12),
        ["round 12:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 12: the recorder stores the reasoning trace", 16),
        ["round 12: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 12: the recorder stores the reasoning trace", 24),
        ["round 12: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 12: the recorder stores the reasoning trace", 32),
        ["round 12: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 12: the angel watches the processor run", 4),
        ["round", "12:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 12: the angel watches the processor run", 8),
        ["round", "12: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 12: the angel watches the processor run", 12),
        ["round 12:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 12: the angel watches the processor run", 16), ["round 12: the", "angel watches", "the processor", "run"]),
    (("round 12: the angel watches the processor run", 24), ["round 12: the angel", "watches the processor", "run"]),
    (("round 12: the angel watches the processor run", 32), ["round 12: the angel watches the", "processor run"]),
    (
        ("round 12: angle of the vector decides the match", 4),
        ["round", "12:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 12: angle of the vector decides the match", 8),
        ["round", "12:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 12: angle of the vector decides the match", 12),
        ["round 12:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 12: angle of the vector decides the match", 16),
        ["round 12: angle", "of the vector", "decides the", "match"],
    ),
    (("round 12: angle of the vector decides the match", 24), ["round 12: angle of the", "vector decides the match"]),
    (("round 12: angle of the vector decides the match", 32), ["round 12: angle of the vector", "decides the match"]),
    (
        ("round 12: the candle burns twice as long at night", 4),
        ["round", "12:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 12: the candle burns twice as long at night", 8),
        ["round", "12: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 12: the candle burns twice as long at night", 12),
        ["round 12:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 12: the candle burns twice as long at night", 16),
        ["round 12: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 12: the candle burns twice as long at night", 24),
        ["round 12: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 12: the candle burns twice as long at night", 32),
        ["round 12: the candle burns twice", "as long at night"],
    ),
    (
        ("round 12: a mirror of the universe in one line", 4),
        ["round", "12:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 12: a mirror of the universe in one line", 8),
        ["round", "12: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 12: a mirror of the universe in one line", 12),
        ["round 12: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 12: a mirror of the universe in one line", 16),
        ["round 12: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 12: a mirror of the universe in one line", 24), ["round 12: a mirror of", "the universe in one line"]),
    (("round 12: a mirror of the universe in one line", 32), ["round 12: a mirror of the", "universe in one line"]),
    (
        ("round 12: the queue drains before the storm", 4),
        ["round", "12:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 12: the queue drains before the storm", 8),
        ["round", "12: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 12: the queue drains before the storm", 12), ["round 12:", "the queue", "drains", "before the", "storm"]),
    (("round 12: the queue drains before the storm", 16), ["round 12: the", "queue drains", "before the storm"]),
    (("round 12: the queue drains before the storm", 24), ["round 12: the queue", "drains before the storm"]),
    (("round 12: the queue drains before the storm", 32), ["round 12: the queue drains", "before the storm"]),
    (
        ("kitten12 sitting12 agent12 angle12 universe12 memory12", 6),
        ["kitten12", "sitting12", "agent12", "angle12", "universe12", "memory12"],
    ),
    (
        ("kitten12 sitting12 agent12 angle12 universe12 memory12", 10),
        ["kitten12", "sitting12", "agent12", "angle12", "universe12", "memory12"],
    ),
    (
        ("kitten12 sitting12 agent12 angle12 universe12 memory12", 18),
        ["kitten12 sitting12", "agent12 angle12", "universe12", "memory12"],
    ),
    (
        ("kitten12 sitting12 agent12 angle12 universe12 memory12", 28),
        ["kitten12 sitting12 agent12", "angle12 universe12 memory12"],
    ),
    (
        ("sitting12 agent12 angle12 universe12 memory12 stream12", 6),
        ["sitting12", "agent12", "angle12", "universe12", "memory12", "stream12"],
    ),
    (
        ("sitting12 agent12 angle12 universe12 memory12 stream12", 10),
        ["sitting12", "agent12", "angle12", "universe12", "memory12", "stream12"],
    ),
    (
        ("sitting12 agent12 angle12 universe12 memory12 stream12", 18),
        ["sitting12 agent12", "angle12 universe12", "memory12 stream12"],
    ),
    (
        ("sitting12 agent12 angle12 universe12 memory12 stream12", 28),
        ["sitting12 agent12 angle12", "universe12 memory12 stream12"],
    ),
    (
        ("agent12 angle12 universe12 memory12 stream12 context12", 6),
        ["agent12", "angle12", "universe12", "memory12", "stream12", "context12"],
    ),
    (
        ("agent12 angle12 universe12 memory12 stream12 context12", 10),
        ["agent12", "angle12", "universe12", "memory12", "stream12", "context12"],
    ),
    (
        ("agent12 angle12 universe12 memory12 stream12 context12", 18),
        ["agent12 angle12", "universe12", "memory12 stream12", "context12"],
    ),
    (
        ("agent12 angle12 universe12 memory12 stream12 context12", 28),
        ["agent12 angle12 universe12", "memory12 stream12 context12"],
    ),
    (
        ("angle12 universe12 memory12 stream12 context12 knowledge12", 6),
        ["angle12", "universe12", "memory12", "stream12", "context12", "knowledge12"],
    ),
    (
        ("angle12 universe12 memory12 stream12 context12 knowledge12", 10),
        ["angle12", "universe12", "memory12", "stream12", "context12", "knowledge12"],
    ),
    (
        ("angle12 universe12 memory12 stream12 context12 knowledge12", 18),
        ["angle12 universe12", "memory12 stream12", "context12", "knowledge12"],
    ),
    (
        ("angle12 universe12 memory12 stream12 context12 knowledge12", 28),
        ["angle12 universe12 memory12", "stream12 context12", "knowledge12"],
    ),
    (
        ("universe12 memory12 stream12 context12 knowledge12 vector12", 6),
        ["universe12", "memory12", "stream12", "context12", "knowledge12", "vector12"],
    ),
    (
        ("universe12 memory12 stream12 context12 knowledge12 vector12", 10),
        ["universe12", "memory12", "stream12", "context12", "knowledge12", "vector12"],
    ),
    (
        ("universe12 memory12 stream12 context12 knowledge12 vector12", 18),
        ["universe12", "memory12 stream12", "context12", "knowledge12", "vector12"],
    ),
    (
        ("universe12 memory12 stream12 context12 knowledge12 vector12", 28),
        ["universe12 memory12 stream12", "context12 knowledge12", "vector12"],
    ),
    (
        ("memory12 stream12 context12 knowledge12 vector12 processor12", 6),
        ["memory12", "stream12", "context12", "knowledge12", "vector12", "processor12"],
    ),
    (
        ("memory12 stream12 context12 knowledge12 vector12 processor12", 10),
        ["memory12", "stream12", "context12", "knowledge12", "vector12", "processor12"],
    ),
    (
        ("memory12 stream12 context12 knowledge12 vector12 processor12", 18),
        ["memory12 stream12", "context12", "knowledge12", "vector12", "processor12"],
    ),
    (
        ("memory12 stream12 context12 knowledge12 vector12 processor12", 28),
        ["memory12 stream12 context12", "knowledge12 vector12", "processor12"],
    ),
    (
        ("stream12 context12 knowledge12 vector12 processor12 reasoning12", 6),
        ["stream12", "context12", "knowledge12", "vector12", "processor12", "reasoning12"],
    ),
    (
        ("stream12 context12 knowledge12 vector12 processor12 reasoning12", 10),
        ["stream12", "context12", "knowledge12", "vector12", "processor12", "reasoning12"],
    ),
    (
        ("stream12 context12 knowledge12 vector12 processor12 reasoning12", 18),
        ["stream12 context12", "knowledge12", "vector12", "processor12", "reasoning12"],
    ),
    (
        ("stream12 context12 knowledge12 vector12 processor12 reasoning12", 28),
        ["stream12 context12", "knowledge12 vector12", "processor12 reasoning12"],
    ),
    (
        ("context12 knowledge12 vector12 processor12 reasoning12 machine12", 6),
        ["context12", "knowledge12", "vector12", "processor12", "reasoning12", "machine12"],
    ),
    (
        ("context12 knowledge12 vector12 processor12 reasoning12 machine12", 10),
        ["context12", "knowledge12", "vector12", "processor12", "reasoning12", "machine12"],
    ),
    (
        ("context12 knowledge12 vector12 processor12 reasoning12 machine12", 18),
        ["context12", "knowledge12", "vector12", "processor12", "reasoning12", "machine12"],
    ),
    (
        ("context12 knowledge12 vector12 processor12 reasoning12 machine12", 28),
        ["context12 knowledge12", "vector12 processor12", "reasoning12 machine12"],
    ),
    (
        ("knowledge12 vector12 processor12 reasoning12 machine12 learning12", 6),
        ["knowledge12", "vector12", "processor12", "reasoning12", "machine12", "learning12"],
    ),
    (
        ("knowledge12 vector12 processor12 reasoning12 machine12 learning12", 10),
        ["knowledge12", "vector12", "processor12", "reasoning12", "machine12", "learning12"],
    ),
    (
        ("knowledge12 vector12 processor12 reasoning12 machine12 learning12", 18),
        ["knowledge12", "vector12", "processor12", "reasoning12", "machine12", "learning12"],
    ),
    (
        ("knowledge12 vector12 processor12 reasoning12 machine12 learning12", 28),
        ["knowledge12 vector12", "processor12 reasoning12", "machine12 learning12"],
    ),
    (
        ("vector12 processor12 reasoning12 machine12 learning12 model12", 6),
        ["vector12", "processor12", "reasoning12", "machine12", "learning12", "model12"],
    ),
    (
        ("vector12 processor12 reasoning12 machine12 learning12 model12", 10),
        ["vector12", "processor12", "reasoning12", "machine12", "learning12", "model12"],
    ),
    (
        ("vector12 processor12 reasoning12 machine12 learning12 model12", 18),
        ["vector12", "processor12", "reasoning12", "machine12", "learning12 model12"],
    ),
    (
        ("vector12 processor12 reasoning12 machine12 learning12 model12", 28),
        ["vector12 processor12", "reasoning12 machine12", "learning12 model12"],
    ),
    (
        ("processor12 reasoning12 machine12 learning12 model12 token12", 6),
        ["processor12", "reasoning12", "machine12", "learning12", "model12", "token12"],
    ),
    (
        ("processor12 reasoning12 machine12 learning12 model12 token12", 10),
        ["processor12", "reasoning12", "machine12", "learning12", "model12", "token12"],
    ),
    (
        ("processor12 reasoning12 machine12 learning12 model12 token12", 18),
        ["processor12", "reasoning12", "machine12", "learning12 model12", "token12"],
    ),
    (
        ("processor12 reasoning12 machine12 learning12 model12 token12", 28),
        ["processor12 reasoning12", "machine12 learning12 model12", "token12"],
    ),
    (
        ("reasoning12 machine12 learning12 model12 token12 prompt12", 6),
        ["reasoning12", "machine12", "learning12", "model12", "token12", "prompt12"],
    ),
    (
        ("reasoning12 machine12 learning12 model12 token12 prompt12", 10),
        ["reasoning12", "machine12", "learning12", "model12", "token12", "prompt12"],
    ),
    (
        ("reasoning12 machine12 learning12 model12 token12 prompt12", 18),
        ["reasoning12", "machine12", "learning12 model12", "token12 prompt12"],
    ),
    (
        ("reasoning12 machine12 learning12 model12 token12 prompt12", 28),
        ["reasoning12 machine12", "learning12 model12 token12", "prompt12"],
    ),
    (
        ("machine12 learning12 model12 token12 prompt12 session12", 6),
        ["machine12", "learning12", "model12", "token12", "prompt12", "session12"],
    ),
    (
        ("machine12 learning12 model12 token12 prompt12 session12", 10),
        ["machine12", "learning12", "model12", "token12", "prompt12", "session12"],
    ),
    (
        ("machine12 learning12 model12 token12 prompt12 session12", 18),
        ["machine12", "learning12 model12", "token12 prompt12", "session12"],
    ),
    (
        ("machine12 learning12 model12 token12 prompt12 session12", 28),
        ["machine12 learning12 model12", "token12 prompt12 session12"],
    ),
    (
        ("learning12 model12 token12 prompt12 session12 library12", 6),
        ["learning12", "model12", "token12", "prompt12", "session12", "library12"],
    ),
    (
        ("learning12 model12 token12 prompt12 session12 library12", 10),
        ["learning12", "model12", "token12", "prompt12", "session12", "library12"],
    ),
    (
        ("learning12 model12 token12 prompt12 session12 library12", 18),
        ["learning12 model12", "token12 prompt12", "session12", "library12"],
    ),
    (
        ("learning12 model12 token12 prompt12 session12 library12", 28),
        ["learning12 model12 token12", "prompt12 session12 library12"],
    ),
    (
        ("model12 token12 prompt12 session12 library12 service12", 6),
        ["model12", "token12", "prompt12", "session12", "library12", "service12"],
    ),
    (
        ("model12 token12 prompt12 session12 library12 service12", 10),
        ["model12", "token12", "prompt12", "session12", "library12", "service12"],
    ),
    (
        ("model12 token12 prompt12 session12 library12 service12", 18),
        ["model12 token12", "prompt12 session12", "library12", "service12"],
    ),
    (
        ("model12 token12 prompt12 session12 library12 service12", 28),
        ["model12 token12 prompt12", "session12 library12", "service12"],
    ),
    (
        ("token12 prompt12 session12 library12 service12 gateway12", 6),
        ["token12", "prompt12", "session12", "library12", "service12", "gateway12"],
    ),
    (
        ("token12 prompt12 session12 library12 service12 gateway12", 10),
        ["token12", "prompt12", "session12", "library12", "service12", "gateway12"],
    ),
    (
        ("token12 prompt12 session12 library12 service12 gateway12", 18),
        ["token12 prompt12", "session12", "library12", "service12", "gateway12"],
    ),
    (
        ("token12 prompt12 session12 library12 service12 gateway12", 28),
        ["token12 prompt12 session12", "library12 service12", "gateway12"],
    ),
    (
        ("prompt12 session12 library12 service12 gateway12 storage12", 6),
        ["prompt12", "session12", "library12", "service12", "gateway12", "storage12"],
    ),
    (
        ("prompt12 session12 library12 service12 gateway12 storage12", 10),
        ["prompt12", "session12", "library12", "service12", "gateway12", "storage12"],
    ),
    (
        ("prompt12 session12 library12 service12 gateway12 storage12", 18),
        ["prompt12 session12", "library12", "service12", "gateway12", "storage12"],
    ),
    (
        ("prompt12 session12 library12 service12 gateway12 storage12", 28),
        ["prompt12 session12 library12", "service12 gateway12", "storage12"],
    ),
    (
        ("session12 library12 service12 gateway12 storage12 network12", 6),
        ["session12", "library12", "service12", "gateway12", "storage12", "network12"],
    ),
    (
        ("session12 library12 service12 gateway12 storage12 network12", 10),
        ["session12", "library12", "service12", "gateway12", "storage12", "network12"],
    ),
    (
        ("session12 library12 service12 gateway12 storage12 network12", 18),
        ["session12", "library12", "service12", "gateway12", "storage12", "network12"],
    ),
    (
        ("session12 library12 service12 gateway12 storage12 network12", 28),
        ["session12 library12", "service12 gateway12", "storage12 network12"],
    ),
    (
        ("library12 service12 gateway12 storage12 network12 latency12", 6),
        ["library12", "service12", "gateway12", "storage12", "network12", "latency12"],
    ),
    (
        ("library12 service12 gateway12 storage12 network12 latency12", 10),
        ["library12", "service12", "gateway12", "storage12", "network12", "latency12"],
    ),
    (
        ("library12 service12 gateway12 storage12 network12 latency12", 18),
        ["library12", "service12", "gateway12", "storage12", "network12", "latency12"],
    ),
    (
        ("library12 service12 gateway12 storage12 network12 latency12", 28),
        ["library12 service12", "gateway12 storage12", "network12 latency12"],
    ),
    (
        ("service12 gateway12 storage12 network12 latency12 buffer12", 6),
        ["service12", "gateway12", "storage12", "network12", "latency12", "buffer12"],
    ),
    (
        ("service12 gateway12 storage12 network12 latency12 buffer12", 10),
        ["service12", "gateway12", "storage12", "network12", "latency12", "buffer12"],
    ),
    (
        ("service12 gateway12 storage12 network12 latency12 buffer12", 18),
        ["service12", "gateway12", "storage12", "network12", "latency12 buffer12"],
    ),
    (
        ("service12 gateway12 storage12 network12 latency12 buffer12", 28),
        ["service12 gateway12", "storage12 network12", "latency12 buffer12"],
    ),
    (
        ("gateway12 storage12 network12 latency12 buffer12 queue12", 6),
        ["gateway12", "storage12", "network12", "latency12", "buffer12", "queue12"],
    ),
    (
        ("gateway12 storage12 network12 latency12 buffer12 queue12", 10),
        ["gateway12", "storage12", "network12", "latency12", "buffer12", "queue12"],
    ),
    (
        ("gateway12 storage12 network12 latency12 buffer12 queue12", 18),
        ["gateway12", "storage12", "network12", "latency12 buffer12", "queue12"],
    ),
    (
        ("gateway12 storage12 network12 latency12 buffer12 queue12", 28),
        ["gateway12 storage12", "network12 latency12 buffer12", "queue12"],
    ),
    (
        ("storage12 network12 latency12 buffer12 queue12 worker12", 6),
        ["storage12", "network12", "latency12", "buffer12", "queue12", "worker12"],
    ),
    (
        ("storage12 network12 latency12 buffer12 queue12 worker12", 10),
        ["storage12", "network12", "latency12", "buffer12", "queue12", "worker12"],
    ),
    (
        ("storage12 network12 latency12 buffer12 queue12 worker12", 18),
        ["storage12", "network12", "latency12 buffer12", "queue12 worker12"],
    ),
    (
        ("storage12 network12 latency12 buffer12 queue12 worker12", 28),
        ["storage12 network12", "latency12 buffer12 queue12", "worker12"],
    ),
    (
        ("network12 latency12 buffer12 queue12 worker12 kernel12", 6),
        ["network12", "latency12", "buffer12", "queue12", "worker12", "kernel12"],
    ),
    (
        ("network12 latency12 buffer12 queue12 worker12 kernel12", 10),
        ["network12", "latency12", "buffer12", "queue12", "worker12", "kernel12"],
    ),
    (
        ("network12 latency12 buffer12 queue12 worker12 kernel12", 18),
        ["network12", "latency12 buffer12", "queue12 worker12", "kernel12"],
    ),
    (
        ("network12 latency12 buffer12 queue12 worker12 kernel12", 28),
        ["network12 latency12 buffer12", "queue12 worker12 kernel12"],
    ),
    (
        ("latency12 buffer12 queue12 worker12 kernel12 signal12", 6),
        ["latency12", "buffer12", "queue12", "worker12", "kernel12", "signal12"],
    ),
    (
        ("latency12 buffer12 queue12 worker12 kernel12 signal12", 10),
        ["latency12", "buffer12", "queue12", "worker12", "kernel12", "signal12"],
    ),
    (
        ("latency12 buffer12 queue12 worker12 kernel12 signal12", 18),
        ["latency12 buffer12", "queue12 worker12", "kernel12 signal12"],
    ),
    (
        ("latency12 buffer12 queue12 worker12 kernel12 signal12", 28),
        ["latency12 buffer12 queue12", "worker12 kernel12 signal12"],
    ),
    (
        ("buffer12 queue12 worker12 kernel12 signal12 packet12", 6),
        ["buffer12", "queue12", "worker12", "kernel12", "signal12", "packet12"],
    ),
    (
        ("buffer12 queue12 worker12 kernel12 signal12 packet12", 10),
        ["buffer12", "queue12", "worker12", "kernel12", "signal12", "packet12"],
    ),
    (
        ("buffer12 queue12 worker12 kernel12 signal12 packet12", 18),
        ["buffer12 queue12", "worker12 kernel12", "signal12 packet12"],
    ),
    (
        ("buffer12 queue12 worker12 kernel12 signal12 packet12", 28),
        ["buffer12 queue12 worker12", "kernel12 signal12 packet12"],
    ),
    (
        ("queue12 worker12 kernel12 signal12 packet12 router12", 6),
        ["queue12", "worker12", "kernel12", "signal12", "packet12", "router12"],
    ),
    (
        ("queue12 worker12 kernel12 signal12 packet12 router12", 10),
        ["queue12", "worker12", "kernel12", "signal12", "packet12", "router12"],
    ),
    (
        ("queue12 worker12 kernel12 signal12 packet12 router12", 18),
        ["queue12 worker12", "kernel12 signal12", "packet12 router12"],
    ),
    (
        ("queue12 worker12 kernel12 signal12 packet12 router12", 28),
        ["queue12 worker12 kernel12", "signal12 packet12 router12"],
    ),
    (
        ("worker12 kernel12 signal12 packet12 router12 cluster12", 6),
        ["worker12", "kernel12", "signal12", "packet12", "router12", "cluster12"],
    ),
    (
        ("worker12 kernel12 signal12 packet12 router12 cluster12", 10),
        ["worker12", "kernel12", "signal12", "packet12", "router12", "cluster12"],
    ),
    (
        ("worker12 kernel12 signal12 packet12 router12 cluster12", 18),
        ["worker12 kernel12", "signal12 packet12", "router12 cluster12"],
    ),
    (
        ("worker12 kernel12 signal12 packet12 router12 cluster12", 28),
        ["worker12 kernel12 signal12", "packet12 router12 cluster12"],
    ),
    (
        ("kernel12 signal12 packet12 router12 cluster12 mirror12", 6),
        ["kernel12", "signal12", "packet12", "router12", "cluster12", "mirror12"],
    ),
    (
        ("kernel12 signal12 packet12 router12 cluster12 mirror12", 10),
        ["kernel12", "signal12", "packet12", "router12", "cluster12", "mirror12"],
    ),
    (
        ("kernel12 signal12 packet12 router12 cluster12 mirror12", 18),
        ["kernel12 signal12", "packet12 router12", "cluster12 mirror12"],
    ),
    (
        ("kernel12 signal12 packet12 router12 cluster12 mirror12", 28),
        ["kernel12 signal12 packet12", "router12 cluster12 mirror12"],
    ),
    (
        ("signal12 packet12 router12 cluster12 mirror12 filter12", 6),
        ["signal12", "packet12", "router12", "cluster12", "mirror12", "filter12"],
    ),
    (
        ("signal12 packet12 router12 cluster12 mirror12 filter12", 10),
        ["signal12", "packet12", "router12", "cluster12", "mirror12", "filter12"],
    ),
    (
        ("signal12 packet12 router12 cluster12 mirror12 filter12", 18),
        ["signal12 packet12", "router12 cluster12", "mirror12 filter12"],
    ),
    (
        ("signal12 packet12 router12 cluster12 mirror12 filter12", 28),
        ["signal12 packet12 router12", "cluster12 mirror12 filter12"],
    ),
    (
        ("packet12 router12 cluster12 mirror12 filter12 ranking12", 6),
        ["packet12", "router12", "cluster12", "mirror12", "filter12", "ranking12"],
    ),
    (
        ("packet12 router12 cluster12 mirror12 filter12 ranking12", 10),
        ["packet12", "router12", "cluster12", "mirror12", "filter12", "ranking12"],
    ),
    (
        ("packet12 router12 cluster12 mirror12 filter12 ranking12", 18),
        ["packet12 router12", "cluster12 mirror12", "filter12 ranking12"],
    ),
    (
        ("packet12 router12 cluster12 mirror12 filter12 ranking12", 28),
        ["packet12 router12 cluster12", "mirror12 filter12 ranking12"],
    ),
    (
        ("router12 cluster12 mirror12 filter12 ranking12 encoding12", 6),
        ["router12", "cluster12", "mirror12", "filter12", "ranking12", "encoding12"],
    ),
    (
        ("router12 cluster12 mirror12 filter12 ranking12 encoding12", 10),
        ["router12", "cluster12", "mirror12", "filter12", "ranking12", "encoding12"],
    ),
    (
        ("router12 cluster12 mirror12 filter12 ranking12 encoding12", 18),
        ["router12 cluster12", "mirror12 filter12", "ranking12", "encoding12"],
    ),
    (
        ("router12 cluster12 mirror12 filter12 ranking12 encoding12", 28),
        ["router12 cluster12 mirror12", "filter12 ranking12", "encoding12"],
    ),
    (
        ("cluster12 mirror12 filter12 ranking12 encoding12 mapping12", 6),
        ["cluster12", "mirror12", "filter12", "ranking12", "encoding12", "mapping12"],
    ),
    (
        ("cluster12 mirror12 filter12 ranking12 encoding12 mapping12", 10),
        ["cluster12", "mirror12", "filter12", "ranking12", "encoding12", "mapping12"],
    ),
    (
        ("cluster12 mirror12 filter12 ranking12 encoding12 mapping12", 18),
        ["cluster12 mirror12", "filter12 ranking12", "encoding12", "mapping12"],
    ),
    (
        ("cluster12 mirror12 filter12 ranking12 encoding12 mapping12", 28),
        ["cluster12 mirror12 filter12", "ranking12 encoding12", "mapping12"],
    ),
    (
        ("mirror12 filter12 ranking12 encoding12 mapping12 record12", 6),
        ["mirror12", "filter12", "ranking12", "encoding12", "mapping12", "record12"],
    ),
    (
        ("mirror12 filter12 ranking12 encoding12 mapping12 record12", 10),
        ["mirror12", "filter12", "ranking12", "encoding12", "mapping12", "record12"],
    ),
    (
        ("mirror12 filter12 ranking12 encoding12 mapping12 record12", 18),
        ["mirror12 filter12", "ranking12", "encoding12", "mapping12 record12"],
    ),
    (
        ("mirror12 filter12 ranking12 encoding12 mapping12 record12", 28),
        ["mirror12 filter12 ranking12", "encoding12 mapping12", "record12"],
    ),
    (
        ("filter12 ranking12 encoding12 mapping12 record12 candle12", 6),
        ["filter12", "ranking12", "encoding12", "mapping12", "record12", "candle12"],
    ),
    (
        ("filter12 ranking12 encoding12 mapping12 record12 candle12", 10),
        ["filter12", "ranking12", "encoding12", "mapping12", "record12", "candle12"],
    ),
    (
        ("filter12 ranking12 encoding12 mapping12 record12 candle12", 18),
        ["filter12 ranking12", "encoding12", "mapping12 record12", "candle12"],
    ),
    (
        ("filter12 ranking12 encoding12 mapping12 record12 candle12", 28),
        ["filter12 ranking12", "encoding12 mapping12", "record12 candle12"],
    ),
    (
        ("ranking12 encoding12 mapping12 record12 candle12 thread12", 6),
        ["ranking12", "encoding12", "mapping12", "record12", "candle12", "thread12"],
    ),
    (
        ("ranking12 encoding12 mapping12 record12 candle12 thread12", 10),
        ["ranking12", "encoding12", "mapping12", "record12", "candle12", "thread12"],
    ),
    (
        ("ranking12 encoding12 mapping12 record12 candle12 thread12", 18),
        ["ranking12", "encoding12", "mapping12 record12", "candle12 thread12"],
    ),
    (
        ("ranking12 encoding12 mapping12 record12 candle12 thread12", 28),
        ["ranking12 encoding12", "mapping12 record12 candle12", "thread12"],
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
