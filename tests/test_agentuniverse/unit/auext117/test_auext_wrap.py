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
        ("round 117: the quick brown fox jumps over the lazy dog", 4),
        ["round", "117:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 117: the quick brown fox jumps over the lazy dog", 8),
        ["round", "117: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 117: the quick brown fox jumps over the lazy dog", 12),
        ["round 117:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 117: the quick brown fox jumps over the lazy dog", 16),
        ["round 117: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 117: the quick brown fox jumps over the lazy dog", 24),
        ["round 117: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 117: the quick brown fox jumps over the lazy dog", 32),
        ["round 117: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 117: agentuniverse is a framework for multi agents", 4),
        ["round", "117:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 117: agentuniverse is a framework for multi agents", 8),
        ["round", "117:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 117: agentuniverse is a framework for multi agents", 12),
        ["round 117:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 117: agentuniverse is a framework for multi agents", 16),
        ["round 117:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 117: agentuniverse is a framework for multi agents", 24),
        ["round 117: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 117: agentuniverse is a framework for multi agents", 32),
        ["round 117: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 117: knowledge stored as vectors enables retrieval", 4),
        ["round", "117:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 117: knowledge stored as vectors enables retrieval", 8),
        ["round", "117:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 117: knowledge stored as vectors enables retrieval", 12),
        ["round 117:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 117: knowledge stored as vectors enables retrieval", 16),
        ["round 117:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 117: knowledge stored as vectors enables retrieval", 24),
        ["round 117: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 117: knowledge stored as vectors enables retrieval", 32),
        ["round 117: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 117: the processor reads the record then stops", 4),
        ["round", "117:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 117: the processor reads the record then stops", 8),
        ["round", "117: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 117: the processor reads the record then stops", 12),
        ["round 117:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 117: the processor reads the record then stops", 16),
        ["round 117: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 117: the processor reads the record then stops", 24),
        ["round 117: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 117: the processor reads the record then stops", 32),
        ["round 117: the processor reads", "the record then stops"],
    ),
    (
        ("round 117: a worker pulls the next task from the queue", 4),
        ["round", "117:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 117: a worker pulls the next task from the queue", 8),
        ["round", "117: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 117: a worker pulls the next task from the queue", 12),
        ["round 117: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 117: a worker pulls the next task from the queue", 16),
        ["round 117: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 117: a worker pulls the next task from the queue", 24),
        ["round 117: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 117: a worker pulls the next task from the queue", 32),
        ["round 117: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 117: signals travel through the network layer", 4),
        ["round", "117:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 117: signals travel through the network layer", 8),
        ["round", "117:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 117: signals travel through the network layer", 12),
        ["round 117:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 117: signals travel through the network layer", 16),
        ["round 117:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 117: signals travel through the network layer", 24),
        ["round 117: signals", "travel through the", "network layer"],
    ),
    (
        ("round 117: signals travel through the network layer", 32),
        ["round 117: signals travel", "through the network layer"],
    ),
    (
        ("round 117: the gateway routes each request by policy", 4),
        ["round", "117:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 117: the gateway routes each request by policy", 8),
        ["round", "117: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 117: the gateway routes each request by policy", 12),
        ["round 117:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 117: the gateway routes each request by policy", 16),
        ["round 117: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 117: the gateway routes each request by policy", 24),
        ["round 117: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 117: the gateway routes each request by policy", 32),
        ["round 117: the gateway routes", "each request by policy"],
    ),
    (
        ("round 117: memory grows until the buffer is full", 4),
        ["round", "117:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 117: memory grows until the buffer is full", 8),
        ["round", "117:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 117: memory grows until the buffer is full", 12),
        ["round 117:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 117: memory grows until the buffer is full", 16),
        ["round 117:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 117: memory grows until the buffer is full", 24), ["round 117: memory grows", "until the buffer is full"]),
    (("round 117: memory grows until the buffer is full", 32), ["round 117: memory grows until", "the buffer is full"]),
    (
        ("round 117: the cluster mirrors every packet twice", 4),
        ["round", "117:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 117: the cluster mirrors every packet twice", 8),
        ["round", "117: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 117: the cluster mirrors every packet twice", 12),
        ["round 117:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 117: the cluster mirrors every packet twice", 16),
        ["round 117: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 117: the cluster mirrors every packet twice", 24),
        ["round 117: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 117: the cluster mirrors every packet twice", 32),
        ["round 117: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 117: ranking uses tokens learned from the corpus", 4),
        ["round", "117:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 117: ranking uses tokens learned from the corpus", 8),
        ["round", "117:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 117: ranking uses tokens learned from the corpus", 12),
        ["round 117:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 117: ranking uses tokens learned from the corpus", 16),
        ["round 117:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 117: ranking uses tokens learned from the corpus", 24),
        ["round 117: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 117: ranking uses tokens learned from the corpus", 32),
        ["round 117: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 117: a long session ends when the candle dies", 4),
        ["round", "117:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 117: a long session ends when the candle dies", 8),
        ["round", "117: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 117: a long session ends when the candle dies", 12),
        ["round 117: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 117: a long session ends when the candle dies", 16),
        ["round 117: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 117: a long session ends when the candle dies", 24),
        ["round 117: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 117: a long session ends when the candle dies", 32),
        ["round 117: a long session ends", "when the candle dies"],
    ),
    (
        ("round 117: encode the prompt then map the result", 4),
        ["round", "117:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 117: encode the prompt then map the result", 8),
        ["round", "117:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 117: encode the prompt then map the result", 12),
        ["round 117:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 117: encode the prompt then map the result", 16),
        ["round 117:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 117: encode the prompt then map the result", 24),
        ["round 117: encode the", "prompt then map the", "result"],
    ),
    (("round 117: encode the prompt then map the result", 32), ["round 117: encode the prompt", "then map the result"]),
    (
        ("round 117: the kernel wakes the worker at dawn", 4),
        ["round", "117:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 117: the kernel wakes the worker at dawn", 8),
        ["round", "117: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 117: the kernel wakes the worker at dawn", 12),
        ["round 117:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 117: the kernel wakes the worker at dawn", 16), ["round 117: the", "kernel wakes the", "worker at dawn"]),
    (("round 117: the kernel wakes the worker at dawn", 24), ["round 117: the kernel", "wakes the worker at dawn"]),
    (("round 117: the kernel wakes the worker at dawn", 32), ["round 117: the kernel wakes the", "worker at dawn"]),
    (
        ("round 117: service latency drops after the patch", 4),
        ["round", "117:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 117: service latency drops after the patch", 8),
        ["round", "117:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 117: service latency drops after the patch", 12),
        ["round 117:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 117: service latency drops after the patch", 16),
        ["round 117:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 117: service latency drops after the patch", 24),
        ["round 117: service", "latency drops after the", "patch"],
    ),
    (("round 117: service latency drops after the patch", 32), ["round 117: service latency drops", "after the patch"]),
    (
        ("round 117: the library caches every vector it sees", 4),
        ["round", "117:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 117: the library caches every vector it sees", 8),
        ["round", "117: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 117: the library caches every vector it sees", 12),
        ["round 117:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 117: the library caches every vector it sees", 16),
        ["round 117: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 117: the library caches every vector it sees", 24),
        ["round 117: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 117: the library caches every vector it sees", 32),
        ["round 117: the library caches", "every vector it sees"],
    ),
    (
        ("round 117: agents argue then the debate resolves", 4),
        ["round", "117:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 117: agents argue then the debate resolves", 8),
        ["round", "117:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 117: agents argue then the debate resolves", 12),
        ["round 117:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 117: agents argue then the debate resolves", 16),
        ["round 117:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 117: agents argue then the debate resolves", 24), ["round 117: agents argue", "then the debate resolves"]),
    (("round 117: agents argue then the debate resolves", 32), ["round 117: agents argue then the", "debate resolves"]),
    (
        ("round 117: the filter keeps only strong matches", 4),
        ["round", "117:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 117: the filter keeps only strong matches", 8),
        ["round", "117: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 117: the filter keeps only strong matches", 12),
        ["round 117:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 117: the filter keeps only strong matches", 16),
        ["round 117: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 117: the filter keeps only strong matches", 24),
        ["round 117: the filter", "keeps only strong", "matches"],
    ),
    (("round 117: the filter keeps only strong matches", 32), ["round 117: the filter keeps only", "strong matches"]),
    (
        ("round 117: the model answers with a short reply", 4),
        ["round", "117:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 117: the model answers with a short reply", 8),
        ["round", "117: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 117: the model answers with a short reply", 12),
        ["round 117:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 117: the model answers with a short reply", 16),
        ["round 117: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 117: the model answers with a short reply", 24),
        ["round 117: the model", "answers with a short", "reply"],
    ),
    (("round 117: the model answers with a short reply", 32), ["round 117: the model answers", "with a short reply"]),
    (
        ("round 117: the recorder stores the reasoning trace", 4),
        ["round", "117:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 117: the recorder stores the reasoning trace", 8),
        ["round", "117: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 117: the recorder stores the reasoning trace", 12),
        ["round 117:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 117: the recorder stores the reasoning trace", 16),
        ["round 117: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 117: the recorder stores the reasoning trace", 24),
        ["round 117: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 117: the recorder stores the reasoning trace", 32),
        ["round 117: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 117: the angel watches the processor run", 4),
        ["round", "117:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 117: the angel watches the processor run", 8),
        ["round", "117: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 117: the angel watches the processor run", 12),
        ["round 117:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 117: the angel watches the processor run", 16),
        ["round 117: the", "angel watches", "the processor", "run"],
    ),
    (("round 117: the angel watches the processor run", 24), ["round 117: the angel", "watches the processor", "run"]),
    (("round 117: the angel watches the processor run", 32), ["round 117: the angel watches the", "processor run"]),
    (
        ("round 117: angle of the vector decides the match", 4),
        ["round", "117:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 117: angle of the vector decides the match", 8),
        ["round", "117:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 117: angle of the vector decides the match", 12),
        ["round 117:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 117: angle of the vector decides the match", 16),
        ["round 117: angle", "of the vector", "decides the", "match"],
    ),
    (("round 117: angle of the vector decides the match", 24), ["round 117: angle of the", "vector decides the match"]),
    (("round 117: angle of the vector decides the match", 32), ["round 117: angle of the vector", "decides the match"]),
    (
        ("round 117: the candle burns twice as long at night", 4),
        ["round", "117:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 117: the candle burns twice as long at night", 8),
        ["round", "117: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 117: the candle burns twice as long at night", 12),
        ["round 117:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 117: the candle burns twice as long at night", 16),
        ["round 117: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 117: the candle burns twice as long at night", 24),
        ["round 117: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 117: the candle burns twice as long at night", 32),
        ["round 117: the candle burns", "twice as long at night"],
    ),
    (
        ("round 117: a mirror of the universe in one line", 4),
        ["round", "117:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 117: a mirror of the universe in one line", 8),
        ["round", "117: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 117: a mirror of the universe in one line", 12),
        ["round 117: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 117: a mirror of the universe in one line", 16),
        ["round 117: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 117: a mirror of the universe in one line", 24), ["round 117: a mirror of", "the universe in one line"]),
    (("round 117: a mirror of the universe in one line", 32), ["round 117: a mirror of the", "universe in one line"]),
    (
        ("round 117: the queue drains before the storm", 4),
        ["round", "117:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 117: the queue drains before the storm", 8),
        ["round", "117: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 117: the queue drains before the storm", 12),
        ["round 117:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 117: the queue drains before the storm", 16), ["round 117: the", "queue drains", "before the storm"]),
    (("round 117: the queue drains before the storm", 24), ["round 117: the queue", "drains before the storm"]),
    (("round 117: the queue drains before the storm", 32), ["round 117: the queue drains", "before the storm"]),
    (
        ("kitten117 sitting117 agent117 angle117 universe117 memory117", 6),
        ["kitten117", "sitting117", "agent117", "angle117", "universe117", "memory117"],
    ),
    (
        ("kitten117 sitting117 agent117 angle117 universe117 memory117", 10),
        ["kitten117", "sitting117", "agent117", "angle117", "universe117", "memory117"],
    ),
    (
        ("kitten117 sitting117 agent117 angle117 universe117 memory117", 18),
        ["kitten117", "sitting117", "agent117 angle117", "universe117", "memory117"],
    ),
    (
        ("kitten117 sitting117 agent117 angle117 universe117 memory117", 28),
        ["kitten117 sitting117", "agent117 angle117", "universe117 memory117"],
    ),
    (
        ("sitting117 agent117 angle117 universe117 memory117 stream117", 6),
        ["sitting117", "agent117", "angle117", "universe117", "memory117", "stream117"],
    ),
    (
        ("sitting117 agent117 angle117 universe117 memory117 stream117", 10),
        ["sitting117", "agent117", "angle117", "universe117", "memory117", "stream117"],
    ),
    (
        ("sitting117 agent117 angle117 universe117 memory117 stream117", 18),
        ["sitting117", "agent117 angle117", "universe117", "memory117", "stream117"],
    ),
    (
        ("sitting117 agent117 angle117 universe117 memory117 stream117", 28),
        ["sitting117 agent117 angle117", "universe117 memory117", "stream117"],
    ),
    (
        ("agent117 angle117 universe117 memory117 stream117 context117", 6),
        ["agent117", "angle117", "universe117", "memory117", "stream117", "context117"],
    ),
    (
        ("agent117 angle117 universe117 memory117 stream117 context117", 10),
        ["agent117", "angle117", "universe117", "memory117", "stream117", "context117"],
    ),
    (
        ("agent117 angle117 universe117 memory117 stream117 context117", 18),
        ["agent117 angle117", "universe117", "memory117", "stream117", "context117"],
    ),
    (
        ("agent117 angle117 universe117 memory117 stream117 context117", 28),
        ["agent117 angle117", "universe117 memory117", "stream117 context117"],
    ),
    (
        ("angle117 universe117 memory117 stream117 context117 knowledge117", 6),
        ["angle117", "universe117", "memory117", "stream117", "context117", "knowledge117"],
    ),
    (
        ("angle117 universe117 memory117 stream117 context117 knowledge117", 10),
        ["angle117", "universe117", "memory117", "stream117", "context117", "knowledge117"],
    ),
    (
        ("angle117 universe117 memory117 stream117 context117 knowledge117", 18),
        ["angle117", "universe117", "memory117", "stream117", "context117", "knowledge117"],
    ),
    (
        ("angle117 universe117 memory117 stream117 context117 knowledge117", 28),
        ["angle117 universe117", "memory117 stream117", "context117 knowledge117"],
    ),
    (
        ("universe117 memory117 stream117 context117 knowledge117 vector117", 6),
        ["universe117", "memory117", "stream117", "context117", "knowledge117", "vector117"],
    ),
    (
        ("universe117 memory117 stream117 context117 knowledge117 vector117", 10),
        ["universe117", "memory117", "stream117", "context117", "knowledge117", "vector117"],
    ),
    (
        ("universe117 memory117 stream117 context117 knowledge117 vector117", 18),
        ["universe117", "memory117", "stream117", "context117", "knowledge117", "vector117"],
    ),
    (
        ("universe117 memory117 stream117 context117 knowledge117 vector117", 28),
        ["universe117 memory117", "stream117 context117", "knowledge117 vector117"],
    ),
    (
        ("memory117 stream117 context117 knowledge117 vector117 processor117", 6),
        ["memory117", "stream117", "context117", "knowledge117", "vector117", "processor117"],
    ),
    (
        ("memory117 stream117 context117 knowledge117 vector117 processor117", 10),
        ["memory117", "stream117", "context117", "knowledge117", "vector117", "processor117"],
    ),
    (
        ("memory117 stream117 context117 knowledge117 vector117 processor117", 18),
        ["memory117", "stream117", "context117", "knowledge117", "vector117", "processor117"],
    ),
    (
        ("memory117 stream117 context117 knowledge117 vector117 processor117", 28),
        ["memory117 stream117", "context117 knowledge117", "vector117 processor117"],
    ),
    (
        ("stream117 context117 knowledge117 vector117 processor117 reasoning117", 6),
        ["stream117", "context117", "knowledge117", "vector117", "processor117", "reasoning117"],
    ),
    (
        ("stream117 context117 knowledge117 vector117 processor117 reasoning117", 10),
        ["stream117", "context117", "knowledge117", "vector117", "processor117", "reasoning117"],
    ),
    (
        ("stream117 context117 knowledge117 vector117 processor117 reasoning117", 18),
        ["stream117", "context117", "knowledge117", "vector117", "processor117", "reasoning117"],
    ),
    (
        ("stream117 context117 knowledge117 vector117 processor117 reasoning117", 28),
        ["stream117 context117", "knowledge117 vector117", "processor117 reasoning117"],
    ),
    (
        ("context117 knowledge117 vector117 processor117 reasoning117 machine117", 6),
        ["context117", "knowledge117", "vector117", "processor117", "reasoning117", "machine117"],
    ),
    (
        ("context117 knowledge117 vector117 processor117 reasoning117 machine117", 10),
        ["context117", "knowledge117", "vector117", "processor117", "reasoning117", "machine117"],
    ),
    (
        ("context117 knowledge117 vector117 processor117 reasoning117 machine117", 18),
        ["context117", "knowledge117", "vector117", "processor117", "reasoning117", "machine117"],
    ),
    (
        ("context117 knowledge117 vector117 processor117 reasoning117 machine117", 28),
        ["context117 knowledge117", "vector117 processor117", "reasoning117 machine117"],
    ),
    (
        ("knowledge117 vector117 processor117 reasoning117 machine117 learning117", 6),
        ["knowledge117", "vector117", "processor117", "reasoning117", "machine117", "learning117"],
    ),
    (
        ("knowledge117 vector117 processor117 reasoning117 machine117 learning117", 10),
        ["knowledge117", "vector117", "processor117", "reasoning117", "machine117", "learning117"],
    ),
    (
        ("knowledge117 vector117 processor117 reasoning117 machine117 learning117", 18),
        ["knowledge117", "vector117", "processor117", "reasoning117", "machine117", "learning117"],
    ),
    (
        ("knowledge117 vector117 processor117 reasoning117 machine117 learning117", 28),
        ["knowledge117 vector117", "processor117 reasoning117", "machine117 learning117"],
    ),
    (
        ("vector117 processor117 reasoning117 machine117 learning117 model117", 6),
        ["vector117", "processor117", "reasoning117", "machine117", "learning117", "model117"],
    ),
    (
        ("vector117 processor117 reasoning117 machine117 learning117 model117", 10),
        ["vector117", "processor117", "reasoning117", "machine117", "learning117", "model117"],
    ),
    (
        ("vector117 processor117 reasoning117 machine117 learning117 model117", 18),
        ["vector117", "processor117", "reasoning117", "machine117", "learning117", "model117"],
    ),
    (
        ("vector117 processor117 reasoning117 machine117 learning117 model117", 28),
        ["vector117 processor117", "reasoning117 machine117", "learning117 model117"],
    ),
    (
        ("processor117 reasoning117 machine117 learning117 model117 token117", 6),
        ["processor117", "reasoning117", "machine117", "learning117", "model117", "token117"],
    ),
    (
        ("processor117 reasoning117 machine117 learning117 model117 token117", 10),
        ["processor117", "reasoning117", "machine117", "learning117", "model117", "token117"],
    ),
    (
        ("processor117 reasoning117 machine117 learning117 model117 token117", 18),
        ["processor117", "reasoning117", "machine117", "learning117", "model117 token117"],
    ),
    (
        ("processor117 reasoning117 machine117 learning117 model117 token117", 28),
        ["processor117 reasoning117", "machine117 learning117", "model117 token117"],
    ),
    (
        ("reasoning117 machine117 learning117 model117 token117 prompt117", 6),
        ["reasoning117", "machine117", "learning117", "model117", "token117", "prompt117"],
    ),
    (
        ("reasoning117 machine117 learning117 model117 token117 prompt117", 10),
        ["reasoning117", "machine117", "learning117", "model117", "token117", "prompt117"],
    ),
    (
        ("reasoning117 machine117 learning117 model117 token117 prompt117", 18),
        ["reasoning117", "machine117", "learning117", "model117 token117", "prompt117"],
    ),
    (
        ("reasoning117 machine117 learning117 model117 token117 prompt117", 28),
        ["reasoning117 machine117", "learning117 model117", "token117 prompt117"],
    ),
    (
        ("machine117 learning117 model117 token117 prompt117 session117", 6),
        ["machine117", "learning117", "model117", "token117", "prompt117", "session117"],
    ),
    (
        ("machine117 learning117 model117 token117 prompt117 session117", 10),
        ["machine117", "learning117", "model117", "token117", "prompt117", "session117"],
    ),
    (
        ("machine117 learning117 model117 token117 prompt117 session117", 18),
        ["machine117", "learning117", "model117 token117", "prompt117", "session117"],
    ),
    (
        ("machine117 learning117 model117 token117 prompt117 session117", 28),
        ["machine117 learning117", "model117 token117 prompt117", "session117"],
    ),
    (
        ("learning117 model117 token117 prompt117 session117 library117", 6),
        ["learning117", "model117", "token117", "prompt117", "session117", "library117"],
    ),
    (
        ("learning117 model117 token117 prompt117 session117 library117", 10),
        ["learning117", "model117", "token117", "prompt117", "session117", "library117"],
    ),
    (
        ("learning117 model117 token117 prompt117 session117 library117", 18),
        ["learning117", "model117 token117", "prompt117", "session117", "library117"],
    ),
    (
        ("learning117 model117 token117 prompt117 session117 library117", 28),
        ["learning117 model117", "token117 prompt117", "session117 library117"],
    ),
    (
        ("model117 token117 prompt117 session117 library117 service117", 6),
        ["model117", "token117", "prompt117", "session117", "library117", "service117"],
    ),
    (
        ("model117 token117 prompt117 session117 library117 service117", 10),
        ["model117", "token117", "prompt117", "session117", "library117", "service117"],
    ),
    (
        ("model117 token117 prompt117 session117 library117 service117", 18),
        ["model117 token117", "prompt117", "session117", "library117", "service117"],
    ),
    (
        ("model117 token117 prompt117 session117 library117 service117", 28),
        ["model117 token117 prompt117", "session117 library117", "service117"],
    ),
    (
        ("token117 prompt117 session117 library117 service117 gateway117", 6),
        ["token117", "prompt117", "session117", "library117", "service117", "gateway117"],
    ),
    (
        ("token117 prompt117 session117 library117 service117 gateway117", 10),
        ["token117", "prompt117", "session117", "library117", "service117", "gateway117"],
    ),
    (
        ("token117 prompt117 session117 library117 service117 gateway117", 18),
        ["token117 prompt117", "session117", "library117", "service117", "gateway117"],
    ),
    (
        ("token117 prompt117 session117 library117 service117 gateway117", 28),
        ["token117 prompt117", "session117 library117", "service117 gateway117"],
    ),
    (
        ("prompt117 session117 library117 service117 gateway117 storage117", 6),
        ["prompt117", "session117", "library117", "service117", "gateway117", "storage117"],
    ),
    (
        ("prompt117 session117 library117 service117 gateway117 storage117", 10),
        ["prompt117", "session117", "library117", "service117", "gateway117", "storage117"],
    ),
    (
        ("prompt117 session117 library117 service117 gateway117 storage117", 18),
        ["prompt117", "session117", "library117", "service117", "gateway117", "storage117"],
    ),
    (
        ("prompt117 session117 library117 service117 gateway117 storage117", 28),
        ["prompt117 session117", "library117 service117", "gateway117 storage117"],
    ),
    (
        ("session117 library117 service117 gateway117 storage117 network117", 6),
        ["session117", "library117", "service117", "gateway117", "storage117", "network117"],
    ),
    (
        ("session117 library117 service117 gateway117 storage117 network117", 10),
        ["session117", "library117", "service117", "gateway117", "storage117", "network117"],
    ),
    (
        ("session117 library117 service117 gateway117 storage117 network117", 18),
        ["session117", "library117", "service117", "gateway117", "storage117", "network117"],
    ),
    (
        ("session117 library117 service117 gateway117 storage117 network117", 28),
        ["session117 library117", "service117 gateway117", "storage117 network117"],
    ),
    (
        ("library117 service117 gateway117 storage117 network117 latency117", 6),
        ["library117", "service117", "gateway117", "storage117", "network117", "latency117"],
    ),
    (
        ("library117 service117 gateway117 storage117 network117 latency117", 10),
        ["library117", "service117", "gateway117", "storage117", "network117", "latency117"],
    ),
    (
        ("library117 service117 gateway117 storage117 network117 latency117", 18),
        ["library117", "service117", "gateway117", "storage117", "network117", "latency117"],
    ),
    (
        ("library117 service117 gateway117 storage117 network117 latency117", 28),
        ["library117 service117", "gateway117 storage117", "network117 latency117"],
    ),
    (
        ("service117 gateway117 storage117 network117 latency117 buffer117", 6),
        ["service117", "gateway117", "storage117", "network117", "latency117", "buffer117"],
    ),
    (
        ("service117 gateway117 storage117 network117 latency117 buffer117", 10),
        ["service117", "gateway117", "storage117", "network117", "latency117", "buffer117"],
    ),
    (
        ("service117 gateway117 storage117 network117 latency117 buffer117", 18),
        ["service117", "gateway117", "storage117", "network117", "latency117", "buffer117"],
    ),
    (
        ("service117 gateway117 storage117 network117 latency117 buffer117", 28),
        ["service117 gateway117", "storage117 network117", "latency117 buffer117"],
    ),
    (
        ("gateway117 storage117 network117 latency117 buffer117 queue117", 6),
        ["gateway117", "storage117", "network117", "latency117", "buffer117", "queue117"],
    ),
    (
        ("gateway117 storage117 network117 latency117 buffer117 queue117", 10),
        ["gateway117", "storage117", "network117", "latency117", "buffer117", "queue117"],
    ),
    (
        ("gateway117 storage117 network117 latency117 buffer117 queue117", 18),
        ["gateway117", "storage117", "network117", "latency117", "buffer117 queue117"],
    ),
    (
        ("gateway117 storage117 network117 latency117 buffer117 queue117", 28),
        ["gateway117 storage117", "network117 latency117", "buffer117 queue117"],
    ),
    (
        ("storage117 network117 latency117 buffer117 queue117 worker117", 6),
        ["storage117", "network117", "latency117", "buffer117", "queue117", "worker117"],
    ),
    (
        ("storage117 network117 latency117 buffer117 queue117 worker117", 10),
        ["storage117", "network117", "latency117", "buffer117", "queue117", "worker117"],
    ),
    (
        ("storage117 network117 latency117 buffer117 queue117 worker117", 18),
        ["storage117", "network117", "latency117", "buffer117 queue117", "worker117"],
    ),
    (
        ("storage117 network117 latency117 buffer117 queue117 worker117", 28),
        ["storage117 network117", "latency117 buffer117", "queue117 worker117"],
    ),
    (
        ("network117 latency117 buffer117 queue117 worker117 kernel117", 6),
        ["network117", "latency117", "buffer117", "queue117", "worker117", "kernel117"],
    ),
    (
        ("network117 latency117 buffer117 queue117 worker117 kernel117", 10),
        ["network117", "latency117", "buffer117", "queue117", "worker117", "kernel117"],
    ),
    (
        ("network117 latency117 buffer117 queue117 worker117 kernel117", 18),
        ["network117", "latency117", "buffer117 queue117", "worker117", "kernel117"],
    ),
    (
        ("network117 latency117 buffer117 queue117 worker117 kernel117", 28),
        ["network117 latency117", "buffer117 queue117 worker117", "kernel117"],
    ),
    (
        ("latency117 buffer117 queue117 worker117 kernel117 signal117", 6),
        ["latency117", "buffer117", "queue117", "worker117", "kernel117", "signal117"],
    ),
    (
        ("latency117 buffer117 queue117 worker117 kernel117 signal117", 10),
        ["latency117", "buffer117", "queue117", "worker117", "kernel117", "signal117"],
    ),
    (
        ("latency117 buffer117 queue117 worker117 kernel117 signal117", 18),
        ["latency117", "buffer117 queue117", "worker117", "kernel117", "signal117"],
    ),
    (
        ("latency117 buffer117 queue117 worker117 kernel117 signal117", 28),
        ["latency117 buffer117", "queue117 worker117 kernel117", "signal117"],
    ),
    (
        ("buffer117 queue117 worker117 kernel117 signal117 packet117", 6),
        ["buffer117", "queue117", "worker117", "kernel117", "signal117", "packet117"],
    ),
    (
        ("buffer117 queue117 worker117 kernel117 signal117 packet117", 10),
        ["buffer117", "queue117", "worker117", "kernel117", "signal117", "packet117"],
    ),
    (
        ("buffer117 queue117 worker117 kernel117 signal117 packet117", 18),
        ["buffer117 queue117", "worker117", "kernel117", "signal117", "packet117"],
    ),
    (
        ("buffer117 queue117 worker117 kernel117 signal117 packet117", 28),
        ["buffer117 queue117 worker117", "kernel117 signal117", "packet117"],
    ),
    (
        ("queue117 worker117 kernel117 signal117 packet117 router117", 6),
        ["queue117", "worker117", "kernel117", "signal117", "packet117", "router117"],
    ),
    (
        ("queue117 worker117 kernel117 signal117 packet117 router117", 10),
        ["queue117", "worker117", "kernel117", "signal117", "packet117", "router117"],
    ),
    (
        ("queue117 worker117 kernel117 signal117 packet117 router117", 18),
        ["queue117 worker117", "kernel117", "signal117", "packet117", "router117"],
    ),
    (
        ("queue117 worker117 kernel117 signal117 packet117 router117", 28),
        ["queue117 worker117 kernel117", "signal117 packet117", "router117"],
    ),
    (
        ("worker117 kernel117 signal117 packet117 router117 cluster117", 6),
        ["worker117", "kernel117", "signal117", "packet117", "router117", "cluster117"],
    ),
    (
        ("worker117 kernel117 signal117 packet117 router117 cluster117", 10),
        ["worker117", "kernel117", "signal117", "packet117", "router117", "cluster117"],
    ),
    (
        ("worker117 kernel117 signal117 packet117 router117 cluster117", 18),
        ["worker117", "kernel117", "signal117", "packet117", "router117", "cluster117"],
    ),
    (
        ("worker117 kernel117 signal117 packet117 router117 cluster117", 28),
        ["worker117 kernel117", "signal117 packet117", "router117 cluster117"],
    ),
    (
        ("kernel117 signal117 packet117 router117 cluster117 mirror117", 6),
        ["kernel117", "signal117", "packet117", "router117", "cluster117", "mirror117"],
    ),
    (
        ("kernel117 signal117 packet117 router117 cluster117 mirror117", 10),
        ["kernel117", "signal117", "packet117", "router117", "cluster117", "mirror117"],
    ),
    (
        ("kernel117 signal117 packet117 router117 cluster117 mirror117", 18),
        ["kernel117", "signal117", "packet117", "router117", "cluster117", "mirror117"],
    ),
    (
        ("kernel117 signal117 packet117 router117 cluster117 mirror117", 28),
        ["kernel117 signal117", "packet117 router117", "cluster117 mirror117"],
    ),
    (
        ("signal117 packet117 router117 cluster117 mirror117 filter117", 6),
        ["signal117", "packet117", "router117", "cluster117", "mirror117", "filter117"],
    ),
    (
        ("signal117 packet117 router117 cluster117 mirror117 filter117", 10),
        ["signal117", "packet117", "router117", "cluster117", "mirror117", "filter117"],
    ),
    (
        ("signal117 packet117 router117 cluster117 mirror117 filter117", 18),
        ["signal117", "packet117", "router117", "cluster117", "mirror117", "filter117"],
    ),
    (
        ("signal117 packet117 router117 cluster117 mirror117 filter117", 28),
        ["signal117 packet117", "router117 cluster117", "mirror117 filter117"],
    ),
    (
        ("packet117 router117 cluster117 mirror117 filter117 ranking117", 6),
        ["packet117", "router117", "cluster117", "mirror117", "filter117", "ranking117"],
    ),
    (
        ("packet117 router117 cluster117 mirror117 filter117 ranking117", 10),
        ["packet117", "router117", "cluster117", "mirror117", "filter117", "ranking117"],
    ),
    (
        ("packet117 router117 cluster117 mirror117 filter117 ranking117", 18),
        ["packet117", "router117", "cluster117", "mirror117", "filter117", "ranking117"],
    ),
    (
        ("packet117 router117 cluster117 mirror117 filter117 ranking117", 28),
        ["packet117 router117", "cluster117 mirror117", "filter117 ranking117"],
    ),
    (
        ("router117 cluster117 mirror117 filter117 ranking117 encoding117", 6),
        ["router117", "cluster117", "mirror117", "filter117", "ranking117", "encoding117"],
    ),
    (
        ("router117 cluster117 mirror117 filter117 ranking117 encoding117", 10),
        ["router117", "cluster117", "mirror117", "filter117", "ranking117", "encoding117"],
    ),
    (
        ("router117 cluster117 mirror117 filter117 ranking117 encoding117", 18),
        ["router117", "cluster117", "mirror117", "filter117", "ranking117", "encoding117"],
    ),
    (
        ("router117 cluster117 mirror117 filter117 ranking117 encoding117", 28),
        ["router117 cluster117", "mirror117 filter117", "ranking117 encoding117"],
    ),
    (
        ("cluster117 mirror117 filter117 ranking117 encoding117 mapping117", 6),
        ["cluster117", "mirror117", "filter117", "ranking117", "encoding117", "mapping117"],
    ),
    (
        ("cluster117 mirror117 filter117 ranking117 encoding117 mapping117", 10),
        ["cluster117", "mirror117", "filter117", "ranking117", "encoding117", "mapping117"],
    ),
    (
        ("cluster117 mirror117 filter117 ranking117 encoding117 mapping117", 18),
        ["cluster117", "mirror117", "filter117", "ranking117", "encoding117", "mapping117"],
    ),
    (
        ("cluster117 mirror117 filter117 ranking117 encoding117 mapping117", 28),
        ["cluster117 mirror117", "filter117 ranking117", "encoding117 mapping117"],
    ),
    (
        ("mirror117 filter117 ranking117 encoding117 mapping117 record117", 6),
        ["mirror117", "filter117", "ranking117", "encoding117", "mapping117", "record117"],
    ),
    (
        ("mirror117 filter117 ranking117 encoding117 mapping117 record117", 10),
        ["mirror117", "filter117", "ranking117", "encoding117", "mapping117", "record117"],
    ),
    (
        ("mirror117 filter117 ranking117 encoding117 mapping117 record117", 18),
        ["mirror117", "filter117", "ranking117", "encoding117", "mapping117", "record117"],
    ),
    (
        ("mirror117 filter117 ranking117 encoding117 mapping117 record117", 28),
        ["mirror117 filter117", "ranking117 encoding117", "mapping117 record117"],
    ),
    (
        ("filter117 ranking117 encoding117 mapping117 record117 candle117", 6),
        ["filter117", "ranking117", "encoding117", "mapping117", "record117", "candle117"],
    ),
    (
        ("filter117 ranking117 encoding117 mapping117 record117 candle117", 10),
        ["filter117", "ranking117", "encoding117", "mapping117", "record117", "candle117"],
    ),
    (
        ("filter117 ranking117 encoding117 mapping117 record117 candle117", 18),
        ["filter117", "ranking117", "encoding117", "mapping117", "record117", "candle117"],
    ),
    (
        ("filter117 ranking117 encoding117 mapping117 record117 candle117", 28),
        ["filter117 ranking117", "encoding117 mapping117", "record117 candle117"],
    ),
    (
        ("ranking117 encoding117 mapping117 record117 candle117 thread117", 6),
        ["ranking117", "encoding117", "mapping117", "record117", "candle117", "thread117"],
    ),
    (
        ("ranking117 encoding117 mapping117 record117 candle117 thread117", 10),
        ["ranking117", "encoding117", "mapping117", "record117", "candle117", "thread117"],
    ),
    (
        ("ranking117 encoding117 mapping117 record117 candle117 thread117", 18),
        ["ranking117", "encoding117", "mapping117", "record117", "candle117", "thread117"],
    ),
    (
        ("ranking117 encoding117 mapping117 record117 candle117 thread117", 28),
        ["ranking117 encoding117", "mapping117 record117", "candle117 thread117"],
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
