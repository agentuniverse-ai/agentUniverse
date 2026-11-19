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
        ("round 16: the quick brown fox jumps over the lazy dog", 4),
        ["round", "16:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 16: the quick brown fox jumps over the lazy dog", 8),
        ["round", "16: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 16: the quick brown fox jumps over the lazy dog", 12),
        ["round 16:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 16: the quick brown fox jumps over the lazy dog", 16),
        ["round 16: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 16: the quick brown fox jumps over the lazy dog", 24),
        ["round 16: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 16: the quick brown fox jumps over the lazy dog", 32),
        ["round 16: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 16: agentuniverse is a framework for multi agents", 4),
        ["round", "16:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 16: agentuniverse is a framework for multi agents", 8),
        ["round", "16:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 16: agentuniverse is a framework for multi agents", 12),
        ["round 16:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 16: agentuniverse is a framework for multi agents", 16),
        ["round 16:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 16: agentuniverse is a framework for multi agents", 24),
        ["round 16: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 16: agentuniverse is a framework for multi agents", 32),
        ["round 16: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 16: knowledge stored as vectors enables retrieval", 4),
        ["round", "16:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 16: knowledge stored as vectors enables retrieval", 8),
        ["round", "16:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 16: knowledge stored as vectors enables retrieval", 12),
        ["round 16:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 16: knowledge stored as vectors enables retrieval", 16),
        ["round 16:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 16: knowledge stored as vectors enables retrieval", 24),
        ["round 16: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 16: knowledge stored as vectors enables retrieval", 32),
        ["round 16: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 16: the processor reads the record then stops", 4),
        ["round", "16:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 16: the processor reads the record then stops", 8),
        ["round", "16: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 16: the processor reads the record then stops", 12),
        ["round 16:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 16: the processor reads the record then stops", 16),
        ["round 16: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 16: the processor reads the record then stops", 24),
        ["round 16: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 16: the processor reads the record then stops", 32),
        ["round 16: the processor reads", "the record then stops"],
    ),
    (
        ("round 16: a worker pulls the next task from the queue", 4),
        ["round", "16:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 16: a worker pulls the next task from the queue", 8),
        ["round", "16: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 16: a worker pulls the next task from the queue", 12),
        ["round 16: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 16: a worker pulls the next task from the queue", 16),
        ["round 16: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 16: a worker pulls the next task from the queue", 24),
        ["round 16: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 16: a worker pulls the next task from the queue", 32),
        ["round 16: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 16: signals travel through the network layer", 4),
        ["round", "16:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 16: signals travel through the network layer", 8),
        ["round", "16:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 16: signals travel through the network layer", 12),
        ["round 16:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 16: signals travel through the network layer", 16),
        ["round 16:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 16: signals travel through the network layer", 24),
        ["round 16: signals travel", "through the network", "layer"],
    ),
    (
        ("round 16: signals travel through the network layer", 32),
        ["round 16: signals travel through", "the network layer"],
    ),
    (
        ("round 16: the gateway routes each request by policy", 4),
        ["round", "16:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 16: the gateway routes each request by policy", 8),
        ["round", "16: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 16: the gateway routes each request by policy", 12),
        ["round 16:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 16: the gateway routes each request by policy", 16),
        ["round 16: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 16: the gateway routes each request by policy", 24),
        ["round 16: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 16: the gateway routes each request by policy", 32),
        ["round 16: the gateway routes", "each request by policy"],
    ),
    (
        ("round 16: memory grows until the buffer is full", 4),
        ["round", "16:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 16: memory grows until the buffer is full", 8),
        ["round", "16:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 16: memory grows until the buffer is full", 12),
        ["round 16:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 16: memory grows until the buffer is full", 16),
        ["round 16: memory", "grows until the", "buffer is full"],
    ),
    (("round 16: memory grows until the buffer is full", 24), ["round 16: memory grows", "until the buffer is full"]),
    (("round 16: memory grows until the buffer is full", 32), ["round 16: memory grows until the", "buffer is full"]),
    (
        ("round 16: the cluster mirrors every packet twice", 4),
        ["round", "16:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 16: the cluster mirrors every packet twice", 8),
        ["round", "16: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 16: the cluster mirrors every packet twice", 12),
        ["round 16:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 16: the cluster mirrors every packet twice", 16),
        ["round 16: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 16: the cluster mirrors every packet twice", 24),
        ["round 16: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 16: the cluster mirrors every packet twice", 32), ["round 16: the cluster mirrors", "every packet twice"]),
    (
        ("round 16: ranking uses tokens learned from the corpus", 4),
        ["round", "16:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 16: ranking uses tokens learned from the corpus", 8),
        ["round", "16:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 16: ranking uses tokens learned from the corpus", 12),
        ["round 16:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 16: ranking uses tokens learned from the corpus", 16),
        ["round 16:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 16: ranking uses tokens learned from the corpus", 24),
        ["round 16: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 16: ranking uses tokens learned from the corpus", 32),
        ["round 16: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 16: a long session ends when the candle dies", 4),
        ["round", "16:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 16: a long session ends when the candle dies", 8),
        ["round", "16: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 16: a long session ends when the candle dies", 12),
        ["round 16: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 16: a long session ends when the candle dies", 16),
        ["round 16: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 16: a long session ends when the candle dies", 24),
        ["round 16: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 16: a long session ends when the candle dies", 32),
        ["round 16: a long session ends", "when the candle dies"],
    ),
    (
        ("round 16: encode the prompt then map the result", 4),
        ["round", "16:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 16: encode the prompt then map the result", 8),
        ["round", "16:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 16: encode the prompt then map the result", 12),
        ["round 16:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 16: encode the prompt then map the result", 16),
        ["round 16: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 16: encode the prompt then map the result", 24),
        ["round 16: encode the", "prompt then map the", "result"],
    ),
    (("round 16: encode the prompt then map the result", 32), ["round 16: encode the prompt then", "map the result"]),
    (
        ("round 16: the kernel wakes the worker at dawn", 4),
        ["round", "16:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 16: the kernel wakes the worker at dawn", 8),
        ["round", "16: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 16: the kernel wakes the worker at dawn", 12),
        ["round 16:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 16: the kernel wakes the worker at dawn", 16), ["round 16: the", "kernel wakes the", "worker at dawn"]),
    (("round 16: the kernel wakes the worker at dawn", 24), ["round 16: the kernel", "wakes the worker at dawn"]),
    (("round 16: the kernel wakes the worker at dawn", 32), ["round 16: the kernel wakes the", "worker at dawn"]),
    (
        ("round 16: service latency drops after the patch", 4),
        ["round", "16:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 16: service latency drops after the patch", 8),
        ["round", "16:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 16: service latency drops after the patch", 12),
        ["round 16:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 16: service latency drops after the patch", 16),
        ["round 16:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 16: service latency drops after the patch", 24),
        ["round 16: service", "latency drops after the", "patch"],
    ),
    (("round 16: service latency drops after the patch", 32), ["round 16: service latency drops", "after the patch"]),
    (
        ("round 16: the library caches every vector it sees", 4),
        ["round", "16:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 16: the library caches every vector it sees", 8),
        ["round", "16: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 16: the library caches every vector it sees", 12),
        ["round 16:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 16: the library caches every vector it sees", 16),
        ["round 16: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 16: the library caches every vector it sees", 24),
        ["round 16: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 16: the library caches every vector it sees", 32),
        ["round 16: the library caches", "every vector it sees"],
    ),
    (
        ("round 16: agents argue then the debate resolves", 4),
        ["round", "16:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 16: agents argue then the debate resolves", 8),
        ["round", "16:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 16: agents argue then the debate resolves", 12),
        ["round 16:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 16: agents argue then the debate resolves", 16),
        ["round 16: agents", "argue then the", "debate resolves"],
    ),
    (("round 16: agents argue then the debate resolves", 24), ["round 16: agents argue", "then the debate resolves"]),
    (("round 16: agents argue then the debate resolves", 32), ["round 16: agents argue then the", "debate resolves"]),
    (
        ("round 16: the filter keeps only strong matches", 4),
        ["round", "16:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 16: the filter keeps only strong matches", 8),
        ["round", "16: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 16: the filter keeps only strong matches", 12),
        ["round 16:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 16: the filter keeps only strong matches", 16),
        ["round 16: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 16: the filter keeps only strong matches", 24), ["round 16: the filter", "keeps only strong", "matches"]),
    (("round 16: the filter keeps only strong matches", 32), ["round 16: the filter keeps only", "strong matches"]),
    (
        ("round 16: the model answers with a short reply", 4),
        ["round", "16:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 16: the model answers with a short reply", 8),
        ["round", "16: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 16: the model answers with a short reply", 12),
        ["round 16:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 16: the model answers with a short reply", 16),
        ["round 16: the", "model answers", "with a short", "reply"],
    ),
    (("round 16: the model answers with a short reply", 24), ["round 16: the model", "answers with a short", "reply"]),
    (("round 16: the model answers with a short reply", 32), ["round 16: the model answers with", "a short reply"]),
    (
        ("round 16: the recorder stores the reasoning trace", 4),
        ["round", "16:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 16: the recorder stores the reasoning trace", 8),
        ["round", "16: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 16: the recorder stores the reasoning trace", 12),
        ["round 16:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 16: the recorder stores the reasoning trace", 16),
        ["round 16: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 16: the recorder stores the reasoning trace", 24),
        ["round 16: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 16: the recorder stores the reasoning trace", 32),
        ["round 16: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 16: the angel watches the processor run", 4),
        ["round", "16:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 16: the angel watches the processor run", 8),
        ["round", "16: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 16: the angel watches the processor run", 12),
        ["round 16:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 16: the angel watches the processor run", 16), ["round 16: the", "angel watches", "the processor", "run"]),
    (("round 16: the angel watches the processor run", 24), ["round 16: the angel", "watches the processor", "run"]),
    (("round 16: the angel watches the processor run", 32), ["round 16: the angel watches the", "processor run"]),
    (
        ("round 16: angle of the vector decides the match", 4),
        ["round", "16:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 16: angle of the vector decides the match", 8),
        ["round", "16:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 16: angle of the vector decides the match", 12),
        ["round 16:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 16: angle of the vector decides the match", 16),
        ["round 16: angle", "of the vector", "decides the", "match"],
    ),
    (("round 16: angle of the vector decides the match", 24), ["round 16: angle of the", "vector decides the match"]),
    (("round 16: angle of the vector decides the match", 32), ["round 16: angle of the vector", "decides the match"]),
    (
        ("round 16: the candle burns twice as long at night", 4),
        ["round", "16:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 16: the candle burns twice as long at night", 8),
        ["round", "16: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 16: the candle burns twice as long at night", 12),
        ["round 16:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 16: the candle burns twice as long at night", 16),
        ["round 16: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 16: the candle burns twice as long at night", 24),
        ["round 16: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 16: the candle burns twice as long at night", 32),
        ["round 16: the candle burns twice", "as long at night"],
    ),
    (
        ("round 16: a mirror of the universe in one line", 4),
        ["round", "16:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 16: a mirror of the universe in one line", 8),
        ["round", "16: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 16: a mirror of the universe in one line", 12),
        ["round 16: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 16: a mirror of the universe in one line", 16),
        ["round 16: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 16: a mirror of the universe in one line", 24), ["round 16: a mirror of", "the universe in one line"]),
    (("round 16: a mirror of the universe in one line", 32), ["round 16: a mirror of the", "universe in one line"]),
    (
        ("round 16: the queue drains before the storm", 4),
        ["round", "16:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 16: the queue drains before the storm", 8),
        ["round", "16: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 16: the queue drains before the storm", 12), ["round 16:", "the queue", "drains", "before the", "storm"]),
    (("round 16: the queue drains before the storm", 16), ["round 16: the", "queue drains", "before the storm"]),
    (("round 16: the queue drains before the storm", 24), ["round 16: the queue", "drains before the storm"]),
    (("round 16: the queue drains before the storm", 32), ["round 16: the queue drains", "before the storm"]),
    (
        ("kitten16 sitting16 agent16 angle16 universe16 memory16", 6),
        ["kitten16", "sitting16", "agent16", "angle16", "universe16", "memory16"],
    ),
    (
        ("kitten16 sitting16 agent16 angle16 universe16 memory16", 10),
        ["kitten16", "sitting16", "agent16", "angle16", "universe16", "memory16"],
    ),
    (
        ("kitten16 sitting16 agent16 angle16 universe16 memory16", 18),
        ["kitten16 sitting16", "agent16 angle16", "universe16", "memory16"],
    ),
    (
        ("kitten16 sitting16 agent16 angle16 universe16 memory16", 28),
        ["kitten16 sitting16 agent16", "angle16 universe16 memory16"],
    ),
    (
        ("sitting16 agent16 angle16 universe16 memory16 stream16", 6),
        ["sitting16", "agent16", "angle16", "universe16", "memory16", "stream16"],
    ),
    (
        ("sitting16 agent16 angle16 universe16 memory16 stream16", 10),
        ["sitting16", "agent16", "angle16", "universe16", "memory16", "stream16"],
    ),
    (
        ("sitting16 agent16 angle16 universe16 memory16 stream16", 18),
        ["sitting16 agent16", "angle16 universe16", "memory16 stream16"],
    ),
    (
        ("sitting16 agent16 angle16 universe16 memory16 stream16", 28),
        ["sitting16 agent16 angle16", "universe16 memory16 stream16"],
    ),
    (
        ("agent16 angle16 universe16 memory16 stream16 context16", 6),
        ["agent16", "angle16", "universe16", "memory16", "stream16", "context16"],
    ),
    (
        ("agent16 angle16 universe16 memory16 stream16 context16", 10),
        ["agent16", "angle16", "universe16", "memory16", "stream16", "context16"],
    ),
    (
        ("agent16 angle16 universe16 memory16 stream16 context16", 18),
        ["agent16 angle16", "universe16", "memory16 stream16", "context16"],
    ),
    (
        ("agent16 angle16 universe16 memory16 stream16 context16", 28),
        ["agent16 angle16 universe16", "memory16 stream16 context16"],
    ),
    (
        ("angle16 universe16 memory16 stream16 context16 knowledge16", 6),
        ["angle16", "universe16", "memory16", "stream16", "context16", "knowledge16"],
    ),
    (
        ("angle16 universe16 memory16 stream16 context16 knowledge16", 10),
        ["angle16", "universe16", "memory16", "stream16", "context16", "knowledge16"],
    ),
    (
        ("angle16 universe16 memory16 stream16 context16 knowledge16", 18),
        ["angle16 universe16", "memory16 stream16", "context16", "knowledge16"],
    ),
    (
        ("angle16 universe16 memory16 stream16 context16 knowledge16", 28),
        ["angle16 universe16 memory16", "stream16 context16", "knowledge16"],
    ),
    (
        ("universe16 memory16 stream16 context16 knowledge16 vector16", 6),
        ["universe16", "memory16", "stream16", "context16", "knowledge16", "vector16"],
    ),
    (
        ("universe16 memory16 stream16 context16 knowledge16 vector16", 10),
        ["universe16", "memory16", "stream16", "context16", "knowledge16", "vector16"],
    ),
    (
        ("universe16 memory16 stream16 context16 knowledge16 vector16", 18),
        ["universe16", "memory16 stream16", "context16", "knowledge16", "vector16"],
    ),
    (
        ("universe16 memory16 stream16 context16 knowledge16 vector16", 28),
        ["universe16 memory16 stream16", "context16 knowledge16", "vector16"],
    ),
    (
        ("memory16 stream16 context16 knowledge16 vector16 processor16", 6),
        ["memory16", "stream16", "context16", "knowledge16", "vector16", "processor16"],
    ),
    (
        ("memory16 stream16 context16 knowledge16 vector16 processor16", 10),
        ["memory16", "stream16", "context16", "knowledge16", "vector16", "processor16"],
    ),
    (
        ("memory16 stream16 context16 knowledge16 vector16 processor16", 18),
        ["memory16 stream16", "context16", "knowledge16", "vector16", "processor16"],
    ),
    (
        ("memory16 stream16 context16 knowledge16 vector16 processor16", 28),
        ["memory16 stream16 context16", "knowledge16 vector16", "processor16"],
    ),
    (
        ("stream16 context16 knowledge16 vector16 processor16 reasoning16", 6),
        ["stream16", "context16", "knowledge16", "vector16", "processor16", "reasoning16"],
    ),
    (
        ("stream16 context16 knowledge16 vector16 processor16 reasoning16", 10),
        ["stream16", "context16", "knowledge16", "vector16", "processor16", "reasoning16"],
    ),
    (
        ("stream16 context16 knowledge16 vector16 processor16 reasoning16", 18),
        ["stream16 context16", "knowledge16", "vector16", "processor16", "reasoning16"],
    ),
    (
        ("stream16 context16 knowledge16 vector16 processor16 reasoning16", 28),
        ["stream16 context16", "knowledge16 vector16", "processor16 reasoning16"],
    ),
    (
        ("context16 knowledge16 vector16 processor16 reasoning16 machine16", 6),
        ["context16", "knowledge16", "vector16", "processor16", "reasoning16", "machine16"],
    ),
    (
        ("context16 knowledge16 vector16 processor16 reasoning16 machine16", 10),
        ["context16", "knowledge16", "vector16", "processor16", "reasoning16", "machine16"],
    ),
    (
        ("context16 knowledge16 vector16 processor16 reasoning16 machine16", 18),
        ["context16", "knowledge16", "vector16", "processor16", "reasoning16", "machine16"],
    ),
    (
        ("context16 knowledge16 vector16 processor16 reasoning16 machine16", 28),
        ["context16 knowledge16", "vector16 processor16", "reasoning16 machine16"],
    ),
    (
        ("knowledge16 vector16 processor16 reasoning16 machine16 learning16", 6),
        ["knowledge16", "vector16", "processor16", "reasoning16", "machine16", "learning16"],
    ),
    (
        ("knowledge16 vector16 processor16 reasoning16 machine16 learning16", 10),
        ["knowledge16", "vector16", "processor16", "reasoning16", "machine16", "learning16"],
    ),
    (
        ("knowledge16 vector16 processor16 reasoning16 machine16 learning16", 18),
        ["knowledge16", "vector16", "processor16", "reasoning16", "machine16", "learning16"],
    ),
    (
        ("knowledge16 vector16 processor16 reasoning16 machine16 learning16", 28),
        ["knowledge16 vector16", "processor16 reasoning16", "machine16 learning16"],
    ),
    (
        ("vector16 processor16 reasoning16 machine16 learning16 model16", 6),
        ["vector16", "processor16", "reasoning16", "machine16", "learning16", "model16"],
    ),
    (
        ("vector16 processor16 reasoning16 machine16 learning16 model16", 10),
        ["vector16", "processor16", "reasoning16", "machine16", "learning16", "model16"],
    ),
    (
        ("vector16 processor16 reasoning16 machine16 learning16 model16", 18),
        ["vector16", "processor16", "reasoning16", "machine16", "learning16 model16"],
    ),
    (
        ("vector16 processor16 reasoning16 machine16 learning16 model16", 28),
        ["vector16 processor16", "reasoning16 machine16", "learning16 model16"],
    ),
    (
        ("processor16 reasoning16 machine16 learning16 model16 token16", 6),
        ["processor16", "reasoning16", "machine16", "learning16", "model16", "token16"],
    ),
    (
        ("processor16 reasoning16 machine16 learning16 model16 token16", 10),
        ["processor16", "reasoning16", "machine16", "learning16", "model16", "token16"],
    ),
    (
        ("processor16 reasoning16 machine16 learning16 model16 token16", 18),
        ["processor16", "reasoning16", "machine16", "learning16 model16", "token16"],
    ),
    (
        ("processor16 reasoning16 machine16 learning16 model16 token16", 28),
        ["processor16 reasoning16", "machine16 learning16 model16", "token16"],
    ),
    (
        ("reasoning16 machine16 learning16 model16 token16 prompt16", 6),
        ["reasoning16", "machine16", "learning16", "model16", "token16", "prompt16"],
    ),
    (
        ("reasoning16 machine16 learning16 model16 token16 prompt16", 10),
        ["reasoning16", "machine16", "learning16", "model16", "token16", "prompt16"],
    ),
    (
        ("reasoning16 machine16 learning16 model16 token16 prompt16", 18),
        ["reasoning16", "machine16", "learning16 model16", "token16 prompt16"],
    ),
    (
        ("reasoning16 machine16 learning16 model16 token16 prompt16", 28),
        ["reasoning16 machine16", "learning16 model16 token16", "prompt16"],
    ),
    (
        ("machine16 learning16 model16 token16 prompt16 session16", 6),
        ["machine16", "learning16", "model16", "token16", "prompt16", "session16"],
    ),
    (
        ("machine16 learning16 model16 token16 prompt16 session16", 10),
        ["machine16", "learning16", "model16", "token16", "prompt16", "session16"],
    ),
    (
        ("machine16 learning16 model16 token16 prompt16 session16", 18),
        ["machine16", "learning16 model16", "token16 prompt16", "session16"],
    ),
    (
        ("machine16 learning16 model16 token16 prompt16 session16", 28),
        ["machine16 learning16 model16", "token16 prompt16 session16"],
    ),
    (
        ("learning16 model16 token16 prompt16 session16 library16", 6),
        ["learning16", "model16", "token16", "prompt16", "session16", "library16"],
    ),
    (
        ("learning16 model16 token16 prompt16 session16 library16", 10),
        ["learning16", "model16", "token16", "prompt16", "session16", "library16"],
    ),
    (
        ("learning16 model16 token16 prompt16 session16 library16", 18),
        ["learning16 model16", "token16 prompt16", "session16", "library16"],
    ),
    (
        ("learning16 model16 token16 prompt16 session16 library16", 28),
        ["learning16 model16 token16", "prompt16 session16 library16"],
    ),
    (
        ("model16 token16 prompt16 session16 library16 service16", 6),
        ["model16", "token16", "prompt16", "session16", "library16", "service16"],
    ),
    (
        ("model16 token16 prompt16 session16 library16 service16", 10),
        ["model16", "token16", "prompt16", "session16", "library16", "service16"],
    ),
    (
        ("model16 token16 prompt16 session16 library16 service16", 18),
        ["model16 token16", "prompt16 session16", "library16", "service16"],
    ),
    (
        ("model16 token16 prompt16 session16 library16 service16", 28),
        ["model16 token16 prompt16", "session16 library16", "service16"],
    ),
    (
        ("token16 prompt16 session16 library16 service16 gateway16", 6),
        ["token16", "prompt16", "session16", "library16", "service16", "gateway16"],
    ),
    (
        ("token16 prompt16 session16 library16 service16 gateway16", 10),
        ["token16", "prompt16", "session16", "library16", "service16", "gateway16"],
    ),
    (
        ("token16 prompt16 session16 library16 service16 gateway16", 18),
        ["token16 prompt16", "session16", "library16", "service16", "gateway16"],
    ),
    (
        ("token16 prompt16 session16 library16 service16 gateway16", 28),
        ["token16 prompt16 session16", "library16 service16", "gateway16"],
    ),
    (
        ("prompt16 session16 library16 service16 gateway16 storage16", 6),
        ["prompt16", "session16", "library16", "service16", "gateway16", "storage16"],
    ),
    (
        ("prompt16 session16 library16 service16 gateway16 storage16", 10),
        ["prompt16", "session16", "library16", "service16", "gateway16", "storage16"],
    ),
    (
        ("prompt16 session16 library16 service16 gateway16 storage16", 18),
        ["prompt16 session16", "library16", "service16", "gateway16", "storage16"],
    ),
    (
        ("prompt16 session16 library16 service16 gateway16 storage16", 28),
        ["prompt16 session16 library16", "service16 gateway16", "storage16"],
    ),
    (
        ("session16 library16 service16 gateway16 storage16 network16", 6),
        ["session16", "library16", "service16", "gateway16", "storage16", "network16"],
    ),
    (
        ("session16 library16 service16 gateway16 storage16 network16", 10),
        ["session16", "library16", "service16", "gateway16", "storage16", "network16"],
    ),
    (
        ("session16 library16 service16 gateway16 storage16 network16", 18),
        ["session16", "library16", "service16", "gateway16", "storage16", "network16"],
    ),
    (
        ("session16 library16 service16 gateway16 storage16 network16", 28),
        ["session16 library16", "service16 gateway16", "storage16 network16"],
    ),
    (
        ("library16 service16 gateway16 storage16 network16 latency16", 6),
        ["library16", "service16", "gateway16", "storage16", "network16", "latency16"],
    ),
    (
        ("library16 service16 gateway16 storage16 network16 latency16", 10),
        ["library16", "service16", "gateway16", "storage16", "network16", "latency16"],
    ),
    (
        ("library16 service16 gateway16 storage16 network16 latency16", 18),
        ["library16", "service16", "gateway16", "storage16", "network16", "latency16"],
    ),
    (
        ("library16 service16 gateway16 storage16 network16 latency16", 28),
        ["library16 service16", "gateway16 storage16", "network16 latency16"],
    ),
    (
        ("service16 gateway16 storage16 network16 latency16 buffer16", 6),
        ["service16", "gateway16", "storage16", "network16", "latency16", "buffer16"],
    ),
    (
        ("service16 gateway16 storage16 network16 latency16 buffer16", 10),
        ["service16", "gateway16", "storage16", "network16", "latency16", "buffer16"],
    ),
    (
        ("service16 gateway16 storage16 network16 latency16 buffer16", 18),
        ["service16", "gateway16", "storage16", "network16", "latency16 buffer16"],
    ),
    (
        ("service16 gateway16 storage16 network16 latency16 buffer16", 28),
        ["service16 gateway16", "storage16 network16", "latency16 buffer16"],
    ),
    (
        ("gateway16 storage16 network16 latency16 buffer16 queue16", 6),
        ["gateway16", "storage16", "network16", "latency16", "buffer16", "queue16"],
    ),
    (
        ("gateway16 storage16 network16 latency16 buffer16 queue16", 10),
        ["gateway16", "storage16", "network16", "latency16", "buffer16", "queue16"],
    ),
    (
        ("gateway16 storage16 network16 latency16 buffer16 queue16", 18),
        ["gateway16", "storage16", "network16", "latency16 buffer16", "queue16"],
    ),
    (
        ("gateway16 storage16 network16 latency16 buffer16 queue16", 28),
        ["gateway16 storage16", "network16 latency16 buffer16", "queue16"],
    ),
    (
        ("storage16 network16 latency16 buffer16 queue16 worker16", 6),
        ["storage16", "network16", "latency16", "buffer16", "queue16", "worker16"],
    ),
    (
        ("storage16 network16 latency16 buffer16 queue16 worker16", 10),
        ["storage16", "network16", "latency16", "buffer16", "queue16", "worker16"],
    ),
    (
        ("storage16 network16 latency16 buffer16 queue16 worker16", 18),
        ["storage16", "network16", "latency16 buffer16", "queue16 worker16"],
    ),
    (
        ("storage16 network16 latency16 buffer16 queue16 worker16", 28),
        ["storage16 network16", "latency16 buffer16 queue16", "worker16"],
    ),
    (
        ("network16 latency16 buffer16 queue16 worker16 kernel16", 6),
        ["network16", "latency16", "buffer16", "queue16", "worker16", "kernel16"],
    ),
    (
        ("network16 latency16 buffer16 queue16 worker16 kernel16", 10),
        ["network16", "latency16", "buffer16", "queue16", "worker16", "kernel16"],
    ),
    (
        ("network16 latency16 buffer16 queue16 worker16 kernel16", 18),
        ["network16", "latency16 buffer16", "queue16 worker16", "kernel16"],
    ),
    (
        ("network16 latency16 buffer16 queue16 worker16 kernel16", 28),
        ["network16 latency16 buffer16", "queue16 worker16 kernel16"],
    ),
    (
        ("latency16 buffer16 queue16 worker16 kernel16 signal16", 6),
        ["latency16", "buffer16", "queue16", "worker16", "kernel16", "signal16"],
    ),
    (
        ("latency16 buffer16 queue16 worker16 kernel16 signal16", 10),
        ["latency16", "buffer16", "queue16", "worker16", "kernel16", "signal16"],
    ),
    (
        ("latency16 buffer16 queue16 worker16 kernel16 signal16", 18),
        ["latency16 buffer16", "queue16 worker16", "kernel16 signal16"],
    ),
    (
        ("latency16 buffer16 queue16 worker16 kernel16 signal16", 28),
        ["latency16 buffer16 queue16", "worker16 kernel16 signal16"],
    ),
    (
        ("buffer16 queue16 worker16 kernel16 signal16 packet16", 6),
        ["buffer16", "queue16", "worker16", "kernel16", "signal16", "packet16"],
    ),
    (
        ("buffer16 queue16 worker16 kernel16 signal16 packet16", 10),
        ["buffer16", "queue16", "worker16", "kernel16", "signal16", "packet16"],
    ),
    (
        ("buffer16 queue16 worker16 kernel16 signal16 packet16", 18),
        ["buffer16 queue16", "worker16 kernel16", "signal16 packet16"],
    ),
    (
        ("buffer16 queue16 worker16 kernel16 signal16 packet16", 28),
        ["buffer16 queue16 worker16", "kernel16 signal16 packet16"],
    ),
    (
        ("queue16 worker16 kernel16 signal16 packet16 router16", 6),
        ["queue16", "worker16", "kernel16", "signal16", "packet16", "router16"],
    ),
    (
        ("queue16 worker16 kernel16 signal16 packet16 router16", 10),
        ["queue16", "worker16", "kernel16", "signal16", "packet16", "router16"],
    ),
    (
        ("queue16 worker16 kernel16 signal16 packet16 router16", 18),
        ["queue16 worker16", "kernel16 signal16", "packet16 router16"],
    ),
    (
        ("queue16 worker16 kernel16 signal16 packet16 router16", 28),
        ["queue16 worker16 kernel16", "signal16 packet16 router16"],
    ),
    (
        ("worker16 kernel16 signal16 packet16 router16 cluster16", 6),
        ["worker16", "kernel16", "signal16", "packet16", "router16", "cluster16"],
    ),
    (
        ("worker16 kernel16 signal16 packet16 router16 cluster16", 10),
        ["worker16", "kernel16", "signal16", "packet16", "router16", "cluster16"],
    ),
    (
        ("worker16 kernel16 signal16 packet16 router16 cluster16", 18),
        ["worker16 kernel16", "signal16 packet16", "router16 cluster16"],
    ),
    (
        ("worker16 kernel16 signal16 packet16 router16 cluster16", 28),
        ["worker16 kernel16 signal16", "packet16 router16 cluster16"],
    ),
    (
        ("kernel16 signal16 packet16 router16 cluster16 mirror16", 6),
        ["kernel16", "signal16", "packet16", "router16", "cluster16", "mirror16"],
    ),
    (
        ("kernel16 signal16 packet16 router16 cluster16 mirror16", 10),
        ["kernel16", "signal16", "packet16", "router16", "cluster16", "mirror16"],
    ),
    (
        ("kernel16 signal16 packet16 router16 cluster16 mirror16", 18),
        ["kernel16 signal16", "packet16 router16", "cluster16 mirror16"],
    ),
    (
        ("kernel16 signal16 packet16 router16 cluster16 mirror16", 28),
        ["kernel16 signal16 packet16", "router16 cluster16 mirror16"],
    ),
    (
        ("signal16 packet16 router16 cluster16 mirror16 filter16", 6),
        ["signal16", "packet16", "router16", "cluster16", "mirror16", "filter16"],
    ),
    (
        ("signal16 packet16 router16 cluster16 mirror16 filter16", 10),
        ["signal16", "packet16", "router16", "cluster16", "mirror16", "filter16"],
    ),
    (
        ("signal16 packet16 router16 cluster16 mirror16 filter16", 18),
        ["signal16 packet16", "router16 cluster16", "mirror16 filter16"],
    ),
    (
        ("signal16 packet16 router16 cluster16 mirror16 filter16", 28),
        ["signal16 packet16 router16", "cluster16 mirror16 filter16"],
    ),
    (
        ("packet16 router16 cluster16 mirror16 filter16 ranking16", 6),
        ["packet16", "router16", "cluster16", "mirror16", "filter16", "ranking16"],
    ),
    (
        ("packet16 router16 cluster16 mirror16 filter16 ranking16", 10),
        ["packet16", "router16", "cluster16", "mirror16", "filter16", "ranking16"],
    ),
    (
        ("packet16 router16 cluster16 mirror16 filter16 ranking16", 18),
        ["packet16 router16", "cluster16 mirror16", "filter16 ranking16"],
    ),
    (
        ("packet16 router16 cluster16 mirror16 filter16 ranking16", 28),
        ["packet16 router16 cluster16", "mirror16 filter16 ranking16"],
    ),
    (
        ("router16 cluster16 mirror16 filter16 ranking16 encoding16", 6),
        ["router16", "cluster16", "mirror16", "filter16", "ranking16", "encoding16"],
    ),
    (
        ("router16 cluster16 mirror16 filter16 ranking16 encoding16", 10),
        ["router16", "cluster16", "mirror16", "filter16", "ranking16", "encoding16"],
    ),
    (
        ("router16 cluster16 mirror16 filter16 ranking16 encoding16", 18),
        ["router16 cluster16", "mirror16 filter16", "ranking16", "encoding16"],
    ),
    (
        ("router16 cluster16 mirror16 filter16 ranking16 encoding16", 28),
        ["router16 cluster16 mirror16", "filter16 ranking16", "encoding16"],
    ),
    (
        ("cluster16 mirror16 filter16 ranking16 encoding16 mapping16", 6),
        ["cluster16", "mirror16", "filter16", "ranking16", "encoding16", "mapping16"],
    ),
    (
        ("cluster16 mirror16 filter16 ranking16 encoding16 mapping16", 10),
        ["cluster16", "mirror16", "filter16", "ranking16", "encoding16", "mapping16"],
    ),
    (
        ("cluster16 mirror16 filter16 ranking16 encoding16 mapping16", 18),
        ["cluster16 mirror16", "filter16 ranking16", "encoding16", "mapping16"],
    ),
    (
        ("cluster16 mirror16 filter16 ranking16 encoding16 mapping16", 28),
        ["cluster16 mirror16 filter16", "ranking16 encoding16", "mapping16"],
    ),
    (
        ("mirror16 filter16 ranking16 encoding16 mapping16 record16", 6),
        ["mirror16", "filter16", "ranking16", "encoding16", "mapping16", "record16"],
    ),
    (
        ("mirror16 filter16 ranking16 encoding16 mapping16 record16", 10),
        ["mirror16", "filter16", "ranking16", "encoding16", "mapping16", "record16"],
    ),
    (
        ("mirror16 filter16 ranking16 encoding16 mapping16 record16", 18),
        ["mirror16 filter16", "ranking16", "encoding16", "mapping16 record16"],
    ),
    (
        ("mirror16 filter16 ranking16 encoding16 mapping16 record16", 28),
        ["mirror16 filter16 ranking16", "encoding16 mapping16", "record16"],
    ),
    (
        ("filter16 ranking16 encoding16 mapping16 record16 candle16", 6),
        ["filter16", "ranking16", "encoding16", "mapping16", "record16", "candle16"],
    ),
    (
        ("filter16 ranking16 encoding16 mapping16 record16 candle16", 10),
        ["filter16", "ranking16", "encoding16", "mapping16", "record16", "candle16"],
    ),
    (
        ("filter16 ranking16 encoding16 mapping16 record16 candle16", 18),
        ["filter16 ranking16", "encoding16", "mapping16 record16", "candle16"],
    ),
    (
        ("filter16 ranking16 encoding16 mapping16 record16 candle16", 28),
        ["filter16 ranking16", "encoding16 mapping16", "record16 candle16"],
    ),
    (
        ("ranking16 encoding16 mapping16 record16 candle16 thread16", 6),
        ["ranking16", "encoding16", "mapping16", "record16", "candle16", "thread16"],
    ),
    (
        ("ranking16 encoding16 mapping16 record16 candle16 thread16", 10),
        ["ranking16", "encoding16", "mapping16", "record16", "candle16", "thread16"],
    ),
    (
        ("ranking16 encoding16 mapping16 record16 candle16 thread16", 18),
        ["ranking16", "encoding16", "mapping16 record16", "candle16 thread16"],
    ),
    (
        ("ranking16 encoding16 mapping16 record16 candle16 thread16", 28),
        ["ranking16 encoding16", "mapping16 record16 candle16", "thread16"],
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
