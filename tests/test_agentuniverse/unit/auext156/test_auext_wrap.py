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
        ("round 156: the quick brown fox jumps over the lazy dog", 4),
        ["round", "156:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 156: the quick brown fox jumps over the lazy dog", 8),
        ["round", "156: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 156: the quick brown fox jumps over the lazy dog", 12),
        ["round 156:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 156: the quick brown fox jumps over the lazy dog", 16),
        ["round 156: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 156: the quick brown fox jumps over the lazy dog", 24),
        ["round 156: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 156: the quick brown fox jumps over the lazy dog", 32),
        ["round 156: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 156: agentuniverse is a framework for multi agents", 4),
        ["round", "156:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 156: agentuniverse is a framework for multi agents", 8),
        ["round", "156:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 156: agentuniverse is a framework for multi agents", 12),
        ["round 156:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 156: agentuniverse is a framework for multi agents", 16),
        ["round 156:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 156: agentuniverse is a framework for multi agents", 24),
        ["round 156: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 156: agentuniverse is a framework for multi agents", 32),
        ["round 156: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 156: knowledge stored as vectors enables retrieval", 4),
        ["round", "156:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 156: knowledge stored as vectors enables retrieval", 8),
        ["round", "156:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 156: knowledge stored as vectors enables retrieval", 12),
        ["round 156:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 156: knowledge stored as vectors enables retrieval", 16),
        ["round 156:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 156: knowledge stored as vectors enables retrieval", 24),
        ["round 156: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 156: knowledge stored as vectors enables retrieval", 32),
        ["round 156: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 156: the processor reads the record then stops", 4),
        ["round", "156:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 156: the processor reads the record then stops", 8),
        ["round", "156: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 156: the processor reads the record then stops", 12),
        ["round 156:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 156: the processor reads the record then stops", 16),
        ["round 156: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 156: the processor reads the record then stops", 24),
        ["round 156: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 156: the processor reads the record then stops", 32),
        ["round 156: the processor reads", "the record then stops"],
    ),
    (
        ("round 156: a worker pulls the next task from the queue", 4),
        ["round", "156:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 156: a worker pulls the next task from the queue", 8),
        ["round", "156: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 156: a worker pulls the next task from the queue", 12),
        ["round 156: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 156: a worker pulls the next task from the queue", 16),
        ["round 156: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 156: a worker pulls the next task from the queue", 24),
        ["round 156: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 156: a worker pulls the next task from the queue", 32),
        ["round 156: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 156: signals travel through the network layer", 4),
        ["round", "156:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 156: signals travel through the network layer", 8),
        ["round", "156:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 156: signals travel through the network layer", 12),
        ["round 156:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 156: signals travel through the network layer", 16),
        ["round 156:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 156: signals travel through the network layer", 24),
        ["round 156: signals", "travel through the", "network layer"],
    ),
    (
        ("round 156: signals travel through the network layer", 32),
        ["round 156: signals travel", "through the network layer"],
    ),
    (
        ("round 156: the gateway routes each request by policy", 4),
        ["round", "156:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 156: the gateway routes each request by policy", 8),
        ["round", "156: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 156: the gateway routes each request by policy", 12),
        ["round 156:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 156: the gateway routes each request by policy", 16),
        ["round 156: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 156: the gateway routes each request by policy", 24),
        ["round 156: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 156: the gateway routes each request by policy", 32),
        ["round 156: the gateway routes", "each request by policy"],
    ),
    (
        ("round 156: memory grows until the buffer is full", 4),
        ["round", "156:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 156: memory grows until the buffer is full", 8),
        ["round", "156:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 156: memory grows until the buffer is full", 12),
        ["round 156:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 156: memory grows until the buffer is full", 16),
        ["round 156:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 156: memory grows until the buffer is full", 24), ["round 156: memory grows", "until the buffer is full"]),
    (("round 156: memory grows until the buffer is full", 32), ["round 156: memory grows until", "the buffer is full"]),
    (
        ("round 156: the cluster mirrors every packet twice", 4),
        ["round", "156:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 156: the cluster mirrors every packet twice", 8),
        ["round", "156: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 156: the cluster mirrors every packet twice", 12),
        ["round 156:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 156: the cluster mirrors every packet twice", 16),
        ["round 156: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 156: the cluster mirrors every packet twice", 24),
        ["round 156: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 156: the cluster mirrors every packet twice", 32),
        ["round 156: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 156: ranking uses tokens learned from the corpus", 4),
        ["round", "156:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 156: ranking uses tokens learned from the corpus", 8),
        ["round", "156:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 156: ranking uses tokens learned from the corpus", 12),
        ["round 156:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 156: ranking uses tokens learned from the corpus", 16),
        ["round 156:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 156: ranking uses tokens learned from the corpus", 24),
        ["round 156: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 156: ranking uses tokens learned from the corpus", 32),
        ["round 156: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 156: a long session ends when the candle dies", 4),
        ["round", "156:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 156: a long session ends when the candle dies", 8),
        ["round", "156: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 156: a long session ends when the candle dies", 12),
        ["round 156: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 156: a long session ends when the candle dies", 16),
        ["round 156: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 156: a long session ends when the candle dies", 24),
        ["round 156: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 156: a long session ends when the candle dies", 32),
        ["round 156: a long session ends", "when the candle dies"],
    ),
    (
        ("round 156: encode the prompt then map the result", 4),
        ["round", "156:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 156: encode the prompt then map the result", 8),
        ["round", "156:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 156: encode the prompt then map the result", 12),
        ["round 156:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 156: encode the prompt then map the result", 16),
        ["round 156:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 156: encode the prompt then map the result", 24),
        ["round 156: encode the", "prompt then map the", "result"],
    ),
    (("round 156: encode the prompt then map the result", 32), ["round 156: encode the prompt", "then map the result"]),
    (
        ("round 156: the kernel wakes the worker at dawn", 4),
        ["round", "156:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 156: the kernel wakes the worker at dawn", 8),
        ["round", "156: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 156: the kernel wakes the worker at dawn", 12),
        ["round 156:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 156: the kernel wakes the worker at dawn", 16), ["round 156: the", "kernel wakes the", "worker at dawn"]),
    (("round 156: the kernel wakes the worker at dawn", 24), ["round 156: the kernel", "wakes the worker at dawn"]),
    (("round 156: the kernel wakes the worker at dawn", 32), ["round 156: the kernel wakes the", "worker at dawn"]),
    (
        ("round 156: service latency drops after the patch", 4),
        ["round", "156:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 156: service latency drops after the patch", 8),
        ["round", "156:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 156: service latency drops after the patch", 12),
        ["round 156:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 156: service latency drops after the patch", 16),
        ["round 156:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 156: service latency drops after the patch", 24),
        ["round 156: service", "latency drops after the", "patch"],
    ),
    (("round 156: service latency drops after the patch", 32), ["round 156: service latency drops", "after the patch"]),
    (
        ("round 156: the library caches every vector it sees", 4),
        ["round", "156:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 156: the library caches every vector it sees", 8),
        ["round", "156: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 156: the library caches every vector it sees", 12),
        ["round 156:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 156: the library caches every vector it sees", 16),
        ["round 156: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 156: the library caches every vector it sees", 24),
        ["round 156: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 156: the library caches every vector it sees", 32),
        ["round 156: the library caches", "every vector it sees"],
    ),
    (
        ("round 156: agents argue then the debate resolves", 4),
        ["round", "156:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 156: agents argue then the debate resolves", 8),
        ["round", "156:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 156: agents argue then the debate resolves", 12),
        ["round 156:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 156: agents argue then the debate resolves", 16),
        ["round 156:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 156: agents argue then the debate resolves", 24), ["round 156: agents argue", "then the debate resolves"]),
    (("round 156: agents argue then the debate resolves", 32), ["round 156: agents argue then the", "debate resolves"]),
    (
        ("round 156: the filter keeps only strong matches", 4),
        ["round", "156:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 156: the filter keeps only strong matches", 8),
        ["round", "156: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 156: the filter keeps only strong matches", 12),
        ["round 156:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 156: the filter keeps only strong matches", 16),
        ["round 156: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 156: the filter keeps only strong matches", 24),
        ["round 156: the filter", "keeps only strong", "matches"],
    ),
    (("round 156: the filter keeps only strong matches", 32), ["round 156: the filter keeps only", "strong matches"]),
    (
        ("round 156: the model answers with a short reply", 4),
        ["round", "156:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 156: the model answers with a short reply", 8),
        ["round", "156: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 156: the model answers with a short reply", 12),
        ["round 156:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 156: the model answers with a short reply", 16),
        ["round 156: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 156: the model answers with a short reply", 24),
        ["round 156: the model", "answers with a short", "reply"],
    ),
    (("round 156: the model answers with a short reply", 32), ["round 156: the model answers", "with a short reply"]),
    (
        ("round 156: the recorder stores the reasoning trace", 4),
        ["round", "156:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 156: the recorder stores the reasoning trace", 8),
        ["round", "156: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 156: the recorder stores the reasoning trace", 12),
        ["round 156:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 156: the recorder stores the reasoning trace", 16),
        ["round 156: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 156: the recorder stores the reasoning trace", 24),
        ["round 156: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 156: the recorder stores the reasoning trace", 32),
        ["round 156: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 156: the angel watches the processor run", 4),
        ["round", "156:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 156: the angel watches the processor run", 8),
        ["round", "156: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 156: the angel watches the processor run", 12),
        ["round 156:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 156: the angel watches the processor run", 16),
        ["round 156: the", "angel watches", "the processor", "run"],
    ),
    (("round 156: the angel watches the processor run", 24), ["round 156: the angel", "watches the processor", "run"]),
    (("round 156: the angel watches the processor run", 32), ["round 156: the angel watches the", "processor run"]),
    (
        ("round 156: angle of the vector decides the match", 4),
        ["round", "156:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 156: angle of the vector decides the match", 8),
        ["round", "156:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 156: angle of the vector decides the match", 12),
        ["round 156:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 156: angle of the vector decides the match", 16),
        ["round 156: angle", "of the vector", "decides the", "match"],
    ),
    (("round 156: angle of the vector decides the match", 24), ["round 156: angle of the", "vector decides the match"]),
    (("round 156: angle of the vector decides the match", 32), ["round 156: angle of the vector", "decides the match"]),
    (
        ("round 156: the candle burns twice as long at night", 4),
        ["round", "156:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 156: the candle burns twice as long at night", 8),
        ["round", "156: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 156: the candle burns twice as long at night", 12),
        ["round 156:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 156: the candle burns twice as long at night", 16),
        ["round 156: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 156: the candle burns twice as long at night", 24),
        ["round 156: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 156: the candle burns twice as long at night", 32),
        ["round 156: the candle burns", "twice as long at night"],
    ),
    (
        ("round 156: a mirror of the universe in one line", 4),
        ["round", "156:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 156: a mirror of the universe in one line", 8),
        ["round", "156: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 156: a mirror of the universe in one line", 12),
        ["round 156: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 156: a mirror of the universe in one line", 16),
        ["round 156: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 156: a mirror of the universe in one line", 24), ["round 156: a mirror of", "the universe in one line"]),
    (("round 156: a mirror of the universe in one line", 32), ["round 156: a mirror of the", "universe in one line"]),
    (
        ("round 156: the queue drains before the storm", 4),
        ["round", "156:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 156: the queue drains before the storm", 8),
        ["round", "156: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 156: the queue drains before the storm", 12),
        ["round 156:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 156: the queue drains before the storm", 16), ["round 156: the", "queue drains", "before the storm"]),
    (("round 156: the queue drains before the storm", 24), ["round 156: the queue", "drains before the storm"]),
    (("round 156: the queue drains before the storm", 32), ["round 156: the queue drains", "before the storm"]),
    (
        ("kitten156 sitting156 agent156 angle156 universe156 memory156", 6),
        ["kitten156", "sitting156", "agent156", "angle156", "universe156", "memory156"],
    ),
    (
        ("kitten156 sitting156 agent156 angle156 universe156 memory156", 10),
        ["kitten156", "sitting156", "agent156", "angle156", "universe156", "memory156"],
    ),
    (
        ("kitten156 sitting156 agent156 angle156 universe156 memory156", 18),
        ["kitten156", "sitting156", "agent156 angle156", "universe156", "memory156"],
    ),
    (
        ("kitten156 sitting156 agent156 angle156 universe156 memory156", 28),
        ["kitten156 sitting156", "agent156 angle156", "universe156 memory156"],
    ),
    (
        ("sitting156 agent156 angle156 universe156 memory156 stream156", 6),
        ["sitting156", "agent156", "angle156", "universe156", "memory156", "stream156"],
    ),
    (
        ("sitting156 agent156 angle156 universe156 memory156 stream156", 10),
        ["sitting156", "agent156", "angle156", "universe156", "memory156", "stream156"],
    ),
    (
        ("sitting156 agent156 angle156 universe156 memory156 stream156", 18),
        ["sitting156", "agent156 angle156", "universe156", "memory156", "stream156"],
    ),
    (
        ("sitting156 agent156 angle156 universe156 memory156 stream156", 28),
        ["sitting156 agent156 angle156", "universe156 memory156", "stream156"],
    ),
    (
        ("agent156 angle156 universe156 memory156 stream156 context156", 6),
        ["agent156", "angle156", "universe156", "memory156", "stream156", "context156"],
    ),
    (
        ("agent156 angle156 universe156 memory156 stream156 context156", 10),
        ["agent156", "angle156", "universe156", "memory156", "stream156", "context156"],
    ),
    (
        ("agent156 angle156 universe156 memory156 stream156 context156", 18),
        ["agent156 angle156", "universe156", "memory156", "stream156", "context156"],
    ),
    (
        ("agent156 angle156 universe156 memory156 stream156 context156", 28),
        ["agent156 angle156", "universe156 memory156", "stream156 context156"],
    ),
    (
        ("angle156 universe156 memory156 stream156 context156 knowledge156", 6),
        ["angle156", "universe156", "memory156", "stream156", "context156", "knowledge156"],
    ),
    (
        ("angle156 universe156 memory156 stream156 context156 knowledge156", 10),
        ["angle156", "universe156", "memory156", "stream156", "context156", "knowledge156"],
    ),
    (
        ("angle156 universe156 memory156 stream156 context156 knowledge156", 18),
        ["angle156", "universe156", "memory156", "stream156", "context156", "knowledge156"],
    ),
    (
        ("angle156 universe156 memory156 stream156 context156 knowledge156", 28),
        ["angle156 universe156", "memory156 stream156", "context156 knowledge156"],
    ),
    (
        ("universe156 memory156 stream156 context156 knowledge156 vector156", 6),
        ["universe156", "memory156", "stream156", "context156", "knowledge156", "vector156"],
    ),
    (
        ("universe156 memory156 stream156 context156 knowledge156 vector156", 10),
        ["universe156", "memory156", "stream156", "context156", "knowledge156", "vector156"],
    ),
    (
        ("universe156 memory156 stream156 context156 knowledge156 vector156", 18),
        ["universe156", "memory156", "stream156", "context156", "knowledge156", "vector156"],
    ),
    (
        ("universe156 memory156 stream156 context156 knowledge156 vector156", 28),
        ["universe156 memory156", "stream156 context156", "knowledge156 vector156"],
    ),
    (
        ("memory156 stream156 context156 knowledge156 vector156 processor156", 6),
        ["memory156", "stream156", "context156", "knowledge156", "vector156", "processor156"],
    ),
    (
        ("memory156 stream156 context156 knowledge156 vector156 processor156", 10),
        ["memory156", "stream156", "context156", "knowledge156", "vector156", "processor156"],
    ),
    (
        ("memory156 stream156 context156 knowledge156 vector156 processor156", 18),
        ["memory156", "stream156", "context156", "knowledge156", "vector156", "processor156"],
    ),
    (
        ("memory156 stream156 context156 knowledge156 vector156 processor156", 28),
        ["memory156 stream156", "context156 knowledge156", "vector156 processor156"],
    ),
    (
        ("stream156 context156 knowledge156 vector156 processor156 reasoning156", 6),
        ["stream156", "context156", "knowledge156", "vector156", "processor156", "reasoning156"],
    ),
    (
        ("stream156 context156 knowledge156 vector156 processor156 reasoning156", 10),
        ["stream156", "context156", "knowledge156", "vector156", "processor156", "reasoning156"],
    ),
    (
        ("stream156 context156 knowledge156 vector156 processor156 reasoning156", 18),
        ["stream156", "context156", "knowledge156", "vector156", "processor156", "reasoning156"],
    ),
    (
        ("stream156 context156 knowledge156 vector156 processor156 reasoning156", 28),
        ["stream156 context156", "knowledge156 vector156", "processor156 reasoning156"],
    ),
    (
        ("context156 knowledge156 vector156 processor156 reasoning156 machine156", 6),
        ["context156", "knowledge156", "vector156", "processor156", "reasoning156", "machine156"],
    ),
    (
        ("context156 knowledge156 vector156 processor156 reasoning156 machine156", 10),
        ["context156", "knowledge156", "vector156", "processor156", "reasoning156", "machine156"],
    ),
    (
        ("context156 knowledge156 vector156 processor156 reasoning156 machine156", 18),
        ["context156", "knowledge156", "vector156", "processor156", "reasoning156", "machine156"],
    ),
    (
        ("context156 knowledge156 vector156 processor156 reasoning156 machine156", 28),
        ["context156 knowledge156", "vector156 processor156", "reasoning156 machine156"],
    ),
    (
        ("knowledge156 vector156 processor156 reasoning156 machine156 learning156", 6),
        ["knowledge156", "vector156", "processor156", "reasoning156", "machine156", "learning156"],
    ),
    (
        ("knowledge156 vector156 processor156 reasoning156 machine156 learning156", 10),
        ["knowledge156", "vector156", "processor156", "reasoning156", "machine156", "learning156"],
    ),
    (
        ("knowledge156 vector156 processor156 reasoning156 machine156 learning156", 18),
        ["knowledge156", "vector156", "processor156", "reasoning156", "machine156", "learning156"],
    ),
    (
        ("knowledge156 vector156 processor156 reasoning156 machine156 learning156", 28),
        ["knowledge156 vector156", "processor156 reasoning156", "machine156 learning156"],
    ),
    (
        ("vector156 processor156 reasoning156 machine156 learning156 model156", 6),
        ["vector156", "processor156", "reasoning156", "machine156", "learning156", "model156"],
    ),
    (
        ("vector156 processor156 reasoning156 machine156 learning156 model156", 10),
        ["vector156", "processor156", "reasoning156", "machine156", "learning156", "model156"],
    ),
    (
        ("vector156 processor156 reasoning156 machine156 learning156 model156", 18),
        ["vector156", "processor156", "reasoning156", "machine156", "learning156", "model156"],
    ),
    (
        ("vector156 processor156 reasoning156 machine156 learning156 model156", 28),
        ["vector156 processor156", "reasoning156 machine156", "learning156 model156"],
    ),
    (
        ("processor156 reasoning156 machine156 learning156 model156 token156", 6),
        ["processor156", "reasoning156", "machine156", "learning156", "model156", "token156"],
    ),
    (
        ("processor156 reasoning156 machine156 learning156 model156 token156", 10),
        ["processor156", "reasoning156", "machine156", "learning156", "model156", "token156"],
    ),
    (
        ("processor156 reasoning156 machine156 learning156 model156 token156", 18),
        ["processor156", "reasoning156", "machine156", "learning156", "model156 token156"],
    ),
    (
        ("processor156 reasoning156 machine156 learning156 model156 token156", 28),
        ["processor156 reasoning156", "machine156 learning156", "model156 token156"],
    ),
    (
        ("reasoning156 machine156 learning156 model156 token156 prompt156", 6),
        ["reasoning156", "machine156", "learning156", "model156", "token156", "prompt156"],
    ),
    (
        ("reasoning156 machine156 learning156 model156 token156 prompt156", 10),
        ["reasoning156", "machine156", "learning156", "model156", "token156", "prompt156"],
    ),
    (
        ("reasoning156 machine156 learning156 model156 token156 prompt156", 18),
        ["reasoning156", "machine156", "learning156", "model156 token156", "prompt156"],
    ),
    (
        ("reasoning156 machine156 learning156 model156 token156 prompt156", 28),
        ["reasoning156 machine156", "learning156 model156", "token156 prompt156"],
    ),
    (
        ("machine156 learning156 model156 token156 prompt156 session156", 6),
        ["machine156", "learning156", "model156", "token156", "prompt156", "session156"],
    ),
    (
        ("machine156 learning156 model156 token156 prompt156 session156", 10),
        ["machine156", "learning156", "model156", "token156", "prompt156", "session156"],
    ),
    (
        ("machine156 learning156 model156 token156 prompt156 session156", 18),
        ["machine156", "learning156", "model156 token156", "prompt156", "session156"],
    ),
    (
        ("machine156 learning156 model156 token156 prompt156 session156", 28),
        ["machine156 learning156", "model156 token156 prompt156", "session156"],
    ),
    (
        ("learning156 model156 token156 prompt156 session156 library156", 6),
        ["learning156", "model156", "token156", "prompt156", "session156", "library156"],
    ),
    (
        ("learning156 model156 token156 prompt156 session156 library156", 10),
        ["learning156", "model156", "token156", "prompt156", "session156", "library156"],
    ),
    (
        ("learning156 model156 token156 prompt156 session156 library156", 18),
        ["learning156", "model156 token156", "prompt156", "session156", "library156"],
    ),
    (
        ("learning156 model156 token156 prompt156 session156 library156", 28),
        ["learning156 model156", "token156 prompt156", "session156 library156"],
    ),
    (
        ("model156 token156 prompt156 session156 library156 service156", 6),
        ["model156", "token156", "prompt156", "session156", "library156", "service156"],
    ),
    (
        ("model156 token156 prompt156 session156 library156 service156", 10),
        ["model156", "token156", "prompt156", "session156", "library156", "service156"],
    ),
    (
        ("model156 token156 prompt156 session156 library156 service156", 18),
        ["model156 token156", "prompt156", "session156", "library156", "service156"],
    ),
    (
        ("model156 token156 prompt156 session156 library156 service156", 28),
        ["model156 token156 prompt156", "session156 library156", "service156"],
    ),
    (
        ("token156 prompt156 session156 library156 service156 gateway156", 6),
        ["token156", "prompt156", "session156", "library156", "service156", "gateway156"],
    ),
    (
        ("token156 prompt156 session156 library156 service156 gateway156", 10),
        ["token156", "prompt156", "session156", "library156", "service156", "gateway156"],
    ),
    (
        ("token156 prompt156 session156 library156 service156 gateway156", 18),
        ["token156 prompt156", "session156", "library156", "service156", "gateway156"],
    ),
    (
        ("token156 prompt156 session156 library156 service156 gateway156", 28),
        ["token156 prompt156", "session156 library156", "service156 gateway156"],
    ),
    (
        ("prompt156 session156 library156 service156 gateway156 storage156", 6),
        ["prompt156", "session156", "library156", "service156", "gateway156", "storage156"],
    ),
    (
        ("prompt156 session156 library156 service156 gateway156 storage156", 10),
        ["prompt156", "session156", "library156", "service156", "gateway156", "storage156"],
    ),
    (
        ("prompt156 session156 library156 service156 gateway156 storage156", 18),
        ["prompt156", "session156", "library156", "service156", "gateway156", "storage156"],
    ),
    (
        ("prompt156 session156 library156 service156 gateway156 storage156", 28),
        ["prompt156 session156", "library156 service156", "gateway156 storage156"],
    ),
    (
        ("session156 library156 service156 gateway156 storage156 network156", 6),
        ["session156", "library156", "service156", "gateway156", "storage156", "network156"],
    ),
    (
        ("session156 library156 service156 gateway156 storage156 network156", 10),
        ["session156", "library156", "service156", "gateway156", "storage156", "network156"],
    ),
    (
        ("session156 library156 service156 gateway156 storage156 network156", 18),
        ["session156", "library156", "service156", "gateway156", "storage156", "network156"],
    ),
    (
        ("session156 library156 service156 gateway156 storage156 network156", 28),
        ["session156 library156", "service156 gateway156", "storage156 network156"],
    ),
    (
        ("library156 service156 gateway156 storage156 network156 latency156", 6),
        ["library156", "service156", "gateway156", "storage156", "network156", "latency156"],
    ),
    (
        ("library156 service156 gateway156 storage156 network156 latency156", 10),
        ["library156", "service156", "gateway156", "storage156", "network156", "latency156"],
    ),
    (
        ("library156 service156 gateway156 storage156 network156 latency156", 18),
        ["library156", "service156", "gateway156", "storage156", "network156", "latency156"],
    ),
    (
        ("library156 service156 gateway156 storage156 network156 latency156", 28),
        ["library156 service156", "gateway156 storage156", "network156 latency156"],
    ),
    (
        ("service156 gateway156 storage156 network156 latency156 buffer156", 6),
        ["service156", "gateway156", "storage156", "network156", "latency156", "buffer156"],
    ),
    (
        ("service156 gateway156 storage156 network156 latency156 buffer156", 10),
        ["service156", "gateway156", "storage156", "network156", "latency156", "buffer156"],
    ),
    (
        ("service156 gateway156 storage156 network156 latency156 buffer156", 18),
        ["service156", "gateway156", "storage156", "network156", "latency156", "buffer156"],
    ),
    (
        ("service156 gateway156 storage156 network156 latency156 buffer156", 28),
        ["service156 gateway156", "storage156 network156", "latency156 buffer156"],
    ),
    (
        ("gateway156 storage156 network156 latency156 buffer156 queue156", 6),
        ["gateway156", "storage156", "network156", "latency156", "buffer156", "queue156"],
    ),
    (
        ("gateway156 storage156 network156 latency156 buffer156 queue156", 10),
        ["gateway156", "storage156", "network156", "latency156", "buffer156", "queue156"],
    ),
    (
        ("gateway156 storage156 network156 latency156 buffer156 queue156", 18),
        ["gateway156", "storage156", "network156", "latency156", "buffer156 queue156"],
    ),
    (
        ("gateway156 storage156 network156 latency156 buffer156 queue156", 28),
        ["gateway156 storage156", "network156 latency156", "buffer156 queue156"],
    ),
    (
        ("storage156 network156 latency156 buffer156 queue156 worker156", 6),
        ["storage156", "network156", "latency156", "buffer156", "queue156", "worker156"],
    ),
    (
        ("storage156 network156 latency156 buffer156 queue156 worker156", 10),
        ["storage156", "network156", "latency156", "buffer156", "queue156", "worker156"],
    ),
    (
        ("storage156 network156 latency156 buffer156 queue156 worker156", 18),
        ["storage156", "network156", "latency156", "buffer156 queue156", "worker156"],
    ),
    (
        ("storage156 network156 latency156 buffer156 queue156 worker156", 28),
        ["storage156 network156", "latency156 buffer156", "queue156 worker156"],
    ),
    (
        ("network156 latency156 buffer156 queue156 worker156 kernel156", 6),
        ["network156", "latency156", "buffer156", "queue156", "worker156", "kernel156"],
    ),
    (
        ("network156 latency156 buffer156 queue156 worker156 kernel156", 10),
        ["network156", "latency156", "buffer156", "queue156", "worker156", "kernel156"],
    ),
    (
        ("network156 latency156 buffer156 queue156 worker156 kernel156", 18),
        ["network156", "latency156", "buffer156 queue156", "worker156", "kernel156"],
    ),
    (
        ("network156 latency156 buffer156 queue156 worker156 kernel156", 28),
        ["network156 latency156", "buffer156 queue156 worker156", "kernel156"],
    ),
    (
        ("latency156 buffer156 queue156 worker156 kernel156 signal156", 6),
        ["latency156", "buffer156", "queue156", "worker156", "kernel156", "signal156"],
    ),
    (
        ("latency156 buffer156 queue156 worker156 kernel156 signal156", 10),
        ["latency156", "buffer156", "queue156", "worker156", "kernel156", "signal156"],
    ),
    (
        ("latency156 buffer156 queue156 worker156 kernel156 signal156", 18),
        ["latency156", "buffer156 queue156", "worker156", "kernel156", "signal156"],
    ),
    (
        ("latency156 buffer156 queue156 worker156 kernel156 signal156", 28),
        ["latency156 buffer156", "queue156 worker156 kernel156", "signal156"],
    ),
    (
        ("buffer156 queue156 worker156 kernel156 signal156 packet156", 6),
        ["buffer156", "queue156", "worker156", "kernel156", "signal156", "packet156"],
    ),
    (
        ("buffer156 queue156 worker156 kernel156 signal156 packet156", 10),
        ["buffer156", "queue156", "worker156", "kernel156", "signal156", "packet156"],
    ),
    (
        ("buffer156 queue156 worker156 kernel156 signal156 packet156", 18),
        ["buffer156 queue156", "worker156", "kernel156", "signal156", "packet156"],
    ),
    (
        ("buffer156 queue156 worker156 kernel156 signal156 packet156", 28),
        ["buffer156 queue156 worker156", "kernel156 signal156", "packet156"],
    ),
    (
        ("queue156 worker156 kernel156 signal156 packet156 router156", 6),
        ["queue156", "worker156", "kernel156", "signal156", "packet156", "router156"],
    ),
    (
        ("queue156 worker156 kernel156 signal156 packet156 router156", 10),
        ["queue156", "worker156", "kernel156", "signal156", "packet156", "router156"],
    ),
    (
        ("queue156 worker156 kernel156 signal156 packet156 router156", 18),
        ["queue156 worker156", "kernel156", "signal156", "packet156", "router156"],
    ),
    (
        ("queue156 worker156 kernel156 signal156 packet156 router156", 28),
        ["queue156 worker156 kernel156", "signal156 packet156", "router156"],
    ),
    (
        ("worker156 kernel156 signal156 packet156 router156 cluster156", 6),
        ["worker156", "kernel156", "signal156", "packet156", "router156", "cluster156"],
    ),
    (
        ("worker156 kernel156 signal156 packet156 router156 cluster156", 10),
        ["worker156", "kernel156", "signal156", "packet156", "router156", "cluster156"],
    ),
    (
        ("worker156 kernel156 signal156 packet156 router156 cluster156", 18),
        ["worker156", "kernel156", "signal156", "packet156", "router156", "cluster156"],
    ),
    (
        ("worker156 kernel156 signal156 packet156 router156 cluster156", 28),
        ["worker156 kernel156", "signal156 packet156", "router156 cluster156"],
    ),
    (
        ("kernel156 signal156 packet156 router156 cluster156 mirror156", 6),
        ["kernel156", "signal156", "packet156", "router156", "cluster156", "mirror156"],
    ),
    (
        ("kernel156 signal156 packet156 router156 cluster156 mirror156", 10),
        ["kernel156", "signal156", "packet156", "router156", "cluster156", "mirror156"],
    ),
    (
        ("kernel156 signal156 packet156 router156 cluster156 mirror156", 18),
        ["kernel156", "signal156", "packet156", "router156", "cluster156", "mirror156"],
    ),
    (
        ("kernel156 signal156 packet156 router156 cluster156 mirror156", 28),
        ["kernel156 signal156", "packet156 router156", "cluster156 mirror156"],
    ),
    (
        ("signal156 packet156 router156 cluster156 mirror156 filter156", 6),
        ["signal156", "packet156", "router156", "cluster156", "mirror156", "filter156"],
    ),
    (
        ("signal156 packet156 router156 cluster156 mirror156 filter156", 10),
        ["signal156", "packet156", "router156", "cluster156", "mirror156", "filter156"],
    ),
    (
        ("signal156 packet156 router156 cluster156 mirror156 filter156", 18),
        ["signal156", "packet156", "router156", "cluster156", "mirror156", "filter156"],
    ),
    (
        ("signal156 packet156 router156 cluster156 mirror156 filter156", 28),
        ["signal156 packet156", "router156 cluster156", "mirror156 filter156"],
    ),
    (
        ("packet156 router156 cluster156 mirror156 filter156 ranking156", 6),
        ["packet156", "router156", "cluster156", "mirror156", "filter156", "ranking156"],
    ),
    (
        ("packet156 router156 cluster156 mirror156 filter156 ranking156", 10),
        ["packet156", "router156", "cluster156", "mirror156", "filter156", "ranking156"],
    ),
    (
        ("packet156 router156 cluster156 mirror156 filter156 ranking156", 18),
        ["packet156", "router156", "cluster156", "mirror156", "filter156", "ranking156"],
    ),
    (
        ("packet156 router156 cluster156 mirror156 filter156 ranking156", 28),
        ["packet156 router156", "cluster156 mirror156", "filter156 ranking156"],
    ),
    (
        ("router156 cluster156 mirror156 filter156 ranking156 encoding156", 6),
        ["router156", "cluster156", "mirror156", "filter156", "ranking156", "encoding156"],
    ),
    (
        ("router156 cluster156 mirror156 filter156 ranking156 encoding156", 10),
        ["router156", "cluster156", "mirror156", "filter156", "ranking156", "encoding156"],
    ),
    (
        ("router156 cluster156 mirror156 filter156 ranking156 encoding156", 18),
        ["router156", "cluster156", "mirror156", "filter156", "ranking156", "encoding156"],
    ),
    (
        ("router156 cluster156 mirror156 filter156 ranking156 encoding156", 28),
        ["router156 cluster156", "mirror156 filter156", "ranking156 encoding156"],
    ),
    (
        ("cluster156 mirror156 filter156 ranking156 encoding156 mapping156", 6),
        ["cluster156", "mirror156", "filter156", "ranking156", "encoding156", "mapping156"],
    ),
    (
        ("cluster156 mirror156 filter156 ranking156 encoding156 mapping156", 10),
        ["cluster156", "mirror156", "filter156", "ranking156", "encoding156", "mapping156"],
    ),
    (
        ("cluster156 mirror156 filter156 ranking156 encoding156 mapping156", 18),
        ["cluster156", "mirror156", "filter156", "ranking156", "encoding156", "mapping156"],
    ),
    (
        ("cluster156 mirror156 filter156 ranking156 encoding156 mapping156", 28),
        ["cluster156 mirror156", "filter156 ranking156", "encoding156 mapping156"],
    ),
    (
        ("mirror156 filter156 ranking156 encoding156 mapping156 record156", 6),
        ["mirror156", "filter156", "ranking156", "encoding156", "mapping156", "record156"],
    ),
    (
        ("mirror156 filter156 ranking156 encoding156 mapping156 record156", 10),
        ["mirror156", "filter156", "ranking156", "encoding156", "mapping156", "record156"],
    ),
    (
        ("mirror156 filter156 ranking156 encoding156 mapping156 record156", 18),
        ["mirror156", "filter156", "ranking156", "encoding156", "mapping156", "record156"],
    ),
    (
        ("mirror156 filter156 ranking156 encoding156 mapping156 record156", 28),
        ["mirror156 filter156", "ranking156 encoding156", "mapping156 record156"],
    ),
    (
        ("filter156 ranking156 encoding156 mapping156 record156 candle156", 6),
        ["filter156", "ranking156", "encoding156", "mapping156", "record156", "candle156"],
    ),
    (
        ("filter156 ranking156 encoding156 mapping156 record156 candle156", 10),
        ["filter156", "ranking156", "encoding156", "mapping156", "record156", "candle156"],
    ),
    (
        ("filter156 ranking156 encoding156 mapping156 record156 candle156", 18),
        ["filter156", "ranking156", "encoding156", "mapping156", "record156", "candle156"],
    ),
    (
        ("filter156 ranking156 encoding156 mapping156 record156 candle156", 28),
        ["filter156 ranking156", "encoding156 mapping156", "record156 candle156"],
    ),
    (
        ("ranking156 encoding156 mapping156 record156 candle156 thread156", 6),
        ["ranking156", "encoding156", "mapping156", "record156", "candle156", "thread156"],
    ),
    (
        ("ranking156 encoding156 mapping156 record156 candle156 thread156", 10),
        ["ranking156", "encoding156", "mapping156", "record156", "candle156", "thread156"],
    ),
    (
        ("ranking156 encoding156 mapping156 record156 candle156 thread156", 18),
        ["ranking156", "encoding156", "mapping156", "record156", "candle156", "thread156"],
    ),
    (
        ("ranking156 encoding156 mapping156 record156 candle156 thread156", 28),
        ["ranking156 encoding156", "mapping156 record156", "candle156 thread156"],
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
