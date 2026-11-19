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
        ("round 143: the quick brown fox jumps over the lazy dog", 4),
        ["round", "143:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 143: the quick brown fox jumps over the lazy dog", 8),
        ["round", "143: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 143: the quick brown fox jumps over the lazy dog", 12),
        ["round 143:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 143: the quick brown fox jumps over the lazy dog", 16),
        ["round 143: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 143: the quick brown fox jumps over the lazy dog", 24),
        ["round 143: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 143: the quick brown fox jumps over the lazy dog", 32),
        ["round 143: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 143: agentuniverse is a framework for multi agents", 4),
        ["round", "143:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 143: agentuniverse is a framework for multi agents", 8),
        ["round", "143:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 143: agentuniverse is a framework for multi agents", 12),
        ["round 143:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 143: agentuniverse is a framework for multi agents", 16),
        ["round 143:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 143: agentuniverse is a framework for multi agents", 24),
        ["round 143: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 143: agentuniverse is a framework for multi agents", 32),
        ["round 143: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 143: knowledge stored as vectors enables retrieval", 4),
        ["round", "143:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 143: knowledge stored as vectors enables retrieval", 8),
        ["round", "143:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 143: knowledge stored as vectors enables retrieval", 12),
        ["round 143:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 143: knowledge stored as vectors enables retrieval", 16),
        ["round 143:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 143: knowledge stored as vectors enables retrieval", 24),
        ["round 143: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 143: knowledge stored as vectors enables retrieval", 32),
        ["round 143: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 143: the processor reads the record then stops", 4),
        ["round", "143:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 143: the processor reads the record then stops", 8),
        ["round", "143: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 143: the processor reads the record then stops", 12),
        ["round 143:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 143: the processor reads the record then stops", 16),
        ["round 143: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 143: the processor reads the record then stops", 24),
        ["round 143: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 143: the processor reads the record then stops", 32),
        ["round 143: the processor reads", "the record then stops"],
    ),
    (
        ("round 143: a worker pulls the next task from the queue", 4),
        ["round", "143:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 143: a worker pulls the next task from the queue", 8),
        ["round", "143: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 143: a worker pulls the next task from the queue", 12),
        ["round 143: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 143: a worker pulls the next task from the queue", 16),
        ["round 143: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 143: a worker pulls the next task from the queue", 24),
        ["round 143: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 143: a worker pulls the next task from the queue", 32),
        ["round 143: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 143: signals travel through the network layer", 4),
        ["round", "143:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 143: signals travel through the network layer", 8),
        ["round", "143:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 143: signals travel through the network layer", 12),
        ["round 143:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 143: signals travel through the network layer", 16),
        ["round 143:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 143: signals travel through the network layer", 24),
        ["round 143: signals", "travel through the", "network layer"],
    ),
    (
        ("round 143: signals travel through the network layer", 32),
        ["round 143: signals travel", "through the network layer"],
    ),
    (
        ("round 143: the gateway routes each request by policy", 4),
        ["round", "143:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 143: the gateway routes each request by policy", 8),
        ["round", "143: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 143: the gateway routes each request by policy", 12),
        ["round 143:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 143: the gateway routes each request by policy", 16),
        ["round 143: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 143: the gateway routes each request by policy", 24),
        ["round 143: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 143: the gateway routes each request by policy", 32),
        ["round 143: the gateway routes", "each request by policy"],
    ),
    (
        ("round 143: memory grows until the buffer is full", 4),
        ["round", "143:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 143: memory grows until the buffer is full", 8),
        ["round", "143:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 143: memory grows until the buffer is full", 12),
        ["round 143:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 143: memory grows until the buffer is full", 16),
        ["round 143:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 143: memory grows until the buffer is full", 24), ["round 143: memory grows", "until the buffer is full"]),
    (("round 143: memory grows until the buffer is full", 32), ["round 143: memory grows until", "the buffer is full"]),
    (
        ("round 143: the cluster mirrors every packet twice", 4),
        ["round", "143:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 143: the cluster mirrors every packet twice", 8),
        ["round", "143: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 143: the cluster mirrors every packet twice", 12),
        ["round 143:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 143: the cluster mirrors every packet twice", 16),
        ["round 143: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 143: the cluster mirrors every packet twice", 24),
        ["round 143: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 143: the cluster mirrors every packet twice", 32),
        ["round 143: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 143: ranking uses tokens learned from the corpus", 4),
        ["round", "143:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 143: ranking uses tokens learned from the corpus", 8),
        ["round", "143:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 143: ranking uses tokens learned from the corpus", 12),
        ["round 143:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 143: ranking uses tokens learned from the corpus", 16),
        ["round 143:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 143: ranking uses tokens learned from the corpus", 24),
        ["round 143: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 143: ranking uses tokens learned from the corpus", 32),
        ["round 143: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 143: a long session ends when the candle dies", 4),
        ["round", "143:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 143: a long session ends when the candle dies", 8),
        ["round", "143: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 143: a long session ends when the candle dies", 12),
        ["round 143: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 143: a long session ends when the candle dies", 16),
        ["round 143: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 143: a long session ends when the candle dies", 24),
        ["round 143: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 143: a long session ends when the candle dies", 32),
        ["round 143: a long session ends", "when the candle dies"],
    ),
    (
        ("round 143: encode the prompt then map the result", 4),
        ["round", "143:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 143: encode the prompt then map the result", 8),
        ["round", "143:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 143: encode the prompt then map the result", 12),
        ["round 143:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 143: encode the prompt then map the result", 16),
        ["round 143:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 143: encode the prompt then map the result", 24),
        ["round 143: encode the", "prompt then map the", "result"],
    ),
    (("round 143: encode the prompt then map the result", 32), ["round 143: encode the prompt", "then map the result"]),
    (
        ("round 143: the kernel wakes the worker at dawn", 4),
        ["round", "143:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 143: the kernel wakes the worker at dawn", 8),
        ["round", "143: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 143: the kernel wakes the worker at dawn", 12),
        ["round 143:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 143: the kernel wakes the worker at dawn", 16), ["round 143: the", "kernel wakes the", "worker at dawn"]),
    (("round 143: the kernel wakes the worker at dawn", 24), ["round 143: the kernel", "wakes the worker at dawn"]),
    (("round 143: the kernel wakes the worker at dawn", 32), ["round 143: the kernel wakes the", "worker at dawn"]),
    (
        ("round 143: service latency drops after the patch", 4),
        ["round", "143:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 143: service latency drops after the patch", 8),
        ["round", "143:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 143: service latency drops after the patch", 12),
        ["round 143:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 143: service latency drops after the patch", 16),
        ["round 143:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 143: service latency drops after the patch", 24),
        ["round 143: service", "latency drops after the", "patch"],
    ),
    (("round 143: service latency drops after the patch", 32), ["round 143: service latency drops", "after the patch"]),
    (
        ("round 143: the library caches every vector it sees", 4),
        ["round", "143:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 143: the library caches every vector it sees", 8),
        ["round", "143: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 143: the library caches every vector it sees", 12),
        ["round 143:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 143: the library caches every vector it sees", 16),
        ["round 143: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 143: the library caches every vector it sees", 24),
        ["round 143: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 143: the library caches every vector it sees", 32),
        ["round 143: the library caches", "every vector it sees"],
    ),
    (
        ("round 143: agents argue then the debate resolves", 4),
        ["round", "143:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 143: agents argue then the debate resolves", 8),
        ["round", "143:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 143: agents argue then the debate resolves", 12),
        ["round 143:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 143: agents argue then the debate resolves", 16),
        ["round 143:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 143: agents argue then the debate resolves", 24), ["round 143: agents argue", "then the debate resolves"]),
    (("round 143: agents argue then the debate resolves", 32), ["round 143: agents argue then the", "debate resolves"]),
    (
        ("round 143: the filter keeps only strong matches", 4),
        ["round", "143:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 143: the filter keeps only strong matches", 8),
        ["round", "143: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 143: the filter keeps only strong matches", 12),
        ["round 143:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 143: the filter keeps only strong matches", 16),
        ["round 143: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 143: the filter keeps only strong matches", 24),
        ["round 143: the filter", "keeps only strong", "matches"],
    ),
    (("round 143: the filter keeps only strong matches", 32), ["round 143: the filter keeps only", "strong matches"]),
    (
        ("round 143: the model answers with a short reply", 4),
        ["round", "143:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 143: the model answers with a short reply", 8),
        ["round", "143: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 143: the model answers with a short reply", 12),
        ["round 143:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 143: the model answers with a short reply", 16),
        ["round 143: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 143: the model answers with a short reply", 24),
        ["round 143: the model", "answers with a short", "reply"],
    ),
    (("round 143: the model answers with a short reply", 32), ["round 143: the model answers", "with a short reply"]),
    (
        ("round 143: the recorder stores the reasoning trace", 4),
        ["round", "143:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 143: the recorder stores the reasoning trace", 8),
        ["round", "143: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 143: the recorder stores the reasoning trace", 12),
        ["round 143:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 143: the recorder stores the reasoning trace", 16),
        ["round 143: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 143: the recorder stores the reasoning trace", 24),
        ["round 143: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 143: the recorder stores the reasoning trace", 32),
        ["round 143: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 143: the angel watches the processor run", 4),
        ["round", "143:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 143: the angel watches the processor run", 8),
        ["round", "143: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 143: the angel watches the processor run", 12),
        ["round 143:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 143: the angel watches the processor run", 16),
        ["round 143: the", "angel watches", "the processor", "run"],
    ),
    (("round 143: the angel watches the processor run", 24), ["round 143: the angel", "watches the processor", "run"]),
    (("round 143: the angel watches the processor run", 32), ["round 143: the angel watches the", "processor run"]),
    (
        ("round 143: angle of the vector decides the match", 4),
        ["round", "143:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 143: angle of the vector decides the match", 8),
        ["round", "143:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 143: angle of the vector decides the match", 12),
        ["round 143:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 143: angle of the vector decides the match", 16),
        ["round 143: angle", "of the vector", "decides the", "match"],
    ),
    (("round 143: angle of the vector decides the match", 24), ["round 143: angle of the", "vector decides the match"]),
    (("round 143: angle of the vector decides the match", 32), ["round 143: angle of the vector", "decides the match"]),
    (
        ("round 143: the candle burns twice as long at night", 4),
        ["round", "143:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 143: the candle burns twice as long at night", 8),
        ["round", "143: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 143: the candle burns twice as long at night", 12),
        ["round 143:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 143: the candle burns twice as long at night", 16),
        ["round 143: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 143: the candle burns twice as long at night", 24),
        ["round 143: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 143: the candle burns twice as long at night", 32),
        ["round 143: the candle burns", "twice as long at night"],
    ),
    (
        ("round 143: a mirror of the universe in one line", 4),
        ["round", "143:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 143: a mirror of the universe in one line", 8),
        ["round", "143: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 143: a mirror of the universe in one line", 12),
        ["round 143: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 143: a mirror of the universe in one line", 16),
        ["round 143: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 143: a mirror of the universe in one line", 24), ["round 143: a mirror of", "the universe in one line"]),
    (("round 143: a mirror of the universe in one line", 32), ["round 143: a mirror of the", "universe in one line"]),
    (
        ("round 143: the queue drains before the storm", 4),
        ["round", "143:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 143: the queue drains before the storm", 8),
        ["round", "143: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 143: the queue drains before the storm", 12),
        ["round 143:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 143: the queue drains before the storm", 16), ["round 143: the", "queue drains", "before the storm"]),
    (("round 143: the queue drains before the storm", 24), ["round 143: the queue", "drains before the storm"]),
    (("round 143: the queue drains before the storm", 32), ["round 143: the queue drains", "before the storm"]),
    (
        ("kitten143 sitting143 agent143 angle143 universe143 memory143", 6),
        ["kitten143", "sitting143", "agent143", "angle143", "universe143", "memory143"],
    ),
    (
        ("kitten143 sitting143 agent143 angle143 universe143 memory143", 10),
        ["kitten143", "sitting143", "agent143", "angle143", "universe143", "memory143"],
    ),
    (
        ("kitten143 sitting143 agent143 angle143 universe143 memory143", 18),
        ["kitten143", "sitting143", "agent143 angle143", "universe143", "memory143"],
    ),
    (
        ("kitten143 sitting143 agent143 angle143 universe143 memory143", 28),
        ["kitten143 sitting143", "agent143 angle143", "universe143 memory143"],
    ),
    (
        ("sitting143 agent143 angle143 universe143 memory143 stream143", 6),
        ["sitting143", "agent143", "angle143", "universe143", "memory143", "stream143"],
    ),
    (
        ("sitting143 agent143 angle143 universe143 memory143 stream143", 10),
        ["sitting143", "agent143", "angle143", "universe143", "memory143", "stream143"],
    ),
    (
        ("sitting143 agent143 angle143 universe143 memory143 stream143", 18),
        ["sitting143", "agent143 angle143", "universe143", "memory143", "stream143"],
    ),
    (
        ("sitting143 agent143 angle143 universe143 memory143 stream143", 28),
        ["sitting143 agent143 angle143", "universe143 memory143", "stream143"],
    ),
    (
        ("agent143 angle143 universe143 memory143 stream143 context143", 6),
        ["agent143", "angle143", "universe143", "memory143", "stream143", "context143"],
    ),
    (
        ("agent143 angle143 universe143 memory143 stream143 context143", 10),
        ["agent143", "angle143", "universe143", "memory143", "stream143", "context143"],
    ),
    (
        ("agent143 angle143 universe143 memory143 stream143 context143", 18),
        ["agent143 angle143", "universe143", "memory143", "stream143", "context143"],
    ),
    (
        ("agent143 angle143 universe143 memory143 stream143 context143", 28),
        ["agent143 angle143", "universe143 memory143", "stream143 context143"],
    ),
    (
        ("angle143 universe143 memory143 stream143 context143 knowledge143", 6),
        ["angle143", "universe143", "memory143", "stream143", "context143", "knowledge143"],
    ),
    (
        ("angle143 universe143 memory143 stream143 context143 knowledge143", 10),
        ["angle143", "universe143", "memory143", "stream143", "context143", "knowledge143"],
    ),
    (
        ("angle143 universe143 memory143 stream143 context143 knowledge143", 18),
        ["angle143", "universe143", "memory143", "stream143", "context143", "knowledge143"],
    ),
    (
        ("angle143 universe143 memory143 stream143 context143 knowledge143", 28),
        ["angle143 universe143", "memory143 stream143", "context143 knowledge143"],
    ),
    (
        ("universe143 memory143 stream143 context143 knowledge143 vector143", 6),
        ["universe143", "memory143", "stream143", "context143", "knowledge143", "vector143"],
    ),
    (
        ("universe143 memory143 stream143 context143 knowledge143 vector143", 10),
        ["universe143", "memory143", "stream143", "context143", "knowledge143", "vector143"],
    ),
    (
        ("universe143 memory143 stream143 context143 knowledge143 vector143", 18),
        ["universe143", "memory143", "stream143", "context143", "knowledge143", "vector143"],
    ),
    (
        ("universe143 memory143 stream143 context143 knowledge143 vector143", 28),
        ["universe143 memory143", "stream143 context143", "knowledge143 vector143"],
    ),
    (
        ("memory143 stream143 context143 knowledge143 vector143 processor143", 6),
        ["memory143", "stream143", "context143", "knowledge143", "vector143", "processor143"],
    ),
    (
        ("memory143 stream143 context143 knowledge143 vector143 processor143", 10),
        ["memory143", "stream143", "context143", "knowledge143", "vector143", "processor143"],
    ),
    (
        ("memory143 stream143 context143 knowledge143 vector143 processor143", 18),
        ["memory143", "stream143", "context143", "knowledge143", "vector143", "processor143"],
    ),
    (
        ("memory143 stream143 context143 knowledge143 vector143 processor143", 28),
        ["memory143 stream143", "context143 knowledge143", "vector143 processor143"],
    ),
    (
        ("stream143 context143 knowledge143 vector143 processor143 reasoning143", 6),
        ["stream143", "context143", "knowledge143", "vector143", "processor143", "reasoning143"],
    ),
    (
        ("stream143 context143 knowledge143 vector143 processor143 reasoning143", 10),
        ["stream143", "context143", "knowledge143", "vector143", "processor143", "reasoning143"],
    ),
    (
        ("stream143 context143 knowledge143 vector143 processor143 reasoning143", 18),
        ["stream143", "context143", "knowledge143", "vector143", "processor143", "reasoning143"],
    ),
    (
        ("stream143 context143 knowledge143 vector143 processor143 reasoning143", 28),
        ["stream143 context143", "knowledge143 vector143", "processor143 reasoning143"],
    ),
    (
        ("context143 knowledge143 vector143 processor143 reasoning143 machine143", 6),
        ["context143", "knowledge143", "vector143", "processor143", "reasoning143", "machine143"],
    ),
    (
        ("context143 knowledge143 vector143 processor143 reasoning143 machine143", 10),
        ["context143", "knowledge143", "vector143", "processor143", "reasoning143", "machine143"],
    ),
    (
        ("context143 knowledge143 vector143 processor143 reasoning143 machine143", 18),
        ["context143", "knowledge143", "vector143", "processor143", "reasoning143", "machine143"],
    ),
    (
        ("context143 knowledge143 vector143 processor143 reasoning143 machine143", 28),
        ["context143 knowledge143", "vector143 processor143", "reasoning143 machine143"],
    ),
    (
        ("knowledge143 vector143 processor143 reasoning143 machine143 learning143", 6),
        ["knowledge143", "vector143", "processor143", "reasoning143", "machine143", "learning143"],
    ),
    (
        ("knowledge143 vector143 processor143 reasoning143 machine143 learning143", 10),
        ["knowledge143", "vector143", "processor143", "reasoning143", "machine143", "learning143"],
    ),
    (
        ("knowledge143 vector143 processor143 reasoning143 machine143 learning143", 18),
        ["knowledge143", "vector143", "processor143", "reasoning143", "machine143", "learning143"],
    ),
    (
        ("knowledge143 vector143 processor143 reasoning143 machine143 learning143", 28),
        ["knowledge143 vector143", "processor143 reasoning143", "machine143 learning143"],
    ),
    (
        ("vector143 processor143 reasoning143 machine143 learning143 model143", 6),
        ["vector143", "processor143", "reasoning143", "machine143", "learning143", "model143"],
    ),
    (
        ("vector143 processor143 reasoning143 machine143 learning143 model143", 10),
        ["vector143", "processor143", "reasoning143", "machine143", "learning143", "model143"],
    ),
    (
        ("vector143 processor143 reasoning143 machine143 learning143 model143", 18),
        ["vector143", "processor143", "reasoning143", "machine143", "learning143", "model143"],
    ),
    (
        ("vector143 processor143 reasoning143 machine143 learning143 model143", 28),
        ["vector143 processor143", "reasoning143 machine143", "learning143 model143"],
    ),
    (
        ("processor143 reasoning143 machine143 learning143 model143 token143", 6),
        ["processor143", "reasoning143", "machine143", "learning143", "model143", "token143"],
    ),
    (
        ("processor143 reasoning143 machine143 learning143 model143 token143", 10),
        ["processor143", "reasoning143", "machine143", "learning143", "model143", "token143"],
    ),
    (
        ("processor143 reasoning143 machine143 learning143 model143 token143", 18),
        ["processor143", "reasoning143", "machine143", "learning143", "model143 token143"],
    ),
    (
        ("processor143 reasoning143 machine143 learning143 model143 token143", 28),
        ["processor143 reasoning143", "machine143 learning143", "model143 token143"],
    ),
    (
        ("reasoning143 machine143 learning143 model143 token143 prompt143", 6),
        ["reasoning143", "machine143", "learning143", "model143", "token143", "prompt143"],
    ),
    (
        ("reasoning143 machine143 learning143 model143 token143 prompt143", 10),
        ["reasoning143", "machine143", "learning143", "model143", "token143", "prompt143"],
    ),
    (
        ("reasoning143 machine143 learning143 model143 token143 prompt143", 18),
        ["reasoning143", "machine143", "learning143", "model143 token143", "prompt143"],
    ),
    (
        ("reasoning143 machine143 learning143 model143 token143 prompt143", 28),
        ["reasoning143 machine143", "learning143 model143", "token143 prompt143"],
    ),
    (
        ("machine143 learning143 model143 token143 prompt143 session143", 6),
        ["machine143", "learning143", "model143", "token143", "prompt143", "session143"],
    ),
    (
        ("machine143 learning143 model143 token143 prompt143 session143", 10),
        ["machine143", "learning143", "model143", "token143", "prompt143", "session143"],
    ),
    (
        ("machine143 learning143 model143 token143 prompt143 session143", 18),
        ["machine143", "learning143", "model143 token143", "prompt143", "session143"],
    ),
    (
        ("machine143 learning143 model143 token143 prompt143 session143", 28),
        ["machine143 learning143", "model143 token143 prompt143", "session143"],
    ),
    (
        ("learning143 model143 token143 prompt143 session143 library143", 6),
        ["learning143", "model143", "token143", "prompt143", "session143", "library143"],
    ),
    (
        ("learning143 model143 token143 prompt143 session143 library143", 10),
        ["learning143", "model143", "token143", "prompt143", "session143", "library143"],
    ),
    (
        ("learning143 model143 token143 prompt143 session143 library143", 18),
        ["learning143", "model143 token143", "prompt143", "session143", "library143"],
    ),
    (
        ("learning143 model143 token143 prompt143 session143 library143", 28),
        ["learning143 model143", "token143 prompt143", "session143 library143"],
    ),
    (
        ("model143 token143 prompt143 session143 library143 service143", 6),
        ["model143", "token143", "prompt143", "session143", "library143", "service143"],
    ),
    (
        ("model143 token143 prompt143 session143 library143 service143", 10),
        ["model143", "token143", "prompt143", "session143", "library143", "service143"],
    ),
    (
        ("model143 token143 prompt143 session143 library143 service143", 18),
        ["model143 token143", "prompt143", "session143", "library143", "service143"],
    ),
    (
        ("model143 token143 prompt143 session143 library143 service143", 28),
        ["model143 token143 prompt143", "session143 library143", "service143"],
    ),
    (
        ("token143 prompt143 session143 library143 service143 gateway143", 6),
        ["token143", "prompt143", "session143", "library143", "service143", "gateway143"],
    ),
    (
        ("token143 prompt143 session143 library143 service143 gateway143", 10),
        ["token143", "prompt143", "session143", "library143", "service143", "gateway143"],
    ),
    (
        ("token143 prompt143 session143 library143 service143 gateway143", 18),
        ["token143 prompt143", "session143", "library143", "service143", "gateway143"],
    ),
    (
        ("token143 prompt143 session143 library143 service143 gateway143", 28),
        ["token143 prompt143", "session143 library143", "service143 gateway143"],
    ),
    (
        ("prompt143 session143 library143 service143 gateway143 storage143", 6),
        ["prompt143", "session143", "library143", "service143", "gateway143", "storage143"],
    ),
    (
        ("prompt143 session143 library143 service143 gateway143 storage143", 10),
        ["prompt143", "session143", "library143", "service143", "gateway143", "storage143"],
    ),
    (
        ("prompt143 session143 library143 service143 gateway143 storage143", 18),
        ["prompt143", "session143", "library143", "service143", "gateway143", "storage143"],
    ),
    (
        ("prompt143 session143 library143 service143 gateway143 storage143", 28),
        ["prompt143 session143", "library143 service143", "gateway143 storage143"],
    ),
    (
        ("session143 library143 service143 gateway143 storage143 network143", 6),
        ["session143", "library143", "service143", "gateway143", "storage143", "network143"],
    ),
    (
        ("session143 library143 service143 gateway143 storage143 network143", 10),
        ["session143", "library143", "service143", "gateway143", "storage143", "network143"],
    ),
    (
        ("session143 library143 service143 gateway143 storage143 network143", 18),
        ["session143", "library143", "service143", "gateway143", "storage143", "network143"],
    ),
    (
        ("session143 library143 service143 gateway143 storage143 network143", 28),
        ["session143 library143", "service143 gateway143", "storage143 network143"],
    ),
    (
        ("library143 service143 gateway143 storage143 network143 latency143", 6),
        ["library143", "service143", "gateway143", "storage143", "network143", "latency143"],
    ),
    (
        ("library143 service143 gateway143 storage143 network143 latency143", 10),
        ["library143", "service143", "gateway143", "storage143", "network143", "latency143"],
    ),
    (
        ("library143 service143 gateway143 storage143 network143 latency143", 18),
        ["library143", "service143", "gateway143", "storage143", "network143", "latency143"],
    ),
    (
        ("library143 service143 gateway143 storage143 network143 latency143", 28),
        ["library143 service143", "gateway143 storage143", "network143 latency143"],
    ),
    (
        ("service143 gateway143 storage143 network143 latency143 buffer143", 6),
        ["service143", "gateway143", "storage143", "network143", "latency143", "buffer143"],
    ),
    (
        ("service143 gateway143 storage143 network143 latency143 buffer143", 10),
        ["service143", "gateway143", "storage143", "network143", "latency143", "buffer143"],
    ),
    (
        ("service143 gateway143 storage143 network143 latency143 buffer143", 18),
        ["service143", "gateway143", "storage143", "network143", "latency143", "buffer143"],
    ),
    (
        ("service143 gateway143 storage143 network143 latency143 buffer143", 28),
        ["service143 gateway143", "storage143 network143", "latency143 buffer143"],
    ),
    (
        ("gateway143 storage143 network143 latency143 buffer143 queue143", 6),
        ["gateway143", "storage143", "network143", "latency143", "buffer143", "queue143"],
    ),
    (
        ("gateway143 storage143 network143 latency143 buffer143 queue143", 10),
        ["gateway143", "storage143", "network143", "latency143", "buffer143", "queue143"],
    ),
    (
        ("gateway143 storage143 network143 latency143 buffer143 queue143", 18),
        ["gateway143", "storage143", "network143", "latency143", "buffer143 queue143"],
    ),
    (
        ("gateway143 storage143 network143 latency143 buffer143 queue143", 28),
        ["gateway143 storage143", "network143 latency143", "buffer143 queue143"],
    ),
    (
        ("storage143 network143 latency143 buffer143 queue143 worker143", 6),
        ["storage143", "network143", "latency143", "buffer143", "queue143", "worker143"],
    ),
    (
        ("storage143 network143 latency143 buffer143 queue143 worker143", 10),
        ["storage143", "network143", "latency143", "buffer143", "queue143", "worker143"],
    ),
    (
        ("storage143 network143 latency143 buffer143 queue143 worker143", 18),
        ["storage143", "network143", "latency143", "buffer143 queue143", "worker143"],
    ),
    (
        ("storage143 network143 latency143 buffer143 queue143 worker143", 28),
        ["storage143 network143", "latency143 buffer143", "queue143 worker143"],
    ),
    (
        ("network143 latency143 buffer143 queue143 worker143 kernel143", 6),
        ["network143", "latency143", "buffer143", "queue143", "worker143", "kernel143"],
    ),
    (
        ("network143 latency143 buffer143 queue143 worker143 kernel143", 10),
        ["network143", "latency143", "buffer143", "queue143", "worker143", "kernel143"],
    ),
    (
        ("network143 latency143 buffer143 queue143 worker143 kernel143", 18),
        ["network143", "latency143", "buffer143 queue143", "worker143", "kernel143"],
    ),
    (
        ("network143 latency143 buffer143 queue143 worker143 kernel143", 28),
        ["network143 latency143", "buffer143 queue143 worker143", "kernel143"],
    ),
    (
        ("latency143 buffer143 queue143 worker143 kernel143 signal143", 6),
        ["latency143", "buffer143", "queue143", "worker143", "kernel143", "signal143"],
    ),
    (
        ("latency143 buffer143 queue143 worker143 kernel143 signal143", 10),
        ["latency143", "buffer143", "queue143", "worker143", "kernel143", "signal143"],
    ),
    (
        ("latency143 buffer143 queue143 worker143 kernel143 signal143", 18),
        ["latency143", "buffer143 queue143", "worker143", "kernel143", "signal143"],
    ),
    (
        ("latency143 buffer143 queue143 worker143 kernel143 signal143", 28),
        ["latency143 buffer143", "queue143 worker143 kernel143", "signal143"],
    ),
    (
        ("buffer143 queue143 worker143 kernel143 signal143 packet143", 6),
        ["buffer143", "queue143", "worker143", "kernel143", "signal143", "packet143"],
    ),
    (
        ("buffer143 queue143 worker143 kernel143 signal143 packet143", 10),
        ["buffer143", "queue143", "worker143", "kernel143", "signal143", "packet143"],
    ),
    (
        ("buffer143 queue143 worker143 kernel143 signal143 packet143", 18),
        ["buffer143 queue143", "worker143", "kernel143", "signal143", "packet143"],
    ),
    (
        ("buffer143 queue143 worker143 kernel143 signal143 packet143", 28),
        ["buffer143 queue143 worker143", "kernel143 signal143", "packet143"],
    ),
    (
        ("queue143 worker143 kernel143 signal143 packet143 router143", 6),
        ["queue143", "worker143", "kernel143", "signal143", "packet143", "router143"],
    ),
    (
        ("queue143 worker143 kernel143 signal143 packet143 router143", 10),
        ["queue143", "worker143", "kernel143", "signal143", "packet143", "router143"],
    ),
    (
        ("queue143 worker143 kernel143 signal143 packet143 router143", 18),
        ["queue143 worker143", "kernel143", "signal143", "packet143", "router143"],
    ),
    (
        ("queue143 worker143 kernel143 signal143 packet143 router143", 28),
        ["queue143 worker143 kernel143", "signal143 packet143", "router143"],
    ),
    (
        ("worker143 kernel143 signal143 packet143 router143 cluster143", 6),
        ["worker143", "kernel143", "signal143", "packet143", "router143", "cluster143"],
    ),
    (
        ("worker143 kernel143 signal143 packet143 router143 cluster143", 10),
        ["worker143", "kernel143", "signal143", "packet143", "router143", "cluster143"],
    ),
    (
        ("worker143 kernel143 signal143 packet143 router143 cluster143", 18),
        ["worker143", "kernel143", "signal143", "packet143", "router143", "cluster143"],
    ),
    (
        ("worker143 kernel143 signal143 packet143 router143 cluster143", 28),
        ["worker143 kernel143", "signal143 packet143", "router143 cluster143"],
    ),
    (
        ("kernel143 signal143 packet143 router143 cluster143 mirror143", 6),
        ["kernel143", "signal143", "packet143", "router143", "cluster143", "mirror143"],
    ),
    (
        ("kernel143 signal143 packet143 router143 cluster143 mirror143", 10),
        ["kernel143", "signal143", "packet143", "router143", "cluster143", "mirror143"],
    ),
    (
        ("kernel143 signal143 packet143 router143 cluster143 mirror143", 18),
        ["kernel143", "signal143", "packet143", "router143", "cluster143", "mirror143"],
    ),
    (
        ("kernel143 signal143 packet143 router143 cluster143 mirror143", 28),
        ["kernel143 signal143", "packet143 router143", "cluster143 mirror143"],
    ),
    (
        ("signal143 packet143 router143 cluster143 mirror143 filter143", 6),
        ["signal143", "packet143", "router143", "cluster143", "mirror143", "filter143"],
    ),
    (
        ("signal143 packet143 router143 cluster143 mirror143 filter143", 10),
        ["signal143", "packet143", "router143", "cluster143", "mirror143", "filter143"],
    ),
    (
        ("signal143 packet143 router143 cluster143 mirror143 filter143", 18),
        ["signal143", "packet143", "router143", "cluster143", "mirror143", "filter143"],
    ),
    (
        ("signal143 packet143 router143 cluster143 mirror143 filter143", 28),
        ["signal143 packet143", "router143 cluster143", "mirror143 filter143"],
    ),
    (
        ("packet143 router143 cluster143 mirror143 filter143 ranking143", 6),
        ["packet143", "router143", "cluster143", "mirror143", "filter143", "ranking143"],
    ),
    (
        ("packet143 router143 cluster143 mirror143 filter143 ranking143", 10),
        ["packet143", "router143", "cluster143", "mirror143", "filter143", "ranking143"],
    ),
    (
        ("packet143 router143 cluster143 mirror143 filter143 ranking143", 18),
        ["packet143", "router143", "cluster143", "mirror143", "filter143", "ranking143"],
    ),
    (
        ("packet143 router143 cluster143 mirror143 filter143 ranking143", 28),
        ["packet143 router143", "cluster143 mirror143", "filter143 ranking143"],
    ),
    (
        ("router143 cluster143 mirror143 filter143 ranking143 encoding143", 6),
        ["router143", "cluster143", "mirror143", "filter143", "ranking143", "encoding143"],
    ),
    (
        ("router143 cluster143 mirror143 filter143 ranking143 encoding143", 10),
        ["router143", "cluster143", "mirror143", "filter143", "ranking143", "encoding143"],
    ),
    (
        ("router143 cluster143 mirror143 filter143 ranking143 encoding143", 18),
        ["router143", "cluster143", "mirror143", "filter143", "ranking143", "encoding143"],
    ),
    (
        ("router143 cluster143 mirror143 filter143 ranking143 encoding143", 28),
        ["router143 cluster143", "mirror143 filter143", "ranking143 encoding143"],
    ),
    (
        ("cluster143 mirror143 filter143 ranking143 encoding143 mapping143", 6),
        ["cluster143", "mirror143", "filter143", "ranking143", "encoding143", "mapping143"],
    ),
    (
        ("cluster143 mirror143 filter143 ranking143 encoding143 mapping143", 10),
        ["cluster143", "mirror143", "filter143", "ranking143", "encoding143", "mapping143"],
    ),
    (
        ("cluster143 mirror143 filter143 ranking143 encoding143 mapping143", 18),
        ["cluster143", "mirror143", "filter143", "ranking143", "encoding143", "mapping143"],
    ),
    (
        ("cluster143 mirror143 filter143 ranking143 encoding143 mapping143", 28),
        ["cluster143 mirror143", "filter143 ranking143", "encoding143 mapping143"],
    ),
    (
        ("mirror143 filter143 ranking143 encoding143 mapping143 record143", 6),
        ["mirror143", "filter143", "ranking143", "encoding143", "mapping143", "record143"],
    ),
    (
        ("mirror143 filter143 ranking143 encoding143 mapping143 record143", 10),
        ["mirror143", "filter143", "ranking143", "encoding143", "mapping143", "record143"],
    ),
    (
        ("mirror143 filter143 ranking143 encoding143 mapping143 record143", 18),
        ["mirror143", "filter143", "ranking143", "encoding143", "mapping143", "record143"],
    ),
    (
        ("mirror143 filter143 ranking143 encoding143 mapping143 record143", 28),
        ["mirror143 filter143", "ranking143 encoding143", "mapping143 record143"],
    ),
    (
        ("filter143 ranking143 encoding143 mapping143 record143 candle143", 6),
        ["filter143", "ranking143", "encoding143", "mapping143", "record143", "candle143"],
    ),
    (
        ("filter143 ranking143 encoding143 mapping143 record143 candle143", 10),
        ["filter143", "ranking143", "encoding143", "mapping143", "record143", "candle143"],
    ),
    (
        ("filter143 ranking143 encoding143 mapping143 record143 candle143", 18),
        ["filter143", "ranking143", "encoding143", "mapping143", "record143", "candle143"],
    ),
    (
        ("filter143 ranking143 encoding143 mapping143 record143 candle143", 28),
        ["filter143 ranking143", "encoding143 mapping143", "record143 candle143"],
    ),
    (
        ("ranking143 encoding143 mapping143 record143 candle143 thread143", 6),
        ["ranking143", "encoding143", "mapping143", "record143", "candle143", "thread143"],
    ),
    (
        ("ranking143 encoding143 mapping143 record143 candle143 thread143", 10),
        ["ranking143", "encoding143", "mapping143", "record143", "candle143", "thread143"],
    ),
    (
        ("ranking143 encoding143 mapping143 record143 candle143 thread143", 18),
        ["ranking143", "encoding143", "mapping143", "record143", "candle143", "thread143"],
    ),
    (
        ("ranking143 encoding143 mapping143 record143 candle143 thread143", 28),
        ["ranking143 encoding143", "mapping143 record143", "candle143 thread143"],
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
