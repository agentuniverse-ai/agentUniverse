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
        ("round 146: the quick brown fox jumps over the lazy dog", 4),
        ["round", "146:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 146: the quick brown fox jumps over the lazy dog", 8),
        ["round", "146: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 146: the quick brown fox jumps over the lazy dog", 12),
        ["round 146:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 146: the quick brown fox jumps over the lazy dog", 16),
        ["round 146: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 146: the quick brown fox jumps over the lazy dog", 24),
        ["round 146: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 146: the quick brown fox jumps over the lazy dog", 32),
        ["round 146: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 146: agentuniverse is a framework for multi agents", 4),
        ["round", "146:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 146: agentuniverse is a framework for multi agents", 8),
        ["round", "146:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 146: agentuniverse is a framework for multi agents", 12),
        ["round 146:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 146: agentuniverse is a framework for multi agents", 16),
        ["round 146:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 146: agentuniverse is a framework for multi agents", 24),
        ["round 146: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 146: agentuniverse is a framework for multi agents", 32),
        ["round 146: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 146: knowledge stored as vectors enables retrieval", 4),
        ["round", "146:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 146: knowledge stored as vectors enables retrieval", 8),
        ["round", "146:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 146: knowledge stored as vectors enables retrieval", 12),
        ["round 146:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 146: knowledge stored as vectors enables retrieval", 16),
        ["round 146:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 146: knowledge stored as vectors enables retrieval", 24),
        ["round 146: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 146: knowledge stored as vectors enables retrieval", 32),
        ["round 146: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 146: the processor reads the record then stops", 4),
        ["round", "146:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 146: the processor reads the record then stops", 8),
        ["round", "146: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 146: the processor reads the record then stops", 12),
        ["round 146:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 146: the processor reads the record then stops", 16),
        ["round 146: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 146: the processor reads the record then stops", 24),
        ["round 146: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 146: the processor reads the record then stops", 32),
        ["round 146: the processor reads", "the record then stops"],
    ),
    (
        ("round 146: a worker pulls the next task from the queue", 4),
        ["round", "146:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 146: a worker pulls the next task from the queue", 8),
        ["round", "146: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 146: a worker pulls the next task from the queue", 12),
        ["round 146: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 146: a worker pulls the next task from the queue", 16),
        ["round 146: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 146: a worker pulls the next task from the queue", 24),
        ["round 146: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 146: a worker pulls the next task from the queue", 32),
        ["round 146: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 146: signals travel through the network layer", 4),
        ["round", "146:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 146: signals travel through the network layer", 8),
        ["round", "146:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 146: signals travel through the network layer", 12),
        ["round 146:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 146: signals travel through the network layer", 16),
        ["round 146:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 146: signals travel through the network layer", 24),
        ["round 146: signals", "travel through the", "network layer"],
    ),
    (
        ("round 146: signals travel through the network layer", 32),
        ["round 146: signals travel", "through the network layer"],
    ),
    (
        ("round 146: the gateway routes each request by policy", 4),
        ["round", "146:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 146: the gateway routes each request by policy", 8),
        ["round", "146: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 146: the gateway routes each request by policy", 12),
        ["round 146:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 146: the gateway routes each request by policy", 16),
        ["round 146: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 146: the gateway routes each request by policy", 24),
        ["round 146: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 146: the gateway routes each request by policy", 32),
        ["round 146: the gateway routes", "each request by policy"],
    ),
    (
        ("round 146: memory grows until the buffer is full", 4),
        ["round", "146:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 146: memory grows until the buffer is full", 8),
        ["round", "146:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 146: memory grows until the buffer is full", 12),
        ["round 146:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 146: memory grows until the buffer is full", 16),
        ["round 146:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 146: memory grows until the buffer is full", 24), ["round 146: memory grows", "until the buffer is full"]),
    (("round 146: memory grows until the buffer is full", 32), ["round 146: memory grows until", "the buffer is full"]),
    (
        ("round 146: the cluster mirrors every packet twice", 4),
        ["round", "146:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 146: the cluster mirrors every packet twice", 8),
        ["round", "146: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 146: the cluster mirrors every packet twice", 12),
        ["round 146:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 146: the cluster mirrors every packet twice", 16),
        ["round 146: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 146: the cluster mirrors every packet twice", 24),
        ["round 146: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 146: the cluster mirrors every packet twice", 32),
        ["round 146: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 146: ranking uses tokens learned from the corpus", 4),
        ["round", "146:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 146: ranking uses tokens learned from the corpus", 8),
        ["round", "146:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 146: ranking uses tokens learned from the corpus", 12),
        ["round 146:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 146: ranking uses tokens learned from the corpus", 16),
        ["round 146:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 146: ranking uses tokens learned from the corpus", 24),
        ["round 146: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 146: ranking uses tokens learned from the corpus", 32),
        ["round 146: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 146: a long session ends when the candle dies", 4),
        ["round", "146:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 146: a long session ends when the candle dies", 8),
        ["round", "146: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 146: a long session ends when the candle dies", 12),
        ["round 146: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 146: a long session ends when the candle dies", 16),
        ["round 146: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 146: a long session ends when the candle dies", 24),
        ["round 146: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 146: a long session ends when the candle dies", 32),
        ["round 146: a long session ends", "when the candle dies"],
    ),
    (
        ("round 146: encode the prompt then map the result", 4),
        ["round", "146:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 146: encode the prompt then map the result", 8),
        ["round", "146:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 146: encode the prompt then map the result", 12),
        ["round 146:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 146: encode the prompt then map the result", 16),
        ["round 146:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 146: encode the prompt then map the result", 24),
        ["round 146: encode the", "prompt then map the", "result"],
    ),
    (("round 146: encode the prompt then map the result", 32), ["round 146: encode the prompt", "then map the result"]),
    (
        ("round 146: the kernel wakes the worker at dawn", 4),
        ["round", "146:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 146: the kernel wakes the worker at dawn", 8),
        ["round", "146: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 146: the kernel wakes the worker at dawn", 12),
        ["round 146:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 146: the kernel wakes the worker at dawn", 16), ["round 146: the", "kernel wakes the", "worker at dawn"]),
    (("round 146: the kernel wakes the worker at dawn", 24), ["round 146: the kernel", "wakes the worker at dawn"]),
    (("round 146: the kernel wakes the worker at dawn", 32), ["round 146: the kernel wakes the", "worker at dawn"]),
    (
        ("round 146: service latency drops after the patch", 4),
        ["round", "146:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 146: service latency drops after the patch", 8),
        ["round", "146:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 146: service latency drops after the patch", 12),
        ["round 146:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 146: service latency drops after the patch", 16),
        ["round 146:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 146: service latency drops after the patch", 24),
        ["round 146: service", "latency drops after the", "patch"],
    ),
    (("round 146: service latency drops after the patch", 32), ["round 146: service latency drops", "after the patch"]),
    (
        ("round 146: the library caches every vector it sees", 4),
        ["round", "146:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 146: the library caches every vector it sees", 8),
        ["round", "146: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 146: the library caches every vector it sees", 12),
        ["round 146:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 146: the library caches every vector it sees", 16),
        ["round 146: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 146: the library caches every vector it sees", 24),
        ["round 146: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 146: the library caches every vector it sees", 32),
        ["round 146: the library caches", "every vector it sees"],
    ),
    (
        ("round 146: agents argue then the debate resolves", 4),
        ["round", "146:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 146: agents argue then the debate resolves", 8),
        ["round", "146:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 146: agents argue then the debate resolves", 12),
        ["round 146:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 146: agents argue then the debate resolves", 16),
        ["round 146:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 146: agents argue then the debate resolves", 24), ["round 146: agents argue", "then the debate resolves"]),
    (("round 146: agents argue then the debate resolves", 32), ["round 146: agents argue then the", "debate resolves"]),
    (
        ("round 146: the filter keeps only strong matches", 4),
        ["round", "146:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 146: the filter keeps only strong matches", 8),
        ["round", "146: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 146: the filter keeps only strong matches", 12),
        ["round 146:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 146: the filter keeps only strong matches", 16),
        ["round 146: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 146: the filter keeps only strong matches", 24),
        ["round 146: the filter", "keeps only strong", "matches"],
    ),
    (("round 146: the filter keeps only strong matches", 32), ["round 146: the filter keeps only", "strong matches"]),
    (
        ("round 146: the model answers with a short reply", 4),
        ["round", "146:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 146: the model answers with a short reply", 8),
        ["round", "146: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 146: the model answers with a short reply", 12),
        ["round 146:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 146: the model answers with a short reply", 16),
        ["round 146: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 146: the model answers with a short reply", 24),
        ["round 146: the model", "answers with a short", "reply"],
    ),
    (("round 146: the model answers with a short reply", 32), ["round 146: the model answers", "with a short reply"]),
    (
        ("round 146: the recorder stores the reasoning trace", 4),
        ["round", "146:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 146: the recorder stores the reasoning trace", 8),
        ["round", "146: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 146: the recorder stores the reasoning trace", 12),
        ["round 146:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 146: the recorder stores the reasoning trace", 16),
        ["round 146: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 146: the recorder stores the reasoning trace", 24),
        ["round 146: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 146: the recorder stores the reasoning trace", 32),
        ["round 146: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 146: the angel watches the processor run", 4),
        ["round", "146:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 146: the angel watches the processor run", 8),
        ["round", "146: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 146: the angel watches the processor run", 12),
        ["round 146:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 146: the angel watches the processor run", 16),
        ["round 146: the", "angel watches", "the processor", "run"],
    ),
    (("round 146: the angel watches the processor run", 24), ["round 146: the angel", "watches the processor", "run"]),
    (("round 146: the angel watches the processor run", 32), ["round 146: the angel watches the", "processor run"]),
    (
        ("round 146: angle of the vector decides the match", 4),
        ["round", "146:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 146: angle of the vector decides the match", 8),
        ["round", "146:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 146: angle of the vector decides the match", 12),
        ["round 146:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 146: angle of the vector decides the match", 16),
        ["round 146: angle", "of the vector", "decides the", "match"],
    ),
    (("round 146: angle of the vector decides the match", 24), ["round 146: angle of the", "vector decides the match"]),
    (("round 146: angle of the vector decides the match", 32), ["round 146: angle of the vector", "decides the match"]),
    (
        ("round 146: the candle burns twice as long at night", 4),
        ["round", "146:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 146: the candle burns twice as long at night", 8),
        ["round", "146: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 146: the candle burns twice as long at night", 12),
        ["round 146:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 146: the candle burns twice as long at night", 16),
        ["round 146: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 146: the candle burns twice as long at night", 24),
        ["round 146: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 146: the candle burns twice as long at night", 32),
        ["round 146: the candle burns", "twice as long at night"],
    ),
    (
        ("round 146: a mirror of the universe in one line", 4),
        ["round", "146:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 146: a mirror of the universe in one line", 8),
        ["round", "146: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 146: a mirror of the universe in one line", 12),
        ["round 146: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 146: a mirror of the universe in one line", 16),
        ["round 146: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 146: a mirror of the universe in one line", 24), ["round 146: a mirror of", "the universe in one line"]),
    (("round 146: a mirror of the universe in one line", 32), ["round 146: a mirror of the", "universe in one line"]),
    (
        ("round 146: the queue drains before the storm", 4),
        ["round", "146:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 146: the queue drains before the storm", 8),
        ["round", "146: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 146: the queue drains before the storm", 12),
        ["round 146:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 146: the queue drains before the storm", 16), ["round 146: the", "queue drains", "before the storm"]),
    (("round 146: the queue drains before the storm", 24), ["round 146: the queue", "drains before the storm"]),
    (("round 146: the queue drains before the storm", 32), ["round 146: the queue drains", "before the storm"]),
    (
        ("kitten146 sitting146 agent146 angle146 universe146 memory146", 6),
        ["kitten146", "sitting146", "agent146", "angle146", "universe146", "memory146"],
    ),
    (
        ("kitten146 sitting146 agent146 angle146 universe146 memory146", 10),
        ["kitten146", "sitting146", "agent146", "angle146", "universe146", "memory146"],
    ),
    (
        ("kitten146 sitting146 agent146 angle146 universe146 memory146", 18),
        ["kitten146", "sitting146", "agent146 angle146", "universe146", "memory146"],
    ),
    (
        ("kitten146 sitting146 agent146 angle146 universe146 memory146", 28),
        ["kitten146 sitting146", "agent146 angle146", "universe146 memory146"],
    ),
    (
        ("sitting146 agent146 angle146 universe146 memory146 stream146", 6),
        ["sitting146", "agent146", "angle146", "universe146", "memory146", "stream146"],
    ),
    (
        ("sitting146 agent146 angle146 universe146 memory146 stream146", 10),
        ["sitting146", "agent146", "angle146", "universe146", "memory146", "stream146"],
    ),
    (
        ("sitting146 agent146 angle146 universe146 memory146 stream146", 18),
        ["sitting146", "agent146 angle146", "universe146", "memory146", "stream146"],
    ),
    (
        ("sitting146 agent146 angle146 universe146 memory146 stream146", 28),
        ["sitting146 agent146 angle146", "universe146 memory146", "stream146"],
    ),
    (
        ("agent146 angle146 universe146 memory146 stream146 context146", 6),
        ["agent146", "angle146", "universe146", "memory146", "stream146", "context146"],
    ),
    (
        ("agent146 angle146 universe146 memory146 stream146 context146", 10),
        ["agent146", "angle146", "universe146", "memory146", "stream146", "context146"],
    ),
    (
        ("agent146 angle146 universe146 memory146 stream146 context146", 18),
        ["agent146 angle146", "universe146", "memory146", "stream146", "context146"],
    ),
    (
        ("agent146 angle146 universe146 memory146 stream146 context146", 28),
        ["agent146 angle146", "universe146 memory146", "stream146 context146"],
    ),
    (
        ("angle146 universe146 memory146 stream146 context146 knowledge146", 6),
        ["angle146", "universe146", "memory146", "stream146", "context146", "knowledge146"],
    ),
    (
        ("angle146 universe146 memory146 stream146 context146 knowledge146", 10),
        ["angle146", "universe146", "memory146", "stream146", "context146", "knowledge146"],
    ),
    (
        ("angle146 universe146 memory146 stream146 context146 knowledge146", 18),
        ["angle146", "universe146", "memory146", "stream146", "context146", "knowledge146"],
    ),
    (
        ("angle146 universe146 memory146 stream146 context146 knowledge146", 28),
        ["angle146 universe146", "memory146 stream146", "context146 knowledge146"],
    ),
    (
        ("universe146 memory146 stream146 context146 knowledge146 vector146", 6),
        ["universe146", "memory146", "stream146", "context146", "knowledge146", "vector146"],
    ),
    (
        ("universe146 memory146 stream146 context146 knowledge146 vector146", 10),
        ["universe146", "memory146", "stream146", "context146", "knowledge146", "vector146"],
    ),
    (
        ("universe146 memory146 stream146 context146 knowledge146 vector146", 18),
        ["universe146", "memory146", "stream146", "context146", "knowledge146", "vector146"],
    ),
    (
        ("universe146 memory146 stream146 context146 knowledge146 vector146", 28),
        ["universe146 memory146", "stream146 context146", "knowledge146 vector146"],
    ),
    (
        ("memory146 stream146 context146 knowledge146 vector146 processor146", 6),
        ["memory146", "stream146", "context146", "knowledge146", "vector146", "processor146"],
    ),
    (
        ("memory146 stream146 context146 knowledge146 vector146 processor146", 10),
        ["memory146", "stream146", "context146", "knowledge146", "vector146", "processor146"],
    ),
    (
        ("memory146 stream146 context146 knowledge146 vector146 processor146", 18),
        ["memory146", "stream146", "context146", "knowledge146", "vector146", "processor146"],
    ),
    (
        ("memory146 stream146 context146 knowledge146 vector146 processor146", 28),
        ["memory146 stream146", "context146 knowledge146", "vector146 processor146"],
    ),
    (
        ("stream146 context146 knowledge146 vector146 processor146 reasoning146", 6),
        ["stream146", "context146", "knowledge146", "vector146", "processor146", "reasoning146"],
    ),
    (
        ("stream146 context146 knowledge146 vector146 processor146 reasoning146", 10),
        ["stream146", "context146", "knowledge146", "vector146", "processor146", "reasoning146"],
    ),
    (
        ("stream146 context146 knowledge146 vector146 processor146 reasoning146", 18),
        ["stream146", "context146", "knowledge146", "vector146", "processor146", "reasoning146"],
    ),
    (
        ("stream146 context146 knowledge146 vector146 processor146 reasoning146", 28),
        ["stream146 context146", "knowledge146 vector146", "processor146 reasoning146"],
    ),
    (
        ("context146 knowledge146 vector146 processor146 reasoning146 machine146", 6),
        ["context146", "knowledge146", "vector146", "processor146", "reasoning146", "machine146"],
    ),
    (
        ("context146 knowledge146 vector146 processor146 reasoning146 machine146", 10),
        ["context146", "knowledge146", "vector146", "processor146", "reasoning146", "machine146"],
    ),
    (
        ("context146 knowledge146 vector146 processor146 reasoning146 machine146", 18),
        ["context146", "knowledge146", "vector146", "processor146", "reasoning146", "machine146"],
    ),
    (
        ("context146 knowledge146 vector146 processor146 reasoning146 machine146", 28),
        ["context146 knowledge146", "vector146 processor146", "reasoning146 machine146"],
    ),
    (
        ("knowledge146 vector146 processor146 reasoning146 machine146 learning146", 6),
        ["knowledge146", "vector146", "processor146", "reasoning146", "machine146", "learning146"],
    ),
    (
        ("knowledge146 vector146 processor146 reasoning146 machine146 learning146", 10),
        ["knowledge146", "vector146", "processor146", "reasoning146", "machine146", "learning146"],
    ),
    (
        ("knowledge146 vector146 processor146 reasoning146 machine146 learning146", 18),
        ["knowledge146", "vector146", "processor146", "reasoning146", "machine146", "learning146"],
    ),
    (
        ("knowledge146 vector146 processor146 reasoning146 machine146 learning146", 28),
        ["knowledge146 vector146", "processor146 reasoning146", "machine146 learning146"],
    ),
    (
        ("vector146 processor146 reasoning146 machine146 learning146 model146", 6),
        ["vector146", "processor146", "reasoning146", "machine146", "learning146", "model146"],
    ),
    (
        ("vector146 processor146 reasoning146 machine146 learning146 model146", 10),
        ["vector146", "processor146", "reasoning146", "machine146", "learning146", "model146"],
    ),
    (
        ("vector146 processor146 reasoning146 machine146 learning146 model146", 18),
        ["vector146", "processor146", "reasoning146", "machine146", "learning146", "model146"],
    ),
    (
        ("vector146 processor146 reasoning146 machine146 learning146 model146", 28),
        ["vector146 processor146", "reasoning146 machine146", "learning146 model146"],
    ),
    (
        ("processor146 reasoning146 machine146 learning146 model146 token146", 6),
        ["processor146", "reasoning146", "machine146", "learning146", "model146", "token146"],
    ),
    (
        ("processor146 reasoning146 machine146 learning146 model146 token146", 10),
        ["processor146", "reasoning146", "machine146", "learning146", "model146", "token146"],
    ),
    (
        ("processor146 reasoning146 machine146 learning146 model146 token146", 18),
        ["processor146", "reasoning146", "machine146", "learning146", "model146 token146"],
    ),
    (
        ("processor146 reasoning146 machine146 learning146 model146 token146", 28),
        ["processor146 reasoning146", "machine146 learning146", "model146 token146"],
    ),
    (
        ("reasoning146 machine146 learning146 model146 token146 prompt146", 6),
        ["reasoning146", "machine146", "learning146", "model146", "token146", "prompt146"],
    ),
    (
        ("reasoning146 machine146 learning146 model146 token146 prompt146", 10),
        ["reasoning146", "machine146", "learning146", "model146", "token146", "prompt146"],
    ),
    (
        ("reasoning146 machine146 learning146 model146 token146 prompt146", 18),
        ["reasoning146", "machine146", "learning146", "model146 token146", "prompt146"],
    ),
    (
        ("reasoning146 machine146 learning146 model146 token146 prompt146", 28),
        ["reasoning146 machine146", "learning146 model146", "token146 prompt146"],
    ),
    (
        ("machine146 learning146 model146 token146 prompt146 session146", 6),
        ["machine146", "learning146", "model146", "token146", "prompt146", "session146"],
    ),
    (
        ("machine146 learning146 model146 token146 prompt146 session146", 10),
        ["machine146", "learning146", "model146", "token146", "prompt146", "session146"],
    ),
    (
        ("machine146 learning146 model146 token146 prompt146 session146", 18),
        ["machine146", "learning146", "model146 token146", "prompt146", "session146"],
    ),
    (
        ("machine146 learning146 model146 token146 prompt146 session146", 28),
        ["machine146 learning146", "model146 token146 prompt146", "session146"],
    ),
    (
        ("learning146 model146 token146 prompt146 session146 library146", 6),
        ["learning146", "model146", "token146", "prompt146", "session146", "library146"],
    ),
    (
        ("learning146 model146 token146 prompt146 session146 library146", 10),
        ["learning146", "model146", "token146", "prompt146", "session146", "library146"],
    ),
    (
        ("learning146 model146 token146 prompt146 session146 library146", 18),
        ["learning146", "model146 token146", "prompt146", "session146", "library146"],
    ),
    (
        ("learning146 model146 token146 prompt146 session146 library146", 28),
        ["learning146 model146", "token146 prompt146", "session146 library146"],
    ),
    (
        ("model146 token146 prompt146 session146 library146 service146", 6),
        ["model146", "token146", "prompt146", "session146", "library146", "service146"],
    ),
    (
        ("model146 token146 prompt146 session146 library146 service146", 10),
        ["model146", "token146", "prompt146", "session146", "library146", "service146"],
    ),
    (
        ("model146 token146 prompt146 session146 library146 service146", 18),
        ["model146 token146", "prompt146", "session146", "library146", "service146"],
    ),
    (
        ("model146 token146 prompt146 session146 library146 service146", 28),
        ["model146 token146 prompt146", "session146 library146", "service146"],
    ),
    (
        ("token146 prompt146 session146 library146 service146 gateway146", 6),
        ["token146", "prompt146", "session146", "library146", "service146", "gateway146"],
    ),
    (
        ("token146 prompt146 session146 library146 service146 gateway146", 10),
        ["token146", "prompt146", "session146", "library146", "service146", "gateway146"],
    ),
    (
        ("token146 prompt146 session146 library146 service146 gateway146", 18),
        ["token146 prompt146", "session146", "library146", "service146", "gateway146"],
    ),
    (
        ("token146 prompt146 session146 library146 service146 gateway146", 28),
        ["token146 prompt146", "session146 library146", "service146 gateway146"],
    ),
    (
        ("prompt146 session146 library146 service146 gateway146 storage146", 6),
        ["prompt146", "session146", "library146", "service146", "gateway146", "storage146"],
    ),
    (
        ("prompt146 session146 library146 service146 gateway146 storage146", 10),
        ["prompt146", "session146", "library146", "service146", "gateway146", "storage146"],
    ),
    (
        ("prompt146 session146 library146 service146 gateway146 storage146", 18),
        ["prompt146", "session146", "library146", "service146", "gateway146", "storage146"],
    ),
    (
        ("prompt146 session146 library146 service146 gateway146 storage146", 28),
        ["prompt146 session146", "library146 service146", "gateway146 storage146"],
    ),
    (
        ("session146 library146 service146 gateway146 storage146 network146", 6),
        ["session146", "library146", "service146", "gateway146", "storage146", "network146"],
    ),
    (
        ("session146 library146 service146 gateway146 storage146 network146", 10),
        ["session146", "library146", "service146", "gateway146", "storage146", "network146"],
    ),
    (
        ("session146 library146 service146 gateway146 storage146 network146", 18),
        ["session146", "library146", "service146", "gateway146", "storage146", "network146"],
    ),
    (
        ("session146 library146 service146 gateway146 storage146 network146", 28),
        ["session146 library146", "service146 gateway146", "storage146 network146"],
    ),
    (
        ("library146 service146 gateway146 storage146 network146 latency146", 6),
        ["library146", "service146", "gateway146", "storage146", "network146", "latency146"],
    ),
    (
        ("library146 service146 gateway146 storage146 network146 latency146", 10),
        ["library146", "service146", "gateway146", "storage146", "network146", "latency146"],
    ),
    (
        ("library146 service146 gateway146 storage146 network146 latency146", 18),
        ["library146", "service146", "gateway146", "storage146", "network146", "latency146"],
    ),
    (
        ("library146 service146 gateway146 storage146 network146 latency146", 28),
        ["library146 service146", "gateway146 storage146", "network146 latency146"],
    ),
    (
        ("service146 gateway146 storage146 network146 latency146 buffer146", 6),
        ["service146", "gateway146", "storage146", "network146", "latency146", "buffer146"],
    ),
    (
        ("service146 gateway146 storage146 network146 latency146 buffer146", 10),
        ["service146", "gateway146", "storage146", "network146", "latency146", "buffer146"],
    ),
    (
        ("service146 gateway146 storage146 network146 latency146 buffer146", 18),
        ["service146", "gateway146", "storage146", "network146", "latency146", "buffer146"],
    ),
    (
        ("service146 gateway146 storage146 network146 latency146 buffer146", 28),
        ["service146 gateway146", "storage146 network146", "latency146 buffer146"],
    ),
    (
        ("gateway146 storage146 network146 latency146 buffer146 queue146", 6),
        ["gateway146", "storage146", "network146", "latency146", "buffer146", "queue146"],
    ),
    (
        ("gateway146 storage146 network146 latency146 buffer146 queue146", 10),
        ["gateway146", "storage146", "network146", "latency146", "buffer146", "queue146"],
    ),
    (
        ("gateway146 storage146 network146 latency146 buffer146 queue146", 18),
        ["gateway146", "storage146", "network146", "latency146", "buffer146 queue146"],
    ),
    (
        ("gateway146 storage146 network146 latency146 buffer146 queue146", 28),
        ["gateway146 storage146", "network146 latency146", "buffer146 queue146"],
    ),
    (
        ("storage146 network146 latency146 buffer146 queue146 worker146", 6),
        ["storage146", "network146", "latency146", "buffer146", "queue146", "worker146"],
    ),
    (
        ("storage146 network146 latency146 buffer146 queue146 worker146", 10),
        ["storage146", "network146", "latency146", "buffer146", "queue146", "worker146"],
    ),
    (
        ("storage146 network146 latency146 buffer146 queue146 worker146", 18),
        ["storage146", "network146", "latency146", "buffer146 queue146", "worker146"],
    ),
    (
        ("storage146 network146 latency146 buffer146 queue146 worker146", 28),
        ["storage146 network146", "latency146 buffer146", "queue146 worker146"],
    ),
    (
        ("network146 latency146 buffer146 queue146 worker146 kernel146", 6),
        ["network146", "latency146", "buffer146", "queue146", "worker146", "kernel146"],
    ),
    (
        ("network146 latency146 buffer146 queue146 worker146 kernel146", 10),
        ["network146", "latency146", "buffer146", "queue146", "worker146", "kernel146"],
    ),
    (
        ("network146 latency146 buffer146 queue146 worker146 kernel146", 18),
        ["network146", "latency146", "buffer146 queue146", "worker146", "kernel146"],
    ),
    (
        ("network146 latency146 buffer146 queue146 worker146 kernel146", 28),
        ["network146 latency146", "buffer146 queue146 worker146", "kernel146"],
    ),
    (
        ("latency146 buffer146 queue146 worker146 kernel146 signal146", 6),
        ["latency146", "buffer146", "queue146", "worker146", "kernel146", "signal146"],
    ),
    (
        ("latency146 buffer146 queue146 worker146 kernel146 signal146", 10),
        ["latency146", "buffer146", "queue146", "worker146", "kernel146", "signal146"],
    ),
    (
        ("latency146 buffer146 queue146 worker146 kernel146 signal146", 18),
        ["latency146", "buffer146 queue146", "worker146", "kernel146", "signal146"],
    ),
    (
        ("latency146 buffer146 queue146 worker146 kernel146 signal146", 28),
        ["latency146 buffer146", "queue146 worker146 kernel146", "signal146"],
    ),
    (
        ("buffer146 queue146 worker146 kernel146 signal146 packet146", 6),
        ["buffer146", "queue146", "worker146", "kernel146", "signal146", "packet146"],
    ),
    (
        ("buffer146 queue146 worker146 kernel146 signal146 packet146", 10),
        ["buffer146", "queue146", "worker146", "kernel146", "signal146", "packet146"],
    ),
    (
        ("buffer146 queue146 worker146 kernel146 signal146 packet146", 18),
        ["buffer146 queue146", "worker146", "kernel146", "signal146", "packet146"],
    ),
    (
        ("buffer146 queue146 worker146 kernel146 signal146 packet146", 28),
        ["buffer146 queue146 worker146", "kernel146 signal146", "packet146"],
    ),
    (
        ("queue146 worker146 kernel146 signal146 packet146 router146", 6),
        ["queue146", "worker146", "kernel146", "signal146", "packet146", "router146"],
    ),
    (
        ("queue146 worker146 kernel146 signal146 packet146 router146", 10),
        ["queue146", "worker146", "kernel146", "signal146", "packet146", "router146"],
    ),
    (
        ("queue146 worker146 kernel146 signal146 packet146 router146", 18),
        ["queue146 worker146", "kernel146", "signal146", "packet146", "router146"],
    ),
    (
        ("queue146 worker146 kernel146 signal146 packet146 router146", 28),
        ["queue146 worker146 kernel146", "signal146 packet146", "router146"],
    ),
    (
        ("worker146 kernel146 signal146 packet146 router146 cluster146", 6),
        ["worker146", "kernel146", "signal146", "packet146", "router146", "cluster146"],
    ),
    (
        ("worker146 kernel146 signal146 packet146 router146 cluster146", 10),
        ["worker146", "kernel146", "signal146", "packet146", "router146", "cluster146"],
    ),
    (
        ("worker146 kernel146 signal146 packet146 router146 cluster146", 18),
        ["worker146", "kernel146", "signal146", "packet146", "router146", "cluster146"],
    ),
    (
        ("worker146 kernel146 signal146 packet146 router146 cluster146", 28),
        ["worker146 kernel146", "signal146 packet146", "router146 cluster146"],
    ),
    (
        ("kernel146 signal146 packet146 router146 cluster146 mirror146", 6),
        ["kernel146", "signal146", "packet146", "router146", "cluster146", "mirror146"],
    ),
    (
        ("kernel146 signal146 packet146 router146 cluster146 mirror146", 10),
        ["kernel146", "signal146", "packet146", "router146", "cluster146", "mirror146"],
    ),
    (
        ("kernel146 signal146 packet146 router146 cluster146 mirror146", 18),
        ["kernel146", "signal146", "packet146", "router146", "cluster146", "mirror146"],
    ),
    (
        ("kernel146 signal146 packet146 router146 cluster146 mirror146", 28),
        ["kernel146 signal146", "packet146 router146", "cluster146 mirror146"],
    ),
    (
        ("signal146 packet146 router146 cluster146 mirror146 filter146", 6),
        ["signal146", "packet146", "router146", "cluster146", "mirror146", "filter146"],
    ),
    (
        ("signal146 packet146 router146 cluster146 mirror146 filter146", 10),
        ["signal146", "packet146", "router146", "cluster146", "mirror146", "filter146"],
    ),
    (
        ("signal146 packet146 router146 cluster146 mirror146 filter146", 18),
        ["signal146", "packet146", "router146", "cluster146", "mirror146", "filter146"],
    ),
    (
        ("signal146 packet146 router146 cluster146 mirror146 filter146", 28),
        ["signal146 packet146", "router146 cluster146", "mirror146 filter146"],
    ),
    (
        ("packet146 router146 cluster146 mirror146 filter146 ranking146", 6),
        ["packet146", "router146", "cluster146", "mirror146", "filter146", "ranking146"],
    ),
    (
        ("packet146 router146 cluster146 mirror146 filter146 ranking146", 10),
        ["packet146", "router146", "cluster146", "mirror146", "filter146", "ranking146"],
    ),
    (
        ("packet146 router146 cluster146 mirror146 filter146 ranking146", 18),
        ["packet146", "router146", "cluster146", "mirror146", "filter146", "ranking146"],
    ),
    (
        ("packet146 router146 cluster146 mirror146 filter146 ranking146", 28),
        ["packet146 router146", "cluster146 mirror146", "filter146 ranking146"],
    ),
    (
        ("router146 cluster146 mirror146 filter146 ranking146 encoding146", 6),
        ["router146", "cluster146", "mirror146", "filter146", "ranking146", "encoding146"],
    ),
    (
        ("router146 cluster146 mirror146 filter146 ranking146 encoding146", 10),
        ["router146", "cluster146", "mirror146", "filter146", "ranking146", "encoding146"],
    ),
    (
        ("router146 cluster146 mirror146 filter146 ranking146 encoding146", 18),
        ["router146", "cluster146", "mirror146", "filter146", "ranking146", "encoding146"],
    ),
    (
        ("router146 cluster146 mirror146 filter146 ranking146 encoding146", 28),
        ["router146 cluster146", "mirror146 filter146", "ranking146 encoding146"],
    ),
    (
        ("cluster146 mirror146 filter146 ranking146 encoding146 mapping146", 6),
        ["cluster146", "mirror146", "filter146", "ranking146", "encoding146", "mapping146"],
    ),
    (
        ("cluster146 mirror146 filter146 ranking146 encoding146 mapping146", 10),
        ["cluster146", "mirror146", "filter146", "ranking146", "encoding146", "mapping146"],
    ),
    (
        ("cluster146 mirror146 filter146 ranking146 encoding146 mapping146", 18),
        ["cluster146", "mirror146", "filter146", "ranking146", "encoding146", "mapping146"],
    ),
    (
        ("cluster146 mirror146 filter146 ranking146 encoding146 mapping146", 28),
        ["cluster146 mirror146", "filter146 ranking146", "encoding146 mapping146"],
    ),
    (
        ("mirror146 filter146 ranking146 encoding146 mapping146 record146", 6),
        ["mirror146", "filter146", "ranking146", "encoding146", "mapping146", "record146"],
    ),
    (
        ("mirror146 filter146 ranking146 encoding146 mapping146 record146", 10),
        ["mirror146", "filter146", "ranking146", "encoding146", "mapping146", "record146"],
    ),
    (
        ("mirror146 filter146 ranking146 encoding146 mapping146 record146", 18),
        ["mirror146", "filter146", "ranking146", "encoding146", "mapping146", "record146"],
    ),
    (
        ("mirror146 filter146 ranking146 encoding146 mapping146 record146", 28),
        ["mirror146 filter146", "ranking146 encoding146", "mapping146 record146"],
    ),
    (
        ("filter146 ranking146 encoding146 mapping146 record146 candle146", 6),
        ["filter146", "ranking146", "encoding146", "mapping146", "record146", "candle146"],
    ),
    (
        ("filter146 ranking146 encoding146 mapping146 record146 candle146", 10),
        ["filter146", "ranking146", "encoding146", "mapping146", "record146", "candle146"],
    ),
    (
        ("filter146 ranking146 encoding146 mapping146 record146 candle146", 18),
        ["filter146", "ranking146", "encoding146", "mapping146", "record146", "candle146"],
    ),
    (
        ("filter146 ranking146 encoding146 mapping146 record146 candle146", 28),
        ["filter146 ranking146", "encoding146 mapping146", "record146 candle146"],
    ),
    (
        ("ranking146 encoding146 mapping146 record146 candle146 thread146", 6),
        ["ranking146", "encoding146", "mapping146", "record146", "candle146", "thread146"],
    ),
    (
        ("ranking146 encoding146 mapping146 record146 candle146 thread146", 10),
        ["ranking146", "encoding146", "mapping146", "record146", "candle146", "thread146"],
    ),
    (
        ("ranking146 encoding146 mapping146 record146 candle146 thread146", 18),
        ["ranking146", "encoding146", "mapping146", "record146", "candle146", "thread146"],
    ),
    (
        ("ranking146 encoding146 mapping146 record146 candle146 thread146", 28),
        ["ranking146 encoding146", "mapping146 record146", "candle146 thread146"],
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
