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
        ("round 130: the quick brown fox jumps over the lazy dog", 4),
        ["round", "130:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 130: the quick brown fox jumps over the lazy dog", 8),
        ["round", "130: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 130: the quick brown fox jumps over the lazy dog", 12),
        ["round 130:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 130: the quick brown fox jumps over the lazy dog", 16),
        ["round 130: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 130: the quick brown fox jumps over the lazy dog", 24),
        ["round 130: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 130: the quick brown fox jumps over the lazy dog", 32),
        ["round 130: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 130: agentuniverse is a framework for multi agents", 4),
        ["round", "130:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 130: agentuniverse is a framework for multi agents", 8),
        ["round", "130:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 130: agentuniverse is a framework for multi agents", 12),
        ["round 130:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 130: agentuniverse is a framework for multi agents", 16),
        ["round 130:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 130: agentuniverse is a framework for multi agents", 24),
        ["round 130: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 130: agentuniverse is a framework for multi agents", 32),
        ["round 130: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 130: knowledge stored as vectors enables retrieval", 4),
        ["round", "130:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 130: knowledge stored as vectors enables retrieval", 8),
        ["round", "130:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 130: knowledge stored as vectors enables retrieval", 12),
        ["round 130:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 130: knowledge stored as vectors enables retrieval", 16),
        ["round 130:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 130: knowledge stored as vectors enables retrieval", 24),
        ["round 130: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 130: knowledge stored as vectors enables retrieval", 32),
        ["round 130: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 130: the processor reads the record then stops", 4),
        ["round", "130:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 130: the processor reads the record then stops", 8),
        ["round", "130: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 130: the processor reads the record then stops", 12),
        ["round 130:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 130: the processor reads the record then stops", 16),
        ["round 130: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 130: the processor reads the record then stops", 24),
        ["round 130: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 130: the processor reads the record then stops", 32),
        ["round 130: the processor reads", "the record then stops"],
    ),
    (
        ("round 130: a worker pulls the next task from the queue", 4),
        ["round", "130:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 130: a worker pulls the next task from the queue", 8),
        ["round", "130: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 130: a worker pulls the next task from the queue", 12),
        ["round 130: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 130: a worker pulls the next task from the queue", 16),
        ["round 130: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 130: a worker pulls the next task from the queue", 24),
        ["round 130: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 130: a worker pulls the next task from the queue", 32),
        ["round 130: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 130: signals travel through the network layer", 4),
        ["round", "130:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 130: signals travel through the network layer", 8),
        ["round", "130:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 130: signals travel through the network layer", 12),
        ["round 130:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 130: signals travel through the network layer", 16),
        ["round 130:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 130: signals travel through the network layer", 24),
        ["round 130: signals", "travel through the", "network layer"],
    ),
    (
        ("round 130: signals travel through the network layer", 32),
        ["round 130: signals travel", "through the network layer"],
    ),
    (
        ("round 130: the gateway routes each request by policy", 4),
        ["round", "130:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 130: the gateway routes each request by policy", 8),
        ["round", "130: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 130: the gateway routes each request by policy", 12),
        ["round 130:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 130: the gateway routes each request by policy", 16),
        ["round 130: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 130: the gateway routes each request by policy", 24),
        ["round 130: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 130: the gateway routes each request by policy", 32),
        ["round 130: the gateway routes", "each request by policy"],
    ),
    (
        ("round 130: memory grows until the buffer is full", 4),
        ["round", "130:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 130: memory grows until the buffer is full", 8),
        ["round", "130:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 130: memory grows until the buffer is full", 12),
        ["round 130:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 130: memory grows until the buffer is full", 16),
        ["round 130:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 130: memory grows until the buffer is full", 24), ["round 130: memory grows", "until the buffer is full"]),
    (("round 130: memory grows until the buffer is full", 32), ["round 130: memory grows until", "the buffer is full"]),
    (
        ("round 130: the cluster mirrors every packet twice", 4),
        ["round", "130:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 130: the cluster mirrors every packet twice", 8),
        ["round", "130: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 130: the cluster mirrors every packet twice", 12),
        ["round 130:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 130: the cluster mirrors every packet twice", 16),
        ["round 130: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 130: the cluster mirrors every packet twice", 24),
        ["round 130: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 130: the cluster mirrors every packet twice", 32),
        ["round 130: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 130: ranking uses tokens learned from the corpus", 4),
        ["round", "130:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 130: ranking uses tokens learned from the corpus", 8),
        ["round", "130:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 130: ranking uses tokens learned from the corpus", 12),
        ["round 130:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 130: ranking uses tokens learned from the corpus", 16),
        ["round 130:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 130: ranking uses tokens learned from the corpus", 24),
        ["round 130: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 130: ranking uses tokens learned from the corpus", 32),
        ["round 130: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 130: a long session ends when the candle dies", 4),
        ["round", "130:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 130: a long session ends when the candle dies", 8),
        ["round", "130: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 130: a long session ends when the candle dies", 12),
        ["round 130: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 130: a long session ends when the candle dies", 16),
        ["round 130: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 130: a long session ends when the candle dies", 24),
        ["round 130: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 130: a long session ends when the candle dies", 32),
        ["round 130: a long session ends", "when the candle dies"],
    ),
    (
        ("round 130: encode the prompt then map the result", 4),
        ["round", "130:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 130: encode the prompt then map the result", 8),
        ["round", "130:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 130: encode the prompt then map the result", 12),
        ["round 130:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 130: encode the prompt then map the result", 16),
        ["round 130:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 130: encode the prompt then map the result", 24),
        ["round 130: encode the", "prompt then map the", "result"],
    ),
    (("round 130: encode the prompt then map the result", 32), ["round 130: encode the prompt", "then map the result"]),
    (
        ("round 130: the kernel wakes the worker at dawn", 4),
        ["round", "130:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 130: the kernel wakes the worker at dawn", 8),
        ["round", "130: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 130: the kernel wakes the worker at dawn", 12),
        ["round 130:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 130: the kernel wakes the worker at dawn", 16), ["round 130: the", "kernel wakes the", "worker at dawn"]),
    (("round 130: the kernel wakes the worker at dawn", 24), ["round 130: the kernel", "wakes the worker at dawn"]),
    (("round 130: the kernel wakes the worker at dawn", 32), ["round 130: the kernel wakes the", "worker at dawn"]),
    (
        ("round 130: service latency drops after the patch", 4),
        ["round", "130:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 130: service latency drops after the patch", 8),
        ["round", "130:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 130: service latency drops after the patch", 12),
        ["round 130:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 130: service latency drops after the patch", 16),
        ["round 130:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 130: service latency drops after the patch", 24),
        ["round 130: service", "latency drops after the", "patch"],
    ),
    (("round 130: service latency drops after the patch", 32), ["round 130: service latency drops", "after the patch"]),
    (
        ("round 130: the library caches every vector it sees", 4),
        ["round", "130:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 130: the library caches every vector it sees", 8),
        ["round", "130: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 130: the library caches every vector it sees", 12),
        ["round 130:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 130: the library caches every vector it sees", 16),
        ["round 130: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 130: the library caches every vector it sees", 24),
        ["round 130: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 130: the library caches every vector it sees", 32),
        ["round 130: the library caches", "every vector it sees"],
    ),
    (
        ("round 130: agents argue then the debate resolves", 4),
        ["round", "130:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 130: agents argue then the debate resolves", 8),
        ["round", "130:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 130: agents argue then the debate resolves", 12),
        ["round 130:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 130: agents argue then the debate resolves", 16),
        ["round 130:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 130: agents argue then the debate resolves", 24), ["round 130: agents argue", "then the debate resolves"]),
    (("round 130: agents argue then the debate resolves", 32), ["round 130: agents argue then the", "debate resolves"]),
    (
        ("round 130: the filter keeps only strong matches", 4),
        ["round", "130:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 130: the filter keeps only strong matches", 8),
        ["round", "130: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 130: the filter keeps only strong matches", 12),
        ["round 130:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 130: the filter keeps only strong matches", 16),
        ["round 130: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 130: the filter keeps only strong matches", 24),
        ["round 130: the filter", "keeps only strong", "matches"],
    ),
    (("round 130: the filter keeps only strong matches", 32), ["round 130: the filter keeps only", "strong matches"]),
    (
        ("round 130: the model answers with a short reply", 4),
        ["round", "130:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 130: the model answers with a short reply", 8),
        ["round", "130: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 130: the model answers with a short reply", 12),
        ["round 130:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 130: the model answers with a short reply", 16),
        ["round 130: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 130: the model answers with a short reply", 24),
        ["round 130: the model", "answers with a short", "reply"],
    ),
    (("round 130: the model answers with a short reply", 32), ["round 130: the model answers", "with a short reply"]),
    (
        ("round 130: the recorder stores the reasoning trace", 4),
        ["round", "130:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 130: the recorder stores the reasoning trace", 8),
        ["round", "130: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 130: the recorder stores the reasoning trace", 12),
        ["round 130:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 130: the recorder stores the reasoning trace", 16),
        ["round 130: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 130: the recorder stores the reasoning trace", 24),
        ["round 130: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 130: the recorder stores the reasoning trace", 32),
        ["round 130: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 130: the angel watches the processor run", 4),
        ["round", "130:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 130: the angel watches the processor run", 8),
        ["round", "130: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 130: the angel watches the processor run", 12),
        ["round 130:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 130: the angel watches the processor run", 16),
        ["round 130: the", "angel watches", "the processor", "run"],
    ),
    (("round 130: the angel watches the processor run", 24), ["round 130: the angel", "watches the processor", "run"]),
    (("round 130: the angel watches the processor run", 32), ["round 130: the angel watches the", "processor run"]),
    (
        ("round 130: angle of the vector decides the match", 4),
        ["round", "130:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 130: angle of the vector decides the match", 8),
        ["round", "130:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 130: angle of the vector decides the match", 12),
        ["round 130:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 130: angle of the vector decides the match", 16),
        ["round 130: angle", "of the vector", "decides the", "match"],
    ),
    (("round 130: angle of the vector decides the match", 24), ["round 130: angle of the", "vector decides the match"]),
    (("round 130: angle of the vector decides the match", 32), ["round 130: angle of the vector", "decides the match"]),
    (
        ("round 130: the candle burns twice as long at night", 4),
        ["round", "130:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 130: the candle burns twice as long at night", 8),
        ["round", "130: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 130: the candle burns twice as long at night", 12),
        ["round 130:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 130: the candle burns twice as long at night", 16),
        ["round 130: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 130: the candle burns twice as long at night", 24),
        ["round 130: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 130: the candle burns twice as long at night", 32),
        ["round 130: the candle burns", "twice as long at night"],
    ),
    (
        ("round 130: a mirror of the universe in one line", 4),
        ["round", "130:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 130: a mirror of the universe in one line", 8),
        ["round", "130: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 130: a mirror of the universe in one line", 12),
        ["round 130: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 130: a mirror of the universe in one line", 16),
        ["round 130: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 130: a mirror of the universe in one line", 24), ["round 130: a mirror of", "the universe in one line"]),
    (("round 130: a mirror of the universe in one line", 32), ["round 130: a mirror of the", "universe in one line"]),
    (
        ("round 130: the queue drains before the storm", 4),
        ["round", "130:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 130: the queue drains before the storm", 8),
        ["round", "130: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 130: the queue drains before the storm", 12),
        ["round 130:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 130: the queue drains before the storm", 16), ["round 130: the", "queue drains", "before the storm"]),
    (("round 130: the queue drains before the storm", 24), ["round 130: the queue", "drains before the storm"]),
    (("round 130: the queue drains before the storm", 32), ["round 130: the queue drains", "before the storm"]),
    (
        ("kitten130 sitting130 agent130 angle130 universe130 memory130", 6),
        ["kitten130", "sitting130", "agent130", "angle130", "universe130", "memory130"],
    ),
    (
        ("kitten130 sitting130 agent130 angle130 universe130 memory130", 10),
        ["kitten130", "sitting130", "agent130", "angle130", "universe130", "memory130"],
    ),
    (
        ("kitten130 sitting130 agent130 angle130 universe130 memory130", 18),
        ["kitten130", "sitting130", "agent130 angle130", "universe130", "memory130"],
    ),
    (
        ("kitten130 sitting130 agent130 angle130 universe130 memory130", 28),
        ["kitten130 sitting130", "agent130 angle130", "universe130 memory130"],
    ),
    (
        ("sitting130 agent130 angle130 universe130 memory130 stream130", 6),
        ["sitting130", "agent130", "angle130", "universe130", "memory130", "stream130"],
    ),
    (
        ("sitting130 agent130 angle130 universe130 memory130 stream130", 10),
        ["sitting130", "agent130", "angle130", "universe130", "memory130", "stream130"],
    ),
    (
        ("sitting130 agent130 angle130 universe130 memory130 stream130", 18),
        ["sitting130", "agent130 angle130", "universe130", "memory130", "stream130"],
    ),
    (
        ("sitting130 agent130 angle130 universe130 memory130 stream130", 28),
        ["sitting130 agent130 angle130", "universe130 memory130", "stream130"],
    ),
    (
        ("agent130 angle130 universe130 memory130 stream130 context130", 6),
        ["agent130", "angle130", "universe130", "memory130", "stream130", "context130"],
    ),
    (
        ("agent130 angle130 universe130 memory130 stream130 context130", 10),
        ["agent130", "angle130", "universe130", "memory130", "stream130", "context130"],
    ),
    (
        ("agent130 angle130 universe130 memory130 stream130 context130", 18),
        ["agent130 angle130", "universe130", "memory130", "stream130", "context130"],
    ),
    (
        ("agent130 angle130 universe130 memory130 stream130 context130", 28),
        ["agent130 angle130", "universe130 memory130", "stream130 context130"],
    ),
    (
        ("angle130 universe130 memory130 stream130 context130 knowledge130", 6),
        ["angle130", "universe130", "memory130", "stream130", "context130", "knowledge130"],
    ),
    (
        ("angle130 universe130 memory130 stream130 context130 knowledge130", 10),
        ["angle130", "universe130", "memory130", "stream130", "context130", "knowledge130"],
    ),
    (
        ("angle130 universe130 memory130 stream130 context130 knowledge130", 18),
        ["angle130", "universe130", "memory130", "stream130", "context130", "knowledge130"],
    ),
    (
        ("angle130 universe130 memory130 stream130 context130 knowledge130", 28),
        ["angle130 universe130", "memory130 stream130", "context130 knowledge130"],
    ),
    (
        ("universe130 memory130 stream130 context130 knowledge130 vector130", 6),
        ["universe130", "memory130", "stream130", "context130", "knowledge130", "vector130"],
    ),
    (
        ("universe130 memory130 stream130 context130 knowledge130 vector130", 10),
        ["universe130", "memory130", "stream130", "context130", "knowledge130", "vector130"],
    ),
    (
        ("universe130 memory130 stream130 context130 knowledge130 vector130", 18),
        ["universe130", "memory130", "stream130", "context130", "knowledge130", "vector130"],
    ),
    (
        ("universe130 memory130 stream130 context130 knowledge130 vector130", 28),
        ["universe130 memory130", "stream130 context130", "knowledge130 vector130"],
    ),
    (
        ("memory130 stream130 context130 knowledge130 vector130 processor130", 6),
        ["memory130", "stream130", "context130", "knowledge130", "vector130", "processor130"],
    ),
    (
        ("memory130 stream130 context130 knowledge130 vector130 processor130", 10),
        ["memory130", "stream130", "context130", "knowledge130", "vector130", "processor130"],
    ),
    (
        ("memory130 stream130 context130 knowledge130 vector130 processor130", 18),
        ["memory130", "stream130", "context130", "knowledge130", "vector130", "processor130"],
    ),
    (
        ("memory130 stream130 context130 knowledge130 vector130 processor130", 28),
        ["memory130 stream130", "context130 knowledge130", "vector130 processor130"],
    ),
    (
        ("stream130 context130 knowledge130 vector130 processor130 reasoning130", 6),
        ["stream130", "context130", "knowledge130", "vector130", "processor130", "reasoning130"],
    ),
    (
        ("stream130 context130 knowledge130 vector130 processor130 reasoning130", 10),
        ["stream130", "context130", "knowledge130", "vector130", "processor130", "reasoning130"],
    ),
    (
        ("stream130 context130 knowledge130 vector130 processor130 reasoning130", 18),
        ["stream130", "context130", "knowledge130", "vector130", "processor130", "reasoning130"],
    ),
    (
        ("stream130 context130 knowledge130 vector130 processor130 reasoning130", 28),
        ["stream130 context130", "knowledge130 vector130", "processor130 reasoning130"],
    ),
    (
        ("context130 knowledge130 vector130 processor130 reasoning130 machine130", 6),
        ["context130", "knowledge130", "vector130", "processor130", "reasoning130", "machine130"],
    ),
    (
        ("context130 knowledge130 vector130 processor130 reasoning130 machine130", 10),
        ["context130", "knowledge130", "vector130", "processor130", "reasoning130", "machine130"],
    ),
    (
        ("context130 knowledge130 vector130 processor130 reasoning130 machine130", 18),
        ["context130", "knowledge130", "vector130", "processor130", "reasoning130", "machine130"],
    ),
    (
        ("context130 knowledge130 vector130 processor130 reasoning130 machine130", 28),
        ["context130 knowledge130", "vector130 processor130", "reasoning130 machine130"],
    ),
    (
        ("knowledge130 vector130 processor130 reasoning130 machine130 learning130", 6),
        ["knowledge130", "vector130", "processor130", "reasoning130", "machine130", "learning130"],
    ),
    (
        ("knowledge130 vector130 processor130 reasoning130 machine130 learning130", 10),
        ["knowledge130", "vector130", "processor130", "reasoning130", "machine130", "learning130"],
    ),
    (
        ("knowledge130 vector130 processor130 reasoning130 machine130 learning130", 18),
        ["knowledge130", "vector130", "processor130", "reasoning130", "machine130", "learning130"],
    ),
    (
        ("knowledge130 vector130 processor130 reasoning130 machine130 learning130", 28),
        ["knowledge130 vector130", "processor130 reasoning130", "machine130 learning130"],
    ),
    (
        ("vector130 processor130 reasoning130 machine130 learning130 model130", 6),
        ["vector130", "processor130", "reasoning130", "machine130", "learning130", "model130"],
    ),
    (
        ("vector130 processor130 reasoning130 machine130 learning130 model130", 10),
        ["vector130", "processor130", "reasoning130", "machine130", "learning130", "model130"],
    ),
    (
        ("vector130 processor130 reasoning130 machine130 learning130 model130", 18),
        ["vector130", "processor130", "reasoning130", "machine130", "learning130", "model130"],
    ),
    (
        ("vector130 processor130 reasoning130 machine130 learning130 model130", 28),
        ["vector130 processor130", "reasoning130 machine130", "learning130 model130"],
    ),
    (
        ("processor130 reasoning130 machine130 learning130 model130 token130", 6),
        ["processor130", "reasoning130", "machine130", "learning130", "model130", "token130"],
    ),
    (
        ("processor130 reasoning130 machine130 learning130 model130 token130", 10),
        ["processor130", "reasoning130", "machine130", "learning130", "model130", "token130"],
    ),
    (
        ("processor130 reasoning130 machine130 learning130 model130 token130", 18),
        ["processor130", "reasoning130", "machine130", "learning130", "model130 token130"],
    ),
    (
        ("processor130 reasoning130 machine130 learning130 model130 token130", 28),
        ["processor130 reasoning130", "machine130 learning130", "model130 token130"],
    ),
    (
        ("reasoning130 machine130 learning130 model130 token130 prompt130", 6),
        ["reasoning130", "machine130", "learning130", "model130", "token130", "prompt130"],
    ),
    (
        ("reasoning130 machine130 learning130 model130 token130 prompt130", 10),
        ["reasoning130", "machine130", "learning130", "model130", "token130", "prompt130"],
    ),
    (
        ("reasoning130 machine130 learning130 model130 token130 prompt130", 18),
        ["reasoning130", "machine130", "learning130", "model130 token130", "prompt130"],
    ),
    (
        ("reasoning130 machine130 learning130 model130 token130 prompt130", 28),
        ["reasoning130 machine130", "learning130 model130", "token130 prompt130"],
    ),
    (
        ("machine130 learning130 model130 token130 prompt130 session130", 6),
        ["machine130", "learning130", "model130", "token130", "prompt130", "session130"],
    ),
    (
        ("machine130 learning130 model130 token130 prompt130 session130", 10),
        ["machine130", "learning130", "model130", "token130", "prompt130", "session130"],
    ),
    (
        ("machine130 learning130 model130 token130 prompt130 session130", 18),
        ["machine130", "learning130", "model130 token130", "prompt130", "session130"],
    ),
    (
        ("machine130 learning130 model130 token130 prompt130 session130", 28),
        ["machine130 learning130", "model130 token130 prompt130", "session130"],
    ),
    (
        ("learning130 model130 token130 prompt130 session130 library130", 6),
        ["learning130", "model130", "token130", "prompt130", "session130", "library130"],
    ),
    (
        ("learning130 model130 token130 prompt130 session130 library130", 10),
        ["learning130", "model130", "token130", "prompt130", "session130", "library130"],
    ),
    (
        ("learning130 model130 token130 prompt130 session130 library130", 18),
        ["learning130", "model130 token130", "prompt130", "session130", "library130"],
    ),
    (
        ("learning130 model130 token130 prompt130 session130 library130", 28),
        ["learning130 model130", "token130 prompt130", "session130 library130"],
    ),
    (
        ("model130 token130 prompt130 session130 library130 service130", 6),
        ["model130", "token130", "prompt130", "session130", "library130", "service130"],
    ),
    (
        ("model130 token130 prompt130 session130 library130 service130", 10),
        ["model130", "token130", "prompt130", "session130", "library130", "service130"],
    ),
    (
        ("model130 token130 prompt130 session130 library130 service130", 18),
        ["model130 token130", "prompt130", "session130", "library130", "service130"],
    ),
    (
        ("model130 token130 prompt130 session130 library130 service130", 28),
        ["model130 token130 prompt130", "session130 library130", "service130"],
    ),
    (
        ("token130 prompt130 session130 library130 service130 gateway130", 6),
        ["token130", "prompt130", "session130", "library130", "service130", "gateway130"],
    ),
    (
        ("token130 prompt130 session130 library130 service130 gateway130", 10),
        ["token130", "prompt130", "session130", "library130", "service130", "gateway130"],
    ),
    (
        ("token130 prompt130 session130 library130 service130 gateway130", 18),
        ["token130 prompt130", "session130", "library130", "service130", "gateway130"],
    ),
    (
        ("token130 prompt130 session130 library130 service130 gateway130", 28),
        ["token130 prompt130", "session130 library130", "service130 gateway130"],
    ),
    (
        ("prompt130 session130 library130 service130 gateway130 storage130", 6),
        ["prompt130", "session130", "library130", "service130", "gateway130", "storage130"],
    ),
    (
        ("prompt130 session130 library130 service130 gateway130 storage130", 10),
        ["prompt130", "session130", "library130", "service130", "gateway130", "storage130"],
    ),
    (
        ("prompt130 session130 library130 service130 gateway130 storage130", 18),
        ["prompt130", "session130", "library130", "service130", "gateway130", "storage130"],
    ),
    (
        ("prompt130 session130 library130 service130 gateway130 storage130", 28),
        ["prompt130 session130", "library130 service130", "gateway130 storage130"],
    ),
    (
        ("session130 library130 service130 gateway130 storage130 network130", 6),
        ["session130", "library130", "service130", "gateway130", "storage130", "network130"],
    ),
    (
        ("session130 library130 service130 gateway130 storage130 network130", 10),
        ["session130", "library130", "service130", "gateway130", "storage130", "network130"],
    ),
    (
        ("session130 library130 service130 gateway130 storage130 network130", 18),
        ["session130", "library130", "service130", "gateway130", "storage130", "network130"],
    ),
    (
        ("session130 library130 service130 gateway130 storage130 network130", 28),
        ["session130 library130", "service130 gateway130", "storage130 network130"],
    ),
    (
        ("library130 service130 gateway130 storage130 network130 latency130", 6),
        ["library130", "service130", "gateway130", "storage130", "network130", "latency130"],
    ),
    (
        ("library130 service130 gateway130 storage130 network130 latency130", 10),
        ["library130", "service130", "gateway130", "storage130", "network130", "latency130"],
    ),
    (
        ("library130 service130 gateway130 storage130 network130 latency130", 18),
        ["library130", "service130", "gateway130", "storage130", "network130", "latency130"],
    ),
    (
        ("library130 service130 gateway130 storage130 network130 latency130", 28),
        ["library130 service130", "gateway130 storage130", "network130 latency130"],
    ),
    (
        ("service130 gateway130 storage130 network130 latency130 buffer130", 6),
        ["service130", "gateway130", "storage130", "network130", "latency130", "buffer130"],
    ),
    (
        ("service130 gateway130 storage130 network130 latency130 buffer130", 10),
        ["service130", "gateway130", "storage130", "network130", "latency130", "buffer130"],
    ),
    (
        ("service130 gateway130 storage130 network130 latency130 buffer130", 18),
        ["service130", "gateway130", "storage130", "network130", "latency130", "buffer130"],
    ),
    (
        ("service130 gateway130 storage130 network130 latency130 buffer130", 28),
        ["service130 gateway130", "storage130 network130", "latency130 buffer130"],
    ),
    (
        ("gateway130 storage130 network130 latency130 buffer130 queue130", 6),
        ["gateway130", "storage130", "network130", "latency130", "buffer130", "queue130"],
    ),
    (
        ("gateway130 storage130 network130 latency130 buffer130 queue130", 10),
        ["gateway130", "storage130", "network130", "latency130", "buffer130", "queue130"],
    ),
    (
        ("gateway130 storage130 network130 latency130 buffer130 queue130", 18),
        ["gateway130", "storage130", "network130", "latency130", "buffer130 queue130"],
    ),
    (
        ("gateway130 storage130 network130 latency130 buffer130 queue130", 28),
        ["gateway130 storage130", "network130 latency130", "buffer130 queue130"],
    ),
    (
        ("storage130 network130 latency130 buffer130 queue130 worker130", 6),
        ["storage130", "network130", "latency130", "buffer130", "queue130", "worker130"],
    ),
    (
        ("storage130 network130 latency130 buffer130 queue130 worker130", 10),
        ["storage130", "network130", "latency130", "buffer130", "queue130", "worker130"],
    ),
    (
        ("storage130 network130 latency130 buffer130 queue130 worker130", 18),
        ["storage130", "network130", "latency130", "buffer130 queue130", "worker130"],
    ),
    (
        ("storage130 network130 latency130 buffer130 queue130 worker130", 28),
        ["storage130 network130", "latency130 buffer130", "queue130 worker130"],
    ),
    (
        ("network130 latency130 buffer130 queue130 worker130 kernel130", 6),
        ["network130", "latency130", "buffer130", "queue130", "worker130", "kernel130"],
    ),
    (
        ("network130 latency130 buffer130 queue130 worker130 kernel130", 10),
        ["network130", "latency130", "buffer130", "queue130", "worker130", "kernel130"],
    ),
    (
        ("network130 latency130 buffer130 queue130 worker130 kernel130", 18),
        ["network130", "latency130", "buffer130 queue130", "worker130", "kernel130"],
    ),
    (
        ("network130 latency130 buffer130 queue130 worker130 kernel130", 28),
        ["network130 latency130", "buffer130 queue130 worker130", "kernel130"],
    ),
    (
        ("latency130 buffer130 queue130 worker130 kernel130 signal130", 6),
        ["latency130", "buffer130", "queue130", "worker130", "kernel130", "signal130"],
    ),
    (
        ("latency130 buffer130 queue130 worker130 kernel130 signal130", 10),
        ["latency130", "buffer130", "queue130", "worker130", "kernel130", "signal130"],
    ),
    (
        ("latency130 buffer130 queue130 worker130 kernel130 signal130", 18),
        ["latency130", "buffer130 queue130", "worker130", "kernel130", "signal130"],
    ),
    (
        ("latency130 buffer130 queue130 worker130 kernel130 signal130", 28),
        ["latency130 buffer130", "queue130 worker130 kernel130", "signal130"],
    ),
    (
        ("buffer130 queue130 worker130 kernel130 signal130 packet130", 6),
        ["buffer130", "queue130", "worker130", "kernel130", "signal130", "packet130"],
    ),
    (
        ("buffer130 queue130 worker130 kernel130 signal130 packet130", 10),
        ["buffer130", "queue130", "worker130", "kernel130", "signal130", "packet130"],
    ),
    (
        ("buffer130 queue130 worker130 kernel130 signal130 packet130", 18),
        ["buffer130 queue130", "worker130", "kernel130", "signal130", "packet130"],
    ),
    (
        ("buffer130 queue130 worker130 kernel130 signal130 packet130", 28),
        ["buffer130 queue130 worker130", "kernel130 signal130", "packet130"],
    ),
    (
        ("queue130 worker130 kernel130 signal130 packet130 router130", 6),
        ["queue130", "worker130", "kernel130", "signal130", "packet130", "router130"],
    ),
    (
        ("queue130 worker130 kernel130 signal130 packet130 router130", 10),
        ["queue130", "worker130", "kernel130", "signal130", "packet130", "router130"],
    ),
    (
        ("queue130 worker130 kernel130 signal130 packet130 router130", 18),
        ["queue130 worker130", "kernel130", "signal130", "packet130", "router130"],
    ),
    (
        ("queue130 worker130 kernel130 signal130 packet130 router130", 28),
        ["queue130 worker130 kernel130", "signal130 packet130", "router130"],
    ),
    (
        ("worker130 kernel130 signal130 packet130 router130 cluster130", 6),
        ["worker130", "kernel130", "signal130", "packet130", "router130", "cluster130"],
    ),
    (
        ("worker130 kernel130 signal130 packet130 router130 cluster130", 10),
        ["worker130", "kernel130", "signal130", "packet130", "router130", "cluster130"],
    ),
    (
        ("worker130 kernel130 signal130 packet130 router130 cluster130", 18),
        ["worker130", "kernel130", "signal130", "packet130", "router130", "cluster130"],
    ),
    (
        ("worker130 kernel130 signal130 packet130 router130 cluster130", 28),
        ["worker130 kernel130", "signal130 packet130", "router130 cluster130"],
    ),
    (
        ("kernel130 signal130 packet130 router130 cluster130 mirror130", 6),
        ["kernel130", "signal130", "packet130", "router130", "cluster130", "mirror130"],
    ),
    (
        ("kernel130 signal130 packet130 router130 cluster130 mirror130", 10),
        ["kernel130", "signal130", "packet130", "router130", "cluster130", "mirror130"],
    ),
    (
        ("kernel130 signal130 packet130 router130 cluster130 mirror130", 18),
        ["kernel130", "signal130", "packet130", "router130", "cluster130", "mirror130"],
    ),
    (
        ("kernel130 signal130 packet130 router130 cluster130 mirror130", 28),
        ["kernel130 signal130", "packet130 router130", "cluster130 mirror130"],
    ),
    (
        ("signal130 packet130 router130 cluster130 mirror130 filter130", 6),
        ["signal130", "packet130", "router130", "cluster130", "mirror130", "filter130"],
    ),
    (
        ("signal130 packet130 router130 cluster130 mirror130 filter130", 10),
        ["signal130", "packet130", "router130", "cluster130", "mirror130", "filter130"],
    ),
    (
        ("signal130 packet130 router130 cluster130 mirror130 filter130", 18),
        ["signal130", "packet130", "router130", "cluster130", "mirror130", "filter130"],
    ),
    (
        ("signal130 packet130 router130 cluster130 mirror130 filter130", 28),
        ["signal130 packet130", "router130 cluster130", "mirror130 filter130"],
    ),
    (
        ("packet130 router130 cluster130 mirror130 filter130 ranking130", 6),
        ["packet130", "router130", "cluster130", "mirror130", "filter130", "ranking130"],
    ),
    (
        ("packet130 router130 cluster130 mirror130 filter130 ranking130", 10),
        ["packet130", "router130", "cluster130", "mirror130", "filter130", "ranking130"],
    ),
    (
        ("packet130 router130 cluster130 mirror130 filter130 ranking130", 18),
        ["packet130", "router130", "cluster130", "mirror130", "filter130", "ranking130"],
    ),
    (
        ("packet130 router130 cluster130 mirror130 filter130 ranking130", 28),
        ["packet130 router130", "cluster130 mirror130", "filter130 ranking130"],
    ),
    (
        ("router130 cluster130 mirror130 filter130 ranking130 encoding130", 6),
        ["router130", "cluster130", "mirror130", "filter130", "ranking130", "encoding130"],
    ),
    (
        ("router130 cluster130 mirror130 filter130 ranking130 encoding130", 10),
        ["router130", "cluster130", "mirror130", "filter130", "ranking130", "encoding130"],
    ),
    (
        ("router130 cluster130 mirror130 filter130 ranking130 encoding130", 18),
        ["router130", "cluster130", "mirror130", "filter130", "ranking130", "encoding130"],
    ),
    (
        ("router130 cluster130 mirror130 filter130 ranking130 encoding130", 28),
        ["router130 cluster130", "mirror130 filter130", "ranking130 encoding130"],
    ),
    (
        ("cluster130 mirror130 filter130 ranking130 encoding130 mapping130", 6),
        ["cluster130", "mirror130", "filter130", "ranking130", "encoding130", "mapping130"],
    ),
    (
        ("cluster130 mirror130 filter130 ranking130 encoding130 mapping130", 10),
        ["cluster130", "mirror130", "filter130", "ranking130", "encoding130", "mapping130"],
    ),
    (
        ("cluster130 mirror130 filter130 ranking130 encoding130 mapping130", 18),
        ["cluster130", "mirror130", "filter130", "ranking130", "encoding130", "mapping130"],
    ),
    (
        ("cluster130 mirror130 filter130 ranking130 encoding130 mapping130", 28),
        ["cluster130 mirror130", "filter130 ranking130", "encoding130 mapping130"],
    ),
    (
        ("mirror130 filter130 ranking130 encoding130 mapping130 record130", 6),
        ["mirror130", "filter130", "ranking130", "encoding130", "mapping130", "record130"],
    ),
    (
        ("mirror130 filter130 ranking130 encoding130 mapping130 record130", 10),
        ["mirror130", "filter130", "ranking130", "encoding130", "mapping130", "record130"],
    ),
    (
        ("mirror130 filter130 ranking130 encoding130 mapping130 record130", 18),
        ["mirror130", "filter130", "ranking130", "encoding130", "mapping130", "record130"],
    ),
    (
        ("mirror130 filter130 ranking130 encoding130 mapping130 record130", 28),
        ["mirror130 filter130", "ranking130 encoding130", "mapping130 record130"],
    ),
    (
        ("filter130 ranking130 encoding130 mapping130 record130 candle130", 6),
        ["filter130", "ranking130", "encoding130", "mapping130", "record130", "candle130"],
    ),
    (
        ("filter130 ranking130 encoding130 mapping130 record130 candle130", 10),
        ["filter130", "ranking130", "encoding130", "mapping130", "record130", "candle130"],
    ),
    (
        ("filter130 ranking130 encoding130 mapping130 record130 candle130", 18),
        ["filter130", "ranking130", "encoding130", "mapping130", "record130", "candle130"],
    ),
    (
        ("filter130 ranking130 encoding130 mapping130 record130 candle130", 28),
        ["filter130 ranking130", "encoding130 mapping130", "record130 candle130"],
    ),
    (
        ("ranking130 encoding130 mapping130 record130 candle130 thread130", 6),
        ["ranking130", "encoding130", "mapping130", "record130", "candle130", "thread130"],
    ),
    (
        ("ranking130 encoding130 mapping130 record130 candle130 thread130", 10),
        ["ranking130", "encoding130", "mapping130", "record130", "candle130", "thread130"],
    ),
    (
        ("ranking130 encoding130 mapping130 record130 candle130 thread130", 18),
        ["ranking130", "encoding130", "mapping130", "record130", "candle130", "thread130"],
    ),
    (
        ("ranking130 encoding130 mapping130 record130 candle130 thread130", 28),
        ["ranking130 encoding130", "mapping130 record130", "candle130 thread130"],
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
