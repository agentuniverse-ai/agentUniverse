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
        ("round 55: the quick brown fox jumps over the lazy dog", 4),
        ["round", "55:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 55: the quick brown fox jumps over the lazy dog", 8),
        ["round", "55: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 55: the quick brown fox jumps over the lazy dog", 12),
        ["round 55:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 55: the quick brown fox jumps over the lazy dog", 16),
        ["round 55: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 55: the quick brown fox jumps over the lazy dog", 24),
        ["round 55: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 55: the quick brown fox jumps over the lazy dog", 32),
        ["round 55: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 55: agentuniverse is a framework for multi agents", 4),
        ["round", "55:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 55: agentuniverse is a framework for multi agents", 8),
        ["round", "55:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 55: agentuniverse is a framework for multi agents", 12),
        ["round 55:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 55: agentuniverse is a framework for multi agents", 16),
        ["round 55:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 55: agentuniverse is a framework for multi agents", 24),
        ["round 55: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 55: agentuniverse is a framework for multi agents", 32),
        ["round 55: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 55: knowledge stored as vectors enables retrieval", 4),
        ["round", "55:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 55: knowledge stored as vectors enables retrieval", 8),
        ["round", "55:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 55: knowledge stored as vectors enables retrieval", 12),
        ["round 55:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 55: knowledge stored as vectors enables retrieval", 16),
        ["round 55:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 55: knowledge stored as vectors enables retrieval", 24),
        ["round 55: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 55: knowledge stored as vectors enables retrieval", 32),
        ["round 55: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 55: the processor reads the record then stops", 4),
        ["round", "55:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 55: the processor reads the record then stops", 8),
        ["round", "55: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 55: the processor reads the record then stops", 12),
        ["round 55:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 55: the processor reads the record then stops", 16),
        ["round 55: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 55: the processor reads the record then stops", 24),
        ["round 55: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 55: the processor reads the record then stops", 32),
        ["round 55: the processor reads", "the record then stops"],
    ),
    (
        ("round 55: a worker pulls the next task from the queue", 4),
        ["round", "55:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 55: a worker pulls the next task from the queue", 8),
        ["round", "55: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 55: a worker pulls the next task from the queue", 12),
        ["round 55: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 55: a worker pulls the next task from the queue", 16),
        ["round 55: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 55: a worker pulls the next task from the queue", 24),
        ["round 55: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 55: a worker pulls the next task from the queue", 32),
        ["round 55: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 55: signals travel through the network layer", 4),
        ["round", "55:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 55: signals travel through the network layer", 8),
        ["round", "55:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 55: signals travel through the network layer", 12),
        ["round 55:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 55: signals travel through the network layer", 16),
        ["round 55:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 55: signals travel through the network layer", 24),
        ["round 55: signals travel", "through the network", "layer"],
    ),
    (
        ("round 55: signals travel through the network layer", 32),
        ["round 55: signals travel through", "the network layer"],
    ),
    (
        ("round 55: the gateway routes each request by policy", 4),
        ["round", "55:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 55: the gateway routes each request by policy", 8),
        ["round", "55: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 55: the gateway routes each request by policy", 12),
        ["round 55:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 55: the gateway routes each request by policy", 16),
        ["round 55: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 55: the gateway routes each request by policy", 24),
        ["round 55: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 55: the gateway routes each request by policy", 32),
        ["round 55: the gateway routes", "each request by policy"],
    ),
    (
        ("round 55: memory grows until the buffer is full", 4),
        ["round", "55:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 55: memory grows until the buffer is full", 8),
        ["round", "55:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 55: memory grows until the buffer is full", 12),
        ["round 55:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 55: memory grows until the buffer is full", 16),
        ["round 55: memory", "grows until the", "buffer is full"],
    ),
    (("round 55: memory grows until the buffer is full", 24), ["round 55: memory grows", "until the buffer is full"]),
    (("round 55: memory grows until the buffer is full", 32), ["round 55: memory grows until the", "buffer is full"]),
    (
        ("round 55: the cluster mirrors every packet twice", 4),
        ["round", "55:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 55: the cluster mirrors every packet twice", 8),
        ["round", "55: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 55: the cluster mirrors every packet twice", 12),
        ["round 55:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 55: the cluster mirrors every packet twice", 16),
        ["round 55: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 55: the cluster mirrors every packet twice", 24),
        ["round 55: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 55: the cluster mirrors every packet twice", 32), ["round 55: the cluster mirrors", "every packet twice"]),
    (
        ("round 55: ranking uses tokens learned from the corpus", 4),
        ["round", "55:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 55: ranking uses tokens learned from the corpus", 8),
        ["round", "55:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 55: ranking uses tokens learned from the corpus", 12),
        ["round 55:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 55: ranking uses tokens learned from the corpus", 16),
        ["round 55:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 55: ranking uses tokens learned from the corpus", 24),
        ["round 55: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 55: ranking uses tokens learned from the corpus", 32),
        ["round 55: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 55: a long session ends when the candle dies", 4),
        ["round", "55:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 55: a long session ends when the candle dies", 8),
        ["round", "55: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 55: a long session ends when the candle dies", 12),
        ["round 55: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 55: a long session ends when the candle dies", 16),
        ["round 55: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 55: a long session ends when the candle dies", 24),
        ["round 55: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 55: a long session ends when the candle dies", 32),
        ["round 55: a long session ends", "when the candle dies"],
    ),
    (
        ("round 55: encode the prompt then map the result", 4),
        ["round", "55:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 55: encode the prompt then map the result", 8),
        ["round", "55:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 55: encode the prompt then map the result", 12),
        ["round 55:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 55: encode the prompt then map the result", 16),
        ["round 55: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 55: encode the prompt then map the result", 24),
        ["round 55: encode the", "prompt then map the", "result"],
    ),
    (("round 55: encode the prompt then map the result", 32), ["round 55: encode the prompt then", "map the result"]),
    (
        ("round 55: the kernel wakes the worker at dawn", 4),
        ["round", "55:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 55: the kernel wakes the worker at dawn", 8),
        ["round", "55: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 55: the kernel wakes the worker at dawn", 12),
        ["round 55:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 55: the kernel wakes the worker at dawn", 16), ["round 55: the", "kernel wakes the", "worker at dawn"]),
    (("round 55: the kernel wakes the worker at dawn", 24), ["round 55: the kernel", "wakes the worker at dawn"]),
    (("round 55: the kernel wakes the worker at dawn", 32), ["round 55: the kernel wakes the", "worker at dawn"]),
    (
        ("round 55: service latency drops after the patch", 4),
        ["round", "55:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 55: service latency drops after the patch", 8),
        ["round", "55:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 55: service latency drops after the patch", 12),
        ["round 55:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 55: service latency drops after the patch", 16),
        ["round 55:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 55: service latency drops after the patch", 24),
        ["round 55: service", "latency drops after the", "patch"],
    ),
    (("round 55: service latency drops after the patch", 32), ["round 55: service latency drops", "after the patch"]),
    (
        ("round 55: the library caches every vector it sees", 4),
        ["round", "55:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 55: the library caches every vector it sees", 8),
        ["round", "55: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 55: the library caches every vector it sees", 12),
        ["round 55:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 55: the library caches every vector it sees", 16),
        ["round 55: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 55: the library caches every vector it sees", 24),
        ["round 55: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 55: the library caches every vector it sees", 32),
        ["round 55: the library caches", "every vector it sees"],
    ),
    (
        ("round 55: agents argue then the debate resolves", 4),
        ["round", "55:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 55: agents argue then the debate resolves", 8),
        ["round", "55:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 55: agents argue then the debate resolves", 12),
        ["round 55:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 55: agents argue then the debate resolves", 16),
        ["round 55: agents", "argue then the", "debate resolves"],
    ),
    (("round 55: agents argue then the debate resolves", 24), ["round 55: agents argue", "then the debate resolves"]),
    (("round 55: agents argue then the debate resolves", 32), ["round 55: agents argue then the", "debate resolves"]),
    (
        ("round 55: the filter keeps only strong matches", 4),
        ["round", "55:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 55: the filter keeps only strong matches", 8),
        ["round", "55: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 55: the filter keeps only strong matches", 12),
        ["round 55:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 55: the filter keeps only strong matches", 16),
        ["round 55: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 55: the filter keeps only strong matches", 24), ["round 55: the filter", "keeps only strong", "matches"]),
    (("round 55: the filter keeps only strong matches", 32), ["round 55: the filter keeps only", "strong matches"]),
    (
        ("round 55: the model answers with a short reply", 4),
        ["round", "55:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 55: the model answers with a short reply", 8),
        ["round", "55: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 55: the model answers with a short reply", 12),
        ["round 55:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 55: the model answers with a short reply", 16),
        ["round 55: the", "model answers", "with a short", "reply"],
    ),
    (("round 55: the model answers with a short reply", 24), ["round 55: the model", "answers with a short", "reply"]),
    (("round 55: the model answers with a short reply", 32), ["round 55: the model answers with", "a short reply"]),
    (
        ("round 55: the recorder stores the reasoning trace", 4),
        ["round", "55:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 55: the recorder stores the reasoning trace", 8),
        ["round", "55: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 55: the recorder stores the reasoning trace", 12),
        ["round 55:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 55: the recorder stores the reasoning trace", 16),
        ["round 55: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 55: the recorder stores the reasoning trace", 24),
        ["round 55: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 55: the recorder stores the reasoning trace", 32),
        ["round 55: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 55: the angel watches the processor run", 4),
        ["round", "55:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 55: the angel watches the processor run", 8),
        ["round", "55: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 55: the angel watches the processor run", 12),
        ["round 55:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 55: the angel watches the processor run", 16), ["round 55: the", "angel watches", "the processor", "run"]),
    (("round 55: the angel watches the processor run", 24), ["round 55: the angel", "watches the processor", "run"]),
    (("round 55: the angel watches the processor run", 32), ["round 55: the angel watches the", "processor run"]),
    (
        ("round 55: angle of the vector decides the match", 4),
        ["round", "55:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 55: angle of the vector decides the match", 8),
        ["round", "55:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 55: angle of the vector decides the match", 12),
        ["round 55:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 55: angle of the vector decides the match", 16),
        ["round 55: angle", "of the vector", "decides the", "match"],
    ),
    (("round 55: angle of the vector decides the match", 24), ["round 55: angle of the", "vector decides the match"]),
    (("round 55: angle of the vector decides the match", 32), ["round 55: angle of the vector", "decides the match"]),
    (
        ("round 55: the candle burns twice as long at night", 4),
        ["round", "55:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 55: the candle burns twice as long at night", 8),
        ["round", "55: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 55: the candle burns twice as long at night", 12),
        ["round 55:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 55: the candle burns twice as long at night", 16),
        ["round 55: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 55: the candle burns twice as long at night", 24),
        ["round 55: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 55: the candle burns twice as long at night", 32),
        ["round 55: the candle burns twice", "as long at night"],
    ),
    (
        ("round 55: a mirror of the universe in one line", 4),
        ["round", "55:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 55: a mirror of the universe in one line", 8),
        ["round", "55: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 55: a mirror of the universe in one line", 12),
        ["round 55: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 55: a mirror of the universe in one line", 16),
        ["round 55: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 55: a mirror of the universe in one line", 24), ["round 55: a mirror of", "the universe in one line"]),
    (("round 55: a mirror of the universe in one line", 32), ["round 55: a mirror of the", "universe in one line"]),
    (
        ("round 55: the queue drains before the storm", 4),
        ["round", "55:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 55: the queue drains before the storm", 8),
        ["round", "55: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 55: the queue drains before the storm", 12), ["round 55:", "the queue", "drains", "before the", "storm"]),
    (("round 55: the queue drains before the storm", 16), ["round 55: the", "queue drains", "before the storm"]),
    (("round 55: the queue drains before the storm", 24), ["round 55: the queue", "drains before the storm"]),
    (("round 55: the queue drains before the storm", 32), ["round 55: the queue drains", "before the storm"]),
    (
        ("kitten55 sitting55 agent55 angle55 universe55 memory55", 6),
        ["kitten55", "sitting55", "agent55", "angle55", "universe55", "memory55"],
    ),
    (
        ("kitten55 sitting55 agent55 angle55 universe55 memory55", 10),
        ["kitten55", "sitting55", "agent55", "angle55", "universe55", "memory55"],
    ),
    (
        ("kitten55 sitting55 agent55 angle55 universe55 memory55", 18),
        ["kitten55 sitting55", "agent55 angle55", "universe55", "memory55"],
    ),
    (
        ("kitten55 sitting55 agent55 angle55 universe55 memory55", 28),
        ["kitten55 sitting55 agent55", "angle55 universe55 memory55"],
    ),
    (
        ("sitting55 agent55 angle55 universe55 memory55 stream55", 6),
        ["sitting55", "agent55", "angle55", "universe55", "memory55", "stream55"],
    ),
    (
        ("sitting55 agent55 angle55 universe55 memory55 stream55", 10),
        ["sitting55", "agent55", "angle55", "universe55", "memory55", "stream55"],
    ),
    (
        ("sitting55 agent55 angle55 universe55 memory55 stream55", 18),
        ["sitting55 agent55", "angle55 universe55", "memory55 stream55"],
    ),
    (
        ("sitting55 agent55 angle55 universe55 memory55 stream55", 28),
        ["sitting55 agent55 angle55", "universe55 memory55 stream55"],
    ),
    (
        ("agent55 angle55 universe55 memory55 stream55 context55", 6),
        ["agent55", "angle55", "universe55", "memory55", "stream55", "context55"],
    ),
    (
        ("agent55 angle55 universe55 memory55 stream55 context55", 10),
        ["agent55", "angle55", "universe55", "memory55", "stream55", "context55"],
    ),
    (
        ("agent55 angle55 universe55 memory55 stream55 context55", 18),
        ["agent55 angle55", "universe55", "memory55 stream55", "context55"],
    ),
    (
        ("agent55 angle55 universe55 memory55 stream55 context55", 28),
        ["agent55 angle55 universe55", "memory55 stream55 context55"],
    ),
    (
        ("angle55 universe55 memory55 stream55 context55 knowledge55", 6),
        ["angle55", "universe55", "memory55", "stream55", "context55", "knowledge55"],
    ),
    (
        ("angle55 universe55 memory55 stream55 context55 knowledge55", 10),
        ["angle55", "universe55", "memory55", "stream55", "context55", "knowledge55"],
    ),
    (
        ("angle55 universe55 memory55 stream55 context55 knowledge55", 18),
        ["angle55 universe55", "memory55 stream55", "context55", "knowledge55"],
    ),
    (
        ("angle55 universe55 memory55 stream55 context55 knowledge55", 28),
        ["angle55 universe55 memory55", "stream55 context55", "knowledge55"],
    ),
    (
        ("universe55 memory55 stream55 context55 knowledge55 vector55", 6),
        ["universe55", "memory55", "stream55", "context55", "knowledge55", "vector55"],
    ),
    (
        ("universe55 memory55 stream55 context55 knowledge55 vector55", 10),
        ["universe55", "memory55", "stream55", "context55", "knowledge55", "vector55"],
    ),
    (
        ("universe55 memory55 stream55 context55 knowledge55 vector55", 18),
        ["universe55", "memory55 stream55", "context55", "knowledge55", "vector55"],
    ),
    (
        ("universe55 memory55 stream55 context55 knowledge55 vector55", 28),
        ["universe55 memory55 stream55", "context55 knowledge55", "vector55"],
    ),
    (
        ("memory55 stream55 context55 knowledge55 vector55 processor55", 6),
        ["memory55", "stream55", "context55", "knowledge55", "vector55", "processor55"],
    ),
    (
        ("memory55 stream55 context55 knowledge55 vector55 processor55", 10),
        ["memory55", "stream55", "context55", "knowledge55", "vector55", "processor55"],
    ),
    (
        ("memory55 stream55 context55 knowledge55 vector55 processor55", 18),
        ["memory55 stream55", "context55", "knowledge55", "vector55", "processor55"],
    ),
    (
        ("memory55 stream55 context55 knowledge55 vector55 processor55", 28),
        ["memory55 stream55 context55", "knowledge55 vector55", "processor55"],
    ),
    (
        ("stream55 context55 knowledge55 vector55 processor55 reasoning55", 6),
        ["stream55", "context55", "knowledge55", "vector55", "processor55", "reasoning55"],
    ),
    (
        ("stream55 context55 knowledge55 vector55 processor55 reasoning55", 10),
        ["stream55", "context55", "knowledge55", "vector55", "processor55", "reasoning55"],
    ),
    (
        ("stream55 context55 knowledge55 vector55 processor55 reasoning55", 18),
        ["stream55 context55", "knowledge55", "vector55", "processor55", "reasoning55"],
    ),
    (
        ("stream55 context55 knowledge55 vector55 processor55 reasoning55", 28),
        ["stream55 context55", "knowledge55 vector55", "processor55 reasoning55"],
    ),
    (
        ("context55 knowledge55 vector55 processor55 reasoning55 machine55", 6),
        ["context55", "knowledge55", "vector55", "processor55", "reasoning55", "machine55"],
    ),
    (
        ("context55 knowledge55 vector55 processor55 reasoning55 machine55", 10),
        ["context55", "knowledge55", "vector55", "processor55", "reasoning55", "machine55"],
    ),
    (
        ("context55 knowledge55 vector55 processor55 reasoning55 machine55", 18),
        ["context55", "knowledge55", "vector55", "processor55", "reasoning55", "machine55"],
    ),
    (
        ("context55 knowledge55 vector55 processor55 reasoning55 machine55", 28),
        ["context55 knowledge55", "vector55 processor55", "reasoning55 machine55"],
    ),
    (
        ("knowledge55 vector55 processor55 reasoning55 machine55 learning55", 6),
        ["knowledge55", "vector55", "processor55", "reasoning55", "machine55", "learning55"],
    ),
    (
        ("knowledge55 vector55 processor55 reasoning55 machine55 learning55", 10),
        ["knowledge55", "vector55", "processor55", "reasoning55", "machine55", "learning55"],
    ),
    (
        ("knowledge55 vector55 processor55 reasoning55 machine55 learning55", 18),
        ["knowledge55", "vector55", "processor55", "reasoning55", "machine55", "learning55"],
    ),
    (
        ("knowledge55 vector55 processor55 reasoning55 machine55 learning55", 28),
        ["knowledge55 vector55", "processor55 reasoning55", "machine55 learning55"],
    ),
    (
        ("vector55 processor55 reasoning55 machine55 learning55 model55", 6),
        ["vector55", "processor55", "reasoning55", "machine55", "learning55", "model55"],
    ),
    (
        ("vector55 processor55 reasoning55 machine55 learning55 model55", 10),
        ["vector55", "processor55", "reasoning55", "machine55", "learning55", "model55"],
    ),
    (
        ("vector55 processor55 reasoning55 machine55 learning55 model55", 18),
        ["vector55", "processor55", "reasoning55", "machine55", "learning55 model55"],
    ),
    (
        ("vector55 processor55 reasoning55 machine55 learning55 model55", 28),
        ["vector55 processor55", "reasoning55 machine55", "learning55 model55"],
    ),
    (
        ("processor55 reasoning55 machine55 learning55 model55 token55", 6),
        ["processor55", "reasoning55", "machine55", "learning55", "model55", "token55"],
    ),
    (
        ("processor55 reasoning55 machine55 learning55 model55 token55", 10),
        ["processor55", "reasoning55", "machine55", "learning55", "model55", "token55"],
    ),
    (
        ("processor55 reasoning55 machine55 learning55 model55 token55", 18),
        ["processor55", "reasoning55", "machine55", "learning55 model55", "token55"],
    ),
    (
        ("processor55 reasoning55 machine55 learning55 model55 token55", 28),
        ["processor55 reasoning55", "machine55 learning55 model55", "token55"],
    ),
    (
        ("reasoning55 machine55 learning55 model55 token55 prompt55", 6),
        ["reasoning55", "machine55", "learning55", "model55", "token55", "prompt55"],
    ),
    (
        ("reasoning55 machine55 learning55 model55 token55 prompt55", 10),
        ["reasoning55", "machine55", "learning55", "model55", "token55", "prompt55"],
    ),
    (
        ("reasoning55 machine55 learning55 model55 token55 prompt55", 18),
        ["reasoning55", "machine55", "learning55 model55", "token55 prompt55"],
    ),
    (
        ("reasoning55 machine55 learning55 model55 token55 prompt55", 28),
        ["reasoning55 machine55", "learning55 model55 token55", "prompt55"],
    ),
    (
        ("machine55 learning55 model55 token55 prompt55 session55", 6),
        ["machine55", "learning55", "model55", "token55", "prompt55", "session55"],
    ),
    (
        ("machine55 learning55 model55 token55 prompt55 session55", 10),
        ["machine55", "learning55", "model55", "token55", "prompt55", "session55"],
    ),
    (
        ("machine55 learning55 model55 token55 prompt55 session55", 18),
        ["machine55", "learning55 model55", "token55 prompt55", "session55"],
    ),
    (
        ("machine55 learning55 model55 token55 prompt55 session55", 28),
        ["machine55 learning55 model55", "token55 prompt55 session55"],
    ),
    (
        ("learning55 model55 token55 prompt55 session55 library55", 6),
        ["learning55", "model55", "token55", "prompt55", "session55", "library55"],
    ),
    (
        ("learning55 model55 token55 prompt55 session55 library55", 10),
        ["learning55", "model55", "token55", "prompt55", "session55", "library55"],
    ),
    (
        ("learning55 model55 token55 prompt55 session55 library55", 18),
        ["learning55 model55", "token55 prompt55", "session55", "library55"],
    ),
    (
        ("learning55 model55 token55 prompt55 session55 library55", 28),
        ["learning55 model55 token55", "prompt55 session55 library55"],
    ),
    (
        ("model55 token55 prompt55 session55 library55 service55", 6),
        ["model55", "token55", "prompt55", "session55", "library55", "service55"],
    ),
    (
        ("model55 token55 prompt55 session55 library55 service55", 10),
        ["model55", "token55", "prompt55", "session55", "library55", "service55"],
    ),
    (
        ("model55 token55 prompt55 session55 library55 service55", 18),
        ["model55 token55", "prompt55 session55", "library55", "service55"],
    ),
    (
        ("model55 token55 prompt55 session55 library55 service55", 28),
        ["model55 token55 prompt55", "session55 library55", "service55"],
    ),
    (
        ("token55 prompt55 session55 library55 service55 gateway55", 6),
        ["token55", "prompt55", "session55", "library55", "service55", "gateway55"],
    ),
    (
        ("token55 prompt55 session55 library55 service55 gateway55", 10),
        ["token55", "prompt55", "session55", "library55", "service55", "gateway55"],
    ),
    (
        ("token55 prompt55 session55 library55 service55 gateway55", 18),
        ["token55 prompt55", "session55", "library55", "service55", "gateway55"],
    ),
    (
        ("token55 prompt55 session55 library55 service55 gateway55", 28),
        ["token55 prompt55 session55", "library55 service55", "gateway55"],
    ),
    (
        ("prompt55 session55 library55 service55 gateway55 storage55", 6),
        ["prompt55", "session55", "library55", "service55", "gateway55", "storage55"],
    ),
    (
        ("prompt55 session55 library55 service55 gateway55 storage55", 10),
        ["prompt55", "session55", "library55", "service55", "gateway55", "storage55"],
    ),
    (
        ("prompt55 session55 library55 service55 gateway55 storage55", 18),
        ["prompt55 session55", "library55", "service55", "gateway55", "storage55"],
    ),
    (
        ("prompt55 session55 library55 service55 gateway55 storage55", 28),
        ["prompt55 session55 library55", "service55 gateway55", "storage55"],
    ),
    (
        ("session55 library55 service55 gateway55 storage55 network55", 6),
        ["session55", "library55", "service55", "gateway55", "storage55", "network55"],
    ),
    (
        ("session55 library55 service55 gateway55 storage55 network55", 10),
        ["session55", "library55", "service55", "gateway55", "storage55", "network55"],
    ),
    (
        ("session55 library55 service55 gateway55 storage55 network55", 18),
        ["session55", "library55", "service55", "gateway55", "storage55", "network55"],
    ),
    (
        ("session55 library55 service55 gateway55 storage55 network55", 28),
        ["session55 library55", "service55 gateway55", "storage55 network55"],
    ),
    (
        ("library55 service55 gateway55 storage55 network55 latency55", 6),
        ["library55", "service55", "gateway55", "storage55", "network55", "latency55"],
    ),
    (
        ("library55 service55 gateway55 storage55 network55 latency55", 10),
        ["library55", "service55", "gateway55", "storage55", "network55", "latency55"],
    ),
    (
        ("library55 service55 gateway55 storage55 network55 latency55", 18),
        ["library55", "service55", "gateway55", "storage55", "network55", "latency55"],
    ),
    (
        ("library55 service55 gateway55 storage55 network55 latency55", 28),
        ["library55 service55", "gateway55 storage55", "network55 latency55"],
    ),
    (
        ("service55 gateway55 storage55 network55 latency55 buffer55", 6),
        ["service55", "gateway55", "storage55", "network55", "latency55", "buffer55"],
    ),
    (
        ("service55 gateway55 storage55 network55 latency55 buffer55", 10),
        ["service55", "gateway55", "storage55", "network55", "latency55", "buffer55"],
    ),
    (
        ("service55 gateway55 storage55 network55 latency55 buffer55", 18),
        ["service55", "gateway55", "storage55", "network55", "latency55 buffer55"],
    ),
    (
        ("service55 gateway55 storage55 network55 latency55 buffer55", 28),
        ["service55 gateway55", "storage55 network55", "latency55 buffer55"],
    ),
    (
        ("gateway55 storage55 network55 latency55 buffer55 queue55", 6),
        ["gateway55", "storage55", "network55", "latency55", "buffer55", "queue55"],
    ),
    (
        ("gateway55 storage55 network55 latency55 buffer55 queue55", 10),
        ["gateway55", "storage55", "network55", "latency55", "buffer55", "queue55"],
    ),
    (
        ("gateway55 storage55 network55 latency55 buffer55 queue55", 18),
        ["gateway55", "storage55", "network55", "latency55 buffer55", "queue55"],
    ),
    (
        ("gateway55 storage55 network55 latency55 buffer55 queue55", 28),
        ["gateway55 storage55", "network55 latency55 buffer55", "queue55"],
    ),
    (
        ("storage55 network55 latency55 buffer55 queue55 worker55", 6),
        ["storage55", "network55", "latency55", "buffer55", "queue55", "worker55"],
    ),
    (
        ("storage55 network55 latency55 buffer55 queue55 worker55", 10),
        ["storage55", "network55", "latency55", "buffer55", "queue55", "worker55"],
    ),
    (
        ("storage55 network55 latency55 buffer55 queue55 worker55", 18),
        ["storage55", "network55", "latency55 buffer55", "queue55 worker55"],
    ),
    (
        ("storage55 network55 latency55 buffer55 queue55 worker55", 28),
        ["storage55 network55", "latency55 buffer55 queue55", "worker55"],
    ),
    (
        ("network55 latency55 buffer55 queue55 worker55 kernel55", 6),
        ["network55", "latency55", "buffer55", "queue55", "worker55", "kernel55"],
    ),
    (
        ("network55 latency55 buffer55 queue55 worker55 kernel55", 10),
        ["network55", "latency55", "buffer55", "queue55", "worker55", "kernel55"],
    ),
    (
        ("network55 latency55 buffer55 queue55 worker55 kernel55", 18),
        ["network55", "latency55 buffer55", "queue55 worker55", "kernel55"],
    ),
    (
        ("network55 latency55 buffer55 queue55 worker55 kernel55", 28),
        ["network55 latency55 buffer55", "queue55 worker55 kernel55"],
    ),
    (
        ("latency55 buffer55 queue55 worker55 kernel55 signal55", 6),
        ["latency55", "buffer55", "queue55", "worker55", "kernel55", "signal55"],
    ),
    (
        ("latency55 buffer55 queue55 worker55 kernel55 signal55", 10),
        ["latency55", "buffer55", "queue55", "worker55", "kernel55", "signal55"],
    ),
    (
        ("latency55 buffer55 queue55 worker55 kernel55 signal55", 18),
        ["latency55 buffer55", "queue55 worker55", "kernel55 signal55"],
    ),
    (
        ("latency55 buffer55 queue55 worker55 kernel55 signal55", 28),
        ["latency55 buffer55 queue55", "worker55 kernel55 signal55"],
    ),
    (
        ("buffer55 queue55 worker55 kernel55 signal55 packet55", 6),
        ["buffer55", "queue55", "worker55", "kernel55", "signal55", "packet55"],
    ),
    (
        ("buffer55 queue55 worker55 kernel55 signal55 packet55", 10),
        ["buffer55", "queue55", "worker55", "kernel55", "signal55", "packet55"],
    ),
    (
        ("buffer55 queue55 worker55 kernel55 signal55 packet55", 18),
        ["buffer55 queue55", "worker55 kernel55", "signal55 packet55"],
    ),
    (
        ("buffer55 queue55 worker55 kernel55 signal55 packet55", 28),
        ["buffer55 queue55 worker55", "kernel55 signal55 packet55"],
    ),
    (
        ("queue55 worker55 kernel55 signal55 packet55 router55", 6),
        ["queue55", "worker55", "kernel55", "signal55", "packet55", "router55"],
    ),
    (
        ("queue55 worker55 kernel55 signal55 packet55 router55", 10),
        ["queue55", "worker55", "kernel55", "signal55", "packet55", "router55"],
    ),
    (
        ("queue55 worker55 kernel55 signal55 packet55 router55", 18),
        ["queue55 worker55", "kernel55 signal55", "packet55 router55"],
    ),
    (
        ("queue55 worker55 kernel55 signal55 packet55 router55", 28),
        ["queue55 worker55 kernel55", "signal55 packet55 router55"],
    ),
    (
        ("worker55 kernel55 signal55 packet55 router55 cluster55", 6),
        ["worker55", "kernel55", "signal55", "packet55", "router55", "cluster55"],
    ),
    (
        ("worker55 kernel55 signal55 packet55 router55 cluster55", 10),
        ["worker55", "kernel55", "signal55", "packet55", "router55", "cluster55"],
    ),
    (
        ("worker55 kernel55 signal55 packet55 router55 cluster55", 18),
        ["worker55 kernel55", "signal55 packet55", "router55 cluster55"],
    ),
    (
        ("worker55 kernel55 signal55 packet55 router55 cluster55", 28),
        ["worker55 kernel55 signal55", "packet55 router55 cluster55"],
    ),
    (
        ("kernel55 signal55 packet55 router55 cluster55 mirror55", 6),
        ["kernel55", "signal55", "packet55", "router55", "cluster55", "mirror55"],
    ),
    (
        ("kernel55 signal55 packet55 router55 cluster55 mirror55", 10),
        ["kernel55", "signal55", "packet55", "router55", "cluster55", "mirror55"],
    ),
    (
        ("kernel55 signal55 packet55 router55 cluster55 mirror55", 18),
        ["kernel55 signal55", "packet55 router55", "cluster55 mirror55"],
    ),
    (
        ("kernel55 signal55 packet55 router55 cluster55 mirror55", 28),
        ["kernel55 signal55 packet55", "router55 cluster55 mirror55"],
    ),
    (
        ("signal55 packet55 router55 cluster55 mirror55 filter55", 6),
        ["signal55", "packet55", "router55", "cluster55", "mirror55", "filter55"],
    ),
    (
        ("signal55 packet55 router55 cluster55 mirror55 filter55", 10),
        ["signal55", "packet55", "router55", "cluster55", "mirror55", "filter55"],
    ),
    (
        ("signal55 packet55 router55 cluster55 mirror55 filter55", 18),
        ["signal55 packet55", "router55 cluster55", "mirror55 filter55"],
    ),
    (
        ("signal55 packet55 router55 cluster55 mirror55 filter55", 28),
        ["signal55 packet55 router55", "cluster55 mirror55 filter55"],
    ),
    (
        ("packet55 router55 cluster55 mirror55 filter55 ranking55", 6),
        ["packet55", "router55", "cluster55", "mirror55", "filter55", "ranking55"],
    ),
    (
        ("packet55 router55 cluster55 mirror55 filter55 ranking55", 10),
        ["packet55", "router55", "cluster55", "mirror55", "filter55", "ranking55"],
    ),
    (
        ("packet55 router55 cluster55 mirror55 filter55 ranking55", 18),
        ["packet55 router55", "cluster55 mirror55", "filter55 ranking55"],
    ),
    (
        ("packet55 router55 cluster55 mirror55 filter55 ranking55", 28),
        ["packet55 router55 cluster55", "mirror55 filter55 ranking55"],
    ),
    (
        ("router55 cluster55 mirror55 filter55 ranking55 encoding55", 6),
        ["router55", "cluster55", "mirror55", "filter55", "ranking55", "encoding55"],
    ),
    (
        ("router55 cluster55 mirror55 filter55 ranking55 encoding55", 10),
        ["router55", "cluster55", "mirror55", "filter55", "ranking55", "encoding55"],
    ),
    (
        ("router55 cluster55 mirror55 filter55 ranking55 encoding55", 18),
        ["router55 cluster55", "mirror55 filter55", "ranking55", "encoding55"],
    ),
    (
        ("router55 cluster55 mirror55 filter55 ranking55 encoding55", 28),
        ["router55 cluster55 mirror55", "filter55 ranking55", "encoding55"],
    ),
    (
        ("cluster55 mirror55 filter55 ranking55 encoding55 mapping55", 6),
        ["cluster55", "mirror55", "filter55", "ranking55", "encoding55", "mapping55"],
    ),
    (
        ("cluster55 mirror55 filter55 ranking55 encoding55 mapping55", 10),
        ["cluster55", "mirror55", "filter55", "ranking55", "encoding55", "mapping55"],
    ),
    (
        ("cluster55 mirror55 filter55 ranking55 encoding55 mapping55", 18),
        ["cluster55 mirror55", "filter55 ranking55", "encoding55", "mapping55"],
    ),
    (
        ("cluster55 mirror55 filter55 ranking55 encoding55 mapping55", 28),
        ["cluster55 mirror55 filter55", "ranking55 encoding55", "mapping55"],
    ),
    (
        ("mirror55 filter55 ranking55 encoding55 mapping55 record55", 6),
        ["mirror55", "filter55", "ranking55", "encoding55", "mapping55", "record55"],
    ),
    (
        ("mirror55 filter55 ranking55 encoding55 mapping55 record55", 10),
        ["mirror55", "filter55", "ranking55", "encoding55", "mapping55", "record55"],
    ),
    (
        ("mirror55 filter55 ranking55 encoding55 mapping55 record55", 18),
        ["mirror55 filter55", "ranking55", "encoding55", "mapping55 record55"],
    ),
    (
        ("mirror55 filter55 ranking55 encoding55 mapping55 record55", 28),
        ["mirror55 filter55 ranking55", "encoding55 mapping55", "record55"],
    ),
    (
        ("filter55 ranking55 encoding55 mapping55 record55 candle55", 6),
        ["filter55", "ranking55", "encoding55", "mapping55", "record55", "candle55"],
    ),
    (
        ("filter55 ranking55 encoding55 mapping55 record55 candle55", 10),
        ["filter55", "ranking55", "encoding55", "mapping55", "record55", "candle55"],
    ),
    (
        ("filter55 ranking55 encoding55 mapping55 record55 candle55", 18),
        ["filter55 ranking55", "encoding55", "mapping55 record55", "candle55"],
    ),
    (
        ("filter55 ranking55 encoding55 mapping55 record55 candle55", 28),
        ["filter55 ranking55", "encoding55 mapping55", "record55 candle55"],
    ),
    (
        ("ranking55 encoding55 mapping55 record55 candle55 thread55", 6),
        ["ranking55", "encoding55", "mapping55", "record55", "candle55", "thread55"],
    ),
    (
        ("ranking55 encoding55 mapping55 record55 candle55 thread55", 10),
        ["ranking55", "encoding55", "mapping55", "record55", "candle55", "thread55"],
    ),
    (
        ("ranking55 encoding55 mapping55 record55 candle55 thread55", 18),
        ["ranking55", "encoding55", "mapping55 record55", "candle55 thread55"],
    ),
    (
        ("ranking55 encoding55 mapping55 record55 candle55 thread55", 28),
        ["ranking55 encoding55", "mapping55 record55 candle55", "thread55"],
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
