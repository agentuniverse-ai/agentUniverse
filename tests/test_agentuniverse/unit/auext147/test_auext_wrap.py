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
        ("round 147: the quick brown fox jumps over the lazy dog", 4),
        ["round", "147:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 147: the quick brown fox jumps over the lazy dog", 8),
        ["round", "147: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 147: the quick brown fox jumps over the lazy dog", 12),
        ["round 147:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 147: the quick brown fox jumps over the lazy dog", 16),
        ["round 147: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 147: the quick brown fox jumps over the lazy dog", 24),
        ["round 147: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 147: the quick brown fox jumps over the lazy dog", 32),
        ["round 147: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 147: agentuniverse is a framework for multi agents", 4),
        ["round", "147:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 147: agentuniverse is a framework for multi agents", 8),
        ["round", "147:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 147: agentuniverse is a framework for multi agents", 12),
        ["round 147:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 147: agentuniverse is a framework for multi agents", 16),
        ["round 147:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 147: agentuniverse is a framework for multi agents", 24),
        ["round 147: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 147: agentuniverse is a framework for multi agents", 32),
        ["round 147: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 147: knowledge stored as vectors enables retrieval", 4),
        ["round", "147:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 147: knowledge stored as vectors enables retrieval", 8),
        ["round", "147:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 147: knowledge stored as vectors enables retrieval", 12),
        ["round 147:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 147: knowledge stored as vectors enables retrieval", 16),
        ["round 147:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 147: knowledge stored as vectors enables retrieval", 24),
        ["round 147: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 147: knowledge stored as vectors enables retrieval", 32),
        ["round 147: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 147: the processor reads the record then stops", 4),
        ["round", "147:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 147: the processor reads the record then stops", 8),
        ["round", "147: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 147: the processor reads the record then stops", 12),
        ["round 147:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 147: the processor reads the record then stops", 16),
        ["round 147: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 147: the processor reads the record then stops", 24),
        ["round 147: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 147: the processor reads the record then stops", 32),
        ["round 147: the processor reads", "the record then stops"],
    ),
    (
        ("round 147: a worker pulls the next task from the queue", 4),
        ["round", "147:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 147: a worker pulls the next task from the queue", 8),
        ["round", "147: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 147: a worker pulls the next task from the queue", 12),
        ["round 147: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 147: a worker pulls the next task from the queue", 16),
        ["round 147: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 147: a worker pulls the next task from the queue", 24),
        ["round 147: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 147: a worker pulls the next task from the queue", 32),
        ["round 147: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 147: signals travel through the network layer", 4),
        ["round", "147:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 147: signals travel through the network layer", 8),
        ["round", "147:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 147: signals travel through the network layer", 12),
        ["round 147:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 147: signals travel through the network layer", 16),
        ["round 147:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 147: signals travel through the network layer", 24),
        ["round 147: signals", "travel through the", "network layer"],
    ),
    (
        ("round 147: signals travel through the network layer", 32),
        ["round 147: signals travel", "through the network layer"],
    ),
    (
        ("round 147: the gateway routes each request by policy", 4),
        ["round", "147:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 147: the gateway routes each request by policy", 8),
        ["round", "147: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 147: the gateway routes each request by policy", 12),
        ["round 147:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 147: the gateway routes each request by policy", 16),
        ["round 147: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 147: the gateway routes each request by policy", 24),
        ["round 147: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 147: the gateway routes each request by policy", 32),
        ["round 147: the gateway routes", "each request by policy"],
    ),
    (
        ("round 147: memory grows until the buffer is full", 4),
        ["round", "147:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 147: memory grows until the buffer is full", 8),
        ["round", "147:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 147: memory grows until the buffer is full", 12),
        ["round 147:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 147: memory grows until the buffer is full", 16),
        ["round 147:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 147: memory grows until the buffer is full", 24), ["round 147: memory grows", "until the buffer is full"]),
    (("round 147: memory grows until the buffer is full", 32), ["round 147: memory grows until", "the buffer is full"]),
    (
        ("round 147: the cluster mirrors every packet twice", 4),
        ["round", "147:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 147: the cluster mirrors every packet twice", 8),
        ["round", "147: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 147: the cluster mirrors every packet twice", 12),
        ["round 147:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 147: the cluster mirrors every packet twice", 16),
        ["round 147: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 147: the cluster mirrors every packet twice", 24),
        ["round 147: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 147: the cluster mirrors every packet twice", 32),
        ["round 147: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 147: ranking uses tokens learned from the corpus", 4),
        ["round", "147:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 147: ranking uses tokens learned from the corpus", 8),
        ["round", "147:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 147: ranking uses tokens learned from the corpus", 12),
        ["round 147:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 147: ranking uses tokens learned from the corpus", 16),
        ["round 147:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 147: ranking uses tokens learned from the corpus", 24),
        ["round 147: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 147: ranking uses tokens learned from the corpus", 32),
        ["round 147: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 147: a long session ends when the candle dies", 4),
        ["round", "147:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 147: a long session ends when the candle dies", 8),
        ["round", "147: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 147: a long session ends when the candle dies", 12),
        ["round 147: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 147: a long session ends when the candle dies", 16),
        ["round 147: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 147: a long session ends when the candle dies", 24),
        ["round 147: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 147: a long session ends when the candle dies", 32),
        ["round 147: a long session ends", "when the candle dies"],
    ),
    (
        ("round 147: encode the prompt then map the result", 4),
        ["round", "147:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 147: encode the prompt then map the result", 8),
        ["round", "147:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 147: encode the prompt then map the result", 12),
        ["round 147:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 147: encode the prompt then map the result", 16),
        ["round 147:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 147: encode the prompt then map the result", 24),
        ["round 147: encode the", "prompt then map the", "result"],
    ),
    (("round 147: encode the prompt then map the result", 32), ["round 147: encode the prompt", "then map the result"]),
    (
        ("round 147: the kernel wakes the worker at dawn", 4),
        ["round", "147:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 147: the kernel wakes the worker at dawn", 8),
        ["round", "147: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 147: the kernel wakes the worker at dawn", 12),
        ["round 147:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 147: the kernel wakes the worker at dawn", 16), ["round 147: the", "kernel wakes the", "worker at dawn"]),
    (("round 147: the kernel wakes the worker at dawn", 24), ["round 147: the kernel", "wakes the worker at dawn"]),
    (("round 147: the kernel wakes the worker at dawn", 32), ["round 147: the kernel wakes the", "worker at dawn"]),
    (
        ("round 147: service latency drops after the patch", 4),
        ["round", "147:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 147: service latency drops after the patch", 8),
        ["round", "147:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 147: service latency drops after the patch", 12),
        ["round 147:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 147: service latency drops after the patch", 16),
        ["round 147:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 147: service latency drops after the patch", 24),
        ["round 147: service", "latency drops after the", "patch"],
    ),
    (("round 147: service latency drops after the patch", 32), ["round 147: service latency drops", "after the patch"]),
    (
        ("round 147: the library caches every vector it sees", 4),
        ["round", "147:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 147: the library caches every vector it sees", 8),
        ["round", "147: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 147: the library caches every vector it sees", 12),
        ["round 147:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 147: the library caches every vector it sees", 16),
        ["round 147: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 147: the library caches every vector it sees", 24),
        ["round 147: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 147: the library caches every vector it sees", 32),
        ["round 147: the library caches", "every vector it sees"],
    ),
    (
        ("round 147: agents argue then the debate resolves", 4),
        ["round", "147:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 147: agents argue then the debate resolves", 8),
        ["round", "147:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 147: agents argue then the debate resolves", 12),
        ["round 147:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 147: agents argue then the debate resolves", 16),
        ["round 147:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 147: agents argue then the debate resolves", 24), ["round 147: agents argue", "then the debate resolves"]),
    (("round 147: agents argue then the debate resolves", 32), ["round 147: agents argue then the", "debate resolves"]),
    (
        ("round 147: the filter keeps only strong matches", 4),
        ["round", "147:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 147: the filter keeps only strong matches", 8),
        ["round", "147: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 147: the filter keeps only strong matches", 12),
        ["round 147:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 147: the filter keeps only strong matches", 16),
        ["round 147: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 147: the filter keeps only strong matches", 24),
        ["round 147: the filter", "keeps only strong", "matches"],
    ),
    (("round 147: the filter keeps only strong matches", 32), ["round 147: the filter keeps only", "strong matches"]),
    (
        ("round 147: the model answers with a short reply", 4),
        ["round", "147:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 147: the model answers with a short reply", 8),
        ["round", "147: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 147: the model answers with a short reply", 12),
        ["round 147:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 147: the model answers with a short reply", 16),
        ["round 147: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 147: the model answers with a short reply", 24),
        ["round 147: the model", "answers with a short", "reply"],
    ),
    (("round 147: the model answers with a short reply", 32), ["round 147: the model answers", "with a short reply"]),
    (
        ("round 147: the recorder stores the reasoning trace", 4),
        ["round", "147:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 147: the recorder stores the reasoning trace", 8),
        ["round", "147: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 147: the recorder stores the reasoning trace", 12),
        ["round 147:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 147: the recorder stores the reasoning trace", 16),
        ["round 147: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 147: the recorder stores the reasoning trace", 24),
        ["round 147: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 147: the recorder stores the reasoning trace", 32),
        ["round 147: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 147: the angel watches the processor run", 4),
        ["round", "147:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 147: the angel watches the processor run", 8),
        ["round", "147: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 147: the angel watches the processor run", 12),
        ["round 147:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 147: the angel watches the processor run", 16),
        ["round 147: the", "angel watches", "the processor", "run"],
    ),
    (("round 147: the angel watches the processor run", 24), ["round 147: the angel", "watches the processor", "run"]),
    (("round 147: the angel watches the processor run", 32), ["round 147: the angel watches the", "processor run"]),
    (
        ("round 147: angle of the vector decides the match", 4),
        ["round", "147:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 147: angle of the vector decides the match", 8),
        ["round", "147:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 147: angle of the vector decides the match", 12),
        ["round 147:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 147: angle of the vector decides the match", 16),
        ["round 147: angle", "of the vector", "decides the", "match"],
    ),
    (("round 147: angle of the vector decides the match", 24), ["round 147: angle of the", "vector decides the match"]),
    (("round 147: angle of the vector decides the match", 32), ["round 147: angle of the vector", "decides the match"]),
    (
        ("round 147: the candle burns twice as long at night", 4),
        ["round", "147:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 147: the candle burns twice as long at night", 8),
        ["round", "147: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 147: the candle burns twice as long at night", 12),
        ["round 147:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 147: the candle burns twice as long at night", 16),
        ["round 147: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 147: the candle burns twice as long at night", 24),
        ["round 147: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 147: the candle burns twice as long at night", 32),
        ["round 147: the candle burns", "twice as long at night"],
    ),
    (
        ("round 147: a mirror of the universe in one line", 4),
        ["round", "147:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 147: a mirror of the universe in one line", 8),
        ["round", "147: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 147: a mirror of the universe in one line", 12),
        ["round 147: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 147: a mirror of the universe in one line", 16),
        ["round 147: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 147: a mirror of the universe in one line", 24), ["round 147: a mirror of", "the universe in one line"]),
    (("round 147: a mirror of the universe in one line", 32), ["round 147: a mirror of the", "universe in one line"]),
    (
        ("round 147: the queue drains before the storm", 4),
        ["round", "147:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 147: the queue drains before the storm", 8),
        ["round", "147: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 147: the queue drains before the storm", 12),
        ["round 147:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 147: the queue drains before the storm", 16), ["round 147: the", "queue drains", "before the storm"]),
    (("round 147: the queue drains before the storm", 24), ["round 147: the queue", "drains before the storm"]),
    (("round 147: the queue drains before the storm", 32), ["round 147: the queue drains", "before the storm"]),
    (
        ("kitten147 sitting147 agent147 angle147 universe147 memory147", 6),
        ["kitten147", "sitting147", "agent147", "angle147", "universe147", "memory147"],
    ),
    (
        ("kitten147 sitting147 agent147 angle147 universe147 memory147", 10),
        ["kitten147", "sitting147", "agent147", "angle147", "universe147", "memory147"],
    ),
    (
        ("kitten147 sitting147 agent147 angle147 universe147 memory147", 18),
        ["kitten147", "sitting147", "agent147 angle147", "universe147", "memory147"],
    ),
    (
        ("kitten147 sitting147 agent147 angle147 universe147 memory147", 28),
        ["kitten147 sitting147", "agent147 angle147", "universe147 memory147"],
    ),
    (
        ("sitting147 agent147 angle147 universe147 memory147 stream147", 6),
        ["sitting147", "agent147", "angle147", "universe147", "memory147", "stream147"],
    ),
    (
        ("sitting147 agent147 angle147 universe147 memory147 stream147", 10),
        ["sitting147", "agent147", "angle147", "universe147", "memory147", "stream147"],
    ),
    (
        ("sitting147 agent147 angle147 universe147 memory147 stream147", 18),
        ["sitting147", "agent147 angle147", "universe147", "memory147", "stream147"],
    ),
    (
        ("sitting147 agent147 angle147 universe147 memory147 stream147", 28),
        ["sitting147 agent147 angle147", "universe147 memory147", "stream147"],
    ),
    (
        ("agent147 angle147 universe147 memory147 stream147 context147", 6),
        ["agent147", "angle147", "universe147", "memory147", "stream147", "context147"],
    ),
    (
        ("agent147 angle147 universe147 memory147 stream147 context147", 10),
        ["agent147", "angle147", "universe147", "memory147", "stream147", "context147"],
    ),
    (
        ("agent147 angle147 universe147 memory147 stream147 context147", 18),
        ["agent147 angle147", "universe147", "memory147", "stream147", "context147"],
    ),
    (
        ("agent147 angle147 universe147 memory147 stream147 context147", 28),
        ["agent147 angle147", "universe147 memory147", "stream147 context147"],
    ),
    (
        ("angle147 universe147 memory147 stream147 context147 knowledge147", 6),
        ["angle147", "universe147", "memory147", "stream147", "context147", "knowledge147"],
    ),
    (
        ("angle147 universe147 memory147 stream147 context147 knowledge147", 10),
        ["angle147", "universe147", "memory147", "stream147", "context147", "knowledge147"],
    ),
    (
        ("angle147 universe147 memory147 stream147 context147 knowledge147", 18),
        ["angle147", "universe147", "memory147", "stream147", "context147", "knowledge147"],
    ),
    (
        ("angle147 universe147 memory147 stream147 context147 knowledge147", 28),
        ["angle147 universe147", "memory147 stream147", "context147 knowledge147"],
    ),
    (
        ("universe147 memory147 stream147 context147 knowledge147 vector147", 6),
        ["universe147", "memory147", "stream147", "context147", "knowledge147", "vector147"],
    ),
    (
        ("universe147 memory147 stream147 context147 knowledge147 vector147", 10),
        ["universe147", "memory147", "stream147", "context147", "knowledge147", "vector147"],
    ),
    (
        ("universe147 memory147 stream147 context147 knowledge147 vector147", 18),
        ["universe147", "memory147", "stream147", "context147", "knowledge147", "vector147"],
    ),
    (
        ("universe147 memory147 stream147 context147 knowledge147 vector147", 28),
        ["universe147 memory147", "stream147 context147", "knowledge147 vector147"],
    ),
    (
        ("memory147 stream147 context147 knowledge147 vector147 processor147", 6),
        ["memory147", "stream147", "context147", "knowledge147", "vector147", "processor147"],
    ),
    (
        ("memory147 stream147 context147 knowledge147 vector147 processor147", 10),
        ["memory147", "stream147", "context147", "knowledge147", "vector147", "processor147"],
    ),
    (
        ("memory147 stream147 context147 knowledge147 vector147 processor147", 18),
        ["memory147", "stream147", "context147", "knowledge147", "vector147", "processor147"],
    ),
    (
        ("memory147 stream147 context147 knowledge147 vector147 processor147", 28),
        ["memory147 stream147", "context147 knowledge147", "vector147 processor147"],
    ),
    (
        ("stream147 context147 knowledge147 vector147 processor147 reasoning147", 6),
        ["stream147", "context147", "knowledge147", "vector147", "processor147", "reasoning147"],
    ),
    (
        ("stream147 context147 knowledge147 vector147 processor147 reasoning147", 10),
        ["stream147", "context147", "knowledge147", "vector147", "processor147", "reasoning147"],
    ),
    (
        ("stream147 context147 knowledge147 vector147 processor147 reasoning147", 18),
        ["stream147", "context147", "knowledge147", "vector147", "processor147", "reasoning147"],
    ),
    (
        ("stream147 context147 knowledge147 vector147 processor147 reasoning147", 28),
        ["stream147 context147", "knowledge147 vector147", "processor147 reasoning147"],
    ),
    (
        ("context147 knowledge147 vector147 processor147 reasoning147 machine147", 6),
        ["context147", "knowledge147", "vector147", "processor147", "reasoning147", "machine147"],
    ),
    (
        ("context147 knowledge147 vector147 processor147 reasoning147 machine147", 10),
        ["context147", "knowledge147", "vector147", "processor147", "reasoning147", "machine147"],
    ),
    (
        ("context147 knowledge147 vector147 processor147 reasoning147 machine147", 18),
        ["context147", "knowledge147", "vector147", "processor147", "reasoning147", "machine147"],
    ),
    (
        ("context147 knowledge147 vector147 processor147 reasoning147 machine147", 28),
        ["context147 knowledge147", "vector147 processor147", "reasoning147 machine147"],
    ),
    (
        ("knowledge147 vector147 processor147 reasoning147 machine147 learning147", 6),
        ["knowledge147", "vector147", "processor147", "reasoning147", "machine147", "learning147"],
    ),
    (
        ("knowledge147 vector147 processor147 reasoning147 machine147 learning147", 10),
        ["knowledge147", "vector147", "processor147", "reasoning147", "machine147", "learning147"],
    ),
    (
        ("knowledge147 vector147 processor147 reasoning147 machine147 learning147", 18),
        ["knowledge147", "vector147", "processor147", "reasoning147", "machine147", "learning147"],
    ),
    (
        ("knowledge147 vector147 processor147 reasoning147 machine147 learning147", 28),
        ["knowledge147 vector147", "processor147 reasoning147", "machine147 learning147"],
    ),
    (
        ("vector147 processor147 reasoning147 machine147 learning147 model147", 6),
        ["vector147", "processor147", "reasoning147", "machine147", "learning147", "model147"],
    ),
    (
        ("vector147 processor147 reasoning147 machine147 learning147 model147", 10),
        ["vector147", "processor147", "reasoning147", "machine147", "learning147", "model147"],
    ),
    (
        ("vector147 processor147 reasoning147 machine147 learning147 model147", 18),
        ["vector147", "processor147", "reasoning147", "machine147", "learning147", "model147"],
    ),
    (
        ("vector147 processor147 reasoning147 machine147 learning147 model147", 28),
        ["vector147 processor147", "reasoning147 machine147", "learning147 model147"],
    ),
    (
        ("processor147 reasoning147 machine147 learning147 model147 token147", 6),
        ["processor147", "reasoning147", "machine147", "learning147", "model147", "token147"],
    ),
    (
        ("processor147 reasoning147 machine147 learning147 model147 token147", 10),
        ["processor147", "reasoning147", "machine147", "learning147", "model147", "token147"],
    ),
    (
        ("processor147 reasoning147 machine147 learning147 model147 token147", 18),
        ["processor147", "reasoning147", "machine147", "learning147", "model147 token147"],
    ),
    (
        ("processor147 reasoning147 machine147 learning147 model147 token147", 28),
        ["processor147 reasoning147", "machine147 learning147", "model147 token147"],
    ),
    (
        ("reasoning147 machine147 learning147 model147 token147 prompt147", 6),
        ["reasoning147", "machine147", "learning147", "model147", "token147", "prompt147"],
    ),
    (
        ("reasoning147 machine147 learning147 model147 token147 prompt147", 10),
        ["reasoning147", "machine147", "learning147", "model147", "token147", "prompt147"],
    ),
    (
        ("reasoning147 machine147 learning147 model147 token147 prompt147", 18),
        ["reasoning147", "machine147", "learning147", "model147 token147", "prompt147"],
    ),
    (
        ("reasoning147 machine147 learning147 model147 token147 prompt147", 28),
        ["reasoning147 machine147", "learning147 model147", "token147 prompt147"],
    ),
    (
        ("machine147 learning147 model147 token147 prompt147 session147", 6),
        ["machine147", "learning147", "model147", "token147", "prompt147", "session147"],
    ),
    (
        ("machine147 learning147 model147 token147 prompt147 session147", 10),
        ["machine147", "learning147", "model147", "token147", "prompt147", "session147"],
    ),
    (
        ("machine147 learning147 model147 token147 prompt147 session147", 18),
        ["machine147", "learning147", "model147 token147", "prompt147", "session147"],
    ),
    (
        ("machine147 learning147 model147 token147 prompt147 session147", 28),
        ["machine147 learning147", "model147 token147 prompt147", "session147"],
    ),
    (
        ("learning147 model147 token147 prompt147 session147 library147", 6),
        ["learning147", "model147", "token147", "prompt147", "session147", "library147"],
    ),
    (
        ("learning147 model147 token147 prompt147 session147 library147", 10),
        ["learning147", "model147", "token147", "prompt147", "session147", "library147"],
    ),
    (
        ("learning147 model147 token147 prompt147 session147 library147", 18),
        ["learning147", "model147 token147", "prompt147", "session147", "library147"],
    ),
    (
        ("learning147 model147 token147 prompt147 session147 library147", 28),
        ["learning147 model147", "token147 prompt147", "session147 library147"],
    ),
    (
        ("model147 token147 prompt147 session147 library147 service147", 6),
        ["model147", "token147", "prompt147", "session147", "library147", "service147"],
    ),
    (
        ("model147 token147 prompt147 session147 library147 service147", 10),
        ["model147", "token147", "prompt147", "session147", "library147", "service147"],
    ),
    (
        ("model147 token147 prompt147 session147 library147 service147", 18),
        ["model147 token147", "prompt147", "session147", "library147", "service147"],
    ),
    (
        ("model147 token147 prompt147 session147 library147 service147", 28),
        ["model147 token147 prompt147", "session147 library147", "service147"],
    ),
    (
        ("token147 prompt147 session147 library147 service147 gateway147", 6),
        ["token147", "prompt147", "session147", "library147", "service147", "gateway147"],
    ),
    (
        ("token147 prompt147 session147 library147 service147 gateway147", 10),
        ["token147", "prompt147", "session147", "library147", "service147", "gateway147"],
    ),
    (
        ("token147 prompt147 session147 library147 service147 gateway147", 18),
        ["token147 prompt147", "session147", "library147", "service147", "gateway147"],
    ),
    (
        ("token147 prompt147 session147 library147 service147 gateway147", 28),
        ["token147 prompt147", "session147 library147", "service147 gateway147"],
    ),
    (
        ("prompt147 session147 library147 service147 gateway147 storage147", 6),
        ["prompt147", "session147", "library147", "service147", "gateway147", "storage147"],
    ),
    (
        ("prompt147 session147 library147 service147 gateway147 storage147", 10),
        ["prompt147", "session147", "library147", "service147", "gateway147", "storage147"],
    ),
    (
        ("prompt147 session147 library147 service147 gateway147 storage147", 18),
        ["prompt147", "session147", "library147", "service147", "gateway147", "storage147"],
    ),
    (
        ("prompt147 session147 library147 service147 gateway147 storage147", 28),
        ["prompt147 session147", "library147 service147", "gateway147 storage147"],
    ),
    (
        ("session147 library147 service147 gateway147 storage147 network147", 6),
        ["session147", "library147", "service147", "gateway147", "storage147", "network147"],
    ),
    (
        ("session147 library147 service147 gateway147 storage147 network147", 10),
        ["session147", "library147", "service147", "gateway147", "storage147", "network147"],
    ),
    (
        ("session147 library147 service147 gateway147 storage147 network147", 18),
        ["session147", "library147", "service147", "gateway147", "storage147", "network147"],
    ),
    (
        ("session147 library147 service147 gateway147 storage147 network147", 28),
        ["session147 library147", "service147 gateway147", "storage147 network147"],
    ),
    (
        ("library147 service147 gateway147 storage147 network147 latency147", 6),
        ["library147", "service147", "gateway147", "storage147", "network147", "latency147"],
    ),
    (
        ("library147 service147 gateway147 storage147 network147 latency147", 10),
        ["library147", "service147", "gateway147", "storage147", "network147", "latency147"],
    ),
    (
        ("library147 service147 gateway147 storage147 network147 latency147", 18),
        ["library147", "service147", "gateway147", "storage147", "network147", "latency147"],
    ),
    (
        ("library147 service147 gateway147 storage147 network147 latency147", 28),
        ["library147 service147", "gateway147 storage147", "network147 latency147"],
    ),
    (
        ("service147 gateway147 storage147 network147 latency147 buffer147", 6),
        ["service147", "gateway147", "storage147", "network147", "latency147", "buffer147"],
    ),
    (
        ("service147 gateway147 storage147 network147 latency147 buffer147", 10),
        ["service147", "gateway147", "storage147", "network147", "latency147", "buffer147"],
    ),
    (
        ("service147 gateway147 storage147 network147 latency147 buffer147", 18),
        ["service147", "gateway147", "storage147", "network147", "latency147", "buffer147"],
    ),
    (
        ("service147 gateway147 storage147 network147 latency147 buffer147", 28),
        ["service147 gateway147", "storage147 network147", "latency147 buffer147"],
    ),
    (
        ("gateway147 storage147 network147 latency147 buffer147 queue147", 6),
        ["gateway147", "storage147", "network147", "latency147", "buffer147", "queue147"],
    ),
    (
        ("gateway147 storage147 network147 latency147 buffer147 queue147", 10),
        ["gateway147", "storage147", "network147", "latency147", "buffer147", "queue147"],
    ),
    (
        ("gateway147 storage147 network147 latency147 buffer147 queue147", 18),
        ["gateway147", "storage147", "network147", "latency147", "buffer147 queue147"],
    ),
    (
        ("gateway147 storage147 network147 latency147 buffer147 queue147", 28),
        ["gateway147 storage147", "network147 latency147", "buffer147 queue147"],
    ),
    (
        ("storage147 network147 latency147 buffer147 queue147 worker147", 6),
        ["storage147", "network147", "latency147", "buffer147", "queue147", "worker147"],
    ),
    (
        ("storage147 network147 latency147 buffer147 queue147 worker147", 10),
        ["storage147", "network147", "latency147", "buffer147", "queue147", "worker147"],
    ),
    (
        ("storage147 network147 latency147 buffer147 queue147 worker147", 18),
        ["storage147", "network147", "latency147", "buffer147 queue147", "worker147"],
    ),
    (
        ("storage147 network147 latency147 buffer147 queue147 worker147", 28),
        ["storage147 network147", "latency147 buffer147", "queue147 worker147"],
    ),
    (
        ("network147 latency147 buffer147 queue147 worker147 kernel147", 6),
        ["network147", "latency147", "buffer147", "queue147", "worker147", "kernel147"],
    ),
    (
        ("network147 latency147 buffer147 queue147 worker147 kernel147", 10),
        ["network147", "latency147", "buffer147", "queue147", "worker147", "kernel147"],
    ),
    (
        ("network147 latency147 buffer147 queue147 worker147 kernel147", 18),
        ["network147", "latency147", "buffer147 queue147", "worker147", "kernel147"],
    ),
    (
        ("network147 latency147 buffer147 queue147 worker147 kernel147", 28),
        ["network147 latency147", "buffer147 queue147 worker147", "kernel147"],
    ),
    (
        ("latency147 buffer147 queue147 worker147 kernel147 signal147", 6),
        ["latency147", "buffer147", "queue147", "worker147", "kernel147", "signal147"],
    ),
    (
        ("latency147 buffer147 queue147 worker147 kernel147 signal147", 10),
        ["latency147", "buffer147", "queue147", "worker147", "kernel147", "signal147"],
    ),
    (
        ("latency147 buffer147 queue147 worker147 kernel147 signal147", 18),
        ["latency147", "buffer147 queue147", "worker147", "kernel147", "signal147"],
    ),
    (
        ("latency147 buffer147 queue147 worker147 kernel147 signal147", 28),
        ["latency147 buffer147", "queue147 worker147 kernel147", "signal147"],
    ),
    (
        ("buffer147 queue147 worker147 kernel147 signal147 packet147", 6),
        ["buffer147", "queue147", "worker147", "kernel147", "signal147", "packet147"],
    ),
    (
        ("buffer147 queue147 worker147 kernel147 signal147 packet147", 10),
        ["buffer147", "queue147", "worker147", "kernel147", "signal147", "packet147"],
    ),
    (
        ("buffer147 queue147 worker147 kernel147 signal147 packet147", 18),
        ["buffer147 queue147", "worker147", "kernel147", "signal147", "packet147"],
    ),
    (
        ("buffer147 queue147 worker147 kernel147 signal147 packet147", 28),
        ["buffer147 queue147 worker147", "kernel147 signal147", "packet147"],
    ),
    (
        ("queue147 worker147 kernel147 signal147 packet147 router147", 6),
        ["queue147", "worker147", "kernel147", "signal147", "packet147", "router147"],
    ),
    (
        ("queue147 worker147 kernel147 signal147 packet147 router147", 10),
        ["queue147", "worker147", "kernel147", "signal147", "packet147", "router147"],
    ),
    (
        ("queue147 worker147 kernel147 signal147 packet147 router147", 18),
        ["queue147 worker147", "kernel147", "signal147", "packet147", "router147"],
    ),
    (
        ("queue147 worker147 kernel147 signal147 packet147 router147", 28),
        ["queue147 worker147 kernel147", "signal147 packet147", "router147"],
    ),
    (
        ("worker147 kernel147 signal147 packet147 router147 cluster147", 6),
        ["worker147", "kernel147", "signal147", "packet147", "router147", "cluster147"],
    ),
    (
        ("worker147 kernel147 signal147 packet147 router147 cluster147", 10),
        ["worker147", "kernel147", "signal147", "packet147", "router147", "cluster147"],
    ),
    (
        ("worker147 kernel147 signal147 packet147 router147 cluster147", 18),
        ["worker147", "kernel147", "signal147", "packet147", "router147", "cluster147"],
    ),
    (
        ("worker147 kernel147 signal147 packet147 router147 cluster147", 28),
        ["worker147 kernel147", "signal147 packet147", "router147 cluster147"],
    ),
    (
        ("kernel147 signal147 packet147 router147 cluster147 mirror147", 6),
        ["kernel147", "signal147", "packet147", "router147", "cluster147", "mirror147"],
    ),
    (
        ("kernel147 signal147 packet147 router147 cluster147 mirror147", 10),
        ["kernel147", "signal147", "packet147", "router147", "cluster147", "mirror147"],
    ),
    (
        ("kernel147 signal147 packet147 router147 cluster147 mirror147", 18),
        ["kernel147", "signal147", "packet147", "router147", "cluster147", "mirror147"],
    ),
    (
        ("kernel147 signal147 packet147 router147 cluster147 mirror147", 28),
        ["kernel147 signal147", "packet147 router147", "cluster147 mirror147"],
    ),
    (
        ("signal147 packet147 router147 cluster147 mirror147 filter147", 6),
        ["signal147", "packet147", "router147", "cluster147", "mirror147", "filter147"],
    ),
    (
        ("signal147 packet147 router147 cluster147 mirror147 filter147", 10),
        ["signal147", "packet147", "router147", "cluster147", "mirror147", "filter147"],
    ),
    (
        ("signal147 packet147 router147 cluster147 mirror147 filter147", 18),
        ["signal147", "packet147", "router147", "cluster147", "mirror147", "filter147"],
    ),
    (
        ("signal147 packet147 router147 cluster147 mirror147 filter147", 28),
        ["signal147 packet147", "router147 cluster147", "mirror147 filter147"],
    ),
    (
        ("packet147 router147 cluster147 mirror147 filter147 ranking147", 6),
        ["packet147", "router147", "cluster147", "mirror147", "filter147", "ranking147"],
    ),
    (
        ("packet147 router147 cluster147 mirror147 filter147 ranking147", 10),
        ["packet147", "router147", "cluster147", "mirror147", "filter147", "ranking147"],
    ),
    (
        ("packet147 router147 cluster147 mirror147 filter147 ranking147", 18),
        ["packet147", "router147", "cluster147", "mirror147", "filter147", "ranking147"],
    ),
    (
        ("packet147 router147 cluster147 mirror147 filter147 ranking147", 28),
        ["packet147 router147", "cluster147 mirror147", "filter147 ranking147"],
    ),
    (
        ("router147 cluster147 mirror147 filter147 ranking147 encoding147", 6),
        ["router147", "cluster147", "mirror147", "filter147", "ranking147", "encoding147"],
    ),
    (
        ("router147 cluster147 mirror147 filter147 ranking147 encoding147", 10),
        ["router147", "cluster147", "mirror147", "filter147", "ranking147", "encoding147"],
    ),
    (
        ("router147 cluster147 mirror147 filter147 ranking147 encoding147", 18),
        ["router147", "cluster147", "mirror147", "filter147", "ranking147", "encoding147"],
    ),
    (
        ("router147 cluster147 mirror147 filter147 ranking147 encoding147", 28),
        ["router147 cluster147", "mirror147 filter147", "ranking147 encoding147"],
    ),
    (
        ("cluster147 mirror147 filter147 ranking147 encoding147 mapping147", 6),
        ["cluster147", "mirror147", "filter147", "ranking147", "encoding147", "mapping147"],
    ),
    (
        ("cluster147 mirror147 filter147 ranking147 encoding147 mapping147", 10),
        ["cluster147", "mirror147", "filter147", "ranking147", "encoding147", "mapping147"],
    ),
    (
        ("cluster147 mirror147 filter147 ranking147 encoding147 mapping147", 18),
        ["cluster147", "mirror147", "filter147", "ranking147", "encoding147", "mapping147"],
    ),
    (
        ("cluster147 mirror147 filter147 ranking147 encoding147 mapping147", 28),
        ["cluster147 mirror147", "filter147 ranking147", "encoding147 mapping147"],
    ),
    (
        ("mirror147 filter147 ranking147 encoding147 mapping147 record147", 6),
        ["mirror147", "filter147", "ranking147", "encoding147", "mapping147", "record147"],
    ),
    (
        ("mirror147 filter147 ranking147 encoding147 mapping147 record147", 10),
        ["mirror147", "filter147", "ranking147", "encoding147", "mapping147", "record147"],
    ),
    (
        ("mirror147 filter147 ranking147 encoding147 mapping147 record147", 18),
        ["mirror147", "filter147", "ranking147", "encoding147", "mapping147", "record147"],
    ),
    (
        ("mirror147 filter147 ranking147 encoding147 mapping147 record147", 28),
        ["mirror147 filter147", "ranking147 encoding147", "mapping147 record147"],
    ),
    (
        ("filter147 ranking147 encoding147 mapping147 record147 candle147", 6),
        ["filter147", "ranking147", "encoding147", "mapping147", "record147", "candle147"],
    ),
    (
        ("filter147 ranking147 encoding147 mapping147 record147 candle147", 10),
        ["filter147", "ranking147", "encoding147", "mapping147", "record147", "candle147"],
    ),
    (
        ("filter147 ranking147 encoding147 mapping147 record147 candle147", 18),
        ["filter147", "ranking147", "encoding147", "mapping147", "record147", "candle147"],
    ),
    (
        ("filter147 ranking147 encoding147 mapping147 record147 candle147", 28),
        ["filter147 ranking147", "encoding147 mapping147", "record147 candle147"],
    ),
    (
        ("ranking147 encoding147 mapping147 record147 candle147 thread147", 6),
        ["ranking147", "encoding147", "mapping147", "record147", "candle147", "thread147"],
    ),
    (
        ("ranking147 encoding147 mapping147 record147 candle147 thread147", 10),
        ["ranking147", "encoding147", "mapping147", "record147", "candle147", "thread147"],
    ),
    (
        ("ranking147 encoding147 mapping147 record147 candle147 thread147", 18),
        ["ranking147", "encoding147", "mapping147", "record147", "candle147", "thread147"],
    ),
    (
        ("ranking147 encoding147 mapping147 record147 candle147 thread147", 28),
        ["ranking147 encoding147", "mapping147 record147", "candle147 thread147"],
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
