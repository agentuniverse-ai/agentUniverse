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
        ("round 105: the quick brown fox jumps over the lazy dog", 4),
        ["round", "105:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 105: the quick brown fox jumps over the lazy dog", 8),
        ["round", "105: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 105: the quick brown fox jumps over the lazy dog", 12),
        ["round 105:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 105: the quick brown fox jumps over the lazy dog", 16),
        ["round 105: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 105: the quick brown fox jumps over the lazy dog", 24),
        ["round 105: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 105: the quick brown fox jumps over the lazy dog", 32),
        ["round 105: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 105: agentuniverse is a framework for multi agents", 4),
        ["round", "105:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 105: agentuniverse is a framework for multi agents", 8),
        ["round", "105:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 105: agentuniverse is a framework for multi agents", 12),
        ["round 105:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 105: agentuniverse is a framework for multi agents", 16),
        ["round 105:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 105: agentuniverse is a framework for multi agents", 24),
        ["round 105: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 105: agentuniverse is a framework for multi agents", 32),
        ["round 105: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 105: knowledge stored as vectors enables retrieval", 4),
        ["round", "105:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 105: knowledge stored as vectors enables retrieval", 8),
        ["round", "105:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 105: knowledge stored as vectors enables retrieval", 12),
        ["round 105:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 105: knowledge stored as vectors enables retrieval", 16),
        ["round 105:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 105: knowledge stored as vectors enables retrieval", 24),
        ["round 105: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 105: knowledge stored as vectors enables retrieval", 32),
        ["round 105: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 105: the processor reads the record then stops", 4),
        ["round", "105:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 105: the processor reads the record then stops", 8),
        ["round", "105: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 105: the processor reads the record then stops", 12),
        ["round 105:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 105: the processor reads the record then stops", 16),
        ["round 105: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 105: the processor reads the record then stops", 24),
        ["round 105: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 105: the processor reads the record then stops", 32),
        ["round 105: the processor reads", "the record then stops"],
    ),
    (
        ("round 105: a worker pulls the next task from the queue", 4),
        ["round", "105:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 105: a worker pulls the next task from the queue", 8),
        ["round", "105: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 105: a worker pulls the next task from the queue", 12),
        ["round 105: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 105: a worker pulls the next task from the queue", 16),
        ["round 105: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 105: a worker pulls the next task from the queue", 24),
        ["round 105: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 105: a worker pulls the next task from the queue", 32),
        ["round 105: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 105: signals travel through the network layer", 4),
        ["round", "105:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 105: signals travel through the network layer", 8),
        ["round", "105:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 105: signals travel through the network layer", 12),
        ["round 105:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 105: signals travel through the network layer", 16),
        ["round 105:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 105: signals travel through the network layer", 24),
        ["round 105: signals", "travel through the", "network layer"],
    ),
    (
        ("round 105: signals travel through the network layer", 32),
        ["round 105: signals travel", "through the network layer"],
    ),
    (
        ("round 105: the gateway routes each request by policy", 4),
        ["round", "105:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 105: the gateway routes each request by policy", 8),
        ["round", "105: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 105: the gateway routes each request by policy", 12),
        ["round 105:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 105: the gateway routes each request by policy", 16),
        ["round 105: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 105: the gateway routes each request by policy", 24),
        ["round 105: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 105: the gateway routes each request by policy", 32),
        ["round 105: the gateway routes", "each request by policy"],
    ),
    (
        ("round 105: memory grows until the buffer is full", 4),
        ["round", "105:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 105: memory grows until the buffer is full", 8),
        ["round", "105:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 105: memory grows until the buffer is full", 12),
        ["round 105:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 105: memory grows until the buffer is full", 16),
        ["round 105:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 105: memory grows until the buffer is full", 24), ["round 105: memory grows", "until the buffer is full"]),
    (("round 105: memory grows until the buffer is full", 32), ["round 105: memory grows until", "the buffer is full"]),
    (
        ("round 105: the cluster mirrors every packet twice", 4),
        ["round", "105:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 105: the cluster mirrors every packet twice", 8),
        ["round", "105: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 105: the cluster mirrors every packet twice", 12),
        ["round 105:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 105: the cluster mirrors every packet twice", 16),
        ["round 105: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 105: the cluster mirrors every packet twice", 24),
        ["round 105: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 105: the cluster mirrors every packet twice", 32),
        ["round 105: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 105: ranking uses tokens learned from the corpus", 4),
        ["round", "105:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 105: ranking uses tokens learned from the corpus", 8),
        ["round", "105:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 105: ranking uses tokens learned from the corpus", 12),
        ["round 105:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 105: ranking uses tokens learned from the corpus", 16),
        ["round 105:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 105: ranking uses tokens learned from the corpus", 24),
        ["round 105: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 105: ranking uses tokens learned from the corpus", 32),
        ["round 105: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 105: a long session ends when the candle dies", 4),
        ["round", "105:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 105: a long session ends when the candle dies", 8),
        ["round", "105: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 105: a long session ends when the candle dies", 12),
        ["round 105: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 105: a long session ends when the candle dies", 16),
        ["round 105: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 105: a long session ends when the candle dies", 24),
        ["round 105: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 105: a long session ends when the candle dies", 32),
        ["round 105: a long session ends", "when the candle dies"],
    ),
    (
        ("round 105: encode the prompt then map the result", 4),
        ["round", "105:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 105: encode the prompt then map the result", 8),
        ["round", "105:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 105: encode the prompt then map the result", 12),
        ["round 105:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 105: encode the prompt then map the result", 16),
        ["round 105:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 105: encode the prompt then map the result", 24),
        ["round 105: encode the", "prompt then map the", "result"],
    ),
    (("round 105: encode the prompt then map the result", 32), ["round 105: encode the prompt", "then map the result"]),
    (
        ("round 105: the kernel wakes the worker at dawn", 4),
        ["round", "105:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 105: the kernel wakes the worker at dawn", 8),
        ["round", "105: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 105: the kernel wakes the worker at dawn", 12),
        ["round 105:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 105: the kernel wakes the worker at dawn", 16), ["round 105: the", "kernel wakes the", "worker at dawn"]),
    (("round 105: the kernel wakes the worker at dawn", 24), ["round 105: the kernel", "wakes the worker at dawn"]),
    (("round 105: the kernel wakes the worker at dawn", 32), ["round 105: the kernel wakes the", "worker at dawn"]),
    (
        ("round 105: service latency drops after the patch", 4),
        ["round", "105:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 105: service latency drops after the patch", 8),
        ["round", "105:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 105: service latency drops after the patch", 12),
        ["round 105:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 105: service latency drops after the patch", 16),
        ["round 105:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 105: service latency drops after the patch", 24),
        ["round 105: service", "latency drops after the", "patch"],
    ),
    (("round 105: service latency drops after the patch", 32), ["round 105: service latency drops", "after the patch"]),
    (
        ("round 105: the library caches every vector it sees", 4),
        ["round", "105:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 105: the library caches every vector it sees", 8),
        ["round", "105: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 105: the library caches every vector it sees", 12),
        ["round 105:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 105: the library caches every vector it sees", 16),
        ["round 105: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 105: the library caches every vector it sees", 24),
        ["round 105: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 105: the library caches every vector it sees", 32),
        ["round 105: the library caches", "every vector it sees"],
    ),
    (
        ("round 105: agents argue then the debate resolves", 4),
        ["round", "105:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 105: agents argue then the debate resolves", 8),
        ["round", "105:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 105: agents argue then the debate resolves", 12),
        ["round 105:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 105: agents argue then the debate resolves", 16),
        ["round 105:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 105: agents argue then the debate resolves", 24), ["round 105: agents argue", "then the debate resolves"]),
    (("round 105: agents argue then the debate resolves", 32), ["round 105: agents argue then the", "debate resolves"]),
    (
        ("round 105: the filter keeps only strong matches", 4),
        ["round", "105:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 105: the filter keeps only strong matches", 8),
        ["round", "105: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 105: the filter keeps only strong matches", 12),
        ["round 105:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 105: the filter keeps only strong matches", 16),
        ["round 105: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 105: the filter keeps only strong matches", 24),
        ["round 105: the filter", "keeps only strong", "matches"],
    ),
    (("round 105: the filter keeps only strong matches", 32), ["round 105: the filter keeps only", "strong matches"]),
    (
        ("round 105: the model answers with a short reply", 4),
        ["round", "105:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 105: the model answers with a short reply", 8),
        ["round", "105: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 105: the model answers with a short reply", 12),
        ["round 105:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 105: the model answers with a short reply", 16),
        ["round 105: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 105: the model answers with a short reply", 24),
        ["round 105: the model", "answers with a short", "reply"],
    ),
    (("round 105: the model answers with a short reply", 32), ["round 105: the model answers", "with a short reply"]),
    (
        ("round 105: the recorder stores the reasoning trace", 4),
        ["round", "105:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 105: the recorder stores the reasoning trace", 8),
        ["round", "105: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 105: the recorder stores the reasoning trace", 12),
        ["round 105:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 105: the recorder stores the reasoning trace", 16),
        ["round 105: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 105: the recorder stores the reasoning trace", 24),
        ["round 105: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 105: the recorder stores the reasoning trace", 32),
        ["round 105: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 105: the angel watches the processor run", 4),
        ["round", "105:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 105: the angel watches the processor run", 8),
        ["round", "105: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 105: the angel watches the processor run", 12),
        ["round 105:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 105: the angel watches the processor run", 16),
        ["round 105: the", "angel watches", "the processor", "run"],
    ),
    (("round 105: the angel watches the processor run", 24), ["round 105: the angel", "watches the processor", "run"]),
    (("round 105: the angel watches the processor run", 32), ["round 105: the angel watches the", "processor run"]),
    (
        ("round 105: angle of the vector decides the match", 4),
        ["round", "105:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 105: angle of the vector decides the match", 8),
        ["round", "105:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 105: angle of the vector decides the match", 12),
        ["round 105:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 105: angle of the vector decides the match", 16),
        ["round 105: angle", "of the vector", "decides the", "match"],
    ),
    (("round 105: angle of the vector decides the match", 24), ["round 105: angle of the", "vector decides the match"]),
    (("round 105: angle of the vector decides the match", 32), ["round 105: angle of the vector", "decides the match"]),
    (
        ("round 105: the candle burns twice as long at night", 4),
        ["round", "105:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 105: the candle burns twice as long at night", 8),
        ["round", "105: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 105: the candle burns twice as long at night", 12),
        ["round 105:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 105: the candle burns twice as long at night", 16),
        ["round 105: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 105: the candle burns twice as long at night", 24),
        ["round 105: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 105: the candle burns twice as long at night", 32),
        ["round 105: the candle burns", "twice as long at night"],
    ),
    (
        ("round 105: a mirror of the universe in one line", 4),
        ["round", "105:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 105: a mirror of the universe in one line", 8),
        ["round", "105: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 105: a mirror of the universe in one line", 12),
        ["round 105: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 105: a mirror of the universe in one line", 16),
        ["round 105: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 105: a mirror of the universe in one line", 24), ["round 105: a mirror of", "the universe in one line"]),
    (("round 105: a mirror of the universe in one line", 32), ["round 105: a mirror of the", "universe in one line"]),
    (
        ("round 105: the queue drains before the storm", 4),
        ["round", "105:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 105: the queue drains before the storm", 8),
        ["round", "105: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 105: the queue drains before the storm", 12),
        ["round 105:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 105: the queue drains before the storm", 16), ["round 105: the", "queue drains", "before the storm"]),
    (("round 105: the queue drains before the storm", 24), ["round 105: the queue", "drains before the storm"]),
    (("round 105: the queue drains before the storm", 32), ["round 105: the queue drains", "before the storm"]),
    (
        ("kitten105 sitting105 agent105 angle105 universe105 memory105", 6),
        ["kitten105", "sitting105", "agent105", "angle105", "universe105", "memory105"],
    ),
    (
        ("kitten105 sitting105 agent105 angle105 universe105 memory105", 10),
        ["kitten105", "sitting105", "agent105", "angle105", "universe105", "memory105"],
    ),
    (
        ("kitten105 sitting105 agent105 angle105 universe105 memory105", 18),
        ["kitten105", "sitting105", "agent105 angle105", "universe105", "memory105"],
    ),
    (
        ("kitten105 sitting105 agent105 angle105 universe105 memory105", 28),
        ["kitten105 sitting105", "agent105 angle105", "universe105 memory105"],
    ),
    (
        ("sitting105 agent105 angle105 universe105 memory105 stream105", 6),
        ["sitting105", "agent105", "angle105", "universe105", "memory105", "stream105"],
    ),
    (
        ("sitting105 agent105 angle105 universe105 memory105 stream105", 10),
        ["sitting105", "agent105", "angle105", "universe105", "memory105", "stream105"],
    ),
    (
        ("sitting105 agent105 angle105 universe105 memory105 stream105", 18),
        ["sitting105", "agent105 angle105", "universe105", "memory105", "stream105"],
    ),
    (
        ("sitting105 agent105 angle105 universe105 memory105 stream105", 28),
        ["sitting105 agent105 angle105", "universe105 memory105", "stream105"],
    ),
    (
        ("agent105 angle105 universe105 memory105 stream105 context105", 6),
        ["agent105", "angle105", "universe105", "memory105", "stream105", "context105"],
    ),
    (
        ("agent105 angle105 universe105 memory105 stream105 context105", 10),
        ["agent105", "angle105", "universe105", "memory105", "stream105", "context105"],
    ),
    (
        ("agent105 angle105 universe105 memory105 stream105 context105", 18),
        ["agent105 angle105", "universe105", "memory105", "stream105", "context105"],
    ),
    (
        ("agent105 angle105 universe105 memory105 stream105 context105", 28),
        ["agent105 angle105", "universe105 memory105", "stream105 context105"],
    ),
    (
        ("angle105 universe105 memory105 stream105 context105 knowledge105", 6),
        ["angle105", "universe105", "memory105", "stream105", "context105", "knowledge105"],
    ),
    (
        ("angle105 universe105 memory105 stream105 context105 knowledge105", 10),
        ["angle105", "universe105", "memory105", "stream105", "context105", "knowledge105"],
    ),
    (
        ("angle105 universe105 memory105 stream105 context105 knowledge105", 18),
        ["angle105", "universe105", "memory105", "stream105", "context105", "knowledge105"],
    ),
    (
        ("angle105 universe105 memory105 stream105 context105 knowledge105", 28),
        ["angle105 universe105", "memory105 stream105", "context105 knowledge105"],
    ),
    (
        ("universe105 memory105 stream105 context105 knowledge105 vector105", 6),
        ["universe105", "memory105", "stream105", "context105", "knowledge105", "vector105"],
    ),
    (
        ("universe105 memory105 stream105 context105 knowledge105 vector105", 10),
        ["universe105", "memory105", "stream105", "context105", "knowledge105", "vector105"],
    ),
    (
        ("universe105 memory105 stream105 context105 knowledge105 vector105", 18),
        ["universe105", "memory105", "stream105", "context105", "knowledge105", "vector105"],
    ),
    (
        ("universe105 memory105 stream105 context105 knowledge105 vector105", 28),
        ["universe105 memory105", "stream105 context105", "knowledge105 vector105"],
    ),
    (
        ("memory105 stream105 context105 knowledge105 vector105 processor105", 6),
        ["memory105", "stream105", "context105", "knowledge105", "vector105", "processor105"],
    ),
    (
        ("memory105 stream105 context105 knowledge105 vector105 processor105", 10),
        ["memory105", "stream105", "context105", "knowledge105", "vector105", "processor105"],
    ),
    (
        ("memory105 stream105 context105 knowledge105 vector105 processor105", 18),
        ["memory105", "stream105", "context105", "knowledge105", "vector105", "processor105"],
    ),
    (
        ("memory105 stream105 context105 knowledge105 vector105 processor105", 28),
        ["memory105 stream105", "context105 knowledge105", "vector105 processor105"],
    ),
    (
        ("stream105 context105 knowledge105 vector105 processor105 reasoning105", 6),
        ["stream105", "context105", "knowledge105", "vector105", "processor105", "reasoning105"],
    ),
    (
        ("stream105 context105 knowledge105 vector105 processor105 reasoning105", 10),
        ["stream105", "context105", "knowledge105", "vector105", "processor105", "reasoning105"],
    ),
    (
        ("stream105 context105 knowledge105 vector105 processor105 reasoning105", 18),
        ["stream105", "context105", "knowledge105", "vector105", "processor105", "reasoning105"],
    ),
    (
        ("stream105 context105 knowledge105 vector105 processor105 reasoning105", 28),
        ["stream105 context105", "knowledge105 vector105", "processor105 reasoning105"],
    ),
    (
        ("context105 knowledge105 vector105 processor105 reasoning105 machine105", 6),
        ["context105", "knowledge105", "vector105", "processor105", "reasoning105", "machine105"],
    ),
    (
        ("context105 knowledge105 vector105 processor105 reasoning105 machine105", 10),
        ["context105", "knowledge105", "vector105", "processor105", "reasoning105", "machine105"],
    ),
    (
        ("context105 knowledge105 vector105 processor105 reasoning105 machine105", 18),
        ["context105", "knowledge105", "vector105", "processor105", "reasoning105", "machine105"],
    ),
    (
        ("context105 knowledge105 vector105 processor105 reasoning105 machine105", 28),
        ["context105 knowledge105", "vector105 processor105", "reasoning105 machine105"],
    ),
    (
        ("knowledge105 vector105 processor105 reasoning105 machine105 learning105", 6),
        ["knowledge105", "vector105", "processor105", "reasoning105", "machine105", "learning105"],
    ),
    (
        ("knowledge105 vector105 processor105 reasoning105 machine105 learning105", 10),
        ["knowledge105", "vector105", "processor105", "reasoning105", "machine105", "learning105"],
    ),
    (
        ("knowledge105 vector105 processor105 reasoning105 machine105 learning105", 18),
        ["knowledge105", "vector105", "processor105", "reasoning105", "machine105", "learning105"],
    ),
    (
        ("knowledge105 vector105 processor105 reasoning105 machine105 learning105", 28),
        ["knowledge105 vector105", "processor105 reasoning105", "machine105 learning105"],
    ),
    (
        ("vector105 processor105 reasoning105 machine105 learning105 model105", 6),
        ["vector105", "processor105", "reasoning105", "machine105", "learning105", "model105"],
    ),
    (
        ("vector105 processor105 reasoning105 machine105 learning105 model105", 10),
        ["vector105", "processor105", "reasoning105", "machine105", "learning105", "model105"],
    ),
    (
        ("vector105 processor105 reasoning105 machine105 learning105 model105", 18),
        ["vector105", "processor105", "reasoning105", "machine105", "learning105", "model105"],
    ),
    (
        ("vector105 processor105 reasoning105 machine105 learning105 model105", 28),
        ["vector105 processor105", "reasoning105 machine105", "learning105 model105"],
    ),
    (
        ("processor105 reasoning105 machine105 learning105 model105 token105", 6),
        ["processor105", "reasoning105", "machine105", "learning105", "model105", "token105"],
    ),
    (
        ("processor105 reasoning105 machine105 learning105 model105 token105", 10),
        ["processor105", "reasoning105", "machine105", "learning105", "model105", "token105"],
    ),
    (
        ("processor105 reasoning105 machine105 learning105 model105 token105", 18),
        ["processor105", "reasoning105", "machine105", "learning105", "model105 token105"],
    ),
    (
        ("processor105 reasoning105 machine105 learning105 model105 token105", 28),
        ["processor105 reasoning105", "machine105 learning105", "model105 token105"],
    ),
    (
        ("reasoning105 machine105 learning105 model105 token105 prompt105", 6),
        ["reasoning105", "machine105", "learning105", "model105", "token105", "prompt105"],
    ),
    (
        ("reasoning105 machine105 learning105 model105 token105 prompt105", 10),
        ["reasoning105", "machine105", "learning105", "model105", "token105", "prompt105"],
    ),
    (
        ("reasoning105 machine105 learning105 model105 token105 prompt105", 18),
        ["reasoning105", "machine105", "learning105", "model105 token105", "prompt105"],
    ),
    (
        ("reasoning105 machine105 learning105 model105 token105 prompt105", 28),
        ["reasoning105 machine105", "learning105 model105", "token105 prompt105"],
    ),
    (
        ("machine105 learning105 model105 token105 prompt105 session105", 6),
        ["machine105", "learning105", "model105", "token105", "prompt105", "session105"],
    ),
    (
        ("machine105 learning105 model105 token105 prompt105 session105", 10),
        ["machine105", "learning105", "model105", "token105", "prompt105", "session105"],
    ),
    (
        ("machine105 learning105 model105 token105 prompt105 session105", 18),
        ["machine105", "learning105", "model105 token105", "prompt105", "session105"],
    ),
    (
        ("machine105 learning105 model105 token105 prompt105 session105", 28),
        ["machine105 learning105", "model105 token105 prompt105", "session105"],
    ),
    (
        ("learning105 model105 token105 prompt105 session105 library105", 6),
        ["learning105", "model105", "token105", "prompt105", "session105", "library105"],
    ),
    (
        ("learning105 model105 token105 prompt105 session105 library105", 10),
        ["learning105", "model105", "token105", "prompt105", "session105", "library105"],
    ),
    (
        ("learning105 model105 token105 prompt105 session105 library105", 18),
        ["learning105", "model105 token105", "prompt105", "session105", "library105"],
    ),
    (
        ("learning105 model105 token105 prompt105 session105 library105", 28),
        ["learning105 model105", "token105 prompt105", "session105 library105"],
    ),
    (
        ("model105 token105 prompt105 session105 library105 service105", 6),
        ["model105", "token105", "prompt105", "session105", "library105", "service105"],
    ),
    (
        ("model105 token105 prompt105 session105 library105 service105", 10),
        ["model105", "token105", "prompt105", "session105", "library105", "service105"],
    ),
    (
        ("model105 token105 prompt105 session105 library105 service105", 18),
        ["model105 token105", "prompt105", "session105", "library105", "service105"],
    ),
    (
        ("model105 token105 prompt105 session105 library105 service105", 28),
        ["model105 token105 prompt105", "session105 library105", "service105"],
    ),
    (
        ("token105 prompt105 session105 library105 service105 gateway105", 6),
        ["token105", "prompt105", "session105", "library105", "service105", "gateway105"],
    ),
    (
        ("token105 prompt105 session105 library105 service105 gateway105", 10),
        ["token105", "prompt105", "session105", "library105", "service105", "gateway105"],
    ),
    (
        ("token105 prompt105 session105 library105 service105 gateway105", 18),
        ["token105 prompt105", "session105", "library105", "service105", "gateway105"],
    ),
    (
        ("token105 prompt105 session105 library105 service105 gateway105", 28),
        ["token105 prompt105", "session105 library105", "service105 gateway105"],
    ),
    (
        ("prompt105 session105 library105 service105 gateway105 storage105", 6),
        ["prompt105", "session105", "library105", "service105", "gateway105", "storage105"],
    ),
    (
        ("prompt105 session105 library105 service105 gateway105 storage105", 10),
        ["prompt105", "session105", "library105", "service105", "gateway105", "storage105"],
    ),
    (
        ("prompt105 session105 library105 service105 gateway105 storage105", 18),
        ["prompt105", "session105", "library105", "service105", "gateway105", "storage105"],
    ),
    (
        ("prompt105 session105 library105 service105 gateway105 storage105", 28),
        ["prompt105 session105", "library105 service105", "gateway105 storage105"],
    ),
    (
        ("session105 library105 service105 gateway105 storage105 network105", 6),
        ["session105", "library105", "service105", "gateway105", "storage105", "network105"],
    ),
    (
        ("session105 library105 service105 gateway105 storage105 network105", 10),
        ["session105", "library105", "service105", "gateway105", "storage105", "network105"],
    ),
    (
        ("session105 library105 service105 gateway105 storage105 network105", 18),
        ["session105", "library105", "service105", "gateway105", "storage105", "network105"],
    ),
    (
        ("session105 library105 service105 gateway105 storage105 network105", 28),
        ["session105 library105", "service105 gateway105", "storage105 network105"],
    ),
    (
        ("library105 service105 gateway105 storage105 network105 latency105", 6),
        ["library105", "service105", "gateway105", "storage105", "network105", "latency105"],
    ),
    (
        ("library105 service105 gateway105 storage105 network105 latency105", 10),
        ["library105", "service105", "gateway105", "storage105", "network105", "latency105"],
    ),
    (
        ("library105 service105 gateway105 storage105 network105 latency105", 18),
        ["library105", "service105", "gateway105", "storage105", "network105", "latency105"],
    ),
    (
        ("library105 service105 gateway105 storage105 network105 latency105", 28),
        ["library105 service105", "gateway105 storage105", "network105 latency105"],
    ),
    (
        ("service105 gateway105 storage105 network105 latency105 buffer105", 6),
        ["service105", "gateway105", "storage105", "network105", "latency105", "buffer105"],
    ),
    (
        ("service105 gateway105 storage105 network105 latency105 buffer105", 10),
        ["service105", "gateway105", "storage105", "network105", "latency105", "buffer105"],
    ),
    (
        ("service105 gateway105 storage105 network105 latency105 buffer105", 18),
        ["service105", "gateway105", "storage105", "network105", "latency105", "buffer105"],
    ),
    (
        ("service105 gateway105 storage105 network105 latency105 buffer105", 28),
        ["service105 gateway105", "storage105 network105", "latency105 buffer105"],
    ),
    (
        ("gateway105 storage105 network105 latency105 buffer105 queue105", 6),
        ["gateway105", "storage105", "network105", "latency105", "buffer105", "queue105"],
    ),
    (
        ("gateway105 storage105 network105 latency105 buffer105 queue105", 10),
        ["gateway105", "storage105", "network105", "latency105", "buffer105", "queue105"],
    ),
    (
        ("gateway105 storage105 network105 latency105 buffer105 queue105", 18),
        ["gateway105", "storage105", "network105", "latency105", "buffer105 queue105"],
    ),
    (
        ("gateway105 storage105 network105 latency105 buffer105 queue105", 28),
        ["gateway105 storage105", "network105 latency105", "buffer105 queue105"],
    ),
    (
        ("storage105 network105 latency105 buffer105 queue105 worker105", 6),
        ["storage105", "network105", "latency105", "buffer105", "queue105", "worker105"],
    ),
    (
        ("storage105 network105 latency105 buffer105 queue105 worker105", 10),
        ["storage105", "network105", "latency105", "buffer105", "queue105", "worker105"],
    ),
    (
        ("storage105 network105 latency105 buffer105 queue105 worker105", 18),
        ["storage105", "network105", "latency105", "buffer105 queue105", "worker105"],
    ),
    (
        ("storage105 network105 latency105 buffer105 queue105 worker105", 28),
        ["storage105 network105", "latency105 buffer105", "queue105 worker105"],
    ),
    (
        ("network105 latency105 buffer105 queue105 worker105 kernel105", 6),
        ["network105", "latency105", "buffer105", "queue105", "worker105", "kernel105"],
    ),
    (
        ("network105 latency105 buffer105 queue105 worker105 kernel105", 10),
        ["network105", "latency105", "buffer105", "queue105", "worker105", "kernel105"],
    ),
    (
        ("network105 latency105 buffer105 queue105 worker105 kernel105", 18),
        ["network105", "latency105", "buffer105 queue105", "worker105", "kernel105"],
    ),
    (
        ("network105 latency105 buffer105 queue105 worker105 kernel105", 28),
        ["network105 latency105", "buffer105 queue105 worker105", "kernel105"],
    ),
    (
        ("latency105 buffer105 queue105 worker105 kernel105 signal105", 6),
        ["latency105", "buffer105", "queue105", "worker105", "kernel105", "signal105"],
    ),
    (
        ("latency105 buffer105 queue105 worker105 kernel105 signal105", 10),
        ["latency105", "buffer105", "queue105", "worker105", "kernel105", "signal105"],
    ),
    (
        ("latency105 buffer105 queue105 worker105 kernel105 signal105", 18),
        ["latency105", "buffer105 queue105", "worker105", "kernel105", "signal105"],
    ),
    (
        ("latency105 buffer105 queue105 worker105 kernel105 signal105", 28),
        ["latency105 buffer105", "queue105 worker105 kernel105", "signal105"],
    ),
    (
        ("buffer105 queue105 worker105 kernel105 signal105 packet105", 6),
        ["buffer105", "queue105", "worker105", "kernel105", "signal105", "packet105"],
    ),
    (
        ("buffer105 queue105 worker105 kernel105 signal105 packet105", 10),
        ["buffer105", "queue105", "worker105", "kernel105", "signal105", "packet105"],
    ),
    (
        ("buffer105 queue105 worker105 kernel105 signal105 packet105", 18),
        ["buffer105 queue105", "worker105", "kernel105", "signal105", "packet105"],
    ),
    (
        ("buffer105 queue105 worker105 kernel105 signal105 packet105", 28),
        ["buffer105 queue105 worker105", "kernel105 signal105", "packet105"],
    ),
    (
        ("queue105 worker105 kernel105 signal105 packet105 router105", 6),
        ["queue105", "worker105", "kernel105", "signal105", "packet105", "router105"],
    ),
    (
        ("queue105 worker105 kernel105 signal105 packet105 router105", 10),
        ["queue105", "worker105", "kernel105", "signal105", "packet105", "router105"],
    ),
    (
        ("queue105 worker105 kernel105 signal105 packet105 router105", 18),
        ["queue105 worker105", "kernel105", "signal105", "packet105", "router105"],
    ),
    (
        ("queue105 worker105 kernel105 signal105 packet105 router105", 28),
        ["queue105 worker105 kernel105", "signal105 packet105", "router105"],
    ),
    (
        ("worker105 kernel105 signal105 packet105 router105 cluster105", 6),
        ["worker105", "kernel105", "signal105", "packet105", "router105", "cluster105"],
    ),
    (
        ("worker105 kernel105 signal105 packet105 router105 cluster105", 10),
        ["worker105", "kernel105", "signal105", "packet105", "router105", "cluster105"],
    ),
    (
        ("worker105 kernel105 signal105 packet105 router105 cluster105", 18),
        ["worker105", "kernel105", "signal105", "packet105", "router105", "cluster105"],
    ),
    (
        ("worker105 kernel105 signal105 packet105 router105 cluster105", 28),
        ["worker105 kernel105", "signal105 packet105", "router105 cluster105"],
    ),
    (
        ("kernel105 signal105 packet105 router105 cluster105 mirror105", 6),
        ["kernel105", "signal105", "packet105", "router105", "cluster105", "mirror105"],
    ),
    (
        ("kernel105 signal105 packet105 router105 cluster105 mirror105", 10),
        ["kernel105", "signal105", "packet105", "router105", "cluster105", "mirror105"],
    ),
    (
        ("kernel105 signal105 packet105 router105 cluster105 mirror105", 18),
        ["kernel105", "signal105", "packet105", "router105", "cluster105", "mirror105"],
    ),
    (
        ("kernel105 signal105 packet105 router105 cluster105 mirror105", 28),
        ["kernel105 signal105", "packet105 router105", "cluster105 mirror105"],
    ),
    (
        ("signal105 packet105 router105 cluster105 mirror105 filter105", 6),
        ["signal105", "packet105", "router105", "cluster105", "mirror105", "filter105"],
    ),
    (
        ("signal105 packet105 router105 cluster105 mirror105 filter105", 10),
        ["signal105", "packet105", "router105", "cluster105", "mirror105", "filter105"],
    ),
    (
        ("signal105 packet105 router105 cluster105 mirror105 filter105", 18),
        ["signal105", "packet105", "router105", "cluster105", "mirror105", "filter105"],
    ),
    (
        ("signal105 packet105 router105 cluster105 mirror105 filter105", 28),
        ["signal105 packet105", "router105 cluster105", "mirror105 filter105"],
    ),
    (
        ("packet105 router105 cluster105 mirror105 filter105 ranking105", 6),
        ["packet105", "router105", "cluster105", "mirror105", "filter105", "ranking105"],
    ),
    (
        ("packet105 router105 cluster105 mirror105 filter105 ranking105", 10),
        ["packet105", "router105", "cluster105", "mirror105", "filter105", "ranking105"],
    ),
    (
        ("packet105 router105 cluster105 mirror105 filter105 ranking105", 18),
        ["packet105", "router105", "cluster105", "mirror105", "filter105", "ranking105"],
    ),
    (
        ("packet105 router105 cluster105 mirror105 filter105 ranking105", 28),
        ["packet105 router105", "cluster105 mirror105", "filter105 ranking105"],
    ),
    (
        ("router105 cluster105 mirror105 filter105 ranking105 encoding105", 6),
        ["router105", "cluster105", "mirror105", "filter105", "ranking105", "encoding105"],
    ),
    (
        ("router105 cluster105 mirror105 filter105 ranking105 encoding105", 10),
        ["router105", "cluster105", "mirror105", "filter105", "ranking105", "encoding105"],
    ),
    (
        ("router105 cluster105 mirror105 filter105 ranking105 encoding105", 18),
        ["router105", "cluster105", "mirror105", "filter105", "ranking105", "encoding105"],
    ),
    (
        ("router105 cluster105 mirror105 filter105 ranking105 encoding105", 28),
        ["router105 cluster105", "mirror105 filter105", "ranking105 encoding105"],
    ),
    (
        ("cluster105 mirror105 filter105 ranking105 encoding105 mapping105", 6),
        ["cluster105", "mirror105", "filter105", "ranking105", "encoding105", "mapping105"],
    ),
    (
        ("cluster105 mirror105 filter105 ranking105 encoding105 mapping105", 10),
        ["cluster105", "mirror105", "filter105", "ranking105", "encoding105", "mapping105"],
    ),
    (
        ("cluster105 mirror105 filter105 ranking105 encoding105 mapping105", 18),
        ["cluster105", "mirror105", "filter105", "ranking105", "encoding105", "mapping105"],
    ),
    (
        ("cluster105 mirror105 filter105 ranking105 encoding105 mapping105", 28),
        ["cluster105 mirror105", "filter105 ranking105", "encoding105 mapping105"],
    ),
    (
        ("mirror105 filter105 ranking105 encoding105 mapping105 record105", 6),
        ["mirror105", "filter105", "ranking105", "encoding105", "mapping105", "record105"],
    ),
    (
        ("mirror105 filter105 ranking105 encoding105 mapping105 record105", 10),
        ["mirror105", "filter105", "ranking105", "encoding105", "mapping105", "record105"],
    ),
    (
        ("mirror105 filter105 ranking105 encoding105 mapping105 record105", 18),
        ["mirror105", "filter105", "ranking105", "encoding105", "mapping105", "record105"],
    ),
    (
        ("mirror105 filter105 ranking105 encoding105 mapping105 record105", 28),
        ["mirror105 filter105", "ranking105 encoding105", "mapping105 record105"],
    ),
    (
        ("filter105 ranking105 encoding105 mapping105 record105 candle105", 6),
        ["filter105", "ranking105", "encoding105", "mapping105", "record105", "candle105"],
    ),
    (
        ("filter105 ranking105 encoding105 mapping105 record105 candle105", 10),
        ["filter105", "ranking105", "encoding105", "mapping105", "record105", "candle105"],
    ),
    (
        ("filter105 ranking105 encoding105 mapping105 record105 candle105", 18),
        ["filter105", "ranking105", "encoding105", "mapping105", "record105", "candle105"],
    ),
    (
        ("filter105 ranking105 encoding105 mapping105 record105 candle105", 28),
        ["filter105 ranking105", "encoding105 mapping105", "record105 candle105"],
    ),
    (
        ("ranking105 encoding105 mapping105 record105 candle105 thread105", 6),
        ["ranking105", "encoding105", "mapping105", "record105", "candle105", "thread105"],
    ),
    (
        ("ranking105 encoding105 mapping105 record105 candle105 thread105", 10),
        ["ranking105", "encoding105", "mapping105", "record105", "candle105", "thread105"],
    ),
    (
        ("ranking105 encoding105 mapping105 record105 candle105 thread105", 18),
        ["ranking105", "encoding105", "mapping105", "record105", "candle105", "thread105"],
    ),
    (
        ("ranking105 encoding105 mapping105 record105 candle105 thread105", 28),
        ["ranking105 encoding105", "mapping105 record105", "candle105 thread105"],
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
