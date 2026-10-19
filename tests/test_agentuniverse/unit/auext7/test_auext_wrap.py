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
        ("round 7: the quick brown fox jumps over the lazy dog", 4),
        ["round", "7:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 7: the quick brown fox jumps over the lazy dog", 8),
        ["round 7:", "the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 7: the quick brown fox jumps over the lazy dog", 12),
        ["round 7: the", "quick brown", "fox jumps", "over the", "lazy dog"],
    ),
    (
        ("round 7: the quick brown fox jumps over the lazy dog", 16),
        ["round 7: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 7: the quick brown fox jumps over the lazy dog", 24),
        ["round 7: the quick brown", "fox jumps over the lazy", "dog"],
    ),
    (
        ("round 7: the quick brown fox jumps over the lazy dog", 32),
        ["round 7: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 7: agentuniverse is a framework for multi agents", 4),
        ["round", "7:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 7: agentuniverse is a framework for multi agents", 8),
        ["round 7:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 7: agentuniverse is a framework for multi agents", 12),
        ["round 7:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 7: agentuniverse is a framework for multi agents", 16),
        ["round 7:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 7: agentuniverse is a framework for multi agents", 24),
        ["round 7: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 7: agentuniverse is a framework for multi agents", 32),
        ["round 7: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 7: knowledge stored as vectors enables retrieval", 4),
        ["round", "7:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 7: knowledge stored as vectors enables retrieval", 8),
        ["round 7:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 7: knowledge stored as vectors enables retrieval", 12),
        ["round 7:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 7: knowledge stored as vectors enables retrieval", 16),
        ["round 7:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 7: knowledge stored as vectors enables retrieval", 24),
        ["round 7: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 7: knowledge stored as vectors enables retrieval", 32),
        ["round 7: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 7: the processor reads the record then stops", 4),
        ["round", "7:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 7: the processor reads the record then stops", 8),
        ["round 7:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 7: the processor reads the record then stops", 12),
        ["round 7: the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 7: the processor reads the record then stops", 16),
        ["round 7: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 7: the processor reads the record then stops", 24),
        ["round 7: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 7: the processor reads the record then stops", 32),
        ["round 7: the processor reads the", "record then stops"],
    ),
    (
        ("round 7: a worker pulls the next task from the queue", 4),
        ["round", "7: a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 7: a worker pulls the next task from the queue", 8),
        ["round 7:", "a worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 7: a worker pulls the next task from the queue", 12),
        ["round 7: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 7: a worker pulls the next task from the queue", 16),
        ["round 7: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 7: a worker pulls the next task from the queue", 24),
        ["round 7: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 7: a worker pulls the next task from the queue", 32),
        ["round 7: a worker pulls the next", "task from the queue"],
    ),
    (
        ("round 7: signals travel through the network layer", 4),
        ["round", "7:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 7: signals travel through the network layer", 8),
        ["round 7:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 7: signals travel through the network layer", 12),
        ["round 7:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 7: signals travel through the network layer", 16),
        ["round 7: signals", "travel through", "the network", "layer"],
    ),
    (
        ("round 7: signals travel through the network layer", 24),
        ["round 7: signals travel", "through the network", "layer"],
    ),
    (
        ("round 7: signals travel through the network layer", 32),
        ["round 7: signals travel through", "the network layer"],
    ),
    (
        ("round 7: the gateway routes each request by policy", 4),
        ["round", "7:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 7: the gateway routes each request by policy", 8),
        ["round 7:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 7: the gateway routes each request by policy", 12),
        ["round 7: the", "gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 7: the gateway routes each request by policy", 16),
        ["round 7: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 7: the gateway routes each request by policy", 24),
        ["round 7: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 7: the gateway routes each request by policy", 32),
        ["round 7: the gateway routes each", "request by policy"],
    ),
    (
        ("round 7: memory grows until the buffer is full", 4),
        ["round", "7:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 7: memory grows until the buffer is full", 8),
        ["round 7:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 7: memory grows until the buffer is full", 12),
        ["round 7:", "memory grows", "until the", "buffer is", "full"],
    ),
    (("round 7: memory grows until the buffer is full", 16), ["round 7: memory", "grows until the", "buffer is full"]),
    (("round 7: memory grows until the buffer is full", 24), ["round 7: memory grows", "until the buffer is full"]),
    (("round 7: memory grows until the buffer is full", 32), ["round 7: memory grows until the", "buffer is full"]),
    (
        ("round 7: the cluster mirrors every packet twice", 4),
        ["round", "7:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 7: the cluster mirrors every packet twice", 8),
        ["round 7:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 7: the cluster mirrors every packet twice", 12),
        ["round 7: the", "cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 7: the cluster mirrors every packet twice", 16),
        ["round 7: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 7: the cluster mirrors every packet twice", 24),
        ["round 7: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 7: the cluster mirrors every packet twice", 32), ["round 7: the cluster mirrors", "every packet twice"]),
    (
        ("round 7: ranking uses tokens learned from the corpus", 4),
        ["round", "7:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 7: ranking uses tokens learned from the corpus", 8),
        ["round 7:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 7: ranking uses tokens learned from the corpus", 12),
        ["round 7:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 7: ranking uses tokens learned from the corpus", 16),
        ["round 7: ranking", "uses tokens", "learned from the", "corpus"],
    ),
    (
        ("round 7: ranking uses tokens learned from the corpus", 24),
        ["round 7: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 7: ranking uses tokens learned from the corpus", 32),
        ["round 7: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 7: a long session ends when the candle dies", 4),
        ["round", "7: a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 7: a long session ends when the candle dies", 8),
        ["round 7:", "a long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 7: a long session ends when the candle dies", 12),
        ["round 7: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 7: a long session ends when the candle dies", 16),
        ["round 7: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 7: a long session ends when the candle dies", 24),
        ["round 7: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 7: a long session ends when the candle dies", 32),
        ["round 7: a long session ends", "when the candle dies"],
    ),
    (
        ("round 7: encode the prompt then map the result", 4),
        ["round", "7:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 7: encode the prompt then map the result", 8),
        ["round 7:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 7: encode the prompt then map the result", 12),
        ["round 7:", "encode the", "prompt then", "map the", "result"],
    ),
    (("round 7: encode the prompt then map the result", 16), ["round 7: encode", "the prompt then", "map the result"]),
    (("round 7: encode the prompt then map the result", 24), ["round 7: encode the", "prompt then map the", "result"]),
    (("round 7: encode the prompt then map the result", 32), ["round 7: encode the prompt then", "map the result"]),
    (
        ("round 7: the kernel wakes the worker at dawn", 4),
        ["round", "7:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 7: the kernel wakes the worker at dawn", 8),
        ["round 7:", "the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (("round 7: the kernel wakes the worker at dawn", 12), ["round 7: the", "kernel wakes", "the worker", "at dawn"]),
    (("round 7: the kernel wakes the worker at dawn", 16), ["round 7: the", "kernel wakes the", "worker at dawn"]),
    (("round 7: the kernel wakes the worker at dawn", 24), ["round 7: the kernel", "wakes the worker at dawn"]),
    (("round 7: the kernel wakes the worker at dawn", 32), ["round 7: the kernel wakes the", "worker at dawn"]),
    (
        ("round 7: service latency drops after the patch", 4),
        ["round", "7:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 7: service latency drops after the patch", 8),
        ["round 7:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 7: service latency drops after the patch", 12),
        ["round 7:", "service", "latency", "drops after", "the patch"],
    ),
    (("round 7: service latency drops after the patch", 16), ["round 7: service", "latency drops", "after the patch"]),
    (("round 7: service latency drops after the patch", 24), ["round 7: service latency", "drops after the patch"]),
    (("round 7: service latency drops after the patch", 32), ["round 7: service latency drops", "after the patch"]),
    (
        ("round 7: the library caches every vector it sees", 4),
        ["round", "7:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 7: the library caches every vector it sees", 8),
        ["round 7:", "the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 7: the library caches every vector it sees", 12),
        ["round 7: the", "library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 7: the library caches every vector it sees", 16),
        ["round 7: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 7: the library caches every vector it sees", 24),
        ["round 7: the library", "caches every vector it", "sees"],
    ),
    (("round 7: the library caches every vector it sees", 32), ["round 7: the library caches", "every vector it sees"]),
    (
        ("round 7: agents argue then the debate resolves", 4),
        ["round", "7:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 7: agents argue then the debate resolves", 8),
        ["round 7:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 7: agents argue then the debate resolves", 12),
        ["round 7:", "agents argue", "then the", "debate", "resolves"],
    ),
    (("round 7: agents argue then the debate resolves", 16), ["round 7: agents", "argue then the", "debate resolves"]),
    (("round 7: agents argue then the debate resolves", 24), ["round 7: agents argue", "then the debate resolves"]),
    (("round 7: agents argue then the debate resolves", 32), ["round 7: agents argue then the", "debate resolves"]),
    (
        ("round 7: the filter keeps only strong matches", 4),
        ["round", "7:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 7: the filter keeps only strong matches", 8),
        ["round 7:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (("round 7: the filter keeps only strong matches", 12), ["round 7: the", "filter keeps", "only strong", "matches"]),
    (("round 7: the filter keeps only strong matches", 16), ["round 7: the", "filter keeps", "only strong", "matches"]),
    (("round 7: the filter keeps only strong matches", 24), ["round 7: the filter", "keeps only strong", "matches"]),
    (("round 7: the filter keeps only strong matches", 32), ["round 7: the filter keeps only", "strong matches"]),
    (
        ("round 7: the model answers with a short reply", 4),
        ["round", "7:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 7: the model answers with a short reply", 8),
        ["round 7:", "the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 7: the model answers with a short reply", 12),
        ["round 7: the", "model", "answers with", "a short", "reply"],
    ),
    (("round 7: the model answers with a short reply", 16), ["round 7: the", "model answers", "with a short", "reply"]),
    (("round 7: the model answers with a short reply", 24), ["round 7: the model", "answers with a short", "reply"]),
    (("round 7: the model answers with a short reply", 32), ["round 7: the model answers with", "a short reply"]),
    (
        ("round 7: the recorder stores the reasoning trace", 4),
        ["round", "7:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 7: the recorder stores the reasoning trace", 8),
        ["round 7:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 7: the recorder stores the reasoning trace", 12),
        ["round 7: the", "recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 7: the recorder stores the reasoning trace", 16),
        ["round 7: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 7: the recorder stores the reasoning trace", 24),
        ["round 7: the recorder", "stores the reasoning", "trace"],
    ),
    (("round 7: the recorder stores the reasoning trace", 32), ["round 7: the recorder stores the", "reasoning trace"]),
    (
        ("round 7: the angel watches the processor run", 4),
        ["round", "7:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 7: the angel watches the processor run", 8),
        ["round 7:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 7: the angel watches the processor run", 12),
        ["round 7: the", "angel", "watches the", "processor", "run"],
    ),
    (("round 7: the angel watches the processor run", 16), ["round 7: the", "angel watches", "the processor", "run"]),
    (("round 7: the angel watches the processor run", 24), ["round 7: the angel", "watches the processor", "run"]),
    (("round 7: the angel watches the processor run", 32), ["round 7: the angel watches the", "processor run"]),
    (
        ("round 7: angle of the vector decides the match", 4),
        ["round", "7:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 7: angle of the vector decides the match", 8),
        ["round 7:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 7: angle of the vector decides the match", 12),
        ["round 7:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 7: angle of the vector decides the match", 16),
        ["round 7: angle", "of the vector", "decides the", "match"],
    ),
    (("round 7: angle of the vector decides the match", 24), ["round 7: angle of the", "vector decides the match"]),
    (("round 7: angle of the vector decides the match", 32), ["round 7: angle of the vector", "decides the match"]),
    (
        ("round 7: the candle burns twice as long at night", 4),
        ["round", "7:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 7: the candle burns twice as long at night", 8),
        ["round 7:", "the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 7: the candle burns twice as long at night", 12),
        ["round 7: the", "candle burns", "twice as", "long at", "night"],
    ),
    (
        ("round 7: the candle burns twice as long at night", 16),
        ["round 7: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 7: the candle burns twice as long at night", 24),
        ["round 7: the candle", "burns twice as long at", "night"],
    ),
    (("round 7: the candle burns twice as long at night", 32), ["round 7: the candle burns twice", "as long at night"]),
    (
        ("round 7: a mirror of the universe in one line", 4),
        ["round", "7: a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 7: a mirror of the universe in one line", 8),
        ["round 7:", "a mirror", "of the", "universe", "in one", "line"],
    ),
    (("round 7: a mirror of the universe in one line", 12), ["round 7: a", "mirror of", "the universe", "in one line"]),
    (("round 7: a mirror of the universe in one line", 16), ["round 7: a", "mirror of the", "universe in one", "line"]),
    (("round 7: a mirror of the universe in one line", 24), ["round 7: a mirror of the", "universe in one line"]),
    (("round 7: a mirror of the universe in one line", 32), ["round 7: a mirror of the", "universe in one line"]),
    (
        ("round 7: the queue drains before the storm", 4),
        ["round", "7:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 7: the queue drains before the storm", 8),
        ["round 7:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 7: the queue drains before the storm", 12), ["round 7: the", "queue drains", "before the", "storm"]),
    (("round 7: the queue drains before the storm", 16), ["round 7: the", "queue drains", "before the storm"]),
    (("round 7: the queue drains before the storm", 24), ["round 7: the queue", "drains before the storm"]),
    (("round 7: the queue drains before the storm", 32), ["round 7: the queue drains before", "the storm"]),
    (
        ("kitten7 sitting7 agent7 angle7 universe7 memory7", 6),
        ["kitten7", "sitting7", "agent7", "angle7", "universe7", "memory7"],
    ),
    (
        ("kitten7 sitting7 agent7 angle7 universe7 memory7", 10),
        ["kitten7", "sitting7", "agent7", "angle7", "universe7", "memory7"],
    ),
    (
        ("kitten7 sitting7 agent7 angle7 universe7 memory7", 18),
        ["kitten7 sitting7", "agent7 angle7", "universe7 memory7"],
    ),
    (("kitten7 sitting7 agent7 angle7 universe7 memory7", 28), ["kitten7 sitting7 agent7", "angle7 universe7 memory7"]),
    (
        ("sitting7 agent7 angle7 universe7 memory7 stream7", 6),
        ["sitting7", "agent7", "angle7", "universe7", "memory7", "stream7"],
    ),
    (
        ("sitting7 agent7 angle7 universe7 memory7 stream7", 10),
        ["sitting7", "agent7", "angle7", "universe7", "memory7", "stream7"],
    ),
    (
        ("sitting7 agent7 angle7 universe7 memory7 stream7", 18),
        ["sitting7 agent7", "angle7 universe7", "memory7 stream7"],
    ),
    (("sitting7 agent7 angle7 universe7 memory7 stream7", 28), ["sitting7 agent7 angle7", "universe7 memory7 stream7"]),
    (
        ("agent7 angle7 universe7 memory7 stream7 context7", 6),
        ["agent7", "angle7", "universe7", "memory7", "stream7", "context7"],
    ),
    (
        ("agent7 angle7 universe7 memory7 stream7 context7", 10),
        ["agent7", "angle7", "universe7", "memory7", "stream7", "context7"],
    ),
    (
        ("agent7 angle7 universe7 memory7 stream7 context7", 18),
        ["agent7 angle7", "universe7 memory7", "stream7 context7"],
    ),
    (("agent7 angle7 universe7 memory7 stream7 context7", 28), ["agent7 angle7 universe7", "memory7 stream7 context7"]),
    (
        ("angle7 universe7 memory7 stream7 context7 knowledge7", 6),
        ["angle7", "universe7", "memory7", "stream7", "context7", "knowledge7"],
    ),
    (
        ("angle7 universe7 memory7 stream7 context7 knowledge7", 10),
        ["angle7", "universe7", "memory7", "stream7", "context7", "knowledge7"],
    ),
    (
        ("angle7 universe7 memory7 stream7 context7 knowledge7", 18),
        ["angle7 universe7", "memory7 stream7", "context7", "knowledge7"],
    ),
    (
        ("angle7 universe7 memory7 stream7 context7 knowledge7", 28),
        ["angle7 universe7 memory7", "stream7 context7 knowledge7"],
    ),
    (
        ("universe7 memory7 stream7 context7 knowledge7 vector7", 6),
        ["universe7", "memory7", "stream7", "context7", "knowledge7", "vector7"],
    ),
    (
        ("universe7 memory7 stream7 context7 knowledge7 vector7", 10),
        ["universe7", "memory7", "stream7", "context7", "knowledge7", "vector7"],
    ),
    (
        ("universe7 memory7 stream7 context7 knowledge7 vector7", 18),
        ["universe7 memory7", "stream7 context7", "knowledge7 vector7"],
    ),
    (
        ("universe7 memory7 stream7 context7 knowledge7 vector7", 28),
        ["universe7 memory7 stream7", "context7 knowledge7 vector7"],
    ),
    (
        ("memory7 stream7 context7 knowledge7 vector7 processor7", 6),
        ["memory7", "stream7", "context7", "knowledge7", "vector7", "processor7"],
    ),
    (
        ("memory7 stream7 context7 knowledge7 vector7 processor7", 10),
        ["memory7", "stream7", "context7", "knowledge7", "vector7", "processor7"],
    ),
    (
        ("memory7 stream7 context7 knowledge7 vector7 processor7", 18),
        ["memory7 stream7", "context7", "knowledge7 vector7", "processor7"],
    ),
    (
        ("memory7 stream7 context7 knowledge7 vector7 processor7", 28),
        ["memory7 stream7 context7", "knowledge7 vector7", "processor7"],
    ),
    (
        ("stream7 context7 knowledge7 vector7 processor7 reasoning7", 6),
        ["stream7", "context7", "knowledge7", "vector7", "processor7", "reasoning7"],
    ),
    (
        ("stream7 context7 knowledge7 vector7 processor7 reasoning7", 10),
        ["stream7", "context7", "knowledge7", "vector7", "processor7", "reasoning7"],
    ),
    (
        ("stream7 context7 knowledge7 vector7 processor7 reasoning7", 18),
        ["stream7 context7", "knowledge7 vector7", "processor7", "reasoning7"],
    ),
    (
        ("stream7 context7 knowledge7 vector7 processor7 reasoning7", 28),
        ["stream7 context7 knowledge7", "vector7 processor7", "reasoning7"],
    ),
    (
        ("context7 knowledge7 vector7 processor7 reasoning7 machine7", 6),
        ["context7", "knowledge7", "vector7", "processor7", "reasoning7", "machine7"],
    ),
    (
        ("context7 knowledge7 vector7 processor7 reasoning7 machine7", 10),
        ["context7", "knowledge7", "vector7", "processor7", "reasoning7", "machine7"],
    ),
    (
        ("context7 knowledge7 vector7 processor7 reasoning7 machine7", 18),
        ["context7", "knowledge7 vector7", "processor7", "reasoning7", "machine7"],
    ),
    (
        ("context7 knowledge7 vector7 processor7 reasoning7 machine7", 28),
        ["context7 knowledge7 vector7", "processor7 reasoning7", "machine7"],
    ),
    (
        ("knowledge7 vector7 processor7 reasoning7 machine7 learning7", 6),
        ["knowledge7", "vector7", "processor7", "reasoning7", "machine7", "learning7"],
    ),
    (
        ("knowledge7 vector7 processor7 reasoning7 machine7 learning7", 10),
        ["knowledge7", "vector7", "processor7", "reasoning7", "machine7", "learning7"],
    ),
    (
        ("knowledge7 vector7 processor7 reasoning7 machine7 learning7", 18),
        ["knowledge7 vector7", "processor7", "reasoning7", "machine7 learning7"],
    ),
    (
        ("knowledge7 vector7 processor7 reasoning7 machine7 learning7", 28),
        ["knowledge7 vector7", "processor7 reasoning7", "machine7 learning7"],
    ),
    (
        ("vector7 processor7 reasoning7 machine7 learning7 model7", 6),
        ["vector7", "processor7", "reasoning7", "machine7", "learning7", "model7"],
    ),
    (
        ("vector7 processor7 reasoning7 machine7 learning7 model7", 10),
        ["vector7", "processor7", "reasoning7", "machine7", "learning7", "model7"],
    ),
    (
        ("vector7 processor7 reasoning7 machine7 learning7 model7", 18),
        ["vector7 processor7", "reasoning7", "machine7 learning7", "model7"],
    ),
    (
        ("vector7 processor7 reasoning7 machine7 learning7 model7", 28),
        ["vector7 processor7", "reasoning7 machine7", "learning7 model7"],
    ),
    (
        ("processor7 reasoning7 machine7 learning7 model7 token7", 6),
        ["processor7", "reasoning7", "machine7", "learning7", "model7", "token7"],
    ),
    (
        ("processor7 reasoning7 machine7 learning7 model7 token7", 10),
        ["processor7", "reasoning7", "machine7", "learning7", "model7", "token7"],
    ),
    (
        ("processor7 reasoning7 machine7 learning7 model7 token7", 18),
        ["processor7", "reasoning7", "machine7 learning7", "model7 token7"],
    ),
    (
        ("processor7 reasoning7 machine7 learning7 model7 token7", 28),
        ["processor7 reasoning7", "machine7 learning7 model7", "token7"],
    ),
    (
        ("reasoning7 machine7 learning7 model7 token7 prompt7", 6),
        ["reasoning7", "machine7", "learning7", "model7", "token7", "prompt7"],
    ),
    (
        ("reasoning7 machine7 learning7 model7 token7 prompt7", 10),
        ["reasoning7", "machine7", "learning7", "model7", "token7", "prompt7"],
    ),
    (
        ("reasoning7 machine7 learning7 model7 token7 prompt7", 18),
        ["reasoning7", "machine7 learning7", "model7 token7", "prompt7"],
    ),
    (
        ("reasoning7 machine7 learning7 model7 token7 prompt7", 28),
        ["reasoning7 machine7", "learning7 model7 token7", "prompt7"],
    ),
    (
        ("machine7 learning7 model7 token7 prompt7 session7", 6),
        ["machine7", "learning7", "model7", "token7", "prompt7", "session7"],
    ),
    (
        ("machine7 learning7 model7 token7 prompt7 session7", 10),
        ["machine7", "learning7", "model7", "token7", "prompt7", "session7"],
    ),
    (
        ("machine7 learning7 model7 token7 prompt7 session7", 18),
        ["machine7 learning7", "model7 token7", "prompt7 session7"],
    ),
    (
        ("machine7 learning7 model7 token7 prompt7 session7", 28),
        ["machine7 learning7 model7", "token7 prompt7 session7"],
    ),
    (
        ("learning7 model7 token7 prompt7 session7 library7", 6),
        ["learning7", "model7", "token7", "prompt7", "session7", "library7"],
    ),
    (
        ("learning7 model7 token7 prompt7 session7 library7", 10),
        ["learning7", "model7", "token7", "prompt7", "session7", "library7"],
    ),
    (
        ("learning7 model7 token7 prompt7 session7 library7", 18),
        ["learning7 model7", "token7 prompt7", "session7 library7"],
    ),
    (
        ("learning7 model7 token7 prompt7 session7 library7", 28),
        ["learning7 model7 token7", "prompt7 session7 library7"],
    ),
    (
        ("model7 token7 prompt7 session7 library7 service7", 6),
        ["model7", "token7", "prompt7", "session7", "library7", "service7"],
    ),
    (
        ("model7 token7 prompt7 session7 library7 service7", 10),
        ["model7", "token7", "prompt7", "session7", "library7", "service7"],
    ),
    (
        ("model7 token7 prompt7 session7 library7 service7", 18),
        ["model7 token7", "prompt7 session7", "library7 service7"],
    ),
    (("model7 token7 prompt7 session7 library7 service7", 28), ["model7 token7 prompt7", "session7 library7 service7"]),
    (
        ("token7 prompt7 session7 library7 service7 gateway7", 6),
        ["token7", "prompt7", "session7", "library7", "service7", "gateway7"],
    ),
    (
        ("token7 prompt7 session7 library7 service7 gateway7", 10),
        ["token7", "prompt7", "session7", "library7", "service7", "gateway7"],
    ),
    (
        ("token7 prompt7 session7 library7 service7 gateway7", 18),
        ["token7 prompt7", "session7 library7", "service7 gateway7"],
    ),
    (
        ("token7 prompt7 session7 library7 service7 gateway7", 28),
        ["token7 prompt7 session7", "library7 service7 gateway7"],
    ),
    (
        ("prompt7 session7 library7 service7 gateway7 storage7", 6),
        ["prompt7", "session7", "library7", "service7", "gateway7", "storage7"],
    ),
    (
        ("prompt7 session7 library7 service7 gateway7 storage7", 10),
        ["prompt7", "session7", "library7", "service7", "gateway7", "storage7"],
    ),
    (
        ("prompt7 session7 library7 service7 gateway7 storage7", 18),
        ["prompt7 session7", "library7 service7", "gateway7 storage7"],
    ),
    (
        ("prompt7 session7 library7 service7 gateway7 storage7", 28),
        ["prompt7 session7 library7", "service7 gateway7 storage7"],
    ),
    (
        ("session7 library7 service7 gateway7 storage7 network7", 6),
        ["session7", "library7", "service7", "gateway7", "storage7", "network7"],
    ),
    (
        ("session7 library7 service7 gateway7 storage7 network7", 10),
        ["session7", "library7", "service7", "gateway7", "storage7", "network7"],
    ),
    (
        ("session7 library7 service7 gateway7 storage7 network7", 18),
        ["session7 library7", "service7 gateway7", "storage7 network7"],
    ),
    (
        ("session7 library7 service7 gateway7 storage7 network7", 28),
        ["session7 library7 service7", "gateway7 storage7 network7"],
    ),
    (
        ("library7 service7 gateway7 storage7 network7 latency7", 6),
        ["library7", "service7", "gateway7", "storage7", "network7", "latency7"],
    ),
    (
        ("library7 service7 gateway7 storage7 network7 latency7", 10),
        ["library7", "service7", "gateway7", "storage7", "network7", "latency7"],
    ),
    (
        ("library7 service7 gateway7 storage7 network7 latency7", 18),
        ["library7 service7", "gateway7 storage7", "network7 latency7"],
    ),
    (
        ("library7 service7 gateway7 storage7 network7 latency7", 28),
        ["library7 service7 gateway7", "storage7 network7 latency7"],
    ),
    (
        ("service7 gateway7 storage7 network7 latency7 buffer7", 6),
        ["service7", "gateway7", "storage7", "network7", "latency7", "buffer7"],
    ),
    (
        ("service7 gateway7 storage7 network7 latency7 buffer7", 10),
        ["service7", "gateway7", "storage7", "network7", "latency7", "buffer7"],
    ),
    (
        ("service7 gateway7 storage7 network7 latency7 buffer7", 18),
        ["service7 gateway7", "storage7 network7", "latency7 buffer7"],
    ),
    (
        ("service7 gateway7 storage7 network7 latency7 buffer7", 28),
        ["service7 gateway7 storage7", "network7 latency7 buffer7"],
    ),
    (
        ("gateway7 storage7 network7 latency7 buffer7 queue7", 6),
        ["gateway7", "storage7", "network7", "latency7", "buffer7", "queue7"],
    ),
    (
        ("gateway7 storage7 network7 latency7 buffer7 queue7", 10),
        ["gateway7", "storage7", "network7", "latency7", "buffer7", "queue7"],
    ),
    (
        ("gateway7 storage7 network7 latency7 buffer7 queue7", 18),
        ["gateway7 storage7", "network7 latency7", "buffer7 queue7"],
    ),
    (
        ("gateway7 storage7 network7 latency7 buffer7 queue7", 28),
        ["gateway7 storage7 network7", "latency7 buffer7 queue7"],
    ),
    (
        ("storage7 network7 latency7 buffer7 queue7 worker7", 6),
        ["storage7", "network7", "latency7", "buffer7", "queue7", "worker7"],
    ),
    (
        ("storage7 network7 latency7 buffer7 queue7 worker7", 10),
        ["storage7", "network7", "latency7", "buffer7", "queue7", "worker7"],
    ),
    (
        ("storage7 network7 latency7 buffer7 queue7 worker7", 18),
        ["storage7 network7", "latency7 buffer7", "queue7 worker7"],
    ),
    (
        ("storage7 network7 latency7 buffer7 queue7 worker7", 28),
        ["storage7 network7 latency7", "buffer7 queue7 worker7"],
    ),
    (
        ("network7 latency7 buffer7 queue7 worker7 kernel7", 6),
        ["network7", "latency7", "buffer7", "queue7", "worker7", "kernel7"],
    ),
    (
        ("network7 latency7 buffer7 queue7 worker7 kernel7", 10),
        ["network7", "latency7", "buffer7", "queue7", "worker7", "kernel7"],
    ),
    (
        ("network7 latency7 buffer7 queue7 worker7 kernel7", 18),
        ["network7 latency7", "buffer7 queue7", "worker7 kernel7"],
    ),
    (("network7 latency7 buffer7 queue7 worker7 kernel7", 28), ["network7 latency7 buffer7", "queue7 worker7 kernel7"]),
    (
        ("latency7 buffer7 queue7 worker7 kernel7 signal7", 6),
        ["latency7", "buffer7", "queue7", "worker7", "kernel7", "signal7"],
    ),
    (
        ("latency7 buffer7 queue7 worker7 kernel7 signal7", 10),
        ["latency7", "buffer7", "queue7", "worker7", "kernel7", "signal7"],
    ),
    (
        ("latency7 buffer7 queue7 worker7 kernel7 signal7", 18),
        ["latency7 buffer7", "queue7 worker7", "kernel7 signal7"],
    ),
    (("latency7 buffer7 queue7 worker7 kernel7 signal7", 28), ["latency7 buffer7 queue7", "worker7 kernel7 signal7"]),
    (
        ("buffer7 queue7 worker7 kernel7 signal7 packet7", 6),
        ["buffer7", "queue7", "worker7", "kernel7", "signal7", "packet7"],
    ),
    (
        ("buffer7 queue7 worker7 kernel7 signal7 packet7", 10),
        ["buffer7", "queue7", "worker7", "kernel7", "signal7", "packet7"],
    ),
    (("buffer7 queue7 worker7 kernel7 signal7 packet7", 18), ["buffer7 queue7", "worker7 kernel7", "signal7 packet7"]),
    (("buffer7 queue7 worker7 kernel7 signal7 packet7", 28), ["buffer7 queue7 worker7", "kernel7 signal7 packet7"]),
    (
        ("queue7 worker7 kernel7 signal7 packet7 router7", 6),
        ["queue7", "worker7", "kernel7", "signal7", "packet7", "router7"],
    ),
    (
        ("queue7 worker7 kernel7 signal7 packet7 router7", 10),
        ["queue7", "worker7", "kernel7", "signal7", "packet7", "router7"],
    ),
    (("queue7 worker7 kernel7 signal7 packet7 router7", 18), ["queue7 worker7", "kernel7 signal7", "packet7 router7"]),
    (("queue7 worker7 kernel7 signal7 packet7 router7", 28), ["queue7 worker7 kernel7", "signal7 packet7 router7"]),
    (
        ("worker7 kernel7 signal7 packet7 router7 cluster7", 6),
        ["worker7", "kernel7", "signal7", "packet7", "router7", "cluster7"],
    ),
    (
        ("worker7 kernel7 signal7 packet7 router7 cluster7", 10),
        ["worker7", "kernel7", "signal7", "packet7", "router7", "cluster7"],
    ),
    (
        ("worker7 kernel7 signal7 packet7 router7 cluster7", 18),
        ["worker7 kernel7", "signal7 packet7", "router7 cluster7"],
    ),
    (("worker7 kernel7 signal7 packet7 router7 cluster7", 28), ["worker7 kernel7 signal7", "packet7 router7 cluster7"]),
    (
        ("kernel7 signal7 packet7 router7 cluster7 mirror7", 6),
        ["kernel7", "signal7", "packet7", "router7", "cluster7", "mirror7"],
    ),
    (
        ("kernel7 signal7 packet7 router7 cluster7 mirror7", 10),
        ["kernel7", "signal7", "packet7", "router7", "cluster7", "mirror7"],
    ),
    (
        ("kernel7 signal7 packet7 router7 cluster7 mirror7", 18),
        ["kernel7 signal7", "packet7 router7", "cluster7 mirror7"],
    ),
    (("kernel7 signal7 packet7 router7 cluster7 mirror7", 28), ["kernel7 signal7 packet7", "router7 cluster7 mirror7"]),
    (
        ("signal7 packet7 router7 cluster7 mirror7 filter7", 6),
        ["signal7", "packet7", "router7", "cluster7", "mirror7", "filter7"],
    ),
    (
        ("signal7 packet7 router7 cluster7 mirror7 filter7", 10),
        ["signal7", "packet7", "router7", "cluster7", "mirror7", "filter7"],
    ),
    (
        ("signal7 packet7 router7 cluster7 mirror7 filter7", 18),
        ["signal7 packet7", "router7 cluster7", "mirror7 filter7"],
    ),
    (("signal7 packet7 router7 cluster7 mirror7 filter7", 28), ["signal7 packet7 router7", "cluster7 mirror7 filter7"]),
    (
        ("packet7 router7 cluster7 mirror7 filter7 ranking7", 6),
        ["packet7", "router7", "cluster7", "mirror7", "filter7", "ranking7"],
    ),
    (
        ("packet7 router7 cluster7 mirror7 filter7 ranking7", 10),
        ["packet7", "router7", "cluster7", "mirror7", "filter7", "ranking7"],
    ),
    (
        ("packet7 router7 cluster7 mirror7 filter7 ranking7", 18),
        ["packet7 router7", "cluster7 mirror7", "filter7 ranking7"],
    ),
    (
        ("packet7 router7 cluster7 mirror7 filter7 ranking7", 28),
        ["packet7 router7 cluster7", "mirror7 filter7 ranking7"],
    ),
    (
        ("router7 cluster7 mirror7 filter7 ranking7 encoding7", 6),
        ["router7", "cluster7", "mirror7", "filter7", "ranking7", "encoding7"],
    ),
    (
        ("router7 cluster7 mirror7 filter7 ranking7 encoding7", 10),
        ["router7", "cluster7", "mirror7", "filter7", "ranking7", "encoding7"],
    ),
    (
        ("router7 cluster7 mirror7 filter7 ranking7 encoding7", 18),
        ["router7 cluster7", "mirror7 filter7", "ranking7 encoding7"],
    ),
    (
        ("router7 cluster7 mirror7 filter7 ranking7 encoding7", 28),
        ["router7 cluster7 mirror7", "filter7 ranking7 encoding7"],
    ),
    (
        ("cluster7 mirror7 filter7 ranking7 encoding7 mapping7", 6),
        ["cluster7", "mirror7", "filter7", "ranking7", "encoding7", "mapping7"],
    ),
    (
        ("cluster7 mirror7 filter7 ranking7 encoding7 mapping7", 10),
        ["cluster7", "mirror7", "filter7", "ranking7", "encoding7", "mapping7"],
    ),
    (
        ("cluster7 mirror7 filter7 ranking7 encoding7 mapping7", 18),
        ["cluster7 mirror7", "filter7 ranking7", "encoding7 mapping7"],
    ),
    (
        ("cluster7 mirror7 filter7 ranking7 encoding7 mapping7", 28),
        ["cluster7 mirror7 filter7", "ranking7 encoding7 mapping7"],
    ),
    (
        ("mirror7 filter7 ranking7 encoding7 mapping7 record7", 6),
        ["mirror7", "filter7", "ranking7", "encoding7", "mapping7", "record7"],
    ),
    (
        ("mirror7 filter7 ranking7 encoding7 mapping7 record7", 10),
        ["mirror7", "filter7", "ranking7", "encoding7", "mapping7", "record7"],
    ),
    (
        ("mirror7 filter7 ranking7 encoding7 mapping7 record7", 18),
        ["mirror7 filter7", "ranking7 encoding7", "mapping7 record7"],
    ),
    (
        ("mirror7 filter7 ranking7 encoding7 mapping7 record7", 28),
        ["mirror7 filter7 ranking7", "encoding7 mapping7 record7"],
    ),
    (
        ("filter7 ranking7 encoding7 mapping7 record7 candle7", 6),
        ["filter7", "ranking7", "encoding7", "mapping7", "record7", "candle7"],
    ),
    (
        ("filter7 ranking7 encoding7 mapping7 record7 candle7", 10),
        ["filter7", "ranking7", "encoding7", "mapping7", "record7", "candle7"],
    ),
    (
        ("filter7 ranking7 encoding7 mapping7 record7 candle7", 18),
        ["filter7 ranking7", "encoding7 mapping7", "record7 candle7"],
    ),
    (
        ("filter7 ranking7 encoding7 mapping7 record7 candle7", 28),
        ["filter7 ranking7 encoding7", "mapping7 record7 candle7"],
    ),
    (
        ("ranking7 encoding7 mapping7 record7 candle7 thread7", 6),
        ["ranking7", "encoding7", "mapping7", "record7", "candle7", "thread7"],
    ),
    (
        ("ranking7 encoding7 mapping7 record7 candle7 thread7", 10),
        ["ranking7", "encoding7", "mapping7", "record7", "candle7", "thread7"],
    ),
    (
        ("ranking7 encoding7 mapping7 record7 candle7 thread7", 18),
        ["ranking7 encoding7", "mapping7 record7", "candle7 thread7"],
    ),
    (
        ("ranking7 encoding7 mapping7 record7 candle7 thread7", 28),
        ["ranking7 encoding7 mapping7", "record7 candle7 thread7"],
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
