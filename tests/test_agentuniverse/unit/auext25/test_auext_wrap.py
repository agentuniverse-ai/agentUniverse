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
        ("round 25: the quick brown fox jumps over the lazy dog", 4),
        ["round", "25:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 25: the quick brown fox jumps over the lazy dog", 8),
        ["round", "25: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 25: the quick brown fox jumps over the lazy dog", 12),
        ["round 25:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 25: the quick brown fox jumps over the lazy dog", 16),
        ["round 25: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 25: the quick brown fox jumps over the lazy dog", 24),
        ["round 25: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 25: the quick brown fox jumps over the lazy dog", 32),
        ["round 25: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 25: agentuniverse is a framework for multi agents", 4),
        ["round", "25:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 25: agentuniverse is a framework for multi agents", 8),
        ["round", "25:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 25: agentuniverse is a framework for multi agents", 12),
        ["round 25:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 25: agentuniverse is a framework for multi agents", 16),
        ["round 25:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 25: agentuniverse is a framework for multi agents", 24),
        ["round 25: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 25: agentuniverse is a framework for multi agents", 32),
        ["round 25: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 25: knowledge stored as vectors enables retrieval", 4),
        ["round", "25:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 25: knowledge stored as vectors enables retrieval", 8),
        ["round", "25:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 25: knowledge stored as vectors enables retrieval", 12),
        ["round 25:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 25: knowledge stored as vectors enables retrieval", 16),
        ["round 25:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 25: knowledge stored as vectors enables retrieval", 24),
        ["round 25: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 25: knowledge stored as vectors enables retrieval", 32),
        ["round 25: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 25: the processor reads the record then stops", 4),
        ["round", "25:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 25: the processor reads the record then stops", 8),
        ["round", "25: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 25: the processor reads the record then stops", 12),
        ["round 25:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 25: the processor reads the record then stops", 16),
        ["round 25: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 25: the processor reads the record then stops", 24),
        ["round 25: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 25: the processor reads the record then stops", 32),
        ["round 25: the processor reads", "the record then stops"],
    ),
    (
        ("round 25: a worker pulls the next task from the queue", 4),
        ["round", "25:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 25: a worker pulls the next task from the queue", 8),
        ["round", "25: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 25: a worker pulls the next task from the queue", 12),
        ["round 25: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 25: a worker pulls the next task from the queue", 16),
        ["round 25: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 25: a worker pulls the next task from the queue", 24),
        ["round 25: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 25: a worker pulls the next task from the queue", 32),
        ["round 25: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 25: signals travel through the network layer", 4),
        ["round", "25:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 25: signals travel through the network layer", 8),
        ["round", "25:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 25: signals travel through the network layer", 12),
        ["round 25:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 25: signals travel through the network layer", 16),
        ["round 25:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 25: signals travel through the network layer", 24),
        ["round 25: signals travel", "through the network", "layer"],
    ),
    (
        ("round 25: signals travel through the network layer", 32),
        ["round 25: signals travel through", "the network layer"],
    ),
    (
        ("round 25: the gateway routes each request by policy", 4),
        ["round", "25:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 25: the gateway routes each request by policy", 8),
        ["round", "25: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 25: the gateway routes each request by policy", 12),
        ["round 25:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 25: the gateway routes each request by policy", 16),
        ["round 25: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 25: the gateway routes each request by policy", 24),
        ["round 25: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 25: the gateway routes each request by policy", 32),
        ["round 25: the gateway routes", "each request by policy"],
    ),
    (
        ("round 25: memory grows until the buffer is full", 4),
        ["round", "25:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 25: memory grows until the buffer is full", 8),
        ["round", "25:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 25: memory grows until the buffer is full", 12),
        ["round 25:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 25: memory grows until the buffer is full", 16),
        ["round 25: memory", "grows until the", "buffer is full"],
    ),
    (("round 25: memory grows until the buffer is full", 24), ["round 25: memory grows", "until the buffer is full"]),
    (("round 25: memory grows until the buffer is full", 32), ["round 25: memory grows until the", "buffer is full"]),
    (
        ("round 25: the cluster mirrors every packet twice", 4),
        ["round", "25:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 25: the cluster mirrors every packet twice", 8),
        ["round", "25: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 25: the cluster mirrors every packet twice", 12),
        ["round 25:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 25: the cluster mirrors every packet twice", 16),
        ["round 25: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 25: the cluster mirrors every packet twice", 24),
        ["round 25: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 25: the cluster mirrors every packet twice", 32), ["round 25: the cluster mirrors", "every packet twice"]),
    (
        ("round 25: ranking uses tokens learned from the corpus", 4),
        ["round", "25:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 25: ranking uses tokens learned from the corpus", 8),
        ["round", "25:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 25: ranking uses tokens learned from the corpus", 12),
        ["round 25:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 25: ranking uses tokens learned from the corpus", 16),
        ["round 25:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 25: ranking uses tokens learned from the corpus", 24),
        ["round 25: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 25: ranking uses tokens learned from the corpus", 32),
        ["round 25: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 25: a long session ends when the candle dies", 4),
        ["round", "25:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 25: a long session ends when the candle dies", 8),
        ["round", "25: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 25: a long session ends when the candle dies", 12),
        ["round 25: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 25: a long session ends when the candle dies", 16),
        ["round 25: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 25: a long session ends when the candle dies", 24),
        ["round 25: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 25: a long session ends when the candle dies", 32),
        ["round 25: a long session ends", "when the candle dies"],
    ),
    (
        ("round 25: encode the prompt then map the result", 4),
        ["round", "25:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 25: encode the prompt then map the result", 8),
        ["round", "25:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 25: encode the prompt then map the result", 12),
        ["round 25:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 25: encode the prompt then map the result", 16),
        ["round 25: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 25: encode the prompt then map the result", 24),
        ["round 25: encode the", "prompt then map the", "result"],
    ),
    (("round 25: encode the prompt then map the result", 32), ["round 25: encode the prompt then", "map the result"]),
    (
        ("round 25: the kernel wakes the worker at dawn", 4),
        ["round", "25:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 25: the kernel wakes the worker at dawn", 8),
        ["round", "25: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 25: the kernel wakes the worker at dawn", 12),
        ["round 25:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 25: the kernel wakes the worker at dawn", 16), ["round 25: the", "kernel wakes the", "worker at dawn"]),
    (("round 25: the kernel wakes the worker at dawn", 24), ["round 25: the kernel", "wakes the worker at dawn"]),
    (("round 25: the kernel wakes the worker at dawn", 32), ["round 25: the kernel wakes the", "worker at dawn"]),
    (
        ("round 25: service latency drops after the patch", 4),
        ["round", "25:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 25: service latency drops after the patch", 8),
        ["round", "25:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 25: service latency drops after the patch", 12),
        ["round 25:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 25: service latency drops after the patch", 16),
        ["round 25:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 25: service latency drops after the patch", 24),
        ["round 25: service", "latency drops after the", "patch"],
    ),
    (("round 25: service latency drops after the patch", 32), ["round 25: service latency drops", "after the patch"]),
    (
        ("round 25: the library caches every vector it sees", 4),
        ["round", "25:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 25: the library caches every vector it sees", 8),
        ["round", "25: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 25: the library caches every vector it sees", 12),
        ["round 25:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 25: the library caches every vector it sees", 16),
        ["round 25: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 25: the library caches every vector it sees", 24),
        ["round 25: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 25: the library caches every vector it sees", 32),
        ["round 25: the library caches", "every vector it sees"],
    ),
    (
        ("round 25: agents argue then the debate resolves", 4),
        ["round", "25:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 25: agents argue then the debate resolves", 8),
        ["round", "25:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 25: agents argue then the debate resolves", 12),
        ["round 25:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 25: agents argue then the debate resolves", 16),
        ["round 25: agents", "argue then the", "debate resolves"],
    ),
    (("round 25: agents argue then the debate resolves", 24), ["round 25: agents argue", "then the debate resolves"]),
    (("round 25: agents argue then the debate resolves", 32), ["round 25: agents argue then the", "debate resolves"]),
    (
        ("round 25: the filter keeps only strong matches", 4),
        ["round", "25:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 25: the filter keeps only strong matches", 8),
        ["round", "25: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 25: the filter keeps only strong matches", 12),
        ["round 25:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 25: the filter keeps only strong matches", 16),
        ["round 25: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 25: the filter keeps only strong matches", 24), ["round 25: the filter", "keeps only strong", "matches"]),
    (("round 25: the filter keeps only strong matches", 32), ["round 25: the filter keeps only", "strong matches"]),
    (
        ("round 25: the model answers with a short reply", 4),
        ["round", "25:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 25: the model answers with a short reply", 8),
        ["round", "25: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 25: the model answers with a short reply", 12),
        ["round 25:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 25: the model answers with a short reply", 16),
        ["round 25: the", "model answers", "with a short", "reply"],
    ),
    (("round 25: the model answers with a short reply", 24), ["round 25: the model", "answers with a short", "reply"]),
    (("round 25: the model answers with a short reply", 32), ["round 25: the model answers with", "a short reply"]),
    (
        ("round 25: the recorder stores the reasoning trace", 4),
        ["round", "25:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 25: the recorder stores the reasoning trace", 8),
        ["round", "25: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 25: the recorder stores the reasoning trace", 12),
        ["round 25:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 25: the recorder stores the reasoning trace", 16),
        ["round 25: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 25: the recorder stores the reasoning trace", 24),
        ["round 25: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 25: the recorder stores the reasoning trace", 32),
        ["round 25: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 25: the angel watches the processor run", 4),
        ["round", "25:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 25: the angel watches the processor run", 8),
        ["round", "25: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 25: the angel watches the processor run", 12),
        ["round 25:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 25: the angel watches the processor run", 16), ["round 25: the", "angel watches", "the processor", "run"]),
    (("round 25: the angel watches the processor run", 24), ["round 25: the angel", "watches the processor", "run"]),
    (("round 25: the angel watches the processor run", 32), ["round 25: the angel watches the", "processor run"]),
    (
        ("round 25: angle of the vector decides the match", 4),
        ["round", "25:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 25: angle of the vector decides the match", 8),
        ["round", "25:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 25: angle of the vector decides the match", 12),
        ["round 25:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 25: angle of the vector decides the match", 16),
        ["round 25: angle", "of the vector", "decides the", "match"],
    ),
    (("round 25: angle of the vector decides the match", 24), ["round 25: angle of the", "vector decides the match"]),
    (("round 25: angle of the vector decides the match", 32), ["round 25: angle of the vector", "decides the match"]),
    (
        ("round 25: the candle burns twice as long at night", 4),
        ["round", "25:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 25: the candle burns twice as long at night", 8),
        ["round", "25: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 25: the candle burns twice as long at night", 12),
        ["round 25:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 25: the candle burns twice as long at night", 16),
        ["round 25: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 25: the candle burns twice as long at night", 24),
        ["round 25: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 25: the candle burns twice as long at night", 32),
        ["round 25: the candle burns twice", "as long at night"],
    ),
    (
        ("round 25: a mirror of the universe in one line", 4),
        ["round", "25:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 25: a mirror of the universe in one line", 8),
        ["round", "25: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 25: a mirror of the universe in one line", 12),
        ["round 25: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 25: a mirror of the universe in one line", 16),
        ["round 25: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 25: a mirror of the universe in one line", 24), ["round 25: a mirror of", "the universe in one line"]),
    (("round 25: a mirror of the universe in one line", 32), ["round 25: a mirror of the", "universe in one line"]),
    (
        ("round 25: the queue drains before the storm", 4),
        ["round", "25:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 25: the queue drains before the storm", 8),
        ["round", "25: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 25: the queue drains before the storm", 12), ["round 25:", "the queue", "drains", "before the", "storm"]),
    (("round 25: the queue drains before the storm", 16), ["round 25: the", "queue drains", "before the storm"]),
    (("round 25: the queue drains before the storm", 24), ["round 25: the queue", "drains before the storm"]),
    (("round 25: the queue drains before the storm", 32), ["round 25: the queue drains", "before the storm"]),
    (
        ("kitten25 sitting25 agent25 angle25 universe25 memory25", 6),
        ["kitten25", "sitting25", "agent25", "angle25", "universe25", "memory25"],
    ),
    (
        ("kitten25 sitting25 agent25 angle25 universe25 memory25", 10),
        ["kitten25", "sitting25", "agent25", "angle25", "universe25", "memory25"],
    ),
    (
        ("kitten25 sitting25 agent25 angle25 universe25 memory25", 18),
        ["kitten25 sitting25", "agent25 angle25", "universe25", "memory25"],
    ),
    (
        ("kitten25 sitting25 agent25 angle25 universe25 memory25", 28),
        ["kitten25 sitting25 agent25", "angle25 universe25 memory25"],
    ),
    (
        ("sitting25 agent25 angle25 universe25 memory25 stream25", 6),
        ["sitting25", "agent25", "angle25", "universe25", "memory25", "stream25"],
    ),
    (
        ("sitting25 agent25 angle25 universe25 memory25 stream25", 10),
        ["sitting25", "agent25", "angle25", "universe25", "memory25", "stream25"],
    ),
    (
        ("sitting25 agent25 angle25 universe25 memory25 stream25", 18),
        ["sitting25 agent25", "angle25 universe25", "memory25 stream25"],
    ),
    (
        ("sitting25 agent25 angle25 universe25 memory25 stream25", 28),
        ["sitting25 agent25 angle25", "universe25 memory25 stream25"],
    ),
    (
        ("agent25 angle25 universe25 memory25 stream25 context25", 6),
        ["agent25", "angle25", "universe25", "memory25", "stream25", "context25"],
    ),
    (
        ("agent25 angle25 universe25 memory25 stream25 context25", 10),
        ["agent25", "angle25", "universe25", "memory25", "stream25", "context25"],
    ),
    (
        ("agent25 angle25 universe25 memory25 stream25 context25", 18),
        ["agent25 angle25", "universe25", "memory25 stream25", "context25"],
    ),
    (
        ("agent25 angle25 universe25 memory25 stream25 context25", 28),
        ["agent25 angle25 universe25", "memory25 stream25 context25"],
    ),
    (
        ("angle25 universe25 memory25 stream25 context25 knowledge25", 6),
        ["angle25", "universe25", "memory25", "stream25", "context25", "knowledge25"],
    ),
    (
        ("angle25 universe25 memory25 stream25 context25 knowledge25", 10),
        ["angle25", "universe25", "memory25", "stream25", "context25", "knowledge25"],
    ),
    (
        ("angle25 universe25 memory25 stream25 context25 knowledge25", 18),
        ["angle25 universe25", "memory25 stream25", "context25", "knowledge25"],
    ),
    (
        ("angle25 universe25 memory25 stream25 context25 knowledge25", 28),
        ["angle25 universe25 memory25", "stream25 context25", "knowledge25"],
    ),
    (
        ("universe25 memory25 stream25 context25 knowledge25 vector25", 6),
        ["universe25", "memory25", "stream25", "context25", "knowledge25", "vector25"],
    ),
    (
        ("universe25 memory25 stream25 context25 knowledge25 vector25", 10),
        ["universe25", "memory25", "stream25", "context25", "knowledge25", "vector25"],
    ),
    (
        ("universe25 memory25 stream25 context25 knowledge25 vector25", 18),
        ["universe25", "memory25 stream25", "context25", "knowledge25", "vector25"],
    ),
    (
        ("universe25 memory25 stream25 context25 knowledge25 vector25", 28),
        ["universe25 memory25 stream25", "context25 knowledge25", "vector25"],
    ),
    (
        ("memory25 stream25 context25 knowledge25 vector25 processor25", 6),
        ["memory25", "stream25", "context25", "knowledge25", "vector25", "processor25"],
    ),
    (
        ("memory25 stream25 context25 knowledge25 vector25 processor25", 10),
        ["memory25", "stream25", "context25", "knowledge25", "vector25", "processor25"],
    ),
    (
        ("memory25 stream25 context25 knowledge25 vector25 processor25", 18),
        ["memory25 stream25", "context25", "knowledge25", "vector25", "processor25"],
    ),
    (
        ("memory25 stream25 context25 knowledge25 vector25 processor25", 28),
        ["memory25 stream25 context25", "knowledge25 vector25", "processor25"],
    ),
    (
        ("stream25 context25 knowledge25 vector25 processor25 reasoning25", 6),
        ["stream25", "context25", "knowledge25", "vector25", "processor25", "reasoning25"],
    ),
    (
        ("stream25 context25 knowledge25 vector25 processor25 reasoning25", 10),
        ["stream25", "context25", "knowledge25", "vector25", "processor25", "reasoning25"],
    ),
    (
        ("stream25 context25 knowledge25 vector25 processor25 reasoning25", 18),
        ["stream25 context25", "knowledge25", "vector25", "processor25", "reasoning25"],
    ),
    (
        ("stream25 context25 knowledge25 vector25 processor25 reasoning25", 28),
        ["stream25 context25", "knowledge25 vector25", "processor25 reasoning25"],
    ),
    (
        ("context25 knowledge25 vector25 processor25 reasoning25 machine25", 6),
        ["context25", "knowledge25", "vector25", "processor25", "reasoning25", "machine25"],
    ),
    (
        ("context25 knowledge25 vector25 processor25 reasoning25 machine25", 10),
        ["context25", "knowledge25", "vector25", "processor25", "reasoning25", "machine25"],
    ),
    (
        ("context25 knowledge25 vector25 processor25 reasoning25 machine25", 18),
        ["context25", "knowledge25", "vector25", "processor25", "reasoning25", "machine25"],
    ),
    (
        ("context25 knowledge25 vector25 processor25 reasoning25 machine25", 28),
        ["context25 knowledge25", "vector25 processor25", "reasoning25 machine25"],
    ),
    (
        ("knowledge25 vector25 processor25 reasoning25 machine25 learning25", 6),
        ["knowledge25", "vector25", "processor25", "reasoning25", "machine25", "learning25"],
    ),
    (
        ("knowledge25 vector25 processor25 reasoning25 machine25 learning25", 10),
        ["knowledge25", "vector25", "processor25", "reasoning25", "machine25", "learning25"],
    ),
    (
        ("knowledge25 vector25 processor25 reasoning25 machine25 learning25", 18),
        ["knowledge25", "vector25", "processor25", "reasoning25", "machine25", "learning25"],
    ),
    (
        ("knowledge25 vector25 processor25 reasoning25 machine25 learning25", 28),
        ["knowledge25 vector25", "processor25 reasoning25", "machine25 learning25"],
    ),
    (
        ("vector25 processor25 reasoning25 machine25 learning25 model25", 6),
        ["vector25", "processor25", "reasoning25", "machine25", "learning25", "model25"],
    ),
    (
        ("vector25 processor25 reasoning25 machine25 learning25 model25", 10),
        ["vector25", "processor25", "reasoning25", "machine25", "learning25", "model25"],
    ),
    (
        ("vector25 processor25 reasoning25 machine25 learning25 model25", 18),
        ["vector25", "processor25", "reasoning25", "machine25", "learning25 model25"],
    ),
    (
        ("vector25 processor25 reasoning25 machine25 learning25 model25", 28),
        ["vector25 processor25", "reasoning25 machine25", "learning25 model25"],
    ),
    (
        ("processor25 reasoning25 machine25 learning25 model25 token25", 6),
        ["processor25", "reasoning25", "machine25", "learning25", "model25", "token25"],
    ),
    (
        ("processor25 reasoning25 machine25 learning25 model25 token25", 10),
        ["processor25", "reasoning25", "machine25", "learning25", "model25", "token25"],
    ),
    (
        ("processor25 reasoning25 machine25 learning25 model25 token25", 18),
        ["processor25", "reasoning25", "machine25", "learning25 model25", "token25"],
    ),
    (
        ("processor25 reasoning25 machine25 learning25 model25 token25", 28),
        ["processor25 reasoning25", "machine25 learning25 model25", "token25"],
    ),
    (
        ("reasoning25 machine25 learning25 model25 token25 prompt25", 6),
        ["reasoning25", "machine25", "learning25", "model25", "token25", "prompt25"],
    ),
    (
        ("reasoning25 machine25 learning25 model25 token25 prompt25", 10),
        ["reasoning25", "machine25", "learning25", "model25", "token25", "prompt25"],
    ),
    (
        ("reasoning25 machine25 learning25 model25 token25 prompt25", 18),
        ["reasoning25", "machine25", "learning25 model25", "token25 prompt25"],
    ),
    (
        ("reasoning25 machine25 learning25 model25 token25 prompt25", 28),
        ["reasoning25 machine25", "learning25 model25 token25", "prompt25"],
    ),
    (
        ("machine25 learning25 model25 token25 prompt25 session25", 6),
        ["machine25", "learning25", "model25", "token25", "prompt25", "session25"],
    ),
    (
        ("machine25 learning25 model25 token25 prompt25 session25", 10),
        ["machine25", "learning25", "model25", "token25", "prompt25", "session25"],
    ),
    (
        ("machine25 learning25 model25 token25 prompt25 session25", 18),
        ["machine25", "learning25 model25", "token25 prompt25", "session25"],
    ),
    (
        ("machine25 learning25 model25 token25 prompt25 session25", 28),
        ["machine25 learning25 model25", "token25 prompt25 session25"],
    ),
    (
        ("learning25 model25 token25 prompt25 session25 library25", 6),
        ["learning25", "model25", "token25", "prompt25", "session25", "library25"],
    ),
    (
        ("learning25 model25 token25 prompt25 session25 library25", 10),
        ["learning25", "model25", "token25", "prompt25", "session25", "library25"],
    ),
    (
        ("learning25 model25 token25 prompt25 session25 library25", 18),
        ["learning25 model25", "token25 prompt25", "session25", "library25"],
    ),
    (
        ("learning25 model25 token25 prompt25 session25 library25", 28),
        ["learning25 model25 token25", "prompt25 session25 library25"],
    ),
    (
        ("model25 token25 prompt25 session25 library25 service25", 6),
        ["model25", "token25", "prompt25", "session25", "library25", "service25"],
    ),
    (
        ("model25 token25 prompt25 session25 library25 service25", 10),
        ["model25", "token25", "prompt25", "session25", "library25", "service25"],
    ),
    (
        ("model25 token25 prompt25 session25 library25 service25", 18),
        ["model25 token25", "prompt25 session25", "library25", "service25"],
    ),
    (
        ("model25 token25 prompt25 session25 library25 service25", 28),
        ["model25 token25 prompt25", "session25 library25", "service25"],
    ),
    (
        ("token25 prompt25 session25 library25 service25 gateway25", 6),
        ["token25", "prompt25", "session25", "library25", "service25", "gateway25"],
    ),
    (
        ("token25 prompt25 session25 library25 service25 gateway25", 10),
        ["token25", "prompt25", "session25", "library25", "service25", "gateway25"],
    ),
    (
        ("token25 prompt25 session25 library25 service25 gateway25", 18),
        ["token25 prompt25", "session25", "library25", "service25", "gateway25"],
    ),
    (
        ("token25 prompt25 session25 library25 service25 gateway25", 28),
        ["token25 prompt25 session25", "library25 service25", "gateway25"],
    ),
    (
        ("prompt25 session25 library25 service25 gateway25 storage25", 6),
        ["prompt25", "session25", "library25", "service25", "gateway25", "storage25"],
    ),
    (
        ("prompt25 session25 library25 service25 gateway25 storage25", 10),
        ["prompt25", "session25", "library25", "service25", "gateway25", "storage25"],
    ),
    (
        ("prompt25 session25 library25 service25 gateway25 storage25", 18),
        ["prompt25 session25", "library25", "service25", "gateway25", "storage25"],
    ),
    (
        ("prompt25 session25 library25 service25 gateway25 storage25", 28),
        ["prompt25 session25 library25", "service25 gateway25", "storage25"],
    ),
    (
        ("session25 library25 service25 gateway25 storage25 network25", 6),
        ["session25", "library25", "service25", "gateway25", "storage25", "network25"],
    ),
    (
        ("session25 library25 service25 gateway25 storage25 network25", 10),
        ["session25", "library25", "service25", "gateway25", "storage25", "network25"],
    ),
    (
        ("session25 library25 service25 gateway25 storage25 network25", 18),
        ["session25", "library25", "service25", "gateway25", "storage25", "network25"],
    ),
    (
        ("session25 library25 service25 gateway25 storage25 network25", 28),
        ["session25 library25", "service25 gateway25", "storage25 network25"],
    ),
    (
        ("library25 service25 gateway25 storage25 network25 latency25", 6),
        ["library25", "service25", "gateway25", "storage25", "network25", "latency25"],
    ),
    (
        ("library25 service25 gateway25 storage25 network25 latency25", 10),
        ["library25", "service25", "gateway25", "storage25", "network25", "latency25"],
    ),
    (
        ("library25 service25 gateway25 storage25 network25 latency25", 18),
        ["library25", "service25", "gateway25", "storage25", "network25", "latency25"],
    ),
    (
        ("library25 service25 gateway25 storage25 network25 latency25", 28),
        ["library25 service25", "gateway25 storage25", "network25 latency25"],
    ),
    (
        ("service25 gateway25 storage25 network25 latency25 buffer25", 6),
        ["service25", "gateway25", "storage25", "network25", "latency25", "buffer25"],
    ),
    (
        ("service25 gateway25 storage25 network25 latency25 buffer25", 10),
        ["service25", "gateway25", "storage25", "network25", "latency25", "buffer25"],
    ),
    (
        ("service25 gateway25 storage25 network25 latency25 buffer25", 18),
        ["service25", "gateway25", "storage25", "network25", "latency25 buffer25"],
    ),
    (
        ("service25 gateway25 storage25 network25 latency25 buffer25", 28),
        ["service25 gateway25", "storage25 network25", "latency25 buffer25"],
    ),
    (
        ("gateway25 storage25 network25 latency25 buffer25 queue25", 6),
        ["gateway25", "storage25", "network25", "latency25", "buffer25", "queue25"],
    ),
    (
        ("gateway25 storage25 network25 latency25 buffer25 queue25", 10),
        ["gateway25", "storage25", "network25", "latency25", "buffer25", "queue25"],
    ),
    (
        ("gateway25 storage25 network25 latency25 buffer25 queue25", 18),
        ["gateway25", "storage25", "network25", "latency25 buffer25", "queue25"],
    ),
    (
        ("gateway25 storage25 network25 latency25 buffer25 queue25", 28),
        ["gateway25 storage25", "network25 latency25 buffer25", "queue25"],
    ),
    (
        ("storage25 network25 latency25 buffer25 queue25 worker25", 6),
        ["storage25", "network25", "latency25", "buffer25", "queue25", "worker25"],
    ),
    (
        ("storage25 network25 latency25 buffer25 queue25 worker25", 10),
        ["storage25", "network25", "latency25", "buffer25", "queue25", "worker25"],
    ),
    (
        ("storage25 network25 latency25 buffer25 queue25 worker25", 18),
        ["storage25", "network25", "latency25 buffer25", "queue25 worker25"],
    ),
    (
        ("storage25 network25 latency25 buffer25 queue25 worker25", 28),
        ["storage25 network25", "latency25 buffer25 queue25", "worker25"],
    ),
    (
        ("network25 latency25 buffer25 queue25 worker25 kernel25", 6),
        ["network25", "latency25", "buffer25", "queue25", "worker25", "kernel25"],
    ),
    (
        ("network25 latency25 buffer25 queue25 worker25 kernel25", 10),
        ["network25", "latency25", "buffer25", "queue25", "worker25", "kernel25"],
    ),
    (
        ("network25 latency25 buffer25 queue25 worker25 kernel25", 18),
        ["network25", "latency25 buffer25", "queue25 worker25", "kernel25"],
    ),
    (
        ("network25 latency25 buffer25 queue25 worker25 kernel25", 28),
        ["network25 latency25 buffer25", "queue25 worker25 kernel25"],
    ),
    (
        ("latency25 buffer25 queue25 worker25 kernel25 signal25", 6),
        ["latency25", "buffer25", "queue25", "worker25", "kernel25", "signal25"],
    ),
    (
        ("latency25 buffer25 queue25 worker25 kernel25 signal25", 10),
        ["latency25", "buffer25", "queue25", "worker25", "kernel25", "signal25"],
    ),
    (
        ("latency25 buffer25 queue25 worker25 kernel25 signal25", 18),
        ["latency25 buffer25", "queue25 worker25", "kernel25 signal25"],
    ),
    (
        ("latency25 buffer25 queue25 worker25 kernel25 signal25", 28),
        ["latency25 buffer25 queue25", "worker25 kernel25 signal25"],
    ),
    (
        ("buffer25 queue25 worker25 kernel25 signal25 packet25", 6),
        ["buffer25", "queue25", "worker25", "kernel25", "signal25", "packet25"],
    ),
    (
        ("buffer25 queue25 worker25 kernel25 signal25 packet25", 10),
        ["buffer25", "queue25", "worker25", "kernel25", "signal25", "packet25"],
    ),
    (
        ("buffer25 queue25 worker25 kernel25 signal25 packet25", 18),
        ["buffer25 queue25", "worker25 kernel25", "signal25 packet25"],
    ),
    (
        ("buffer25 queue25 worker25 kernel25 signal25 packet25", 28),
        ["buffer25 queue25 worker25", "kernel25 signal25 packet25"],
    ),
    (
        ("queue25 worker25 kernel25 signal25 packet25 router25", 6),
        ["queue25", "worker25", "kernel25", "signal25", "packet25", "router25"],
    ),
    (
        ("queue25 worker25 kernel25 signal25 packet25 router25", 10),
        ["queue25", "worker25", "kernel25", "signal25", "packet25", "router25"],
    ),
    (
        ("queue25 worker25 kernel25 signal25 packet25 router25", 18),
        ["queue25 worker25", "kernel25 signal25", "packet25 router25"],
    ),
    (
        ("queue25 worker25 kernel25 signal25 packet25 router25", 28),
        ["queue25 worker25 kernel25", "signal25 packet25 router25"],
    ),
    (
        ("worker25 kernel25 signal25 packet25 router25 cluster25", 6),
        ["worker25", "kernel25", "signal25", "packet25", "router25", "cluster25"],
    ),
    (
        ("worker25 kernel25 signal25 packet25 router25 cluster25", 10),
        ["worker25", "kernel25", "signal25", "packet25", "router25", "cluster25"],
    ),
    (
        ("worker25 kernel25 signal25 packet25 router25 cluster25", 18),
        ["worker25 kernel25", "signal25 packet25", "router25 cluster25"],
    ),
    (
        ("worker25 kernel25 signal25 packet25 router25 cluster25", 28),
        ["worker25 kernel25 signal25", "packet25 router25 cluster25"],
    ),
    (
        ("kernel25 signal25 packet25 router25 cluster25 mirror25", 6),
        ["kernel25", "signal25", "packet25", "router25", "cluster25", "mirror25"],
    ),
    (
        ("kernel25 signal25 packet25 router25 cluster25 mirror25", 10),
        ["kernel25", "signal25", "packet25", "router25", "cluster25", "mirror25"],
    ),
    (
        ("kernel25 signal25 packet25 router25 cluster25 mirror25", 18),
        ["kernel25 signal25", "packet25 router25", "cluster25 mirror25"],
    ),
    (
        ("kernel25 signal25 packet25 router25 cluster25 mirror25", 28),
        ["kernel25 signal25 packet25", "router25 cluster25 mirror25"],
    ),
    (
        ("signal25 packet25 router25 cluster25 mirror25 filter25", 6),
        ["signal25", "packet25", "router25", "cluster25", "mirror25", "filter25"],
    ),
    (
        ("signal25 packet25 router25 cluster25 mirror25 filter25", 10),
        ["signal25", "packet25", "router25", "cluster25", "mirror25", "filter25"],
    ),
    (
        ("signal25 packet25 router25 cluster25 mirror25 filter25", 18),
        ["signal25 packet25", "router25 cluster25", "mirror25 filter25"],
    ),
    (
        ("signal25 packet25 router25 cluster25 mirror25 filter25", 28),
        ["signal25 packet25 router25", "cluster25 mirror25 filter25"],
    ),
    (
        ("packet25 router25 cluster25 mirror25 filter25 ranking25", 6),
        ["packet25", "router25", "cluster25", "mirror25", "filter25", "ranking25"],
    ),
    (
        ("packet25 router25 cluster25 mirror25 filter25 ranking25", 10),
        ["packet25", "router25", "cluster25", "mirror25", "filter25", "ranking25"],
    ),
    (
        ("packet25 router25 cluster25 mirror25 filter25 ranking25", 18),
        ["packet25 router25", "cluster25 mirror25", "filter25 ranking25"],
    ),
    (
        ("packet25 router25 cluster25 mirror25 filter25 ranking25", 28),
        ["packet25 router25 cluster25", "mirror25 filter25 ranking25"],
    ),
    (
        ("router25 cluster25 mirror25 filter25 ranking25 encoding25", 6),
        ["router25", "cluster25", "mirror25", "filter25", "ranking25", "encoding25"],
    ),
    (
        ("router25 cluster25 mirror25 filter25 ranking25 encoding25", 10),
        ["router25", "cluster25", "mirror25", "filter25", "ranking25", "encoding25"],
    ),
    (
        ("router25 cluster25 mirror25 filter25 ranking25 encoding25", 18),
        ["router25 cluster25", "mirror25 filter25", "ranking25", "encoding25"],
    ),
    (
        ("router25 cluster25 mirror25 filter25 ranking25 encoding25", 28),
        ["router25 cluster25 mirror25", "filter25 ranking25", "encoding25"],
    ),
    (
        ("cluster25 mirror25 filter25 ranking25 encoding25 mapping25", 6),
        ["cluster25", "mirror25", "filter25", "ranking25", "encoding25", "mapping25"],
    ),
    (
        ("cluster25 mirror25 filter25 ranking25 encoding25 mapping25", 10),
        ["cluster25", "mirror25", "filter25", "ranking25", "encoding25", "mapping25"],
    ),
    (
        ("cluster25 mirror25 filter25 ranking25 encoding25 mapping25", 18),
        ["cluster25 mirror25", "filter25 ranking25", "encoding25", "mapping25"],
    ),
    (
        ("cluster25 mirror25 filter25 ranking25 encoding25 mapping25", 28),
        ["cluster25 mirror25 filter25", "ranking25 encoding25", "mapping25"],
    ),
    (
        ("mirror25 filter25 ranking25 encoding25 mapping25 record25", 6),
        ["mirror25", "filter25", "ranking25", "encoding25", "mapping25", "record25"],
    ),
    (
        ("mirror25 filter25 ranking25 encoding25 mapping25 record25", 10),
        ["mirror25", "filter25", "ranking25", "encoding25", "mapping25", "record25"],
    ),
    (
        ("mirror25 filter25 ranking25 encoding25 mapping25 record25", 18),
        ["mirror25 filter25", "ranking25", "encoding25", "mapping25 record25"],
    ),
    (
        ("mirror25 filter25 ranking25 encoding25 mapping25 record25", 28),
        ["mirror25 filter25 ranking25", "encoding25 mapping25", "record25"],
    ),
    (
        ("filter25 ranking25 encoding25 mapping25 record25 candle25", 6),
        ["filter25", "ranking25", "encoding25", "mapping25", "record25", "candle25"],
    ),
    (
        ("filter25 ranking25 encoding25 mapping25 record25 candle25", 10),
        ["filter25", "ranking25", "encoding25", "mapping25", "record25", "candle25"],
    ),
    (
        ("filter25 ranking25 encoding25 mapping25 record25 candle25", 18),
        ["filter25 ranking25", "encoding25", "mapping25 record25", "candle25"],
    ),
    (
        ("filter25 ranking25 encoding25 mapping25 record25 candle25", 28),
        ["filter25 ranking25", "encoding25 mapping25", "record25 candle25"],
    ),
    (
        ("ranking25 encoding25 mapping25 record25 candle25 thread25", 6),
        ["ranking25", "encoding25", "mapping25", "record25", "candle25", "thread25"],
    ),
    (
        ("ranking25 encoding25 mapping25 record25 candle25 thread25", 10),
        ["ranking25", "encoding25", "mapping25", "record25", "candle25", "thread25"],
    ),
    (
        ("ranking25 encoding25 mapping25 record25 candle25 thread25", 18),
        ["ranking25", "encoding25", "mapping25 record25", "candle25 thread25"],
    ),
    (
        ("ranking25 encoding25 mapping25 record25 candle25 thread25", 28),
        ["ranking25 encoding25", "mapping25 record25 candle25", "thread25"],
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
