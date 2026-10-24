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
        ("round 78: the quick brown fox jumps over the lazy dog", 4),
        ["round", "78:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 78: the quick brown fox jumps over the lazy dog", 8),
        ["round", "78: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 78: the quick brown fox jumps over the lazy dog", 12),
        ["round 78:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 78: the quick brown fox jumps over the lazy dog", 16),
        ["round 78: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 78: the quick brown fox jumps over the lazy dog", 24),
        ["round 78: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 78: the quick brown fox jumps over the lazy dog", 32),
        ["round 78: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 78: agentuniverse is a framework for multi agents", 4),
        ["round", "78:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 78: agentuniverse is a framework for multi agents", 8),
        ["round", "78:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 78: agentuniverse is a framework for multi agents", 12),
        ["round 78:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 78: agentuniverse is a framework for multi agents", 16),
        ["round 78:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 78: agentuniverse is a framework for multi agents", 24),
        ["round 78: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 78: agentuniverse is a framework for multi agents", 32),
        ["round 78: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 78: knowledge stored as vectors enables retrieval", 4),
        ["round", "78:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 78: knowledge stored as vectors enables retrieval", 8),
        ["round", "78:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 78: knowledge stored as vectors enables retrieval", 12),
        ["round 78:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 78: knowledge stored as vectors enables retrieval", 16),
        ["round 78:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 78: knowledge stored as vectors enables retrieval", 24),
        ["round 78: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 78: knowledge stored as vectors enables retrieval", 32),
        ["round 78: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 78: the processor reads the record then stops", 4),
        ["round", "78:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 78: the processor reads the record then stops", 8),
        ["round", "78: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 78: the processor reads the record then stops", 12),
        ["round 78:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 78: the processor reads the record then stops", 16),
        ["round 78: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 78: the processor reads the record then stops", 24),
        ["round 78: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 78: the processor reads the record then stops", 32),
        ["round 78: the processor reads", "the record then stops"],
    ),
    (
        ("round 78: a worker pulls the next task from the queue", 4),
        ["round", "78:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 78: a worker pulls the next task from the queue", 8),
        ["round", "78: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 78: a worker pulls the next task from the queue", 12),
        ["round 78: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 78: a worker pulls the next task from the queue", 16),
        ["round 78: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 78: a worker pulls the next task from the queue", 24),
        ["round 78: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 78: a worker pulls the next task from the queue", 32),
        ["round 78: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 78: signals travel through the network layer", 4),
        ["round", "78:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 78: signals travel through the network layer", 8),
        ["round", "78:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 78: signals travel through the network layer", 12),
        ["round 78:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 78: signals travel through the network layer", 16),
        ["round 78:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 78: signals travel through the network layer", 24),
        ["round 78: signals travel", "through the network", "layer"],
    ),
    (
        ("round 78: signals travel through the network layer", 32),
        ["round 78: signals travel through", "the network layer"],
    ),
    (
        ("round 78: the gateway routes each request by policy", 4),
        ["round", "78:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 78: the gateway routes each request by policy", 8),
        ["round", "78: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 78: the gateway routes each request by policy", 12),
        ["round 78:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 78: the gateway routes each request by policy", 16),
        ["round 78: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 78: the gateway routes each request by policy", 24),
        ["round 78: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 78: the gateway routes each request by policy", 32),
        ["round 78: the gateway routes", "each request by policy"],
    ),
    (
        ("round 78: memory grows until the buffer is full", 4),
        ["round", "78:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 78: memory grows until the buffer is full", 8),
        ["round", "78:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 78: memory grows until the buffer is full", 12),
        ["round 78:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 78: memory grows until the buffer is full", 16),
        ["round 78: memory", "grows until the", "buffer is full"],
    ),
    (("round 78: memory grows until the buffer is full", 24), ["round 78: memory grows", "until the buffer is full"]),
    (("round 78: memory grows until the buffer is full", 32), ["round 78: memory grows until the", "buffer is full"]),
    (
        ("round 78: the cluster mirrors every packet twice", 4),
        ["round", "78:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 78: the cluster mirrors every packet twice", 8),
        ["round", "78: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 78: the cluster mirrors every packet twice", 12),
        ["round 78:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 78: the cluster mirrors every packet twice", 16),
        ["round 78: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 78: the cluster mirrors every packet twice", 24),
        ["round 78: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 78: the cluster mirrors every packet twice", 32), ["round 78: the cluster mirrors", "every packet twice"]),
    (
        ("round 78: ranking uses tokens learned from the corpus", 4),
        ["round", "78:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 78: ranking uses tokens learned from the corpus", 8),
        ["round", "78:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 78: ranking uses tokens learned from the corpus", 12),
        ["round 78:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 78: ranking uses tokens learned from the corpus", 16),
        ["round 78:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 78: ranking uses tokens learned from the corpus", 24),
        ["round 78: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 78: ranking uses tokens learned from the corpus", 32),
        ["round 78: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 78: a long session ends when the candle dies", 4),
        ["round", "78:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 78: a long session ends when the candle dies", 8),
        ["round", "78: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 78: a long session ends when the candle dies", 12),
        ["round 78: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 78: a long session ends when the candle dies", 16),
        ["round 78: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 78: a long session ends when the candle dies", 24),
        ["round 78: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 78: a long session ends when the candle dies", 32),
        ["round 78: a long session ends", "when the candle dies"],
    ),
    (
        ("round 78: encode the prompt then map the result", 4),
        ["round", "78:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 78: encode the prompt then map the result", 8),
        ["round", "78:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 78: encode the prompt then map the result", 12),
        ["round 78:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 78: encode the prompt then map the result", 16),
        ["round 78: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 78: encode the prompt then map the result", 24),
        ["round 78: encode the", "prompt then map the", "result"],
    ),
    (("round 78: encode the prompt then map the result", 32), ["round 78: encode the prompt then", "map the result"]),
    (
        ("round 78: the kernel wakes the worker at dawn", 4),
        ["round", "78:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 78: the kernel wakes the worker at dawn", 8),
        ["round", "78: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 78: the kernel wakes the worker at dawn", 12),
        ["round 78:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 78: the kernel wakes the worker at dawn", 16), ["round 78: the", "kernel wakes the", "worker at dawn"]),
    (("round 78: the kernel wakes the worker at dawn", 24), ["round 78: the kernel", "wakes the worker at dawn"]),
    (("round 78: the kernel wakes the worker at dawn", 32), ["round 78: the kernel wakes the", "worker at dawn"]),
    (
        ("round 78: service latency drops after the patch", 4),
        ["round", "78:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 78: service latency drops after the patch", 8),
        ["round", "78:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 78: service latency drops after the patch", 12),
        ["round 78:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 78: service latency drops after the patch", 16),
        ["round 78:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 78: service latency drops after the patch", 24),
        ["round 78: service", "latency drops after the", "patch"],
    ),
    (("round 78: service latency drops after the patch", 32), ["round 78: service latency drops", "after the patch"]),
    (
        ("round 78: the library caches every vector it sees", 4),
        ["round", "78:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 78: the library caches every vector it sees", 8),
        ["round", "78: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 78: the library caches every vector it sees", 12),
        ["round 78:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 78: the library caches every vector it sees", 16),
        ["round 78: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 78: the library caches every vector it sees", 24),
        ["round 78: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 78: the library caches every vector it sees", 32),
        ["round 78: the library caches", "every vector it sees"],
    ),
    (
        ("round 78: agents argue then the debate resolves", 4),
        ["round", "78:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 78: agents argue then the debate resolves", 8),
        ["round", "78:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 78: agents argue then the debate resolves", 12),
        ["round 78:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 78: agents argue then the debate resolves", 16),
        ["round 78: agents", "argue then the", "debate resolves"],
    ),
    (("round 78: agents argue then the debate resolves", 24), ["round 78: agents argue", "then the debate resolves"]),
    (("round 78: agents argue then the debate resolves", 32), ["round 78: agents argue then the", "debate resolves"]),
    (
        ("round 78: the filter keeps only strong matches", 4),
        ["round", "78:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 78: the filter keeps only strong matches", 8),
        ["round", "78: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 78: the filter keeps only strong matches", 12),
        ["round 78:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 78: the filter keeps only strong matches", 16),
        ["round 78: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 78: the filter keeps only strong matches", 24), ["round 78: the filter", "keeps only strong", "matches"]),
    (("round 78: the filter keeps only strong matches", 32), ["round 78: the filter keeps only", "strong matches"]),
    (
        ("round 78: the model answers with a short reply", 4),
        ["round", "78:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 78: the model answers with a short reply", 8),
        ["round", "78: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 78: the model answers with a short reply", 12),
        ["round 78:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 78: the model answers with a short reply", 16),
        ["round 78: the", "model answers", "with a short", "reply"],
    ),
    (("round 78: the model answers with a short reply", 24), ["round 78: the model", "answers with a short", "reply"]),
    (("round 78: the model answers with a short reply", 32), ["round 78: the model answers with", "a short reply"]),
    (
        ("round 78: the recorder stores the reasoning trace", 4),
        ["round", "78:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 78: the recorder stores the reasoning trace", 8),
        ["round", "78: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 78: the recorder stores the reasoning trace", 12),
        ["round 78:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 78: the recorder stores the reasoning trace", 16),
        ["round 78: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 78: the recorder stores the reasoning trace", 24),
        ["round 78: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 78: the recorder stores the reasoning trace", 32),
        ["round 78: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 78: the angel watches the processor run", 4),
        ["round", "78:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 78: the angel watches the processor run", 8),
        ["round", "78: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 78: the angel watches the processor run", 12),
        ["round 78:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 78: the angel watches the processor run", 16), ["round 78: the", "angel watches", "the processor", "run"]),
    (("round 78: the angel watches the processor run", 24), ["round 78: the angel", "watches the processor", "run"]),
    (("round 78: the angel watches the processor run", 32), ["round 78: the angel watches the", "processor run"]),
    (
        ("round 78: angle of the vector decides the match", 4),
        ["round", "78:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 78: angle of the vector decides the match", 8),
        ["round", "78:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 78: angle of the vector decides the match", 12),
        ["round 78:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 78: angle of the vector decides the match", 16),
        ["round 78: angle", "of the vector", "decides the", "match"],
    ),
    (("round 78: angle of the vector decides the match", 24), ["round 78: angle of the", "vector decides the match"]),
    (("round 78: angle of the vector decides the match", 32), ["round 78: angle of the vector", "decides the match"]),
    (
        ("round 78: the candle burns twice as long at night", 4),
        ["round", "78:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 78: the candle burns twice as long at night", 8),
        ["round", "78: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 78: the candle burns twice as long at night", 12),
        ["round 78:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 78: the candle burns twice as long at night", 16),
        ["round 78: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 78: the candle burns twice as long at night", 24),
        ["round 78: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 78: the candle burns twice as long at night", 32),
        ["round 78: the candle burns twice", "as long at night"],
    ),
    (
        ("round 78: a mirror of the universe in one line", 4),
        ["round", "78:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 78: a mirror of the universe in one line", 8),
        ["round", "78: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 78: a mirror of the universe in one line", 12),
        ["round 78: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 78: a mirror of the universe in one line", 16),
        ["round 78: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 78: a mirror of the universe in one line", 24), ["round 78: a mirror of", "the universe in one line"]),
    (("round 78: a mirror of the universe in one line", 32), ["round 78: a mirror of the", "universe in one line"]),
    (
        ("round 78: the queue drains before the storm", 4),
        ["round", "78:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 78: the queue drains before the storm", 8),
        ["round", "78: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 78: the queue drains before the storm", 12), ["round 78:", "the queue", "drains", "before the", "storm"]),
    (("round 78: the queue drains before the storm", 16), ["round 78: the", "queue drains", "before the storm"]),
    (("round 78: the queue drains before the storm", 24), ["round 78: the queue", "drains before the storm"]),
    (("round 78: the queue drains before the storm", 32), ["round 78: the queue drains", "before the storm"]),
    (
        ("kitten78 sitting78 agent78 angle78 universe78 memory78", 6),
        ["kitten78", "sitting78", "agent78", "angle78", "universe78", "memory78"],
    ),
    (
        ("kitten78 sitting78 agent78 angle78 universe78 memory78", 10),
        ["kitten78", "sitting78", "agent78", "angle78", "universe78", "memory78"],
    ),
    (
        ("kitten78 sitting78 agent78 angle78 universe78 memory78", 18),
        ["kitten78 sitting78", "agent78 angle78", "universe78", "memory78"],
    ),
    (
        ("kitten78 sitting78 agent78 angle78 universe78 memory78", 28),
        ["kitten78 sitting78 agent78", "angle78 universe78 memory78"],
    ),
    (
        ("sitting78 agent78 angle78 universe78 memory78 stream78", 6),
        ["sitting78", "agent78", "angle78", "universe78", "memory78", "stream78"],
    ),
    (
        ("sitting78 agent78 angle78 universe78 memory78 stream78", 10),
        ["sitting78", "agent78", "angle78", "universe78", "memory78", "stream78"],
    ),
    (
        ("sitting78 agent78 angle78 universe78 memory78 stream78", 18),
        ["sitting78 agent78", "angle78 universe78", "memory78 stream78"],
    ),
    (
        ("sitting78 agent78 angle78 universe78 memory78 stream78", 28),
        ["sitting78 agent78 angle78", "universe78 memory78 stream78"],
    ),
    (
        ("agent78 angle78 universe78 memory78 stream78 context78", 6),
        ["agent78", "angle78", "universe78", "memory78", "stream78", "context78"],
    ),
    (
        ("agent78 angle78 universe78 memory78 stream78 context78", 10),
        ["agent78", "angle78", "universe78", "memory78", "stream78", "context78"],
    ),
    (
        ("agent78 angle78 universe78 memory78 stream78 context78", 18),
        ["agent78 angle78", "universe78", "memory78 stream78", "context78"],
    ),
    (
        ("agent78 angle78 universe78 memory78 stream78 context78", 28),
        ["agent78 angle78 universe78", "memory78 stream78 context78"],
    ),
    (
        ("angle78 universe78 memory78 stream78 context78 knowledge78", 6),
        ["angle78", "universe78", "memory78", "stream78", "context78", "knowledge78"],
    ),
    (
        ("angle78 universe78 memory78 stream78 context78 knowledge78", 10),
        ["angle78", "universe78", "memory78", "stream78", "context78", "knowledge78"],
    ),
    (
        ("angle78 universe78 memory78 stream78 context78 knowledge78", 18),
        ["angle78 universe78", "memory78 stream78", "context78", "knowledge78"],
    ),
    (
        ("angle78 universe78 memory78 stream78 context78 knowledge78", 28),
        ["angle78 universe78 memory78", "stream78 context78", "knowledge78"],
    ),
    (
        ("universe78 memory78 stream78 context78 knowledge78 vector78", 6),
        ["universe78", "memory78", "stream78", "context78", "knowledge78", "vector78"],
    ),
    (
        ("universe78 memory78 stream78 context78 knowledge78 vector78", 10),
        ["universe78", "memory78", "stream78", "context78", "knowledge78", "vector78"],
    ),
    (
        ("universe78 memory78 stream78 context78 knowledge78 vector78", 18),
        ["universe78", "memory78 stream78", "context78", "knowledge78", "vector78"],
    ),
    (
        ("universe78 memory78 stream78 context78 knowledge78 vector78", 28),
        ["universe78 memory78 stream78", "context78 knowledge78", "vector78"],
    ),
    (
        ("memory78 stream78 context78 knowledge78 vector78 processor78", 6),
        ["memory78", "stream78", "context78", "knowledge78", "vector78", "processor78"],
    ),
    (
        ("memory78 stream78 context78 knowledge78 vector78 processor78", 10),
        ["memory78", "stream78", "context78", "knowledge78", "vector78", "processor78"],
    ),
    (
        ("memory78 stream78 context78 knowledge78 vector78 processor78", 18),
        ["memory78 stream78", "context78", "knowledge78", "vector78", "processor78"],
    ),
    (
        ("memory78 stream78 context78 knowledge78 vector78 processor78", 28),
        ["memory78 stream78 context78", "knowledge78 vector78", "processor78"],
    ),
    (
        ("stream78 context78 knowledge78 vector78 processor78 reasoning78", 6),
        ["stream78", "context78", "knowledge78", "vector78", "processor78", "reasoning78"],
    ),
    (
        ("stream78 context78 knowledge78 vector78 processor78 reasoning78", 10),
        ["stream78", "context78", "knowledge78", "vector78", "processor78", "reasoning78"],
    ),
    (
        ("stream78 context78 knowledge78 vector78 processor78 reasoning78", 18),
        ["stream78 context78", "knowledge78", "vector78", "processor78", "reasoning78"],
    ),
    (
        ("stream78 context78 knowledge78 vector78 processor78 reasoning78", 28),
        ["stream78 context78", "knowledge78 vector78", "processor78 reasoning78"],
    ),
    (
        ("context78 knowledge78 vector78 processor78 reasoning78 machine78", 6),
        ["context78", "knowledge78", "vector78", "processor78", "reasoning78", "machine78"],
    ),
    (
        ("context78 knowledge78 vector78 processor78 reasoning78 machine78", 10),
        ["context78", "knowledge78", "vector78", "processor78", "reasoning78", "machine78"],
    ),
    (
        ("context78 knowledge78 vector78 processor78 reasoning78 machine78", 18),
        ["context78", "knowledge78", "vector78", "processor78", "reasoning78", "machine78"],
    ),
    (
        ("context78 knowledge78 vector78 processor78 reasoning78 machine78", 28),
        ["context78 knowledge78", "vector78 processor78", "reasoning78 machine78"],
    ),
    (
        ("knowledge78 vector78 processor78 reasoning78 machine78 learning78", 6),
        ["knowledge78", "vector78", "processor78", "reasoning78", "machine78", "learning78"],
    ),
    (
        ("knowledge78 vector78 processor78 reasoning78 machine78 learning78", 10),
        ["knowledge78", "vector78", "processor78", "reasoning78", "machine78", "learning78"],
    ),
    (
        ("knowledge78 vector78 processor78 reasoning78 machine78 learning78", 18),
        ["knowledge78", "vector78", "processor78", "reasoning78", "machine78", "learning78"],
    ),
    (
        ("knowledge78 vector78 processor78 reasoning78 machine78 learning78", 28),
        ["knowledge78 vector78", "processor78 reasoning78", "machine78 learning78"],
    ),
    (
        ("vector78 processor78 reasoning78 machine78 learning78 model78", 6),
        ["vector78", "processor78", "reasoning78", "machine78", "learning78", "model78"],
    ),
    (
        ("vector78 processor78 reasoning78 machine78 learning78 model78", 10),
        ["vector78", "processor78", "reasoning78", "machine78", "learning78", "model78"],
    ),
    (
        ("vector78 processor78 reasoning78 machine78 learning78 model78", 18),
        ["vector78", "processor78", "reasoning78", "machine78", "learning78 model78"],
    ),
    (
        ("vector78 processor78 reasoning78 machine78 learning78 model78", 28),
        ["vector78 processor78", "reasoning78 machine78", "learning78 model78"],
    ),
    (
        ("processor78 reasoning78 machine78 learning78 model78 token78", 6),
        ["processor78", "reasoning78", "machine78", "learning78", "model78", "token78"],
    ),
    (
        ("processor78 reasoning78 machine78 learning78 model78 token78", 10),
        ["processor78", "reasoning78", "machine78", "learning78", "model78", "token78"],
    ),
    (
        ("processor78 reasoning78 machine78 learning78 model78 token78", 18),
        ["processor78", "reasoning78", "machine78", "learning78 model78", "token78"],
    ),
    (
        ("processor78 reasoning78 machine78 learning78 model78 token78", 28),
        ["processor78 reasoning78", "machine78 learning78 model78", "token78"],
    ),
    (
        ("reasoning78 machine78 learning78 model78 token78 prompt78", 6),
        ["reasoning78", "machine78", "learning78", "model78", "token78", "prompt78"],
    ),
    (
        ("reasoning78 machine78 learning78 model78 token78 prompt78", 10),
        ["reasoning78", "machine78", "learning78", "model78", "token78", "prompt78"],
    ),
    (
        ("reasoning78 machine78 learning78 model78 token78 prompt78", 18),
        ["reasoning78", "machine78", "learning78 model78", "token78 prompt78"],
    ),
    (
        ("reasoning78 machine78 learning78 model78 token78 prompt78", 28),
        ["reasoning78 machine78", "learning78 model78 token78", "prompt78"],
    ),
    (
        ("machine78 learning78 model78 token78 prompt78 session78", 6),
        ["machine78", "learning78", "model78", "token78", "prompt78", "session78"],
    ),
    (
        ("machine78 learning78 model78 token78 prompt78 session78", 10),
        ["machine78", "learning78", "model78", "token78", "prompt78", "session78"],
    ),
    (
        ("machine78 learning78 model78 token78 prompt78 session78", 18),
        ["machine78", "learning78 model78", "token78 prompt78", "session78"],
    ),
    (
        ("machine78 learning78 model78 token78 prompt78 session78", 28),
        ["machine78 learning78 model78", "token78 prompt78 session78"],
    ),
    (
        ("learning78 model78 token78 prompt78 session78 library78", 6),
        ["learning78", "model78", "token78", "prompt78", "session78", "library78"],
    ),
    (
        ("learning78 model78 token78 prompt78 session78 library78", 10),
        ["learning78", "model78", "token78", "prompt78", "session78", "library78"],
    ),
    (
        ("learning78 model78 token78 prompt78 session78 library78", 18),
        ["learning78 model78", "token78 prompt78", "session78", "library78"],
    ),
    (
        ("learning78 model78 token78 prompt78 session78 library78", 28),
        ["learning78 model78 token78", "prompt78 session78 library78"],
    ),
    (
        ("model78 token78 prompt78 session78 library78 service78", 6),
        ["model78", "token78", "prompt78", "session78", "library78", "service78"],
    ),
    (
        ("model78 token78 prompt78 session78 library78 service78", 10),
        ["model78", "token78", "prompt78", "session78", "library78", "service78"],
    ),
    (
        ("model78 token78 prompt78 session78 library78 service78", 18),
        ["model78 token78", "prompt78 session78", "library78", "service78"],
    ),
    (
        ("model78 token78 prompt78 session78 library78 service78", 28),
        ["model78 token78 prompt78", "session78 library78", "service78"],
    ),
    (
        ("token78 prompt78 session78 library78 service78 gateway78", 6),
        ["token78", "prompt78", "session78", "library78", "service78", "gateway78"],
    ),
    (
        ("token78 prompt78 session78 library78 service78 gateway78", 10),
        ["token78", "prompt78", "session78", "library78", "service78", "gateway78"],
    ),
    (
        ("token78 prompt78 session78 library78 service78 gateway78", 18),
        ["token78 prompt78", "session78", "library78", "service78", "gateway78"],
    ),
    (
        ("token78 prompt78 session78 library78 service78 gateway78", 28),
        ["token78 prompt78 session78", "library78 service78", "gateway78"],
    ),
    (
        ("prompt78 session78 library78 service78 gateway78 storage78", 6),
        ["prompt78", "session78", "library78", "service78", "gateway78", "storage78"],
    ),
    (
        ("prompt78 session78 library78 service78 gateway78 storage78", 10),
        ["prompt78", "session78", "library78", "service78", "gateway78", "storage78"],
    ),
    (
        ("prompt78 session78 library78 service78 gateway78 storage78", 18),
        ["prompt78 session78", "library78", "service78", "gateway78", "storage78"],
    ),
    (
        ("prompt78 session78 library78 service78 gateway78 storage78", 28),
        ["prompt78 session78 library78", "service78 gateway78", "storage78"],
    ),
    (
        ("session78 library78 service78 gateway78 storage78 network78", 6),
        ["session78", "library78", "service78", "gateway78", "storage78", "network78"],
    ),
    (
        ("session78 library78 service78 gateway78 storage78 network78", 10),
        ["session78", "library78", "service78", "gateway78", "storage78", "network78"],
    ),
    (
        ("session78 library78 service78 gateway78 storage78 network78", 18),
        ["session78", "library78", "service78", "gateway78", "storage78", "network78"],
    ),
    (
        ("session78 library78 service78 gateway78 storage78 network78", 28),
        ["session78 library78", "service78 gateway78", "storage78 network78"],
    ),
    (
        ("library78 service78 gateway78 storage78 network78 latency78", 6),
        ["library78", "service78", "gateway78", "storage78", "network78", "latency78"],
    ),
    (
        ("library78 service78 gateway78 storage78 network78 latency78", 10),
        ["library78", "service78", "gateway78", "storage78", "network78", "latency78"],
    ),
    (
        ("library78 service78 gateway78 storage78 network78 latency78", 18),
        ["library78", "service78", "gateway78", "storage78", "network78", "latency78"],
    ),
    (
        ("library78 service78 gateway78 storage78 network78 latency78", 28),
        ["library78 service78", "gateway78 storage78", "network78 latency78"],
    ),
    (
        ("service78 gateway78 storage78 network78 latency78 buffer78", 6),
        ["service78", "gateway78", "storage78", "network78", "latency78", "buffer78"],
    ),
    (
        ("service78 gateway78 storage78 network78 latency78 buffer78", 10),
        ["service78", "gateway78", "storage78", "network78", "latency78", "buffer78"],
    ),
    (
        ("service78 gateway78 storage78 network78 latency78 buffer78", 18),
        ["service78", "gateway78", "storage78", "network78", "latency78 buffer78"],
    ),
    (
        ("service78 gateway78 storage78 network78 latency78 buffer78", 28),
        ["service78 gateway78", "storage78 network78", "latency78 buffer78"],
    ),
    (
        ("gateway78 storage78 network78 latency78 buffer78 queue78", 6),
        ["gateway78", "storage78", "network78", "latency78", "buffer78", "queue78"],
    ),
    (
        ("gateway78 storage78 network78 latency78 buffer78 queue78", 10),
        ["gateway78", "storage78", "network78", "latency78", "buffer78", "queue78"],
    ),
    (
        ("gateway78 storage78 network78 latency78 buffer78 queue78", 18),
        ["gateway78", "storage78", "network78", "latency78 buffer78", "queue78"],
    ),
    (
        ("gateway78 storage78 network78 latency78 buffer78 queue78", 28),
        ["gateway78 storage78", "network78 latency78 buffer78", "queue78"],
    ),
    (
        ("storage78 network78 latency78 buffer78 queue78 worker78", 6),
        ["storage78", "network78", "latency78", "buffer78", "queue78", "worker78"],
    ),
    (
        ("storage78 network78 latency78 buffer78 queue78 worker78", 10),
        ["storage78", "network78", "latency78", "buffer78", "queue78", "worker78"],
    ),
    (
        ("storage78 network78 latency78 buffer78 queue78 worker78", 18),
        ["storage78", "network78", "latency78 buffer78", "queue78 worker78"],
    ),
    (
        ("storage78 network78 latency78 buffer78 queue78 worker78", 28),
        ["storage78 network78", "latency78 buffer78 queue78", "worker78"],
    ),
    (
        ("network78 latency78 buffer78 queue78 worker78 kernel78", 6),
        ["network78", "latency78", "buffer78", "queue78", "worker78", "kernel78"],
    ),
    (
        ("network78 latency78 buffer78 queue78 worker78 kernel78", 10),
        ["network78", "latency78", "buffer78", "queue78", "worker78", "kernel78"],
    ),
    (
        ("network78 latency78 buffer78 queue78 worker78 kernel78", 18),
        ["network78", "latency78 buffer78", "queue78 worker78", "kernel78"],
    ),
    (
        ("network78 latency78 buffer78 queue78 worker78 kernel78", 28),
        ["network78 latency78 buffer78", "queue78 worker78 kernel78"],
    ),
    (
        ("latency78 buffer78 queue78 worker78 kernel78 signal78", 6),
        ["latency78", "buffer78", "queue78", "worker78", "kernel78", "signal78"],
    ),
    (
        ("latency78 buffer78 queue78 worker78 kernel78 signal78", 10),
        ["latency78", "buffer78", "queue78", "worker78", "kernel78", "signal78"],
    ),
    (
        ("latency78 buffer78 queue78 worker78 kernel78 signal78", 18),
        ["latency78 buffer78", "queue78 worker78", "kernel78 signal78"],
    ),
    (
        ("latency78 buffer78 queue78 worker78 kernel78 signal78", 28),
        ["latency78 buffer78 queue78", "worker78 kernel78 signal78"],
    ),
    (
        ("buffer78 queue78 worker78 kernel78 signal78 packet78", 6),
        ["buffer78", "queue78", "worker78", "kernel78", "signal78", "packet78"],
    ),
    (
        ("buffer78 queue78 worker78 kernel78 signal78 packet78", 10),
        ["buffer78", "queue78", "worker78", "kernel78", "signal78", "packet78"],
    ),
    (
        ("buffer78 queue78 worker78 kernel78 signal78 packet78", 18),
        ["buffer78 queue78", "worker78 kernel78", "signal78 packet78"],
    ),
    (
        ("buffer78 queue78 worker78 kernel78 signal78 packet78", 28),
        ["buffer78 queue78 worker78", "kernel78 signal78 packet78"],
    ),
    (
        ("queue78 worker78 kernel78 signal78 packet78 router78", 6),
        ["queue78", "worker78", "kernel78", "signal78", "packet78", "router78"],
    ),
    (
        ("queue78 worker78 kernel78 signal78 packet78 router78", 10),
        ["queue78", "worker78", "kernel78", "signal78", "packet78", "router78"],
    ),
    (
        ("queue78 worker78 kernel78 signal78 packet78 router78", 18),
        ["queue78 worker78", "kernel78 signal78", "packet78 router78"],
    ),
    (
        ("queue78 worker78 kernel78 signal78 packet78 router78", 28),
        ["queue78 worker78 kernel78", "signal78 packet78 router78"],
    ),
    (
        ("worker78 kernel78 signal78 packet78 router78 cluster78", 6),
        ["worker78", "kernel78", "signal78", "packet78", "router78", "cluster78"],
    ),
    (
        ("worker78 kernel78 signal78 packet78 router78 cluster78", 10),
        ["worker78", "kernel78", "signal78", "packet78", "router78", "cluster78"],
    ),
    (
        ("worker78 kernel78 signal78 packet78 router78 cluster78", 18),
        ["worker78 kernel78", "signal78 packet78", "router78 cluster78"],
    ),
    (
        ("worker78 kernel78 signal78 packet78 router78 cluster78", 28),
        ["worker78 kernel78 signal78", "packet78 router78 cluster78"],
    ),
    (
        ("kernel78 signal78 packet78 router78 cluster78 mirror78", 6),
        ["kernel78", "signal78", "packet78", "router78", "cluster78", "mirror78"],
    ),
    (
        ("kernel78 signal78 packet78 router78 cluster78 mirror78", 10),
        ["kernel78", "signal78", "packet78", "router78", "cluster78", "mirror78"],
    ),
    (
        ("kernel78 signal78 packet78 router78 cluster78 mirror78", 18),
        ["kernel78 signal78", "packet78 router78", "cluster78 mirror78"],
    ),
    (
        ("kernel78 signal78 packet78 router78 cluster78 mirror78", 28),
        ["kernel78 signal78 packet78", "router78 cluster78 mirror78"],
    ),
    (
        ("signal78 packet78 router78 cluster78 mirror78 filter78", 6),
        ["signal78", "packet78", "router78", "cluster78", "mirror78", "filter78"],
    ),
    (
        ("signal78 packet78 router78 cluster78 mirror78 filter78", 10),
        ["signal78", "packet78", "router78", "cluster78", "mirror78", "filter78"],
    ),
    (
        ("signal78 packet78 router78 cluster78 mirror78 filter78", 18),
        ["signal78 packet78", "router78 cluster78", "mirror78 filter78"],
    ),
    (
        ("signal78 packet78 router78 cluster78 mirror78 filter78", 28),
        ["signal78 packet78 router78", "cluster78 mirror78 filter78"],
    ),
    (
        ("packet78 router78 cluster78 mirror78 filter78 ranking78", 6),
        ["packet78", "router78", "cluster78", "mirror78", "filter78", "ranking78"],
    ),
    (
        ("packet78 router78 cluster78 mirror78 filter78 ranking78", 10),
        ["packet78", "router78", "cluster78", "mirror78", "filter78", "ranking78"],
    ),
    (
        ("packet78 router78 cluster78 mirror78 filter78 ranking78", 18),
        ["packet78 router78", "cluster78 mirror78", "filter78 ranking78"],
    ),
    (
        ("packet78 router78 cluster78 mirror78 filter78 ranking78", 28),
        ["packet78 router78 cluster78", "mirror78 filter78 ranking78"],
    ),
    (
        ("router78 cluster78 mirror78 filter78 ranking78 encoding78", 6),
        ["router78", "cluster78", "mirror78", "filter78", "ranking78", "encoding78"],
    ),
    (
        ("router78 cluster78 mirror78 filter78 ranking78 encoding78", 10),
        ["router78", "cluster78", "mirror78", "filter78", "ranking78", "encoding78"],
    ),
    (
        ("router78 cluster78 mirror78 filter78 ranking78 encoding78", 18),
        ["router78 cluster78", "mirror78 filter78", "ranking78", "encoding78"],
    ),
    (
        ("router78 cluster78 mirror78 filter78 ranking78 encoding78", 28),
        ["router78 cluster78 mirror78", "filter78 ranking78", "encoding78"],
    ),
    (
        ("cluster78 mirror78 filter78 ranking78 encoding78 mapping78", 6),
        ["cluster78", "mirror78", "filter78", "ranking78", "encoding78", "mapping78"],
    ),
    (
        ("cluster78 mirror78 filter78 ranking78 encoding78 mapping78", 10),
        ["cluster78", "mirror78", "filter78", "ranking78", "encoding78", "mapping78"],
    ),
    (
        ("cluster78 mirror78 filter78 ranking78 encoding78 mapping78", 18),
        ["cluster78 mirror78", "filter78 ranking78", "encoding78", "mapping78"],
    ),
    (
        ("cluster78 mirror78 filter78 ranking78 encoding78 mapping78", 28),
        ["cluster78 mirror78 filter78", "ranking78 encoding78", "mapping78"],
    ),
    (
        ("mirror78 filter78 ranking78 encoding78 mapping78 record78", 6),
        ["mirror78", "filter78", "ranking78", "encoding78", "mapping78", "record78"],
    ),
    (
        ("mirror78 filter78 ranking78 encoding78 mapping78 record78", 10),
        ["mirror78", "filter78", "ranking78", "encoding78", "mapping78", "record78"],
    ),
    (
        ("mirror78 filter78 ranking78 encoding78 mapping78 record78", 18),
        ["mirror78 filter78", "ranking78", "encoding78", "mapping78 record78"],
    ),
    (
        ("mirror78 filter78 ranking78 encoding78 mapping78 record78", 28),
        ["mirror78 filter78 ranking78", "encoding78 mapping78", "record78"],
    ),
    (
        ("filter78 ranking78 encoding78 mapping78 record78 candle78", 6),
        ["filter78", "ranking78", "encoding78", "mapping78", "record78", "candle78"],
    ),
    (
        ("filter78 ranking78 encoding78 mapping78 record78 candle78", 10),
        ["filter78", "ranking78", "encoding78", "mapping78", "record78", "candle78"],
    ),
    (
        ("filter78 ranking78 encoding78 mapping78 record78 candle78", 18),
        ["filter78 ranking78", "encoding78", "mapping78 record78", "candle78"],
    ),
    (
        ("filter78 ranking78 encoding78 mapping78 record78 candle78", 28),
        ["filter78 ranking78", "encoding78 mapping78", "record78 candle78"],
    ),
    (
        ("ranking78 encoding78 mapping78 record78 candle78 thread78", 6),
        ["ranking78", "encoding78", "mapping78", "record78", "candle78", "thread78"],
    ),
    (
        ("ranking78 encoding78 mapping78 record78 candle78 thread78", 10),
        ["ranking78", "encoding78", "mapping78", "record78", "candle78", "thread78"],
    ),
    (
        ("ranking78 encoding78 mapping78 record78 candle78 thread78", 18),
        ["ranking78", "encoding78", "mapping78 record78", "candle78 thread78"],
    ),
    (
        ("ranking78 encoding78 mapping78 record78 candle78 thread78", 28),
        ["ranking78 encoding78", "mapping78 record78 candle78", "thread78"],
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
