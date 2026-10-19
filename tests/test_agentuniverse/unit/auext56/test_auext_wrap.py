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
        ("round 56: the quick brown fox jumps over the lazy dog", 4),
        ["round", "56:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 56: the quick brown fox jumps over the lazy dog", 8),
        ["round", "56: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 56: the quick brown fox jumps over the lazy dog", 12),
        ["round 56:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 56: the quick brown fox jumps over the lazy dog", 16),
        ["round 56: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 56: the quick brown fox jumps over the lazy dog", 24),
        ["round 56: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 56: the quick brown fox jumps over the lazy dog", 32),
        ["round 56: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 56: agentuniverse is a framework for multi agents", 4),
        ["round", "56:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 56: agentuniverse is a framework for multi agents", 8),
        ["round", "56:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 56: agentuniverse is a framework for multi agents", 12),
        ["round 56:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 56: agentuniverse is a framework for multi agents", 16),
        ["round 56:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 56: agentuniverse is a framework for multi agents", 24),
        ["round 56: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 56: agentuniverse is a framework for multi agents", 32),
        ["round 56: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 56: knowledge stored as vectors enables retrieval", 4),
        ["round", "56:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 56: knowledge stored as vectors enables retrieval", 8),
        ["round", "56:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 56: knowledge stored as vectors enables retrieval", 12),
        ["round 56:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 56: knowledge stored as vectors enables retrieval", 16),
        ["round 56:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 56: knowledge stored as vectors enables retrieval", 24),
        ["round 56: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 56: knowledge stored as vectors enables retrieval", 32),
        ["round 56: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 56: the processor reads the record then stops", 4),
        ["round", "56:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 56: the processor reads the record then stops", 8),
        ["round", "56: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 56: the processor reads the record then stops", 12),
        ["round 56:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 56: the processor reads the record then stops", 16),
        ["round 56: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 56: the processor reads the record then stops", 24),
        ["round 56: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 56: the processor reads the record then stops", 32),
        ["round 56: the processor reads", "the record then stops"],
    ),
    (
        ("round 56: a worker pulls the next task from the queue", 4),
        ["round", "56:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 56: a worker pulls the next task from the queue", 8),
        ["round", "56: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 56: a worker pulls the next task from the queue", 12),
        ["round 56: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 56: a worker pulls the next task from the queue", 16),
        ["round 56: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 56: a worker pulls the next task from the queue", 24),
        ["round 56: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 56: a worker pulls the next task from the queue", 32),
        ["round 56: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 56: signals travel through the network layer", 4),
        ["round", "56:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 56: signals travel through the network layer", 8),
        ["round", "56:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 56: signals travel through the network layer", 12),
        ["round 56:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 56: signals travel through the network layer", 16),
        ["round 56:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 56: signals travel through the network layer", 24),
        ["round 56: signals travel", "through the network", "layer"],
    ),
    (
        ("round 56: signals travel through the network layer", 32),
        ["round 56: signals travel through", "the network layer"],
    ),
    (
        ("round 56: the gateway routes each request by policy", 4),
        ["round", "56:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 56: the gateway routes each request by policy", 8),
        ["round", "56: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 56: the gateway routes each request by policy", 12),
        ["round 56:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 56: the gateway routes each request by policy", 16),
        ["round 56: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 56: the gateway routes each request by policy", 24),
        ["round 56: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 56: the gateway routes each request by policy", 32),
        ["round 56: the gateway routes", "each request by policy"],
    ),
    (
        ("round 56: memory grows until the buffer is full", 4),
        ["round", "56:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 56: memory grows until the buffer is full", 8),
        ["round", "56:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 56: memory grows until the buffer is full", 12),
        ["round 56:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 56: memory grows until the buffer is full", 16),
        ["round 56: memory", "grows until the", "buffer is full"],
    ),
    (("round 56: memory grows until the buffer is full", 24), ["round 56: memory grows", "until the buffer is full"]),
    (("round 56: memory grows until the buffer is full", 32), ["round 56: memory grows until the", "buffer is full"]),
    (
        ("round 56: the cluster mirrors every packet twice", 4),
        ["round", "56:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 56: the cluster mirrors every packet twice", 8),
        ["round", "56: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 56: the cluster mirrors every packet twice", 12),
        ["round 56:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 56: the cluster mirrors every packet twice", 16),
        ["round 56: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 56: the cluster mirrors every packet twice", 24),
        ["round 56: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 56: the cluster mirrors every packet twice", 32), ["round 56: the cluster mirrors", "every packet twice"]),
    (
        ("round 56: ranking uses tokens learned from the corpus", 4),
        ["round", "56:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 56: ranking uses tokens learned from the corpus", 8),
        ["round", "56:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 56: ranking uses tokens learned from the corpus", 12),
        ["round 56:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 56: ranking uses tokens learned from the corpus", 16),
        ["round 56:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 56: ranking uses tokens learned from the corpus", 24),
        ["round 56: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 56: ranking uses tokens learned from the corpus", 32),
        ["round 56: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 56: a long session ends when the candle dies", 4),
        ["round", "56:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 56: a long session ends when the candle dies", 8),
        ["round", "56: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 56: a long session ends when the candle dies", 12),
        ["round 56: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 56: a long session ends when the candle dies", 16),
        ["round 56: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 56: a long session ends when the candle dies", 24),
        ["round 56: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 56: a long session ends when the candle dies", 32),
        ["round 56: a long session ends", "when the candle dies"],
    ),
    (
        ("round 56: encode the prompt then map the result", 4),
        ["round", "56:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 56: encode the prompt then map the result", 8),
        ["round", "56:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 56: encode the prompt then map the result", 12),
        ["round 56:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 56: encode the prompt then map the result", 16),
        ["round 56: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 56: encode the prompt then map the result", 24),
        ["round 56: encode the", "prompt then map the", "result"],
    ),
    (("round 56: encode the prompt then map the result", 32), ["round 56: encode the prompt then", "map the result"]),
    (
        ("round 56: the kernel wakes the worker at dawn", 4),
        ["round", "56:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 56: the kernel wakes the worker at dawn", 8),
        ["round", "56: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 56: the kernel wakes the worker at dawn", 12),
        ["round 56:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 56: the kernel wakes the worker at dawn", 16), ["round 56: the", "kernel wakes the", "worker at dawn"]),
    (("round 56: the kernel wakes the worker at dawn", 24), ["round 56: the kernel", "wakes the worker at dawn"]),
    (("round 56: the kernel wakes the worker at dawn", 32), ["round 56: the kernel wakes the", "worker at dawn"]),
    (
        ("round 56: service latency drops after the patch", 4),
        ["round", "56:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 56: service latency drops after the patch", 8),
        ["round", "56:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 56: service latency drops after the patch", 12),
        ["round 56:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 56: service latency drops after the patch", 16),
        ["round 56:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 56: service latency drops after the patch", 24),
        ["round 56: service", "latency drops after the", "patch"],
    ),
    (("round 56: service latency drops after the patch", 32), ["round 56: service latency drops", "after the patch"]),
    (
        ("round 56: the library caches every vector it sees", 4),
        ["round", "56:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 56: the library caches every vector it sees", 8),
        ["round", "56: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 56: the library caches every vector it sees", 12),
        ["round 56:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 56: the library caches every vector it sees", 16),
        ["round 56: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 56: the library caches every vector it sees", 24),
        ["round 56: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 56: the library caches every vector it sees", 32),
        ["round 56: the library caches", "every vector it sees"],
    ),
    (
        ("round 56: agents argue then the debate resolves", 4),
        ["round", "56:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 56: agents argue then the debate resolves", 8),
        ["round", "56:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 56: agents argue then the debate resolves", 12),
        ["round 56:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 56: agents argue then the debate resolves", 16),
        ["round 56: agents", "argue then the", "debate resolves"],
    ),
    (("round 56: agents argue then the debate resolves", 24), ["round 56: agents argue", "then the debate resolves"]),
    (("round 56: agents argue then the debate resolves", 32), ["round 56: agents argue then the", "debate resolves"]),
    (
        ("round 56: the filter keeps only strong matches", 4),
        ["round", "56:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 56: the filter keeps only strong matches", 8),
        ["round", "56: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 56: the filter keeps only strong matches", 12),
        ["round 56:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 56: the filter keeps only strong matches", 16),
        ["round 56: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 56: the filter keeps only strong matches", 24), ["round 56: the filter", "keeps only strong", "matches"]),
    (("round 56: the filter keeps only strong matches", 32), ["round 56: the filter keeps only", "strong matches"]),
    (
        ("round 56: the model answers with a short reply", 4),
        ["round", "56:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 56: the model answers with a short reply", 8),
        ["round", "56: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 56: the model answers with a short reply", 12),
        ["round 56:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 56: the model answers with a short reply", 16),
        ["round 56: the", "model answers", "with a short", "reply"],
    ),
    (("round 56: the model answers with a short reply", 24), ["round 56: the model", "answers with a short", "reply"]),
    (("round 56: the model answers with a short reply", 32), ["round 56: the model answers with", "a short reply"]),
    (
        ("round 56: the recorder stores the reasoning trace", 4),
        ["round", "56:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 56: the recorder stores the reasoning trace", 8),
        ["round", "56: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 56: the recorder stores the reasoning trace", 12),
        ["round 56:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 56: the recorder stores the reasoning trace", 16),
        ["round 56: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 56: the recorder stores the reasoning trace", 24),
        ["round 56: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 56: the recorder stores the reasoning trace", 32),
        ["round 56: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 56: the angel watches the processor run", 4),
        ["round", "56:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 56: the angel watches the processor run", 8),
        ["round", "56: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 56: the angel watches the processor run", 12),
        ["round 56:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 56: the angel watches the processor run", 16), ["round 56: the", "angel watches", "the processor", "run"]),
    (("round 56: the angel watches the processor run", 24), ["round 56: the angel", "watches the processor", "run"]),
    (("round 56: the angel watches the processor run", 32), ["round 56: the angel watches the", "processor run"]),
    (
        ("round 56: angle of the vector decides the match", 4),
        ["round", "56:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 56: angle of the vector decides the match", 8),
        ["round", "56:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 56: angle of the vector decides the match", 12),
        ["round 56:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 56: angle of the vector decides the match", 16),
        ["round 56: angle", "of the vector", "decides the", "match"],
    ),
    (("round 56: angle of the vector decides the match", 24), ["round 56: angle of the", "vector decides the match"]),
    (("round 56: angle of the vector decides the match", 32), ["round 56: angle of the vector", "decides the match"]),
    (
        ("round 56: the candle burns twice as long at night", 4),
        ["round", "56:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 56: the candle burns twice as long at night", 8),
        ["round", "56: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 56: the candle burns twice as long at night", 12),
        ["round 56:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 56: the candle burns twice as long at night", 16),
        ["round 56: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 56: the candle burns twice as long at night", 24),
        ["round 56: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 56: the candle burns twice as long at night", 32),
        ["round 56: the candle burns twice", "as long at night"],
    ),
    (
        ("round 56: a mirror of the universe in one line", 4),
        ["round", "56:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 56: a mirror of the universe in one line", 8),
        ["round", "56: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 56: a mirror of the universe in one line", 12),
        ["round 56: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 56: a mirror of the universe in one line", 16),
        ["round 56: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 56: a mirror of the universe in one line", 24), ["round 56: a mirror of", "the universe in one line"]),
    (("round 56: a mirror of the universe in one line", 32), ["round 56: a mirror of the", "universe in one line"]),
    (
        ("round 56: the queue drains before the storm", 4),
        ["round", "56:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 56: the queue drains before the storm", 8),
        ["round", "56: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 56: the queue drains before the storm", 12), ["round 56:", "the queue", "drains", "before the", "storm"]),
    (("round 56: the queue drains before the storm", 16), ["round 56: the", "queue drains", "before the storm"]),
    (("round 56: the queue drains before the storm", 24), ["round 56: the queue", "drains before the storm"]),
    (("round 56: the queue drains before the storm", 32), ["round 56: the queue drains", "before the storm"]),
    (
        ("kitten56 sitting56 agent56 angle56 universe56 memory56", 6),
        ["kitten56", "sitting56", "agent56", "angle56", "universe56", "memory56"],
    ),
    (
        ("kitten56 sitting56 agent56 angle56 universe56 memory56", 10),
        ["kitten56", "sitting56", "agent56", "angle56", "universe56", "memory56"],
    ),
    (
        ("kitten56 sitting56 agent56 angle56 universe56 memory56", 18),
        ["kitten56 sitting56", "agent56 angle56", "universe56", "memory56"],
    ),
    (
        ("kitten56 sitting56 agent56 angle56 universe56 memory56", 28),
        ["kitten56 sitting56 agent56", "angle56 universe56 memory56"],
    ),
    (
        ("sitting56 agent56 angle56 universe56 memory56 stream56", 6),
        ["sitting56", "agent56", "angle56", "universe56", "memory56", "stream56"],
    ),
    (
        ("sitting56 agent56 angle56 universe56 memory56 stream56", 10),
        ["sitting56", "agent56", "angle56", "universe56", "memory56", "stream56"],
    ),
    (
        ("sitting56 agent56 angle56 universe56 memory56 stream56", 18),
        ["sitting56 agent56", "angle56 universe56", "memory56 stream56"],
    ),
    (
        ("sitting56 agent56 angle56 universe56 memory56 stream56", 28),
        ["sitting56 agent56 angle56", "universe56 memory56 stream56"],
    ),
    (
        ("agent56 angle56 universe56 memory56 stream56 context56", 6),
        ["agent56", "angle56", "universe56", "memory56", "stream56", "context56"],
    ),
    (
        ("agent56 angle56 universe56 memory56 stream56 context56", 10),
        ["agent56", "angle56", "universe56", "memory56", "stream56", "context56"],
    ),
    (
        ("agent56 angle56 universe56 memory56 stream56 context56", 18),
        ["agent56 angle56", "universe56", "memory56 stream56", "context56"],
    ),
    (
        ("agent56 angle56 universe56 memory56 stream56 context56", 28),
        ["agent56 angle56 universe56", "memory56 stream56 context56"],
    ),
    (
        ("angle56 universe56 memory56 stream56 context56 knowledge56", 6),
        ["angle56", "universe56", "memory56", "stream56", "context56", "knowledge56"],
    ),
    (
        ("angle56 universe56 memory56 stream56 context56 knowledge56", 10),
        ["angle56", "universe56", "memory56", "stream56", "context56", "knowledge56"],
    ),
    (
        ("angle56 universe56 memory56 stream56 context56 knowledge56", 18),
        ["angle56 universe56", "memory56 stream56", "context56", "knowledge56"],
    ),
    (
        ("angle56 universe56 memory56 stream56 context56 knowledge56", 28),
        ["angle56 universe56 memory56", "stream56 context56", "knowledge56"],
    ),
    (
        ("universe56 memory56 stream56 context56 knowledge56 vector56", 6),
        ["universe56", "memory56", "stream56", "context56", "knowledge56", "vector56"],
    ),
    (
        ("universe56 memory56 stream56 context56 knowledge56 vector56", 10),
        ["universe56", "memory56", "stream56", "context56", "knowledge56", "vector56"],
    ),
    (
        ("universe56 memory56 stream56 context56 knowledge56 vector56", 18),
        ["universe56", "memory56 stream56", "context56", "knowledge56", "vector56"],
    ),
    (
        ("universe56 memory56 stream56 context56 knowledge56 vector56", 28),
        ["universe56 memory56 stream56", "context56 knowledge56", "vector56"],
    ),
    (
        ("memory56 stream56 context56 knowledge56 vector56 processor56", 6),
        ["memory56", "stream56", "context56", "knowledge56", "vector56", "processor56"],
    ),
    (
        ("memory56 stream56 context56 knowledge56 vector56 processor56", 10),
        ["memory56", "stream56", "context56", "knowledge56", "vector56", "processor56"],
    ),
    (
        ("memory56 stream56 context56 knowledge56 vector56 processor56", 18),
        ["memory56 stream56", "context56", "knowledge56", "vector56", "processor56"],
    ),
    (
        ("memory56 stream56 context56 knowledge56 vector56 processor56", 28),
        ["memory56 stream56 context56", "knowledge56 vector56", "processor56"],
    ),
    (
        ("stream56 context56 knowledge56 vector56 processor56 reasoning56", 6),
        ["stream56", "context56", "knowledge56", "vector56", "processor56", "reasoning56"],
    ),
    (
        ("stream56 context56 knowledge56 vector56 processor56 reasoning56", 10),
        ["stream56", "context56", "knowledge56", "vector56", "processor56", "reasoning56"],
    ),
    (
        ("stream56 context56 knowledge56 vector56 processor56 reasoning56", 18),
        ["stream56 context56", "knowledge56", "vector56", "processor56", "reasoning56"],
    ),
    (
        ("stream56 context56 knowledge56 vector56 processor56 reasoning56", 28),
        ["stream56 context56", "knowledge56 vector56", "processor56 reasoning56"],
    ),
    (
        ("context56 knowledge56 vector56 processor56 reasoning56 machine56", 6),
        ["context56", "knowledge56", "vector56", "processor56", "reasoning56", "machine56"],
    ),
    (
        ("context56 knowledge56 vector56 processor56 reasoning56 machine56", 10),
        ["context56", "knowledge56", "vector56", "processor56", "reasoning56", "machine56"],
    ),
    (
        ("context56 knowledge56 vector56 processor56 reasoning56 machine56", 18),
        ["context56", "knowledge56", "vector56", "processor56", "reasoning56", "machine56"],
    ),
    (
        ("context56 knowledge56 vector56 processor56 reasoning56 machine56", 28),
        ["context56 knowledge56", "vector56 processor56", "reasoning56 machine56"],
    ),
    (
        ("knowledge56 vector56 processor56 reasoning56 machine56 learning56", 6),
        ["knowledge56", "vector56", "processor56", "reasoning56", "machine56", "learning56"],
    ),
    (
        ("knowledge56 vector56 processor56 reasoning56 machine56 learning56", 10),
        ["knowledge56", "vector56", "processor56", "reasoning56", "machine56", "learning56"],
    ),
    (
        ("knowledge56 vector56 processor56 reasoning56 machine56 learning56", 18),
        ["knowledge56", "vector56", "processor56", "reasoning56", "machine56", "learning56"],
    ),
    (
        ("knowledge56 vector56 processor56 reasoning56 machine56 learning56", 28),
        ["knowledge56 vector56", "processor56 reasoning56", "machine56 learning56"],
    ),
    (
        ("vector56 processor56 reasoning56 machine56 learning56 model56", 6),
        ["vector56", "processor56", "reasoning56", "machine56", "learning56", "model56"],
    ),
    (
        ("vector56 processor56 reasoning56 machine56 learning56 model56", 10),
        ["vector56", "processor56", "reasoning56", "machine56", "learning56", "model56"],
    ),
    (
        ("vector56 processor56 reasoning56 machine56 learning56 model56", 18),
        ["vector56", "processor56", "reasoning56", "machine56", "learning56 model56"],
    ),
    (
        ("vector56 processor56 reasoning56 machine56 learning56 model56", 28),
        ["vector56 processor56", "reasoning56 machine56", "learning56 model56"],
    ),
    (
        ("processor56 reasoning56 machine56 learning56 model56 token56", 6),
        ["processor56", "reasoning56", "machine56", "learning56", "model56", "token56"],
    ),
    (
        ("processor56 reasoning56 machine56 learning56 model56 token56", 10),
        ["processor56", "reasoning56", "machine56", "learning56", "model56", "token56"],
    ),
    (
        ("processor56 reasoning56 machine56 learning56 model56 token56", 18),
        ["processor56", "reasoning56", "machine56", "learning56 model56", "token56"],
    ),
    (
        ("processor56 reasoning56 machine56 learning56 model56 token56", 28),
        ["processor56 reasoning56", "machine56 learning56 model56", "token56"],
    ),
    (
        ("reasoning56 machine56 learning56 model56 token56 prompt56", 6),
        ["reasoning56", "machine56", "learning56", "model56", "token56", "prompt56"],
    ),
    (
        ("reasoning56 machine56 learning56 model56 token56 prompt56", 10),
        ["reasoning56", "machine56", "learning56", "model56", "token56", "prompt56"],
    ),
    (
        ("reasoning56 machine56 learning56 model56 token56 prompt56", 18),
        ["reasoning56", "machine56", "learning56 model56", "token56 prompt56"],
    ),
    (
        ("reasoning56 machine56 learning56 model56 token56 prompt56", 28),
        ["reasoning56 machine56", "learning56 model56 token56", "prompt56"],
    ),
    (
        ("machine56 learning56 model56 token56 prompt56 session56", 6),
        ["machine56", "learning56", "model56", "token56", "prompt56", "session56"],
    ),
    (
        ("machine56 learning56 model56 token56 prompt56 session56", 10),
        ["machine56", "learning56", "model56", "token56", "prompt56", "session56"],
    ),
    (
        ("machine56 learning56 model56 token56 prompt56 session56", 18),
        ["machine56", "learning56 model56", "token56 prompt56", "session56"],
    ),
    (
        ("machine56 learning56 model56 token56 prompt56 session56", 28),
        ["machine56 learning56 model56", "token56 prompt56 session56"],
    ),
    (
        ("learning56 model56 token56 prompt56 session56 library56", 6),
        ["learning56", "model56", "token56", "prompt56", "session56", "library56"],
    ),
    (
        ("learning56 model56 token56 prompt56 session56 library56", 10),
        ["learning56", "model56", "token56", "prompt56", "session56", "library56"],
    ),
    (
        ("learning56 model56 token56 prompt56 session56 library56", 18),
        ["learning56 model56", "token56 prompt56", "session56", "library56"],
    ),
    (
        ("learning56 model56 token56 prompt56 session56 library56", 28),
        ["learning56 model56 token56", "prompt56 session56 library56"],
    ),
    (
        ("model56 token56 prompt56 session56 library56 service56", 6),
        ["model56", "token56", "prompt56", "session56", "library56", "service56"],
    ),
    (
        ("model56 token56 prompt56 session56 library56 service56", 10),
        ["model56", "token56", "prompt56", "session56", "library56", "service56"],
    ),
    (
        ("model56 token56 prompt56 session56 library56 service56", 18),
        ["model56 token56", "prompt56 session56", "library56", "service56"],
    ),
    (
        ("model56 token56 prompt56 session56 library56 service56", 28),
        ["model56 token56 prompt56", "session56 library56", "service56"],
    ),
    (
        ("token56 prompt56 session56 library56 service56 gateway56", 6),
        ["token56", "prompt56", "session56", "library56", "service56", "gateway56"],
    ),
    (
        ("token56 prompt56 session56 library56 service56 gateway56", 10),
        ["token56", "prompt56", "session56", "library56", "service56", "gateway56"],
    ),
    (
        ("token56 prompt56 session56 library56 service56 gateway56", 18),
        ["token56 prompt56", "session56", "library56", "service56", "gateway56"],
    ),
    (
        ("token56 prompt56 session56 library56 service56 gateway56", 28),
        ["token56 prompt56 session56", "library56 service56", "gateway56"],
    ),
    (
        ("prompt56 session56 library56 service56 gateway56 storage56", 6),
        ["prompt56", "session56", "library56", "service56", "gateway56", "storage56"],
    ),
    (
        ("prompt56 session56 library56 service56 gateway56 storage56", 10),
        ["prompt56", "session56", "library56", "service56", "gateway56", "storage56"],
    ),
    (
        ("prompt56 session56 library56 service56 gateway56 storage56", 18),
        ["prompt56 session56", "library56", "service56", "gateway56", "storage56"],
    ),
    (
        ("prompt56 session56 library56 service56 gateway56 storage56", 28),
        ["prompt56 session56 library56", "service56 gateway56", "storage56"],
    ),
    (
        ("session56 library56 service56 gateway56 storage56 network56", 6),
        ["session56", "library56", "service56", "gateway56", "storage56", "network56"],
    ),
    (
        ("session56 library56 service56 gateway56 storage56 network56", 10),
        ["session56", "library56", "service56", "gateway56", "storage56", "network56"],
    ),
    (
        ("session56 library56 service56 gateway56 storage56 network56", 18),
        ["session56", "library56", "service56", "gateway56", "storage56", "network56"],
    ),
    (
        ("session56 library56 service56 gateway56 storage56 network56", 28),
        ["session56 library56", "service56 gateway56", "storage56 network56"],
    ),
    (
        ("library56 service56 gateway56 storage56 network56 latency56", 6),
        ["library56", "service56", "gateway56", "storage56", "network56", "latency56"],
    ),
    (
        ("library56 service56 gateway56 storage56 network56 latency56", 10),
        ["library56", "service56", "gateway56", "storage56", "network56", "latency56"],
    ),
    (
        ("library56 service56 gateway56 storage56 network56 latency56", 18),
        ["library56", "service56", "gateway56", "storage56", "network56", "latency56"],
    ),
    (
        ("library56 service56 gateway56 storage56 network56 latency56", 28),
        ["library56 service56", "gateway56 storage56", "network56 latency56"],
    ),
    (
        ("service56 gateway56 storage56 network56 latency56 buffer56", 6),
        ["service56", "gateway56", "storage56", "network56", "latency56", "buffer56"],
    ),
    (
        ("service56 gateway56 storage56 network56 latency56 buffer56", 10),
        ["service56", "gateway56", "storage56", "network56", "latency56", "buffer56"],
    ),
    (
        ("service56 gateway56 storage56 network56 latency56 buffer56", 18),
        ["service56", "gateway56", "storage56", "network56", "latency56 buffer56"],
    ),
    (
        ("service56 gateway56 storage56 network56 latency56 buffer56", 28),
        ["service56 gateway56", "storage56 network56", "latency56 buffer56"],
    ),
    (
        ("gateway56 storage56 network56 latency56 buffer56 queue56", 6),
        ["gateway56", "storage56", "network56", "latency56", "buffer56", "queue56"],
    ),
    (
        ("gateway56 storage56 network56 latency56 buffer56 queue56", 10),
        ["gateway56", "storage56", "network56", "latency56", "buffer56", "queue56"],
    ),
    (
        ("gateway56 storage56 network56 latency56 buffer56 queue56", 18),
        ["gateway56", "storage56", "network56", "latency56 buffer56", "queue56"],
    ),
    (
        ("gateway56 storage56 network56 latency56 buffer56 queue56", 28),
        ["gateway56 storage56", "network56 latency56 buffer56", "queue56"],
    ),
    (
        ("storage56 network56 latency56 buffer56 queue56 worker56", 6),
        ["storage56", "network56", "latency56", "buffer56", "queue56", "worker56"],
    ),
    (
        ("storage56 network56 latency56 buffer56 queue56 worker56", 10),
        ["storage56", "network56", "latency56", "buffer56", "queue56", "worker56"],
    ),
    (
        ("storage56 network56 latency56 buffer56 queue56 worker56", 18),
        ["storage56", "network56", "latency56 buffer56", "queue56 worker56"],
    ),
    (
        ("storage56 network56 latency56 buffer56 queue56 worker56", 28),
        ["storage56 network56", "latency56 buffer56 queue56", "worker56"],
    ),
    (
        ("network56 latency56 buffer56 queue56 worker56 kernel56", 6),
        ["network56", "latency56", "buffer56", "queue56", "worker56", "kernel56"],
    ),
    (
        ("network56 latency56 buffer56 queue56 worker56 kernel56", 10),
        ["network56", "latency56", "buffer56", "queue56", "worker56", "kernel56"],
    ),
    (
        ("network56 latency56 buffer56 queue56 worker56 kernel56", 18),
        ["network56", "latency56 buffer56", "queue56 worker56", "kernel56"],
    ),
    (
        ("network56 latency56 buffer56 queue56 worker56 kernel56", 28),
        ["network56 latency56 buffer56", "queue56 worker56 kernel56"],
    ),
    (
        ("latency56 buffer56 queue56 worker56 kernel56 signal56", 6),
        ["latency56", "buffer56", "queue56", "worker56", "kernel56", "signal56"],
    ),
    (
        ("latency56 buffer56 queue56 worker56 kernel56 signal56", 10),
        ["latency56", "buffer56", "queue56", "worker56", "kernel56", "signal56"],
    ),
    (
        ("latency56 buffer56 queue56 worker56 kernel56 signal56", 18),
        ["latency56 buffer56", "queue56 worker56", "kernel56 signal56"],
    ),
    (
        ("latency56 buffer56 queue56 worker56 kernel56 signal56", 28),
        ["latency56 buffer56 queue56", "worker56 kernel56 signal56"],
    ),
    (
        ("buffer56 queue56 worker56 kernel56 signal56 packet56", 6),
        ["buffer56", "queue56", "worker56", "kernel56", "signal56", "packet56"],
    ),
    (
        ("buffer56 queue56 worker56 kernel56 signal56 packet56", 10),
        ["buffer56", "queue56", "worker56", "kernel56", "signal56", "packet56"],
    ),
    (
        ("buffer56 queue56 worker56 kernel56 signal56 packet56", 18),
        ["buffer56 queue56", "worker56 kernel56", "signal56 packet56"],
    ),
    (
        ("buffer56 queue56 worker56 kernel56 signal56 packet56", 28),
        ["buffer56 queue56 worker56", "kernel56 signal56 packet56"],
    ),
    (
        ("queue56 worker56 kernel56 signal56 packet56 router56", 6),
        ["queue56", "worker56", "kernel56", "signal56", "packet56", "router56"],
    ),
    (
        ("queue56 worker56 kernel56 signal56 packet56 router56", 10),
        ["queue56", "worker56", "kernel56", "signal56", "packet56", "router56"],
    ),
    (
        ("queue56 worker56 kernel56 signal56 packet56 router56", 18),
        ["queue56 worker56", "kernel56 signal56", "packet56 router56"],
    ),
    (
        ("queue56 worker56 kernel56 signal56 packet56 router56", 28),
        ["queue56 worker56 kernel56", "signal56 packet56 router56"],
    ),
    (
        ("worker56 kernel56 signal56 packet56 router56 cluster56", 6),
        ["worker56", "kernel56", "signal56", "packet56", "router56", "cluster56"],
    ),
    (
        ("worker56 kernel56 signal56 packet56 router56 cluster56", 10),
        ["worker56", "kernel56", "signal56", "packet56", "router56", "cluster56"],
    ),
    (
        ("worker56 kernel56 signal56 packet56 router56 cluster56", 18),
        ["worker56 kernel56", "signal56 packet56", "router56 cluster56"],
    ),
    (
        ("worker56 kernel56 signal56 packet56 router56 cluster56", 28),
        ["worker56 kernel56 signal56", "packet56 router56 cluster56"],
    ),
    (
        ("kernel56 signal56 packet56 router56 cluster56 mirror56", 6),
        ["kernel56", "signal56", "packet56", "router56", "cluster56", "mirror56"],
    ),
    (
        ("kernel56 signal56 packet56 router56 cluster56 mirror56", 10),
        ["kernel56", "signal56", "packet56", "router56", "cluster56", "mirror56"],
    ),
    (
        ("kernel56 signal56 packet56 router56 cluster56 mirror56", 18),
        ["kernel56 signal56", "packet56 router56", "cluster56 mirror56"],
    ),
    (
        ("kernel56 signal56 packet56 router56 cluster56 mirror56", 28),
        ["kernel56 signal56 packet56", "router56 cluster56 mirror56"],
    ),
    (
        ("signal56 packet56 router56 cluster56 mirror56 filter56", 6),
        ["signal56", "packet56", "router56", "cluster56", "mirror56", "filter56"],
    ),
    (
        ("signal56 packet56 router56 cluster56 mirror56 filter56", 10),
        ["signal56", "packet56", "router56", "cluster56", "mirror56", "filter56"],
    ),
    (
        ("signal56 packet56 router56 cluster56 mirror56 filter56", 18),
        ["signal56 packet56", "router56 cluster56", "mirror56 filter56"],
    ),
    (
        ("signal56 packet56 router56 cluster56 mirror56 filter56", 28),
        ["signal56 packet56 router56", "cluster56 mirror56 filter56"],
    ),
    (
        ("packet56 router56 cluster56 mirror56 filter56 ranking56", 6),
        ["packet56", "router56", "cluster56", "mirror56", "filter56", "ranking56"],
    ),
    (
        ("packet56 router56 cluster56 mirror56 filter56 ranking56", 10),
        ["packet56", "router56", "cluster56", "mirror56", "filter56", "ranking56"],
    ),
    (
        ("packet56 router56 cluster56 mirror56 filter56 ranking56", 18),
        ["packet56 router56", "cluster56 mirror56", "filter56 ranking56"],
    ),
    (
        ("packet56 router56 cluster56 mirror56 filter56 ranking56", 28),
        ["packet56 router56 cluster56", "mirror56 filter56 ranking56"],
    ),
    (
        ("router56 cluster56 mirror56 filter56 ranking56 encoding56", 6),
        ["router56", "cluster56", "mirror56", "filter56", "ranking56", "encoding56"],
    ),
    (
        ("router56 cluster56 mirror56 filter56 ranking56 encoding56", 10),
        ["router56", "cluster56", "mirror56", "filter56", "ranking56", "encoding56"],
    ),
    (
        ("router56 cluster56 mirror56 filter56 ranking56 encoding56", 18),
        ["router56 cluster56", "mirror56 filter56", "ranking56", "encoding56"],
    ),
    (
        ("router56 cluster56 mirror56 filter56 ranking56 encoding56", 28),
        ["router56 cluster56 mirror56", "filter56 ranking56", "encoding56"],
    ),
    (
        ("cluster56 mirror56 filter56 ranking56 encoding56 mapping56", 6),
        ["cluster56", "mirror56", "filter56", "ranking56", "encoding56", "mapping56"],
    ),
    (
        ("cluster56 mirror56 filter56 ranking56 encoding56 mapping56", 10),
        ["cluster56", "mirror56", "filter56", "ranking56", "encoding56", "mapping56"],
    ),
    (
        ("cluster56 mirror56 filter56 ranking56 encoding56 mapping56", 18),
        ["cluster56 mirror56", "filter56 ranking56", "encoding56", "mapping56"],
    ),
    (
        ("cluster56 mirror56 filter56 ranking56 encoding56 mapping56", 28),
        ["cluster56 mirror56 filter56", "ranking56 encoding56", "mapping56"],
    ),
    (
        ("mirror56 filter56 ranking56 encoding56 mapping56 record56", 6),
        ["mirror56", "filter56", "ranking56", "encoding56", "mapping56", "record56"],
    ),
    (
        ("mirror56 filter56 ranking56 encoding56 mapping56 record56", 10),
        ["mirror56", "filter56", "ranking56", "encoding56", "mapping56", "record56"],
    ),
    (
        ("mirror56 filter56 ranking56 encoding56 mapping56 record56", 18),
        ["mirror56 filter56", "ranking56", "encoding56", "mapping56 record56"],
    ),
    (
        ("mirror56 filter56 ranking56 encoding56 mapping56 record56", 28),
        ["mirror56 filter56 ranking56", "encoding56 mapping56", "record56"],
    ),
    (
        ("filter56 ranking56 encoding56 mapping56 record56 candle56", 6),
        ["filter56", "ranking56", "encoding56", "mapping56", "record56", "candle56"],
    ),
    (
        ("filter56 ranking56 encoding56 mapping56 record56 candle56", 10),
        ["filter56", "ranking56", "encoding56", "mapping56", "record56", "candle56"],
    ),
    (
        ("filter56 ranking56 encoding56 mapping56 record56 candle56", 18),
        ["filter56 ranking56", "encoding56", "mapping56 record56", "candle56"],
    ),
    (
        ("filter56 ranking56 encoding56 mapping56 record56 candle56", 28),
        ["filter56 ranking56", "encoding56 mapping56", "record56 candle56"],
    ),
    (
        ("ranking56 encoding56 mapping56 record56 candle56 thread56", 6),
        ["ranking56", "encoding56", "mapping56", "record56", "candle56", "thread56"],
    ),
    (
        ("ranking56 encoding56 mapping56 record56 candle56 thread56", 10),
        ["ranking56", "encoding56", "mapping56", "record56", "candle56", "thread56"],
    ),
    (
        ("ranking56 encoding56 mapping56 record56 candle56 thread56", 18),
        ["ranking56", "encoding56", "mapping56 record56", "candle56 thread56"],
    ),
    (
        ("ranking56 encoding56 mapping56 record56 candle56 thread56", 28),
        ["ranking56 encoding56", "mapping56 record56 candle56", "thread56"],
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
