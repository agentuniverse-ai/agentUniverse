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
        ("round 196: the quick brown fox jumps over the lazy dog", 4),
        ["round", "196:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 196: the quick brown fox jumps over the lazy dog", 8),
        ["round", "196: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 196: the quick brown fox jumps over the lazy dog", 12),
        ["round 196:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 196: the quick brown fox jumps over the lazy dog", 16),
        ["round 196: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 196: the quick brown fox jumps over the lazy dog", 24),
        ["round 196: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 196: the quick brown fox jumps over the lazy dog", 32),
        ["round 196: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 196: agentuniverse is a framework for multi agents", 4),
        ["round", "196:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 196: agentuniverse is a framework for multi agents", 8),
        ["round", "196:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 196: agentuniverse is a framework for multi agents", 12),
        ["round 196:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 196: agentuniverse is a framework for multi agents", 16),
        ["round 196:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 196: agentuniverse is a framework for multi agents", 24),
        ["round 196: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 196: agentuniverse is a framework for multi agents", 32),
        ["round 196: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 196: knowledge stored as vectors enables retrieval", 4),
        ["round", "196:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 196: knowledge stored as vectors enables retrieval", 8),
        ["round", "196:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 196: knowledge stored as vectors enables retrieval", 12),
        ["round 196:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 196: knowledge stored as vectors enables retrieval", 16),
        ["round 196:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 196: knowledge stored as vectors enables retrieval", 24),
        ["round 196: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 196: knowledge stored as vectors enables retrieval", 32),
        ["round 196: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 196: the processor reads the record then stops", 4),
        ["round", "196:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 196: the processor reads the record then stops", 8),
        ["round", "196: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 196: the processor reads the record then stops", 12),
        ["round 196:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 196: the processor reads the record then stops", 16),
        ["round 196: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 196: the processor reads the record then stops", 24),
        ["round 196: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 196: the processor reads the record then stops", 32),
        ["round 196: the processor reads", "the record then stops"],
    ),
    (
        ("round 196: a worker pulls the next task from the queue", 4),
        ["round", "196:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 196: a worker pulls the next task from the queue", 8),
        ["round", "196: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 196: a worker pulls the next task from the queue", 12),
        ["round 196: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 196: a worker pulls the next task from the queue", 16),
        ["round 196: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 196: a worker pulls the next task from the queue", 24),
        ["round 196: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 196: a worker pulls the next task from the queue", 32),
        ["round 196: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 196: signals travel through the network layer", 4),
        ["round", "196:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 196: signals travel through the network layer", 8),
        ["round", "196:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 196: signals travel through the network layer", 12),
        ["round 196:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 196: signals travel through the network layer", 16),
        ["round 196:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 196: signals travel through the network layer", 24),
        ["round 196: signals", "travel through the", "network layer"],
    ),
    (
        ("round 196: signals travel through the network layer", 32),
        ["round 196: signals travel", "through the network layer"],
    ),
    (
        ("round 196: the gateway routes each request by policy", 4),
        ["round", "196:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 196: the gateway routes each request by policy", 8),
        ["round", "196: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 196: the gateway routes each request by policy", 12),
        ["round 196:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 196: the gateway routes each request by policy", 16),
        ["round 196: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 196: the gateway routes each request by policy", 24),
        ["round 196: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 196: the gateway routes each request by policy", 32),
        ["round 196: the gateway routes", "each request by policy"],
    ),
    (
        ("round 196: memory grows until the buffer is full", 4),
        ["round", "196:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 196: memory grows until the buffer is full", 8),
        ["round", "196:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 196: memory grows until the buffer is full", 12),
        ["round 196:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 196: memory grows until the buffer is full", 16),
        ["round 196:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 196: memory grows until the buffer is full", 24), ["round 196: memory grows", "until the buffer is full"]),
    (("round 196: memory grows until the buffer is full", 32), ["round 196: memory grows until", "the buffer is full"]),
    (
        ("round 196: the cluster mirrors every packet twice", 4),
        ["round", "196:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 196: the cluster mirrors every packet twice", 8),
        ["round", "196: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 196: the cluster mirrors every packet twice", 12),
        ["round 196:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 196: the cluster mirrors every packet twice", 16),
        ["round 196: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 196: the cluster mirrors every packet twice", 24),
        ["round 196: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 196: the cluster mirrors every packet twice", 32),
        ["round 196: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 196: ranking uses tokens learned from the corpus", 4),
        ["round", "196:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 196: ranking uses tokens learned from the corpus", 8),
        ["round", "196:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 196: ranking uses tokens learned from the corpus", 12),
        ["round 196:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 196: ranking uses tokens learned from the corpus", 16),
        ["round 196:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 196: ranking uses tokens learned from the corpus", 24),
        ["round 196: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 196: ranking uses tokens learned from the corpus", 32),
        ["round 196: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 196: a long session ends when the candle dies", 4),
        ["round", "196:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 196: a long session ends when the candle dies", 8),
        ["round", "196: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 196: a long session ends when the candle dies", 12),
        ["round 196: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 196: a long session ends when the candle dies", 16),
        ["round 196: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 196: a long session ends when the candle dies", 24),
        ["round 196: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 196: a long session ends when the candle dies", 32),
        ["round 196: a long session ends", "when the candle dies"],
    ),
    (
        ("round 196: encode the prompt then map the result", 4),
        ["round", "196:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 196: encode the prompt then map the result", 8),
        ["round", "196:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 196: encode the prompt then map the result", 12),
        ["round 196:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 196: encode the prompt then map the result", 16),
        ["round 196:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 196: encode the prompt then map the result", 24),
        ["round 196: encode the", "prompt then map the", "result"],
    ),
    (("round 196: encode the prompt then map the result", 32), ["round 196: encode the prompt", "then map the result"]),
    (
        ("round 196: the kernel wakes the worker at dawn", 4),
        ["round", "196:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 196: the kernel wakes the worker at dawn", 8),
        ["round", "196: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 196: the kernel wakes the worker at dawn", 12),
        ["round 196:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 196: the kernel wakes the worker at dawn", 16), ["round 196: the", "kernel wakes the", "worker at dawn"]),
    (("round 196: the kernel wakes the worker at dawn", 24), ["round 196: the kernel", "wakes the worker at dawn"]),
    (("round 196: the kernel wakes the worker at dawn", 32), ["round 196: the kernel wakes the", "worker at dawn"]),
    (
        ("round 196: service latency drops after the patch", 4),
        ["round", "196:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 196: service latency drops after the patch", 8),
        ["round", "196:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 196: service latency drops after the patch", 12),
        ["round 196:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 196: service latency drops after the patch", 16),
        ["round 196:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 196: service latency drops after the patch", 24),
        ["round 196: service", "latency drops after the", "patch"],
    ),
    (("round 196: service latency drops after the patch", 32), ["round 196: service latency drops", "after the patch"]),
    (
        ("round 196: the library caches every vector it sees", 4),
        ["round", "196:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 196: the library caches every vector it sees", 8),
        ["round", "196: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 196: the library caches every vector it sees", 12),
        ["round 196:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 196: the library caches every vector it sees", 16),
        ["round 196: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 196: the library caches every vector it sees", 24),
        ["round 196: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 196: the library caches every vector it sees", 32),
        ["round 196: the library caches", "every vector it sees"],
    ),
    (
        ("round 196: agents argue then the debate resolves", 4),
        ["round", "196:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 196: agents argue then the debate resolves", 8),
        ["round", "196:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 196: agents argue then the debate resolves", 12),
        ["round 196:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 196: agents argue then the debate resolves", 16),
        ["round 196:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 196: agents argue then the debate resolves", 24), ["round 196: agents argue", "then the debate resolves"]),
    (("round 196: agents argue then the debate resolves", 32), ["round 196: agents argue then the", "debate resolves"]),
    (
        ("round 196: the filter keeps only strong matches", 4),
        ["round", "196:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 196: the filter keeps only strong matches", 8),
        ["round", "196: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 196: the filter keeps only strong matches", 12),
        ["round 196:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 196: the filter keeps only strong matches", 16),
        ["round 196: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 196: the filter keeps only strong matches", 24),
        ["round 196: the filter", "keeps only strong", "matches"],
    ),
    (("round 196: the filter keeps only strong matches", 32), ["round 196: the filter keeps only", "strong matches"]),
    (
        ("round 196: the model answers with a short reply", 4),
        ["round", "196:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 196: the model answers with a short reply", 8),
        ["round", "196: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 196: the model answers with a short reply", 12),
        ["round 196:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 196: the model answers with a short reply", 16),
        ["round 196: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 196: the model answers with a short reply", 24),
        ["round 196: the model", "answers with a short", "reply"],
    ),
    (("round 196: the model answers with a short reply", 32), ["round 196: the model answers", "with a short reply"]),
    (
        ("round 196: the recorder stores the reasoning trace", 4),
        ["round", "196:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 196: the recorder stores the reasoning trace", 8),
        ["round", "196: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 196: the recorder stores the reasoning trace", 12),
        ["round 196:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 196: the recorder stores the reasoning trace", 16),
        ["round 196: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 196: the recorder stores the reasoning trace", 24),
        ["round 196: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 196: the recorder stores the reasoning trace", 32),
        ["round 196: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 196: the angel watches the processor run", 4),
        ["round", "196:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 196: the angel watches the processor run", 8),
        ["round", "196: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 196: the angel watches the processor run", 12),
        ["round 196:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 196: the angel watches the processor run", 16),
        ["round 196: the", "angel watches", "the processor", "run"],
    ),
    (("round 196: the angel watches the processor run", 24), ["round 196: the angel", "watches the processor", "run"]),
    (("round 196: the angel watches the processor run", 32), ["round 196: the angel watches the", "processor run"]),
    (
        ("round 196: angle of the vector decides the match", 4),
        ["round", "196:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 196: angle of the vector decides the match", 8),
        ["round", "196:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 196: angle of the vector decides the match", 12),
        ["round 196:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 196: angle of the vector decides the match", 16),
        ["round 196: angle", "of the vector", "decides the", "match"],
    ),
    (("round 196: angle of the vector decides the match", 24), ["round 196: angle of the", "vector decides the match"]),
    (("round 196: angle of the vector decides the match", 32), ["round 196: angle of the vector", "decides the match"]),
    (
        ("round 196: the candle burns twice as long at night", 4),
        ["round", "196:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 196: the candle burns twice as long at night", 8),
        ["round", "196: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 196: the candle burns twice as long at night", 12),
        ["round 196:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 196: the candle burns twice as long at night", 16),
        ["round 196: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 196: the candle burns twice as long at night", 24),
        ["round 196: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 196: the candle burns twice as long at night", 32),
        ["round 196: the candle burns", "twice as long at night"],
    ),
    (
        ("round 196: a mirror of the universe in one line", 4),
        ["round", "196:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 196: a mirror of the universe in one line", 8),
        ["round", "196: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 196: a mirror of the universe in one line", 12),
        ["round 196: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 196: a mirror of the universe in one line", 16),
        ["round 196: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 196: a mirror of the universe in one line", 24), ["round 196: a mirror of", "the universe in one line"]),
    (("round 196: a mirror of the universe in one line", 32), ["round 196: a mirror of the", "universe in one line"]),
    (
        ("round 196: the queue drains before the storm", 4),
        ["round", "196:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 196: the queue drains before the storm", 8),
        ["round", "196: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 196: the queue drains before the storm", 12),
        ["round 196:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 196: the queue drains before the storm", 16), ["round 196: the", "queue drains", "before the storm"]),
    (("round 196: the queue drains before the storm", 24), ["round 196: the queue", "drains before the storm"]),
    (("round 196: the queue drains before the storm", 32), ["round 196: the queue drains", "before the storm"]),
    (
        ("kitten196 sitting196 agent196 angle196 universe196 memory196", 6),
        ["kitten196", "sitting196", "agent196", "angle196", "universe196", "memory196"],
    ),
    (
        ("kitten196 sitting196 agent196 angle196 universe196 memory196", 10),
        ["kitten196", "sitting196", "agent196", "angle196", "universe196", "memory196"],
    ),
    (
        ("kitten196 sitting196 agent196 angle196 universe196 memory196", 18),
        ["kitten196", "sitting196", "agent196 angle196", "universe196", "memory196"],
    ),
    (
        ("kitten196 sitting196 agent196 angle196 universe196 memory196", 28),
        ["kitten196 sitting196", "agent196 angle196", "universe196 memory196"],
    ),
    (
        ("sitting196 agent196 angle196 universe196 memory196 stream196", 6),
        ["sitting196", "agent196", "angle196", "universe196", "memory196", "stream196"],
    ),
    (
        ("sitting196 agent196 angle196 universe196 memory196 stream196", 10),
        ["sitting196", "agent196", "angle196", "universe196", "memory196", "stream196"],
    ),
    (
        ("sitting196 agent196 angle196 universe196 memory196 stream196", 18),
        ["sitting196", "agent196 angle196", "universe196", "memory196", "stream196"],
    ),
    (
        ("sitting196 agent196 angle196 universe196 memory196 stream196", 28),
        ["sitting196 agent196 angle196", "universe196 memory196", "stream196"],
    ),
    (
        ("agent196 angle196 universe196 memory196 stream196 context196", 6),
        ["agent196", "angle196", "universe196", "memory196", "stream196", "context196"],
    ),
    (
        ("agent196 angle196 universe196 memory196 stream196 context196", 10),
        ["agent196", "angle196", "universe196", "memory196", "stream196", "context196"],
    ),
    (
        ("agent196 angle196 universe196 memory196 stream196 context196", 18),
        ["agent196 angle196", "universe196", "memory196", "stream196", "context196"],
    ),
    (
        ("agent196 angle196 universe196 memory196 stream196 context196", 28),
        ["agent196 angle196", "universe196 memory196", "stream196 context196"],
    ),
    (
        ("angle196 universe196 memory196 stream196 context196 knowledge196", 6),
        ["angle196", "universe196", "memory196", "stream196", "context196", "knowledge196"],
    ),
    (
        ("angle196 universe196 memory196 stream196 context196 knowledge196", 10),
        ["angle196", "universe196", "memory196", "stream196", "context196", "knowledge196"],
    ),
    (
        ("angle196 universe196 memory196 stream196 context196 knowledge196", 18),
        ["angle196", "universe196", "memory196", "stream196", "context196", "knowledge196"],
    ),
    (
        ("angle196 universe196 memory196 stream196 context196 knowledge196", 28),
        ["angle196 universe196", "memory196 stream196", "context196 knowledge196"],
    ),
    (
        ("universe196 memory196 stream196 context196 knowledge196 vector196", 6),
        ["universe196", "memory196", "stream196", "context196", "knowledge196", "vector196"],
    ),
    (
        ("universe196 memory196 stream196 context196 knowledge196 vector196", 10),
        ["universe196", "memory196", "stream196", "context196", "knowledge196", "vector196"],
    ),
    (
        ("universe196 memory196 stream196 context196 knowledge196 vector196", 18),
        ["universe196", "memory196", "stream196", "context196", "knowledge196", "vector196"],
    ),
    (
        ("universe196 memory196 stream196 context196 knowledge196 vector196", 28),
        ["universe196 memory196", "stream196 context196", "knowledge196 vector196"],
    ),
    (
        ("memory196 stream196 context196 knowledge196 vector196 processor196", 6),
        ["memory196", "stream196", "context196", "knowledge196", "vector196", "processor196"],
    ),
    (
        ("memory196 stream196 context196 knowledge196 vector196 processor196", 10),
        ["memory196", "stream196", "context196", "knowledge196", "vector196", "processor196"],
    ),
    (
        ("memory196 stream196 context196 knowledge196 vector196 processor196", 18),
        ["memory196", "stream196", "context196", "knowledge196", "vector196", "processor196"],
    ),
    (
        ("memory196 stream196 context196 knowledge196 vector196 processor196", 28),
        ["memory196 stream196", "context196 knowledge196", "vector196 processor196"],
    ),
    (
        ("stream196 context196 knowledge196 vector196 processor196 reasoning196", 6),
        ["stream196", "context196", "knowledge196", "vector196", "processor196", "reasoning196"],
    ),
    (
        ("stream196 context196 knowledge196 vector196 processor196 reasoning196", 10),
        ["stream196", "context196", "knowledge196", "vector196", "processor196", "reasoning196"],
    ),
    (
        ("stream196 context196 knowledge196 vector196 processor196 reasoning196", 18),
        ["stream196", "context196", "knowledge196", "vector196", "processor196", "reasoning196"],
    ),
    (
        ("stream196 context196 knowledge196 vector196 processor196 reasoning196", 28),
        ["stream196 context196", "knowledge196 vector196", "processor196 reasoning196"],
    ),
    (
        ("context196 knowledge196 vector196 processor196 reasoning196 machine196", 6),
        ["context196", "knowledge196", "vector196", "processor196", "reasoning196", "machine196"],
    ),
    (
        ("context196 knowledge196 vector196 processor196 reasoning196 machine196", 10),
        ["context196", "knowledge196", "vector196", "processor196", "reasoning196", "machine196"],
    ),
    (
        ("context196 knowledge196 vector196 processor196 reasoning196 machine196", 18),
        ["context196", "knowledge196", "vector196", "processor196", "reasoning196", "machine196"],
    ),
    (
        ("context196 knowledge196 vector196 processor196 reasoning196 machine196", 28),
        ["context196 knowledge196", "vector196 processor196", "reasoning196 machine196"],
    ),
    (
        ("knowledge196 vector196 processor196 reasoning196 machine196 learning196", 6),
        ["knowledge196", "vector196", "processor196", "reasoning196", "machine196", "learning196"],
    ),
    (
        ("knowledge196 vector196 processor196 reasoning196 machine196 learning196", 10),
        ["knowledge196", "vector196", "processor196", "reasoning196", "machine196", "learning196"],
    ),
    (
        ("knowledge196 vector196 processor196 reasoning196 machine196 learning196", 18),
        ["knowledge196", "vector196", "processor196", "reasoning196", "machine196", "learning196"],
    ),
    (
        ("knowledge196 vector196 processor196 reasoning196 machine196 learning196", 28),
        ["knowledge196 vector196", "processor196 reasoning196", "machine196 learning196"],
    ),
    (
        ("vector196 processor196 reasoning196 machine196 learning196 model196", 6),
        ["vector196", "processor196", "reasoning196", "machine196", "learning196", "model196"],
    ),
    (
        ("vector196 processor196 reasoning196 machine196 learning196 model196", 10),
        ["vector196", "processor196", "reasoning196", "machine196", "learning196", "model196"],
    ),
    (
        ("vector196 processor196 reasoning196 machine196 learning196 model196", 18),
        ["vector196", "processor196", "reasoning196", "machine196", "learning196", "model196"],
    ),
    (
        ("vector196 processor196 reasoning196 machine196 learning196 model196", 28),
        ["vector196 processor196", "reasoning196 machine196", "learning196 model196"],
    ),
    (
        ("processor196 reasoning196 machine196 learning196 model196 token196", 6),
        ["processor196", "reasoning196", "machine196", "learning196", "model196", "token196"],
    ),
    (
        ("processor196 reasoning196 machine196 learning196 model196 token196", 10),
        ["processor196", "reasoning196", "machine196", "learning196", "model196", "token196"],
    ),
    (
        ("processor196 reasoning196 machine196 learning196 model196 token196", 18),
        ["processor196", "reasoning196", "machine196", "learning196", "model196 token196"],
    ),
    (
        ("processor196 reasoning196 machine196 learning196 model196 token196", 28),
        ["processor196 reasoning196", "machine196 learning196", "model196 token196"],
    ),
    (
        ("reasoning196 machine196 learning196 model196 token196 prompt196", 6),
        ["reasoning196", "machine196", "learning196", "model196", "token196", "prompt196"],
    ),
    (
        ("reasoning196 machine196 learning196 model196 token196 prompt196", 10),
        ["reasoning196", "machine196", "learning196", "model196", "token196", "prompt196"],
    ),
    (
        ("reasoning196 machine196 learning196 model196 token196 prompt196", 18),
        ["reasoning196", "machine196", "learning196", "model196 token196", "prompt196"],
    ),
    (
        ("reasoning196 machine196 learning196 model196 token196 prompt196", 28),
        ["reasoning196 machine196", "learning196 model196", "token196 prompt196"],
    ),
    (
        ("machine196 learning196 model196 token196 prompt196 session196", 6),
        ["machine196", "learning196", "model196", "token196", "prompt196", "session196"],
    ),
    (
        ("machine196 learning196 model196 token196 prompt196 session196", 10),
        ["machine196", "learning196", "model196", "token196", "prompt196", "session196"],
    ),
    (
        ("machine196 learning196 model196 token196 prompt196 session196", 18),
        ["machine196", "learning196", "model196 token196", "prompt196", "session196"],
    ),
    (
        ("machine196 learning196 model196 token196 prompt196 session196", 28),
        ["machine196 learning196", "model196 token196 prompt196", "session196"],
    ),
    (
        ("learning196 model196 token196 prompt196 session196 library196", 6),
        ["learning196", "model196", "token196", "prompt196", "session196", "library196"],
    ),
    (
        ("learning196 model196 token196 prompt196 session196 library196", 10),
        ["learning196", "model196", "token196", "prompt196", "session196", "library196"],
    ),
    (
        ("learning196 model196 token196 prompt196 session196 library196", 18),
        ["learning196", "model196 token196", "prompt196", "session196", "library196"],
    ),
    (
        ("learning196 model196 token196 prompt196 session196 library196", 28),
        ["learning196 model196", "token196 prompt196", "session196 library196"],
    ),
    (
        ("model196 token196 prompt196 session196 library196 service196", 6),
        ["model196", "token196", "prompt196", "session196", "library196", "service196"],
    ),
    (
        ("model196 token196 prompt196 session196 library196 service196", 10),
        ["model196", "token196", "prompt196", "session196", "library196", "service196"],
    ),
    (
        ("model196 token196 prompt196 session196 library196 service196", 18),
        ["model196 token196", "prompt196", "session196", "library196", "service196"],
    ),
    (
        ("model196 token196 prompt196 session196 library196 service196", 28),
        ["model196 token196 prompt196", "session196 library196", "service196"],
    ),
    (
        ("token196 prompt196 session196 library196 service196 gateway196", 6),
        ["token196", "prompt196", "session196", "library196", "service196", "gateway196"],
    ),
    (
        ("token196 prompt196 session196 library196 service196 gateway196", 10),
        ["token196", "prompt196", "session196", "library196", "service196", "gateway196"],
    ),
    (
        ("token196 prompt196 session196 library196 service196 gateway196", 18),
        ["token196 prompt196", "session196", "library196", "service196", "gateway196"],
    ),
    (
        ("token196 prompt196 session196 library196 service196 gateway196", 28),
        ["token196 prompt196", "session196 library196", "service196 gateway196"],
    ),
    (
        ("prompt196 session196 library196 service196 gateway196 storage196", 6),
        ["prompt196", "session196", "library196", "service196", "gateway196", "storage196"],
    ),
    (
        ("prompt196 session196 library196 service196 gateway196 storage196", 10),
        ["prompt196", "session196", "library196", "service196", "gateway196", "storage196"],
    ),
    (
        ("prompt196 session196 library196 service196 gateway196 storage196", 18),
        ["prompt196", "session196", "library196", "service196", "gateway196", "storage196"],
    ),
    (
        ("prompt196 session196 library196 service196 gateway196 storage196", 28),
        ["prompt196 session196", "library196 service196", "gateway196 storage196"],
    ),
    (
        ("session196 library196 service196 gateway196 storage196 network196", 6),
        ["session196", "library196", "service196", "gateway196", "storage196", "network196"],
    ),
    (
        ("session196 library196 service196 gateway196 storage196 network196", 10),
        ["session196", "library196", "service196", "gateway196", "storage196", "network196"],
    ),
    (
        ("session196 library196 service196 gateway196 storage196 network196", 18),
        ["session196", "library196", "service196", "gateway196", "storage196", "network196"],
    ),
    (
        ("session196 library196 service196 gateway196 storage196 network196", 28),
        ["session196 library196", "service196 gateway196", "storage196 network196"],
    ),
    (
        ("library196 service196 gateway196 storage196 network196 latency196", 6),
        ["library196", "service196", "gateway196", "storage196", "network196", "latency196"],
    ),
    (
        ("library196 service196 gateway196 storage196 network196 latency196", 10),
        ["library196", "service196", "gateway196", "storage196", "network196", "latency196"],
    ),
    (
        ("library196 service196 gateway196 storage196 network196 latency196", 18),
        ["library196", "service196", "gateway196", "storage196", "network196", "latency196"],
    ),
    (
        ("library196 service196 gateway196 storage196 network196 latency196", 28),
        ["library196 service196", "gateway196 storage196", "network196 latency196"],
    ),
    (
        ("service196 gateway196 storage196 network196 latency196 buffer196", 6),
        ["service196", "gateway196", "storage196", "network196", "latency196", "buffer196"],
    ),
    (
        ("service196 gateway196 storage196 network196 latency196 buffer196", 10),
        ["service196", "gateway196", "storage196", "network196", "latency196", "buffer196"],
    ),
    (
        ("service196 gateway196 storage196 network196 latency196 buffer196", 18),
        ["service196", "gateway196", "storage196", "network196", "latency196", "buffer196"],
    ),
    (
        ("service196 gateway196 storage196 network196 latency196 buffer196", 28),
        ["service196 gateway196", "storage196 network196", "latency196 buffer196"],
    ),
    (
        ("gateway196 storage196 network196 latency196 buffer196 queue196", 6),
        ["gateway196", "storage196", "network196", "latency196", "buffer196", "queue196"],
    ),
    (
        ("gateway196 storage196 network196 latency196 buffer196 queue196", 10),
        ["gateway196", "storage196", "network196", "latency196", "buffer196", "queue196"],
    ),
    (
        ("gateway196 storage196 network196 latency196 buffer196 queue196", 18),
        ["gateway196", "storage196", "network196", "latency196", "buffer196 queue196"],
    ),
    (
        ("gateway196 storage196 network196 latency196 buffer196 queue196", 28),
        ["gateway196 storage196", "network196 latency196", "buffer196 queue196"],
    ),
    (
        ("storage196 network196 latency196 buffer196 queue196 worker196", 6),
        ["storage196", "network196", "latency196", "buffer196", "queue196", "worker196"],
    ),
    (
        ("storage196 network196 latency196 buffer196 queue196 worker196", 10),
        ["storage196", "network196", "latency196", "buffer196", "queue196", "worker196"],
    ),
    (
        ("storage196 network196 latency196 buffer196 queue196 worker196", 18),
        ["storage196", "network196", "latency196", "buffer196 queue196", "worker196"],
    ),
    (
        ("storage196 network196 latency196 buffer196 queue196 worker196", 28),
        ["storage196 network196", "latency196 buffer196", "queue196 worker196"],
    ),
    (
        ("network196 latency196 buffer196 queue196 worker196 kernel196", 6),
        ["network196", "latency196", "buffer196", "queue196", "worker196", "kernel196"],
    ),
    (
        ("network196 latency196 buffer196 queue196 worker196 kernel196", 10),
        ["network196", "latency196", "buffer196", "queue196", "worker196", "kernel196"],
    ),
    (
        ("network196 latency196 buffer196 queue196 worker196 kernel196", 18),
        ["network196", "latency196", "buffer196 queue196", "worker196", "kernel196"],
    ),
    (
        ("network196 latency196 buffer196 queue196 worker196 kernel196", 28),
        ["network196 latency196", "buffer196 queue196 worker196", "kernel196"],
    ),
    (
        ("latency196 buffer196 queue196 worker196 kernel196 signal196", 6),
        ["latency196", "buffer196", "queue196", "worker196", "kernel196", "signal196"],
    ),
    (
        ("latency196 buffer196 queue196 worker196 kernel196 signal196", 10),
        ["latency196", "buffer196", "queue196", "worker196", "kernel196", "signal196"],
    ),
    (
        ("latency196 buffer196 queue196 worker196 kernel196 signal196", 18),
        ["latency196", "buffer196 queue196", "worker196", "kernel196", "signal196"],
    ),
    (
        ("latency196 buffer196 queue196 worker196 kernel196 signal196", 28),
        ["latency196 buffer196", "queue196 worker196 kernel196", "signal196"],
    ),
    (
        ("buffer196 queue196 worker196 kernel196 signal196 packet196", 6),
        ["buffer196", "queue196", "worker196", "kernel196", "signal196", "packet196"],
    ),
    (
        ("buffer196 queue196 worker196 kernel196 signal196 packet196", 10),
        ["buffer196", "queue196", "worker196", "kernel196", "signal196", "packet196"],
    ),
    (
        ("buffer196 queue196 worker196 kernel196 signal196 packet196", 18),
        ["buffer196 queue196", "worker196", "kernel196", "signal196", "packet196"],
    ),
    (
        ("buffer196 queue196 worker196 kernel196 signal196 packet196", 28),
        ["buffer196 queue196 worker196", "kernel196 signal196", "packet196"],
    ),
    (
        ("queue196 worker196 kernel196 signal196 packet196 router196", 6),
        ["queue196", "worker196", "kernel196", "signal196", "packet196", "router196"],
    ),
    (
        ("queue196 worker196 kernel196 signal196 packet196 router196", 10),
        ["queue196", "worker196", "kernel196", "signal196", "packet196", "router196"],
    ),
    (
        ("queue196 worker196 kernel196 signal196 packet196 router196", 18),
        ["queue196 worker196", "kernel196", "signal196", "packet196", "router196"],
    ),
    (
        ("queue196 worker196 kernel196 signal196 packet196 router196", 28),
        ["queue196 worker196 kernel196", "signal196 packet196", "router196"],
    ),
    (
        ("worker196 kernel196 signal196 packet196 router196 cluster196", 6),
        ["worker196", "kernel196", "signal196", "packet196", "router196", "cluster196"],
    ),
    (
        ("worker196 kernel196 signal196 packet196 router196 cluster196", 10),
        ["worker196", "kernel196", "signal196", "packet196", "router196", "cluster196"],
    ),
    (
        ("worker196 kernel196 signal196 packet196 router196 cluster196", 18),
        ["worker196", "kernel196", "signal196", "packet196", "router196", "cluster196"],
    ),
    (
        ("worker196 kernel196 signal196 packet196 router196 cluster196", 28),
        ["worker196 kernel196", "signal196 packet196", "router196 cluster196"],
    ),
    (
        ("kernel196 signal196 packet196 router196 cluster196 mirror196", 6),
        ["kernel196", "signal196", "packet196", "router196", "cluster196", "mirror196"],
    ),
    (
        ("kernel196 signal196 packet196 router196 cluster196 mirror196", 10),
        ["kernel196", "signal196", "packet196", "router196", "cluster196", "mirror196"],
    ),
    (
        ("kernel196 signal196 packet196 router196 cluster196 mirror196", 18),
        ["kernel196", "signal196", "packet196", "router196", "cluster196", "mirror196"],
    ),
    (
        ("kernel196 signal196 packet196 router196 cluster196 mirror196", 28),
        ["kernel196 signal196", "packet196 router196", "cluster196 mirror196"],
    ),
    (
        ("signal196 packet196 router196 cluster196 mirror196 filter196", 6),
        ["signal196", "packet196", "router196", "cluster196", "mirror196", "filter196"],
    ),
    (
        ("signal196 packet196 router196 cluster196 mirror196 filter196", 10),
        ["signal196", "packet196", "router196", "cluster196", "mirror196", "filter196"],
    ),
    (
        ("signal196 packet196 router196 cluster196 mirror196 filter196", 18),
        ["signal196", "packet196", "router196", "cluster196", "mirror196", "filter196"],
    ),
    (
        ("signal196 packet196 router196 cluster196 mirror196 filter196", 28),
        ["signal196 packet196", "router196 cluster196", "mirror196 filter196"],
    ),
    (
        ("packet196 router196 cluster196 mirror196 filter196 ranking196", 6),
        ["packet196", "router196", "cluster196", "mirror196", "filter196", "ranking196"],
    ),
    (
        ("packet196 router196 cluster196 mirror196 filter196 ranking196", 10),
        ["packet196", "router196", "cluster196", "mirror196", "filter196", "ranking196"],
    ),
    (
        ("packet196 router196 cluster196 mirror196 filter196 ranking196", 18),
        ["packet196", "router196", "cluster196", "mirror196", "filter196", "ranking196"],
    ),
    (
        ("packet196 router196 cluster196 mirror196 filter196 ranking196", 28),
        ["packet196 router196", "cluster196 mirror196", "filter196 ranking196"],
    ),
    (
        ("router196 cluster196 mirror196 filter196 ranking196 encoding196", 6),
        ["router196", "cluster196", "mirror196", "filter196", "ranking196", "encoding196"],
    ),
    (
        ("router196 cluster196 mirror196 filter196 ranking196 encoding196", 10),
        ["router196", "cluster196", "mirror196", "filter196", "ranking196", "encoding196"],
    ),
    (
        ("router196 cluster196 mirror196 filter196 ranking196 encoding196", 18),
        ["router196", "cluster196", "mirror196", "filter196", "ranking196", "encoding196"],
    ),
    (
        ("router196 cluster196 mirror196 filter196 ranking196 encoding196", 28),
        ["router196 cluster196", "mirror196 filter196", "ranking196 encoding196"],
    ),
    (
        ("cluster196 mirror196 filter196 ranking196 encoding196 mapping196", 6),
        ["cluster196", "mirror196", "filter196", "ranking196", "encoding196", "mapping196"],
    ),
    (
        ("cluster196 mirror196 filter196 ranking196 encoding196 mapping196", 10),
        ["cluster196", "mirror196", "filter196", "ranking196", "encoding196", "mapping196"],
    ),
    (
        ("cluster196 mirror196 filter196 ranking196 encoding196 mapping196", 18),
        ["cluster196", "mirror196", "filter196", "ranking196", "encoding196", "mapping196"],
    ),
    (
        ("cluster196 mirror196 filter196 ranking196 encoding196 mapping196", 28),
        ["cluster196 mirror196", "filter196 ranking196", "encoding196 mapping196"],
    ),
    (
        ("mirror196 filter196 ranking196 encoding196 mapping196 record196", 6),
        ["mirror196", "filter196", "ranking196", "encoding196", "mapping196", "record196"],
    ),
    (
        ("mirror196 filter196 ranking196 encoding196 mapping196 record196", 10),
        ["mirror196", "filter196", "ranking196", "encoding196", "mapping196", "record196"],
    ),
    (
        ("mirror196 filter196 ranking196 encoding196 mapping196 record196", 18),
        ["mirror196", "filter196", "ranking196", "encoding196", "mapping196", "record196"],
    ),
    (
        ("mirror196 filter196 ranking196 encoding196 mapping196 record196", 28),
        ["mirror196 filter196", "ranking196 encoding196", "mapping196 record196"],
    ),
    (
        ("filter196 ranking196 encoding196 mapping196 record196 candle196", 6),
        ["filter196", "ranking196", "encoding196", "mapping196", "record196", "candle196"],
    ),
    (
        ("filter196 ranking196 encoding196 mapping196 record196 candle196", 10),
        ["filter196", "ranking196", "encoding196", "mapping196", "record196", "candle196"],
    ),
    (
        ("filter196 ranking196 encoding196 mapping196 record196 candle196", 18),
        ["filter196", "ranking196", "encoding196", "mapping196", "record196", "candle196"],
    ),
    (
        ("filter196 ranking196 encoding196 mapping196 record196 candle196", 28),
        ["filter196 ranking196", "encoding196 mapping196", "record196 candle196"],
    ),
    (
        ("ranking196 encoding196 mapping196 record196 candle196 thread196", 6),
        ["ranking196", "encoding196", "mapping196", "record196", "candle196", "thread196"],
    ),
    (
        ("ranking196 encoding196 mapping196 record196 candle196 thread196", 10),
        ["ranking196", "encoding196", "mapping196", "record196", "candle196", "thread196"],
    ),
    (
        ("ranking196 encoding196 mapping196 record196 candle196 thread196", 18),
        ["ranking196", "encoding196", "mapping196", "record196", "candle196", "thread196"],
    ),
    (
        ("ranking196 encoding196 mapping196 record196 candle196 thread196", 28),
        ["ranking196 encoding196", "mapping196 record196", "candle196 thread196"],
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
