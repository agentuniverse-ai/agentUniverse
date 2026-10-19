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
        ("round 181: the quick brown fox jumps over the lazy dog", 4),
        ["round", "181:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 181: the quick brown fox jumps over the lazy dog", 8),
        ["round", "181: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 181: the quick brown fox jumps over the lazy dog", 12),
        ["round 181:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 181: the quick brown fox jumps over the lazy dog", 16),
        ["round 181: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 181: the quick brown fox jumps over the lazy dog", 24),
        ["round 181: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 181: the quick brown fox jumps over the lazy dog", 32),
        ["round 181: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 181: agentuniverse is a framework for multi agents", 4),
        ["round", "181:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 181: agentuniverse is a framework for multi agents", 8),
        ["round", "181:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 181: agentuniverse is a framework for multi agents", 12),
        ["round 181:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 181: agentuniverse is a framework for multi agents", 16),
        ["round 181:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 181: agentuniverse is a framework for multi agents", 24),
        ["round 181: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 181: agentuniverse is a framework for multi agents", 32),
        ["round 181: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 181: knowledge stored as vectors enables retrieval", 4),
        ["round", "181:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 181: knowledge stored as vectors enables retrieval", 8),
        ["round", "181:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 181: knowledge stored as vectors enables retrieval", 12),
        ["round 181:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 181: knowledge stored as vectors enables retrieval", 16),
        ["round 181:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 181: knowledge stored as vectors enables retrieval", 24),
        ["round 181: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 181: knowledge stored as vectors enables retrieval", 32),
        ["round 181: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 181: the processor reads the record then stops", 4),
        ["round", "181:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 181: the processor reads the record then stops", 8),
        ["round", "181: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 181: the processor reads the record then stops", 12),
        ["round 181:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 181: the processor reads the record then stops", 16),
        ["round 181: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 181: the processor reads the record then stops", 24),
        ["round 181: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 181: the processor reads the record then stops", 32),
        ["round 181: the processor reads", "the record then stops"],
    ),
    (
        ("round 181: a worker pulls the next task from the queue", 4),
        ["round", "181:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 181: a worker pulls the next task from the queue", 8),
        ["round", "181: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 181: a worker pulls the next task from the queue", 12),
        ["round 181: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 181: a worker pulls the next task from the queue", 16),
        ["round 181: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 181: a worker pulls the next task from the queue", 24),
        ["round 181: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 181: a worker pulls the next task from the queue", 32),
        ["round 181: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 181: signals travel through the network layer", 4),
        ["round", "181:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 181: signals travel through the network layer", 8),
        ["round", "181:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 181: signals travel through the network layer", 12),
        ["round 181:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 181: signals travel through the network layer", 16),
        ["round 181:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 181: signals travel through the network layer", 24),
        ["round 181: signals", "travel through the", "network layer"],
    ),
    (
        ("round 181: signals travel through the network layer", 32),
        ["round 181: signals travel", "through the network layer"],
    ),
    (
        ("round 181: the gateway routes each request by policy", 4),
        ["round", "181:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 181: the gateway routes each request by policy", 8),
        ["round", "181: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 181: the gateway routes each request by policy", 12),
        ["round 181:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 181: the gateway routes each request by policy", 16),
        ["round 181: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 181: the gateway routes each request by policy", 24),
        ["round 181: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 181: the gateway routes each request by policy", 32),
        ["round 181: the gateway routes", "each request by policy"],
    ),
    (
        ("round 181: memory grows until the buffer is full", 4),
        ["round", "181:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 181: memory grows until the buffer is full", 8),
        ["round", "181:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 181: memory grows until the buffer is full", 12),
        ["round 181:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 181: memory grows until the buffer is full", 16),
        ["round 181:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 181: memory grows until the buffer is full", 24), ["round 181: memory grows", "until the buffer is full"]),
    (("round 181: memory grows until the buffer is full", 32), ["round 181: memory grows until", "the buffer is full"]),
    (
        ("round 181: the cluster mirrors every packet twice", 4),
        ["round", "181:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 181: the cluster mirrors every packet twice", 8),
        ["round", "181: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 181: the cluster mirrors every packet twice", 12),
        ["round 181:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 181: the cluster mirrors every packet twice", 16),
        ["round 181: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 181: the cluster mirrors every packet twice", 24),
        ["round 181: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 181: the cluster mirrors every packet twice", 32),
        ["round 181: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 181: ranking uses tokens learned from the corpus", 4),
        ["round", "181:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 181: ranking uses tokens learned from the corpus", 8),
        ["round", "181:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 181: ranking uses tokens learned from the corpus", 12),
        ["round 181:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 181: ranking uses tokens learned from the corpus", 16),
        ["round 181:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 181: ranking uses tokens learned from the corpus", 24),
        ["round 181: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 181: ranking uses tokens learned from the corpus", 32),
        ["round 181: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 181: a long session ends when the candle dies", 4),
        ["round", "181:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 181: a long session ends when the candle dies", 8),
        ["round", "181: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 181: a long session ends when the candle dies", 12),
        ["round 181: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 181: a long session ends when the candle dies", 16),
        ["round 181: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 181: a long session ends when the candle dies", 24),
        ["round 181: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 181: a long session ends when the candle dies", 32),
        ["round 181: a long session ends", "when the candle dies"],
    ),
    (
        ("round 181: encode the prompt then map the result", 4),
        ["round", "181:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 181: encode the prompt then map the result", 8),
        ["round", "181:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 181: encode the prompt then map the result", 12),
        ["round 181:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 181: encode the prompt then map the result", 16),
        ["round 181:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 181: encode the prompt then map the result", 24),
        ["round 181: encode the", "prompt then map the", "result"],
    ),
    (("round 181: encode the prompt then map the result", 32), ["round 181: encode the prompt", "then map the result"]),
    (
        ("round 181: the kernel wakes the worker at dawn", 4),
        ["round", "181:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 181: the kernel wakes the worker at dawn", 8),
        ["round", "181: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 181: the kernel wakes the worker at dawn", 12),
        ["round 181:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 181: the kernel wakes the worker at dawn", 16), ["round 181: the", "kernel wakes the", "worker at dawn"]),
    (("round 181: the kernel wakes the worker at dawn", 24), ["round 181: the kernel", "wakes the worker at dawn"]),
    (("round 181: the kernel wakes the worker at dawn", 32), ["round 181: the kernel wakes the", "worker at dawn"]),
    (
        ("round 181: service latency drops after the patch", 4),
        ["round", "181:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 181: service latency drops after the patch", 8),
        ["round", "181:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 181: service latency drops after the patch", 12),
        ["round 181:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 181: service latency drops after the patch", 16),
        ["round 181:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 181: service latency drops after the patch", 24),
        ["round 181: service", "latency drops after the", "patch"],
    ),
    (("round 181: service latency drops after the patch", 32), ["round 181: service latency drops", "after the patch"]),
    (
        ("round 181: the library caches every vector it sees", 4),
        ["round", "181:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 181: the library caches every vector it sees", 8),
        ["round", "181: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 181: the library caches every vector it sees", 12),
        ["round 181:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 181: the library caches every vector it sees", 16),
        ["round 181: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 181: the library caches every vector it sees", 24),
        ["round 181: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 181: the library caches every vector it sees", 32),
        ["round 181: the library caches", "every vector it sees"],
    ),
    (
        ("round 181: agents argue then the debate resolves", 4),
        ["round", "181:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 181: agents argue then the debate resolves", 8),
        ["round", "181:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 181: agents argue then the debate resolves", 12),
        ["round 181:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 181: agents argue then the debate resolves", 16),
        ["round 181:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 181: agents argue then the debate resolves", 24), ["round 181: agents argue", "then the debate resolves"]),
    (("round 181: agents argue then the debate resolves", 32), ["round 181: agents argue then the", "debate resolves"]),
    (
        ("round 181: the filter keeps only strong matches", 4),
        ["round", "181:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 181: the filter keeps only strong matches", 8),
        ["round", "181: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 181: the filter keeps only strong matches", 12),
        ["round 181:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 181: the filter keeps only strong matches", 16),
        ["round 181: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 181: the filter keeps only strong matches", 24),
        ["round 181: the filter", "keeps only strong", "matches"],
    ),
    (("round 181: the filter keeps only strong matches", 32), ["round 181: the filter keeps only", "strong matches"]),
    (
        ("round 181: the model answers with a short reply", 4),
        ["round", "181:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 181: the model answers with a short reply", 8),
        ["round", "181: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 181: the model answers with a short reply", 12),
        ["round 181:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 181: the model answers with a short reply", 16),
        ["round 181: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 181: the model answers with a short reply", 24),
        ["round 181: the model", "answers with a short", "reply"],
    ),
    (("round 181: the model answers with a short reply", 32), ["round 181: the model answers", "with a short reply"]),
    (
        ("round 181: the recorder stores the reasoning trace", 4),
        ["round", "181:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 181: the recorder stores the reasoning trace", 8),
        ["round", "181: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 181: the recorder stores the reasoning trace", 12),
        ["round 181:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 181: the recorder stores the reasoning trace", 16),
        ["round 181: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 181: the recorder stores the reasoning trace", 24),
        ["round 181: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 181: the recorder stores the reasoning trace", 32),
        ["round 181: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 181: the angel watches the processor run", 4),
        ["round", "181:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 181: the angel watches the processor run", 8),
        ["round", "181: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 181: the angel watches the processor run", 12),
        ["round 181:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 181: the angel watches the processor run", 16),
        ["round 181: the", "angel watches", "the processor", "run"],
    ),
    (("round 181: the angel watches the processor run", 24), ["round 181: the angel", "watches the processor", "run"]),
    (("round 181: the angel watches the processor run", 32), ["round 181: the angel watches the", "processor run"]),
    (
        ("round 181: angle of the vector decides the match", 4),
        ["round", "181:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 181: angle of the vector decides the match", 8),
        ["round", "181:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 181: angle of the vector decides the match", 12),
        ["round 181:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 181: angle of the vector decides the match", 16),
        ["round 181: angle", "of the vector", "decides the", "match"],
    ),
    (("round 181: angle of the vector decides the match", 24), ["round 181: angle of the", "vector decides the match"]),
    (("round 181: angle of the vector decides the match", 32), ["round 181: angle of the vector", "decides the match"]),
    (
        ("round 181: the candle burns twice as long at night", 4),
        ["round", "181:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 181: the candle burns twice as long at night", 8),
        ["round", "181: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 181: the candle burns twice as long at night", 12),
        ["round 181:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 181: the candle burns twice as long at night", 16),
        ["round 181: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 181: the candle burns twice as long at night", 24),
        ["round 181: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 181: the candle burns twice as long at night", 32),
        ["round 181: the candle burns", "twice as long at night"],
    ),
    (
        ("round 181: a mirror of the universe in one line", 4),
        ["round", "181:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 181: a mirror of the universe in one line", 8),
        ["round", "181: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 181: a mirror of the universe in one line", 12),
        ["round 181: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 181: a mirror of the universe in one line", 16),
        ["round 181: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 181: a mirror of the universe in one line", 24), ["round 181: a mirror of", "the universe in one line"]),
    (("round 181: a mirror of the universe in one line", 32), ["round 181: a mirror of the", "universe in one line"]),
    (
        ("round 181: the queue drains before the storm", 4),
        ["round", "181:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 181: the queue drains before the storm", 8),
        ["round", "181: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 181: the queue drains before the storm", 12),
        ["round 181:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 181: the queue drains before the storm", 16), ["round 181: the", "queue drains", "before the storm"]),
    (("round 181: the queue drains before the storm", 24), ["round 181: the queue", "drains before the storm"]),
    (("round 181: the queue drains before the storm", 32), ["round 181: the queue drains", "before the storm"]),
    (
        ("kitten181 sitting181 agent181 angle181 universe181 memory181", 6),
        ["kitten181", "sitting181", "agent181", "angle181", "universe181", "memory181"],
    ),
    (
        ("kitten181 sitting181 agent181 angle181 universe181 memory181", 10),
        ["kitten181", "sitting181", "agent181", "angle181", "universe181", "memory181"],
    ),
    (
        ("kitten181 sitting181 agent181 angle181 universe181 memory181", 18),
        ["kitten181", "sitting181", "agent181 angle181", "universe181", "memory181"],
    ),
    (
        ("kitten181 sitting181 agent181 angle181 universe181 memory181", 28),
        ["kitten181 sitting181", "agent181 angle181", "universe181 memory181"],
    ),
    (
        ("sitting181 agent181 angle181 universe181 memory181 stream181", 6),
        ["sitting181", "agent181", "angle181", "universe181", "memory181", "stream181"],
    ),
    (
        ("sitting181 agent181 angle181 universe181 memory181 stream181", 10),
        ["sitting181", "agent181", "angle181", "universe181", "memory181", "stream181"],
    ),
    (
        ("sitting181 agent181 angle181 universe181 memory181 stream181", 18),
        ["sitting181", "agent181 angle181", "universe181", "memory181", "stream181"],
    ),
    (
        ("sitting181 agent181 angle181 universe181 memory181 stream181", 28),
        ["sitting181 agent181 angle181", "universe181 memory181", "stream181"],
    ),
    (
        ("agent181 angle181 universe181 memory181 stream181 context181", 6),
        ["agent181", "angle181", "universe181", "memory181", "stream181", "context181"],
    ),
    (
        ("agent181 angle181 universe181 memory181 stream181 context181", 10),
        ["agent181", "angle181", "universe181", "memory181", "stream181", "context181"],
    ),
    (
        ("agent181 angle181 universe181 memory181 stream181 context181", 18),
        ["agent181 angle181", "universe181", "memory181", "stream181", "context181"],
    ),
    (
        ("agent181 angle181 universe181 memory181 stream181 context181", 28),
        ["agent181 angle181", "universe181 memory181", "stream181 context181"],
    ),
    (
        ("angle181 universe181 memory181 stream181 context181 knowledge181", 6),
        ["angle181", "universe181", "memory181", "stream181", "context181", "knowledge181"],
    ),
    (
        ("angle181 universe181 memory181 stream181 context181 knowledge181", 10),
        ["angle181", "universe181", "memory181", "stream181", "context181", "knowledge181"],
    ),
    (
        ("angle181 universe181 memory181 stream181 context181 knowledge181", 18),
        ["angle181", "universe181", "memory181", "stream181", "context181", "knowledge181"],
    ),
    (
        ("angle181 universe181 memory181 stream181 context181 knowledge181", 28),
        ["angle181 universe181", "memory181 stream181", "context181 knowledge181"],
    ),
    (
        ("universe181 memory181 stream181 context181 knowledge181 vector181", 6),
        ["universe181", "memory181", "stream181", "context181", "knowledge181", "vector181"],
    ),
    (
        ("universe181 memory181 stream181 context181 knowledge181 vector181", 10),
        ["universe181", "memory181", "stream181", "context181", "knowledge181", "vector181"],
    ),
    (
        ("universe181 memory181 stream181 context181 knowledge181 vector181", 18),
        ["universe181", "memory181", "stream181", "context181", "knowledge181", "vector181"],
    ),
    (
        ("universe181 memory181 stream181 context181 knowledge181 vector181", 28),
        ["universe181 memory181", "stream181 context181", "knowledge181 vector181"],
    ),
    (
        ("memory181 stream181 context181 knowledge181 vector181 processor181", 6),
        ["memory181", "stream181", "context181", "knowledge181", "vector181", "processor181"],
    ),
    (
        ("memory181 stream181 context181 knowledge181 vector181 processor181", 10),
        ["memory181", "stream181", "context181", "knowledge181", "vector181", "processor181"],
    ),
    (
        ("memory181 stream181 context181 knowledge181 vector181 processor181", 18),
        ["memory181", "stream181", "context181", "knowledge181", "vector181", "processor181"],
    ),
    (
        ("memory181 stream181 context181 knowledge181 vector181 processor181", 28),
        ["memory181 stream181", "context181 knowledge181", "vector181 processor181"],
    ),
    (
        ("stream181 context181 knowledge181 vector181 processor181 reasoning181", 6),
        ["stream181", "context181", "knowledge181", "vector181", "processor181", "reasoning181"],
    ),
    (
        ("stream181 context181 knowledge181 vector181 processor181 reasoning181", 10),
        ["stream181", "context181", "knowledge181", "vector181", "processor181", "reasoning181"],
    ),
    (
        ("stream181 context181 knowledge181 vector181 processor181 reasoning181", 18),
        ["stream181", "context181", "knowledge181", "vector181", "processor181", "reasoning181"],
    ),
    (
        ("stream181 context181 knowledge181 vector181 processor181 reasoning181", 28),
        ["stream181 context181", "knowledge181 vector181", "processor181 reasoning181"],
    ),
    (
        ("context181 knowledge181 vector181 processor181 reasoning181 machine181", 6),
        ["context181", "knowledge181", "vector181", "processor181", "reasoning181", "machine181"],
    ),
    (
        ("context181 knowledge181 vector181 processor181 reasoning181 machine181", 10),
        ["context181", "knowledge181", "vector181", "processor181", "reasoning181", "machine181"],
    ),
    (
        ("context181 knowledge181 vector181 processor181 reasoning181 machine181", 18),
        ["context181", "knowledge181", "vector181", "processor181", "reasoning181", "machine181"],
    ),
    (
        ("context181 knowledge181 vector181 processor181 reasoning181 machine181", 28),
        ["context181 knowledge181", "vector181 processor181", "reasoning181 machine181"],
    ),
    (
        ("knowledge181 vector181 processor181 reasoning181 machine181 learning181", 6),
        ["knowledge181", "vector181", "processor181", "reasoning181", "machine181", "learning181"],
    ),
    (
        ("knowledge181 vector181 processor181 reasoning181 machine181 learning181", 10),
        ["knowledge181", "vector181", "processor181", "reasoning181", "machine181", "learning181"],
    ),
    (
        ("knowledge181 vector181 processor181 reasoning181 machine181 learning181", 18),
        ["knowledge181", "vector181", "processor181", "reasoning181", "machine181", "learning181"],
    ),
    (
        ("knowledge181 vector181 processor181 reasoning181 machine181 learning181", 28),
        ["knowledge181 vector181", "processor181 reasoning181", "machine181 learning181"],
    ),
    (
        ("vector181 processor181 reasoning181 machine181 learning181 model181", 6),
        ["vector181", "processor181", "reasoning181", "machine181", "learning181", "model181"],
    ),
    (
        ("vector181 processor181 reasoning181 machine181 learning181 model181", 10),
        ["vector181", "processor181", "reasoning181", "machine181", "learning181", "model181"],
    ),
    (
        ("vector181 processor181 reasoning181 machine181 learning181 model181", 18),
        ["vector181", "processor181", "reasoning181", "machine181", "learning181", "model181"],
    ),
    (
        ("vector181 processor181 reasoning181 machine181 learning181 model181", 28),
        ["vector181 processor181", "reasoning181 machine181", "learning181 model181"],
    ),
    (
        ("processor181 reasoning181 machine181 learning181 model181 token181", 6),
        ["processor181", "reasoning181", "machine181", "learning181", "model181", "token181"],
    ),
    (
        ("processor181 reasoning181 machine181 learning181 model181 token181", 10),
        ["processor181", "reasoning181", "machine181", "learning181", "model181", "token181"],
    ),
    (
        ("processor181 reasoning181 machine181 learning181 model181 token181", 18),
        ["processor181", "reasoning181", "machine181", "learning181", "model181 token181"],
    ),
    (
        ("processor181 reasoning181 machine181 learning181 model181 token181", 28),
        ["processor181 reasoning181", "machine181 learning181", "model181 token181"],
    ),
    (
        ("reasoning181 machine181 learning181 model181 token181 prompt181", 6),
        ["reasoning181", "machine181", "learning181", "model181", "token181", "prompt181"],
    ),
    (
        ("reasoning181 machine181 learning181 model181 token181 prompt181", 10),
        ["reasoning181", "machine181", "learning181", "model181", "token181", "prompt181"],
    ),
    (
        ("reasoning181 machine181 learning181 model181 token181 prompt181", 18),
        ["reasoning181", "machine181", "learning181", "model181 token181", "prompt181"],
    ),
    (
        ("reasoning181 machine181 learning181 model181 token181 prompt181", 28),
        ["reasoning181 machine181", "learning181 model181", "token181 prompt181"],
    ),
    (
        ("machine181 learning181 model181 token181 prompt181 session181", 6),
        ["machine181", "learning181", "model181", "token181", "prompt181", "session181"],
    ),
    (
        ("machine181 learning181 model181 token181 prompt181 session181", 10),
        ["machine181", "learning181", "model181", "token181", "prompt181", "session181"],
    ),
    (
        ("machine181 learning181 model181 token181 prompt181 session181", 18),
        ["machine181", "learning181", "model181 token181", "prompt181", "session181"],
    ),
    (
        ("machine181 learning181 model181 token181 prompt181 session181", 28),
        ["machine181 learning181", "model181 token181 prompt181", "session181"],
    ),
    (
        ("learning181 model181 token181 prompt181 session181 library181", 6),
        ["learning181", "model181", "token181", "prompt181", "session181", "library181"],
    ),
    (
        ("learning181 model181 token181 prompt181 session181 library181", 10),
        ["learning181", "model181", "token181", "prompt181", "session181", "library181"],
    ),
    (
        ("learning181 model181 token181 prompt181 session181 library181", 18),
        ["learning181", "model181 token181", "prompt181", "session181", "library181"],
    ),
    (
        ("learning181 model181 token181 prompt181 session181 library181", 28),
        ["learning181 model181", "token181 prompt181", "session181 library181"],
    ),
    (
        ("model181 token181 prompt181 session181 library181 service181", 6),
        ["model181", "token181", "prompt181", "session181", "library181", "service181"],
    ),
    (
        ("model181 token181 prompt181 session181 library181 service181", 10),
        ["model181", "token181", "prompt181", "session181", "library181", "service181"],
    ),
    (
        ("model181 token181 prompt181 session181 library181 service181", 18),
        ["model181 token181", "prompt181", "session181", "library181", "service181"],
    ),
    (
        ("model181 token181 prompt181 session181 library181 service181", 28),
        ["model181 token181 prompt181", "session181 library181", "service181"],
    ),
    (
        ("token181 prompt181 session181 library181 service181 gateway181", 6),
        ["token181", "prompt181", "session181", "library181", "service181", "gateway181"],
    ),
    (
        ("token181 prompt181 session181 library181 service181 gateway181", 10),
        ["token181", "prompt181", "session181", "library181", "service181", "gateway181"],
    ),
    (
        ("token181 prompt181 session181 library181 service181 gateway181", 18),
        ["token181 prompt181", "session181", "library181", "service181", "gateway181"],
    ),
    (
        ("token181 prompt181 session181 library181 service181 gateway181", 28),
        ["token181 prompt181", "session181 library181", "service181 gateway181"],
    ),
    (
        ("prompt181 session181 library181 service181 gateway181 storage181", 6),
        ["prompt181", "session181", "library181", "service181", "gateway181", "storage181"],
    ),
    (
        ("prompt181 session181 library181 service181 gateway181 storage181", 10),
        ["prompt181", "session181", "library181", "service181", "gateway181", "storage181"],
    ),
    (
        ("prompt181 session181 library181 service181 gateway181 storage181", 18),
        ["prompt181", "session181", "library181", "service181", "gateway181", "storage181"],
    ),
    (
        ("prompt181 session181 library181 service181 gateway181 storage181", 28),
        ["prompt181 session181", "library181 service181", "gateway181 storage181"],
    ),
    (
        ("session181 library181 service181 gateway181 storage181 network181", 6),
        ["session181", "library181", "service181", "gateway181", "storage181", "network181"],
    ),
    (
        ("session181 library181 service181 gateway181 storage181 network181", 10),
        ["session181", "library181", "service181", "gateway181", "storage181", "network181"],
    ),
    (
        ("session181 library181 service181 gateway181 storage181 network181", 18),
        ["session181", "library181", "service181", "gateway181", "storage181", "network181"],
    ),
    (
        ("session181 library181 service181 gateway181 storage181 network181", 28),
        ["session181 library181", "service181 gateway181", "storage181 network181"],
    ),
    (
        ("library181 service181 gateway181 storage181 network181 latency181", 6),
        ["library181", "service181", "gateway181", "storage181", "network181", "latency181"],
    ),
    (
        ("library181 service181 gateway181 storage181 network181 latency181", 10),
        ["library181", "service181", "gateway181", "storage181", "network181", "latency181"],
    ),
    (
        ("library181 service181 gateway181 storage181 network181 latency181", 18),
        ["library181", "service181", "gateway181", "storage181", "network181", "latency181"],
    ),
    (
        ("library181 service181 gateway181 storage181 network181 latency181", 28),
        ["library181 service181", "gateway181 storage181", "network181 latency181"],
    ),
    (
        ("service181 gateway181 storage181 network181 latency181 buffer181", 6),
        ["service181", "gateway181", "storage181", "network181", "latency181", "buffer181"],
    ),
    (
        ("service181 gateway181 storage181 network181 latency181 buffer181", 10),
        ["service181", "gateway181", "storage181", "network181", "latency181", "buffer181"],
    ),
    (
        ("service181 gateway181 storage181 network181 latency181 buffer181", 18),
        ["service181", "gateway181", "storage181", "network181", "latency181", "buffer181"],
    ),
    (
        ("service181 gateway181 storage181 network181 latency181 buffer181", 28),
        ["service181 gateway181", "storage181 network181", "latency181 buffer181"],
    ),
    (
        ("gateway181 storage181 network181 latency181 buffer181 queue181", 6),
        ["gateway181", "storage181", "network181", "latency181", "buffer181", "queue181"],
    ),
    (
        ("gateway181 storage181 network181 latency181 buffer181 queue181", 10),
        ["gateway181", "storage181", "network181", "latency181", "buffer181", "queue181"],
    ),
    (
        ("gateway181 storage181 network181 latency181 buffer181 queue181", 18),
        ["gateway181", "storage181", "network181", "latency181", "buffer181 queue181"],
    ),
    (
        ("gateway181 storage181 network181 latency181 buffer181 queue181", 28),
        ["gateway181 storage181", "network181 latency181", "buffer181 queue181"],
    ),
    (
        ("storage181 network181 latency181 buffer181 queue181 worker181", 6),
        ["storage181", "network181", "latency181", "buffer181", "queue181", "worker181"],
    ),
    (
        ("storage181 network181 latency181 buffer181 queue181 worker181", 10),
        ["storage181", "network181", "latency181", "buffer181", "queue181", "worker181"],
    ),
    (
        ("storage181 network181 latency181 buffer181 queue181 worker181", 18),
        ["storage181", "network181", "latency181", "buffer181 queue181", "worker181"],
    ),
    (
        ("storage181 network181 latency181 buffer181 queue181 worker181", 28),
        ["storage181 network181", "latency181 buffer181", "queue181 worker181"],
    ),
    (
        ("network181 latency181 buffer181 queue181 worker181 kernel181", 6),
        ["network181", "latency181", "buffer181", "queue181", "worker181", "kernel181"],
    ),
    (
        ("network181 latency181 buffer181 queue181 worker181 kernel181", 10),
        ["network181", "latency181", "buffer181", "queue181", "worker181", "kernel181"],
    ),
    (
        ("network181 latency181 buffer181 queue181 worker181 kernel181", 18),
        ["network181", "latency181", "buffer181 queue181", "worker181", "kernel181"],
    ),
    (
        ("network181 latency181 buffer181 queue181 worker181 kernel181", 28),
        ["network181 latency181", "buffer181 queue181 worker181", "kernel181"],
    ),
    (
        ("latency181 buffer181 queue181 worker181 kernel181 signal181", 6),
        ["latency181", "buffer181", "queue181", "worker181", "kernel181", "signal181"],
    ),
    (
        ("latency181 buffer181 queue181 worker181 kernel181 signal181", 10),
        ["latency181", "buffer181", "queue181", "worker181", "kernel181", "signal181"],
    ),
    (
        ("latency181 buffer181 queue181 worker181 kernel181 signal181", 18),
        ["latency181", "buffer181 queue181", "worker181", "kernel181", "signal181"],
    ),
    (
        ("latency181 buffer181 queue181 worker181 kernel181 signal181", 28),
        ["latency181 buffer181", "queue181 worker181 kernel181", "signal181"],
    ),
    (
        ("buffer181 queue181 worker181 kernel181 signal181 packet181", 6),
        ["buffer181", "queue181", "worker181", "kernel181", "signal181", "packet181"],
    ),
    (
        ("buffer181 queue181 worker181 kernel181 signal181 packet181", 10),
        ["buffer181", "queue181", "worker181", "kernel181", "signal181", "packet181"],
    ),
    (
        ("buffer181 queue181 worker181 kernel181 signal181 packet181", 18),
        ["buffer181 queue181", "worker181", "kernel181", "signal181", "packet181"],
    ),
    (
        ("buffer181 queue181 worker181 kernel181 signal181 packet181", 28),
        ["buffer181 queue181 worker181", "kernel181 signal181", "packet181"],
    ),
    (
        ("queue181 worker181 kernel181 signal181 packet181 router181", 6),
        ["queue181", "worker181", "kernel181", "signal181", "packet181", "router181"],
    ),
    (
        ("queue181 worker181 kernel181 signal181 packet181 router181", 10),
        ["queue181", "worker181", "kernel181", "signal181", "packet181", "router181"],
    ),
    (
        ("queue181 worker181 kernel181 signal181 packet181 router181", 18),
        ["queue181 worker181", "kernel181", "signal181", "packet181", "router181"],
    ),
    (
        ("queue181 worker181 kernel181 signal181 packet181 router181", 28),
        ["queue181 worker181 kernel181", "signal181 packet181", "router181"],
    ),
    (
        ("worker181 kernel181 signal181 packet181 router181 cluster181", 6),
        ["worker181", "kernel181", "signal181", "packet181", "router181", "cluster181"],
    ),
    (
        ("worker181 kernel181 signal181 packet181 router181 cluster181", 10),
        ["worker181", "kernel181", "signal181", "packet181", "router181", "cluster181"],
    ),
    (
        ("worker181 kernel181 signal181 packet181 router181 cluster181", 18),
        ["worker181", "kernel181", "signal181", "packet181", "router181", "cluster181"],
    ),
    (
        ("worker181 kernel181 signal181 packet181 router181 cluster181", 28),
        ["worker181 kernel181", "signal181 packet181", "router181 cluster181"],
    ),
    (
        ("kernel181 signal181 packet181 router181 cluster181 mirror181", 6),
        ["kernel181", "signal181", "packet181", "router181", "cluster181", "mirror181"],
    ),
    (
        ("kernel181 signal181 packet181 router181 cluster181 mirror181", 10),
        ["kernel181", "signal181", "packet181", "router181", "cluster181", "mirror181"],
    ),
    (
        ("kernel181 signal181 packet181 router181 cluster181 mirror181", 18),
        ["kernel181", "signal181", "packet181", "router181", "cluster181", "mirror181"],
    ),
    (
        ("kernel181 signal181 packet181 router181 cluster181 mirror181", 28),
        ["kernel181 signal181", "packet181 router181", "cluster181 mirror181"],
    ),
    (
        ("signal181 packet181 router181 cluster181 mirror181 filter181", 6),
        ["signal181", "packet181", "router181", "cluster181", "mirror181", "filter181"],
    ),
    (
        ("signal181 packet181 router181 cluster181 mirror181 filter181", 10),
        ["signal181", "packet181", "router181", "cluster181", "mirror181", "filter181"],
    ),
    (
        ("signal181 packet181 router181 cluster181 mirror181 filter181", 18),
        ["signal181", "packet181", "router181", "cluster181", "mirror181", "filter181"],
    ),
    (
        ("signal181 packet181 router181 cluster181 mirror181 filter181", 28),
        ["signal181 packet181", "router181 cluster181", "mirror181 filter181"],
    ),
    (
        ("packet181 router181 cluster181 mirror181 filter181 ranking181", 6),
        ["packet181", "router181", "cluster181", "mirror181", "filter181", "ranking181"],
    ),
    (
        ("packet181 router181 cluster181 mirror181 filter181 ranking181", 10),
        ["packet181", "router181", "cluster181", "mirror181", "filter181", "ranking181"],
    ),
    (
        ("packet181 router181 cluster181 mirror181 filter181 ranking181", 18),
        ["packet181", "router181", "cluster181", "mirror181", "filter181", "ranking181"],
    ),
    (
        ("packet181 router181 cluster181 mirror181 filter181 ranking181", 28),
        ["packet181 router181", "cluster181 mirror181", "filter181 ranking181"],
    ),
    (
        ("router181 cluster181 mirror181 filter181 ranking181 encoding181", 6),
        ["router181", "cluster181", "mirror181", "filter181", "ranking181", "encoding181"],
    ),
    (
        ("router181 cluster181 mirror181 filter181 ranking181 encoding181", 10),
        ["router181", "cluster181", "mirror181", "filter181", "ranking181", "encoding181"],
    ),
    (
        ("router181 cluster181 mirror181 filter181 ranking181 encoding181", 18),
        ["router181", "cluster181", "mirror181", "filter181", "ranking181", "encoding181"],
    ),
    (
        ("router181 cluster181 mirror181 filter181 ranking181 encoding181", 28),
        ["router181 cluster181", "mirror181 filter181", "ranking181 encoding181"],
    ),
    (
        ("cluster181 mirror181 filter181 ranking181 encoding181 mapping181", 6),
        ["cluster181", "mirror181", "filter181", "ranking181", "encoding181", "mapping181"],
    ),
    (
        ("cluster181 mirror181 filter181 ranking181 encoding181 mapping181", 10),
        ["cluster181", "mirror181", "filter181", "ranking181", "encoding181", "mapping181"],
    ),
    (
        ("cluster181 mirror181 filter181 ranking181 encoding181 mapping181", 18),
        ["cluster181", "mirror181", "filter181", "ranking181", "encoding181", "mapping181"],
    ),
    (
        ("cluster181 mirror181 filter181 ranking181 encoding181 mapping181", 28),
        ["cluster181 mirror181", "filter181 ranking181", "encoding181 mapping181"],
    ),
    (
        ("mirror181 filter181 ranking181 encoding181 mapping181 record181", 6),
        ["mirror181", "filter181", "ranking181", "encoding181", "mapping181", "record181"],
    ),
    (
        ("mirror181 filter181 ranking181 encoding181 mapping181 record181", 10),
        ["mirror181", "filter181", "ranking181", "encoding181", "mapping181", "record181"],
    ),
    (
        ("mirror181 filter181 ranking181 encoding181 mapping181 record181", 18),
        ["mirror181", "filter181", "ranking181", "encoding181", "mapping181", "record181"],
    ),
    (
        ("mirror181 filter181 ranking181 encoding181 mapping181 record181", 28),
        ["mirror181 filter181", "ranking181 encoding181", "mapping181 record181"],
    ),
    (
        ("filter181 ranking181 encoding181 mapping181 record181 candle181", 6),
        ["filter181", "ranking181", "encoding181", "mapping181", "record181", "candle181"],
    ),
    (
        ("filter181 ranking181 encoding181 mapping181 record181 candle181", 10),
        ["filter181", "ranking181", "encoding181", "mapping181", "record181", "candle181"],
    ),
    (
        ("filter181 ranking181 encoding181 mapping181 record181 candle181", 18),
        ["filter181", "ranking181", "encoding181", "mapping181", "record181", "candle181"],
    ),
    (
        ("filter181 ranking181 encoding181 mapping181 record181 candle181", 28),
        ["filter181 ranking181", "encoding181 mapping181", "record181 candle181"],
    ),
    (
        ("ranking181 encoding181 mapping181 record181 candle181 thread181", 6),
        ["ranking181", "encoding181", "mapping181", "record181", "candle181", "thread181"],
    ),
    (
        ("ranking181 encoding181 mapping181 record181 candle181 thread181", 10),
        ["ranking181", "encoding181", "mapping181", "record181", "candle181", "thread181"],
    ),
    (
        ("ranking181 encoding181 mapping181 record181 candle181 thread181", 18),
        ["ranking181", "encoding181", "mapping181", "record181", "candle181", "thread181"],
    ),
    (
        ("ranking181 encoding181 mapping181 record181 candle181 thread181", 28),
        ["ranking181 encoding181", "mapping181 record181", "candle181 thread181"],
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
