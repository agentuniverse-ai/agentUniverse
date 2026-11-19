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
        ("round 10: the quick brown fox jumps over the lazy dog", 4),
        ["round", "10:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 10: the quick brown fox jumps over the lazy dog", 8),
        ["round", "10: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 10: the quick brown fox jumps over the lazy dog", 12),
        ["round 10:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 10: the quick brown fox jumps over the lazy dog", 16),
        ["round 10: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 10: the quick brown fox jumps over the lazy dog", 24),
        ["round 10: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 10: the quick brown fox jumps over the lazy dog", 32),
        ["round 10: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 10: agentuniverse is a framework for multi agents", 4),
        ["round", "10:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 10: agentuniverse is a framework for multi agents", 8),
        ["round", "10:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 10: agentuniverse is a framework for multi agents", 12),
        ["round 10:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 10: agentuniverse is a framework for multi agents", 16),
        ["round 10:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 10: agentuniverse is a framework for multi agents", 24),
        ["round 10: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 10: agentuniverse is a framework for multi agents", 32),
        ["round 10: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 10: knowledge stored as vectors enables retrieval", 4),
        ["round", "10:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 10: knowledge stored as vectors enables retrieval", 8),
        ["round", "10:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 10: knowledge stored as vectors enables retrieval", 12),
        ["round 10:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 10: knowledge stored as vectors enables retrieval", 16),
        ["round 10:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 10: knowledge stored as vectors enables retrieval", 24),
        ["round 10: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 10: knowledge stored as vectors enables retrieval", 32),
        ["round 10: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 10: the processor reads the record then stops", 4),
        ["round", "10:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 10: the processor reads the record then stops", 8),
        ["round", "10: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 10: the processor reads the record then stops", 12),
        ["round 10:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 10: the processor reads the record then stops", 16),
        ["round 10: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 10: the processor reads the record then stops", 24),
        ["round 10: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 10: the processor reads the record then stops", 32),
        ["round 10: the processor reads", "the record then stops"],
    ),
    (
        ("round 10: a worker pulls the next task from the queue", 4),
        ["round", "10:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 10: a worker pulls the next task from the queue", 8),
        ["round", "10: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 10: a worker pulls the next task from the queue", 12),
        ["round 10: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 10: a worker pulls the next task from the queue", 16),
        ["round 10: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 10: a worker pulls the next task from the queue", 24),
        ["round 10: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 10: a worker pulls the next task from the queue", 32),
        ["round 10: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 10: signals travel through the network layer", 4),
        ["round", "10:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 10: signals travel through the network layer", 8),
        ["round", "10:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 10: signals travel through the network layer", 12),
        ["round 10:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 10: signals travel through the network layer", 16),
        ["round 10:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 10: signals travel through the network layer", 24),
        ["round 10: signals travel", "through the network", "layer"],
    ),
    (
        ("round 10: signals travel through the network layer", 32),
        ["round 10: signals travel through", "the network layer"],
    ),
    (
        ("round 10: the gateway routes each request by policy", 4),
        ["round", "10:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 10: the gateway routes each request by policy", 8),
        ["round", "10: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 10: the gateway routes each request by policy", 12),
        ["round 10:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 10: the gateway routes each request by policy", 16),
        ["round 10: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 10: the gateway routes each request by policy", 24),
        ["round 10: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 10: the gateway routes each request by policy", 32),
        ["round 10: the gateway routes", "each request by policy"],
    ),
    (
        ("round 10: memory grows until the buffer is full", 4),
        ["round", "10:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 10: memory grows until the buffer is full", 8),
        ["round", "10:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 10: memory grows until the buffer is full", 12),
        ["round 10:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 10: memory grows until the buffer is full", 16),
        ["round 10: memory", "grows until the", "buffer is full"],
    ),
    (("round 10: memory grows until the buffer is full", 24), ["round 10: memory grows", "until the buffer is full"]),
    (("round 10: memory grows until the buffer is full", 32), ["round 10: memory grows until the", "buffer is full"]),
    (
        ("round 10: the cluster mirrors every packet twice", 4),
        ["round", "10:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 10: the cluster mirrors every packet twice", 8),
        ["round", "10: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 10: the cluster mirrors every packet twice", 12),
        ["round 10:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 10: the cluster mirrors every packet twice", 16),
        ["round 10: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 10: the cluster mirrors every packet twice", 24),
        ["round 10: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 10: the cluster mirrors every packet twice", 32), ["round 10: the cluster mirrors", "every packet twice"]),
    (
        ("round 10: ranking uses tokens learned from the corpus", 4),
        ["round", "10:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 10: ranking uses tokens learned from the corpus", 8),
        ["round", "10:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 10: ranking uses tokens learned from the corpus", 12),
        ["round 10:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 10: ranking uses tokens learned from the corpus", 16),
        ["round 10:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 10: ranking uses tokens learned from the corpus", 24),
        ["round 10: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 10: ranking uses tokens learned from the corpus", 32),
        ["round 10: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 10: a long session ends when the candle dies", 4),
        ["round", "10:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 10: a long session ends when the candle dies", 8),
        ["round", "10: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 10: a long session ends when the candle dies", 12),
        ["round 10: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 10: a long session ends when the candle dies", 16),
        ["round 10: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 10: a long session ends when the candle dies", 24),
        ["round 10: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 10: a long session ends when the candle dies", 32),
        ["round 10: a long session ends", "when the candle dies"],
    ),
    (
        ("round 10: encode the prompt then map the result", 4),
        ["round", "10:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 10: encode the prompt then map the result", 8),
        ["round", "10:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 10: encode the prompt then map the result", 12),
        ["round 10:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 10: encode the prompt then map the result", 16),
        ["round 10: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 10: encode the prompt then map the result", 24),
        ["round 10: encode the", "prompt then map the", "result"],
    ),
    (("round 10: encode the prompt then map the result", 32), ["round 10: encode the prompt then", "map the result"]),
    (
        ("round 10: the kernel wakes the worker at dawn", 4),
        ["round", "10:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 10: the kernel wakes the worker at dawn", 8),
        ["round", "10: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 10: the kernel wakes the worker at dawn", 12),
        ["round 10:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 10: the kernel wakes the worker at dawn", 16), ["round 10: the", "kernel wakes the", "worker at dawn"]),
    (("round 10: the kernel wakes the worker at dawn", 24), ["round 10: the kernel", "wakes the worker at dawn"]),
    (("round 10: the kernel wakes the worker at dawn", 32), ["round 10: the kernel wakes the", "worker at dawn"]),
    (
        ("round 10: service latency drops after the patch", 4),
        ["round", "10:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 10: service latency drops after the patch", 8),
        ["round", "10:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 10: service latency drops after the patch", 12),
        ["round 10:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 10: service latency drops after the patch", 16),
        ["round 10:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 10: service latency drops after the patch", 24),
        ["round 10: service", "latency drops after the", "patch"],
    ),
    (("round 10: service latency drops after the patch", 32), ["round 10: service latency drops", "after the patch"]),
    (
        ("round 10: the library caches every vector it sees", 4),
        ["round", "10:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 10: the library caches every vector it sees", 8),
        ["round", "10: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 10: the library caches every vector it sees", 12),
        ["round 10:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 10: the library caches every vector it sees", 16),
        ["round 10: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 10: the library caches every vector it sees", 24),
        ["round 10: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 10: the library caches every vector it sees", 32),
        ["round 10: the library caches", "every vector it sees"],
    ),
    (
        ("round 10: agents argue then the debate resolves", 4),
        ["round", "10:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 10: agents argue then the debate resolves", 8),
        ["round", "10:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 10: agents argue then the debate resolves", 12),
        ["round 10:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 10: agents argue then the debate resolves", 16),
        ["round 10: agents", "argue then the", "debate resolves"],
    ),
    (("round 10: agents argue then the debate resolves", 24), ["round 10: agents argue", "then the debate resolves"]),
    (("round 10: agents argue then the debate resolves", 32), ["round 10: agents argue then the", "debate resolves"]),
    (
        ("round 10: the filter keeps only strong matches", 4),
        ["round", "10:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 10: the filter keeps only strong matches", 8),
        ["round", "10: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 10: the filter keeps only strong matches", 12),
        ["round 10:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 10: the filter keeps only strong matches", 16),
        ["round 10: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 10: the filter keeps only strong matches", 24), ["round 10: the filter", "keeps only strong", "matches"]),
    (("round 10: the filter keeps only strong matches", 32), ["round 10: the filter keeps only", "strong matches"]),
    (
        ("round 10: the model answers with a short reply", 4),
        ["round", "10:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 10: the model answers with a short reply", 8),
        ["round", "10: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 10: the model answers with a short reply", 12),
        ["round 10:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 10: the model answers with a short reply", 16),
        ["round 10: the", "model answers", "with a short", "reply"],
    ),
    (("round 10: the model answers with a short reply", 24), ["round 10: the model", "answers with a short", "reply"]),
    (("round 10: the model answers with a short reply", 32), ["round 10: the model answers with", "a short reply"]),
    (
        ("round 10: the recorder stores the reasoning trace", 4),
        ["round", "10:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 10: the recorder stores the reasoning trace", 8),
        ["round", "10: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 10: the recorder stores the reasoning trace", 12),
        ["round 10:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 10: the recorder stores the reasoning trace", 16),
        ["round 10: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 10: the recorder stores the reasoning trace", 24),
        ["round 10: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 10: the recorder stores the reasoning trace", 32),
        ["round 10: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 10: the angel watches the processor run", 4),
        ["round", "10:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 10: the angel watches the processor run", 8),
        ["round", "10: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 10: the angel watches the processor run", 12),
        ["round 10:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 10: the angel watches the processor run", 16), ["round 10: the", "angel watches", "the processor", "run"]),
    (("round 10: the angel watches the processor run", 24), ["round 10: the angel", "watches the processor", "run"]),
    (("round 10: the angel watches the processor run", 32), ["round 10: the angel watches the", "processor run"]),
    (
        ("round 10: angle of the vector decides the match", 4),
        ["round", "10:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 10: angle of the vector decides the match", 8),
        ["round", "10:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 10: angle of the vector decides the match", 12),
        ["round 10:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 10: angle of the vector decides the match", 16),
        ["round 10: angle", "of the vector", "decides the", "match"],
    ),
    (("round 10: angle of the vector decides the match", 24), ["round 10: angle of the", "vector decides the match"]),
    (("round 10: angle of the vector decides the match", 32), ["round 10: angle of the vector", "decides the match"]),
    (
        ("round 10: the candle burns twice as long at night", 4),
        ["round", "10:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 10: the candle burns twice as long at night", 8),
        ["round", "10: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 10: the candle burns twice as long at night", 12),
        ["round 10:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 10: the candle burns twice as long at night", 16),
        ["round 10: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 10: the candle burns twice as long at night", 24),
        ["round 10: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 10: the candle burns twice as long at night", 32),
        ["round 10: the candle burns twice", "as long at night"],
    ),
    (
        ("round 10: a mirror of the universe in one line", 4),
        ["round", "10:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 10: a mirror of the universe in one line", 8),
        ["round", "10: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 10: a mirror of the universe in one line", 12),
        ["round 10: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 10: a mirror of the universe in one line", 16),
        ["round 10: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 10: a mirror of the universe in one line", 24), ["round 10: a mirror of", "the universe in one line"]),
    (("round 10: a mirror of the universe in one line", 32), ["round 10: a mirror of the", "universe in one line"]),
    (
        ("round 10: the queue drains before the storm", 4),
        ["round", "10:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 10: the queue drains before the storm", 8),
        ["round", "10: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 10: the queue drains before the storm", 12), ["round 10:", "the queue", "drains", "before the", "storm"]),
    (("round 10: the queue drains before the storm", 16), ["round 10: the", "queue drains", "before the storm"]),
    (("round 10: the queue drains before the storm", 24), ["round 10: the queue", "drains before the storm"]),
    (("round 10: the queue drains before the storm", 32), ["round 10: the queue drains", "before the storm"]),
    (
        ("kitten10 sitting10 agent10 angle10 universe10 memory10", 6),
        ["kitten10", "sitting10", "agent10", "angle10", "universe10", "memory10"],
    ),
    (
        ("kitten10 sitting10 agent10 angle10 universe10 memory10", 10),
        ["kitten10", "sitting10", "agent10", "angle10", "universe10", "memory10"],
    ),
    (
        ("kitten10 sitting10 agent10 angle10 universe10 memory10", 18),
        ["kitten10 sitting10", "agent10 angle10", "universe10", "memory10"],
    ),
    (
        ("kitten10 sitting10 agent10 angle10 universe10 memory10", 28),
        ["kitten10 sitting10 agent10", "angle10 universe10 memory10"],
    ),
    (
        ("sitting10 agent10 angle10 universe10 memory10 stream10", 6),
        ["sitting10", "agent10", "angle10", "universe10", "memory10", "stream10"],
    ),
    (
        ("sitting10 agent10 angle10 universe10 memory10 stream10", 10),
        ["sitting10", "agent10", "angle10", "universe10", "memory10", "stream10"],
    ),
    (
        ("sitting10 agent10 angle10 universe10 memory10 stream10", 18),
        ["sitting10 agent10", "angle10 universe10", "memory10 stream10"],
    ),
    (
        ("sitting10 agent10 angle10 universe10 memory10 stream10", 28),
        ["sitting10 agent10 angle10", "universe10 memory10 stream10"],
    ),
    (
        ("agent10 angle10 universe10 memory10 stream10 context10", 6),
        ["agent10", "angle10", "universe10", "memory10", "stream10", "context10"],
    ),
    (
        ("agent10 angle10 universe10 memory10 stream10 context10", 10),
        ["agent10", "angle10", "universe10", "memory10", "stream10", "context10"],
    ),
    (
        ("agent10 angle10 universe10 memory10 stream10 context10", 18),
        ["agent10 angle10", "universe10", "memory10 stream10", "context10"],
    ),
    (
        ("agent10 angle10 universe10 memory10 stream10 context10", 28),
        ["agent10 angle10 universe10", "memory10 stream10 context10"],
    ),
    (
        ("angle10 universe10 memory10 stream10 context10 knowledge10", 6),
        ["angle10", "universe10", "memory10", "stream10", "context10", "knowledge10"],
    ),
    (
        ("angle10 universe10 memory10 stream10 context10 knowledge10", 10),
        ["angle10", "universe10", "memory10", "stream10", "context10", "knowledge10"],
    ),
    (
        ("angle10 universe10 memory10 stream10 context10 knowledge10", 18),
        ["angle10 universe10", "memory10 stream10", "context10", "knowledge10"],
    ),
    (
        ("angle10 universe10 memory10 stream10 context10 knowledge10", 28),
        ["angle10 universe10 memory10", "stream10 context10", "knowledge10"],
    ),
    (
        ("universe10 memory10 stream10 context10 knowledge10 vector10", 6),
        ["universe10", "memory10", "stream10", "context10", "knowledge10", "vector10"],
    ),
    (
        ("universe10 memory10 stream10 context10 knowledge10 vector10", 10),
        ["universe10", "memory10", "stream10", "context10", "knowledge10", "vector10"],
    ),
    (
        ("universe10 memory10 stream10 context10 knowledge10 vector10", 18),
        ["universe10", "memory10 stream10", "context10", "knowledge10", "vector10"],
    ),
    (
        ("universe10 memory10 stream10 context10 knowledge10 vector10", 28),
        ["universe10 memory10 stream10", "context10 knowledge10", "vector10"],
    ),
    (
        ("memory10 stream10 context10 knowledge10 vector10 processor10", 6),
        ["memory10", "stream10", "context10", "knowledge10", "vector10", "processor10"],
    ),
    (
        ("memory10 stream10 context10 knowledge10 vector10 processor10", 10),
        ["memory10", "stream10", "context10", "knowledge10", "vector10", "processor10"],
    ),
    (
        ("memory10 stream10 context10 knowledge10 vector10 processor10", 18),
        ["memory10 stream10", "context10", "knowledge10", "vector10", "processor10"],
    ),
    (
        ("memory10 stream10 context10 knowledge10 vector10 processor10", 28),
        ["memory10 stream10 context10", "knowledge10 vector10", "processor10"],
    ),
    (
        ("stream10 context10 knowledge10 vector10 processor10 reasoning10", 6),
        ["stream10", "context10", "knowledge10", "vector10", "processor10", "reasoning10"],
    ),
    (
        ("stream10 context10 knowledge10 vector10 processor10 reasoning10", 10),
        ["stream10", "context10", "knowledge10", "vector10", "processor10", "reasoning10"],
    ),
    (
        ("stream10 context10 knowledge10 vector10 processor10 reasoning10", 18),
        ["stream10 context10", "knowledge10", "vector10", "processor10", "reasoning10"],
    ),
    (
        ("stream10 context10 knowledge10 vector10 processor10 reasoning10", 28),
        ["stream10 context10", "knowledge10 vector10", "processor10 reasoning10"],
    ),
    (
        ("context10 knowledge10 vector10 processor10 reasoning10 machine10", 6),
        ["context10", "knowledge10", "vector10", "processor10", "reasoning10", "machine10"],
    ),
    (
        ("context10 knowledge10 vector10 processor10 reasoning10 machine10", 10),
        ["context10", "knowledge10", "vector10", "processor10", "reasoning10", "machine10"],
    ),
    (
        ("context10 knowledge10 vector10 processor10 reasoning10 machine10", 18),
        ["context10", "knowledge10", "vector10", "processor10", "reasoning10", "machine10"],
    ),
    (
        ("context10 knowledge10 vector10 processor10 reasoning10 machine10", 28),
        ["context10 knowledge10", "vector10 processor10", "reasoning10 machine10"],
    ),
    (
        ("knowledge10 vector10 processor10 reasoning10 machine10 learning10", 6),
        ["knowledge10", "vector10", "processor10", "reasoning10", "machine10", "learning10"],
    ),
    (
        ("knowledge10 vector10 processor10 reasoning10 machine10 learning10", 10),
        ["knowledge10", "vector10", "processor10", "reasoning10", "machine10", "learning10"],
    ),
    (
        ("knowledge10 vector10 processor10 reasoning10 machine10 learning10", 18),
        ["knowledge10", "vector10", "processor10", "reasoning10", "machine10", "learning10"],
    ),
    (
        ("knowledge10 vector10 processor10 reasoning10 machine10 learning10", 28),
        ["knowledge10 vector10", "processor10 reasoning10", "machine10 learning10"],
    ),
    (
        ("vector10 processor10 reasoning10 machine10 learning10 model10", 6),
        ["vector10", "processor10", "reasoning10", "machine10", "learning10", "model10"],
    ),
    (
        ("vector10 processor10 reasoning10 machine10 learning10 model10", 10),
        ["vector10", "processor10", "reasoning10", "machine10", "learning10", "model10"],
    ),
    (
        ("vector10 processor10 reasoning10 machine10 learning10 model10", 18),
        ["vector10", "processor10", "reasoning10", "machine10", "learning10 model10"],
    ),
    (
        ("vector10 processor10 reasoning10 machine10 learning10 model10", 28),
        ["vector10 processor10", "reasoning10 machine10", "learning10 model10"],
    ),
    (
        ("processor10 reasoning10 machine10 learning10 model10 token10", 6),
        ["processor10", "reasoning10", "machine10", "learning10", "model10", "token10"],
    ),
    (
        ("processor10 reasoning10 machine10 learning10 model10 token10", 10),
        ["processor10", "reasoning10", "machine10", "learning10", "model10", "token10"],
    ),
    (
        ("processor10 reasoning10 machine10 learning10 model10 token10", 18),
        ["processor10", "reasoning10", "machine10", "learning10 model10", "token10"],
    ),
    (
        ("processor10 reasoning10 machine10 learning10 model10 token10", 28),
        ["processor10 reasoning10", "machine10 learning10 model10", "token10"],
    ),
    (
        ("reasoning10 machine10 learning10 model10 token10 prompt10", 6),
        ["reasoning10", "machine10", "learning10", "model10", "token10", "prompt10"],
    ),
    (
        ("reasoning10 machine10 learning10 model10 token10 prompt10", 10),
        ["reasoning10", "machine10", "learning10", "model10", "token10", "prompt10"],
    ),
    (
        ("reasoning10 machine10 learning10 model10 token10 prompt10", 18),
        ["reasoning10", "machine10", "learning10 model10", "token10 prompt10"],
    ),
    (
        ("reasoning10 machine10 learning10 model10 token10 prompt10", 28),
        ["reasoning10 machine10", "learning10 model10 token10", "prompt10"],
    ),
    (
        ("machine10 learning10 model10 token10 prompt10 session10", 6),
        ["machine10", "learning10", "model10", "token10", "prompt10", "session10"],
    ),
    (
        ("machine10 learning10 model10 token10 prompt10 session10", 10),
        ["machine10", "learning10", "model10", "token10", "prompt10", "session10"],
    ),
    (
        ("machine10 learning10 model10 token10 prompt10 session10", 18),
        ["machine10", "learning10 model10", "token10 prompt10", "session10"],
    ),
    (
        ("machine10 learning10 model10 token10 prompt10 session10", 28),
        ["machine10 learning10 model10", "token10 prompt10 session10"],
    ),
    (
        ("learning10 model10 token10 prompt10 session10 library10", 6),
        ["learning10", "model10", "token10", "prompt10", "session10", "library10"],
    ),
    (
        ("learning10 model10 token10 prompt10 session10 library10", 10),
        ["learning10", "model10", "token10", "prompt10", "session10", "library10"],
    ),
    (
        ("learning10 model10 token10 prompt10 session10 library10", 18),
        ["learning10 model10", "token10 prompt10", "session10", "library10"],
    ),
    (
        ("learning10 model10 token10 prompt10 session10 library10", 28),
        ["learning10 model10 token10", "prompt10 session10 library10"],
    ),
    (
        ("model10 token10 prompt10 session10 library10 service10", 6),
        ["model10", "token10", "prompt10", "session10", "library10", "service10"],
    ),
    (
        ("model10 token10 prompt10 session10 library10 service10", 10),
        ["model10", "token10", "prompt10", "session10", "library10", "service10"],
    ),
    (
        ("model10 token10 prompt10 session10 library10 service10", 18),
        ["model10 token10", "prompt10 session10", "library10", "service10"],
    ),
    (
        ("model10 token10 prompt10 session10 library10 service10", 28),
        ["model10 token10 prompt10", "session10 library10", "service10"],
    ),
    (
        ("token10 prompt10 session10 library10 service10 gateway10", 6),
        ["token10", "prompt10", "session10", "library10", "service10", "gateway10"],
    ),
    (
        ("token10 prompt10 session10 library10 service10 gateway10", 10),
        ["token10", "prompt10", "session10", "library10", "service10", "gateway10"],
    ),
    (
        ("token10 prompt10 session10 library10 service10 gateway10", 18),
        ["token10 prompt10", "session10", "library10", "service10", "gateway10"],
    ),
    (
        ("token10 prompt10 session10 library10 service10 gateway10", 28),
        ["token10 prompt10 session10", "library10 service10", "gateway10"],
    ),
    (
        ("prompt10 session10 library10 service10 gateway10 storage10", 6),
        ["prompt10", "session10", "library10", "service10", "gateway10", "storage10"],
    ),
    (
        ("prompt10 session10 library10 service10 gateway10 storage10", 10),
        ["prompt10", "session10", "library10", "service10", "gateway10", "storage10"],
    ),
    (
        ("prompt10 session10 library10 service10 gateway10 storage10", 18),
        ["prompt10 session10", "library10", "service10", "gateway10", "storage10"],
    ),
    (
        ("prompt10 session10 library10 service10 gateway10 storage10", 28),
        ["prompt10 session10 library10", "service10 gateway10", "storage10"],
    ),
    (
        ("session10 library10 service10 gateway10 storage10 network10", 6),
        ["session10", "library10", "service10", "gateway10", "storage10", "network10"],
    ),
    (
        ("session10 library10 service10 gateway10 storage10 network10", 10),
        ["session10", "library10", "service10", "gateway10", "storage10", "network10"],
    ),
    (
        ("session10 library10 service10 gateway10 storage10 network10", 18),
        ["session10", "library10", "service10", "gateway10", "storage10", "network10"],
    ),
    (
        ("session10 library10 service10 gateway10 storage10 network10", 28),
        ["session10 library10", "service10 gateway10", "storage10 network10"],
    ),
    (
        ("library10 service10 gateway10 storage10 network10 latency10", 6),
        ["library10", "service10", "gateway10", "storage10", "network10", "latency10"],
    ),
    (
        ("library10 service10 gateway10 storage10 network10 latency10", 10),
        ["library10", "service10", "gateway10", "storage10", "network10", "latency10"],
    ),
    (
        ("library10 service10 gateway10 storage10 network10 latency10", 18),
        ["library10", "service10", "gateway10", "storage10", "network10", "latency10"],
    ),
    (
        ("library10 service10 gateway10 storage10 network10 latency10", 28),
        ["library10 service10", "gateway10 storage10", "network10 latency10"],
    ),
    (
        ("service10 gateway10 storage10 network10 latency10 buffer10", 6),
        ["service10", "gateway10", "storage10", "network10", "latency10", "buffer10"],
    ),
    (
        ("service10 gateway10 storage10 network10 latency10 buffer10", 10),
        ["service10", "gateway10", "storage10", "network10", "latency10", "buffer10"],
    ),
    (
        ("service10 gateway10 storage10 network10 latency10 buffer10", 18),
        ["service10", "gateway10", "storage10", "network10", "latency10 buffer10"],
    ),
    (
        ("service10 gateway10 storage10 network10 latency10 buffer10", 28),
        ["service10 gateway10", "storage10 network10", "latency10 buffer10"],
    ),
    (
        ("gateway10 storage10 network10 latency10 buffer10 queue10", 6),
        ["gateway10", "storage10", "network10", "latency10", "buffer10", "queue10"],
    ),
    (
        ("gateway10 storage10 network10 latency10 buffer10 queue10", 10),
        ["gateway10", "storage10", "network10", "latency10", "buffer10", "queue10"],
    ),
    (
        ("gateway10 storage10 network10 latency10 buffer10 queue10", 18),
        ["gateway10", "storage10", "network10", "latency10 buffer10", "queue10"],
    ),
    (
        ("gateway10 storage10 network10 latency10 buffer10 queue10", 28),
        ["gateway10 storage10", "network10 latency10 buffer10", "queue10"],
    ),
    (
        ("storage10 network10 latency10 buffer10 queue10 worker10", 6),
        ["storage10", "network10", "latency10", "buffer10", "queue10", "worker10"],
    ),
    (
        ("storage10 network10 latency10 buffer10 queue10 worker10", 10),
        ["storage10", "network10", "latency10", "buffer10", "queue10", "worker10"],
    ),
    (
        ("storage10 network10 latency10 buffer10 queue10 worker10", 18),
        ["storage10", "network10", "latency10 buffer10", "queue10 worker10"],
    ),
    (
        ("storage10 network10 latency10 buffer10 queue10 worker10", 28),
        ["storage10 network10", "latency10 buffer10 queue10", "worker10"],
    ),
    (
        ("network10 latency10 buffer10 queue10 worker10 kernel10", 6),
        ["network10", "latency10", "buffer10", "queue10", "worker10", "kernel10"],
    ),
    (
        ("network10 latency10 buffer10 queue10 worker10 kernel10", 10),
        ["network10", "latency10", "buffer10", "queue10", "worker10", "kernel10"],
    ),
    (
        ("network10 latency10 buffer10 queue10 worker10 kernel10", 18),
        ["network10", "latency10 buffer10", "queue10 worker10", "kernel10"],
    ),
    (
        ("network10 latency10 buffer10 queue10 worker10 kernel10", 28),
        ["network10 latency10 buffer10", "queue10 worker10 kernel10"],
    ),
    (
        ("latency10 buffer10 queue10 worker10 kernel10 signal10", 6),
        ["latency10", "buffer10", "queue10", "worker10", "kernel10", "signal10"],
    ),
    (
        ("latency10 buffer10 queue10 worker10 kernel10 signal10", 10),
        ["latency10", "buffer10", "queue10", "worker10", "kernel10", "signal10"],
    ),
    (
        ("latency10 buffer10 queue10 worker10 kernel10 signal10", 18),
        ["latency10 buffer10", "queue10 worker10", "kernel10 signal10"],
    ),
    (
        ("latency10 buffer10 queue10 worker10 kernel10 signal10", 28),
        ["latency10 buffer10 queue10", "worker10 kernel10 signal10"],
    ),
    (
        ("buffer10 queue10 worker10 kernel10 signal10 packet10", 6),
        ["buffer10", "queue10", "worker10", "kernel10", "signal10", "packet10"],
    ),
    (
        ("buffer10 queue10 worker10 kernel10 signal10 packet10", 10),
        ["buffer10", "queue10", "worker10", "kernel10", "signal10", "packet10"],
    ),
    (
        ("buffer10 queue10 worker10 kernel10 signal10 packet10", 18),
        ["buffer10 queue10", "worker10 kernel10", "signal10 packet10"],
    ),
    (
        ("buffer10 queue10 worker10 kernel10 signal10 packet10", 28),
        ["buffer10 queue10 worker10", "kernel10 signal10 packet10"],
    ),
    (
        ("queue10 worker10 kernel10 signal10 packet10 router10", 6),
        ["queue10", "worker10", "kernel10", "signal10", "packet10", "router10"],
    ),
    (
        ("queue10 worker10 kernel10 signal10 packet10 router10", 10),
        ["queue10", "worker10", "kernel10", "signal10", "packet10", "router10"],
    ),
    (
        ("queue10 worker10 kernel10 signal10 packet10 router10", 18),
        ["queue10 worker10", "kernel10 signal10", "packet10 router10"],
    ),
    (
        ("queue10 worker10 kernel10 signal10 packet10 router10", 28),
        ["queue10 worker10 kernel10", "signal10 packet10 router10"],
    ),
    (
        ("worker10 kernel10 signal10 packet10 router10 cluster10", 6),
        ["worker10", "kernel10", "signal10", "packet10", "router10", "cluster10"],
    ),
    (
        ("worker10 kernel10 signal10 packet10 router10 cluster10", 10),
        ["worker10", "kernel10", "signal10", "packet10", "router10", "cluster10"],
    ),
    (
        ("worker10 kernel10 signal10 packet10 router10 cluster10", 18),
        ["worker10 kernel10", "signal10 packet10", "router10 cluster10"],
    ),
    (
        ("worker10 kernel10 signal10 packet10 router10 cluster10", 28),
        ["worker10 kernel10 signal10", "packet10 router10 cluster10"],
    ),
    (
        ("kernel10 signal10 packet10 router10 cluster10 mirror10", 6),
        ["kernel10", "signal10", "packet10", "router10", "cluster10", "mirror10"],
    ),
    (
        ("kernel10 signal10 packet10 router10 cluster10 mirror10", 10),
        ["kernel10", "signal10", "packet10", "router10", "cluster10", "mirror10"],
    ),
    (
        ("kernel10 signal10 packet10 router10 cluster10 mirror10", 18),
        ["kernel10 signal10", "packet10 router10", "cluster10 mirror10"],
    ),
    (
        ("kernel10 signal10 packet10 router10 cluster10 mirror10", 28),
        ["kernel10 signal10 packet10", "router10 cluster10 mirror10"],
    ),
    (
        ("signal10 packet10 router10 cluster10 mirror10 filter10", 6),
        ["signal10", "packet10", "router10", "cluster10", "mirror10", "filter10"],
    ),
    (
        ("signal10 packet10 router10 cluster10 mirror10 filter10", 10),
        ["signal10", "packet10", "router10", "cluster10", "mirror10", "filter10"],
    ),
    (
        ("signal10 packet10 router10 cluster10 mirror10 filter10", 18),
        ["signal10 packet10", "router10 cluster10", "mirror10 filter10"],
    ),
    (
        ("signal10 packet10 router10 cluster10 mirror10 filter10", 28),
        ["signal10 packet10 router10", "cluster10 mirror10 filter10"],
    ),
    (
        ("packet10 router10 cluster10 mirror10 filter10 ranking10", 6),
        ["packet10", "router10", "cluster10", "mirror10", "filter10", "ranking10"],
    ),
    (
        ("packet10 router10 cluster10 mirror10 filter10 ranking10", 10),
        ["packet10", "router10", "cluster10", "mirror10", "filter10", "ranking10"],
    ),
    (
        ("packet10 router10 cluster10 mirror10 filter10 ranking10", 18),
        ["packet10 router10", "cluster10 mirror10", "filter10 ranking10"],
    ),
    (
        ("packet10 router10 cluster10 mirror10 filter10 ranking10", 28),
        ["packet10 router10 cluster10", "mirror10 filter10 ranking10"],
    ),
    (
        ("router10 cluster10 mirror10 filter10 ranking10 encoding10", 6),
        ["router10", "cluster10", "mirror10", "filter10", "ranking10", "encoding10"],
    ),
    (
        ("router10 cluster10 mirror10 filter10 ranking10 encoding10", 10),
        ["router10", "cluster10", "mirror10", "filter10", "ranking10", "encoding10"],
    ),
    (
        ("router10 cluster10 mirror10 filter10 ranking10 encoding10", 18),
        ["router10 cluster10", "mirror10 filter10", "ranking10", "encoding10"],
    ),
    (
        ("router10 cluster10 mirror10 filter10 ranking10 encoding10", 28),
        ["router10 cluster10 mirror10", "filter10 ranking10", "encoding10"],
    ),
    (
        ("cluster10 mirror10 filter10 ranking10 encoding10 mapping10", 6),
        ["cluster10", "mirror10", "filter10", "ranking10", "encoding10", "mapping10"],
    ),
    (
        ("cluster10 mirror10 filter10 ranking10 encoding10 mapping10", 10),
        ["cluster10", "mirror10", "filter10", "ranking10", "encoding10", "mapping10"],
    ),
    (
        ("cluster10 mirror10 filter10 ranking10 encoding10 mapping10", 18),
        ["cluster10 mirror10", "filter10 ranking10", "encoding10", "mapping10"],
    ),
    (
        ("cluster10 mirror10 filter10 ranking10 encoding10 mapping10", 28),
        ["cluster10 mirror10 filter10", "ranking10 encoding10", "mapping10"],
    ),
    (
        ("mirror10 filter10 ranking10 encoding10 mapping10 record10", 6),
        ["mirror10", "filter10", "ranking10", "encoding10", "mapping10", "record10"],
    ),
    (
        ("mirror10 filter10 ranking10 encoding10 mapping10 record10", 10),
        ["mirror10", "filter10", "ranking10", "encoding10", "mapping10", "record10"],
    ),
    (
        ("mirror10 filter10 ranking10 encoding10 mapping10 record10", 18),
        ["mirror10 filter10", "ranking10", "encoding10", "mapping10 record10"],
    ),
    (
        ("mirror10 filter10 ranking10 encoding10 mapping10 record10", 28),
        ["mirror10 filter10 ranking10", "encoding10 mapping10", "record10"],
    ),
    (
        ("filter10 ranking10 encoding10 mapping10 record10 candle10", 6),
        ["filter10", "ranking10", "encoding10", "mapping10", "record10", "candle10"],
    ),
    (
        ("filter10 ranking10 encoding10 mapping10 record10 candle10", 10),
        ["filter10", "ranking10", "encoding10", "mapping10", "record10", "candle10"],
    ),
    (
        ("filter10 ranking10 encoding10 mapping10 record10 candle10", 18),
        ["filter10 ranking10", "encoding10", "mapping10 record10", "candle10"],
    ),
    (
        ("filter10 ranking10 encoding10 mapping10 record10 candle10", 28),
        ["filter10 ranking10", "encoding10 mapping10", "record10 candle10"],
    ),
    (
        ("ranking10 encoding10 mapping10 record10 candle10 thread10", 6),
        ["ranking10", "encoding10", "mapping10", "record10", "candle10", "thread10"],
    ),
    (
        ("ranking10 encoding10 mapping10 record10 candle10 thread10", 10),
        ["ranking10", "encoding10", "mapping10", "record10", "candle10", "thread10"],
    ),
    (
        ("ranking10 encoding10 mapping10 record10 candle10 thread10", 18),
        ["ranking10", "encoding10", "mapping10 record10", "candle10 thread10"],
    ),
    (
        ("ranking10 encoding10 mapping10 record10 candle10 thread10", 28),
        ["ranking10 encoding10", "mapping10 record10 candle10", "thread10"],
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
