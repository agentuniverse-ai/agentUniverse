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
        ("round 158: the quick brown fox jumps over the lazy dog", 4),
        ["round", "158:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 158: the quick brown fox jumps over the lazy dog", 8),
        ["round", "158: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 158: the quick brown fox jumps over the lazy dog", 12),
        ["round 158:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 158: the quick brown fox jumps over the lazy dog", 16),
        ["round 158: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 158: the quick brown fox jumps over the lazy dog", 24),
        ["round 158: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 158: the quick brown fox jumps over the lazy dog", 32),
        ["round 158: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 158: agentuniverse is a framework for multi agents", 4),
        ["round", "158:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 158: agentuniverse is a framework for multi agents", 8),
        ["round", "158:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 158: agentuniverse is a framework for multi agents", 12),
        ["round 158:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 158: agentuniverse is a framework for multi agents", 16),
        ["round 158:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 158: agentuniverse is a framework for multi agents", 24),
        ["round 158: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 158: agentuniverse is a framework for multi agents", 32),
        ["round 158: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 158: knowledge stored as vectors enables retrieval", 4),
        ["round", "158:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 158: knowledge stored as vectors enables retrieval", 8),
        ["round", "158:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 158: knowledge stored as vectors enables retrieval", 12),
        ["round 158:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 158: knowledge stored as vectors enables retrieval", 16),
        ["round 158:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 158: knowledge stored as vectors enables retrieval", 24),
        ["round 158: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 158: knowledge stored as vectors enables retrieval", 32),
        ["round 158: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 158: the processor reads the record then stops", 4),
        ["round", "158:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 158: the processor reads the record then stops", 8),
        ["round", "158: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 158: the processor reads the record then stops", 12),
        ["round 158:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 158: the processor reads the record then stops", 16),
        ["round 158: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 158: the processor reads the record then stops", 24),
        ["round 158: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 158: the processor reads the record then stops", 32),
        ["round 158: the processor reads", "the record then stops"],
    ),
    (
        ("round 158: a worker pulls the next task from the queue", 4),
        ["round", "158:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 158: a worker pulls the next task from the queue", 8),
        ["round", "158: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 158: a worker pulls the next task from the queue", 12),
        ["round 158: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 158: a worker pulls the next task from the queue", 16),
        ["round 158: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 158: a worker pulls the next task from the queue", 24),
        ["round 158: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 158: a worker pulls the next task from the queue", 32),
        ["round 158: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 158: signals travel through the network layer", 4),
        ["round", "158:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 158: signals travel through the network layer", 8),
        ["round", "158:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 158: signals travel through the network layer", 12),
        ["round 158:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 158: signals travel through the network layer", 16),
        ["round 158:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 158: signals travel through the network layer", 24),
        ["round 158: signals", "travel through the", "network layer"],
    ),
    (
        ("round 158: signals travel through the network layer", 32),
        ["round 158: signals travel", "through the network layer"],
    ),
    (
        ("round 158: the gateway routes each request by policy", 4),
        ["round", "158:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 158: the gateway routes each request by policy", 8),
        ["round", "158: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 158: the gateway routes each request by policy", 12),
        ["round 158:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 158: the gateway routes each request by policy", 16),
        ["round 158: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 158: the gateway routes each request by policy", 24),
        ["round 158: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 158: the gateway routes each request by policy", 32),
        ["round 158: the gateway routes", "each request by policy"],
    ),
    (
        ("round 158: memory grows until the buffer is full", 4),
        ["round", "158:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 158: memory grows until the buffer is full", 8),
        ["round", "158:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 158: memory grows until the buffer is full", 12),
        ["round 158:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 158: memory grows until the buffer is full", 16),
        ["round 158:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 158: memory grows until the buffer is full", 24), ["round 158: memory grows", "until the buffer is full"]),
    (("round 158: memory grows until the buffer is full", 32), ["round 158: memory grows until", "the buffer is full"]),
    (
        ("round 158: the cluster mirrors every packet twice", 4),
        ["round", "158:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 158: the cluster mirrors every packet twice", 8),
        ["round", "158: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 158: the cluster mirrors every packet twice", 12),
        ["round 158:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 158: the cluster mirrors every packet twice", 16),
        ["round 158: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 158: the cluster mirrors every packet twice", 24),
        ["round 158: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 158: the cluster mirrors every packet twice", 32),
        ["round 158: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 158: ranking uses tokens learned from the corpus", 4),
        ["round", "158:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 158: ranking uses tokens learned from the corpus", 8),
        ["round", "158:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 158: ranking uses tokens learned from the corpus", 12),
        ["round 158:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 158: ranking uses tokens learned from the corpus", 16),
        ["round 158:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 158: ranking uses tokens learned from the corpus", 24),
        ["round 158: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 158: ranking uses tokens learned from the corpus", 32),
        ["round 158: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 158: a long session ends when the candle dies", 4),
        ["round", "158:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 158: a long session ends when the candle dies", 8),
        ["round", "158: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 158: a long session ends when the candle dies", 12),
        ["round 158: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 158: a long session ends when the candle dies", 16),
        ["round 158: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 158: a long session ends when the candle dies", 24),
        ["round 158: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 158: a long session ends when the candle dies", 32),
        ["round 158: a long session ends", "when the candle dies"],
    ),
    (
        ("round 158: encode the prompt then map the result", 4),
        ["round", "158:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 158: encode the prompt then map the result", 8),
        ["round", "158:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 158: encode the prompt then map the result", 12),
        ["round 158:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 158: encode the prompt then map the result", 16),
        ["round 158:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 158: encode the prompt then map the result", 24),
        ["round 158: encode the", "prompt then map the", "result"],
    ),
    (("round 158: encode the prompt then map the result", 32), ["round 158: encode the prompt", "then map the result"]),
    (
        ("round 158: the kernel wakes the worker at dawn", 4),
        ["round", "158:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 158: the kernel wakes the worker at dawn", 8),
        ["round", "158: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 158: the kernel wakes the worker at dawn", 12),
        ["round 158:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 158: the kernel wakes the worker at dawn", 16), ["round 158: the", "kernel wakes the", "worker at dawn"]),
    (("round 158: the kernel wakes the worker at dawn", 24), ["round 158: the kernel", "wakes the worker at dawn"]),
    (("round 158: the kernel wakes the worker at dawn", 32), ["round 158: the kernel wakes the", "worker at dawn"]),
    (
        ("round 158: service latency drops after the patch", 4),
        ["round", "158:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 158: service latency drops after the patch", 8),
        ["round", "158:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 158: service latency drops after the patch", 12),
        ["round 158:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 158: service latency drops after the patch", 16),
        ["round 158:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 158: service latency drops after the patch", 24),
        ["round 158: service", "latency drops after the", "patch"],
    ),
    (("round 158: service latency drops after the patch", 32), ["round 158: service latency drops", "after the patch"]),
    (
        ("round 158: the library caches every vector it sees", 4),
        ["round", "158:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 158: the library caches every vector it sees", 8),
        ["round", "158: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 158: the library caches every vector it sees", 12),
        ["round 158:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 158: the library caches every vector it sees", 16),
        ["round 158: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 158: the library caches every vector it sees", 24),
        ["round 158: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 158: the library caches every vector it sees", 32),
        ["round 158: the library caches", "every vector it sees"],
    ),
    (
        ("round 158: agents argue then the debate resolves", 4),
        ["round", "158:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 158: agents argue then the debate resolves", 8),
        ["round", "158:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 158: agents argue then the debate resolves", 12),
        ["round 158:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 158: agents argue then the debate resolves", 16),
        ["round 158:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 158: agents argue then the debate resolves", 24), ["round 158: agents argue", "then the debate resolves"]),
    (("round 158: agents argue then the debate resolves", 32), ["round 158: agents argue then the", "debate resolves"]),
    (
        ("round 158: the filter keeps only strong matches", 4),
        ["round", "158:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 158: the filter keeps only strong matches", 8),
        ["round", "158: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 158: the filter keeps only strong matches", 12),
        ["round 158:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 158: the filter keeps only strong matches", 16),
        ["round 158: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 158: the filter keeps only strong matches", 24),
        ["round 158: the filter", "keeps only strong", "matches"],
    ),
    (("round 158: the filter keeps only strong matches", 32), ["round 158: the filter keeps only", "strong matches"]),
    (
        ("round 158: the model answers with a short reply", 4),
        ["round", "158:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 158: the model answers with a short reply", 8),
        ["round", "158: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 158: the model answers with a short reply", 12),
        ["round 158:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 158: the model answers with a short reply", 16),
        ["round 158: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 158: the model answers with a short reply", 24),
        ["round 158: the model", "answers with a short", "reply"],
    ),
    (("round 158: the model answers with a short reply", 32), ["round 158: the model answers", "with a short reply"]),
    (
        ("round 158: the recorder stores the reasoning trace", 4),
        ["round", "158:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 158: the recorder stores the reasoning trace", 8),
        ["round", "158: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 158: the recorder stores the reasoning trace", 12),
        ["round 158:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 158: the recorder stores the reasoning trace", 16),
        ["round 158: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 158: the recorder stores the reasoning trace", 24),
        ["round 158: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 158: the recorder stores the reasoning trace", 32),
        ["round 158: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 158: the angel watches the processor run", 4),
        ["round", "158:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 158: the angel watches the processor run", 8),
        ["round", "158: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 158: the angel watches the processor run", 12),
        ["round 158:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 158: the angel watches the processor run", 16),
        ["round 158: the", "angel watches", "the processor", "run"],
    ),
    (("round 158: the angel watches the processor run", 24), ["round 158: the angel", "watches the processor", "run"]),
    (("round 158: the angel watches the processor run", 32), ["round 158: the angel watches the", "processor run"]),
    (
        ("round 158: angle of the vector decides the match", 4),
        ["round", "158:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 158: angle of the vector decides the match", 8),
        ["round", "158:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 158: angle of the vector decides the match", 12),
        ["round 158:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 158: angle of the vector decides the match", 16),
        ["round 158: angle", "of the vector", "decides the", "match"],
    ),
    (("round 158: angle of the vector decides the match", 24), ["round 158: angle of the", "vector decides the match"]),
    (("round 158: angle of the vector decides the match", 32), ["round 158: angle of the vector", "decides the match"]),
    (
        ("round 158: the candle burns twice as long at night", 4),
        ["round", "158:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 158: the candle burns twice as long at night", 8),
        ["round", "158: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 158: the candle burns twice as long at night", 12),
        ["round 158:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 158: the candle burns twice as long at night", 16),
        ["round 158: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 158: the candle burns twice as long at night", 24),
        ["round 158: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 158: the candle burns twice as long at night", 32),
        ["round 158: the candle burns", "twice as long at night"],
    ),
    (
        ("round 158: a mirror of the universe in one line", 4),
        ["round", "158:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 158: a mirror of the universe in one line", 8),
        ["round", "158: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 158: a mirror of the universe in one line", 12),
        ["round 158: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 158: a mirror of the universe in one line", 16),
        ["round 158: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 158: a mirror of the universe in one line", 24), ["round 158: a mirror of", "the universe in one line"]),
    (("round 158: a mirror of the universe in one line", 32), ["round 158: a mirror of the", "universe in one line"]),
    (
        ("round 158: the queue drains before the storm", 4),
        ["round", "158:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 158: the queue drains before the storm", 8),
        ["round", "158: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 158: the queue drains before the storm", 12),
        ["round 158:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 158: the queue drains before the storm", 16), ["round 158: the", "queue drains", "before the storm"]),
    (("round 158: the queue drains before the storm", 24), ["round 158: the queue", "drains before the storm"]),
    (("round 158: the queue drains before the storm", 32), ["round 158: the queue drains", "before the storm"]),
    (
        ("kitten158 sitting158 agent158 angle158 universe158 memory158", 6),
        ["kitten158", "sitting158", "agent158", "angle158", "universe158", "memory158"],
    ),
    (
        ("kitten158 sitting158 agent158 angle158 universe158 memory158", 10),
        ["kitten158", "sitting158", "agent158", "angle158", "universe158", "memory158"],
    ),
    (
        ("kitten158 sitting158 agent158 angle158 universe158 memory158", 18),
        ["kitten158", "sitting158", "agent158 angle158", "universe158", "memory158"],
    ),
    (
        ("kitten158 sitting158 agent158 angle158 universe158 memory158", 28),
        ["kitten158 sitting158", "agent158 angle158", "universe158 memory158"],
    ),
    (
        ("sitting158 agent158 angle158 universe158 memory158 stream158", 6),
        ["sitting158", "agent158", "angle158", "universe158", "memory158", "stream158"],
    ),
    (
        ("sitting158 agent158 angle158 universe158 memory158 stream158", 10),
        ["sitting158", "agent158", "angle158", "universe158", "memory158", "stream158"],
    ),
    (
        ("sitting158 agent158 angle158 universe158 memory158 stream158", 18),
        ["sitting158", "agent158 angle158", "universe158", "memory158", "stream158"],
    ),
    (
        ("sitting158 agent158 angle158 universe158 memory158 stream158", 28),
        ["sitting158 agent158 angle158", "universe158 memory158", "stream158"],
    ),
    (
        ("agent158 angle158 universe158 memory158 stream158 context158", 6),
        ["agent158", "angle158", "universe158", "memory158", "stream158", "context158"],
    ),
    (
        ("agent158 angle158 universe158 memory158 stream158 context158", 10),
        ["agent158", "angle158", "universe158", "memory158", "stream158", "context158"],
    ),
    (
        ("agent158 angle158 universe158 memory158 stream158 context158", 18),
        ["agent158 angle158", "universe158", "memory158", "stream158", "context158"],
    ),
    (
        ("agent158 angle158 universe158 memory158 stream158 context158", 28),
        ["agent158 angle158", "universe158 memory158", "stream158 context158"],
    ),
    (
        ("angle158 universe158 memory158 stream158 context158 knowledge158", 6),
        ["angle158", "universe158", "memory158", "stream158", "context158", "knowledge158"],
    ),
    (
        ("angle158 universe158 memory158 stream158 context158 knowledge158", 10),
        ["angle158", "universe158", "memory158", "stream158", "context158", "knowledge158"],
    ),
    (
        ("angle158 universe158 memory158 stream158 context158 knowledge158", 18),
        ["angle158", "universe158", "memory158", "stream158", "context158", "knowledge158"],
    ),
    (
        ("angle158 universe158 memory158 stream158 context158 knowledge158", 28),
        ["angle158 universe158", "memory158 stream158", "context158 knowledge158"],
    ),
    (
        ("universe158 memory158 stream158 context158 knowledge158 vector158", 6),
        ["universe158", "memory158", "stream158", "context158", "knowledge158", "vector158"],
    ),
    (
        ("universe158 memory158 stream158 context158 knowledge158 vector158", 10),
        ["universe158", "memory158", "stream158", "context158", "knowledge158", "vector158"],
    ),
    (
        ("universe158 memory158 stream158 context158 knowledge158 vector158", 18),
        ["universe158", "memory158", "stream158", "context158", "knowledge158", "vector158"],
    ),
    (
        ("universe158 memory158 stream158 context158 knowledge158 vector158", 28),
        ["universe158 memory158", "stream158 context158", "knowledge158 vector158"],
    ),
    (
        ("memory158 stream158 context158 knowledge158 vector158 processor158", 6),
        ["memory158", "stream158", "context158", "knowledge158", "vector158", "processor158"],
    ),
    (
        ("memory158 stream158 context158 knowledge158 vector158 processor158", 10),
        ["memory158", "stream158", "context158", "knowledge158", "vector158", "processor158"],
    ),
    (
        ("memory158 stream158 context158 knowledge158 vector158 processor158", 18),
        ["memory158", "stream158", "context158", "knowledge158", "vector158", "processor158"],
    ),
    (
        ("memory158 stream158 context158 knowledge158 vector158 processor158", 28),
        ["memory158 stream158", "context158 knowledge158", "vector158 processor158"],
    ),
    (
        ("stream158 context158 knowledge158 vector158 processor158 reasoning158", 6),
        ["stream158", "context158", "knowledge158", "vector158", "processor158", "reasoning158"],
    ),
    (
        ("stream158 context158 knowledge158 vector158 processor158 reasoning158", 10),
        ["stream158", "context158", "knowledge158", "vector158", "processor158", "reasoning158"],
    ),
    (
        ("stream158 context158 knowledge158 vector158 processor158 reasoning158", 18),
        ["stream158", "context158", "knowledge158", "vector158", "processor158", "reasoning158"],
    ),
    (
        ("stream158 context158 knowledge158 vector158 processor158 reasoning158", 28),
        ["stream158 context158", "knowledge158 vector158", "processor158 reasoning158"],
    ),
    (
        ("context158 knowledge158 vector158 processor158 reasoning158 machine158", 6),
        ["context158", "knowledge158", "vector158", "processor158", "reasoning158", "machine158"],
    ),
    (
        ("context158 knowledge158 vector158 processor158 reasoning158 machine158", 10),
        ["context158", "knowledge158", "vector158", "processor158", "reasoning158", "machine158"],
    ),
    (
        ("context158 knowledge158 vector158 processor158 reasoning158 machine158", 18),
        ["context158", "knowledge158", "vector158", "processor158", "reasoning158", "machine158"],
    ),
    (
        ("context158 knowledge158 vector158 processor158 reasoning158 machine158", 28),
        ["context158 knowledge158", "vector158 processor158", "reasoning158 machine158"],
    ),
    (
        ("knowledge158 vector158 processor158 reasoning158 machine158 learning158", 6),
        ["knowledge158", "vector158", "processor158", "reasoning158", "machine158", "learning158"],
    ),
    (
        ("knowledge158 vector158 processor158 reasoning158 machine158 learning158", 10),
        ["knowledge158", "vector158", "processor158", "reasoning158", "machine158", "learning158"],
    ),
    (
        ("knowledge158 vector158 processor158 reasoning158 machine158 learning158", 18),
        ["knowledge158", "vector158", "processor158", "reasoning158", "machine158", "learning158"],
    ),
    (
        ("knowledge158 vector158 processor158 reasoning158 machine158 learning158", 28),
        ["knowledge158 vector158", "processor158 reasoning158", "machine158 learning158"],
    ),
    (
        ("vector158 processor158 reasoning158 machine158 learning158 model158", 6),
        ["vector158", "processor158", "reasoning158", "machine158", "learning158", "model158"],
    ),
    (
        ("vector158 processor158 reasoning158 machine158 learning158 model158", 10),
        ["vector158", "processor158", "reasoning158", "machine158", "learning158", "model158"],
    ),
    (
        ("vector158 processor158 reasoning158 machine158 learning158 model158", 18),
        ["vector158", "processor158", "reasoning158", "machine158", "learning158", "model158"],
    ),
    (
        ("vector158 processor158 reasoning158 machine158 learning158 model158", 28),
        ["vector158 processor158", "reasoning158 machine158", "learning158 model158"],
    ),
    (
        ("processor158 reasoning158 machine158 learning158 model158 token158", 6),
        ["processor158", "reasoning158", "machine158", "learning158", "model158", "token158"],
    ),
    (
        ("processor158 reasoning158 machine158 learning158 model158 token158", 10),
        ["processor158", "reasoning158", "machine158", "learning158", "model158", "token158"],
    ),
    (
        ("processor158 reasoning158 machine158 learning158 model158 token158", 18),
        ["processor158", "reasoning158", "machine158", "learning158", "model158 token158"],
    ),
    (
        ("processor158 reasoning158 machine158 learning158 model158 token158", 28),
        ["processor158 reasoning158", "machine158 learning158", "model158 token158"],
    ),
    (
        ("reasoning158 machine158 learning158 model158 token158 prompt158", 6),
        ["reasoning158", "machine158", "learning158", "model158", "token158", "prompt158"],
    ),
    (
        ("reasoning158 machine158 learning158 model158 token158 prompt158", 10),
        ["reasoning158", "machine158", "learning158", "model158", "token158", "prompt158"],
    ),
    (
        ("reasoning158 machine158 learning158 model158 token158 prompt158", 18),
        ["reasoning158", "machine158", "learning158", "model158 token158", "prompt158"],
    ),
    (
        ("reasoning158 machine158 learning158 model158 token158 prompt158", 28),
        ["reasoning158 machine158", "learning158 model158", "token158 prompt158"],
    ),
    (
        ("machine158 learning158 model158 token158 prompt158 session158", 6),
        ["machine158", "learning158", "model158", "token158", "prompt158", "session158"],
    ),
    (
        ("machine158 learning158 model158 token158 prompt158 session158", 10),
        ["machine158", "learning158", "model158", "token158", "prompt158", "session158"],
    ),
    (
        ("machine158 learning158 model158 token158 prompt158 session158", 18),
        ["machine158", "learning158", "model158 token158", "prompt158", "session158"],
    ),
    (
        ("machine158 learning158 model158 token158 prompt158 session158", 28),
        ["machine158 learning158", "model158 token158 prompt158", "session158"],
    ),
    (
        ("learning158 model158 token158 prompt158 session158 library158", 6),
        ["learning158", "model158", "token158", "prompt158", "session158", "library158"],
    ),
    (
        ("learning158 model158 token158 prompt158 session158 library158", 10),
        ["learning158", "model158", "token158", "prompt158", "session158", "library158"],
    ),
    (
        ("learning158 model158 token158 prompt158 session158 library158", 18),
        ["learning158", "model158 token158", "prompt158", "session158", "library158"],
    ),
    (
        ("learning158 model158 token158 prompt158 session158 library158", 28),
        ["learning158 model158", "token158 prompt158", "session158 library158"],
    ),
    (
        ("model158 token158 prompt158 session158 library158 service158", 6),
        ["model158", "token158", "prompt158", "session158", "library158", "service158"],
    ),
    (
        ("model158 token158 prompt158 session158 library158 service158", 10),
        ["model158", "token158", "prompt158", "session158", "library158", "service158"],
    ),
    (
        ("model158 token158 prompt158 session158 library158 service158", 18),
        ["model158 token158", "prompt158", "session158", "library158", "service158"],
    ),
    (
        ("model158 token158 prompt158 session158 library158 service158", 28),
        ["model158 token158 prompt158", "session158 library158", "service158"],
    ),
    (
        ("token158 prompt158 session158 library158 service158 gateway158", 6),
        ["token158", "prompt158", "session158", "library158", "service158", "gateway158"],
    ),
    (
        ("token158 prompt158 session158 library158 service158 gateway158", 10),
        ["token158", "prompt158", "session158", "library158", "service158", "gateway158"],
    ),
    (
        ("token158 prompt158 session158 library158 service158 gateway158", 18),
        ["token158 prompt158", "session158", "library158", "service158", "gateway158"],
    ),
    (
        ("token158 prompt158 session158 library158 service158 gateway158", 28),
        ["token158 prompt158", "session158 library158", "service158 gateway158"],
    ),
    (
        ("prompt158 session158 library158 service158 gateway158 storage158", 6),
        ["prompt158", "session158", "library158", "service158", "gateway158", "storage158"],
    ),
    (
        ("prompt158 session158 library158 service158 gateway158 storage158", 10),
        ["prompt158", "session158", "library158", "service158", "gateway158", "storage158"],
    ),
    (
        ("prompt158 session158 library158 service158 gateway158 storage158", 18),
        ["prompt158", "session158", "library158", "service158", "gateway158", "storage158"],
    ),
    (
        ("prompt158 session158 library158 service158 gateway158 storage158", 28),
        ["prompt158 session158", "library158 service158", "gateway158 storage158"],
    ),
    (
        ("session158 library158 service158 gateway158 storage158 network158", 6),
        ["session158", "library158", "service158", "gateway158", "storage158", "network158"],
    ),
    (
        ("session158 library158 service158 gateway158 storage158 network158", 10),
        ["session158", "library158", "service158", "gateway158", "storage158", "network158"],
    ),
    (
        ("session158 library158 service158 gateway158 storage158 network158", 18),
        ["session158", "library158", "service158", "gateway158", "storage158", "network158"],
    ),
    (
        ("session158 library158 service158 gateway158 storage158 network158", 28),
        ["session158 library158", "service158 gateway158", "storage158 network158"],
    ),
    (
        ("library158 service158 gateway158 storage158 network158 latency158", 6),
        ["library158", "service158", "gateway158", "storage158", "network158", "latency158"],
    ),
    (
        ("library158 service158 gateway158 storage158 network158 latency158", 10),
        ["library158", "service158", "gateway158", "storage158", "network158", "latency158"],
    ),
    (
        ("library158 service158 gateway158 storage158 network158 latency158", 18),
        ["library158", "service158", "gateway158", "storage158", "network158", "latency158"],
    ),
    (
        ("library158 service158 gateway158 storage158 network158 latency158", 28),
        ["library158 service158", "gateway158 storage158", "network158 latency158"],
    ),
    (
        ("service158 gateway158 storage158 network158 latency158 buffer158", 6),
        ["service158", "gateway158", "storage158", "network158", "latency158", "buffer158"],
    ),
    (
        ("service158 gateway158 storage158 network158 latency158 buffer158", 10),
        ["service158", "gateway158", "storage158", "network158", "latency158", "buffer158"],
    ),
    (
        ("service158 gateway158 storage158 network158 latency158 buffer158", 18),
        ["service158", "gateway158", "storage158", "network158", "latency158", "buffer158"],
    ),
    (
        ("service158 gateway158 storage158 network158 latency158 buffer158", 28),
        ["service158 gateway158", "storage158 network158", "latency158 buffer158"],
    ),
    (
        ("gateway158 storage158 network158 latency158 buffer158 queue158", 6),
        ["gateway158", "storage158", "network158", "latency158", "buffer158", "queue158"],
    ),
    (
        ("gateway158 storage158 network158 latency158 buffer158 queue158", 10),
        ["gateway158", "storage158", "network158", "latency158", "buffer158", "queue158"],
    ),
    (
        ("gateway158 storage158 network158 latency158 buffer158 queue158", 18),
        ["gateway158", "storage158", "network158", "latency158", "buffer158 queue158"],
    ),
    (
        ("gateway158 storage158 network158 latency158 buffer158 queue158", 28),
        ["gateway158 storage158", "network158 latency158", "buffer158 queue158"],
    ),
    (
        ("storage158 network158 latency158 buffer158 queue158 worker158", 6),
        ["storage158", "network158", "latency158", "buffer158", "queue158", "worker158"],
    ),
    (
        ("storage158 network158 latency158 buffer158 queue158 worker158", 10),
        ["storage158", "network158", "latency158", "buffer158", "queue158", "worker158"],
    ),
    (
        ("storage158 network158 latency158 buffer158 queue158 worker158", 18),
        ["storage158", "network158", "latency158", "buffer158 queue158", "worker158"],
    ),
    (
        ("storage158 network158 latency158 buffer158 queue158 worker158", 28),
        ["storage158 network158", "latency158 buffer158", "queue158 worker158"],
    ),
    (
        ("network158 latency158 buffer158 queue158 worker158 kernel158", 6),
        ["network158", "latency158", "buffer158", "queue158", "worker158", "kernel158"],
    ),
    (
        ("network158 latency158 buffer158 queue158 worker158 kernel158", 10),
        ["network158", "latency158", "buffer158", "queue158", "worker158", "kernel158"],
    ),
    (
        ("network158 latency158 buffer158 queue158 worker158 kernel158", 18),
        ["network158", "latency158", "buffer158 queue158", "worker158", "kernel158"],
    ),
    (
        ("network158 latency158 buffer158 queue158 worker158 kernel158", 28),
        ["network158 latency158", "buffer158 queue158 worker158", "kernel158"],
    ),
    (
        ("latency158 buffer158 queue158 worker158 kernel158 signal158", 6),
        ["latency158", "buffer158", "queue158", "worker158", "kernel158", "signal158"],
    ),
    (
        ("latency158 buffer158 queue158 worker158 kernel158 signal158", 10),
        ["latency158", "buffer158", "queue158", "worker158", "kernel158", "signal158"],
    ),
    (
        ("latency158 buffer158 queue158 worker158 kernel158 signal158", 18),
        ["latency158", "buffer158 queue158", "worker158", "kernel158", "signal158"],
    ),
    (
        ("latency158 buffer158 queue158 worker158 kernel158 signal158", 28),
        ["latency158 buffer158", "queue158 worker158 kernel158", "signal158"],
    ),
    (
        ("buffer158 queue158 worker158 kernel158 signal158 packet158", 6),
        ["buffer158", "queue158", "worker158", "kernel158", "signal158", "packet158"],
    ),
    (
        ("buffer158 queue158 worker158 kernel158 signal158 packet158", 10),
        ["buffer158", "queue158", "worker158", "kernel158", "signal158", "packet158"],
    ),
    (
        ("buffer158 queue158 worker158 kernel158 signal158 packet158", 18),
        ["buffer158 queue158", "worker158", "kernel158", "signal158", "packet158"],
    ),
    (
        ("buffer158 queue158 worker158 kernel158 signal158 packet158", 28),
        ["buffer158 queue158 worker158", "kernel158 signal158", "packet158"],
    ),
    (
        ("queue158 worker158 kernel158 signal158 packet158 router158", 6),
        ["queue158", "worker158", "kernel158", "signal158", "packet158", "router158"],
    ),
    (
        ("queue158 worker158 kernel158 signal158 packet158 router158", 10),
        ["queue158", "worker158", "kernel158", "signal158", "packet158", "router158"],
    ),
    (
        ("queue158 worker158 kernel158 signal158 packet158 router158", 18),
        ["queue158 worker158", "kernel158", "signal158", "packet158", "router158"],
    ),
    (
        ("queue158 worker158 kernel158 signal158 packet158 router158", 28),
        ["queue158 worker158 kernel158", "signal158 packet158", "router158"],
    ),
    (
        ("worker158 kernel158 signal158 packet158 router158 cluster158", 6),
        ["worker158", "kernel158", "signal158", "packet158", "router158", "cluster158"],
    ),
    (
        ("worker158 kernel158 signal158 packet158 router158 cluster158", 10),
        ["worker158", "kernel158", "signal158", "packet158", "router158", "cluster158"],
    ),
    (
        ("worker158 kernel158 signal158 packet158 router158 cluster158", 18),
        ["worker158", "kernel158", "signal158", "packet158", "router158", "cluster158"],
    ),
    (
        ("worker158 kernel158 signal158 packet158 router158 cluster158", 28),
        ["worker158 kernel158", "signal158 packet158", "router158 cluster158"],
    ),
    (
        ("kernel158 signal158 packet158 router158 cluster158 mirror158", 6),
        ["kernel158", "signal158", "packet158", "router158", "cluster158", "mirror158"],
    ),
    (
        ("kernel158 signal158 packet158 router158 cluster158 mirror158", 10),
        ["kernel158", "signal158", "packet158", "router158", "cluster158", "mirror158"],
    ),
    (
        ("kernel158 signal158 packet158 router158 cluster158 mirror158", 18),
        ["kernel158", "signal158", "packet158", "router158", "cluster158", "mirror158"],
    ),
    (
        ("kernel158 signal158 packet158 router158 cluster158 mirror158", 28),
        ["kernel158 signal158", "packet158 router158", "cluster158 mirror158"],
    ),
    (
        ("signal158 packet158 router158 cluster158 mirror158 filter158", 6),
        ["signal158", "packet158", "router158", "cluster158", "mirror158", "filter158"],
    ),
    (
        ("signal158 packet158 router158 cluster158 mirror158 filter158", 10),
        ["signal158", "packet158", "router158", "cluster158", "mirror158", "filter158"],
    ),
    (
        ("signal158 packet158 router158 cluster158 mirror158 filter158", 18),
        ["signal158", "packet158", "router158", "cluster158", "mirror158", "filter158"],
    ),
    (
        ("signal158 packet158 router158 cluster158 mirror158 filter158", 28),
        ["signal158 packet158", "router158 cluster158", "mirror158 filter158"],
    ),
    (
        ("packet158 router158 cluster158 mirror158 filter158 ranking158", 6),
        ["packet158", "router158", "cluster158", "mirror158", "filter158", "ranking158"],
    ),
    (
        ("packet158 router158 cluster158 mirror158 filter158 ranking158", 10),
        ["packet158", "router158", "cluster158", "mirror158", "filter158", "ranking158"],
    ),
    (
        ("packet158 router158 cluster158 mirror158 filter158 ranking158", 18),
        ["packet158", "router158", "cluster158", "mirror158", "filter158", "ranking158"],
    ),
    (
        ("packet158 router158 cluster158 mirror158 filter158 ranking158", 28),
        ["packet158 router158", "cluster158 mirror158", "filter158 ranking158"],
    ),
    (
        ("router158 cluster158 mirror158 filter158 ranking158 encoding158", 6),
        ["router158", "cluster158", "mirror158", "filter158", "ranking158", "encoding158"],
    ),
    (
        ("router158 cluster158 mirror158 filter158 ranking158 encoding158", 10),
        ["router158", "cluster158", "mirror158", "filter158", "ranking158", "encoding158"],
    ),
    (
        ("router158 cluster158 mirror158 filter158 ranking158 encoding158", 18),
        ["router158", "cluster158", "mirror158", "filter158", "ranking158", "encoding158"],
    ),
    (
        ("router158 cluster158 mirror158 filter158 ranking158 encoding158", 28),
        ["router158 cluster158", "mirror158 filter158", "ranking158 encoding158"],
    ),
    (
        ("cluster158 mirror158 filter158 ranking158 encoding158 mapping158", 6),
        ["cluster158", "mirror158", "filter158", "ranking158", "encoding158", "mapping158"],
    ),
    (
        ("cluster158 mirror158 filter158 ranking158 encoding158 mapping158", 10),
        ["cluster158", "mirror158", "filter158", "ranking158", "encoding158", "mapping158"],
    ),
    (
        ("cluster158 mirror158 filter158 ranking158 encoding158 mapping158", 18),
        ["cluster158", "mirror158", "filter158", "ranking158", "encoding158", "mapping158"],
    ),
    (
        ("cluster158 mirror158 filter158 ranking158 encoding158 mapping158", 28),
        ["cluster158 mirror158", "filter158 ranking158", "encoding158 mapping158"],
    ),
    (
        ("mirror158 filter158 ranking158 encoding158 mapping158 record158", 6),
        ["mirror158", "filter158", "ranking158", "encoding158", "mapping158", "record158"],
    ),
    (
        ("mirror158 filter158 ranking158 encoding158 mapping158 record158", 10),
        ["mirror158", "filter158", "ranking158", "encoding158", "mapping158", "record158"],
    ),
    (
        ("mirror158 filter158 ranking158 encoding158 mapping158 record158", 18),
        ["mirror158", "filter158", "ranking158", "encoding158", "mapping158", "record158"],
    ),
    (
        ("mirror158 filter158 ranking158 encoding158 mapping158 record158", 28),
        ["mirror158 filter158", "ranking158 encoding158", "mapping158 record158"],
    ),
    (
        ("filter158 ranking158 encoding158 mapping158 record158 candle158", 6),
        ["filter158", "ranking158", "encoding158", "mapping158", "record158", "candle158"],
    ),
    (
        ("filter158 ranking158 encoding158 mapping158 record158 candle158", 10),
        ["filter158", "ranking158", "encoding158", "mapping158", "record158", "candle158"],
    ),
    (
        ("filter158 ranking158 encoding158 mapping158 record158 candle158", 18),
        ["filter158", "ranking158", "encoding158", "mapping158", "record158", "candle158"],
    ),
    (
        ("filter158 ranking158 encoding158 mapping158 record158 candle158", 28),
        ["filter158 ranking158", "encoding158 mapping158", "record158 candle158"],
    ),
    (
        ("ranking158 encoding158 mapping158 record158 candle158 thread158", 6),
        ["ranking158", "encoding158", "mapping158", "record158", "candle158", "thread158"],
    ),
    (
        ("ranking158 encoding158 mapping158 record158 candle158 thread158", 10),
        ["ranking158", "encoding158", "mapping158", "record158", "candle158", "thread158"],
    ),
    (
        ("ranking158 encoding158 mapping158 record158 candle158 thread158", 18),
        ["ranking158", "encoding158", "mapping158", "record158", "candle158", "thread158"],
    ),
    (
        ("ranking158 encoding158 mapping158 record158 candle158 thread158", 28),
        ["ranking158 encoding158", "mapping158 record158", "candle158 thread158"],
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
