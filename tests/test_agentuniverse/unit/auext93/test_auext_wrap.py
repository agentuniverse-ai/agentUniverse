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
        ("round 93: the quick brown fox jumps over the lazy dog", 4),
        ["round", "93:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 93: the quick brown fox jumps over the lazy dog", 8),
        ["round", "93: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 93: the quick brown fox jumps over the lazy dog", 12),
        ["round 93:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 93: the quick brown fox jumps over the lazy dog", 16),
        ["round 93: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 93: the quick brown fox jumps over the lazy dog", 24),
        ["round 93: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 93: the quick brown fox jumps over the lazy dog", 32),
        ["round 93: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 93: agentuniverse is a framework for multi agents", 4),
        ["round", "93:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 93: agentuniverse is a framework for multi agents", 8),
        ["round", "93:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 93: agentuniverse is a framework for multi agents", 12),
        ["round 93:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 93: agentuniverse is a framework for multi agents", 16),
        ["round 93:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 93: agentuniverse is a framework for multi agents", 24),
        ["round 93: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 93: agentuniverse is a framework for multi agents", 32),
        ["round 93: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 93: knowledge stored as vectors enables retrieval", 4),
        ["round", "93:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 93: knowledge stored as vectors enables retrieval", 8),
        ["round", "93:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 93: knowledge stored as vectors enables retrieval", 12),
        ["round 93:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 93: knowledge stored as vectors enables retrieval", 16),
        ["round 93:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 93: knowledge stored as vectors enables retrieval", 24),
        ["round 93: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 93: knowledge stored as vectors enables retrieval", 32),
        ["round 93: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 93: the processor reads the record then stops", 4),
        ["round", "93:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 93: the processor reads the record then stops", 8),
        ["round", "93: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 93: the processor reads the record then stops", 12),
        ["round 93:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 93: the processor reads the record then stops", 16),
        ["round 93: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 93: the processor reads the record then stops", 24),
        ["round 93: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 93: the processor reads the record then stops", 32),
        ["round 93: the processor reads", "the record then stops"],
    ),
    (
        ("round 93: a worker pulls the next task from the queue", 4),
        ["round", "93:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 93: a worker pulls the next task from the queue", 8),
        ["round", "93: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 93: a worker pulls the next task from the queue", 12),
        ["round 93: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 93: a worker pulls the next task from the queue", 16),
        ["round 93: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 93: a worker pulls the next task from the queue", 24),
        ["round 93: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 93: a worker pulls the next task from the queue", 32),
        ["round 93: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 93: signals travel through the network layer", 4),
        ["round", "93:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 93: signals travel through the network layer", 8),
        ["round", "93:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 93: signals travel through the network layer", 12),
        ["round 93:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 93: signals travel through the network layer", 16),
        ["round 93:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 93: signals travel through the network layer", 24),
        ["round 93: signals travel", "through the network", "layer"],
    ),
    (
        ("round 93: signals travel through the network layer", 32),
        ["round 93: signals travel through", "the network layer"],
    ),
    (
        ("round 93: the gateway routes each request by policy", 4),
        ["round", "93:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 93: the gateway routes each request by policy", 8),
        ["round", "93: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 93: the gateway routes each request by policy", 12),
        ["round 93:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 93: the gateway routes each request by policy", 16),
        ["round 93: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 93: the gateway routes each request by policy", 24),
        ["round 93: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 93: the gateway routes each request by policy", 32),
        ["round 93: the gateway routes", "each request by policy"],
    ),
    (
        ("round 93: memory grows until the buffer is full", 4),
        ["round", "93:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 93: memory grows until the buffer is full", 8),
        ["round", "93:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 93: memory grows until the buffer is full", 12),
        ["round 93:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 93: memory grows until the buffer is full", 16),
        ["round 93: memory", "grows until the", "buffer is full"],
    ),
    (("round 93: memory grows until the buffer is full", 24), ["round 93: memory grows", "until the buffer is full"]),
    (("round 93: memory grows until the buffer is full", 32), ["round 93: memory grows until the", "buffer is full"]),
    (
        ("round 93: the cluster mirrors every packet twice", 4),
        ["round", "93:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 93: the cluster mirrors every packet twice", 8),
        ["round", "93: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 93: the cluster mirrors every packet twice", 12),
        ["round 93:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 93: the cluster mirrors every packet twice", 16),
        ["round 93: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 93: the cluster mirrors every packet twice", 24),
        ["round 93: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 93: the cluster mirrors every packet twice", 32), ["round 93: the cluster mirrors", "every packet twice"]),
    (
        ("round 93: ranking uses tokens learned from the corpus", 4),
        ["round", "93:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 93: ranking uses tokens learned from the corpus", 8),
        ["round", "93:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 93: ranking uses tokens learned from the corpus", 12),
        ["round 93:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 93: ranking uses tokens learned from the corpus", 16),
        ["round 93:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 93: ranking uses tokens learned from the corpus", 24),
        ["round 93: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 93: ranking uses tokens learned from the corpus", 32),
        ["round 93: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 93: a long session ends when the candle dies", 4),
        ["round", "93:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 93: a long session ends when the candle dies", 8),
        ["round", "93: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 93: a long session ends when the candle dies", 12),
        ["round 93: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 93: a long session ends when the candle dies", 16),
        ["round 93: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 93: a long session ends when the candle dies", 24),
        ["round 93: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 93: a long session ends when the candle dies", 32),
        ["round 93: a long session ends", "when the candle dies"],
    ),
    (
        ("round 93: encode the prompt then map the result", 4),
        ["round", "93:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 93: encode the prompt then map the result", 8),
        ["round", "93:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 93: encode the prompt then map the result", 12),
        ["round 93:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 93: encode the prompt then map the result", 16),
        ["round 93: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 93: encode the prompt then map the result", 24),
        ["round 93: encode the", "prompt then map the", "result"],
    ),
    (("round 93: encode the prompt then map the result", 32), ["round 93: encode the prompt then", "map the result"]),
    (
        ("round 93: the kernel wakes the worker at dawn", 4),
        ["round", "93:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 93: the kernel wakes the worker at dawn", 8),
        ["round", "93: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 93: the kernel wakes the worker at dawn", 12),
        ["round 93:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 93: the kernel wakes the worker at dawn", 16), ["round 93: the", "kernel wakes the", "worker at dawn"]),
    (("round 93: the kernel wakes the worker at dawn", 24), ["round 93: the kernel", "wakes the worker at dawn"]),
    (("round 93: the kernel wakes the worker at dawn", 32), ["round 93: the kernel wakes the", "worker at dawn"]),
    (
        ("round 93: service latency drops after the patch", 4),
        ["round", "93:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 93: service latency drops after the patch", 8),
        ["round", "93:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 93: service latency drops after the patch", 12),
        ["round 93:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 93: service latency drops after the patch", 16),
        ["round 93:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 93: service latency drops after the patch", 24),
        ["round 93: service", "latency drops after the", "patch"],
    ),
    (("round 93: service latency drops after the patch", 32), ["round 93: service latency drops", "after the patch"]),
    (
        ("round 93: the library caches every vector it sees", 4),
        ["round", "93:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 93: the library caches every vector it sees", 8),
        ["round", "93: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 93: the library caches every vector it sees", 12),
        ["round 93:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 93: the library caches every vector it sees", 16),
        ["round 93: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 93: the library caches every vector it sees", 24),
        ["round 93: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 93: the library caches every vector it sees", 32),
        ["round 93: the library caches", "every vector it sees"],
    ),
    (
        ("round 93: agents argue then the debate resolves", 4),
        ["round", "93:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 93: agents argue then the debate resolves", 8),
        ["round", "93:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 93: agents argue then the debate resolves", 12),
        ["round 93:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 93: agents argue then the debate resolves", 16),
        ["round 93: agents", "argue then the", "debate resolves"],
    ),
    (("round 93: agents argue then the debate resolves", 24), ["round 93: agents argue", "then the debate resolves"]),
    (("round 93: agents argue then the debate resolves", 32), ["round 93: agents argue then the", "debate resolves"]),
    (
        ("round 93: the filter keeps only strong matches", 4),
        ["round", "93:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 93: the filter keeps only strong matches", 8),
        ["round", "93: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 93: the filter keeps only strong matches", 12),
        ["round 93:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 93: the filter keeps only strong matches", 16),
        ["round 93: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 93: the filter keeps only strong matches", 24), ["round 93: the filter", "keeps only strong", "matches"]),
    (("round 93: the filter keeps only strong matches", 32), ["round 93: the filter keeps only", "strong matches"]),
    (
        ("round 93: the model answers with a short reply", 4),
        ["round", "93:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 93: the model answers with a short reply", 8),
        ["round", "93: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 93: the model answers with a short reply", 12),
        ["round 93:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 93: the model answers with a short reply", 16),
        ["round 93: the", "model answers", "with a short", "reply"],
    ),
    (("round 93: the model answers with a short reply", 24), ["round 93: the model", "answers with a short", "reply"]),
    (("round 93: the model answers with a short reply", 32), ["round 93: the model answers with", "a short reply"]),
    (
        ("round 93: the recorder stores the reasoning trace", 4),
        ["round", "93:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 93: the recorder stores the reasoning trace", 8),
        ["round", "93: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 93: the recorder stores the reasoning trace", 12),
        ["round 93:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 93: the recorder stores the reasoning trace", 16),
        ["round 93: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 93: the recorder stores the reasoning trace", 24),
        ["round 93: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 93: the recorder stores the reasoning trace", 32),
        ["round 93: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 93: the angel watches the processor run", 4),
        ["round", "93:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 93: the angel watches the processor run", 8),
        ["round", "93: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 93: the angel watches the processor run", 12),
        ["round 93:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 93: the angel watches the processor run", 16), ["round 93: the", "angel watches", "the processor", "run"]),
    (("round 93: the angel watches the processor run", 24), ["round 93: the angel", "watches the processor", "run"]),
    (("round 93: the angel watches the processor run", 32), ["round 93: the angel watches the", "processor run"]),
    (
        ("round 93: angle of the vector decides the match", 4),
        ["round", "93:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 93: angle of the vector decides the match", 8),
        ["round", "93:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 93: angle of the vector decides the match", 12),
        ["round 93:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 93: angle of the vector decides the match", 16),
        ["round 93: angle", "of the vector", "decides the", "match"],
    ),
    (("round 93: angle of the vector decides the match", 24), ["round 93: angle of the", "vector decides the match"]),
    (("round 93: angle of the vector decides the match", 32), ["round 93: angle of the vector", "decides the match"]),
    (
        ("round 93: the candle burns twice as long at night", 4),
        ["round", "93:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 93: the candle burns twice as long at night", 8),
        ["round", "93: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 93: the candle burns twice as long at night", 12),
        ["round 93:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 93: the candle burns twice as long at night", 16),
        ["round 93: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 93: the candle burns twice as long at night", 24),
        ["round 93: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 93: the candle burns twice as long at night", 32),
        ["round 93: the candle burns twice", "as long at night"],
    ),
    (
        ("round 93: a mirror of the universe in one line", 4),
        ["round", "93:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 93: a mirror of the universe in one line", 8),
        ["round", "93: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 93: a mirror of the universe in one line", 12),
        ["round 93: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 93: a mirror of the universe in one line", 16),
        ["round 93: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 93: a mirror of the universe in one line", 24), ["round 93: a mirror of", "the universe in one line"]),
    (("round 93: a mirror of the universe in one line", 32), ["round 93: a mirror of the", "universe in one line"]),
    (
        ("round 93: the queue drains before the storm", 4),
        ["round", "93:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 93: the queue drains before the storm", 8),
        ["round", "93: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 93: the queue drains before the storm", 12), ["round 93:", "the queue", "drains", "before the", "storm"]),
    (("round 93: the queue drains before the storm", 16), ["round 93: the", "queue drains", "before the storm"]),
    (("round 93: the queue drains before the storm", 24), ["round 93: the queue", "drains before the storm"]),
    (("round 93: the queue drains before the storm", 32), ["round 93: the queue drains", "before the storm"]),
    (
        ("kitten93 sitting93 agent93 angle93 universe93 memory93", 6),
        ["kitten93", "sitting93", "agent93", "angle93", "universe93", "memory93"],
    ),
    (
        ("kitten93 sitting93 agent93 angle93 universe93 memory93", 10),
        ["kitten93", "sitting93", "agent93", "angle93", "universe93", "memory93"],
    ),
    (
        ("kitten93 sitting93 agent93 angle93 universe93 memory93", 18),
        ["kitten93 sitting93", "agent93 angle93", "universe93", "memory93"],
    ),
    (
        ("kitten93 sitting93 agent93 angle93 universe93 memory93", 28),
        ["kitten93 sitting93 agent93", "angle93 universe93 memory93"],
    ),
    (
        ("sitting93 agent93 angle93 universe93 memory93 stream93", 6),
        ["sitting93", "agent93", "angle93", "universe93", "memory93", "stream93"],
    ),
    (
        ("sitting93 agent93 angle93 universe93 memory93 stream93", 10),
        ["sitting93", "agent93", "angle93", "universe93", "memory93", "stream93"],
    ),
    (
        ("sitting93 agent93 angle93 universe93 memory93 stream93", 18),
        ["sitting93 agent93", "angle93 universe93", "memory93 stream93"],
    ),
    (
        ("sitting93 agent93 angle93 universe93 memory93 stream93", 28),
        ["sitting93 agent93 angle93", "universe93 memory93 stream93"],
    ),
    (
        ("agent93 angle93 universe93 memory93 stream93 context93", 6),
        ["agent93", "angle93", "universe93", "memory93", "stream93", "context93"],
    ),
    (
        ("agent93 angle93 universe93 memory93 stream93 context93", 10),
        ["agent93", "angle93", "universe93", "memory93", "stream93", "context93"],
    ),
    (
        ("agent93 angle93 universe93 memory93 stream93 context93", 18),
        ["agent93 angle93", "universe93", "memory93 stream93", "context93"],
    ),
    (
        ("agent93 angle93 universe93 memory93 stream93 context93", 28),
        ["agent93 angle93 universe93", "memory93 stream93 context93"],
    ),
    (
        ("angle93 universe93 memory93 stream93 context93 knowledge93", 6),
        ["angle93", "universe93", "memory93", "stream93", "context93", "knowledge93"],
    ),
    (
        ("angle93 universe93 memory93 stream93 context93 knowledge93", 10),
        ["angle93", "universe93", "memory93", "stream93", "context93", "knowledge93"],
    ),
    (
        ("angle93 universe93 memory93 stream93 context93 knowledge93", 18),
        ["angle93 universe93", "memory93 stream93", "context93", "knowledge93"],
    ),
    (
        ("angle93 universe93 memory93 stream93 context93 knowledge93", 28),
        ["angle93 universe93 memory93", "stream93 context93", "knowledge93"],
    ),
    (
        ("universe93 memory93 stream93 context93 knowledge93 vector93", 6),
        ["universe93", "memory93", "stream93", "context93", "knowledge93", "vector93"],
    ),
    (
        ("universe93 memory93 stream93 context93 knowledge93 vector93", 10),
        ["universe93", "memory93", "stream93", "context93", "knowledge93", "vector93"],
    ),
    (
        ("universe93 memory93 stream93 context93 knowledge93 vector93", 18),
        ["universe93", "memory93 stream93", "context93", "knowledge93", "vector93"],
    ),
    (
        ("universe93 memory93 stream93 context93 knowledge93 vector93", 28),
        ["universe93 memory93 stream93", "context93 knowledge93", "vector93"],
    ),
    (
        ("memory93 stream93 context93 knowledge93 vector93 processor93", 6),
        ["memory93", "stream93", "context93", "knowledge93", "vector93", "processor93"],
    ),
    (
        ("memory93 stream93 context93 knowledge93 vector93 processor93", 10),
        ["memory93", "stream93", "context93", "knowledge93", "vector93", "processor93"],
    ),
    (
        ("memory93 stream93 context93 knowledge93 vector93 processor93", 18),
        ["memory93 stream93", "context93", "knowledge93", "vector93", "processor93"],
    ),
    (
        ("memory93 stream93 context93 knowledge93 vector93 processor93", 28),
        ["memory93 stream93 context93", "knowledge93 vector93", "processor93"],
    ),
    (
        ("stream93 context93 knowledge93 vector93 processor93 reasoning93", 6),
        ["stream93", "context93", "knowledge93", "vector93", "processor93", "reasoning93"],
    ),
    (
        ("stream93 context93 knowledge93 vector93 processor93 reasoning93", 10),
        ["stream93", "context93", "knowledge93", "vector93", "processor93", "reasoning93"],
    ),
    (
        ("stream93 context93 knowledge93 vector93 processor93 reasoning93", 18),
        ["stream93 context93", "knowledge93", "vector93", "processor93", "reasoning93"],
    ),
    (
        ("stream93 context93 knowledge93 vector93 processor93 reasoning93", 28),
        ["stream93 context93", "knowledge93 vector93", "processor93 reasoning93"],
    ),
    (
        ("context93 knowledge93 vector93 processor93 reasoning93 machine93", 6),
        ["context93", "knowledge93", "vector93", "processor93", "reasoning93", "machine93"],
    ),
    (
        ("context93 knowledge93 vector93 processor93 reasoning93 machine93", 10),
        ["context93", "knowledge93", "vector93", "processor93", "reasoning93", "machine93"],
    ),
    (
        ("context93 knowledge93 vector93 processor93 reasoning93 machine93", 18),
        ["context93", "knowledge93", "vector93", "processor93", "reasoning93", "machine93"],
    ),
    (
        ("context93 knowledge93 vector93 processor93 reasoning93 machine93", 28),
        ["context93 knowledge93", "vector93 processor93", "reasoning93 machine93"],
    ),
    (
        ("knowledge93 vector93 processor93 reasoning93 machine93 learning93", 6),
        ["knowledge93", "vector93", "processor93", "reasoning93", "machine93", "learning93"],
    ),
    (
        ("knowledge93 vector93 processor93 reasoning93 machine93 learning93", 10),
        ["knowledge93", "vector93", "processor93", "reasoning93", "machine93", "learning93"],
    ),
    (
        ("knowledge93 vector93 processor93 reasoning93 machine93 learning93", 18),
        ["knowledge93", "vector93", "processor93", "reasoning93", "machine93", "learning93"],
    ),
    (
        ("knowledge93 vector93 processor93 reasoning93 machine93 learning93", 28),
        ["knowledge93 vector93", "processor93 reasoning93", "machine93 learning93"],
    ),
    (
        ("vector93 processor93 reasoning93 machine93 learning93 model93", 6),
        ["vector93", "processor93", "reasoning93", "machine93", "learning93", "model93"],
    ),
    (
        ("vector93 processor93 reasoning93 machine93 learning93 model93", 10),
        ["vector93", "processor93", "reasoning93", "machine93", "learning93", "model93"],
    ),
    (
        ("vector93 processor93 reasoning93 machine93 learning93 model93", 18),
        ["vector93", "processor93", "reasoning93", "machine93", "learning93 model93"],
    ),
    (
        ("vector93 processor93 reasoning93 machine93 learning93 model93", 28),
        ["vector93 processor93", "reasoning93 machine93", "learning93 model93"],
    ),
    (
        ("processor93 reasoning93 machine93 learning93 model93 token93", 6),
        ["processor93", "reasoning93", "machine93", "learning93", "model93", "token93"],
    ),
    (
        ("processor93 reasoning93 machine93 learning93 model93 token93", 10),
        ["processor93", "reasoning93", "machine93", "learning93", "model93", "token93"],
    ),
    (
        ("processor93 reasoning93 machine93 learning93 model93 token93", 18),
        ["processor93", "reasoning93", "machine93", "learning93 model93", "token93"],
    ),
    (
        ("processor93 reasoning93 machine93 learning93 model93 token93", 28),
        ["processor93 reasoning93", "machine93 learning93 model93", "token93"],
    ),
    (
        ("reasoning93 machine93 learning93 model93 token93 prompt93", 6),
        ["reasoning93", "machine93", "learning93", "model93", "token93", "prompt93"],
    ),
    (
        ("reasoning93 machine93 learning93 model93 token93 prompt93", 10),
        ["reasoning93", "machine93", "learning93", "model93", "token93", "prompt93"],
    ),
    (
        ("reasoning93 machine93 learning93 model93 token93 prompt93", 18),
        ["reasoning93", "machine93", "learning93 model93", "token93 prompt93"],
    ),
    (
        ("reasoning93 machine93 learning93 model93 token93 prompt93", 28),
        ["reasoning93 machine93", "learning93 model93 token93", "prompt93"],
    ),
    (
        ("machine93 learning93 model93 token93 prompt93 session93", 6),
        ["machine93", "learning93", "model93", "token93", "prompt93", "session93"],
    ),
    (
        ("machine93 learning93 model93 token93 prompt93 session93", 10),
        ["machine93", "learning93", "model93", "token93", "prompt93", "session93"],
    ),
    (
        ("machine93 learning93 model93 token93 prompt93 session93", 18),
        ["machine93", "learning93 model93", "token93 prompt93", "session93"],
    ),
    (
        ("machine93 learning93 model93 token93 prompt93 session93", 28),
        ["machine93 learning93 model93", "token93 prompt93 session93"],
    ),
    (
        ("learning93 model93 token93 prompt93 session93 library93", 6),
        ["learning93", "model93", "token93", "prompt93", "session93", "library93"],
    ),
    (
        ("learning93 model93 token93 prompt93 session93 library93", 10),
        ["learning93", "model93", "token93", "prompt93", "session93", "library93"],
    ),
    (
        ("learning93 model93 token93 prompt93 session93 library93", 18),
        ["learning93 model93", "token93 prompt93", "session93", "library93"],
    ),
    (
        ("learning93 model93 token93 prompt93 session93 library93", 28),
        ["learning93 model93 token93", "prompt93 session93 library93"],
    ),
    (
        ("model93 token93 prompt93 session93 library93 service93", 6),
        ["model93", "token93", "prompt93", "session93", "library93", "service93"],
    ),
    (
        ("model93 token93 prompt93 session93 library93 service93", 10),
        ["model93", "token93", "prompt93", "session93", "library93", "service93"],
    ),
    (
        ("model93 token93 prompt93 session93 library93 service93", 18),
        ["model93 token93", "prompt93 session93", "library93", "service93"],
    ),
    (
        ("model93 token93 prompt93 session93 library93 service93", 28),
        ["model93 token93 prompt93", "session93 library93", "service93"],
    ),
    (
        ("token93 prompt93 session93 library93 service93 gateway93", 6),
        ["token93", "prompt93", "session93", "library93", "service93", "gateway93"],
    ),
    (
        ("token93 prompt93 session93 library93 service93 gateway93", 10),
        ["token93", "prompt93", "session93", "library93", "service93", "gateway93"],
    ),
    (
        ("token93 prompt93 session93 library93 service93 gateway93", 18),
        ["token93 prompt93", "session93", "library93", "service93", "gateway93"],
    ),
    (
        ("token93 prompt93 session93 library93 service93 gateway93", 28),
        ["token93 prompt93 session93", "library93 service93", "gateway93"],
    ),
    (
        ("prompt93 session93 library93 service93 gateway93 storage93", 6),
        ["prompt93", "session93", "library93", "service93", "gateway93", "storage93"],
    ),
    (
        ("prompt93 session93 library93 service93 gateway93 storage93", 10),
        ["prompt93", "session93", "library93", "service93", "gateway93", "storage93"],
    ),
    (
        ("prompt93 session93 library93 service93 gateway93 storage93", 18),
        ["prompt93 session93", "library93", "service93", "gateway93", "storage93"],
    ),
    (
        ("prompt93 session93 library93 service93 gateway93 storage93", 28),
        ["prompt93 session93 library93", "service93 gateway93", "storage93"],
    ),
    (
        ("session93 library93 service93 gateway93 storage93 network93", 6),
        ["session93", "library93", "service93", "gateway93", "storage93", "network93"],
    ),
    (
        ("session93 library93 service93 gateway93 storage93 network93", 10),
        ["session93", "library93", "service93", "gateway93", "storage93", "network93"],
    ),
    (
        ("session93 library93 service93 gateway93 storage93 network93", 18),
        ["session93", "library93", "service93", "gateway93", "storage93", "network93"],
    ),
    (
        ("session93 library93 service93 gateway93 storage93 network93", 28),
        ["session93 library93", "service93 gateway93", "storage93 network93"],
    ),
    (
        ("library93 service93 gateway93 storage93 network93 latency93", 6),
        ["library93", "service93", "gateway93", "storage93", "network93", "latency93"],
    ),
    (
        ("library93 service93 gateway93 storage93 network93 latency93", 10),
        ["library93", "service93", "gateway93", "storage93", "network93", "latency93"],
    ),
    (
        ("library93 service93 gateway93 storage93 network93 latency93", 18),
        ["library93", "service93", "gateway93", "storage93", "network93", "latency93"],
    ),
    (
        ("library93 service93 gateway93 storage93 network93 latency93", 28),
        ["library93 service93", "gateway93 storage93", "network93 latency93"],
    ),
    (
        ("service93 gateway93 storage93 network93 latency93 buffer93", 6),
        ["service93", "gateway93", "storage93", "network93", "latency93", "buffer93"],
    ),
    (
        ("service93 gateway93 storage93 network93 latency93 buffer93", 10),
        ["service93", "gateway93", "storage93", "network93", "latency93", "buffer93"],
    ),
    (
        ("service93 gateway93 storage93 network93 latency93 buffer93", 18),
        ["service93", "gateway93", "storage93", "network93", "latency93 buffer93"],
    ),
    (
        ("service93 gateway93 storage93 network93 latency93 buffer93", 28),
        ["service93 gateway93", "storage93 network93", "latency93 buffer93"],
    ),
    (
        ("gateway93 storage93 network93 latency93 buffer93 queue93", 6),
        ["gateway93", "storage93", "network93", "latency93", "buffer93", "queue93"],
    ),
    (
        ("gateway93 storage93 network93 latency93 buffer93 queue93", 10),
        ["gateway93", "storage93", "network93", "latency93", "buffer93", "queue93"],
    ),
    (
        ("gateway93 storage93 network93 latency93 buffer93 queue93", 18),
        ["gateway93", "storage93", "network93", "latency93 buffer93", "queue93"],
    ),
    (
        ("gateway93 storage93 network93 latency93 buffer93 queue93", 28),
        ["gateway93 storage93", "network93 latency93 buffer93", "queue93"],
    ),
    (
        ("storage93 network93 latency93 buffer93 queue93 worker93", 6),
        ["storage93", "network93", "latency93", "buffer93", "queue93", "worker93"],
    ),
    (
        ("storage93 network93 latency93 buffer93 queue93 worker93", 10),
        ["storage93", "network93", "latency93", "buffer93", "queue93", "worker93"],
    ),
    (
        ("storage93 network93 latency93 buffer93 queue93 worker93", 18),
        ["storage93", "network93", "latency93 buffer93", "queue93 worker93"],
    ),
    (
        ("storage93 network93 latency93 buffer93 queue93 worker93", 28),
        ["storage93 network93", "latency93 buffer93 queue93", "worker93"],
    ),
    (
        ("network93 latency93 buffer93 queue93 worker93 kernel93", 6),
        ["network93", "latency93", "buffer93", "queue93", "worker93", "kernel93"],
    ),
    (
        ("network93 latency93 buffer93 queue93 worker93 kernel93", 10),
        ["network93", "latency93", "buffer93", "queue93", "worker93", "kernel93"],
    ),
    (
        ("network93 latency93 buffer93 queue93 worker93 kernel93", 18),
        ["network93", "latency93 buffer93", "queue93 worker93", "kernel93"],
    ),
    (
        ("network93 latency93 buffer93 queue93 worker93 kernel93", 28),
        ["network93 latency93 buffer93", "queue93 worker93 kernel93"],
    ),
    (
        ("latency93 buffer93 queue93 worker93 kernel93 signal93", 6),
        ["latency93", "buffer93", "queue93", "worker93", "kernel93", "signal93"],
    ),
    (
        ("latency93 buffer93 queue93 worker93 kernel93 signal93", 10),
        ["latency93", "buffer93", "queue93", "worker93", "kernel93", "signal93"],
    ),
    (
        ("latency93 buffer93 queue93 worker93 kernel93 signal93", 18),
        ["latency93 buffer93", "queue93 worker93", "kernel93 signal93"],
    ),
    (
        ("latency93 buffer93 queue93 worker93 kernel93 signal93", 28),
        ["latency93 buffer93 queue93", "worker93 kernel93 signal93"],
    ),
    (
        ("buffer93 queue93 worker93 kernel93 signal93 packet93", 6),
        ["buffer93", "queue93", "worker93", "kernel93", "signal93", "packet93"],
    ),
    (
        ("buffer93 queue93 worker93 kernel93 signal93 packet93", 10),
        ["buffer93", "queue93", "worker93", "kernel93", "signal93", "packet93"],
    ),
    (
        ("buffer93 queue93 worker93 kernel93 signal93 packet93", 18),
        ["buffer93 queue93", "worker93 kernel93", "signal93 packet93"],
    ),
    (
        ("buffer93 queue93 worker93 kernel93 signal93 packet93", 28),
        ["buffer93 queue93 worker93", "kernel93 signal93 packet93"],
    ),
    (
        ("queue93 worker93 kernel93 signal93 packet93 router93", 6),
        ["queue93", "worker93", "kernel93", "signal93", "packet93", "router93"],
    ),
    (
        ("queue93 worker93 kernel93 signal93 packet93 router93", 10),
        ["queue93", "worker93", "kernel93", "signal93", "packet93", "router93"],
    ),
    (
        ("queue93 worker93 kernel93 signal93 packet93 router93", 18),
        ["queue93 worker93", "kernel93 signal93", "packet93 router93"],
    ),
    (
        ("queue93 worker93 kernel93 signal93 packet93 router93", 28),
        ["queue93 worker93 kernel93", "signal93 packet93 router93"],
    ),
    (
        ("worker93 kernel93 signal93 packet93 router93 cluster93", 6),
        ["worker93", "kernel93", "signal93", "packet93", "router93", "cluster93"],
    ),
    (
        ("worker93 kernel93 signal93 packet93 router93 cluster93", 10),
        ["worker93", "kernel93", "signal93", "packet93", "router93", "cluster93"],
    ),
    (
        ("worker93 kernel93 signal93 packet93 router93 cluster93", 18),
        ["worker93 kernel93", "signal93 packet93", "router93 cluster93"],
    ),
    (
        ("worker93 kernel93 signal93 packet93 router93 cluster93", 28),
        ["worker93 kernel93 signal93", "packet93 router93 cluster93"],
    ),
    (
        ("kernel93 signal93 packet93 router93 cluster93 mirror93", 6),
        ["kernel93", "signal93", "packet93", "router93", "cluster93", "mirror93"],
    ),
    (
        ("kernel93 signal93 packet93 router93 cluster93 mirror93", 10),
        ["kernel93", "signal93", "packet93", "router93", "cluster93", "mirror93"],
    ),
    (
        ("kernel93 signal93 packet93 router93 cluster93 mirror93", 18),
        ["kernel93 signal93", "packet93 router93", "cluster93 mirror93"],
    ),
    (
        ("kernel93 signal93 packet93 router93 cluster93 mirror93", 28),
        ["kernel93 signal93 packet93", "router93 cluster93 mirror93"],
    ),
    (
        ("signal93 packet93 router93 cluster93 mirror93 filter93", 6),
        ["signal93", "packet93", "router93", "cluster93", "mirror93", "filter93"],
    ),
    (
        ("signal93 packet93 router93 cluster93 mirror93 filter93", 10),
        ["signal93", "packet93", "router93", "cluster93", "mirror93", "filter93"],
    ),
    (
        ("signal93 packet93 router93 cluster93 mirror93 filter93", 18),
        ["signal93 packet93", "router93 cluster93", "mirror93 filter93"],
    ),
    (
        ("signal93 packet93 router93 cluster93 mirror93 filter93", 28),
        ["signal93 packet93 router93", "cluster93 mirror93 filter93"],
    ),
    (
        ("packet93 router93 cluster93 mirror93 filter93 ranking93", 6),
        ["packet93", "router93", "cluster93", "mirror93", "filter93", "ranking93"],
    ),
    (
        ("packet93 router93 cluster93 mirror93 filter93 ranking93", 10),
        ["packet93", "router93", "cluster93", "mirror93", "filter93", "ranking93"],
    ),
    (
        ("packet93 router93 cluster93 mirror93 filter93 ranking93", 18),
        ["packet93 router93", "cluster93 mirror93", "filter93 ranking93"],
    ),
    (
        ("packet93 router93 cluster93 mirror93 filter93 ranking93", 28),
        ["packet93 router93 cluster93", "mirror93 filter93 ranking93"],
    ),
    (
        ("router93 cluster93 mirror93 filter93 ranking93 encoding93", 6),
        ["router93", "cluster93", "mirror93", "filter93", "ranking93", "encoding93"],
    ),
    (
        ("router93 cluster93 mirror93 filter93 ranking93 encoding93", 10),
        ["router93", "cluster93", "mirror93", "filter93", "ranking93", "encoding93"],
    ),
    (
        ("router93 cluster93 mirror93 filter93 ranking93 encoding93", 18),
        ["router93 cluster93", "mirror93 filter93", "ranking93", "encoding93"],
    ),
    (
        ("router93 cluster93 mirror93 filter93 ranking93 encoding93", 28),
        ["router93 cluster93 mirror93", "filter93 ranking93", "encoding93"],
    ),
    (
        ("cluster93 mirror93 filter93 ranking93 encoding93 mapping93", 6),
        ["cluster93", "mirror93", "filter93", "ranking93", "encoding93", "mapping93"],
    ),
    (
        ("cluster93 mirror93 filter93 ranking93 encoding93 mapping93", 10),
        ["cluster93", "mirror93", "filter93", "ranking93", "encoding93", "mapping93"],
    ),
    (
        ("cluster93 mirror93 filter93 ranking93 encoding93 mapping93", 18),
        ["cluster93 mirror93", "filter93 ranking93", "encoding93", "mapping93"],
    ),
    (
        ("cluster93 mirror93 filter93 ranking93 encoding93 mapping93", 28),
        ["cluster93 mirror93 filter93", "ranking93 encoding93", "mapping93"],
    ),
    (
        ("mirror93 filter93 ranking93 encoding93 mapping93 record93", 6),
        ["mirror93", "filter93", "ranking93", "encoding93", "mapping93", "record93"],
    ),
    (
        ("mirror93 filter93 ranking93 encoding93 mapping93 record93", 10),
        ["mirror93", "filter93", "ranking93", "encoding93", "mapping93", "record93"],
    ),
    (
        ("mirror93 filter93 ranking93 encoding93 mapping93 record93", 18),
        ["mirror93 filter93", "ranking93", "encoding93", "mapping93 record93"],
    ),
    (
        ("mirror93 filter93 ranking93 encoding93 mapping93 record93", 28),
        ["mirror93 filter93 ranking93", "encoding93 mapping93", "record93"],
    ),
    (
        ("filter93 ranking93 encoding93 mapping93 record93 candle93", 6),
        ["filter93", "ranking93", "encoding93", "mapping93", "record93", "candle93"],
    ),
    (
        ("filter93 ranking93 encoding93 mapping93 record93 candle93", 10),
        ["filter93", "ranking93", "encoding93", "mapping93", "record93", "candle93"],
    ),
    (
        ("filter93 ranking93 encoding93 mapping93 record93 candle93", 18),
        ["filter93 ranking93", "encoding93", "mapping93 record93", "candle93"],
    ),
    (
        ("filter93 ranking93 encoding93 mapping93 record93 candle93", 28),
        ["filter93 ranking93", "encoding93 mapping93", "record93 candle93"],
    ),
    (
        ("ranking93 encoding93 mapping93 record93 candle93 thread93", 6),
        ["ranking93", "encoding93", "mapping93", "record93", "candle93", "thread93"],
    ),
    (
        ("ranking93 encoding93 mapping93 record93 candle93 thread93", 10),
        ["ranking93", "encoding93", "mapping93", "record93", "candle93", "thread93"],
    ),
    (
        ("ranking93 encoding93 mapping93 record93 candle93 thread93", 18),
        ["ranking93", "encoding93", "mapping93 record93", "candle93 thread93"],
    ),
    (
        ("ranking93 encoding93 mapping93 record93 candle93 thread93", 28),
        ["ranking93 encoding93", "mapping93 record93 candle93", "thread93"],
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
