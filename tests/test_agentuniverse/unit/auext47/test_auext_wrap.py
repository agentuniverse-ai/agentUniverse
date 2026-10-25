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
        ("round 47: the quick brown fox jumps over the lazy dog", 4),
        ["round", "47:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 47: the quick brown fox jumps over the lazy dog", 8),
        ["round", "47: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 47: the quick brown fox jumps over the lazy dog", 12),
        ["round 47:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 47: the quick brown fox jumps over the lazy dog", 16),
        ["round 47: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 47: the quick brown fox jumps over the lazy dog", 24),
        ["round 47: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 47: the quick brown fox jumps over the lazy dog", 32),
        ["round 47: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 47: agentuniverse is a framework for multi agents", 4),
        ["round", "47:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 47: agentuniverse is a framework for multi agents", 8),
        ["round", "47:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 47: agentuniverse is a framework for multi agents", 12),
        ["round 47:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 47: agentuniverse is a framework for multi agents", 16),
        ["round 47:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 47: agentuniverse is a framework for multi agents", 24),
        ["round 47: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 47: agentuniverse is a framework for multi agents", 32),
        ["round 47: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 47: knowledge stored as vectors enables retrieval", 4),
        ["round", "47:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 47: knowledge stored as vectors enables retrieval", 8),
        ["round", "47:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 47: knowledge stored as vectors enables retrieval", 12),
        ["round 47:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 47: knowledge stored as vectors enables retrieval", 16),
        ["round 47:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 47: knowledge stored as vectors enables retrieval", 24),
        ["round 47: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 47: knowledge stored as vectors enables retrieval", 32),
        ["round 47: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 47: the processor reads the record then stops", 4),
        ["round", "47:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 47: the processor reads the record then stops", 8),
        ["round", "47: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 47: the processor reads the record then stops", 12),
        ["round 47:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 47: the processor reads the record then stops", 16),
        ["round 47: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 47: the processor reads the record then stops", 24),
        ["round 47: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 47: the processor reads the record then stops", 32),
        ["round 47: the processor reads", "the record then stops"],
    ),
    (
        ("round 47: a worker pulls the next task from the queue", 4),
        ["round", "47:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 47: a worker pulls the next task from the queue", 8),
        ["round", "47: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 47: a worker pulls the next task from the queue", 12),
        ["round 47: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 47: a worker pulls the next task from the queue", 16),
        ["round 47: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 47: a worker pulls the next task from the queue", 24),
        ["round 47: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 47: a worker pulls the next task from the queue", 32),
        ["round 47: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 47: signals travel through the network layer", 4),
        ["round", "47:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 47: signals travel through the network layer", 8),
        ["round", "47:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 47: signals travel through the network layer", 12),
        ["round 47:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 47: signals travel through the network layer", 16),
        ["round 47:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 47: signals travel through the network layer", 24),
        ["round 47: signals travel", "through the network", "layer"],
    ),
    (
        ("round 47: signals travel through the network layer", 32),
        ["round 47: signals travel through", "the network layer"],
    ),
    (
        ("round 47: the gateway routes each request by policy", 4),
        ["round", "47:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 47: the gateway routes each request by policy", 8),
        ["round", "47: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 47: the gateway routes each request by policy", 12),
        ["round 47:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 47: the gateway routes each request by policy", 16),
        ["round 47: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 47: the gateway routes each request by policy", 24),
        ["round 47: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 47: the gateway routes each request by policy", 32),
        ["round 47: the gateway routes", "each request by policy"],
    ),
    (
        ("round 47: memory grows until the buffer is full", 4),
        ["round", "47:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 47: memory grows until the buffer is full", 8),
        ["round", "47:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 47: memory grows until the buffer is full", 12),
        ["round 47:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 47: memory grows until the buffer is full", 16),
        ["round 47: memory", "grows until the", "buffer is full"],
    ),
    (("round 47: memory grows until the buffer is full", 24), ["round 47: memory grows", "until the buffer is full"]),
    (("round 47: memory grows until the buffer is full", 32), ["round 47: memory grows until the", "buffer is full"]),
    (
        ("round 47: the cluster mirrors every packet twice", 4),
        ["round", "47:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 47: the cluster mirrors every packet twice", 8),
        ["round", "47: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 47: the cluster mirrors every packet twice", 12),
        ["round 47:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 47: the cluster mirrors every packet twice", 16),
        ["round 47: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 47: the cluster mirrors every packet twice", 24),
        ["round 47: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 47: the cluster mirrors every packet twice", 32), ["round 47: the cluster mirrors", "every packet twice"]),
    (
        ("round 47: ranking uses tokens learned from the corpus", 4),
        ["round", "47:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 47: ranking uses tokens learned from the corpus", 8),
        ["round", "47:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 47: ranking uses tokens learned from the corpus", 12),
        ["round 47:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 47: ranking uses tokens learned from the corpus", 16),
        ["round 47:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 47: ranking uses tokens learned from the corpus", 24),
        ["round 47: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 47: ranking uses tokens learned from the corpus", 32),
        ["round 47: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 47: a long session ends when the candle dies", 4),
        ["round", "47:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 47: a long session ends when the candle dies", 8),
        ["round", "47: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 47: a long session ends when the candle dies", 12),
        ["round 47: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 47: a long session ends when the candle dies", 16),
        ["round 47: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 47: a long session ends when the candle dies", 24),
        ["round 47: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 47: a long session ends when the candle dies", 32),
        ["round 47: a long session ends", "when the candle dies"],
    ),
    (
        ("round 47: encode the prompt then map the result", 4),
        ["round", "47:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 47: encode the prompt then map the result", 8),
        ["round", "47:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 47: encode the prompt then map the result", 12),
        ["round 47:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 47: encode the prompt then map the result", 16),
        ["round 47: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 47: encode the prompt then map the result", 24),
        ["round 47: encode the", "prompt then map the", "result"],
    ),
    (("round 47: encode the prompt then map the result", 32), ["round 47: encode the prompt then", "map the result"]),
    (
        ("round 47: the kernel wakes the worker at dawn", 4),
        ["round", "47:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 47: the kernel wakes the worker at dawn", 8),
        ["round", "47: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 47: the kernel wakes the worker at dawn", 12),
        ["round 47:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 47: the kernel wakes the worker at dawn", 16), ["round 47: the", "kernel wakes the", "worker at dawn"]),
    (("round 47: the kernel wakes the worker at dawn", 24), ["round 47: the kernel", "wakes the worker at dawn"]),
    (("round 47: the kernel wakes the worker at dawn", 32), ["round 47: the kernel wakes the", "worker at dawn"]),
    (
        ("round 47: service latency drops after the patch", 4),
        ["round", "47:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 47: service latency drops after the patch", 8),
        ["round", "47:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 47: service latency drops after the patch", 12),
        ["round 47:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 47: service latency drops after the patch", 16),
        ["round 47:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 47: service latency drops after the patch", 24),
        ["round 47: service", "latency drops after the", "patch"],
    ),
    (("round 47: service latency drops after the patch", 32), ["round 47: service latency drops", "after the patch"]),
    (
        ("round 47: the library caches every vector it sees", 4),
        ["round", "47:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 47: the library caches every vector it sees", 8),
        ["round", "47: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 47: the library caches every vector it sees", 12),
        ["round 47:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 47: the library caches every vector it sees", 16),
        ["round 47: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 47: the library caches every vector it sees", 24),
        ["round 47: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 47: the library caches every vector it sees", 32),
        ["round 47: the library caches", "every vector it sees"],
    ),
    (
        ("round 47: agents argue then the debate resolves", 4),
        ["round", "47:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 47: agents argue then the debate resolves", 8),
        ["round", "47:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 47: agents argue then the debate resolves", 12),
        ["round 47:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 47: agents argue then the debate resolves", 16),
        ["round 47: agents", "argue then the", "debate resolves"],
    ),
    (("round 47: agents argue then the debate resolves", 24), ["round 47: agents argue", "then the debate resolves"]),
    (("round 47: agents argue then the debate resolves", 32), ["round 47: agents argue then the", "debate resolves"]),
    (
        ("round 47: the filter keeps only strong matches", 4),
        ["round", "47:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 47: the filter keeps only strong matches", 8),
        ["round", "47: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 47: the filter keeps only strong matches", 12),
        ["round 47:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 47: the filter keeps only strong matches", 16),
        ["round 47: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 47: the filter keeps only strong matches", 24), ["round 47: the filter", "keeps only strong", "matches"]),
    (("round 47: the filter keeps only strong matches", 32), ["round 47: the filter keeps only", "strong matches"]),
    (
        ("round 47: the model answers with a short reply", 4),
        ["round", "47:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 47: the model answers with a short reply", 8),
        ["round", "47: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 47: the model answers with a short reply", 12),
        ["round 47:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 47: the model answers with a short reply", 16),
        ["round 47: the", "model answers", "with a short", "reply"],
    ),
    (("round 47: the model answers with a short reply", 24), ["round 47: the model", "answers with a short", "reply"]),
    (("round 47: the model answers with a short reply", 32), ["round 47: the model answers with", "a short reply"]),
    (
        ("round 47: the recorder stores the reasoning trace", 4),
        ["round", "47:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 47: the recorder stores the reasoning trace", 8),
        ["round", "47: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 47: the recorder stores the reasoning trace", 12),
        ["round 47:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 47: the recorder stores the reasoning trace", 16),
        ["round 47: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 47: the recorder stores the reasoning trace", 24),
        ["round 47: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 47: the recorder stores the reasoning trace", 32),
        ["round 47: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 47: the angel watches the processor run", 4),
        ["round", "47:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 47: the angel watches the processor run", 8),
        ["round", "47: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 47: the angel watches the processor run", 12),
        ["round 47:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 47: the angel watches the processor run", 16), ["round 47: the", "angel watches", "the processor", "run"]),
    (("round 47: the angel watches the processor run", 24), ["round 47: the angel", "watches the processor", "run"]),
    (("round 47: the angel watches the processor run", 32), ["round 47: the angel watches the", "processor run"]),
    (
        ("round 47: angle of the vector decides the match", 4),
        ["round", "47:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 47: angle of the vector decides the match", 8),
        ["round", "47:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 47: angle of the vector decides the match", 12),
        ["round 47:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 47: angle of the vector decides the match", 16),
        ["round 47: angle", "of the vector", "decides the", "match"],
    ),
    (("round 47: angle of the vector decides the match", 24), ["round 47: angle of the", "vector decides the match"]),
    (("round 47: angle of the vector decides the match", 32), ["round 47: angle of the vector", "decides the match"]),
    (
        ("round 47: the candle burns twice as long at night", 4),
        ["round", "47:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 47: the candle burns twice as long at night", 8),
        ["round", "47: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 47: the candle burns twice as long at night", 12),
        ["round 47:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 47: the candle burns twice as long at night", 16),
        ["round 47: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 47: the candle burns twice as long at night", 24),
        ["round 47: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 47: the candle burns twice as long at night", 32),
        ["round 47: the candle burns twice", "as long at night"],
    ),
    (
        ("round 47: a mirror of the universe in one line", 4),
        ["round", "47:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 47: a mirror of the universe in one line", 8),
        ["round", "47: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 47: a mirror of the universe in one line", 12),
        ["round 47: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 47: a mirror of the universe in one line", 16),
        ["round 47: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 47: a mirror of the universe in one line", 24), ["round 47: a mirror of", "the universe in one line"]),
    (("round 47: a mirror of the universe in one line", 32), ["round 47: a mirror of the", "universe in one line"]),
    (
        ("round 47: the queue drains before the storm", 4),
        ["round", "47:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 47: the queue drains before the storm", 8),
        ["round", "47: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 47: the queue drains before the storm", 12), ["round 47:", "the queue", "drains", "before the", "storm"]),
    (("round 47: the queue drains before the storm", 16), ["round 47: the", "queue drains", "before the storm"]),
    (("round 47: the queue drains before the storm", 24), ["round 47: the queue", "drains before the storm"]),
    (("round 47: the queue drains before the storm", 32), ["round 47: the queue drains", "before the storm"]),
    (
        ("kitten47 sitting47 agent47 angle47 universe47 memory47", 6),
        ["kitten47", "sitting47", "agent47", "angle47", "universe47", "memory47"],
    ),
    (
        ("kitten47 sitting47 agent47 angle47 universe47 memory47", 10),
        ["kitten47", "sitting47", "agent47", "angle47", "universe47", "memory47"],
    ),
    (
        ("kitten47 sitting47 agent47 angle47 universe47 memory47", 18),
        ["kitten47 sitting47", "agent47 angle47", "universe47", "memory47"],
    ),
    (
        ("kitten47 sitting47 agent47 angle47 universe47 memory47", 28),
        ["kitten47 sitting47 agent47", "angle47 universe47 memory47"],
    ),
    (
        ("sitting47 agent47 angle47 universe47 memory47 stream47", 6),
        ["sitting47", "agent47", "angle47", "universe47", "memory47", "stream47"],
    ),
    (
        ("sitting47 agent47 angle47 universe47 memory47 stream47", 10),
        ["sitting47", "agent47", "angle47", "universe47", "memory47", "stream47"],
    ),
    (
        ("sitting47 agent47 angle47 universe47 memory47 stream47", 18),
        ["sitting47 agent47", "angle47 universe47", "memory47 stream47"],
    ),
    (
        ("sitting47 agent47 angle47 universe47 memory47 stream47", 28),
        ["sitting47 agent47 angle47", "universe47 memory47 stream47"],
    ),
    (
        ("agent47 angle47 universe47 memory47 stream47 context47", 6),
        ["agent47", "angle47", "universe47", "memory47", "stream47", "context47"],
    ),
    (
        ("agent47 angle47 universe47 memory47 stream47 context47", 10),
        ["agent47", "angle47", "universe47", "memory47", "stream47", "context47"],
    ),
    (
        ("agent47 angle47 universe47 memory47 stream47 context47", 18),
        ["agent47 angle47", "universe47", "memory47 stream47", "context47"],
    ),
    (
        ("agent47 angle47 universe47 memory47 stream47 context47", 28),
        ["agent47 angle47 universe47", "memory47 stream47 context47"],
    ),
    (
        ("angle47 universe47 memory47 stream47 context47 knowledge47", 6),
        ["angle47", "universe47", "memory47", "stream47", "context47", "knowledge47"],
    ),
    (
        ("angle47 universe47 memory47 stream47 context47 knowledge47", 10),
        ["angle47", "universe47", "memory47", "stream47", "context47", "knowledge47"],
    ),
    (
        ("angle47 universe47 memory47 stream47 context47 knowledge47", 18),
        ["angle47 universe47", "memory47 stream47", "context47", "knowledge47"],
    ),
    (
        ("angle47 universe47 memory47 stream47 context47 knowledge47", 28),
        ["angle47 universe47 memory47", "stream47 context47", "knowledge47"],
    ),
    (
        ("universe47 memory47 stream47 context47 knowledge47 vector47", 6),
        ["universe47", "memory47", "stream47", "context47", "knowledge47", "vector47"],
    ),
    (
        ("universe47 memory47 stream47 context47 knowledge47 vector47", 10),
        ["universe47", "memory47", "stream47", "context47", "knowledge47", "vector47"],
    ),
    (
        ("universe47 memory47 stream47 context47 knowledge47 vector47", 18),
        ["universe47", "memory47 stream47", "context47", "knowledge47", "vector47"],
    ),
    (
        ("universe47 memory47 stream47 context47 knowledge47 vector47", 28),
        ["universe47 memory47 stream47", "context47 knowledge47", "vector47"],
    ),
    (
        ("memory47 stream47 context47 knowledge47 vector47 processor47", 6),
        ["memory47", "stream47", "context47", "knowledge47", "vector47", "processor47"],
    ),
    (
        ("memory47 stream47 context47 knowledge47 vector47 processor47", 10),
        ["memory47", "stream47", "context47", "knowledge47", "vector47", "processor47"],
    ),
    (
        ("memory47 stream47 context47 knowledge47 vector47 processor47", 18),
        ["memory47 stream47", "context47", "knowledge47", "vector47", "processor47"],
    ),
    (
        ("memory47 stream47 context47 knowledge47 vector47 processor47", 28),
        ["memory47 stream47 context47", "knowledge47 vector47", "processor47"],
    ),
    (
        ("stream47 context47 knowledge47 vector47 processor47 reasoning47", 6),
        ["stream47", "context47", "knowledge47", "vector47", "processor47", "reasoning47"],
    ),
    (
        ("stream47 context47 knowledge47 vector47 processor47 reasoning47", 10),
        ["stream47", "context47", "knowledge47", "vector47", "processor47", "reasoning47"],
    ),
    (
        ("stream47 context47 knowledge47 vector47 processor47 reasoning47", 18),
        ["stream47 context47", "knowledge47", "vector47", "processor47", "reasoning47"],
    ),
    (
        ("stream47 context47 knowledge47 vector47 processor47 reasoning47", 28),
        ["stream47 context47", "knowledge47 vector47", "processor47 reasoning47"],
    ),
    (
        ("context47 knowledge47 vector47 processor47 reasoning47 machine47", 6),
        ["context47", "knowledge47", "vector47", "processor47", "reasoning47", "machine47"],
    ),
    (
        ("context47 knowledge47 vector47 processor47 reasoning47 machine47", 10),
        ["context47", "knowledge47", "vector47", "processor47", "reasoning47", "machine47"],
    ),
    (
        ("context47 knowledge47 vector47 processor47 reasoning47 machine47", 18),
        ["context47", "knowledge47", "vector47", "processor47", "reasoning47", "machine47"],
    ),
    (
        ("context47 knowledge47 vector47 processor47 reasoning47 machine47", 28),
        ["context47 knowledge47", "vector47 processor47", "reasoning47 machine47"],
    ),
    (
        ("knowledge47 vector47 processor47 reasoning47 machine47 learning47", 6),
        ["knowledge47", "vector47", "processor47", "reasoning47", "machine47", "learning47"],
    ),
    (
        ("knowledge47 vector47 processor47 reasoning47 machine47 learning47", 10),
        ["knowledge47", "vector47", "processor47", "reasoning47", "machine47", "learning47"],
    ),
    (
        ("knowledge47 vector47 processor47 reasoning47 machine47 learning47", 18),
        ["knowledge47", "vector47", "processor47", "reasoning47", "machine47", "learning47"],
    ),
    (
        ("knowledge47 vector47 processor47 reasoning47 machine47 learning47", 28),
        ["knowledge47 vector47", "processor47 reasoning47", "machine47 learning47"],
    ),
    (
        ("vector47 processor47 reasoning47 machine47 learning47 model47", 6),
        ["vector47", "processor47", "reasoning47", "machine47", "learning47", "model47"],
    ),
    (
        ("vector47 processor47 reasoning47 machine47 learning47 model47", 10),
        ["vector47", "processor47", "reasoning47", "machine47", "learning47", "model47"],
    ),
    (
        ("vector47 processor47 reasoning47 machine47 learning47 model47", 18),
        ["vector47", "processor47", "reasoning47", "machine47", "learning47 model47"],
    ),
    (
        ("vector47 processor47 reasoning47 machine47 learning47 model47", 28),
        ["vector47 processor47", "reasoning47 machine47", "learning47 model47"],
    ),
    (
        ("processor47 reasoning47 machine47 learning47 model47 token47", 6),
        ["processor47", "reasoning47", "machine47", "learning47", "model47", "token47"],
    ),
    (
        ("processor47 reasoning47 machine47 learning47 model47 token47", 10),
        ["processor47", "reasoning47", "machine47", "learning47", "model47", "token47"],
    ),
    (
        ("processor47 reasoning47 machine47 learning47 model47 token47", 18),
        ["processor47", "reasoning47", "machine47", "learning47 model47", "token47"],
    ),
    (
        ("processor47 reasoning47 machine47 learning47 model47 token47", 28),
        ["processor47 reasoning47", "machine47 learning47 model47", "token47"],
    ),
    (
        ("reasoning47 machine47 learning47 model47 token47 prompt47", 6),
        ["reasoning47", "machine47", "learning47", "model47", "token47", "prompt47"],
    ),
    (
        ("reasoning47 machine47 learning47 model47 token47 prompt47", 10),
        ["reasoning47", "machine47", "learning47", "model47", "token47", "prompt47"],
    ),
    (
        ("reasoning47 machine47 learning47 model47 token47 prompt47", 18),
        ["reasoning47", "machine47", "learning47 model47", "token47 prompt47"],
    ),
    (
        ("reasoning47 machine47 learning47 model47 token47 prompt47", 28),
        ["reasoning47 machine47", "learning47 model47 token47", "prompt47"],
    ),
    (
        ("machine47 learning47 model47 token47 prompt47 session47", 6),
        ["machine47", "learning47", "model47", "token47", "prompt47", "session47"],
    ),
    (
        ("machine47 learning47 model47 token47 prompt47 session47", 10),
        ["machine47", "learning47", "model47", "token47", "prompt47", "session47"],
    ),
    (
        ("machine47 learning47 model47 token47 prompt47 session47", 18),
        ["machine47", "learning47 model47", "token47 prompt47", "session47"],
    ),
    (
        ("machine47 learning47 model47 token47 prompt47 session47", 28),
        ["machine47 learning47 model47", "token47 prompt47 session47"],
    ),
    (
        ("learning47 model47 token47 prompt47 session47 library47", 6),
        ["learning47", "model47", "token47", "prompt47", "session47", "library47"],
    ),
    (
        ("learning47 model47 token47 prompt47 session47 library47", 10),
        ["learning47", "model47", "token47", "prompt47", "session47", "library47"],
    ),
    (
        ("learning47 model47 token47 prompt47 session47 library47", 18),
        ["learning47 model47", "token47 prompt47", "session47", "library47"],
    ),
    (
        ("learning47 model47 token47 prompt47 session47 library47", 28),
        ["learning47 model47 token47", "prompt47 session47 library47"],
    ),
    (
        ("model47 token47 prompt47 session47 library47 service47", 6),
        ["model47", "token47", "prompt47", "session47", "library47", "service47"],
    ),
    (
        ("model47 token47 prompt47 session47 library47 service47", 10),
        ["model47", "token47", "prompt47", "session47", "library47", "service47"],
    ),
    (
        ("model47 token47 prompt47 session47 library47 service47", 18),
        ["model47 token47", "prompt47 session47", "library47", "service47"],
    ),
    (
        ("model47 token47 prompt47 session47 library47 service47", 28),
        ["model47 token47 prompt47", "session47 library47", "service47"],
    ),
    (
        ("token47 prompt47 session47 library47 service47 gateway47", 6),
        ["token47", "prompt47", "session47", "library47", "service47", "gateway47"],
    ),
    (
        ("token47 prompt47 session47 library47 service47 gateway47", 10),
        ["token47", "prompt47", "session47", "library47", "service47", "gateway47"],
    ),
    (
        ("token47 prompt47 session47 library47 service47 gateway47", 18),
        ["token47 prompt47", "session47", "library47", "service47", "gateway47"],
    ),
    (
        ("token47 prompt47 session47 library47 service47 gateway47", 28),
        ["token47 prompt47 session47", "library47 service47", "gateway47"],
    ),
    (
        ("prompt47 session47 library47 service47 gateway47 storage47", 6),
        ["prompt47", "session47", "library47", "service47", "gateway47", "storage47"],
    ),
    (
        ("prompt47 session47 library47 service47 gateway47 storage47", 10),
        ["prompt47", "session47", "library47", "service47", "gateway47", "storage47"],
    ),
    (
        ("prompt47 session47 library47 service47 gateway47 storage47", 18),
        ["prompt47 session47", "library47", "service47", "gateway47", "storage47"],
    ),
    (
        ("prompt47 session47 library47 service47 gateway47 storage47", 28),
        ["prompt47 session47 library47", "service47 gateway47", "storage47"],
    ),
    (
        ("session47 library47 service47 gateway47 storage47 network47", 6),
        ["session47", "library47", "service47", "gateway47", "storage47", "network47"],
    ),
    (
        ("session47 library47 service47 gateway47 storage47 network47", 10),
        ["session47", "library47", "service47", "gateway47", "storage47", "network47"],
    ),
    (
        ("session47 library47 service47 gateway47 storage47 network47", 18),
        ["session47", "library47", "service47", "gateway47", "storage47", "network47"],
    ),
    (
        ("session47 library47 service47 gateway47 storage47 network47", 28),
        ["session47 library47", "service47 gateway47", "storage47 network47"],
    ),
    (
        ("library47 service47 gateway47 storage47 network47 latency47", 6),
        ["library47", "service47", "gateway47", "storage47", "network47", "latency47"],
    ),
    (
        ("library47 service47 gateway47 storage47 network47 latency47", 10),
        ["library47", "service47", "gateway47", "storage47", "network47", "latency47"],
    ),
    (
        ("library47 service47 gateway47 storage47 network47 latency47", 18),
        ["library47", "service47", "gateway47", "storage47", "network47", "latency47"],
    ),
    (
        ("library47 service47 gateway47 storage47 network47 latency47", 28),
        ["library47 service47", "gateway47 storage47", "network47 latency47"],
    ),
    (
        ("service47 gateway47 storage47 network47 latency47 buffer47", 6),
        ["service47", "gateway47", "storage47", "network47", "latency47", "buffer47"],
    ),
    (
        ("service47 gateway47 storage47 network47 latency47 buffer47", 10),
        ["service47", "gateway47", "storage47", "network47", "latency47", "buffer47"],
    ),
    (
        ("service47 gateway47 storage47 network47 latency47 buffer47", 18),
        ["service47", "gateway47", "storage47", "network47", "latency47 buffer47"],
    ),
    (
        ("service47 gateway47 storage47 network47 latency47 buffer47", 28),
        ["service47 gateway47", "storage47 network47", "latency47 buffer47"],
    ),
    (
        ("gateway47 storage47 network47 latency47 buffer47 queue47", 6),
        ["gateway47", "storage47", "network47", "latency47", "buffer47", "queue47"],
    ),
    (
        ("gateway47 storage47 network47 latency47 buffer47 queue47", 10),
        ["gateway47", "storage47", "network47", "latency47", "buffer47", "queue47"],
    ),
    (
        ("gateway47 storage47 network47 latency47 buffer47 queue47", 18),
        ["gateway47", "storage47", "network47", "latency47 buffer47", "queue47"],
    ),
    (
        ("gateway47 storage47 network47 latency47 buffer47 queue47", 28),
        ["gateway47 storage47", "network47 latency47 buffer47", "queue47"],
    ),
    (
        ("storage47 network47 latency47 buffer47 queue47 worker47", 6),
        ["storage47", "network47", "latency47", "buffer47", "queue47", "worker47"],
    ),
    (
        ("storage47 network47 latency47 buffer47 queue47 worker47", 10),
        ["storage47", "network47", "latency47", "buffer47", "queue47", "worker47"],
    ),
    (
        ("storage47 network47 latency47 buffer47 queue47 worker47", 18),
        ["storage47", "network47", "latency47 buffer47", "queue47 worker47"],
    ),
    (
        ("storage47 network47 latency47 buffer47 queue47 worker47", 28),
        ["storage47 network47", "latency47 buffer47 queue47", "worker47"],
    ),
    (
        ("network47 latency47 buffer47 queue47 worker47 kernel47", 6),
        ["network47", "latency47", "buffer47", "queue47", "worker47", "kernel47"],
    ),
    (
        ("network47 latency47 buffer47 queue47 worker47 kernel47", 10),
        ["network47", "latency47", "buffer47", "queue47", "worker47", "kernel47"],
    ),
    (
        ("network47 latency47 buffer47 queue47 worker47 kernel47", 18),
        ["network47", "latency47 buffer47", "queue47 worker47", "kernel47"],
    ),
    (
        ("network47 latency47 buffer47 queue47 worker47 kernel47", 28),
        ["network47 latency47 buffer47", "queue47 worker47 kernel47"],
    ),
    (
        ("latency47 buffer47 queue47 worker47 kernel47 signal47", 6),
        ["latency47", "buffer47", "queue47", "worker47", "kernel47", "signal47"],
    ),
    (
        ("latency47 buffer47 queue47 worker47 kernel47 signal47", 10),
        ["latency47", "buffer47", "queue47", "worker47", "kernel47", "signal47"],
    ),
    (
        ("latency47 buffer47 queue47 worker47 kernel47 signal47", 18),
        ["latency47 buffer47", "queue47 worker47", "kernel47 signal47"],
    ),
    (
        ("latency47 buffer47 queue47 worker47 kernel47 signal47", 28),
        ["latency47 buffer47 queue47", "worker47 kernel47 signal47"],
    ),
    (
        ("buffer47 queue47 worker47 kernel47 signal47 packet47", 6),
        ["buffer47", "queue47", "worker47", "kernel47", "signal47", "packet47"],
    ),
    (
        ("buffer47 queue47 worker47 kernel47 signal47 packet47", 10),
        ["buffer47", "queue47", "worker47", "kernel47", "signal47", "packet47"],
    ),
    (
        ("buffer47 queue47 worker47 kernel47 signal47 packet47", 18),
        ["buffer47 queue47", "worker47 kernel47", "signal47 packet47"],
    ),
    (
        ("buffer47 queue47 worker47 kernel47 signal47 packet47", 28),
        ["buffer47 queue47 worker47", "kernel47 signal47 packet47"],
    ),
    (
        ("queue47 worker47 kernel47 signal47 packet47 router47", 6),
        ["queue47", "worker47", "kernel47", "signal47", "packet47", "router47"],
    ),
    (
        ("queue47 worker47 kernel47 signal47 packet47 router47", 10),
        ["queue47", "worker47", "kernel47", "signal47", "packet47", "router47"],
    ),
    (
        ("queue47 worker47 kernel47 signal47 packet47 router47", 18),
        ["queue47 worker47", "kernel47 signal47", "packet47 router47"],
    ),
    (
        ("queue47 worker47 kernel47 signal47 packet47 router47", 28),
        ["queue47 worker47 kernel47", "signal47 packet47 router47"],
    ),
    (
        ("worker47 kernel47 signal47 packet47 router47 cluster47", 6),
        ["worker47", "kernel47", "signal47", "packet47", "router47", "cluster47"],
    ),
    (
        ("worker47 kernel47 signal47 packet47 router47 cluster47", 10),
        ["worker47", "kernel47", "signal47", "packet47", "router47", "cluster47"],
    ),
    (
        ("worker47 kernel47 signal47 packet47 router47 cluster47", 18),
        ["worker47 kernel47", "signal47 packet47", "router47 cluster47"],
    ),
    (
        ("worker47 kernel47 signal47 packet47 router47 cluster47", 28),
        ["worker47 kernel47 signal47", "packet47 router47 cluster47"],
    ),
    (
        ("kernel47 signal47 packet47 router47 cluster47 mirror47", 6),
        ["kernel47", "signal47", "packet47", "router47", "cluster47", "mirror47"],
    ),
    (
        ("kernel47 signal47 packet47 router47 cluster47 mirror47", 10),
        ["kernel47", "signal47", "packet47", "router47", "cluster47", "mirror47"],
    ),
    (
        ("kernel47 signal47 packet47 router47 cluster47 mirror47", 18),
        ["kernel47 signal47", "packet47 router47", "cluster47 mirror47"],
    ),
    (
        ("kernel47 signal47 packet47 router47 cluster47 mirror47", 28),
        ["kernel47 signal47 packet47", "router47 cluster47 mirror47"],
    ),
    (
        ("signal47 packet47 router47 cluster47 mirror47 filter47", 6),
        ["signal47", "packet47", "router47", "cluster47", "mirror47", "filter47"],
    ),
    (
        ("signal47 packet47 router47 cluster47 mirror47 filter47", 10),
        ["signal47", "packet47", "router47", "cluster47", "mirror47", "filter47"],
    ),
    (
        ("signal47 packet47 router47 cluster47 mirror47 filter47", 18),
        ["signal47 packet47", "router47 cluster47", "mirror47 filter47"],
    ),
    (
        ("signal47 packet47 router47 cluster47 mirror47 filter47", 28),
        ["signal47 packet47 router47", "cluster47 mirror47 filter47"],
    ),
    (
        ("packet47 router47 cluster47 mirror47 filter47 ranking47", 6),
        ["packet47", "router47", "cluster47", "mirror47", "filter47", "ranking47"],
    ),
    (
        ("packet47 router47 cluster47 mirror47 filter47 ranking47", 10),
        ["packet47", "router47", "cluster47", "mirror47", "filter47", "ranking47"],
    ),
    (
        ("packet47 router47 cluster47 mirror47 filter47 ranking47", 18),
        ["packet47 router47", "cluster47 mirror47", "filter47 ranking47"],
    ),
    (
        ("packet47 router47 cluster47 mirror47 filter47 ranking47", 28),
        ["packet47 router47 cluster47", "mirror47 filter47 ranking47"],
    ),
    (
        ("router47 cluster47 mirror47 filter47 ranking47 encoding47", 6),
        ["router47", "cluster47", "mirror47", "filter47", "ranking47", "encoding47"],
    ),
    (
        ("router47 cluster47 mirror47 filter47 ranking47 encoding47", 10),
        ["router47", "cluster47", "mirror47", "filter47", "ranking47", "encoding47"],
    ),
    (
        ("router47 cluster47 mirror47 filter47 ranking47 encoding47", 18),
        ["router47 cluster47", "mirror47 filter47", "ranking47", "encoding47"],
    ),
    (
        ("router47 cluster47 mirror47 filter47 ranking47 encoding47", 28),
        ["router47 cluster47 mirror47", "filter47 ranking47", "encoding47"],
    ),
    (
        ("cluster47 mirror47 filter47 ranking47 encoding47 mapping47", 6),
        ["cluster47", "mirror47", "filter47", "ranking47", "encoding47", "mapping47"],
    ),
    (
        ("cluster47 mirror47 filter47 ranking47 encoding47 mapping47", 10),
        ["cluster47", "mirror47", "filter47", "ranking47", "encoding47", "mapping47"],
    ),
    (
        ("cluster47 mirror47 filter47 ranking47 encoding47 mapping47", 18),
        ["cluster47 mirror47", "filter47 ranking47", "encoding47", "mapping47"],
    ),
    (
        ("cluster47 mirror47 filter47 ranking47 encoding47 mapping47", 28),
        ["cluster47 mirror47 filter47", "ranking47 encoding47", "mapping47"],
    ),
    (
        ("mirror47 filter47 ranking47 encoding47 mapping47 record47", 6),
        ["mirror47", "filter47", "ranking47", "encoding47", "mapping47", "record47"],
    ),
    (
        ("mirror47 filter47 ranking47 encoding47 mapping47 record47", 10),
        ["mirror47", "filter47", "ranking47", "encoding47", "mapping47", "record47"],
    ),
    (
        ("mirror47 filter47 ranking47 encoding47 mapping47 record47", 18),
        ["mirror47 filter47", "ranking47", "encoding47", "mapping47 record47"],
    ),
    (
        ("mirror47 filter47 ranking47 encoding47 mapping47 record47", 28),
        ["mirror47 filter47 ranking47", "encoding47 mapping47", "record47"],
    ),
    (
        ("filter47 ranking47 encoding47 mapping47 record47 candle47", 6),
        ["filter47", "ranking47", "encoding47", "mapping47", "record47", "candle47"],
    ),
    (
        ("filter47 ranking47 encoding47 mapping47 record47 candle47", 10),
        ["filter47", "ranking47", "encoding47", "mapping47", "record47", "candle47"],
    ),
    (
        ("filter47 ranking47 encoding47 mapping47 record47 candle47", 18),
        ["filter47 ranking47", "encoding47", "mapping47 record47", "candle47"],
    ),
    (
        ("filter47 ranking47 encoding47 mapping47 record47 candle47", 28),
        ["filter47 ranking47", "encoding47 mapping47", "record47 candle47"],
    ),
    (
        ("ranking47 encoding47 mapping47 record47 candle47 thread47", 6),
        ["ranking47", "encoding47", "mapping47", "record47", "candle47", "thread47"],
    ),
    (
        ("ranking47 encoding47 mapping47 record47 candle47 thread47", 10),
        ["ranking47", "encoding47", "mapping47", "record47", "candle47", "thread47"],
    ),
    (
        ("ranking47 encoding47 mapping47 record47 candle47 thread47", 18),
        ["ranking47", "encoding47", "mapping47 record47", "candle47 thread47"],
    ),
    (
        ("ranking47 encoding47 mapping47 record47 candle47 thread47", 28),
        ["ranking47 encoding47", "mapping47 record47 candle47", "thread47"],
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
