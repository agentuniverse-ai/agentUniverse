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
        ("round 44: the quick brown fox jumps over the lazy dog", 4),
        ["round", "44:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 44: the quick brown fox jumps over the lazy dog", 8),
        ["round", "44: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 44: the quick brown fox jumps over the lazy dog", 12),
        ["round 44:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 44: the quick brown fox jumps over the lazy dog", 16),
        ["round 44: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 44: the quick brown fox jumps over the lazy dog", 24),
        ["round 44: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 44: the quick brown fox jumps over the lazy dog", 32),
        ["round 44: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 44: agentuniverse is a framework for multi agents", 4),
        ["round", "44:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 44: agentuniverse is a framework for multi agents", 8),
        ["round", "44:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 44: agentuniverse is a framework for multi agents", 12),
        ["round 44:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 44: agentuniverse is a framework for multi agents", 16),
        ["round 44:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 44: agentuniverse is a framework for multi agents", 24),
        ["round 44: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 44: agentuniverse is a framework for multi agents", 32),
        ["round 44: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 44: knowledge stored as vectors enables retrieval", 4),
        ["round", "44:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 44: knowledge stored as vectors enables retrieval", 8),
        ["round", "44:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 44: knowledge stored as vectors enables retrieval", 12),
        ["round 44:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 44: knowledge stored as vectors enables retrieval", 16),
        ["round 44:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 44: knowledge stored as vectors enables retrieval", 24),
        ["round 44: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 44: knowledge stored as vectors enables retrieval", 32),
        ["round 44: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 44: the processor reads the record then stops", 4),
        ["round", "44:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 44: the processor reads the record then stops", 8),
        ["round", "44: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 44: the processor reads the record then stops", 12),
        ["round 44:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 44: the processor reads the record then stops", 16),
        ["round 44: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 44: the processor reads the record then stops", 24),
        ["round 44: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 44: the processor reads the record then stops", 32),
        ["round 44: the processor reads", "the record then stops"],
    ),
    (
        ("round 44: a worker pulls the next task from the queue", 4),
        ["round", "44:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 44: a worker pulls the next task from the queue", 8),
        ["round", "44: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 44: a worker pulls the next task from the queue", 12),
        ["round 44: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 44: a worker pulls the next task from the queue", 16),
        ["round 44: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 44: a worker pulls the next task from the queue", 24),
        ["round 44: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 44: a worker pulls the next task from the queue", 32),
        ["round 44: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 44: signals travel through the network layer", 4),
        ["round", "44:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 44: signals travel through the network layer", 8),
        ["round", "44:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 44: signals travel through the network layer", 12),
        ["round 44:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 44: signals travel through the network layer", 16),
        ["round 44:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 44: signals travel through the network layer", 24),
        ["round 44: signals travel", "through the network", "layer"],
    ),
    (
        ("round 44: signals travel through the network layer", 32),
        ["round 44: signals travel through", "the network layer"],
    ),
    (
        ("round 44: the gateway routes each request by policy", 4),
        ["round", "44:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 44: the gateway routes each request by policy", 8),
        ["round", "44: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 44: the gateway routes each request by policy", 12),
        ["round 44:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 44: the gateway routes each request by policy", 16),
        ["round 44: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 44: the gateway routes each request by policy", 24),
        ["round 44: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 44: the gateway routes each request by policy", 32),
        ["round 44: the gateway routes", "each request by policy"],
    ),
    (
        ("round 44: memory grows until the buffer is full", 4),
        ["round", "44:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 44: memory grows until the buffer is full", 8),
        ["round", "44:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 44: memory grows until the buffer is full", 12),
        ["round 44:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 44: memory grows until the buffer is full", 16),
        ["round 44: memory", "grows until the", "buffer is full"],
    ),
    (("round 44: memory grows until the buffer is full", 24), ["round 44: memory grows", "until the buffer is full"]),
    (("round 44: memory grows until the buffer is full", 32), ["round 44: memory grows until the", "buffer is full"]),
    (
        ("round 44: the cluster mirrors every packet twice", 4),
        ["round", "44:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 44: the cluster mirrors every packet twice", 8),
        ["round", "44: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 44: the cluster mirrors every packet twice", 12),
        ["round 44:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 44: the cluster mirrors every packet twice", 16),
        ["round 44: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 44: the cluster mirrors every packet twice", 24),
        ["round 44: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 44: the cluster mirrors every packet twice", 32), ["round 44: the cluster mirrors", "every packet twice"]),
    (
        ("round 44: ranking uses tokens learned from the corpus", 4),
        ["round", "44:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 44: ranking uses tokens learned from the corpus", 8),
        ["round", "44:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 44: ranking uses tokens learned from the corpus", 12),
        ["round 44:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 44: ranking uses tokens learned from the corpus", 16),
        ["round 44:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 44: ranking uses tokens learned from the corpus", 24),
        ["round 44: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 44: ranking uses tokens learned from the corpus", 32),
        ["round 44: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 44: a long session ends when the candle dies", 4),
        ["round", "44:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 44: a long session ends when the candle dies", 8),
        ["round", "44: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 44: a long session ends when the candle dies", 12),
        ["round 44: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 44: a long session ends when the candle dies", 16),
        ["round 44: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 44: a long session ends when the candle dies", 24),
        ["round 44: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 44: a long session ends when the candle dies", 32),
        ["round 44: a long session ends", "when the candle dies"],
    ),
    (
        ("round 44: encode the prompt then map the result", 4),
        ["round", "44:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 44: encode the prompt then map the result", 8),
        ["round", "44:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 44: encode the prompt then map the result", 12),
        ["round 44:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 44: encode the prompt then map the result", 16),
        ["round 44: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 44: encode the prompt then map the result", 24),
        ["round 44: encode the", "prompt then map the", "result"],
    ),
    (("round 44: encode the prompt then map the result", 32), ["round 44: encode the prompt then", "map the result"]),
    (
        ("round 44: the kernel wakes the worker at dawn", 4),
        ["round", "44:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 44: the kernel wakes the worker at dawn", 8),
        ["round", "44: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 44: the kernel wakes the worker at dawn", 12),
        ["round 44:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 44: the kernel wakes the worker at dawn", 16), ["round 44: the", "kernel wakes the", "worker at dawn"]),
    (("round 44: the kernel wakes the worker at dawn", 24), ["round 44: the kernel", "wakes the worker at dawn"]),
    (("round 44: the kernel wakes the worker at dawn", 32), ["round 44: the kernel wakes the", "worker at dawn"]),
    (
        ("round 44: service latency drops after the patch", 4),
        ["round", "44:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 44: service latency drops after the patch", 8),
        ["round", "44:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 44: service latency drops after the patch", 12),
        ["round 44:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 44: service latency drops after the patch", 16),
        ["round 44:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 44: service latency drops after the patch", 24),
        ["round 44: service", "latency drops after the", "patch"],
    ),
    (("round 44: service latency drops after the patch", 32), ["round 44: service latency drops", "after the patch"]),
    (
        ("round 44: the library caches every vector it sees", 4),
        ["round", "44:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 44: the library caches every vector it sees", 8),
        ["round", "44: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 44: the library caches every vector it sees", 12),
        ["round 44:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 44: the library caches every vector it sees", 16),
        ["round 44: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 44: the library caches every vector it sees", 24),
        ["round 44: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 44: the library caches every vector it sees", 32),
        ["round 44: the library caches", "every vector it sees"],
    ),
    (
        ("round 44: agents argue then the debate resolves", 4),
        ["round", "44:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 44: agents argue then the debate resolves", 8),
        ["round", "44:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 44: agents argue then the debate resolves", 12),
        ["round 44:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 44: agents argue then the debate resolves", 16),
        ["round 44: agents", "argue then the", "debate resolves"],
    ),
    (("round 44: agents argue then the debate resolves", 24), ["round 44: agents argue", "then the debate resolves"]),
    (("round 44: agents argue then the debate resolves", 32), ["round 44: agents argue then the", "debate resolves"]),
    (
        ("round 44: the filter keeps only strong matches", 4),
        ["round", "44:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 44: the filter keeps only strong matches", 8),
        ["round", "44: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 44: the filter keeps only strong matches", 12),
        ["round 44:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 44: the filter keeps only strong matches", 16),
        ["round 44: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 44: the filter keeps only strong matches", 24), ["round 44: the filter", "keeps only strong", "matches"]),
    (("round 44: the filter keeps only strong matches", 32), ["round 44: the filter keeps only", "strong matches"]),
    (
        ("round 44: the model answers with a short reply", 4),
        ["round", "44:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 44: the model answers with a short reply", 8),
        ["round", "44: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 44: the model answers with a short reply", 12),
        ["round 44:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 44: the model answers with a short reply", 16),
        ["round 44: the", "model answers", "with a short", "reply"],
    ),
    (("round 44: the model answers with a short reply", 24), ["round 44: the model", "answers with a short", "reply"]),
    (("round 44: the model answers with a short reply", 32), ["round 44: the model answers with", "a short reply"]),
    (
        ("round 44: the recorder stores the reasoning trace", 4),
        ["round", "44:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 44: the recorder stores the reasoning trace", 8),
        ["round", "44: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 44: the recorder stores the reasoning trace", 12),
        ["round 44:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 44: the recorder stores the reasoning trace", 16),
        ["round 44: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 44: the recorder stores the reasoning trace", 24),
        ["round 44: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 44: the recorder stores the reasoning trace", 32),
        ["round 44: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 44: the angel watches the processor run", 4),
        ["round", "44:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 44: the angel watches the processor run", 8),
        ["round", "44: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 44: the angel watches the processor run", 12),
        ["round 44:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 44: the angel watches the processor run", 16), ["round 44: the", "angel watches", "the processor", "run"]),
    (("round 44: the angel watches the processor run", 24), ["round 44: the angel", "watches the processor", "run"]),
    (("round 44: the angel watches the processor run", 32), ["round 44: the angel watches the", "processor run"]),
    (
        ("round 44: angle of the vector decides the match", 4),
        ["round", "44:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 44: angle of the vector decides the match", 8),
        ["round", "44:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 44: angle of the vector decides the match", 12),
        ["round 44:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 44: angle of the vector decides the match", 16),
        ["round 44: angle", "of the vector", "decides the", "match"],
    ),
    (("round 44: angle of the vector decides the match", 24), ["round 44: angle of the", "vector decides the match"]),
    (("round 44: angle of the vector decides the match", 32), ["round 44: angle of the vector", "decides the match"]),
    (
        ("round 44: the candle burns twice as long at night", 4),
        ["round", "44:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 44: the candle burns twice as long at night", 8),
        ["round", "44: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 44: the candle burns twice as long at night", 12),
        ["round 44:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 44: the candle burns twice as long at night", 16),
        ["round 44: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 44: the candle burns twice as long at night", 24),
        ["round 44: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 44: the candle burns twice as long at night", 32),
        ["round 44: the candle burns twice", "as long at night"],
    ),
    (
        ("round 44: a mirror of the universe in one line", 4),
        ["round", "44:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 44: a mirror of the universe in one line", 8),
        ["round", "44: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 44: a mirror of the universe in one line", 12),
        ["round 44: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 44: a mirror of the universe in one line", 16),
        ["round 44: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 44: a mirror of the universe in one line", 24), ["round 44: a mirror of", "the universe in one line"]),
    (("round 44: a mirror of the universe in one line", 32), ["round 44: a mirror of the", "universe in one line"]),
    (
        ("round 44: the queue drains before the storm", 4),
        ["round", "44:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 44: the queue drains before the storm", 8),
        ["round", "44: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 44: the queue drains before the storm", 12), ["round 44:", "the queue", "drains", "before the", "storm"]),
    (("round 44: the queue drains before the storm", 16), ["round 44: the", "queue drains", "before the storm"]),
    (("round 44: the queue drains before the storm", 24), ["round 44: the queue", "drains before the storm"]),
    (("round 44: the queue drains before the storm", 32), ["round 44: the queue drains", "before the storm"]),
    (
        ("kitten44 sitting44 agent44 angle44 universe44 memory44", 6),
        ["kitten44", "sitting44", "agent44", "angle44", "universe44", "memory44"],
    ),
    (
        ("kitten44 sitting44 agent44 angle44 universe44 memory44", 10),
        ["kitten44", "sitting44", "agent44", "angle44", "universe44", "memory44"],
    ),
    (
        ("kitten44 sitting44 agent44 angle44 universe44 memory44", 18),
        ["kitten44 sitting44", "agent44 angle44", "universe44", "memory44"],
    ),
    (
        ("kitten44 sitting44 agent44 angle44 universe44 memory44", 28),
        ["kitten44 sitting44 agent44", "angle44 universe44 memory44"],
    ),
    (
        ("sitting44 agent44 angle44 universe44 memory44 stream44", 6),
        ["sitting44", "agent44", "angle44", "universe44", "memory44", "stream44"],
    ),
    (
        ("sitting44 agent44 angle44 universe44 memory44 stream44", 10),
        ["sitting44", "agent44", "angle44", "universe44", "memory44", "stream44"],
    ),
    (
        ("sitting44 agent44 angle44 universe44 memory44 stream44", 18),
        ["sitting44 agent44", "angle44 universe44", "memory44 stream44"],
    ),
    (
        ("sitting44 agent44 angle44 universe44 memory44 stream44", 28),
        ["sitting44 agent44 angle44", "universe44 memory44 stream44"],
    ),
    (
        ("agent44 angle44 universe44 memory44 stream44 context44", 6),
        ["agent44", "angle44", "universe44", "memory44", "stream44", "context44"],
    ),
    (
        ("agent44 angle44 universe44 memory44 stream44 context44", 10),
        ["agent44", "angle44", "universe44", "memory44", "stream44", "context44"],
    ),
    (
        ("agent44 angle44 universe44 memory44 stream44 context44", 18),
        ["agent44 angle44", "universe44", "memory44 stream44", "context44"],
    ),
    (
        ("agent44 angle44 universe44 memory44 stream44 context44", 28),
        ["agent44 angle44 universe44", "memory44 stream44 context44"],
    ),
    (
        ("angle44 universe44 memory44 stream44 context44 knowledge44", 6),
        ["angle44", "universe44", "memory44", "stream44", "context44", "knowledge44"],
    ),
    (
        ("angle44 universe44 memory44 stream44 context44 knowledge44", 10),
        ["angle44", "universe44", "memory44", "stream44", "context44", "knowledge44"],
    ),
    (
        ("angle44 universe44 memory44 stream44 context44 knowledge44", 18),
        ["angle44 universe44", "memory44 stream44", "context44", "knowledge44"],
    ),
    (
        ("angle44 universe44 memory44 stream44 context44 knowledge44", 28),
        ["angle44 universe44 memory44", "stream44 context44", "knowledge44"],
    ),
    (
        ("universe44 memory44 stream44 context44 knowledge44 vector44", 6),
        ["universe44", "memory44", "stream44", "context44", "knowledge44", "vector44"],
    ),
    (
        ("universe44 memory44 stream44 context44 knowledge44 vector44", 10),
        ["universe44", "memory44", "stream44", "context44", "knowledge44", "vector44"],
    ),
    (
        ("universe44 memory44 stream44 context44 knowledge44 vector44", 18),
        ["universe44", "memory44 stream44", "context44", "knowledge44", "vector44"],
    ),
    (
        ("universe44 memory44 stream44 context44 knowledge44 vector44", 28),
        ["universe44 memory44 stream44", "context44 knowledge44", "vector44"],
    ),
    (
        ("memory44 stream44 context44 knowledge44 vector44 processor44", 6),
        ["memory44", "stream44", "context44", "knowledge44", "vector44", "processor44"],
    ),
    (
        ("memory44 stream44 context44 knowledge44 vector44 processor44", 10),
        ["memory44", "stream44", "context44", "knowledge44", "vector44", "processor44"],
    ),
    (
        ("memory44 stream44 context44 knowledge44 vector44 processor44", 18),
        ["memory44 stream44", "context44", "knowledge44", "vector44", "processor44"],
    ),
    (
        ("memory44 stream44 context44 knowledge44 vector44 processor44", 28),
        ["memory44 stream44 context44", "knowledge44 vector44", "processor44"],
    ),
    (
        ("stream44 context44 knowledge44 vector44 processor44 reasoning44", 6),
        ["stream44", "context44", "knowledge44", "vector44", "processor44", "reasoning44"],
    ),
    (
        ("stream44 context44 knowledge44 vector44 processor44 reasoning44", 10),
        ["stream44", "context44", "knowledge44", "vector44", "processor44", "reasoning44"],
    ),
    (
        ("stream44 context44 knowledge44 vector44 processor44 reasoning44", 18),
        ["stream44 context44", "knowledge44", "vector44", "processor44", "reasoning44"],
    ),
    (
        ("stream44 context44 knowledge44 vector44 processor44 reasoning44", 28),
        ["stream44 context44", "knowledge44 vector44", "processor44 reasoning44"],
    ),
    (
        ("context44 knowledge44 vector44 processor44 reasoning44 machine44", 6),
        ["context44", "knowledge44", "vector44", "processor44", "reasoning44", "machine44"],
    ),
    (
        ("context44 knowledge44 vector44 processor44 reasoning44 machine44", 10),
        ["context44", "knowledge44", "vector44", "processor44", "reasoning44", "machine44"],
    ),
    (
        ("context44 knowledge44 vector44 processor44 reasoning44 machine44", 18),
        ["context44", "knowledge44", "vector44", "processor44", "reasoning44", "machine44"],
    ),
    (
        ("context44 knowledge44 vector44 processor44 reasoning44 machine44", 28),
        ["context44 knowledge44", "vector44 processor44", "reasoning44 machine44"],
    ),
    (
        ("knowledge44 vector44 processor44 reasoning44 machine44 learning44", 6),
        ["knowledge44", "vector44", "processor44", "reasoning44", "machine44", "learning44"],
    ),
    (
        ("knowledge44 vector44 processor44 reasoning44 machine44 learning44", 10),
        ["knowledge44", "vector44", "processor44", "reasoning44", "machine44", "learning44"],
    ),
    (
        ("knowledge44 vector44 processor44 reasoning44 machine44 learning44", 18),
        ["knowledge44", "vector44", "processor44", "reasoning44", "machine44", "learning44"],
    ),
    (
        ("knowledge44 vector44 processor44 reasoning44 machine44 learning44", 28),
        ["knowledge44 vector44", "processor44 reasoning44", "machine44 learning44"],
    ),
    (
        ("vector44 processor44 reasoning44 machine44 learning44 model44", 6),
        ["vector44", "processor44", "reasoning44", "machine44", "learning44", "model44"],
    ),
    (
        ("vector44 processor44 reasoning44 machine44 learning44 model44", 10),
        ["vector44", "processor44", "reasoning44", "machine44", "learning44", "model44"],
    ),
    (
        ("vector44 processor44 reasoning44 machine44 learning44 model44", 18),
        ["vector44", "processor44", "reasoning44", "machine44", "learning44 model44"],
    ),
    (
        ("vector44 processor44 reasoning44 machine44 learning44 model44", 28),
        ["vector44 processor44", "reasoning44 machine44", "learning44 model44"],
    ),
    (
        ("processor44 reasoning44 machine44 learning44 model44 token44", 6),
        ["processor44", "reasoning44", "machine44", "learning44", "model44", "token44"],
    ),
    (
        ("processor44 reasoning44 machine44 learning44 model44 token44", 10),
        ["processor44", "reasoning44", "machine44", "learning44", "model44", "token44"],
    ),
    (
        ("processor44 reasoning44 machine44 learning44 model44 token44", 18),
        ["processor44", "reasoning44", "machine44", "learning44 model44", "token44"],
    ),
    (
        ("processor44 reasoning44 machine44 learning44 model44 token44", 28),
        ["processor44 reasoning44", "machine44 learning44 model44", "token44"],
    ),
    (
        ("reasoning44 machine44 learning44 model44 token44 prompt44", 6),
        ["reasoning44", "machine44", "learning44", "model44", "token44", "prompt44"],
    ),
    (
        ("reasoning44 machine44 learning44 model44 token44 prompt44", 10),
        ["reasoning44", "machine44", "learning44", "model44", "token44", "prompt44"],
    ),
    (
        ("reasoning44 machine44 learning44 model44 token44 prompt44", 18),
        ["reasoning44", "machine44", "learning44 model44", "token44 prompt44"],
    ),
    (
        ("reasoning44 machine44 learning44 model44 token44 prompt44", 28),
        ["reasoning44 machine44", "learning44 model44 token44", "prompt44"],
    ),
    (
        ("machine44 learning44 model44 token44 prompt44 session44", 6),
        ["machine44", "learning44", "model44", "token44", "prompt44", "session44"],
    ),
    (
        ("machine44 learning44 model44 token44 prompt44 session44", 10),
        ["machine44", "learning44", "model44", "token44", "prompt44", "session44"],
    ),
    (
        ("machine44 learning44 model44 token44 prompt44 session44", 18),
        ["machine44", "learning44 model44", "token44 prompt44", "session44"],
    ),
    (
        ("machine44 learning44 model44 token44 prompt44 session44", 28),
        ["machine44 learning44 model44", "token44 prompt44 session44"],
    ),
    (
        ("learning44 model44 token44 prompt44 session44 library44", 6),
        ["learning44", "model44", "token44", "prompt44", "session44", "library44"],
    ),
    (
        ("learning44 model44 token44 prompt44 session44 library44", 10),
        ["learning44", "model44", "token44", "prompt44", "session44", "library44"],
    ),
    (
        ("learning44 model44 token44 prompt44 session44 library44", 18),
        ["learning44 model44", "token44 prompt44", "session44", "library44"],
    ),
    (
        ("learning44 model44 token44 prompt44 session44 library44", 28),
        ["learning44 model44 token44", "prompt44 session44 library44"],
    ),
    (
        ("model44 token44 prompt44 session44 library44 service44", 6),
        ["model44", "token44", "prompt44", "session44", "library44", "service44"],
    ),
    (
        ("model44 token44 prompt44 session44 library44 service44", 10),
        ["model44", "token44", "prompt44", "session44", "library44", "service44"],
    ),
    (
        ("model44 token44 prompt44 session44 library44 service44", 18),
        ["model44 token44", "prompt44 session44", "library44", "service44"],
    ),
    (
        ("model44 token44 prompt44 session44 library44 service44", 28),
        ["model44 token44 prompt44", "session44 library44", "service44"],
    ),
    (
        ("token44 prompt44 session44 library44 service44 gateway44", 6),
        ["token44", "prompt44", "session44", "library44", "service44", "gateway44"],
    ),
    (
        ("token44 prompt44 session44 library44 service44 gateway44", 10),
        ["token44", "prompt44", "session44", "library44", "service44", "gateway44"],
    ),
    (
        ("token44 prompt44 session44 library44 service44 gateway44", 18),
        ["token44 prompt44", "session44", "library44", "service44", "gateway44"],
    ),
    (
        ("token44 prompt44 session44 library44 service44 gateway44", 28),
        ["token44 prompt44 session44", "library44 service44", "gateway44"],
    ),
    (
        ("prompt44 session44 library44 service44 gateway44 storage44", 6),
        ["prompt44", "session44", "library44", "service44", "gateway44", "storage44"],
    ),
    (
        ("prompt44 session44 library44 service44 gateway44 storage44", 10),
        ["prompt44", "session44", "library44", "service44", "gateway44", "storage44"],
    ),
    (
        ("prompt44 session44 library44 service44 gateway44 storage44", 18),
        ["prompt44 session44", "library44", "service44", "gateway44", "storage44"],
    ),
    (
        ("prompt44 session44 library44 service44 gateway44 storage44", 28),
        ["prompt44 session44 library44", "service44 gateway44", "storage44"],
    ),
    (
        ("session44 library44 service44 gateway44 storage44 network44", 6),
        ["session44", "library44", "service44", "gateway44", "storage44", "network44"],
    ),
    (
        ("session44 library44 service44 gateway44 storage44 network44", 10),
        ["session44", "library44", "service44", "gateway44", "storage44", "network44"],
    ),
    (
        ("session44 library44 service44 gateway44 storage44 network44", 18),
        ["session44", "library44", "service44", "gateway44", "storage44", "network44"],
    ),
    (
        ("session44 library44 service44 gateway44 storage44 network44", 28),
        ["session44 library44", "service44 gateway44", "storage44 network44"],
    ),
    (
        ("library44 service44 gateway44 storage44 network44 latency44", 6),
        ["library44", "service44", "gateway44", "storage44", "network44", "latency44"],
    ),
    (
        ("library44 service44 gateway44 storage44 network44 latency44", 10),
        ["library44", "service44", "gateway44", "storage44", "network44", "latency44"],
    ),
    (
        ("library44 service44 gateway44 storage44 network44 latency44", 18),
        ["library44", "service44", "gateway44", "storage44", "network44", "latency44"],
    ),
    (
        ("library44 service44 gateway44 storage44 network44 latency44", 28),
        ["library44 service44", "gateway44 storage44", "network44 latency44"],
    ),
    (
        ("service44 gateway44 storage44 network44 latency44 buffer44", 6),
        ["service44", "gateway44", "storage44", "network44", "latency44", "buffer44"],
    ),
    (
        ("service44 gateway44 storage44 network44 latency44 buffer44", 10),
        ["service44", "gateway44", "storage44", "network44", "latency44", "buffer44"],
    ),
    (
        ("service44 gateway44 storage44 network44 latency44 buffer44", 18),
        ["service44", "gateway44", "storage44", "network44", "latency44 buffer44"],
    ),
    (
        ("service44 gateway44 storage44 network44 latency44 buffer44", 28),
        ["service44 gateway44", "storage44 network44", "latency44 buffer44"],
    ),
    (
        ("gateway44 storage44 network44 latency44 buffer44 queue44", 6),
        ["gateway44", "storage44", "network44", "latency44", "buffer44", "queue44"],
    ),
    (
        ("gateway44 storage44 network44 latency44 buffer44 queue44", 10),
        ["gateway44", "storage44", "network44", "latency44", "buffer44", "queue44"],
    ),
    (
        ("gateway44 storage44 network44 latency44 buffer44 queue44", 18),
        ["gateway44", "storage44", "network44", "latency44 buffer44", "queue44"],
    ),
    (
        ("gateway44 storage44 network44 latency44 buffer44 queue44", 28),
        ["gateway44 storage44", "network44 latency44 buffer44", "queue44"],
    ),
    (
        ("storage44 network44 latency44 buffer44 queue44 worker44", 6),
        ["storage44", "network44", "latency44", "buffer44", "queue44", "worker44"],
    ),
    (
        ("storage44 network44 latency44 buffer44 queue44 worker44", 10),
        ["storage44", "network44", "latency44", "buffer44", "queue44", "worker44"],
    ),
    (
        ("storage44 network44 latency44 buffer44 queue44 worker44", 18),
        ["storage44", "network44", "latency44 buffer44", "queue44 worker44"],
    ),
    (
        ("storage44 network44 latency44 buffer44 queue44 worker44", 28),
        ["storage44 network44", "latency44 buffer44 queue44", "worker44"],
    ),
    (
        ("network44 latency44 buffer44 queue44 worker44 kernel44", 6),
        ["network44", "latency44", "buffer44", "queue44", "worker44", "kernel44"],
    ),
    (
        ("network44 latency44 buffer44 queue44 worker44 kernel44", 10),
        ["network44", "latency44", "buffer44", "queue44", "worker44", "kernel44"],
    ),
    (
        ("network44 latency44 buffer44 queue44 worker44 kernel44", 18),
        ["network44", "latency44 buffer44", "queue44 worker44", "kernel44"],
    ),
    (
        ("network44 latency44 buffer44 queue44 worker44 kernel44", 28),
        ["network44 latency44 buffer44", "queue44 worker44 kernel44"],
    ),
    (
        ("latency44 buffer44 queue44 worker44 kernel44 signal44", 6),
        ["latency44", "buffer44", "queue44", "worker44", "kernel44", "signal44"],
    ),
    (
        ("latency44 buffer44 queue44 worker44 kernel44 signal44", 10),
        ["latency44", "buffer44", "queue44", "worker44", "kernel44", "signal44"],
    ),
    (
        ("latency44 buffer44 queue44 worker44 kernel44 signal44", 18),
        ["latency44 buffer44", "queue44 worker44", "kernel44 signal44"],
    ),
    (
        ("latency44 buffer44 queue44 worker44 kernel44 signal44", 28),
        ["latency44 buffer44 queue44", "worker44 kernel44 signal44"],
    ),
    (
        ("buffer44 queue44 worker44 kernel44 signal44 packet44", 6),
        ["buffer44", "queue44", "worker44", "kernel44", "signal44", "packet44"],
    ),
    (
        ("buffer44 queue44 worker44 kernel44 signal44 packet44", 10),
        ["buffer44", "queue44", "worker44", "kernel44", "signal44", "packet44"],
    ),
    (
        ("buffer44 queue44 worker44 kernel44 signal44 packet44", 18),
        ["buffer44 queue44", "worker44 kernel44", "signal44 packet44"],
    ),
    (
        ("buffer44 queue44 worker44 kernel44 signal44 packet44", 28),
        ["buffer44 queue44 worker44", "kernel44 signal44 packet44"],
    ),
    (
        ("queue44 worker44 kernel44 signal44 packet44 router44", 6),
        ["queue44", "worker44", "kernel44", "signal44", "packet44", "router44"],
    ),
    (
        ("queue44 worker44 kernel44 signal44 packet44 router44", 10),
        ["queue44", "worker44", "kernel44", "signal44", "packet44", "router44"],
    ),
    (
        ("queue44 worker44 kernel44 signal44 packet44 router44", 18),
        ["queue44 worker44", "kernel44 signal44", "packet44 router44"],
    ),
    (
        ("queue44 worker44 kernel44 signal44 packet44 router44", 28),
        ["queue44 worker44 kernel44", "signal44 packet44 router44"],
    ),
    (
        ("worker44 kernel44 signal44 packet44 router44 cluster44", 6),
        ["worker44", "kernel44", "signal44", "packet44", "router44", "cluster44"],
    ),
    (
        ("worker44 kernel44 signal44 packet44 router44 cluster44", 10),
        ["worker44", "kernel44", "signal44", "packet44", "router44", "cluster44"],
    ),
    (
        ("worker44 kernel44 signal44 packet44 router44 cluster44", 18),
        ["worker44 kernel44", "signal44 packet44", "router44 cluster44"],
    ),
    (
        ("worker44 kernel44 signal44 packet44 router44 cluster44", 28),
        ["worker44 kernel44 signal44", "packet44 router44 cluster44"],
    ),
    (
        ("kernel44 signal44 packet44 router44 cluster44 mirror44", 6),
        ["kernel44", "signal44", "packet44", "router44", "cluster44", "mirror44"],
    ),
    (
        ("kernel44 signal44 packet44 router44 cluster44 mirror44", 10),
        ["kernel44", "signal44", "packet44", "router44", "cluster44", "mirror44"],
    ),
    (
        ("kernel44 signal44 packet44 router44 cluster44 mirror44", 18),
        ["kernel44 signal44", "packet44 router44", "cluster44 mirror44"],
    ),
    (
        ("kernel44 signal44 packet44 router44 cluster44 mirror44", 28),
        ["kernel44 signal44 packet44", "router44 cluster44 mirror44"],
    ),
    (
        ("signal44 packet44 router44 cluster44 mirror44 filter44", 6),
        ["signal44", "packet44", "router44", "cluster44", "mirror44", "filter44"],
    ),
    (
        ("signal44 packet44 router44 cluster44 mirror44 filter44", 10),
        ["signal44", "packet44", "router44", "cluster44", "mirror44", "filter44"],
    ),
    (
        ("signal44 packet44 router44 cluster44 mirror44 filter44", 18),
        ["signal44 packet44", "router44 cluster44", "mirror44 filter44"],
    ),
    (
        ("signal44 packet44 router44 cluster44 mirror44 filter44", 28),
        ["signal44 packet44 router44", "cluster44 mirror44 filter44"],
    ),
    (
        ("packet44 router44 cluster44 mirror44 filter44 ranking44", 6),
        ["packet44", "router44", "cluster44", "mirror44", "filter44", "ranking44"],
    ),
    (
        ("packet44 router44 cluster44 mirror44 filter44 ranking44", 10),
        ["packet44", "router44", "cluster44", "mirror44", "filter44", "ranking44"],
    ),
    (
        ("packet44 router44 cluster44 mirror44 filter44 ranking44", 18),
        ["packet44 router44", "cluster44 mirror44", "filter44 ranking44"],
    ),
    (
        ("packet44 router44 cluster44 mirror44 filter44 ranking44", 28),
        ["packet44 router44 cluster44", "mirror44 filter44 ranking44"],
    ),
    (
        ("router44 cluster44 mirror44 filter44 ranking44 encoding44", 6),
        ["router44", "cluster44", "mirror44", "filter44", "ranking44", "encoding44"],
    ),
    (
        ("router44 cluster44 mirror44 filter44 ranking44 encoding44", 10),
        ["router44", "cluster44", "mirror44", "filter44", "ranking44", "encoding44"],
    ),
    (
        ("router44 cluster44 mirror44 filter44 ranking44 encoding44", 18),
        ["router44 cluster44", "mirror44 filter44", "ranking44", "encoding44"],
    ),
    (
        ("router44 cluster44 mirror44 filter44 ranking44 encoding44", 28),
        ["router44 cluster44 mirror44", "filter44 ranking44", "encoding44"],
    ),
    (
        ("cluster44 mirror44 filter44 ranking44 encoding44 mapping44", 6),
        ["cluster44", "mirror44", "filter44", "ranking44", "encoding44", "mapping44"],
    ),
    (
        ("cluster44 mirror44 filter44 ranking44 encoding44 mapping44", 10),
        ["cluster44", "mirror44", "filter44", "ranking44", "encoding44", "mapping44"],
    ),
    (
        ("cluster44 mirror44 filter44 ranking44 encoding44 mapping44", 18),
        ["cluster44 mirror44", "filter44 ranking44", "encoding44", "mapping44"],
    ),
    (
        ("cluster44 mirror44 filter44 ranking44 encoding44 mapping44", 28),
        ["cluster44 mirror44 filter44", "ranking44 encoding44", "mapping44"],
    ),
    (
        ("mirror44 filter44 ranking44 encoding44 mapping44 record44", 6),
        ["mirror44", "filter44", "ranking44", "encoding44", "mapping44", "record44"],
    ),
    (
        ("mirror44 filter44 ranking44 encoding44 mapping44 record44", 10),
        ["mirror44", "filter44", "ranking44", "encoding44", "mapping44", "record44"],
    ),
    (
        ("mirror44 filter44 ranking44 encoding44 mapping44 record44", 18),
        ["mirror44 filter44", "ranking44", "encoding44", "mapping44 record44"],
    ),
    (
        ("mirror44 filter44 ranking44 encoding44 mapping44 record44", 28),
        ["mirror44 filter44 ranking44", "encoding44 mapping44", "record44"],
    ),
    (
        ("filter44 ranking44 encoding44 mapping44 record44 candle44", 6),
        ["filter44", "ranking44", "encoding44", "mapping44", "record44", "candle44"],
    ),
    (
        ("filter44 ranking44 encoding44 mapping44 record44 candle44", 10),
        ["filter44", "ranking44", "encoding44", "mapping44", "record44", "candle44"],
    ),
    (
        ("filter44 ranking44 encoding44 mapping44 record44 candle44", 18),
        ["filter44 ranking44", "encoding44", "mapping44 record44", "candle44"],
    ),
    (
        ("filter44 ranking44 encoding44 mapping44 record44 candle44", 28),
        ["filter44 ranking44", "encoding44 mapping44", "record44 candle44"],
    ),
    (
        ("ranking44 encoding44 mapping44 record44 candle44 thread44", 6),
        ["ranking44", "encoding44", "mapping44", "record44", "candle44", "thread44"],
    ),
    (
        ("ranking44 encoding44 mapping44 record44 candle44 thread44", 10),
        ["ranking44", "encoding44", "mapping44", "record44", "candle44", "thread44"],
    ),
    (
        ("ranking44 encoding44 mapping44 record44 candle44 thread44", 18),
        ["ranking44", "encoding44", "mapping44 record44", "candle44 thread44"],
    ),
    (
        ("ranking44 encoding44 mapping44 record44 candle44 thread44", 28),
        ["ranking44 encoding44", "mapping44 record44 candle44", "thread44"],
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
