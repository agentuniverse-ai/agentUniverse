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
        ("round 730: the quick brown fox jumps over the lazy dog", 4),
        ["round", "730:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 730: the quick brown fox jumps over the lazy dog", 8),
        ["round", "730: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 730: the quick brown fox jumps over the lazy dog", 12),
        ["round 730:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 730: the quick brown fox jumps over the lazy dog", 16),
        ["round 730: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 730: the quick brown fox jumps over the lazy dog", 24),
        ["round 730: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 730: the quick brown fox jumps over the lazy dog", 32),
        ["round 730: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 730: agentuniverse is a framework for multi agents", 4),
        ["round", "730:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 730: agentuniverse is a framework for multi agents", 8),
        ["round", "730:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 730: agentuniverse is a framework for multi agents", 12),
        ["round 730:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 730: agentuniverse is a framework for multi agents", 16),
        ["round 730:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 730: agentuniverse is a framework for multi agents", 24),
        ["round 730: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 730: agentuniverse is a framework for multi agents", 32),
        ["round 730: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 730: knowledge stored as vectors enables retrieval", 4),
        ["round", "730:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 730: knowledge stored as vectors enables retrieval", 8),
        ["round", "730:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 730: knowledge stored as vectors enables retrieval", 12),
        ["round 730:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 730: knowledge stored as vectors enables retrieval", 16),
        ["round 730:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 730: knowledge stored as vectors enables retrieval", 24),
        ["round 730: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 730: knowledge stored as vectors enables retrieval", 32),
        ["round 730: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 730: the processor reads the record then stops", 4),
        ["round", "730:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 730: the processor reads the record then stops", 8),
        ["round", "730: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 730: the processor reads the record then stops", 12),
        ["round 730:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 730: the processor reads the record then stops", 16),
        ["round 730: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 730: the processor reads the record then stops", 24),
        ["round 730: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 730: the processor reads the record then stops", 32),
        ["round 730: the processor reads", "the record then stops"],
    ),
    (
        ("round 730: a worker pulls the next task from the queue", 4),
        ["round", "730:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 730: a worker pulls the next task from the queue", 8),
        ["round", "730: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 730: a worker pulls the next task from the queue", 12),
        ["round 730: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 730: a worker pulls the next task from the queue", 16),
        ["round 730: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 730: a worker pulls the next task from the queue", 24),
        ["round 730: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 730: a worker pulls the next task from the queue", 32),
        ["round 730: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 730: signals travel through the network layer", 4),
        ["round", "730:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 730: signals travel through the network layer", 8),
        ["round", "730:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 730: signals travel through the network layer", 12),
        ["round 730:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 730: signals travel through the network layer", 16),
        ["round 730:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 730: signals travel through the network layer", 24),
        ["round 730: signals", "travel through the", "network layer"],
    ),
    (
        ("round 730: signals travel through the network layer", 32),
        ["round 730: signals travel", "through the network layer"],
    ),
    (
        ("round 730: the gateway routes each request by policy", 4),
        ["round", "730:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 730: the gateway routes each request by policy", 8),
        ["round", "730: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 730: the gateway routes each request by policy", 12),
        ["round 730:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 730: the gateway routes each request by policy", 16),
        ["round 730: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 730: the gateway routes each request by policy", 24),
        ["round 730: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 730: the gateway routes each request by policy", 32),
        ["round 730: the gateway routes", "each request by policy"],
    ),
    (
        ("round 730: memory grows until the buffer is full", 4),
        ["round", "730:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 730: memory grows until the buffer is full", 8),
        ["round", "730:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 730: memory grows until the buffer is full", 12),
        ["round 730:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 730: memory grows until the buffer is full", 16),
        ["round 730:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 730: memory grows until the buffer is full", 24), ["round 730: memory grows", "until the buffer is full"]),
    (("round 730: memory grows until the buffer is full", 32), ["round 730: memory grows until", "the buffer is full"]),
    (
        ("round 730: the cluster mirrors every packet twice", 4),
        ["round", "730:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 730: the cluster mirrors every packet twice", 8),
        ["round", "730: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 730: the cluster mirrors every packet twice", 12),
        ["round 730:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 730: the cluster mirrors every packet twice", 16),
        ["round 730: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 730: the cluster mirrors every packet twice", 24),
        ["round 730: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 730: the cluster mirrors every packet twice", 32),
        ["round 730: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 730: ranking uses tokens learned from the corpus", 4),
        ["round", "730:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 730: ranking uses tokens learned from the corpus", 8),
        ["round", "730:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 730: ranking uses tokens learned from the corpus", 12),
        ["round 730:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 730: ranking uses tokens learned from the corpus", 16),
        ["round 730:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 730: ranking uses tokens learned from the corpus", 24),
        ["round 730: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 730: ranking uses tokens learned from the corpus", 32),
        ["round 730: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 730: a long session ends when the candle dies", 4),
        ["round", "730:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 730: a long session ends when the candle dies", 8),
        ["round", "730: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 730: a long session ends when the candle dies", 12),
        ["round 730: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 730: a long session ends when the candle dies", 16),
        ["round 730: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 730: a long session ends when the candle dies", 24),
        ["round 730: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 730: a long session ends when the candle dies", 32),
        ["round 730: a long session ends", "when the candle dies"],
    ),
    (
        ("round 730: encode the prompt then map the result", 4),
        ["round", "730:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 730: encode the prompt then map the result", 8),
        ["round", "730:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 730: encode the prompt then map the result", 12),
        ["round 730:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 730: encode the prompt then map the result", 16),
        ["round 730:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 730: encode the prompt then map the result", 24),
        ["round 730: encode the", "prompt then map the", "result"],
    ),
    (("round 730: encode the prompt then map the result", 32), ["round 730: encode the prompt", "then map the result"]),
    (
        ("round 730: the kernel wakes the worker at dawn", 4),
        ["round", "730:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 730: the kernel wakes the worker at dawn", 8),
        ["round", "730: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 730: the kernel wakes the worker at dawn", 12),
        ["round 730:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 730: the kernel wakes the worker at dawn", 16), ["round 730: the", "kernel wakes the", "worker at dawn"]),
    (("round 730: the kernel wakes the worker at dawn", 24), ["round 730: the kernel", "wakes the worker at dawn"]),
    (("round 730: the kernel wakes the worker at dawn", 32), ["round 730: the kernel wakes the", "worker at dawn"]),
    (
        ("round 730: service latency drops after the patch", 4),
        ["round", "730:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 730: service latency drops after the patch", 8),
        ["round", "730:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 730: service latency drops after the patch", 12),
        ["round 730:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 730: service latency drops after the patch", 16),
        ["round 730:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 730: service latency drops after the patch", 24),
        ["round 730: service", "latency drops after the", "patch"],
    ),
    (("round 730: service latency drops after the patch", 32), ["round 730: service latency drops", "after the patch"]),
    (
        ("round 730: the library caches every vector it sees", 4),
        ["round", "730:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 730: the library caches every vector it sees", 8),
        ["round", "730: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 730: the library caches every vector it sees", 12),
        ["round 730:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 730: the library caches every vector it sees", 16),
        ["round 730: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 730: the library caches every vector it sees", 24),
        ["round 730: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 730: the library caches every vector it sees", 32),
        ["round 730: the library caches", "every vector it sees"],
    ),
    (
        ("round 730: agents argue then the debate resolves", 4),
        ["round", "730:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 730: agents argue then the debate resolves", 8),
        ["round", "730:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 730: agents argue then the debate resolves", 12),
        ["round 730:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 730: agents argue then the debate resolves", 16),
        ["round 730:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 730: agents argue then the debate resolves", 24), ["round 730: agents argue", "then the debate resolves"]),
    (("round 730: agents argue then the debate resolves", 32), ["round 730: agents argue then the", "debate resolves"]),
    (
        ("round 730: the filter keeps only strong matches", 4),
        ["round", "730:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 730: the filter keeps only strong matches", 8),
        ["round", "730: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 730: the filter keeps only strong matches", 12),
        ["round 730:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 730: the filter keeps only strong matches", 16),
        ["round 730: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 730: the filter keeps only strong matches", 24),
        ["round 730: the filter", "keeps only strong", "matches"],
    ),
    (("round 730: the filter keeps only strong matches", 32), ["round 730: the filter keeps only", "strong matches"]),
    (
        ("round 730: the model answers with a short reply", 4),
        ["round", "730:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 730: the model answers with a short reply", 8),
        ["round", "730: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 730: the model answers with a short reply", 12),
        ["round 730:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 730: the model answers with a short reply", 16),
        ["round 730: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 730: the model answers with a short reply", 24),
        ["round 730: the model", "answers with a short", "reply"],
    ),
    (("round 730: the model answers with a short reply", 32), ["round 730: the model answers", "with a short reply"]),
    (
        ("round 730: the recorder stores the reasoning trace", 4),
        ["round", "730:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 730: the recorder stores the reasoning trace", 8),
        ["round", "730: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 730: the recorder stores the reasoning trace", 12),
        ["round 730:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 730: the recorder stores the reasoning trace", 16),
        ["round 730: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 730: the recorder stores the reasoning trace", 24),
        ["round 730: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 730: the recorder stores the reasoning trace", 32),
        ["round 730: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 730: the angel watches the processor run", 4),
        ["round", "730:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 730: the angel watches the processor run", 8),
        ["round", "730: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 730: the angel watches the processor run", 12),
        ["round 730:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 730: the angel watches the processor run", 16),
        ["round 730: the", "angel watches", "the processor", "run"],
    ),
    (("round 730: the angel watches the processor run", 24), ["round 730: the angel", "watches the processor", "run"]),
    (("round 730: the angel watches the processor run", 32), ["round 730: the angel watches the", "processor run"]),
    (
        ("round 730: angle of the vector decides the match", 4),
        ["round", "730:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 730: angle of the vector decides the match", 8),
        ["round", "730:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 730: angle of the vector decides the match", 12),
        ["round 730:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 730: angle of the vector decides the match", 16),
        ["round 730: angle", "of the vector", "decides the", "match"],
    ),
    (("round 730: angle of the vector decides the match", 24), ["round 730: angle of the", "vector decides the match"]),
    (("round 730: angle of the vector decides the match", 32), ["round 730: angle of the vector", "decides the match"]),
    (
        ("round 730: the candle burns twice as long at night", 4),
        ["round", "730:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 730: the candle burns twice as long at night", 8),
        ["round", "730: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 730: the candle burns twice as long at night", 12),
        ["round 730:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 730: the candle burns twice as long at night", 16),
        ["round 730: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 730: the candle burns twice as long at night", 24),
        ["round 730: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 730: the candle burns twice as long at night", 32),
        ["round 730: the candle burns", "twice as long at night"],
    ),
    (
        ("round 730: a mirror of the universe in one line", 4),
        ["round", "730:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 730: a mirror of the universe in one line", 8),
        ["round", "730: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 730: a mirror of the universe in one line", 12),
        ["round 730: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 730: a mirror of the universe in one line", 16),
        ["round 730: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 730: a mirror of the universe in one line", 24), ["round 730: a mirror of", "the universe in one line"]),
    (("round 730: a mirror of the universe in one line", 32), ["round 730: a mirror of the", "universe in one line"]),
    (
        ("round 730: the queue drains before the storm", 4),
        ["round", "730:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 730: the queue drains before the storm", 8),
        ["round", "730: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 730: the queue drains before the storm", 12),
        ["round 730:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 730: the queue drains before the storm", 16), ["round 730: the", "queue drains", "before the storm"]),
    (("round 730: the queue drains before the storm", 24), ["round 730: the queue", "drains before the storm"]),
    (("round 730: the queue drains before the storm", 32), ["round 730: the queue drains", "before the storm"]),
    (
        ("kitten730 sitting730 agent730 angle730 universe730 memory730", 6),
        ["kitten730", "sitting730", "agent730", "angle730", "universe730", "memory730"],
    ),
    (
        ("kitten730 sitting730 agent730 angle730 universe730 memory730", 10),
        ["kitten730", "sitting730", "agent730", "angle730", "universe730", "memory730"],
    ),
    (
        ("kitten730 sitting730 agent730 angle730 universe730 memory730", 18),
        ["kitten730", "sitting730", "agent730 angle730", "universe730", "memory730"],
    ),
    (
        ("kitten730 sitting730 agent730 angle730 universe730 memory730", 28),
        ["kitten730 sitting730", "agent730 angle730", "universe730 memory730"],
    ),
    (
        ("sitting730 agent730 angle730 universe730 memory730 stream730", 6),
        ["sitting730", "agent730", "angle730", "universe730", "memory730", "stream730"],
    ),
    (
        ("sitting730 agent730 angle730 universe730 memory730 stream730", 10),
        ["sitting730", "agent730", "angle730", "universe730", "memory730", "stream730"],
    ),
    (
        ("sitting730 agent730 angle730 universe730 memory730 stream730", 18),
        ["sitting730", "agent730 angle730", "universe730", "memory730", "stream730"],
    ),
    (
        ("sitting730 agent730 angle730 universe730 memory730 stream730", 28),
        ["sitting730 agent730 angle730", "universe730 memory730", "stream730"],
    ),
    (
        ("agent730 angle730 universe730 memory730 stream730 context730", 6),
        ["agent730", "angle730", "universe730", "memory730", "stream730", "context730"],
    ),
    (
        ("agent730 angle730 universe730 memory730 stream730 context730", 10),
        ["agent730", "angle730", "universe730", "memory730", "stream730", "context730"],
    ),
    (
        ("agent730 angle730 universe730 memory730 stream730 context730", 18),
        ["agent730 angle730", "universe730", "memory730", "stream730", "context730"],
    ),
    (
        ("agent730 angle730 universe730 memory730 stream730 context730", 28),
        ["agent730 angle730", "universe730 memory730", "stream730 context730"],
    ),
    (
        ("angle730 universe730 memory730 stream730 context730 knowledge730", 6),
        ["angle730", "universe730", "memory730", "stream730", "context730", "knowledge730"],
    ),
    (
        ("angle730 universe730 memory730 stream730 context730 knowledge730", 10),
        ["angle730", "universe730", "memory730", "stream730", "context730", "knowledge730"],
    ),
    (
        ("angle730 universe730 memory730 stream730 context730 knowledge730", 18),
        ["angle730", "universe730", "memory730", "stream730", "context730", "knowledge730"],
    ),
    (
        ("angle730 universe730 memory730 stream730 context730 knowledge730", 28),
        ["angle730 universe730", "memory730 stream730", "context730 knowledge730"],
    ),
    (
        ("universe730 memory730 stream730 context730 knowledge730 vector730", 6),
        ["universe730", "memory730", "stream730", "context730", "knowledge730", "vector730"],
    ),
    (
        ("universe730 memory730 stream730 context730 knowledge730 vector730", 10),
        ["universe730", "memory730", "stream730", "context730", "knowledge730", "vector730"],
    ),
    (
        ("universe730 memory730 stream730 context730 knowledge730 vector730", 18),
        ["universe730", "memory730", "stream730", "context730", "knowledge730", "vector730"],
    ),
    (
        ("universe730 memory730 stream730 context730 knowledge730 vector730", 28),
        ["universe730 memory730", "stream730 context730", "knowledge730 vector730"],
    ),
    (
        ("memory730 stream730 context730 knowledge730 vector730 processor730", 6),
        ["memory730", "stream730", "context730", "knowledge730", "vector730", "processor730"],
    ),
    (
        ("memory730 stream730 context730 knowledge730 vector730 processor730", 10),
        ["memory730", "stream730", "context730", "knowledge730", "vector730", "processor730"],
    ),
    (
        ("memory730 stream730 context730 knowledge730 vector730 processor730", 18),
        ["memory730", "stream730", "context730", "knowledge730", "vector730", "processor730"],
    ),
    (
        ("memory730 stream730 context730 knowledge730 vector730 processor730", 28),
        ["memory730 stream730", "context730 knowledge730", "vector730 processor730"],
    ),
    (
        ("stream730 context730 knowledge730 vector730 processor730 reasoning730", 6),
        ["stream730", "context730", "knowledge730", "vector730", "processor730", "reasoning730"],
    ),
    (
        ("stream730 context730 knowledge730 vector730 processor730 reasoning730", 10),
        ["stream730", "context730", "knowledge730", "vector730", "processor730", "reasoning730"],
    ),
    (
        ("stream730 context730 knowledge730 vector730 processor730 reasoning730", 18),
        ["stream730", "context730", "knowledge730", "vector730", "processor730", "reasoning730"],
    ),
    (
        ("stream730 context730 knowledge730 vector730 processor730 reasoning730", 28),
        ["stream730 context730", "knowledge730 vector730", "processor730 reasoning730"],
    ),
    (
        ("context730 knowledge730 vector730 processor730 reasoning730 machine730", 6),
        ["context730", "knowledge730", "vector730", "processor730", "reasoning730", "machine730"],
    ),
    (
        ("context730 knowledge730 vector730 processor730 reasoning730 machine730", 10),
        ["context730", "knowledge730", "vector730", "processor730", "reasoning730", "machine730"],
    ),
    (
        ("context730 knowledge730 vector730 processor730 reasoning730 machine730", 18),
        ["context730", "knowledge730", "vector730", "processor730", "reasoning730", "machine730"],
    ),
    (
        ("context730 knowledge730 vector730 processor730 reasoning730 machine730", 28),
        ["context730 knowledge730", "vector730 processor730", "reasoning730 machine730"],
    ),
    (
        ("knowledge730 vector730 processor730 reasoning730 machine730 learning730", 6),
        ["knowledge730", "vector730", "processor730", "reasoning730", "machine730", "learning730"],
    ),
    (
        ("knowledge730 vector730 processor730 reasoning730 machine730 learning730", 10),
        ["knowledge730", "vector730", "processor730", "reasoning730", "machine730", "learning730"],
    ),
    (
        ("knowledge730 vector730 processor730 reasoning730 machine730 learning730", 18),
        ["knowledge730", "vector730", "processor730", "reasoning730", "machine730", "learning730"],
    ),
    (
        ("knowledge730 vector730 processor730 reasoning730 machine730 learning730", 28),
        ["knowledge730 vector730", "processor730 reasoning730", "machine730 learning730"],
    ),
    (
        ("vector730 processor730 reasoning730 machine730 learning730 model730", 6),
        ["vector730", "processor730", "reasoning730", "machine730", "learning730", "model730"],
    ),
    (
        ("vector730 processor730 reasoning730 machine730 learning730 model730", 10),
        ["vector730", "processor730", "reasoning730", "machine730", "learning730", "model730"],
    ),
    (
        ("vector730 processor730 reasoning730 machine730 learning730 model730", 18),
        ["vector730", "processor730", "reasoning730", "machine730", "learning730", "model730"],
    ),
    (
        ("vector730 processor730 reasoning730 machine730 learning730 model730", 28),
        ["vector730 processor730", "reasoning730 machine730", "learning730 model730"],
    ),
    (
        ("processor730 reasoning730 machine730 learning730 model730 token730", 6),
        ["processor730", "reasoning730", "machine730", "learning730", "model730", "token730"],
    ),
    (
        ("processor730 reasoning730 machine730 learning730 model730 token730", 10),
        ["processor730", "reasoning730", "machine730", "learning730", "model730", "token730"],
    ),
    (
        ("processor730 reasoning730 machine730 learning730 model730 token730", 18),
        ["processor730", "reasoning730", "machine730", "learning730", "model730 token730"],
    ),
    (
        ("processor730 reasoning730 machine730 learning730 model730 token730", 28),
        ["processor730 reasoning730", "machine730 learning730", "model730 token730"],
    ),
    (
        ("reasoning730 machine730 learning730 model730 token730 prompt730", 6),
        ["reasoning730", "machine730", "learning730", "model730", "token730", "prompt730"],
    ),
    (
        ("reasoning730 machine730 learning730 model730 token730 prompt730", 10),
        ["reasoning730", "machine730", "learning730", "model730", "token730", "prompt730"],
    ),
    (
        ("reasoning730 machine730 learning730 model730 token730 prompt730", 18),
        ["reasoning730", "machine730", "learning730", "model730 token730", "prompt730"],
    ),
    (
        ("reasoning730 machine730 learning730 model730 token730 prompt730", 28),
        ["reasoning730 machine730", "learning730 model730", "token730 prompt730"],
    ),
    (
        ("machine730 learning730 model730 token730 prompt730 session730", 6),
        ["machine730", "learning730", "model730", "token730", "prompt730", "session730"],
    ),
    (
        ("machine730 learning730 model730 token730 prompt730 session730", 10),
        ["machine730", "learning730", "model730", "token730", "prompt730", "session730"],
    ),
    (
        ("machine730 learning730 model730 token730 prompt730 session730", 18),
        ["machine730", "learning730", "model730 token730", "prompt730", "session730"],
    ),
    (
        ("machine730 learning730 model730 token730 prompt730 session730", 28),
        ["machine730 learning730", "model730 token730 prompt730", "session730"],
    ),
    (
        ("learning730 model730 token730 prompt730 session730 library730", 6),
        ["learning730", "model730", "token730", "prompt730", "session730", "library730"],
    ),
    (
        ("learning730 model730 token730 prompt730 session730 library730", 10),
        ["learning730", "model730", "token730", "prompt730", "session730", "library730"],
    ),
    (
        ("learning730 model730 token730 prompt730 session730 library730", 18),
        ["learning730", "model730 token730", "prompt730", "session730", "library730"],
    ),
    (
        ("learning730 model730 token730 prompt730 session730 library730", 28),
        ["learning730 model730", "token730 prompt730", "session730 library730"],
    ),
    (
        ("model730 token730 prompt730 session730 library730 service730", 6),
        ["model730", "token730", "prompt730", "session730", "library730", "service730"],
    ),
    (
        ("model730 token730 prompt730 session730 library730 service730", 10),
        ["model730", "token730", "prompt730", "session730", "library730", "service730"],
    ),
    (
        ("model730 token730 prompt730 session730 library730 service730", 18),
        ["model730 token730", "prompt730", "session730", "library730", "service730"],
    ),
    (
        ("model730 token730 prompt730 session730 library730 service730", 28),
        ["model730 token730 prompt730", "session730 library730", "service730"],
    ),
    (
        ("token730 prompt730 session730 library730 service730 gateway730", 6),
        ["token730", "prompt730", "session730", "library730", "service730", "gateway730"],
    ),
    (
        ("token730 prompt730 session730 library730 service730 gateway730", 10),
        ["token730", "prompt730", "session730", "library730", "service730", "gateway730"],
    ),
    (
        ("token730 prompt730 session730 library730 service730 gateway730", 18),
        ["token730 prompt730", "session730", "library730", "service730", "gateway730"],
    ),
    (
        ("token730 prompt730 session730 library730 service730 gateway730", 28),
        ["token730 prompt730", "session730 library730", "service730 gateway730"],
    ),
    (
        ("prompt730 session730 library730 service730 gateway730 storage730", 6),
        ["prompt730", "session730", "library730", "service730", "gateway730", "storage730"],
    ),
    (
        ("prompt730 session730 library730 service730 gateway730 storage730", 10),
        ["prompt730", "session730", "library730", "service730", "gateway730", "storage730"],
    ),
    (
        ("prompt730 session730 library730 service730 gateway730 storage730", 18),
        ["prompt730", "session730", "library730", "service730", "gateway730", "storage730"],
    ),
    (
        ("prompt730 session730 library730 service730 gateway730 storage730", 28),
        ["prompt730 session730", "library730 service730", "gateway730 storage730"],
    ),
    (
        ("session730 library730 service730 gateway730 storage730 network730", 6),
        ["session730", "library730", "service730", "gateway730", "storage730", "network730"],
    ),
    (
        ("session730 library730 service730 gateway730 storage730 network730", 10),
        ["session730", "library730", "service730", "gateway730", "storage730", "network730"],
    ),
    (
        ("session730 library730 service730 gateway730 storage730 network730", 18),
        ["session730", "library730", "service730", "gateway730", "storage730", "network730"],
    ),
    (
        ("session730 library730 service730 gateway730 storage730 network730", 28),
        ["session730 library730", "service730 gateway730", "storage730 network730"],
    ),
    (
        ("library730 service730 gateway730 storage730 network730 latency730", 6),
        ["library730", "service730", "gateway730", "storage730", "network730", "latency730"],
    ),
    (
        ("library730 service730 gateway730 storage730 network730 latency730", 10),
        ["library730", "service730", "gateway730", "storage730", "network730", "latency730"],
    ),
    (
        ("library730 service730 gateway730 storage730 network730 latency730", 18),
        ["library730", "service730", "gateway730", "storage730", "network730", "latency730"],
    ),
    (
        ("library730 service730 gateway730 storage730 network730 latency730", 28),
        ["library730 service730", "gateway730 storage730", "network730 latency730"],
    ),
    (
        ("service730 gateway730 storage730 network730 latency730 buffer730", 6),
        ["service730", "gateway730", "storage730", "network730", "latency730", "buffer730"],
    ),
    (
        ("service730 gateway730 storage730 network730 latency730 buffer730", 10),
        ["service730", "gateway730", "storage730", "network730", "latency730", "buffer730"],
    ),
    (
        ("service730 gateway730 storage730 network730 latency730 buffer730", 18),
        ["service730", "gateway730", "storage730", "network730", "latency730", "buffer730"],
    ),
    (
        ("service730 gateway730 storage730 network730 latency730 buffer730", 28),
        ["service730 gateway730", "storage730 network730", "latency730 buffer730"],
    ),
    (
        ("gateway730 storage730 network730 latency730 buffer730 queue730", 6),
        ["gateway730", "storage730", "network730", "latency730", "buffer730", "queue730"],
    ),
    (
        ("gateway730 storage730 network730 latency730 buffer730 queue730", 10),
        ["gateway730", "storage730", "network730", "latency730", "buffer730", "queue730"],
    ),
    (
        ("gateway730 storage730 network730 latency730 buffer730 queue730", 18),
        ["gateway730", "storage730", "network730", "latency730", "buffer730 queue730"],
    ),
    (
        ("gateway730 storage730 network730 latency730 buffer730 queue730", 28),
        ["gateway730 storage730", "network730 latency730", "buffer730 queue730"],
    ),
    (
        ("storage730 network730 latency730 buffer730 queue730 worker730", 6),
        ["storage730", "network730", "latency730", "buffer730", "queue730", "worker730"],
    ),
    (
        ("storage730 network730 latency730 buffer730 queue730 worker730", 10),
        ["storage730", "network730", "latency730", "buffer730", "queue730", "worker730"],
    ),
    (
        ("storage730 network730 latency730 buffer730 queue730 worker730", 18),
        ["storage730", "network730", "latency730", "buffer730 queue730", "worker730"],
    ),
    (
        ("storage730 network730 latency730 buffer730 queue730 worker730", 28),
        ["storage730 network730", "latency730 buffer730", "queue730 worker730"],
    ),
    (
        ("network730 latency730 buffer730 queue730 worker730 kernel730", 6),
        ["network730", "latency730", "buffer730", "queue730", "worker730", "kernel730"],
    ),
    (
        ("network730 latency730 buffer730 queue730 worker730 kernel730", 10),
        ["network730", "latency730", "buffer730", "queue730", "worker730", "kernel730"],
    ),
    (
        ("network730 latency730 buffer730 queue730 worker730 kernel730", 18),
        ["network730", "latency730", "buffer730 queue730", "worker730", "kernel730"],
    ),
    (
        ("network730 latency730 buffer730 queue730 worker730 kernel730", 28),
        ["network730 latency730", "buffer730 queue730 worker730", "kernel730"],
    ),
    (
        ("latency730 buffer730 queue730 worker730 kernel730 signal730", 6),
        ["latency730", "buffer730", "queue730", "worker730", "kernel730", "signal730"],
    ),
    (
        ("latency730 buffer730 queue730 worker730 kernel730 signal730", 10),
        ["latency730", "buffer730", "queue730", "worker730", "kernel730", "signal730"],
    ),
    (
        ("latency730 buffer730 queue730 worker730 kernel730 signal730", 18),
        ["latency730", "buffer730 queue730", "worker730", "kernel730", "signal730"],
    ),
    (
        ("latency730 buffer730 queue730 worker730 kernel730 signal730", 28),
        ["latency730 buffer730", "queue730 worker730 kernel730", "signal730"],
    ),
    (
        ("buffer730 queue730 worker730 kernel730 signal730 packet730", 6),
        ["buffer730", "queue730", "worker730", "kernel730", "signal730", "packet730"],
    ),
    (
        ("buffer730 queue730 worker730 kernel730 signal730 packet730", 10),
        ["buffer730", "queue730", "worker730", "kernel730", "signal730", "packet730"],
    ),
    (
        ("buffer730 queue730 worker730 kernel730 signal730 packet730", 18),
        ["buffer730 queue730", "worker730", "kernel730", "signal730", "packet730"],
    ),
    (
        ("buffer730 queue730 worker730 kernel730 signal730 packet730", 28),
        ["buffer730 queue730 worker730", "kernel730 signal730", "packet730"],
    ),
    (
        ("queue730 worker730 kernel730 signal730 packet730 router730", 6),
        ["queue730", "worker730", "kernel730", "signal730", "packet730", "router730"],
    ),
    (
        ("queue730 worker730 kernel730 signal730 packet730 router730", 10),
        ["queue730", "worker730", "kernel730", "signal730", "packet730", "router730"],
    ),
    (
        ("queue730 worker730 kernel730 signal730 packet730 router730", 18),
        ["queue730 worker730", "kernel730", "signal730", "packet730", "router730"],
    ),
    (
        ("queue730 worker730 kernel730 signal730 packet730 router730", 28),
        ["queue730 worker730 kernel730", "signal730 packet730", "router730"],
    ),
    (
        ("worker730 kernel730 signal730 packet730 router730 cluster730", 6),
        ["worker730", "kernel730", "signal730", "packet730", "router730", "cluster730"],
    ),
    (
        ("worker730 kernel730 signal730 packet730 router730 cluster730", 10),
        ["worker730", "kernel730", "signal730", "packet730", "router730", "cluster730"],
    ),
    (
        ("worker730 kernel730 signal730 packet730 router730 cluster730", 18),
        ["worker730", "kernel730", "signal730", "packet730", "router730", "cluster730"],
    ),
    (
        ("worker730 kernel730 signal730 packet730 router730 cluster730", 28),
        ["worker730 kernel730", "signal730 packet730", "router730 cluster730"],
    ),
    (
        ("kernel730 signal730 packet730 router730 cluster730 mirror730", 6),
        ["kernel730", "signal730", "packet730", "router730", "cluster730", "mirror730"],
    ),
    (
        ("kernel730 signal730 packet730 router730 cluster730 mirror730", 10),
        ["kernel730", "signal730", "packet730", "router730", "cluster730", "mirror730"],
    ),
    (
        ("kernel730 signal730 packet730 router730 cluster730 mirror730", 18),
        ["kernel730", "signal730", "packet730", "router730", "cluster730", "mirror730"],
    ),
    (
        ("kernel730 signal730 packet730 router730 cluster730 mirror730", 28),
        ["kernel730 signal730", "packet730 router730", "cluster730 mirror730"],
    ),
    (
        ("signal730 packet730 router730 cluster730 mirror730 filter730", 6),
        ["signal730", "packet730", "router730", "cluster730", "mirror730", "filter730"],
    ),
    (
        ("signal730 packet730 router730 cluster730 mirror730 filter730", 10),
        ["signal730", "packet730", "router730", "cluster730", "mirror730", "filter730"],
    ),
    (
        ("signal730 packet730 router730 cluster730 mirror730 filter730", 18),
        ["signal730", "packet730", "router730", "cluster730", "mirror730", "filter730"],
    ),
    (
        ("signal730 packet730 router730 cluster730 mirror730 filter730", 28),
        ["signal730 packet730", "router730 cluster730", "mirror730 filter730"],
    ),
    (
        ("packet730 router730 cluster730 mirror730 filter730 ranking730", 6),
        ["packet730", "router730", "cluster730", "mirror730", "filter730", "ranking730"],
    ),
    (
        ("packet730 router730 cluster730 mirror730 filter730 ranking730", 10),
        ["packet730", "router730", "cluster730", "mirror730", "filter730", "ranking730"],
    ),
    (
        ("packet730 router730 cluster730 mirror730 filter730 ranking730", 18),
        ["packet730", "router730", "cluster730", "mirror730", "filter730", "ranking730"],
    ),
    (
        ("packet730 router730 cluster730 mirror730 filter730 ranking730", 28),
        ["packet730 router730", "cluster730 mirror730", "filter730 ranking730"],
    ),
    (
        ("router730 cluster730 mirror730 filter730 ranking730 encoding730", 6),
        ["router730", "cluster730", "mirror730", "filter730", "ranking730", "encoding730"],
    ),
    (
        ("router730 cluster730 mirror730 filter730 ranking730 encoding730", 10),
        ["router730", "cluster730", "mirror730", "filter730", "ranking730", "encoding730"],
    ),
    (
        ("router730 cluster730 mirror730 filter730 ranking730 encoding730", 18),
        ["router730", "cluster730", "mirror730", "filter730", "ranking730", "encoding730"],
    ),
    (
        ("router730 cluster730 mirror730 filter730 ranking730 encoding730", 28),
        ["router730 cluster730", "mirror730 filter730", "ranking730 encoding730"],
    ),
    (
        ("cluster730 mirror730 filter730 ranking730 encoding730 mapping730", 6),
        ["cluster730", "mirror730", "filter730", "ranking730", "encoding730", "mapping730"],
    ),
    (
        ("cluster730 mirror730 filter730 ranking730 encoding730 mapping730", 10),
        ["cluster730", "mirror730", "filter730", "ranking730", "encoding730", "mapping730"],
    ),
    (
        ("cluster730 mirror730 filter730 ranking730 encoding730 mapping730", 18),
        ["cluster730", "mirror730", "filter730", "ranking730", "encoding730", "mapping730"],
    ),
    (
        ("cluster730 mirror730 filter730 ranking730 encoding730 mapping730", 28),
        ["cluster730 mirror730", "filter730 ranking730", "encoding730 mapping730"],
    ),
    (
        ("mirror730 filter730 ranking730 encoding730 mapping730 record730", 6),
        ["mirror730", "filter730", "ranking730", "encoding730", "mapping730", "record730"],
    ),
    (
        ("mirror730 filter730 ranking730 encoding730 mapping730 record730", 10),
        ["mirror730", "filter730", "ranking730", "encoding730", "mapping730", "record730"],
    ),
    (
        ("mirror730 filter730 ranking730 encoding730 mapping730 record730", 18),
        ["mirror730", "filter730", "ranking730", "encoding730", "mapping730", "record730"],
    ),
    (
        ("mirror730 filter730 ranking730 encoding730 mapping730 record730", 28),
        ["mirror730 filter730", "ranking730 encoding730", "mapping730 record730"],
    ),
    (
        ("filter730 ranking730 encoding730 mapping730 record730 candle730", 6),
        ["filter730", "ranking730", "encoding730", "mapping730", "record730", "candle730"],
    ),
    (
        ("filter730 ranking730 encoding730 mapping730 record730 candle730", 10),
        ["filter730", "ranking730", "encoding730", "mapping730", "record730", "candle730"],
    ),
    (
        ("filter730 ranking730 encoding730 mapping730 record730 candle730", 18),
        ["filter730", "ranking730", "encoding730", "mapping730", "record730", "candle730"],
    ),
    (
        ("filter730 ranking730 encoding730 mapping730 record730 candle730", 28),
        ["filter730 ranking730", "encoding730 mapping730", "record730 candle730"],
    ),
    (
        ("ranking730 encoding730 mapping730 record730 candle730 thread730", 6),
        ["ranking730", "encoding730", "mapping730", "record730", "candle730", "thread730"],
    ),
    (
        ("ranking730 encoding730 mapping730 record730 candle730 thread730", 10),
        ["ranking730", "encoding730", "mapping730", "record730", "candle730", "thread730"],
    ),
    (
        ("ranking730 encoding730 mapping730 record730 candle730 thread730", 18),
        ["ranking730", "encoding730", "mapping730", "record730", "candle730", "thread730"],
    ),
    (
        ("ranking730 encoding730 mapping730 record730 candle730 thread730", 28),
        ["ranking730 encoding730", "mapping730 record730", "candle730 thread730"],
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
