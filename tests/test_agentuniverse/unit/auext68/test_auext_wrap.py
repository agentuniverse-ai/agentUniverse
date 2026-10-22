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
        ("round 68: the quick brown fox jumps over the lazy dog", 4),
        ["round", "68:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 68: the quick brown fox jumps over the lazy dog", 8),
        ["round", "68: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 68: the quick brown fox jumps over the lazy dog", 12),
        ["round 68:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 68: the quick brown fox jumps over the lazy dog", 16),
        ["round 68: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 68: the quick brown fox jumps over the lazy dog", 24),
        ["round 68: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 68: the quick brown fox jumps over the lazy dog", 32),
        ["round 68: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 68: agentuniverse is a framework for multi agents", 4),
        ["round", "68:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 68: agentuniverse is a framework for multi agents", 8),
        ["round", "68:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 68: agentuniverse is a framework for multi agents", 12),
        ["round 68:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 68: agentuniverse is a framework for multi agents", 16),
        ["round 68:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 68: agentuniverse is a framework for multi agents", 24),
        ["round 68: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 68: agentuniverse is a framework for multi agents", 32),
        ["round 68: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 68: knowledge stored as vectors enables retrieval", 4),
        ["round", "68:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 68: knowledge stored as vectors enables retrieval", 8),
        ["round", "68:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 68: knowledge stored as vectors enables retrieval", 12),
        ["round 68:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 68: knowledge stored as vectors enables retrieval", 16),
        ["round 68:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 68: knowledge stored as vectors enables retrieval", 24),
        ["round 68: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 68: knowledge stored as vectors enables retrieval", 32),
        ["round 68: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 68: the processor reads the record then stops", 4),
        ["round", "68:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 68: the processor reads the record then stops", 8),
        ["round", "68: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 68: the processor reads the record then stops", 12),
        ["round 68:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 68: the processor reads the record then stops", 16),
        ["round 68: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 68: the processor reads the record then stops", 24),
        ["round 68: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 68: the processor reads the record then stops", 32),
        ["round 68: the processor reads", "the record then stops"],
    ),
    (
        ("round 68: a worker pulls the next task from the queue", 4),
        ["round", "68:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 68: a worker pulls the next task from the queue", 8),
        ["round", "68: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 68: a worker pulls the next task from the queue", 12),
        ["round 68: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 68: a worker pulls the next task from the queue", 16),
        ["round 68: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 68: a worker pulls the next task from the queue", 24),
        ["round 68: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 68: a worker pulls the next task from the queue", 32),
        ["round 68: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 68: signals travel through the network layer", 4),
        ["round", "68:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 68: signals travel through the network layer", 8),
        ["round", "68:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 68: signals travel through the network layer", 12),
        ["round 68:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 68: signals travel through the network layer", 16),
        ["round 68:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 68: signals travel through the network layer", 24),
        ["round 68: signals travel", "through the network", "layer"],
    ),
    (
        ("round 68: signals travel through the network layer", 32),
        ["round 68: signals travel through", "the network layer"],
    ),
    (
        ("round 68: the gateway routes each request by policy", 4),
        ["round", "68:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 68: the gateway routes each request by policy", 8),
        ["round", "68: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 68: the gateway routes each request by policy", 12),
        ["round 68:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 68: the gateway routes each request by policy", 16),
        ["round 68: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 68: the gateway routes each request by policy", 24),
        ["round 68: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 68: the gateway routes each request by policy", 32),
        ["round 68: the gateway routes", "each request by policy"],
    ),
    (
        ("round 68: memory grows until the buffer is full", 4),
        ["round", "68:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 68: memory grows until the buffer is full", 8),
        ["round", "68:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 68: memory grows until the buffer is full", 12),
        ["round 68:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 68: memory grows until the buffer is full", 16),
        ["round 68: memory", "grows until the", "buffer is full"],
    ),
    (("round 68: memory grows until the buffer is full", 24), ["round 68: memory grows", "until the buffer is full"]),
    (("round 68: memory grows until the buffer is full", 32), ["round 68: memory grows until the", "buffer is full"]),
    (
        ("round 68: the cluster mirrors every packet twice", 4),
        ["round", "68:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 68: the cluster mirrors every packet twice", 8),
        ["round", "68: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 68: the cluster mirrors every packet twice", 12),
        ["round 68:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 68: the cluster mirrors every packet twice", 16),
        ["round 68: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 68: the cluster mirrors every packet twice", 24),
        ["round 68: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 68: the cluster mirrors every packet twice", 32), ["round 68: the cluster mirrors", "every packet twice"]),
    (
        ("round 68: ranking uses tokens learned from the corpus", 4),
        ["round", "68:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 68: ranking uses tokens learned from the corpus", 8),
        ["round", "68:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 68: ranking uses tokens learned from the corpus", 12),
        ["round 68:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 68: ranking uses tokens learned from the corpus", 16),
        ["round 68:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 68: ranking uses tokens learned from the corpus", 24),
        ["round 68: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 68: ranking uses tokens learned from the corpus", 32),
        ["round 68: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 68: a long session ends when the candle dies", 4),
        ["round", "68:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 68: a long session ends when the candle dies", 8),
        ["round", "68: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 68: a long session ends when the candle dies", 12),
        ["round 68: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 68: a long session ends when the candle dies", 16),
        ["round 68: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 68: a long session ends when the candle dies", 24),
        ["round 68: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 68: a long session ends when the candle dies", 32),
        ["round 68: a long session ends", "when the candle dies"],
    ),
    (
        ("round 68: encode the prompt then map the result", 4),
        ["round", "68:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 68: encode the prompt then map the result", 8),
        ["round", "68:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 68: encode the prompt then map the result", 12),
        ["round 68:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 68: encode the prompt then map the result", 16),
        ["round 68: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 68: encode the prompt then map the result", 24),
        ["round 68: encode the", "prompt then map the", "result"],
    ),
    (("round 68: encode the prompt then map the result", 32), ["round 68: encode the prompt then", "map the result"]),
    (
        ("round 68: the kernel wakes the worker at dawn", 4),
        ["round", "68:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 68: the kernel wakes the worker at dawn", 8),
        ["round", "68: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 68: the kernel wakes the worker at dawn", 12),
        ["round 68:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 68: the kernel wakes the worker at dawn", 16), ["round 68: the", "kernel wakes the", "worker at dawn"]),
    (("round 68: the kernel wakes the worker at dawn", 24), ["round 68: the kernel", "wakes the worker at dawn"]),
    (("round 68: the kernel wakes the worker at dawn", 32), ["round 68: the kernel wakes the", "worker at dawn"]),
    (
        ("round 68: service latency drops after the patch", 4),
        ["round", "68:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 68: service latency drops after the patch", 8),
        ["round", "68:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 68: service latency drops after the patch", 12),
        ["round 68:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 68: service latency drops after the patch", 16),
        ["round 68:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 68: service latency drops after the patch", 24),
        ["round 68: service", "latency drops after the", "patch"],
    ),
    (("round 68: service latency drops after the patch", 32), ["round 68: service latency drops", "after the patch"]),
    (
        ("round 68: the library caches every vector it sees", 4),
        ["round", "68:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 68: the library caches every vector it sees", 8),
        ["round", "68: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 68: the library caches every vector it sees", 12),
        ["round 68:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 68: the library caches every vector it sees", 16),
        ["round 68: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 68: the library caches every vector it sees", 24),
        ["round 68: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 68: the library caches every vector it sees", 32),
        ["round 68: the library caches", "every vector it sees"],
    ),
    (
        ("round 68: agents argue then the debate resolves", 4),
        ["round", "68:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 68: agents argue then the debate resolves", 8),
        ["round", "68:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 68: agents argue then the debate resolves", 12),
        ["round 68:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 68: agents argue then the debate resolves", 16),
        ["round 68: agents", "argue then the", "debate resolves"],
    ),
    (("round 68: agents argue then the debate resolves", 24), ["round 68: agents argue", "then the debate resolves"]),
    (("round 68: agents argue then the debate resolves", 32), ["round 68: agents argue then the", "debate resolves"]),
    (
        ("round 68: the filter keeps only strong matches", 4),
        ["round", "68:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 68: the filter keeps only strong matches", 8),
        ["round", "68: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 68: the filter keeps only strong matches", 12),
        ["round 68:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 68: the filter keeps only strong matches", 16),
        ["round 68: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 68: the filter keeps only strong matches", 24), ["round 68: the filter", "keeps only strong", "matches"]),
    (("round 68: the filter keeps only strong matches", 32), ["round 68: the filter keeps only", "strong matches"]),
    (
        ("round 68: the model answers with a short reply", 4),
        ["round", "68:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 68: the model answers with a short reply", 8),
        ["round", "68: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 68: the model answers with a short reply", 12),
        ["round 68:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 68: the model answers with a short reply", 16),
        ["round 68: the", "model answers", "with a short", "reply"],
    ),
    (("round 68: the model answers with a short reply", 24), ["round 68: the model", "answers with a short", "reply"]),
    (("round 68: the model answers with a short reply", 32), ["round 68: the model answers with", "a short reply"]),
    (
        ("round 68: the recorder stores the reasoning trace", 4),
        ["round", "68:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 68: the recorder stores the reasoning trace", 8),
        ["round", "68: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 68: the recorder stores the reasoning trace", 12),
        ["round 68:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 68: the recorder stores the reasoning trace", 16),
        ["round 68: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 68: the recorder stores the reasoning trace", 24),
        ["round 68: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 68: the recorder stores the reasoning trace", 32),
        ["round 68: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 68: the angel watches the processor run", 4),
        ["round", "68:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 68: the angel watches the processor run", 8),
        ["round", "68: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 68: the angel watches the processor run", 12),
        ["round 68:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 68: the angel watches the processor run", 16), ["round 68: the", "angel watches", "the processor", "run"]),
    (("round 68: the angel watches the processor run", 24), ["round 68: the angel", "watches the processor", "run"]),
    (("round 68: the angel watches the processor run", 32), ["round 68: the angel watches the", "processor run"]),
    (
        ("round 68: angle of the vector decides the match", 4),
        ["round", "68:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 68: angle of the vector decides the match", 8),
        ["round", "68:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 68: angle of the vector decides the match", 12),
        ["round 68:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 68: angle of the vector decides the match", 16),
        ["round 68: angle", "of the vector", "decides the", "match"],
    ),
    (("round 68: angle of the vector decides the match", 24), ["round 68: angle of the", "vector decides the match"]),
    (("round 68: angle of the vector decides the match", 32), ["round 68: angle of the vector", "decides the match"]),
    (
        ("round 68: the candle burns twice as long at night", 4),
        ["round", "68:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 68: the candle burns twice as long at night", 8),
        ["round", "68: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 68: the candle burns twice as long at night", 12),
        ["round 68:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 68: the candle burns twice as long at night", 16),
        ["round 68: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 68: the candle burns twice as long at night", 24),
        ["round 68: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 68: the candle burns twice as long at night", 32),
        ["round 68: the candle burns twice", "as long at night"],
    ),
    (
        ("round 68: a mirror of the universe in one line", 4),
        ["round", "68:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 68: a mirror of the universe in one line", 8),
        ["round", "68: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 68: a mirror of the universe in one line", 12),
        ["round 68: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 68: a mirror of the universe in one line", 16),
        ["round 68: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 68: a mirror of the universe in one line", 24), ["round 68: a mirror of", "the universe in one line"]),
    (("round 68: a mirror of the universe in one line", 32), ["round 68: a mirror of the", "universe in one line"]),
    (
        ("round 68: the queue drains before the storm", 4),
        ["round", "68:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 68: the queue drains before the storm", 8),
        ["round", "68: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 68: the queue drains before the storm", 12), ["round 68:", "the queue", "drains", "before the", "storm"]),
    (("round 68: the queue drains before the storm", 16), ["round 68: the", "queue drains", "before the storm"]),
    (("round 68: the queue drains before the storm", 24), ["round 68: the queue", "drains before the storm"]),
    (("round 68: the queue drains before the storm", 32), ["round 68: the queue drains", "before the storm"]),
    (
        ("kitten68 sitting68 agent68 angle68 universe68 memory68", 6),
        ["kitten68", "sitting68", "agent68", "angle68", "universe68", "memory68"],
    ),
    (
        ("kitten68 sitting68 agent68 angle68 universe68 memory68", 10),
        ["kitten68", "sitting68", "agent68", "angle68", "universe68", "memory68"],
    ),
    (
        ("kitten68 sitting68 agent68 angle68 universe68 memory68", 18),
        ["kitten68 sitting68", "agent68 angle68", "universe68", "memory68"],
    ),
    (
        ("kitten68 sitting68 agent68 angle68 universe68 memory68", 28),
        ["kitten68 sitting68 agent68", "angle68 universe68 memory68"],
    ),
    (
        ("sitting68 agent68 angle68 universe68 memory68 stream68", 6),
        ["sitting68", "agent68", "angle68", "universe68", "memory68", "stream68"],
    ),
    (
        ("sitting68 agent68 angle68 universe68 memory68 stream68", 10),
        ["sitting68", "agent68", "angle68", "universe68", "memory68", "stream68"],
    ),
    (
        ("sitting68 agent68 angle68 universe68 memory68 stream68", 18),
        ["sitting68 agent68", "angle68 universe68", "memory68 stream68"],
    ),
    (
        ("sitting68 agent68 angle68 universe68 memory68 stream68", 28),
        ["sitting68 agent68 angle68", "universe68 memory68 stream68"],
    ),
    (
        ("agent68 angle68 universe68 memory68 stream68 context68", 6),
        ["agent68", "angle68", "universe68", "memory68", "stream68", "context68"],
    ),
    (
        ("agent68 angle68 universe68 memory68 stream68 context68", 10),
        ["agent68", "angle68", "universe68", "memory68", "stream68", "context68"],
    ),
    (
        ("agent68 angle68 universe68 memory68 stream68 context68", 18),
        ["agent68 angle68", "universe68", "memory68 stream68", "context68"],
    ),
    (
        ("agent68 angle68 universe68 memory68 stream68 context68", 28),
        ["agent68 angle68 universe68", "memory68 stream68 context68"],
    ),
    (
        ("angle68 universe68 memory68 stream68 context68 knowledge68", 6),
        ["angle68", "universe68", "memory68", "stream68", "context68", "knowledge68"],
    ),
    (
        ("angle68 universe68 memory68 stream68 context68 knowledge68", 10),
        ["angle68", "universe68", "memory68", "stream68", "context68", "knowledge68"],
    ),
    (
        ("angle68 universe68 memory68 stream68 context68 knowledge68", 18),
        ["angle68 universe68", "memory68 stream68", "context68", "knowledge68"],
    ),
    (
        ("angle68 universe68 memory68 stream68 context68 knowledge68", 28),
        ["angle68 universe68 memory68", "stream68 context68", "knowledge68"],
    ),
    (
        ("universe68 memory68 stream68 context68 knowledge68 vector68", 6),
        ["universe68", "memory68", "stream68", "context68", "knowledge68", "vector68"],
    ),
    (
        ("universe68 memory68 stream68 context68 knowledge68 vector68", 10),
        ["universe68", "memory68", "stream68", "context68", "knowledge68", "vector68"],
    ),
    (
        ("universe68 memory68 stream68 context68 knowledge68 vector68", 18),
        ["universe68", "memory68 stream68", "context68", "knowledge68", "vector68"],
    ),
    (
        ("universe68 memory68 stream68 context68 knowledge68 vector68", 28),
        ["universe68 memory68 stream68", "context68 knowledge68", "vector68"],
    ),
    (
        ("memory68 stream68 context68 knowledge68 vector68 processor68", 6),
        ["memory68", "stream68", "context68", "knowledge68", "vector68", "processor68"],
    ),
    (
        ("memory68 stream68 context68 knowledge68 vector68 processor68", 10),
        ["memory68", "stream68", "context68", "knowledge68", "vector68", "processor68"],
    ),
    (
        ("memory68 stream68 context68 knowledge68 vector68 processor68", 18),
        ["memory68 stream68", "context68", "knowledge68", "vector68", "processor68"],
    ),
    (
        ("memory68 stream68 context68 knowledge68 vector68 processor68", 28),
        ["memory68 stream68 context68", "knowledge68 vector68", "processor68"],
    ),
    (
        ("stream68 context68 knowledge68 vector68 processor68 reasoning68", 6),
        ["stream68", "context68", "knowledge68", "vector68", "processor68", "reasoning68"],
    ),
    (
        ("stream68 context68 knowledge68 vector68 processor68 reasoning68", 10),
        ["stream68", "context68", "knowledge68", "vector68", "processor68", "reasoning68"],
    ),
    (
        ("stream68 context68 knowledge68 vector68 processor68 reasoning68", 18),
        ["stream68 context68", "knowledge68", "vector68", "processor68", "reasoning68"],
    ),
    (
        ("stream68 context68 knowledge68 vector68 processor68 reasoning68", 28),
        ["stream68 context68", "knowledge68 vector68", "processor68 reasoning68"],
    ),
    (
        ("context68 knowledge68 vector68 processor68 reasoning68 machine68", 6),
        ["context68", "knowledge68", "vector68", "processor68", "reasoning68", "machine68"],
    ),
    (
        ("context68 knowledge68 vector68 processor68 reasoning68 machine68", 10),
        ["context68", "knowledge68", "vector68", "processor68", "reasoning68", "machine68"],
    ),
    (
        ("context68 knowledge68 vector68 processor68 reasoning68 machine68", 18),
        ["context68", "knowledge68", "vector68", "processor68", "reasoning68", "machine68"],
    ),
    (
        ("context68 knowledge68 vector68 processor68 reasoning68 machine68", 28),
        ["context68 knowledge68", "vector68 processor68", "reasoning68 machine68"],
    ),
    (
        ("knowledge68 vector68 processor68 reasoning68 machine68 learning68", 6),
        ["knowledge68", "vector68", "processor68", "reasoning68", "machine68", "learning68"],
    ),
    (
        ("knowledge68 vector68 processor68 reasoning68 machine68 learning68", 10),
        ["knowledge68", "vector68", "processor68", "reasoning68", "machine68", "learning68"],
    ),
    (
        ("knowledge68 vector68 processor68 reasoning68 machine68 learning68", 18),
        ["knowledge68", "vector68", "processor68", "reasoning68", "machine68", "learning68"],
    ),
    (
        ("knowledge68 vector68 processor68 reasoning68 machine68 learning68", 28),
        ["knowledge68 vector68", "processor68 reasoning68", "machine68 learning68"],
    ),
    (
        ("vector68 processor68 reasoning68 machine68 learning68 model68", 6),
        ["vector68", "processor68", "reasoning68", "machine68", "learning68", "model68"],
    ),
    (
        ("vector68 processor68 reasoning68 machine68 learning68 model68", 10),
        ["vector68", "processor68", "reasoning68", "machine68", "learning68", "model68"],
    ),
    (
        ("vector68 processor68 reasoning68 machine68 learning68 model68", 18),
        ["vector68", "processor68", "reasoning68", "machine68", "learning68 model68"],
    ),
    (
        ("vector68 processor68 reasoning68 machine68 learning68 model68", 28),
        ["vector68 processor68", "reasoning68 machine68", "learning68 model68"],
    ),
    (
        ("processor68 reasoning68 machine68 learning68 model68 token68", 6),
        ["processor68", "reasoning68", "machine68", "learning68", "model68", "token68"],
    ),
    (
        ("processor68 reasoning68 machine68 learning68 model68 token68", 10),
        ["processor68", "reasoning68", "machine68", "learning68", "model68", "token68"],
    ),
    (
        ("processor68 reasoning68 machine68 learning68 model68 token68", 18),
        ["processor68", "reasoning68", "machine68", "learning68 model68", "token68"],
    ),
    (
        ("processor68 reasoning68 machine68 learning68 model68 token68", 28),
        ["processor68 reasoning68", "machine68 learning68 model68", "token68"],
    ),
    (
        ("reasoning68 machine68 learning68 model68 token68 prompt68", 6),
        ["reasoning68", "machine68", "learning68", "model68", "token68", "prompt68"],
    ),
    (
        ("reasoning68 machine68 learning68 model68 token68 prompt68", 10),
        ["reasoning68", "machine68", "learning68", "model68", "token68", "prompt68"],
    ),
    (
        ("reasoning68 machine68 learning68 model68 token68 prompt68", 18),
        ["reasoning68", "machine68", "learning68 model68", "token68 prompt68"],
    ),
    (
        ("reasoning68 machine68 learning68 model68 token68 prompt68", 28),
        ["reasoning68 machine68", "learning68 model68 token68", "prompt68"],
    ),
    (
        ("machine68 learning68 model68 token68 prompt68 session68", 6),
        ["machine68", "learning68", "model68", "token68", "prompt68", "session68"],
    ),
    (
        ("machine68 learning68 model68 token68 prompt68 session68", 10),
        ["machine68", "learning68", "model68", "token68", "prompt68", "session68"],
    ),
    (
        ("machine68 learning68 model68 token68 prompt68 session68", 18),
        ["machine68", "learning68 model68", "token68 prompt68", "session68"],
    ),
    (
        ("machine68 learning68 model68 token68 prompt68 session68", 28),
        ["machine68 learning68 model68", "token68 prompt68 session68"],
    ),
    (
        ("learning68 model68 token68 prompt68 session68 library68", 6),
        ["learning68", "model68", "token68", "prompt68", "session68", "library68"],
    ),
    (
        ("learning68 model68 token68 prompt68 session68 library68", 10),
        ["learning68", "model68", "token68", "prompt68", "session68", "library68"],
    ),
    (
        ("learning68 model68 token68 prompt68 session68 library68", 18),
        ["learning68 model68", "token68 prompt68", "session68", "library68"],
    ),
    (
        ("learning68 model68 token68 prompt68 session68 library68", 28),
        ["learning68 model68 token68", "prompt68 session68 library68"],
    ),
    (
        ("model68 token68 prompt68 session68 library68 service68", 6),
        ["model68", "token68", "prompt68", "session68", "library68", "service68"],
    ),
    (
        ("model68 token68 prompt68 session68 library68 service68", 10),
        ["model68", "token68", "prompt68", "session68", "library68", "service68"],
    ),
    (
        ("model68 token68 prompt68 session68 library68 service68", 18),
        ["model68 token68", "prompt68 session68", "library68", "service68"],
    ),
    (
        ("model68 token68 prompt68 session68 library68 service68", 28),
        ["model68 token68 prompt68", "session68 library68", "service68"],
    ),
    (
        ("token68 prompt68 session68 library68 service68 gateway68", 6),
        ["token68", "prompt68", "session68", "library68", "service68", "gateway68"],
    ),
    (
        ("token68 prompt68 session68 library68 service68 gateway68", 10),
        ["token68", "prompt68", "session68", "library68", "service68", "gateway68"],
    ),
    (
        ("token68 prompt68 session68 library68 service68 gateway68", 18),
        ["token68 prompt68", "session68", "library68", "service68", "gateway68"],
    ),
    (
        ("token68 prompt68 session68 library68 service68 gateway68", 28),
        ["token68 prompt68 session68", "library68 service68", "gateway68"],
    ),
    (
        ("prompt68 session68 library68 service68 gateway68 storage68", 6),
        ["prompt68", "session68", "library68", "service68", "gateway68", "storage68"],
    ),
    (
        ("prompt68 session68 library68 service68 gateway68 storage68", 10),
        ["prompt68", "session68", "library68", "service68", "gateway68", "storage68"],
    ),
    (
        ("prompt68 session68 library68 service68 gateway68 storage68", 18),
        ["prompt68 session68", "library68", "service68", "gateway68", "storage68"],
    ),
    (
        ("prompt68 session68 library68 service68 gateway68 storage68", 28),
        ["prompt68 session68 library68", "service68 gateway68", "storage68"],
    ),
    (
        ("session68 library68 service68 gateway68 storage68 network68", 6),
        ["session68", "library68", "service68", "gateway68", "storage68", "network68"],
    ),
    (
        ("session68 library68 service68 gateway68 storage68 network68", 10),
        ["session68", "library68", "service68", "gateway68", "storage68", "network68"],
    ),
    (
        ("session68 library68 service68 gateway68 storage68 network68", 18),
        ["session68", "library68", "service68", "gateway68", "storage68", "network68"],
    ),
    (
        ("session68 library68 service68 gateway68 storage68 network68", 28),
        ["session68 library68", "service68 gateway68", "storage68 network68"],
    ),
    (
        ("library68 service68 gateway68 storage68 network68 latency68", 6),
        ["library68", "service68", "gateway68", "storage68", "network68", "latency68"],
    ),
    (
        ("library68 service68 gateway68 storage68 network68 latency68", 10),
        ["library68", "service68", "gateway68", "storage68", "network68", "latency68"],
    ),
    (
        ("library68 service68 gateway68 storage68 network68 latency68", 18),
        ["library68", "service68", "gateway68", "storage68", "network68", "latency68"],
    ),
    (
        ("library68 service68 gateway68 storage68 network68 latency68", 28),
        ["library68 service68", "gateway68 storage68", "network68 latency68"],
    ),
    (
        ("service68 gateway68 storage68 network68 latency68 buffer68", 6),
        ["service68", "gateway68", "storage68", "network68", "latency68", "buffer68"],
    ),
    (
        ("service68 gateway68 storage68 network68 latency68 buffer68", 10),
        ["service68", "gateway68", "storage68", "network68", "latency68", "buffer68"],
    ),
    (
        ("service68 gateway68 storage68 network68 latency68 buffer68", 18),
        ["service68", "gateway68", "storage68", "network68", "latency68 buffer68"],
    ),
    (
        ("service68 gateway68 storage68 network68 latency68 buffer68", 28),
        ["service68 gateway68", "storage68 network68", "latency68 buffer68"],
    ),
    (
        ("gateway68 storage68 network68 latency68 buffer68 queue68", 6),
        ["gateway68", "storage68", "network68", "latency68", "buffer68", "queue68"],
    ),
    (
        ("gateway68 storage68 network68 latency68 buffer68 queue68", 10),
        ["gateway68", "storage68", "network68", "latency68", "buffer68", "queue68"],
    ),
    (
        ("gateway68 storage68 network68 latency68 buffer68 queue68", 18),
        ["gateway68", "storage68", "network68", "latency68 buffer68", "queue68"],
    ),
    (
        ("gateway68 storage68 network68 latency68 buffer68 queue68", 28),
        ["gateway68 storage68", "network68 latency68 buffer68", "queue68"],
    ),
    (
        ("storage68 network68 latency68 buffer68 queue68 worker68", 6),
        ["storage68", "network68", "latency68", "buffer68", "queue68", "worker68"],
    ),
    (
        ("storage68 network68 latency68 buffer68 queue68 worker68", 10),
        ["storage68", "network68", "latency68", "buffer68", "queue68", "worker68"],
    ),
    (
        ("storage68 network68 latency68 buffer68 queue68 worker68", 18),
        ["storage68", "network68", "latency68 buffer68", "queue68 worker68"],
    ),
    (
        ("storage68 network68 latency68 buffer68 queue68 worker68", 28),
        ["storage68 network68", "latency68 buffer68 queue68", "worker68"],
    ),
    (
        ("network68 latency68 buffer68 queue68 worker68 kernel68", 6),
        ["network68", "latency68", "buffer68", "queue68", "worker68", "kernel68"],
    ),
    (
        ("network68 latency68 buffer68 queue68 worker68 kernel68", 10),
        ["network68", "latency68", "buffer68", "queue68", "worker68", "kernel68"],
    ),
    (
        ("network68 latency68 buffer68 queue68 worker68 kernel68", 18),
        ["network68", "latency68 buffer68", "queue68 worker68", "kernel68"],
    ),
    (
        ("network68 latency68 buffer68 queue68 worker68 kernel68", 28),
        ["network68 latency68 buffer68", "queue68 worker68 kernel68"],
    ),
    (
        ("latency68 buffer68 queue68 worker68 kernel68 signal68", 6),
        ["latency68", "buffer68", "queue68", "worker68", "kernel68", "signal68"],
    ),
    (
        ("latency68 buffer68 queue68 worker68 kernel68 signal68", 10),
        ["latency68", "buffer68", "queue68", "worker68", "kernel68", "signal68"],
    ),
    (
        ("latency68 buffer68 queue68 worker68 kernel68 signal68", 18),
        ["latency68 buffer68", "queue68 worker68", "kernel68 signal68"],
    ),
    (
        ("latency68 buffer68 queue68 worker68 kernel68 signal68", 28),
        ["latency68 buffer68 queue68", "worker68 kernel68 signal68"],
    ),
    (
        ("buffer68 queue68 worker68 kernel68 signal68 packet68", 6),
        ["buffer68", "queue68", "worker68", "kernel68", "signal68", "packet68"],
    ),
    (
        ("buffer68 queue68 worker68 kernel68 signal68 packet68", 10),
        ["buffer68", "queue68", "worker68", "kernel68", "signal68", "packet68"],
    ),
    (
        ("buffer68 queue68 worker68 kernel68 signal68 packet68", 18),
        ["buffer68 queue68", "worker68 kernel68", "signal68 packet68"],
    ),
    (
        ("buffer68 queue68 worker68 kernel68 signal68 packet68", 28),
        ["buffer68 queue68 worker68", "kernel68 signal68 packet68"],
    ),
    (
        ("queue68 worker68 kernel68 signal68 packet68 router68", 6),
        ["queue68", "worker68", "kernel68", "signal68", "packet68", "router68"],
    ),
    (
        ("queue68 worker68 kernel68 signal68 packet68 router68", 10),
        ["queue68", "worker68", "kernel68", "signal68", "packet68", "router68"],
    ),
    (
        ("queue68 worker68 kernel68 signal68 packet68 router68", 18),
        ["queue68 worker68", "kernel68 signal68", "packet68 router68"],
    ),
    (
        ("queue68 worker68 kernel68 signal68 packet68 router68", 28),
        ["queue68 worker68 kernel68", "signal68 packet68 router68"],
    ),
    (
        ("worker68 kernel68 signal68 packet68 router68 cluster68", 6),
        ["worker68", "kernel68", "signal68", "packet68", "router68", "cluster68"],
    ),
    (
        ("worker68 kernel68 signal68 packet68 router68 cluster68", 10),
        ["worker68", "kernel68", "signal68", "packet68", "router68", "cluster68"],
    ),
    (
        ("worker68 kernel68 signal68 packet68 router68 cluster68", 18),
        ["worker68 kernel68", "signal68 packet68", "router68 cluster68"],
    ),
    (
        ("worker68 kernel68 signal68 packet68 router68 cluster68", 28),
        ["worker68 kernel68 signal68", "packet68 router68 cluster68"],
    ),
    (
        ("kernel68 signal68 packet68 router68 cluster68 mirror68", 6),
        ["kernel68", "signal68", "packet68", "router68", "cluster68", "mirror68"],
    ),
    (
        ("kernel68 signal68 packet68 router68 cluster68 mirror68", 10),
        ["kernel68", "signal68", "packet68", "router68", "cluster68", "mirror68"],
    ),
    (
        ("kernel68 signal68 packet68 router68 cluster68 mirror68", 18),
        ["kernel68 signal68", "packet68 router68", "cluster68 mirror68"],
    ),
    (
        ("kernel68 signal68 packet68 router68 cluster68 mirror68", 28),
        ["kernel68 signal68 packet68", "router68 cluster68 mirror68"],
    ),
    (
        ("signal68 packet68 router68 cluster68 mirror68 filter68", 6),
        ["signal68", "packet68", "router68", "cluster68", "mirror68", "filter68"],
    ),
    (
        ("signal68 packet68 router68 cluster68 mirror68 filter68", 10),
        ["signal68", "packet68", "router68", "cluster68", "mirror68", "filter68"],
    ),
    (
        ("signal68 packet68 router68 cluster68 mirror68 filter68", 18),
        ["signal68 packet68", "router68 cluster68", "mirror68 filter68"],
    ),
    (
        ("signal68 packet68 router68 cluster68 mirror68 filter68", 28),
        ["signal68 packet68 router68", "cluster68 mirror68 filter68"],
    ),
    (
        ("packet68 router68 cluster68 mirror68 filter68 ranking68", 6),
        ["packet68", "router68", "cluster68", "mirror68", "filter68", "ranking68"],
    ),
    (
        ("packet68 router68 cluster68 mirror68 filter68 ranking68", 10),
        ["packet68", "router68", "cluster68", "mirror68", "filter68", "ranking68"],
    ),
    (
        ("packet68 router68 cluster68 mirror68 filter68 ranking68", 18),
        ["packet68 router68", "cluster68 mirror68", "filter68 ranking68"],
    ),
    (
        ("packet68 router68 cluster68 mirror68 filter68 ranking68", 28),
        ["packet68 router68 cluster68", "mirror68 filter68 ranking68"],
    ),
    (
        ("router68 cluster68 mirror68 filter68 ranking68 encoding68", 6),
        ["router68", "cluster68", "mirror68", "filter68", "ranking68", "encoding68"],
    ),
    (
        ("router68 cluster68 mirror68 filter68 ranking68 encoding68", 10),
        ["router68", "cluster68", "mirror68", "filter68", "ranking68", "encoding68"],
    ),
    (
        ("router68 cluster68 mirror68 filter68 ranking68 encoding68", 18),
        ["router68 cluster68", "mirror68 filter68", "ranking68", "encoding68"],
    ),
    (
        ("router68 cluster68 mirror68 filter68 ranking68 encoding68", 28),
        ["router68 cluster68 mirror68", "filter68 ranking68", "encoding68"],
    ),
    (
        ("cluster68 mirror68 filter68 ranking68 encoding68 mapping68", 6),
        ["cluster68", "mirror68", "filter68", "ranking68", "encoding68", "mapping68"],
    ),
    (
        ("cluster68 mirror68 filter68 ranking68 encoding68 mapping68", 10),
        ["cluster68", "mirror68", "filter68", "ranking68", "encoding68", "mapping68"],
    ),
    (
        ("cluster68 mirror68 filter68 ranking68 encoding68 mapping68", 18),
        ["cluster68 mirror68", "filter68 ranking68", "encoding68", "mapping68"],
    ),
    (
        ("cluster68 mirror68 filter68 ranking68 encoding68 mapping68", 28),
        ["cluster68 mirror68 filter68", "ranking68 encoding68", "mapping68"],
    ),
    (
        ("mirror68 filter68 ranking68 encoding68 mapping68 record68", 6),
        ["mirror68", "filter68", "ranking68", "encoding68", "mapping68", "record68"],
    ),
    (
        ("mirror68 filter68 ranking68 encoding68 mapping68 record68", 10),
        ["mirror68", "filter68", "ranking68", "encoding68", "mapping68", "record68"],
    ),
    (
        ("mirror68 filter68 ranking68 encoding68 mapping68 record68", 18),
        ["mirror68 filter68", "ranking68", "encoding68", "mapping68 record68"],
    ),
    (
        ("mirror68 filter68 ranking68 encoding68 mapping68 record68", 28),
        ["mirror68 filter68 ranking68", "encoding68 mapping68", "record68"],
    ),
    (
        ("filter68 ranking68 encoding68 mapping68 record68 candle68", 6),
        ["filter68", "ranking68", "encoding68", "mapping68", "record68", "candle68"],
    ),
    (
        ("filter68 ranking68 encoding68 mapping68 record68 candle68", 10),
        ["filter68", "ranking68", "encoding68", "mapping68", "record68", "candle68"],
    ),
    (
        ("filter68 ranking68 encoding68 mapping68 record68 candle68", 18),
        ["filter68 ranking68", "encoding68", "mapping68 record68", "candle68"],
    ),
    (
        ("filter68 ranking68 encoding68 mapping68 record68 candle68", 28),
        ["filter68 ranking68", "encoding68 mapping68", "record68 candle68"],
    ),
    (
        ("ranking68 encoding68 mapping68 record68 candle68 thread68", 6),
        ["ranking68", "encoding68", "mapping68", "record68", "candle68", "thread68"],
    ),
    (
        ("ranking68 encoding68 mapping68 record68 candle68 thread68", 10),
        ["ranking68", "encoding68", "mapping68", "record68", "candle68", "thread68"],
    ),
    (
        ("ranking68 encoding68 mapping68 record68 candle68 thread68", 18),
        ["ranking68", "encoding68", "mapping68 record68", "candle68 thread68"],
    ),
    (
        ("ranking68 encoding68 mapping68 record68 candle68 thread68", 28),
        ["ranking68 encoding68", "mapping68 record68 candle68", "thread68"],
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
