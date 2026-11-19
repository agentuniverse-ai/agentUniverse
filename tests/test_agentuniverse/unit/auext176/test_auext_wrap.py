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
        ("round 176: the quick brown fox jumps over the lazy dog", 4),
        ["round", "176:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 176: the quick brown fox jumps over the lazy dog", 8),
        ["round", "176: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 176: the quick brown fox jumps over the lazy dog", 12),
        ["round 176:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 176: the quick brown fox jumps over the lazy dog", 16),
        ["round 176: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 176: the quick brown fox jumps over the lazy dog", 24),
        ["round 176: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 176: the quick brown fox jumps over the lazy dog", 32),
        ["round 176: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 176: agentuniverse is a framework for multi agents", 4),
        ["round", "176:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 176: agentuniverse is a framework for multi agents", 8),
        ["round", "176:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 176: agentuniverse is a framework for multi agents", 12),
        ["round 176:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 176: agentuniverse is a framework for multi agents", 16),
        ["round 176:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 176: agentuniverse is a framework for multi agents", 24),
        ["round 176: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 176: agentuniverse is a framework for multi agents", 32),
        ["round 176: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 176: knowledge stored as vectors enables retrieval", 4),
        ["round", "176:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 176: knowledge stored as vectors enables retrieval", 8),
        ["round", "176:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 176: knowledge stored as vectors enables retrieval", 12),
        ["round 176:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 176: knowledge stored as vectors enables retrieval", 16),
        ["round 176:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 176: knowledge stored as vectors enables retrieval", 24),
        ["round 176: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 176: knowledge stored as vectors enables retrieval", 32),
        ["round 176: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 176: the processor reads the record then stops", 4),
        ["round", "176:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 176: the processor reads the record then stops", 8),
        ["round", "176: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 176: the processor reads the record then stops", 12),
        ["round 176:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 176: the processor reads the record then stops", 16),
        ["round 176: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 176: the processor reads the record then stops", 24),
        ["round 176: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 176: the processor reads the record then stops", 32),
        ["round 176: the processor reads", "the record then stops"],
    ),
    (
        ("round 176: a worker pulls the next task from the queue", 4),
        ["round", "176:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 176: a worker pulls the next task from the queue", 8),
        ["round", "176: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 176: a worker pulls the next task from the queue", 12),
        ["round 176: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 176: a worker pulls the next task from the queue", 16),
        ["round 176: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 176: a worker pulls the next task from the queue", 24),
        ["round 176: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 176: a worker pulls the next task from the queue", 32),
        ["round 176: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 176: signals travel through the network layer", 4),
        ["round", "176:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 176: signals travel through the network layer", 8),
        ["round", "176:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 176: signals travel through the network layer", 12),
        ["round 176:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 176: signals travel through the network layer", 16),
        ["round 176:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 176: signals travel through the network layer", 24),
        ["round 176: signals", "travel through the", "network layer"],
    ),
    (
        ("round 176: signals travel through the network layer", 32),
        ["round 176: signals travel", "through the network layer"],
    ),
    (
        ("round 176: the gateway routes each request by policy", 4),
        ["round", "176:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 176: the gateway routes each request by policy", 8),
        ["round", "176: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 176: the gateway routes each request by policy", 12),
        ["round 176:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 176: the gateway routes each request by policy", 16),
        ["round 176: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 176: the gateway routes each request by policy", 24),
        ["round 176: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 176: the gateway routes each request by policy", 32),
        ["round 176: the gateway routes", "each request by policy"],
    ),
    (
        ("round 176: memory grows until the buffer is full", 4),
        ["round", "176:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 176: memory grows until the buffer is full", 8),
        ["round", "176:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 176: memory grows until the buffer is full", 12),
        ["round 176:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 176: memory grows until the buffer is full", 16),
        ["round 176:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 176: memory grows until the buffer is full", 24), ["round 176: memory grows", "until the buffer is full"]),
    (("round 176: memory grows until the buffer is full", 32), ["round 176: memory grows until", "the buffer is full"]),
    (
        ("round 176: the cluster mirrors every packet twice", 4),
        ["round", "176:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 176: the cluster mirrors every packet twice", 8),
        ["round", "176: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 176: the cluster mirrors every packet twice", 12),
        ["round 176:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 176: the cluster mirrors every packet twice", 16),
        ["round 176: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 176: the cluster mirrors every packet twice", 24),
        ["round 176: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 176: the cluster mirrors every packet twice", 32),
        ["round 176: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 176: ranking uses tokens learned from the corpus", 4),
        ["round", "176:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 176: ranking uses tokens learned from the corpus", 8),
        ["round", "176:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 176: ranking uses tokens learned from the corpus", 12),
        ["round 176:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 176: ranking uses tokens learned from the corpus", 16),
        ["round 176:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 176: ranking uses tokens learned from the corpus", 24),
        ["round 176: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 176: ranking uses tokens learned from the corpus", 32),
        ["round 176: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 176: a long session ends when the candle dies", 4),
        ["round", "176:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 176: a long session ends when the candle dies", 8),
        ["round", "176: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 176: a long session ends when the candle dies", 12),
        ["round 176: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 176: a long session ends when the candle dies", 16),
        ["round 176: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 176: a long session ends when the candle dies", 24),
        ["round 176: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 176: a long session ends when the candle dies", 32),
        ["round 176: a long session ends", "when the candle dies"],
    ),
    (
        ("round 176: encode the prompt then map the result", 4),
        ["round", "176:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 176: encode the prompt then map the result", 8),
        ["round", "176:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 176: encode the prompt then map the result", 12),
        ["round 176:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 176: encode the prompt then map the result", 16),
        ["round 176:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 176: encode the prompt then map the result", 24),
        ["round 176: encode the", "prompt then map the", "result"],
    ),
    (("round 176: encode the prompt then map the result", 32), ["round 176: encode the prompt", "then map the result"]),
    (
        ("round 176: the kernel wakes the worker at dawn", 4),
        ["round", "176:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 176: the kernel wakes the worker at dawn", 8),
        ["round", "176: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 176: the kernel wakes the worker at dawn", 12),
        ["round 176:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 176: the kernel wakes the worker at dawn", 16), ["round 176: the", "kernel wakes the", "worker at dawn"]),
    (("round 176: the kernel wakes the worker at dawn", 24), ["round 176: the kernel", "wakes the worker at dawn"]),
    (("round 176: the kernel wakes the worker at dawn", 32), ["round 176: the kernel wakes the", "worker at dawn"]),
    (
        ("round 176: service latency drops after the patch", 4),
        ["round", "176:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 176: service latency drops after the patch", 8),
        ["round", "176:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 176: service latency drops after the patch", 12),
        ["round 176:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 176: service latency drops after the patch", 16),
        ["round 176:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 176: service latency drops after the patch", 24),
        ["round 176: service", "latency drops after the", "patch"],
    ),
    (("round 176: service latency drops after the patch", 32), ["round 176: service latency drops", "after the patch"]),
    (
        ("round 176: the library caches every vector it sees", 4),
        ["round", "176:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 176: the library caches every vector it sees", 8),
        ["round", "176: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 176: the library caches every vector it sees", 12),
        ["round 176:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 176: the library caches every vector it sees", 16),
        ["round 176: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 176: the library caches every vector it sees", 24),
        ["round 176: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 176: the library caches every vector it sees", 32),
        ["round 176: the library caches", "every vector it sees"],
    ),
    (
        ("round 176: agents argue then the debate resolves", 4),
        ["round", "176:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 176: agents argue then the debate resolves", 8),
        ["round", "176:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 176: agents argue then the debate resolves", 12),
        ["round 176:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 176: agents argue then the debate resolves", 16),
        ["round 176:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 176: agents argue then the debate resolves", 24), ["round 176: agents argue", "then the debate resolves"]),
    (("round 176: agents argue then the debate resolves", 32), ["round 176: agents argue then the", "debate resolves"]),
    (
        ("round 176: the filter keeps only strong matches", 4),
        ["round", "176:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 176: the filter keeps only strong matches", 8),
        ["round", "176: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 176: the filter keeps only strong matches", 12),
        ["round 176:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 176: the filter keeps only strong matches", 16),
        ["round 176: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 176: the filter keeps only strong matches", 24),
        ["round 176: the filter", "keeps only strong", "matches"],
    ),
    (("round 176: the filter keeps only strong matches", 32), ["round 176: the filter keeps only", "strong matches"]),
    (
        ("round 176: the model answers with a short reply", 4),
        ["round", "176:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 176: the model answers with a short reply", 8),
        ["round", "176: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 176: the model answers with a short reply", 12),
        ["round 176:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 176: the model answers with a short reply", 16),
        ["round 176: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 176: the model answers with a short reply", 24),
        ["round 176: the model", "answers with a short", "reply"],
    ),
    (("round 176: the model answers with a short reply", 32), ["round 176: the model answers", "with a short reply"]),
    (
        ("round 176: the recorder stores the reasoning trace", 4),
        ["round", "176:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 176: the recorder stores the reasoning trace", 8),
        ["round", "176: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 176: the recorder stores the reasoning trace", 12),
        ["round 176:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 176: the recorder stores the reasoning trace", 16),
        ["round 176: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 176: the recorder stores the reasoning trace", 24),
        ["round 176: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 176: the recorder stores the reasoning trace", 32),
        ["round 176: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 176: the angel watches the processor run", 4),
        ["round", "176:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 176: the angel watches the processor run", 8),
        ["round", "176: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 176: the angel watches the processor run", 12),
        ["round 176:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 176: the angel watches the processor run", 16),
        ["round 176: the", "angel watches", "the processor", "run"],
    ),
    (("round 176: the angel watches the processor run", 24), ["round 176: the angel", "watches the processor", "run"]),
    (("round 176: the angel watches the processor run", 32), ["round 176: the angel watches the", "processor run"]),
    (
        ("round 176: angle of the vector decides the match", 4),
        ["round", "176:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 176: angle of the vector decides the match", 8),
        ["round", "176:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 176: angle of the vector decides the match", 12),
        ["round 176:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 176: angle of the vector decides the match", 16),
        ["round 176: angle", "of the vector", "decides the", "match"],
    ),
    (("round 176: angle of the vector decides the match", 24), ["round 176: angle of the", "vector decides the match"]),
    (("round 176: angle of the vector decides the match", 32), ["round 176: angle of the vector", "decides the match"]),
    (
        ("round 176: the candle burns twice as long at night", 4),
        ["round", "176:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 176: the candle burns twice as long at night", 8),
        ["round", "176: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 176: the candle burns twice as long at night", 12),
        ["round 176:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 176: the candle burns twice as long at night", 16),
        ["round 176: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 176: the candle burns twice as long at night", 24),
        ["round 176: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 176: the candle burns twice as long at night", 32),
        ["round 176: the candle burns", "twice as long at night"],
    ),
    (
        ("round 176: a mirror of the universe in one line", 4),
        ["round", "176:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 176: a mirror of the universe in one line", 8),
        ["round", "176: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 176: a mirror of the universe in one line", 12),
        ["round 176: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 176: a mirror of the universe in one line", 16),
        ["round 176: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 176: a mirror of the universe in one line", 24), ["round 176: a mirror of", "the universe in one line"]),
    (("round 176: a mirror of the universe in one line", 32), ["round 176: a mirror of the", "universe in one line"]),
    (
        ("round 176: the queue drains before the storm", 4),
        ["round", "176:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 176: the queue drains before the storm", 8),
        ["round", "176: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 176: the queue drains before the storm", 12),
        ["round 176:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 176: the queue drains before the storm", 16), ["round 176: the", "queue drains", "before the storm"]),
    (("round 176: the queue drains before the storm", 24), ["round 176: the queue", "drains before the storm"]),
    (("round 176: the queue drains before the storm", 32), ["round 176: the queue drains", "before the storm"]),
    (
        ("kitten176 sitting176 agent176 angle176 universe176 memory176", 6),
        ["kitten176", "sitting176", "agent176", "angle176", "universe176", "memory176"],
    ),
    (
        ("kitten176 sitting176 agent176 angle176 universe176 memory176", 10),
        ["kitten176", "sitting176", "agent176", "angle176", "universe176", "memory176"],
    ),
    (
        ("kitten176 sitting176 agent176 angle176 universe176 memory176", 18),
        ["kitten176", "sitting176", "agent176 angle176", "universe176", "memory176"],
    ),
    (
        ("kitten176 sitting176 agent176 angle176 universe176 memory176", 28),
        ["kitten176 sitting176", "agent176 angle176", "universe176 memory176"],
    ),
    (
        ("sitting176 agent176 angle176 universe176 memory176 stream176", 6),
        ["sitting176", "agent176", "angle176", "universe176", "memory176", "stream176"],
    ),
    (
        ("sitting176 agent176 angle176 universe176 memory176 stream176", 10),
        ["sitting176", "agent176", "angle176", "universe176", "memory176", "stream176"],
    ),
    (
        ("sitting176 agent176 angle176 universe176 memory176 stream176", 18),
        ["sitting176", "agent176 angle176", "universe176", "memory176", "stream176"],
    ),
    (
        ("sitting176 agent176 angle176 universe176 memory176 stream176", 28),
        ["sitting176 agent176 angle176", "universe176 memory176", "stream176"],
    ),
    (
        ("agent176 angle176 universe176 memory176 stream176 context176", 6),
        ["agent176", "angle176", "universe176", "memory176", "stream176", "context176"],
    ),
    (
        ("agent176 angle176 universe176 memory176 stream176 context176", 10),
        ["agent176", "angle176", "universe176", "memory176", "stream176", "context176"],
    ),
    (
        ("agent176 angle176 universe176 memory176 stream176 context176", 18),
        ["agent176 angle176", "universe176", "memory176", "stream176", "context176"],
    ),
    (
        ("agent176 angle176 universe176 memory176 stream176 context176", 28),
        ["agent176 angle176", "universe176 memory176", "stream176 context176"],
    ),
    (
        ("angle176 universe176 memory176 stream176 context176 knowledge176", 6),
        ["angle176", "universe176", "memory176", "stream176", "context176", "knowledge176"],
    ),
    (
        ("angle176 universe176 memory176 stream176 context176 knowledge176", 10),
        ["angle176", "universe176", "memory176", "stream176", "context176", "knowledge176"],
    ),
    (
        ("angle176 universe176 memory176 stream176 context176 knowledge176", 18),
        ["angle176", "universe176", "memory176", "stream176", "context176", "knowledge176"],
    ),
    (
        ("angle176 universe176 memory176 stream176 context176 knowledge176", 28),
        ["angle176 universe176", "memory176 stream176", "context176 knowledge176"],
    ),
    (
        ("universe176 memory176 stream176 context176 knowledge176 vector176", 6),
        ["universe176", "memory176", "stream176", "context176", "knowledge176", "vector176"],
    ),
    (
        ("universe176 memory176 stream176 context176 knowledge176 vector176", 10),
        ["universe176", "memory176", "stream176", "context176", "knowledge176", "vector176"],
    ),
    (
        ("universe176 memory176 stream176 context176 knowledge176 vector176", 18),
        ["universe176", "memory176", "stream176", "context176", "knowledge176", "vector176"],
    ),
    (
        ("universe176 memory176 stream176 context176 knowledge176 vector176", 28),
        ["universe176 memory176", "stream176 context176", "knowledge176 vector176"],
    ),
    (
        ("memory176 stream176 context176 knowledge176 vector176 processor176", 6),
        ["memory176", "stream176", "context176", "knowledge176", "vector176", "processor176"],
    ),
    (
        ("memory176 stream176 context176 knowledge176 vector176 processor176", 10),
        ["memory176", "stream176", "context176", "knowledge176", "vector176", "processor176"],
    ),
    (
        ("memory176 stream176 context176 knowledge176 vector176 processor176", 18),
        ["memory176", "stream176", "context176", "knowledge176", "vector176", "processor176"],
    ),
    (
        ("memory176 stream176 context176 knowledge176 vector176 processor176", 28),
        ["memory176 stream176", "context176 knowledge176", "vector176 processor176"],
    ),
    (
        ("stream176 context176 knowledge176 vector176 processor176 reasoning176", 6),
        ["stream176", "context176", "knowledge176", "vector176", "processor176", "reasoning176"],
    ),
    (
        ("stream176 context176 knowledge176 vector176 processor176 reasoning176", 10),
        ["stream176", "context176", "knowledge176", "vector176", "processor176", "reasoning176"],
    ),
    (
        ("stream176 context176 knowledge176 vector176 processor176 reasoning176", 18),
        ["stream176", "context176", "knowledge176", "vector176", "processor176", "reasoning176"],
    ),
    (
        ("stream176 context176 knowledge176 vector176 processor176 reasoning176", 28),
        ["stream176 context176", "knowledge176 vector176", "processor176 reasoning176"],
    ),
    (
        ("context176 knowledge176 vector176 processor176 reasoning176 machine176", 6),
        ["context176", "knowledge176", "vector176", "processor176", "reasoning176", "machine176"],
    ),
    (
        ("context176 knowledge176 vector176 processor176 reasoning176 machine176", 10),
        ["context176", "knowledge176", "vector176", "processor176", "reasoning176", "machine176"],
    ),
    (
        ("context176 knowledge176 vector176 processor176 reasoning176 machine176", 18),
        ["context176", "knowledge176", "vector176", "processor176", "reasoning176", "machine176"],
    ),
    (
        ("context176 knowledge176 vector176 processor176 reasoning176 machine176", 28),
        ["context176 knowledge176", "vector176 processor176", "reasoning176 machine176"],
    ),
    (
        ("knowledge176 vector176 processor176 reasoning176 machine176 learning176", 6),
        ["knowledge176", "vector176", "processor176", "reasoning176", "machine176", "learning176"],
    ),
    (
        ("knowledge176 vector176 processor176 reasoning176 machine176 learning176", 10),
        ["knowledge176", "vector176", "processor176", "reasoning176", "machine176", "learning176"],
    ),
    (
        ("knowledge176 vector176 processor176 reasoning176 machine176 learning176", 18),
        ["knowledge176", "vector176", "processor176", "reasoning176", "machine176", "learning176"],
    ),
    (
        ("knowledge176 vector176 processor176 reasoning176 machine176 learning176", 28),
        ["knowledge176 vector176", "processor176 reasoning176", "machine176 learning176"],
    ),
    (
        ("vector176 processor176 reasoning176 machine176 learning176 model176", 6),
        ["vector176", "processor176", "reasoning176", "machine176", "learning176", "model176"],
    ),
    (
        ("vector176 processor176 reasoning176 machine176 learning176 model176", 10),
        ["vector176", "processor176", "reasoning176", "machine176", "learning176", "model176"],
    ),
    (
        ("vector176 processor176 reasoning176 machine176 learning176 model176", 18),
        ["vector176", "processor176", "reasoning176", "machine176", "learning176", "model176"],
    ),
    (
        ("vector176 processor176 reasoning176 machine176 learning176 model176", 28),
        ["vector176 processor176", "reasoning176 machine176", "learning176 model176"],
    ),
    (
        ("processor176 reasoning176 machine176 learning176 model176 token176", 6),
        ["processor176", "reasoning176", "machine176", "learning176", "model176", "token176"],
    ),
    (
        ("processor176 reasoning176 machine176 learning176 model176 token176", 10),
        ["processor176", "reasoning176", "machine176", "learning176", "model176", "token176"],
    ),
    (
        ("processor176 reasoning176 machine176 learning176 model176 token176", 18),
        ["processor176", "reasoning176", "machine176", "learning176", "model176 token176"],
    ),
    (
        ("processor176 reasoning176 machine176 learning176 model176 token176", 28),
        ["processor176 reasoning176", "machine176 learning176", "model176 token176"],
    ),
    (
        ("reasoning176 machine176 learning176 model176 token176 prompt176", 6),
        ["reasoning176", "machine176", "learning176", "model176", "token176", "prompt176"],
    ),
    (
        ("reasoning176 machine176 learning176 model176 token176 prompt176", 10),
        ["reasoning176", "machine176", "learning176", "model176", "token176", "prompt176"],
    ),
    (
        ("reasoning176 machine176 learning176 model176 token176 prompt176", 18),
        ["reasoning176", "machine176", "learning176", "model176 token176", "prompt176"],
    ),
    (
        ("reasoning176 machine176 learning176 model176 token176 prompt176", 28),
        ["reasoning176 machine176", "learning176 model176", "token176 prompt176"],
    ),
    (
        ("machine176 learning176 model176 token176 prompt176 session176", 6),
        ["machine176", "learning176", "model176", "token176", "prompt176", "session176"],
    ),
    (
        ("machine176 learning176 model176 token176 prompt176 session176", 10),
        ["machine176", "learning176", "model176", "token176", "prompt176", "session176"],
    ),
    (
        ("machine176 learning176 model176 token176 prompt176 session176", 18),
        ["machine176", "learning176", "model176 token176", "prompt176", "session176"],
    ),
    (
        ("machine176 learning176 model176 token176 prompt176 session176", 28),
        ["machine176 learning176", "model176 token176 prompt176", "session176"],
    ),
    (
        ("learning176 model176 token176 prompt176 session176 library176", 6),
        ["learning176", "model176", "token176", "prompt176", "session176", "library176"],
    ),
    (
        ("learning176 model176 token176 prompt176 session176 library176", 10),
        ["learning176", "model176", "token176", "prompt176", "session176", "library176"],
    ),
    (
        ("learning176 model176 token176 prompt176 session176 library176", 18),
        ["learning176", "model176 token176", "prompt176", "session176", "library176"],
    ),
    (
        ("learning176 model176 token176 prompt176 session176 library176", 28),
        ["learning176 model176", "token176 prompt176", "session176 library176"],
    ),
    (
        ("model176 token176 prompt176 session176 library176 service176", 6),
        ["model176", "token176", "prompt176", "session176", "library176", "service176"],
    ),
    (
        ("model176 token176 prompt176 session176 library176 service176", 10),
        ["model176", "token176", "prompt176", "session176", "library176", "service176"],
    ),
    (
        ("model176 token176 prompt176 session176 library176 service176", 18),
        ["model176 token176", "prompt176", "session176", "library176", "service176"],
    ),
    (
        ("model176 token176 prompt176 session176 library176 service176", 28),
        ["model176 token176 prompt176", "session176 library176", "service176"],
    ),
    (
        ("token176 prompt176 session176 library176 service176 gateway176", 6),
        ["token176", "prompt176", "session176", "library176", "service176", "gateway176"],
    ),
    (
        ("token176 prompt176 session176 library176 service176 gateway176", 10),
        ["token176", "prompt176", "session176", "library176", "service176", "gateway176"],
    ),
    (
        ("token176 prompt176 session176 library176 service176 gateway176", 18),
        ["token176 prompt176", "session176", "library176", "service176", "gateway176"],
    ),
    (
        ("token176 prompt176 session176 library176 service176 gateway176", 28),
        ["token176 prompt176", "session176 library176", "service176 gateway176"],
    ),
    (
        ("prompt176 session176 library176 service176 gateway176 storage176", 6),
        ["prompt176", "session176", "library176", "service176", "gateway176", "storage176"],
    ),
    (
        ("prompt176 session176 library176 service176 gateway176 storage176", 10),
        ["prompt176", "session176", "library176", "service176", "gateway176", "storage176"],
    ),
    (
        ("prompt176 session176 library176 service176 gateway176 storage176", 18),
        ["prompt176", "session176", "library176", "service176", "gateway176", "storage176"],
    ),
    (
        ("prompt176 session176 library176 service176 gateway176 storage176", 28),
        ["prompt176 session176", "library176 service176", "gateway176 storage176"],
    ),
    (
        ("session176 library176 service176 gateway176 storage176 network176", 6),
        ["session176", "library176", "service176", "gateway176", "storage176", "network176"],
    ),
    (
        ("session176 library176 service176 gateway176 storage176 network176", 10),
        ["session176", "library176", "service176", "gateway176", "storage176", "network176"],
    ),
    (
        ("session176 library176 service176 gateway176 storage176 network176", 18),
        ["session176", "library176", "service176", "gateway176", "storage176", "network176"],
    ),
    (
        ("session176 library176 service176 gateway176 storage176 network176", 28),
        ["session176 library176", "service176 gateway176", "storage176 network176"],
    ),
    (
        ("library176 service176 gateway176 storage176 network176 latency176", 6),
        ["library176", "service176", "gateway176", "storage176", "network176", "latency176"],
    ),
    (
        ("library176 service176 gateway176 storage176 network176 latency176", 10),
        ["library176", "service176", "gateway176", "storage176", "network176", "latency176"],
    ),
    (
        ("library176 service176 gateway176 storage176 network176 latency176", 18),
        ["library176", "service176", "gateway176", "storage176", "network176", "latency176"],
    ),
    (
        ("library176 service176 gateway176 storage176 network176 latency176", 28),
        ["library176 service176", "gateway176 storage176", "network176 latency176"],
    ),
    (
        ("service176 gateway176 storage176 network176 latency176 buffer176", 6),
        ["service176", "gateway176", "storage176", "network176", "latency176", "buffer176"],
    ),
    (
        ("service176 gateway176 storage176 network176 latency176 buffer176", 10),
        ["service176", "gateway176", "storage176", "network176", "latency176", "buffer176"],
    ),
    (
        ("service176 gateway176 storage176 network176 latency176 buffer176", 18),
        ["service176", "gateway176", "storage176", "network176", "latency176", "buffer176"],
    ),
    (
        ("service176 gateway176 storage176 network176 latency176 buffer176", 28),
        ["service176 gateway176", "storage176 network176", "latency176 buffer176"],
    ),
    (
        ("gateway176 storage176 network176 latency176 buffer176 queue176", 6),
        ["gateway176", "storage176", "network176", "latency176", "buffer176", "queue176"],
    ),
    (
        ("gateway176 storage176 network176 latency176 buffer176 queue176", 10),
        ["gateway176", "storage176", "network176", "latency176", "buffer176", "queue176"],
    ),
    (
        ("gateway176 storage176 network176 latency176 buffer176 queue176", 18),
        ["gateway176", "storage176", "network176", "latency176", "buffer176 queue176"],
    ),
    (
        ("gateway176 storage176 network176 latency176 buffer176 queue176", 28),
        ["gateway176 storage176", "network176 latency176", "buffer176 queue176"],
    ),
    (
        ("storage176 network176 latency176 buffer176 queue176 worker176", 6),
        ["storage176", "network176", "latency176", "buffer176", "queue176", "worker176"],
    ),
    (
        ("storage176 network176 latency176 buffer176 queue176 worker176", 10),
        ["storage176", "network176", "latency176", "buffer176", "queue176", "worker176"],
    ),
    (
        ("storage176 network176 latency176 buffer176 queue176 worker176", 18),
        ["storage176", "network176", "latency176", "buffer176 queue176", "worker176"],
    ),
    (
        ("storage176 network176 latency176 buffer176 queue176 worker176", 28),
        ["storage176 network176", "latency176 buffer176", "queue176 worker176"],
    ),
    (
        ("network176 latency176 buffer176 queue176 worker176 kernel176", 6),
        ["network176", "latency176", "buffer176", "queue176", "worker176", "kernel176"],
    ),
    (
        ("network176 latency176 buffer176 queue176 worker176 kernel176", 10),
        ["network176", "latency176", "buffer176", "queue176", "worker176", "kernel176"],
    ),
    (
        ("network176 latency176 buffer176 queue176 worker176 kernel176", 18),
        ["network176", "latency176", "buffer176 queue176", "worker176", "kernel176"],
    ),
    (
        ("network176 latency176 buffer176 queue176 worker176 kernel176", 28),
        ["network176 latency176", "buffer176 queue176 worker176", "kernel176"],
    ),
    (
        ("latency176 buffer176 queue176 worker176 kernel176 signal176", 6),
        ["latency176", "buffer176", "queue176", "worker176", "kernel176", "signal176"],
    ),
    (
        ("latency176 buffer176 queue176 worker176 kernel176 signal176", 10),
        ["latency176", "buffer176", "queue176", "worker176", "kernel176", "signal176"],
    ),
    (
        ("latency176 buffer176 queue176 worker176 kernel176 signal176", 18),
        ["latency176", "buffer176 queue176", "worker176", "kernel176", "signal176"],
    ),
    (
        ("latency176 buffer176 queue176 worker176 kernel176 signal176", 28),
        ["latency176 buffer176", "queue176 worker176 kernel176", "signal176"],
    ),
    (
        ("buffer176 queue176 worker176 kernel176 signal176 packet176", 6),
        ["buffer176", "queue176", "worker176", "kernel176", "signal176", "packet176"],
    ),
    (
        ("buffer176 queue176 worker176 kernel176 signal176 packet176", 10),
        ["buffer176", "queue176", "worker176", "kernel176", "signal176", "packet176"],
    ),
    (
        ("buffer176 queue176 worker176 kernel176 signal176 packet176", 18),
        ["buffer176 queue176", "worker176", "kernel176", "signal176", "packet176"],
    ),
    (
        ("buffer176 queue176 worker176 kernel176 signal176 packet176", 28),
        ["buffer176 queue176 worker176", "kernel176 signal176", "packet176"],
    ),
    (
        ("queue176 worker176 kernel176 signal176 packet176 router176", 6),
        ["queue176", "worker176", "kernel176", "signal176", "packet176", "router176"],
    ),
    (
        ("queue176 worker176 kernel176 signal176 packet176 router176", 10),
        ["queue176", "worker176", "kernel176", "signal176", "packet176", "router176"],
    ),
    (
        ("queue176 worker176 kernel176 signal176 packet176 router176", 18),
        ["queue176 worker176", "kernel176", "signal176", "packet176", "router176"],
    ),
    (
        ("queue176 worker176 kernel176 signal176 packet176 router176", 28),
        ["queue176 worker176 kernel176", "signal176 packet176", "router176"],
    ),
    (
        ("worker176 kernel176 signal176 packet176 router176 cluster176", 6),
        ["worker176", "kernel176", "signal176", "packet176", "router176", "cluster176"],
    ),
    (
        ("worker176 kernel176 signal176 packet176 router176 cluster176", 10),
        ["worker176", "kernel176", "signal176", "packet176", "router176", "cluster176"],
    ),
    (
        ("worker176 kernel176 signal176 packet176 router176 cluster176", 18),
        ["worker176", "kernel176", "signal176", "packet176", "router176", "cluster176"],
    ),
    (
        ("worker176 kernel176 signal176 packet176 router176 cluster176", 28),
        ["worker176 kernel176", "signal176 packet176", "router176 cluster176"],
    ),
    (
        ("kernel176 signal176 packet176 router176 cluster176 mirror176", 6),
        ["kernel176", "signal176", "packet176", "router176", "cluster176", "mirror176"],
    ),
    (
        ("kernel176 signal176 packet176 router176 cluster176 mirror176", 10),
        ["kernel176", "signal176", "packet176", "router176", "cluster176", "mirror176"],
    ),
    (
        ("kernel176 signal176 packet176 router176 cluster176 mirror176", 18),
        ["kernel176", "signal176", "packet176", "router176", "cluster176", "mirror176"],
    ),
    (
        ("kernel176 signal176 packet176 router176 cluster176 mirror176", 28),
        ["kernel176 signal176", "packet176 router176", "cluster176 mirror176"],
    ),
    (
        ("signal176 packet176 router176 cluster176 mirror176 filter176", 6),
        ["signal176", "packet176", "router176", "cluster176", "mirror176", "filter176"],
    ),
    (
        ("signal176 packet176 router176 cluster176 mirror176 filter176", 10),
        ["signal176", "packet176", "router176", "cluster176", "mirror176", "filter176"],
    ),
    (
        ("signal176 packet176 router176 cluster176 mirror176 filter176", 18),
        ["signal176", "packet176", "router176", "cluster176", "mirror176", "filter176"],
    ),
    (
        ("signal176 packet176 router176 cluster176 mirror176 filter176", 28),
        ["signal176 packet176", "router176 cluster176", "mirror176 filter176"],
    ),
    (
        ("packet176 router176 cluster176 mirror176 filter176 ranking176", 6),
        ["packet176", "router176", "cluster176", "mirror176", "filter176", "ranking176"],
    ),
    (
        ("packet176 router176 cluster176 mirror176 filter176 ranking176", 10),
        ["packet176", "router176", "cluster176", "mirror176", "filter176", "ranking176"],
    ),
    (
        ("packet176 router176 cluster176 mirror176 filter176 ranking176", 18),
        ["packet176", "router176", "cluster176", "mirror176", "filter176", "ranking176"],
    ),
    (
        ("packet176 router176 cluster176 mirror176 filter176 ranking176", 28),
        ["packet176 router176", "cluster176 mirror176", "filter176 ranking176"],
    ),
    (
        ("router176 cluster176 mirror176 filter176 ranking176 encoding176", 6),
        ["router176", "cluster176", "mirror176", "filter176", "ranking176", "encoding176"],
    ),
    (
        ("router176 cluster176 mirror176 filter176 ranking176 encoding176", 10),
        ["router176", "cluster176", "mirror176", "filter176", "ranking176", "encoding176"],
    ),
    (
        ("router176 cluster176 mirror176 filter176 ranking176 encoding176", 18),
        ["router176", "cluster176", "mirror176", "filter176", "ranking176", "encoding176"],
    ),
    (
        ("router176 cluster176 mirror176 filter176 ranking176 encoding176", 28),
        ["router176 cluster176", "mirror176 filter176", "ranking176 encoding176"],
    ),
    (
        ("cluster176 mirror176 filter176 ranking176 encoding176 mapping176", 6),
        ["cluster176", "mirror176", "filter176", "ranking176", "encoding176", "mapping176"],
    ),
    (
        ("cluster176 mirror176 filter176 ranking176 encoding176 mapping176", 10),
        ["cluster176", "mirror176", "filter176", "ranking176", "encoding176", "mapping176"],
    ),
    (
        ("cluster176 mirror176 filter176 ranking176 encoding176 mapping176", 18),
        ["cluster176", "mirror176", "filter176", "ranking176", "encoding176", "mapping176"],
    ),
    (
        ("cluster176 mirror176 filter176 ranking176 encoding176 mapping176", 28),
        ["cluster176 mirror176", "filter176 ranking176", "encoding176 mapping176"],
    ),
    (
        ("mirror176 filter176 ranking176 encoding176 mapping176 record176", 6),
        ["mirror176", "filter176", "ranking176", "encoding176", "mapping176", "record176"],
    ),
    (
        ("mirror176 filter176 ranking176 encoding176 mapping176 record176", 10),
        ["mirror176", "filter176", "ranking176", "encoding176", "mapping176", "record176"],
    ),
    (
        ("mirror176 filter176 ranking176 encoding176 mapping176 record176", 18),
        ["mirror176", "filter176", "ranking176", "encoding176", "mapping176", "record176"],
    ),
    (
        ("mirror176 filter176 ranking176 encoding176 mapping176 record176", 28),
        ["mirror176 filter176", "ranking176 encoding176", "mapping176 record176"],
    ),
    (
        ("filter176 ranking176 encoding176 mapping176 record176 candle176", 6),
        ["filter176", "ranking176", "encoding176", "mapping176", "record176", "candle176"],
    ),
    (
        ("filter176 ranking176 encoding176 mapping176 record176 candle176", 10),
        ["filter176", "ranking176", "encoding176", "mapping176", "record176", "candle176"],
    ),
    (
        ("filter176 ranking176 encoding176 mapping176 record176 candle176", 18),
        ["filter176", "ranking176", "encoding176", "mapping176", "record176", "candle176"],
    ),
    (
        ("filter176 ranking176 encoding176 mapping176 record176 candle176", 28),
        ["filter176 ranking176", "encoding176 mapping176", "record176 candle176"],
    ),
    (
        ("ranking176 encoding176 mapping176 record176 candle176 thread176", 6),
        ["ranking176", "encoding176", "mapping176", "record176", "candle176", "thread176"],
    ),
    (
        ("ranking176 encoding176 mapping176 record176 candle176 thread176", 10),
        ["ranking176", "encoding176", "mapping176", "record176", "candle176", "thread176"],
    ),
    (
        ("ranking176 encoding176 mapping176 record176 candle176 thread176", 18),
        ["ranking176", "encoding176", "mapping176", "record176", "candle176", "thread176"],
    ),
    (
        ("ranking176 encoding176 mapping176 record176 candle176 thread176", 28),
        ["ranking176 encoding176", "mapping176 record176", "candle176 thread176"],
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
