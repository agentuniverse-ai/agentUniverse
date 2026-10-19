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
        ("round 17: the quick brown fox jumps over the lazy dog", 4),
        ["round", "17:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 17: the quick brown fox jumps over the lazy dog", 8),
        ["round", "17: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 17: the quick brown fox jumps over the lazy dog", 12),
        ["round 17:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 17: the quick brown fox jumps over the lazy dog", 16),
        ["round 17: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 17: the quick brown fox jumps over the lazy dog", 24),
        ["round 17: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 17: the quick brown fox jumps over the lazy dog", 32),
        ["round 17: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 17: agentuniverse is a framework for multi agents", 4),
        ["round", "17:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 17: agentuniverse is a framework for multi agents", 8),
        ["round", "17:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 17: agentuniverse is a framework for multi agents", 12),
        ["round 17:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 17: agentuniverse is a framework for multi agents", 16),
        ["round 17:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 17: agentuniverse is a framework for multi agents", 24),
        ["round 17: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 17: agentuniverse is a framework for multi agents", 32),
        ["round 17: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 17: knowledge stored as vectors enables retrieval", 4),
        ["round", "17:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 17: knowledge stored as vectors enables retrieval", 8),
        ["round", "17:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 17: knowledge stored as vectors enables retrieval", 12),
        ["round 17:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 17: knowledge stored as vectors enables retrieval", 16),
        ["round 17:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 17: knowledge stored as vectors enables retrieval", 24),
        ["round 17: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 17: knowledge stored as vectors enables retrieval", 32),
        ["round 17: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 17: the processor reads the record then stops", 4),
        ["round", "17:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 17: the processor reads the record then stops", 8),
        ["round", "17: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 17: the processor reads the record then stops", 12),
        ["round 17:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 17: the processor reads the record then stops", 16),
        ["round 17: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 17: the processor reads the record then stops", 24),
        ["round 17: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 17: the processor reads the record then stops", 32),
        ["round 17: the processor reads", "the record then stops"],
    ),
    (
        ("round 17: a worker pulls the next task from the queue", 4),
        ["round", "17:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 17: a worker pulls the next task from the queue", 8),
        ["round", "17: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 17: a worker pulls the next task from the queue", 12),
        ["round 17: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 17: a worker pulls the next task from the queue", 16),
        ["round 17: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 17: a worker pulls the next task from the queue", 24),
        ["round 17: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 17: a worker pulls the next task from the queue", 32),
        ["round 17: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 17: signals travel through the network layer", 4),
        ["round", "17:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 17: signals travel through the network layer", 8),
        ["round", "17:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 17: signals travel through the network layer", 12),
        ["round 17:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 17: signals travel through the network layer", 16),
        ["round 17:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 17: signals travel through the network layer", 24),
        ["round 17: signals travel", "through the network", "layer"],
    ),
    (
        ("round 17: signals travel through the network layer", 32),
        ["round 17: signals travel through", "the network layer"],
    ),
    (
        ("round 17: the gateway routes each request by policy", 4),
        ["round", "17:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 17: the gateway routes each request by policy", 8),
        ["round", "17: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 17: the gateway routes each request by policy", 12),
        ["round 17:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 17: the gateway routes each request by policy", 16),
        ["round 17: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 17: the gateway routes each request by policy", 24),
        ["round 17: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 17: the gateway routes each request by policy", 32),
        ["round 17: the gateway routes", "each request by policy"],
    ),
    (
        ("round 17: memory grows until the buffer is full", 4),
        ["round", "17:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 17: memory grows until the buffer is full", 8),
        ["round", "17:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 17: memory grows until the buffer is full", 12),
        ["round 17:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 17: memory grows until the buffer is full", 16),
        ["round 17: memory", "grows until the", "buffer is full"],
    ),
    (("round 17: memory grows until the buffer is full", 24), ["round 17: memory grows", "until the buffer is full"]),
    (("round 17: memory grows until the buffer is full", 32), ["round 17: memory grows until the", "buffer is full"]),
    (
        ("round 17: the cluster mirrors every packet twice", 4),
        ["round", "17:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 17: the cluster mirrors every packet twice", 8),
        ["round", "17: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 17: the cluster mirrors every packet twice", 12),
        ["round 17:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 17: the cluster mirrors every packet twice", 16),
        ["round 17: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 17: the cluster mirrors every packet twice", 24),
        ["round 17: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 17: the cluster mirrors every packet twice", 32), ["round 17: the cluster mirrors", "every packet twice"]),
    (
        ("round 17: ranking uses tokens learned from the corpus", 4),
        ["round", "17:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 17: ranking uses tokens learned from the corpus", 8),
        ["round", "17:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 17: ranking uses tokens learned from the corpus", 12),
        ["round 17:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 17: ranking uses tokens learned from the corpus", 16),
        ["round 17:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 17: ranking uses tokens learned from the corpus", 24),
        ["round 17: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 17: ranking uses tokens learned from the corpus", 32),
        ["round 17: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 17: a long session ends when the candle dies", 4),
        ["round", "17:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 17: a long session ends when the candle dies", 8),
        ["round", "17: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 17: a long session ends when the candle dies", 12),
        ["round 17: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 17: a long session ends when the candle dies", 16),
        ["round 17: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 17: a long session ends when the candle dies", 24),
        ["round 17: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 17: a long session ends when the candle dies", 32),
        ["round 17: a long session ends", "when the candle dies"],
    ),
    (
        ("round 17: encode the prompt then map the result", 4),
        ["round", "17:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 17: encode the prompt then map the result", 8),
        ["round", "17:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 17: encode the prompt then map the result", 12),
        ["round 17:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 17: encode the prompt then map the result", 16),
        ["round 17: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 17: encode the prompt then map the result", 24),
        ["round 17: encode the", "prompt then map the", "result"],
    ),
    (("round 17: encode the prompt then map the result", 32), ["round 17: encode the prompt then", "map the result"]),
    (
        ("round 17: the kernel wakes the worker at dawn", 4),
        ["round", "17:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 17: the kernel wakes the worker at dawn", 8),
        ["round", "17: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 17: the kernel wakes the worker at dawn", 12),
        ["round 17:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 17: the kernel wakes the worker at dawn", 16), ["round 17: the", "kernel wakes the", "worker at dawn"]),
    (("round 17: the kernel wakes the worker at dawn", 24), ["round 17: the kernel", "wakes the worker at dawn"]),
    (("round 17: the kernel wakes the worker at dawn", 32), ["round 17: the kernel wakes the", "worker at dawn"]),
    (
        ("round 17: service latency drops after the patch", 4),
        ["round", "17:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 17: service latency drops after the patch", 8),
        ["round", "17:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 17: service latency drops after the patch", 12),
        ["round 17:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 17: service latency drops after the patch", 16),
        ["round 17:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 17: service latency drops after the patch", 24),
        ["round 17: service", "latency drops after the", "patch"],
    ),
    (("round 17: service latency drops after the patch", 32), ["round 17: service latency drops", "after the patch"]),
    (
        ("round 17: the library caches every vector it sees", 4),
        ["round", "17:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 17: the library caches every vector it sees", 8),
        ["round", "17: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 17: the library caches every vector it sees", 12),
        ["round 17:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 17: the library caches every vector it sees", 16),
        ["round 17: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 17: the library caches every vector it sees", 24),
        ["round 17: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 17: the library caches every vector it sees", 32),
        ["round 17: the library caches", "every vector it sees"],
    ),
    (
        ("round 17: agents argue then the debate resolves", 4),
        ["round", "17:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 17: agents argue then the debate resolves", 8),
        ["round", "17:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 17: agents argue then the debate resolves", 12),
        ["round 17:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 17: agents argue then the debate resolves", 16),
        ["round 17: agents", "argue then the", "debate resolves"],
    ),
    (("round 17: agents argue then the debate resolves", 24), ["round 17: agents argue", "then the debate resolves"]),
    (("round 17: agents argue then the debate resolves", 32), ["round 17: agents argue then the", "debate resolves"]),
    (
        ("round 17: the filter keeps only strong matches", 4),
        ["round", "17:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 17: the filter keeps only strong matches", 8),
        ["round", "17: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 17: the filter keeps only strong matches", 12),
        ["round 17:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 17: the filter keeps only strong matches", 16),
        ["round 17: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 17: the filter keeps only strong matches", 24), ["round 17: the filter", "keeps only strong", "matches"]),
    (("round 17: the filter keeps only strong matches", 32), ["round 17: the filter keeps only", "strong matches"]),
    (
        ("round 17: the model answers with a short reply", 4),
        ["round", "17:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 17: the model answers with a short reply", 8),
        ["round", "17: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 17: the model answers with a short reply", 12),
        ["round 17:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 17: the model answers with a short reply", 16),
        ["round 17: the", "model answers", "with a short", "reply"],
    ),
    (("round 17: the model answers with a short reply", 24), ["round 17: the model", "answers with a short", "reply"]),
    (("round 17: the model answers with a short reply", 32), ["round 17: the model answers with", "a short reply"]),
    (
        ("round 17: the recorder stores the reasoning trace", 4),
        ["round", "17:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 17: the recorder stores the reasoning trace", 8),
        ["round", "17: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 17: the recorder stores the reasoning trace", 12),
        ["round 17:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 17: the recorder stores the reasoning trace", 16),
        ["round 17: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 17: the recorder stores the reasoning trace", 24),
        ["round 17: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 17: the recorder stores the reasoning trace", 32),
        ["round 17: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 17: the angel watches the processor run", 4),
        ["round", "17:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 17: the angel watches the processor run", 8),
        ["round", "17: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 17: the angel watches the processor run", 12),
        ["round 17:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 17: the angel watches the processor run", 16), ["round 17: the", "angel watches", "the processor", "run"]),
    (("round 17: the angel watches the processor run", 24), ["round 17: the angel", "watches the processor", "run"]),
    (("round 17: the angel watches the processor run", 32), ["round 17: the angel watches the", "processor run"]),
    (
        ("round 17: angle of the vector decides the match", 4),
        ["round", "17:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 17: angle of the vector decides the match", 8),
        ["round", "17:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 17: angle of the vector decides the match", 12),
        ["round 17:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 17: angle of the vector decides the match", 16),
        ["round 17: angle", "of the vector", "decides the", "match"],
    ),
    (("round 17: angle of the vector decides the match", 24), ["round 17: angle of the", "vector decides the match"]),
    (("round 17: angle of the vector decides the match", 32), ["round 17: angle of the vector", "decides the match"]),
    (
        ("round 17: the candle burns twice as long at night", 4),
        ["round", "17:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 17: the candle burns twice as long at night", 8),
        ["round", "17: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 17: the candle burns twice as long at night", 12),
        ["round 17:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 17: the candle burns twice as long at night", 16),
        ["round 17: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 17: the candle burns twice as long at night", 24),
        ["round 17: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 17: the candle burns twice as long at night", 32),
        ["round 17: the candle burns twice", "as long at night"],
    ),
    (
        ("round 17: a mirror of the universe in one line", 4),
        ["round", "17:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 17: a mirror of the universe in one line", 8),
        ["round", "17: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 17: a mirror of the universe in one line", 12),
        ["round 17: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 17: a mirror of the universe in one line", 16),
        ["round 17: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 17: a mirror of the universe in one line", 24), ["round 17: a mirror of", "the universe in one line"]),
    (("round 17: a mirror of the universe in one line", 32), ["round 17: a mirror of the", "universe in one line"]),
    (
        ("round 17: the queue drains before the storm", 4),
        ["round", "17:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 17: the queue drains before the storm", 8),
        ["round", "17: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 17: the queue drains before the storm", 12), ["round 17:", "the queue", "drains", "before the", "storm"]),
    (("round 17: the queue drains before the storm", 16), ["round 17: the", "queue drains", "before the storm"]),
    (("round 17: the queue drains before the storm", 24), ["round 17: the queue", "drains before the storm"]),
    (("round 17: the queue drains before the storm", 32), ["round 17: the queue drains", "before the storm"]),
    (
        ("kitten17 sitting17 agent17 angle17 universe17 memory17", 6),
        ["kitten17", "sitting17", "agent17", "angle17", "universe17", "memory17"],
    ),
    (
        ("kitten17 sitting17 agent17 angle17 universe17 memory17", 10),
        ["kitten17", "sitting17", "agent17", "angle17", "universe17", "memory17"],
    ),
    (
        ("kitten17 sitting17 agent17 angle17 universe17 memory17", 18),
        ["kitten17 sitting17", "agent17 angle17", "universe17", "memory17"],
    ),
    (
        ("kitten17 sitting17 agent17 angle17 universe17 memory17", 28),
        ["kitten17 sitting17 agent17", "angle17 universe17 memory17"],
    ),
    (
        ("sitting17 agent17 angle17 universe17 memory17 stream17", 6),
        ["sitting17", "agent17", "angle17", "universe17", "memory17", "stream17"],
    ),
    (
        ("sitting17 agent17 angle17 universe17 memory17 stream17", 10),
        ["sitting17", "agent17", "angle17", "universe17", "memory17", "stream17"],
    ),
    (
        ("sitting17 agent17 angle17 universe17 memory17 stream17", 18),
        ["sitting17 agent17", "angle17 universe17", "memory17 stream17"],
    ),
    (
        ("sitting17 agent17 angle17 universe17 memory17 stream17", 28),
        ["sitting17 agent17 angle17", "universe17 memory17 stream17"],
    ),
    (
        ("agent17 angle17 universe17 memory17 stream17 context17", 6),
        ["agent17", "angle17", "universe17", "memory17", "stream17", "context17"],
    ),
    (
        ("agent17 angle17 universe17 memory17 stream17 context17", 10),
        ["agent17", "angle17", "universe17", "memory17", "stream17", "context17"],
    ),
    (
        ("agent17 angle17 universe17 memory17 stream17 context17", 18),
        ["agent17 angle17", "universe17", "memory17 stream17", "context17"],
    ),
    (
        ("agent17 angle17 universe17 memory17 stream17 context17", 28),
        ["agent17 angle17 universe17", "memory17 stream17 context17"],
    ),
    (
        ("angle17 universe17 memory17 stream17 context17 knowledge17", 6),
        ["angle17", "universe17", "memory17", "stream17", "context17", "knowledge17"],
    ),
    (
        ("angle17 universe17 memory17 stream17 context17 knowledge17", 10),
        ["angle17", "universe17", "memory17", "stream17", "context17", "knowledge17"],
    ),
    (
        ("angle17 universe17 memory17 stream17 context17 knowledge17", 18),
        ["angle17 universe17", "memory17 stream17", "context17", "knowledge17"],
    ),
    (
        ("angle17 universe17 memory17 stream17 context17 knowledge17", 28),
        ["angle17 universe17 memory17", "stream17 context17", "knowledge17"],
    ),
    (
        ("universe17 memory17 stream17 context17 knowledge17 vector17", 6),
        ["universe17", "memory17", "stream17", "context17", "knowledge17", "vector17"],
    ),
    (
        ("universe17 memory17 stream17 context17 knowledge17 vector17", 10),
        ["universe17", "memory17", "stream17", "context17", "knowledge17", "vector17"],
    ),
    (
        ("universe17 memory17 stream17 context17 knowledge17 vector17", 18),
        ["universe17", "memory17 stream17", "context17", "knowledge17", "vector17"],
    ),
    (
        ("universe17 memory17 stream17 context17 knowledge17 vector17", 28),
        ["universe17 memory17 stream17", "context17 knowledge17", "vector17"],
    ),
    (
        ("memory17 stream17 context17 knowledge17 vector17 processor17", 6),
        ["memory17", "stream17", "context17", "knowledge17", "vector17", "processor17"],
    ),
    (
        ("memory17 stream17 context17 knowledge17 vector17 processor17", 10),
        ["memory17", "stream17", "context17", "knowledge17", "vector17", "processor17"],
    ),
    (
        ("memory17 stream17 context17 knowledge17 vector17 processor17", 18),
        ["memory17 stream17", "context17", "knowledge17", "vector17", "processor17"],
    ),
    (
        ("memory17 stream17 context17 knowledge17 vector17 processor17", 28),
        ["memory17 stream17 context17", "knowledge17 vector17", "processor17"],
    ),
    (
        ("stream17 context17 knowledge17 vector17 processor17 reasoning17", 6),
        ["stream17", "context17", "knowledge17", "vector17", "processor17", "reasoning17"],
    ),
    (
        ("stream17 context17 knowledge17 vector17 processor17 reasoning17", 10),
        ["stream17", "context17", "knowledge17", "vector17", "processor17", "reasoning17"],
    ),
    (
        ("stream17 context17 knowledge17 vector17 processor17 reasoning17", 18),
        ["stream17 context17", "knowledge17", "vector17", "processor17", "reasoning17"],
    ),
    (
        ("stream17 context17 knowledge17 vector17 processor17 reasoning17", 28),
        ["stream17 context17", "knowledge17 vector17", "processor17 reasoning17"],
    ),
    (
        ("context17 knowledge17 vector17 processor17 reasoning17 machine17", 6),
        ["context17", "knowledge17", "vector17", "processor17", "reasoning17", "machine17"],
    ),
    (
        ("context17 knowledge17 vector17 processor17 reasoning17 machine17", 10),
        ["context17", "knowledge17", "vector17", "processor17", "reasoning17", "machine17"],
    ),
    (
        ("context17 knowledge17 vector17 processor17 reasoning17 machine17", 18),
        ["context17", "knowledge17", "vector17", "processor17", "reasoning17", "machine17"],
    ),
    (
        ("context17 knowledge17 vector17 processor17 reasoning17 machine17", 28),
        ["context17 knowledge17", "vector17 processor17", "reasoning17 machine17"],
    ),
    (
        ("knowledge17 vector17 processor17 reasoning17 machine17 learning17", 6),
        ["knowledge17", "vector17", "processor17", "reasoning17", "machine17", "learning17"],
    ),
    (
        ("knowledge17 vector17 processor17 reasoning17 machine17 learning17", 10),
        ["knowledge17", "vector17", "processor17", "reasoning17", "machine17", "learning17"],
    ),
    (
        ("knowledge17 vector17 processor17 reasoning17 machine17 learning17", 18),
        ["knowledge17", "vector17", "processor17", "reasoning17", "machine17", "learning17"],
    ),
    (
        ("knowledge17 vector17 processor17 reasoning17 machine17 learning17", 28),
        ["knowledge17 vector17", "processor17 reasoning17", "machine17 learning17"],
    ),
    (
        ("vector17 processor17 reasoning17 machine17 learning17 model17", 6),
        ["vector17", "processor17", "reasoning17", "machine17", "learning17", "model17"],
    ),
    (
        ("vector17 processor17 reasoning17 machine17 learning17 model17", 10),
        ["vector17", "processor17", "reasoning17", "machine17", "learning17", "model17"],
    ),
    (
        ("vector17 processor17 reasoning17 machine17 learning17 model17", 18),
        ["vector17", "processor17", "reasoning17", "machine17", "learning17 model17"],
    ),
    (
        ("vector17 processor17 reasoning17 machine17 learning17 model17", 28),
        ["vector17 processor17", "reasoning17 machine17", "learning17 model17"],
    ),
    (
        ("processor17 reasoning17 machine17 learning17 model17 token17", 6),
        ["processor17", "reasoning17", "machine17", "learning17", "model17", "token17"],
    ),
    (
        ("processor17 reasoning17 machine17 learning17 model17 token17", 10),
        ["processor17", "reasoning17", "machine17", "learning17", "model17", "token17"],
    ),
    (
        ("processor17 reasoning17 machine17 learning17 model17 token17", 18),
        ["processor17", "reasoning17", "machine17", "learning17 model17", "token17"],
    ),
    (
        ("processor17 reasoning17 machine17 learning17 model17 token17", 28),
        ["processor17 reasoning17", "machine17 learning17 model17", "token17"],
    ),
    (
        ("reasoning17 machine17 learning17 model17 token17 prompt17", 6),
        ["reasoning17", "machine17", "learning17", "model17", "token17", "prompt17"],
    ),
    (
        ("reasoning17 machine17 learning17 model17 token17 prompt17", 10),
        ["reasoning17", "machine17", "learning17", "model17", "token17", "prompt17"],
    ),
    (
        ("reasoning17 machine17 learning17 model17 token17 prompt17", 18),
        ["reasoning17", "machine17", "learning17 model17", "token17 prompt17"],
    ),
    (
        ("reasoning17 machine17 learning17 model17 token17 prompt17", 28),
        ["reasoning17 machine17", "learning17 model17 token17", "prompt17"],
    ),
    (
        ("machine17 learning17 model17 token17 prompt17 session17", 6),
        ["machine17", "learning17", "model17", "token17", "prompt17", "session17"],
    ),
    (
        ("machine17 learning17 model17 token17 prompt17 session17", 10),
        ["machine17", "learning17", "model17", "token17", "prompt17", "session17"],
    ),
    (
        ("machine17 learning17 model17 token17 prompt17 session17", 18),
        ["machine17", "learning17 model17", "token17 prompt17", "session17"],
    ),
    (
        ("machine17 learning17 model17 token17 prompt17 session17", 28),
        ["machine17 learning17 model17", "token17 prompt17 session17"],
    ),
    (
        ("learning17 model17 token17 prompt17 session17 library17", 6),
        ["learning17", "model17", "token17", "prompt17", "session17", "library17"],
    ),
    (
        ("learning17 model17 token17 prompt17 session17 library17", 10),
        ["learning17", "model17", "token17", "prompt17", "session17", "library17"],
    ),
    (
        ("learning17 model17 token17 prompt17 session17 library17", 18),
        ["learning17 model17", "token17 prompt17", "session17", "library17"],
    ),
    (
        ("learning17 model17 token17 prompt17 session17 library17", 28),
        ["learning17 model17 token17", "prompt17 session17 library17"],
    ),
    (
        ("model17 token17 prompt17 session17 library17 service17", 6),
        ["model17", "token17", "prompt17", "session17", "library17", "service17"],
    ),
    (
        ("model17 token17 prompt17 session17 library17 service17", 10),
        ["model17", "token17", "prompt17", "session17", "library17", "service17"],
    ),
    (
        ("model17 token17 prompt17 session17 library17 service17", 18),
        ["model17 token17", "prompt17 session17", "library17", "service17"],
    ),
    (
        ("model17 token17 prompt17 session17 library17 service17", 28),
        ["model17 token17 prompt17", "session17 library17", "service17"],
    ),
    (
        ("token17 prompt17 session17 library17 service17 gateway17", 6),
        ["token17", "prompt17", "session17", "library17", "service17", "gateway17"],
    ),
    (
        ("token17 prompt17 session17 library17 service17 gateway17", 10),
        ["token17", "prompt17", "session17", "library17", "service17", "gateway17"],
    ),
    (
        ("token17 prompt17 session17 library17 service17 gateway17", 18),
        ["token17 prompt17", "session17", "library17", "service17", "gateway17"],
    ),
    (
        ("token17 prompt17 session17 library17 service17 gateway17", 28),
        ["token17 prompt17 session17", "library17 service17", "gateway17"],
    ),
    (
        ("prompt17 session17 library17 service17 gateway17 storage17", 6),
        ["prompt17", "session17", "library17", "service17", "gateway17", "storage17"],
    ),
    (
        ("prompt17 session17 library17 service17 gateway17 storage17", 10),
        ["prompt17", "session17", "library17", "service17", "gateway17", "storage17"],
    ),
    (
        ("prompt17 session17 library17 service17 gateway17 storage17", 18),
        ["prompt17 session17", "library17", "service17", "gateway17", "storage17"],
    ),
    (
        ("prompt17 session17 library17 service17 gateway17 storage17", 28),
        ["prompt17 session17 library17", "service17 gateway17", "storage17"],
    ),
    (
        ("session17 library17 service17 gateway17 storage17 network17", 6),
        ["session17", "library17", "service17", "gateway17", "storage17", "network17"],
    ),
    (
        ("session17 library17 service17 gateway17 storage17 network17", 10),
        ["session17", "library17", "service17", "gateway17", "storage17", "network17"],
    ),
    (
        ("session17 library17 service17 gateway17 storage17 network17", 18),
        ["session17", "library17", "service17", "gateway17", "storage17", "network17"],
    ),
    (
        ("session17 library17 service17 gateway17 storage17 network17", 28),
        ["session17 library17", "service17 gateway17", "storage17 network17"],
    ),
    (
        ("library17 service17 gateway17 storage17 network17 latency17", 6),
        ["library17", "service17", "gateway17", "storage17", "network17", "latency17"],
    ),
    (
        ("library17 service17 gateway17 storage17 network17 latency17", 10),
        ["library17", "service17", "gateway17", "storage17", "network17", "latency17"],
    ),
    (
        ("library17 service17 gateway17 storage17 network17 latency17", 18),
        ["library17", "service17", "gateway17", "storage17", "network17", "latency17"],
    ),
    (
        ("library17 service17 gateway17 storage17 network17 latency17", 28),
        ["library17 service17", "gateway17 storage17", "network17 latency17"],
    ),
    (
        ("service17 gateway17 storage17 network17 latency17 buffer17", 6),
        ["service17", "gateway17", "storage17", "network17", "latency17", "buffer17"],
    ),
    (
        ("service17 gateway17 storage17 network17 latency17 buffer17", 10),
        ["service17", "gateway17", "storage17", "network17", "latency17", "buffer17"],
    ),
    (
        ("service17 gateway17 storage17 network17 latency17 buffer17", 18),
        ["service17", "gateway17", "storage17", "network17", "latency17 buffer17"],
    ),
    (
        ("service17 gateway17 storage17 network17 latency17 buffer17", 28),
        ["service17 gateway17", "storage17 network17", "latency17 buffer17"],
    ),
    (
        ("gateway17 storage17 network17 latency17 buffer17 queue17", 6),
        ["gateway17", "storage17", "network17", "latency17", "buffer17", "queue17"],
    ),
    (
        ("gateway17 storage17 network17 latency17 buffer17 queue17", 10),
        ["gateway17", "storage17", "network17", "latency17", "buffer17", "queue17"],
    ),
    (
        ("gateway17 storage17 network17 latency17 buffer17 queue17", 18),
        ["gateway17", "storage17", "network17", "latency17 buffer17", "queue17"],
    ),
    (
        ("gateway17 storage17 network17 latency17 buffer17 queue17", 28),
        ["gateway17 storage17", "network17 latency17 buffer17", "queue17"],
    ),
    (
        ("storage17 network17 latency17 buffer17 queue17 worker17", 6),
        ["storage17", "network17", "latency17", "buffer17", "queue17", "worker17"],
    ),
    (
        ("storage17 network17 latency17 buffer17 queue17 worker17", 10),
        ["storage17", "network17", "latency17", "buffer17", "queue17", "worker17"],
    ),
    (
        ("storage17 network17 latency17 buffer17 queue17 worker17", 18),
        ["storage17", "network17", "latency17 buffer17", "queue17 worker17"],
    ),
    (
        ("storage17 network17 latency17 buffer17 queue17 worker17", 28),
        ["storage17 network17", "latency17 buffer17 queue17", "worker17"],
    ),
    (
        ("network17 latency17 buffer17 queue17 worker17 kernel17", 6),
        ["network17", "latency17", "buffer17", "queue17", "worker17", "kernel17"],
    ),
    (
        ("network17 latency17 buffer17 queue17 worker17 kernel17", 10),
        ["network17", "latency17", "buffer17", "queue17", "worker17", "kernel17"],
    ),
    (
        ("network17 latency17 buffer17 queue17 worker17 kernel17", 18),
        ["network17", "latency17 buffer17", "queue17 worker17", "kernel17"],
    ),
    (
        ("network17 latency17 buffer17 queue17 worker17 kernel17", 28),
        ["network17 latency17 buffer17", "queue17 worker17 kernel17"],
    ),
    (
        ("latency17 buffer17 queue17 worker17 kernel17 signal17", 6),
        ["latency17", "buffer17", "queue17", "worker17", "kernel17", "signal17"],
    ),
    (
        ("latency17 buffer17 queue17 worker17 kernel17 signal17", 10),
        ["latency17", "buffer17", "queue17", "worker17", "kernel17", "signal17"],
    ),
    (
        ("latency17 buffer17 queue17 worker17 kernel17 signal17", 18),
        ["latency17 buffer17", "queue17 worker17", "kernel17 signal17"],
    ),
    (
        ("latency17 buffer17 queue17 worker17 kernel17 signal17", 28),
        ["latency17 buffer17 queue17", "worker17 kernel17 signal17"],
    ),
    (
        ("buffer17 queue17 worker17 kernel17 signal17 packet17", 6),
        ["buffer17", "queue17", "worker17", "kernel17", "signal17", "packet17"],
    ),
    (
        ("buffer17 queue17 worker17 kernel17 signal17 packet17", 10),
        ["buffer17", "queue17", "worker17", "kernel17", "signal17", "packet17"],
    ),
    (
        ("buffer17 queue17 worker17 kernel17 signal17 packet17", 18),
        ["buffer17 queue17", "worker17 kernel17", "signal17 packet17"],
    ),
    (
        ("buffer17 queue17 worker17 kernel17 signal17 packet17", 28),
        ["buffer17 queue17 worker17", "kernel17 signal17 packet17"],
    ),
    (
        ("queue17 worker17 kernel17 signal17 packet17 router17", 6),
        ["queue17", "worker17", "kernel17", "signal17", "packet17", "router17"],
    ),
    (
        ("queue17 worker17 kernel17 signal17 packet17 router17", 10),
        ["queue17", "worker17", "kernel17", "signal17", "packet17", "router17"],
    ),
    (
        ("queue17 worker17 kernel17 signal17 packet17 router17", 18),
        ["queue17 worker17", "kernel17 signal17", "packet17 router17"],
    ),
    (
        ("queue17 worker17 kernel17 signal17 packet17 router17", 28),
        ["queue17 worker17 kernel17", "signal17 packet17 router17"],
    ),
    (
        ("worker17 kernel17 signal17 packet17 router17 cluster17", 6),
        ["worker17", "kernel17", "signal17", "packet17", "router17", "cluster17"],
    ),
    (
        ("worker17 kernel17 signal17 packet17 router17 cluster17", 10),
        ["worker17", "kernel17", "signal17", "packet17", "router17", "cluster17"],
    ),
    (
        ("worker17 kernel17 signal17 packet17 router17 cluster17", 18),
        ["worker17 kernel17", "signal17 packet17", "router17 cluster17"],
    ),
    (
        ("worker17 kernel17 signal17 packet17 router17 cluster17", 28),
        ["worker17 kernel17 signal17", "packet17 router17 cluster17"],
    ),
    (
        ("kernel17 signal17 packet17 router17 cluster17 mirror17", 6),
        ["kernel17", "signal17", "packet17", "router17", "cluster17", "mirror17"],
    ),
    (
        ("kernel17 signal17 packet17 router17 cluster17 mirror17", 10),
        ["kernel17", "signal17", "packet17", "router17", "cluster17", "mirror17"],
    ),
    (
        ("kernel17 signal17 packet17 router17 cluster17 mirror17", 18),
        ["kernel17 signal17", "packet17 router17", "cluster17 mirror17"],
    ),
    (
        ("kernel17 signal17 packet17 router17 cluster17 mirror17", 28),
        ["kernel17 signal17 packet17", "router17 cluster17 mirror17"],
    ),
    (
        ("signal17 packet17 router17 cluster17 mirror17 filter17", 6),
        ["signal17", "packet17", "router17", "cluster17", "mirror17", "filter17"],
    ),
    (
        ("signal17 packet17 router17 cluster17 mirror17 filter17", 10),
        ["signal17", "packet17", "router17", "cluster17", "mirror17", "filter17"],
    ),
    (
        ("signal17 packet17 router17 cluster17 mirror17 filter17", 18),
        ["signal17 packet17", "router17 cluster17", "mirror17 filter17"],
    ),
    (
        ("signal17 packet17 router17 cluster17 mirror17 filter17", 28),
        ["signal17 packet17 router17", "cluster17 mirror17 filter17"],
    ),
    (
        ("packet17 router17 cluster17 mirror17 filter17 ranking17", 6),
        ["packet17", "router17", "cluster17", "mirror17", "filter17", "ranking17"],
    ),
    (
        ("packet17 router17 cluster17 mirror17 filter17 ranking17", 10),
        ["packet17", "router17", "cluster17", "mirror17", "filter17", "ranking17"],
    ),
    (
        ("packet17 router17 cluster17 mirror17 filter17 ranking17", 18),
        ["packet17 router17", "cluster17 mirror17", "filter17 ranking17"],
    ),
    (
        ("packet17 router17 cluster17 mirror17 filter17 ranking17", 28),
        ["packet17 router17 cluster17", "mirror17 filter17 ranking17"],
    ),
    (
        ("router17 cluster17 mirror17 filter17 ranking17 encoding17", 6),
        ["router17", "cluster17", "mirror17", "filter17", "ranking17", "encoding17"],
    ),
    (
        ("router17 cluster17 mirror17 filter17 ranking17 encoding17", 10),
        ["router17", "cluster17", "mirror17", "filter17", "ranking17", "encoding17"],
    ),
    (
        ("router17 cluster17 mirror17 filter17 ranking17 encoding17", 18),
        ["router17 cluster17", "mirror17 filter17", "ranking17", "encoding17"],
    ),
    (
        ("router17 cluster17 mirror17 filter17 ranking17 encoding17", 28),
        ["router17 cluster17 mirror17", "filter17 ranking17", "encoding17"],
    ),
    (
        ("cluster17 mirror17 filter17 ranking17 encoding17 mapping17", 6),
        ["cluster17", "mirror17", "filter17", "ranking17", "encoding17", "mapping17"],
    ),
    (
        ("cluster17 mirror17 filter17 ranking17 encoding17 mapping17", 10),
        ["cluster17", "mirror17", "filter17", "ranking17", "encoding17", "mapping17"],
    ),
    (
        ("cluster17 mirror17 filter17 ranking17 encoding17 mapping17", 18),
        ["cluster17 mirror17", "filter17 ranking17", "encoding17", "mapping17"],
    ),
    (
        ("cluster17 mirror17 filter17 ranking17 encoding17 mapping17", 28),
        ["cluster17 mirror17 filter17", "ranking17 encoding17", "mapping17"],
    ),
    (
        ("mirror17 filter17 ranking17 encoding17 mapping17 record17", 6),
        ["mirror17", "filter17", "ranking17", "encoding17", "mapping17", "record17"],
    ),
    (
        ("mirror17 filter17 ranking17 encoding17 mapping17 record17", 10),
        ["mirror17", "filter17", "ranking17", "encoding17", "mapping17", "record17"],
    ),
    (
        ("mirror17 filter17 ranking17 encoding17 mapping17 record17", 18),
        ["mirror17 filter17", "ranking17", "encoding17", "mapping17 record17"],
    ),
    (
        ("mirror17 filter17 ranking17 encoding17 mapping17 record17", 28),
        ["mirror17 filter17 ranking17", "encoding17 mapping17", "record17"],
    ),
    (
        ("filter17 ranking17 encoding17 mapping17 record17 candle17", 6),
        ["filter17", "ranking17", "encoding17", "mapping17", "record17", "candle17"],
    ),
    (
        ("filter17 ranking17 encoding17 mapping17 record17 candle17", 10),
        ["filter17", "ranking17", "encoding17", "mapping17", "record17", "candle17"],
    ),
    (
        ("filter17 ranking17 encoding17 mapping17 record17 candle17", 18),
        ["filter17 ranking17", "encoding17", "mapping17 record17", "candle17"],
    ),
    (
        ("filter17 ranking17 encoding17 mapping17 record17 candle17", 28),
        ["filter17 ranking17", "encoding17 mapping17", "record17 candle17"],
    ),
    (
        ("ranking17 encoding17 mapping17 record17 candle17 thread17", 6),
        ["ranking17", "encoding17", "mapping17", "record17", "candle17", "thread17"],
    ),
    (
        ("ranking17 encoding17 mapping17 record17 candle17 thread17", 10),
        ["ranking17", "encoding17", "mapping17", "record17", "candle17", "thread17"],
    ),
    (
        ("ranking17 encoding17 mapping17 record17 candle17 thread17", 18),
        ["ranking17", "encoding17", "mapping17 record17", "candle17 thread17"],
    ),
    (
        ("ranking17 encoding17 mapping17 record17 candle17 thread17", 28),
        ["ranking17 encoding17", "mapping17 record17 candle17", "thread17"],
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
