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
        ("round 118: the quick brown fox jumps over the lazy dog", 4),
        ["round", "118:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 118: the quick brown fox jumps over the lazy dog", 8),
        ["round", "118: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 118: the quick brown fox jumps over the lazy dog", 12),
        ["round 118:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 118: the quick brown fox jumps over the lazy dog", 16),
        ["round 118: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 118: the quick brown fox jumps over the lazy dog", 24),
        ["round 118: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 118: the quick brown fox jumps over the lazy dog", 32),
        ["round 118: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 118: agentuniverse is a framework for multi agents", 4),
        ["round", "118:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 118: agentuniverse is a framework for multi agents", 8),
        ["round", "118:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 118: agentuniverse is a framework for multi agents", 12),
        ["round 118:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 118: agentuniverse is a framework for multi agents", 16),
        ["round 118:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 118: agentuniverse is a framework for multi agents", 24),
        ["round 118: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 118: agentuniverse is a framework for multi agents", 32),
        ["round 118: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 118: knowledge stored as vectors enables retrieval", 4),
        ["round", "118:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 118: knowledge stored as vectors enables retrieval", 8),
        ["round", "118:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 118: knowledge stored as vectors enables retrieval", 12),
        ["round 118:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 118: knowledge stored as vectors enables retrieval", 16),
        ["round 118:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 118: knowledge stored as vectors enables retrieval", 24),
        ["round 118: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 118: knowledge stored as vectors enables retrieval", 32),
        ["round 118: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 118: the processor reads the record then stops", 4),
        ["round", "118:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 118: the processor reads the record then stops", 8),
        ["round", "118: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 118: the processor reads the record then stops", 12),
        ["round 118:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 118: the processor reads the record then stops", 16),
        ["round 118: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 118: the processor reads the record then stops", 24),
        ["round 118: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 118: the processor reads the record then stops", 32),
        ["round 118: the processor reads", "the record then stops"],
    ),
    (
        ("round 118: a worker pulls the next task from the queue", 4),
        ["round", "118:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 118: a worker pulls the next task from the queue", 8),
        ["round", "118: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 118: a worker pulls the next task from the queue", 12),
        ["round 118: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 118: a worker pulls the next task from the queue", 16),
        ["round 118: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 118: a worker pulls the next task from the queue", 24),
        ["round 118: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 118: a worker pulls the next task from the queue", 32),
        ["round 118: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 118: signals travel through the network layer", 4),
        ["round", "118:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 118: signals travel through the network layer", 8),
        ["round", "118:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 118: signals travel through the network layer", 12),
        ["round 118:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 118: signals travel through the network layer", 16),
        ["round 118:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 118: signals travel through the network layer", 24),
        ["round 118: signals", "travel through the", "network layer"],
    ),
    (
        ("round 118: signals travel through the network layer", 32),
        ["round 118: signals travel", "through the network layer"],
    ),
    (
        ("round 118: the gateway routes each request by policy", 4),
        ["round", "118:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 118: the gateway routes each request by policy", 8),
        ["round", "118: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 118: the gateway routes each request by policy", 12),
        ["round 118:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 118: the gateway routes each request by policy", 16),
        ["round 118: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 118: the gateway routes each request by policy", 24),
        ["round 118: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 118: the gateway routes each request by policy", 32),
        ["round 118: the gateway routes", "each request by policy"],
    ),
    (
        ("round 118: memory grows until the buffer is full", 4),
        ["round", "118:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 118: memory grows until the buffer is full", 8),
        ["round", "118:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 118: memory grows until the buffer is full", 12),
        ["round 118:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 118: memory grows until the buffer is full", 16),
        ["round 118:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 118: memory grows until the buffer is full", 24), ["round 118: memory grows", "until the buffer is full"]),
    (("round 118: memory grows until the buffer is full", 32), ["round 118: memory grows until", "the buffer is full"]),
    (
        ("round 118: the cluster mirrors every packet twice", 4),
        ["round", "118:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 118: the cluster mirrors every packet twice", 8),
        ["round", "118: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 118: the cluster mirrors every packet twice", 12),
        ["round 118:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 118: the cluster mirrors every packet twice", 16),
        ["round 118: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 118: the cluster mirrors every packet twice", 24),
        ["round 118: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 118: the cluster mirrors every packet twice", 32),
        ["round 118: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 118: ranking uses tokens learned from the corpus", 4),
        ["round", "118:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 118: ranking uses tokens learned from the corpus", 8),
        ["round", "118:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 118: ranking uses tokens learned from the corpus", 12),
        ["round 118:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 118: ranking uses tokens learned from the corpus", 16),
        ["round 118:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 118: ranking uses tokens learned from the corpus", 24),
        ["round 118: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 118: ranking uses tokens learned from the corpus", 32),
        ["round 118: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 118: a long session ends when the candle dies", 4),
        ["round", "118:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 118: a long session ends when the candle dies", 8),
        ["round", "118: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 118: a long session ends when the candle dies", 12),
        ["round 118: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 118: a long session ends when the candle dies", 16),
        ["round 118: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 118: a long session ends when the candle dies", 24),
        ["round 118: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 118: a long session ends when the candle dies", 32),
        ["round 118: a long session ends", "when the candle dies"],
    ),
    (
        ("round 118: encode the prompt then map the result", 4),
        ["round", "118:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 118: encode the prompt then map the result", 8),
        ["round", "118:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 118: encode the prompt then map the result", 12),
        ["round 118:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 118: encode the prompt then map the result", 16),
        ["round 118:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 118: encode the prompt then map the result", 24),
        ["round 118: encode the", "prompt then map the", "result"],
    ),
    (("round 118: encode the prompt then map the result", 32), ["round 118: encode the prompt", "then map the result"]),
    (
        ("round 118: the kernel wakes the worker at dawn", 4),
        ["round", "118:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 118: the kernel wakes the worker at dawn", 8),
        ["round", "118: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 118: the kernel wakes the worker at dawn", 12),
        ["round 118:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 118: the kernel wakes the worker at dawn", 16), ["round 118: the", "kernel wakes the", "worker at dawn"]),
    (("round 118: the kernel wakes the worker at dawn", 24), ["round 118: the kernel", "wakes the worker at dawn"]),
    (("round 118: the kernel wakes the worker at dawn", 32), ["round 118: the kernel wakes the", "worker at dawn"]),
    (
        ("round 118: service latency drops after the patch", 4),
        ["round", "118:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 118: service latency drops after the patch", 8),
        ["round", "118:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 118: service latency drops after the patch", 12),
        ["round 118:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 118: service latency drops after the patch", 16),
        ["round 118:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 118: service latency drops after the patch", 24),
        ["round 118: service", "latency drops after the", "patch"],
    ),
    (("round 118: service latency drops after the patch", 32), ["round 118: service latency drops", "after the patch"]),
    (
        ("round 118: the library caches every vector it sees", 4),
        ["round", "118:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 118: the library caches every vector it sees", 8),
        ["round", "118: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 118: the library caches every vector it sees", 12),
        ["round 118:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 118: the library caches every vector it sees", 16),
        ["round 118: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 118: the library caches every vector it sees", 24),
        ["round 118: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 118: the library caches every vector it sees", 32),
        ["round 118: the library caches", "every vector it sees"],
    ),
    (
        ("round 118: agents argue then the debate resolves", 4),
        ["round", "118:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 118: agents argue then the debate resolves", 8),
        ["round", "118:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 118: agents argue then the debate resolves", 12),
        ["round 118:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 118: agents argue then the debate resolves", 16),
        ["round 118:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 118: agents argue then the debate resolves", 24), ["round 118: agents argue", "then the debate resolves"]),
    (("round 118: agents argue then the debate resolves", 32), ["round 118: agents argue then the", "debate resolves"]),
    (
        ("round 118: the filter keeps only strong matches", 4),
        ["round", "118:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 118: the filter keeps only strong matches", 8),
        ["round", "118: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 118: the filter keeps only strong matches", 12),
        ["round 118:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 118: the filter keeps only strong matches", 16),
        ["round 118: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 118: the filter keeps only strong matches", 24),
        ["round 118: the filter", "keeps only strong", "matches"],
    ),
    (("round 118: the filter keeps only strong matches", 32), ["round 118: the filter keeps only", "strong matches"]),
    (
        ("round 118: the model answers with a short reply", 4),
        ["round", "118:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 118: the model answers with a short reply", 8),
        ["round", "118: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 118: the model answers with a short reply", 12),
        ["round 118:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 118: the model answers with a short reply", 16),
        ["round 118: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 118: the model answers with a short reply", 24),
        ["round 118: the model", "answers with a short", "reply"],
    ),
    (("round 118: the model answers with a short reply", 32), ["round 118: the model answers", "with a short reply"]),
    (
        ("round 118: the recorder stores the reasoning trace", 4),
        ["round", "118:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 118: the recorder stores the reasoning trace", 8),
        ["round", "118: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 118: the recorder stores the reasoning trace", 12),
        ["round 118:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 118: the recorder stores the reasoning trace", 16),
        ["round 118: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 118: the recorder stores the reasoning trace", 24),
        ["round 118: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 118: the recorder stores the reasoning trace", 32),
        ["round 118: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 118: the angel watches the processor run", 4),
        ["round", "118:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 118: the angel watches the processor run", 8),
        ["round", "118: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 118: the angel watches the processor run", 12),
        ["round 118:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 118: the angel watches the processor run", 16),
        ["round 118: the", "angel watches", "the processor", "run"],
    ),
    (("round 118: the angel watches the processor run", 24), ["round 118: the angel", "watches the processor", "run"]),
    (("round 118: the angel watches the processor run", 32), ["round 118: the angel watches the", "processor run"]),
    (
        ("round 118: angle of the vector decides the match", 4),
        ["round", "118:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 118: angle of the vector decides the match", 8),
        ["round", "118:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 118: angle of the vector decides the match", 12),
        ["round 118:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 118: angle of the vector decides the match", 16),
        ["round 118: angle", "of the vector", "decides the", "match"],
    ),
    (("round 118: angle of the vector decides the match", 24), ["round 118: angle of the", "vector decides the match"]),
    (("round 118: angle of the vector decides the match", 32), ["round 118: angle of the vector", "decides the match"]),
    (
        ("round 118: the candle burns twice as long at night", 4),
        ["round", "118:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 118: the candle burns twice as long at night", 8),
        ["round", "118: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 118: the candle burns twice as long at night", 12),
        ["round 118:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 118: the candle burns twice as long at night", 16),
        ["round 118: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 118: the candle burns twice as long at night", 24),
        ["round 118: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 118: the candle burns twice as long at night", 32),
        ["round 118: the candle burns", "twice as long at night"],
    ),
    (
        ("round 118: a mirror of the universe in one line", 4),
        ["round", "118:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 118: a mirror of the universe in one line", 8),
        ["round", "118: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 118: a mirror of the universe in one line", 12),
        ["round 118: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 118: a mirror of the universe in one line", 16),
        ["round 118: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 118: a mirror of the universe in one line", 24), ["round 118: a mirror of", "the universe in one line"]),
    (("round 118: a mirror of the universe in one line", 32), ["round 118: a mirror of the", "universe in one line"]),
    (
        ("round 118: the queue drains before the storm", 4),
        ["round", "118:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 118: the queue drains before the storm", 8),
        ["round", "118: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 118: the queue drains before the storm", 12),
        ["round 118:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 118: the queue drains before the storm", 16), ["round 118: the", "queue drains", "before the storm"]),
    (("round 118: the queue drains before the storm", 24), ["round 118: the queue", "drains before the storm"]),
    (("round 118: the queue drains before the storm", 32), ["round 118: the queue drains", "before the storm"]),
    (
        ("kitten118 sitting118 agent118 angle118 universe118 memory118", 6),
        ["kitten118", "sitting118", "agent118", "angle118", "universe118", "memory118"],
    ),
    (
        ("kitten118 sitting118 agent118 angle118 universe118 memory118", 10),
        ["kitten118", "sitting118", "agent118", "angle118", "universe118", "memory118"],
    ),
    (
        ("kitten118 sitting118 agent118 angle118 universe118 memory118", 18),
        ["kitten118", "sitting118", "agent118 angle118", "universe118", "memory118"],
    ),
    (
        ("kitten118 sitting118 agent118 angle118 universe118 memory118", 28),
        ["kitten118 sitting118", "agent118 angle118", "universe118 memory118"],
    ),
    (
        ("sitting118 agent118 angle118 universe118 memory118 stream118", 6),
        ["sitting118", "agent118", "angle118", "universe118", "memory118", "stream118"],
    ),
    (
        ("sitting118 agent118 angle118 universe118 memory118 stream118", 10),
        ["sitting118", "agent118", "angle118", "universe118", "memory118", "stream118"],
    ),
    (
        ("sitting118 agent118 angle118 universe118 memory118 stream118", 18),
        ["sitting118", "agent118 angle118", "universe118", "memory118", "stream118"],
    ),
    (
        ("sitting118 agent118 angle118 universe118 memory118 stream118", 28),
        ["sitting118 agent118 angle118", "universe118 memory118", "stream118"],
    ),
    (
        ("agent118 angle118 universe118 memory118 stream118 context118", 6),
        ["agent118", "angle118", "universe118", "memory118", "stream118", "context118"],
    ),
    (
        ("agent118 angle118 universe118 memory118 stream118 context118", 10),
        ["agent118", "angle118", "universe118", "memory118", "stream118", "context118"],
    ),
    (
        ("agent118 angle118 universe118 memory118 stream118 context118", 18),
        ["agent118 angle118", "universe118", "memory118", "stream118", "context118"],
    ),
    (
        ("agent118 angle118 universe118 memory118 stream118 context118", 28),
        ["agent118 angle118", "universe118 memory118", "stream118 context118"],
    ),
    (
        ("angle118 universe118 memory118 stream118 context118 knowledge118", 6),
        ["angle118", "universe118", "memory118", "stream118", "context118", "knowledge118"],
    ),
    (
        ("angle118 universe118 memory118 stream118 context118 knowledge118", 10),
        ["angle118", "universe118", "memory118", "stream118", "context118", "knowledge118"],
    ),
    (
        ("angle118 universe118 memory118 stream118 context118 knowledge118", 18),
        ["angle118", "universe118", "memory118", "stream118", "context118", "knowledge118"],
    ),
    (
        ("angle118 universe118 memory118 stream118 context118 knowledge118", 28),
        ["angle118 universe118", "memory118 stream118", "context118 knowledge118"],
    ),
    (
        ("universe118 memory118 stream118 context118 knowledge118 vector118", 6),
        ["universe118", "memory118", "stream118", "context118", "knowledge118", "vector118"],
    ),
    (
        ("universe118 memory118 stream118 context118 knowledge118 vector118", 10),
        ["universe118", "memory118", "stream118", "context118", "knowledge118", "vector118"],
    ),
    (
        ("universe118 memory118 stream118 context118 knowledge118 vector118", 18),
        ["universe118", "memory118", "stream118", "context118", "knowledge118", "vector118"],
    ),
    (
        ("universe118 memory118 stream118 context118 knowledge118 vector118", 28),
        ["universe118 memory118", "stream118 context118", "knowledge118 vector118"],
    ),
    (
        ("memory118 stream118 context118 knowledge118 vector118 processor118", 6),
        ["memory118", "stream118", "context118", "knowledge118", "vector118", "processor118"],
    ),
    (
        ("memory118 stream118 context118 knowledge118 vector118 processor118", 10),
        ["memory118", "stream118", "context118", "knowledge118", "vector118", "processor118"],
    ),
    (
        ("memory118 stream118 context118 knowledge118 vector118 processor118", 18),
        ["memory118", "stream118", "context118", "knowledge118", "vector118", "processor118"],
    ),
    (
        ("memory118 stream118 context118 knowledge118 vector118 processor118", 28),
        ["memory118 stream118", "context118 knowledge118", "vector118 processor118"],
    ),
    (
        ("stream118 context118 knowledge118 vector118 processor118 reasoning118", 6),
        ["stream118", "context118", "knowledge118", "vector118", "processor118", "reasoning118"],
    ),
    (
        ("stream118 context118 knowledge118 vector118 processor118 reasoning118", 10),
        ["stream118", "context118", "knowledge118", "vector118", "processor118", "reasoning118"],
    ),
    (
        ("stream118 context118 knowledge118 vector118 processor118 reasoning118", 18),
        ["stream118", "context118", "knowledge118", "vector118", "processor118", "reasoning118"],
    ),
    (
        ("stream118 context118 knowledge118 vector118 processor118 reasoning118", 28),
        ["stream118 context118", "knowledge118 vector118", "processor118 reasoning118"],
    ),
    (
        ("context118 knowledge118 vector118 processor118 reasoning118 machine118", 6),
        ["context118", "knowledge118", "vector118", "processor118", "reasoning118", "machine118"],
    ),
    (
        ("context118 knowledge118 vector118 processor118 reasoning118 machine118", 10),
        ["context118", "knowledge118", "vector118", "processor118", "reasoning118", "machine118"],
    ),
    (
        ("context118 knowledge118 vector118 processor118 reasoning118 machine118", 18),
        ["context118", "knowledge118", "vector118", "processor118", "reasoning118", "machine118"],
    ),
    (
        ("context118 knowledge118 vector118 processor118 reasoning118 machine118", 28),
        ["context118 knowledge118", "vector118 processor118", "reasoning118 machine118"],
    ),
    (
        ("knowledge118 vector118 processor118 reasoning118 machine118 learning118", 6),
        ["knowledge118", "vector118", "processor118", "reasoning118", "machine118", "learning118"],
    ),
    (
        ("knowledge118 vector118 processor118 reasoning118 machine118 learning118", 10),
        ["knowledge118", "vector118", "processor118", "reasoning118", "machine118", "learning118"],
    ),
    (
        ("knowledge118 vector118 processor118 reasoning118 machine118 learning118", 18),
        ["knowledge118", "vector118", "processor118", "reasoning118", "machine118", "learning118"],
    ),
    (
        ("knowledge118 vector118 processor118 reasoning118 machine118 learning118", 28),
        ["knowledge118 vector118", "processor118 reasoning118", "machine118 learning118"],
    ),
    (
        ("vector118 processor118 reasoning118 machine118 learning118 model118", 6),
        ["vector118", "processor118", "reasoning118", "machine118", "learning118", "model118"],
    ),
    (
        ("vector118 processor118 reasoning118 machine118 learning118 model118", 10),
        ["vector118", "processor118", "reasoning118", "machine118", "learning118", "model118"],
    ),
    (
        ("vector118 processor118 reasoning118 machine118 learning118 model118", 18),
        ["vector118", "processor118", "reasoning118", "machine118", "learning118", "model118"],
    ),
    (
        ("vector118 processor118 reasoning118 machine118 learning118 model118", 28),
        ["vector118 processor118", "reasoning118 machine118", "learning118 model118"],
    ),
    (
        ("processor118 reasoning118 machine118 learning118 model118 token118", 6),
        ["processor118", "reasoning118", "machine118", "learning118", "model118", "token118"],
    ),
    (
        ("processor118 reasoning118 machine118 learning118 model118 token118", 10),
        ["processor118", "reasoning118", "machine118", "learning118", "model118", "token118"],
    ),
    (
        ("processor118 reasoning118 machine118 learning118 model118 token118", 18),
        ["processor118", "reasoning118", "machine118", "learning118", "model118 token118"],
    ),
    (
        ("processor118 reasoning118 machine118 learning118 model118 token118", 28),
        ["processor118 reasoning118", "machine118 learning118", "model118 token118"],
    ),
    (
        ("reasoning118 machine118 learning118 model118 token118 prompt118", 6),
        ["reasoning118", "machine118", "learning118", "model118", "token118", "prompt118"],
    ),
    (
        ("reasoning118 machine118 learning118 model118 token118 prompt118", 10),
        ["reasoning118", "machine118", "learning118", "model118", "token118", "prompt118"],
    ),
    (
        ("reasoning118 machine118 learning118 model118 token118 prompt118", 18),
        ["reasoning118", "machine118", "learning118", "model118 token118", "prompt118"],
    ),
    (
        ("reasoning118 machine118 learning118 model118 token118 prompt118", 28),
        ["reasoning118 machine118", "learning118 model118", "token118 prompt118"],
    ),
    (
        ("machine118 learning118 model118 token118 prompt118 session118", 6),
        ["machine118", "learning118", "model118", "token118", "prompt118", "session118"],
    ),
    (
        ("machine118 learning118 model118 token118 prompt118 session118", 10),
        ["machine118", "learning118", "model118", "token118", "prompt118", "session118"],
    ),
    (
        ("machine118 learning118 model118 token118 prompt118 session118", 18),
        ["machine118", "learning118", "model118 token118", "prompt118", "session118"],
    ),
    (
        ("machine118 learning118 model118 token118 prompt118 session118", 28),
        ["machine118 learning118", "model118 token118 prompt118", "session118"],
    ),
    (
        ("learning118 model118 token118 prompt118 session118 library118", 6),
        ["learning118", "model118", "token118", "prompt118", "session118", "library118"],
    ),
    (
        ("learning118 model118 token118 prompt118 session118 library118", 10),
        ["learning118", "model118", "token118", "prompt118", "session118", "library118"],
    ),
    (
        ("learning118 model118 token118 prompt118 session118 library118", 18),
        ["learning118", "model118 token118", "prompt118", "session118", "library118"],
    ),
    (
        ("learning118 model118 token118 prompt118 session118 library118", 28),
        ["learning118 model118", "token118 prompt118", "session118 library118"],
    ),
    (
        ("model118 token118 prompt118 session118 library118 service118", 6),
        ["model118", "token118", "prompt118", "session118", "library118", "service118"],
    ),
    (
        ("model118 token118 prompt118 session118 library118 service118", 10),
        ["model118", "token118", "prompt118", "session118", "library118", "service118"],
    ),
    (
        ("model118 token118 prompt118 session118 library118 service118", 18),
        ["model118 token118", "prompt118", "session118", "library118", "service118"],
    ),
    (
        ("model118 token118 prompt118 session118 library118 service118", 28),
        ["model118 token118 prompt118", "session118 library118", "service118"],
    ),
    (
        ("token118 prompt118 session118 library118 service118 gateway118", 6),
        ["token118", "prompt118", "session118", "library118", "service118", "gateway118"],
    ),
    (
        ("token118 prompt118 session118 library118 service118 gateway118", 10),
        ["token118", "prompt118", "session118", "library118", "service118", "gateway118"],
    ),
    (
        ("token118 prompt118 session118 library118 service118 gateway118", 18),
        ["token118 prompt118", "session118", "library118", "service118", "gateway118"],
    ),
    (
        ("token118 prompt118 session118 library118 service118 gateway118", 28),
        ["token118 prompt118", "session118 library118", "service118 gateway118"],
    ),
    (
        ("prompt118 session118 library118 service118 gateway118 storage118", 6),
        ["prompt118", "session118", "library118", "service118", "gateway118", "storage118"],
    ),
    (
        ("prompt118 session118 library118 service118 gateway118 storage118", 10),
        ["prompt118", "session118", "library118", "service118", "gateway118", "storage118"],
    ),
    (
        ("prompt118 session118 library118 service118 gateway118 storage118", 18),
        ["prompt118", "session118", "library118", "service118", "gateway118", "storage118"],
    ),
    (
        ("prompt118 session118 library118 service118 gateway118 storage118", 28),
        ["prompt118 session118", "library118 service118", "gateway118 storage118"],
    ),
    (
        ("session118 library118 service118 gateway118 storage118 network118", 6),
        ["session118", "library118", "service118", "gateway118", "storage118", "network118"],
    ),
    (
        ("session118 library118 service118 gateway118 storage118 network118", 10),
        ["session118", "library118", "service118", "gateway118", "storage118", "network118"],
    ),
    (
        ("session118 library118 service118 gateway118 storage118 network118", 18),
        ["session118", "library118", "service118", "gateway118", "storage118", "network118"],
    ),
    (
        ("session118 library118 service118 gateway118 storage118 network118", 28),
        ["session118 library118", "service118 gateway118", "storage118 network118"],
    ),
    (
        ("library118 service118 gateway118 storage118 network118 latency118", 6),
        ["library118", "service118", "gateway118", "storage118", "network118", "latency118"],
    ),
    (
        ("library118 service118 gateway118 storage118 network118 latency118", 10),
        ["library118", "service118", "gateway118", "storage118", "network118", "latency118"],
    ),
    (
        ("library118 service118 gateway118 storage118 network118 latency118", 18),
        ["library118", "service118", "gateway118", "storage118", "network118", "latency118"],
    ),
    (
        ("library118 service118 gateway118 storage118 network118 latency118", 28),
        ["library118 service118", "gateway118 storage118", "network118 latency118"],
    ),
    (
        ("service118 gateway118 storage118 network118 latency118 buffer118", 6),
        ["service118", "gateway118", "storage118", "network118", "latency118", "buffer118"],
    ),
    (
        ("service118 gateway118 storage118 network118 latency118 buffer118", 10),
        ["service118", "gateway118", "storage118", "network118", "latency118", "buffer118"],
    ),
    (
        ("service118 gateway118 storage118 network118 latency118 buffer118", 18),
        ["service118", "gateway118", "storage118", "network118", "latency118", "buffer118"],
    ),
    (
        ("service118 gateway118 storage118 network118 latency118 buffer118", 28),
        ["service118 gateway118", "storage118 network118", "latency118 buffer118"],
    ),
    (
        ("gateway118 storage118 network118 latency118 buffer118 queue118", 6),
        ["gateway118", "storage118", "network118", "latency118", "buffer118", "queue118"],
    ),
    (
        ("gateway118 storage118 network118 latency118 buffer118 queue118", 10),
        ["gateway118", "storage118", "network118", "latency118", "buffer118", "queue118"],
    ),
    (
        ("gateway118 storage118 network118 latency118 buffer118 queue118", 18),
        ["gateway118", "storage118", "network118", "latency118", "buffer118 queue118"],
    ),
    (
        ("gateway118 storage118 network118 latency118 buffer118 queue118", 28),
        ["gateway118 storage118", "network118 latency118", "buffer118 queue118"],
    ),
    (
        ("storage118 network118 latency118 buffer118 queue118 worker118", 6),
        ["storage118", "network118", "latency118", "buffer118", "queue118", "worker118"],
    ),
    (
        ("storage118 network118 latency118 buffer118 queue118 worker118", 10),
        ["storage118", "network118", "latency118", "buffer118", "queue118", "worker118"],
    ),
    (
        ("storage118 network118 latency118 buffer118 queue118 worker118", 18),
        ["storage118", "network118", "latency118", "buffer118 queue118", "worker118"],
    ),
    (
        ("storage118 network118 latency118 buffer118 queue118 worker118", 28),
        ["storage118 network118", "latency118 buffer118", "queue118 worker118"],
    ),
    (
        ("network118 latency118 buffer118 queue118 worker118 kernel118", 6),
        ["network118", "latency118", "buffer118", "queue118", "worker118", "kernel118"],
    ),
    (
        ("network118 latency118 buffer118 queue118 worker118 kernel118", 10),
        ["network118", "latency118", "buffer118", "queue118", "worker118", "kernel118"],
    ),
    (
        ("network118 latency118 buffer118 queue118 worker118 kernel118", 18),
        ["network118", "latency118", "buffer118 queue118", "worker118", "kernel118"],
    ),
    (
        ("network118 latency118 buffer118 queue118 worker118 kernel118", 28),
        ["network118 latency118", "buffer118 queue118 worker118", "kernel118"],
    ),
    (
        ("latency118 buffer118 queue118 worker118 kernel118 signal118", 6),
        ["latency118", "buffer118", "queue118", "worker118", "kernel118", "signal118"],
    ),
    (
        ("latency118 buffer118 queue118 worker118 kernel118 signal118", 10),
        ["latency118", "buffer118", "queue118", "worker118", "kernel118", "signal118"],
    ),
    (
        ("latency118 buffer118 queue118 worker118 kernel118 signal118", 18),
        ["latency118", "buffer118 queue118", "worker118", "kernel118", "signal118"],
    ),
    (
        ("latency118 buffer118 queue118 worker118 kernel118 signal118", 28),
        ["latency118 buffer118", "queue118 worker118 kernel118", "signal118"],
    ),
    (
        ("buffer118 queue118 worker118 kernel118 signal118 packet118", 6),
        ["buffer118", "queue118", "worker118", "kernel118", "signal118", "packet118"],
    ),
    (
        ("buffer118 queue118 worker118 kernel118 signal118 packet118", 10),
        ["buffer118", "queue118", "worker118", "kernel118", "signal118", "packet118"],
    ),
    (
        ("buffer118 queue118 worker118 kernel118 signal118 packet118", 18),
        ["buffer118 queue118", "worker118", "kernel118", "signal118", "packet118"],
    ),
    (
        ("buffer118 queue118 worker118 kernel118 signal118 packet118", 28),
        ["buffer118 queue118 worker118", "kernel118 signal118", "packet118"],
    ),
    (
        ("queue118 worker118 kernel118 signal118 packet118 router118", 6),
        ["queue118", "worker118", "kernel118", "signal118", "packet118", "router118"],
    ),
    (
        ("queue118 worker118 kernel118 signal118 packet118 router118", 10),
        ["queue118", "worker118", "kernel118", "signal118", "packet118", "router118"],
    ),
    (
        ("queue118 worker118 kernel118 signal118 packet118 router118", 18),
        ["queue118 worker118", "kernel118", "signal118", "packet118", "router118"],
    ),
    (
        ("queue118 worker118 kernel118 signal118 packet118 router118", 28),
        ["queue118 worker118 kernel118", "signal118 packet118", "router118"],
    ),
    (
        ("worker118 kernel118 signal118 packet118 router118 cluster118", 6),
        ["worker118", "kernel118", "signal118", "packet118", "router118", "cluster118"],
    ),
    (
        ("worker118 kernel118 signal118 packet118 router118 cluster118", 10),
        ["worker118", "kernel118", "signal118", "packet118", "router118", "cluster118"],
    ),
    (
        ("worker118 kernel118 signal118 packet118 router118 cluster118", 18),
        ["worker118", "kernel118", "signal118", "packet118", "router118", "cluster118"],
    ),
    (
        ("worker118 kernel118 signal118 packet118 router118 cluster118", 28),
        ["worker118 kernel118", "signal118 packet118", "router118 cluster118"],
    ),
    (
        ("kernel118 signal118 packet118 router118 cluster118 mirror118", 6),
        ["kernel118", "signal118", "packet118", "router118", "cluster118", "mirror118"],
    ),
    (
        ("kernel118 signal118 packet118 router118 cluster118 mirror118", 10),
        ["kernel118", "signal118", "packet118", "router118", "cluster118", "mirror118"],
    ),
    (
        ("kernel118 signal118 packet118 router118 cluster118 mirror118", 18),
        ["kernel118", "signal118", "packet118", "router118", "cluster118", "mirror118"],
    ),
    (
        ("kernel118 signal118 packet118 router118 cluster118 mirror118", 28),
        ["kernel118 signal118", "packet118 router118", "cluster118 mirror118"],
    ),
    (
        ("signal118 packet118 router118 cluster118 mirror118 filter118", 6),
        ["signal118", "packet118", "router118", "cluster118", "mirror118", "filter118"],
    ),
    (
        ("signal118 packet118 router118 cluster118 mirror118 filter118", 10),
        ["signal118", "packet118", "router118", "cluster118", "mirror118", "filter118"],
    ),
    (
        ("signal118 packet118 router118 cluster118 mirror118 filter118", 18),
        ["signal118", "packet118", "router118", "cluster118", "mirror118", "filter118"],
    ),
    (
        ("signal118 packet118 router118 cluster118 mirror118 filter118", 28),
        ["signal118 packet118", "router118 cluster118", "mirror118 filter118"],
    ),
    (
        ("packet118 router118 cluster118 mirror118 filter118 ranking118", 6),
        ["packet118", "router118", "cluster118", "mirror118", "filter118", "ranking118"],
    ),
    (
        ("packet118 router118 cluster118 mirror118 filter118 ranking118", 10),
        ["packet118", "router118", "cluster118", "mirror118", "filter118", "ranking118"],
    ),
    (
        ("packet118 router118 cluster118 mirror118 filter118 ranking118", 18),
        ["packet118", "router118", "cluster118", "mirror118", "filter118", "ranking118"],
    ),
    (
        ("packet118 router118 cluster118 mirror118 filter118 ranking118", 28),
        ["packet118 router118", "cluster118 mirror118", "filter118 ranking118"],
    ),
    (
        ("router118 cluster118 mirror118 filter118 ranking118 encoding118", 6),
        ["router118", "cluster118", "mirror118", "filter118", "ranking118", "encoding118"],
    ),
    (
        ("router118 cluster118 mirror118 filter118 ranking118 encoding118", 10),
        ["router118", "cluster118", "mirror118", "filter118", "ranking118", "encoding118"],
    ),
    (
        ("router118 cluster118 mirror118 filter118 ranking118 encoding118", 18),
        ["router118", "cluster118", "mirror118", "filter118", "ranking118", "encoding118"],
    ),
    (
        ("router118 cluster118 mirror118 filter118 ranking118 encoding118", 28),
        ["router118 cluster118", "mirror118 filter118", "ranking118 encoding118"],
    ),
    (
        ("cluster118 mirror118 filter118 ranking118 encoding118 mapping118", 6),
        ["cluster118", "mirror118", "filter118", "ranking118", "encoding118", "mapping118"],
    ),
    (
        ("cluster118 mirror118 filter118 ranking118 encoding118 mapping118", 10),
        ["cluster118", "mirror118", "filter118", "ranking118", "encoding118", "mapping118"],
    ),
    (
        ("cluster118 mirror118 filter118 ranking118 encoding118 mapping118", 18),
        ["cluster118", "mirror118", "filter118", "ranking118", "encoding118", "mapping118"],
    ),
    (
        ("cluster118 mirror118 filter118 ranking118 encoding118 mapping118", 28),
        ["cluster118 mirror118", "filter118 ranking118", "encoding118 mapping118"],
    ),
    (
        ("mirror118 filter118 ranking118 encoding118 mapping118 record118", 6),
        ["mirror118", "filter118", "ranking118", "encoding118", "mapping118", "record118"],
    ),
    (
        ("mirror118 filter118 ranking118 encoding118 mapping118 record118", 10),
        ["mirror118", "filter118", "ranking118", "encoding118", "mapping118", "record118"],
    ),
    (
        ("mirror118 filter118 ranking118 encoding118 mapping118 record118", 18),
        ["mirror118", "filter118", "ranking118", "encoding118", "mapping118", "record118"],
    ),
    (
        ("mirror118 filter118 ranking118 encoding118 mapping118 record118", 28),
        ["mirror118 filter118", "ranking118 encoding118", "mapping118 record118"],
    ),
    (
        ("filter118 ranking118 encoding118 mapping118 record118 candle118", 6),
        ["filter118", "ranking118", "encoding118", "mapping118", "record118", "candle118"],
    ),
    (
        ("filter118 ranking118 encoding118 mapping118 record118 candle118", 10),
        ["filter118", "ranking118", "encoding118", "mapping118", "record118", "candle118"],
    ),
    (
        ("filter118 ranking118 encoding118 mapping118 record118 candle118", 18),
        ["filter118", "ranking118", "encoding118", "mapping118", "record118", "candle118"],
    ),
    (
        ("filter118 ranking118 encoding118 mapping118 record118 candle118", 28),
        ["filter118 ranking118", "encoding118 mapping118", "record118 candle118"],
    ),
    (
        ("ranking118 encoding118 mapping118 record118 candle118 thread118", 6),
        ["ranking118", "encoding118", "mapping118", "record118", "candle118", "thread118"],
    ),
    (
        ("ranking118 encoding118 mapping118 record118 candle118 thread118", 10),
        ["ranking118", "encoding118", "mapping118", "record118", "candle118", "thread118"],
    ),
    (
        ("ranking118 encoding118 mapping118 record118 candle118 thread118", 18),
        ["ranking118", "encoding118", "mapping118", "record118", "candle118", "thread118"],
    ),
    (
        ("ranking118 encoding118 mapping118 record118 candle118 thread118", 28),
        ["ranking118 encoding118", "mapping118 record118", "candle118 thread118"],
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
