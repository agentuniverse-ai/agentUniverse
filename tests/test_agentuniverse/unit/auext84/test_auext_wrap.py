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
        ("round 84: the quick brown fox jumps over the lazy dog", 4),
        ["round", "84:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 84: the quick brown fox jumps over the lazy dog", 8),
        ["round", "84: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 84: the quick brown fox jumps over the lazy dog", 12),
        ["round 84:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 84: the quick brown fox jumps over the lazy dog", 16),
        ["round 84: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 84: the quick brown fox jumps over the lazy dog", 24),
        ["round 84: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 84: the quick brown fox jumps over the lazy dog", 32),
        ["round 84: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 84: agentuniverse is a framework for multi agents", 4),
        ["round", "84:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 84: agentuniverse is a framework for multi agents", 8),
        ["round", "84:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 84: agentuniverse is a framework for multi agents", 12),
        ["round 84:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 84: agentuniverse is a framework for multi agents", 16),
        ["round 84:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 84: agentuniverse is a framework for multi agents", 24),
        ["round 84: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 84: agentuniverse is a framework for multi agents", 32),
        ["round 84: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 84: knowledge stored as vectors enables retrieval", 4),
        ["round", "84:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 84: knowledge stored as vectors enables retrieval", 8),
        ["round", "84:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 84: knowledge stored as vectors enables retrieval", 12),
        ["round 84:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 84: knowledge stored as vectors enables retrieval", 16),
        ["round 84:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 84: knowledge stored as vectors enables retrieval", 24),
        ["round 84: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 84: knowledge stored as vectors enables retrieval", 32),
        ["round 84: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 84: the processor reads the record then stops", 4),
        ["round", "84:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 84: the processor reads the record then stops", 8),
        ["round", "84: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 84: the processor reads the record then stops", 12),
        ["round 84:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 84: the processor reads the record then stops", 16),
        ["round 84: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 84: the processor reads the record then stops", 24),
        ["round 84: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 84: the processor reads the record then stops", 32),
        ["round 84: the processor reads", "the record then stops"],
    ),
    (
        ("round 84: a worker pulls the next task from the queue", 4),
        ["round", "84:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 84: a worker pulls the next task from the queue", 8),
        ["round", "84: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 84: a worker pulls the next task from the queue", 12),
        ["round 84: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 84: a worker pulls the next task from the queue", 16),
        ["round 84: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 84: a worker pulls the next task from the queue", 24),
        ["round 84: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 84: a worker pulls the next task from the queue", 32),
        ["round 84: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 84: signals travel through the network layer", 4),
        ["round", "84:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 84: signals travel through the network layer", 8),
        ["round", "84:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 84: signals travel through the network layer", 12),
        ["round 84:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 84: signals travel through the network layer", 16),
        ["round 84:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 84: signals travel through the network layer", 24),
        ["round 84: signals travel", "through the network", "layer"],
    ),
    (
        ("round 84: signals travel through the network layer", 32),
        ["round 84: signals travel through", "the network layer"],
    ),
    (
        ("round 84: the gateway routes each request by policy", 4),
        ["round", "84:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 84: the gateway routes each request by policy", 8),
        ["round", "84: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 84: the gateway routes each request by policy", 12),
        ["round 84:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 84: the gateway routes each request by policy", 16),
        ["round 84: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 84: the gateway routes each request by policy", 24),
        ["round 84: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 84: the gateway routes each request by policy", 32),
        ["round 84: the gateway routes", "each request by policy"],
    ),
    (
        ("round 84: memory grows until the buffer is full", 4),
        ["round", "84:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 84: memory grows until the buffer is full", 8),
        ["round", "84:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 84: memory grows until the buffer is full", 12),
        ["round 84:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 84: memory grows until the buffer is full", 16),
        ["round 84: memory", "grows until the", "buffer is full"],
    ),
    (("round 84: memory grows until the buffer is full", 24), ["round 84: memory grows", "until the buffer is full"]),
    (("round 84: memory grows until the buffer is full", 32), ["round 84: memory grows until the", "buffer is full"]),
    (
        ("round 84: the cluster mirrors every packet twice", 4),
        ["round", "84:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 84: the cluster mirrors every packet twice", 8),
        ["round", "84: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 84: the cluster mirrors every packet twice", 12),
        ["round 84:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 84: the cluster mirrors every packet twice", 16),
        ["round 84: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 84: the cluster mirrors every packet twice", 24),
        ["round 84: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 84: the cluster mirrors every packet twice", 32), ["round 84: the cluster mirrors", "every packet twice"]),
    (
        ("round 84: ranking uses tokens learned from the corpus", 4),
        ["round", "84:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 84: ranking uses tokens learned from the corpus", 8),
        ["round", "84:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 84: ranking uses tokens learned from the corpus", 12),
        ["round 84:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 84: ranking uses tokens learned from the corpus", 16),
        ["round 84:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 84: ranking uses tokens learned from the corpus", 24),
        ["round 84: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 84: ranking uses tokens learned from the corpus", 32),
        ["round 84: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 84: a long session ends when the candle dies", 4),
        ["round", "84:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 84: a long session ends when the candle dies", 8),
        ["round", "84: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 84: a long session ends when the candle dies", 12),
        ["round 84: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 84: a long session ends when the candle dies", 16),
        ["round 84: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 84: a long session ends when the candle dies", 24),
        ["round 84: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 84: a long session ends when the candle dies", 32),
        ["round 84: a long session ends", "when the candle dies"],
    ),
    (
        ("round 84: encode the prompt then map the result", 4),
        ["round", "84:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 84: encode the prompt then map the result", 8),
        ["round", "84:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 84: encode the prompt then map the result", 12),
        ["round 84:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 84: encode the prompt then map the result", 16),
        ["round 84: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 84: encode the prompt then map the result", 24),
        ["round 84: encode the", "prompt then map the", "result"],
    ),
    (("round 84: encode the prompt then map the result", 32), ["round 84: encode the prompt then", "map the result"]),
    (
        ("round 84: the kernel wakes the worker at dawn", 4),
        ["round", "84:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 84: the kernel wakes the worker at dawn", 8),
        ["round", "84: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 84: the kernel wakes the worker at dawn", 12),
        ["round 84:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 84: the kernel wakes the worker at dawn", 16), ["round 84: the", "kernel wakes the", "worker at dawn"]),
    (("round 84: the kernel wakes the worker at dawn", 24), ["round 84: the kernel", "wakes the worker at dawn"]),
    (("round 84: the kernel wakes the worker at dawn", 32), ["round 84: the kernel wakes the", "worker at dawn"]),
    (
        ("round 84: service latency drops after the patch", 4),
        ["round", "84:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 84: service latency drops after the patch", 8),
        ["round", "84:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 84: service latency drops after the patch", 12),
        ["round 84:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 84: service latency drops after the patch", 16),
        ["round 84:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 84: service latency drops after the patch", 24),
        ["round 84: service", "latency drops after the", "patch"],
    ),
    (("round 84: service latency drops after the patch", 32), ["round 84: service latency drops", "after the patch"]),
    (
        ("round 84: the library caches every vector it sees", 4),
        ["round", "84:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 84: the library caches every vector it sees", 8),
        ["round", "84: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 84: the library caches every vector it sees", 12),
        ["round 84:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 84: the library caches every vector it sees", 16),
        ["round 84: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 84: the library caches every vector it sees", 24),
        ["round 84: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 84: the library caches every vector it sees", 32),
        ["round 84: the library caches", "every vector it sees"],
    ),
    (
        ("round 84: agents argue then the debate resolves", 4),
        ["round", "84:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 84: agents argue then the debate resolves", 8),
        ["round", "84:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 84: agents argue then the debate resolves", 12),
        ["round 84:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 84: agents argue then the debate resolves", 16),
        ["round 84: agents", "argue then the", "debate resolves"],
    ),
    (("round 84: agents argue then the debate resolves", 24), ["round 84: agents argue", "then the debate resolves"]),
    (("round 84: agents argue then the debate resolves", 32), ["round 84: agents argue then the", "debate resolves"]),
    (
        ("round 84: the filter keeps only strong matches", 4),
        ["round", "84:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 84: the filter keeps only strong matches", 8),
        ["round", "84: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 84: the filter keeps only strong matches", 12),
        ["round 84:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 84: the filter keeps only strong matches", 16),
        ["round 84: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 84: the filter keeps only strong matches", 24), ["round 84: the filter", "keeps only strong", "matches"]),
    (("round 84: the filter keeps only strong matches", 32), ["round 84: the filter keeps only", "strong matches"]),
    (
        ("round 84: the model answers with a short reply", 4),
        ["round", "84:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 84: the model answers with a short reply", 8),
        ["round", "84: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 84: the model answers with a short reply", 12),
        ["round 84:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 84: the model answers with a short reply", 16),
        ["round 84: the", "model answers", "with a short", "reply"],
    ),
    (("round 84: the model answers with a short reply", 24), ["round 84: the model", "answers with a short", "reply"]),
    (("round 84: the model answers with a short reply", 32), ["round 84: the model answers with", "a short reply"]),
    (
        ("round 84: the recorder stores the reasoning trace", 4),
        ["round", "84:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 84: the recorder stores the reasoning trace", 8),
        ["round", "84: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 84: the recorder stores the reasoning trace", 12),
        ["round 84:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 84: the recorder stores the reasoning trace", 16),
        ["round 84: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 84: the recorder stores the reasoning trace", 24),
        ["round 84: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 84: the recorder stores the reasoning trace", 32),
        ["round 84: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 84: the angel watches the processor run", 4),
        ["round", "84:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 84: the angel watches the processor run", 8),
        ["round", "84: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 84: the angel watches the processor run", 12),
        ["round 84:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 84: the angel watches the processor run", 16), ["round 84: the", "angel watches", "the processor", "run"]),
    (("round 84: the angel watches the processor run", 24), ["round 84: the angel", "watches the processor", "run"]),
    (("round 84: the angel watches the processor run", 32), ["round 84: the angel watches the", "processor run"]),
    (
        ("round 84: angle of the vector decides the match", 4),
        ["round", "84:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 84: angle of the vector decides the match", 8),
        ["round", "84:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 84: angle of the vector decides the match", 12),
        ["round 84:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 84: angle of the vector decides the match", 16),
        ["round 84: angle", "of the vector", "decides the", "match"],
    ),
    (("round 84: angle of the vector decides the match", 24), ["round 84: angle of the", "vector decides the match"]),
    (("round 84: angle of the vector decides the match", 32), ["round 84: angle of the vector", "decides the match"]),
    (
        ("round 84: the candle burns twice as long at night", 4),
        ["round", "84:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 84: the candle burns twice as long at night", 8),
        ["round", "84: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 84: the candle burns twice as long at night", 12),
        ["round 84:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 84: the candle burns twice as long at night", 16),
        ["round 84: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 84: the candle burns twice as long at night", 24),
        ["round 84: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 84: the candle burns twice as long at night", 32),
        ["round 84: the candle burns twice", "as long at night"],
    ),
    (
        ("round 84: a mirror of the universe in one line", 4),
        ["round", "84:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 84: a mirror of the universe in one line", 8),
        ["round", "84: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 84: a mirror of the universe in one line", 12),
        ["round 84: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 84: a mirror of the universe in one line", 16),
        ["round 84: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 84: a mirror of the universe in one line", 24), ["round 84: a mirror of", "the universe in one line"]),
    (("round 84: a mirror of the universe in one line", 32), ["round 84: a mirror of the", "universe in one line"]),
    (
        ("round 84: the queue drains before the storm", 4),
        ["round", "84:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 84: the queue drains before the storm", 8),
        ["round", "84: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 84: the queue drains before the storm", 12), ["round 84:", "the queue", "drains", "before the", "storm"]),
    (("round 84: the queue drains before the storm", 16), ["round 84: the", "queue drains", "before the storm"]),
    (("round 84: the queue drains before the storm", 24), ["round 84: the queue", "drains before the storm"]),
    (("round 84: the queue drains before the storm", 32), ["round 84: the queue drains", "before the storm"]),
    (
        ("kitten84 sitting84 agent84 angle84 universe84 memory84", 6),
        ["kitten84", "sitting84", "agent84", "angle84", "universe84", "memory84"],
    ),
    (
        ("kitten84 sitting84 agent84 angle84 universe84 memory84", 10),
        ["kitten84", "sitting84", "agent84", "angle84", "universe84", "memory84"],
    ),
    (
        ("kitten84 sitting84 agent84 angle84 universe84 memory84", 18),
        ["kitten84 sitting84", "agent84 angle84", "universe84", "memory84"],
    ),
    (
        ("kitten84 sitting84 agent84 angle84 universe84 memory84", 28),
        ["kitten84 sitting84 agent84", "angle84 universe84 memory84"],
    ),
    (
        ("sitting84 agent84 angle84 universe84 memory84 stream84", 6),
        ["sitting84", "agent84", "angle84", "universe84", "memory84", "stream84"],
    ),
    (
        ("sitting84 agent84 angle84 universe84 memory84 stream84", 10),
        ["sitting84", "agent84", "angle84", "universe84", "memory84", "stream84"],
    ),
    (
        ("sitting84 agent84 angle84 universe84 memory84 stream84", 18),
        ["sitting84 agent84", "angle84 universe84", "memory84 stream84"],
    ),
    (
        ("sitting84 agent84 angle84 universe84 memory84 stream84", 28),
        ["sitting84 agent84 angle84", "universe84 memory84 stream84"],
    ),
    (
        ("agent84 angle84 universe84 memory84 stream84 context84", 6),
        ["agent84", "angle84", "universe84", "memory84", "stream84", "context84"],
    ),
    (
        ("agent84 angle84 universe84 memory84 stream84 context84", 10),
        ["agent84", "angle84", "universe84", "memory84", "stream84", "context84"],
    ),
    (
        ("agent84 angle84 universe84 memory84 stream84 context84", 18),
        ["agent84 angle84", "universe84", "memory84 stream84", "context84"],
    ),
    (
        ("agent84 angle84 universe84 memory84 stream84 context84", 28),
        ["agent84 angle84 universe84", "memory84 stream84 context84"],
    ),
    (
        ("angle84 universe84 memory84 stream84 context84 knowledge84", 6),
        ["angle84", "universe84", "memory84", "stream84", "context84", "knowledge84"],
    ),
    (
        ("angle84 universe84 memory84 stream84 context84 knowledge84", 10),
        ["angle84", "universe84", "memory84", "stream84", "context84", "knowledge84"],
    ),
    (
        ("angle84 universe84 memory84 stream84 context84 knowledge84", 18),
        ["angle84 universe84", "memory84 stream84", "context84", "knowledge84"],
    ),
    (
        ("angle84 universe84 memory84 stream84 context84 knowledge84", 28),
        ["angle84 universe84 memory84", "stream84 context84", "knowledge84"],
    ),
    (
        ("universe84 memory84 stream84 context84 knowledge84 vector84", 6),
        ["universe84", "memory84", "stream84", "context84", "knowledge84", "vector84"],
    ),
    (
        ("universe84 memory84 stream84 context84 knowledge84 vector84", 10),
        ["universe84", "memory84", "stream84", "context84", "knowledge84", "vector84"],
    ),
    (
        ("universe84 memory84 stream84 context84 knowledge84 vector84", 18),
        ["universe84", "memory84 stream84", "context84", "knowledge84", "vector84"],
    ),
    (
        ("universe84 memory84 stream84 context84 knowledge84 vector84", 28),
        ["universe84 memory84 stream84", "context84 knowledge84", "vector84"],
    ),
    (
        ("memory84 stream84 context84 knowledge84 vector84 processor84", 6),
        ["memory84", "stream84", "context84", "knowledge84", "vector84", "processor84"],
    ),
    (
        ("memory84 stream84 context84 knowledge84 vector84 processor84", 10),
        ["memory84", "stream84", "context84", "knowledge84", "vector84", "processor84"],
    ),
    (
        ("memory84 stream84 context84 knowledge84 vector84 processor84", 18),
        ["memory84 stream84", "context84", "knowledge84", "vector84", "processor84"],
    ),
    (
        ("memory84 stream84 context84 knowledge84 vector84 processor84", 28),
        ["memory84 stream84 context84", "knowledge84 vector84", "processor84"],
    ),
    (
        ("stream84 context84 knowledge84 vector84 processor84 reasoning84", 6),
        ["stream84", "context84", "knowledge84", "vector84", "processor84", "reasoning84"],
    ),
    (
        ("stream84 context84 knowledge84 vector84 processor84 reasoning84", 10),
        ["stream84", "context84", "knowledge84", "vector84", "processor84", "reasoning84"],
    ),
    (
        ("stream84 context84 knowledge84 vector84 processor84 reasoning84", 18),
        ["stream84 context84", "knowledge84", "vector84", "processor84", "reasoning84"],
    ),
    (
        ("stream84 context84 knowledge84 vector84 processor84 reasoning84", 28),
        ["stream84 context84", "knowledge84 vector84", "processor84 reasoning84"],
    ),
    (
        ("context84 knowledge84 vector84 processor84 reasoning84 machine84", 6),
        ["context84", "knowledge84", "vector84", "processor84", "reasoning84", "machine84"],
    ),
    (
        ("context84 knowledge84 vector84 processor84 reasoning84 machine84", 10),
        ["context84", "knowledge84", "vector84", "processor84", "reasoning84", "machine84"],
    ),
    (
        ("context84 knowledge84 vector84 processor84 reasoning84 machine84", 18),
        ["context84", "knowledge84", "vector84", "processor84", "reasoning84", "machine84"],
    ),
    (
        ("context84 knowledge84 vector84 processor84 reasoning84 machine84", 28),
        ["context84 knowledge84", "vector84 processor84", "reasoning84 machine84"],
    ),
    (
        ("knowledge84 vector84 processor84 reasoning84 machine84 learning84", 6),
        ["knowledge84", "vector84", "processor84", "reasoning84", "machine84", "learning84"],
    ),
    (
        ("knowledge84 vector84 processor84 reasoning84 machine84 learning84", 10),
        ["knowledge84", "vector84", "processor84", "reasoning84", "machine84", "learning84"],
    ),
    (
        ("knowledge84 vector84 processor84 reasoning84 machine84 learning84", 18),
        ["knowledge84", "vector84", "processor84", "reasoning84", "machine84", "learning84"],
    ),
    (
        ("knowledge84 vector84 processor84 reasoning84 machine84 learning84", 28),
        ["knowledge84 vector84", "processor84 reasoning84", "machine84 learning84"],
    ),
    (
        ("vector84 processor84 reasoning84 machine84 learning84 model84", 6),
        ["vector84", "processor84", "reasoning84", "machine84", "learning84", "model84"],
    ),
    (
        ("vector84 processor84 reasoning84 machine84 learning84 model84", 10),
        ["vector84", "processor84", "reasoning84", "machine84", "learning84", "model84"],
    ),
    (
        ("vector84 processor84 reasoning84 machine84 learning84 model84", 18),
        ["vector84", "processor84", "reasoning84", "machine84", "learning84 model84"],
    ),
    (
        ("vector84 processor84 reasoning84 machine84 learning84 model84", 28),
        ["vector84 processor84", "reasoning84 machine84", "learning84 model84"],
    ),
    (
        ("processor84 reasoning84 machine84 learning84 model84 token84", 6),
        ["processor84", "reasoning84", "machine84", "learning84", "model84", "token84"],
    ),
    (
        ("processor84 reasoning84 machine84 learning84 model84 token84", 10),
        ["processor84", "reasoning84", "machine84", "learning84", "model84", "token84"],
    ),
    (
        ("processor84 reasoning84 machine84 learning84 model84 token84", 18),
        ["processor84", "reasoning84", "machine84", "learning84 model84", "token84"],
    ),
    (
        ("processor84 reasoning84 machine84 learning84 model84 token84", 28),
        ["processor84 reasoning84", "machine84 learning84 model84", "token84"],
    ),
    (
        ("reasoning84 machine84 learning84 model84 token84 prompt84", 6),
        ["reasoning84", "machine84", "learning84", "model84", "token84", "prompt84"],
    ),
    (
        ("reasoning84 machine84 learning84 model84 token84 prompt84", 10),
        ["reasoning84", "machine84", "learning84", "model84", "token84", "prompt84"],
    ),
    (
        ("reasoning84 machine84 learning84 model84 token84 prompt84", 18),
        ["reasoning84", "machine84", "learning84 model84", "token84 prompt84"],
    ),
    (
        ("reasoning84 machine84 learning84 model84 token84 prompt84", 28),
        ["reasoning84 machine84", "learning84 model84 token84", "prompt84"],
    ),
    (
        ("machine84 learning84 model84 token84 prompt84 session84", 6),
        ["machine84", "learning84", "model84", "token84", "prompt84", "session84"],
    ),
    (
        ("machine84 learning84 model84 token84 prompt84 session84", 10),
        ["machine84", "learning84", "model84", "token84", "prompt84", "session84"],
    ),
    (
        ("machine84 learning84 model84 token84 prompt84 session84", 18),
        ["machine84", "learning84 model84", "token84 prompt84", "session84"],
    ),
    (
        ("machine84 learning84 model84 token84 prompt84 session84", 28),
        ["machine84 learning84 model84", "token84 prompt84 session84"],
    ),
    (
        ("learning84 model84 token84 prompt84 session84 library84", 6),
        ["learning84", "model84", "token84", "prompt84", "session84", "library84"],
    ),
    (
        ("learning84 model84 token84 prompt84 session84 library84", 10),
        ["learning84", "model84", "token84", "prompt84", "session84", "library84"],
    ),
    (
        ("learning84 model84 token84 prompt84 session84 library84", 18),
        ["learning84 model84", "token84 prompt84", "session84", "library84"],
    ),
    (
        ("learning84 model84 token84 prompt84 session84 library84", 28),
        ["learning84 model84 token84", "prompt84 session84 library84"],
    ),
    (
        ("model84 token84 prompt84 session84 library84 service84", 6),
        ["model84", "token84", "prompt84", "session84", "library84", "service84"],
    ),
    (
        ("model84 token84 prompt84 session84 library84 service84", 10),
        ["model84", "token84", "prompt84", "session84", "library84", "service84"],
    ),
    (
        ("model84 token84 prompt84 session84 library84 service84", 18),
        ["model84 token84", "prompt84 session84", "library84", "service84"],
    ),
    (
        ("model84 token84 prompt84 session84 library84 service84", 28),
        ["model84 token84 prompt84", "session84 library84", "service84"],
    ),
    (
        ("token84 prompt84 session84 library84 service84 gateway84", 6),
        ["token84", "prompt84", "session84", "library84", "service84", "gateway84"],
    ),
    (
        ("token84 prompt84 session84 library84 service84 gateway84", 10),
        ["token84", "prompt84", "session84", "library84", "service84", "gateway84"],
    ),
    (
        ("token84 prompt84 session84 library84 service84 gateway84", 18),
        ["token84 prompt84", "session84", "library84", "service84", "gateway84"],
    ),
    (
        ("token84 prompt84 session84 library84 service84 gateway84", 28),
        ["token84 prompt84 session84", "library84 service84", "gateway84"],
    ),
    (
        ("prompt84 session84 library84 service84 gateway84 storage84", 6),
        ["prompt84", "session84", "library84", "service84", "gateway84", "storage84"],
    ),
    (
        ("prompt84 session84 library84 service84 gateway84 storage84", 10),
        ["prompt84", "session84", "library84", "service84", "gateway84", "storage84"],
    ),
    (
        ("prompt84 session84 library84 service84 gateway84 storage84", 18),
        ["prompt84 session84", "library84", "service84", "gateway84", "storage84"],
    ),
    (
        ("prompt84 session84 library84 service84 gateway84 storage84", 28),
        ["prompt84 session84 library84", "service84 gateway84", "storage84"],
    ),
    (
        ("session84 library84 service84 gateway84 storage84 network84", 6),
        ["session84", "library84", "service84", "gateway84", "storage84", "network84"],
    ),
    (
        ("session84 library84 service84 gateway84 storage84 network84", 10),
        ["session84", "library84", "service84", "gateway84", "storage84", "network84"],
    ),
    (
        ("session84 library84 service84 gateway84 storage84 network84", 18),
        ["session84", "library84", "service84", "gateway84", "storage84", "network84"],
    ),
    (
        ("session84 library84 service84 gateway84 storage84 network84", 28),
        ["session84 library84", "service84 gateway84", "storage84 network84"],
    ),
    (
        ("library84 service84 gateway84 storage84 network84 latency84", 6),
        ["library84", "service84", "gateway84", "storage84", "network84", "latency84"],
    ),
    (
        ("library84 service84 gateway84 storage84 network84 latency84", 10),
        ["library84", "service84", "gateway84", "storage84", "network84", "latency84"],
    ),
    (
        ("library84 service84 gateway84 storage84 network84 latency84", 18),
        ["library84", "service84", "gateway84", "storage84", "network84", "latency84"],
    ),
    (
        ("library84 service84 gateway84 storage84 network84 latency84", 28),
        ["library84 service84", "gateway84 storage84", "network84 latency84"],
    ),
    (
        ("service84 gateway84 storage84 network84 latency84 buffer84", 6),
        ["service84", "gateway84", "storage84", "network84", "latency84", "buffer84"],
    ),
    (
        ("service84 gateway84 storage84 network84 latency84 buffer84", 10),
        ["service84", "gateway84", "storage84", "network84", "latency84", "buffer84"],
    ),
    (
        ("service84 gateway84 storage84 network84 latency84 buffer84", 18),
        ["service84", "gateway84", "storage84", "network84", "latency84 buffer84"],
    ),
    (
        ("service84 gateway84 storage84 network84 latency84 buffer84", 28),
        ["service84 gateway84", "storage84 network84", "latency84 buffer84"],
    ),
    (
        ("gateway84 storage84 network84 latency84 buffer84 queue84", 6),
        ["gateway84", "storage84", "network84", "latency84", "buffer84", "queue84"],
    ),
    (
        ("gateway84 storage84 network84 latency84 buffer84 queue84", 10),
        ["gateway84", "storage84", "network84", "latency84", "buffer84", "queue84"],
    ),
    (
        ("gateway84 storage84 network84 latency84 buffer84 queue84", 18),
        ["gateway84", "storage84", "network84", "latency84 buffer84", "queue84"],
    ),
    (
        ("gateway84 storage84 network84 latency84 buffer84 queue84", 28),
        ["gateway84 storage84", "network84 latency84 buffer84", "queue84"],
    ),
    (
        ("storage84 network84 latency84 buffer84 queue84 worker84", 6),
        ["storage84", "network84", "latency84", "buffer84", "queue84", "worker84"],
    ),
    (
        ("storage84 network84 latency84 buffer84 queue84 worker84", 10),
        ["storage84", "network84", "latency84", "buffer84", "queue84", "worker84"],
    ),
    (
        ("storage84 network84 latency84 buffer84 queue84 worker84", 18),
        ["storage84", "network84", "latency84 buffer84", "queue84 worker84"],
    ),
    (
        ("storage84 network84 latency84 buffer84 queue84 worker84", 28),
        ["storage84 network84", "latency84 buffer84 queue84", "worker84"],
    ),
    (
        ("network84 latency84 buffer84 queue84 worker84 kernel84", 6),
        ["network84", "latency84", "buffer84", "queue84", "worker84", "kernel84"],
    ),
    (
        ("network84 latency84 buffer84 queue84 worker84 kernel84", 10),
        ["network84", "latency84", "buffer84", "queue84", "worker84", "kernel84"],
    ),
    (
        ("network84 latency84 buffer84 queue84 worker84 kernel84", 18),
        ["network84", "latency84 buffer84", "queue84 worker84", "kernel84"],
    ),
    (
        ("network84 latency84 buffer84 queue84 worker84 kernel84", 28),
        ["network84 latency84 buffer84", "queue84 worker84 kernel84"],
    ),
    (
        ("latency84 buffer84 queue84 worker84 kernel84 signal84", 6),
        ["latency84", "buffer84", "queue84", "worker84", "kernel84", "signal84"],
    ),
    (
        ("latency84 buffer84 queue84 worker84 kernel84 signal84", 10),
        ["latency84", "buffer84", "queue84", "worker84", "kernel84", "signal84"],
    ),
    (
        ("latency84 buffer84 queue84 worker84 kernel84 signal84", 18),
        ["latency84 buffer84", "queue84 worker84", "kernel84 signal84"],
    ),
    (
        ("latency84 buffer84 queue84 worker84 kernel84 signal84", 28),
        ["latency84 buffer84 queue84", "worker84 kernel84 signal84"],
    ),
    (
        ("buffer84 queue84 worker84 kernel84 signal84 packet84", 6),
        ["buffer84", "queue84", "worker84", "kernel84", "signal84", "packet84"],
    ),
    (
        ("buffer84 queue84 worker84 kernel84 signal84 packet84", 10),
        ["buffer84", "queue84", "worker84", "kernel84", "signal84", "packet84"],
    ),
    (
        ("buffer84 queue84 worker84 kernel84 signal84 packet84", 18),
        ["buffer84 queue84", "worker84 kernel84", "signal84 packet84"],
    ),
    (
        ("buffer84 queue84 worker84 kernel84 signal84 packet84", 28),
        ["buffer84 queue84 worker84", "kernel84 signal84 packet84"],
    ),
    (
        ("queue84 worker84 kernel84 signal84 packet84 router84", 6),
        ["queue84", "worker84", "kernel84", "signal84", "packet84", "router84"],
    ),
    (
        ("queue84 worker84 kernel84 signal84 packet84 router84", 10),
        ["queue84", "worker84", "kernel84", "signal84", "packet84", "router84"],
    ),
    (
        ("queue84 worker84 kernel84 signal84 packet84 router84", 18),
        ["queue84 worker84", "kernel84 signal84", "packet84 router84"],
    ),
    (
        ("queue84 worker84 kernel84 signal84 packet84 router84", 28),
        ["queue84 worker84 kernel84", "signal84 packet84 router84"],
    ),
    (
        ("worker84 kernel84 signal84 packet84 router84 cluster84", 6),
        ["worker84", "kernel84", "signal84", "packet84", "router84", "cluster84"],
    ),
    (
        ("worker84 kernel84 signal84 packet84 router84 cluster84", 10),
        ["worker84", "kernel84", "signal84", "packet84", "router84", "cluster84"],
    ),
    (
        ("worker84 kernel84 signal84 packet84 router84 cluster84", 18),
        ["worker84 kernel84", "signal84 packet84", "router84 cluster84"],
    ),
    (
        ("worker84 kernel84 signal84 packet84 router84 cluster84", 28),
        ["worker84 kernel84 signal84", "packet84 router84 cluster84"],
    ),
    (
        ("kernel84 signal84 packet84 router84 cluster84 mirror84", 6),
        ["kernel84", "signal84", "packet84", "router84", "cluster84", "mirror84"],
    ),
    (
        ("kernel84 signal84 packet84 router84 cluster84 mirror84", 10),
        ["kernel84", "signal84", "packet84", "router84", "cluster84", "mirror84"],
    ),
    (
        ("kernel84 signal84 packet84 router84 cluster84 mirror84", 18),
        ["kernel84 signal84", "packet84 router84", "cluster84 mirror84"],
    ),
    (
        ("kernel84 signal84 packet84 router84 cluster84 mirror84", 28),
        ["kernel84 signal84 packet84", "router84 cluster84 mirror84"],
    ),
    (
        ("signal84 packet84 router84 cluster84 mirror84 filter84", 6),
        ["signal84", "packet84", "router84", "cluster84", "mirror84", "filter84"],
    ),
    (
        ("signal84 packet84 router84 cluster84 mirror84 filter84", 10),
        ["signal84", "packet84", "router84", "cluster84", "mirror84", "filter84"],
    ),
    (
        ("signal84 packet84 router84 cluster84 mirror84 filter84", 18),
        ["signal84 packet84", "router84 cluster84", "mirror84 filter84"],
    ),
    (
        ("signal84 packet84 router84 cluster84 mirror84 filter84", 28),
        ["signal84 packet84 router84", "cluster84 mirror84 filter84"],
    ),
    (
        ("packet84 router84 cluster84 mirror84 filter84 ranking84", 6),
        ["packet84", "router84", "cluster84", "mirror84", "filter84", "ranking84"],
    ),
    (
        ("packet84 router84 cluster84 mirror84 filter84 ranking84", 10),
        ["packet84", "router84", "cluster84", "mirror84", "filter84", "ranking84"],
    ),
    (
        ("packet84 router84 cluster84 mirror84 filter84 ranking84", 18),
        ["packet84 router84", "cluster84 mirror84", "filter84 ranking84"],
    ),
    (
        ("packet84 router84 cluster84 mirror84 filter84 ranking84", 28),
        ["packet84 router84 cluster84", "mirror84 filter84 ranking84"],
    ),
    (
        ("router84 cluster84 mirror84 filter84 ranking84 encoding84", 6),
        ["router84", "cluster84", "mirror84", "filter84", "ranking84", "encoding84"],
    ),
    (
        ("router84 cluster84 mirror84 filter84 ranking84 encoding84", 10),
        ["router84", "cluster84", "mirror84", "filter84", "ranking84", "encoding84"],
    ),
    (
        ("router84 cluster84 mirror84 filter84 ranking84 encoding84", 18),
        ["router84 cluster84", "mirror84 filter84", "ranking84", "encoding84"],
    ),
    (
        ("router84 cluster84 mirror84 filter84 ranking84 encoding84", 28),
        ["router84 cluster84 mirror84", "filter84 ranking84", "encoding84"],
    ),
    (
        ("cluster84 mirror84 filter84 ranking84 encoding84 mapping84", 6),
        ["cluster84", "mirror84", "filter84", "ranking84", "encoding84", "mapping84"],
    ),
    (
        ("cluster84 mirror84 filter84 ranking84 encoding84 mapping84", 10),
        ["cluster84", "mirror84", "filter84", "ranking84", "encoding84", "mapping84"],
    ),
    (
        ("cluster84 mirror84 filter84 ranking84 encoding84 mapping84", 18),
        ["cluster84 mirror84", "filter84 ranking84", "encoding84", "mapping84"],
    ),
    (
        ("cluster84 mirror84 filter84 ranking84 encoding84 mapping84", 28),
        ["cluster84 mirror84 filter84", "ranking84 encoding84", "mapping84"],
    ),
    (
        ("mirror84 filter84 ranking84 encoding84 mapping84 record84", 6),
        ["mirror84", "filter84", "ranking84", "encoding84", "mapping84", "record84"],
    ),
    (
        ("mirror84 filter84 ranking84 encoding84 mapping84 record84", 10),
        ["mirror84", "filter84", "ranking84", "encoding84", "mapping84", "record84"],
    ),
    (
        ("mirror84 filter84 ranking84 encoding84 mapping84 record84", 18),
        ["mirror84 filter84", "ranking84", "encoding84", "mapping84 record84"],
    ),
    (
        ("mirror84 filter84 ranking84 encoding84 mapping84 record84", 28),
        ["mirror84 filter84 ranking84", "encoding84 mapping84", "record84"],
    ),
    (
        ("filter84 ranking84 encoding84 mapping84 record84 candle84", 6),
        ["filter84", "ranking84", "encoding84", "mapping84", "record84", "candle84"],
    ),
    (
        ("filter84 ranking84 encoding84 mapping84 record84 candle84", 10),
        ["filter84", "ranking84", "encoding84", "mapping84", "record84", "candle84"],
    ),
    (
        ("filter84 ranking84 encoding84 mapping84 record84 candle84", 18),
        ["filter84 ranking84", "encoding84", "mapping84 record84", "candle84"],
    ),
    (
        ("filter84 ranking84 encoding84 mapping84 record84 candle84", 28),
        ["filter84 ranking84", "encoding84 mapping84", "record84 candle84"],
    ),
    (
        ("ranking84 encoding84 mapping84 record84 candle84 thread84", 6),
        ["ranking84", "encoding84", "mapping84", "record84", "candle84", "thread84"],
    ),
    (
        ("ranking84 encoding84 mapping84 record84 candle84 thread84", 10),
        ["ranking84", "encoding84", "mapping84", "record84", "candle84", "thread84"],
    ),
    (
        ("ranking84 encoding84 mapping84 record84 candle84 thread84", 18),
        ["ranking84", "encoding84", "mapping84 record84", "candle84 thread84"],
    ),
    (
        ("ranking84 encoding84 mapping84 record84 candle84 thread84", 28),
        ["ranking84 encoding84", "mapping84 record84 candle84", "thread84"],
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
