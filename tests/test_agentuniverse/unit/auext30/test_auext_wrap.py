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
        ("round 30: the quick brown fox jumps over the lazy dog", 4),
        ["round", "30:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 30: the quick brown fox jumps over the lazy dog", 8),
        ["round", "30: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 30: the quick brown fox jumps over the lazy dog", 12),
        ["round 30:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 30: the quick brown fox jumps over the lazy dog", 16),
        ["round 30: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 30: the quick brown fox jumps over the lazy dog", 24),
        ["round 30: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 30: the quick brown fox jumps over the lazy dog", 32),
        ["round 30: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 30: agentuniverse is a framework for multi agents", 4),
        ["round", "30:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 30: agentuniverse is a framework for multi agents", 8),
        ["round", "30:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 30: agentuniverse is a framework for multi agents", 12),
        ["round 30:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 30: agentuniverse is a framework for multi agents", 16),
        ["round 30:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 30: agentuniverse is a framework for multi agents", 24),
        ["round 30: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 30: agentuniverse is a framework for multi agents", 32),
        ["round 30: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 30: knowledge stored as vectors enables retrieval", 4),
        ["round", "30:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 30: knowledge stored as vectors enables retrieval", 8),
        ["round", "30:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 30: knowledge stored as vectors enables retrieval", 12),
        ["round 30:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 30: knowledge stored as vectors enables retrieval", 16),
        ["round 30:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 30: knowledge stored as vectors enables retrieval", 24),
        ["round 30: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 30: knowledge stored as vectors enables retrieval", 32),
        ["round 30: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 30: the processor reads the record then stops", 4),
        ["round", "30:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 30: the processor reads the record then stops", 8),
        ["round", "30: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 30: the processor reads the record then stops", 12),
        ["round 30:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 30: the processor reads the record then stops", 16),
        ["round 30: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 30: the processor reads the record then stops", 24),
        ["round 30: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 30: the processor reads the record then stops", 32),
        ["round 30: the processor reads", "the record then stops"],
    ),
    (
        ("round 30: a worker pulls the next task from the queue", 4),
        ["round", "30:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 30: a worker pulls the next task from the queue", 8),
        ["round", "30: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 30: a worker pulls the next task from the queue", 12),
        ["round 30: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 30: a worker pulls the next task from the queue", 16),
        ["round 30: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 30: a worker pulls the next task from the queue", 24),
        ["round 30: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 30: a worker pulls the next task from the queue", 32),
        ["round 30: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 30: signals travel through the network layer", 4),
        ["round", "30:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 30: signals travel through the network layer", 8),
        ["round", "30:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 30: signals travel through the network layer", 12),
        ["round 30:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 30: signals travel through the network layer", 16),
        ["round 30:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 30: signals travel through the network layer", 24),
        ["round 30: signals travel", "through the network", "layer"],
    ),
    (
        ("round 30: signals travel through the network layer", 32),
        ["round 30: signals travel through", "the network layer"],
    ),
    (
        ("round 30: the gateway routes each request by policy", 4),
        ["round", "30:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 30: the gateway routes each request by policy", 8),
        ["round", "30: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 30: the gateway routes each request by policy", 12),
        ["round 30:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 30: the gateway routes each request by policy", 16),
        ["round 30: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 30: the gateway routes each request by policy", 24),
        ["round 30: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 30: the gateway routes each request by policy", 32),
        ["round 30: the gateway routes", "each request by policy"],
    ),
    (
        ("round 30: memory grows until the buffer is full", 4),
        ["round", "30:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 30: memory grows until the buffer is full", 8),
        ["round", "30:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 30: memory grows until the buffer is full", 12),
        ["round 30:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 30: memory grows until the buffer is full", 16),
        ["round 30: memory", "grows until the", "buffer is full"],
    ),
    (("round 30: memory grows until the buffer is full", 24), ["round 30: memory grows", "until the buffer is full"]),
    (("round 30: memory grows until the buffer is full", 32), ["round 30: memory grows until the", "buffer is full"]),
    (
        ("round 30: the cluster mirrors every packet twice", 4),
        ["round", "30:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 30: the cluster mirrors every packet twice", 8),
        ["round", "30: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 30: the cluster mirrors every packet twice", 12),
        ["round 30:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 30: the cluster mirrors every packet twice", 16),
        ["round 30: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 30: the cluster mirrors every packet twice", 24),
        ["round 30: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 30: the cluster mirrors every packet twice", 32), ["round 30: the cluster mirrors", "every packet twice"]),
    (
        ("round 30: ranking uses tokens learned from the corpus", 4),
        ["round", "30:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 30: ranking uses tokens learned from the corpus", 8),
        ["round", "30:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 30: ranking uses tokens learned from the corpus", 12),
        ["round 30:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 30: ranking uses tokens learned from the corpus", 16),
        ["round 30:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 30: ranking uses tokens learned from the corpus", 24),
        ["round 30: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 30: ranking uses tokens learned from the corpus", 32),
        ["round 30: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 30: a long session ends when the candle dies", 4),
        ["round", "30:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 30: a long session ends when the candle dies", 8),
        ["round", "30: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 30: a long session ends when the candle dies", 12),
        ["round 30: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 30: a long session ends when the candle dies", 16),
        ["round 30: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 30: a long session ends when the candle dies", 24),
        ["round 30: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 30: a long session ends when the candle dies", 32),
        ["round 30: a long session ends", "when the candle dies"],
    ),
    (
        ("round 30: encode the prompt then map the result", 4),
        ["round", "30:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 30: encode the prompt then map the result", 8),
        ["round", "30:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 30: encode the prompt then map the result", 12),
        ["round 30:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 30: encode the prompt then map the result", 16),
        ["round 30: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 30: encode the prompt then map the result", 24),
        ["round 30: encode the", "prompt then map the", "result"],
    ),
    (("round 30: encode the prompt then map the result", 32), ["round 30: encode the prompt then", "map the result"]),
    (
        ("round 30: the kernel wakes the worker at dawn", 4),
        ["round", "30:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 30: the kernel wakes the worker at dawn", 8),
        ["round", "30: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 30: the kernel wakes the worker at dawn", 12),
        ["round 30:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 30: the kernel wakes the worker at dawn", 16), ["round 30: the", "kernel wakes the", "worker at dawn"]),
    (("round 30: the kernel wakes the worker at dawn", 24), ["round 30: the kernel", "wakes the worker at dawn"]),
    (("round 30: the kernel wakes the worker at dawn", 32), ["round 30: the kernel wakes the", "worker at dawn"]),
    (
        ("round 30: service latency drops after the patch", 4),
        ["round", "30:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 30: service latency drops after the patch", 8),
        ["round", "30:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 30: service latency drops after the patch", 12),
        ["round 30:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 30: service latency drops after the patch", 16),
        ["round 30:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 30: service latency drops after the patch", 24),
        ["round 30: service", "latency drops after the", "patch"],
    ),
    (("round 30: service latency drops after the patch", 32), ["round 30: service latency drops", "after the patch"]),
    (
        ("round 30: the library caches every vector it sees", 4),
        ["round", "30:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 30: the library caches every vector it sees", 8),
        ["round", "30: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 30: the library caches every vector it sees", 12),
        ["round 30:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 30: the library caches every vector it sees", 16),
        ["round 30: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 30: the library caches every vector it sees", 24),
        ["round 30: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 30: the library caches every vector it sees", 32),
        ["round 30: the library caches", "every vector it sees"],
    ),
    (
        ("round 30: agents argue then the debate resolves", 4),
        ["round", "30:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 30: agents argue then the debate resolves", 8),
        ["round", "30:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 30: agents argue then the debate resolves", 12),
        ["round 30:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 30: agents argue then the debate resolves", 16),
        ["round 30: agents", "argue then the", "debate resolves"],
    ),
    (("round 30: agents argue then the debate resolves", 24), ["round 30: agents argue", "then the debate resolves"]),
    (("round 30: agents argue then the debate resolves", 32), ["round 30: agents argue then the", "debate resolves"]),
    (
        ("round 30: the filter keeps only strong matches", 4),
        ["round", "30:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 30: the filter keeps only strong matches", 8),
        ["round", "30: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 30: the filter keeps only strong matches", 12),
        ["round 30:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 30: the filter keeps only strong matches", 16),
        ["round 30: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 30: the filter keeps only strong matches", 24), ["round 30: the filter", "keeps only strong", "matches"]),
    (("round 30: the filter keeps only strong matches", 32), ["round 30: the filter keeps only", "strong matches"]),
    (
        ("round 30: the model answers with a short reply", 4),
        ["round", "30:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 30: the model answers with a short reply", 8),
        ["round", "30: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 30: the model answers with a short reply", 12),
        ["round 30:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 30: the model answers with a short reply", 16),
        ["round 30: the", "model answers", "with a short", "reply"],
    ),
    (("round 30: the model answers with a short reply", 24), ["round 30: the model", "answers with a short", "reply"]),
    (("round 30: the model answers with a short reply", 32), ["round 30: the model answers with", "a short reply"]),
    (
        ("round 30: the recorder stores the reasoning trace", 4),
        ["round", "30:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 30: the recorder stores the reasoning trace", 8),
        ["round", "30: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 30: the recorder stores the reasoning trace", 12),
        ["round 30:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 30: the recorder stores the reasoning trace", 16),
        ["round 30: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 30: the recorder stores the reasoning trace", 24),
        ["round 30: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 30: the recorder stores the reasoning trace", 32),
        ["round 30: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 30: the angel watches the processor run", 4),
        ["round", "30:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 30: the angel watches the processor run", 8),
        ["round", "30: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 30: the angel watches the processor run", 12),
        ["round 30:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 30: the angel watches the processor run", 16), ["round 30: the", "angel watches", "the processor", "run"]),
    (("round 30: the angel watches the processor run", 24), ["round 30: the angel", "watches the processor", "run"]),
    (("round 30: the angel watches the processor run", 32), ["round 30: the angel watches the", "processor run"]),
    (
        ("round 30: angle of the vector decides the match", 4),
        ["round", "30:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 30: angle of the vector decides the match", 8),
        ["round", "30:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 30: angle of the vector decides the match", 12),
        ["round 30:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 30: angle of the vector decides the match", 16),
        ["round 30: angle", "of the vector", "decides the", "match"],
    ),
    (("round 30: angle of the vector decides the match", 24), ["round 30: angle of the", "vector decides the match"]),
    (("round 30: angle of the vector decides the match", 32), ["round 30: angle of the vector", "decides the match"]),
    (
        ("round 30: the candle burns twice as long at night", 4),
        ["round", "30:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 30: the candle burns twice as long at night", 8),
        ["round", "30: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 30: the candle burns twice as long at night", 12),
        ["round 30:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 30: the candle burns twice as long at night", 16),
        ["round 30: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 30: the candle burns twice as long at night", 24),
        ["round 30: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 30: the candle burns twice as long at night", 32),
        ["round 30: the candle burns twice", "as long at night"],
    ),
    (
        ("round 30: a mirror of the universe in one line", 4),
        ["round", "30:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 30: a mirror of the universe in one line", 8),
        ["round", "30: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 30: a mirror of the universe in one line", 12),
        ["round 30: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 30: a mirror of the universe in one line", 16),
        ["round 30: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 30: a mirror of the universe in one line", 24), ["round 30: a mirror of", "the universe in one line"]),
    (("round 30: a mirror of the universe in one line", 32), ["round 30: a mirror of the", "universe in one line"]),
    (
        ("round 30: the queue drains before the storm", 4),
        ["round", "30:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 30: the queue drains before the storm", 8),
        ["round", "30: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 30: the queue drains before the storm", 12), ["round 30:", "the queue", "drains", "before the", "storm"]),
    (("round 30: the queue drains before the storm", 16), ["round 30: the", "queue drains", "before the storm"]),
    (("round 30: the queue drains before the storm", 24), ["round 30: the queue", "drains before the storm"]),
    (("round 30: the queue drains before the storm", 32), ["round 30: the queue drains", "before the storm"]),
    (
        ("kitten30 sitting30 agent30 angle30 universe30 memory30", 6),
        ["kitten30", "sitting30", "agent30", "angle30", "universe30", "memory30"],
    ),
    (
        ("kitten30 sitting30 agent30 angle30 universe30 memory30", 10),
        ["kitten30", "sitting30", "agent30", "angle30", "universe30", "memory30"],
    ),
    (
        ("kitten30 sitting30 agent30 angle30 universe30 memory30", 18),
        ["kitten30 sitting30", "agent30 angle30", "universe30", "memory30"],
    ),
    (
        ("kitten30 sitting30 agent30 angle30 universe30 memory30", 28),
        ["kitten30 sitting30 agent30", "angle30 universe30 memory30"],
    ),
    (
        ("sitting30 agent30 angle30 universe30 memory30 stream30", 6),
        ["sitting30", "agent30", "angle30", "universe30", "memory30", "stream30"],
    ),
    (
        ("sitting30 agent30 angle30 universe30 memory30 stream30", 10),
        ["sitting30", "agent30", "angle30", "universe30", "memory30", "stream30"],
    ),
    (
        ("sitting30 agent30 angle30 universe30 memory30 stream30", 18),
        ["sitting30 agent30", "angle30 universe30", "memory30 stream30"],
    ),
    (
        ("sitting30 agent30 angle30 universe30 memory30 stream30", 28),
        ["sitting30 agent30 angle30", "universe30 memory30 stream30"],
    ),
    (
        ("agent30 angle30 universe30 memory30 stream30 context30", 6),
        ["agent30", "angle30", "universe30", "memory30", "stream30", "context30"],
    ),
    (
        ("agent30 angle30 universe30 memory30 stream30 context30", 10),
        ["agent30", "angle30", "universe30", "memory30", "stream30", "context30"],
    ),
    (
        ("agent30 angle30 universe30 memory30 stream30 context30", 18),
        ["agent30 angle30", "universe30", "memory30 stream30", "context30"],
    ),
    (
        ("agent30 angle30 universe30 memory30 stream30 context30", 28),
        ["agent30 angle30 universe30", "memory30 stream30 context30"],
    ),
    (
        ("angle30 universe30 memory30 stream30 context30 knowledge30", 6),
        ["angle30", "universe30", "memory30", "stream30", "context30", "knowledge30"],
    ),
    (
        ("angle30 universe30 memory30 stream30 context30 knowledge30", 10),
        ["angle30", "universe30", "memory30", "stream30", "context30", "knowledge30"],
    ),
    (
        ("angle30 universe30 memory30 stream30 context30 knowledge30", 18),
        ["angle30 universe30", "memory30 stream30", "context30", "knowledge30"],
    ),
    (
        ("angle30 universe30 memory30 stream30 context30 knowledge30", 28),
        ["angle30 universe30 memory30", "stream30 context30", "knowledge30"],
    ),
    (
        ("universe30 memory30 stream30 context30 knowledge30 vector30", 6),
        ["universe30", "memory30", "stream30", "context30", "knowledge30", "vector30"],
    ),
    (
        ("universe30 memory30 stream30 context30 knowledge30 vector30", 10),
        ["universe30", "memory30", "stream30", "context30", "knowledge30", "vector30"],
    ),
    (
        ("universe30 memory30 stream30 context30 knowledge30 vector30", 18),
        ["universe30", "memory30 stream30", "context30", "knowledge30", "vector30"],
    ),
    (
        ("universe30 memory30 stream30 context30 knowledge30 vector30", 28),
        ["universe30 memory30 stream30", "context30 knowledge30", "vector30"],
    ),
    (
        ("memory30 stream30 context30 knowledge30 vector30 processor30", 6),
        ["memory30", "stream30", "context30", "knowledge30", "vector30", "processor30"],
    ),
    (
        ("memory30 stream30 context30 knowledge30 vector30 processor30", 10),
        ["memory30", "stream30", "context30", "knowledge30", "vector30", "processor30"],
    ),
    (
        ("memory30 stream30 context30 knowledge30 vector30 processor30", 18),
        ["memory30 stream30", "context30", "knowledge30", "vector30", "processor30"],
    ),
    (
        ("memory30 stream30 context30 knowledge30 vector30 processor30", 28),
        ["memory30 stream30 context30", "knowledge30 vector30", "processor30"],
    ),
    (
        ("stream30 context30 knowledge30 vector30 processor30 reasoning30", 6),
        ["stream30", "context30", "knowledge30", "vector30", "processor30", "reasoning30"],
    ),
    (
        ("stream30 context30 knowledge30 vector30 processor30 reasoning30", 10),
        ["stream30", "context30", "knowledge30", "vector30", "processor30", "reasoning30"],
    ),
    (
        ("stream30 context30 knowledge30 vector30 processor30 reasoning30", 18),
        ["stream30 context30", "knowledge30", "vector30", "processor30", "reasoning30"],
    ),
    (
        ("stream30 context30 knowledge30 vector30 processor30 reasoning30", 28),
        ["stream30 context30", "knowledge30 vector30", "processor30 reasoning30"],
    ),
    (
        ("context30 knowledge30 vector30 processor30 reasoning30 machine30", 6),
        ["context30", "knowledge30", "vector30", "processor30", "reasoning30", "machine30"],
    ),
    (
        ("context30 knowledge30 vector30 processor30 reasoning30 machine30", 10),
        ["context30", "knowledge30", "vector30", "processor30", "reasoning30", "machine30"],
    ),
    (
        ("context30 knowledge30 vector30 processor30 reasoning30 machine30", 18),
        ["context30", "knowledge30", "vector30", "processor30", "reasoning30", "machine30"],
    ),
    (
        ("context30 knowledge30 vector30 processor30 reasoning30 machine30", 28),
        ["context30 knowledge30", "vector30 processor30", "reasoning30 machine30"],
    ),
    (
        ("knowledge30 vector30 processor30 reasoning30 machine30 learning30", 6),
        ["knowledge30", "vector30", "processor30", "reasoning30", "machine30", "learning30"],
    ),
    (
        ("knowledge30 vector30 processor30 reasoning30 machine30 learning30", 10),
        ["knowledge30", "vector30", "processor30", "reasoning30", "machine30", "learning30"],
    ),
    (
        ("knowledge30 vector30 processor30 reasoning30 machine30 learning30", 18),
        ["knowledge30", "vector30", "processor30", "reasoning30", "machine30", "learning30"],
    ),
    (
        ("knowledge30 vector30 processor30 reasoning30 machine30 learning30", 28),
        ["knowledge30 vector30", "processor30 reasoning30", "machine30 learning30"],
    ),
    (
        ("vector30 processor30 reasoning30 machine30 learning30 model30", 6),
        ["vector30", "processor30", "reasoning30", "machine30", "learning30", "model30"],
    ),
    (
        ("vector30 processor30 reasoning30 machine30 learning30 model30", 10),
        ["vector30", "processor30", "reasoning30", "machine30", "learning30", "model30"],
    ),
    (
        ("vector30 processor30 reasoning30 machine30 learning30 model30", 18),
        ["vector30", "processor30", "reasoning30", "machine30", "learning30 model30"],
    ),
    (
        ("vector30 processor30 reasoning30 machine30 learning30 model30", 28),
        ["vector30 processor30", "reasoning30 machine30", "learning30 model30"],
    ),
    (
        ("processor30 reasoning30 machine30 learning30 model30 token30", 6),
        ["processor30", "reasoning30", "machine30", "learning30", "model30", "token30"],
    ),
    (
        ("processor30 reasoning30 machine30 learning30 model30 token30", 10),
        ["processor30", "reasoning30", "machine30", "learning30", "model30", "token30"],
    ),
    (
        ("processor30 reasoning30 machine30 learning30 model30 token30", 18),
        ["processor30", "reasoning30", "machine30", "learning30 model30", "token30"],
    ),
    (
        ("processor30 reasoning30 machine30 learning30 model30 token30", 28),
        ["processor30 reasoning30", "machine30 learning30 model30", "token30"],
    ),
    (
        ("reasoning30 machine30 learning30 model30 token30 prompt30", 6),
        ["reasoning30", "machine30", "learning30", "model30", "token30", "prompt30"],
    ),
    (
        ("reasoning30 machine30 learning30 model30 token30 prompt30", 10),
        ["reasoning30", "machine30", "learning30", "model30", "token30", "prompt30"],
    ),
    (
        ("reasoning30 machine30 learning30 model30 token30 prompt30", 18),
        ["reasoning30", "machine30", "learning30 model30", "token30 prompt30"],
    ),
    (
        ("reasoning30 machine30 learning30 model30 token30 prompt30", 28),
        ["reasoning30 machine30", "learning30 model30 token30", "prompt30"],
    ),
    (
        ("machine30 learning30 model30 token30 prompt30 session30", 6),
        ["machine30", "learning30", "model30", "token30", "prompt30", "session30"],
    ),
    (
        ("machine30 learning30 model30 token30 prompt30 session30", 10),
        ["machine30", "learning30", "model30", "token30", "prompt30", "session30"],
    ),
    (
        ("machine30 learning30 model30 token30 prompt30 session30", 18),
        ["machine30", "learning30 model30", "token30 prompt30", "session30"],
    ),
    (
        ("machine30 learning30 model30 token30 prompt30 session30", 28),
        ["machine30 learning30 model30", "token30 prompt30 session30"],
    ),
    (
        ("learning30 model30 token30 prompt30 session30 library30", 6),
        ["learning30", "model30", "token30", "prompt30", "session30", "library30"],
    ),
    (
        ("learning30 model30 token30 prompt30 session30 library30", 10),
        ["learning30", "model30", "token30", "prompt30", "session30", "library30"],
    ),
    (
        ("learning30 model30 token30 prompt30 session30 library30", 18),
        ["learning30 model30", "token30 prompt30", "session30", "library30"],
    ),
    (
        ("learning30 model30 token30 prompt30 session30 library30", 28),
        ["learning30 model30 token30", "prompt30 session30 library30"],
    ),
    (
        ("model30 token30 prompt30 session30 library30 service30", 6),
        ["model30", "token30", "prompt30", "session30", "library30", "service30"],
    ),
    (
        ("model30 token30 prompt30 session30 library30 service30", 10),
        ["model30", "token30", "prompt30", "session30", "library30", "service30"],
    ),
    (
        ("model30 token30 prompt30 session30 library30 service30", 18),
        ["model30 token30", "prompt30 session30", "library30", "service30"],
    ),
    (
        ("model30 token30 prompt30 session30 library30 service30", 28),
        ["model30 token30 prompt30", "session30 library30", "service30"],
    ),
    (
        ("token30 prompt30 session30 library30 service30 gateway30", 6),
        ["token30", "prompt30", "session30", "library30", "service30", "gateway30"],
    ),
    (
        ("token30 prompt30 session30 library30 service30 gateway30", 10),
        ["token30", "prompt30", "session30", "library30", "service30", "gateway30"],
    ),
    (
        ("token30 prompt30 session30 library30 service30 gateway30", 18),
        ["token30 prompt30", "session30", "library30", "service30", "gateway30"],
    ),
    (
        ("token30 prompt30 session30 library30 service30 gateway30", 28),
        ["token30 prompt30 session30", "library30 service30", "gateway30"],
    ),
    (
        ("prompt30 session30 library30 service30 gateway30 storage30", 6),
        ["prompt30", "session30", "library30", "service30", "gateway30", "storage30"],
    ),
    (
        ("prompt30 session30 library30 service30 gateway30 storage30", 10),
        ["prompt30", "session30", "library30", "service30", "gateway30", "storage30"],
    ),
    (
        ("prompt30 session30 library30 service30 gateway30 storage30", 18),
        ["prompt30 session30", "library30", "service30", "gateway30", "storage30"],
    ),
    (
        ("prompt30 session30 library30 service30 gateway30 storage30", 28),
        ["prompt30 session30 library30", "service30 gateway30", "storage30"],
    ),
    (
        ("session30 library30 service30 gateway30 storage30 network30", 6),
        ["session30", "library30", "service30", "gateway30", "storage30", "network30"],
    ),
    (
        ("session30 library30 service30 gateway30 storage30 network30", 10),
        ["session30", "library30", "service30", "gateway30", "storage30", "network30"],
    ),
    (
        ("session30 library30 service30 gateway30 storage30 network30", 18),
        ["session30", "library30", "service30", "gateway30", "storage30", "network30"],
    ),
    (
        ("session30 library30 service30 gateway30 storage30 network30", 28),
        ["session30 library30", "service30 gateway30", "storage30 network30"],
    ),
    (
        ("library30 service30 gateway30 storage30 network30 latency30", 6),
        ["library30", "service30", "gateway30", "storage30", "network30", "latency30"],
    ),
    (
        ("library30 service30 gateway30 storage30 network30 latency30", 10),
        ["library30", "service30", "gateway30", "storage30", "network30", "latency30"],
    ),
    (
        ("library30 service30 gateway30 storage30 network30 latency30", 18),
        ["library30", "service30", "gateway30", "storage30", "network30", "latency30"],
    ),
    (
        ("library30 service30 gateway30 storage30 network30 latency30", 28),
        ["library30 service30", "gateway30 storage30", "network30 latency30"],
    ),
    (
        ("service30 gateway30 storage30 network30 latency30 buffer30", 6),
        ["service30", "gateway30", "storage30", "network30", "latency30", "buffer30"],
    ),
    (
        ("service30 gateway30 storage30 network30 latency30 buffer30", 10),
        ["service30", "gateway30", "storage30", "network30", "latency30", "buffer30"],
    ),
    (
        ("service30 gateway30 storage30 network30 latency30 buffer30", 18),
        ["service30", "gateway30", "storage30", "network30", "latency30 buffer30"],
    ),
    (
        ("service30 gateway30 storage30 network30 latency30 buffer30", 28),
        ["service30 gateway30", "storage30 network30", "latency30 buffer30"],
    ),
    (
        ("gateway30 storage30 network30 latency30 buffer30 queue30", 6),
        ["gateway30", "storage30", "network30", "latency30", "buffer30", "queue30"],
    ),
    (
        ("gateway30 storage30 network30 latency30 buffer30 queue30", 10),
        ["gateway30", "storage30", "network30", "latency30", "buffer30", "queue30"],
    ),
    (
        ("gateway30 storage30 network30 latency30 buffer30 queue30", 18),
        ["gateway30", "storage30", "network30", "latency30 buffer30", "queue30"],
    ),
    (
        ("gateway30 storage30 network30 latency30 buffer30 queue30", 28),
        ["gateway30 storage30", "network30 latency30 buffer30", "queue30"],
    ),
    (
        ("storage30 network30 latency30 buffer30 queue30 worker30", 6),
        ["storage30", "network30", "latency30", "buffer30", "queue30", "worker30"],
    ),
    (
        ("storage30 network30 latency30 buffer30 queue30 worker30", 10),
        ["storage30", "network30", "latency30", "buffer30", "queue30", "worker30"],
    ),
    (
        ("storage30 network30 latency30 buffer30 queue30 worker30", 18),
        ["storage30", "network30", "latency30 buffer30", "queue30 worker30"],
    ),
    (
        ("storage30 network30 latency30 buffer30 queue30 worker30", 28),
        ["storage30 network30", "latency30 buffer30 queue30", "worker30"],
    ),
    (
        ("network30 latency30 buffer30 queue30 worker30 kernel30", 6),
        ["network30", "latency30", "buffer30", "queue30", "worker30", "kernel30"],
    ),
    (
        ("network30 latency30 buffer30 queue30 worker30 kernel30", 10),
        ["network30", "latency30", "buffer30", "queue30", "worker30", "kernel30"],
    ),
    (
        ("network30 latency30 buffer30 queue30 worker30 kernel30", 18),
        ["network30", "latency30 buffer30", "queue30 worker30", "kernel30"],
    ),
    (
        ("network30 latency30 buffer30 queue30 worker30 kernel30", 28),
        ["network30 latency30 buffer30", "queue30 worker30 kernel30"],
    ),
    (
        ("latency30 buffer30 queue30 worker30 kernel30 signal30", 6),
        ["latency30", "buffer30", "queue30", "worker30", "kernel30", "signal30"],
    ),
    (
        ("latency30 buffer30 queue30 worker30 kernel30 signal30", 10),
        ["latency30", "buffer30", "queue30", "worker30", "kernel30", "signal30"],
    ),
    (
        ("latency30 buffer30 queue30 worker30 kernel30 signal30", 18),
        ["latency30 buffer30", "queue30 worker30", "kernel30 signal30"],
    ),
    (
        ("latency30 buffer30 queue30 worker30 kernel30 signal30", 28),
        ["latency30 buffer30 queue30", "worker30 kernel30 signal30"],
    ),
    (
        ("buffer30 queue30 worker30 kernel30 signal30 packet30", 6),
        ["buffer30", "queue30", "worker30", "kernel30", "signal30", "packet30"],
    ),
    (
        ("buffer30 queue30 worker30 kernel30 signal30 packet30", 10),
        ["buffer30", "queue30", "worker30", "kernel30", "signal30", "packet30"],
    ),
    (
        ("buffer30 queue30 worker30 kernel30 signal30 packet30", 18),
        ["buffer30 queue30", "worker30 kernel30", "signal30 packet30"],
    ),
    (
        ("buffer30 queue30 worker30 kernel30 signal30 packet30", 28),
        ["buffer30 queue30 worker30", "kernel30 signal30 packet30"],
    ),
    (
        ("queue30 worker30 kernel30 signal30 packet30 router30", 6),
        ["queue30", "worker30", "kernel30", "signal30", "packet30", "router30"],
    ),
    (
        ("queue30 worker30 kernel30 signal30 packet30 router30", 10),
        ["queue30", "worker30", "kernel30", "signal30", "packet30", "router30"],
    ),
    (
        ("queue30 worker30 kernel30 signal30 packet30 router30", 18),
        ["queue30 worker30", "kernel30 signal30", "packet30 router30"],
    ),
    (
        ("queue30 worker30 kernel30 signal30 packet30 router30", 28),
        ["queue30 worker30 kernel30", "signal30 packet30 router30"],
    ),
    (
        ("worker30 kernel30 signal30 packet30 router30 cluster30", 6),
        ["worker30", "kernel30", "signal30", "packet30", "router30", "cluster30"],
    ),
    (
        ("worker30 kernel30 signal30 packet30 router30 cluster30", 10),
        ["worker30", "kernel30", "signal30", "packet30", "router30", "cluster30"],
    ),
    (
        ("worker30 kernel30 signal30 packet30 router30 cluster30", 18),
        ["worker30 kernel30", "signal30 packet30", "router30 cluster30"],
    ),
    (
        ("worker30 kernel30 signal30 packet30 router30 cluster30", 28),
        ["worker30 kernel30 signal30", "packet30 router30 cluster30"],
    ),
    (
        ("kernel30 signal30 packet30 router30 cluster30 mirror30", 6),
        ["kernel30", "signal30", "packet30", "router30", "cluster30", "mirror30"],
    ),
    (
        ("kernel30 signal30 packet30 router30 cluster30 mirror30", 10),
        ["kernel30", "signal30", "packet30", "router30", "cluster30", "mirror30"],
    ),
    (
        ("kernel30 signal30 packet30 router30 cluster30 mirror30", 18),
        ["kernel30 signal30", "packet30 router30", "cluster30 mirror30"],
    ),
    (
        ("kernel30 signal30 packet30 router30 cluster30 mirror30", 28),
        ["kernel30 signal30 packet30", "router30 cluster30 mirror30"],
    ),
    (
        ("signal30 packet30 router30 cluster30 mirror30 filter30", 6),
        ["signal30", "packet30", "router30", "cluster30", "mirror30", "filter30"],
    ),
    (
        ("signal30 packet30 router30 cluster30 mirror30 filter30", 10),
        ["signal30", "packet30", "router30", "cluster30", "mirror30", "filter30"],
    ),
    (
        ("signal30 packet30 router30 cluster30 mirror30 filter30", 18),
        ["signal30 packet30", "router30 cluster30", "mirror30 filter30"],
    ),
    (
        ("signal30 packet30 router30 cluster30 mirror30 filter30", 28),
        ["signal30 packet30 router30", "cluster30 mirror30 filter30"],
    ),
    (
        ("packet30 router30 cluster30 mirror30 filter30 ranking30", 6),
        ["packet30", "router30", "cluster30", "mirror30", "filter30", "ranking30"],
    ),
    (
        ("packet30 router30 cluster30 mirror30 filter30 ranking30", 10),
        ["packet30", "router30", "cluster30", "mirror30", "filter30", "ranking30"],
    ),
    (
        ("packet30 router30 cluster30 mirror30 filter30 ranking30", 18),
        ["packet30 router30", "cluster30 mirror30", "filter30 ranking30"],
    ),
    (
        ("packet30 router30 cluster30 mirror30 filter30 ranking30", 28),
        ["packet30 router30 cluster30", "mirror30 filter30 ranking30"],
    ),
    (
        ("router30 cluster30 mirror30 filter30 ranking30 encoding30", 6),
        ["router30", "cluster30", "mirror30", "filter30", "ranking30", "encoding30"],
    ),
    (
        ("router30 cluster30 mirror30 filter30 ranking30 encoding30", 10),
        ["router30", "cluster30", "mirror30", "filter30", "ranking30", "encoding30"],
    ),
    (
        ("router30 cluster30 mirror30 filter30 ranking30 encoding30", 18),
        ["router30 cluster30", "mirror30 filter30", "ranking30", "encoding30"],
    ),
    (
        ("router30 cluster30 mirror30 filter30 ranking30 encoding30", 28),
        ["router30 cluster30 mirror30", "filter30 ranking30", "encoding30"],
    ),
    (
        ("cluster30 mirror30 filter30 ranking30 encoding30 mapping30", 6),
        ["cluster30", "mirror30", "filter30", "ranking30", "encoding30", "mapping30"],
    ),
    (
        ("cluster30 mirror30 filter30 ranking30 encoding30 mapping30", 10),
        ["cluster30", "mirror30", "filter30", "ranking30", "encoding30", "mapping30"],
    ),
    (
        ("cluster30 mirror30 filter30 ranking30 encoding30 mapping30", 18),
        ["cluster30 mirror30", "filter30 ranking30", "encoding30", "mapping30"],
    ),
    (
        ("cluster30 mirror30 filter30 ranking30 encoding30 mapping30", 28),
        ["cluster30 mirror30 filter30", "ranking30 encoding30", "mapping30"],
    ),
    (
        ("mirror30 filter30 ranking30 encoding30 mapping30 record30", 6),
        ["mirror30", "filter30", "ranking30", "encoding30", "mapping30", "record30"],
    ),
    (
        ("mirror30 filter30 ranking30 encoding30 mapping30 record30", 10),
        ["mirror30", "filter30", "ranking30", "encoding30", "mapping30", "record30"],
    ),
    (
        ("mirror30 filter30 ranking30 encoding30 mapping30 record30", 18),
        ["mirror30 filter30", "ranking30", "encoding30", "mapping30 record30"],
    ),
    (
        ("mirror30 filter30 ranking30 encoding30 mapping30 record30", 28),
        ["mirror30 filter30 ranking30", "encoding30 mapping30", "record30"],
    ),
    (
        ("filter30 ranking30 encoding30 mapping30 record30 candle30", 6),
        ["filter30", "ranking30", "encoding30", "mapping30", "record30", "candle30"],
    ),
    (
        ("filter30 ranking30 encoding30 mapping30 record30 candle30", 10),
        ["filter30", "ranking30", "encoding30", "mapping30", "record30", "candle30"],
    ),
    (
        ("filter30 ranking30 encoding30 mapping30 record30 candle30", 18),
        ["filter30 ranking30", "encoding30", "mapping30 record30", "candle30"],
    ),
    (
        ("filter30 ranking30 encoding30 mapping30 record30 candle30", 28),
        ["filter30 ranking30", "encoding30 mapping30", "record30 candle30"],
    ),
    (
        ("ranking30 encoding30 mapping30 record30 candle30 thread30", 6),
        ["ranking30", "encoding30", "mapping30", "record30", "candle30", "thread30"],
    ),
    (
        ("ranking30 encoding30 mapping30 record30 candle30 thread30", 10),
        ["ranking30", "encoding30", "mapping30", "record30", "candle30", "thread30"],
    ),
    (
        ("ranking30 encoding30 mapping30 record30 candle30 thread30", 18),
        ["ranking30", "encoding30", "mapping30 record30", "candle30 thread30"],
    ),
    (
        ("ranking30 encoding30 mapping30 record30 candle30 thread30", 28),
        ["ranking30 encoding30", "mapping30 record30 candle30", "thread30"],
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
