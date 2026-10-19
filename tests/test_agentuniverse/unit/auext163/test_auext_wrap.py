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
        ("round 163: the quick brown fox jumps over the lazy dog", 4),
        ["round", "163:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 163: the quick brown fox jumps over the lazy dog", 8),
        ["round", "163: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 163: the quick brown fox jumps over the lazy dog", 12),
        ["round 163:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 163: the quick brown fox jumps over the lazy dog", 16),
        ["round 163: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 163: the quick brown fox jumps over the lazy dog", 24),
        ["round 163: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 163: the quick brown fox jumps over the lazy dog", 32),
        ["round 163: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 163: agentuniverse is a framework for multi agents", 4),
        ["round", "163:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 163: agentuniverse is a framework for multi agents", 8),
        ["round", "163:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 163: agentuniverse is a framework for multi agents", 12),
        ["round 163:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 163: agentuniverse is a framework for multi agents", 16),
        ["round 163:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 163: agentuniverse is a framework for multi agents", 24),
        ["round 163: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 163: agentuniverse is a framework for multi agents", 32),
        ["round 163: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 163: knowledge stored as vectors enables retrieval", 4),
        ["round", "163:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 163: knowledge stored as vectors enables retrieval", 8),
        ["round", "163:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 163: knowledge stored as vectors enables retrieval", 12),
        ["round 163:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 163: knowledge stored as vectors enables retrieval", 16),
        ["round 163:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 163: knowledge stored as vectors enables retrieval", 24),
        ["round 163: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 163: knowledge stored as vectors enables retrieval", 32),
        ["round 163: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 163: the processor reads the record then stops", 4),
        ["round", "163:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 163: the processor reads the record then stops", 8),
        ["round", "163: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 163: the processor reads the record then stops", 12),
        ["round 163:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 163: the processor reads the record then stops", 16),
        ["round 163: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 163: the processor reads the record then stops", 24),
        ["round 163: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 163: the processor reads the record then stops", 32),
        ["round 163: the processor reads", "the record then stops"],
    ),
    (
        ("round 163: a worker pulls the next task from the queue", 4),
        ["round", "163:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 163: a worker pulls the next task from the queue", 8),
        ["round", "163: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 163: a worker pulls the next task from the queue", 12),
        ["round 163: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 163: a worker pulls the next task from the queue", 16),
        ["round 163: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 163: a worker pulls the next task from the queue", 24),
        ["round 163: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 163: a worker pulls the next task from the queue", 32),
        ["round 163: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 163: signals travel through the network layer", 4),
        ["round", "163:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 163: signals travel through the network layer", 8),
        ["round", "163:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 163: signals travel through the network layer", 12),
        ["round 163:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 163: signals travel through the network layer", 16),
        ["round 163:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 163: signals travel through the network layer", 24),
        ["round 163: signals", "travel through the", "network layer"],
    ),
    (
        ("round 163: signals travel through the network layer", 32),
        ["round 163: signals travel", "through the network layer"],
    ),
    (
        ("round 163: the gateway routes each request by policy", 4),
        ["round", "163:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 163: the gateway routes each request by policy", 8),
        ["round", "163: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 163: the gateway routes each request by policy", 12),
        ["round 163:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 163: the gateway routes each request by policy", 16),
        ["round 163: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 163: the gateway routes each request by policy", 24),
        ["round 163: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 163: the gateway routes each request by policy", 32),
        ["round 163: the gateway routes", "each request by policy"],
    ),
    (
        ("round 163: memory grows until the buffer is full", 4),
        ["round", "163:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 163: memory grows until the buffer is full", 8),
        ["round", "163:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 163: memory grows until the buffer is full", 12),
        ["round 163:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 163: memory grows until the buffer is full", 16),
        ["round 163:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 163: memory grows until the buffer is full", 24), ["round 163: memory grows", "until the buffer is full"]),
    (("round 163: memory grows until the buffer is full", 32), ["round 163: memory grows until", "the buffer is full"]),
    (
        ("round 163: the cluster mirrors every packet twice", 4),
        ["round", "163:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 163: the cluster mirrors every packet twice", 8),
        ["round", "163: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 163: the cluster mirrors every packet twice", 12),
        ["round 163:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 163: the cluster mirrors every packet twice", 16),
        ["round 163: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 163: the cluster mirrors every packet twice", 24),
        ["round 163: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 163: the cluster mirrors every packet twice", 32),
        ["round 163: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 163: ranking uses tokens learned from the corpus", 4),
        ["round", "163:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 163: ranking uses tokens learned from the corpus", 8),
        ["round", "163:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 163: ranking uses tokens learned from the corpus", 12),
        ["round 163:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 163: ranking uses tokens learned from the corpus", 16),
        ["round 163:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 163: ranking uses tokens learned from the corpus", 24),
        ["round 163: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 163: ranking uses tokens learned from the corpus", 32),
        ["round 163: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 163: a long session ends when the candle dies", 4),
        ["round", "163:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 163: a long session ends when the candle dies", 8),
        ["round", "163: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 163: a long session ends when the candle dies", 12),
        ["round 163: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 163: a long session ends when the candle dies", 16),
        ["round 163: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 163: a long session ends when the candle dies", 24),
        ["round 163: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 163: a long session ends when the candle dies", 32),
        ["round 163: a long session ends", "when the candle dies"],
    ),
    (
        ("round 163: encode the prompt then map the result", 4),
        ["round", "163:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 163: encode the prompt then map the result", 8),
        ["round", "163:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 163: encode the prompt then map the result", 12),
        ["round 163:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 163: encode the prompt then map the result", 16),
        ["round 163:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 163: encode the prompt then map the result", 24),
        ["round 163: encode the", "prompt then map the", "result"],
    ),
    (("round 163: encode the prompt then map the result", 32), ["round 163: encode the prompt", "then map the result"]),
    (
        ("round 163: the kernel wakes the worker at dawn", 4),
        ["round", "163:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 163: the kernel wakes the worker at dawn", 8),
        ["round", "163: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 163: the kernel wakes the worker at dawn", 12),
        ["round 163:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 163: the kernel wakes the worker at dawn", 16), ["round 163: the", "kernel wakes the", "worker at dawn"]),
    (("round 163: the kernel wakes the worker at dawn", 24), ["round 163: the kernel", "wakes the worker at dawn"]),
    (("round 163: the kernel wakes the worker at dawn", 32), ["round 163: the kernel wakes the", "worker at dawn"]),
    (
        ("round 163: service latency drops after the patch", 4),
        ["round", "163:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 163: service latency drops after the patch", 8),
        ["round", "163:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 163: service latency drops after the patch", 12),
        ["round 163:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 163: service latency drops after the patch", 16),
        ["round 163:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 163: service latency drops after the patch", 24),
        ["round 163: service", "latency drops after the", "patch"],
    ),
    (("round 163: service latency drops after the patch", 32), ["round 163: service latency drops", "after the patch"]),
    (
        ("round 163: the library caches every vector it sees", 4),
        ["round", "163:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 163: the library caches every vector it sees", 8),
        ["round", "163: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 163: the library caches every vector it sees", 12),
        ["round 163:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 163: the library caches every vector it sees", 16),
        ["round 163: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 163: the library caches every vector it sees", 24),
        ["round 163: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 163: the library caches every vector it sees", 32),
        ["round 163: the library caches", "every vector it sees"],
    ),
    (
        ("round 163: agents argue then the debate resolves", 4),
        ["round", "163:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 163: agents argue then the debate resolves", 8),
        ["round", "163:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 163: agents argue then the debate resolves", 12),
        ["round 163:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 163: agents argue then the debate resolves", 16),
        ["round 163:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 163: agents argue then the debate resolves", 24), ["round 163: agents argue", "then the debate resolves"]),
    (("round 163: agents argue then the debate resolves", 32), ["round 163: agents argue then the", "debate resolves"]),
    (
        ("round 163: the filter keeps only strong matches", 4),
        ["round", "163:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 163: the filter keeps only strong matches", 8),
        ["round", "163: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 163: the filter keeps only strong matches", 12),
        ["round 163:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 163: the filter keeps only strong matches", 16),
        ["round 163: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 163: the filter keeps only strong matches", 24),
        ["round 163: the filter", "keeps only strong", "matches"],
    ),
    (("round 163: the filter keeps only strong matches", 32), ["round 163: the filter keeps only", "strong matches"]),
    (
        ("round 163: the model answers with a short reply", 4),
        ["round", "163:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 163: the model answers with a short reply", 8),
        ["round", "163: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 163: the model answers with a short reply", 12),
        ["round 163:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 163: the model answers with a short reply", 16),
        ["round 163: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 163: the model answers with a short reply", 24),
        ["round 163: the model", "answers with a short", "reply"],
    ),
    (("round 163: the model answers with a short reply", 32), ["round 163: the model answers", "with a short reply"]),
    (
        ("round 163: the recorder stores the reasoning trace", 4),
        ["round", "163:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 163: the recorder stores the reasoning trace", 8),
        ["round", "163: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 163: the recorder stores the reasoning trace", 12),
        ["round 163:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 163: the recorder stores the reasoning trace", 16),
        ["round 163: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 163: the recorder stores the reasoning trace", 24),
        ["round 163: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 163: the recorder stores the reasoning trace", 32),
        ["round 163: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 163: the angel watches the processor run", 4),
        ["round", "163:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 163: the angel watches the processor run", 8),
        ["round", "163: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 163: the angel watches the processor run", 12),
        ["round 163:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 163: the angel watches the processor run", 16),
        ["round 163: the", "angel watches", "the processor", "run"],
    ),
    (("round 163: the angel watches the processor run", 24), ["round 163: the angel", "watches the processor", "run"]),
    (("round 163: the angel watches the processor run", 32), ["round 163: the angel watches the", "processor run"]),
    (
        ("round 163: angle of the vector decides the match", 4),
        ["round", "163:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 163: angle of the vector decides the match", 8),
        ["round", "163:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 163: angle of the vector decides the match", 12),
        ["round 163:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 163: angle of the vector decides the match", 16),
        ["round 163: angle", "of the vector", "decides the", "match"],
    ),
    (("round 163: angle of the vector decides the match", 24), ["round 163: angle of the", "vector decides the match"]),
    (("round 163: angle of the vector decides the match", 32), ["round 163: angle of the vector", "decides the match"]),
    (
        ("round 163: the candle burns twice as long at night", 4),
        ["round", "163:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 163: the candle burns twice as long at night", 8),
        ["round", "163: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 163: the candle burns twice as long at night", 12),
        ["round 163:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 163: the candle burns twice as long at night", 16),
        ["round 163: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 163: the candle burns twice as long at night", 24),
        ["round 163: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 163: the candle burns twice as long at night", 32),
        ["round 163: the candle burns", "twice as long at night"],
    ),
    (
        ("round 163: a mirror of the universe in one line", 4),
        ["round", "163:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 163: a mirror of the universe in one line", 8),
        ["round", "163: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 163: a mirror of the universe in one line", 12),
        ["round 163: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 163: a mirror of the universe in one line", 16),
        ["round 163: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 163: a mirror of the universe in one line", 24), ["round 163: a mirror of", "the universe in one line"]),
    (("round 163: a mirror of the universe in one line", 32), ["round 163: a mirror of the", "universe in one line"]),
    (
        ("round 163: the queue drains before the storm", 4),
        ["round", "163:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 163: the queue drains before the storm", 8),
        ["round", "163: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 163: the queue drains before the storm", 12),
        ["round 163:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 163: the queue drains before the storm", 16), ["round 163: the", "queue drains", "before the storm"]),
    (("round 163: the queue drains before the storm", 24), ["round 163: the queue", "drains before the storm"]),
    (("round 163: the queue drains before the storm", 32), ["round 163: the queue drains", "before the storm"]),
    (
        ("kitten163 sitting163 agent163 angle163 universe163 memory163", 6),
        ["kitten163", "sitting163", "agent163", "angle163", "universe163", "memory163"],
    ),
    (
        ("kitten163 sitting163 agent163 angle163 universe163 memory163", 10),
        ["kitten163", "sitting163", "agent163", "angle163", "universe163", "memory163"],
    ),
    (
        ("kitten163 sitting163 agent163 angle163 universe163 memory163", 18),
        ["kitten163", "sitting163", "agent163 angle163", "universe163", "memory163"],
    ),
    (
        ("kitten163 sitting163 agent163 angle163 universe163 memory163", 28),
        ["kitten163 sitting163", "agent163 angle163", "universe163 memory163"],
    ),
    (
        ("sitting163 agent163 angle163 universe163 memory163 stream163", 6),
        ["sitting163", "agent163", "angle163", "universe163", "memory163", "stream163"],
    ),
    (
        ("sitting163 agent163 angle163 universe163 memory163 stream163", 10),
        ["sitting163", "agent163", "angle163", "universe163", "memory163", "stream163"],
    ),
    (
        ("sitting163 agent163 angle163 universe163 memory163 stream163", 18),
        ["sitting163", "agent163 angle163", "universe163", "memory163", "stream163"],
    ),
    (
        ("sitting163 agent163 angle163 universe163 memory163 stream163", 28),
        ["sitting163 agent163 angle163", "universe163 memory163", "stream163"],
    ),
    (
        ("agent163 angle163 universe163 memory163 stream163 context163", 6),
        ["agent163", "angle163", "universe163", "memory163", "stream163", "context163"],
    ),
    (
        ("agent163 angle163 universe163 memory163 stream163 context163", 10),
        ["agent163", "angle163", "universe163", "memory163", "stream163", "context163"],
    ),
    (
        ("agent163 angle163 universe163 memory163 stream163 context163", 18),
        ["agent163 angle163", "universe163", "memory163", "stream163", "context163"],
    ),
    (
        ("agent163 angle163 universe163 memory163 stream163 context163", 28),
        ["agent163 angle163", "universe163 memory163", "stream163 context163"],
    ),
    (
        ("angle163 universe163 memory163 stream163 context163 knowledge163", 6),
        ["angle163", "universe163", "memory163", "stream163", "context163", "knowledge163"],
    ),
    (
        ("angle163 universe163 memory163 stream163 context163 knowledge163", 10),
        ["angle163", "universe163", "memory163", "stream163", "context163", "knowledge163"],
    ),
    (
        ("angle163 universe163 memory163 stream163 context163 knowledge163", 18),
        ["angle163", "universe163", "memory163", "stream163", "context163", "knowledge163"],
    ),
    (
        ("angle163 universe163 memory163 stream163 context163 knowledge163", 28),
        ["angle163 universe163", "memory163 stream163", "context163 knowledge163"],
    ),
    (
        ("universe163 memory163 stream163 context163 knowledge163 vector163", 6),
        ["universe163", "memory163", "stream163", "context163", "knowledge163", "vector163"],
    ),
    (
        ("universe163 memory163 stream163 context163 knowledge163 vector163", 10),
        ["universe163", "memory163", "stream163", "context163", "knowledge163", "vector163"],
    ),
    (
        ("universe163 memory163 stream163 context163 knowledge163 vector163", 18),
        ["universe163", "memory163", "stream163", "context163", "knowledge163", "vector163"],
    ),
    (
        ("universe163 memory163 stream163 context163 knowledge163 vector163", 28),
        ["universe163 memory163", "stream163 context163", "knowledge163 vector163"],
    ),
    (
        ("memory163 stream163 context163 knowledge163 vector163 processor163", 6),
        ["memory163", "stream163", "context163", "knowledge163", "vector163", "processor163"],
    ),
    (
        ("memory163 stream163 context163 knowledge163 vector163 processor163", 10),
        ["memory163", "stream163", "context163", "knowledge163", "vector163", "processor163"],
    ),
    (
        ("memory163 stream163 context163 knowledge163 vector163 processor163", 18),
        ["memory163", "stream163", "context163", "knowledge163", "vector163", "processor163"],
    ),
    (
        ("memory163 stream163 context163 knowledge163 vector163 processor163", 28),
        ["memory163 stream163", "context163 knowledge163", "vector163 processor163"],
    ),
    (
        ("stream163 context163 knowledge163 vector163 processor163 reasoning163", 6),
        ["stream163", "context163", "knowledge163", "vector163", "processor163", "reasoning163"],
    ),
    (
        ("stream163 context163 knowledge163 vector163 processor163 reasoning163", 10),
        ["stream163", "context163", "knowledge163", "vector163", "processor163", "reasoning163"],
    ),
    (
        ("stream163 context163 knowledge163 vector163 processor163 reasoning163", 18),
        ["stream163", "context163", "knowledge163", "vector163", "processor163", "reasoning163"],
    ),
    (
        ("stream163 context163 knowledge163 vector163 processor163 reasoning163", 28),
        ["stream163 context163", "knowledge163 vector163", "processor163 reasoning163"],
    ),
    (
        ("context163 knowledge163 vector163 processor163 reasoning163 machine163", 6),
        ["context163", "knowledge163", "vector163", "processor163", "reasoning163", "machine163"],
    ),
    (
        ("context163 knowledge163 vector163 processor163 reasoning163 machine163", 10),
        ["context163", "knowledge163", "vector163", "processor163", "reasoning163", "machine163"],
    ),
    (
        ("context163 knowledge163 vector163 processor163 reasoning163 machine163", 18),
        ["context163", "knowledge163", "vector163", "processor163", "reasoning163", "machine163"],
    ),
    (
        ("context163 knowledge163 vector163 processor163 reasoning163 machine163", 28),
        ["context163 knowledge163", "vector163 processor163", "reasoning163 machine163"],
    ),
    (
        ("knowledge163 vector163 processor163 reasoning163 machine163 learning163", 6),
        ["knowledge163", "vector163", "processor163", "reasoning163", "machine163", "learning163"],
    ),
    (
        ("knowledge163 vector163 processor163 reasoning163 machine163 learning163", 10),
        ["knowledge163", "vector163", "processor163", "reasoning163", "machine163", "learning163"],
    ),
    (
        ("knowledge163 vector163 processor163 reasoning163 machine163 learning163", 18),
        ["knowledge163", "vector163", "processor163", "reasoning163", "machine163", "learning163"],
    ),
    (
        ("knowledge163 vector163 processor163 reasoning163 machine163 learning163", 28),
        ["knowledge163 vector163", "processor163 reasoning163", "machine163 learning163"],
    ),
    (
        ("vector163 processor163 reasoning163 machine163 learning163 model163", 6),
        ["vector163", "processor163", "reasoning163", "machine163", "learning163", "model163"],
    ),
    (
        ("vector163 processor163 reasoning163 machine163 learning163 model163", 10),
        ["vector163", "processor163", "reasoning163", "machine163", "learning163", "model163"],
    ),
    (
        ("vector163 processor163 reasoning163 machine163 learning163 model163", 18),
        ["vector163", "processor163", "reasoning163", "machine163", "learning163", "model163"],
    ),
    (
        ("vector163 processor163 reasoning163 machine163 learning163 model163", 28),
        ["vector163 processor163", "reasoning163 machine163", "learning163 model163"],
    ),
    (
        ("processor163 reasoning163 machine163 learning163 model163 token163", 6),
        ["processor163", "reasoning163", "machine163", "learning163", "model163", "token163"],
    ),
    (
        ("processor163 reasoning163 machine163 learning163 model163 token163", 10),
        ["processor163", "reasoning163", "machine163", "learning163", "model163", "token163"],
    ),
    (
        ("processor163 reasoning163 machine163 learning163 model163 token163", 18),
        ["processor163", "reasoning163", "machine163", "learning163", "model163 token163"],
    ),
    (
        ("processor163 reasoning163 machine163 learning163 model163 token163", 28),
        ["processor163 reasoning163", "machine163 learning163", "model163 token163"],
    ),
    (
        ("reasoning163 machine163 learning163 model163 token163 prompt163", 6),
        ["reasoning163", "machine163", "learning163", "model163", "token163", "prompt163"],
    ),
    (
        ("reasoning163 machine163 learning163 model163 token163 prompt163", 10),
        ["reasoning163", "machine163", "learning163", "model163", "token163", "prompt163"],
    ),
    (
        ("reasoning163 machine163 learning163 model163 token163 prompt163", 18),
        ["reasoning163", "machine163", "learning163", "model163 token163", "prompt163"],
    ),
    (
        ("reasoning163 machine163 learning163 model163 token163 prompt163", 28),
        ["reasoning163 machine163", "learning163 model163", "token163 prompt163"],
    ),
    (
        ("machine163 learning163 model163 token163 prompt163 session163", 6),
        ["machine163", "learning163", "model163", "token163", "prompt163", "session163"],
    ),
    (
        ("machine163 learning163 model163 token163 prompt163 session163", 10),
        ["machine163", "learning163", "model163", "token163", "prompt163", "session163"],
    ),
    (
        ("machine163 learning163 model163 token163 prompt163 session163", 18),
        ["machine163", "learning163", "model163 token163", "prompt163", "session163"],
    ),
    (
        ("machine163 learning163 model163 token163 prompt163 session163", 28),
        ["machine163 learning163", "model163 token163 prompt163", "session163"],
    ),
    (
        ("learning163 model163 token163 prompt163 session163 library163", 6),
        ["learning163", "model163", "token163", "prompt163", "session163", "library163"],
    ),
    (
        ("learning163 model163 token163 prompt163 session163 library163", 10),
        ["learning163", "model163", "token163", "prompt163", "session163", "library163"],
    ),
    (
        ("learning163 model163 token163 prompt163 session163 library163", 18),
        ["learning163", "model163 token163", "prompt163", "session163", "library163"],
    ),
    (
        ("learning163 model163 token163 prompt163 session163 library163", 28),
        ["learning163 model163", "token163 prompt163", "session163 library163"],
    ),
    (
        ("model163 token163 prompt163 session163 library163 service163", 6),
        ["model163", "token163", "prompt163", "session163", "library163", "service163"],
    ),
    (
        ("model163 token163 prompt163 session163 library163 service163", 10),
        ["model163", "token163", "prompt163", "session163", "library163", "service163"],
    ),
    (
        ("model163 token163 prompt163 session163 library163 service163", 18),
        ["model163 token163", "prompt163", "session163", "library163", "service163"],
    ),
    (
        ("model163 token163 prompt163 session163 library163 service163", 28),
        ["model163 token163 prompt163", "session163 library163", "service163"],
    ),
    (
        ("token163 prompt163 session163 library163 service163 gateway163", 6),
        ["token163", "prompt163", "session163", "library163", "service163", "gateway163"],
    ),
    (
        ("token163 prompt163 session163 library163 service163 gateway163", 10),
        ["token163", "prompt163", "session163", "library163", "service163", "gateway163"],
    ),
    (
        ("token163 prompt163 session163 library163 service163 gateway163", 18),
        ["token163 prompt163", "session163", "library163", "service163", "gateway163"],
    ),
    (
        ("token163 prompt163 session163 library163 service163 gateway163", 28),
        ["token163 prompt163", "session163 library163", "service163 gateway163"],
    ),
    (
        ("prompt163 session163 library163 service163 gateway163 storage163", 6),
        ["prompt163", "session163", "library163", "service163", "gateway163", "storage163"],
    ),
    (
        ("prompt163 session163 library163 service163 gateway163 storage163", 10),
        ["prompt163", "session163", "library163", "service163", "gateway163", "storage163"],
    ),
    (
        ("prompt163 session163 library163 service163 gateway163 storage163", 18),
        ["prompt163", "session163", "library163", "service163", "gateway163", "storage163"],
    ),
    (
        ("prompt163 session163 library163 service163 gateway163 storage163", 28),
        ["prompt163 session163", "library163 service163", "gateway163 storage163"],
    ),
    (
        ("session163 library163 service163 gateway163 storage163 network163", 6),
        ["session163", "library163", "service163", "gateway163", "storage163", "network163"],
    ),
    (
        ("session163 library163 service163 gateway163 storage163 network163", 10),
        ["session163", "library163", "service163", "gateway163", "storage163", "network163"],
    ),
    (
        ("session163 library163 service163 gateway163 storage163 network163", 18),
        ["session163", "library163", "service163", "gateway163", "storage163", "network163"],
    ),
    (
        ("session163 library163 service163 gateway163 storage163 network163", 28),
        ["session163 library163", "service163 gateway163", "storage163 network163"],
    ),
    (
        ("library163 service163 gateway163 storage163 network163 latency163", 6),
        ["library163", "service163", "gateway163", "storage163", "network163", "latency163"],
    ),
    (
        ("library163 service163 gateway163 storage163 network163 latency163", 10),
        ["library163", "service163", "gateway163", "storage163", "network163", "latency163"],
    ),
    (
        ("library163 service163 gateway163 storage163 network163 latency163", 18),
        ["library163", "service163", "gateway163", "storage163", "network163", "latency163"],
    ),
    (
        ("library163 service163 gateway163 storage163 network163 latency163", 28),
        ["library163 service163", "gateway163 storage163", "network163 latency163"],
    ),
    (
        ("service163 gateway163 storage163 network163 latency163 buffer163", 6),
        ["service163", "gateway163", "storage163", "network163", "latency163", "buffer163"],
    ),
    (
        ("service163 gateway163 storage163 network163 latency163 buffer163", 10),
        ["service163", "gateway163", "storage163", "network163", "latency163", "buffer163"],
    ),
    (
        ("service163 gateway163 storage163 network163 latency163 buffer163", 18),
        ["service163", "gateway163", "storage163", "network163", "latency163", "buffer163"],
    ),
    (
        ("service163 gateway163 storage163 network163 latency163 buffer163", 28),
        ["service163 gateway163", "storage163 network163", "latency163 buffer163"],
    ),
    (
        ("gateway163 storage163 network163 latency163 buffer163 queue163", 6),
        ["gateway163", "storage163", "network163", "latency163", "buffer163", "queue163"],
    ),
    (
        ("gateway163 storage163 network163 latency163 buffer163 queue163", 10),
        ["gateway163", "storage163", "network163", "latency163", "buffer163", "queue163"],
    ),
    (
        ("gateway163 storage163 network163 latency163 buffer163 queue163", 18),
        ["gateway163", "storage163", "network163", "latency163", "buffer163 queue163"],
    ),
    (
        ("gateway163 storage163 network163 latency163 buffer163 queue163", 28),
        ["gateway163 storage163", "network163 latency163", "buffer163 queue163"],
    ),
    (
        ("storage163 network163 latency163 buffer163 queue163 worker163", 6),
        ["storage163", "network163", "latency163", "buffer163", "queue163", "worker163"],
    ),
    (
        ("storage163 network163 latency163 buffer163 queue163 worker163", 10),
        ["storage163", "network163", "latency163", "buffer163", "queue163", "worker163"],
    ),
    (
        ("storage163 network163 latency163 buffer163 queue163 worker163", 18),
        ["storage163", "network163", "latency163", "buffer163 queue163", "worker163"],
    ),
    (
        ("storage163 network163 latency163 buffer163 queue163 worker163", 28),
        ["storage163 network163", "latency163 buffer163", "queue163 worker163"],
    ),
    (
        ("network163 latency163 buffer163 queue163 worker163 kernel163", 6),
        ["network163", "latency163", "buffer163", "queue163", "worker163", "kernel163"],
    ),
    (
        ("network163 latency163 buffer163 queue163 worker163 kernel163", 10),
        ["network163", "latency163", "buffer163", "queue163", "worker163", "kernel163"],
    ),
    (
        ("network163 latency163 buffer163 queue163 worker163 kernel163", 18),
        ["network163", "latency163", "buffer163 queue163", "worker163", "kernel163"],
    ),
    (
        ("network163 latency163 buffer163 queue163 worker163 kernel163", 28),
        ["network163 latency163", "buffer163 queue163 worker163", "kernel163"],
    ),
    (
        ("latency163 buffer163 queue163 worker163 kernel163 signal163", 6),
        ["latency163", "buffer163", "queue163", "worker163", "kernel163", "signal163"],
    ),
    (
        ("latency163 buffer163 queue163 worker163 kernel163 signal163", 10),
        ["latency163", "buffer163", "queue163", "worker163", "kernel163", "signal163"],
    ),
    (
        ("latency163 buffer163 queue163 worker163 kernel163 signal163", 18),
        ["latency163", "buffer163 queue163", "worker163", "kernel163", "signal163"],
    ),
    (
        ("latency163 buffer163 queue163 worker163 kernel163 signal163", 28),
        ["latency163 buffer163", "queue163 worker163 kernel163", "signal163"],
    ),
    (
        ("buffer163 queue163 worker163 kernel163 signal163 packet163", 6),
        ["buffer163", "queue163", "worker163", "kernel163", "signal163", "packet163"],
    ),
    (
        ("buffer163 queue163 worker163 kernel163 signal163 packet163", 10),
        ["buffer163", "queue163", "worker163", "kernel163", "signal163", "packet163"],
    ),
    (
        ("buffer163 queue163 worker163 kernel163 signal163 packet163", 18),
        ["buffer163 queue163", "worker163", "kernel163", "signal163", "packet163"],
    ),
    (
        ("buffer163 queue163 worker163 kernel163 signal163 packet163", 28),
        ["buffer163 queue163 worker163", "kernel163 signal163", "packet163"],
    ),
    (
        ("queue163 worker163 kernel163 signal163 packet163 router163", 6),
        ["queue163", "worker163", "kernel163", "signal163", "packet163", "router163"],
    ),
    (
        ("queue163 worker163 kernel163 signal163 packet163 router163", 10),
        ["queue163", "worker163", "kernel163", "signal163", "packet163", "router163"],
    ),
    (
        ("queue163 worker163 kernel163 signal163 packet163 router163", 18),
        ["queue163 worker163", "kernel163", "signal163", "packet163", "router163"],
    ),
    (
        ("queue163 worker163 kernel163 signal163 packet163 router163", 28),
        ["queue163 worker163 kernel163", "signal163 packet163", "router163"],
    ),
    (
        ("worker163 kernel163 signal163 packet163 router163 cluster163", 6),
        ["worker163", "kernel163", "signal163", "packet163", "router163", "cluster163"],
    ),
    (
        ("worker163 kernel163 signal163 packet163 router163 cluster163", 10),
        ["worker163", "kernel163", "signal163", "packet163", "router163", "cluster163"],
    ),
    (
        ("worker163 kernel163 signal163 packet163 router163 cluster163", 18),
        ["worker163", "kernel163", "signal163", "packet163", "router163", "cluster163"],
    ),
    (
        ("worker163 kernel163 signal163 packet163 router163 cluster163", 28),
        ["worker163 kernel163", "signal163 packet163", "router163 cluster163"],
    ),
    (
        ("kernel163 signal163 packet163 router163 cluster163 mirror163", 6),
        ["kernel163", "signal163", "packet163", "router163", "cluster163", "mirror163"],
    ),
    (
        ("kernel163 signal163 packet163 router163 cluster163 mirror163", 10),
        ["kernel163", "signal163", "packet163", "router163", "cluster163", "mirror163"],
    ),
    (
        ("kernel163 signal163 packet163 router163 cluster163 mirror163", 18),
        ["kernel163", "signal163", "packet163", "router163", "cluster163", "mirror163"],
    ),
    (
        ("kernel163 signal163 packet163 router163 cluster163 mirror163", 28),
        ["kernel163 signal163", "packet163 router163", "cluster163 mirror163"],
    ),
    (
        ("signal163 packet163 router163 cluster163 mirror163 filter163", 6),
        ["signal163", "packet163", "router163", "cluster163", "mirror163", "filter163"],
    ),
    (
        ("signal163 packet163 router163 cluster163 mirror163 filter163", 10),
        ["signal163", "packet163", "router163", "cluster163", "mirror163", "filter163"],
    ),
    (
        ("signal163 packet163 router163 cluster163 mirror163 filter163", 18),
        ["signal163", "packet163", "router163", "cluster163", "mirror163", "filter163"],
    ),
    (
        ("signal163 packet163 router163 cluster163 mirror163 filter163", 28),
        ["signal163 packet163", "router163 cluster163", "mirror163 filter163"],
    ),
    (
        ("packet163 router163 cluster163 mirror163 filter163 ranking163", 6),
        ["packet163", "router163", "cluster163", "mirror163", "filter163", "ranking163"],
    ),
    (
        ("packet163 router163 cluster163 mirror163 filter163 ranking163", 10),
        ["packet163", "router163", "cluster163", "mirror163", "filter163", "ranking163"],
    ),
    (
        ("packet163 router163 cluster163 mirror163 filter163 ranking163", 18),
        ["packet163", "router163", "cluster163", "mirror163", "filter163", "ranking163"],
    ),
    (
        ("packet163 router163 cluster163 mirror163 filter163 ranking163", 28),
        ["packet163 router163", "cluster163 mirror163", "filter163 ranking163"],
    ),
    (
        ("router163 cluster163 mirror163 filter163 ranking163 encoding163", 6),
        ["router163", "cluster163", "mirror163", "filter163", "ranking163", "encoding163"],
    ),
    (
        ("router163 cluster163 mirror163 filter163 ranking163 encoding163", 10),
        ["router163", "cluster163", "mirror163", "filter163", "ranking163", "encoding163"],
    ),
    (
        ("router163 cluster163 mirror163 filter163 ranking163 encoding163", 18),
        ["router163", "cluster163", "mirror163", "filter163", "ranking163", "encoding163"],
    ),
    (
        ("router163 cluster163 mirror163 filter163 ranking163 encoding163", 28),
        ["router163 cluster163", "mirror163 filter163", "ranking163 encoding163"],
    ),
    (
        ("cluster163 mirror163 filter163 ranking163 encoding163 mapping163", 6),
        ["cluster163", "mirror163", "filter163", "ranking163", "encoding163", "mapping163"],
    ),
    (
        ("cluster163 mirror163 filter163 ranking163 encoding163 mapping163", 10),
        ["cluster163", "mirror163", "filter163", "ranking163", "encoding163", "mapping163"],
    ),
    (
        ("cluster163 mirror163 filter163 ranking163 encoding163 mapping163", 18),
        ["cluster163", "mirror163", "filter163", "ranking163", "encoding163", "mapping163"],
    ),
    (
        ("cluster163 mirror163 filter163 ranking163 encoding163 mapping163", 28),
        ["cluster163 mirror163", "filter163 ranking163", "encoding163 mapping163"],
    ),
    (
        ("mirror163 filter163 ranking163 encoding163 mapping163 record163", 6),
        ["mirror163", "filter163", "ranking163", "encoding163", "mapping163", "record163"],
    ),
    (
        ("mirror163 filter163 ranking163 encoding163 mapping163 record163", 10),
        ["mirror163", "filter163", "ranking163", "encoding163", "mapping163", "record163"],
    ),
    (
        ("mirror163 filter163 ranking163 encoding163 mapping163 record163", 18),
        ["mirror163", "filter163", "ranking163", "encoding163", "mapping163", "record163"],
    ),
    (
        ("mirror163 filter163 ranking163 encoding163 mapping163 record163", 28),
        ["mirror163 filter163", "ranking163 encoding163", "mapping163 record163"],
    ),
    (
        ("filter163 ranking163 encoding163 mapping163 record163 candle163", 6),
        ["filter163", "ranking163", "encoding163", "mapping163", "record163", "candle163"],
    ),
    (
        ("filter163 ranking163 encoding163 mapping163 record163 candle163", 10),
        ["filter163", "ranking163", "encoding163", "mapping163", "record163", "candle163"],
    ),
    (
        ("filter163 ranking163 encoding163 mapping163 record163 candle163", 18),
        ["filter163", "ranking163", "encoding163", "mapping163", "record163", "candle163"],
    ),
    (
        ("filter163 ranking163 encoding163 mapping163 record163 candle163", 28),
        ["filter163 ranking163", "encoding163 mapping163", "record163 candle163"],
    ),
    (
        ("ranking163 encoding163 mapping163 record163 candle163 thread163", 6),
        ["ranking163", "encoding163", "mapping163", "record163", "candle163", "thread163"],
    ),
    (
        ("ranking163 encoding163 mapping163 record163 candle163 thread163", 10),
        ["ranking163", "encoding163", "mapping163", "record163", "candle163", "thread163"],
    ),
    (
        ("ranking163 encoding163 mapping163 record163 candle163 thread163", 18),
        ["ranking163", "encoding163", "mapping163", "record163", "candle163", "thread163"],
    ),
    (
        ("ranking163 encoding163 mapping163 record163 candle163 thread163", 28),
        ["ranking163 encoding163", "mapping163 record163", "candle163 thread163"],
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
