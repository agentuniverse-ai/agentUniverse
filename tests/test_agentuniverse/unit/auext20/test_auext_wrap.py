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
        ("round 20: the quick brown fox jumps over the lazy dog", 4),
        ["round", "20:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 20: the quick brown fox jumps over the lazy dog", 8),
        ["round", "20: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 20: the quick brown fox jumps over the lazy dog", 12),
        ["round 20:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 20: the quick brown fox jumps over the lazy dog", 16),
        ["round 20: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 20: the quick brown fox jumps over the lazy dog", 24),
        ["round 20: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 20: the quick brown fox jumps over the lazy dog", 32),
        ["round 20: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 20: agentuniverse is a framework for multi agents", 4),
        ["round", "20:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 20: agentuniverse is a framework for multi agents", 8),
        ["round", "20:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 20: agentuniverse is a framework for multi agents", 12),
        ["round 20:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 20: agentuniverse is a framework for multi agents", 16),
        ["round 20:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 20: agentuniverse is a framework for multi agents", 24),
        ["round 20: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 20: agentuniverse is a framework for multi agents", 32),
        ["round 20: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 20: knowledge stored as vectors enables retrieval", 4),
        ["round", "20:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 20: knowledge stored as vectors enables retrieval", 8),
        ["round", "20:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 20: knowledge stored as vectors enables retrieval", 12),
        ["round 20:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 20: knowledge stored as vectors enables retrieval", 16),
        ["round 20:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 20: knowledge stored as vectors enables retrieval", 24),
        ["round 20: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 20: knowledge stored as vectors enables retrieval", 32),
        ["round 20: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 20: the processor reads the record then stops", 4),
        ["round", "20:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 20: the processor reads the record then stops", 8),
        ["round", "20: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 20: the processor reads the record then stops", 12),
        ["round 20:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 20: the processor reads the record then stops", 16),
        ["round 20: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 20: the processor reads the record then stops", 24),
        ["round 20: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 20: the processor reads the record then stops", 32),
        ["round 20: the processor reads", "the record then stops"],
    ),
    (
        ("round 20: a worker pulls the next task from the queue", 4),
        ["round", "20:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 20: a worker pulls the next task from the queue", 8),
        ["round", "20: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 20: a worker pulls the next task from the queue", 12),
        ["round 20: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 20: a worker pulls the next task from the queue", 16),
        ["round 20: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 20: a worker pulls the next task from the queue", 24),
        ["round 20: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 20: a worker pulls the next task from the queue", 32),
        ["round 20: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 20: signals travel through the network layer", 4),
        ["round", "20:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 20: signals travel through the network layer", 8),
        ["round", "20:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 20: signals travel through the network layer", 12),
        ["round 20:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 20: signals travel through the network layer", 16),
        ["round 20:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 20: signals travel through the network layer", 24),
        ["round 20: signals travel", "through the network", "layer"],
    ),
    (
        ("round 20: signals travel through the network layer", 32),
        ["round 20: signals travel through", "the network layer"],
    ),
    (
        ("round 20: the gateway routes each request by policy", 4),
        ["round", "20:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 20: the gateway routes each request by policy", 8),
        ["round", "20: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 20: the gateway routes each request by policy", 12),
        ["round 20:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 20: the gateway routes each request by policy", 16),
        ["round 20: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 20: the gateway routes each request by policy", 24),
        ["round 20: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 20: the gateway routes each request by policy", 32),
        ["round 20: the gateway routes", "each request by policy"],
    ),
    (
        ("round 20: memory grows until the buffer is full", 4),
        ["round", "20:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 20: memory grows until the buffer is full", 8),
        ["round", "20:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 20: memory grows until the buffer is full", 12),
        ["round 20:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 20: memory grows until the buffer is full", 16),
        ["round 20: memory", "grows until the", "buffer is full"],
    ),
    (("round 20: memory grows until the buffer is full", 24), ["round 20: memory grows", "until the buffer is full"]),
    (("round 20: memory grows until the buffer is full", 32), ["round 20: memory grows until the", "buffer is full"]),
    (
        ("round 20: the cluster mirrors every packet twice", 4),
        ["round", "20:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 20: the cluster mirrors every packet twice", 8),
        ["round", "20: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 20: the cluster mirrors every packet twice", 12),
        ["round 20:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 20: the cluster mirrors every packet twice", 16),
        ["round 20: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 20: the cluster mirrors every packet twice", 24),
        ["round 20: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 20: the cluster mirrors every packet twice", 32), ["round 20: the cluster mirrors", "every packet twice"]),
    (
        ("round 20: ranking uses tokens learned from the corpus", 4),
        ["round", "20:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 20: ranking uses tokens learned from the corpus", 8),
        ["round", "20:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 20: ranking uses tokens learned from the corpus", 12),
        ["round 20:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 20: ranking uses tokens learned from the corpus", 16),
        ["round 20:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 20: ranking uses tokens learned from the corpus", 24),
        ["round 20: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 20: ranking uses tokens learned from the corpus", 32),
        ["round 20: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 20: a long session ends when the candle dies", 4),
        ["round", "20:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 20: a long session ends when the candle dies", 8),
        ["round", "20: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 20: a long session ends when the candle dies", 12),
        ["round 20: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 20: a long session ends when the candle dies", 16),
        ["round 20: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 20: a long session ends when the candle dies", 24),
        ["round 20: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 20: a long session ends when the candle dies", 32),
        ["round 20: a long session ends", "when the candle dies"],
    ),
    (
        ("round 20: encode the prompt then map the result", 4),
        ["round", "20:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 20: encode the prompt then map the result", 8),
        ["round", "20:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 20: encode the prompt then map the result", 12),
        ["round 20:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 20: encode the prompt then map the result", 16),
        ["round 20: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 20: encode the prompt then map the result", 24),
        ["round 20: encode the", "prompt then map the", "result"],
    ),
    (("round 20: encode the prompt then map the result", 32), ["round 20: encode the prompt then", "map the result"]),
    (
        ("round 20: the kernel wakes the worker at dawn", 4),
        ["round", "20:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 20: the kernel wakes the worker at dawn", 8),
        ["round", "20: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 20: the kernel wakes the worker at dawn", 12),
        ["round 20:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 20: the kernel wakes the worker at dawn", 16), ["round 20: the", "kernel wakes the", "worker at dawn"]),
    (("round 20: the kernel wakes the worker at dawn", 24), ["round 20: the kernel", "wakes the worker at dawn"]),
    (("round 20: the kernel wakes the worker at dawn", 32), ["round 20: the kernel wakes the", "worker at dawn"]),
    (
        ("round 20: service latency drops after the patch", 4),
        ["round", "20:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 20: service latency drops after the patch", 8),
        ["round", "20:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 20: service latency drops after the patch", 12),
        ["round 20:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 20: service latency drops after the patch", 16),
        ["round 20:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 20: service latency drops after the patch", 24),
        ["round 20: service", "latency drops after the", "patch"],
    ),
    (("round 20: service latency drops after the patch", 32), ["round 20: service latency drops", "after the patch"]),
    (
        ("round 20: the library caches every vector it sees", 4),
        ["round", "20:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 20: the library caches every vector it sees", 8),
        ["round", "20: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 20: the library caches every vector it sees", 12),
        ["round 20:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 20: the library caches every vector it sees", 16),
        ["round 20: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 20: the library caches every vector it sees", 24),
        ["round 20: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 20: the library caches every vector it sees", 32),
        ["round 20: the library caches", "every vector it sees"],
    ),
    (
        ("round 20: agents argue then the debate resolves", 4),
        ["round", "20:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 20: agents argue then the debate resolves", 8),
        ["round", "20:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 20: agents argue then the debate resolves", 12),
        ["round 20:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 20: agents argue then the debate resolves", 16),
        ["round 20: agents", "argue then the", "debate resolves"],
    ),
    (("round 20: agents argue then the debate resolves", 24), ["round 20: agents argue", "then the debate resolves"]),
    (("round 20: agents argue then the debate resolves", 32), ["round 20: agents argue then the", "debate resolves"]),
    (
        ("round 20: the filter keeps only strong matches", 4),
        ["round", "20:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 20: the filter keeps only strong matches", 8),
        ["round", "20: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 20: the filter keeps only strong matches", 12),
        ["round 20:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 20: the filter keeps only strong matches", 16),
        ["round 20: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 20: the filter keeps only strong matches", 24), ["round 20: the filter", "keeps only strong", "matches"]),
    (("round 20: the filter keeps only strong matches", 32), ["round 20: the filter keeps only", "strong matches"]),
    (
        ("round 20: the model answers with a short reply", 4),
        ["round", "20:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 20: the model answers with a short reply", 8),
        ["round", "20: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 20: the model answers with a short reply", 12),
        ["round 20:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 20: the model answers with a short reply", 16),
        ["round 20: the", "model answers", "with a short", "reply"],
    ),
    (("round 20: the model answers with a short reply", 24), ["round 20: the model", "answers with a short", "reply"]),
    (("round 20: the model answers with a short reply", 32), ["round 20: the model answers with", "a short reply"]),
    (
        ("round 20: the recorder stores the reasoning trace", 4),
        ["round", "20:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 20: the recorder stores the reasoning trace", 8),
        ["round", "20: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 20: the recorder stores the reasoning trace", 12),
        ["round 20:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 20: the recorder stores the reasoning trace", 16),
        ["round 20: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 20: the recorder stores the reasoning trace", 24),
        ["round 20: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 20: the recorder stores the reasoning trace", 32),
        ["round 20: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 20: the angel watches the processor run", 4),
        ["round", "20:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 20: the angel watches the processor run", 8),
        ["round", "20: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 20: the angel watches the processor run", 12),
        ["round 20:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 20: the angel watches the processor run", 16), ["round 20: the", "angel watches", "the processor", "run"]),
    (("round 20: the angel watches the processor run", 24), ["round 20: the angel", "watches the processor", "run"]),
    (("round 20: the angel watches the processor run", 32), ["round 20: the angel watches the", "processor run"]),
    (
        ("round 20: angle of the vector decides the match", 4),
        ["round", "20:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 20: angle of the vector decides the match", 8),
        ["round", "20:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 20: angle of the vector decides the match", 12),
        ["round 20:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 20: angle of the vector decides the match", 16),
        ["round 20: angle", "of the vector", "decides the", "match"],
    ),
    (("round 20: angle of the vector decides the match", 24), ["round 20: angle of the", "vector decides the match"]),
    (("round 20: angle of the vector decides the match", 32), ["round 20: angle of the vector", "decides the match"]),
    (
        ("round 20: the candle burns twice as long at night", 4),
        ["round", "20:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 20: the candle burns twice as long at night", 8),
        ["round", "20: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 20: the candle burns twice as long at night", 12),
        ["round 20:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 20: the candle burns twice as long at night", 16),
        ["round 20: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 20: the candle burns twice as long at night", 24),
        ["round 20: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 20: the candle burns twice as long at night", 32),
        ["round 20: the candle burns twice", "as long at night"],
    ),
    (
        ("round 20: a mirror of the universe in one line", 4),
        ["round", "20:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 20: a mirror of the universe in one line", 8),
        ["round", "20: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 20: a mirror of the universe in one line", 12),
        ["round 20: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 20: a mirror of the universe in one line", 16),
        ["round 20: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 20: a mirror of the universe in one line", 24), ["round 20: a mirror of", "the universe in one line"]),
    (("round 20: a mirror of the universe in one line", 32), ["round 20: a mirror of the", "universe in one line"]),
    (
        ("round 20: the queue drains before the storm", 4),
        ["round", "20:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 20: the queue drains before the storm", 8),
        ["round", "20: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 20: the queue drains before the storm", 12), ["round 20:", "the queue", "drains", "before the", "storm"]),
    (("round 20: the queue drains before the storm", 16), ["round 20: the", "queue drains", "before the storm"]),
    (("round 20: the queue drains before the storm", 24), ["round 20: the queue", "drains before the storm"]),
    (("round 20: the queue drains before the storm", 32), ["round 20: the queue drains", "before the storm"]),
    (
        ("kitten20 sitting20 agent20 angle20 universe20 memory20", 6),
        ["kitten20", "sitting20", "agent20", "angle20", "universe20", "memory20"],
    ),
    (
        ("kitten20 sitting20 agent20 angle20 universe20 memory20", 10),
        ["kitten20", "sitting20", "agent20", "angle20", "universe20", "memory20"],
    ),
    (
        ("kitten20 sitting20 agent20 angle20 universe20 memory20", 18),
        ["kitten20 sitting20", "agent20 angle20", "universe20", "memory20"],
    ),
    (
        ("kitten20 sitting20 agent20 angle20 universe20 memory20", 28),
        ["kitten20 sitting20 agent20", "angle20 universe20 memory20"],
    ),
    (
        ("sitting20 agent20 angle20 universe20 memory20 stream20", 6),
        ["sitting20", "agent20", "angle20", "universe20", "memory20", "stream20"],
    ),
    (
        ("sitting20 agent20 angle20 universe20 memory20 stream20", 10),
        ["sitting20", "agent20", "angle20", "universe20", "memory20", "stream20"],
    ),
    (
        ("sitting20 agent20 angle20 universe20 memory20 stream20", 18),
        ["sitting20 agent20", "angle20 universe20", "memory20 stream20"],
    ),
    (
        ("sitting20 agent20 angle20 universe20 memory20 stream20", 28),
        ["sitting20 agent20 angle20", "universe20 memory20 stream20"],
    ),
    (
        ("agent20 angle20 universe20 memory20 stream20 context20", 6),
        ["agent20", "angle20", "universe20", "memory20", "stream20", "context20"],
    ),
    (
        ("agent20 angle20 universe20 memory20 stream20 context20", 10),
        ["agent20", "angle20", "universe20", "memory20", "stream20", "context20"],
    ),
    (
        ("agent20 angle20 universe20 memory20 stream20 context20", 18),
        ["agent20 angle20", "universe20", "memory20 stream20", "context20"],
    ),
    (
        ("agent20 angle20 universe20 memory20 stream20 context20", 28),
        ["agent20 angle20 universe20", "memory20 stream20 context20"],
    ),
    (
        ("angle20 universe20 memory20 stream20 context20 knowledge20", 6),
        ["angle20", "universe20", "memory20", "stream20", "context20", "knowledge20"],
    ),
    (
        ("angle20 universe20 memory20 stream20 context20 knowledge20", 10),
        ["angle20", "universe20", "memory20", "stream20", "context20", "knowledge20"],
    ),
    (
        ("angle20 universe20 memory20 stream20 context20 knowledge20", 18),
        ["angle20 universe20", "memory20 stream20", "context20", "knowledge20"],
    ),
    (
        ("angle20 universe20 memory20 stream20 context20 knowledge20", 28),
        ["angle20 universe20 memory20", "stream20 context20", "knowledge20"],
    ),
    (
        ("universe20 memory20 stream20 context20 knowledge20 vector20", 6),
        ["universe20", "memory20", "stream20", "context20", "knowledge20", "vector20"],
    ),
    (
        ("universe20 memory20 stream20 context20 knowledge20 vector20", 10),
        ["universe20", "memory20", "stream20", "context20", "knowledge20", "vector20"],
    ),
    (
        ("universe20 memory20 stream20 context20 knowledge20 vector20", 18),
        ["universe20", "memory20 stream20", "context20", "knowledge20", "vector20"],
    ),
    (
        ("universe20 memory20 stream20 context20 knowledge20 vector20", 28),
        ["universe20 memory20 stream20", "context20 knowledge20", "vector20"],
    ),
    (
        ("memory20 stream20 context20 knowledge20 vector20 processor20", 6),
        ["memory20", "stream20", "context20", "knowledge20", "vector20", "processor20"],
    ),
    (
        ("memory20 stream20 context20 knowledge20 vector20 processor20", 10),
        ["memory20", "stream20", "context20", "knowledge20", "vector20", "processor20"],
    ),
    (
        ("memory20 stream20 context20 knowledge20 vector20 processor20", 18),
        ["memory20 stream20", "context20", "knowledge20", "vector20", "processor20"],
    ),
    (
        ("memory20 stream20 context20 knowledge20 vector20 processor20", 28),
        ["memory20 stream20 context20", "knowledge20 vector20", "processor20"],
    ),
    (
        ("stream20 context20 knowledge20 vector20 processor20 reasoning20", 6),
        ["stream20", "context20", "knowledge20", "vector20", "processor20", "reasoning20"],
    ),
    (
        ("stream20 context20 knowledge20 vector20 processor20 reasoning20", 10),
        ["stream20", "context20", "knowledge20", "vector20", "processor20", "reasoning20"],
    ),
    (
        ("stream20 context20 knowledge20 vector20 processor20 reasoning20", 18),
        ["stream20 context20", "knowledge20", "vector20", "processor20", "reasoning20"],
    ),
    (
        ("stream20 context20 knowledge20 vector20 processor20 reasoning20", 28),
        ["stream20 context20", "knowledge20 vector20", "processor20 reasoning20"],
    ),
    (
        ("context20 knowledge20 vector20 processor20 reasoning20 machine20", 6),
        ["context20", "knowledge20", "vector20", "processor20", "reasoning20", "machine20"],
    ),
    (
        ("context20 knowledge20 vector20 processor20 reasoning20 machine20", 10),
        ["context20", "knowledge20", "vector20", "processor20", "reasoning20", "machine20"],
    ),
    (
        ("context20 knowledge20 vector20 processor20 reasoning20 machine20", 18),
        ["context20", "knowledge20", "vector20", "processor20", "reasoning20", "machine20"],
    ),
    (
        ("context20 knowledge20 vector20 processor20 reasoning20 machine20", 28),
        ["context20 knowledge20", "vector20 processor20", "reasoning20 machine20"],
    ),
    (
        ("knowledge20 vector20 processor20 reasoning20 machine20 learning20", 6),
        ["knowledge20", "vector20", "processor20", "reasoning20", "machine20", "learning20"],
    ),
    (
        ("knowledge20 vector20 processor20 reasoning20 machine20 learning20", 10),
        ["knowledge20", "vector20", "processor20", "reasoning20", "machine20", "learning20"],
    ),
    (
        ("knowledge20 vector20 processor20 reasoning20 machine20 learning20", 18),
        ["knowledge20", "vector20", "processor20", "reasoning20", "machine20", "learning20"],
    ),
    (
        ("knowledge20 vector20 processor20 reasoning20 machine20 learning20", 28),
        ["knowledge20 vector20", "processor20 reasoning20", "machine20 learning20"],
    ),
    (
        ("vector20 processor20 reasoning20 machine20 learning20 model20", 6),
        ["vector20", "processor20", "reasoning20", "machine20", "learning20", "model20"],
    ),
    (
        ("vector20 processor20 reasoning20 machine20 learning20 model20", 10),
        ["vector20", "processor20", "reasoning20", "machine20", "learning20", "model20"],
    ),
    (
        ("vector20 processor20 reasoning20 machine20 learning20 model20", 18),
        ["vector20", "processor20", "reasoning20", "machine20", "learning20 model20"],
    ),
    (
        ("vector20 processor20 reasoning20 machine20 learning20 model20", 28),
        ["vector20 processor20", "reasoning20 machine20", "learning20 model20"],
    ),
    (
        ("processor20 reasoning20 machine20 learning20 model20 token20", 6),
        ["processor20", "reasoning20", "machine20", "learning20", "model20", "token20"],
    ),
    (
        ("processor20 reasoning20 machine20 learning20 model20 token20", 10),
        ["processor20", "reasoning20", "machine20", "learning20", "model20", "token20"],
    ),
    (
        ("processor20 reasoning20 machine20 learning20 model20 token20", 18),
        ["processor20", "reasoning20", "machine20", "learning20 model20", "token20"],
    ),
    (
        ("processor20 reasoning20 machine20 learning20 model20 token20", 28),
        ["processor20 reasoning20", "machine20 learning20 model20", "token20"],
    ),
    (
        ("reasoning20 machine20 learning20 model20 token20 prompt20", 6),
        ["reasoning20", "machine20", "learning20", "model20", "token20", "prompt20"],
    ),
    (
        ("reasoning20 machine20 learning20 model20 token20 prompt20", 10),
        ["reasoning20", "machine20", "learning20", "model20", "token20", "prompt20"],
    ),
    (
        ("reasoning20 machine20 learning20 model20 token20 prompt20", 18),
        ["reasoning20", "machine20", "learning20 model20", "token20 prompt20"],
    ),
    (
        ("reasoning20 machine20 learning20 model20 token20 prompt20", 28),
        ["reasoning20 machine20", "learning20 model20 token20", "prompt20"],
    ),
    (
        ("machine20 learning20 model20 token20 prompt20 session20", 6),
        ["machine20", "learning20", "model20", "token20", "prompt20", "session20"],
    ),
    (
        ("machine20 learning20 model20 token20 prompt20 session20", 10),
        ["machine20", "learning20", "model20", "token20", "prompt20", "session20"],
    ),
    (
        ("machine20 learning20 model20 token20 prompt20 session20", 18),
        ["machine20", "learning20 model20", "token20 prompt20", "session20"],
    ),
    (
        ("machine20 learning20 model20 token20 prompt20 session20", 28),
        ["machine20 learning20 model20", "token20 prompt20 session20"],
    ),
    (
        ("learning20 model20 token20 prompt20 session20 library20", 6),
        ["learning20", "model20", "token20", "prompt20", "session20", "library20"],
    ),
    (
        ("learning20 model20 token20 prompt20 session20 library20", 10),
        ["learning20", "model20", "token20", "prompt20", "session20", "library20"],
    ),
    (
        ("learning20 model20 token20 prompt20 session20 library20", 18),
        ["learning20 model20", "token20 prompt20", "session20", "library20"],
    ),
    (
        ("learning20 model20 token20 prompt20 session20 library20", 28),
        ["learning20 model20 token20", "prompt20 session20 library20"],
    ),
    (
        ("model20 token20 prompt20 session20 library20 service20", 6),
        ["model20", "token20", "prompt20", "session20", "library20", "service20"],
    ),
    (
        ("model20 token20 prompt20 session20 library20 service20", 10),
        ["model20", "token20", "prompt20", "session20", "library20", "service20"],
    ),
    (
        ("model20 token20 prompt20 session20 library20 service20", 18),
        ["model20 token20", "prompt20 session20", "library20", "service20"],
    ),
    (
        ("model20 token20 prompt20 session20 library20 service20", 28),
        ["model20 token20 prompt20", "session20 library20", "service20"],
    ),
    (
        ("token20 prompt20 session20 library20 service20 gateway20", 6),
        ["token20", "prompt20", "session20", "library20", "service20", "gateway20"],
    ),
    (
        ("token20 prompt20 session20 library20 service20 gateway20", 10),
        ["token20", "prompt20", "session20", "library20", "service20", "gateway20"],
    ),
    (
        ("token20 prompt20 session20 library20 service20 gateway20", 18),
        ["token20 prompt20", "session20", "library20", "service20", "gateway20"],
    ),
    (
        ("token20 prompt20 session20 library20 service20 gateway20", 28),
        ["token20 prompt20 session20", "library20 service20", "gateway20"],
    ),
    (
        ("prompt20 session20 library20 service20 gateway20 storage20", 6),
        ["prompt20", "session20", "library20", "service20", "gateway20", "storage20"],
    ),
    (
        ("prompt20 session20 library20 service20 gateway20 storage20", 10),
        ["prompt20", "session20", "library20", "service20", "gateway20", "storage20"],
    ),
    (
        ("prompt20 session20 library20 service20 gateway20 storage20", 18),
        ["prompt20 session20", "library20", "service20", "gateway20", "storage20"],
    ),
    (
        ("prompt20 session20 library20 service20 gateway20 storage20", 28),
        ["prompt20 session20 library20", "service20 gateway20", "storage20"],
    ),
    (
        ("session20 library20 service20 gateway20 storage20 network20", 6),
        ["session20", "library20", "service20", "gateway20", "storage20", "network20"],
    ),
    (
        ("session20 library20 service20 gateway20 storage20 network20", 10),
        ["session20", "library20", "service20", "gateway20", "storage20", "network20"],
    ),
    (
        ("session20 library20 service20 gateway20 storage20 network20", 18),
        ["session20", "library20", "service20", "gateway20", "storage20", "network20"],
    ),
    (
        ("session20 library20 service20 gateway20 storage20 network20", 28),
        ["session20 library20", "service20 gateway20", "storage20 network20"],
    ),
    (
        ("library20 service20 gateway20 storage20 network20 latency20", 6),
        ["library20", "service20", "gateway20", "storage20", "network20", "latency20"],
    ),
    (
        ("library20 service20 gateway20 storage20 network20 latency20", 10),
        ["library20", "service20", "gateway20", "storage20", "network20", "latency20"],
    ),
    (
        ("library20 service20 gateway20 storage20 network20 latency20", 18),
        ["library20", "service20", "gateway20", "storage20", "network20", "latency20"],
    ),
    (
        ("library20 service20 gateway20 storage20 network20 latency20", 28),
        ["library20 service20", "gateway20 storage20", "network20 latency20"],
    ),
    (
        ("service20 gateway20 storage20 network20 latency20 buffer20", 6),
        ["service20", "gateway20", "storage20", "network20", "latency20", "buffer20"],
    ),
    (
        ("service20 gateway20 storage20 network20 latency20 buffer20", 10),
        ["service20", "gateway20", "storage20", "network20", "latency20", "buffer20"],
    ),
    (
        ("service20 gateway20 storage20 network20 latency20 buffer20", 18),
        ["service20", "gateway20", "storage20", "network20", "latency20 buffer20"],
    ),
    (
        ("service20 gateway20 storage20 network20 latency20 buffer20", 28),
        ["service20 gateway20", "storage20 network20", "latency20 buffer20"],
    ),
    (
        ("gateway20 storage20 network20 latency20 buffer20 queue20", 6),
        ["gateway20", "storage20", "network20", "latency20", "buffer20", "queue20"],
    ),
    (
        ("gateway20 storage20 network20 latency20 buffer20 queue20", 10),
        ["gateway20", "storage20", "network20", "latency20", "buffer20", "queue20"],
    ),
    (
        ("gateway20 storage20 network20 latency20 buffer20 queue20", 18),
        ["gateway20", "storage20", "network20", "latency20 buffer20", "queue20"],
    ),
    (
        ("gateway20 storage20 network20 latency20 buffer20 queue20", 28),
        ["gateway20 storage20", "network20 latency20 buffer20", "queue20"],
    ),
    (
        ("storage20 network20 latency20 buffer20 queue20 worker20", 6),
        ["storage20", "network20", "latency20", "buffer20", "queue20", "worker20"],
    ),
    (
        ("storage20 network20 latency20 buffer20 queue20 worker20", 10),
        ["storage20", "network20", "latency20", "buffer20", "queue20", "worker20"],
    ),
    (
        ("storage20 network20 latency20 buffer20 queue20 worker20", 18),
        ["storage20", "network20", "latency20 buffer20", "queue20 worker20"],
    ),
    (
        ("storage20 network20 latency20 buffer20 queue20 worker20", 28),
        ["storage20 network20", "latency20 buffer20 queue20", "worker20"],
    ),
    (
        ("network20 latency20 buffer20 queue20 worker20 kernel20", 6),
        ["network20", "latency20", "buffer20", "queue20", "worker20", "kernel20"],
    ),
    (
        ("network20 latency20 buffer20 queue20 worker20 kernel20", 10),
        ["network20", "latency20", "buffer20", "queue20", "worker20", "kernel20"],
    ),
    (
        ("network20 latency20 buffer20 queue20 worker20 kernel20", 18),
        ["network20", "latency20 buffer20", "queue20 worker20", "kernel20"],
    ),
    (
        ("network20 latency20 buffer20 queue20 worker20 kernel20", 28),
        ["network20 latency20 buffer20", "queue20 worker20 kernel20"],
    ),
    (
        ("latency20 buffer20 queue20 worker20 kernel20 signal20", 6),
        ["latency20", "buffer20", "queue20", "worker20", "kernel20", "signal20"],
    ),
    (
        ("latency20 buffer20 queue20 worker20 kernel20 signal20", 10),
        ["latency20", "buffer20", "queue20", "worker20", "kernel20", "signal20"],
    ),
    (
        ("latency20 buffer20 queue20 worker20 kernel20 signal20", 18),
        ["latency20 buffer20", "queue20 worker20", "kernel20 signal20"],
    ),
    (
        ("latency20 buffer20 queue20 worker20 kernel20 signal20", 28),
        ["latency20 buffer20 queue20", "worker20 kernel20 signal20"],
    ),
    (
        ("buffer20 queue20 worker20 kernel20 signal20 packet20", 6),
        ["buffer20", "queue20", "worker20", "kernel20", "signal20", "packet20"],
    ),
    (
        ("buffer20 queue20 worker20 kernel20 signal20 packet20", 10),
        ["buffer20", "queue20", "worker20", "kernel20", "signal20", "packet20"],
    ),
    (
        ("buffer20 queue20 worker20 kernel20 signal20 packet20", 18),
        ["buffer20 queue20", "worker20 kernel20", "signal20 packet20"],
    ),
    (
        ("buffer20 queue20 worker20 kernel20 signal20 packet20", 28),
        ["buffer20 queue20 worker20", "kernel20 signal20 packet20"],
    ),
    (
        ("queue20 worker20 kernel20 signal20 packet20 router20", 6),
        ["queue20", "worker20", "kernel20", "signal20", "packet20", "router20"],
    ),
    (
        ("queue20 worker20 kernel20 signal20 packet20 router20", 10),
        ["queue20", "worker20", "kernel20", "signal20", "packet20", "router20"],
    ),
    (
        ("queue20 worker20 kernel20 signal20 packet20 router20", 18),
        ["queue20 worker20", "kernel20 signal20", "packet20 router20"],
    ),
    (
        ("queue20 worker20 kernel20 signal20 packet20 router20", 28),
        ["queue20 worker20 kernel20", "signal20 packet20 router20"],
    ),
    (
        ("worker20 kernel20 signal20 packet20 router20 cluster20", 6),
        ["worker20", "kernel20", "signal20", "packet20", "router20", "cluster20"],
    ),
    (
        ("worker20 kernel20 signal20 packet20 router20 cluster20", 10),
        ["worker20", "kernel20", "signal20", "packet20", "router20", "cluster20"],
    ),
    (
        ("worker20 kernel20 signal20 packet20 router20 cluster20", 18),
        ["worker20 kernel20", "signal20 packet20", "router20 cluster20"],
    ),
    (
        ("worker20 kernel20 signal20 packet20 router20 cluster20", 28),
        ["worker20 kernel20 signal20", "packet20 router20 cluster20"],
    ),
    (
        ("kernel20 signal20 packet20 router20 cluster20 mirror20", 6),
        ["kernel20", "signal20", "packet20", "router20", "cluster20", "mirror20"],
    ),
    (
        ("kernel20 signal20 packet20 router20 cluster20 mirror20", 10),
        ["kernel20", "signal20", "packet20", "router20", "cluster20", "mirror20"],
    ),
    (
        ("kernel20 signal20 packet20 router20 cluster20 mirror20", 18),
        ["kernel20 signal20", "packet20 router20", "cluster20 mirror20"],
    ),
    (
        ("kernel20 signal20 packet20 router20 cluster20 mirror20", 28),
        ["kernel20 signal20 packet20", "router20 cluster20 mirror20"],
    ),
    (
        ("signal20 packet20 router20 cluster20 mirror20 filter20", 6),
        ["signal20", "packet20", "router20", "cluster20", "mirror20", "filter20"],
    ),
    (
        ("signal20 packet20 router20 cluster20 mirror20 filter20", 10),
        ["signal20", "packet20", "router20", "cluster20", "mirror20", "filter20"],
    ),
    (
        ("signal20 packet20 router20 cluster20 mirror20 filter20", 18),
        ["signal20 packet20", "router20 cluster20", "mirror20 filter20"],
    ),
    (
        ("signal20 packet20 router20 cluster20 mirror20 filter20", 28),
        ["signal20 packet20 router20", "cluster20 mirror20 filter20"],
    ),
    (
        ("packet20 router20 cluster20 mirror20 filter20 ranking20", 6),
        ["packet20", "router20", "cluster20", "mirror20", "filter20", "ranking20"],
    ),
    (
        ("packet20 router20 cluster20 mirror20 filter20 ranking20", 10),
        ["packet20", "router20", "cluster20", "mirror20", "filter20", "ranking20"],
    ),
    (
        ("packet20 router20 cluster20 mirror20 filter20 ranking20", 18),
        ["packet20 router20", "cluster20 mirror20", "filter20 ranking20"],
    ),
    (
        ("packet20 router20 cluster20 mirror20 filter20 ranking20", 28),
        ["packet20 router20 cluster20", "mirror20 filter20 ranking20"],
    ),
    (
        ("router20 cluster20 mirror20 filter20 ranking20 encoding20", 6),
        ["router20", "cluster20", "mirror20", "filter20", "ranking20", "encoding20"],
    ),
    (
        ("router20 cluster20 mirror20 filter20 ranking20 encoding20", 10),
        ["router20", "cluster20", "mirror20", "filter20", "ranking20", "encoding20"],
    ),
    (
        ("router20 cluster20 mirror20 filter20 ranking20 encoding20", 18),
        ["router20 cluster20", "mirror20 filter20", "ranking20", "encoding20"],
    ),
    (
        ("router20 cluster20 mirror20 filter20 ranking20 encoding20", 28),
        ["router20 cluster20 mirror20", "filter20 ranking20", "encoding20"],
    ),
    (
        ("cluster20 mirror20 filter20 ranking20 encoding20 mapping20", 6),
        ["cluster20", "mirror20", "filter20", "ranking20", "encoding20", "mapping20"],
    ),
    (
        ("cluster20 mirror20 filter20 ranking20 encoding20 mapping20", 10),
        ["cluster20", "mirror20", "filter20", "ranking20", "encoding20", "mapping20"],
    ),
    (
        ("cluster20 mirror20 filter20 ranking20 encoding20 mapping20", 18),
        ["cluster20 mirror20", "filter20 ranking20", "encoding20", "mapping20"],
    ),
    (
        ("cluster20 mirror20 filter20 ranking20 encoding20 mapping20", 28),
        ["cluster20 mirror20 filter20", "ranking20 encoding20", "mapping20"],
    ),
    (
        ("mirror20 filter20 ranking20 encoding20 mapping20 record20", 6),
        ["mirror20", "filter20", "ranking20", "encoding20", "mapping20", "record20"],
    ),
    (
        ("mirror20 filter20 ranking20 encoding20 mapping20 record20", 10),
        ["mirror20", "filter20", "ranking20", "encoding20", "mapping20", "record20"],
    ),
    (
        ("mirror20 filter20 ranking20 encoding20 mapping20 record20", 18),
        ["mirror20 filter20", "ranking20", "encoding20", "mapping20 record20"],
    ),
    (
        ("mirror20 filter20 ranking20 encoding20 mapping20 record20", 28),
        ["mirror20 filter20 ranking20", "encoding20 mapping20", "record20"],
    ),
    (
        ("filter20 ranking20 encoding20 mapping20 record20 candle20", 6),
        ["filter20", "ranking20", "encoding20", "mapping20", "record20", "candle20"],
    ),
    (
        ("filter20 ranking20 encoding20 mapping20 record20 candle20", 10),
        ["filter20", "ranking20", "encoding20", "mapping20", "record20", "candle20"],
    ),
    (
        ("filter20 ranking20 encoding20 mapping20 record20 candle20", 18),
        ["filter20 ranking20", "encoding20", "mapping20 record20", "candle20"],
    ),
    (
        ("filter20 ranking20 encoding20 mapping20 record20 candle20", 28),
        ["filter20 ranking20", "encoding20 mapping20", "record20 candle20"],
    ),
    (
        ("ranking20 encoding20 mapping20 record20 candle20 thread20", 6),
        ["ranking20", "encoding20", "mapping20", "record20", "candle20", "thread20"],
    ),
    (
        ("ranking20 encoding20 mapping20 record20 candle20 thread20", 10),
        ["ranking20", "encoding20", "mapping20", "record20", "candle20", "thread20"],
    ),
    (
        ("ranking20 encoding20 mapping20 record20 candle20 thread20", 18),
        ["ranking20", "encoding20", "mapping20 record20", "candle20 thread20"],
    ),
    (
        ("ranking20 encoding20 mapping20 record20 candle20 thread20", 28),
        ["ranking20 encoding20", "mapping20 record20 candle20", "thread20"],
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
