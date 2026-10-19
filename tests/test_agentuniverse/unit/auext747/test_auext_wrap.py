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
        ("round 747: the quick brown fox jumps over the lazy dog", 4),
        ["round", "747:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 747: the quick brown fox jumps over the lazy dog", 8),
        ["round", "747: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 747: the quick brown fox jumps over the lazy dog", 12),
        ["round 747:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 747: the quick brown fox jumps over the lazy dog", 16),
        ["round 747: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 747: the quick brown fox jumps over the lazy dog", 24),
        ["round 747: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 747: the quick brown fox jumps over the lazy dog", 32),
        ["round 747: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 747: agentuniverse is a framework for multi agents", 4),
        ["round", "747:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 747: agentuniverse is a framework for multi agents", 8),
        ["round", "747:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 747: agentuniverse is a framework for multi agents", 12),
        ["round 747:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 747: agentuniverse is a framework for multi agents", 16),
        ["round 747:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 747: agentuniverse is a framework for multi agents", 24),
        ["round 747: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 747: agentuniverse is a framework for multi agents", 32),
        ["round 747: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 747: knowledge stored as vectors enables retrieval", 4),
        ["round", "747:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 747: knowledge stored as vectors enables retrieval", 8),
        ["round", "747:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 747: knowledge stored as vectors enables retrieval", 12),
        ["round 747:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 747: knowledge stored as vectors enables retrieval", 16),
        ["round 747:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 747: knowledge stored as vectors enables retrieval", 24),
        ["round 747: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 747: knowledge stored as vectors enables retrieval", 32),
        ["round 747: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 747: the processor reads the record then stops", 4),
        ["round", "747:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 747: the processor reads the record then stops", 8),
        ["round", "747: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 747: the processor reads the record then stops", 12),
        ["round 747:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 747: the processor reads the record then stops", 16),
        ["round 747: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 747: the processor reads the record then stops", 24),
        ["round 747: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 747: the processor reads the record then stops", 32),
        ["round 747: the processor reads", "the record then stops"],
    ),
    (
        ("round 747: a worker pulls the next task from the queue", 4),
        ["round", "747:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 747: a worker pulls the next task from the queue", 8),
        ["round", "747: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 747: a worker pulls the next task from the queue", 12),
        ["round 747: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 747: a worker pulls the next task from the queue", 16),
        ["round 747: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 747: a worker pulls the next task from the queue", 24),
        ["round 747: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 747: a worker pulls the next task from the queue", 32),
        ["round 747: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 747: signals travel through the network layer", 4),
        ["round", "747:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 747: signals travel through the network layer", 8),
        ["round", "747:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 747: signals travel through the network layer", 12),
        ["round 747:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 747: signals travel through the network layer", 16),
        ["round 747:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 747: signals travel through the network layer", 24),
        ["round 747: signals", "travel through the", "network layer"],
    ),
    (
        ("round 747: signals travel through the network layer", 32),
        ["round 747: signals travel", "through the network layer"],
    ),
    (
        ("round 747: the gateway routes each request by policy", 4),
        ["round", "747:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 747: the gateway routes each request by policy", 8),
        ["round", "747: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 747: the gateway routes each request by policy", 12),
        ["round 747:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 747: the gateway routes each request by policy", 16),
        ["round 747: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 747: the gateway routes each request by policy", 24),
        ["round 747: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 747: the gateway routes each request by policy", 32),
        ["round 747: the gateway routes", "each request by policy"],
    ),
    (
        ("round 747: memory grows until the buffer is full", 4),
        ["round", "747:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 747: memory grows until the buffer is full", 8),
        ["round", "747:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 747: memory grows until the buffer is full", 12),
        ["round 747:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 747: memory grows until the buffer is full", 16),
        ["round 747:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 747: memory grows until the buffer is full", 24), ["round 747: memory grows", "until the buffer is full"]),
    (("round 747: memory grows until the buffer is full", 32), ["round 747: memory grows until", "the buffer is full"]),
    (
        ("round 747: the cluster mirrors every packet twice", 4),
        ["round", "747:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 747: the cluster mirrors every packet twice", 8),
        ["round", "747: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 747: the cluster mirrors every packet twice", 12),
        ["round 747:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 747: the cluster mirrors every packet twice", 16),
        ["round 747: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 747: the cluster mirrors every packet twice", 24),
        ["round 747: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 747: the cluster mirrors every packet twice", 32),
        ["round 747: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 747: ranking uses tokens learned from the corpus", 4),
        ["round", "747:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 747: ranking uses tokens learned from the corpus", 8),
        ["round", "747:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 747: ranking uses tokens learned from the corpus", 12),
        ["round 747:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 747: ranking uses tokens learned from the corpus", 16),
        ["round 747:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 747: ranking uses tokens learned from the corpus", 24),
        ["round 747: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 747: ranking uses tokens learned from the corpus", 32),
        ["round 747: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 747: a long session ends when the candle dies", 4),
        ["round", "747:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 747: a long session ends when the candle dies", 8),
        ["round", "747: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 747: a long session ends when the candle dies", 12),
        ["round 747: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 747: a long session ends when the candle dies", 16),
        ["round 747: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 747: a long session ends when the candle dies", 24),
        ["round 747: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 747: a long session ends when the candle dies", 32),
        ["round 747: a long session ends", "when the candle dies"],
    ),
    (
        ("round 747: encode the prompt then map the result", 4),
        ["round", "747:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 747: encode the prompt then map the result", 8),
        ["round", "747:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 747: encode the prompt then map the result", 12),
        ["round 747:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 747: encode the prompt then map the result", 16),
        ["round 747:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 747: encode the prompt then map the result", 24),
        ["round 747: encode the", "prompt then map the", "result"],
    ),
    (("round 747: encode the prompt then map the result", 32), ["round 747: encode the prompt", "then map the result"]),
    (
        ("round 747: the kernel wakes the worker at dawn", 4),
        ["round", "747:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 747: the kernel wakes the worker at dawn", 8),
        ["round", "747: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 747: the kernel wakes the worker at dawn", 12),
        ["round 747:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 747: the kernel wakes the worker at dawn", 16), ["round 747: the", "kernel wakes the", "worker at dawn"]),
    (("round 747: the kernel wakes the worker at dawn", 24), ["round 747: the kernel", "wakes the worker at dawn"]),
    (("round 747: the kernel wakes the worker at dawn", 32), ["round 747: the kernel wakes the", "worker at dawn"]),
    (
        ("round 747: service latency drops after the patch", 4),
        ["round", "747:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 747: service latency drops after the patch", 8),
        ["round", "747:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 747: service latency drops after the patch", 12),
        ["round 747:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 747: service latency drops after the patch", 16),
        ["round 747:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 747: service latency drops after the patch", 24),
        ["round 747: service", "latency drops after the", "patch"],
    ),
    (("round 747: service latency drops after the patch", 32), ["round 747: service latency drops", "after the patch"]),
    (
        ("round 747: the library caches every vector it sees", 4),
        ["round", "747:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 747: the library caches every vector it sees", 8),
        ["round", "747: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 747: the library caches every vector it sees", 12),
        ["round 747:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 747: the library caches every vector it sees", 16),
        ["round 747: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 747: the library caches every vector it sees", 24),
        ["round 747: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 747: the library caches every vector it sees", 32),
        ["round 747: the library caches", "every vector it sees"],
    ),
    (
        ("round 747: agents argue then the debate resolves", 4),
        ["round", "747:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 747: agents argue then the debate resolves", 8),
        ["round", "747:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 747: agents argue then the debate resolves", 12),
        ["round 747:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 747: agents argue then the debate resolves", 16),
        ["round 747:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 747: agents argue then the debate resolves", 24), ["round 747: agents argue", "then the debate resolves"]),
    (("round 747: agents argue then the debate resolves", 32), ["round 747: agents argue then the", "debate resolves"]),
    (
        ("round 747: the filter keeps only strong matches", 4),
        ["round", "747:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 747: the filter keeps only strong matches", 8),
        ["round", "747: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 747: the filter keeps only strong matches", 12),
        ["round 747:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 747: the filter keeps only strong matches", 16),
        ["round 747: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 747: the filter keeps only strong matches", 24),
        ["round 747: the filter", "keeps only strong", "matches"],
    ),
    (("round 747: the filter keeps only strong matches", 32), ["round 747: the filter keeps only", "strong matches"]),
    (
        ("round 747: the model answers with a short reply", 4),
        ["round", "747:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 747: the model answers with a short reply", 8),
        ["round", "747: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 747: the model answers with a short reply", 12),
        ["round 747:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 747: the model answers with a short reply", 16),
        ["round 747: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 747: the model answers with a short reply", 24),
        ["round 747: the model", "answers with a short", "reply"],
    ),
    (("round 747: the model answers with a short reply", 32), ["round 747: the model answers", "with a short reply"]),
    (
        ("round 747: the recorder stores the reasoning trace", 4),
        ["round", "747:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 747: the recorder stores the reasoning trace", 8),
        ["round", "747: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 747: the recorder stores the reasoning trace", 12),
        ["round 747:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 747: the recorder stores the reasoning trace", 16),
        ["round 747: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 747: the recorder stores the reasoning trace", 24),
        ["round 747: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 747: the recorder stores the reasoning trace", 32),
        ["round 747: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 747: the angel watches the processor run", 4),
        ["round", "747:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 747: the angel watches the processor run", 8),
        ["round", "747: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 747: the angel watches the processor run", 12),
        ["round 747:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 747: the angel watches the processor run", 16),
        ["round 747: the", "angel watches", "the processor", "run"],
    ),
    (("round 747: the angel watches the processor run", 24), ["round 747: the angel", "watches the processor", "run"]),
    (("round 747: the angel watches the processor run", 32), ["round 747: the angel watches the", "processor run"]),
    (
        ("round 747: angle of the vector decides the match", 4),
        ["round", "747:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 747: angle of the vector decides the match", 8),
        ["round", "747:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 747: angle of the vector decides the match", 12),
        ["round 747:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 747: angle of the vector decides the match", 16),
        ["round 747: angle", "of the vector", "decides the", "match"],
    ),
    (("round 747: angle of the vector decides the match", 24), ["round 747: angle of the", "vector decides the match"]),
    (("round 747: angle of the vector decides the match", 32), ["round 747: angle of the vector", "decides the match"]),
    (
        ("round 747: the candle burns twice as long at night", 4),
        ["round", "747:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 747: the candle burns twice as long at night", 8),
        ["round", "747: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 747: the candle burns twice as long at night", 12),
        ["round 747:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 747: the candle burns twice as long at night", 16),
        ["round 747: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 747: the candle burns twice as long at night", 24),
        ["round 747: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 747: the candle burns twice as long at night", 32),
        ["round 747: the candle burns", "twice as long at night"],
    ),
    (
        ("round 747: a mirror of the universe in one line", 4),
        ["round", "747:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 747: a mirror of the universe in one line", 8),
        ["round", "747: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 747: a mirror of the universe in one line", 12),
        ["round 747: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 747: a mirror of the universe in one line", 16),
        ["round 747: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 747: a mirror of the universe in one line", 24), ["round 747: a mirror of", "the universe in one line"]),
    (("round 747: a mirror of the universe in one line", 32), ["round 747: a mirror of the", "universe in one line"]),
    (
        ("round 747: the queue drains before the storm", 4),
        ["round", "747:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 747: the queue drains before the storm", 8),
        ["round", "747: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 747: the queue drains before the storm", 12),
        ["round 747:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 747: the queue drains before the storm", 16), ["round 747: the", "queue drains", "before the storm"]),
    (("round 747: the queue drains before the storm", 24), ["round 747: the queue", "drains before the storm"]),
    (("round 747: the queue drains before the storm", 32), ["round 747: the queue drains", "before the storm"]),
    (
        ("kitten747 sitting747 agent747 angle747 universe747 memory747", 6),
        ["kitten747", "sitting747", "agent747", "angle747", "universe747", "memory747"],
    ),
    (
        ("kitten747 sitting747 agent747 angle747 universe747 memory747", 10),
        ["kitten747", "sitting747", "agent747", "angle747", "universe747", "memory747"],
    ),
    (
        ("kitten747 sitting747 agent747 angle747 universe747 memory747", 18),
        ["kitten747", "sitting747", "agent747 angle747", "universe747", "memory747"],
    ),
    (
        ("kitten747 sitting747 agent747 angle747 universe747 memory747", 28),
        ["kitten747 sitting747", "agent747 angle747", "universe747 memory747"],
    ),
    (
        ("sitting747 agent747 angle747 universe747 memory747 stream747", 6),
        ["sitting747", "agent747", "angle747", "universe747", "memory747", "stream747"],
    ),
    (
        ("sitting747 agent747 angle747 universe747 memory747 stream747", 10),
        ["sitting747", "agent747", "angle747", "universe747", "memory747", "stream747"],
    ),
    (
        ("sitting747 agent747 angle747 universe747 memory747 stream747", 18),
        ["sitting747", "agent747 angle747", "universe747", "memory747", "stream747"],
    ),
    (
        ("sitting747 agent747 angle747 universe747 memory747 stream747", 28),
        ["sitting747 agent747 angle747", "universe747 memory747", "stream747"],
    ),
    (
        ("agent747 angle747 universe747 memory747 stream747 context747", 6),
        ["agent747", "angle747", "universe747", "memory747", "stream747", "context747"],
    ),
    (
        ("agent747 angle747 universe747 memory747 stream747 context747", 10),
        ["agent747", "angle747", "universe747", "memory747", "stream747", "context747"],
    ),
    (
        ("agent747 angle747 universe747 memory747 stream747 context747", 18),
        ["agent747 angle747", "universe747", "memory747", "stream747", "context747"],
    ),
    (
        ("agent747 angle747 universe747 memory747 stream747 context747", 28),
        ["agent747 angle747", "universe747 memory747", "stream747 context747"],
    ),
    (
        ("angle747 universe747 memory747 stream747 context747 knowledge747", 6),
        ["angle747", "universe747", "memory747", "stream747", "context747", "knowledge747"],
    ),
    (
        ("angle747 universe747 memory747 stream747 context747 knowledge747", 10),
        ["angle747", "universe747", "memory747", "stream747", "context747", "knowledge747"],
    ),
    (
        ("angle747 universe747 memory747 stream747 context747 knowledge747", 18),
        ["angle747", "universe747", "memory747", "stream747", "context747", "knowledge747"],
    ),
    (
        ("angle747 universe747 memory747 stream747 context747 knowledge747", 28),
        ["angle747 universe747", "memory747 stream747", "context747 knowledge747"],
    ),
    (
        ("universe747 memory747 stream747 context747 knowledge747 vector747", 6),
        ["universe747", "memory747", "stream747", "context747", "knowledge747", "vector747"],
    ),
    (
        ("universe747 memory747 stream747 context747 knowledge747 vector747", 10),
        ["universe747", "memory747", "stream747", "context747", "knowledge747", "vector747"],
    ),
    (
        ("universe747 memory747 stream747 context747 knowledge747 vector747", 18),
        ["universe747", "memory747", "stream747", "context747", "knowledge747", "vector747"],
    ),
    (
        ("universe747 memory747 stream747 context747 knowledge747 vector747", 28),
        ["universe747 memory747", "stream747 context747", "knowledge747 vector747"],
    ),
    (
        ("memory747 stream747 context747 knowledge747 vector747 processor747", 6),
        ["memory747", "stream747", "context747", "knowledge747", "vector747", "processor747"],
    ),
    (
        ("memory747 stream747 context747 knowledge747 vector747 processor747", 10),
        ["memory747", "stream747", "context747", "knowledge747", "vector747", "processor747"],
    ),
    (
        ("memory747 stream747 context747 knowledge747 vector747 processor747", 18),
        ["memory747", "stream747", "context747", "knowledge747", "vector747", "processor747"],
    ),
    (
        ("memory747 stream747 context747 knowledge747 vector747 processor747", 28),
        ["memory747 stream747", "context747 knowledge747", "vector747 processor747"],
    ),
    (
        ("stream747 context747 knowledge747 vector747 processor747 reasoning747", 6),
        ["stream747", "context747", "knowledge747", "vector747", "processor747", "reasoning747"],
    ),
    (
        ("stream747 context747 knowledge747 vector747 processor747 reasoning747", 10),
        ["stream747", "context747", "knowledge747", "vector747", "processor747", "reasoning747"],
    ),
    (
        ("stream747 context747 knowledge747 vector747 processor747 reasoning747", 18),
        ["stream747", "context747", "knowledge747", "vector747", "processor747", "reasoning747"],
    ),
    (
        ("stream747 context747 knowledge747 vector747 processor747 reasoning747", 28),
        ["stream747 context747", "knowledge747 vector747", "processor747 reasoning747"],
    ),
    (
        ("context747 knowledge747 vector747 processor747 reasoning747 machine747", 6),
        ["context747", "knowledge747", "vector747", "processor747", "reasoning747", "machine747"],
    ),
    (
        ("context747 knowledge747 vector747 processor747 reasoning747 machine747", 10),
        ["context747", "knowledge747", "vector747", "processor747", "reasoning747", "machine747"],
    ),
    (
        ("context747 knowledge747 vector747 processor747 reasoning747 machine747", 18),
        ["context747", "knowledge747", "vector747", "processor747", "reasoning747", "machine747"],
    ),
    (
        ("context747 knowledge747 vector747 processor747 reasoning747 machine747", 28),
        ["context747 knowledge747", "vector747 processor747", "reasoning747 machine747"],
    ),
    (
        ("knowledge747 vector747 processor747 reasoning747 machine747 learning747", 6),
        ["knowledge747", "vector747", "processor747", "reasoning747", "machine747", "learning747"],
    ),
    (
        ("knowledge747 vector747 processor747 reasoning747 machine747 learning747", 10),
        ["knowledge747", "vector747", "processor747", "reasoning747", "machine747", "learning747"],
    ),
    (
        ("knowledge747 vector747 processor747 reasoning747 machine747 learning747", 18),
        ["knowledge747", "vector747", "processor747", "reasoning747", "machine747", "learning747"],
    ),
    (
        ("knowledge747 vector747 processor747 reasoning747 machine747 learning747", 28),
        ["knowledge747 vector747", "processor747 reasoning747", "machine747 learning747"],
    ),
    (
        ("vector747 processor747 reasoning747 machine747 learning747 model747", 6),
        ["vector747", "processor747", "reasoning747", "machine747", "learning747", "model747"],
    ),
    (
        ("vector747 processor747 reasoning747 machine747 learning747 model747", 10),
        ["vector747", "processor747", "reasoning747", "machine747", "learning747", "model747"],
    ),
    (
        ("vector747 processor747 reasoning747 machine747 learning747 model747", 18),
        ["vector747", "processor747", "reasoning747", "machine747", "learning747", "model747"],
    ),
    (
        ("vector747 processor747 reasoning747 machine747 learning747 model747", 28),
        ["vector747 processor747", "reasoning747 machine747", "learning747 model747"],
    ),
    (
        ("processor747 reasoning747 machine747 learning747 model747 token747", 6),
        ["processor747", "reasoning747", "machine747", "learning747", "model747", "token747"],
    ),
    (
        ("processor747 reasoning747 machine747 learning747 model747 token747", 10),
        ["processor747", "reasoning747", "machine747", "learning747", "model747", "token747"],
    ),
    (
        ("processor747 reasoning747 machine747 learning747 model747 token747", 18),
        ["processor747", "reasoning747", "machine747", "learning747", "model747 token747"],
    ),
    (
        ("processor747 reasoning747 machine747 learning747 model747 token747", 28),
        ["processor747 reasoning747", "machine747 learning747", "model747 token747"],
    ),
    (
        ("reasoning747 machine747 learning747 model747 token747 prompt747", 6),
        ["reasoning747", "machine747", "learning747", "model747", "token747", "prompt747"],
    ),
    (
        ("reasoning747 machine747 learning747 model747 token747 prompt747", 10),
        ["reasoning747", "machine747", "learning747", "model747", "token747", "prompt747"],
    ),
    (
        ("reasoning747 machine747 learning747 model747 token747 prompt747", 18),
        ["reasoning747", "machine747", "learning747", "model747 token747", "prompt747"],
    ),
    (
        ("reasoning747 machine747 learning747 model747 token747 prompt747", 28),
        ["reasoning747 machine747", "learning747 model747", "token747 prompt747"],
    ),
    (
        ("machine747 learning747 model747 token747 prompt747 session747", 6),
        ["machine747", "learning747", "model747", "token747", "prompt747", "session747"],
    ),
    (
        ("machine747 learning747 model747 token747 prompt747 session747", 10),
        ["machine747", "learning747", "model747", "token747", "prompt747", "session747"],
    ),
    (
        ("machine747 learning747 model747 token747 prompt747 session747", 18),
        ["machine747", "learning747", "model747 token747", "prompt747", "session747"],
    ),
    (
        ("machine747 learning747 model747 token747 prompt747 session747", 28),
        ["machine747 learning747", "model747 token747 prompt747", "session747"],
    ),
    (
        ("learning747 model747 token747 prompt747 session747 library747", 6),
        ["learning747", "model747", "token747", "prompt747", "session747", "library747"],
    ),
    (
        ("learning747 model747 token747 prompt747 session747 library747", 10),
        ["learning747", "model747", "token747", "prompt747", "session747", "library747"],
    ),
    (
        ("learning747 model747 token747 prompt747 session747 library747", 18),
        ["learning747", "model747 token747", "prompt747", "session747", "library747"],
    ),
    (
        ("learning747 model747 token747 prompt747 session747 library747", 28),
        ["learning747 model747", "token747 prompt747", "session747 library747"],
    ),
    (
        ("model747 token747 prompt747 session747 library747 service747", 6),
        ["model747", "token747", "prompt747", "session747", "library747", "service747"],
    ),
    (
        ("model747 token747 prompt747 session747 library747 service747", 10),
        ["model747", "token747", "prompt747", "session747", "library747", "service747"],
    ),
    (
        ("model747 token747 prompt747 session747 library747 service747", 18),
        ["model747 token747", "prompt747", "session747", "library747", "service747"],
    ),
    (
        ("model747 token747 prompt747 session747 library747 service747", 28),
        ["model747 token747 prompt747", "session747 library747", "service747"],
    ),
    (
        ("token747 prompt747 session747 library747 service747 gateway747", 6),
        ["token747", "prompt747", "session747", "library747", "service747", "gateway747"],
    ),
    (
        ("token747 prompt747 session747 library747 service747 gateway747", 10),
        ["token747", "prompt747", "session747", "library747", "service747", "gateway747"],
    ),
    (
        ("token747 prompt747 session747 library747 service747 gateway747", 18),
        ["token747 prompt747", "session747", "library747", "service747", "gateway747"],
    ),
    (
        ("token747 prompt747 session747 library747 service747 gateway747", 28),
        ["token747 prompt747", "session747 library747", "service747 gateway747"],
    ),
    (
        ("prompt747 session747 library747 service747 gateway747 storage747", 6),
        ["prompt747", "session747", "library747", "service747", "gateway747", "storage747"],
    ),
    (
        ("prompt747 session747 library747 service747 gateway747 storage747", 10),
        ["prompt747", "session747", "library747", "service747", "gateway747", "storage747"],
    ),
    (
        ("prompt747 session747 library747 service747 gateway747 storage747", 18),
        ["prompt747", "session747", "library747", "service747", "gateway747", "storage747"],
    ),
    (
        ("prompt747 session747 library747 service747 gateway747 storage747", 28),
        ["prompt747 session747", "library747 service747", "gateway747 storage747"],
    ),
    (
        ("session747 library747 service747 gateway747 storage747 network747", 6),
        ["session747", "library747", "service747", "gateway747", "storage747", "network747"],
    ),
    (
        ("session747 library747 service747 gateway747 storage747 network747", 10),
        ["session747", "library747", "service747", "gateway747", "storage747", "network747"],
    ),
    (
        ("session747 library747 service747 gateway747 storage747 network747", 18),
        ["session747", "library747", "service747", "gateway747", "storage747", "network747"],
    ),
    (
        ("session747 library747 service747 gateway747 storage747 network747", 28),
        ["session747 library747", "service747 gateway747", "storage747 network747"],
    ),
    (
        ("library747 service747 gateway747 storage747 network747 latency747", 6),
        ["library747", "service747", "gateway747", "storage747", "network747", "latency747"],
    ),
    (
        ("library747 service747 gateway747 storage747 network747 latency747", 10),
        ["library747", "service747", "gateway747", "storage747", "network747", "latency747"],
    ),
    (
        ("library747 service747 gateway747 storage747 network747 latency747", 18),
        ["library747", "service747", "gateway747", "storage747", "network747", "latency747"],
    ),
    (
        ("library747 service747 gateway747 storage747 network747 latency747", 28),
        ["library747 service747", "gateway747 storage747", "network747 latency747"],
    ),
    (
        ("service747 gateway747 storage747 network747 latency747 buffer747", 6),
        ["service747", "gateway747", "storage747", "network747", "latency747", "buffer747"],
    ),
    (
        ("service747 gateway747 storage747 network747 latency747 buffer747", 10),
        ["service747", "gateway747", "storage747", "network747", "latency747", "buffer747"],
    ),
    (
        ("service747 gateway747 storage747 network747 latency747 buffer747", 18),
        ["service747", "gateway747", "storage747", "network747", "latency747", "buffer747"],
    ),
    (
        ("service747 gateway747 storage747 network747 latency747 buffer747", 28),
        ["service747 gateway747", "storage747 network747", "latency747 buffer747"],
    ),
    (
        ("gateway747 storage747 network747 latency747 buffer747 queue747", 6),
        ["gateway747", "storage747", "network747", "latency747", "buffer747", "queue747"],
    ),
    (
        ("gateway747 storage747 network747 latency747 buffer747 queue747", 10),
        ["gateway747", "storage747", "network747", "latency747", "buffer747", "queue747"],
    ),
    (
        ("gateway747 storage747 network747 latency747 buffer747 queue747", 18),
        ["gateway747", "storage747", "network747", "latency747", "buffer747 queue747"],
    ),
    (
        ("gateway747 storage747 network747 latency747 buffer747 queue747", 28),
        ["gateway747 storage747", "network747 latency747", "buffer747 queue747"],
    ),
    (
        ("storage747 network747 latency747 buffer747 queue747 worker747", 6),
        ["storage747", "network747", "latency747", "buffer747", "queue747", "worker747"],
    ),
    (
        ("storage747 network747 latency747 buffer747 queue747 worker747", 10),
        ["storage747", "network747", "latency747", "buffer747", "queue747", "worker747"],
    ),
    (
        ("storage747 network747 latency747 buffer747 queue747 worker747", 18),
        ["storage747", "network747", "latency747", "buffer747 queue747", "worker747"],
    ),
    (
        ("storage747 network747 latency747 buffer747 queue747 worker747", 28),
        ["storage747 network747", "latency747 buffer747", "queue747 worker747"],
    ),
    (
        ("network747 latency747 buffer747 queue747 worker747 kernel747", 6),
        ["network747", "latency747", "buffer747", "queue747", "worker747", "kernel747"],
    ),
    (
        ("network747 latency747 buffer747 queue747 worker747 kernel747", 10),
        ["network747", "latency747", "buffer747", "queue747", "worker747", "kernel747"],
    ),
    (
        ("network747 latency747 buffer747 queue747 worker747 kernel747", 18),
        ["network747", "latency747", "buffer747 queue747", "worker747", "kernel747"],
    ),
    (
        ("network747 latency747 buffer747 queue747 worker747 kernel747", 28),
        ["network747 latency747", "buffer747 queue747 worker747", "kernel747"],
    ),
    (
        ("latency747 buffer747 queue747 worker747 kernel747 signal747", 6),
        ["latency747", "buffer747", "queue747", "worker747", "kernel747", "signal747"],
    ),
    (
        ("latency747 buffer747 queue747 worker747 kernel747 signal747", 10),
        ["latency747", "buffer747", "queue747", "worker747", "kernel747", "signal747"],
    ),
    (
        ("latency747 buffer747 queue747 worker747 kernel747 signal747", 18),
        ["latency747", "buffer747 queue747", "worker747", "kernel747", "signal747"],
    ),
    (
        ("latency747 buffer747 queue747 worker747 kernel747 signal747", 28),
        ["latency747 buffer747", "queue747 worker747 kernel747", "signal747"],
    ),
    (
        ("buffer747 queue747 worker747 kernel747 signal747 packet747", 6),
        ["buffer747", "queue747", "worker747", "kernel747", "signal747", "packet747"],
    ),
    (
        ("buffer747 queue747 worker747 kernel747 signal747 packet747", 10),
        ["buffer747", "queue747", "worker747", "kernel747", "signal747", "packet747"],
    ),
    (
        ("buffer747 queue747 worker747 kernel747 signal747 packet747", 18),
        ["buffer747 queue747", "worker747", "kernel747", "signal747", "packet747"],
    ),
    (
        ("buffer747 queue747 worker747 kernel747 signal747 packet747", 28),
        ["buffer747 queue747 worker747", "kernel747 signal747", "packet747"],
    ),
    (
        ("queue747 worker747 kernel747 signal747 packet747 router747", 6),
        ["queue747", "worker747", "kernel747", "signal747", "packet747", "router747"],
    ),
    (
        ("queue747 worker747 kernel747 signal747 packet747 router747", 10),
        ["queue747", "worker747", "kernel747", "signal747", "packet747", "router747"],
    ),
    (
        ("queue747 worker747 kernel747 signal747 packet747 router747", 18),
        ["queue747 worker747", "kernel747", "signal747", "packet747", "router747"],
    ),
    (
        ("queue747 worker747 kernel747 signal747 packet747 router747", 28),
        ["queue747 worker747 kernel747", "signal747 packet747", "router747"],
    ),
    (
        ("worker747 kernel747 signal747 packet747 router747 cluster747", 6),
        ["worker747", "kernel747", "signal747", "packet747", "router747", "cluster747"],
    ),
    (
        ("worker747 kernel747 signal747 packet747 router747 cluster747", 10),
        ["worker747", "kernel747", "signal747", "packet747", "router747", "cluster747"],
    ),
    (
        ("worker747 kernel747 signal747 packet747 router747 cluster747", 18),
        ["worker747", "kernel747", "signal747", "packet747", "router747", "cluster747"],
    ),
    (
        ("worker747 kernel747 signal747 packet747 router747 cluster747", 28),
        ["worker747 kernel747", "signal747 packet747", "router747 cluster747"],
    ),
    (
        ("kernel747 signal747 packet747 router747 cluster747 mirror747", 6),
        ["kernel747", "signal747", "packet747", "router747", "cluster747", "mirror747"],
    ),
    (
        ("kernel747 signal747 packet747 router747 cluster747 mirror747", 10),
        ["kernel747", "signal747", "packet747", "router747", "cluster747", "mirror747"],
    ),
    (
        ("kernel747 signal747 packet747 router747 cluster747 mirror747", 18),
        ["kernel747", "signal747", "packet747", "router747", "cluster747", "mirror747"],
    ),
    (
        ("kernel747 signal747 packet747 router747 cluster747 mirror747", 28),
        ["kernel747 signal747", "packet747 router747", "cluster747 mirror747"],
    ),
    (
        ("signal747 packet747 router747 cluster747 mirror747 filter747", 6),
        ["signal747", "packet747", "router747", "cluster747", "mirror747", "filter747"],
    ),
    (
        ("signal747 packet747 router747 cluster747 mirror747 filter747", 10),
        ["signal747", "packet747", "router747", "cluster747", "mirror747", "filter747"],
    ),
    (
        ("signal747 packet747 router747 cluster747 mirror747 filter747", 18),
        ["signal747", "packet747", "router747", "cluster747", "mirror747", "filter747"],
    ),
    (
        ("signal747 packet747 router747 cluster747 mirror747 filter747", 28),
        ["signal747 packet747", "router747 cluster747", "mirror747 filter747"],
    ),
    (
        ("packet747 router747 cluster747 mirror747 filter747 ranking747", 6),
        ["packet747", "router747", "cluster747", "mirror747", "filter747", "ranking747"],
    ),
    (
        ("packet747 router747 cluster747 mirror747 filter747 ranking747", 10),
        ["packet747", "router747", "cluster747", "mirror747", "filter747", "ranking747"],
    ),
    (
        ("packet747 router747 cluster747 mirror747 filter747 ranking747", 18),
        ["packet747", "router747", "cluster747", "mirror747", "filter747", "ranking747"],
    ),
    (
        ("packet747 router747 cluster747 mirror747 filter747 ranking747", 28),
        ["packet747 router747", "cluster747 mirror747", "filter747 ranking747"],
    ),
    (
        ("router747 cluster747 mirror747 filter747 ranking747 encoding747", 6),
        ["router747", "cluster747", "mirror747", "filter747", "ranking747", "encoding747"],
    ),
    (
        ("router747 cluster747 mirror747 filter747 ranking747 encoding747", 10),
        ["router747", "cluster747", "mirror747", "filter747", "ranking747", "encoding747"],
    ),
    (
        ("router747 cluster747 mirror747 filter747 ranking747 encoding747", 18),
        ["router747", "cluster747", "mirror747", "filter747", "ranking747", "encoding747"],
    ),
    (
        ("router747 cluster747 mirror747 filter747 ranking747 encoding747", 28),
        ["router747 cluster747", "mirror747 filter747", "ranking747 encoding747"],
    ),
    (
        ("cluster747 mirror747 filter747 ranking747 encoding747 mapping747", 6),
        ["cluster747", "mirror747", "filter747", "ranking747", "encoding747", "mapping747"],
    ),
    (
        ("cluster747 mirror747 filter747 ranking747 encoding747 mapping747", 10),
        ["cluster747", "mirror747", "filter747", "ranking747", "encoding747", "mapping747"],
    ),
    (
        ("cluster747 mirror747 filter747 ranking747 encoding747 mapping747", 18),
        ["cluster747", "mirror747", "filter747", "ranking747", "encoding747", "mapping747"],
    ),
    (
        ("cluster747 mirror747 filter747 ranking747 encoding747 mapping747", 28),
        ["cluster747 mirror747", "filter747 ranking747", "encoding747 mapping747"],
    ),
    (
        ("mirror747 filter747 ranking747 encoding747 mapping747 record747", 6),
        ["mirror747", "filter747", "ranking747", "encoding747", "mapping747", "record747"],
    ),
    (
        ("mirror747 filter747 ranking747 encoding747 mapping747 record747", 10),
        ["mirror747", "filter747", "ranking747", "encoding747", "mapping747", "record747"],
    ),
    (
        ("mirror747 filter747 ranking747 encoding747 mapping747 record747", 18),
        ["mirror747", "filter747", "ranking747", "encoding747", "mapping747", "record747"],
    ),
    (
        ("mirror747 filter747 ranking747 encoding747 mapping747 record747", 28),
        ["mirror747 filter747", "ranking747 encoding747", "mapping747 record747"],
    ),
    (
        ("filter747 ranking747 encoding747 mapping747 record747 candle747", 6),
        ["filter747", "ranking747", "encoding747", "mapping747", "record747", "candle747"],
    ),
    (
        ("filter747 ranking747 encoding747 mapping747 record747 candle747", 10),
        ["filter747", "ranking747", "encoding747", "mapping747", "record747", "candle747"],
    ),
    (
        ("filter747 ranking747 encoding747 mapping747 record747 candle747", 18),
        ["filter747", "ranking747", "encoding747", "mapping747", "record747", "candle747"],
    ),
    (
        ("filter747 ranking747 encoding747 mapping747 record747 candle747", 28),
        ["filter747 ranking747", "encoding747 mapping747", "record747 candle747"],
    ),
    (
        ("ranking747 encoding747 mapping747 record747 candle747 thread747", 6),
        ["ranking747", "encoding747", "mapping747", "record747", "candle747", "thread747"],
    ),
    (
        ("ranking747 encoding747 mapping747 record747 candle747 thread747", 10),
        ["ranking747", "encoding747", "mapping747", "record747", "candle747", "thread747"],
    ),
    (
        ("ranking747 encoding747 mapping747 record747 candle747 thread747", 18),
        ["ranking747", "encoding747", "mapping747", "record747", "candle747", "thread747"],
    ),
    (
        ("ranking747 encoding747 mapping747 record747 candle747 thread747", 28),
        ["ranking747 encoding747", "mapping747 record747", "candle747 thread747"],
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
