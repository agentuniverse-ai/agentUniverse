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
        ("round 19: the quick brown fox jumps over the lazy dog", 4),
        ["round", "19:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 19: the quick brown fox jumps over the lazy dog", 8),
        ["round", "19: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 19: the quick brown fox jumps over the lazy dog", 12),
        ["round 19:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 19: the quick brown fox jumps over the lazy dog", 16),
        ["round 19: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 19: the quick brown fox jumps over the lazy dog", 24),
        ["round 19: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 19: the quick brown fox jumps over the lazy dog", 32),
        ["round 19: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 19: agentuniverse is a framework for multi agents", 4),
        ["round", "19:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 19: agentuniverse is a framework for multi agents", 8),
        ["round", "19:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 19: agentuniverse is a framework for multi agents", 12),
        ["round 19:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 19: agentuniverse is a framework for multi agents", 16),
        ["round 19:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 19: agentuniverse is a framework for multi agents", 24),
        ["round 19: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 19: agentuniverse is a framework for multi agents", 32),
        ["round 19: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 19: knowledge stored as vectors enables retrieval", 4),
        ["round", "19:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 19: knowledge stored as vectors enables retrieval", 8),
        ["round", "19:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 19: knowledge stored as vectors enables retrieval", 12),
        ["round 19:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 19: knowledge stored as vectors enables retrieval", 16),
        ["round 19:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 19: knowledge stored as vectors enables retrieval", 24),
        ["round 19: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 19: knowledge stored as vectors enables retrieval", 32),
        ["round 19: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 19: the processor reads the record then stops", 4),
        ["round", "19:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 19: the processor reads the record then stops", 8),
        ["round", "19: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 19: the processor reads the record then stops", 12),
        ["round 19:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 19: the processor reads the record then stops", 16),
        ["round 19: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 19: the processor reads the record then stops", 24),
        ["round 19: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 19: the processor reads the record then stops", 32),
        ["round 19: the processor reads", "the record then stops"],
    ),
    (
        ("round 19: a worker pulls the next task from the queue", 4),
        ["round", "19:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 19: a worker pulls the next task from the queue", 8),
        ["round", "19: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 19: a worker pulls the next task from the queue", 12),
        ["round 19: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 19: a worker pulls the next task from the queue", 16),
        ["round 19: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 19: a worker pulls the next task from the queue", 24),
        ["round 19: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 19: a worker pulls the next task from the queue", 32),
        ["round 19: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 19: signals travel through the network layer", 4),
        ["round", "19:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 19: signals travel through the network layer", 8),
        ["round", "19:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 19: signals travel through the network layer", 12),
        ["round 19:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 19: signals travel through the network layer", 16),
        ["round 19:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 19: signals travel through the network layer", 24),
        ["round 19: signals travel", "through the network", "layer"],
    ),
    (
        ("round 19: signals travel through the network layer", 32),
        ["round 19: signals travel through", "the network layer"],
    ),
    (
        ("round 19: the gateway routes each request by policy", 4),
        ["round", "19:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 19: the gateway routes each request by policy", 8),
        ["round", "19: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 19: the gateway routes each request by policy", 12),
        ["round 19:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 19: the gateway routes each request by policy", 16),
        ["round 19: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 19: the gateway routes each request by policy", 24),
        ["round 19: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 19: the gateway routes each request by policy", 32),
        ["round 19: the gateway routes", "each request by policy"],
    ),
    (
        ("round 19: memory grows until the buffer is full", 4),
        ["round", "19:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 19: memory grows until the buffer is full", 8),
        ["round", "19:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 19: memory grows until the buffer is full", 12),
        ["round 19:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 19: memory grows until the buffer is full", 16),
        ["round 19: memory", "grows until the", "buffer is full"],
    ),
    (("round 19: memory grows until the buffer is full", 24), ["round 19: memory grows", "until the buffer is full"]),
    (("round 19: memory grows until the buffer is full", 32), ["round 19: memory grows until the", "buffer is full"]),
    (
        ("round 19: the cluster mirrors every packet twice", 4),
        ["round", "19:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 19: the cluster mirrors every packet twice", 8),
        ["round", "19: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 19: the cluster mirrors every packet twice", 12),
        ["round 19:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 19: the cluster mirrors every packet twice", 16),
        ["round 19: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 19: the cluster mirrors every packet twice", 24),
        ["round 19: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 19: the cluster mirrors every packet twice", 32), ["round 19: the cluster mirrors", "every packet twice"]),
    (
        ("round 19: ranking uses tokens learned from the corpus", 4),
        ["round", "19:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 19: ranking uses tokens learned from the corpus", 8),
        ["round", "19:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 19: ranking uses tokens learned from the corpus", 12),
        ["round 19:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 19: ranking uses tokens learned from the corpus", 16),
        ["round 19:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 19: ranking uses tokens learned from the corpus", 24),
        ["round 19: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 19: ranking uses tokens learned from the corpus", 32),
        ["round 19: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 19: a long session ends when the candle dies", 4),
        ["round", "19:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 19: a long session ends when the candle dies", 8),
        ["round", "19: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 19: a long session ends when the candle dies", 12),
        ["round 19: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 19: a long session ends when the candle dies", 16),
        ["round 19: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 19: a long session ends when the candle dies", 24),
        ["round 19: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 19: a long session ends when the candle dies", 32),
        ["round 19: a long session ends", "when the candle dies"],
    ),
    (
        ("round 19: encode the prompt then map the result", 4),
        ["round", "19:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 19: encode the prompt then map the result", 8),
        ["round", "19:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 19: encode the prompt then map the result", 12),
        ["round 19:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 19: encode the prompt then map the result", 16),
        ["round 19: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 19: encode the prompt then map the result", 24),
        ["round 19: encode the", "prompt then map the", "result"],
    ),
    (("round 19: encode the prompt then map the result", 32), ["round 19: encode the prompt then", "map the result"]),
    (
        ("round 19: the kernel wakes the worker at dawn", 4),
        ["round", "19:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 19: the kernel wakes the worker at dawn", 8),
        ["round", "19: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 19: the kernel wakes the worker at dawn", 12),
        ["round 19:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 19: the kernel wakes the worker at dawn", 16), ["round 19: the", "kernel wakes the", "worker at dawn"]),
    (("round 19: the kernel wakes the worker at dawn", 24), ["round 19: the kernel", "wakes the worker at dawn"]),
    (("round 19: the kernel wakes the worker at dawn", 32), ["round 19: the kernel wakes the", "worker at dawn"]),
    (
        ("round 19: service latency drops after the patch", 4),
        ["round", "19:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 19: service latency drops after the patch", 8),
        ["round", "19:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 19: service latency drops after the patch", 12),
        ["round 19:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 19: service latency drops after the patch", 16),
        ["round 19:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 19: service latency drops after the patch", 24),
        ["round 19: service", "latency drops after the", "patch"],
    ),
    (("round 19: service latency drops after the patch", 32), ["round 19: service latency drops", "after the patch"]),
    (
        ("round 19: the library caches every vector it sees", 4),
        ["round", "19:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 19: the library caches every vector it sees", 8),
        ["round", "19: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 19: the library caches every vector it sees", 12),
        ["round 19:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 19: the library caches every vector it sees", 16),
        ["round 19: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 19: the library caches every vector it sees", 24),
        ["round 19: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 19: the library caches every vector it sees", 32),
        ["round 19: the library caches", "every vector it sees"],
    ),
    (
        ("round 19: agents argue then the debate resolves", 4),
        ["round", "19:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 19: agents argue then the debate resolves", 8),
        ["round", "19:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 19: agents argue then the debate resolves", 12),
        ["round 19:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 19: agents argue then the debate resolves", 16),
        ["round 19: agents", "argue then the", "debate resolves"],
    ),
    (("round 19: agents argue then the debate resolves", 24), ["round 19: agents argue", "then the debate resolves"]),
    (("round 19: agents argue then the debate resolves", 32), ["round 19: agents argue then the", "debate resolves"]),
    (
        ("round 19: the filter keeps only strong matches", 4),
        ["round", "19:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 19: the filter keeps only strong matches", 8),
        ["round", "19: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 19: the filter keeps only strong matches", 12),
        ["round 19:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 19: the filter keeps only strong matches", 16),
        ["round 19: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 19: the filter keeps only strong matches", 24), ["round 19: the filter", "keeps only strong", "matches"]),
    (("round 19: the filter keeps only strong matches", 32), ["round 19: the filter keeps only", "strong matches"]),
    (
        ("round 19: the model answers with a short reply", 4),
        ["round", "19:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 19: the model answers with a short reply", 8),
        ["round", "19: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 19: the model answers with a short reply", 12),
        ["round 19:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 19: the model answers with a short reply", 16),
        ["round 19: the", "model answers", "with a short", "reply"],
    ),
    (("round 19: the model answers with a short reply", 24), ["round 19: the model", "answers with a short", "reply"]),
    (("round 19: the model answers with a short reply", 32), ["round 19: the model answers with", "a short reply"]),
    (
        ("round 19: the recorder stores the reasoning trace", 4),
        ["round", "19:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 19: the recorder stores the reasoning trace", 8),
        ["round", "19: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 19: the recorder stores the reasoning trace", 12),
        ["round 19:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 19: the recorder stores the reasoning trace", 16),
        ["round 19: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 19: the recorder stores the reasoning trace", 24),
        ["round 19: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 19: the recorder stores the reasoning trace", 32),
        ["round 19: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 19: the angel watches the processor run", 4),
        ["round", "19:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 19: the angel watches the processor run", 8),
        ["round", "19: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 19: the angel watches the processor run", 12),
        ["round 19:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 19: the angel watches the processor run", 16), ["round 19: the", "angel watches", "the processor", "run"]),
    (("round 19: the angel watches the processor run", 24), ["round 19: the angel", "watches the processor", "run"]),
    (("round 19: the angel watches the processor run", 32), ["round 19: the angel watches the", "processor run"]),
    (
        ("round 19: angle of the vector decides the match", 4),
        ["round", "19:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 19: angle of the vector decides the match", 8),
        ["round", "19:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 19: angle of the vector decides the match", 12),
        ["round 19:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 19: angle of the vector decides the match", 16),
        ["round 19: angle", "of the vector", "decides the", "match"],
    ),
    (("round 19: angle of the vector decides the match", 24), ["round 19: angle of the", "vector decides the match"]),
    (("round 19: angle of the vector decides the match", 32), ["round 19: angle of the vector", "decides the match"]),
    (
        ("round 19: the candle burns twice as long at night", 4),
        ["round", "19:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 19: the candle burns twice as long at night", 8),
        ["round", "19: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 19: the candle burns twice as long at night", 12),
        ["round 19:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 19: the candle burns twice as long at night", 16),
        ["round 19: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 19: the candle burns twice as long at night", 24),
        ["round 19: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 19: the candle burns twice as long at night", 32),
        ["round 19: the candle burns twice", "as long at night"],
    ),
    (
        ("round 19: a mirror of the universe in one line", 4),
        ["round", "19:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 19: a mirror of the universe in one line", 8),
        ["round", "19: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 19: a mirror of the universe in one line", 12),
        ["round 19: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 19: a mirror of the universe in one line", 16),
        ["round 19: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 19: a mirror of the universe in one line", 24), ["round 19: a mirror of", "the universe in one line"]),
    (("round 19: a mirror of the universe in one line", 32), ["round 19: a mirror of the", "universe in one line"]),
    (
        ("round 19: the queue drains before the storm", 4),
        ["round", "19:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 19: the queue drains before the storm", 8),
        ["round", "19: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 19: the queue drains before the storm", 12), ["round 19:", "the queue", "drains", "before the", "storm"]),
    (("round 19: the queue drains before the storm", 16), ["round 19: the", "queue drains", "before the storm"]),
    (("round 19: the queue drains before the storm", 24), ["round 19: the queue", "drains before the storm"]),
    (("round 19: the queue drains before the storm", 32), ["round 19: the queue drains", "before the storm"]),
    (
        ("kitten19 sitting19 agent19 angle19 universe19 memory19", 6),
        ["kitten19", "sitting19", "agent19", "angle19", "universe19", "memory19"],
    ),
    (
        ("kitten19 sitting19 agent19 angle19 universe19 memory19", 10),
        ["kitten19", "sitting19", "agent19", "angle19", "universe19", "memory19"],
    ),
    (
        ("kitten19 sitting19 agent19 angle19 universe19 memory19", 18),
        ["kitten19 sitting19", "agent19 angle19", "universe19", "memory19"],
    ),
    (
        ("kitten19 sitting19 agent19 angle19 universe19 memory19", 28),
        ["kitten19 sitting19 agent19", "angle19 universe19 memory19"],
    ),
    (
        ("sitting19 agent19 angle19 universe19 memory19 stream19", 6),
        ["sitting19", "agent19", "angle19", "universe19", "memory19", "stream19"],
    ),
    (
        ("sitting19 agent19 angle19 universe19 memory19 stream19", 10),
        ["sitting19", "agent19", "angle19", "universe19", "memory19", "stream19"],
    ),
    (
        ("sitting19 agent19 angle19 universe19 memory19 stream19", 18),
        ["sitting19 agent19", "angle19 universe19", "memory19 stream19"],
    ),
    (
        ("sitting19 agent19 angle19 universe19 memory19 stream19", 28),
        ["sitting19 agent19 angle19", "universe19 memory19 stream19"],
    ),
    (
        ("agent19 angle19 universe19 memory19 stream19 context19", 6),
        ["agent19", "angle19", "universe19", "memory19", "stream19", "context19"],
    ),
    (
        ("agent19 angle19 universe19 memory19 stream19 context19", 10),
        ["agent19", "angle19", "universe19", "memory19", "stream19", "context19"],
    ),
    (
        ("agent19 angle19 universe19 memory19 stream19 context19", 18),
        ["agent19 angle19", "universe19", "memory19 stream19", "context19"],
    ),
    (
        ("agent19 angle19 universe19 memory19 stream19 context19", 28),
        ["agent19 angle19 universe19", "memory19 stream19 context19"],
    ),
    (
        ("angle19 universe19 memory19 stream19 context19 knowledge19", 6),
        ["angle19", "universe19", "memory19", "stream19", "context19", "knowledge19"],
    ),
    (
        ("angle19 universe19 memory19 stream19 context19 knowledge19", 10),
        ["angle19", "universe19", "memory19", "stream19", "context19", "knowledge19"],
    ),
    (
        ("angle19 universe19 memory19 stream19 context19 knowledge19", 18),
        ["angle19 universe19", "memory19 stream19", "context19", "knowledge19"],
    ),
    (
        ("angle19 universe19 memory19 stream19 context19 knowledge19", 28),
        ["angle19 universe19 memory19", "stream19 context19", "knowledge19"],
    ),
    (
        ("universe19 memory19 stream19 context19 knowledge19 vector19", 6),
        ["universe19", "memory19", "stream19", "context19", "knowledge19", "vector19"],
    ),
    (
        ("universe19 memory19 stream19 context19 knowledge19 vector19", 10),
        ["universe19", "memory19", "stream19", "context19", "knowledge19", "vector19"],
    ),
    (
        ("universe19 memory19 stream19 context19 knowledge19 vector19", 18),
        ["universe19", "memory19 stream19", "context19", "knowledge19", "vector19"],
    ),
    (
        ("universe19 memory19 stream19 context19 knowledge19 vector19", 28),
        ["universe19 memory19 stream19", "context19 knowledge19", "vector19"],
    ),
    (
        ("memory19 stream19 context19 knowledge19 vector19 processor19", 6),
        ["memory19", "stream19", "context19", "knowledge19", "vector19", "processor19"],
    ),
    (
        ("memory19 stream19 context19 knowledge19 vector19 processor19", 10),
        ["memory19", "stream19", "context19", "knowledge19", "vector19", "processor19"],
    ),
    (
        ("memory19 stream19 context19 knowledge19 vector19 processor19", 18),
        ["memory19 stream19", "context19", "knowledge19", "vector19", "processor19"],
    ),
    (
        ("memory19 stream19 context19 knowledge19 vector19 processor19", 28),
        ["memory19 stream19 context19", "knowledge19 vector19", "processor19"],
    ),
    (
        ("stream19 context19 knowledge19 vector19 processor19 reasoning19", 6),
        ["stream19", "context19", "knowledge19", "vector19", "processor19", "reasoning19"],
    ),
    (
        ("stream19 context19 knowledge19 vector19 processor19 reasoning19", 10),
        ["stream19", "context19", "knowledge19", "vector19", "processor19", "reasoning19"],
    ),
    (
        ("stream19 context19 knowledge19 vector19 processor19 reasoning19", 18),
        ["stream19 context19", "knowledge19", "vector19", "processor19", "reasoning19"],
    ),
    (
        ("stream19 context19 knowledge19 vector19 processor19 reasoning19", 28),
        ["stream19 context19", "knowledge19 vector19", "processor19 reasoning19"],
    ),
    (
        ("context19 knowledge19 vector19 processor19 reasoning19 machine19", 6),
        ["context19", "knowledge19", "vector19", "processor19", "reasoning19", "machine19"],
    ),
    (
        ("context19 knowledge19 vector19 processor19 reasoning19 machine19", 10),
        ["context19", "knowledge19", "vector19", "processor19", "reasoning19", "machine19"],
    ),
    (
        ("context19 knowledge19 vector19 processor19 reasoning19 machine19", 18),
        ["context19", "knowledge19", "vector19", "processor19", "reasoning19", "machine19"],
    ),
    (
        ("context19 knowledge19 vector19 processor19 reasoning19 machine19", 28),
        ["context19 knowledge19", "vector19 processor19", "reasoning19 machine19"],
    ),
    (
        ("knowledge19 vector19 processor19 reasoning19 machine19 learning19", 6),
        ["knowledge19", "vector19", "processor19", "reasoning19", "machine19", "learning19"],
    ),
    (
        ("knowledge19 vector19 processor19 reasoning19 machine19 learning19", 10),
        ["knowledge19", "vector19", "processor19", "reasoning19", "machine19", "learning19"],
    ),
    (
        ("knowledge19 vector19 processor19 reasoning19 machine19 learning19", 18),
        ["knowledge19", "vector19", "processor19", "reasoning19", "machine19", "learning19"],
    ),
    (
        ("knowledge19 vector19 processor19 reasoning19 machine19 learning19", 28),
        ["knowledge19 vector19", "processor19 reasoning19", "machine19 learning19"],
    ),
    (
        ("vector19 processor19 reasoning19 machine19 learning19 model19", 6),
        ["vector19", "processor19", "reasoning19", "machine19", "learning19", "model19"],
    ),
    (
        ("vector19 processor19 reasoning19 machine19 learning19 model19", 10),
        ["vector19", "processor19", "reasoning19", "machine19", "learning19", "model19"],
    ),
    (
        ("vector19 processor19 reasoning19 machine19 learning19 model19", 18),
        ["vector19", "processor19", "reasoning19", "machine19", "learning19 model19"],
    ),
    (
        ("vector19 processor19 reasoning19 machine19 learning19 model19", 28),
        ["vector19 processor19", "reasoning19 machine19", "learning19 model19"],
    ),
    (
        ("processor19 reasoning19 machine19 learning19 model19 token19", 6),
        ["processor19", "reasoning19", "machine19", "learning19", "model19", "token19"],
    ),
    (
        ("processor19 reasoning19 machine19 learning19 model19 token19", 10),
        ["processor19", "reasoning19", "machine19", "learning19", "model19", "token19"],
    ),
    (
        ("processor19 reasoning19 machine19 learning19 model19 token19", 18),
        ["processor19", "reasoning19", "machine19", "learning19 model19", "token19"],
    ),
    (
        ("processor19 reasoning19 machine19 learning19 model19 token19", 28),
        ["processor19 reasoning19", "machine19 learning19 model19", "token19"],
    ),
    (
        ("reasoning19 machine19 learning19 model19 token19 prompt19", 6),
        ["reasoning19", "machine19", "learning19", "model19", "token19", "prompt19"],
    ),
    (
        ("reasoning19 machine19 learning19 model19 token19 prompt19", 10),
        ["reasoning19", "machine19", "learning19", "model19", "token19", "prompt19"],
    ),
    (
        ("reasoning19 machine19 learning19 model19 token19 prompt19", 18),
        ["reasoning19", "machine19", "learning19 model19", "token19 prompt19"],
    ),
    (
        ("reasoning19 machine19 learning19 model19 token19 prompt19", 28),
        ["reasoning19 machine19", "learning19 model19 token19", "prompt19"],
    ),
    (
        ("machine19 learning19 model19 token19 prompt19 session19", 6),
        ["machine19", "learning19", "model19", "token19", "prompt19", "session19"],
    ),
    (
        ("machine19 learning19 model19 token19 prompt19 session19", 10),
        ["machine19", "learning19", "model19", "token19", "prompt19", "session19"],
    ),
    (
        ("machine19 learning19 model19 token19 prompt19 session19", 18),
        ["machine19", "learning19 model19", "token19 prompt19", "session19"],
    ),
    (
        ("machine19 learning19 model19 token19 prompt19 session19", 28),
        ["machine19 learning19 model19", "token19 prompt19 session19"],
    ),
    (
        ("learning19 model19 token19 prompt19 session19 library19", 6),
        ["learning19", "model19", "token19", "prompt19", "session19", "library19"],
    ),
    (
        ("learning19 model19 token19 prompt19 session19 library19", 10),
        ["learning19", "model19", "token19", "prompt19", "session19", "library19"],
    ),
    (
        ("learning19 model19 token19 prompt19 session19 library19", 18),
        ["learning19 model19", "token19 prompt19", "session19", "library19"],
    ),
    (
        ("learning19 model19 token19 prompt19 session19 library19", 28),
        ["learning19 model19 token19", "prompt19 session19 library19"],
    ),
    (
        ("model19 token19 prompt19 session19 library19 service19", 6),
        ["model19", "token19", "prompt19", "session19", "library19", "service19"],
    ),
    (
        ("model19 token19 prompt19 session19 library19 service19", 10),
        ["model19", "token19", "prompt19", "session19", "library19", "service19"],
    ),
    (
        ("model19 token19 prompt19 session19 library19 service19", 18),
        ["model19 token19", "prompt19 session19", "library19", "service19"],
    ),
    (
        ("model19 token19 prompt19 session19 library19 service19", 28),
        ["model19 token19 prompt19", "session19 library19", "service19"],
    ),
    (
        ("token19 prompt19 session19 library19 service19 gateway19", 6),
        ["token19", "prompt19", "session19", "library19", "service19", "gateway19"],
    ),
    (
        ("token19 prompt19 session19 library19 service19 gateway19", 10),
        ["token19", "prompt19", "session19", "library19", "service19", "gateway19"],
    ),
    (
        ("token19 prompt19 session19 library19 service19 gateway19", 18),
        ["token19 prompt19", "session19", "library19", "service19", "gateway19"],
    ),
    (
        ("token19 prompt19 session19 library19 service19 gateway19", 28),
        ["token19 prompt19 session19", "library19 service19", "gateway19"],
    ),
    (
        ("prompt19 session19 library19 service19 gateway19 storage19", 6),
        ["prompt19", "session19", "library19", "service19", "gateway19", "storage19"],
    ),
    (
        ("prompt19 session19 library19 service19 gateway19 storage19", 10),
        ["prompt19", "session19", "library19", "service19", "gateway19", "storage19"],
    ),
    (
        ("prompt19 session19 library19 service19 gateway19 storage19", 18),
        ["prompt19 session19", "library19", "service19", "gateway19", "storage19"],
    ),
    (
        ("prompt19 session19 library19 service19 gateway19 storage19", 28),
        ["prompt19 session19 library19", "service19 gateway19", "storage19"],
    ),
    (
        ("session19 library19 service19 gateway19 storage19 network19", 6),
        ["session19", "library19", "service19", "gateway19", "storage19", "network19"],
    ),
    (
        ("session19 library19 service19 gateway19 storage19 network19", 10),
        ["session19", "library19", "service19", "gateway19", "storage19", "network19"],
    ),
    (
        ("session19 library19 service19 gateway19 storage19 network19", 18),
        ["session19", "library19", "service19", "gateway19", "storage19", "network19"],
    ),
    (
        ("session19 library19 service19 gateway19 storage19 network19", 28),
        ["session19 library19", "service19 gateway19", "storage19 network19"],
    ),
    (
        ("library19 service19 gateway19 storage19 network19 latency19", 6),
        ["library19", "service19", "gateway19", "storage19", "network19", "latency19"],
    ),
    (
        ("library19 service19 gateway19 storage19 network19 latency19", 10),
        ["library19", "service19", "gateway19", "storage19", "network19", "latency19"],
    ),
    (
        ("library19 service19 gateway19 storage19 network19 latency19", 18),
        ["library19", "service19", "gateway19", "storage19", "network19", "latency19"],
    ),
    (
        ("library19 service19 gateway19 storage19 network19 latency19", 28),
        ["library19 service19", "gateway19 storage19", "network19 latency19"],
    ),
    (
        ("service19 gateway19 storage19 network19 latency19 buffer19", 6),
        ["service19", "gateway19", "storage19", "network19", "latency19", "buffer19"],
    ),
    (
        ("service19 gateway19 storage19 network19 latency19 buffer19", 10),
        ["service19", "gateway19", "storage19", "network19", "latency19", "buffer19"],
    ),
    (
        ("service19 gateway19 storage19 network19 latency19 buffer19", 18),
        ["service19", "gateway19", "storage19", "network19", "latency19 buffer19"],
    ),
    (
        ("service19 gateway19 storage19 network19 latency19 buffer19", 28),
        ["service19 gateway19", "storage19 network19", "latency19 buffer19"],
    ),
    (
        ("gateway19 storage19 network19 latency19 buffer19 queue19", 6),
        ["gateway19", "storage19", "network19", "latency19", "buffer19", "queue19"],
    ),
    (
        ("gateway19 storage19 network19 latency19 buffer19 queue19", 10),
        ["gateway19", "storage19", "network19", "latency19", "buffer19", "queue19"],
    ),
    (
        ("gateway19 storage19 network19 latency19 buffer19 queue19", 18),
        ["gateway19", "storage19", "network19", "latency19 buffer19", "queue19"],
    ),
    (
        ("gateway19 storage19 network19 latency19 buffer19 queue19", 28),
        ["gateway19 storage19", "network19 latency19 buffer19", "queue19"],
    ),
    (
        ("storage19 network19 latency19 buffer19 queue19 worker19", 6),
        ["storage19", "network19", "latency19", "buffer19", "queue19", "worker19"],
    ),
    (
        ("storage19 network19 latency19 buffer19 queue19 worker19", 10),
        ["storage19", "network19", "latency19", "buffer19", "queue19", "worker19"],
    ),
    (
        ("storage19 network19 latency19 buffer19 queue19 worker19", 18),
        ["storage19", "network19", "latency19 buffer19", "queue19 worker19"],
    ),
    (
        ("storage19 network19 latency19 buffer19 queue19 worker19", 28),
        ["storage19 network19", "latency19 buffer19 queue19", "worker19"],
    ),
    (
        ("network19 latency19 buffer19 queue19 worker19 kernel19", 6),
        ["network19", "latency19", "buffer19", "queue19", "worker19", "kernel19"],
    ),
    (
        ("network19 latency19 buffer19 queue19 worker19 kernel19", 10),
        ["network19", "latency19", "buffer19", "queue19", "worker19", "kernel19"],
    ),
    (
        ("network19 latency19 buffer19 queue19 worker19 kernel19", 18),
        ["network19", "latency19 buffer19", "queue19 worker19", "kernel19"],
    ),
    (
        ("network19 latency19 buffer19 queue19 worker19 kernel19", 28),
        ["network19 latency19 buffer19", "queue19 worker19 kernel19"],
    ),
    (
        ("latency19 buffer19 queue19 worker19 kernel19 signal19", 6),
        ["latency19", "buffer19", "queue19", "worker19", "kernel19", "signal19"],
    ),
    (
        ("latency19 buffer19 queue19 worker19 kernel19 signal19", 10),
        ["latency19", "buffer19", "queue19", "worker19", "kernel19", "signal19"],
    ),
    (
        ("latency19 buffer19 queue19 worker19 kernel19 signal19", 18),
        ["latency19 buffer19", "queue19 worker19", "kernel19 signal19"],
    ),
    (
        ("latency19 buffer19 queue19 worker19 kernel19 signal19", 28),
        ["latency19 buffer19 queue19", "worker19 kernel19 signal19"],
    ),
    (
        ("buffer19 queue19 worker19 kernel19 signal19 packet19", 6),
        ["buffer19", "queue19", "worker19", "kernel19", "signal19", "packet19"],
    ),
    (
        ("buffer19 queue19 worker19 kernel19 signal19 packet19", 10),
        ["buffer19", "queue19", "worker19", "kernel19", "signal19", "packet19"],
    ),
    (
        ("buffer19 queue19 worker19 kernel19 signal19 packet19", 18),
        ["buffer19 queue19", "worker19 kernel19", "signal19 packet19"],
    ),
    (
        ("buffer19 queue19 worker19 kernel19 signal19 packet19", 28),
        ["buffer19 queue19 worker19", "kernel19 signal19 packet19"],
    ),
    (
        ("queue19 worker19 kernel19 signal19 packet19 router19", 6),
        ["queue19", "worker19", "kernel19", "signal19", "packet19", "router19"],
    ),
    (
        ("queue19 worker19 kernel19 signal19 packet19 router19", 10),
        ["queue19", "worker19", "kernel19", "signal19", "packet19", "router19"],
    ),
    (
        ("queue19 worker19 kernel19 signal19 packet19 router19", 18),
        ["queue19 worker19", "kernel19 signal19", "packet19 router19"],
    ),
    (
        ("queue19 worker19 kernel19 signal19 packet19 router19", 28),
        ["queue19 worker19 kernel19", "signal19 packet19 router19"],
    ),
    (
        ("worker19 kernel19 signal19 packet19 router19 cluster19", 6),
        ["worker19", "kernel19", "signal19", "packet19", "router19", "cluster19"],
    ),
    (
        ("worker19 kernel19 signal19 packet19 router19 cluster19", 10),
        ["worker19", "kernel19", "signal19", "packet19", "router19", "cluster19"],
    ),
    (
        ("worker19 kernel19 signal19 packet19 router19 cluster19", 18),
        ["worker19 kernel19", "signal19 packet19", "router19 cluster19"],
    ),
    (
        ("worker19 kernel19 signal19 packet19 router19 cluster19", 28),
        ["worker19 kernel19 signal19", "packet19 router19 cluster19"],
    ),
    (
        ("kernel19 signal19 packet19 router19 cluster19 mirror19", 6),
        ["kernel19", "signal19", "packet19", "router19", "cluster19", "mirror19"],
    ),
    (
        ("kernel19 signal19 packet19 router19 cluster19 mirror19", 10),
        ["kernel19", "signal19", "packet19", "router19", "cluster19", "mirror19"],
    ),
    (
        ("kernel19 signal19 packet19 router19 cluster19 mirror19", 18),
        ["kernel19 signal19", "packet19 router19", "cluster19 mirror19"],
    ),
    (
        ("kernel19 signal19 packet19 router19 cluster19 mirror19", 28),
        ["kernel19 signal19 packet19", "router19 cluster19 mirror19"],
    ),
    (
        ("signal19 packet19 router19 cluster19 mirror19 filter19", 6),
        ["signal19", "packet19", "router19", "cluster19", "mirror19", "filter19"],
    ),
    (
        ("signal19 packet19 router19 cluster19 mirror19 filter19", 10),
        ["signal19", "packet19", "router19", "cluster19", "mirror19", "filter19"],
    ),
    (
        ("signal19 packet19 router19 cluster19 mirror19 filter19", 18),
        ["signal19 packet19", "router19 cluster19", "mirror19 filter19"],
    ),
    (
        ("signal19 packet19 router19 cluster19 mirror19 filter19", 28),
        ["signal19 packet19 router19", "cluster19 mirror19 filter19"],
    ),
    (
        ("packet19 router19 cluster19 mirror19 filter19 ranking19", 6),
        ["packet19", "router19", "cluster19", "mirror19", "filter19", "ranking19"],
    ),
    (
        ("packet19 router19 cluster19 mirror19 filter19 ranking19", 10),
        ["packet19", "router19", "cluster19", "mirror19", "filter19", "ranking19"],
    ),
    (
        ("packet19 router19 cluster19 mirror19 filter19 ranking19", 18),
        ["packet19 router19", "cluster19 mirror19", "filter19 ranking19"],
    ),
    (
        ("packet19 router19 cluster19 mirror19 filter19 ranking19", 28),
        ["packet19 router19 cluster19", "mirror19 filter19 ranking19"],
    ),
    (
        ("router19 cluster19 mirror19 filter19 ranking19 encoding19", 6),
        ["router19", "cluster19", "mirror19", "filter19", "ranking19", "encoding19"],
    ),
    (
        ("router19 cluster19 mirror19 filter19 ranking19 encoding19", 10),
        ["router19", "cluster19", "mirror19", "filter19", "ranking19", "encoding19"],
    ),
    (
        ("router19 cluster19 mirror19 filter19 ranking19 encoding19", 18),
        ["router19 cluster19", "mirror19 filter19", "ranking19", "encoding19"],
    ),
    (
        ("router19 cluster19 mirror19 filter19 ranking19 encoding19", 28),
        ["router19 cluster19 mirror19", "filter19 ranking19", "encoding19"],
    ),
    (
        ("cluster19 mirror19 filter19 ranking19 encoding19 mapping19", 6),
        ["cluster19", "mirror19", "filter19", "ranking19", "encoding19", "mapping19"],
    ),
    (
        ("cluster19 mirror19 filter19 ranking19 encoding19 mapping19", 10),
        ["cluster19", "mirror19", "filter19", "ranking19", "encoding19", "mapping19"],
    ),
    (
        ("cluster19 mirror19 filter19 ranking19 encoding19 mapping19", 18),
        ["cluster19 mirror19", "filter19 ranking19", "encoding19", "mapping19"],
    ),
    (
        ("cluster19 mirror19 filter19 ranking19 encoding19 mapping19", 28),
        ["cluster19 mirror19 filter19", "ranking19 encoding19", "mapping19"],
    ),
    (
        ("mirror19 filter19 ranking19 encoding19 mapping19 record19", 6),
        ["mirror19", "filter19", "ranking19", "encoding19", "mapping19", "record19"],
    ),
    (
        ("mirror19 filter19 ranking19 encoding19 mapping19 record19", 10),
        ["mirror19", "filter19", "ranking19", "encoding19", "mapping19", "record19"],
    ),
    (
        ("mirror19 filter19 ranking19 encoding19 mapping19 record19", 18),
        ["mirror19 filter19", "ranking19", "encoding19", "mapping19 record19"],
    ),
    (
        ("mirror19 filter19 ranking19 encoding19 mapping19 record19", 28),
        ["mirror19 filter19 ranking19", "encoding19 mapping19", "record19"],
    ),
    (
        ("filter19 ranking19 encoding19 mapping19 record19 candle19", 6),
        ["filter19", "ranking19", "encoding19", "mapping19", "record19", "candle19"],
    ),
    (
        ("filter19 ranking19 encoding19 mapping19 record19 candle19", 10),
        ["filter19", "ranking19", "encoding19", "mapping19", "record19", "candle19"],
    ),
    (
        ("filter19 ranking19 encoding19 mapping19 record19 candle19", 18),
        ["filter19 ranking19", "encoding19", "mapping19 record19", "candle19"],
    ),
    (
        ("filter19 ranking19 encoding19 mapping19 record19 candle19", 28),
        ["filter19 ranking19", "encoding19 mapping19", "record19 candle19"],
    ),
    (
        ("ranking19 encoding19 mapping19 record19 candle19 thread19", 6),
        ["ranking19", "encoding19", "mapping19", "record19", "candle19", "thread19"],
    ),
    (
        ("ranking19 encoding19 mapping19 record19 candle19 thread19", 10),
        ["ranking19", "encoding19", "mapping19", "record19", "candle19", "thread19"],
    ),
    (
        ("ranking19 encoding19 mapping19 record19 candle19 thread19", 18),
        ["ranking19", "encoding19", "mapping19 record19", "candle19 thread19"],
    ),
    (
        ("ranking19 encoding19 mapping19 record19 candle19 thread19", 28),
        ["ranking19 encoding19", "mapping19 record19 candle19", "thread19"],
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
