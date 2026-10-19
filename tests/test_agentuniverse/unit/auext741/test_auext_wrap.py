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
        ("round 741: the quick brown fox jumps over the lazy dog", 4),
        ["round", "741:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 741: the quick brown fox jumps over the lazy dog", 8),
        ["round", "741: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 741: the quick brown fox jumps over the lazy dog", 12),
        ["round 741:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 741: the quick brown fox jumps over the lazy dog", 16),
        ["round 741: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 741: the quick brown fox jumps over the lazy dog", 24),
        ["round 741: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 741: the quick brown fox jumps over the lazy dog", 32),
        ["round 741: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 741: agentuniverse is a framework for multi agents", 4),
        ["round", "741:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 741: agentuniverse is a framework for multi agents", 8),
        ["round", "741:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 741: agentuniverse is a framework for multi agents", 12),
        ["round 741:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 741: agentuniverse is a framework for multi agents", 16),
        ["round 741:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 741: agentuniverse is a framework for multi agents", 24),
        ["round 741: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 741: agentuniverse is a framework for multi agents", 32),
        ["round 741: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 741: knowledge stored as vectors enables retrieval", 4),
        ["round", "741:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 741: knowledge stored as vectors enables retrieval", 8),
        ["round", "741:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 741: knowledge stored as vectors enables retrieval", 12),
        ["round 741:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 741: knowledge stored as vectors enables retrieval", 16),
        ["round 741:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 741: knowledge stored as vectors enables retrieval", 24),
        ["round 741: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 741: knowledge stored as vectors enables retrieval", 32),
        ["round 741: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 741: the processor reads the record then stops", 4),
        ["round", "741:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 741: the processor reads the record then stops", 8),
        ["round", "741: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 741: the processor reads the record then stops", 12),
        ["round 741:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 741: the processor reads the record then stops", 16),
        ["round 741: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 741: the processor reads the record then stops", 24),
        ["round 741: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 741: the processor reads the record then stops", 32),
        ["round 741: the processor reads", "the record then stops"],
    ),
    (
        ("round 741: a worker pulls the next task from the queue", 4),
        ["round", "741:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 741: a worker pulls the next task from the queue", 8),
        ["round", "741: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 741: a worker pulls the next task from the queue", 12),
        ["round 741: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 741: a worker pulls the next task from the queue", 16),
        ["round 741: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 741: a worker pulls the next task from the queue", 24),
        ["round 741: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 741: a worker pulls the next task from the queue", 32),
        ["round 741: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 741: signals travel through the network layer", 4),
        ["round", "741:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 741: signals travel through the network layer", 8),
        ["round", "741:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 741: signals travel through the network layer", 12),
        ["round 741:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 741: signals travel through the network layer", 16),
        ["round 741:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 741: signals travel through the network layer", 24),
        ["round 741: signals", "travel through the", "network layer"],
    ),
    (
        ("round 741: signals travel through the network layer", 32),
        ["round 741: signals travel", "through the network layer"],
    ),
    (
        ("round 741: the gateway routes each request by policy", 4),
        ["round", "741:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 741: the gateway routes each request by policy", 8),
        ["round", "741: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 741: the gateway routes each request by policy", 12),
        ["round 741:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 741: the gateway routes each request by policy", 16),
        ["round 741: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 741: the gateway routes each request by policy", 24),
        ["round 741: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 741: the gateway routes each request by policy", 32),
        ["round 741: the gateway routes", "each request by policy"],
    ),
    (
        ("round 741: memory grows until the buffer is full", 4),
        ["round", "741:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 741: memory grows until the buffer is full", 8),
        ["round", "741:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 741: memory grows until the buffer is full", 12),
        ["round 741:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 741: memory grows until the buffer is full", 16),
        ["round 741:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 741: memory grows until the buffer is full", 24), ["round 741: memory grows", "until the buffer is full"]),
    (("round 741: memory grows until the buffer is full", 32), ["round 741: memory grows until", "the buffer is full"]),
    (
        ("round 741: the cluster mirrors every packet twice", 4),
        ["round", "741:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 741: the cluster mirrors every packet twice", 8),
        ["round", "741: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 741: the cluster mirrors every packet twice", 12),
        ["round 741:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 741: the cluster mirrors every packet twice", 16),
        ["round 741: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 741: the cluster mirrors every packet twice", 24),
        ["round 741: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 741: the cluster mirrors every packet twice", 32),
        ["round 741: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 741: ranking uses tokens learned from the corpus", 4),
        ["round", "741:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 741: ranking uses tokens learned from the corpus", 8),
        ["round", "741:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 741: ranking uses tokens learned from the corpus", 12),
        ["round 741:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 741: ranking uses tokens learned from the corpus", 16),
        ["round 741:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 741: ranking uses tokens learned from the corpus", 24),
        ["round 741: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 741: ranking uses tokens learned from the corpus", 32),
        ["round 741: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 741: a long session ends when the candle dies", 4),
        ["round", "741:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 741: a long session ends when the candle dies", 8),
        ["round", "741: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 741: a long session ends when the candle dies", 12),
        ["round 741: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 741: a long session ends when the candle dies", 16),
        ["round 741: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 741: a long session ends when the candle dies", 24),
        ["round 741: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 741: a long session ends when the candle dies", 32),
        ["round 741: a long session ends", "when the candle dies"],
    ),
    (
        ("round 741: encode the prompt then map the result", 4),
        ["round", "741:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 741: encode the prompt then map the result", 8),
        ["round", "741:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 741: encode the prompt then map the result", 12),
        ["round 741:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 741: encode the prompt then map the result", 16),
        ["round 741:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 741: encode the prompt then map the result", 24),
        ["round 741: encode the", "prompt then map the", "result"],
    ),
    (("round 741: encode the prompt then map the result", 32), ["round 741: encode the prompt", "then map the result"]),
    (
        ("round 741: the kernel wakes the worker at dawn", 4),
        ["round", "741:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 741: the kernel wakes the worker at dawn", 8),
        ["round", "741: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 741: the kernel wakes the worker at dawn", 12),
        ["round 741:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 741: the kernel wakes the worker at dawn", 16), ["round 741: the", "kernel wakes the", "worker at dawn"]),
    (("round 741: the kernel wakes the worker at dawn", 24), ["round 741: the kernel", "wakes the worker at dawn"]),
    (("round 741: the kernel wakes the worker at dawn", 32), ["round 741: the kernel wakes the", "worker at dawn"]),
    (
        ("round 741: service latency drops after the patch", 4),
        ["round", "741:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 741: service latency drops after the patch", 8),
        ["round", "741:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 741: service latency drops after the patch", 12),
        ["round 741:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 741: service latency drops after the patch", 16),
        ["round 741:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 741: service latency drops after the patch", 24),
        ["round 741: service", "latency drops after the", "patch"],
    ),
    (("round 741: service latency drops after the patch", 32), ["round 741: service latency drops", "after the patch"]),
    (
        ("round 741: the library caches every vector it sees", 4),
        ["round", "741:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 741: the library caches every vector it sees", 8),
        ["round", "741: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 741: the library caches every vector it sees", 12),
        ["round 741:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 741: the library caches every vector it sees", 16),
        ["round 741: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 741: the library caches every vector it sees", 24),
        ["round 741: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 741: the library caches every vector it sees", 32),
        ["round 741: the library caches", "every vector it sees"],
    ),
    (
        ("round 741: agents argue then the debate resolves", 4),
        ["round", "741:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 741: agents argue then the debate resolves", 8),
        ["round", "741:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 741: agents argue then the debate resolves", 12),
        ["round 741:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 741: agents argue then the debate resolves", 16),
        ["round 741:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 741: agents argue then the debate resolves", 24), ["round 741: agents argue", "then the debate resolves"]),
    (("round 741: agents argue then the debate resolves", 32), ["round 741: agents argue then the", "debate resolves"]),
    (
        ("round 741: the filter keeps only strong matches", 4),
        ["round", "741:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 741: the filter keeps only strong matches", 8),
        ["round", "741: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 741: the filter keeps only strong matches", 12),
        ["round 741:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 741: the filter keeps only strong matches", 16),
        ["round 741: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 741: the filter keeps only strong matches", 24),
        ["round 741: the filter", "keeps only strong", "matches"],
    ),
    (("round 741: the filter keeps only strong matches", 32), ["round 741: the filter keeps only", "strong matches"]),
    (
        ("round 741: the model answers with a short reply", 4),
        ["round", "741:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 741: the model answers with a short reply", 8),
        ["round", "741: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 741: the model answers with a short reply", 12),
        ["round 741:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 741: the model answers with a short reply", 16),
        ["round 741: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 741: the model answers with a short reply", 24),
        ["round 741: the model", "answers with a short", "reply"],
    ),
    (("round 741: the model answers with a short reply", 32), ["round 741: the model answers", "with a short reply"]),
    (
        ("round 741: the recorder stores the reasoning trace", 4),
        ["round", "741:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 741: the recorder stores the reasoning trace", 8),
        ["round", "741: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 741: the recorder stores the reasoning trace", 12),
        ["round 741:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 741: the recorder stores the reasoning trace", 16),
        ["round 741: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 741: the recorder stores the reasoning trace", 24),
        ["round 741: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 741: the recorder stores the reasoning trace", 32),
        ["round 741: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 741: the angel watches the processor run", 4),
        ["round", "741:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 741: the angel watches the processor run", 8),
        ["round", "741: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 741: the angel watches the processor run", 12),
        ["round 741:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 741: the angel watches the processor run", 16),
        ["round 741: the", "angel watches", "the processor", "run"],
    ),
    (("round 741: the angel watches the processor run", 24), ["round 741: the angel", "watches the processor", "run"]),
    (("round 741: the angel watches the processor run", 32), ["round 741: the angel watches the", "processor run"]),
    (
        ("round 741: angle of the vector decides the match", 4),
        ["round", "741:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 741: angle of the vector decides the match", 8),
        ["round", "741:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 741: angle of the vector decides the match", 12),
        ["round 741:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 741: angle of the vector decides the match", 16),
        ["round 741: angle", "of the vector", "decides the", "match"],
    ),
    (("round 741: angle of the vector decides the match", 24), ["round 741: angle of the", "vector decides the match"]),
    (("round 741: angle of the vector decides the match", 32), ["round 741: angle of the vector", "decides the match"]),
    (
        ("round 741: the candle burns twice as long at night", 4),
        ["round", "741:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 741: the candle burns twice as long at night", 8),
        ["round", "741: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 741: the candle burns twice as long at night", 12),
        ["round 741:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 741: the candle burns twice as long at night", 16),
        ["round 741: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 741: the candle burns twice as long at night", 24),
        ["round 741: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 741: the candle burns twice as long at night", 32),
        ["round 741: the candle burns", "twice as long at night"],
    ),
    (
        ("round 741: a mirror of the universe in one line", 4),
        ["round", "741:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 741: a mirror of the universe in one line", 8),
        ["round", "741: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 741: a mirror of the universe in one line", 12),
        ["round 741: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 741: a mirror of the universe in one line", 16),
        ["round 741: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 741: a mirror of the universe in one line", 24), ["round 741: a mirror of", "the universe in one line"]),
    (("round 741: a mirror of the universe in one line", 32), ["round 741: a mirror of the", "universe in one line"]),
    (
        ("round 741: the queue drains before the storm", 4),
        ["round", "741:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 741: the queue drains before the storm", 8),
        ["round", "741: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 741: the queue drains before the storm", 12),
        ["round 741:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 741: the queue drains before the storm", 16), ["round 741: the", "queue drains", "before the storm"]),
    (("round 741: the queue drains before the storm", 24), ["round 741: the queue", "drains before the storm"]),
    (("round 741: the queue drains before the storm", 32), ["round 741: the queue drains", "before the storm"]),
    (
        ("kitten741 sitting741 agent741 angle741 universe741 memory741", 6),
        ["kitten741", "sitting741", "agent741", "angle741", "universe741", "memory741"],
    ),
    (
        ("kitten741 sitting741 agent741 angle741 universe741 memory741", 10),
        ["kitten741", "sitting741", "agent741", "angle741", "universe741", "memory741"],
    ),
    (
        ("kitten741 sitting741 agent741 angle741 universe741 memory741", 18),
        ["kitten741", "sitting741", "agent741 angle741", "universe741", "memory741"],
    ),
    (
        ("kitten741 sitting741 agent741 angle741 universe741 memory741", 28),
        ["kitten741 sitting741", "agent741 angle741", "universe741 memory741"],
    ),
    (
        ("sitting741 agent741 angle741 universe741 memory741 stream741", 6),
        ["sitting741", "agent741", "angle741", "universe741", "memory741", "stream741"],
    ),
    (
        ("sitting741 agent741 angle741 universe741 memory741 stream741", 10),
        ["sitting741", "agent741", "angle741", "universe741", "memory741", "stream741"],
    ),
    (
        ("sitting741 agent741 angle741 universe741 memory741 stream741", 18),
        ["sitting741", "agent741 angle741", "universe741", "memory741", "stream741"],
    ),
    (
        ("sitting741 agent741 angle741 universe741 memory741 stream741", 28),
        ["sitting741 agent741 angle741", "universe741 memory741", "stream741"],
    ),
    (
        ("agent741 angle741 universe741 memory741 stream741 context741", 6),
        ["agent741", "angle741", "universe741", "memory741", "stream741", "context741"],
    ),
    (
        ("agent741 angle741 universe741 memory741 stream741 context741", 10),
        ["agent741", "angle741", "universe741", "memory741", "stream741", "context741"],
    ),
    (
        ("agent741 angle741 universe741 memory741 stream741 context741", 18),
        ["agent741 angle741", "universe741", "memory741", "stream741", "context741"],
    ),
    (
        ("agent741 angle741 universe741 memory741 stream741 context741", 28),
        ["agent741 angle741", "universe741 memory741", "stream741 context741"],
    ),
    (
        ("angle741 universe741 memory741 stream741 context741 knowledge741", 6),
        ["angle741", "universe741", "memory741", "stream741", "context741", "knowledge741"],
    ),
    (
        ("angle741 universe741 memory741 stream741 context741 knowledge741", 10),
        ["angle741", "universe741", "memory741", "stream741", "context741", "knowledge741"],
    ),
    (
        ("angle741 universe741 memory741 stream741 context741 knowledge741", 18),
        ["angle741", "universe741", "memory741", "stream741", "context741", "knowledge741"],
    ),
    (
        ("angle741 universe741 memory741 stream741 context741 knowledge741", 28),
        ["angle741 universe741", "memory741 stream741", "context741 knowledge741"],
    ),
    (
        ("universe741 memory741 stream741 context741 knowledge741 vector741", 6),
        ["universe741", "memory741", "stream741", "context741", "knowledge741", "vector741"],
    ),
    (
        ("universe741 memory741 stream741 context741 knowledge741 vector741", 10),
        ["universe741", "memory741", "stream741", "context741", "knowledge741", "vector741"],
    ),
    (
        ("universe741 memory741 stream741 context741 knowledge741 vector741", 18),
        ["universe741", "memory741", "stream741", "context741", "knowledge741", "vector741"],
    ),
    (
        ("universe741 memory741 stream741 context741 knowledge741 vector741", 28),
        ["universe741 memory741", "stream741 context741", "knowledge741 vector741"],
    ),
    (
        ("memory741 stream741 context741 knowledge741 vector741 processor741", 6),
        ["memory741", "stream741", "context741", "knowledge741", "vector741", "processor741"],
    ),
    (
        ("memory741 stream741 context741 knowledge741 vector741 processor741", 10),
        ["memory741", "stream741", "context741", "knowledge741", "vector741", "processor741"],
    ),
    (
        ("memory741 stream741 context741 knowledge741 vector741 processor741", 18),
        ["memory741", "stream741", "context741", "knowledge741", "vector741", "processor741"],
    ),
    (
        ("memory741 stream741 context741 knowledge741 vector741 processor741", 28),
        ["memory741 stream741", "context741 knowledge741", "vector741 processor741"],
    ),
    (
        ("stream741 context741 knowledge741 vector741 processor741 reasoning741", 6),
        ["stream741", "context741", "knowledge741", "vector741", "processor741", "reasoning741"],
    ),
    (
        ("stream741 context741 knowledge741 vector741 processor741 reasoning741", 10),
        ["stream741", "context741", "knowledge741", "vector741", "processor741", "reasoning741"],
    ),
    (
        ("stream741 context741 knowledge741 vector741 processor741 reasoning741", 18),
        ["stream741", "context741", "knowledge741", "vector741", "processor741", "reasoning741"],
    ),
    (
        ("stream741 context741 knowledge741 vector741 processor741 reasoning741", 28),
        ["stream741 context741", "knowledge741 vector741", "processor741 reasoning741"],
    ),
    (
        ("context741 knowledge741 vector741 processor741 reasoning741 machine741", 6),
        ["context741", "knowledge741", "vector741", "processor741", "reasoning741", "machine741"],
    ),
    (
        ("context741 knowledge741 vector741 processor741 reasoning741 machine741", 10),
        ["context741", "knowledge741", "vector741", "processor741", "reasoning741", "machine741"],
    ),
    (
        ("context741 knowledge741 vector741 processor741 reasoning741 machine741", 18),
        ["context741", "knowledge741", "vector741", "processor741", "reasoning741", "machine741"],
    ),
    (
        ("context741 knowledge741 vector741 processor741 reasoning741 machine741", 28),
        ["context741 knowledge741", "vector741 processor741", "reasoning741 machine741"],
    ),
    (
        ("knowledge741 vector741 processor741 reasoning741 machine741 learning741", 6),
        ["knowledge741", "vector741", "processor741", "reasoning741", "machine741", "learning741"],
    ),
    (
        ("knowledge741 vector741 processor741 reasoning741 machine741 learning741", 10),
        ["knowledge741", "vector741", "processor741", "reasoning741", "machine741", "learning741"],
    ),
    (
        ("knowledge741 vector741 processor741 reasoning741 machine741 learning741", 18),
        ["knowledge741", "vector741", "processor741", "reasoning741", "machine741", "learning741"],
    ),
    (
        ("knowledge741 vector741 processor741 reasoning741 machine741 learning741", 28),
        ["knowledge741 vector741", "processor741 reasoning741", "machine741 learning741"],
    ),
    (
        ("vector741 processor741 reasoning741 machine741 learning741 model741", 6),
        ["vector741", "processor741", "reasoning741", "machine741", "learning741", "model741"],
    ),
    (
        ("vector741 processor741 reasoning741 machine741 learning741 model741", 10),
        ["vector741", "processor741", "reasoning741", "machine741", "learning741", "model741"],
    ),
    (
        ("vector741 processor741 reasoning741 machine741 learning741 model741", 18),
        ["vector741", "processor741", "reasoning741", "machine741", "learning741", "model741"],
    ),
    (
        ("vector741 processor741 reasoning741 machine741 learning741 model741", 28),
        ["vector741 processor741", "reasoning741 machine741", "learning741 model741"],
    ),
    (
        ("processor741 reasoning741 machine741 learning741 model741 token741", 6),
        ["processor741", "reasoning741", "machine741", "learning741", "model741", "token741"],
    ),
    (
        ("processor741 reasoning741 machine741 learning741 model741 token741", 10),
        ["processor741", "reasoning741", "machine741", "learning741", "model741", "token741"],
    ),
    (
        ("processor741 reasoning741 machine741 learning741 model741 token741", 18),
        ["processor741", "reasoning741", "machine741", "learning741", "model741 token741"],
    ),
    (
        ("processor741 reasoning741 machine741 learning741 model741 token741", 28),
        ["processor741 reasoning741", "machine741 learning741", "model741 token741"],
    ),
    (
        ("reasoning741 machine741 learning741 model741 token741 prompt741", 6),
        ["reasoning741", "machine741", "learning741", "model741", "token741", "prompt741"],
    ),
    (
        ("reasoning741 machine741 learning741 model741 token741 prompt741", 10),
        ["reasoning741", "machine741", "learning741", "model741", "token741", "prompt741"],
    ),
    (
        ("reasoning741 machine741 learning741 model741 token741 prompt741", 18),
        ["reasoning741", "machine741", "learning741", "model741 token741", "prompt741"],
    ),
    (
        ("reasoning741 machine741 learning741 model741 token741 prompt741", 28),
        ["reasoning741 machine741", "learning741 model741", "token741 prompt741"],
    ),
    (
        ("machine741 learning741 model741 token741 prompt741 session741", 6),
        ["machine741", "learning741", "model741", "token741", "prompt741", "session741"],
    ),
    (
        ("machine741 learning741 model741 token741 prompt741 session741", 10),
        ["machine741", "learning741", "model741", "token741", "prompt741", "session741"],
    ),
    (
        ("machine741 learning741 model741 token741 prompt741 session741", 18),
        ["machine741", "learning741", "model741 token741", "prompt741", "session741"],
    ),
    (
        ("machine741 learning741 model741 token741 prompt741 session741", 28),
        ["machine741 learning741", "model741 token741 prompt741", "session741"],
    ),
    (
        ("learning741 model741 token741 prompt741 session741 library741", 6),
        ["learning741", "model741", "token741", "prompt741", "session741", "library741"],
    ),
    (
        ("learning741 model741 token741 prompt741 session741 library741", 10),
        ["learning741", "model741", "token741", "prompt741", "session741", "library741"],
    ),
    (
        ("learning741 model741 token741 prompt741 session741 library741", 18),
        ["learning741", "model741 token741", "prompt741", "session741", "library741"],
    ),
    (
        ("learning741 model741 token741 prompt741 session741 library741", 28),
        ["learning741 model741", "token741 prompt741", "session741 library741"],
    ),
    (
        ("model741 token741 prompt741 session741 library741 service741", 6),
        ["model741", "token741", "prompt741", "session741", "library741", "service741"],
    ),
    (
        ("model741 token741 prompt741 session741 library741 service741", 10),
        ["model741", "token741", "prompt741", "session741", "library741", "service741"],
    ),
    (
        ("model741 token741 prompt741 session741 library741 service741", 18),
        ["model741 token741", "prompt741", "session741", "library741", "service741"],
    ),
    (
        ("model741 token741 prompt741 session741 library741 service741", 28),
        ["model741 token741 prompt741", "session741 library741", "service741"],
    ),
    (
        ("token741 prompt741 session741 library741 service741 gateway741", 6),
        ["token741", "prompt741", "session741", "library741", "service741", "gateway741"],
    ),
    (
        ("token741 prompt741 session741 library741 service741 gateway741", 10),
        ["token741", "prompt741", "session741", "library741", "service741", "gateway741"],
    ),
    (
        ("token741 prompt741 session741 library741 service741 gateway741", 18),
        ["token741 prompt741", "session741", "library741", "service741", "gateway741"],
    ),
    (
        ("token741 prompt741 session741 library741 service741 gateway741", 28),
        ["token741 prompt741", "session741 library741", "service741 gateway741"],
    ),
    (
        ("prompt741 session741 library741 service741 gateway741 storage741", 6),
        ["prompt741", "session741", "library741", "service741", "gateway741", "storage741"],
    ),
    (
        ("prompt741 session741 library741 service741 gateway741 storage741", 10),
        ["prompt741", "session741", "library741", "service741", "gateway741", "storage741"],
    ),
    (
        ("prompt741 session741 library741 service741 gateway741 storage741", 18),
        ["prompt741", "session741", "library741", "service741", "gateway741", "storage741"],
    ),
    (
        ("prompt741 session741 library741 service741 gateway741 storage741", 28),
        ["prompt741 session741", "library741 service741", "gateway741 storage741"],
    ),
    (
        ("session741 library741 service741 gateway741 storage741 network741", 6),
        ["session741", "library741", "service741", "gateway741", "storage741", "network741"],
    ),
    (
        ("session741 library741 service741 gateway741 storage741 network741", 10),
        ["session741", "library741", "service741", "gateway741", "storage741", "network741"],
    ),
    (
        ("session741 library741 service741 gateway741 storage741 network741", 18),
        ["session741", "library741", "service741", "gateway741", "storage741", "network741"],
    ),
    (
        ("session741 library741 service741 gateway741 storage741 network741", 28),
        ["session741 library741", "service741 gateway741", "storage741 network741"],
    ),
    (
        ("library741 service741 gateway741 storage741 network741 latency741", 6),
        ["library741", "service741", "gateway741", "storage741", "network741", "latency741"],
    ),
    (
        ("library741 service741 gateway741 storage741 network741 latency741", 10),
        ["library741", "service741", "gateway741", "storage741", "network741", "latency741"],
    ),
    (
        ("library741 service741 gateway741 storage741 network741 latency741", 18),
        ["library741", "service741", "gateway741", "storage741", "network741", "latency741"],
    ),
    (
        ("library741 service741 gateway741 storage741 network741 latency741", 28),
        ["library741 service741", "gateway741 storage741", "network741 latency741"],
    ),
    (
        ("service741 gateway741 storage741 network741 latency741 buffer741", 6),
        ["service741", "gateway741", "storage741", "network741", "latency741", "buffer741"],
    ),
    (
        ("service741 gateway741 storage741 network741 latency741 buffer741", 10),
        ["service741", "gateway741", "storage741", "network741", "latency741", "buffer741"],
    ),
    (
        ("service741 gateway741 storage741 network741 latency741 buffer741", 18),
        ["service741", "gateway741", "storage741", "network741", "latency741", "buffer741"],
    ),
    (
        ("service741 gateway741 storage741 network741 latency741 buffer741", 28),
        ["service741 gateway741", "storage741 network741", "latency741 buffer741"],
    ),
    (
        ("gateway741 storage741 network741 latency741 buffer741 queue741", 6),
        ["gateway741", "storage741", "network741", "latency741", "buffer741", "queue741"],
    ),
    (
        ("gateway741 storage741 network741 latency741 buffer741 queue741", 10),
        ["gateway741", "storage741", "network741", "latency741", "buffer741", "queue741"],
    ),
    (
        ("gateway741 storage741 network741 latency741 buffer741 queue741", 18),
        ["gateway741", "storage741", "network741", "latency741", "buffer741 queue741"],
    ),
    (
        ("gateway741 storage741 network741 latency741 buffer741 queue741", 28),
        ["gateway741 storage741", "network741 latency741", "buffer741 queue741"],
    ),
    (
        ("storage741 network741 latency741 buffer741 queue741 worker741", 6),
        ["storage741", "network741", "latency741", "buffer741", "queue741", "worker741"],
    ),
    (
        ("storage741 network741 latency741 buffer741 queue741 worker741", 10),
        ["storage741", "network741", "latency741", "buffer741", "queue741", "worker741"],
    ),
    (
        ("storage741 network741 latency741 buffer741 queue741 worker741", 18),
        ["storage741", "network741", "latency741", "buffer741 queue741", "worker741"],
    ),
    (
        ("storage741 network741 latency741 buffer741 queue741 worker741", 28),
        ["storage741 network741", "latency741 buffer741", "queue741 worker741"],
    ),
    (
        ("network741 latency741 buffer741 queue741 worker741 kernel741", 6),
        ["network741", "latency741", "buffer741", "queue741", "worker741", "kernel741"],
    ),
    (
        ("network741 latency741 buffer741 queue741 worker741 kernel741", 10),
        ["network741", "latency741", "buffer741", "queue741", "worker741", "kernel741"],
    ),
    (
        ("network741 latency741 buffer741 queue741 worker741 kernel741", 18),
        ["network741", "latency741", "buffer741 queue741", "worker741", "kernel741"],
    ),
    (
        ("network741 latency741 buffer741 queue741 worker741 kernel741", 28),
        ["network741 latency741", "buffer741 queue741 worker741", "kernel741"],
    ),
    (
        ("latency741 buffer741 queue741 worker741 kernel741 signal741", 6),
        ["latency741", "buffer741", "queue741", "worker741", "kernel741", "signal741"],
    ),
    (
        ("latency741 buffer741 queue741 worker741 kernel741 signal741", 10),
        ["latency741", "buffer741", "queue741", "worker741", "kernel741", "signal741"],
    ),
    (
        ("latency741 buffer741 queue741 worker741 kernel741 signal741", 18),
        ["latency741", "buffer741 queue741", "worker741", "kernel741", "signal741"],
    ),
    (
        ("latency741 buffer741 queue741 worker741 kernel741 signal741", 28),
        ["latency741 buffer741", "queue741 worker741 kernel741", "signal741"],
    ),
    (
        ("buffer741 queue741 worker741 kernel741 signal741 packet741", 6),
        ["buffer741", "queue741", "worker741", "kernel741", "signal741", "packet741"],
    ),
    (
        ("buffer741 queue741 worker741 kernel741 signal741 packet741", 10),
        ["buffer741", "queue741", "worker741", "kernel741", "signal741", "packet741"],
    ),
    (
        ("buffer741 queue741 worker741 kernel741 signal741 packet741", 18),
        ["buffer741 queue741", "worker741", "kernel741", "signal741", "packet741"],
    ),
    (
        ("buffer741 queue741 worker741 kernel741 signal741 packet741", 28),
        ["buffer741 queue741 worker741", "kernel741 signal741", "packet741"],
    ),
    (
        ("queue741 worker741 kernel741 signal741 packet741 router741", 6),
        ["queue741", "worker741", "kernel741", "signal741", "packet741", "router741"],
    ),
    (
        ("queue741 worker741 kernel741 signal741 packet741 router741", 10),
        ["queue741", "worker741", "kernel741", "signal741", "packet741", "router741"],
    ),
    (
        ("queue741 worker741 kernel741 signal741 packet741 router741", 18),
        ["queue741 worker741", "kernel741", "signal741", "packet741", "router741"],
    ),
    (
        ("queue741 worker741 kernel741 signal741 packet741 router741", 28),
        ["queue741 worker741 kernel741", "signal741 packet741", "router741"],
    ),
    (
        ("worker741 kernel741 signal741 packet741 router741 cluster741", 6),
        ["worker741", "kernel741", "signal741", "packet741", "router741", "cluster741"],
    ),
    (
        ("worker741 kernel741 signal741 packet741 router741 cluster741", 10),
        ["worker741", "kernel741", "signal741", "packet741", "router741", "cluster741"],
    ),
    (
        ("worker741 kernel741 signal741 packet741 router741 cluster741", 18),
        ["worker741", "kernel741", "signal741", "packet741", "router741", "cluster741"],
    ),
    (
        ("worker741 kernel741 signal741 packet741 router741 cluster741", 28),
        ["worker741 kernel741", "signal741 packet741", "router741 cluster741"],
    ),
    (
        ("kernel741 signal741 packet741 router741 cluster741 mirror741", 6),
        ["kernel741", "signal741", "packet741", "router741", "cluster741", "mirror741"],
    ),
    (
        ("kernel741 signal741 packet741 router741 cluster741 mirror741", 10),
        ["kernel741", "signal741", "packet741", "router741", "cluster741", "mirror741"],
    ),
    (
        ("kernel741 signal741 packet741 router741 cluster741 mirror741", 18),
        ["kernel741", "signal741", "packet741", "router741", "cluster741", "mirror741"],
    ),
    (
        ("kernel741 signal741 packet741 router741 cluster741 mirror741", 28),
        ["kernel741 signal741", "packet741 router741", "cluster741 mirror741"],
    ),
    (
        ("signal741 packet741 router741 cluster741 mirror741 filter741", 6),
        ["signal741", "packet741", "router741", "cluster741", "mirror741", "filter741"],
    ),
    (
        ("signal741 packet741 router741 cluster741 mirror741 filter741", 10),
        ["signal741", "packet741", "router741", "cluster741", "mirror741", "filter741"],
    ),
    (
        ("signal741 packet741 router741 cluster741 mirror741 filter741", 18),
        ["signal741", "packet741", "router741", "cluster741", "mirror741", "filter741"],
    ),
    (
        ("signal741 packet741 router741 cluster741 mirror741 filter741", 28),
        ["signal741 packet741", "router741 cluster741", "mirror741 filter741"],
    ),
    (
        ("packet741 router741 cluster741 mirror741 filter741 ranking741", 6),
        ["packet741", "router741", "cluster741", "mirror741", "filter741", "ranking741"],
    ),
    (
        ("packet741 router741 cluster741 mirror741 filter741 ranking741", 10),
        ["packet741", "router741", "cluster741", "mirror741", "filter741", "ranking741"],
    ),
    (
        ("packet741 router741 cluster741 mirror741 filter741 ranking741", 18),
        ["packet741", "router741", "cluster741", "mirror741", "filter741", "ranking741"],
    ),
    (
        ("packet741 router741 cluster741 mirror741 filter741 ranking741", 28),
        ["packet741 router741", "cluster741 mirror741", "filter741 ranking741"],
    ),
    (
        ("router741 cluster741 mirror741 filter741 ranking741 encoding741", 6),
        ["router741", "cluster741", "mirror741", "filter741", "ranking741", "encoding741"],
    ),
    (
        ("router741 cluster741 mirror741 filter741 ranking741 encoding741", 10),
        ["router741", "cluster741", "mirror741", "filter741", "ranking741", "encoding741"],
    ),
    (
        ("router741 cluster741 mirror741 filter741 ranking741 encoding741", 18),
        ["router741", "cluster741", "mirror741", "filter741", "ranking741", "encoding741"],
    ),
    (
        ("router741 cluster741 mirror741 filter741 ranking741 encoding741", 28),
        ["router741 cluster741", "mirror741 filter741", "ranking741 encoding741"],
    ),
    (
        ("cluster741 mirror741 filter741 ranking741 encoding741 mapping741", 6),
        ["cluster741", "mirror741", "filter741", "ranking741", "encoding741", "mapping741"],
    ),
    (
        ("cluster741 mirror741 filter741 ranking741 encoding741 mapping741", 10),
        ["cluster741", "mirror741", "filter741", "ranking741", "encoding741", "mapping741"],
    ),
    (
        ("cluster741 mirror741 filter741 ranking741 encoding741 mapping741", 18),
        ["cluster741", "mirror741", "filter741", "ranking741", "encoding741", "mapping741"],
    ),
    (
        ("cluster741 mirror741 filter741 ranking741 encoding741 mapping741", 28),
        ["cluster741 mirror741", "filter741 ranking741", "encoding741 mapping741"],
    ),
    (
        ("mirror741 filter741 ranking741 encoding741 mapping741 record741", 6),
        ["mirror741", "filter741", "ranking741", "encoding741", "mapping741", "record741"],
    ),
    (
        ("mirror741 filter741 ranking741 encoding741 mapping741 record741", 10),
        ["mirror741", "filter741", "ranking741", "encoding741", "mapping741", "record741"],
    ),
    (
        ("mirror741 filter741 ranking741 encoding741 mapping741 record741", 18),
        ["mirror741", "filter741", "ranking741", "encoding741", "mapping741", "record741"],
    ),
    (
        ("mirror741 filter741 ranking741 encoding741 mapping741 record741", 28),
        ["mirror741 filter741", "ranking741 encoding741", "mapping741 record741"],
    ),
    (
        ("filter741 ranking741 encoding741 mapping741 record741 candle741", 6),
        ["filter741", "ranking741", "encoding741", "mapping741", "record741", "candle741"],
    ),
    (
        ("filter741 ranking741 encoding741 mapping741 record741 candle741", 10),
        ["filter741", "ranking741", "encoding741", "mapping741", "record741", "candle741"],
    ),
    (
        ("filter741 ranking741 encoding741 mapping741 record741 candle741", 18),
        ["filter741", "ranking741", "encoding741", "mapping741", "record741", "candle741"],
    ),
    (
        ("filter741 ranking741 encoding741 mapping741 record741 candle741", 28),
        ["filter741 ranking741", "encoding741 mapping741", "record741 candle741"],
    ),
    (
        ("ranking741 encoding741 mapping741 record741 candle741 thread741", 6),
        ["ranking741", "encoding741", "mapping741", "record741", "candle741", "thread741"],
    ),
    (
        ("ranking741 encoding741 mapping741 record741 candle741 thread741", 10),
        ["ranking741", "encoding741", "mapping741", "record741", "candle741", "thread741"],
    ),
    (
        ("ranking741 encoding741 mapping741 record741 candle741 thread741", 18),
        ["ranking741", "encoding741", "mapping741", "record741", "candle741", "thread741"],
    ),
    (
        ("ranking741 encoding741 mapping741 record741 candle741 thread741", 28),
        ["ranking741 encoding741", "mapping741 record741", "candle741 thread741"],
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
