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
        ("round 111: the quick brown fox jumps over the lazy dog", 4),
        ["round", "111:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 111: the quick brown fox jumps over the lazy dog", 8),
        ["round", "111: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 111: the quick brown fox jumps over the lazy dog", 12),
        ["round 111:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 111: the quick brown fox jumps over the lazy dog", 16),
        ["round 111: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 111: the quick brown fox jumps over the lazy dog", 24),
        ["round 111: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 111: the quick brown fox jumps over the lazy dog", 32),
        ["round 111: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 111: agentuniverse is a framework for multi agents", 4),
        ["round", "111:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 111: agentuniverse is a framework for multi agents", 8),
        ["round", "111:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 111: agentuniverse is a framework for multi agents", 12),
        ["round 111:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 111: agentuniverse is a framework for multi agents", 16),
        ["round 111:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 111: agentuniverse is a framework for multi agents", 24),
        ["round 111: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 111: agentuniverse is a framework for multi agents", 32),
        ["round 111: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 111: knowledge stored as vectors enables retrieval", 4),
        ["round", "111:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 111: knowledge stored as vectors enables retrieval", 8),
        ["round", "111:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 111: knowledge stored as vectors enables retrieval", 12),
        ["round 111:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 111: knowledge stored as vectors enables retrieval", 16),
        ["round 111:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 111: knowledge stored as vectors enables retrieval", 24),
        ["round 111: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 111: knowledge stored as vectors enables retrieval", 32),
        ["round 111: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 111: the processor reads the record then stops", 4),
        ["round", "111:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 111: the processor reads the record then stops", 8),
        ["round", "111: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 111: the processor reads the record then stops", 12),
        ["round 111:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 111: the processor reads the record then stops", 16),
        ["round 111: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 111: the processor reads the record then stops", 24),
        ["round 111: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 111: the processor reads the record then stops", 32),
        ["round 111: the processor reads", "the record then stops"],
    ),
    (
        ("round 111: a worker pulls the next task from the queue", 4),
        ["round", "111:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 111: a worker pulls the next task from the queue", 8),
        ["round", "111: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 111: a worker pulls the next task from the queue", 12),
        ["round 111: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 111: a worker pulls the next task from the queue", 16),
        ["round 111: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 111: a worker pulls the next task from the queue", 24),
        ["round 111: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 111: a worker pulls the next task from the queue", 32),
        ["round 111: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 111: signals travel through the network layer", 4),
        ["round", "111:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 111: signals travel through the network layer", 8),
        ["round", "111:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 111: signals travel through the network layer", 12),
        ["round 111:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 111: signals travel through the network layer", 16),
        ["round 111:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 111: signals travel through the network layer", 24),
        ["round 111: signals", "travel through the", "network layer"],
    ),
    (
        ("round 111: signals travel through the network layer", 32),
        ["round 111: signals travel", "through the network layer"],
    ),
    (
        ("round 111: the gateway routes each request by policy", 4),
        ["round", "111:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 111: the gateway routes each request by policy", 8),
        ["round", "111: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 111: the gateway routes each request by policy", 12),
        ["round 111:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 111: the gateway routes each request by policy", 16),
        ["round 111: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 111: the gateway routes each request by policy", 24),
        ["round 111: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 111: the gateway routes each request by policy", 32),
        ["round 111: the gateway routes", "each request by policy"],
    ),
    (
        ("round 111: memory grows until the buffer is full", 4),
        ["round", "111:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 111: memory grows until the buffer is full", 8),
        ["round", "111:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 111: memory grows until the buffer is full", 12),
        ["round 111:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 111: memory grows until the buffer is full", 16),
        ["round 111:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 111: memory grows until the buffer is full", 24), ["round 111: memory grows", "until the buffer is full"]),
    (("round 111: memory grows until the buffer is full", 32), ["round 111: memory grows until", "the buffer is full"]),
    (
        ("round 111: the cluster mirrors every packet twice", 4),
        ["round", "111:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 111: the cluster mirrors every packet twice", 8),
        ["round", "111: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 111: the cluster mirrors every packet twice", 12),
        ["round 111:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 111: the cluster mirrors every packet twice", 16),
        ["round 111: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 111: the cluster mirrors every packet twice", 24),
        ["round 111: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 111: the cluster mirrors every packet twice", 32),
        ["round 111: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 111: ranking uses tokens learned from the corpus", 4),
        ["round", "111:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 111: ranking uses tokens learned from the corpus", 8),
        ["round", "111:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 111: ranking uses tokens learned from the corpus", 12),
        ["round 111:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 111: ranking uses tokens learned from the corpus", 16),
        ["round 111:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 111: ranking uses tokens learned from the corpus", 24),
        ["round 111: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 111: ranking uses tokens learned from the corpus", 32),
        ["round 111: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 111: a long session ends when the candle dies", 4),
        ["round", "111:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 111: a long session ends when the candle dies", 8),
        ["round", "111: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 111: a long session ends when the candle dies", 12),
        ["round 111: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 111: a long session ends when the candle dies", 16),
        ["round 111: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 111: a long session ends when the candle dies", 24),
        ["round 111: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 111: a long session ends when the candle dies", 32),
        ["round 111: a long session ends", "when the candle dies"],
    ),
    (
        ("round 111: encode the prompt then map the result", 4),
        ["round", "111:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 111: encode the prompt then map the result", 8),
        ["round", "111:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 111: encode the prompt then map the result", 12),
        ["round 111:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 111: encode the prompt then map the result", 16),
        ["round 111:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 111: encode the prompt then map the result", 24),
        ["round 111: encode the", "prompt then map the", "result"],
    ),
    (("round 111: encode the prompt then map the result", 32), ["round 111: encode the prompt", "then map the result"]),
    (
        ("round 111: the kernel wakes the worker at dawn", 4),
        ["round", "111:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 111: the kernel wakes the worker at dawn", 8),
        ["round", "111: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 111: the kernel wakes the worker at dawn", 12),
        ["round 111:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 111: the kernel wakes the worker at dawn", 16), ["round 111: the", "kernel wakes the", "worker at dawn"]),
    (("round 111: the kernel wakes the worker at dawn", 24), ["round 111: the kernel", "wakes the worker at dawn"]),
    (("round 111: the kernel wakes the worker at dawn", 32), ["round 111: the kernel wakes the", "worker at dawn"]),
    (
        ("round 111: service latency drops after the patch", 4),
        ["round", "111:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 111: service latency drops after the patch", 8),
        ["round", "111:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 111: service latency drops after the patch", 12),
        ["round 111:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 111: service latency drops after the patch", 16),
        ["round 111:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 111: service latency drops after the patch", 24),
        ["round 111: service", "latency drops after the", "patch"],
    ),
    (("round 111: service latency drops after the patch", 32), ["round 111: service latency drops", "after the patch"]),
    (
        ("round 111: the library caches every vector it sees", 4),
        ["round", "111:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 111: the library caches every vector it sees", 8),
        ["round", "111: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 111: the library caches every vector it sees", 12),
        ["round 111:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 111: the library caches every vector it sees", 16),
        ["round 111: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 111: the library caches every vector it sees", 24),
        ["round 111: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 111: the library caches every vector it sees", 32),
        ["round 111: the library caches", "every vector it sees"],
    ),
    (
        ("round 111: agents argue then the debate resolves", 4),
        ["round", "111:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 111: agents argue then the debate resolves", 8),
        ["round", "111:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 111: agents argue then the debate resolves", 12),
        ["round 111:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 111: agents argue then the debate resolves", 16),
        ["round 111:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 111: agents argue then the debate resolves", 24), ["round 111: agents argue", "then the debate resolves"]),
    (("round 111: agents argue then the debate resolves", 32), ["round 111: agents argue then the", "debate resolves"]),
    (
        ("round 111: the filter keeps only strong matches", 4),
        ["round", "111:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 111: the filter keeps only strong matches", 8),
        ["round", "111: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 111: the filter keeps only strong matches", 12),
        ["round 111:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 111: the filter keeps only strong matches", 16),
        ["round 111: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 111: the filter keeps only strong matches", 24),
        ["round 111: the filter", "keeps only strong", "matches"],
    ),
    (("round 111: the filter keeps only strong matches", 32), ["round 111: the filter keeps only", "strong matches"]),
    (
        ("round 111: the model answers with a short reply", 4),
        ["round", "111:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 111: the model answers with a short reply", 8),
        ["round", "111: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 111: the model answers with a short reply", 12),
        ["round 111:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 111: the model answers with a short reply", 16),
        ["round 111: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 111: the model answers with a short reply", 24),
        ["round 111: the model", "answers with a short", "reply"],
    ),
    (("round 111: the model answers with a short reply", 32), ["round 111: the model answers", "with a short reply"]),
    (
        ("round 111: the recorder stores the reasoning trace", 4),
        ["round", "111:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 111: the recorder stores the reasoning trace", 8),
        ["round", "111: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 111: the recorder stores the reasoning trace", 12),
        ["round 111:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 111: the recorder stores the reasoning trace", 16),
        ["round 111: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 111: the recorder stores the reasoning trace", 24),
        ["round 111: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 111: the recorder stores the reasoning trace", 32),
        ["round 111: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 111: the angel watches the processor run", 4),
        ["round", "111:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 111: the angel watches the processor run", 8),
        ["round", "111: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 111: the angel watches the processor run", 12),
        ["round 111:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 111: the angel watches the processor run", 16),
        ["round 111: the", "angel watches", "the processor", "run"],
    ),
    (("round 111: the angel watches the processor run", 24), ["round 111: the angel", "watches the processor", "run"]),
    (("round 111: the angel watches the processor run", 32), ["round 111: the angel watches the", "processor run"]),
    (
        ("round 111: angle of the vector decides the match", 4),
        ["round", "111:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 111: angle of the vector decides the match", 8),
        ["round", "111:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 111: angle of the vector decides the match", 12),
        ["round 111:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 111: angle of the vector decides the match", 16),
        ["round 111: angle", "of the vector", "decides the", "match"],
    ),
    (("round 111: angle of the vector decides the match", 24), ["round 111: angle of the", "vector decides the match"]),
    (("round 111: angle of the vector decides the match", 32), ["round 111: angle of the vector", "decides the match"]),
    (
        ("round 111: the candle burns twice as long at night", 4),
        ["round", "111:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 111: the candle burns twice as long at night", 8),
        ["round", "111: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 111: the candle burns twice as long at night", 12),
        ["round 111:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 111: the candle burns twice as long at night", 16),
        ["round 111: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 111: the candle burns twice as long at night", 24),
        ["round 111: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 111: the candle burns twice as long at night", 32),
        ["round 111: the candle burns", "twice as long at night"],
    ),
    (
        ("round 111: a mirror of the universe in one line", 4),
        ["round", "111:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 111: a mirror of the universe in one line", 8),
        ["round", "111: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 111: a mirror of the universe in one line", 12),
        ["round 111: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 111: a mirror of the universe in one line", 16),
        ["round 111: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 111: a mirror of the universe in one line", 24), ["round 111: a mirror of", "the universe in one line"]),
    (("round 111: a mirror of the universe in one line", 32), ["round 111: a mirror of the", "universe in one line"]),
    (
        ("round 111: the queue drains before the storm", 4),
        ["round", "111:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 111: the queue drains before the storm", 8),
        ["round", "111: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 111: the queue drains before the storm", 12),
        ["round 111:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 111: the queue drains before the storm", 16), ["round 111: the", "queue drains", "before the storm"]),
    (("round 111: the queue drains before the storm", 24), ["round 111: the queue", "drains before the storm"]),
    (("round 111: the queue drains before the storm", 32), ["round 111: the queue drains", "before the storm"]),
    (
        ("kitten111 sitting111 agent111 angle111 universe111 memory111", 6),
        ["kitten111", "sitting111", "agent111", "angle111", "universe111", "memory111"],
    ),
    (
        ("kitten111 sitting111 agent111 angle111 universe111 memory111", 10),
        ["kitten111", "sitting111", "agent111", "angle111", "universe111", "memory111"],
    ),
    (
        ("kitten111 sitting111 agent111 angle111 universe111 memory111", 18),
        ["kitten111", "sitting111", "agent111 angle111", "universe111", "memory111"],
    ),
    (
        ("kitten111 sitting111 agent111 angle111 universe111 memory111", 28),
        ["kitten111 sitting111", "agent111 angle111", "universe111 memory111"],
    ),
    (
        ("sitting111 agent111 angle111 universe111 memory111 stream111", 6),
        ["sitting111", "agent111", "angle111", "universe111", "memory111", "stream111"],
    ),
    (
        ("sitting111 agent111 angle111 universe111 memory111 stream111", 10),
        ["sitting111", "agent111", "angle111", "universe111", "memory111", "stream111"],
    ),
    (
        ("sitting111 agent111 angle111 universe111 memory111 stream111", 18),
        ["sitting111", "agent111 angle111", "universe111", "memory111", "stream111"],
    ),
    (
        ("sitting111 agent111 angle111 universe111 memory111 stream111", 28),
        ["sitting111 agent111 angle111", "universe111 memory111", "stream111"],
    ),
    (
        ("agent111 angle111 universe111 memory111 stream111 context111", 6),
        ["agent111", "angle111", "universe111", "memory111", "stream111", "context111"],
    ),
    (
        ("agent111 angle111 universe111 memory111 stream111 context111", 10),
        ["agent111", "angle111", "universe111", "memory111", "stream111", "context111"],
    ),
    (
        ("agent111 angle111 universe111 memory111 stream111 context111", 18),
        ["agent111 angle111", "universe111", "memory111", "stream111", "context111"],
    ),
    (
        ("agent111 angle111 universe111 memory111 stream111 context111", 28),
        ["agent111 angle111", "universe111 memory111", "stream111 context111"],
    ),
    (
        ("angle111 universe111 memory111 stream111 context111 knowledge111", 6),
        ["angle111", "universe111", "memory111", "stream111", "context111", "knowledge111"],
    ),
    (
        ("angle111 universe111 memory111 stream111 context111 knowledge111", 10),
        ["angle111", "universe111", "memory111", "stream111", "context111", "knowledge111"],
    ),
    (
        ("angle111 universe111 memory111 stream111 context111 knowledge111", 18),
        ["angle111", "universe111", "memory111", "stream111", "context111", "knowledge111"],
    ),
    (
        ("angle111 universe111 memory111 stream111 context111 knowledge111", 28),
        ["angle111 universe111", "memory111 stream111", "context111 knowledge111"],
    ),
    (
        ("universe111 memory111 stream111 context111 knowledge111 vector111", 6),
        ["universe111", "memory111", "stream111", "context111", "knowledge111", "vector111"],
    ),
    (
        ("universe111 memory111 stream111 context111 knowledge111 vector111", 10),
        ["universe111", "memory111", "stream111", "context111", "knowledge111", "vector111"],
    ),
    (
        ("universe111 memory111 stream111 context111 knowledge111 vector111", 18),
        ["universe111", "memory111", "stream111", "context111", "knowledge111", "vector111"],
    ),
    (
        ("universe111 memory111 stream111 context111 knowledge111 vector111", 28),
        ["universe111 memory111", "stream111 context111", "knowledge111 vector111"],
    ),
    (
        ("memory111 stream111 context111 knowledge111 vector111 processor111", 6),
        ["memory111", "stream111", "context111", "knowledge111", "vector111", "processor111"],
    ),
    (
        ("memory111 stream111 context111 knowledge111 vector111 processor111", 10),
        ["memory111", "stream111", "context111", "knowledge111", "vector111", "processor111"],
    ),
    (
        ("memory111 stream111 context111 knowledge111 vector111 processor111", 18),
        ["memory111", "stream111", "context111", "knowledge111", "vector111", "processor111"],
    ),
    (
        ("memory111 stream111 context111 knowledge111 vector111 processor111", 28),
        ["memory111 stream111", "context111 knowledge111", "vector111 processor111"],
    ),
    (
        ("stream111 context111 knowledge111 vector111 processor111 reasoning111", 6),
        ["stream111", "context111", "knowledge111", "vector111", "processor111", "reasoning111"],
    ),
    (
        ("stream111 context111 knowledge111 vector111 processor111 reasoning111", 10),
        ["stream111", "context111", "knowledge111", "vector111", "processor111", "reasoning111"],
    ),
    (
        ("stream111 context111 knowledge111 vector111 processor111 reasoning111", 18),
        ["stream111", "context111", "knowledge111", "vector111", "processor111", "reasoning111"],
    ),
    (
        ("stream111 context111 knowledge111 vector111 processor111 reasoning111", 28),
        ["stream111 context111", "knowledge111 vector111", "processor111 reasoning111"],
    ),
    (
        ("context111 knowledge111 vector111 processor111 reasoning111 machine111", 6),
        ["context111", "knowledge111", "vector111", "processor111", "reasoning111", "machine111"],
    ),
    (
        ("context111 knowledge111 vector111 processor111 reasoning111 machine111", 10),
        ["context111", "knowledge111", "vector111", "processor111", "reasoning111", "machine111"],
    ),
    (
        ("context111 knowledge111 vector111 processor111 reasoning111 machine111", 18),
        ["context111", "knowledge111", "vector111", "processor111", "reasoning111", "machine111"],
    ),
    (
        ("context111 knowledge111 vector111 processor111 reasoning111 machine111", 28),
        ["context111 knowledge111", "vector111 processor111", "reasoning111 machine111"],
    ),
    (
        ("knowledge111 vector111 processor111 reasoning111 machine111 learning111", 6),
        ["knowledge111", "vector111", "processor111", "reasoning111", "machine111", "learning111"],
    ),
    (
        ("knowledge111 vector111 processor111 reasoning111 machine111 learning111", 10),
        ["knowledge111", "vector111", "processor111", "reasoning111", "machine111", "learning111"],
    ),
    (
        ("knowledge111 vector111 processor111 reasoning111 machine111 learning111", 18),
        ["knowledge111", "vector111", "processor111", "reasoning111", "machine111", "learning111"],
    ),
    (
        ("knowledge111 vector111 processor111 reasoning111 machine111 learning111", 28),
        ["knowledge111 vector111", "processor111 reasoning111", "machine111 learning111"],
    ),
    (
        ("vector111 processor111 reasoning111 machine111 learning111 model111", 6),
        ["vector111", "processor111", "reasoning111", "machine111", "learning111", "model111"],
    ),
    (
        ("vector111 processor111 reasoning111 machine111 learning111 model111", 10),
        ["vector111", "processor111", "reasoning111", "machine111", "learning111", "model111"],
    ),
    (
        ("vector111 processor111 reasoning111 machine111 learning111 model111", 18),
        ["vector111", "processor111", "reasoning111", "machine111", "learning111", "model111"],
    ),
    (
        ("vector111 processor111 reasoning111 machine111 learning111 model111", 28),
        ["vector111 processor111", "reasoning111 machine111", "learning111 model111"],
    ),
    (
        ("processor111 reasoning111 machine111 learning111 model111 token111", 6),
        ["processor111", "reasoning111", "machine111", "learning111", "model111", "token111"],
    ),
    (
        ("processor111 reasoning111 machine111 learning111 model111 token111", 10),
        ["processor111", "reasoning111", "machine111", "learning111", "model111", "token111"],
    ),
    (
        ("processor111 reasoning111 machine111 learning111 model111 token111", 18),
        ["processor111", "reasoning111", "machine111", "learning111", "model111 token111"],
    ),
    (
        ("processor111 reasoning111 machine111 learning111 model111 token111", 28),
        ["processor111 reasoning111", "machine111 learning111", "model111 token111"],
    ),
    (
        ("reasoning111 machine111 learning111 model111 token111 prompt111", 6),
        ["reasoning111", "machine111", "learning111", "model111", "token111", "prompt111"],
    ),
    (
        ("reasoning111 machine111 learning111 model111 token111 prompt111", 10),
        ["reasoning111", "machine111", "learning111", "model111", "token111", "prompt111"],
    ),
    (
        ("reasoning111 machine111 learning111 model111 token111 prompt111", 18),
        ["reasoning111", "machine111", "learning111", "model111 token111", "prompt111"],
    ),
    (
        ("reasoning111 machine111 learning111 model111 token111 prompt111", 28),
        ["reasoning111 machine111", "learning111 model111", "token111 prompt111"],
    ),
    (
        ("machine111 learning111 model111 token111 prompt111 session111", 6),
        ["machine111", "learning111", "model111", "token111", "prompt111", "session111"],
    ),
    (
        ("machine111 learning111 model111 token111 prompt111 session111", 10),
        ["machine111", "learning111", "model111", "token111", "prompt111", "session111"],
    ),
    (
        ("machine111 learning111 model111 token111 prompt111 session111", 18),
        ["machine111", "learning111", "model111 token111", "prompt111", "session111"],
    ),
    (
        ("machine111 learning111 model111 token111 prompt111 session111", 28),
        ["machine111 learning111", "model111 token111 prompt111", "session111"],
    ),
    (
        ("learning111 model111 token111 prompt111 session111 library111", 6),
        ["learning111", "model111", "token111", "prompt111", "session111", "library111"],
    ),
    (
        ("learning111 model111 token111 prompt111 session111 library111", 10),
        ["learning111", "model111", "token111", "prompt111", "session111", "library111"],
    ),
    (
        ("learning111 model111 token111 prompt111 session111 library111", 18),
        ["learning111", "model111 token111", "prompt111", "session111", "library111"],
    ),
    (
        ("learning111 model111 token111 prompt111 session111 library111", 28),
        ["learning111 model111", "token111 prompt111", "session111 library111"],
    ),
    (
        ("model111 token111 prompt111 session111 library111 service111", 6),
        ["model111", "token111", "prompt111", "session111", "library111", "service111"],
    ),
    (
        ("model111 token111 prompt111 session111 library111 service111", 10),
        ["model111", "token111", "prompt111", "session111", "library111", "service111"],
    ),
    (
        ("model111 token111 prompt111 session111 library111 service111", 18),
        ["model111 token111", "prompt111", "session111", "library111", "service111"],
    ),
    (
        ("model111 token111 prompt111 session111 library111 service111", 28),
        ["model111 token111 prompt111", "session111 library111", "service111"],
    ),
    (
        ("token111 prompt111 session111 library111 service111 gateway111", 6),
        ["token111", "prompt111", "session111", "library111", "service111", "gateway111"],
    ),
    (
        ("token111 prompt111 session111 library111 service111 gateway111", 10),
        ["token111", "prompt111", "session111", "library111", "service111", "gateway111"],
    ),
    (
        ("token111 prompt111 session111 library111 service111 gateway111", 18),
        ["token111 prompt111", "session111", "library111", "service111", "gateway111"],
    ),
    (
        ("token111 prompt111 session111 library111 service111 gateway111", 28),
        ["token111 prompt111", "session111 library111", "service111 gateway111"],
    ),
    (
        ("prompt111 session111 library111 service111 gateway111 storage111", 6),
        ["prompt111", "session111", "library111", "service111", "gateway111", "storage111"],
    ),
    (
        ("prompt111 session111 library111 service111 gateway111 storage111", 10),
        ["prompt111", "session111", "library111", "service111", "gateway111", "storage111"],
    ),
    (
        ("prompt111 session111 library111 service111 gateway111 storage111", 18),
        ["prompt111", "session111", "library111", "service111", "gateway111", "storage111"],
    ),
    (
        ("prompt111 session111 library111 service111 gateway111 storage111", 28),
        ["prompt111 session111", "library111 service111", "gateway111 storage111"],
    ),
    (
        ("session111 library111 service111 gateway111 storage111 network111", 6),
        ["session111", "library111", "service111", "gateway111", "storage111", "network111"],
    ),
    (
        ("session111 library111 service111 gateway111 storage111 network111", 10),
        ["session111", "library111", "service111", "gateway111", "storage111", "network111"],
    ),
    (
        ("session111 library111 service111 gateway111 storage111 network111", 18),
        ["session111", "library111", "service111", "gateway111", "storage111", "network111"],
    ),
    (
        ("session111 library111 service111 gateway111 storage111 network111", 28),
        ["session111 library111", "service111 gateway111", "storage111 network111"],
    ),
    (
        ("library111 service111 gateway111 storage111 network111 latency111", 6),
        ["library111", "service111", "gateway111", "storage111", "network111", "latency111"],
    ),
    (
        ("library111 service111 gateway111 storage111 network111 latency111", 10),
        ["library111", "service111", "gateway111", "storage111", "network111", "latency111"],
    ),
    (
        ("library111 service111 gateway111 storage111 network111 latency111", 18),
        ["library111", "service111", "gateway111", "storage111", "network111", "latency111"],
    ),
    (
        ("library111 service111 gateway111 storage111 network111 latency111", 28),
        ["library111 service111", "gateway111 storage111", "network111 latency111"],
    ),
    (
        ("service111 gateway111 storage111 network111 latency111 buffer111", 6),
        ["service111", "gateway111", "storage111", "network111", "latency111", "buffer111"],
    ),
    (
        ("service111 gateway111 storage111 network111 latency111 buffer111", 10),
        ["service111", "gateway111", "storage111", "network111", "latency111", "buffer111"],
    ),
    (
        ("service111 gateway111 storage111 network111 latency111 buffer111", 18),
        ["service111", "gateway111", "storage111", "network111", "latency111", "buffer111"],
    ),
    (
        ("service111 gateway111 storage111 network111 latency111 buffer111", 28),
        ["service111 gateway111", "storage111 network111", "latency111 buffer111"],
    ),
    (
        ("gateway111 storage111 network111 latency111 buffer111 queue111", 6),
        ["gateway111", "storage111", "network111", "latency111", "buffer111", "queue111"],
    ),
    (
        ("gateway111 storage111 network111 latency111 buffer111 queue111", 10),
        ["gateway111", "storage111", "network111", "latency111", "buffer111", "queue111"],
    ),
    (
        ("gateway111 storage111 network111 latency111 buffer111 queue111", 18),
        ["gateway111", "storage111", "network111", "latency111", "buffer111 queue111"],
    ),
    (
        ("gateway111 storage111 network111 latency111 buffer111 queue111", 28),
        ["gateway111 storage111", "network111 latency111", "buffer111 queue111"],
    ),
    (
        ("storage111 network111 latency111 buffer111 queue111 worker111", 6),
        ["storage111", "network111", "latency111", "buffer111", "queue111", "worker111"],
    ),
    (
        ("storage111 network111 latency111 buffer111 queue111 worker111", 10),
        ["storage111", "network111", "latency111", "buffer111", "queue111", "worker111"],
    ),
    (
        ("storage111 network111 latency111 buffer111 queue111 worker111", 18),
        ["storage111", "network111", "latency111", "buffer111 queue111", "worker111"],
    ),
    (
        ("storage111 network111 latency111 buffer111 queue111 worker111", 28),
        ["storage111 network111", "latency111 buffer111", "queue111 worker111"],
    ),
    (
        ("network111 latency111 buffer111 queue111 worker111 kernel111", 6),
        ["network111", "latency111", "buffer111", "queue111", "worker111", "kernel111"],
    ),
    (
        ("network111 latency111 buffer111 queue111 worker111 kernel111", 10),
        ["network111", "latency111", "buffer111", "queue111", "worker111", "kernel111"],
    ),
    (
        ("network111 latency111 buffer111 queue111 worker111 kernel111", 18),
        ["network111", "latency111", "buffer111 queue111", "worker111", "kernel111"],
    ),
    (
        ("network111 latency111 buffer111 queue111 worker111 kernel111", 28),
        ["network111 latency111", "buffer111 queue111 worker111", "kernel111"],
    ),
    (
        ("latency111 buffer111 queue111 worker111 kernel111 signal111", 6),
        ["latency111", "buffer111", "queue111", "worker111", "kernel111", "signal111"],
    ),
    (
        ("latency111 buffer111 queue111 worker111 kernel111 signal111", 10),
        ["latency111", "buffer111", "queue111", "worker111", "kernel111", "signal111"],
    ),
    (
        ("latency111 buffer111 queue111 worker111 kernel111 signal111", 18),
        ["latency111", "buffer111 queue111", "worker111", "kernel111", "signal111"],
    ),
    (
        ("latency111 buffer111 queue111 worker111 kernel111 signal111", 28),
        ["latency111 buffer111", "queue111 worker111 kernel111", "signal111"],
    ),
    (
        ("buffer111 queue111 worker111 kernel111 signal111 packet111", 6),
        ["buffer111", "queue111", "worker111", "kernel111", "signal111", "packet111"],
    ),
    (
        ("buffer111 queue111 worker111 kernel111 signal111 packet111", 10),
        ["buffer111", "queue111", "worker111", "kernel111", "signal111", "packet111"],
    ),
    (
        ("buffer111 queue111 worker111 kernel111 signal111 packet111", 18),
        ["buffer111 queue111", "worker111", "kernel111", "signal111", "packet111"],
    ),
    (
        ("buffer111 queue111 worker111 kernel111 signal111 packet111", 28),
        ["buffer111 queue111 worker111", "kernel111 signal111", "packet111"],
    ),
    (
        ("queue111 worker111 kernel111 signal111 packet111 router111", 6),
        ["queue111", "worker111", "kernel111", "signal111", "packet111", "router111"],
    ),
    (
        ("queue111 worker111 kernel111 signal111 packet111 router111", 10),
        ["queue111", "worker111", "kernel111", "signal111", "packet111", "router111"],
    ),
    (
        ("queue111 worker111 kernel111 signal111 packet111 router111", 18),
        ["queue111 worker111", "kernel111", "signal111", "packet111", "router111"],
    ),
    (
        ("queue111 worker111 kernel111 signal111 packet111 router111", 28),
        ["queue111 worker111 kernel111", "signal111 packet111", "router111"],
    ),
    (
        ("worker111 kernel111 signal111 packet111 router111 cluster111", 6),
        ["worker111", "kernel111", "signal111", "packet111", "router111", "cluster111"],
    ),
    (
        ("worker111 kernel111 signal111 packet111 router111 cluster111", 10),
        ["worker111", "kernel111", "signal111", "packet111", "router111", "cluster111"],
    ),
    (
        ("worker111 kernel111 signal111 packet111 router111 cluster111", 18),
        ["worker111", "kernel111", "signal111", "packet111", "router111", "cluster111"],
    ),
    (
        ("worker111 kernel111 signal111 packet111 router111 cluster111", 28),
        ["worker111 kernel111", "signal111 packet111", "router111 cluster111"],
    ),
    (
        ("kernel111 signal111 packet111 router111 cluster111 mirror111", 6),
        ["kernel111", "signal111", "packet111", "router111", "cluster111", "mirror111"],
    ),
    (
        ("kernel111 signal111 packet111 router111 cluster111 mirror111", 10),
        ["kernel111", "signal111", "packet111", "router111", "cluster111", "mirror111"],
    ),
    (
        ("kernel111 signal111 packet111 router111 cluster111 mirror111", 18),
        ["kernel111", "signal111", "packet111", "router111", "cluster111", "mirror111"],
    ),
    (
        ("kernel111 signal111 packet111 router111 cluster111 mirror111", 28),
        ["kernel111 signal111", "packet111 router111", "cluster111 mirror111"],
    ),
    (
        ("signal111 packet111 router111 cluster111 mirror111 filter111", 6),
        ["signal111", "packet111", "router111", "cluster111", "mirror111", "filter111"],
    ),
    (
        ("signal111 packet111 router111 cluster111 mirror111 filter111", 10),
        ["signal111", "packet111", "router111", "cluster111", "mirror111", "filter111"],
    ),
    (
        ("signal111 packet111 router111 cluster111 mirror111 filter111", 18),
        ["signal111", "packet111", "router111", "cluster111", "mirror111", "filter111"],
    ),
    (
        ("signal111 packet111 router111 cluster111 mirror111 filter111", 28),
        ["signal111 packet111", "router111 cluster111", "mirror111 filter111"],
    ),
    (
        ("packet111 router111 cluster111 mirror111 filter111 ranking111", 6),
        ["packet111", "router111", "cluster111", "mirror111", "filter111", "ranking111"],
    ),
    (
        ("packet111 router111 cluster111 mirror111 filter111 ranking111", 10),
        ["packet111", "router111", "cluster111", "mirror111", "filter111", "ranking111"],
    ),
    (
        ("packet111 router111 cluster111 mirror111 filter111 ranking111", 18),
        ["packet111", "router111", "cluster111", "mirror111", "filter111", "ranking111"],
    ),
    (
        ("packet111 router111 cluster111 mirror111 filter111 ranking111", 28),
        ["packet111 router111", "cluster111 mirror111", "filter111 ranking111"],
    ),
    (
        ("router111 cluster111 mirror111 filter111 ranking111 encoding111", 6),
        ["router111", "cluster111", "mirror111", "filter111", "ranking111", "encoding111"],
    ),
    (
        ("router111 cluster111 mirror111 filter111 ranking111 encoding111", 10),
        ["router111", "cluster111", "mirror111", "filter111", "ranking111", "encoding111"],
    ),
    (
        ("router111 cluster111 mirror111 filter111 ranking111 encoding111", 18),
        ["router111", "cluster111", "mirror111", "filter111", "ranking111", "encoding111"],
    ),
    (
        ("router111 cluster111 mirror111 filter111 ranking111 encoding111", 28),
        ["router111 cluster111", "mirror111 filter111", "ranking111 encoding111"],
    ),
    (
        ("cluster111 mirror111 filter111 ranking111 encoding111 mapping111", 6),
        ["cluster111", "mirror111", "filter111", "ranking111", "encoding111", "mapping111"],
    ),
    (
        ("cluster111 mirror111 filter111 ranking111 encoding111 mapping111", 10),
        ["cluster111", "mirror111", "filter111", "ranking111", "encoding111", "mapping111"],
    ),
    (
        ("cluster111 mirror111 filter111 ranking111 encoding111 mapping111", 18),
        ["cluster111", "mirror111", "filter111", "ranking111", "encoding111", "mapping111"],
    ),
    (
        ("cluster111 mirror111 filter111 ranking111 encoding111 mapping111", 28),
        ["cluster111 mirror111", "filter111 ranking111", "encoding111 mapping111"],
    ),
    (
        ("mirror111 filter111 ranking111 encoding111 mapping111 record111", 6),
        ["mirror111", "filter111", "ranking111", "encoding111", "mapping111", "record111"],
    ),
    (
        ("mirror111 filter111 ranking111 encoding111 mapping111 record111", 10),
        ["mirror111", "filter111", "ranking111", "encoding111", "mapping111", "record111"],
    ),
    (
        ("mirror111 filter111 ranking111 encoding111 mapping111 record111", 18),
        ["mirror111", "filter111", "ranking111", "encoding111", "mapping111", "record111"],
    ),
    (
        ("mirror111 filter111 ranking111 encoding111 mapping111 record111", 28),
        ["mirror111 filter111", "ranking111 encoding111", "mapping111 record111"],
    ),
    (
        ("filter111 ranking111 encoding111 mapping111 record111 candle111", 6),
        ["filter111", "ranking111", "encoding111", "mapping111", "record111", "candle111"],
    ),
    (
        ("filter111 ranking111 encoding111 mapping111 record111 candle111", 10),
        ["filter111", "ranking111", "encoding111", "mapping111", "record111", "candle111"],
    ),
    (
        ("filter111 ranking111 encoding111 mapping111 record111 candle111", 18),
        ["filter111", "ranking111", "encoding111", "mapping111", "record111", "candle111"],
    ),
    (
        ("filter111 ranking111 encoding111 mapping111 record111 candle111", 28),
        ["filter111 ranking111", "encoding111 mapping111", "record111 candle111"],
    ),
    (
        ("ranking111 encoding111 mapping111 record111 candle111 thread111", 6),
        ["ranking111", "encoding111", "mapping111", "record111", "candle111", "thread111"],
    ),
    (
        ("ranking111 encoding111 mapping111 record111 candle111 thread111", 10),
        ["ranking111", "encoding111", "mapping111", "record111", "candle111", "thread111"],
    ),
    (
        ("ranking111 encoding111 mapping111 record111 candle111 thread111", 18),
        ["ranking111", "encoding111", "mapping111", "record111", "candle111", "thread111"],
    ),
    (
        ("ranking111 encoding111 mapping111 record111 candle111 thread111", 28),
        ["ranking111 encoding111", "mapping111 record111", "candle111 thread111"],
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
