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
        ("round 91: the quick brown fox jumps over the lazy dog", 4),
        ["round", "91:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 91: the quick brown fox jumps over the lazy dog", 8),
        ["round", "91: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 91: the quick brown fox jumps over the lazy dog", 12),
        ["round 91:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 91: the quick brown fox jumps over the lazy dog", 16),
        ["round 91: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 91: the quick brown fox jumps over the lazy dog", 24),
        ["round 91: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 91: the quick brown fox jumps over the lazy dog", 32),
        ["round 91: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 91: agentuniverse is a framework for multi agents", 4),
        ["round", "91:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 91: agentuniverse is a framework for multi agents", 8),
        ["round", "91:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 91: agentuniverse is a framework for multi agents", 12),
        ["round 91:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 91: agentuniverse is a framework for multi agents", 16),
        ["round 91:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 91: agentuniverse is a framework for multi agents", 24),
        ["round 91: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 91: agentuniverse is a framework for multi agents", 32),
        ["round 91: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 91: knowledge stored as vectors enables retrieval", 4),
        ["round", "91:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 91: knowledge stored as vectors enables retrieval", 8),
        ["round", "91:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 91: knowledge stored as vectors enables retrieval", 12),
        ["round 91:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 91: knowledge stored as vectors enables retrieval", 16),
        ["round 91:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 91: knowledge stored as vectors enables retrieval", 24),
        ["round 91: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 91: knowledge stored as vectors enables retrieval", 32),
        ["round 91: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 91: the processor reads the record then stops", 4),
        ["round", "91:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 91: the processor reads the record then stops", 8),
        ["round", "91: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 91: the processor reads the record then stops", 12),
        ["round 91:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 91: the processor reads the record then stops", 16),
        ["round 91: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 91: the processor reads the record then stops", 24),
        ["round 91: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 91: the processor reads the record then stops", 32),
        ["round 91: the processor reads", "the record then stops"],
    ),
    (
        ("round 91: a worker pulls the next task from the queue", 4),
        ["round", "91:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 91: a worker pulls the next task from the queue", 8),
        ["round", "91: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 91: a worker pulls the next task from the queue", 12),
        ["round 91: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 91: a worker pulls the next task from the queue", 16),
        ["round 91: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 91: a worker pulls the next task from the queue", 24),
        ["round 91: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 91: a worker pulls the next task from the queue", 32),
        ["round 91: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 91: signals travel through the network layer", 4),
        ["round", "91:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 91: signals travel through the network layer", 8),
        ["round", "91:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 91: signals travel through the network layer", 12),
        ["round 91:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 91: signals travel through the network layer", 16),
        ["round 91:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 91: signals travel through the network layer", 24),
        ["round 91: signals travel", "through the network", "layer"],
    ),
    (
        ("round 91: signals travel through the network layer", 32),
        ["round 91: signals travel through", "the network layer"],
    ),
    (
        ("round 91: the gateway routes each request by policy", 4),
        ["round", "91:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 91: the gateway routes each request by policy", 8),
        ["round", "91: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 91: the gateway routes each request by policy", 12),
        ["round 91:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 91: the gateway routes each request by policy", 16),
        ["round 91: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 91: the gateway routes each request by policy", 24),
        ["round 91: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 91: the gateway routes each request by policy", 32),
        ["round 91: the gateway routes", "each request by policy"],
    ),
    (
        ("round 91: memory grows until the buffer is full", 4),
        ["round", "91:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 91: memory grows until the buffer is full", 8),
        ["round", "91:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 91: memory grows until the buffer is full", 12),
        ["round 91:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 91: memory grows until the buffer is full", 16),
        ["round 91: memory", "grows until the", "buffer is full"],
    ),
    (("round 91: memory grows until the buffer is full", 24), ["round 91: memory grows", "until the buffer is full"]),
    (("round 91: memory grows until the buffer is full", 32), ["round 91: memory grows until the", "buffer is full"]),
    (
        ("round 91: the cluster mirrors every packet twice", 4),
        ["round", "91:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 91: the cluster mirrors every packet twice", 8),
        ["round", "91: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 91: the cluster mirrors every packet twice", 12),
        ["round 91:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 91: the cluster mirrors every packet twice", 16),
        ["round 91: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 91: the cluster mirrors every packet twice", 24),
        ["round 91: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 91: the cluster mirrors every packet twice", 32), ["round 91: the cluster mirrors", "every packet twice"]),
    (
        ("round 91: ranking uses tokens learned from the corpus", 4),
        ["round", "91:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 91: ranking uses tokens learned from the corpus", 8),
        ["round", "91:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 91: ranking uses tokens learned from the corpus", 12),
        ["round 91:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 91: ranking uses tokens learned from the corpus", 16),
        ["round 91:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 91: ranking uses tokens learned from the corpus", 24),
        ["round 91: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 91: ranking uses tokens learned from the corpus", 32),
        ["round 91: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 91: a long session ends when the candle dies", 4),
        ["round", "91:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 91: a long session ends when the candle dies", 8),
        ["round", "91: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 91: a long session ends when the candle dies", 12),
        ["round 91: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 91: a long session ends when the candle dies", 16),
        ["round 91: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 91: a long session ends when the candle dies", 24),
        ["round 91: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 91: a long session ends when the candle dies", 32),
        ["round 91: a long session ends", "when the candle dies"],
    ),
    (
        ("round 91: encode the prompt then map the result", 4),
        ["round", "91:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 91: encode the prompt then map the result", 8),
        ["round", "91:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 91: encode the prompt then map the result", 12),
        ["round 91:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 91: encode the prompt then map the result", 16),
        ["round 91: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 91: encode the prompt then map the result", 24),
        ["round 91: encode the", "prompt then map the", "result"],
    ),
    (("round 91: encode the prompt then map the result", 32), ["round 91: encode the prompt then", "map the result"]),
    (
        ("round 91: the kernel wakes the worker at dawn", 4),
        ["round", "91:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 91: the kernel wakes the worker at dawn", 8),
        ["round", "91: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 91: the kernel wakes the worker at dawn", 12),
        ["round 91:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 91: the kernel wakes the worker at dawn", 16), ["round 91: the", "kernel wakes the", "worker at dawn"]),
    (("round 91: the kernel wakes the worker at dawn", 24), ["round 91: the kernel", "wakes the worker at dawn"]),
    (("round 91: the kernel wakes the worker at dawn", 32), ["round 91: the kernel wakes the", "worker at dawn"]),
    (
        ("round 91: service latency drops after the patch", 4),
        ["round", "91:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 91: service latency drops after the patch", 8),
        ["round", "91:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 91: service latency drops after the patch", 12),
        ["round 91:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 91: service latency drops after the patch", 16),
        ["round 91:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 91: service latency drops after the patch", 24),
        ["round 91: service", "latency drops after the", "patch"],
    ),
    (("round 91: service latency drops after the patch", 32), ["round 91: service latency drops", "after the patch"]),
    (
        ("round 91: the library caches every vector it sees", 4),
        ["round", "91:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 91: the library caches every vector it sees", 8),
        ["round", "91: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 91: the library caches every vector it sees", 12),
        ["round 91:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 91: the library caches every vector it sees", 16),
        ["round 91: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 91: the library caches every vector it sees", 24),
        ["round 91: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 91: the library caches every vector it sees", 32),
        ["round 91: the library caches", "every vector it sees"],
    ),
    (
        ("round 91: agents argue then the debate resolves", 4),
        ["round", "91:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 91: agents argue then the debate resolves", 8),
        ["round", "91:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 91: agents argue then the debate resolves", 12),
        ["round 91:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 91: agents argue then the debate resolves", 16),
        ["round 91: agents", "argue then the", "debate resolves"],
    ),
    (("round 91: agents argue then the debate resolves", 24), ["round 91: agents argue", "then the debate resolves"]),
    (("round 91: agents argue then the debate resolves", 32), ["round 91: agents argue then the", "debate resolves"]),
    (
        ("round 91: the filter keeps only strong matches", 4),
        ["round", "91:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 91: the filter keeps only strong matches", 8),
        ["round", "91: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 91: the filter keeps only strong matches", 12),
        ["round 91:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 91: the filter keeps only strong matches", 16),
        ["round 91: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 91: the filter keeps only strong matches", 24), ["round 91: the filter", "keeps only strong", "matches"]),
    (("round 91: the filter keeps only strong matches", 32), ["round 91: the filter keeps only", "strong matches"]),
    (
        ("round 91: the model answers with a short reply", 4),
        ["round", "91:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 91: the model answers with a short reply", 8),
        ["round", "91: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 91: the model answers with a short reply", 12),
        ["round 91:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 91: the model answers with a short reply", 16),
        ["round 91: the", "model answers", "with a short", "reply"],
    ),
    (("round 91: the model answers with a short reply", 24), ["round 91: the model", "answers with a short", "reply"]),
    (("round 91: the model answers with a short reply", 32), ["round 91: the model answers with", "a short reply"]),
    (
        ("round 91: the recorder stores the reasoning trace", 4),
        ["round", "91:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 91: the recorder stores the reasoning trace", 8),
        ["round", "91: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 91: the recorder stores the reasoning trace", 12),
        ["round 91:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 91: the recorder stores the reasoning trace", 16),
        ["round 91: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 91: the recorder stores the reasoning trace", 24),
        ["round 91: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 91: the recorder stores the reasoning trace", 32),
        ["round 91: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 91: the angel watches the processor run", 4),
        ["round", "91:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 91: the angel watches the processor run", 8),
        ["round", "91: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 91: the angel watches the processor run", 12),
        ["round 91:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 91: the angel watches the processor run", 16), ["round 91: the", "angel watches", "the processor", "run"]),
    (("round 91: the angel watches the processor run", 24), ["round 91: the angel", "watches the processor", "run"]),
    (("round 91: the angel watches the processor run", 32), ["round 91: the angel watches the", "processor run"]),
    (
        ("round 91: angle of the vector decides the match", 4),
        ["round", "91:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 91: angle of the vector decides the match", 8),
        ["round", "91:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 91: angle of the vector decides the match", 12),
        ["round 91:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 91: angle of the vector decides the match", 16),
        ["round 91: angle", "of the vector", "decides the", "match"],
    ),
    (("round 91: angle of the vector decides the match", 24), ["round 91: angle of the", "vector decides the match"]),
    (("round 91: angle of the vector decides the match", 32), ["round 91: angle of the vector", "decides the match"]),
    (
        ("round 91: the candle burns twice as long at night", 4),
        ["round", "91:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 91: the candle burns twice as long at night", 8),
        ["round", "91: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 91: the candle burns twice as long at night", 12),
        ["round 91:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 91: the candle burns twice as long at night", 16),
        ["round 91: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 91: the candle burns twice as long at night", 24),
        ["round 91: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 91: the candle burns twice as long at night", 32),
        ["round 91: the candle burns twice", "as long at night"],
    ),
    (
        ("round 91: a mirror of the universe in one line", 4),
        ["round", "91:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 91: a mirror of the universe in one line", 8),
        ["round", "91: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 91: a mirror of the universe in one line", 12),
        ["round 91: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 91: a mirror of the universe in one line", 16),
        ["round 91: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 91: a mirror of the universe in one line", 24), ["round 91: a mirror of", "the universe in one line"]),
    (("round 91: a mirror of the universe in one line", 32), ["round 91: a mirror of the", "universe in one line"]),
    (
        ("round 91: the queue drains before the storm", 4),
        ["round", "91:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 91: the queue drains before the storm", 8),
        ["round", "91: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 91: the queue drains before the storm", 12), ["round 91:", "the queue", "drains", "before the", "storm"]),
    (("round 91: the queue drains before the storm", 16), ["round 91: the", "queue drains", "before the storm"]),
    (("round 91: the queue drains before the storm", 24), ["round 91: the queue", "drains before the storm"]),
    (("round 91: the queue drains before the storm", 32), ["round 91: the queue drains", "before the storm"]),
    (
        ("kitten91 sitting91 agent91 angle91 universe91 memory91", 6),
        ["kitten91", "sitting91", "agent91", "angle91", "universe91", "memory91"],
    ),
    (
        ("kitten91 sitting91 agent91 angle91 universe91 memory91", 10),
        ["kitten91", "sitting91", "agent91", "angle91", "universe91", "memory91"],
    ),
    (
        ("kitten91 sitting91 agent91 angle91 universe91 memory91", 18),
        ["kitten91 sitting91", "agent91 angle91", "universe91", "memory91"],
    ),
    (
        ("kitten91 sitting91 agent91 angle91 universe91 memory91", 28),
        ["kitten91 sitting91 agent91", "angle91 universe91 memory91"],
    ),
    (
        ("sitting91 agent91 angle91 universe91 memory91 stream91", 6),
        ["sitting91", "agent91", "angle91", "universe91", "memory91", "stream91"],
    ),
    (
        ("sitting91 agent91 angle91 universe91 memory91 stream91", 10),
        ["sitting91", "agent91", "angle91", "universe91", "memory91", "stream91"],
    ),
    (
        ("sitting91 agent91 angle91 universe91 memory91 stream91", 18),
        ["sitting91 agent91", "angle91 universe91", "memory91 stream91"],
    ),
    (
        ("sitting91 agent91 angle91 universe91 memory91 stream91", 28),
        ["sitting91 agent91 angle91", "universe91 memory91 stream91"],
    ),
    (
        ("agent91 angle91 universe91 memory91 stream91 context91", 6),
        ["agent91", "angle91", "universe91", "memory91", "stream91", "context91"],
    ),
    (
        ("agent91 angle91 universe91 memory91 stream91 context91", 10),
        ["agent91", "angle91", "universe91", "memory91", "stream91", "context91"],
    ),
    (
        ("agent91 angle91 universe91 memory91 stream91 context91", 18),
        ["agent91 angle91", "universe91", "memory91 stream91", "context91"],
    ),
    (
        ("agent91 angle91 universe91 memory91 stream91 context91", 28),
        ["agent91 angle91 universe91", "memory91 stream91 context91"],
    ),
    (
        ("angle91 universe91 memory91 stream91 context91 knowledge91", 6),
        ["angle91", "universe91", "memory91", "stream91", "context91", "knowledge91"],
    ),
    (
        ("angle91 universe91 memory91 stream91 context91 knowledge91", 10),
        ["angle91", "universe91", "memory91", "stream91", "context91", "knowledge91"],
    ),
    (
        ("angle91 universe91 memory91 stream91 context91 knowledge91", 18),
        ["angle91 universe91", "memory91 stream91", "context91", "knowledge91"],
    ),
    (
        ("angle91 universe91 memory91 stream91 context91 knowledge91", 28),
        ["angle91 universe91 memory91", "stream91 context91", "knowledge91"],
    ),
    (
        ("universe91 memory91 stream91 context91 knowledge91 vector91", 6),
        ["universe91", "memory91", "stream91", "context91", "knowledge91", "vector91"],
    ),
    (
        ("universe91 memory91 stream91 context91 knowledge91 vector91", 10),
        ["universe91", "memory91", "stream91", "context91", "knowledge91", "vector91"],
    ),
    (
        ("universe91 memory91 stream91 context91 knowledge91 vector91", 18),
        ["universe91", "memory91 stream91", "context91", "knowledge91", "vector91"],
    ),
    (
        ("universe91 memory91 stream91 context91 knowledge91 vector91", 28),
        ["universe91 memory91 stream91", "context91 knowledge91", "vector91"],
    ),
    (
        ("memory91 stream91 context91 knowledge91 vector91 processor91", 6),
        ["memory91", "stream91", "context91", "knowledge91", "vector91", "processor91"],
    ),
    (
        ("memory91 stream91 context91 knowledge91 vector91 processor91", 10),
        ["memory91", "stream91", "context91", "knowledge91", "vector91", "processor91"],
    ),
    (
        ("memory91 stream91 context91 knowledge91 vector91 processor91", 18),
        ["memory91 stream91", "context91", "knowledge91", "vector91", "processor91"],
    ),
    (
        ("memory91 stream91 context91 knowledge91 vector91 processor91", 28),
        ["memory91 stream91 context91", "knowledge91 vector91", "processor91"],
    ),
    (
        ("stream91 context91 knowledge91 vector91 processor91 reasoning91", 6),
        ["stream91", "context91", "knowledge91", "vector91", "processor91", "reasoning91"],
    ),
    (
        ("stream91 context91 knowledge91 vector91 processor91 reasoning91", 10),
        ["stream91", "context91", "knowledge91", "vector91", "processor91", "reasoning91"],
    ),
    (
        ("stream91 context91 knowledge91 vector91 processor91 reasoning91", 18),
        ["stream91 context91", "knowledge91", "vector91", "processor91", "reasoning91"],
    ),
    (
        ("stream91 context91 knowledge91 vector91 processor91 reasoning91", 28),
        ["stream91 context91", "knowledge91 vector91", "processor91 reasoning91"],
    ),
    (
        ("context91 knowledge91 vector91 processor91 reasoning91 machine91", 6),
        ["context91", "knowledge91", "vector91", "processor91", "reasoning91", "machine91"],
    ),
    (
        ("context91 knowledge91 vector91 processor91 reasoning91 machine91", 10),
        ["context91", "knowledge91", "vector91", "processor91", "reasoning91", "machine91"],
    ),
    (
        ("context91 knowledge91 vector91 processor91 reasoning91 machine91", 18),
        ["context91", "knowledge91", "vector91", "processor91", "reasoning91", "machine91"],
    ),
    (
        ("context91 knowledge91 vector91 processor91 reasoning91 machine91", 28),
        ["context91 knowledge91", "vector91 processor91", "reasoning91 machine91"],
    ),
    (
        ("knowledge91 vector91 processor91 reasoning91 machine91 learning91", 6),
        ["knowledge91", "vector91", "processor91", "reasoning91", "machine91", "learning91"],
    ),
    (
        ("knowledge91 vector91 processor91 reasoning91 machine91 learning91", 10),
        ["knowledge91", "vector91", "processor91", "reasoning91", "machine91", "learning91"],
    ),
    (
        ("knowledge91 vector91 processor91 reasoning91 machine91 learning91", 18),
        ["knowledge91", "vector91", "processor91", "reasoning91", "machine91", "learning91"],
    ),
    (
        ("knowledge91 vector91 processor91 reasoning91 machine91 learning91", 28),
        ["knowledge91 vector91", "processor91 reasoning91", "machine91 learning91"],
    ),
    (
        ("vector91 processor91 reasoning91 machine91 learning91 model91", 6),
        ["vector91", "processor91", "reasoning91", "machine91", "learning91", "model91"],
    ),
    (
        ("vector91 processor91 reasoning91 machine91 learning91 model91", 10),
        ["vector91", "processor91", "reasoning91", "machine91", "learning91", "model91"],
    ),
    (
        ("vector91 processor91 reasoning91 machine91 learning91 model91", 18),
        ["vector91", "processor91", "reasoning91", "machine91", "learning91 model91"],
    ),
    (
        ("vector91 processor91 reasoning91 machine91 learning91 model91", 28),
        ["vector91 processor91", "reasoning91 machine91", "learning91 model91"],
    ),
    (
        ("processor91 reasoning91 machine91 learning91 model91 token91", 6),
        ["processor91", "reasoning91", "machine91", "learning91", "model91", "token91"],
    ),
    (
        ("processor91 reasoning91 machine91 learning91 model91 token91", 10),
        ["processor91", "reasoning91", "machine91", "learning91", "model91", "token91"],
    ),
    (
        ("processor91 reasoning91 machine91 learning91 model91 token91", 18),
        ["processor91", "reasoning91", "machine91", "learning91 model91", "token91"],
    ),
    (
        ("processor91 reasoning91 machine91 learning91 model91 token91", 28),
        ["processor91 reasoning91", "machine91 learning91 model91", "token91"],
    ),
    (
        ("reasoning91 machine91 learning91 model91 token91 prompt91", 6),
        ["reasoning91", "machine91", "learning91", "model91", "token91", "prompt91"],
    ),
    (
        ("reasoning91 machine91 learning91 model91 token91 prompt91", 10),
        ["reasoning91", "machine91", "learning91", "model91", "token91", "prompt91"],
    ),
    (
        ("reasoning91 machine91 learning91 model91 token91 prompt91", 18),
        ["reasoning91", "machine91", "learning91 model91", "token91 prompt91"],
    ),
    (
        ("reasoning91 machine91 learning91 model91 token91 prompt91", 28),
        ["reasoning91 machine91", "learning91 model91 token91", "prompt91"],
    ),
    (
        ("machine91 learning91 model91 token91 prompt91 session91", 6),
        ["machine91", "learning91", "model91", "token91", "prompt91", "session91"],
    ),
    (
        ("machine91 learning91 model91 token91 prompt91 session91", 10),
        ["machine91", "learning91", "model91", "token91", "prompt91", "session91"],
    ),
    (
        ("machine91 learning91 model91 token91 prompt91 session91", 18),
        ["machine91", "learning91 model91", "token91 prompt91", "session91"],
    ),
    (
        ("machine91 learning91 model91 token91 prompt91 session91", 28),
        ["machine91 learning91 model91", "token91 prompt91 session91"],
    ),
    (
        ("learning91 model91 token91 prompt91 session91 library91", 6),
        ["learning91", "model91", "token91", "prompt91", "session91", "library91"],
    ),
    (
        ("learning91 model91 token91 prompt91 session91 library91", 10),
        ["learning91", "model91", "token91", "prompt91", "session91", "library91"],
    ),
    (
        ("learning91 model91 token91 prompt91 session91 library91", 18),
        ["learning91 model91", "token91 prompt91", "session91", "library91"],
    ),
    (
        ("learning91 model91 token91 prompt91 session91 library91", 28),
        ["learning91 model91 token91", "prompt91 session91 library91"],
    ),
    (
        ("model91 token91 prompt91 session91 library91 service91", 6),
        ["model91", "token91", "prompt91", "session91", "library91", "service91"],
    ),
    (
        ("model91 token91 prompt91 session91 library91 service91", 10),
        ["model91", "token91", "prompt91", "session91", "library91", "service91"],
    ),
    (
        ("model91 token91 prompt91 session91 library91 service91", 18),
        ["model91 token91", "prompt91 session91", "library91", "service91"],
    ),
    (
        ("model91 token91 prompt91 session91 library91 service91", 28),
        ["model91 token91 prompt91", "session91 library91", "service91"],
    ),
    (
        ("token91 prompt91 session91 library91 service91 gateway91", 6),
        ["token91", "prompt91", "session91", "library91", "service91", "gateway91"],
    ),
    (
        ("token91 prompt91 session91 library91 service91 gateway91", 10),
        ["token91", "prompt91", "session91", "library91", "service91", "gateway91"],
    ),
    (
        ("token91 prompt91 session91 library91 service91 gateway91", 18),
        ["token91 prompt91", "session91", "library91", "service91", "gateway91"],
    ),
    (
        ("token91 prompt91 session91 library91 service91 gateway91", 28),
        ["token91 prompt91 session91", "library91 service91", "gateway91"],
    ),
    (
        ("prompt91 session91 library91 service91 gateway91 storage91", 6),
        ["prompt91", "session91", "library91", "service91", "gateway91", "storage91"],
    ),
    (
        ("prompt91 session91 library91 service91 gateway91 storage91", 10),
        ["prompt91", "session91", "library91", "service91", "gateway91", "storage91"],
    ),
    (
        ("prompt91 session91 library91 service91 gateway91 storage91", 18),
        ["prompt91 session91", "library91", "service91", "gateway91", "storage91"],
    ),
    (
        ("prompt91 session91 library91 service91 gateway91 storage91", 28),
        ["prompt91 session91 library91", "service91 gateway91", "storage91"],
    ),
    (
        ("session91 library91 service91 gateway91 storage91 network91", 6),
        ["session91", "library91", "service91", "gateway91", "storage91", "network91"],
    ),
    (
        ("session91 library91 service91 gateway91 storage91 network91", 10),
        ["session91", "library91", "service91", "gateway91", "storage91", "network91"],
    ),
    (
        ("session91 library91 service91 gateway91 storage91 network91", 18),
        ["session91", "library91", "service91", "gateway91", "storage91", "network91"],
    ),
    (
        ("session91 library91 service91 gateway91 storage91 network91", 28),
        ["session91 library91", "service91 gateway91", "storage91 network91"],
    ),
    (
        ("library91 service91 gateway91 storage91 network91 latency91", 6),
        ["library91", "service91", "gateway91", "storage91", "network91", "latency91"],
    ),
    (
        ("library91 service91 gateway91 storage91 network91 latency91", 10),
        ["library91", "service91", "gateway91", "storage91", "network91", "latency91"],
    ),
    (
        ("library91 service91 gateway91 storage91 network91 latency91", 18),
        ["library91", "service91", "gateway91", "storage91", "network91", "latency91"],
    ),
    (
        ("library91 service91 gateway91 storage91 network91 latency91", 28),
        ["library91 service91", "gateway91 storage91", "network91 latency91"],
    ),
    (
        ("service91 gateway91 storage91 network91 latency91 buffer91", 6),
        ["service91", "gateway91", "storage91", "network91", "latency91", "buffer91"],
    ),
    (
        ("service91 gateway91 storage91 network91 latency91 buffer91", 10),
        ["service91", "gateway91", "storage91", "network91", "latency91", "buffer91"],
    ),
    (
        ("service91 gateway91 storage91 network91 latency91 buffer91", 18),
        ["service91", "gateway91", "storage91", "network91", "latency91 buffer91"],
    ),
    (
        ("service91 gateway91 storage91 network91 latency91 buffer91", 28),
        ["service91 gateway91", "storage91 network91", "latency91 buffer91"],
    ),
    (
        ("gateway91 storage91 network91 latency91 buffer91 queue91", 6),
        ["gateway91", "storage91", "network91", "latency91", "buffer91", "queue91"],
    ),
    (
        ("gateway91 storage91 network91 latency91 buffer91 queue91", 10),
        ["gateway91", "storage91", "network91", "latency91", "buffer91", "queue91"],
    ),
    (
        ("gateway91 storage91 network91 latency91 buffer91 queue91", 18),
        ["gateway91", "storage91", "network91", "latency91 buffer91", "queue91"],
    ),
    (
        ("gateway91 storage91 network91 latency91 buffer91 queue91", 28),
        ["gateway91 storage91", "network91 latency91 buffer91", "queue91"],
    ),
    (
        ("storage91 network91 latency91 buffer91 queue91 worker91", 6),
        ["storage91", "network91", "latency91", "buffer91", "queue91", "worker91"],
    ),
    (
        ("storage91 network91 latency91 buffer91 queue91 worker91", 10),
        ["storage91", "network91", "latency91", "buffer91", "queue91", "worker91"],
    ),
    (
        ("storage91 network91 latency91 buffer91 queue91 worker91", 18),
        ["storage91", "network91", "latency91 buffer91", "queue91 worker91"],
    ),
    (
        ("storage91 network91 latency91 buffer91 queue91 worker91", 28),
        ["storage91 network91", "latency91 buffer91 queue91", "worker91"],
    ),
    (
        ("network91 latency91 buffer91 queue91 worker91 kernel91", 6),
        ["network91", "latency91", "buffer91", "queue91", "worker91", "kernel91"],
    ),
    (
        ("network91 latency91 buffer91 queue91 worker91 kernel91", 10),
        ["network91", "latency91", "buffer91", "queue91", "worker91", "kernel91"],
    ),
    (
        ("network91 latency91 buffer91 queue91 worker91 kernel91", 18),
        ["network91", "latency91 buffer91", "queue91 worker91", "kernel91"],
    ),
    (
        ("network91 latency91 buffer91 queue91 worker91 kernel91", 28),
        ["network91 latency91 buffer91", "queue91 worker91 kernel91"],
    ),
    (
        ("latency91 buffer91 queue91 worker91 kernel91 signal91", 6),
        ["latency91", "buffer91", "queue91", "worker91", "kernel91", "signal91"],
    ),
    (
        ("latency91 buffer91 queue91 worker91 kernel91 signal91", 10),
        ["latency91", "buffer91", "queue91", "worker91", "kernel91", "signal91"],
    ),
    (
        ("latency91 buffer91 queue91 worker91 kernel91 signal91", 18),
        ["latency91 buffer91", "queue91 worker91", "kernel91 signal91"],
    ),
    (
        ("latency91 buffer91 queue91 worker91 kernel91 signal91", 28),
        ["latency91 buffer91 queue91", "worker91 kernel91 signal91"],
    ),
    (
        ("buffer91 queue91 worker91 kernel91 signal91 packet91", 6),
        ["buffer91", "queue91", "worker91", "kernel91", "signal91", "packet91"],
    ),
    (
        ("buffer91 queue91 worker91 kernel91 signal91 packet91", 10),
        ["buffer91", "queue91", "worker91", "kernel91", "signal91", "packet91"],
    ),
    (
        ("buffer91 queue91 worker91 kernel91 signal91 packet91", 18),
        ["buffer91 queue91", "worker91 kernel91", "signal91 packet91"],
    ),
    (
        ("buffer91 queue91 worker91 kernel91 signal91 packet91", 28),
        ["buffer91 queue91 worker91", "kernel91 signal91 packet91"],
    ),
    (
        ("queue91 worker91 kernel91 signal91 packet91 router91", 6),
        ["queue91", "worker91", "kernel91", "signal91", "packet91", "router91"],
    ),
    (
        ("queue91 worker91 kernel91 signal91 packet91 router91", 10),
        ["queue91", "worker91", "kernel91", "signal91", "packet91", "router91"],
    ),
    (
        ("queue91 worker91 kernel91 signal91 packet91 router91", 18),
        ["queue91 worker91", "kernel91 signal91", "packet91 router91"],
    ),
    (
        ("queue91 worker91 kernel91 signal91 packet91 router91", 28),
        ["queue91 worker91 kernel91", "signal91 packet91 router91"],
    ),
    (
        ("worker91 kernel91 signal91 packet91 router91 cluster91", 6),
        ["worker91", "kernel91", "signal91", "packet91", "router91", "cluster91"],
    ),
    (
        ("worker91 kernel91 signal91 packet91 router91 cluster91", 10),
        ["worker91", "kernel91", "signal91", "packet91", "router91", "cluster91"],
    ),
    (
        ("worker91 kernel91 signal91 packet91 router91 cluster91", 18),
        ["worker91 kernel91", "signal91 packet91", "router91 cluster91"],
    ),
    (
        ("worker91 kernel91 signal91 packet91 router91 cluster91", 28),
        ["worker91 kernel91 signal91", "packet91 router91 cluster91"],
    ),
    (
        ("kernel91 signal91 packet91 router91 cluster91 mirror91", 6),
        ["kernel91", "signal91", "packet91", "router91", "cluster91", "mirror91"],
    ),
    (
        ("kernel91 signal91 packet91 router91 cluster91 mirror91", 10),
        ["kernel91", "signal91", "packet91", "router91", "cluster91", "mirror91"],
    ),
    (
        ("kernel91 signal91 packet91 router91 cluster91 mirror91", 18),
        ["kernel91 signal91", "packet91 router91", "cluster91 mirror91"],
    ),
    (
        ("kernel91 signal91 packet91 router91 cluster91 mirror91", 28),
        ["kernel91 signal91 packet91", "router91 cluster91 mirror91"],
    ),
    (
        ("signal91 packet91 router91 cluster91 mirror91 filter91", 6),
        ["signal91", "packet91", "router91", "cluster91", "mirror91", "filter91"],
    ),
    (
        ("signal91 packet91 router91 cluster91 mirror91 filter91", 10),
        ["signal91", "packet91", "router91", "cluster91", "mirror91", "filter91"],
    ),
    (
        ("signal91 packet91 router91 cluster91 mirror91 filter91", 18),
        ["signal91 packet91", "router91 cluster91", "mirror91 filter91"],
    ),
    (
        ("signal91 packet91 router91 cluster91 mirror91 filter91", 28),
        ["signal91 packet91 router91", "cluster91 mirror91 filter91"],
    ),
    (
        ("packet91 router91 cluster91 mirror91 filter91 ranking91", 6),
        ["packet91", "router91", "cluster91", "mirror91", "filter91", "ranking91"],
    ),
    (
        ("packet91 router91 cluster91 mirror91 filter91 ranking91", 10),
        ["packet91", "router91", "cluster91", "mirror91", "filter91", "ranking91"],
    ),
    (
        ("packet91 router91 cluster91 mirror91 filter91 ranking91", 18),
        ["packet91 router91", "cluster91 mirror91", "filter91 ranking91"],
    ),
    (
        ("packet91 router91 cluster91 mirror91 filter91 ranking91", 28),
        ["packet91 router91 cluster91", "mirror91 filter91 ranking91"],
    ),
    (
        ("router91 cluster91 mirror91 filter91 ranking91 encoding91", 6),
        ["router91", "cluster91", "mirror91", "filter91", "ranking91", "encoding91"],
    ),
    (
        ("router91 cluster91 mirror91 filter91 ranking91 encoding91", 10),
        ["router91", "cluster91", "mirror91", "filter91", "ranking91", "encoding91"],
    ),
    (
        ("router91 cluster91 mirror91 filter91 ranking91 encoding91", 18),
        ["router91 cluster91", "mirror91 filter91", "ranking91", "encoding91"],
    ),
    (
        ("router91 cluster91 mirror91 filter91 ranking91 encoding91", 28),
        ["router91 cluster91 mirror91", "filter91 ranking91", "encoding91"],
    ),
    (
        ("cluster91 mirror91 filter91 ranking91 encoding91 mapping91", 6),
        ["cluster91", "mirror91", "filter91", "ranking91", "encoding91", "mapping91"],
    ),
    (
        ("cluster91 mirror91 filter91 ranking91 encoding91 mapping91", 10),
        ["cluster91", "mirror91", "filter91", "ranking91", "encoding91", "mapping91"],
    ),
    (
        ("cluster91 mirror91 filter91 ranking91 encoding91 mapping91", 18),
        ["cluster91 mirror91", "filter91 ranking91", "encoding91", "mapping91"],
    ),
    (
        ("cluster91 mirror91 filter91 ranking91 encoding91 mapping91", 28),
        ["cluster91 mirror91 filter91", "ranking91 encoding91", "mapping91"],
    ),
    (
        ("mirror91 filter91 ranking91 encoding91 mapping91 record91", 6),
        ["mirror91", "filter91", "ranking91", "encoding91", "mapping91", "record91"],
    ),
    (
        ("mirror91 filter91 ranking91 encoding91 mapping91 record91", 10),
        ["mirror91", "filter91", "ranking91", "encoding91", "mapping91", "record91"],
    ),
    (
        ("mirror91 filter91 ranking91 encoding91 mapping91 record91", 18),
        ["mirror91 filter91", "ranking91", "encoding91", "mapping91 record91"],
    ),
    (
        ("mirror91 filter91 ranking91 encoding91 mapping91 record91", 28),
        ["mirror91 filter91 ranking91", "encoding91 mapping91", "record91"],
    ),
    (
        ("filter91 ranking91 encoding91 mapping91 record91 candle91", 6),
        ["filter91", "ranking91", "encoding91", "mapping91", "record91", "candle91"],
    ),
    (
        ("filter91 ranking91 encoding91 mapping91 record91 candle91", 10),
        ["filter91", "ranking91", "encoding91", "mapping91", "record91", "candle91"],
    ),
    (
        ("filter91 ranking91 encoding91 mapping91 record91 candle91", 18),
        ["filter91 ranking91", "encoding91", "mapping91 record91", "candle91"],
    ),
    (
        ("filter91 ranking91 encoding91 mapping91 record91 candle91", 28),
        ["filter91 ranking91", "encoding91 mapping91", "record91 candle91"],
    ),
    (
        ("ranking91 encoding91 mapping91 record91 candle91 thread91", 6),
        ["ranking91", "encoding91", "mapping91", "record91", "candle91", "thread91"],
    ),
    (
        ("ranking91 encoding91 mapping91 record91 candle91 thread91", 10),
        ["ranking91", "encoding91", "mapping91", "record91", "candle91", "thread91"],
    ),
    (
        ("ranking91 encoding91 mapping91 record91 candle91 thread91", 18),
        ["ranking91", "encoding91", "mapping91 record91", "candle91 thread91"],
    ),
    (
        ("ranking91 encoding91 mapping91 record91 candle91 thread91", 28),
        ["ranking91 encoding91", "mapping91 record91 candle91", "thread91"],
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
