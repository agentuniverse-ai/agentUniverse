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
        ("round 66: the quick brown fox jumps over the lazy dog", 4),
        ["round", "66:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 66: the quick brown fox jumps over the lazy dog", 8),
        ["round", "66: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 66: the quick brown fox jumps over the lazy dog", 12),
        ["round 66:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 66: the quick brown fox jumps over the lazy dog", 16),
        ["round 66: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 66: the quick brown fox jumps over the lazy dog", 24),
        ["round 66: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 66: the quick brown fox jumps over the lazy dog", 32),
        ["round 66: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 66: agentuniverse is a framework for multi agents", 4),
        ["round", "66:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 66: agentuniverse is a framework for multi agents", 8),
        ["round", "66:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 66: agentuniverse is a framework for multi agents", 12),
        ["round 66:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 66: agentuniverse is a framework for multi agents", 16),
        ["round 66:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 66: agentuniverse is a framework for multi agents", 24),
        ["round 66: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 66: agentuniverse is a framework for multi agents", 32),
        ["round 66: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 66: knowledge stored as vectors enables retrieval", 4),
        ["round", "66:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 66: knowledge stored as vectors enables retrieval", 8),
        ["round", "66:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 66: knowledge stored as vectors enables retrieval", 12),
        ["round 66:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 66: knowledge stored as vectors enables retrieval", 16),
        ["round 66:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 66: knowledge stored as vectors enables retrieval", 24),
        ["round 66: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 66: knowledge stored as vectors enables retrieval", 32),
        ["round 66: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 66: the processor reads the record then stops", 4),
        ["round", "66:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 66: the processor reads the record then stops", 8),
        ["round", "66: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 66: the processor reads the record then stops", 12),
        ["round 66:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 66: the processor reads the record then stops", 16),
        ["round 66: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 66: the processor reads the record then stops", 24),
        ["round 66: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 66: the processor reads the record then stops", 32),
        ["round 66: the processor reads", "the record then stops"],
    ),
    (
        ("round 66: a worker pulls the next task from the queue", 4),
        ["round", "66:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 66: a worker pulls the next task from the queue", 8),
        ["round", "66: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 66: a worker pulls the next task from the queue", 12),
        ["round 66: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 66: a worker pulls the next task from the queue", 16),
        ["round 66: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 66: a worker pulls the next task from the queue", 24),
        ["round 66: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 66: a worker pulls the next task from the queue", 32),
        ["round 66: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 66: signals travel through the network layer", 4),
        ["round", "66:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 66: signals travel through the network layer", 8),
        ["round", "66:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 66: signals travel through the network layer", 12),
        ["round 66:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 66: signals travel through the network layer", 16),
        ["round 66:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 66: signals travel through the network layer", 24),
        ["round 66: signals travel", "through the network", "layer"],
    ),
    (
        ("round 66: signals travel through the network layer", 32),
        ["round 66: signals travel through", "the network layer"],
    ),
    (
        ("round 66: the gateway routes each request by policy", 4),
        ["round", "66:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 66: the gateway routes each request by policy", 8),
        ["round", "66: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 66: the gateway routes each request by policy", 12),
        ["round 66:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 66: the gateway routes each request by policy", 16),
        ["round 66: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 66: the gateway routes each request by policy", 24),
        ["round 66: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 66: the gateway routes each request by policy", 32),
        ["round 66: the gateway routes", "each request by policy"],
    ),
    (
        ("round 66: memory grows until the buffer is full", 4),
        ["round", "66:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 66: memory grows until the buffer is full", 8),
        ["round", "66:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 66: memory grows until the buffer is full", 12),
        ["round 66:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 66: memory grows until the buffer is full", 16),
        ["round 66: memory", "grows until the", "buffer is full"],
    ),
    (("round 66: memory grows until the buffer is full", 24), ["round 66: memory grows", "until the buffer is full"]),
    (("round 66: memory grows until the buffer is full", 32), ["round 66: memory grows until the", "buffer is full"]),
    (
        ("round 66: the cluster mirrors every packet twice", 4),
        ["round", "66:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 66: the cluster mirrors every packet twice", 8),
        ["round", "66: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 66: the cluster mirrors every packet twice", 12),
        ["round 66:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 66: the cluster mirrors every packet twice", 16),
        ["round 66: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 66: the cluster mirrors every packet twice", 24),
        ["round 66: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 66: the cluster mirrors every packet twice", 32), ["round 66: the cluster mirrors", "every packet twice"]),
    (
        ("round 66: ranking uses tokens learned from the corpus", 4),
        ["round", "66:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 66: ranking uses tokens learned from the corpus", 8),
        ["round", "66:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 66: ranking uses tokens learned from the corpus", 12),
        ["round 66:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 66: ranking uses tokens learned from the corpus", 16),
        ["round 66:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 66: ranking uses tokens learned from the corpus", 24),
        ["round 66: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 66: ranking uses tokens learned from the corpus", 32),
        ["round 66: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 66: a long session ends when the candle dies", 4),
        ["round", "66:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 66: a long session ends when the candle dies", 8),
        ["round", "66: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 66: a long session ends when the candle dies", 12),
        ["round 66: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 66: a long session ends when the candle dies", 16),
        ["round 66: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 66: a long session ends when the candle dies", 24),
        ["round 66: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 66: a long session ends when the candle dies", 32),
        ["round 66: a long session ends", "when the candle dies"],
    ),
    (
        ("round 66: encode the prompt then map the result", 4),
        ["round", "66:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 66: encode the prompt then map the result", 8),
        ["round", "66:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 66: encode the prompt then map the result", 12),
        ["round 66:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 66: encode the prompt then map the result", 16),
        ["round 66: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 66: encode the prompt then map the result", 24),
        ["round 66: encode the", "prompt then map the", "result"],
    ),
    (("round 66: encode the prompt then map the result", 32), ["round 66: encode the prompt then", "map the result"]),
    (
        ("round 66: the kernel wakes the worker at dawn", 4),
        ["round", "66:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 66: the kernel wakes the worker at dawn", 8),
        ["round", "66: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 66: the kernel wakes the worker at dawn", 12),
        ["round 66:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 66: the kernel wakes the worker at dawn", 16), ["round 66: the", "kernel wakes the", "worker at dawn"]),
    (("round 66: the kernel wakes the worker at dawn", 24), ["round 66: the kernel", "wakes the worker at dawn"]),
    (("round 66: the kernel wakes the worker at dawn", 32), ["round 66: the kernel wakes the", "worker at dawn"]),
    (
        ("round 66: service latency drops after the patch", 4),
        ["round", "66:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 66: service latency drops after the patch", 8),
        ["round", "66:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 66: service latency drops after the patch", 12),
        ["round 66:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 66: service latency drops after the patch", 16),
        ["round 66:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 66: service latency drops after the patch", 24),
        ["round 66: service", "latency drops after the", "patch"],
    ),
    (("round 66: service latency drops after the patch", 32), ["round 66: service latency drops", "after the patch"]),
    (
        ("round 66: the library caches every vector it sees", 4),
        ["round", "66:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 66: the library caches every vector it sees", 8),
        ["round", "66: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 66: the library caches every vector it sees", 12),
        ["round 66:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 66: the library caches every vector it sees", 16),
        ["round 66: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 66: the library caches every vector it sees", 24),
        ["round 66: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 66: the library caches every vector it sees", 32),
        ["round 66: the library caches", "every vector it sees"],
    ),
    (
        ("round 66: agents argue then the debate resolves", 4),
        ["round", "66:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 66: agents argue then the debate resolves", 8),
        ["round", "66:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 66: agents argue then the debate resolves", 12),
        ["round 66:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 66: agents argue then the debate resolves", 16),
        ["round 66: agents", "argue then the", "debate resolves"],
    ),
    (("round 66: agents argue then the debate resolves", 24), ["round 66: agents argue", "then the debate resolves"]),
    (("round 66: agents argue then the debate resolves", 32), ["round 66: agents argue then the", "debate resolves"]),
    (
        ("round 66: the filter keeps only strong matches", 4),
        ["round", "66:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 66: the filter keeps only strong matches", 8),
        ["round", "66: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 66: the filter keeps only strong matches", 12),
        ["round 66:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 66: the filter keeps only strong matches", 16),
        ["round 66: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 66: the filter keeps only strong matches", 24), ["round 66: the filter", "keeps only strong", "matches"]),
    (("round 66: the filter keeps only strong matches", 32), ["round 66: the filter keeps only", "strong matches"]),
    (
        ("round 66: the model answers with a short reply", 4),
        ["round", "66:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 66: the model answers with a short reply", 8),
        ["round", "66: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 66: the model answers with a short reply", 12),
        ["round 66:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 66: the model answers with a short reply", 16),
        ["round 66: the", "model answers", "with a short", "reply"],
    ),
    (("round 66: the model answers with a short reply", 24), ["round 66: the model", "answers with a short", "reply"]),
    (("round 66: the model answers with a short reply", 32), ["round 66: the model answers with", "a short reply"]),
    (
        ("round 66: the recorder stores the reasoning trace", 4),
        ["round", "66:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 66: the recorder stores the reasoning trace", 8),
        ["round", "66: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 66: the recorder stores the reasoning trace", 12),
        ["round 66:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 66: the recorder stores the reasoning trace", 16),
        ["round 66: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 66: the recorder stores the reasoning trace", 24),
        ["round 66: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 66: the recorder stores the reasoning trace", 32),
        ["round 66: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 66: the angel watches the processor run", 4),
        ["round", "66:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 66: the angel watches the processor run", 8),
        ["round", "66: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 66: the angel watches the processor run", 12),
        ["round 66:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 66: the angel watches the processor run", 16), ["round 66: the", "angel watches", "the processor", "run"]),
    (("round 66: the angel watches the processor run", 24), ["round 66: the angel", "watches the processor", "run"]),
    (("round 66: the angel watches the processor run", 32), ["round 66: the angel watches the", "processor run"]),
    (
        ("round 66: angle of the vector decides the match", 4),
        ["round", "66:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 66: angle of the vector decides the match", 8),
        ["round", "66:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 66: angle of the vector decides the match", 12),
        ["round 66:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 66: angle of the vector decides the match", 16),
        ["round 66: angle", "of the vector", "decides the", "match"],
    ),
    (("round 66: angle of the vector decides the match", 24), ["round 66: angle of the", "vector decides the match"]),
    (("round 66: angle of the vector decides the match", 32), ["round 66: angle of the vector", "decides the match"]),
    (
        ("round 66: the candle burns twice as long at night", 4),
        ["round", "66:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 66: the candle burns twice as long at night", 8),
        ["round", "66: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 66: the candle burns twice as long at night", 12),
        ["round 66:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 66: the candle burns twice as long at night", 16),
        ["round 66: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 66: the candle burns twice as long at night", 24),
        ["round 66: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 66: the candle burns twice as long at night", 32),
        ["round 66: the candle burns twice", "as long at night"],
    ),
    (
        ("round 66: a mirror of the universe in one line", 4),
        ["round", "66:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 66: a mirror of the universe in one line", 8),
        ["round", "66: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 66: a mirror of the universe in one line", 12),
        ["round 66: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 66: a mirror of the universe in one line", 16),
        ["round 66: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 66: a mirror of the universe in one line", 24), ["round 66: a mirror of", "the universe in one line"]),
    (("round 66: a mirror of the universe in one line", 32), ["round 66: a mirror of the", "universe in one line"]),
    (
        ("round 66: the queue drains before the storm", 4),
        ["round", "66:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 66: the queue drains before the storm", 8),
        ["round", "66: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 66: the queue drains before the storm", 12), ["round 66:", "the queue", "drains", "before the", "storm"]),
    (("round 66: the queue drains before the storm", 16), ["round 66: the", "queue drains", "before the storm"]),
    (("round 66: the queue drains before the storm", 24), ["round 66: the queue", "drains before the storm"]),
    (("round 66: the queue drains before the storm", 32), ["round 66: the queue drains", "before the storm"]),
    (
        ("kitten66 sitting66 agent66 angle66 universe66 memory66", 6),
        ["kitten66", "sitting66", "agent66", "angle66", "universe66", "memory66"],
    ),
    (
        ("kitten66 sitting66 agent66 angle66 universe66 memory66", 10),
        ["kitten66", "sitting66", "agent66", "angle66", "universe66", "memory66"],
    ),
    (
        ("kitten66 sitting66 agent66 angle66 universe66 memory66", 18),
        ["kitten66 sitting66", "agent66 angle66", "universe66", "memory66"],
    ),
    (
        ("kitten66 sitting66 agent66 angle66 universe66 memory66", 28),
        ["kitten66 sitting66 agent66", "angle66 universe66 memory66"],
    ),
    (
        ("sitting66 agent66 angle66 universe66 memory66 stream66", 6),
        ["sitting66", "agent66", "angle66", "universe66", "memory66", "stream66"],
    ),
    (
        ("sitting66 agent66 angle66 universe66 memory66 stream66", 10),
        ["sitting66", "agent66", "angle66", "universe66", "memory66", "stream66"],
    ),
    (
        ("sitting66 agent66 angle66 universe66 memory66 stream66", 18),
        ["sitting66 agent66", "angle66 universe66", "memory66 stream66"],
    ),
    (
        ("sitting66 agent66 angle66 universe66 memory66 stream66", 28),
        ["sitting66 agent66 angle66", "universe66 memory66 stream66"],
    ),
    (
        ("agent66 angle66 universe66 memory66 stream66 context66", 6),
        ["agent66", "angle66", "universe66", "memory66", "stream66", "context66"],
    ),
    (
        ("agent66 angle66 universe66 memory66 stream66 context66", 10),
        ["agent66", "angle66", "universe66", "memory66", "stream66", "context66"],
    ),
    (
        ("agent66 angle66 universe66 memory66 stream66 context66", 18),
        ["agent66 angle66", "universe66", "memory66 stream66", "context66"],
    ),
    (
        ("agent66 angle66 universe66 memory66 stream66 context66", 28),
        ["agent66 angle66 universe66", "memory66 stream66 context66"],
    ),
    (
        ("angle66 universe66 memory66 stream66 context66 knowledge66", 6),
        ["angle66", "universe66", "memory66", "stream66", "context66", "knowledge66"],
    ),
    (
        ("angle66 universe66 memory66 stream66 context66 knowledge66", 10),
        ["angle66", "universe66", "memory66", "stream66", "context66", "knowledge66"],
    ),
    (
        ("angle66 universe66 memory66 stream66 context66 knowledge66", 18),
        ["angle66 universe66", "memory66 stream66", "context66", "knowledge66"],
    ),
    (
        ("angle66 universe66 memory66 stream66 context66 knowledge66", 28),
        ["angle66 universe66 memory66", "stream66 context66", "knowledge66"],
    ),
    (
        ("universe66 memory66 stream66 context66 knowledge66 vector66", 6),
        ["universe66", "memory66", "stream66", "context66", "knowledge66", "vector66"],
    ),
    (
        ("universe66 memory66 stream66 context66 knowledge66 vector66", 10),
        ["universe66", "memory66", "stream66", "context66", "knowledge66", "vector66"],
    ),
    (
        ("universe66 memory66 stream66 context66 knowledge66 vector66", 18),
        ["universe66", "memory66 stream66", "context66", "knowledge66", "vector66"],
    ),
    (
        ("universe66 memory66 stream66 context66 knowledge66 vector66", 28),
        ["universe66 memory66 stream66", "context66 knowledge66", "vector66"],
    ),
    (
        ("memory66 stream66 context66 knowledge66 vector66 processor66", 6),
        ["memory66", "stream66", "context66", "knowledge66", "vector66", "processor66"],
    ),
    (
        ("memory66 stream66 context66 knowledge66 vector66 processor66", 10),
        ["memory66", "stream66", "context66", "knowledge66", "vector66", "processor66"],
    ),
    (
        ("memory66 stream66 context66 knowledge66 vector66 processor66", 18),
        ["memory66 stream66", "context66", "knowledge66", "vector66", "processor66"],
    ),
    (
        ("memory66 stream66 context66 knowledge66 vector66 processor66", 28),
        ["memory66 stream66 context66", "knowledge66 vector66", "processor66"],
    ),
    (
        ("stream66 context66 knowledge66 vector66 processor66 reasoning66", 6),
        ["stream66", "context66", "knowledge66", "vector66", "processor66", "reasoning66"],
    ),
    (
        ("stream66 context66 knowledge66 vector66 processor66 reasoning66", 10),
        ["stream66", "context66", "knowledge66", "vector66", "processor66", "reasoning66"],
    ),
    (
        ("stream66 context66 knowledge66 vector66 processor66 reasoning66", 18),
        ["stream66 context66", "knowledge66", "vector66", "processor66", "reasoning66"],
    ),
    (
        ("stream66 context66 knowledge66 vector66 processor66 reasoning66", 28),
        ["stream66 context66", "knowledge66 vector66", "processor66 reasoning66"],
    ),
    (
        ("context66 knowledge66 vector66 processor66 reasoning66 machine66", 6),
        ["context66", "knowledge66", "vector66", "processor66", "reasoning66", "machine66"],
    ),
    (
        ("context66 knowledge66 vector66 processor66 reasoning66 machine66", 10),
        ["context66", "knowledge66", "vector66", "processor66", "reasoning66", "machine66"],
    ),
    (
        ("context66 knowledge66 vector66 processor66 reasoning66 machine66", 18),
        ["context66", "knowledge66", "vector66", "processor66", "reasoning66", "machine66"],
    ),
    (
        ("context66 knowledge66 vector66 processor66 reasoning66 machine66", 28),
        ["context66 knowledge66", "vector66 processor66", "reasoning66 machine66"],
    ),
    (
        ("knowledge66 vector66 processor66 reasoning66 machine66 learning66", 6),
        ["knowledge66", "vector66", "processor66", "reasoning66", "machine66", "learning66"],
    ),
    (
        ("knowledge66 vector66 processor66 reasoning66 machine66 learning66", 10),
        ["knowledge66", "vector66", "processor66", "reasoning66", "machine66", "learning66"],
    ),
    (
        ("knowledge66 vector66 processor66 reasoning66 machine66 learning66", 18),
        ["knowledge66", "vector66", "processor66", "reasoning66", "machine66", "learning66"],
    ),
    (
        ("knowledge66 vector66 processor66 reasoning66 machine66 learning66", 28),
        ["knowledge66 vector66", "processor66 reasoning66", "machine66 learning66"],
    ),
    (
        ("vector66 processor66 reasoning66 machine66 learning66 model66", 6),
        ["vector66", "processor66", "reasoning66", "machine66", "learning66", "model66"],
    ),
    (
        ("vector66 processor66 reasoning66 machine66 learning66 model66", 10),
        ["vector66", "processor66", "reasoning66", "machine66", "learning66", "model66"],
    ),
    (
        ("vector66 processor66 reasoning66 machine66 learning66 model66", 18),
        ["vector66", "processor66", "reasoning66", "machine66", "learning66 model66"],
    ),
    (
        ("vector66 processor66 reasoning66 machine66 learning66 model66", 28),
        ["vector66 processor66", "reasoning66 machine66", "learning66 model66"],
    ),
    (
        ("processor66 reasoning66 machine66 learning66 model66 token66", 6),
        ["processor66", "reasoning66", "machine66", "learning66", "model66", "token66"],
    ),
    (
        ("processor66 reasoning66 machine66 learning66 model66 token66", 10),
        ["processor66", "reasoning66", "machine66", "learning66", "model66", "token66"],
    ),
    (
        ("processor66 reasoning66 machine66 learning66 model66 token66", 18),
        ["processor66", "reasoning66", "machine66", "learning66 model66", "token66"],
    ),
    (
        ("processor66 reasoning66 machine66 learning66 model66 token66", 28),
        ["processor66 reasoning66", "machine66 learning66 model66", "token66"],
    ),
    (
        ("reasoning66 machine66 learning66 model66 token66 prompt66", 6),
        ["reasoning66", "machine66", "learning66", "model66", "token66", "prompt66"],
    ),
    (
        ("reasoning66 machine66 learning66 model66 token66 prompt66", 10),
        ["reasoning66", "machine66", "learning66", "model66", "token66", "prompt66"],
    ),
    (
        ("reasoning66 machine66 learning66 model66 token66 prompt66", 18),
        ["reasoning66", "machine66", "learning66 model66", "token66 prompt66"],
    ),
    (
        ("reasoning66 machine66 learning66 model66 token66 prompt66", 28),
        ["reasoning66 machine66", "learning66 model66 token66", "prompt66"],
    ),
    (
        ("machine66 learning66 model66 token66 prompt66 session66", 6),
        ["machine66", "learning66", "model66", "token66", "prompt66", "session66"],
    ),
    (
        ("machine66 learning66 model66 token66 prompt66 session66", 10),
        ["machine66", "learning66", "model66", "token66", "prompt66", "session66"],
    ),
    (
        ("machine66 learning66 model66 token66 prompt66 session66", 18),
        ["machine66", "learning66 model66", "token66 prompt66", "session66"],
    ),
    (
        ("machine66 learning66 model66 token66 prompt66 session66", 28),
        ["machine66 learning66 model66", "token66 prompt66 session66"],
    ),
    (
        ("learning66 model66 token66 prompt66 session66 library66", 6),
        ["learning66", "model66", "token66", "prompt66", "session66", "library66"],
    ),
    (
        ("learning66 model66 token66 prompt66 session66 library66", 10),
        ["learning66", "model66", "token66", "prompt66", "session66", "library66"],
    ),
    (
        ("learning66 model66 token66 prompt66 session66 library66", 18),
        ["learning66 model66", "token66 prompt66", "session66", "library66"],
    ),
    (
        ("learning66 model66 token66 prompt66 session66 library66", 28),
        ["learning66 model66 token66", "prompt66 session66 library66"],
    ),
    (
        ("model66 token66 prompt66 session66 library66 service66", 6),
        ["model66", "token66", "prompt66", "session66", "library66", "service66"],
    ),
    (
        ("model66 token66 prompt66 session66 library66 service66", 10),
        ["model66", "token66", "prompt66", "session66", "library66", "service66"],
    ),
    (
        ("model66 token66 prompt66 session66 library66 service66", 18),
        ["model66 token66", "prompt66 session66", "library66", "service66"],
    ),
    (
        ("model66 token66 prompt66 session66 library66 service66", 28),
        ["model66 token66 prompt66", "session66 library66", "service66"],
    ),
    (
        ("token66 prompt66 session66 library66 service66 gateway66", 6),
        ["token66", "prompt66", "session66", "library66", "service66", "gateway66"],
    ),
    (
        ("token66 prompt66 session66 library66 service66 gateway66", 10),
        ["token66", "prompt66", "session66", "library66", "service66", "gateway66"],
    ),
    (
        ("token66 prompt66 session66 library66 service66 gateway66", 18),
        ["token66 prompt66", "session66", "library66", "service66", "gateway66"],
    ),
    (
        ("token66 prompt66 session66 library66 service66 gateway66", 28),
        ["token66 prompt66 session66", "library66 service66", "gateway66"],
    ),
    (
        ("prompt66 session66 library66 service66 gateway66 storage66", 6),
        ["prompt66", "session66", "library66", "service66", "gateway66", "storage66"],
    ),
    (
        ("prompt66 session66 library66 service66 gateway66 storage66", 10),
        ["prompt66", "session66", "library66", "service66", "gateway66", "storage66"],
    ),
    (
        ("prompt66 session66 library66 service66 gateway66 storage66", 18),
        ["prompt66 session66", "library66", "service66", "gateway66", "storage66"],
    ),
    (
        ("prompt66 session66 library66 service66 gateway66 storage66", 28),
        ["prompt66 session66 library66", "service66 gateway66", "storage66"],
    ),
    (
        ("session66 library66 service66 gateway66 storage66 network66", 6),
        ["session66", "library66", "service66", "gateway66", "storage66", "network66"],
    ),
    (
        ("session66 library66 service66 gateway66 storage66 network66", 10),
        ["session66", "library66", "service66", "gateway66", "storage66", "network66"],
    ),
    (
        ("session66 library66 service66 gateway66 storage66 network66", 18),
        ["session66", "library66", "service66", "gateway66", "storage66", "network66"],
    ),
    (
        ("session66 library66 service66 gateway66 storage66 network66", 28),
        ["session66 library66", "service66 gateway66", "storage66 network66"],
    ),
    (
        ("library66 service66 gateway66 storage66 network66 latency66", 6),
        ["library66", "service66", "gateway66", "storage66", "network66", "latency66"],
    ),
    (
        ("library66 service66 gateway66 storage66 network66 latency66", 10),
        ["library66", "service66", "gateway66", "storage66", "network66", "latency66"],
    ),
    (
        ("library66 service66 gateway66 storage66 network66 latency66", 18),
        ["library66", "service66", "gateway66", "storage66", "network66", "latency66"],
    ),
    (
        ("library66 service66 gateway66 storage66 network66 latency66", 28),
        ["library66 service66", "gateway66 storage66", "network66 latency66"],
    ),
    (
        ("service66 gateway66 storage66 network66 latency66 buffer66", 6),
        ["service66", "gateway66", "storage66", "network66", "latency66", "buffer66"],
    ),
    (
        ("service66 gateway66 storage66 network66 latency66 buffer66", 10),
        ["service66", "gateway66", "storage66", "network66", "latency66", "buffer66"],
    ),
    (
        ("service66 gateway66 storage66 network66 latency66 buffer66", 18),
        ["service66", "gateway66", "storage66", "network66", "latency66 buffer66"],
    ),
    (
        ("service66 gateway66 storage66 network66 latency66 buffer66", 28),
        ["service66 gateway66", "storage66 network66", "latency66 buffer66"],
    ),
    (
        ("gateway66 storage66 network66 latency66 buffer66 queue66", 6),
        ["gateway66", "storage66", "network66", "latency66", "buffer66", "queue66"],
    ),
    (
        ("gateway66 storage66 network66 latency66 buffer66 queue66", 10),
        ["gateway66", "storage66", "network66", "latency66", "buffer66", "queue66"],
    ),
    (
        ("gateway66 storage66 network66 latency66 buffer66 queue66", 18),
        ["gateway66", "storage66", "network66", "latency66 buffer66", "queue66"],
    ),
    (
        ("gateway66 storage66 network66 latency66 buffer66 queue66", 28),
        ["gateway66 storage66", "network66 latency66 buffer66", "queue66"],
    ),
    (
        ("storage66 network66 latency66 buffer66 queue66 worker66", 6),
        ["storage66", "network66", "latency66", "buffer66", "queue66", "worker66"],
    ),
    (
        ("storage66 network66 latency66 buffer66 queue66 worker66", 10),
        ["storage66", "network66", "latency66", "buffer66", "queue66", "worker66"],
    ),
    (
        ("storage66 network66 latency66 buffer66 queue66 worker66", 18),
        ["storage66", "network66", "latency66 buffer66", "queue66 worker66"],
    ),
    (
        ("storage66 network66 latency66 buffer66 queue66 worker66", 28),
        ["storage66 network66", "latency66 buffer66 queue66", "worker66"],
    ),
    (
        ("network66 latency66 buffer66 queue66 worker66 kernel66", 6),
        ["network66", "latency66", "buffer66", "queue66", "worker66", "kernel66"],
    ),
    (
        ("network66 latency66 buffer66 queue66 worker66 kernel66", 10),
        ["network66", "latency66", "buffer66", "queue66", "worker66", "kernel66"],
    ),
    (
        ("network66 latency66 buffer66 queue66 worker66 kernel66", 18),
        ["network66", "latency66 buffer66", "queue66 worker66", "kernel66"],
    ),
    (
        ("network66 latency66 buffer66 queue66 worker66 kernel66", 28),
        ["network66 latency66 buffer66", "queue66 worker66 kernel66"],
    ),
    (
        ("latency66 buffer66 queue66 worker66 kernel66 signal66", 6),
        ["latency66", "buffer66", "queue66", "worker66", "kernel66", "signal66"],
    ),
    (
        ("latency66 buffer66 queue66 worker66 kernel66 signal66", 10),
        ["latency66", "buffer66", "queue66", "worker66", "kernel66", "signal66"],
    ),
    (
        ("latency66 buffer66 queue66 worker66 kernel66 signal66", 18),
        ["latency66 buffer66", "queue66 worker66", "kernel66 signal66"],
    ),
    (
        ("latency66 buffer66 queue66 worker66 kernel66 signal66", 28),
        ["latency66 buffer66 queue66", "worker66 kernel66 signal66"],
    ),
    (
        ("buffer66 queue66 worker66 kernel66 signal66 packet66", 6),
        ["buffer66", "queue66", "worker66", "kernel66", "signal66", "packet66"],
    ),
    (
        ("buffer66 queue66 worker66 kernel66 signal66 packet66", 10),
        ["buffer66", "queue66", "worker66", "kernel66", "signal66", "packet66"],
    ),
    (
        ("buffer66 queue66 worker66 kernel66 signal66 packet66", 18),
        ["buffer66 queue66", "worker66 kernel66", "signal66 packet66"],
    ),
    (
        ("buffer66 queue66 worker66 kernel66 signal66 packet66", 28),
        ["buffer66 queue66 worker66", "kernel66 signal66 packet66"],
    ),
    (
        ("queue66 worker66 kernel66 signal66 packet66 router66", 6),
        ["queue66", "worker66", "kernel66", "signal66", "packet66", "router66"],
    ),
    (
        ("queue66 worker66 kernel66 signal66 packet66 router66", 10),
        ["queue66", "worker66", "kernel66", "signal66", "packet66", "router66"],
    ),
    (
        ("queue66 worker66 kernel66 signal66 packet66 router66", 18),
        ["queue66 worker66", "kernel66 signal66", "packet66 router66"],
    ),
    (
        ("queue66 worker66 kernel66 signal66 packet66 router66", 28),
        ["queue66 worker66 kernel66", "signal66 packet66 router66"],
    ),
    (
        ("worker66 kernel66 signal66 packet66 router66 cluster66", 6),
        ["worker66", "kernel66", "signal66", "packet66", "router66", "cluster66"],
    ),
    (
        ("worker66 kernel66 signal66 packet66 router66 cluster66", 10),
        ["worker66", "kernel66", "signal66", "packet66", "router66", "cluster66"],
    ),
    (
        ("worker66 kernel66 signal66 packet66 router66 cluster66", 18),
        ["worker66 kernel66", "signal66 packet66", "router66 cluster66"],
    ),
    (
        ("worker66 kernel66 signal66 packet66 router66 cluster66", 28),
        ["worker66 kernel66 signal66", "packet66 router66 cluster66"],
    ),
    (
        ("kernel66 signal66 packet66 router66 cluster66 mirror66", 6),
        ["kernel66", "signal66", "packet66", "router66", "cluster66", "mirror66"],
    ),
    (
        ("kernel66 signal66 packet66 router66 cluster66 mirror66", 10),
        ["kernel66", "signal66", "packet66", "router66", "cluster66", "mirror66"],
    ),
    (
        ("kernel66 signal66 packet66 router66 cluster66 mirror66", 18),
        ["kernel66 signal66", "packet66 router66", "cluster66 mirror66"],
    ),
    (
        ("kernel66 signal66 packet66 router66 cluster66 mirror66", 28),
        ["kernel66 signal66 packet66", "router66 cluster66 mirror66"],
    ),
    (
        ("signal66 packet66 router66 cluster66 mirror66 filter66", 6),
        ["signal66", "packet66", "router66", "cluster66", "mirror66", "filter66"],
    ),
    (
        ("signal66 packet66 router66 cluster66 mirror66 filter66", 10),
        ["signal66", "packet66", "router66", "cluster66", "mirror66", "filter66"],
    ),
    (
        ("signal66 packet66 router66 cluster66 mirror66 filter66", 18),
        ["signal66 packet66", "router66 cluster66", "mirror66 filter66"],
    ),
    (
        ("signal66 packet66 router66 cluster66 mirror66 filter66", 28),
        ["signal66 packet66 router66", "cluster66 mirror66 filter66"],
    ),
    (
        ("packet66 router66 cluster66 mirror66 filter66 ranking66", 6),
        ["packet66", "router66", "cluster66", "mirror66", "filter66", "ranking66"],
    ),
    (
        ("packet66 router66 cluster66 mirror66 filter66 ranking66", 10),
        ["packet66", "router66", "cluster66", "mirror66", "filter66", "ranking66"],
    ),
    (
        ("packet66 router66 cluster66 mirror66 filter66 ranking66", 18),
        ["packet66 router66", "cluster66 mirror66", "filter66 ranking66"],
    ),
    (
        ("packet66 router66 cluster66 mirror66 filter66 ranking66", 28),
        ["packet66 router66 cluster66", "mirror66 filter66 ranking66"],
    ),
    (
        ("router66 cluster66 mirror66 filter66 ranking66 encoding66", 6),
        ["router66", "cluster66", "mirror66", "filter66", "ranking66", "encoding66"],
    ),
    (
        ("router66 cluster66 mirror66 filter66 ranking66 encoding66", 10),
        ["router66", "cluster66", "mirror66", "filter66", "ranking66", "encoding66"],
    ),
    (
        ("router66 cluster66 mirror66 filter66 ranking66 encoding66", 18),
        ["router66 cluster66", "mirror66 filter66", "ranking66", "encoding66"],
    ),
    (
        ("router66 cluster66 mirror66 filter66 ranking66 encoding66", 28),
        ["router66 cluster66 mirror66", "filter66 ranking66", "encoding66"],
    ),
    (
        ("cluster66 mirror66 filter66 ranking66 encoding66 mapping66", 6),
        ["cluster66", "mirror66", "filter66", "ranking66", "encoding66", "mapping66"],
    ),
    (
        ("cluster66 mirror66 filter66 ranking66 encoding66 mapping66", 10),
        ["cluster66", "mirror66", "filter66", "ranking66", "encoding66", "mapping66"],
    ),
    (
        ("cluster66 mirror66 filter66 ranking66 encoding66 mapping66", 18),
        ["cluster66 mirror66", "filter66 ranking66", "encoding66", "mapping66"],
    ),
    (
        ("cluster66 mirror66 filter66 ranking66 encoding66 mapping66", 28),
        ["cluster66 mirror66 filter66", "ranking66 encoding66", "mapping66"],
    ),
    (
        ("mirror66 filter66 ranking66 encoding66 mapping66 record66", 6),
        ["mirror66", "filter66", "ranking66", "encoding66", "mapping66", "record66"],
    ),
    (
        ("mirror66 filter66 ranking66 encoding66 mapping66 record66", 10),
        ["mirror66", "filter66", "ranking66", "encoding66", "mapping66", "record66"],
    ),
    (
        ("mirror66 filter66 ranking66 encoding66 mapping66 record66", 18),
        ["mirror66 filter66", "ranking66", "encoding66", "mapping66 record66"],
    ),
    (
        ("mirror66 filter66 ranking66 encoding66 mapping66 record66", 28),
        ["mirror66 filter66 ranking66", "encoding66 mapping66", "record66"],
    ),
    (
        ("filter66 ranking66 encoding66 mapping66 record66 candle66", 6),
        ["filter66", "ranking66", "encoding66", "mapping66", "record66", "candle66"],
    ),
    (
        ("filter66 ranking66 encoding66 mapping66 record66 candle66", 10),
        ["filter66", "ranking66", "encoding66", "mapping66", "record66", "candle66"],
    ),
    (
        ("filter66 ranking66 encoding66 mapping66 record66 candle66", 18),
        ["filter66 ranking66", "encoding66", "mapping66 record66", "candle66"],
    ),
    (
        ("filter66 ranking66 encoding66 mapping66 record66 candle66", 28),
        ["filter66 ranking66", "encoding66 mapping66", "record66 candle66"],
    ),
    (
        ("ranking66 encoding66 mapping66 record66 candle66 thread66", 6),
        ["ranking66", "encoding66", "mapping66", "record66", "candle66", "thread66"],
    ),
    (
        ("ranking66 encoding66 mapping66 record66 candle66 thread66", 10),
        ["ranking66", "encoding66", "mapping66", "record66", "candle66", "thread66"],
    ),
    (
        ("ranking66 encoding66 mapping66 record66 candle66 thread66", 18),
        ["ranking66", "encoding66", "mapping66 record66", "candle66 thread66"],
    ),
    (
        ("ranking66 encoding66 mapping66 record66 candle66 thread66", 28),
        ["ranking66 encoding66", "mapping66 record66 candle66", "thread66"],
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
