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
        ("round 169: the quick brown fox jumps over the lazy dog", 4),
        ["round", "169:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 169: the quick brown fox jumps over the lazy dog", 8),
        ["round", "169: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 169: the quick brown fox jumps over the lazy dog", 12),
        ["round 169:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 169: the quick brown fox jumps over the lazy dog", 16),
        ["round 169: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 169: the quick brown fox jumps over the lazy dog", 24),
        ["round 169: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 169: the quick brown fox jumps over the lazy dog", 32),
        ["round 169: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 169: agentuniverse is a framework for multi agents", 4),
        ["round", "169:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 169: agentuniverse is a framework for multi agents", 8),
        ["round", "169:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 169: agentuniverse is a framework for multi agents", 12),
        ["round 169:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 169: agentuniverse is a framework for multi agents", 16),
        ["round 169:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 169: agentuniverse is a framework for multi agents", 24),
        ["round 169: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 169: agentuniverse is a framework for multi agents", 32),
        ["round 169: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 169: knowledge stored as vectors enables retrieval", 4),
        ["round", "169:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 169: knowledge stored as vectors enables retrieval", 8),
        ["round", "169:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 169: knowledge stored as vectors enables retrieval", 12),
        ["round 169:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 169: knowledge stored as vectors enables retrieval", 16),
        ["round 169:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 169: knowledge stored as vectors enables retrieval", 24),
        ["round 169: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 169: knowledge stored as vectors enables retrieval", 32),
        ["round 169: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 169: the processor reads the record then stops", 4),
        ["round", "169:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 169: the processor reads the record then stops", 8),
        ["round", "169: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 169: the processor reads the record then stops", 12),
        ["round 169:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 169: the processor reads the record then stops", 16),
        ["round 169: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 169: the processor reads the record then stops", 24),
        ["round 169: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 169: the processor reads the record then stops", 32),
        ["round 169: the processor reads", "the record then stops"],
    ),
    (
        ("round 169: a worker pulls the next task from the queue", 4),
        ["round", "169:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 169: a worker pulls the next task from the queue", 8),
        ["round", "169: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 169: a worker pulls the next task from the queue", 12),
        ["round 169: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 169: a worker pulls the next task from the queue", 16),
        ["round 169: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 169: a worker pulls the next task from the queue", 24),
        ["round 169: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 169: a worker pulls the next task from the queue", 32),
        ["round 169: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 169: signals travel through the network layer", 4),
        ["round", "169:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 169: signals travel through the network layer", 8),
        ["round", "169:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 169: signals travel through the network layer", 12),
        ["round 169:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 169: signals travel through the network layer", 16),
        ["round 169:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 169: signals travel through the network layer", 24),
        ["round 169: signals", "travel through the", "network layer"],
    ),
    (
        ("round 169: signals travel through the network layer", 32),
        ["round 169: signals travel", "through the network layer"],
    ),
    (
        ("round 169: the gateway routes each request by policy", 4),
        ["round", "169:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 169: the gateway routes each request by policy", 8),
        ["round", "169: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 169: the gateway routes each request by policy", 12),
        ["round 169:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 169: the gateway routes each request by policy", 16),
        ["round 169: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 169: the gateway routes each request by policy", 24),
        ["round 169: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 169: the gateway routes each request by policy", 32),
        ["round 169: the gateway routes", "each request by policy"],
    ),
    (
        ("round 169: memory grows until the buffer is full", 4),
        ["round", "169:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 169: memory grows until the buffer is full", 8),
        ["round", "169:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 169: memory grows until the buffer is full", 12),
        ["round 169:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 169: memory grows until the buffer is full", 16),
        ["round 169:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 169: memory grows until the buffer is full", 24), ["round 169: memory grows", "until the buffer is full"]),
    (("round 169: memory grows until the buffer is full", 32), ["round 169: memory grows until", "the buffer is full"]),
    (
        ("round 169: the cluster mirrors every packet twice", 4),
        ["round", "169:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 169: the cluster mirrors every packet twice", 8),
        ["round", "169: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 169: the cluster mirrors every packet twice", 12),
        ["round 169:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 169: the cluster mirrors every packet twice", 16),
        ["round 169: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 169: the cluster mirrors every packet twice", 24),
        ["round 169: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 169: the cluster mirrors every packet twice", 32),
        ["round 169: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 169: ranking uses tokens learned from the corpus", 4),
        ["round", "169:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 169: ranking uses tokens learned from the corpus", 8),
        ["round", "169:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 169: ranking uses tokens learned from the corpus", 12),
        ["round 169:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 169: ranking uses tokens learned from the corpus", 16),
        ["round 169:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 169: ranking uses tokens learned from the corpus", 24),
        ["round 169: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 169: ranking uses tokens learned from the corpus", 32),
        ["round 169: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 169: a long session ends when the candle dies", 4),
        ["round", "169:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 169: a long session ends when the candle dies", 8),
        ["round", "169: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 169: a long session ends when the candle dies", 12),
        ["round 169: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 169: a long session ends when the candle dies", 16),
        ["round 169: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 169: a long session ends when the candle dies", 24),
        ["round 169: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 169: a long session ends when the candle dies", 32),
        ["round 169: a long session ends", "when the candle dies"],
    ),
    (
        ("round 169: encode the prompt then map the result", 4),
        ["round", "169:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 169: encode the prompt then map the result", 8),
        ["round", "169:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 169: encode the prompt then map the result", 12),
        ["round 169:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 169: encode the prompt then map the result", 16),
        ["round 169:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 169: encode the prompt then map the result", 24),
        ["round 169: encode the", "prompt then map the", "result"],
    ),
    (("round 169: encode the prompt then map the result", 32), ["round 169: encode the prompt", "then map the result"]),
    (
        ("round 169: the kernel wakes the worker at dawn", 4),
        ["round", "169:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 169: the kernel wakes the worker at dawn", 8),
        ["round", "169: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 169: the kernel wakes the worker at dawn", 12),
        ["round 169:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 169: the kernel wakes the worker at dawn", 16), ["round 169: the", "kernel wakes the", "worker at dawn"]),
    (("round 169: the kernel wakes the worker at dawn", 24), ["round 169: the kernel", "wakes the worker at dawn"]),
    (("round 169: the kernel wakes the worker at dawn", 32), ["round 169: the kernel wakes the", "worker at dawn"]),
    (
        ("round 169: service latency drops after the patch", 4),
        ["round", "169:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 169: service latency drops after the patch", 8),
        ["round", "169:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 169: service latency drops after the patch", 12),
        ["round 169:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 169: service latency drops after the patch", 16),
        ["round 169:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 169: service latency drops after the patch", 24),
        ["round 169: service", "latency drops after the", "patch"],
    ),
    (("round 169: service latency drops after the patch", 32), ["round 169: service latency drops", "after the patch"]),
    (
        ("round 169: the library caches every vector it sees", 4),
        ["round", "169:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 169: the library caches every vector it sees", 8),
        ["round", "169: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 169: the library caches every vector it sees", 12),
        ["round 169:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 169: the library caches every vector it sees", 16),
        ["round 169: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 169: the library caches every vector it sees", 24),
        ["round 169: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 169: the library caches every vector it sees", 32),
        ["round 169: the library caches", "every vector it sees"],
    ),
    (
        ("round 169: agents argue then the debate resolves", 4),
        ["round", "169:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 169: agents argue then the debate resolves", 8),
        ["round", "169:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 169: agents argue then the debate resolves", 12),
        ["round 169:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 169: agents argue then the debate resolves", 16),
        ["round 169:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 169: agents argue then the debate resolves", 24), ["round 169: agents argue", "then the debate resolves"]),
    (("round 169: agents argue then the debate resolves", 32), ["round 169: agents argue then the", "debate resolves"]),
    (
        ("round 169: the filter keeps only strong matches", 4),
        ["round", "169:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 169: the filter keeps only strong matches", 8),
        ["round", "169: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 169: the filter keeps only strong matches", 12),
        ["round 169:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 169: the filter keeps only strong matches", 16),
        ["round 169: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 169: the filter keeps only strong matches", 24),
        ["round 169: the filter", "keeps only strong", "matches"],
    ),
    (("round 169: the filter keeps only strong matches", 32), ["round 169: the filter keeps only", "strong matches"]),
    (
        ("round 169: the model answers with a short reply", 4),
        ["round", "169:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 169: the model answers with a short reply", 8),
        ["round", "169: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 169: the model answers with a short reply", 12),
        ["round 169:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 169: the model answers with a short reply", 16),
        ["round 169: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 169: the model answers with a short reply", 24),
        ["round 169: the model", "answers with a short", "reply"],
    ),
    (("round 169: the model answers with a short reply", 32), ["round 169: the model answers", "with a short reply"]),
    (
        ("round 169: the recorder stores the reasoning trace", 4),
        ["round", "169:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 169: the recorder stores the reasoning trace", 8),
        ["round", "169: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 169: the recorder stores the reasoning trace", 12),
        ["round 169:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 169: the recorder stores the reasoning trace", 16),
        ["round 169: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 169: the recorder stores the reasoning trace", 24),
        ["round 169: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 169: the recorder stores the reasoning trace", 32),
        ["round 169: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 169: the angel watches the processor run", 4),
        ["round", "169:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 169: the angel watches the processor run", 8),
        ["round", "169: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 169: the angel watches the processor run", 12),
        ["round 169:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 169: the angel watches the processor run", 16),
        ["round 169: the", "angel watches", "the processor", "run"],
    ),
    (("round 169: the angel watches the processor run", 24), ["round 169: the angel", "watches the processor", "run"]),
    (("round 169: the angel watches the processor run", 32), ["round 169: the angel watches the", "processor run"]),
    (
        ("round 169: angle of the vector decides the match", 4),
        ["round", "169:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 169: angle of the vector decides the match", 8),
        ["round", "169:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 169: angle of the vector decides the match", 12),
        ["round 169:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 169: angle of the vector decides the match", 16),
        ["round 169: angle", "of the vector", "decides the", "match"],
    ),
    (("round 169: angle of the vector decides the match", 24), ["round 169: angle of the", "vector decides the match"]),
    (("round 169: angle of the vector decides the match", 32), ["round 169: angle of the vector", "decides the match"]),
    (
        ("round 169: the candle burns twice as long at night", 4),
        ["round", "169:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 169: the candle burns twice as long at night", 8),
        ["round", "169: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 169: the candle burns twice as long at night", 12),
        ["round 169:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 169: the candle burns twice as long at night", 16),
        ["round 169: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 169: the candle burns twice as long at night", 24),
        ["round 169: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 169: the candle burns twice as long at night", 32),
        ["round 169: the candle burns", "twice as long at night"],
    ),
    (
        ("round 169: a mirror of the universe in one line", 4),
        ["round", "169:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 169: a mirror of the universe in one line", 8),
        ["round", "169: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 169: a mirror of the universe in one line", 12),
        ["round 169: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 169: a mirror of the universe in one line", 16),
        ["round 169: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 169: a mirror of the universe in one line", 24), ["round 169: a mirror of", "the universe in one line"]),
    (("round 169: a mirror of the universe in one line", 32), ["round 169: a mirror of the", "universe in one line"]),
    (
        ("round 169: the queue drains before the storm", 4),
        ["round", "169:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 169: the queue drains before the storm", 8),
        ["round", "169: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 169: the queue drains before the storm", 12),
        ["round 169:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 169: the queue drains before the storm", 16), ["round 169: the", "queue drains", "before the storm"]),
    (("round 169: the queue drains before the storm", 24), ["round 169: the queue", "drains before the storm"]),
    (("round 169: the queue drains before the storm", 32), ["round 169: the queue drains", "before the storm"]),
    (
        ("kitten169 sitting169 agent169 angle169 universe169 memory169", 6),
        ["kitten169", "sitting169", "agent169", "angle169", "universe169", "memory169"],
    ),
    (
        ("kitten169 sitting169 agent169 angle169 universe169 memory169", 10),
        ["kitten169", "sitting169", "agent169", "angle169", "universe169", "memory169"],
    ),
    (
        ("kitten169 sitting169 agent169 angle169 universe169 memory169", 18),
        ["kitten169", "sitting169", "agent169 angle169", "universe169", "memory169"],
    ),
    (
        ("kitten169 sitting169 agent169 angle169 universe169 memory169", 28),
        ["kitten169 sitting169", "agent169 angle169", "universe169 memory169"],
    ),
    (
        ("sitting169 agent169 angle169 universe169 memory169 stream169", 6),
        ["sitting169", "agent169", "angle169", "universe169", "memory169", "stream169"],
    ),
    (
        ("sitting169 agent169 angle169 universe169 memory169 stream169", 10),
        ["sitting169", "agent169", "angle169", "universe169", "memory169", "stream169"],
    ),
    (
        ("sitting169 agent169 angle169 universe169 memory169 stream169", 18),
        ["sitting169", "agent169 angle169", "universe169", "memory169", "stream169"],
    ),
    (
        ("sitting169 agent169 angle169 universe169 memory169 stream169", 28),
        ["sitting169 agent169 angle169", "universe169 memory169", "stream169"],
    ),
    (
        ("agent169 angle169 universe169 memory169 stream169 context169", 6),
        ["agent169", "angle169", "universe169", "memory169", "stream169", "context169"],
    ),
    (
        ("agent169 angle169 universe169 memory169 stream169 context169", 10),
        ["agent169", "angle169", "universe169", "memory169", "stream169", "context169"],
    ),
    (
        ("agent169 angle169 universe169 memory169 stream169 context169", 18),
        ["agent169 angle169", "universe169", "memory169", "stream169", "context169"],
    ),
    (
        ("agent169 angle169 universe169 memory169 stream169 context169", 28),
        ["agent169 angle169", "universe169 memory169", "stream169 context169"],
    ),
    (
        ("angle169 universe169 memory169 stream169 context169 knowledge169", 6),
        ["angle169", "universe169", "memory169", "stream169", "context169", "knowledge169"],
    ),
    (
        ("angle169 universe169 memory169 stream169 context169 knowledge169", 10),
        ["angle169", "universe169", "memory169", "stream169", "context169", "knowledge169"],
    ),
    (
        ("angle169 universe169 memory169 stream169 context169 knowledge169", 18),
        ["angle169", "universe169", "memory169", "stream169", "context169", "knowledge169"],
    ),
    (
        ("angle169 universe169 memory169 stream169 context169 knowledge169", 28),
        ["angle169 universe169", "memory169 stream169", "context169 knowledge169"],
    ),
    (
        ("universe169 memory169 stream169 context169 knowledge169 vector169", 6),
        ["universe169", "memory169", "stream169", "context169", "knowledge169", "vector169"],
    ),
    (
        ("universe169 memory169 stream169 context169 knowledge169 vector169", 10),
        ["universe169", "memory169", "stream169", "context169", "knowledge169", "vector169"],
    ),
    (
        ("universe169 memory169 stream169 context169 knowledge169 vector169", 18),
        ["universe169", "memory169", "stream169", "context169", "knowledge169", "vector169"],
    ),
    (
        ("universe169 memory169 stream169 context169 knowledge169 vector169", 28),
        ["universe169 memory169", "stream169 context169", "knowledge169 vector169"],
    ),
    (
        ("memory169 stream169 context169 knowledge169 vector169 processor169", 6),
        ["memory169", "stream169", "context169", "knowledge169", "vector169", "processor169"],
    ),
    (
        ("memory169 stream169 context169 knowledge169 vector169 processor169", 10),
        ["memory169", "stream169", "context169", "knowledge169", "vector169", "processor169"],
    ),
    (
        ("memory169 stream169 context169 knowledge169 vector169 processor169", 18),
        ["memory169", "stream169", "context169", "knowledge169", "vector169", "processor169"],
    ),
    (
        ("memory169 stream169 context169 knowledge169 vector169 processor169", 28),
        ["memory169 stream169", "context169 knowledge169", "vector169 processor169"],
    ),
    (
        ("stream169 context169 knowledge169 vector169 processor169 reasoning169", 6),
        ["stream169", "context169", "knowledge169", "vector169", "processor169", "reasoning169"],
    ),
    (
        ("stream169 context169 knowledge169 vector169 processor169 reasoning169", 10),
        ["stream169", "context169", "knowledge169", "vector169", "processor169", "reasoning169"],
    ),
    (
        ("stream169 context169 knowledge169 vector169 processor169 reasoning169", 18),
        ["stream169", "context169", "knowledge169", "vector169", "processor169", "reasoning169"],
    ),
    (
        ("stream169 context169 knowledge169 vector169 processor169 reasoning169", 28),
        ["stream169 context169", "knowledge169 vector169", "processor169 reasoning169"],
    ),
    (
        ("context169 knowledge169 vector169 processor169 reasoning169 machine169", 6),
        ["context169", "knowledge169", "vector169", "processor169", "reasoning169", "machine169"],
    ),
    (
        ("context169 knowledge169 vector169 processor169 reasoning169 machine169", 10),
        ["context169", "knowledge169", "vector169", "processor169", "reasoning169", "machine169"],
    ),
    (
        ("context169 knowledge169 vector169 processor169 reasoning169 machine169", 18),
        ["context169", "knowledge169", "vector169", "processor169", "reasoning169", "machine169"],
    ),
    (
        ("context169 knowledge169 vector169 processor169 reasoning169 machine169", 28),
        ["context169 knowledge169", "vector169 processor169", "reasoning169 machine169"],
    ),
    (
        ("knowledge169 vector169 processor169 reasoning169 machine169 learning169", 6),
        ["knowledge169", "vector169", "processor169", "reasoning169", "machine169", "learning169"],
    ),
    (
        ("knowledge169 vector169 processor169 reasoning169 machine169 learning169", 10),
        ["knowledge169", "vector169", "processor169", "reasoning169", "machine169", "learning169"],
    ),
    (
        ("knowledge169 vector169 processor169 reasoning169 machine169 learning169", 18),
        ["knowledge169", "vector169", "processor169", "reasoning169", "machine169", "learning169"],
    ),
    (
        ("knowledge169 vector169 processor169 reasoning169 machine169 learning169", 28),
        ["knowledge169 vector169", "processor169 reasoning169", "machine169 learning169"],
    ),
    (
        ("vector169 processor169 reasoning169 machine169 learning169 model169", 6),
        ["vector169", "processor169", "reasoning169", "machine169", "learning169", "model169"],
    ),
    (
        ("vector169 processor169 reasoning169 machine169 learning169 model169", 10),
        ["vector169", "processor169", "reasoning169", "machine169", "learning169", "model169"],
    ),
    (
        ("vector169 processor169 reasoning169 machine169 learning169 model169", 18),
        ["vector169", "processor169", "reasoning169", "machine169", "learning169", "model169"],
    ),
    (
        ("vector169 processor169 reasoning169 machine169 learning169 model169", 28),
        ["vector169 processor169", "reasoning169 machine169", "learning169 model169"],
    ),
    (
        ("processor169 reasoning169 machine169 learning169 model169 token169", 6),
        ["processor169", "reasoning169", "machine169", "learning169", "model169", "token169"],
    ),
    (
        ("processor169 reasoning169 machine169 learning169 model169 token169", 10),
        ["processor169", "reasoning169", "machine169", "learning169", "model169", "token169"],
    ),
    (
        ("processor169 reasoning169 machine169 learning169 model169 token169", 18),
        ["processor169", "reasoning169", "machine169", "learning169", "model169 token169"],
    ),
    (
        ("processor169 reasoning169 machine169 learning169 model169 token169", 28),
        ["processor169 reasoning169", "machine169 learning169", "model169 token169"],
    ),
    (
        ("reasoning169 machine169 learning169 model169 token169 prompt169", 6),
        ["reasoning169", "machine169", "learning169", "model169", "token169", "prompt169"],
    ),
    (
        ("reasoning169 machine169 learning169 model169 token169 prompt169", 10),
        ["reasoning169", "machine169", "learning169", "model169", "token169", "prompt169"],
    ),
    (
        ("reasoning169 machine169 learning169 model169 token169 prompt169", 18),
        ["reasoning169", "machine169", "learning169", "model169 token169", "prompt169"],
    ),
    (
        ("reasoning169 machine169 learning169 model169 token169 prompt169", 28),
        ["reasoning169 machine169", "learning169 model169", "token169 prompt169"],
    ),
    (
        ("machine169 learning169 model169 token169 prompt169 session169", 6),
        ["machine169", "learning169", "model169", "token169", "prompt169", "session169"],
    ),
    (
        ("machine169 learning169 model169 token169 prompt169 session169", 10),
        ["machine169", "learning169", "model169", "token169", "prompt169", "session169"],
    ),
    (
        ("machine169 learning169 model169 token169 prompt169 session169", 18),
        ["machine169", "learning169", "model169 token169", "prompt169", "session169"],
    ),
    (
        ("machine169 learning169 model169 token169 prompt169 session169", 28),
        ["machine169 learning169", "model169 token169 prompt169", "session169"],
    ),
    (
        ("learning169 model169 token169 prompt169 session169 library169", 6),
        ["learning169", "model169", "token169", "prompt169", "session169", "library169"],
    ),
    (
        ("learning169 model169 token169 prompt169 session169 library169", 10),
        ["learning169", "model169", "token169", "prompt169", "session169", "library169"],
    ),
    (
        ("learning169 model169 token169 prompt169 session169 library169", 18),
        ["learning169", "model169 token169", "prompt169", "session169", "library169"],
    ),
    (
        ("learning169 model169 token169 prompt169 session169 library169", 28),
        ["learning169 model169", "token169 prompt169", "session169 library169"],
    ),
    (
        ("model169 token169 prompt169 session169 library169 service169", 6),
        ["model169", "token169", "prompt169", "session169", "library169", "service169"],
    ),
    (
        ("model169 token169 prompt169 session169 library169 service169", 10),
        ["model169", "token169", "prompt169", "session169", "library169", "service169"],
    ),
    (
        ("model169 token169 prompt169 session169 library169 service169", 18),
        ["model169 token169", "prompt169", "session169", "library169", "service169"],
    ),
    (
        ("model169 token169 prompt169 session169 library169 service169", 28),
        ["model169 token169 prompt169", "session169 library169", "service169"],
    ),
    (
        ("token169 prompt169 session169 library169 service169 gateway169", 6),
        ["token169", "prompt169", "session169", "library169", "service169", "gateway169"],
    ),
    (
        ("token169 prompt169 session169 library169 service169 gateway169", 10),
        ["token169", "prompt169", "session169", "library169", "service169", "gateway169"],
    ),
    (
        ("token169 prompt169 session169 library169 service169 gateway169", 18),
        ["token169 prompt169", "session169", "library169", "service169", "gateway169"],
    ),
    (
        ("token169 prompt169 session169 library169 service169 gateway169", 28),
        ["token169 prompt169", "session169 library169", "service169 gateway169"],
    ),
    (
        ("prompt169 session169 library169 service169 gateway169 storage169", 6),
        ["prompt169", "session169", "library169", "service169", "gateway169", "storage169"],
    ),
    (
        ("prompt169 session169 library169 service169 gateway169 storage169", 10),
        ["prompt169", "session169", "library169", "service169", "gateway169", "storage169"],
    ),
    (
        ("prompt169 session169 library169 service169 gateway169 storage169", 18),
        ["prompt169", "session169", "library169", "service169", "gateway169", "storage169"],
    ),
    (
        ("prompt169 session169 library169 service169 gateway169 storage169", 28),
        ["prompt169 session169", "library169 service169", "gateway169 storage169"],
    ),
    (
        ("session169 library169 service169 gateway169 storage169 network169", 6),
        ["session169", "library169", "service169", "gateway169", "storage169", "network169"],
    ),
    (
        ("session169 library169 service169 gateway169 storage169 network169", 10),
        ["session169", "library169", "service169", "gateway169", "storage169", "network169"],
    ),
    (
        ("session169 library169 service169 gateway169 storage169 network169", 18),
        ["session169", "library169", "service169", "gateway169", "storage169", "network169"],
    ),
    (
        ("session169 library169 service169 gateway169 storage169 network169", 28),
        ["session169 library169", "service169 gateway169", "storage169 network169"],
    ),
    (
        ("library169 service169 gateway169 storage169 network169 latency169", 6),
        ["library169", "service169", "gateway169", "storage169", "network169", "latency169"],
    ),
    (
        ("library169 service169 gateway169 storage169 network169 latency169", 10),
        ["library169", "service169", "gateway169", "storage169", "network169", "latency169"],
    ),
    (
        ("library169 service169 gateway169 storage169 network169 latency169", 18),
        ["library169", "service169", "gateway169", "storage169", "network169", "latency169"],
    ),
    (
        ("library169 service169 gateway169 storage169 network169 latency169", 28),
        ["library169 service169", "gateway169 storage169", "network169 latency169"],
    ),
    (
        ("service169 gateway169 storage169 network169 latency169 buffer169", 6),
        ["service169", "gateway169", "storage169", "network169", "latency169", "buffer169"],
    ),
    (
        ("service169 gateway169 storage169 network169 latency169 buffer169", 10),
        ["service169", "gateway169", "storage169", "network169", "latency169", "buffer169"],
    ),
    (
        ("service169 gateway169 storage169 network169 latency169 buffer169", 18),
        ["service169", "gateway169", "storage169", "network169", "latency169", "buffer169"],
    ),
    (
        ("service169 gateway169 storage169 network169 latency169 buffer169", 28),
        ["service169 gateway169", "storage169 network169", "latency169 buffer169"],
    ),
    (
        ("gateway169 storage169 network169 latency169 buffer169 queue169", 6),
        ["gateway169", "storage169", "network169", "latency169", "buffer169", "queue169"],
    ),
    (
        ("gateway169 storage169 network169 latency169 buffer169 queue169", 10),
        ["gateway169", "storage169", "network169", "latency169", "buffer169", "queue169"],
    ),
    (
        ("gateway169 storage169 network169 latency169 buffer169 queue169", 18),
        ["gateway169", "storage169", "network169", "latency169", "buffer169 queue169"],
    ),
    (
        ("gateway169 storage169 network169 latency169 buffer169 queue169", 28),
        ["gateway169 storage169", "network169 latency169", "buffer169 queue169"],
    ),
    (
        ("storage169 network169 latency169 buffer169 queue169 worker169", 6),
        ["storage169", "network169", "latency169", "buffer169", "queue169", "worker169"],
    ),
    (
        ("storage169 network169 latency169 buffer169 queue169 worker169", 10),
        ["storage169", "network169", "latency169", "buffer169", "queue169", "worker169"],
    ),
    (
        ("storage169 network169 latency169 buffer169 queue169 worker169", 18),
        ["storage169", "network169", "latency169", "buffer169 queue169", "worker169"],
    ),
    (
        ("storage169 network169 latency169 buffer169 queue169 worker169", 28),
        ["storage169 network169", "latency169 buffer169", "queue169 worker169"],
    ),
    (
        ("network169 latency169 buffer169 queue169 worker169 kernel169", 6),
        ["network169", "latency169", "buffer169", "queue169", "worker169", "kernel169"],
    ),
    (
        ("network169 latency169 buffer169 queue169 worker169 kernel169", 10),
        ["network169", "latency169", "buffer169", "queue169", "worker169", "kernel169"],
    ),
    (
        ("network169 latency169 buffer169 queue169 worker169 kernel169", 18),
        ["network169", "latency169", "buffer169 queue169", "worker169", "kernel169"],
    ),
    (
        ("network169 latency169 buffer169 queue169 worker169 kernel169", 28),
        ["network169 latency169", "buffer169 queue169 worker169", "kernel169"],
    ),
    (
        ("latency169 buffer169 queue169 worker169 kernel169 signal169", 6),
        ["latency169", "buffer169", "queue169", "worker169", "kernel169", "signal169"],
    ),
    (
        ("latency169 buffer169 queue169 worker169 kernel169 signal169", 10),
        ["latency169", "buffer169", "queue169", "worker169", "kernel169", "signal169"],
    ),
    (
        ("latency169 buffer169 queue169 worker169 kernel169 signal169", 18),
        ["latency169", "buffer169 queue169", "worker169", "kernel169", "signal169"],
    ),
    (
        ("latency169 buffer169 queue169 worker169 kernel169 signal169", 28),
        ["latency169 buffer169", "queue169 worker169 kernel169", "signal169"],
    ),
    (
        ("buffer169 queue169 worker169 kernel169 signal169 packet169", 6),
        ["buffer169", "queue169", "worker169", "kernel169", "signal169", "packet169"],
    ),
    (
        ("buffer169 queue169 worker169 kernel169 signal169 packet169", 10),
        ["buffer169", "queue169", "worker169", "kernel169", "signal169", "packet169"],
    ),
    (
        ("buffer169 queue169 worker169 kernel169 signal169 packet169", 18),
        ["buffer169 queue169", "worker169", "kernel169", "signal169", "packet169"],
    ),
    (
        ("buffer169 queue169 worker169 kernel169 signal169 packet169", 28),
        ["buffer169 queue169 worker169", "kernel169 signal169", "packet169"],
    ),
    (
        ("queue169 worker169 kernel169 signal169 packet169 router169", 6),
        ["queue169", "worker169", "kernel169", "signal169", "packet169", "router169"],
    ),
    (
        ("queue169 worker169 kernel169 signal169 packet169 router169", 10),
        ["queue169", "worker169", "kernel169", "signal169", "packet169", "router169"],
    ),
    (
        ("queue169 worker169 kernel169 signal169 packet169 router169", 18),
        ["queue169 worker169", "kernel169", "signal169", "packet169", "router169"],
    ),
    (
        ("queue169 worker169 kernel169 signal169 packet169 router169", 28),
        ["queue169 worker169 kernel169", "signal169 packet169", "router169"],
    ),
    (
        ("worker169 kernel169 signal169 packet169 router169 cluster169", 6),
        ["worker169", "kernel169", "signal169", "packet169", "router169", "cluster169"],
    ),
    (
        ("worker169 kernel169 signal169 packet169 router169 cluster169", 10),
        ["worker169", "kernel169", "signal169", "packet169", "router169", "cluster169"],
    ),
    (
        ("worker169 kernel169 signal169 packet169 router169 cluster169", 18),
        ["worker169", "kernel169", "signal169", "packet169", "router169", "cluster169"],
    ),
    (
        ("worker169 kernel169 signal169 packet169 router169 cluster169", 28),
        ["worker169 kernel169", "signal169 packet169", "router169 cluster169"],
    ),
    (
        ("kernel169 signal169 packet169 router169 cluster169 mirror169", 6),
        ["kernel169", "signal169", "packet169", "router169", "cluster169", "mirror169"],
    ),
    (
        ("kernel169 signal169 packet169 router169 cluster169 mirror169", 10),
        ["kernel169", "signal169", "packet169", "router169", "cluster169", "mirror169"],
    ),
    (
        ("kernel169 signal169 packet169 router169 cluster169 mirror169", 18),
        ["kernel169", "signal169", "packet169", "router169", "cluster169", "mirror169"],
    ),
    (
        ("kernel169 signal169 packet169 router169 cluster169 mirror169", 28),
        ["kernel169 signal169", "packet169 router169", "cluster169 mirror169"],
    ),
    (
        ("signal169 packet169 router169 cluster169 mirror169 filter169", 6),
        ["signal169", "packet169", "router169", "cluster169", "mirror169", "filter169"],
    ),
    (
        ("signal169 packet169 router169 cluster169 mirror169 filter169", 10),
        ["signal169", "packet169", "router169", "cluster169", "mirror169", "filter169"],
    ),
    (
        ("signal169 packet169 router169 cluster169 mirror169 filter169", 18),
        ["signal169", "packet169", "router169", "cluster169", "mirror169", "filter169"],
    ),
    (
        ("signal169 packet169 router169 cluster169 mirror169 filter169", 28),
        ["signal169 packet169", "router169 cluster169", "mirror169 filter169"],
    ),
    (
        ("packet169 router169 cluster169 mirror169 filter169 ranking169", 6),
        ["packet169", "router169", "cluster169", "mirror169", "filter169", "ranking169"],
    ),
    (
        ("packet169 router169 cluster169 mirror169 filter169 ranking169", 10),
        ["packet169", "router169", "cluster169", "mirror169", "filter169", "ranking169"],
    ),
    (
        ("packet169 router169 cluster169 mirror169 filter169 ranking169", 18),
        ["packet169", "router169", "cluster169", "mirror169", "filter169", "ranking169"],
    ),
    (
        ("packet169 router169 cluster169 mirror169 filter169 ranking169", 28),
        ["packet169 router169", "cluster169 mirror169", "filter169 ranking169"],
    ),
    (
        ("router169 cluster169 mirror169 filter169 ranking169 encoding169", 6),
        ["router169", "cluster169", "mirror169", "filter169", "ranking169", "encoding169"],
    ),
    (
        ("router169 cluster169 mirror169 filter169 ranking169 encoding169", 10),
        ["router169", "cluster169", "mirror169", "filter169", "ranking169", "encoding169"],
    ),
    (
        ("router169 cluster169 mirror169 filter169 ranking169 encoding169", 18),
        ["router169", "cluster169", "mirror169", "filter169", "ranking169", "encoding169"],
    ),
    (
        ("router169 cluster169 mirror169 filter169 ranking169 encoding169", 28),
        ["router169 cluster169", "mirror169 filter169", "ranking169 encoding169"],
    ),
    (
        ("cluster169 mirror169 filter169 ranking169 encoding169 mapping169", 6),
        ["cluster169", "mirror169", "filter169", "ranking169", "encoding169", "mapping169"],
    ),
    (
        ("cluster169 mirror169 filter169 ranking169 encoding169 mapping169", 10),
        ["cluster169", "mirror169", "filter169", "ranking169", "encoding169", "mapping169"],
    ),
    (
        ("cluster169 mirror169 filter169 ranking169 encoding169 mapping169", 18),
        ["cluster169", "mirror169", "filter169", "ranking169", "encoding169", "mapping169"],
    ),
    (
        ("cluster169 mirror169 filter169 ranking169 encoding169 mapping169", 28),
        ["cluster169 mirror169", "filter169 ranking169", "encoding169 mapping169"],
    ),
    (
        ("mirror169 filter169 ranking169 encoding169 mapping169 record169", 6),
        ["mirror169", "filter169", "ranking169", "encoding169", "mapping169", "record169"],
    ),
    (
        ("mirror169 filter169 ranking169 encoding169 mapping169 record169", 10),
        ["mirror169", "filter169", "ranking169", "encoding169", "mapping169", "record169"],
    ),
    (
        ("mirror169 filter169 ranking169 encoding169 mapping169 record169", 18),
        ["mirror169", "filter169", "ranking169", "encoding169", "mapping169", "record169"],
    ),
    (
        ("mirror169 filter169 ranking169 encoding169 mapping169 record169", 28),
        ["mirror169 filter169", "ranking169 encoding169", "mapping169 record169"],
    ),
    (
        ("filter169 ranking169 encoding169 mapping169 record169 candle169", 6),
        ["filter169", "ranking169", "encoding169", "mapping169", "record169", "candle169"],
    ),
    (
        ("filter169 ranking169 encoding169 mapping169 record169 candle169", 10),
        ["filter169", "ranking169", "encoding169", "mapping169", "record169", "candle169"],
    ),
    (
        ("filter169 ranking169 encoding169 mapping169 record169 candle169", 18),
        ["filter169", "ranking169", "encoding169", "mapping169", "record169", "candle169"],
    ),
    (
        ("filter169 ranking169 encoding169 mapping169 record169 candle169", 28),
        ["filter169 ranking169", "encoding169 mapping169", "record169 candle169"],
    ),
    (
        ("ranking169 encoding169 mapping169 record169 candle169 thread169", 6),
        ["ranking169", "encoding169", "mapping169", "record169", "candle169", "thread169"],
    ),
    (
        ("ranking169 encoding169 mapping169 record169 candle169 thread169", 10),
        ["ranking169", "encoding169", "mapping169", "record169", "candle169", "thread169"],
    ),
    (
        ("ranking169 encoding169 mapping169 record169 candle169 thread169", 18),
        ["ranking169", "encoding169", "mapping169", "record169", "candle169", "thread169"],
    ),
    (
        ("ranking169 encoding169 mapping169 record169 candle169 thread169", 28),
        ["ranking169 encoding169", "mapping169 record169", "candle169 thread169"],
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
