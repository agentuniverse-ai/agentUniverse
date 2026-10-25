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
        ("round 45: the quick brown fox jumps over the lazy dog", 4),
        ["round", "45:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 45: the quick brown fox jumps over the lazy dog", 8),
        ["round", "45: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 45: the quick brown fox jumps over the lazy dog", 12),
        ["round 45:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 45: the quick brown fox jumps over the lazy dog", 16),
        ["round 45: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 45: the quick brown fox jumps over the lazy dog", 24),
        ["round 45: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 45: the quick brown fox jumps over the lazy dog", 32),
        ["round 45: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 45: agentuniverse is a framework for multi agents", 4),
        ["round", "45:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 45: agentuniverse is a framework for multi agents", 8),
        ["round", "45:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 45: agentuniverse is a framework for multi agents", 12),
        ["round 45:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 45: agentuniverse is a framework for multi agents", 16),
        ["round 45:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 45: agentuniverse is a framework for multi agents", 24),
        ["round 45: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 45: agentuniverse is a framework for multi agents", 32),
        ["round 45: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 45: knowledge stored as vectors enables retrieval", 4),
        ["round", "45:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 45: knowledge stored as vectors enables retrieval", 8),
        ["round", "45:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 45: knowledge stored as vectors enables retrieval", 12),
        ["round 45:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 45: knowledge stored as vectors enables retrieval", 16),
        ["round 45:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 45: knowledge stored as vectors enables retrieval", 24),
        ["round 45: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 45: knowledge stored as vectors enables retrieval", 32),
        ["round 45: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 45: the processor reads the record then stops", 4),
        ["round", "45:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 45: the processor reads the record then stops", 8),
        ["round", "45: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 45: the processor reads the record then stops", 12),
        ["round 45:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 45: the processor reads the record then stops", 16),
        ["round 45: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 45: the processor reads the record then stops", 24),
        ["round 45: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 45: the processor reads the record then stops", 32),
        ["round 45: the processor reads", "the record then stops"],
    ),
    (
        ("round 45: a worker pulls the next task from the queue", 4),
        ["round", "45:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 45: a worker pulls the next task from the queue", 8),
        ["round", "45: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 45: a worker pulls the next task from the queue", 12),
        ["round 45: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 45: a worker pulls the next task from the queue", 16),
        ["round 45: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 45: a worker pulls the next task from the queue", 24),
        ["round 45: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 45: a worker pulls the next task from the queue", 32),
        ["round 45: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 45: signals travel through the network layer", 4),
        ["round", "45:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 45: signals travel through the network layer", 8),
        ["round", "45:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 45: signals travel through the network layer", 12),
        ["round 45:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 45: signals travel through the network layer", 16),
        ["round 45:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 45: signals travel through the network layer", 24),
        ["round 45: signals travel", "through the network", "layer"],
    ),
    (
        ("round 45: signals travel through the network layer", 32),
        ["round 45: signals travel through", "the network layer"],
    ),
    (
        ("round 45: the gateway routes each request by policy", 4),
        ["round", "45:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 45: the gateway routes each request by policy", 8),
        ["round", "45: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 45: the gateway routes each request by policy", 12),
        ["round 45:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 45: the gateway routes each request by policy", 16),
        ["round 45: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 45: the gateway routes each request by policy", 24),
        ["round 45: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 45: the gateway routes each request by policy", 32),
        ["round 45: the gateway routes", "each request by policy"],
    ),
    (
        ("round 45: memory grows until the buffer is full", 4),
        ["round", "45:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 45: memory grows until the buffer is full", 8),
        ["round", "45:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 45: memory grows until the buffer is full", 12),
        ["round 45:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 45: memory grows until the buffer is full", 16),
        ["round 45: memory", "grows until the", "buffer is full"],
    ),
    (("round 45: memory grows until the buffer is full", 24), ["round 45: memory grows", "until the buffer is full"]),
    (("round 45: memory grows until the buffer is full", 32), ["round 45: memory grows until the", "buffer is full"]),
    (
        ("round 45: the cluster mirrors every packet twice", 4),
        ["round", "45:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 45: the cluster mirrors every packet twice", 8),
        ["round", "45: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 45: the cluster mirrors every packet twice", 12),
        ["round 45:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 45: the cluster mirrors every packet twice", 16),
        ["round 45: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 45: the cluster mirrors every packet twice", 24),
        ["round 45: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 45: the cluster mirrors every packet twice", 32), ["round 45: the cluster mirrors", "every packet twice"]),
    (
        ("round 45: ranking uses tokens learned from the corpus", 4),
        ["round", "45:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 45: ranking uses tokens learned from the corpus", 8),
        ["round", "45:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 45: ranking uses tokens learned from the corpus", 12),
        ["round 45:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 45: ranking uses tokens learned from the corpus", 16),
        ["round 45:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 45: ranking uses tokens learned from the corpus", 24),
        ["round 45: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 45: ranking uses tokens learned from the corpus", 32),
        ["round 45: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 45: a long session ends when the candle dies", 4),
        ["round", "45:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 45: a long session ends when the candle dies", 8),
        ["round", "45: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 45: a long session ends when the candle dies", 12),
        ["round 45: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 45: a long session ends when the candle dies", 16),
        ["round 45: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 45: a long session ends when the candle dies", 24),
        ["round 45: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 45: a long session ends when the candle dies", 32),
        ["round 45: a long session ends", "when the candle dies"],
    ),
    (
        ("round 45: encode the prompt then map the result", 4),
        ["round", "45:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 45: encode the prompt then map the result", 8),
        ["round", "45:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 45: encode the prompt then map the result", 12),
        ["round 45:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 45: encode the prompt then map the result", 16),
        ["round 45: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 45: encode the prompt then map the result", 24),
        ["round 45: encode the", "prompt then map the", "result"],
    ),
    (("round 45: encode the prompt then map the result", 32), ["round 45: encode the prompt then", "map the result"]),
    (
        ("round 45: the kernel wakes the worker at dawn", 4),
        ["round", "45:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 45: the kernel wakes the worker at dawn", 8),
        ["round", "45: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 45: the kernel wakes the worker at dawn", 12),
        ["round 45:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 45: the kernel wakes the worker at dawn", 16), ["round 45: the", "kernel wakes the", "worker at dawn"]),
    (("round 45: the kernel wakes the worker at dawn", 24), ["round 45: the kernel", "wakes the worker at dawn"]),
    (("round 45: the kernel wakes the worker at dawn", 32), ["round 45: the kernel wakes the", "worker at dawn"]),
    (
        ("round 45: service latency drops after the patch", 4),
        ["round", "45:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 45: service latency drops after the patch", 8),
        ["round", "45:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 45: service latency drops after the patch", 12),
        ["round 45:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 45: service latency drops after the patch", 16),
        ["round 45:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 45: service latency drops after the patch", 24),
        ["round 45: service", "latency drops after the", "patch"],
    ),
    (("round 45: service latency drops after the patch", 32), ["round 45: service latency drops", "after the patch"]),
    (
        ("round 45: the library caches every vector it sees", 4),
        ["round", "45:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 45: the library caches every vector it sees", 8),
        ["round", "45: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 45: the library caches every vector it sees", 12),
        ["round 45:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 45: the library caches every vector it sees", 16),
        ["round 45: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 45: the library caches every vector it sees", 24),
        ["round 45: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 45: the library caches every vector it sees", 32),
        ["round 45: the library caches", "every vector it sees"],
    ),
    (
        ("round 45: agents argue then the debate resolves", 4),
        ["round", "45:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 45: agents argue then the debate resolves", 8),
        ["round", "45:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 45: agents argue then the debate resolves", 12),
        ["round 45:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 45: agents argue then the debate resolves", 16),
        ["round 45: agents", "argue then the", "debate resolves"],
    ),
    (("round 45: agents argue then the debate resolves", 24), ["round 45: agents argue", "then the debate resolves"]),
    (("round 45: agents argue then the debate resolves", 32), ["round 45: agents argue then the", "debate resolves"]),
    (
        ("round 45: the filter keeps only strong matches", 4),
        ["round", "45:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 45: the filter keeps only strong matches", 8),
        ["round", "45: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 45: the filter keeps only strong matches", 12),
        ["round 45:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 45: the filter keeps only strong matches", 16),
        ["round 45: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 45: the filter keeps only strong matches", 24), ["round 45: the filter", "keeps only strong", "matches"]),
    (("round 45: the filter keeps only strong matches", 32), ["round 45: the filter keeps only", "strong matches"]),
    (
        ("round 45: the model answers with a short reply", 4),
        ["round", "45:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 45: the model answers with a short reply", 8),
        ["round", "45: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 45: the model answers with a short reply", 12),
        ["round 45:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 45: the model answers with a short reply", 16),
        ["round 45: the", "model answers", "with a short", "reply"],
    ),
    (("round 45: the model answers with a short reply", 24), ["round 45: the model", "answers with a short", "reply"]),
    (("round 45: the model answers with a short reply", 32), ["round 45: the model answers with", "a short reply"]),
    (
        ("round 45: the recorder stores the reasoning trace", 4),
        ["round", "45:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 45: the recorder stores the reasoning trace", 8),
        ["round", "45: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 45: the recorder stores the reasoning trace", 12),
        ["round 45:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 45: the recorder stores the reasoning trace", 16),
        ["round 45: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 45: the recorder stores the reasoning trace", 24),
        ["round 45: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 45: the recorder stores the reasoning trace", 32),
        ["round 45: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 45: the angel watches the processor run", 4),
        ["round", "45:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 45: the angel watches the processor run", 8),
        ["round", "45: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 45: the angel watches the processor run", 12),
        ["round 45:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 45: the angel watches the processor run", 16), ["round 45: the", "angel watches", "the processor", "run"]),
    (("round 45: the angel watches the processor run", 24), ["round 45: the angel", "watches the processor", "run"]),
    (("round 45: the angel watches the processor run", 32), ["round 45: the angel watches the", "processor run"]),
    (
        ("round 45: angle of the vector decides the match", 4),
        ["round", "45:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 45: angle of the vector decides the match", 8),
        ["round", "45:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 45: angle of the vector decides the match", 12),
        ["round 45:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 45: angle of the vector decides the match", 16),
        ["round 45: angle", "of the vector", "decides the", "match"],
    ),
    (("round 45: angle of the vector decides the match", 24), ["round 45: angle of the", "vector decides the match"]),
    (("round 45: angle of the vector decides the match", 32), ["round 45: angle of the vector", "decides the match"]),
    (
        ("round 45: the candle burns twice as long at night", 4),
        ["round", "45:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 45: the candle burns twice as long at night", 8),
        ["round", "45: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 45: the candle burns twice as long at night", 12),
        ["round 45:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 45: the candle burns twice as long at night", 16),
        ["round 45: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 45: the candle burns twice as long at night", 24),
        ["round 45: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 45: the candle burns twice as long at night", 32),
        ["round 45: the candle burns twice", "as long at night"],
    ),
    (
        ("round 45: a mirror of the universe in one line", 4),
        ["round", "45:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 45: a mirror of the universe in one line", 8),
        ["round", "45: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 45: a mirror of the universe in one line", 12),
        ["round 45: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 45: a mirror of the universe in one line", 16),
        ["round 45: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 45: a mirror of the universe in one line", 24), ["round 45: a mirror of", "the universe in one line"]),
    (("round 45: a mirror of the universe in one line", 32), ["round 45: a mirror of the", "universe in one line"]),
    (
        ("round 45: the queue drains before the storm", 4),
        ["round", "45:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 45: the queue drains before the storm", 8),
        ["round", "45: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 45: the queue drains before the storm", 12), ["round 45:", "the queue", "drains", "before the", "storm"]),
    (("round 45: the queue drains before the storm", 16), ["round 45: the", "queue drains", "before the storm"]),
    (("round 45: the queue drains before the storm", 24), ["round 45: the queue", "drains before the storm"]),
    (("round 45: the queue drains before the storm", 32), ["round 45: the queue drains", "before the storm"]),
    (
        ("kitten45 sitting45 agent45 angle45 universe45 memory45", 6),
        ["kitten45", "sitting45", "agent45", "angle45", "universe45", "memory45"],
    ),
    (
        ("kitten45 sitting45 agent45 angle45 universe45 memory45", 10),
        ["kitten45", "sitting45", "agent45", "angle45", "universe45", "memory45"],
    ),
    (
        ("kitten45 sitting45 agent45 angle45 universe45 memory45", 18),
        ["kitten45 sitting45", "agent45 angle45", "universe45", "memory45"],
    ),
    (
        ("kitten45 sitting45 agent45 angle45 universe45 memory45", 28),
        ["kitten45 sitting45 agent45", "angle45 universe45 memory45"],
    ),
    (
        ("sitting45 agent45 angle45 universe45 memory45 stream45", 6),
        ["sitting45", "agent45", "angle45", "universe45", "memory45", "stream45"],
    ),
    (
        ("sitting45 agent45 angle45 universe45 memory45 stream45", 10),
        ["sitting45", "agent45", "angle45", "universe45", "memory45", "stream45"],
    ),
    (
        ("sitting45 agent45 angle45 universe45 memory45 stream45", 18),
        ["sitting45 agent45", "angle45 universe45", "memory45 stream45"],
    ),
    (
        ("sitting45 agent45 angle45 universe45 memory45 stream45", 28),
        ["sitting45 agent45 angle45", "universe45 memory45 stream45"],
    ),
    (
        ("agent45 angle45 universe45 memory45 stream45 context45", 6),
        ["agent45", "angle45", "universe45", "memory45", "stream45", "context45"],
    ),
    (
        ("agent45 angle45 universe45 memory45 stream45 context45", 10),
        ["agent45", "angle45", "universe45", "memory45", "stream45", "context45"],
    ),
    (
        ("agent45 angle45 universe45 memory45 stream45 context45", 18),
        ["agent45 angle45", "universe45", "memory45 stream45", "context45"],
    ),
    (
        ("agent45 angle45 universe45 memory45 stream45 context45", 28),
        ["agent45 angle45 universe45", "memory45 stream45 context45"],
    ),
    (
        ("angle45 universe45 memory45 stream45 context45 knowledge45", 6),
        ["angle45", "universe45", "memory45", "stream45", "context45", "knowledge45"],
    ),
    (
        ("angle45 universe45 memory45 stream45 context45 knowledge45", 10),
        ["angle45", "universe45", "memory45", "stream45", "context45", "knowledge45"],
    ),
    (
        ("angle45 universe45 memory45 stream45 context45 knowledge45", 18),
        ["angle45 universe45", "memory45 stream45", "context45", "knowledge45"],
    ),
    (
        ("angle45 universe45 memory45 stream45 context45 knowledge45", 28),
        ["angle45 universe45 memory45", "stream45 context45", "knowledge45"],
    ),
    (
        ("universe45 memory45 stream45 context45 knowledge45 vector45", 6),
        ["universe45", "memory45", "stream45", "context45", "knowledge45", "vector45"],
    ),
    (
        ("universe45 memory45 stream45 context45 knowledge45 vector45", 10),
        ["universe45", "memory45", "stream45", "context45", "knowledge45", "vector45"],
    ),
    (
        ("universe45 memory45 stream45 context45 knowledge45 vector45", 18),
        ["universe45", "memory45 stream45", "context45", "knowledge45", "vector45"],
    ),
    (
        ("universe45 memory45 stream45 context45 knowledge45 vector45", 28),
        ["universe45 memory45 stream45", "context45 knowledge45", "vector45"],
    ),
    (
        ("memory45 stream45 context45 knowledge45 vector45 processor45", 6),
        ["memory45", "stream45", "context45", "knowledge45", "vector45", "processor45"],
    ),
    (
        ("memory45 stream45 context45 knowledge45 vector45 processor45", 10),
        ["memory45", "stream45", "context45", "knowledge45", "vector45", "processor45"],
    ),
    (
        ("memory45 stream45 context45 knowledge45 vector45 processor45", 18),
        ["memory45 stream45", "context45", "knowledge45", "vector45", "processor45"],
    ),
    (
        ("memory45 stream45 context45 knowledge45 vector45 processor45", 28),
        ["memory45 stream45 context45", "knowledge45 vector45", "processor45"],
    ),
    (
        ("stream45 context45 knowledge45 vector45 processor45 reasoning45", 6),
        ["stream45", "context45", "knowledge45", "vector45", "processor45", "reasoning45"],
    ),
    (
        ("stream45 context45 knowledge45 vector45 processor45 reasoning45", 10),
        ["stream45", "context45", "knowledge45", "vector45", "processor45", "reasoning45"],
    ),
    (
        ("stream45 context45 knowledge45 vector45 processor45 reasoning45", 18),
        ["stream45 context45", "knowledge45", "vector45", "processor45", "reasoning45"],
    ),
    (
        ("stream45 context45 knowledge45 vector45 processor45 reasoning45", 28),
        ["stream45 context45", "knowledge45 vector45", "processor45 reasoning45"],
    ),
    (
        ("context45 knowledge45 vector45 processor45 reasoning45 machine45", 6),
        ["context45", "knowledge45", "vector45", "processor45", "reasoning45", "machine45"],
    ),
    (
        ("context45 knowledge45 vector45 processor45 reasoning45 machine45", 10),
        ["context45", "knowledge45", "vector45", "processor45", "reasoning45", "machine45"],
    ),
    (
        ("context45 knowledge45 vector45 processor45 reasoning45 machine45", 18),
        ["context45", "knowledge45", "vector45", "processor45", "reasoning45", "machine45"],
    ),
    (
        ("context45 knowledge45 vector45 processor45 reasoning45 machine45", 28),
        ["context45 knowledge45", "vector45 processor45", "reasoning45 machine45"],
    ),
    (
        ("knowledge45 vector45 processor45 reasoning45 machine45 learning45", 6),
        ["knowledge45", "vector45", "processor45", "reasoning45", "machine45", "learning45"],
    ),
    (
        ("knowledge45 vector45 processor45 reasoning45 machine45 learning45", 10),
        ["knowledge45", "vector45", "processor45", "reasoning45", "machine45", "learning45"],
    ),
    (
        ("knowledge45 vector45 processor45 reasoning45 machine45 learning45", 18),
        ["knowledge45", "vector45", "processor45", "reasoning45", "machine45", "learning45"],
    ),
    (
        ("knowledge45 vector45 processor45 reasoning45 machine45 learning45", 28),
        ["knowledge45 vector45", "processor45 reasoning45", "machine45 learning45"],
    ),
    (
        ("vector45 processor45 reasoning45 machine45 learning45 model45", 6),
        ["vector45", "processor45", "reasoning45", "machine45", "learning45", "model45"],
    ),
    (
        ("vector45 processor45 reasoning45 machine45 learning45 model45", 10),
        ["vector45", "processor45", "reasoning45", "machine45", "learning45", "model45"],
    ),
    (
        ("vector45 processor45 reasoning45 machine45 learning45 model45", 18),
        ["vector45", "processor45", "reasoning45", "machine45", "learning45 model45"],
    ),
    (
        ("vector45 processor45 reasoning45 machine45 learning45 model45", 28),
        ["vector45 processor45", "reasoning45 machine45", "learning45 model45"],
    ),
    (
        ("processor45 reasoning45 machine45 learning45 model45 token45", 6),
        ["processor45", "reasoning45", "machine45", "learning45", "model45", "token45"],
    ),
    (
        ("processor45 reasoning45 machine45 learning45 model45 token45", 10),
        ["processor45", "reasoning45", "machine45", "learning45", "model45", "token45"],
    ),
    (
        ("processor45 reasoning45 machine45 learning45 model45 token45", 18),
        ["processor45", "reasoning45", "machine45", "learning45 model45", "token45"],
    ),
    (
        ("processor45 reasoning45 machine45 learning45 model45 token45", 28),
        ["processor45 reasoning45", "machine45 learning45 model45", "token45"],
    ),
    (
        ("reasoning45 machine45 learning45 model45 token45 prompt45", 6),
        ["reasoning45", "machine45", "learning45", "model45", "token45", "prompt45"],
    ),
    (
        ("reasoning45 machine45 learning45 model45 token45 prompt45", 10),
        ["reasoning45", "machine45", "learning45", "model45", "token45", "prompt45"],
    ),
    (
        ("reasoning45 machine45 learning45 model45 token45 prompt45", 18),
        ["reasoning45", "machine45", "learning45 model45", "token45 prompt45"],
    ),
    (
        ("reasoning45 machine45 learning45 model45 token45 prompt45", 28),
        ["reasoning45 machine45", "learning45 model45 token45", "prompt45"],
    ),
    (
        ("machine45 learning45 model45 token45 prompt45 session45", 6),
        ["machine45", "learning45", "model45", "token45", "prompt45", "session45"],
    ),
    (
        ("machine45 learning45 model45 token45 prompt45 session45", 10),
        ["machine45", "learning45", "model45", "token45", "prompt45", "session45"],
    ),
    (
        ("machine45 learning45 model45 token45 prompt45 session45", 18),
        ["machine45", "learning45 model45", "token45 prompt45", "session45"],
    ),
    (
        ("machine45 learning45 model45 token45 prompt45 session45", 28),
        ["machine45 learning45 model45", "token45 prompt45 session45"],
    ),
    (
        ("learning45 model45 token45 prompt45 session45 library45", 6),
        ["learning45", "model45", "token45", "prompt45", "session45", "library45"],
    ),
    (
        ("learning45 model45 token45 prompt45 session45 library45", 10),
        ["learning45", "model45", "token45", "prompt45", "session45", "library45"],
    ),
    (
        ("learning45 model45 token45 prompt45 session45 library45", 18),
        ["learning45 model45", "token45 prompt45", "session45", "library45"],
    ),
    (
        ("learning45 model45 token45 prompt45 session45 library45", 28),
        ["learning45 model45 token45", "prompt45 session45 library45"],
    ),
    (
        ("model45 token45 prompt45 session45 library45 service45", 6),
        ["model45", "token45", "prompt45", "session45", "library45", "service45"],
    ),
    (
        ("model45 token45 prompt45 session45 library45 service45", 10),
        ["model45", "token45", "prompt45", "session45", "library45", "service45"],
    ),
    (
        ("model45 token45 prompt45 session45 library45 service45", 18),
        ["model45 token45", "prompt45 session45", "library45", "service45"],
    ),
    (
        ("model45 token45 prompt45 session45 library45 service45", 28),
        ["model45 token45 prompt45", "session45 library45", "service45"],
    ),
    (
        ("token45 prompt45 session45 library45 service45 gateway45", 6),
        ["token45", "prompt45", "session45", "library45", "service45", "gateway45"],
    ),
    (
        ("token45 prompt45 session45 library45 service45 gateway45", 10),
        ["token45", "prompt45", "session45", "library45", "service45", "gateway45"],
    ),
    (
        ("token45 prompt45 session45 library45 service45 gateway45", 18),
        ["token45 prompt45", "session45", "library45", "service45", "gateway45"],
    ),
    (
        ("token45 prompt45 session45 library45 service45 gateway45", 28),
        ["token45 prompt45 session45", "library45 service45", "gateway45"],
    ),
    (
        ("prompt45 session45 library45 service45 gateway45 storage45", 6),
        ["prompt45", "session45", "library45", "service45", "gateway45", "storage45"],
    ),
    (
        ("prompt45 session45 library45 service45 gateway45 storage45", 10),
        ["prompt45", "session45", "library45", "service45", "gateway45", "storage45"],
    ),
    (
        ("prompt45 session45 library45 service45 gateway45 storage45", 18),
        ["prompt45 session45", "library45", "service45", "gateway45", "storage45"],
    ),
    (
        ("prompt45 session45 library45 service45 gateway45 storage45", 28),
        ["prompt45 session45 library45", "service45 gateway45", "storage45"],
    ),
    (
        ("session45 library45 service45 gateway45 storage45 network45", 6),
        ["session45", "library45", "service45", "gateway45", "storage45", "network45"],
    ),
    (
        ("session45 library45 service45 gateway45 storage45 network45", 10),
        ["session45", "library45", "service45", "gateway45", "storage45", "network45"],
    ),
    (
        ("session45 library45 service45 gateway45 storage45 network45", 18),
        ["session45", "library45", "service45", "gateway45", "storage45", "network45"],
    ),
    (
        ("session45 library45 service45 gateway45 storage45 network45", 28),
        ["session45 library45", "service45 gateway45", "storage45 network45"],
    ),
    (
        ("library45 service45 gateway45 storage45 network45 latency45", 6),
        ["library45", "service45", "gateway45", "storage45", "network45", "latency45"],
    ),
    (
        ("library45 service45 gateway45 storage45 network45 latency45", 10),
        ["library45", "service45", "gateway45", "storage45", "network45", "latency45"],
    ),
    (
        ("library45 service45 gateway45 storage45 network45 latency45", 18),
        ["library45", "service45", "gateway45", "storage45", "network45", "latency45"],
    ),
    (
        ("library45 service45 gateway45 storage45 network45 latency45", 28),
        ["library45 service45", "gateway45 storage45", "network45 latency45"],
    ),
    (
        ("service45 gateway45 storage45 network45 latency45 buffer45", 6),
        ["service45", "gateway45", "storage45", "network45", "latency45", "buffer45"],
    ),
    (
        ("service45 gateway45 storage45 network45 latency45 buffer45", 10),
        ["service45", "gateway45", "storage45", "network45", "latency45", "buffer45"],
    ),
    (
        ("service45 gateway45 storage45 network45 latency45 buffer45", 18),
        ["service45", "gateway45", "storage45", "network45", "latency45 buffer45"],
    ),
    (
        ("service45 gateway45 storage45 network45 latency45 buffer45", 28),
        ["service45 gateway45", "storage45 network45", "latency45 buffer45"],
    ),
    (
        ("gateway45 storage45 network45 latency45 buffer45 queue45", 6),
        ["gateway45", "storage45", "network45", "latency45", "buffer45", "queue45"],
    ),
    (
        ("gateway45 storage45 network45 latency45 buffer45 queue45", 10),
        ["gateway45", "storage45", "network45", "latency45", "buffer45", "queue45"],
    ),
    (
        ("gateway45 storage45 network45 latency45 buffer45 queue45", 18),
        ["gateway45", "storage45", "network45", "latency45 buffer45", "queue45"],
    ),
    (
        ("gateway45 storage45 network45 latency45 buffer45 queue45", 28),
        ["gateway45 storage45", "network45 latency45 buffer45", "queue45"],
    ),
    (
        ("storage45 network45 latency45 buffer45 queue45 worker45", 6),
        ["storage45", "network45", "latency45", "buffer45", "queue45", "worker45"],
    ),
    (
        ("storage45 network45 latency45 buffer45 queue45 worker45", 10),
        ["storage45", "network45", "latency45", "buffer45", "queue45", "worker45"],
    ),
    (
        ("storage45 network45 latency45 buffer45 queue45 worker45", 18),
        ["storage45", "network45", "latency45 buffer45", "queue45 worker45"],
    ),
    (
        ("storage45 network45 latency45 buffer45 queue45 worker45", 28),
        ["storage45 network45", "latency45 buffer45 queue45", "worker45"],
    ),
    (
        ("network45 latency45 buffer45 queue45 worker45 kernel45", 6),
        ["network45", "latency45", "buffer45", "queue45", "worker45", "kernel45"],
    ),
    (
        ("network45 latency45 buffer45 queue45 worker45 kernel45", 10),
        ["network45", "latency45", "buffer45", "queue45", "worker45", "kernel45"],
    ),
    (
        ("network45 latency45 buffer45 queue45 worker45 kernel45", 18),
        ["network45", "latency45 buffer45", "queue45 worker45", "kernel45"],
    ),
    (
        ("network45 latency45 buffer45 queue45 worker45 kernel45", 28),
        ["network45 latency45 buffer45", "queue45 worker45 kernel45"],
    ),
    (
        ("latency45 buffer45 queue45 worker45 kernel45 signal45", 6),
        ["latency45", "buffer45", "queue45", "worker45", "kernel45", "signal45"],
    ),
    (
        ("latency45 buffer45 queue45 worker45 kernel45 signal45", 10),
        ["latency45", "buffer45", "queue45", "worker45", "kernel45", "signal45"],
    ),
    (
        ("latency45 buffer45 queue45 worker45 kernel45 signal45", 18),
        ["latency45 buffer45", "queue45 worker45", "kernel45 signal45"],
    ),
    (
        ("latency45 buffer45 queue45 worker45 kernel45 signal45", 28),
        ["latency45 buffer45 queue45", "worker45 kernel45 signal45"],
    ),
    (
        ("buffer45 queue45 worker45 kernel45 signal45 packet45", 6),
        ["buffer45", "queue45", "worker45", "kernel45", "signal45", "packet45"],
    ),
    (
        ("buffer45 queue45 worker45 kernel45 signal45 packet45", 10),
        ["buffer45", "queue45", "worker45", "kernel45", "signal45", "packet45"],
    ),
    (
        ("buffer45 queue45 worker45 kernel45 signal45 packet45", 18),
        ["buffer45 queue45", "worker45 kernel45", "signal45 packet45"],
    ),
    (
        ("buffer45 queue45 worker45 kernel45 signal45 packet45", 28),
        ["buffer45 queue45 worker45", "kernel45 signal45 packet45"],
    ),
    (
        ("queue45 worker45 kernel45 signal45 packet45 router45", 6),
        ["queue45", "worker45", "kernel45", "signal45", "packet45", "router45"],
    ),
    (
        ("queue45 worker45 kernel45 signal45 packet45 router45", 10),
        ["queue45", "worker45", "kernel45", "signal45", "packet45", "router45"],
    ),
    (
        ("queue45 worker45 kernel45 signal45 packet45 router45", 18),
        ["queue45 worker45", "kernel45 signal45", "packet45 router45"],
    ),
    (
        ("queue45 worker45 kernel45 signal45 packet45 router45", 28),
        ["queue45 worker45 kernel45", "signal45 packet45 router45"],
    ),
    (
        ("worker45 kernel45 signal45 packet45 router45 cluster45", 6),
        ["worker45", "kernel45", "signal45", "packet45", "router45", "cluster45"],
    ),
    (
        ("worker45 kernel45 signal45 packet45 router45 cluster45", 10),
        ["worker45", "kernel45", "signal45", "packet45", "router45", "cluster45"],
    ),
    (
        ("worker45 kernel45 signal45 packet45 router45 cluster45", 18),
        ["worker45 kernel45", "signal45 packet45", "router45 cluster45"],
    ),
    (
        ("worker45 kernel45 signal45 packet45 router45 cluster45", 28),
        ["worker45 kernel45 signal45", "packet45 router45 cluster45"],
    ),
    (
        ("kernel45 signal45 packet45 router45 cluster45 mirror45", 6),
        ["kernel45", "signal45", "packet45", "router45", "cluster45", "mirror45"],
    ),
    (
        ("kernel45 signal45 packet45 router45 cluster45 mirror45", 10),
        ["kernel45", "signal45", "packet45", "router45", "cluster45", "mirror45"],
    ),
    (
        ("kernel45 signal45 packet45 router45 cluster45 mirror45", 18),
        ["kernel45 signal45", "packet45 router45", "cluster45 mirror45"],
    ),
    (
        ("kernel45 signal45 packet45 router45 cluster45 mirror45", 28),
        ["kernel45 signal45 packet45", "router45 cluster45 mirror45"],
    ),
    (
        ("signal45 packet45 router45 cluster45 mirror45 filter45", 6),
        ["signal45", "packet45", "router45", "cluster45", "mirror45", "filter45"],
    ),
    (
        ("signal45 packet45 router45 cluster45 mirror45 filter45", 10),
        ["signal45", "packet45", "router45", "cluster45", "mirror45", "filter45"],
    ),
    (
        ("signal45 packet45 router45 cluster45 mirror45 filter45", 18),
        ["signal45 packet45", "router45 cluster45", "mirror45 filter45"],
    ),
    (
        ("signal45 packet45 router45 cluster45 mirror45 filter45", 28),
        ["signal45 packet45 router45", "cluster45 mirror45 filter45"],
    ),
    (
        ("packet45 router45 cluster45 mirror45 filter45 ranking45", 6),
        ["packet45", "router45", "cluster45", "mirror45", "filter45", "ranking45"],
    ),
    (
        ("packet45 router45 cluster45 mirror45 filter45 ranking45", 10),
        ["packet45", "router45", "cluster45", "mirror45", "filter45", "ranking45"],
    ),
    (
        ("packet45 router45 cluster45 mirror45 filter45 ranking45", 18),
        ["packet45 router45", "cluster45 mirror45", "filter45 ranking45"],
    ),
    (
        ("packet45 router45 cluster45 mirror45 filter45 ranking45", 28),
        ["packet45 router45 cluster45", "mirror45 filter45 ranking45"],
    ),
    (
        ("router45 cluster45 mirror45 filter45 ranking45 encoding45", 6),
        ["router45", "cluster45", "mirror45", "filter45", "ranking45", "encoding45"],
    ),
    (
        ("router45 cluster45 mirror45 filter45 ranking45 encoding45", 10),
        ["router45", "cluster45", "mirror45", "filter45", "ranking45", "encoding45"],
    ),
    (
        ("router45 cluster45 mirror45 filter45 ranking45 encoding45", 18),
        ["router45 cluster45", "mirror45 filter45", "ranking45", "encoding45"],
    ),
    (
        ("router45 cluster45 mirror45 filter45 ranking45 encoding45", 28),
        ["router45 cluster45 mirror45", "filter45 ranking45", "encoding45"],
    ),
    (
        ("cluster45 mirror45 filter45 ranking45 encoding45 mapping45", 6),
        ["cluster45", "mirror45", "filter45", "ranking45", "encoding45", "mapping45"],
    ),
    (
        ("cluster45 mirror45 filter45 ranking45 encoding45 mapping45", 10),
        ["cluster45", "mirror45", "filter45", "ranking45", "encoding45", "mapping45"],
    ),
    (
        ("cluster45 mirror45 filter45 ranking45 encoding45 mapping45", 18),
        ["cluster45 mirror45", "filter45 ranking45", "encoding45", "mapping45"],
    ),
    (
        ("cluster45 mirror45 filter45 ranking45 encoding45 mapping45", 28),
        ["cluster45 mirror45 filter45", "ranking45 encoding45", "mapping45"],
    ),
    (
        ("mirror45 filter45 ranking45 encoding45 mapping45 record45", 6),
        ["mirror45", "filter45", "ranking45", "encoding45", "mapping45", "record45"],
    ),
    (
        ("mirror45 filter45 ranking45 encoding45 mapping45 record45", 10),
        ["mirror45", "filter45", "ranking45", "encoding45", "mapping45", "record45"],
    ),
    (
        ("mirror45 filter45 ranking45 encoding45 mapping45 record45", 18),
        ["mirror45 filter45", "ranking45", "encoding45", "mapping45 record45"],
    ),
    (
        ("mirror45 filter45 ranking45 encoding45 mapping45 record45", 28),
        ["mirror45 filter45 ranking45", "encoding45 mapping45", "record45"],
    ),
    (
        ("filter45 ranking45 encoding45 mapping45 record45 candle45", 6),
        ["filter45", "ranking45", "encoding45", "mapping45", "record45", "candle45"],
    ),
    (
        ("filter45 ranking45 encoding45 mapping45 record45 candle45", 10),
        ["filter45", "ranking45", "encoding45", "mapping45", "record45", "candle45"],
    ),
    (
        ("filter45 ranking45 encoding45 mapping45 record45 candle45", 18),
        ["filter45 ranking45", "encoding45", "mapping45 record45", "candle45"],
    ),
    (
        ("filter45 ranking45 encoding45 mapping45 record45 candle45", 28),
        ["filter45 ranking45", "encoding45 mapping45", "record45 candle45"],
    ),
    (
        ("ranking45 encoding45 mapping45 record45 candle45 thread45", 6),
        ["ranking45", "encoding45", "mapping45", "record45", "candle45", "thread45"],
    ),
    (
        ("ranking45 encoding45 mapping45 record45 candle45 thread45", 10),
        ["ranking45", "encoding45", "mapping45", "record45", "candle45", "thread45"],
    ),
    (
        ("ranking45 encoding45 mapping45 record45 candle45 thread45", 18),
        ["ranking45", "encoding45", "mapping45 record45", "candle45 thread45"],
    ),
    (
        ("ranking45 encoding45 mapping45 record45 candle45 thread45", 28),
        ["ranking45 encoding45", "mapping45 record45 candle45", "thread45"],
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
