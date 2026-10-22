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
        ("round 28: the quick brown fox jumps over the lazy dog", 4),
        ["round", "28:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 28: the quick brown fox jumps over the lazy dog", 8),
        ["round", "28: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 28: the quick brown fox jumps over the lazy dog", 12),
        ["round 28:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 28: the quick brown fox jumps over the lazy dog", 16),
        ["round 28: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 28: the quick brown fox jumps over the lazy dog", 24),
        ["round 28: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 28: the quick brown fox jumps over the lazy dog", 32),
        ["round 28: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 28: agentuniverse is a framework for multi agents", 4),
        ["round", "28:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 28: agentuniverse is a framework for multi agents", 8),
        ["round", "28:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 28: agentuniverse is a framework for multi agents", 12),
        ["round 28:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 28: agentuniverse is a framework for multi agents", 16),
        ["round 28:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 28: agentuniverse is a framework for multi agents", 24),
        ["round 28: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 28: agentuniverse is a framework for multi agents", 32),
        ["round 28: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 28: knowledge stored as vectors enables retrieval", 4),
        ["round", "28:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 28: knowledge stored as vectors enables retrieval", 8),
        ["round", "28:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 28: knowledge stored as vectors enables retrieval", 12),
        ["round 28:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 28: knowledge stored as vectors enables retrieval", 16),
        ["round 28:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 28: knowledge stored as vectors enables retrieval", 24),
        ["round 28: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 28: knowledge stored as vectors enables retrieval", 32),
        ["round 28: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 28: the processor reads the record then stops", 4),
        ["round", "28:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 28: the processor reads the record then stops", 8),
        ["round", "28: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 28: the processor reads the record then stops", 12),
        ["round 28:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 28: the processor reads the record then stops", 16),
        ["round 28: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 28: the processor reads the record then stops", 24),
        ["round 28: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 28: the processor reads the record then stops", 32),
        ["round 28: the processor reads", "the record then stops"],
    ),
    (
        ("round 28: a worker pulls the next task from the queue", 4),
        ["round", "28:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 28: a worker pulls the next task from the queue", 8),
        ["round", "28: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 28: a worker pulls the next task from the queue", 12),
        ["round 28: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 28: a worker pulls the next task from the queue", 16),
        ["round 28: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 28: a worker pulls the next task from the queue", 24),
        ["round 28: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 28: a worker pulls the next task from the queue", 32),
        ["round 28: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 28: signals travel through the network layer", 4),
        ["round", "28:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 28: signals travel through the network layer", 8),
        ["round", "28:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 28: signals travel through the network layer", 12),
        ["round 28:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 28: signals travel through the network layer", 16),
        ["round 28:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 28: signals travel through the network layer", 24),
        ["round 28: signals travel", "through the network", "layer"],
    ),
    (
        ("round 28: signals travel through the network layer", 32),
        ["round 28: signals travel through", "the network layer"],
    ),
    (
        ("round 28: the gateway routes each request by policy", 4),
        ["round", "28:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 28: the gateway routes each request by policy", 8),
        ["round", "28: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 28: the gateway routes each request by policy", 12),
        ["round 28:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 28: the gateway routes each request by policy", 16),
        ["round 28: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 28: the gateway routes each request by policy", 24),
        ["round 28: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 28: the gateway routes each request by policy", 32),
        ["round 28: the gateway routes", "each request by policy"],
    ),
    (
        ("round 28: memory grows until the buffer is full", 4),
        ["round", "28:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 28: memory grows until the buffer is full", 8),
        ["round", "28:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 28: memory grows until the buffer is full", 12),
        ["round 28:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 28: memory grows until the buffer is full", 16),
        ["round 28: memory", "grows until the", "buffer is full"],
    ),
    (("round 28: memory grows until the buffer is full", 24), ["round 28: memory grows", "until the buffer is full"]),
    (("round 28: memory grows until the buffer is full", 32), ["round 28: memory grows until the", "buffer is full"]),
    (
        ("round 28: the cluster mirrors every packet twice", 4),
        ["round", "28:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 28: the cluster mirrors every packet twice", 8),
        ["round", "28: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 28: the cluster mirrors every packet twice", 12),
        ["round 28:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 28: the cluster mirrors every packet twice", 16),
        ["round 28: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 28: the cluster mirrors every packet twice", 24),
        ["round 28: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 28: the cluster mirrors every packet twice", 32), ["round 28: the cluster mirrors", "every packet twice"]),
    (
        ("round 28: ranking uses tokens learned from the corpus", 4),
        ["round", "28:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 28: ranking uses tokens learned from the corpus", 8),
        ["round", "28:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 28: ranking uses tokens learned from the corpus", 12),
        ["round 28:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 28: ranking uses tokens learned from the corpus", 16),
        ["round 28:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 28: ranking uses tokens learned from the corpus", 24),
        ["round 28: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 28: ranking uses tokens learned from the corpus", 32),
        ["round 28: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 28: a long session ends when the candle dies", 4),
        ["round", "28:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 28: a long session ends when the candle dies", 8),
        ["round", "28: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 28: a long session ends when the candle dies", 12),
        ["round 28: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 28: a long session ends when the candle dies", 16),
        ["round 28: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 28: a long session ends when the candle dies", 24),
        ["round 28: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 28: a long session ends when the candle dies", 32),
        ["round 28: a long session ends", "when the candle dies"],
    ),
    (
        ("round 28: encode the prompt then map the result", 4),
        ["round", "28:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 28: encode the prompt then map the result", 8),
        ["round", "28:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 28: encode the prompt then map the result", 12),
        ["round 28:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 28: encode the prompt then map the result", 16),
        ["round 28: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 28: encode the prompt then map the result", 24),
        ["round 28: encode the", "prompt then map the", "result"],
    ),
    (("round 28: encode the prompt then map the result", 32), ["round 28: encode the prompt then", "map the result"]),
    (
        ("round 28: the kernel wakes the worker at dawn", 4),
        ["round", "28:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 28: the kernel wakes the worker at dawn", 8),
        ["round", "28: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 28: the kernel wakes the worker at dawn", 12),
        ["round 28:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 28: the kernel wakes the worker at dawn", 16), ["round 28: the", "kernel wakes the", "worker at dawn"]),
    (("round 28: the kernel wakes the worker at dawn", 24), ["round 28: the kernel", "wakes the worker at dawn"]),
    (("round 28: the kernel wakes the worker at dawn", 32), ["round 28: the kernel wakes the", "worker at dawn"]),
    (
        ("round 28: service latency drops after the patch", 4),
        ["round", "28:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 28: service latency drops after the patch", 8),
        ["round", "28:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 28: service latency drops after the patch", 12),
        ["round 28:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 28: service latency drops after the patch", 16),
        ["round 28:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 28: service latency drops after the patch", 24),
        ["round 28: service", "latency drops after the", "patch"],
    ),
    (("round 28: service latency drops after the patch", 32), ["round 28: service latency drops", "after the patch"]),
    (
        ("round 28: the library caches every vector it sees", 4),
        ["round", "28:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 28: the library caches every vector it sees", 8),
        ["round", "28: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 28: the library caches every vector it sees", 12),
        ["round 28:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 28: the library caches every vector it sees", 16),
        ["round 28: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 28: the library caches every vector it sees", 24),
        ["round 28: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 28: the library caches every vector it sees", 32),
        ["round 28: the library caches", "every vector it sees"],
    ),
    (
        ("round 28: agents argue then the debate resolves", 4),
        ["round", "28:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 28: agents argue then the debate resolves", 8),
        ["round", "28:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 28: agents argue then the debate resolves", 12),
        ["round 28:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 28: agents argue then the debate resolves", 16),
        ["round 28: agents", "argue then the", "debate resolves"],
    ),
    (("round 28: agents argue then the debate resolves", 24), ["round 28: agents argue", "then the debate resolves"]),
    (("round 28: agents argue then the debate resolves", 32), ["round 28: agents argue then the", "debate resolves"]),
    (
        ("round 28: the filter keeps only strong matches", 4),
        ["round", "28:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 28: the filter keeps only strong matches", 8),
        ["round", "28: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 28: the filter keeps only strong matches", 12),
        ["round 28:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 28: the filter keeps only strong matches", 16),
        ["round 28: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 28: the filter keeps only strong matches", 24), ["round 28: the filter", "keeps only strong", "matches"]),
    (("round 28: the filter keeps only strong matches", 32), ["round 28: the filter keeps only", "strong matches"]),
    (
        ("round 28: the model answers with a short reply", 4),
        ["round", "28:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 28: the model answers with a short reply", 8),
        ["round", "28: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 28: the model answers with a short reply", 12),
        ["round 28:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 28: the model answers with a short reply", 16),
        ["round 28: the", "model answers", "with a short", "reply"],
    ),
    (("round 28: the model answers with a short reply", 24), ["round 28: the model", "answers with a short", "reply"]),
    (("round 28: the model answers with a short reply", 32), ["round 28: the model answers with", "a short reply"]),
    (
        ("round 28: the recorder stores the reasoning trace", 4),
        ["round", "28:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 28: the recorder stores the reasoning trace", 8),
        ["round", "28: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 28: the recorder stores the reasoning trace", 12),
        ["round 28:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 28: the recorder stores the reasoning trace", 16),
        ["round 28: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 28: the recorder stores the reasoning trace", 24),
        ["round 28: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 28: the recorder stores the reasoning trace", 32),
        ["round 28: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 28: the angel watches the processor run", 4),
        ["round", "28:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 28: the angel watches the processor run", 8),
        ["round", "28: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 28: the angel watches the processor run", 12),
        ["round 28:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 28: the angel watches the processor run", 16), ["round 28: the", "angel watches", "the processor", "run"]),
    (("round 28: the angel watches the processor run", 24), ["round 28: the angel", "watches the processor", "run"]),
    (("round 28: the angel watches the processor run", 32), ["round 28: the angel watches the", "processor run"]),
    (
        ("round 28: angle of the vector decides the match", 4),
        ["round", "28:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 28: angle of the vector decides the match", 8),
        ["round", "28:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 28: angle of the vector decides the match", 12),
        ["round 28:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 28: angle of the vector decides the match", 16),
        ["round 28: angle", "of the vector", "decides the", "match"],
    ),
    (("round 28: angle of the vector decides the match", 24), ["round 28: angle of the", "vector decides the match"]),
    (("round 28: angle of the vector decides the match", 32), ["round 28: angle of the vector", "decides the match"]),
    (
        ("round 28: the candle burns twice as long at night", 4),
        ["round", "28:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 28: the candle burns twice as long at night", 8),
        ["round", "28: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 28: the candle burns twice as long at night", 12),
        ["round 28:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 28: the candle burns twice as long at night", 16),
        ["round 28: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 28: the candle burns twice as long at night", 24),
        ["round 28: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 28: the candle burns twice as long at night", 32),
        ["round 28: the candle burns twice", "as long at night"],
    ),
    (
        ("round 28: a mirror of the universe in one line", 4),
        ["round", "28:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 28: a mirror of the universe in one line", 8),
        ["round", "28: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 28: a mirror of the universe in one line", 12),
        ["round 28: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 28: a mirror of the universe in one line", 16),
        ["round 28: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 28: a mirror of the universe in one line", 24), ["round 28: a mirror of", "the universe in one line"]),
    (("round 28: a mirror of the universe in one line", 32), ["round 28: a mirror of the", "universe in one line"]),
    (
        ("round 28: the queue drains before the storm", 4),
        ["round", "28:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 28: the queue drains before the storm", 8),
        ["round", "28: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 28: the queue drains before the storm", 12), ["round 28:", "the queue", "drains", "before the", "storm"]),
    (("round 28: the queue drains before the storm", 16), ["round 28: the", "queue drains", "before the storm"]),
    (("round 28: the queue drains before the storm", 24), ["round 28: the queue", "drains before the storm"]),
    (("round 28: the queue drains before the storm", 32), ["round 28: the queue drains", "before the storm"]),
    (
        ("kitten28 sitting28 agent28 angle28 universe28 memory28", 6),
        ["kitten28", "sitting28", "agent28", "angle28", "universe28", "memory28"],
    ),
    (
        ("kitten28 sitting28 agent28 angle28 universe28 memory28", 10),
        ["kitten28", "sitting28", "agent28", "angle28", "universe28", "memory28"],
    ),
    (
        ("kitten28 sitting28 agent28 angle28 universe28 memory28", 18),
        ["kitten28 sitting28", "agent28 angle28", "universe28", "memory28"],
    ),
    (
        ("kitten28 sitting28 agent28 angle28 universe28 memory28", 28),
        ["kitten28 sitting28 agent28", "angle28 universe28 memory28"],
    ),
    (
        ("sitting28 agent28 angle28 universe28 memory28 stream28", 6),
        ["sitting28", "agent28", "angle28", "universe28", "memory28", "stream28"],
    ),
    (
        ("sitting28 agent28 angle28 universe28 memory28 stream28", 10),
        ["sitting28", "agent28", "angle28", "universe28", "memory28", "stream28"],
    ),
    (
        ("sitting28 agent28 angle28 universe28 memory28 stream28", 18),
        ["sitting28 agent28", "angle28 universe28", "memory28 stream28"],
    ),
    (
        ("sitting28 agent28 angle28 universe28 memory28 stream28", 28),
        ["sitting28 agent28 angle28", "universe28 memory28 stream28"],
    ),
    (
        ("agent28 angle28 universe28 memory28 stream28 context28", 6),
        ["agent28", "angle28", "universe28", "memory28", "stream28", "context28"],
    ),
    (
        ("agent28 angle28 universe28 memory28 stream28 context28", 10),
        ["agent28", "angle28", "universe28", "memory28", "stream28", "context28"],
    ),
    (
        ("agent28 angle28 universe28 memory28 stream28 context28", 18),
        ["agent28 angle28", "universe28", "memory28 stream28", "context28"],
    ),
    (
        ("agent28 angle28 universe28 memory28 stream28 context28", 28),
        ["agent28 angle28 universe28", "memory28 stream28 context28"],
    ),
    (
        ("angle28 universe28 memory28 stream28 context28 knowledge28", 6),
        ["angle28", "universe28", "memory28", "stream28", "context28", "knowledge28"],
    ),
    (
        ("angle28 universe28 memory28 stream28 context28 knowledge28", 10),
        ["angle28", "universe28", "memory28", "stream28", "context28", "knowledge28"],
    ),
    (
        ("angle28 universe28 memory28 stream28 context28 knowledge28", 18),
        ["angle28 universe28", "memory28 stream28", "context28", "knowledge28"],
    ),
    (
        ("angle28 universe28 memory28 stream28 context28 knowledge28", 28),
        ["angle28 universe28 memory28", "stream28 context28", "knowledge28"],
    ),
    (
        ("universe28 memory28 stream28 context28 knowledge28 vector28", 6),
        ["universe28", "memory28", "stream28", "context28", "knowledge28", "vector28"],
    ),
    (
        ("universe28 memory28 stream28 context28 knowledge28 vector28", 10),
        ["universe28", "memory28", "stream28", "context28", "knowledge28", "vector28"],
    ),
    (
        ("universe28 memory28 stream28 context28 knowledge28 vector28", 18),
        ["universe28", "memory28 stream28", "context28", "knowledge28", "vector28"],
    ),
    (
        ("universe28 memory28 stream28 context28 knowledge28 vector28", 28),
        ["universe28 memory28 stream28", "context28 knowledge28", "vector28"],
    ),
    (
        ("memory28 stream28 context28 knowledge28 vector28 processor28", 6),
        ["memory28", "stream28", "context28", "knowledge28", "vector28", "processor28"],
    ),
    (
        ("memory28 stream28 context28 knowledge28 vector28 processor28", 10),
        ["memory28", "stream28", "context28", "knowledge28", "vector28", "processor28"],
    ),
    (
        ("memory28 stream28 context28 knowledge28 vector28 processor28", 18),
        ["memory28 stream28", "context28", "knowledge28", "vector28", "processor28"],
    ),
    (
        ("memory28 stream28 context28 knowledge28 vector28 processor28", 28),
        ["memory28 stream28 context28", "knowledge28 vector28", "processor28"],
    ),
    (
        ("stream28 context28 knowledge28 vector28 processor28 reasoning28", 6),
        ["stream28", "context28", "knowledge28", "vector28", "processor28", "reasoning28"],
    ),
    (
        ("stream28 context28 knowledge28 vector28 processor28 reasoning28", 10),
        ["stream28", "context28", "knowledge28", "vector28", "processor28", "reasoning28"],
    ),
    (
        ("stream28 context28 knowledge28 vector28 processor28 reasoning28", 18),
        ["stream28 context28", "knowledge28", "vector28", "processor28", "reasoning28"],
    ),
    (
        ("stream28 context28 knowledge28 vector28 processor28 reasoning28", 28),
        ["stream28 context28", "knowledge28 vector28", "processor28 reasoning28"],
    ),
    (
        ("context28 knowledge28 vector28 processor28 reasoning28 machine28", 6),
        ["context28", "knowledge28", "vector28", "processor28", "reasoning28", "machine28"],
    ),
    (
        ("context28 knowledge28 vector28 processor28 reasoning28 machine28", 10),
        ["context28", "knowledge28", "vector28", "processor28", "reasoning28", "machine28"],
    ),
    (
        ("context28 knowledge28 vector28 processor28 reasoning28 machine28", 18),
        ["context28", "knowledge28", "vector28", "processor28", "reasoning28", "machine28"],
    ),
    (
        ("context28 knowledge28 vector28 processor28 reasoning28 machine28", 28),
        ["context28 knowledge28", "vector28 processor28", "reasoning28 machine28"],
    ),
    (
        ("knowledge28 vector28 processor28 reasoning28 machine28 learning28", 6),
        ["knowledge28", "vector28", "processor28", "reasoning28", "machine28", "learning28"],
    ),
    (
        ("knowledge28 vector28 processor28 reasoning28 machine28 learning28", 10),
        ["knowledge28", "vector28", "processor28", "reasoning28", "machine28", "learning28"],
    ),
    (
        ("knowledge28 vector28 processor28 reasoning28 machine28 learning28", 18),
        ["knowledge28", "vector28", "processor28", "reasoning28", "machine28", "learning28"],
    ),
    (
        ("knowledge28 vector28 processor28 reasoning28 machine28 learning28", 28),
        ["knowledge28 vector28", "processor28 reasoning28", "machine28 learning28"],
    ),
    (
        ("vector28 processor28 reasoning28 machine28 learning28 model28", 6),
        ["vector28", "processor28", "reasoning28", "machine28", "learning28", "model28"],
    ),
    (
        ("vector28 processor28 reasoning28 machine28 learning28 model28", 10),
        ["vector28", "processor28", "reasoning28", "machine28", "learning28", "model28"],
    ),
    (
        ("vector28 processor28 reasoning28 machine28 learning28 model28", 18),
        ["vector28", "processor28", "reasoning28", "machine28", "learning28 model28"],
    ),
    (
        ("vector28 processor28 reasoning28 machine28 learning28 model28", 28),
        ["vector28 processor28", "reasoning28 machine28", "learning28 model28"],
    ),
    (
        ("processor28 reasoning28 machine28 learning28 model28 token28", 6),
        ["processor28", "reasoning28", "machine28", "learning28", "model28", "token28"],
    ),
    (
        ("processor28 reasoning28 machine28 learning28 model28 token28", 10),
        ["processor28", "reasoning28", "machine28", "learning28", "model28", "token28"],
    ),
    (
        ("processor28 reasoning28 machine28 learning28 model28 token28", 18),
        ["processor28", "reasoning28", "machine28", "learning28 model28", "token28"],
    ),
    (
        ("processor28 reasoning28 machine28 learning28 model28 token28", 28),
        ["processor28 reasoning28", "machine28 learning28 model28", "token28"],
    ),
    (
        ("reasoning28 machine28 learning28 model28 token28 prompt28", 6),
        ["reasoning28", "machine28", "learning28", "model28", "token28", "prompt28"],
    ),
    (
        ("reasoning28 machine28 learning28 model28 token28 prompt28", 10),
        ["reasoning28", "machine28", "learning28", "model28", "token28", "prompt28"],
    ),
    (
        ("reasoning28 machine28 learning28 model28 token28 prompt28", 18),
        ["reasoning28", "machine28", "learning28 model28", "token28 prompt28"],
    ),
    (
        ("reasoning28 machine28 learning28 model28 token28 prompt28", 28),
        ["reasoning28 machine28", "learning28 model28 token28", "prompt28"],
    ),
    (
        ("machine28 learning28 model28 token28 prompt28 session28", 6),
        ["machine28", "learning28", "model28", "token28", "prompt28", "session28"],
    ),
    (
        ("machine28 learning28 model28 token28 prompt28 session28", 10),
        ["machine28", "learning28", "model28", "token28", "prompt28", "session28"],
    ),
    (
        ("machine28 learning28 model28 token28 prompt28 session28", 18),
        ["machine28", "learning28 model28", "token28 prompt28", "session28"],
    ),
    (
        ("machine28 learning28 model28 token28 prompt28 session28", 28),
        ["machine28 learning28 model28", "token28 prompt28 session28"],
    ),
    (
        ("learning28 model28 token28 prompt28 session28 library28", 6),
        ["learning28", "model28", "token28", "prompt28", "session28", "library28"],
    ),
    (
        ("learning28 model28 token28 prompt28 session28 library28", 10),
        ["learning28", "model28", "token28", "prompt28", "session28", "library28"],
    ),
    (
        ("learning28 model28 token28 prompt28 session28 library28", 18),
        ["learning28 model28", "token28 prompt28", "session28", "library28"],
    ),
    (
        ("learning28 model28 token28 prompt28 session28 library28", 28),
        ["learning28 model28 token28", "prompt28 session28 library28"],
    ),
    (
        ("model28 token28 prompt28 session28 library28 service28", 6),
        ["model28", "token28", "prompt28", "session28", "library28", "service28"],
    ),
    (
        ("model28 token28 prompt28 session28 library28 service28", 10),
        ["model28", "token28", "prompt28", "session28", "library28", "service28"],
    ),
    (
        ("model28 token28 prompt28 session28 library28 service28", 18),
        ["model28 token28", "prompt28 session28", "library28", "service28"],
    ),
    (
        ("model28 token28 prompt28 session28 library28 service28", 28),
        ["model28 token28 prompt28", "session28 library28", "service28"],
    ),
    (
        ("token28 prompt28 session28 library28 service28 gateway28", 6),
        ["token28", "prompt28", "session28", "library28", "service28", "gateway28"],
    ),
    (
        ("token28 prompt28 session28 library28 service28 gateway28", 10),
        ["token28", "prompt28", "session28", "library28", "service28", "gateway28"],
    ),
    (
        ("token28 prompt28 session28 library28 service28 gateway28", 18),
        ["token28 prompt28", "session28", "library28", "service28", "gateway28"],
    ),
    (
        ("token28 prompt28 session28 library28 service28 gateway28", 28),
        ["token28 prompt28 session28", "library28 service28", "gateway28"],
    ),
    (
        ("prompt28 session28 library28 service28 gateway28 storage28", 6),
        ["prompt28", "session28", "library28", "service28", "gateway28", "storage28"],
    ),
    (
        ("prompt28 session28 library28 service28 gateway28 storage28", 10),
        ["prompt28", "session28", "library28", "service28", "gateway28", "storage28"],
    ),
    (
        ("prompt28 session28 library28 service28 gateway28 storage28", 18),
        ["prompt28 session28", "library28", "service28", "gateway28", "storage28"],
    ),
    (
        ("prompt28 session28 library28 service28 gateway28 storage28", 28),
        ["prompt28 session28 library28", "service28 gateway28", "storage28"],
    ),
    (
        ("session28 library28 service28 gateway28 storage28 network28", 6),
        ["session28", "library28", "service28", "gateway28", "storage28", "network28"],
    ),
    (
        ("session28 library28 service28 gateway28 storage28 network28", 10),
        ["session28", "library28", "service28", "gateway28", "storage28", "network28"],
    ),
    (
        ("session28 library28 service28 gateway28 storage28 network28", 18),
        ["session28", "library28", "service28", "gateway28", "storage28", "network28"],
    ),
    (
        ("session28 library28 service28 gateway28 storage28 network28", 28),
        ["session28 library28", "service28 gateway28", "storage28 network28"],
    ),
    (
        ("library28 service28 gateway28 storage28 network28 latency28", 6),
        ["library28", "service28", "gateway28", "storage28", "network28", "latency28"],
    ),
    (
        ("library28 service28 gateway28 storage28 network28 latency28", 10),
        ["library28", "service28", "gateway28", "storage28", "network28", "latency28"],
    ),
    (
        ("library28 service28 gateway28 storage28 network28 latency28", 18),
        ["library28", "service28", "gateway28", "storage28", "network28", "latency28"],
    ),
    (
        ("library28 service28 gateway28 storage28 network28 latency28", 28),
        ["library28 service28", "gateway28 storage28", "network28 latency28"],
    ),
    (
        ("service28 gateway28 storage28 network28 latency28 buffer28", 6),
        ["service28", "gateway28", "storage28", "network28", "latency28", "buffer28"],
    ),
    (
        ("service28 gateway28 storage28 network28 latency28 buffer28", 10),
        ["service28", "gateway28", "storage28", "network28", "latency28", "buffer28"],
    ),
    (
        ("service28 gateway28 storage28 network28 latency28 buffer28", 18),
        ["service28", "gateway28", "storage28", "network28", "latency28 buffer28"],
    ),
    (
        ("service28 gateway28 storage28 network28 latency28 buffer28", 28),
        ["service28 gateway28", "storage28 network28", "latency28 buffer28"],
    ),
    (
        ("gateway28 storage28 network28 latency28 buffer28 queue28", 6),
        ["gateway28", "storage28", "network28", "latency28", "buffer28", "queue28"],
    ),
    (
        ("gateway28 storage28 network28 latency28 buffer28 queue28", 10),
        ["gateway28", "storage28", "network28", "latency28", "buffer28", "queue28"],
    ),
    (
        ("gateway28 storage28 network28 latency28 buffer28 queue28", 18),
        ["gateway28", "storage28", "network28", "latency28 buffer28", "queue28"],
    ),
    (
        ("gateway28 storage28 network28 latency28 buffer28 queue28", 28),
        ["gateway28 storage28", "network28 latency28 buffer28", "queue28"],
    ),
    (
        ("storage28 network28 latency28 buffer28 queue28 worker28", 6),
        ["storage28", "network28", "latency28", "buffer28", "queue28", "worker28"],
    ),
    (
        ("storage28 network28 latency28 buffer28 queue28 worker28", 10),
        ["storage28", "network28", "latency28", "buffer28", "queue28", "worker28"],
    ),
    (
        ("storage28 network28 latency28 buffer28 queue28 worker28", 18),
        ["storage28", "network28", "latency28 buffer28", "queue28 worker28"],
    ),
    (
        ("storage28 network28 latency28 buffer28 queue28 worker28", 28),
        ["storage28 network28", "latency28 buffer28 queue28", "worker28"],
    ),
    (
        ("network28 latency28 buffer28 queue28 worker28 kernel28", 6),
        ["network28", "latency28", "buffer28", "queue28", "worker28", "kernel28"],
    ),
    (
        ("network28 latency28 buffer28 queue28 worker28 kernel28", 10),
        ["network28", "latency28", "buffer28", "queue28", "worker28", "kernel28"],
    ),
    (
        ("network28 latency28 buffer28 queue28 worker28 kernel28", 18),
        ["network28", "latency28 buffer28", "queue28 worker28", "kernel28"],
    ),
    (
        ("network28 latency28 buffer28 queue28 worker28 kernel28", 28),
        ["network28 latency28 buffer28", "queue28 worker28 kernel28"],
    ),
    (
        ("latency28 buffer28 queue28 worker28 kernel28 signal28", 6),
        ["latency28", "buffer28", "queue28", "worker28", "kernel28", "signal28"],
    ),
    (
        ("latency28 buffer28 queue28 worker28 kernel28 signal28", 10),
        ["latency28", "buffer28", "queue28", "worker28", "kernel28", "signal28"],
    ),
    (
        ("latency28 buffer28 queue28 worker28 kernel28 signal28", 18),
        ["latency28 buffer28", "queue28 worker28", "kernel28 signal28"],
    ),
    (
        ("latency28 buffer28 queue28 worker28 kernel28 signal28", 28),
        ["latency28 buffer28 queue28", "worker28 kernel28 signal28"],
    ),
    (
        ("buffer28 queue28 worker28 kernel28 signal28 packet28", 6),
        ["buffer28", "queue28", "worker28", "kernel28", "signal28", "packet28"],
    ),
    (
        ("buffer28 queue28 worker28 kernel28 signal28 packet28", 10),
        ["buffer28", "queue28", "worker28", "kernel28", "signal28", "packet28"],
    ),
    (
        ("buffer28 queue28 worker28 kernel28 signal28 packet28", 18),
        ["buffer28 queue28", "worker28 kernel28", "signal28 packet28"],
    ),
    (
        ("buffer28 queue28 worker28 kernel28 signal28 packet28", 28),
        ["buffer28 queue28 worker28", "kernel28 signal28 packet28"],
    ),
    (
        ("queue28 worker28 kernel28 signal28 packet28 router28", 6),
        ["queue28", "worker28", "kernel28", "signal28", "packet28", "router28"],
    ),
    (
        ("queue28 worker28 kernel28 signal28 packet28 router28", 10),
        ["queue28", "worker28", "kernel28", "signal28", "packet28", "router28"],
    ),
    (
        ("queue28 worker28 kernel28 signal28 packet28 router28", 18),
        ["queue28 worker28", "kernel28 signal28", "packet28 router28"],
    ),
    (
        ("queue28 worker28 kernel28 signal28 packet28 router28", 28),
        ["queue28 worker28 kernel28", "signal28 packet28 router28"],
    ),
    (
        ("worker28 kernel28 signal28 packet28 router28 cluster28", 6),
        ["worker28", "kernel28", "signal28", "packet28", "router28", "cluster28"],
    ),
    (
        ("worker28 kernel28 signal28 packet28 router28 cluster28", 10),
        ["worker28", "kernel28", "signal28", "packet28", "router28", "cluster28"],
    ),
    (
        ("worker28 kernel28 signal28 packet28 router28 cluster28", 18),
        ["worker28 kernel28", "signal28 packet28", "router28 cluster28"],
    ),
    (
        ("worker28 kernel28 signal28 packet28 router28 cluster28", 28),
        ["worker28 kernel28 signal28", "packet28 router28 cluster28"],
    ),
    (
        ("kernel28 signal28 packet28 router28 cluster28 mirror28", 6),
        ["kernel28", "signal28", "packet28", "router28", "cluster28", "mirror28"],
    ),
    (
        ("kernel28 signal28 packet28 router28 cluster28 mirror28", 10),
        ["kernel28", "signal28", "packet28", "router28", "cluster28", "mirror28"],
    ),
    (
        ("kernel28 signal28 packet28 router28 cluster28 mirror28", 18),
        ["kernel28 signal28", "packet28 router28", "cluster28 mirror28"],
    ),
    (
        ("kernel28 signal28 packet28 router28 cluster28 mirror28", 28),
        ["kernel28 signal28 packet28", "router28 cluster28 mirror28"],
    ),
    (
        ("signal28 packet28 router28 cluster28 mirror28 filter28", 6),
        ["signal28", "packet28", "router28", "cluster28", "mirror28", "filter28"],
    ),
    (
        ("signal28 packet28 router28 cluster28 mirror28 filter28", 10),
        ["signal28", "packet28", "router28", "cluster28", "mirror28", "filter28"],
    ),
    (
        ("signal28 packet28 router28 cluster28 mirror28 filter28", 18),
        ["signal28 packet28", "router28 cluster28", "mirror28 filter28"],
    ),
    (
        ("signal28 packet28 router28 cluster28 mirror28 filter28", 28),
        ["signal28 packet28 router28", "cluster28 mirror28 filter28"],
    ),
    (
        ("packet28 router28 cluster28 mirror28 filter28 ranking28", 6),
        ["packet28", "router28", "cluster28", "mirror28", "filter28", "ranking28"],
    ),
    (
        ("packet28 router28 cluster28 mirror28 filter28 ranking28", 10),
        ["packet28", "router28", "cluster28", "mirror28", "filter28", "ranking28"],
    ),
    (
        ("packet28 router28 cluster28 mirror28 filter28 ranking28", 18),
        ["packet28 router28", "cluster28 mirror28", "filter28 ranking28"],
    ),
    (
        ("packet28 router28 cluster28 mirror28 filter28 ranking28", 28),
        ["packet28 router28 cluster28", "mirror28 filter28 ranking28"],
    ),
    (
        ("router28 cluster28 mirror28 filter28 ranking28 encoding28", 6),
        ["router28", "cluster28", "mirror28", "filter28", "ranking28", "encoding28"],
    ),
    (
        ("router28 cluster28 mirror28 filter28 ranking28 encoding28", 10),
        ["router28", "cluster28", "mirror28", "filter28", "ranking28", "encoding28"],
    ),
    (
        ("router28 cluster28 mirror28 filter28 ranking28 encoding28", 18),
        ["router28 cluster28", "mirror28 filter28", "ranking28", "encoding28"],
    ),
    (
        ("router28 cluster28 mirror28 filter28 ranking28 encoding28", 28),
        ["router28 cluster28 mirror28", "filter28 ranking28", "encoding28"],
    ),
    (
        ("cluster28 mirror28 filter28 ranking28 encoding28 mapping28", 6),
        ["cluster28", "mirror28", "filter28", "ranking28", "encoding28", "mapping28"],
    ),
    (
        ("cluster28 mirror28 filter28 ranking28 encoding28 mapping28", 10),
        ["cluster28", "mirror28", "filter28", "ranking28", "encoding28", "mapping28"],
    ),
    (
        ("cluster28 mirror28 filter28 ranking28 encoding28 mapping28", 18),
        ["cluster28 mirror28", "filter28 ranking28", "encoding28", "mapping28"],
    ),
    (
        ("cluster28 mirror28 filter28 ranking28 encoding28 mapping28", 28),
        ["cluster28 mirror28 filter28", "ranking28 encoding28", "mapping28"],
    ),
    (
        ("mirror28 filter28 ranking28 encoding28 mapping28 record28", 6),
        ["mirror28", "filter28", "ranking28", "encoding28", "mapping28", "record28"],
    ),
    (
        ("mirror28 filter28 ranking28 encoding28 mapping28 record28", 10),
        ["mirror28", "filter28", "ranking28", "encoding28", "mapping28", "record28"],
    ),
    (
        ("mirror28 filter28 ranking28 encoding28 mapping28 record28", 18),
        ["mirror28 filter28", "ranking28", "encoding28", "mapping28 record28"],
    ),
    (
        ("mirror28 filter28 ranking28 encoding28 mapping28 record28", 28),
        ["mirror28 filter28 ranking28", "encoding28 mapping28", "record28"],
    ),
    (
        ("filter28 ranking28 encoding28 mapping28 record28 candle28", 6),
        ["filter28", "ranking28", "encoding28", "mapping28", "record28", "candle28"],
    ),
    (
        ("filter28 ranking28 encoding28 mapping28 record28 candle28", 10),
        ["filter28", "ranking28", "encoding28", "mapping28", "record28", "candle28"],
    ),
    (
        ("filter28 ranking28 encoding28 mapping28 record28 candle28", 18),
        ["filter28 ranking28", "encoding28", "mapping28 record28", "candle28"],
    ),
    (
        ("filter28 ranking28 encoding28 mapping28 record28 candle28", 28),
        ["filter28 ranking28", "encoding28 mapping28", "record28 candle28"],
    ),
    (
        ("ranking28 encoding28 mapping28 record28 candle28 thread28", 6),
        ["ranking28", "encoding28", "mapping28", "record28", "candle28", "thread28"],
    ),
    (
        ("ranking28 encoding28 mapping28 record28 candle28 thread28", 10),
        ["ranking28", "encoding28", "mapping28", "record28", "candle28", "thread28"],
    ),
    (
        ("ranking28 encoding28 mapping28 record28 candle28 thread28", 18),
        ["ranking28", "encoding28", "mapping28 record28", "candle28 thread28"],
    ),
    (
        ("ranking28 encoding28 mapping28 record28 candle28 thread28", 28),
        ["ranking28 encoding28", "mapping28 record28 candle28", "thread28"],
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
