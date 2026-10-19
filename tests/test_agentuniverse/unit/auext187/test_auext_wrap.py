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
        ("round 187: the quick brown fox jumps over the lazy dog", 4),
        ["round", "187:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 187: the quick brown fox jumps over the lazy dog", 8),
        ["round", "187: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 187: the quick brown fox jumps over the lazy dog", 12),
        ["round 187:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 187: the quick brown fox jumps over the lazy dog", 16),
        ["round 187: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 187: the quick brown fox jumps over the lazy dog", 24),
        ["round 187: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 187: the quick brown fox jumps over the lazy dog", 32),
        ["round 187: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 187: agentuniverse is a framework for multi agents", 4),
        ["round", "187:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 187: agentuniverse is a framework for multi agents", 8),
        ["round", "187:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 187: agentuniverse is a framework for multi agents", 12),
        ["round 187:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 187: agentuniverse is a framework for multi agents", 16),
        ["round 187:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 187: agentuniverse is a framework for multi agents", 24),
        ["round 187: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 187: agentuniverse is a framework for multi agents", 32),
        ["round 187: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 187: knowledge stored as vectors enables retrieval", 4),
        ["round", "187:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 187: knowledge stored as vectors enables retrieval", 8),
        ["round", "187:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 187: knowledge stored as vectors enables retrieval", 12),
        ["round 187:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 187: knowledge stored as vectors enables retrieval", 16),
        ["round 187:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 187: knowledge stored as vectors enables retrieval", 24),
        ["round 187: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 187: knowledge stored as vectors enables retrieval", 32),
        ["round 187: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 187: the processor reads the record then stops", 4),
        ["round", "187:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 187: the processor reads the record then stops", 8),
        ["round", "187: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 187: the processor reads the record then stops", 12),
        ["round 187:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 187: the processor reads the record then stops", 16),
        ["round 187: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 187: the processor reads the record then stops", 24),
        ["round 187: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 187: the processor reads the record then stops", 32),
        ["round 187: the processor reads", "the record then stops"],
    ),
    (
        ("round 187: a worker pulls the next task from the queue", 4),
        ["round", "187:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 187: a worker pulls the next task from the queue", 8),
        ["round", "187: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 187: a worker pulls the next task from the queue", 12),
        ["round 187: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 187: a worker pulls the next task from the queue", 16),
        ["round 187: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 187: a worker pulls the next task from the queue", 24),
        ["round 187: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 187: a worker pulls the next task from the queue", 32),
        ["round 187: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 187: signals travel through the network layer", 4),
        ["round", "187:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 187: signals travel through the network layer", 8),
        ["round", "187:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 187: signals travel through the network layer", 12),
        ["round 187:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 187: signals travel through the network layer", 16),
        ["round 187:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 187: signals travel through the network layer", 24),
        ["round 187: signals", "travel through the", "network layer"],
    ),
    (
        ("round 187: signals travel through the network layer", 32),
        ["round 187: signals travel", "through the network layer"],
    ),
    (
        ("round 187: the gateway routes each request by policy", 4),
        ["round", "187:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 187: the gateway routes each request by policy", 8),
        ["round", "187: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 187: the gateway routes each request by policy", 12),
        ["round 187:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 187: the gateway routes each request by policy", 16),
        ["round 187: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 187: the gateway routes each request by policy", 24),
        ["round 187: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 187: the gateway routes each request by policy", 32),
        ["round 187: the gateway routes", "each request by policy"],
    ),
    (
        ("round 187: memory grows until the buffer is full", 4),
        ["round", "187:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 187: memory grows until the buffer is full", 8),
        ["round", "187:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 187: memory grows until the buffer is full", 12),
        ["round 187:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 187: memory grows until the buffer is full", 16),
        ["round 187:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 187: memory grows until the buffer is full", 24), ["round 187: memory grows", "until the buffer is full"]),
    (("round 187: memory grows until the buffer is full", 32), ["round 187: memory grows until", "the buffer is full"]),
    (
        ("round 187: the cluster mirrors every packet twice", 4),
        ["round", "187:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 187: the cluster mirrors every packet twice", 8),
        ["round", "187: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 187: the cluster mirrors every packet twice", 12),
        ["round 187:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 187: the cluster mirrors every packet twice", 16),
        ["round 187: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 187: the cluster mirrors every packet twice", 24),
        ["round 187: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 187: the cluster mirrors every packet twice", 32),
        ["round 187: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 187: ranking uses tokens learned from the corpus", 4),
        ["round", "187:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 187: ranking uses tokens learned from the corpus", 8),
        ["round", "187:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 187: ranking uses tokens learned from the corpus", 12),
        ["round 187:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 187: ranking uses tokens learned from the corpus", 16),
        ["round 187:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 187: ranking uses tokens learned from the corpus", 24),
        ["round 187: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 187: ranking uses tokens learned from the corpus", 32),
        ["round 187: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 187: a long session ends when the candle dies", 4),
        ["round", "187:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 187: a long session ends when the candle dies", 8),
        ["round", "187: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 187: a long session ends when the candle dies", 12),
        ["round 187: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 187: a long session ends when the candle dies", 16),
        ["round 187: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 187: a long session ends when the candle dies", 24),
        ["round 187: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 187: a long session ends when the candle dies", 32),
        ["round 187: a long session ends", "when the candle dies"],
    ),
    (
        ("round 187: encode the prompt then map the result", 4),
        ["round", "187:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 187: encode the prompt then map the result", 8),
        ["round", "187:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 187: encode the prompt then map the result", 12),
        ["round 187:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 187: encode the prompt then map the result", 16),
        ["round 187:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 187: encode the prompt then map the result", 24),
        ["round 187: encode the", "prompt then map the", "result"],
    ),
    (("round 187: encode the prompt then map the result", 32), ["round 187: encode the prompt", "then map the result"]),
    (
        ("round 187: the kernel wakes the worker at dawn", 4),
        ["round", "187:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 187: the kernel wakes the worker at dawn", 8),
        ["round", "187: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 187: the kernel wakes the worker at dawn", 12),
        ["round 187:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 187: the kernel wakes the worker at dawn", 16), ["round 187: the", "kernel wakes the", "worker at dawn"]),
    (("round 187: the kernel wakes the worker at dawn", 24), ["round 187: the kernel", "wakes the worker at dawn"]),
    (("round 187: the kernel wakes the worker at dawn", 32), ["round 187: the kernel wakes the", "worker at dawn"]),
    (
        ("round 187: service latency drops after the patch", 4),
        ["round", "187:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 187: service latency drops after the patch", 8),
        ["round", "187:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 187: service latency drops after the patch", 12),
        ["round 187:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 187: service latency drops after the patch", 16),
        ["round 187:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 187: service latency drops after the patch", 24),
        ["round 187: service", "latency drops after the", "patch"],
    ),
    (("round 187: service latency drops after the patch", 32), ["round 187: service latency drops", "after the patch"]),
    (
        ("round 187: the library caches every vector it sees", 4),
        ["round", "187:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 187: the library caches every vector it sees", 8),
        ["round", "187: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 187: the library caches every vector it sees", 12),
        ["round 187:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 187: the library caches every vector it sees", 16),
        ["round 187: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 187: the library caches every vector it sees", 24),
        ["round 187: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 187: the library caches every vector it sees", 32),
        ["round 187: the library caches", "every vector it sees"],
    ),
    (
        ("round 187: agents argue then the debate resolves", 4),
        ["round", "187:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 187: agents argue then the debate resolves", 8),
        ["round", "187:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 187: agents argue then the debate resolves", 12),
        ["round 187:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 187: agents argue then the debate resolves", 16),
        ["round 187:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 187: agents argue then the debate resolves", 24), ["round 187: agents argue", "then the debate resolves"]),
    (("round 187: agents argue then the debate resolves", 32), ["round 187: agents argue then the", "debate resolves"]),
    (
        ("round 187: the filter keeps only strong matches", 4),
        ["round", "187:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 187: the filter keeps only strong matches", 8),
        ["round", "187: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 187: the filter keeps only strong matches", 12),
        ["round 187:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 187: the filter keeps only strong matches", 16),
        ["round 187: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 187: the filter keeps only strong matches", 24),
        ["round 187: the filter", "keeps only strong", "matches"],
    ),
    (("round 187: the filter keeps only strong matches", 32), ["round 187: the filter keeps only", "strong matches"]),
    (
        ("round 187: the model answers with a short reply", 4),
        ["round", "187:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 187: the model answers with a short reply", 8),
        ["round", "187: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 187: the model answers with a short reply", 12),
        ["round 187:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 187: the model answers with a short reply", 16),
        ["round 187: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 187: the model answers with a short reply", 24),
        ["round 187: the model", "answers with a short", "reply"],
    ),
    (("round 187: the model answers with a short reply", 32), ["round 187: the model answers", "with a short reply"]),
    (
        ("round 187: the recorder stores the reasoning trace", 4),
        ["round", "187:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 187: the recorder stores the reasoning trace", 8),
        ["round", "187: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 187: the recorder stores the reasoning trace", 12),
        ["round 187:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 187: the recorder stores the reasoning trace", 16),
        ["round 187: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 187: the recorder stores the reasoning trace", 24),
        ["round 187: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 187: the recorder stores the reasoning trace", 32),
        ["round 187: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 187: the angel watches the processor run", 4),
        ["round", "187:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 187: the angel watches the processor run", 8),
        ["round", "187: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 187: the angel watches the processor run", 12),
        ["round 187:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 187: the angel watches the processor run", 16),
        ["round 187: the", "angel watches", "the processor", "run"],
    ),
    (("round 187: the angel watches the processor run", 24), ["round 187: the angel", "watches the processor", "run"]),
    (("round 187: the angel watches the processor run", 32), ["round 187: the angel watches the", "processor run"]),
    (
        ("round 187: angle of the vector decides the match", 4),
        ["round", "187:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 187: angle of the vector decides the match", 8),
        ["round", "187:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 187: angle of the vector decides the match", 12),
        ["round 187:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 187: angle of the vector decides the match", 16),
        ["round 187: angle", "of the vector", "decides the", "match"],
    ),
    (("round 187: angle of the vector decides the match", 24), ["round 187: angle of the", "vector decides the match"]),
    (("round 187: angle of the vector decides the match", 32), ["round 187: angle of the vector", "decides the match"]),
    (
        ("round 187: the candle burns twice as long at night", 4),
        ["round", "187:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 187: the candle burns twice as long at night", 8),
        ["round", "187: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 187: the candle burns twice as long at night", 12),
        ["round 187:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 187: the candle burns twice as long at night", 16),
        ["round 187: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 187: the candle burns twice as long at night", 24),
        ["round 187: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 187: the candle burns twice as long at night", 32),
        ["round 187: the candle burns", "twice as long at night"],
    ),
    (
        ("round 187: a mirror of the universe in one line", 4),
        ["round", "187:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 187: a mirror of the universe in one line", 8),
        ["round", "187: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 187: a mirror of the universe in one line", 12),
        ["round 187: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 187: a mirror of the universe in one line", 16),
        ["round 187: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 187: a mirror of the universe in one line", 24), ["round 187: a mirror of", "the universe in one line"]),
    (("round 187: a mirror of the universe in one line", 32), ["round 187: a mirror of the", "universe in one line"]),
    (
        ("round 187: the queue drains before the storm", 4),
        ["round", "187:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 187: the queue drains before the storm", 8),
        ["round", "187: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 187: the queue drains before the storm", 12),
        ["round 187:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 187: the queue drains before the storm", 16), ["round 187: the", "queue drains", "before the storm"]),
    (("round 187: the queue drains before the storm", 24), ["round 187: the queue", "drains before the storm"]),
    (("round 187: the queue drains before the storm", 32), ["round 187: the queue drains", "before the storm"]),
    (
        ("kitten187 sitting187 agent187 angle187 universe187 memory187", 6),
        ["kitten187", "sitting187", "agent187", "angle187", "universe187", "memory187"],
    ),
    (
        ("kitten187 sitting187 agent187 angle187 universe187 memory187", 10),
        ["kitten187", "sitting187", "agent187", "angle187", "universe187", "memory187"],
    ),
    (
        ("kitten187 sitting187 agent187 angle187 universe187 memory187", 18),
        ["kitten187", "sitting187", "agent187 angle187", "universe187", "memory187"],
    ),
    (
        ("kitten187 sitting187 agent187 angle187 universe187 memory187", 28),
        ["kitten187 sitting187", "agent187 angle187", "universe187 memory187"],
    ),
    (
        ("sitting187 agent187 angle187 universe187 memory187 stream187", 6),
        ["sitting187", "agent187", "angle187", "universe187", "memory187", "stream187"],
    ),
    (
        ("sitting187 agent187 angle187 universe187 memory187 stream187", 10),
        ["sitting187", "agent187", "angle187", "universe187", "memory187", "stream187"],
    ),
    (
        ("sitting187 agent187 angle187 universe187 memory187 stream187", 18),
        ["sitting187", "agent187 angle187", "universe187", "memory187", "stream187"],
    ),
    (
        ("sitting187 agent187 angle187 universe187 memory187 stream187", 28),
        ["sitting187 agent187 angle187", "universe187 memory187", "stream187"],
    ),
    (
        ("agent187 angle187 universe187 memory187 stream187 context187", 6),
        ["agent187", "angle187", "universe187", "memory187", "stream187", "context187"],
    ),
    (
        ("agent187 angle187 universe187 memory187 stream187 context187", 10),
        ["agent187", "angle187", "universe187", "memory187", "stream187", "context187"],
    ),
    (
        ("agent187 angle187 universe187 memory187 stream187 context187", 18),
        ["agent187 angle187", "universe187", "memory187", "stream187", "context187"],
    ),
    (
        ("agent187 angle187 universe187 memory187 stream187 context187", 28),
        ["agent187 angle187", "universe187 memory187", "stream187 context187"],
    ),
    (
        ("angle187 universe187 memory187 stream187 context187 knowledge187", 6),
        ["angle187", "universe187", "memory187", "stream187", "context187", "knowledge187"],
    ),
    (
        ("angle187 universe187 memory187 stream187 context187 knowledge187", 10),
        ["angle187", "universe187", "memory187", "stream187", "context187", "knowledge187"],
    ),
    (
        ("angle187 universe187 memory187 stream187 context187 knowledge187", 18),
        ["angle187", "universe187", "memory187", "stream187", "context187", "knowledge187"],
    ),
    (
        ("angle187 universe187 memory187 stream187 context187 knowledge187", 28),
        ["angle187 universe187", "memory187 stream187", "context187 knowledge187"],
    ),
    (
        ("universe187 memory187 stream187 context187 knowledge187 vector187", 6),
        ["universe187", "memory187", "stream187", "context187", "knowledge187", "vector187"],
    ),
    (
        ("universe187 memory187 stream187 context187 knowledge187 vector187", 10),
        ["universe187", "memory187", "stream187", "context187", "knowledge187", "vector187"],
    ),
    (
        ("universe187 memory187 stream187 context187 knowledge187 vector187", 18),
        ["universe187", "memory187", "stream187", "context187", "knowledge187", "vector187"],
    ),
    (
        ("universe187 memory187 stream187 context187 knowledge187 vector187", 28),
        ["universe187 memory187", "stream187 context187", "knowledge187 vector187"],
    ),
    (
        ("memory187 stream187 context187 knowledge187 vector187 processor187", 6),
        ["memory187", "stream187", "context187", "knowledge187", "vector187", "processor187"],
    ),
    (
        ("memory187 stream187 context187 knowledge187 vector187 processor187", 10),
        ["memory187", "stream187", "context187", "knowledge187", "vector187", "processor187"],
    ),
    (
        ("memory187 stream187 context187 knowledge187 vector187 processor187", 18),
        ["memory187", "stream187", "context187", "knowledge187", "vector187", "processor187"],
    ),
    (
        ("memory187 stream187 context187 knowledge187 vector187 processor187", 28),
        ["memory187 stream187", "context187 knowledge187", "vector187 processor187"],
    ),
    (
        ("stream187 context187 knowledge187 vector187 processor187 reasoning187", 6),
        ["stream187", "context187", "knowledge187", "vector187", "processor187", "reasoning187"],
    ),
    (
        ("stream187 context187 knowledge187 vector187 processor187 reasoning187", 10),
        ["stream187", "context187", "knowledge187", "vector187", "processor187", "reasoning187"],
    ),
    (
        ("stream187 context187 knowledge187 vector187 processor187 reasoning187", 18),
        ["stream187", "context187", "knowledge187", "vector187", "processor187", "reasoning187"],
    ),
    (
        ("stream187 context187 knowledge187 vector187 processor187 reasoning187", 28),
        ["stream187 context187", "knowledge187 vector187", "processor187 reasoning187"],
    ),
    (
        ("context187 knowledge187 vector187 processor187 reasoning187 machine187", 6),
        ["context187", "knowledge187", "vector187", "processor187", "reasoning187", "machine187"],
    ),
    (
        ("context187 knowledge187 vector187 processor187 reasoning187 machine187", 10),
        ["context187", "knowledge187", "vector187", "processor187", "reasoning187", "machine187"],
    ),
    (
        ("context187 knowledge187 vector187 processor187 reasoning187 machine187", 18),
        ["context187", "knowledge187", "vector187", "processor187", "reasoning187", "machine187"],
    ),
    (
        ("context187 knowledge187 vector187 processor187 reasoning187 machine187", 28),
        ["context187 knowledge187", "vector187 processor187", "reasoning187 machine187"],
    ),
    (
        ("knowledge187 vector187 processor187 reasoning187 machine187 learning187", 6),
        ["knowledge187", "vector187", "processor187", "reasoning187", "machine187", "learning187"],
    ),
    (
        ("knowledge187 vector187 processor187 reasoning187 machine187 learning187", 10),
        ["knowledge187", "vector187", "processor187", "reasoning187", "machine187", "learning187"],
    ),
    (
        ("knowledge187 vector187 processor187 reasoning187 machine187 learning187", 18),
        ["knowledge187", "vector187", "processor187", "reasoning187", "machine187", "learning187"],
    ),
    (
        ("knowledge187 vector187 processor187 reasoning187 machine187 learning187", 28),
        ["knowledge187 vector187", "processor187 reasoning187", "machine187 learning187"],
    ),
    (
        ("vector187 processor187 reasoning187 machine187 learning187 model187", 6),
        ["vector187", "processor187", "reasoning187", "machine187", "learning187", "model187"],
    ),
    (
        ("vector187 processor187 reasoning187 machine187 learning187 model187", 10),
        ["vector187", "processor187", "reasoning187", "machine187", "learning187", "model187"],
    ),
    (
        ("vector187 processor187 reasoning187 machine187 learning187 model187", 18),
        ["vector187", "processor187", "reasoning187", "machine187", "learning187", "model187"],
    ),
    (
        ("vector187 processor187 reasoning187 machine187 learning187 model187", 28),
        ["vector187 processor187", "reasoning187 machine187", "learning187 model187"],
    ),
    (
        ("processor187 reasoning187 machine187 learning187 model187 token187", 6),
        ["processor187", "reasoning187", "machine187", "learning187", "model187", "token187"],
    ),
    (
        ("processor187 reasoning187 machine187 learning187 model187 token187", 10),
        ["processor187", "reasoning187", "machine187", "learning187", "model187", "token187"],
    ),
    (
        ("processor187 reasoning187 machine187 learning187 model187 token187", 18),
        ["processor187", "reasoning187", "machine187", "learning187", "model187 token187"],
    ),
    (
        ("processor187 reasoning187 machine187 learning187 model187 token187", 28),
        ["processor187 reasoning187", "machine187 learning187", "model187 token187"],
    ),
    (
        ("reasoning187 machine187 learning187 model187 token187 prompt187", 6),
        ["reasoning187", "machine187", "learning187", "model187", "token187", "prompt187"],
    ),
    (
        ("reasoning187 machine187 learning187 model187 token187 prompt187", 10),
        ["reasoning187", "machine187", "learning187", "model187", "token187", "prompt187"],
    ),
    (
        ("reasoning187 machine187 learning187 model187 token187 prompt187", 18),
        ["reasoning187", "machine187", "learning187", "model187 token187", "prompt187"],
    ),
    (
        ("reasoning187 machine187 learning187 model187 token187 prompt187", 28),
        ["reasoning187 machine187", "learning187 model187", "token187 prompt187"],
    ),
    (
        ("machine187 learning187 model187 token187 prompt187 session187", 6),
        ["machine187", "learning187", "model187", "token187", "prompt187", "session187"],
    ),
    (
        ("machine187 learning187 model187 token187 prompt187 session187", 10),
        ["machine187", "learning187", "model187", "token187", "prompt187", "session187"],
    ),
    (
        ("machine187 learning187 model187 token187 prompt187 session187", 18),
        ["machine187", "learning187", "model187 token187", "prompt187", "session187"],
    ),
    (
        ("machine187 learning187 model187 token187 prompt187 session187", 28),
        ["machine187 learning187", "model187 token187 prompt187", "session187"],
    ),
    (
        ("learning187 model187 token187 prompt187 session187 library187", 6),
        ["learning187", "model187", "token187", "prompt187", "session187", "library187"],
    ),
    (
        ("learning187 model187 token187 prompt187 session187 library187", 10),
        ["learning187", "model187", "token187", "prompt187", "session187", "library187"],
    ),
    (
        ("learning187 model187 token187 prompt187 session187 library187", 18),
        ["learning187", "model187 token187", "prompt187", "session187", "library187"],
    ),
    (
        ("learning187 model187 token187 prompt187 session187 library187", 28),
        ["learning187 model187", "token187 prompt187", "session187 library187"],
    ),
    (
        ("model187 token187 prompt187 session187 library187 service187", 6),
        ["model187", "token187", "prompt187", "session187", "library187", "service187"],
    ),
    (
        ("model187 token187 prompt187 session187 library187 service187", 10),
        ["model187", "token187", "prompt187", "session187", "library187", "service187"],
    ),
    (
        ("model187 token187 prompt187 session187 library187 service187", 18),
        ["model187 token187", "prompt187", "session187", "library187", "service187"],
    ),
    (
        ("model187 token187 prompt187 session187 library187 service187", 28),
        ["model187 token187 prompt187", "session187 library187", "service187"],
    ),
    (
        ("token187 prompt187 session187 library187 service187 gateway187", 6),
        ["token187", "prompt187", "session187", "library187", "service187", "gateway187"],
    ),
    (
        ("token187 prompt187 session187 library187 service187 gateway187", 10),
        ["token187", "prompt187", "session187", "library187", "service187", "gateway187"],
    ),
    (
        ("token187 prompt187 session187 library187 service187 gateway187", 18),
        ["token187 prompt187", "session187", "library187", "service187", "gateway187"],
    ),
    (
        ("token187 prompt187 session187 library187 service187 gateway187", 28),
        ["token187 prompt187", "session187 library187", "service187 gateway187"],
    ),
    (
        ("prompt187 session187 library187 service187 gateway187 storage187", 6),
        ["prompt187", "session187", "library187", "service187", "gateway187", "storage187"],
    ),
    (
        ("prompt187 session187 library187 service187 gateway187 storage187", 10),
        ["prompt187", "session187", "library187", "service187", "gateway187", "storage187"],
    ),
    (
        ("prompt187 session187 library187 service187 gateway187 storage187", 18),
        ["prompt187", "session187", "library187", "service187", "gateway187", "storage187"],
    ),
    (
        ("prompt187 session187 library187 service187 gateway187 storage187", 28),
        ["prompt187 session187", "library187 service187", "gateway187 storage187"],
    ),
    (
        ("session187 library187 service187 gateway187 storage187 network187", 6),
        ["session187", "library187", "service187", "gateway187", "storage187", "network187"],
    ),
    (
        ("session187 library187 service187 gateway187 storage187 network187", 10),
        ["session187", "library187", "service187", "gateway187", "storage187", "network187"],
    ),
    (
        ("session187 library187 service187 gateway187 storage187 network187", 18),
        ["session187", "library187", "service187", "gateway187", "storage187", "network187"],
    ),
    (
        ("session187 library187 service187 gateway187 storage187 network187", 28),
        ["session187 library187", "service187 gateway187", "storage187 network187"],
    ),
    (
        ("library187 service187 gateway187 storage187 network187 latency187", 6),
        ["library187", "service187", "gateway187", "storage187", "network187", "latency187"],
    ),
    (
        ("library187 service187 gateway187 storage187 network187 latency187", 10),
        ["library187", "service187", "gateway187", "storage187", "network187", "latency187"],
    ),
    (
        ("library187 service187 gateway187 storage187 network187 latency187", 18),
        ["library187", "service187", "gateway187", "storage187", "network187", "latency187"],
    ),
    (
        ("library187 service187 gateway187 storage187 network187 latency187", 28),
        ["library187 service187", "gateway187 storage187", "network187 latency187"],
    ),
    (
        ("service187 gateway187 storage187 network187 latency187 buffer187", 6),
        ["service187", "gateway187", "storage187", "network187", "latency187", "buffer187"],
    ),
    (
        ("service187 gateway187 storage187 network187 latency187 buffer187", 10),
        ["service187", "gateway187", "storage187", "network187", "latency187", "buffer187"],
    ),
    (
        ("service187 gateway187 storage187 network187 latency187 buffer187", 18),
        ["service187", "gateway187", "storage187", "network187", "latency187", "buffer187"],
    ),
    (
        ("service187 gateway187 storage187 network187 latency187 buffer187", 28),
        ["service187 gateway187", "storage187 network187", "latency187 buffer187"],
    ),
    (
        ("gateway187 storage187 network187 latency187 buffer187 queue187", 6),
        ["gateway187", "storage187", "network187", "latency187", "buffer187", "queue187"],
    ),
    (
        ("gateway187 storage187 network187 latency187 buffer187 queue187", 10),
        ["gateway187", "storage187", "network187", "latency187", "buffer187", "queue187"],
    ),
    (
        ("gateway187 storage187 network187 latency187 buffer187 queue187", 18),
        ["gateway187", "storage187", "network187", "latency187", "buffer187 queue187"],
    ),
    (
        ("gateway187 storage187 network187 latency187 buffer187 queue187", 28),
        ["gateway187 storage187", "network187 latency187", "buffer187 queue187"],
    ),
    (
        ("storage187 network187 latency187 buffer187 queue187 worker187", 6),
        ["storage187", "network187", "latency187", "buffer187", "queue187", "worker187"],
    ),
    (
        ("storage187 network187 latency187 buffer187 queue187 worker187", 10),
        ["storage187", "network187", "latency187", "buffer187", "queue187", "worker187"],
    ),
    (
        ("storage187 network187 latency187 buffer187 queue187 worker187", 18),
        ["storage187", "network187", "latency187", "buffer187 queue187", "worker187"],
    ),
    (
        ("storage187 network187 latency187 buffer187 queue187 worker187", 28),
        ["storage187 network187", "latency187 buffer187", "queue187 worker187"],
    ),
    (
        ("network187 latency187 buffer187 queue187 worker187 kernel187", 6),
        ["network187", "latency187", "buffer187", "queue187", "worker187", "kernel187"],
    ),
    (
        ("network187 latency187 buffer187 queue187 worker187 kernel187", 10),
        ["network187", "latency187", "buffer187", "queue187", "worker187", "kernel187"],
    ),
    (
        ("network187 latency187 buffer187 queue187 worker187 kernel187", 18),
        ["network187", "latency187", "buffer187 queue187", "worker187", "kernel187"],
    ),
    (
        ("network187 latency187 buffer187 queue187 worker187 kernel187", 28),
        ["network187 latency187", "buffer187 queue187 worker187", "kernel187"],
    ),
    (
        ("latency187 buffer187 queue187 worker187 kernel187 signal187", 6),
        ["latency187", "buffer187", "queue187", "worker187", "kernel187", "signal187"],
    ),
    (
        ("latency187 buffer187 queue187 worker187 kernel187 signal187", 10),
        ["latency187", "buffer187", "queue187", "worker187", "kernel187", "signal187"],
    ),
    (
        ("latency187 buffer187 queue187 worker187 kernel187 signal187", 18),
        ["latency187", "buffer187 queue187", "worker187", "kernel187", "signal187"],
    ),
    (
        ("latency187 buffer187 queue187 worker187 kernel187 signal187", 28),
        ["latency187 buffer187", "queue187 worker187 kernel187", "signal187"],
    ),
    (
        ("buffer187 queue187 worker187 kernel187 signal187 packet187", 6),
        ["buffer187", "queue187", "worker187", "kernel187", "signal187", "packet187"],
    ),
    (
        ("buffer187 queue187 worker187 kernel187 signal187 packet187", 10),
        ["buffer187", "queue187", "worker187", "kernel187", "signal187", "packet187"],
    ),
    (
        ("buffer187 queue187 worker187 kernel187 signal187 packet187", 18),
        ["buffer187 queue187", "worker187", "kernel187", "signal187", "packet187"],
    ),
    (
        ("buffer187 queue187 worker187 kernel187 signal187 packet187", 28),
        ["buffer187 queue187 worker187", "kernel187 signal187", "packet187"],
    ),
    (
        ("queue187 worker187 kernel187 signal187 packet187 router187", 6),
        ["queue187", "worker187", "kernel187", "signal187", "packet187", "router187"],
    ),
    (
        ("queue187 worker187 kernel187 signal187 packet187 router187", 10),
        ["queue187", "worker187", "kernel187", "signal187", "packet187", "router187"],
    ),
    (
        ("queue187 worker187 kernel187 signal187 packet187 router187", 18),
        ["queue187 worker187", "kernel187", "signal187", "packet187", "router187"],
    ),
    (
        ("queue187 worker187 kernel187 signal187 packet187 router187", 28),
        ["queue187 worker187 kernel187", "signal187 packet187", "router187"],
    ),
    (
        ("worker187 kernel187 signal187 packet187 router187 cluster187", 6),
        ["worker187", "kernel187", "signal187", "packet187", "router187", "cluster187"],
    ),
    (
        ("worker187 kernel187 signal187 packet187 router187 cluster187", 10),
        ["worker187", "kernel187", "signal187", "packet187", "router187", "cluster187"],
    ),
    (
        ("worker187 kernel187 signal187 packet187 router187 cluster187", 18),
        ["worker187", "kernel187", "signal187", "packet187", "router187", "cluster187"],
    ),
    (
        ("worker187 kernel187 signal187 packet187 router187 cluster187", 28),
        ["worker187 kernel187", "signal187 packet187", "router187 cluster187"],
    ),
    (
        ("kernel187 signal187 packet187 router187 cluster187 mirror187", 6),
        ["kernel187", "signal187", "packet187", "router187", "cluster187", "mirror187"],
    ),
    (
        ("kernel187 signal187 packet187 router187 cluster187 mirror187", 10),
        ["kernel187", "signal187", "packet187", "router187", "cluster187", "mirror187"],
    ),
    (
        ("kernel187 signal187 packet187 router187 cluster187 mirror187", 18),
        ["kernel187", "signal187", "packet187", "router187", "cluster187", "mirror187"],
    ),
    (
        ("kernel187 signal187 packet187 router187 cluster187 mirror187", 28),
        ["kernel187 signal187", "packet187 router187", "cluster187 mirror187"],
    ),
    (
        ("signal187 packet187 router187 cluster187 mirror187 filter187", 6),
        ["signal187", "packet187", "router187", "cluster187", "mirror187", "filter187"],
    ),
    (
        ("signal187 packet187 router187 cluster187 mirror187 filter187", 10),
        ["signal187", "packet187", "router187", "cluster187", "mirror187", "filter187"],
    ),
    (
        ("signal187 packet187 router187 cluster187 mirror187 filter187", 18),
        ["signal187", "packet187", "router187", "cluster187", "mirror187", "filter187"],
    ),
    (
        ("signal187 packet187 router187 cluster187 mirror187 filter187", 28),
        ["signal187 packet187", "router187 cluster187", "mirror187 filter187"],
    ),
    (
        ("packet187 router187 cluster187 mirror187 filter187 ranking187", 6),
        ["packet187", "router187", "cluster187", "mirror187", "filter187", "ranking187"],
    ),
    (
        ("packet187 router187 cluster187 mirror187 filter187 ranking187", 10),
        ["packet187", "router187", "cluster187", "mirror187", "filter187", "ranking187"],
    ),
    (
        ("packet187 router187 cluster187 mirror187 filter187 ranking187", 18),
        ["packet187", "router187", "cluster187", "mirror187", "filter187", "ranking187"],
    ),
    (
        ("packet187 router187 cluster187 mirror187 filter187 ranking187", 28),
        ["packet187 router187", "cluster187 mirror187", "filter187 ranking187"],
    ),
    (
        ("router187 cluster187 mirror187 filter187 ranking187 encoding187", 6),
        ["router187", "cluster187", "mirror187", "filter187", "ranking187", "encoding187"],
    ),
    (
        ("router187 cluster187 mirror187 filter187 ranking187 encoding187", 10),
        ["router187", "cluster187", "mirror187", "filter187", "ranking187", "encoding187"],
    ),
    (
        ("router187 cluster187 mirror187 filter187 ranking187 encoding187", 18),
        ["router187", "cluster187", "mirror187", "filter187", "ranking187", "encoding187"],
    ),
    (
        ("router187 cluster187 mirror187 filter187 ranking187 encoding187", 28),
        ["router187 cluster187", "mirror187 filter187", "ranking187 encoding187"],
    ),
    (
        ("cluster187 mirror187 filter187 ranking187 encoding187 mapping187", 6),
        ["cluster187", "mirror187", "filter187", "ranking187", "encoding187", "mapping187"],
    ),
    (
        ("cluster187 mirror187 filter187 ranking187 encoding187 mapping187", 10),
        ["cluster187", "mirror187", "filter187", "ranking187", "encoding187", "mapping187"],
    ),
    (
        ("cluster187 mirror187 filter187 ranking187 encoding187 mapping187", 18),
        ["cluster187", "mirror187", "filter187", "ranking187", "encoding187", "mapping187"],
    ),
    (
        ("cluster187 mirror187 filter187 ranking187 encoding187 mapping187", 28),
        ["cluster187 mirror187", "filter187 ranking187", "encoding187 mapping187"],
    ),
    (
        ("mirror187 filter187 ranking187 encoding187 mapping187 record187", 6),
        ["mirror187", "filter187", "ranking187", "encoding187", "mapping187", "record187"],
    ),
    (
        ("mirror187 filter187 ranking187 encoding187 mapping187 record187", 10),
        ["mirror187", "filter187", "ranking187", "encoding187", "mapping187", "record187"],
    ),
    (
        ("mirror187 filter187 ranking187 encoding187 mapping187 record187", 18),
        ["mirror187", "filter187", "ranking187", "encoding187", "mapping187", "record187"],
    ),
    (
        ("mirror187 filter187 ranking187 encoding187 mapping187 record187", 28),
        ["mirror187 filter187", "ranking187 encoding187", "mapping187 record187"],
    ),
    (
        ("filter187 ranking187 encoding187 mapping187 record187 candle187", 6),
        ["filter187", "ranking187", "encoding187", "mapping187", "record187", "candle187"],
    ),
    (
        ("filter187 ranking187 encoding187 mapping187 record187 candle187", 10),
        ["filter187", "ranking187", "encoding187", "mapping187", "record187", "candle187"],
    ),
    (
        ("filter187 ranking187 encoding187 mapping187 record187 candle187", 18),
        ["filter187", "ranking187", "encoding187", "mapping187", "record187", "candle187"],
    ),
    (
        ("filter187 ranking187 encoding187 mapping187 record187 candle187", 28),
        ["filter187 ranking187", "encoding187 mapping187", "record187 candle187"],
    ),
    (
        ("ranking187 encoding187 mapping187 record187 candle187 thread187", 6),
        ["ranking187", "encoding187", "mapping187", "record187", "candle187", "thread187"],
    ),
    (
        ("ranking187 encoding187 mapping187 record187 candle187 thread187", 10),
        ["ranking187", "encoding187", "mapping187", "record187", "candle187", "thread187"],
    ),
    (
        ("ranking187 encoding187 mapping187 record187 candle187 thread187", 18),
        ["ranking187", "encoding187", "mapping187", "record187", "candle187", "thread187"],
    ),
    (
        ("ranking187 encoding187 mapping187 record187 candle187 thread187", 28),
        ["ranking187 encoding187", "mapping187 record187", "candle187 thread187"],
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
