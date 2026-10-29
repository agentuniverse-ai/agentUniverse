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
        ("round 101: the quick brown fox jumps over the lazy dog", 4),
        ["round", "101:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 101: the quick brown fox jumps over the lazy dog", 8),
        ["round", "101: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 101: the quick brown fox jumps over the lazy dog", 12),
        ["round 101:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 101: the quick brown fox jumps over the lazy dog", 16),
        ["round 101: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 101: the quick brown fox jumps over the lazy dog", 24),
        ["round 101: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 101: the quick brown fox jumps over the lazy dog", 32),
        ["round 101: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 101: agentuniverse is a framework for multi agents", 4),
        ["round", "101:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 101: agentuniverse is a framework for multi agents", 8),
        ["round", "101:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 101: agentuniverse is a framework for multi agents", 12),
        ["round 101:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 101: agentuniverse is a framework for multi agents", 16),
        ["round 101:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 101: agentuniverse is a framework for multi agents", 24),
        ["round 101: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 101: agentuniverse is a framework for multi agents", 32),
        ["round 101: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 101: knowledge stored as vectors enables retrieval", 4),
        ["round", "101:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 101: knowledge stored as vectors enables retrieval", 8),
        ["round", "101:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 101: knowledge stored as vectors enables retrieval", 12),
        ["round 101:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 101: knowledge stored as vectors enables retrieval", 16),
        ["round 101:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 101: knowledge stored as vectors enables retrieval", 24),
        ["round 101: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 101: knowledge stored as vectors enables retrieval", 32),
        ["round 101: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 101: the processor reads the record then stops", 4),
        ["round", "101:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 101: the processor reads the record then stops", 8),
        ["round", "101: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 101: the processor reads the record then stops", 12),
        ["round 101:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 101: the processor reads the record then stops", 16),
        ["round 101: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 101: the processor reads the record then stops", 24),
        ["round 101: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 101: the processor reads the record then stops", 32),
        ["round 101: the processor reads", "the record then stops"],
    ),
    (
        ("round 101: a worker pulls the next task from the queue", 4),
        ["round", "101:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 101: a worker pulls the next task from the queue", 8),
        ["round", "101: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 101: a worker pulls the next task from the queue", 12),
        ["round 101: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 101: a worker pulls the next task from the queue", 16),
        ["round 101: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 101: a worker pulls the next task from the queue", 24),
        ["round 101: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 101: a worker pulls the next task from the queue", 32),
        ["round 101: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 101: signals travel through the network layer", 4),
        ["round", "101:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 101: signals travel through the network layer", 8),
        ["round", "101:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 101: signals travel through the network layer", 12),
        ["round 101:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 101: signals travel through the network layer", 16),
        ["round 101:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 101: signals travel through the network layer", 24),
        ["round 101: signals", "travel through the", "network layer"],
    ),
    (
        ("round 101: signals travel through the network layer", 32),
        ["round 101: signals travel", "through the network layer"],
    ),
    (
        ("round 101: the gateway routes each request by policy", 4),
        ["round", "101:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 101: the gateway routes each request by policy", 8),
        ["round", "101: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 101: the gateway routes each request by policy", 12),
        ["round 101:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 101: the gateway routes each request by policy", 16),
        ["round 101: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 101: the gateway routes each request by policy", 24),
        ["round 101: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 101: the gateway routes each request by policy", 32),
        ["round 101: the gateway routes", "each request by policy"],
    ),
    (
        ("round 101: memory grows until the buffer is full", 4),
        ["round", "101:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 101: memory grows until the buffer is full", 8),
        ["round", "101:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 101: memory grows until the buffer is full", 12),
        ["round 101:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 101: memory grows until the buffer is full", 16),
        ["round 101:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 101: memory grows until the buffer is full", 24), ["round 101: memory grows", "until the buffer is full"]),
    (("round 101: memory grows until the buffer is full", 32), ["round 101: memory grows until", "the buffer is full"]),
    (
        ("round 101: the cluster mirrors every packet twice", 4),
        ["round", "101:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 101: the cluster mirrors every packet twice", 8),
        ["round", "101: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 101: the cluster mirrors every packet twice", 12),
        ["round 101:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 101: the cluster mirrors every packet twice", 16),
        ["round 101: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 101: the cluster mirrors every packet twice", 24),
        ["round 101: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 101: the cluster mirrors every packet twice", 32),
        ["round 101: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 101: ranking uses tokens learned from the corpus", 4),
        ["round", "101:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 101: ranking uses tokens learned from the corpus", 8),
        ["round", "101:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 101: ranking uses tokens learned from the corpus", 12),
        ["round 101:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 101: ranking uses tokens learned from the corpus", 16),
        ["round 101:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 101: ranking uses tokens learned from the corpus", 24),
        ["round 101: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 101: ranking uses tokens learned from the corpus", 32),
        ["round 101: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 101: a long session ends when the candle dies", 4),
        ["round", "101:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 101: a long session ends when the candle dies", 8),
        ["round", "101: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 101: a long session ends when the candle dies", 12),
        ["round 101: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 101: a long session ends when the candle dies", 16),
        ["round 101: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 101: a long session ends when the candle dies", 24),
        ["round 101: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 101: a long session ends when the candle dies", 32),
        ["round 101: a long session ends", "when the candle dies"],
    ),
    (
        ("round 101: encode the prompt then map the result", 4),
        ["round", "101:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 101: encode the prompt then map the result", 8),
        ["round", "101:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 101: encode the prompt then map the result", 12),
        ["round 101:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 101: encode the prompt then map the result", 16),
        ["round 101:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 101: encode the prompt then map the result", 24),
        ["round 101: encode the", "prompt then map the", "result"],
    ),
    (("round 101: encode the prompt then map the result", 32), ["round 101: encode the prompt", "then map the result"]),
    (
        ("round 101: the kernel wakes the worker at dawn", 4),
        ["round", "101:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 101: the kernel wakes the worker at dawn", 8),
        ["round", "101: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 101: the kernel wakes the worker at dawn", 12),
        ["round 101:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 101: the kernel wakes the worker at dawn", 16), ["round 101: the", "kernel wakes the", "worker at dawn"]),
    (("round 101: the kernel wakes the worker at dawn", 24), ["round 101: the kernel", "wakes the worker at dawn"]),
    (("round 101: the kernel wakes the worker at dawn", 32), ["round 101: the kernel wakes the", "worker at dawn"]),
    (
        ("round 101: service latency drops after the patch", 4),
        ["round", "101:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 101: service latency drops after the patch", 8),
        ["round", "101:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 101: service latency drops after the patch", 12),
        ["round 101:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 101: service latency drops after the patch", 16),
        ["round 101:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 101: service latency drops after the patch", 24),
        ["round 101: service", "latency drops after the", "patch"],
    ),
    (("round 101: service latency drops after the patch", 32), ["round 101: service latency drops", "after the patch"]),
    (
        ("round 101: the library caches every vector it sees", 4),
        ["round", "101:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 101: the library caches every vector it sees", 8),
        ["round", "101: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 101: the library caches every vector it sees", 12),
        ["round 101:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 101: the library caches every vector it sees", 16),
        ["round 101: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 101: the library caches every vector it sees", 24),
        ["round 101: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 101: the library caches every vector it sees", 32),
        ["round 101: the library caches", "every vector it sees"],
    ),
    (
        ("round 101: agents argue then the debate resolves", 4),
        ["round", "101:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 101: agents argue then the debate resolves", 8),
        ["round", "101:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 101: agents argue then the debate resolves", 12),
        ["round 101:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 101: agents argue then the debate resolves", 16),
        ["round 101:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 101: agents argue then the debate resolves", 24), ["round 101: agents argue", "then the debate resolves"]),
    (("round 101: agents argue then the debate resolves", 32), ["round 101: agents argue then the", "debate resolves"]),
    (
        ("round 101: the filter keeps only strong matches", 4),
        ["round", "101:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 101: the filter keeps only strong matches", 8),
        ["round", "101: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 101: the filter keeps only strong matches", 12),
        ["round 101:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 101: the filter keeps only strong matches", 16),
        ["round 101: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 101: the filter keeps only strong matches", 24),
        ["round 101: the filter", "keeps only strong", "matches"],
    ),
    (("round 101: the filter keeps only strong matches", 32), ["round 101: the filter keeps only", "strong matches"]),
    (
        ("round 101: the model answers with a short reply", 4),
        ["round", "101:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 101: the model answers with a short reply", 8),
        ["round", "101: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 101: the model answers with a short reply", 12),
        ["round 101:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 101: the model answers with a short reply", 16),
        ["round 101: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 101: the model answers with a short reply", 24),
        ["round 101: the model", "answers with a short", "reply"],
    ),
    (("round 101: the model answers with a short reply", 32), ["round 101: the model answers", "with a short reply"]),
    (
        ("round 101: the recorder stores the reasoning trace", 4),
        ["round", "101:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 101: the recorder stores the reasoning trace", 8),
        ["round", "101: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 101: the recorder stores the reasoning trace", 12),
        ["round 101:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 101: the recorder stores the reasoning trace", 16),
        ["round 101: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 101: the recorder stores the reasoning trace", 24),
        ["round 101: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 101: the recorder stores the reasoning trace", 32),
        ["round 101: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 101: the angel watches the processor run", 4),
        ["round", "101:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 101: the angel watches the processor run", 8),
        ["round", "101: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 101: the angel watches the processor run", 12),
        ["round 101:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 101: the angel watches the processor run", 16),
        ["round 101: the", "angel watches", "the processor", "run"],
    ),
    (("round 101: the angel watches the processor run", 24), ["round 101: the angel", "watches the processor", "run"]),
    (("round 101: the angel watches the processor run", 32), ["round 101: the angel watches the", "processor run"]),
    (
        ("round 101: angle of the vector decides the match", 4),
        ["round", "101:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 101: angle of the vector decides the match", 8),
        ["round", "101:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 101: angle of the vector decides the match", 12),
        ["round 101:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 101: angle of the vector decides the match", 16),
        ["round 101: angle", "of the vector", "decides the", "match"],
    ),
    (("round 101: angle of the vector decides the match", 24), ["round 101: angle of the", "vector decides the match"]),
    (("round 101: angle of the vector decides the match", 32), ["round 101: angle of the vector", "decides the match"]),
    (
        ("round 101: the candle burns twice as long at night", 4),
        ["round", "101:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 101: the candle burns twice as long at night", 8),
        ["round", "101: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 101: the candle burns twice as long at night", 12),
        ["round 101:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 101: the candle burns twice as long at night", 16),
        ["round 101: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 101: the candle burns twice as long at night", 24),
        ["round 101: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 101: the candle burns twice as long at night", 32),
        ["round 101: the candle burns", "twice as long at night"],
    ),
    (
        ("round 101: a mirror of the universe in one line", 4),
        ["round", "101:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 101: a mirror of the universe in one line", 8),
        ["round", "101: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 101: a mirror of the universe in one line", 12),
        ["round 101: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 101: a mirror of the universe in one line", 16),
        ["round 101: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 101: a mirror of the universe in one line", 24), ["round 101: a mirror of", "the universe in one line"]),
    (("round 101: a mirror of the universe in one line", 32), ["round 101: a mirror of the", "universe in one line"]),
    (
        ("round 101: the queue drains before the storm", 4),
        ["round", "101:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 101: the queue drains before the storm", 8),
        ["round", "101: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 101: the queue drains before the storm", 12),
        ["round 101:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 101: the queue drains before the storm", 16), ["round 101: the", "queue drains", "before the storm"]),
    (("round 101: the queue drains before the storm", 24), ["round 101: the queue", "drains before the storm"]),
    (("round 101: the queue drains before the storm", 32), ["round 101: the queue drains", "before the storm"]),
    (
        ("kitten101 sitting101 agent101 angle101 universe101 memory101", 6),
        ["kitten101", "sitting101", "agent101", "angle101", "universe101", "memory101"],
    ),
    (
        ("kitten101 sitting101 agent101 angle101 universe101 memory101", 10),
        ["kitten101", "sitting101", "agent101", "angle101", "universe101", "memory101"],
    ),
    (
        ("kitten101 sitting101 agent101 angle101 universe101 memory101", 18),
        ["kitten101", "sitting101", "agent101 angle101", "universe101", "memory101"],
    ),
    (
        ("kitten101 sitting101 agent101 angle101 universe101 memory101", 28),
        ["kitten101 sitting101", "agent101 angle101", "universe101 memory101"],
    ),
    (
        ("sitting101 agent101 angle101 universe101 memory101 stream101", 6),
        ["sitting101", "agent101", "angle101", "universe101", "memory101", "stream101"],
    ),
    (
        ("sitting101 agent101 angle101 universe101 memory101 stream101", 10),
        ["sitting101", "agent101", "angle101", "universe101", "memory101", "stream101"],
    ),
    (
        ("sitting101 agent101 angle101 universe101 memory101 stream101", 18),
        ["sitting101", "agent101 angle101", "universe101", "memory101", "stream101"],
    ),
    (
        ("sitting101 agent101 angle101 universe101 memory101 stream101", 28),
        ["sitting101 agent101 angle101", "universe101 memory101", "stream101"],
    ),
    (
        ("agent101 angle101 universe101 memory101 stream101 context101", 6),
        ["agent101", "angle101", "universe101", "memory101", "stream101", "context101"],
    ),
    (
        ("agent101 angle101 universe101 memory101 stream101 context101", 10),
        ["agent101", "angle101", "universe101", "memory101", "stream101", "context101"],
    ),
    (
        ("agent101 angle101 universe101 memory101 stream101 context101", 18),
        ["agent101 angle101", "universe101", "memory101", "stream101", "context101"],
    ),
    (
        ("agent101 angle101 universe101 memory101 stream101 context101", 28),
        ["agent101 angle101", "universe101 memory101", "stream101 context101"],
    ),
    (
        ("angle101 universe101 memory101 stream101 context101 knowledge101", 6),
        ["angle101", "universe101", "memory101", "stream101", "context101", "knowledge101"],
    ),
    (
        ("angle101 universe101 memory101 stream101 context101 knowledge101", 10),
        ["angle101", "universe101", "memory101", "stream101", "context101", "knowledge101"],
    ),
    (
        ("angle101 universe101 memory101 stream101 context101 knowledge101", 18),
        ["angle101", "universe101", "memory101", "stream101", "context101", "knowledge101"],
    ),
    (
        ("angle101 universe101 memory101 stream101 context101 knowledge101", 28),
        ["angle101 universe101", "memory101 stream101", "context101 knowledge101"],
    ),
    (
        ("universe101 memory101 stream101 context101 knowledge101 vector101", 6),
        ["universe101", "memory101", "stream101", "context101", "knowledge101", "vector101"],
    ),
    (
        ("universe101 memory101 stream101 context101 knowledge101 vector101", 10),
        ["universe101", "memory101", "stream101", "context101", "knowledge101", "vector101"],
    ),
    (
        ("universe101 memory101 stream101 context101 knowledge101 vector101", 18),
        ["universe101", "memory101", "stream101", "context101", "knowledge101", "vector101"],
    ),
    (
        ("universe101 memory101 stream101 context101 knowledge101 vector101", 28),
        ["universe101 memory101", "stream101 context101", "knowledge101 vector101"],
    ),
    (
        ("memory101 stream101 context101 knowledge101 vector101 processor101", 6),
        ["memory101", "stream101", "context101", "knowledge101", "vector101", "processor101"],
    ),
    (
        ("memory101 stream101 context101 knowledge101 vector101 processor101", 10),
        ["memory101", "stream101", "context101", "knowledge101", "vector101", "processor101"],
    ),
    (
        ("memory101 stream101 context101 knowledge101 vector101 processor101", 18),
        ["memory101", "stream101", "context101", "knowledge101", "vector101", "processor101"],
    ),
    (
        ("memory101 stream101 context101 knowledge101 vector101 processor101", 28),
        ["memory101 stream101", "context101 knowledge101", "vector101 processor101"],
    ),
    (
        ("stream101 context101 knowledge101 vector101 processor101 reasoning101", 6),
        ["stream101", "context101", "knowledge101", "vector101", "processor101", "reasoning101"],
    ),
    (
        ("stream101 context101 knowledge101 vector101 processor101 reasoning101", 10),
        ["stream101", "context101", "knowledge101", "vector101", "processor101", "reasoning101"],
    ),
    (
        ("stream101 context101 knowledge101 vector101 processor101 reasoning101", 18),
        ["stream101", "context101", "knowledge101", "vector101", "processor101", "reasoning101"],
    ),
    (
        ("stream101 context101 knowledge101 vector101 processor101 reasoning101", 28),
        ["stream101 context101", "knowledge101 vector101", "processor101 reasoning101"],
    ),
    (
        ("context101 knowledge101 vector101 processor101 reasoning101 machine101", 6),
        ["context101", "knowledge101", "vector101", "processor101", "reasoning101", "machine101"],
    ),
    (
        ("context101 knowledge101 vector101 processor101 reasoning101 machine101", 10),
        ["context101", "knowledge101", "vector101", "processor101", "reasoning101", "machine101"],
    ),
    (
        ("context101 knowledge101 vector101 processor101 reasoning101 machine101", 18),
        ["context101", "knowledge101", "vector101", "processor101", "reasoning101", "machine101"],
    ),
    (
        ("context101 knowledge101 vector101 processor101 reasoning101 machine101", 28),
        ["context101 knowledge101", "vector101 processor101", "reasoning101 machine101"],
    ),
    (
        ("knowledge101 vector101 processor101 reasoning101 machine101 learning101", 6),
        ["knowledge101", "vector101", "processor101", "reasoning101", "machine101", "learning101"],
    ),
    (
        ("knowledge101 vector101 processor101 reasoning101 machine101 learning101", 10),
        ["knowledge101", "vector101", "processor101", "reasoning101", "machine101", "learning101"],
    ),
    (
        ("knowledge101 vector101 processor101 reasoning101 machine101 learning101", 18),
        ["knowledge101", "vector101", "processor101", "reasoning101", "machine101", "learning101"],
    ),
    (
        ("knowledge101 vector101 processor101 reasoning101 machine101 learning101", 28),
        ["knowledge101 vector101", "processor101 reasoning101", "machine101 learning101"],
    ),
    (
        ("vector101 processor101 reasoning101 machine101 learning101 model101", 6),
        ["vector101", "processor101", "reasoning101", "machine101", "learning101", "model101"],
    ),
    (
        ("vector101 processor101 reasoning101 machine101 learning101 model101", 10),
        ["vector101", "processor101", "reasoning101", "machine101", "learning101", "model101"],
    ),
    (
        ("vector101 processor101 reasoning101 machine101 learning101 model101", 18),
        ["vector101", "processor101", "reasoning101", "machine101", "learning101", "model101"],
    ),
    (
        ("vector101 processor101 reasoning101 machine101 learning101 model101", 28),
        ["vector101 processor101", "reasoning101 machine101", "learning101 model101"],
    ),
    (
        ("processor101 reasoning101 machine101 learning101 model101 token101", 6),
        ["processor101", "reasoning101", "machine101", "learning101", "model101", "token101"],
    ),
    (
        ("processor101 reasoning101 machine101 learning101 model101 token101", 10),
        ["processor101", "reasoning101", "machine101", "learning101", "model101", "token101"],
    ),
    (
        ("processor101 reasoning101 machine101 learning101 model101 token101", 18),
        ["processor101", "reasoning101", "machine101", "learning101", "model101 token101"],
    ),
    (
        ("processor101 reasoning101 machine101 learning101 model101 token101", 28),
        ["processor101 reasoning101", "machine101 learning101", "model101 token101"],
    ),
    (
        ("reasoning101 machine101 learning101 model101 token101 prompt101", 6),
        ["reasoning101", "machine101", "learning101", "model101", "token101", "prompt101"],
    ),
    (
        ("reasoning101 machine101 learning101 model101 token101 prompt101", 10),
        ["reasoning101", "machine101", "learning101", "model101", "token101", "prompt101"],
    ),
    (
        ("reasoning101 machine101 learning101 model101 token101 prompt101", 18),
        ["reasoning101", "machine101", "learning101", "model101 token101", "prompt101"],
    ),
    (
        ("reasoning101 machine101 learning101 model101 token101 prompt101", 28),
        ["reasoning101 machine101", "learning101 model101", "token101 prompt101"],
    ),
    (
        ("machine101 learning101 model101 token101 prompt101 session101", 6),
        ["machine101", "learning101", "model101", "token101", "prompt101", "session101"],
    ),
    (
        ("machine101 learning101 model101 token101 prompt101 session101", 10),
        ["machine101", "learning101", "model101", "token101", "prompt101", "session101"],
    ),
    (
        ("machine101 learning101 model101 token101 prompt101 session101", 18),
        ["machine101", "learning101", "model101 token101", "prompt101", "session101"],
    ),
    (
        ("machine101 learning101 model101 token101 prompt101 session101", 28),
        ["machine101 learning101", "model101 token101 prompt101", "session101"],
    ),
    (
        ("learning101 model101 token101 prompt101 session101 library101", 6),
        ["learning101", "model101", "token101", "prompt101", "session101", "library101"],
    ),
    (
        ("learning101 model101 token101 prompt101 session101 library101", 10),
        ["learning101", "model101", "token101", "prompt101", "session101", "library101"],
    ),
    (
        ("learning101 model101 token101 prompt101 session101 library101", 18),
        ["learning101", "model101 token101", "prompt101", "session101", "library101"],
    ),
    (
        ("learning101 model101 token101 prompt101 session101 library101", 28),
        ["learning101 model101", "token101 prompt101", "session101 library101"],
    ),
    (
        ("model101 token101 prompt101 session101 library101 service101", 6),
        ["model101", "token101", "prompt101", "session101", "library101", "service101"],
    ),
    (
        ("model101 token101 prompt101 session101 library101 service101", 10),
        ["model101", "token101", "prompt101", "session101", "library101", "service101"],
    ),
    (
        ("model101 token101 prompt101 session101 library101 service101", 18),
        ["model101 token101", "prompt101", "session101", "library101", "service101"],
    ),
    (
        ("model101 token101 prompt101 session101 library101 service101", 28),
        ["model101 token101 prompt101", "session101 library101", "service101"],
    ),
    (
        ("token101 prompt101 session101 library101 service101 gateway101", 6),
        ["token101", "prompt101", "session101", "library101", "service101", "gateway101"],
    ),
    (
        ("token101 prompt101 session101 library101 service101 gateway101", 10),
        ["token101", "prompt101", "session101", "library101", "service101", "gateway101"],
    ),
    (
        ("token101 prompt101 session101 library101 service101 gateway101", 18),
        ["token101 prompt101", "session101", "library101", "service101", "gateway101"],
    ),
    (
        ("token101 prompt101 session101 library101 service101 gateway101", 28),
        ["token101 prompt101", "session101 library101", "service101 gateway101"],
    ),
    (
        ("prompt101 session101 library101 service101 gateway101 storage101", 6),
        ["prompt101", "session101", "library101", "service101", "gateway101", "storage101"],
    ),
    (
        ("prompt101 session101 library101 service101 gateway101 storage101", 10),
        ["prompt101", "session101", "library101", "service101", "gateway101", "storage101"],
    ),
    (
        ("prompt101 session101 library101 service101 gateway101 storage101", 18),
        ["prompt101", "session101", "library101", "service101", "gateway101", "storage101"],
    ),
    (
        ("prompt101 session101 library101 service101 gateway101 storage101", 28),
        ["prompt101 session101", "library101 service101", "gateway101 storage101"],
    ),
    (
        ("session101 library101 service101 gateway101 storage101 network101", 6),
        ["session101", "library101", "service101", "gateway101", "storage101", "network101"],
    ),
    (
        ("session101 library101 service101 gateway101 storage101 network101", 10),
        ["session101", "library101", "service101", "gateway101", "storage101", "network101"],
    ),
    (
        ("session101 library101 service101 gateway101 storage101 network101", 18),
        ["session101", "library101", "service101", "gateway101", "storage101", "network101"],
    ),
    (
        ("session101 library101 service101 gateway101 storage101 network101", 28),
        ["session101 library101", "service101 gateway101", "storage101 network101"],
    ),
    (
        ("library101 service101 gateway101 storage101 network101 latency101", 6),
        ["library101", "service101", "gateway101", "storage101", "network101", "latency101"],
    ),
    (
        ("library101 service101 gateway101 storage101 network101 latency101", 10),
        ["library101", "service101", "gateway101", "storage101", "network101", "latency101"],
    ),
    (
        ("library101 service101 gateway101 storage101 network101 latency101", 18),
        ["library101", "service101", "gateway101", "storage101", "network101", "latency101"],
    ),
    (
        ("library101 service101 gateway101 storage101 network101 latency101", 28),
        ["library101 service101", "gateway101 storage101", "network101 latency101"],
    ),
    (
        ("service101 gateway101 storage101 network101 latency101 buffer101", 6),
        ["service101", "gateway101", "storage101", "network101", "latency101", "buffer101"],
    ),
    (
        ("service101 gateway101 storage101 network101 latency101 buffer101", 10),
        ["service101", "gateway101", "storage101", "network101", "latency101", "buffer101"],
    ),
    (
        ("service101 gateway101 storage101 network101 latency101 buffer101", 18),
        ["service101", "gateway101", "storage101", "network101", "latency101", "buffer101"],
    ),
    (
        ("service101 gateway101 storage101 network101 latency101 buffer101", 28),
        ["service101 gateway101", "storage101 network101", "latency101 buffer101"],
    ),
    (
        ("gateway101 storage101 network101 latency101 buffer101 queue101", 6),
        ["gateway101", "storage101", "network101", "latency101", "buffer101", "queue101"],
    ),
    (
        ("gateway101 storage101 network101 latency101 buffer101 queue101", 10),
        ["gateway101", "storage101", "network101", "latency101", "buffer101", "queue101"],
    ),
    (
        ("gateway101 storage101 network101 latency101 buffer101 queue101", 18),
        ["gateway101", "storage101", "network101", "latency101", "buffer101 queue101"],
    ),
    (
        ("gateway101 storage101 network101 latency101 buffer101 queue101", 28),
        ["gateway101 storage101", "network101 latency101", "buffer101 queue101"],
    ),
    (
        ("storage101 network101 latency101 buffer101 queue101 worker101", 6),
        ["storage101", "network101", "latency101", "buffer101", "queue101", "worker101"],
    ),
    (
        ("storage101 network101 latency101 buffer101 queue101 worker101", 10),
        ["storage101", "network101", "latency101", "buffer101", "queue101", "worker101"],
    ),
    (
        ("storage101 network101 latency101 buffer101 queue101 worker101", 18),
        ["storage101", "network101", "latency101", "buffer101 queue101", "worker101"],
    ),
    (
        ("storage101 network101 latency101 buffer101 queue101 worker101", 28),
        ["storage101 network101", "latency101 buffer101", "queue101 worker101"],
    ),
    (
        ("network101 latency101 buffer101 queue101 worker101 kernel101", 6),
        ["network101", "latency101", "buffer101", "queue101", "worker101", "kernel101"],
    ),
    (
        ("network101 latency101 buffer101 queue101 worker101 kernel101", 10),
        ["network101", "latency101", "buffer101", "queue101", "worker101", "kernel101"],
    ),
    (
        ("network101 latency101 buffer101 queue101 worker101 kernel101", 18),
        ["network101", "latency101", "buffer101 queue101", "worker101", "kernel101"],
    ),
    (
        ("network101 latency101 buffer101 queue101 worker101 kernel101", 28),
        ["network101 latency101", "buffer101 queue101 worker101", "kernel101"],
    ),
    (
        ("latency101 buffer101 queue101 worker101 kernel101 signal101", 6),
        ["latency101", "buffer101", "queue101", "worker101", "kernel101", "signal101"],
    ),
    (
        ("latency101 buffer101 queue101 worker101 kernel101 signal101", 10),
        ["latency101", "buffer101", "queue101", "worker101", "kernel101", "signal101"],
    ),
    (
        ("latency101 buffer101 queue101 worker101 kernel101 signal101", 18),
        ["latency101", "buffer101 queue101", "worker101", "kernel101", "signal101"],
    ),
    (
        ("latency101 buffer101 queue101 worker101 kernel101 signal101", 28),
        ["latency101 buffer101", "queue101 worker101 kernel101", "signal101"],
    ),
    (
        ("buffer101 queue101 worker101 kernel101 signal101 packet101", 6),
        ["buffer101", "queue101", "worker101", "kernel101", "signal101", "packet101"],
    ),
    (
        ("buffer101 queue101 worker101 kernel101 signal101 packet101", 10),
        ["buffer101", "queue101", "worker101", "kernel101", "signal101", "packet101"],
    ),
    (
        ("buffer101 queue101 worker101 kernel101 signal101 packet101", 18),
        ["buffer101 queue101", "worker101", "kernel101", "signal101", "packet101"],
    ),
    (
        ("buffer101 queue101 worker101 kernel101 signal101 packet101", 28),
        ["buffer101 queue101 worker101", "kernel101 signal101", "packet101"],
    ),
    (
        ("queue101 worker101 kernel101 signal101 packet101 router101", 6),
        ["queue101", "worker101", "kernel101", "signal101", "packet101", "router101"],
    ),
    (
        ("queue101 worker101 kernel101 signal101 packet101 router101", 10),
        ["queue101", "worker101", "kernel101", "signal101", "packet101", "router101"],
    ),
    (
        ("queue101 worker101 kernel101 signal101 packet101 router101", 18),
        ["queue101 worker101", "kernel101", "signal101", "packet101", "router101"],
    ),
    (
        ("queue101 worker101 kernel101 signal101 packet101 router101", 28),
        ["queue101 worker101 kernel101", "signal101 packet101", "router101"],
    ),
    (
        ("worker101 kernel101 signal101 packet101 router101 cluster101", 6),
        ["worker101", "kernel101", "signal101", "packet101", "router101", "cluster101"],
    ),
    (
        ("worker101 kernel101 signal101 packet101 router101 cluster101", 10),
        ["worker101", "kernel101", "signal101", "packet101", "router101", "cluster101"],
    ),
    (
        ("worker101 kernel101 signal101 packet101 router101 cluster101", 18),
        ["worker101", "kernel101", "signal101", "packet101", "router101", "cluster101"],
    ),
    (
        ("worker101 kernel101 signal101 packet101 router101 cluster101", 28),
        ["worker101 kernel101", "signal101 packet101", "router101 cluster101"],
    ),
    (
        ("kernel101 signal101 packet101 router101 cluster101 mirror101", 6),
        ["kernel101", "signal101", "packet101", "router101", "cluster101", "mirror101"],
    ),
    (
        ("kernel101 signal101 packet101 router101 cluster101 mirror101", 10),
        ["kernel101", "signal101", "packet101", "router101", "cluster101", "mirror101"],
    ),
    (
        ("kernel101 signal101 packet101 router101 cluster101 mirror101", 18),
        ["kernel101", "signal101", "packet101", "router101", "cluster101", "mirror101"],
    ),
    (
        ("kernel101 signal101 packet101 router101 cluster101 mirror101", 28),
        ["kernel101 signal101", "packet101 router101", "cluster101 mirror101"],
    ),
    (
        ("signal101 packet101 router101 cluster101 mirror101 filter101", 6),
        ["signal101", "packet101", "router101", "cluster101", "mirror101", "filter101"],
    ),
    (
        ("signal101 packet101 router101 cluster101 mirror101 filter101", 10),
        ["signal101", "packet101", "router101", "cluster101", "mirror101", "filter101"],
    ),
    (
        ("signal101 packet101 router101 cluster101 mirror101 filter101", 18),
        ["signal101", "packet101", "router101", "cluster101", "mirror101", "filter101"],
    ),
    (
        ("signal101 packet101 router101 cluster101 mirror101 filter101", 28),
        ["signal101 packet101", "router101 cluster101", "mirror101 filter101"],
    ),
    (
        ("packet101 router101 cluster101 mirror101 filter101 ranking101", 6),
        ["packet101", "router101", "cluster101", "mirror101", "filter101", "ranking101"],
    ),
    (
        ("packet101 router101 cluster101 mirror101 filter101 ranking101", 10),
        ["packet101", "router101", "cluster101", "mirror101", "filter101", "ranking101"],
    ),
    (
        ("packet101 router101 cluster101 mirror101 filter101 ranking101", 18),
        ["packet101", "router101", "cluster101", "mirror101", "filter101", "ranking101"],
    ),
    (
        ("packet101 router101 cluster101 mirror101 filter101 ranking101", 28),
        ["packet101 router101", "cluster101 mirror101", "filter101 ranking101"],
    ),
    (
        ("router101 cluster101 mirror101 filter101 ranking101 encoding101", 6),
        ["router101", "cluster101", "mirror101", "filter101", "ranking101", "encoding101"],
    ),
    (
        ("router101 cluster101 mirror101 filter101 ranking101 encoding101", 10),
        ["router101", "cluster101", "mirror101", "filter101", "ranking101", "encoding101"],
    ),
    (
        ("router101 cluster101 mirror101 filter101 ranking101 encoding101", 18),
        ["router101", "cluster101", "mirror101", "filter101", "ranking101", "encoding101"],
    ),
    (
        ("router101 cluster101 mirror101 filter101 ranking101 encoding101", 28),
        ["router101 cluster101", "mirror101 filter101", "ranking101 encoding101"],
    ),
    (
        ("cluster101 mirror101 filter101 ranking101 encoding101 mapping101", 6),
        ["cluster101", "mirror101", "filter101", "ranking101", "encoding101", "mapping101"],
    ),
    (
        ("cluster101 mirror101 filter101 ranking101 encoding101 mapping101", 10),
        ["cluster101", "mirror101", "filter101", "ranking101", "encoding101", "mapping101"],
    ),
    (
        ("cluster101 mirror101 filter101 ranking101 encoding101 mapping101", 18),
        ["cluster101", "mirror101", "filter101", "ranking101", "encoding101", "mapping101"],
    ),
    (
        ("cluster101 mirror101 filter101 ranking101 encoding101 mapping101", 28),
        ["cluster101 mirror101", "filter101 ranking101", "encoding101 mapping101"],
    ),
    (
        ("mirror101 filter101 ranking101 encoding101 mapping101 record101", 6),
        ["mirror101", "filter101", "ranking101", "encoding101", "mapping101", "record101"],
    ),
    (
        ("mirror101 filter101 ranking101 encoding101 mapping101 record101", 10),
        ["mirror101", "filter101", "ranking101", "encoding101", "mapping101", "record101"],
    ),
    (
        ("mirror101 filter101 ranking101 encoding101 mapping101 record101", 18),
        ["mirror101", "filter101", "ranking101", "encoding101", "mapping101", "record101"],
    ),
    (
        ("mirror101 filter101 ranking101 encoding101 mapping101 record101", 28),
        ["mirror101 filter101", "ranking101 encoding101", "mapping101 record101"],
    ),
    (
        ("filter101 ranking101 encoding101 mapping101 record101 candle101", 6),
        ["filter101", "ranking101", "encoding101", "mapping101", "record101", "candle101"],
    ),
    (
        ("filter101 ranking101 encoding101 mapping101 record101 candle101", 10),
        ["filter101", "ranking101", "encoding101", "mapping101", "record101", "candle101"],
    ),
    (
        ("filter101 ranking101 encoding101 mapping101 record101 candle101", 18),
        ["filter101", "ranking101", "encoding101", "mapping101", "record101", "candle101"],
    ),
    (
        ("filter101 ranking101 encoding101 mapping101 record101 candle101", 28),
        ["filter101 ranking101", "encoding101 mapping101", "record101 candle101"],
    ),
    (
        ("ranking101 encoding101 mapping101 record101 candle101 thread101", 6),
        ["ranking101", "encoding101", "mapping101", "record101", "candle101", "thread101"],
    ),
    (
        ("ranking101 encoding101 mapping101 record101 candle101 thread101", 10),
        ["ranking101", "encoding101", "mapping101", "record101", "candle101", "thread101"],
    ),
    (
        ("ranking101 encoding101 mapping101 record101 candle101 thread101", 18),
        ["ranking101", "encoding101", "mapping101", "record101", "candle101", "thread101"],
    ),
    (
        ("ranking101 encoding101 mapping101 record101 candle101 thread101", 28),
        ["ranking101 encoding101", "mapping101 record101", "candle101 thread101"],
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
