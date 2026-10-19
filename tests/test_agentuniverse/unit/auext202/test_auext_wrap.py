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
        ("round 202: the quick brown fox jumps over the lazy dog", 4),
        ["round", "202:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 202: the quick brown fox jumps over the lazy dog", 8),
        ["round", "202: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 202: the quick brown fox jumps over the lazy dog", 12),
        ["round 202:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 202: the quick brown fox jumps over the lazy dog", 16),
        ["round 202: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 202: the quick brown fox jumps over the lazy dog", 24),
        ["round 202: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 202: the quick brown fox jumps over the lazy dog", 32),
        ["round 202: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 202: agentuniverse is a framework for multi agents", 4),
        ["round", "202:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 202: agentuniverse is a framework for multi agents", 8),
        ["round", "202:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 202: agentuniverse is a framework for multi agents", 12),
        ["round 202:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 202: agentuniverse is a framework for multi agents", 16),
        ["round 202:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 202: agentuniverse is a framework for multi agents", 24),
        ["round 202: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 202: agentuniverse is a framework for multi agents", 32),
        ["round 202: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 202: knowledge stored as vectors enables retrieval", 4),
        ["round", "202:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 202: knowledge stored as vectors enables retrieval", 8),
        ["round", "202:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 202: knowledge stored as vectors enables retrieval", 12),
        ["round 202:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 202: knowledge stored as vectors enables retrieval", 16),
        ["round 202:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 202: knowledge stored as vectors enables retrieval", 24),
        ["round 202: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 202: knowledge stored as vectors enables retrieval", 32),
        ["round 202: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 202: the processor reads the record then stops", 4),
        ["round", "202:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 202: the processor reads the record then stops", 8),
        ["round", "202: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 202: the processor reads the record then stops", 12),
        ["round 202:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 202: the processor reads the record then stops", 16),
        ["round 202: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 202: the processor reads the record then stops", 24),
        ["round 202: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 202: the processor reads the record then stops", 32),
        ["round 202: the processor reads", "the record then stops"],
    ),
    (
        ("round 202: a worker pulls the next task from the queue", 4),
        ["round", "202:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 202: a worker pulls the next task from the queue", 8),
        ["round", "202: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 202: a worker pulls the next task from the queue", 12),
        ["round 202: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 202: a worker pulls the next task from the queue", 16),
        ["round 202: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 202: a worker pulls the next task from the queue", 24),
        ["round 202: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 202: a worker pulls the next task from the queue", 32),
        ["round 202: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 202: signals travel through the network layer", 4),
        ["round", "202:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 202: signals travel through the network layer", 8),
        ["round", "202:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 202: signals travel through the network layer", 12),
        ["round 202:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 202: signals travel through the network layer", 16),
        ["round 202:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 202: signals travel through the network layer", 24),
        ["round 202: signals", "travel through the", "network layer"],
    ),
    (
        ("round 202: signals travel through the network layer", 32),
        ["round 202: signals travel", "through the network layer"],
    ),
    (
        ("round 202: the gateway routes each request by policy", 4),
        ["round", "202:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 202: the gateway routes each request by policy", 8),
        ["round", "202: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 202: the gateway routes each request by policy", 12),
        ["round 202:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 202: the gateway routes each request by policy", 16),
        ["round 202: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 202: the gateway routes each request by policy", 24),
        ["round 202: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 202: the gateway routes each request by policy", 32),
        ["round 202: the gateway routes", "each request by policy"],
    ),
    (
        ("round 202: memory grows until the buffer is full", 4),
        ["round", "202:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 202: memory grows until the buffer is full", 8),
        ["round", "202:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 202: memory grows until the buffer is full", 12),
        ["round 202:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 202: memory grows until the buffer is full", 16),
        ["round 202:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 202: memory grows until the buffer is full", 24), ["round 202: memory grows", "until the buffer is full"]),
    (("round 202: memory grows until the buffer is full", 32), ["round 202: memory grows until", "the buffer is full"]),
    (
        ("round 202: the cluster mirrors every packet twice", 4),
        ["round", "202:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 202: the cluster mirrors every packet twice", 8),
        ["round", "202: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 202: the cluster mirrors every packet twice", 12),
        ["round 202:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 202: the cluster mirrors every packet twice", 16),
        ["round 202: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 202: the cluster mirrors every packet twice", 24),
        ["round 202: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 202: the cluster mirrors every packet twice", 32),
        ["round 202: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 202: ranking uses tokens learned from the corpus", 4),
        ["round", "202:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 202: ranking uses tokens learned from the corpus", 8),
        ["round", "202:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 202: ranking uses tokens learned from the corpus", 12),
        ["round 202:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 202: ranking uses tokens learned from the corpus", 16),
        ["round 202:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 202: ranking uses tokens learned from the corpus", 24),
        ["round 202: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 202: ranking uses tokens learned from the corpus", 32),
        ["round 202: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 202: a long session ends when the candle dies", 4),
        ["round", "202:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 202: a long session ends when the candle dies", 8),
        ["round", "202: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 202: a long session ends when the candle dies", 12),
        ["round 202: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 202: a long session ends when the candle dies", 16),
        ["round 202: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 202: a long session ends when the candle dies", 24),
        ["round 202: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 202: a long session ends when the candle dies", 32),
        ["round 202: a long session ends", "when the candle dies"],
    ),
    (
        ("round 202: encode the prompt then map the result", 4),
        ["round", "202:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 202: encode the prompt then map the result", 8),
        ["round", "202:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 202: encode the prompt then map the result", 12),
        ["round 202:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 202: encode the prompt then map the result", 16),
        ["round 202:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 202: encode the prompt then map the result", 24),
        ["round 202: encode the", "prompt then map the", "result"],
    ),
    (("round 202: encode the prompt then map the result", 32), ["round 202: encode the prompt", "then map the result"]),
    (
        ("round 202: the kernel wakes the worker at dawn", 4),
        ["round", "202:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 202: the kernel wakes the worker at dawn", 8),
        ["round", "202: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 202: the kernel wakes the worker at dawn", 12),
        ["round 202:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 202: the kernel wakes the worker at dawn", 16), ["round 202: the", "kernel wakes the", "worker at dawn"]),
    (("round 202: the kernel wakes the worker at dawn", 24), ["round 202: the kernel", "wakes the worker at dawn"]),
    (("round 202: the kernel wakes the worker at dawn", 32), ["round 202: the kernel wakes the", "worker at dawn"]),
    (
        ("round 202: service latency drops after the patch", 4),
        ["round", "202:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 202: service latency drops after the patch", 8),
        ["round", "202:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 202: service latency drops after the patch", 12),
        ["round 202:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 202: service latency drops after the patch", 16),
        ["round 202:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 202: service latency drops after the patch", 24),
        ["round 202: service", "latency drops after the", "patch"],
    ),
    (("round 202: service latency drops after the patch", 32), ["round 202: service latency drops", "after the patch"]),
    (
        ("round 202: the library caches every vector it sees", 4),
        ["round", "202:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 202: the library caches every vector it sees", 8),
        ["round", "202: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 202: the library caches every vector it sees", 12),
        ["round 202:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 202: the library caches every vector it sees", 16),
        ["round 202: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 202: the library caches every vector it sees", 24),
        ["round 202: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 202: the library caches every vector it sees", 32),
        ["round 202: the library caches", "every vector it sees"],
    ),
    (
        ("round 202: agents argue then the debate resolves", 4),
        ["round", "202:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 202: agents argue then the debate resolves", 8),
        ["round", "202:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 202: agents argue then the debate resolves", 12),
        ["round 202:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 202: agents argue then the debate resolves", 16),
        ["round 202:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 202: agents argue then the debate resolves", 24), ["round 202: agents argue", "then the debate resolves"]),
    (("round 202: agents argue then the debate resolves", 32), ["round 202: agents argue then the", "debate resolves"]),
    (
        ("round 202: the filter keeps only strong matches", 4),
        ["round", "202:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 202: the filter keeps only strong matches", 8),
        ["round", "202: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 202: the filter keeps only strong matches", 12),
        ["round 202:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 202: the filter keeps only strong matches", 16),
        ["round 202: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 202: the filter keeps only strong matches", 24),
        ["round 202: the filter", "keeps only strong", "matches"],
    ),
    (("round 202: the filter keeps only strong matches", 32), ["round 202: the filter keeps only", "strong matches"]),
    (
        ("round 202: the model answers with a short reply", 4),
        ["round", "202:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 202: the model answers with a short reply", 8),
        ["round", "202: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 202: the model answers with a short reply", 12),
        ["round 202:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 202: the model answers with a short reply", 16),
        ["round 202: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 202: the model answers with a short reply", 24),
        ["round 202: the model", "answers with a short", "reply"],
    ),
    (("round 202: the model answers with a short reply", 32), ["round 202: the model answers", "with a short reply"]),
    (
        ("round 202: the recorder stores the reasoning trace", 4),
        ["round", "202:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 202: the recorder stores the reasoning trace", 8),
        ["round", "202: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 202: the recorder stores the reasoning trace", 12),
        ["round 202:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 202: the recorder stores the reasoning trace", 16),
        ["round 202: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 202: the recorder stores the reasoning trace", 24),
        ["round 202: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 202: the recorder stores the reasoning trace", 32),
        ["round 202: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 202: the angel watches the processor run", 4),
        ["round", "202:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 202: the angel watches the processor run", 8),
        ["round", "202: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 202: the angel watches the processor run", 12),
        ["round 202:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 202: the angel watches the processor run", 16),
        ["round 202: the", "angel watches", "the processor", "run"],
    ),
    (("round 202: the angel watches the processor run", 24), ["round 202: the angel", "watches the processor", "run"]),
    (("round 202: the angel watches the processor run", 32), ["round 202: the angel watches the", "processor run"]),
    (
        ("round 202: angle of the vector decides the match", 4),
        ["round", "202:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 202: angle of the vector decides the match", 8),
        ["round", "202:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 202: angle of the vector decides the match", 12),
        ["round 202:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 202: angle of the vector decides the match", 16),
        ["round 202: angle", "of the vector", "decides the", "match"],
    ),
    (("round 202: angle of the vector decides the match", 24), ["round 202: angle of the", "vector decides the match"]),
    (("round 202: angle of the vector decides the match", 32), ["round 202: angle of the vector", "decides the match"]),
    (
        ("round 202: the candle burns twice as long at night", 4),
        ["round", "202:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 202: the candle burns twice as long at night", 8),
        ["round", "202: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 202: the candle burns twice as long at night", 12),
        ["round 202:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 202: the candle burns twice as long at night", 16),
        ["round 202: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 202: the candle burns twice as long at night", 24),
        ["round 202: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 202: the candle burns twice as long at night", 32),
        ["round 202: the candle burns", "twice as long at night"],
    ),
    (
        ("round 202: a mirror of the universe in one line", 4),
        ["round", "202:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 202: a mirror of the universe in one line", 8),
        ["round", "202: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 202: a mirror of the universe in one line", 12),
        ["round 202: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 202: a mirror of the universe in one line", 16),
        ["round 202: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 202: a mirror of the universe in one line", 24), ["round 202: a mirror of", "the universe in one line"]),
    (("round 202: a mirror of the universe in one line", 32), ["round 202: a mirror of the", "universe in one line"]),
    (
        ("round 202: the queue drains before the storm", 4),
        ["round", "202:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 202: the queue drains before the storm", 8),
        ["round", "202: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 202: the queue drains before the storm", 12),
        ["round 202:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 202: the queue drains before the storm", 16), ["round 202: the", "queue drains", "before the storm"]),
    (("round 202: the queue drains before the storm", 24), ["round 202: the queue", "drains before the storm"]),
    (("round 202: the queue drains before the storm", 32), ["round 202: the queue drains", "before the storm"]),
    (
        ("kitten202 sitting202 agent202 angle202 universe202 memory202", 6),
        ["kitten202", "sitting202", "agent202", "angle202", "universe202", "memory202"],
    ),
    (
        ("kitten202 sitting202 agent202 angle202 universe202 memory202", 10),
        ["kitten202", "sitting202", "agent202", "angle202", "universe202", "memory202"],
    ),
    (
        ("kitten202 sitting202 agent202 angle202 universe202 memory202", 18),
        ["kitten202", "sitting202", "agent202 angle202", "universe202", "memory202"],
    ),
    (
        ("kitten202 sitting202 agent202 angle202 universe202 memory202", 28),
        ["kitten202 sitting202", "agent202 angle202", "universe202 memory202"],
    ),
    (
        ("sitting202 agent202 angle202 universe202 memory202 stream202", 6),
        ["sitting202", "agent202", "angle202", "universe202", "memory202", "stream202"],
    ),
    (
        ("sitting202 agent202 angle202 universe202 memory202 stream202", 10),
        ["sitting202", "agent202", "angle202", "universe202", "memory202", "stream202"],
    ),
    (
        ("sitting202 agent202 angle202 universe202 memory202 stream202", 18),
        ["sitting202", "agent202 angle202", "universe202", "memory202", "stream202"],
    ),
    (
        ("sitting202 agent202 angle202 universe202 memory202 stream202", 28),
        ["sitting202 agent202 angle202", "universe202 memory202", "stream202"],
    ),
    (
        ("agent202 angle202 universe202 memory202 stream202 context202", 6),
        ["agent202", "angle202", "universe202", "memory202", "stream202", "context202"],
    ),
    (
        ("agent202 angle202 universe202 memory202 stream202 context202", 10),
        ["agent202", "angle202", "universe202", "memory202", "stream202", "context202"],
    ),
    (
        ("agent202 angle202 universe202 memory202 stream202 context202", 18),
        ["agent202 angle202", "universe202", "memory202", "stream202", "context202"],
    ),
    (
        ("agent202 angle202 universe202 memory202 stream202 context202", 28),
        ["agent202 angle202", "universe202 memory202", "stream202 context202"],
    ),
    (
        ("angle202 universe202 memory202 stream202 context202 knowledge202", 6),
        ["angle202", "universe202", "memory202", "stream202", "context202", "knowledge202"],
    ),
    (
        ("angle202 universe202 memory202 stream202 context202 knowledge202", 10),
        ["angle202", "universe202", "memory202", "stream202", "context202", "knowledge202"],
    ),
    (
        ("angle202 universe202 memory202 stream202 context202 knowledge202", 18),
        ["angle202", "universe202", "memory202", "stream202", "context202", "knowledge202"],
    ),
    (
        ("angle202 universe202 memory202 stream202 context202 knowledge202", 28),
        ["angle202 universe202", "memory202 stream202", "context202 knowledge202"],
    ),
    (
        ("universe202 memory202 stream202 context202 knowledge202 vector202", 6),
        ["universe202", "memory202", "stream202", "context202", "knowledge202", "vector202"],
    ),
    (
        ("universe202 memory202 stream202 context202 knowledge202 vector202", 10),
        ["universe202", "memory202", "stream202", "context202", "knowledge202", "vector202"],
    ),
    (
        ("universe202 memory202 stream202 context202 knowledge202 vector202", 18),
        ["universe202", "memory202", "stream202", "context202", "knowledge202", "vector202"],
    ),
    (
        ("universe202 memory202 stream202 context202 knowledge202 vector202", 28),
        ["universe202 memory202", "stream202 context202", "knowledge202 vector202"],
    ),
    (
        ("memory202 stream202 context202 knowledge202 vector202 processor202", 6),
        ["memory202", "stream202", "context202", "knowledge202", "vector202", "processor202"],
    ),
    (
        ("memory202 stream202 context202 knowledge202 vector202 processor202", 10),
        ["memory202", "stream202", "context202", "knowledge202", "vector202", "processor202"],
    ),
    (
        ("memory202 stream202 context202 knowledge202 vector202 processor202", 18),
        ["memory202", "stream202", "context202", "knowledge202", "vector202", "processor202"],
    ),
    (
        ("memory202 stream202 context202 knowledge202 vector202 processor202", 28),
        ["memory202 stream202", "context202 knowledge202", "vector202 processor202"],
    ),
    (
        ("stream202 context202 knowledge202 vector202 processor202 reasoning202", 6),
        ["stream202", "context202", "knowledge202", "vector202", "processor202", "reasoning202"],
    ),
    (
        ("stream202 context202 knowledge202 vector202 processor202 reasoning202", 10),
        ["stream202", "context202", "knowledge202", "vector202", "processor202", "reasoning202"],
    ),
    (
        ("stream202 context202 knowledge202 vector202 processor202 reasoning202", 18),
        ["stream202", "context202", "knowledge202", "vector202", "processor202", "reasoning202"],
    ),
    (
        ("stream202 context202 knowledge202 vector202 processor202 reasoning202", 28),
        ["stream202 context202", "knowledge202 vector202", "processor202 reasoning202"],
    ),
    (
        ("context202 knowledge202 vector202 processor202 reasoning202 machine202", 6),
        ["context202", "knowledge202", "vector202", "processor202", "reasoning202", "machine202"],
    ),
    (
        ("context202 knowledge202 vector202 processor202 reasoning202 machine202", 10),
        ["context202", "knowledge202", "vector202", "processor202", "reasoning202", "machine202"],
    ),
    (
        ("context202 knowledge202 vector202 processor202 reasoning202 machine202", 18),
        ["context202", "knowledge202", "vector202", "processor202", "reasoning202", "machine202"],
    ),
    (
        ("context202 knowledge202 vector202 processor202 reasoning202 machine202", 28),
        ["context202 knowledge202", "vector202 processor202", "reasoning202 machine202"],
    ),
    (
        ("knowledge202 vector202 processor202 reasoning202 machine202 learning202", 6),
        ["knowledge202", "vector202", "processor202", "reasoning202", "machine202", "learning202"],
    ),
    (
        ("knowledge202 vector202 processor202 reasoning202 machine202 learning202", 10),
        ["knowledge202", "vector202", "processor202", "reasoning202", "machine202", "learning202"],
    ),
    (
        ("knowledge202 vector202 processor202 reasoning202 machine202 learning202", 18),
        ["knowledge202", "vector202", "processor202", "reasoning202", "machine202", "learning202"],
    ),
    (
        ("knowledge202 vector202 processor202 reasoning202 machine202 learning202", 28),
        ["knowledge202 vector202", "processor202 reasoning202", "machine202 learning202"],
    ),
    (
        ("vector202 processor202 reasoning202 machine202 learning202 model202", 6),
        ["vector202", "processor202", "reasoning202", "machine202", "learning202", "model202"],
    ),
    (
        ("vector202 processor202 reasoning202 machine202 learning202 model202", 10),
        ["vector202", "processor202", "reasoning202", "machine202", "learning202", "model202"],
    ),
    (
        ("vector202 processor202 reasoning202 machine202 learning202 model202", 18),
        ["vector202", "processor202", "reasoning202", "machine202", "learning202", "model202"],
    ),
    (
        ("vector202 processor202 reasoning202 machine202 learning202 model202", 28),
        ["vector202 processor202", "reasoning202 machine202", "learning202 model202"],
    ),
    (
        ("processor202 reasoning202 machine202 learning202 model202 token202", 6),
        ["processor202", "reasoning202", "machine202", "learning202", "model202", "token202"],
    ),
    (
        ("processor202 reasoning202 machine202 learning202 model202 token202", 10),
        ["processor202", "reasoning202", "machine202", "learning202", "model202", "token202"],
    ),
    (
        ("processor202 reasoning202 machine202 learning202 model202 token202", 18),
        ["processor202", "reasoning202", "machine202", "learning202", "model202 token202"],
    ),
    (
        ("processor202 reasoning202 machine202 learning202 model202 token202", 28),
        ["processor202 reasoning202", "machine202 learning202", "model202 token202"],
    ),
    (
        ("reasoning202 machine202 learning202 model202 token202 prompt202", 6),
        ["reasoning202", "machine202", "learning202", "model202", "token202", "prompt202"],
    ),
    (
        ("reasoning202 machine202 learning202 model202 token202 prompt202", 10),
        ["reasoning202", "machine202", "learning202", "model202", "token202", "prompt202"],
    ),
    (
        ("reasoning202 machine202 learning202 model202 token202 prompt202", 18),
        ["reasoning202", "machine202", "learning202", "model202 token202", "prompt202"],
    ),
    (
        ("reasoning202 machine202 learning202 model202 token202 prompt202", 28),
        ["reasoning202 machine202", "learning202 model202", "token202 prompt202"],
    ),
    (
        ("machine202 learning202 model202 token202 prompt202 session202", 6),
        ["machine202", "learning202", "model202", "token202", "prompt202", "session202"],
    ),
    (
        ("machine202 learning202 model202 token202 prompt202 session202", 10),
        ["machine202", "learning202", "model202", "token202", "prompt202", "session202"],
    ),
    (
        ("machine202 learning202 model202 token202 prompt202 session202", 18),
        ["machine202", "learning202", "model202 token202", "prompt202", "session202"],
    ),
    (
        ("machine202 learning202 model202 token202 prompt202 session202", 28),
        ["machine202 learning202", "model202 token202 prompt202", "session202"],
    ),
    (
        ("learning202 model202 token202 prompt202 session202 library202", 6),
        ["learning202", "model202", "token202", "prompt202", "session202", "library202"],
    ),
    (
        ("learning202 model202 token202 prompt202 session202 library202", 10),
        ["learning202", "model202", "token202", "prompt202", "session202", "library202"],
    ),
    (
        ("learning202 model202 token202 prompt202 session202 library202", 18),
        ["learning202", "model202 token202", "prompt202", "session202", "library202"],
    ),
    (
        ("learning202 model202 token202 prompt202 session202 library202", 28),
        ["learning202 model202", "token202 prompt202", "session202 library202"],
    ),
    (
        ("model202 token202 prompt202 session202 library202 service202", 6),
        ["model202", "token202", "prompt202", "session202", "library202", "service202"],
    ),
    (
        ("model202 token202 prompt202 session202 library202 service202", 10),
        ["model202", "token202", "prompt202", "session202", "library202", "service202"],
    ),
    (
        ("model202 token202 prompt202 session202 library202 service202", 18),
        ["model202 token202", "prompt202", "session202", "library202", "service202"],
    ),
    (
        ("model202 token202 prompt202 session202 library202 service202", 28),
        ["model202 token202 prompt202", "session202 library202", "service202"],
    ),
    (
        ("token202 prompt202 session202 library202 service202 gateway202", 6),
        ["token202", "prompt202", "session202", "library202", "service202", "gateway202"],
    ),
    (
        ("token202 prompt202 session202 library202 service202 gateway202", 10),
        ["token202", "prompt202", "session202", "library202", "service202", "gateway202"],
    ),
    (
        ("token202 prompt202 session202 library202 service202 gateway202", 18),
        ["token202 prompt202", "session202", "library202", "service202", "gateway202"],
    ),
    (
        ("token202 prompt202 session202 library202 service202 gateway202", 28),
        ["token202 prompt202", "session202 library202", "service202 gateway202"],
    ),
    (
        ("prompt202 session202 library202 service202 gateway202 storage202", 6),
        ["prompt202", "session202", "library202", "service202", "gateway202", "storage202"],
    ),
    (
        ("prompt202 session202 library202 service202 gateway202 storage202", 10),
        ["prompt202", "session202", "library202", "service202", "gateway202", "storage202"],
    ),
    (
        ("prompt202 session202 library202 service202 gateway202 storage202", 18),
        ["prompt202", "session202", "library202", "service202", "gateway202", "storage202"],
    ),
    (
        ("prompt202 session202 library202 service202 gateway202 storage202", 28),
        ["prompt202 session202", "library202 service202", "gateway202 storage202"],
    ),
    (
        ("session202 library202 service202 gateway202 storage202 network202", 6),
        ["session202", "library202", "service202", "gateway202", "storage202", "network202"],
    ),
    (
        ("session202 library202 service202 gateway202 storage202 network202", 10),
        ["session202", "library202", "service202", "gateway202", "storage202", "network202"],
    ),
    (
        ("session202 library202 service202 gateway202 storage202 network202", 18),
        ["session202", "library202", "service202", "gateway202", "storage202", "network202"],
    ),
    (
        ("session202 library202 service202 gateway202 storage202 network202", 28),
        ["session202 library202", "service202 gateway202", "storage202 network202"],
    ),
    (
        ("library202 service202 gateway202 storage202 network202 latency202", 6),
        ["library202", "service202", "gateway202", "storage202", "network202", "latency202"],
    ),
    (
        ("library202 service202 gateway202 storage202 network202 latency202", 10),
        ["library202", "service202", "gateway202", "storage202", "network202", "latency202"],
    ),
    (
        ("library202 service202 gateway202 storage202 network202 latency202", 18),
        ["library202", "service202", "gateway202", "storage202", "network202", "latency202"],
    ),
    (
        ("library202 service202 gateway202 storage202 network202 latency202", 28),
        ["library202 service202", "gateway202 storage202", "network202 latency202"],
    ),
    (
        ("service202 gateway202 storage202 network202 latency202 buffer202", 6),
        ["service202", "gateway202", "storage202", "network202", "latency202", "buffer202"],
    ),
    (
        ("service202 gateway202 storage202 network202 latency202 buffer202", 10),
        ["service202", "gateway202", "storage202", "network202", "latency202", "buffer202"],
    ),
    (
        ("service202 gateway202 storage202 network202 latency202 buffer202", 18),
        ["service202", "gateway202", "storage202", "network202", "latency202", "buffer202"],
    ),
    (
        ("service202 gateway202 storage202 network202 latency202 buffer202", 28),
        ["service202 gateway202", "storage202 network202", "latency202 buffer202"],
    ),
    (
        ("gateway202 storage202 network202 latency202 buffer202 queue202", 6),
        ["gateway202", "storage202", "network202", "latency202", "buffer202", "queue202"],
    ),
    (
        ("gateway202 storage202 network202 latency202 buffer202 queue202", 10),
        ["gateway202", "storage202", "network202", "latency202", "buffer202", "queue202"],
    ),
    (
        ("gateway202 storage202 network202 latency202 buffer202 queue202", 18),
        ["gateway202", "storage202", "network202", "latency202", "buffer202 queue202"],
    ),
    (
        ("gateway202 storage202 network202 latency202 buffer202 queue202", 28),
        ["gateway202 storage202", "network202 latency202", "buffer202 queue202"],
    ),
    (
        ("storage202 network202 latency202 buffer202 queue202 worker202", 6),
        ["storage202", "network202", "latency202", "buffer202", "queue202", "worker202"],
    ),
    (
        ("storage202 network202 latency202 buffer202 queue202 worker202", 10),
        ["storage202", "network202", "latency202", "buffer202", "queue202", "worker202"],
    ),
    (
        ("storage202 network202 latency202 buffer202 queue202 worker202", 18),
        ["storage202", "network202", "latency202", "buffer202 queue202", "worker202"],
    ),
    (
        ("storage202 network202 latency202 buffer202 queue202 worker202", 28),
        ["storage202 network202", "latency202 buffer202", "queue202 worker202"],
    ),
    (
        ("network202 latency202 buffer202 queue202 worker202 kernel202", 6),
        ["network202", "latency202", "buffer202", "queue202", "worker202", "kernel202"],
    ),
    (
        ("network202 latency202 buffer202 queue202 worker202 kernel202", 10),
        ["network202", "latency202", "buffer202", "queue202", "worker202", "kernel202"],
    ),
    (
        ("network202 latency202 buffer202 queue202 worker202 kernel202", 18),
        ["network202", "latency202", "buffer202 queue202", "worker202", "kernel202"],
    ),
    (
        ("network202 latency202 buffer202 queue202 worker202 kernel202", 28),
        ["network202 latency202", "buffer202 queue202 worker202", "kernel202"],
    ),
    (
        ("latency202 buffer202 queue202 worker202 kernel202 signal202", 6),
        ["latency202", "buffer202", "queue202", "worker202", "kernel202", "signal202"],
    ),
    (
        ("latency202 buffer202 queue202 worker202 kernel202 signal202", 10),
        ["latency202", "buffer202", "queue202", "worker202", "kernel202", "signal202"],
    ),
    (
        ("latency202 buffer202 queue202 worker202 kernel202 signal202", 18),
        ["latency202", "buffer202 queue202", "worker202", "kernel202", "signal202"],
    ),
    (
        ("latency202 buffer202 queue202 worker202 kernel202 signal202", 28),
        ["latency202 buffer202", "queue202 worker202 kernel202", "signal202"],
    ),
    (
        ("buffer202 queue202 worker202 kernel202 signal202 packet202", 6),
        ["buffer202", "queue202", "worker202", "kernel202", "signal202", "packet202"],
    ),
    (
        ("buffer202 queue202 worker202 kernel202 signal202 packet202", 10),
        ["buffer202", "queue202", "worker202", "kernel202", "signal202", "packet202"],
    ),
    (
        ("buffer202 queue202 worker202 kernel202 signal202 packet202", 18),
        ["buffer202 queue202", "worker202", "kernel202", "signal202", "packet202"],
    ),
    (
        ("buffer202 queue202 worker202 kernel202 signal202 packet202", 28),
        ["buffer202 queue202 worker202", "kernel202 signal202", "packet202"],
    ),
    (
        ("queue202 worker202 kernel202 signal202 packet202 router202", 6),
        ["queue202", "worker202", "kernel202", "signal202", "packet202", "router202"],
    ),
    (
        ("queue202 worker202 kernel202 signal202 packet202 router202", 10),
        ["queue202", "worker202", "kernel202", "signal202", "packet202", "router202"],
    ),
    (
        ("queue202 worker202 kernel202 signal202 packet202 router202", 18),
        ["queue202 worker202", "kernel202", "signal202", "packet202", "router202"],
    ),
    (
        ("queue202 worker202 kernel202 signal202 packet202 router202", 28),
        ["queue202 worker202 kernel202", "signal202 packet202", "router202"],
    ),
    (
        ("worker202 kernel202 signal202 packet202 router202 cluster202", 6),
        ["worker202", "kernel202", "signal202", "packet202", "router202", "cluster202"],
    ),
    (
        ("worker202 kernel202 signal202 packet202 router202 cluster202", 10),
        ["worker202", "kernel202", "signal202", "packet202", "router202", "cluster202"],
    ),
    (
        ("worker202 kernel202 signal202 packet202 router202 cluster202", 18),
        ["worker202", "kernel202", "signal202", "packet202", "router202", "cluster202"],
    ),
    (
        ("worker202 kernel202 signal202 packet202 router202 cluster202", 28),
        ["worker202 kernel202", "signal202 packet202", "router202 cluster202"],
    ),
    (
        ("kernel202 signal202 packet202 router202 cluster202 mirror202", 6),
        ["kernel202", "signal202", "packet202", "router202", "cluster202", "mirror202"],
    ),
    (
        ("kernel202 signal202 packet202 router202 cluster202 mirror202", 10),
        ["kernel202", "signal202", "packet202", "router202", "cluster202", "mirror202"],
    ),
    (
        ("kernel202 signal202 packet202 router202 cluster202 mirror202", 18),
        ["kernel202", "signal202", "packet202", "router202", "cluster202", "mirror202"],
    ),
    (
        ("kernel202 signal202 packet202 router202 cluster202 mirror202", 28),
        ["kernel202 signal202", "packet202 router202", "cluster202 mirror202"],
    ),
    (
        ("signal202 packet202 router202 cluster202 mirror202 filter202", 6),
        ["signal202", "packet202", "router202", "cluster202", "mirror202", "filter202"],
    ),
    (
        ("signal202 packet202 router202 cluster202 mirror202 filter202", 10),
        ["signal202", "packet202", "router202", "cluster202", "mirror202", "filter202"],
    ),
    (
        ("signal202 packet202 router202 cluster202 mirror202 filter202", 18),
        ["signal202", "packet202", "router202", "cluster202", "mirror202", "filter202"],
    ),
    (
        ("signal202 packet202 router202 cluster202 mirror202 filter202", 28),
        ["signal202 packet202", "router202 cluster202", "mirror202 filter202"],
    ),
    (
        ("packet202 router202 cluster202 mirror202 filter202 ranking202", 6),
        ["packet202", "router202", "cluster202", "mirror202", "filter202", "ranking202"],
    ),
    (
        ("packet202 router202 cluster202 mirror202 filter202 ranking202", 10),
        ["packet202", "router202", "cluster202", "mirror202", "filter202", "ranking202"],
    ),
    (
        ("packet202 router202 cluster202 mirror202 filter202 ranking202", 18),
        ["packet202", "router202", "cluster202", "mirror202", "filter202", "ranking202"],
    ),
    (
        ("packet202 router202 cluster202 mirror202 filter202 ranking202", 28),
        ["packet202 router202", "cluster202 mirror202", "filter202 ranking202"],
    ),
    (
        ("router202 cluster202 mirror202 filter202 ranking202 encoding202", 6),
        ["router202", "cluster202", "mirror202", "filter202", "ranking202", "encoding202"],
    ),
    (
        ("router202 cluster202 mirror202 filter202 ranking202 encoding202", 10),
        ["router202", "cluster202", "mirror202", "filter202", "ranking202", "encoding202"],
    ),
    (
        ("router202 cluster202 mirror202 filter202 ranking202 encoding202", 18),
        ["router202", "cluster202", "mirror202", "filter202", "ranking202", "encoding202"],
    ),
    (
        ("router202 cluster202 mirror202 filter202 ranking202 encoding202", 28),
        ["router202 cluster202", "mirror202 filter202", "ranking202 encoding202"],
    ),
    (
        ("cluster202 mirror202 filter202 ranking202 encoding202 mapping202", 6),
        ["cluster202", "mirror202", "filter202", "ranking202", "encoding202", "mapping202"],
    ),
    (
        ("cluster202 mirror202 filter202 ranking202 encoding202 mapping202", 10),
        ["cluster202", "mirror202", "filter202", "ranking202", "encoding202", "mapping202"],
    ),
    (
        ("cluster202 mirror202 filter202 ranking202 encoding202 mapping202", 18),
        ["cluster202", "mirror202", "filter202", "ranking202", "encoding202", "mapping202"],
    ),
    (
        ("cluster202 mirror202 filter202 ranking202 encoding202 mapping202", 28),
        ["cluster202 mirror202", "filter202 ranking202", "encoding202 mapping202"],
    ),
    (
        ("mirror202 filter202 ranking202 encoding202 mapping202 record202", 6),
        ["mirror202", "filter202", "ranking202", "encoding202", "mapping202", "record202"],
    ),
    (
        ("mirror202 filter202 ranking202 encoding202 mapping202 record202", 10),
        ["mirror202", "filter202", "ranking202", "encoding202", "mapping202", "record202"],
    ),
    (
        ("mirror202 filter202 ranking202 encoding202 mapping202 record202", 18),
        ["mirror202", "filter202", "ranking202", "encoding202", "mapping202", "record202"],
    ),
    (
        ("mirror202 filter202 ranking202 encoding202 mapping202 record202", 28),
        ["mirror202 filter202", "ranking202 encoding202", "mapping202 record202"],
    ),
    (
        ("filter202 ranking202 encoding202 mapping202 record202 candle202", 6),
        ["filter202", "ranking202", "encoding202", "mapping202", "record202", "candle202"],
    ),
    (
        ("filter202 ranking202 encoding202 mapping202 record202 candle202", 10),
        ["filter202", "ranking202", "encoding202", "mapping202", "record202", "candle202"],
    ),
    (
        ("filter202 ranking202 encoding202 mapping202 record202 candle202", 18),
        ["filter202", "ranking202", "encoding202", "mapping202", "record202", "candle202"],
    ),
    (
        ("filter202 ranking202 encoding202 mapping202 record202 candle202", 28),
        ["filter202 ranking202", "encoding202 mapping202", "record202 candle202"],
    ),
    (
        ("ranking202 encoding202 mapping202 record202 candle202 thread202", 6),
        ["ranking202", "encoding202", "mapping202", "record202", "candle202", "thread202"],
    ),
    (
        ("ranking202 encoding202 mapping202 record202 candle202 thread202", 10),
        ["ranking202", "encoding202", "mapping202", "record202", "candle202", "thread202"],
    ),
    (
        ("ranking202 encoding202 mapping202 record202 candle202 thread202", 18),
        ["ranking202", "encoding202", "mapping202", "record202", "candle202", "thread202"],
    ),
    (
        ("ranking202 encoding202 mapping202 record202 candle202 thread202", 28),
        ["ranking202 encoding202", "mapping202 record202", "candle202 thread202"],
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
