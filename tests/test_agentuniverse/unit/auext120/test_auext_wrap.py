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
        ("round 120: the quick brown fox jumps over the lazy dog", 4),
        ["round", "120:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 120: the quick brown fox jumps over the lazy dog", 8),
        ["round", "120: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 120: the quick brown fox jumps over the lazy dog", 12),
        ["round 120:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 120: the quick brown fox jumps over the lazy dog", 16),
        ["round 120: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 120: the quick brown fox jumps over the lazy dog", 24),
        ["round 120: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 120: the quick brown fox jumps over the lazy dog", 32),
        ["round 120: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 120: agentuniverse is a framework for multi agents", 4),
        ["round", "120:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 120: agentuniverse is a framework for multi agents", 8),
        ["round", "120:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 120: agentuniverse is a framework for multi agents", 12),
        ["round 120:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 120: agentuniverse is a framework for multi agents", 16),
        ["round 120:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 120: agentuniverse is a framework for multi agents", 24),
        ["round 120: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 120: agentuniverse is a framework for multi agents", 32),
        ["round 120: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 120: knowledge stored as vectors enables retrieval", 4),
        ["round", "120:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 120: knowledge stored as vectors enables retrieval", 8),
        ["round", "120:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 120: knowledge stored as vectors enables retrieval", 12),
        ["round 120:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 120: knowledge stored as vectors enables retrieval", 16),
        ["round 120:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 120: knowledge stored as vectors enables retrieval", 24),
        ["round 120: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 120: knowledge stored as vectors enables retrieval", 32),
        ["round 120: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 120: the processor reads the record then stops", 4),
        ["round", "120:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 120: the processor reads the record then stops", 8),
        ["round", "120: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 120: the processor reads the record then stops", 12),
        ["round 120:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 120: the processor reads the record then stops", 16),
        ["round 120: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 120: the processor reads the record then stops", 24),
        ["round 120: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 120: the processor reads the record then stops", 32),
        ["round 120: the processor reads", "the record then stops"],
    ),
    (
        ("round 120: a worker pulls the next task from the queue", 4),
        ["round", "120:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 120: a worker pulls the next task from the queue", 8),
        ["round", "120: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 120: a worker pulls the next task from the queue", 12),
        ["round 120: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 120: a worker pulls the next task from the queue", 16),
        ["round 120: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 120: a worker pulls the next task from the queue", 24),
        ["round 120: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 120: a worker pulls the next task from the queue", 32),
        ["round 120: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 120: signals travel through the network layer", 4),
        ["round", "120:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 120: signals travel through the network layer", 8),
        ["round", "120:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 120: signals travel through the network layer", 12),
        ["round 120:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 120: signals travel through the network layer", 16),
        ["round 120:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 120: signals travel through the network layer", 24),
        ["round 120: signals", "travel through the", "network layer"],
    ),
    (
        ("round 120: signals travel through the network layer", 32),
        ["round 120: signals travel", "through the network layer"],
    ),
    (
        ("round 120: the gateway routes each request by policy", 4),
        ["round", "120:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 120: the gateway routes each request by policy", 8),
        ["round", "120: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 120: the gateway routes each request by policy", 12),
        ["round 120:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 120: the gateway routes each request by policy", 16),
        ["round 120: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 120: the gateway routes each request by policy", 24),
        ["round 120: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 120: the gateway routes each request by policy", 32),
        ["round 120: the gateway routes", "each request by policy"],
    ),
    (
        ("round 120: memory grows until the buffer is full", 4),
        ["round", "120:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 120: memory grows until the buffer is full", 8),
        ["round", "120:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 120: memory grows until the buffer is full", 12),
        ["round 120:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 120: memory grows until the buffer is full", 16),
        ["round 120:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 120: memory grows until the buffer is full", 24), ["round 120: memory grows", "until the buffer is full"]),
    (("round 120: memory grows until the buffer is full", 32), ["round 120: memory grows until", "the buffer is full"]),
    (
        ("round 120: the cluster mirrors every packet twice", 4),
        ["round", "120:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 120: the cluster mirrors every packet twice", 8),
        ["round", "120: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 120: the cluster mirrors every packet twice", 12),
        ["round 120:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 120: the cluster mirrors every packet twice", 16),
        ["round 120: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 120: the cluster mirrors every packet twice", 24),
        ["round 120: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 120: the cluster mirrors every packet twice", 32),
        ["round 120: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 120: ranking uses tokens learned from the corpus", 4),
        ["round", "120:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 120: ranking uses tokens learned from the corpus", 8),
        ["round", "120:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 120: ranking uses tokens learned from the corpus", 12),
        ["round 120:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 120: ranking uses tokens learned from the corpus", 16),
        ["round 120:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 120: ranking uses tokens learned from the corpus", 24),
        ["round 120: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 120: ranking uses tokens learned from the corpus", 32),
        ["round 120: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 120: a long session ends when the candle dies", 4),
        ["round", "120:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 120: a long session ends when the candle dies", 8),
        ["round", "120: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 120: a long session ends when the candle dies", 12),
        ["round 120: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 120: a long session ends when the candle dies", 16),
        ["round 120: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 120: a long session ends when the candle dies", 24),
        ["round 120: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 120: a long session ends when the candle dies", 32),
        ["round 120: a long session ends", "when the candle dies"],
    ),
    (
        ("round 120: encode the prompt then map the result", 4),
        ["round", "120:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 120: encode the prompt then map the result", 8),
        ["round", "120:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 120: encode the prompt then map the result", 12),
        ["round 120:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 120: encode the prompt then map the result", 16),
        ["round 120:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 120: encode the prompt then map the result", 24),
        ["round 120: encode the", "prompt then map the", "result"],
    ),
    (("round 120: encode the prompt then map the result", 32), ["round 120: encode the prompt", "then map the result"]),
    (
        ("round 120: the kernel wakes the worker at dawn", 4),
        ["round", "120:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 120: the kernel wakes the worker at dawn", 8),
        ["round", "120: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 120: the kernel wakes the worker at dawn", 12),
        ["round 120:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 120: the kernel wakes the worker at dawn", 16), ["round 120: the", "kernel wakes the", "worker at dawn"]),
    (("round 120: the kernel wakes the worker at dawn", 24), ["round 120: the kernel", "wakes the worker at dawn"]),
    (("round 120: the kernel wakes the worker at dawn", 32), ["round 120: the kernel wakes the", "worker at dawn"]),
    (
        ("round 120: service latency drops after the patch", 4),
        ["round", "120:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 120: service latency drops after the patch", 8),
        ["round", "120:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 120: service latency drops after the patch", 12),
        ["round 120:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 120: service latency drops after the patch", 16),
        ["round 120:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 120: service latency drops after the patch", 24),
        ["round 120: service", "latency drops after the", "patch"],
    ),
    (("round 120: service latency drops after the patch", 32), ["round 120: service latency drops", "after the patch"]),
    (
        ("round 120: the library caches every vector it sees", 4),
        ["round", "120:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 120: the library caches every vector it sees", 8),
        ["round", "120: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 120: the library caches every vector it sees", 12),
        ["round 120:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 120: the library caches every vector it sees", 16),
        ["round 120: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 120: the library caches every vector it sees", 24),
        ["round 120: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 120: the library caches every vector it sees", 32),
        ["round 120: the library caches", "every vector it sees"],
    ),
    (
        ("round 120: agents argue then the debate resolves", 4),
        ["round", "120:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 120: agents argue then the debate resolves", 8),
        ["round", "120:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 120: agents argue then the debate resolves", 12),
        ["round 120:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 120: agents argue then the debate resolves", 16),
        ["round 120:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 120: agents argue then the debate resolves", 24), ["round 120: agents argue", "then the debate resolves"]),
    (("round 120: agents argue then the debate resolves", 32), ["round 120: agents argue then the", "debate resolves"]),
    (
        ("round 120: the filter keeps only strong matches", 4),
        ["round", "120:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 120: the filter keeps only strong matches", 8),
        ["round", "120: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 120: the filter keeps only strong matches", 12),
        ["round 120:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 120: the filter keeps only strong matches", 16),
        ["round 120: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 120: the filter keeps only strong matches", 24),
        ["round 120: the filter", "keeps only strong", "matches"],
    ),
    (("round 120: the filter keeps only strong matches", 32), ["round 120: the filter keeps only", "strong matches"]),
    (
        ("round 120: the model answers with a short reply", 4),
        ["round", "120:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 120: the model answers with a short reply", 8),
        ["round", "120: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 120: the model answers with a short reply", 12),
        ["round 120:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 120: the model answers with a short reply", 16),
        ["round 120: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 120: the model answers with a short reply", 24),
        ["round 120: the model", "answers with a short", "reply"],
    ),
    (("round 120: the model answers with a short reply", 32), ["round 120: the model answers", "with a short reply"]),
    (
        ("round 120: the recorder stores the reasoning trace", 4),
        ["round", "120:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 120: the recorder stores the reasoning trace", 8),
        ["round", "120: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 120: the recorder stores the reasoning trace", 12),
        ["round 120:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 120: the recorder stores the reasoning trace", 16),
        ["round 120: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 120: the recorder stores the reasoning trace", 24),
        ["round 120: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 120: the recorder stores the reasoning trace", 32),
        ["round 120: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 120: the angel watches the processor run", 4),
        ["round", "120:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 120: the angel watches the processor run", 8),
        ["round", "120: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 120: the angel watches the processor run", 12),
        ["round 120:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 120: the angel watches the processor run", 16),
        ["round 120: the", "angel watches", "the processor", "run"],
    ),
    (("round 120: the angel watches the processor run", 24), ["round 120: the angel", "watches the processor", "run"]),
    (("round 120: the angel watches the processor run", 32), ["round 120: the angel watches the", "processor run"]),
    (
        ("round 120: angle of the vector decides the match", 4),
        ["round", "120:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 120: angle of the vector decides the match", 8),
        ["round", "120:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 120: angle of the vector decides the match", 12),
        ["round 120:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 120: angle of the vector decides the match", 16),
        ["round 120: angle", "of the vector", "decides the", "match"],
    ),
    (("round 120: angle of the vector decides the match", 24), ["round 120: angle of the", "vector decides the match"]),
    (("round 120: angle of the vector decides the match", 32), ["round 120: angle of the vector", "decides the match"]),
    (
        ("round 120: the candle burns twice as long at night", 4),
        ["round", "120:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 120: the candle burns twice as long at night", 8),
        ["round", "120: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 120: the candle burns twice as long at night", 12),
        ["round 120:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 120: the candle burns twice as long at night", 16),
        ["round 120: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 120: the candle burns twice as long at night", 24),
        ["round 120: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 120: the candle burns twice as long at night", 32),
        ["round 120: the candle burns", "twice as long at night"],
    ),
    (
        ("round 120: a mirror of the universe in one line", 4),
        ["round", "120:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 120: a mirror of the universe in one line", 8),
        ["round", "120: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 120: a mirror of the universe in one line", 12),
        ["round 120: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 120: a mirror of the universe in one line", 16),
        ["round 120: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 120: a mirror of the universe in one line", 24), ["round 120: a mirror of", "the universe in one line"]),
    (("round 120: a mirror of the universe in one line", 32), ["round 120: a mirror of the", "universe in one line"]),
    (
        ("round 120: the queue drains before the storm", 4),
        ["round", "120:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 120: the queue drains before the storm", 8),
        ["round", "120: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 120: the queue drains before the storm", 12),
        ["round 120:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 120: the queue drains before the storm", 16), ["round 120: the", "queue drains", "before the storm"]),
    (("round 120: the queue drains before the storm", 24), ["round 120: the queue", "drains before the storm"]),
    (("round 120: the queue drains before the storm", 32), ["round 120: the queue drains", "before the storm"]),
    (
        ("kitten120 sitting120 agent120 angle120 universe120 memory120", 6),
        ["kitten120", "sitting120", "agent120", "angle120", "universe120", "memory120"],
    ),
    (
        ("kitten120 sitting120 agent120 angle120 universe120 memory120", 10),
        ["kitten120", "sitting120", "agent120", "angle120", "universe120", "memory120"],
    ),
    (
        ("kitten120 sitting120 agent120 angle120 universe120 memory120", 18),
        ["kitten120", "sitting120", "agent120 angle120", "universe120", "memory120"],
    ),
    (
        ("kitten120 sitting120 agent120 angle120 universe120 memory120", 28),
        ["kitten120 sitting120", "agent120 angle120", "universe120 memory120"],
    ),
    (
        ("sitting120 agent120 angle120 universe120 memory120 stream120", 6),
        ["sitting120", "agent120", "angle120", "universe120", "memory120", "stream120"],
    ),
    (
        ("sitting120 agent120 angle120 universe120 memory120 stream120", 10),
        ["sitting120", "agent120", "angle120", "universe120", "memory120", "stream120"],
    ),
    (
        ("sitting120 agent120 angle120 universe120 memory120 stream120", 18),
        ["sitting120", "agent120 angle120", "universe120", "memory120", "stream120"],
    ),
    (
        ("sitting120 agent120 angle120 universe120 memory120 stream120", 28),
        ["sitting120 agent120 angle120", "universe120 memory120", "stream120"],
    ),
    (
        ("agent120 angle120 universe120 memory120 stream120 context120", 6),
        ["agent120", "angle120", "universe120", "memory120", "stream120", "context120"],
    ),
    (
        ("agent120 angle120 universe120 memory120 stream120 context120", 10),
        ["agent120", "angle120", "universe120", "memory120", "stream120", "context120"],
    ),
    (
        ("agent120 angle120 universe120 memory120 stream120 context120", 18),
        ["agent120 angle120", "universe120", "memory120", "stream120", "context120"],
    ),
    (
        ("agent120 angle120 universe120 memory120 stream120 context120", 28),
        ["agent120 angle120", "universe120 memory120", "stream120 context120"],
    ),
    (
        ("angle120 universe120 memory120 stream120 context120 knowledge120", 6),
        ["angle120", "universe120", "memory120", "stream120", "context120", "knowledge120"],
    ),
    (
        ("angle120 universe120 memory120 stream120 context120 knowledge120", 10),
        ["angle120", "universe120", "memory120", "stream120", "context120", "knowledge120"],
    ),
    (
        ("angle120 universe120 memory120 stream120 context120 knowledge120", 18),
        ["angle120", "universe120", "memory120", "stream120", "context120", "knowledge120"],
    ),
    (
        ("angle120 universe120 memory120 stream120 context120 knowledge120", 28),
        ["angle120 universe120", "memory120 stream120", "context120 knowledge120"],
    ),
    (
        ("universe120 memory120 stream120 context120 knowledge120 vector120", 6),
        ["universe120", "memory120", "stream120", "context120", "knowledge120", "vector120"],
    ),
    (
        ("universe120 memory120 stream120 context120 knowledge120 vector120", 10),
        ["universe120", "memory120", "stream120", "context120", "knowledge120", "vector120"],
    ),
    (
        ("universe120 memory120 stream120 context120 knowledge120 vector120", 18),
        ["universe120", "memory120", "stream120", "context120", "knowledge120", "vector120"],
    ),
    (
        ("universe120 memory120 stream120 context120 knowledge120 vector120", 28),
        ["universe120 memory120", "stream120 context120", "knowledge120 vector120"],
    ),
    (
        ("memory120 stream120 context120 knowledge120 vector120 processor120", 6),
        ["memory120", "stream120", "context120", "knowledge120", "vector120", "processor120"],
    ),
    (
        ("memory120 stream120 context120 knowledge120 vector120 processor120", 10),
        ["memory120", "stream120", "context120", "knowledge120", "vector120", "processor120"],
    ),
    (
        ("memory120 stream120 context120 knowledge120 vector120 processor120", 18),
        ["memory120", "stream120", "context120", "knowledge120", "vector120", "processor120"],
    ),
    (
        ("memory120 stream120 context120 knowledge120 vector120 processor120", 28),
        ["memory120 stream120", "context120 knowledge120", "vector120 processor120"],
    ),
    (
        ("stream120 context120 knowledge120 vector120 processor120 reasoning120", 6),
        ["stream120", "context120", "knowledge120", "vector120", "processor120", "reasoning120"],
    ),
    (
        ("stream120 context120 knowledge120 vector120 processor120 reasoning120", 10),
        ["stream120", "context120", "knowledge120", "vector120", "processor120", "reasoning120"],
    ),
    (
        ("stream120 context120 knowledge120 vector120 processor120 reasoning120", 18),
        ["stream120", "context120", "knowledge120", "vector120", "processor120", "reasoning120"],
    ),
    (
        ("stream120 context120 knowledge120 vector120 processor120 reasoning120", 28),
        ["stream120 context120", "knowledge120 vector120", "processor120 reasoning120"],
    ),
    (
        ("context120 knowledge120 vector120 processor120 reasoning120 machine120", 6),
        ["context120", "knowledge120", "vector120", "processor120", "reasoning120", "machine120"],
    ),
    (
        ("context120 knowledge120 vector120 processor120 reasoning120 machine120", 10),
        ["context120", "knowledge120", "vector120", "processor120", "reasoning120", "machine120"],
    ),
    (
        ("context120 knowledge120 vector120 processor120 reasoning120 machine120", 18),
        ["context120", "knowledge120", "vector120", "processor120", "reasoning120", "machine120"],
    ),
    (
        ("context120 knowledge120 vector120 processor120 reasoning120 machine120", 28),
        ["context120 knowledge120", "vector120 processor120", "reasoning120 machine120"],
    ),
    (
        ("knowledge120 vector120 processor120 reasoning120 machine120 learning120", 6),
        ["knowledge120", "vector120", "processor120", "reasoning120", "machine120", "learning120"],
    ),
    (
        ("knowledge120 vector120 processor120 reasoning120 machine120 learning120", 10),
        ["knowledge120", "vector120", "processor120", "reasoning120", "machine120", "learning120"],
    ),
    (
        ("knowledge120 vector120 processor120 reasoning120 machine120 learning120", 18),
        ["knowledge120", "vector120", "processor120", "reasoning120", "machine120", "learning120"],
    ),
    (
        ("knowledge120 vector120 processor120 reasoning120 machine120 learning120", 28),
        ["knowledge120 vector120", "processor120 reasoning120", "machine120 learning120"],
    ),
    (
        ("vector120 processor120 reasoning120 machine120 learning120 model120", 6),
        ["vector120", "processor120", "reasoning120", "machine120", "learning120", "model120"],
    ),
    (
        ("vector120 processor120 reasoning120 machine120 learning120 model120", 10),
        ["vector120", "processor120", "reasoning120", "machine120", "learning120", "model120"],
    ),
    (
        ("vector120 processor120 reasoning120 machine120 learning120 model120", 18),
        ["vector120", "processor120", "reasoning120", "machine120", "learning120", "model120"],
    ),
    (
        ("vector120 processor120 reasoning120 machine120 learning120 model120", 28),
        ["vector120 processor120", "reasoning120 machine120", "learning120 model120"],
    ),
    (
        ("processor120 reasoning120 machine120 learning120 model120 token120", 6),
        ["processor120", "reasoning120", "machine120", "learning120", "model120", "token120"],
    ),
    (
        ("processor120 reasoning120 machine120 learning120 model120 token120", 10),
        ["processor120", "reasoning120", "machine120", "learning120", "model120", "token120"],
    ),
    (
        ("processor120 reasoning120 machine120 learning120 model120 token120", 18),
        ["processor120", "reasoning120", "machine120", "learning120", "model120 token120"],
    ),
    (
        ("processor120 reasoning120 machine120 learning120 model120 token120", 28),
        ["processor120 reasoning120", "machine120 learning120", "model120 token120"],
    ),
    (
        ("reasoning120 machine120 learning120 model120 token120 prompt120", 6),
        ["reasoning120", "machine120", "learning120", "model120", "token120", "prompt120"],
    ),
    (
        ("reasoning120 machine120 learning120 model120 token120 prompt120", 10),
        ["reasoning120", "machine120", "learning120", "model120", "token120", "prompt120"],
    ),
    (
        ("reasoning120 machine120 learning120 model120 token120 prompt120", 18),
        ["reasoning120", "machine120", "learning120", "model120 token120", "prompt120"],
    ),
    (
        ("reasoning120 machine120 learning120 model120 token120 prompt120", 28),
        ["reasoning120 machine120", "learning120 model120", "token120 prompt120"],
    ),
    (
        ("machine120 learning120 model120 token120 prompt120 session120", 6),
        ["machine120", "learning120", "model120", "token120", "prompt120", "session120"],
    ),
    (
        ("machine120 learning120 model120 token120 prompt120 session120", 10),
        ["machine120", "learning120", "model120", "token120", "prompt120", "session120"],
    ),
    (
        ("machine120 learning120 model120 token120 prompt120 session120", 18),
        ["machine120", "learning120", "model120 token120", "prompt120", "session120"],
    ),
    (
        ("machine120 learning120 model120 token120 prompt120 session120", 28),
        ["machine120 learning120", "model120 token120 prompt120", "session120"],
    ),
    (
        ("learning120 model120 token120 prompt120 session120 library120", 6),
        ["learning120", "model120", "token120", "prompt120", "session120", "library120"],
    ),
    (
        ("learning120 model120 token120 prompt120 session120 library120", 10),
        ["learning120", "model120", "token120", "prompt120", "session120", "library120"],
    ),
    (
        ("learning120 model120 token120 prompt120 session120 library120", 18),
        ["learning120", "model120 token120", "prompt120", "session120", "library120"],
    ),
    (
        ("learning120 model120 token120 prompt120 session120 library120", 28),
        ["learning120 model120", "token120 prompt120", "session120 library120"],
    ),
    (
        ("model120 token120 prompt120 session120 library120 service120", 6),
        ["model120", "token120", "prompt120", "session120", "library120", "service120"],
    ),
    (
        ("model120 token120 prompt120 session120 library120 service120", 10),
        ["model120", "token120", "prompt120", "session120", "library120", "service120"],
    ),
    (
        ("model120 token120 prompt120 session120 library120 service120", 18),
        ["model120 token120", "prompt120", "session120", "library120", "service120"],
    ),
    (
        ("model120 token120 prompt120 session120 library120 service120", 28),
        ["model120 token120 prompt120", "session120 library120", "service120"],
    ),
    (
        ("token120 prompt120 session120 library120 service120 gateway120", 6),
        ["token120", "prompt120", "session120", "library120", "service120", "gateway120"],
    ),
    (
        ("token120 prompt120 session120 library120 service120 gateway120", 10),
        ["token120", "prompt120", "session120", "library120", "service120", "gateway120"],
    ),
    (
        ("token120 prompt120 session120 library120 service120 gateway120", 18),
        ["token120 prompt120", "session120", "library120", "service120", "gateway120"],
    ),
    (
        ("token120 prompt120 session120 library120 service120 gateway120", 28),
        ["token120 prompt120", "session120 library120", "service120 gateway120"],
    ),
    (
        ("prompt120 session120 library120 service120 gateway120 storage120", 6),
        ["prompt120", "session120", "library120", "service120", "gateway120", "storage120"],
    ),
    (
        ("prompt120 session120 library120 service120 gateway120 storage120", 10),
        ["prompt120", "session120", "library120", "service120", "gateway120", "storage120"],
    ),
    (
        ("prompt120 session120 library120 service120 gateway120 storage120", 18),
        ["prompt120", "session120", "library120", "service120", "gateway120", "storage120"],
    ),
    (
        ("prompt120 session120 library120 service120 gateway120 storage120", 28),
        ["prompt120 session120", "library120 service120", "gateway120 storage120"],
    ),
    (
        ("session120 library120 service120 gateway120 storage120 network120", 6),
        ["session120", "library120", "service120", "gateway120", "storage120", "network120"],
    ),
    (
        ("session120 library120 service120 gateway120 storage120 network120", 10),
        ["session120", "library120", "service120", "gateway120", "storage120", "network120"],
    ),
    (
        ("session120 library120 service120 gateway120 storage120 network120", 18),
        ["session120", "library120", "service120", "gateway120", "storage120", "network120"],
    ),
    (
        ("session120 library120 service120 gateway120 storage120 network120", 28),
        ["session120 library120", "service120 gateway120", "storage120 network120"],
    ),
    (
        ("library120 service120 gateway120 storage120 network120 latency120", 6),
        ["library120", "service120", "gateway120", "storage120", "network120", "latency120"],
    ),
    (
        ("library120 service120 gateway120 storage120 network120 latency120", 10),
        ["library120", "service120", "gateway120", "storage120", "network120", "latency120"],
    ),
    (
        ("library120 service120 gateway120 storage120 network120 latency120", 18),
        ["library120", "service120", "gateway120", "storage120", "network120", "latency120"],
    ),
    (
        ("library120 service120 gateway120 storage120 network120 latency120", 28),
        ["library120 service120", "gateway120 storage120", "network120 latency120"],
    ),
    (
        ("service120 gateway120 storage120 network120 latency120 buffer120", 6),
        ["service120", "gateway120", "storage120", "network120", "latency120", "buffer120"],
    ),
    (
        ("service120 gateway120 storage120 network120 latency120 buffer120", 10),
        ["service120", "gateway120", "storage120", "network120", "latency120", "buffer120"],
    ),
    (
        ("service120 gateway120 storage120 network120 latency120 buffer120", 18),
        ["service120", "gateway120", "storage120", "network120", "latency120", "buffer120"],
    ),
    (
        ("service120 gateway120 storage120 network120 latency120 buffer120", 28),
        ["service120 gateway120", "storage120 network120", "latency120 buffer120"],
    ),
    (
        ("gateway120 storage120 network120 latency120 buffer120 queue120", 6),
        ["gateway120", "storage120", "network120", "latency120", "buffer120", "queue120"],
    ),
    (
        ("gateway120 storage120 network120 latency120 buffer120 queue120", 10),
        ["gateway120", "storage120", "network120", "latency120", "buffer120", "queue120"],
    ),
    (
        ("gateway120 storage120 network120 latency120 buffer120 queue120", 18),
        ["gateway120", "storage120", "network120", "latency120", "buffer120 queue120"],
    ),
    (
        ("gateway120 storage120 network120 latency120 buffer120 queue120", 28),
        ["gateway120 storage120", "network120 latency120", "buffer120 queue120"],
    ),
    (
        ("storage120 network120 latency120 buffer120 queue120 worker120", 6),
        ["storage120", "network120", "latency120", "buffer120", "queue120", "worker120"],
    ),
    (
        ("storage120 network120 latency120 buffer120 queue120 worker120", 10),
        ["storage120", "network120", "latency120", "buffer120", "queue120", "worker120"],
    ),
    (
        ("storage120 network120 latency120 buffer120 queue120 worker120", 18),
        ["storage120", "network120", "latency120", "buffer120 queue120", "worker120"],
    ),
    (
        ("storage120 network120 latency120 buffer120 queue120 worker120", 28),
        ["storage120 network120", "latency120 buffer120", "queue120 worker120"],
    ),
    (
        ("network120 latency120 buffer120 queue120 worker120 kernel120", 6),
        ["network120", "latency120", "buffer120", "queue120", "worker120", "kernel120"],
    ),
    (
        ("network120 latency120 buffer120 queue120 worker120 kernel120", 10),
        ["network120", "latency120", "buffer120", "queue120", "worker120", "kernel120"],
    ),
    (
        ("network120 latency120 buffer120 queue120 worker120 kernel120", 18),
        ["network120", "latency120", "buffer120 queue120", "worker120", "kernel120"],
    ),
    (
        ("network120 latency120 buffer120 queue120 worker120 kernel120", 28),
        ["network120 latency120", "buffer120 queue120 worker120", "kernel120"],
    ),
    (
        ("latency120 buffer120 queue120 worker120 kernel120 signal120", 6),
        ["latency120", "buffer120", "queue120", "worker120", "kernel120", "signal120"],
    ),
    (
        ("latency120 buffer120 queue120 worker120 kernel120 signal120", 10),
        ["latency120", "buffer120", "queue120", "worker120", "kernel120", "signal120"],
    ),
    (
        ("latency120 buffer120 queue120 worker120 kernel120 signal120", 18),
        ["latency120", "buffer120 queue120", "worker120", "kernel120", "signal120"],
    ),
    (
        ("latency120 buffer120 queue120 worker120 kernel120 signal120", 28),
        ["latency120 buffer120", "queue120 worker120 kernel120", "signal120"],
    ),
    (
        ("buffer120 queue120 worker120 kernel120 signal120 packet120", 6),
        ["buffer120", "queue120", "worker120", "kernel120", "signal120", "packet120"],
    ),
    (
        ("buffer120 queue120 worker120 kernel120 signal120 packet120", 10),
        ["buffer120", "queue120", "worker120", "kernel120", "signal120", "packet120"],
    ),
    (
        ("buffer120 queue120 worker120 kernel120 signal120 packet120", 18),
        ["buffer120 queue120", "worker120", "kernel120", "signal120", "packet120"],
    ),
    (
        ("buffer120 queue120 worker120 kernel120 signal120 packet120", 28),
        ["buffer120 queue120 worker120", "kernel120 signal120", "packet120"],
    ),
    (
        ("queue120 worker120 kernel120 signal120 packet120 router120", 6),
        ["queue120", "worker120", "kernel120", "signal120", "packet120", "router120"],
    ),
    (
        ("queue120 worker120 kernel120 signal120 packet120 router120", 10),
        ["queue120", "worker120", "kernel120", "signal120", "packet120", "router120"],
    ),
    (
        ("queue120 worker120 kernel120 signal120 packet120 router120", 18),
        ["queue120 worker120", "kernel120", "signal120", "packet120", "router120"],
    ),
    (
        ("queue120 worker120 kernel120 signal120 packet120 router120", 28),
        ["queue120 worker120 kernel120", "signal120 packet120", "router120"],
    ),
    (
        ("worker120 kernel120 signal120 packet120 router120 cluster120", 6),
        ["worker120", "kernel120", "signal120", "packet120", "router120", "cluster120"],
    ),
    (
        ("worker120 kernel120 signal120 packet120 router120 cluster120", 10),
        ["worker120", "kernel120", "signal120", "packet120", "router120", "cluster120"],
    ),
    (
        ("worker120 kernel120 signal120 packet120 router120 cluster120", 18),
        ["worker120", "kernel120", "signal120", "packet120", "router120", "cluster120"],
    ),
    (
        ("worker120 kernel120 signal120 packet120 router120 cluster120", 28),
        ["worker120 kernel120", "signal120 packet120", "router120 cluster120"],
    ),
    (
        ("kernel120 signal120 packet120 router120 cluster120 mirror120", 6),
        ["kernel120", "signal120", "packet120", "router120", "cluster120", "mirror120"],
    ),
    (
        ("kernel120 signal120 packet120 router120 cluster120 mirror120", 10),
        ["kernel120", "signal120", "packet120", "router120", "cluster120", "mirror120"],
    ),
    (
        ("kernel120 signal120 packet120 router120 cluster120 mirror120", 18),
        ["kernel120", "signal120", "packet120", "router120", "cluster120", "mirror120"],
    ),
    (
        ("kernel120 signal120 packet120 router120 cluster120 mirror120", 28),
        ["kernel120 signal120", "packet120 router120", "cluster120 mirror120"],
    ),
    (
        ("signal120 packet120 router120 cluster120 mirror120 filter120", 6),
        ["signal120", "packet120", "router120", "cluster120", "mirror120", "filter120"],
    ),
    (
        ("signal120 packet120 router120 cluster120 mirror120 filter120", 10),
        ["signal120", "packet120", "router120", "cluster120", "mirror120", "filter120"],
    ),
    (
        ("signal120 packet120 router120 cluster120 mirror120 filter120", 18),
        ["signal120", "packet120", "router120", "cluster120", "mirror120", "filter120"],
    ),
    (
        ("signal120 packet120 router120 cluster120 mirror120 filter120", 28),
        ["signal120 packet120", "router120 cluster120", "mirror120 filter120"],
    ),
    (
        ("packet120 router120 cluster120 mirror120 filter120 ranking120", 6),
        ["packet120", "router120", "cluster120", "mirror120", "filter120", "ranking120"],
    ),
    (
        ("packet120 router120 cluster120 mirror120 filter120 ranking120", 10),
        ["packet120", "router120", "cluster120", "mirror120", "filter120", "ranking120"],
    ),
    (
        ("packet120 router120 cluster120 mirror120 filter120 ranking120", 18),
        ["packet120", "router120", "cluster120", "mirror120", "filter120", "ranking120"],
    ),
    (
        ("packet120 router120 cluster120 mirror120 filter120 ranking120", 28),
        ["packet120 router120", "cluster120 mirror120", "filter120 ranking120"],
    ),
    (
        ("router120 cluster120 mirror120 filter120 ranking120 encoding120", 6),
        ["router120", "cluster120", "mirror120", "filter120", "ranking120", "encoding120"],
    ),
    (
        ("router120 cluster120 mirror120 filter120 ranking120 encoding120", 10),
        ["router120", "cluster120", "mirror120", "filter120", "ranking120", "encoding120"],
    ),
    (
        ("router120 cluster120 mirror120 filter120 ranking120 encoding120", 18),
        ["router120", "cluster120", "mirror120", "filter120", "ranking120", "encoding120"],
    ),
    (
        ("router120 cluster120 mirror120 filter120 ranking120 encoding120", 28),
        ["router120 cluster120", "mirror120 filter120", "ranking120 encoding120"],
    ),
    (
        ("cluster120 mirror120 filter120 ranking120 encoding120 mapping120", 6),
        ["cluster120", "mirror120", "filter120", "ranking120", "encoding120", "mapping120"],
    ),
    (
        ("cluster120 mirror120 filter120 ranking120 encoding120 mapping120", 10),
        ["cluster120", "mirror120", "filter120", "ranking120", "encoding120", "mapping120"],
    ),
    (
        ("cluster120 mirror120 filter120 ranking120 encoding120 mapping120", 18),
        ["cluster120", "mirror120", "filter120", "ranking120", "encoding120", "mapping120"],
    ),
    (
        ("cluster120 mirror120 filter120 ranking120 encoding120 mapping120", 28),
        ["cluster120 mirror120", "filter120 ranking120", "encoding120 mapping120"],
    ),
    (
        ("mirror120 filter120 ranking120 encoding120 mapping120 record120", 6),
        ["mirror120", "filter120", "ranking120", "encoding120", "mapping120", "record120"],
    ),
    (
        ("mirror120 filter120 ranking120 encoding120 mapping120 record120", 10),
        ["mirror120", "filter120", "ranking120", "encoding120", "mapping120", "record120"],
    ),
    (
        ("mirror120 filter120 ranking120 encoding120 mapping120 record120", 18),
        ["mirror120", "filter120", "ranking120", "encoding120", "mapping120", "record120"],
    ),
    (
        ("mirror120 filter120 ranking120 encoding120 mapping120 record120", 28),
        ["mirror120 filter120", "ranking120 encoding120", "mapping120 record120"],
    ),
    (
        ("filter120 ranking120 encoding120 mapping120 record120 candle120", 6),
        ["filter120", "ranking120", "encoding120", "mapping120", "record120", "candle120"],
    ),
    (
        ("filter120 ranking120 encoding120 mapping120 record120 candle120", 10),
        ["filter120", "ranking120", "encoding120", "mapping120", "record120", "candle120"],
    ),
    (
        ("filter120 ranking120 encoding120 mapping120 record120 candle120", 18),
        ["filter120", "ranking120", "encoding120", "mapping120", "record120", "candle120"],
    ),
    (
        ("filter120 ranking120 encoding120 mapping120 record120 candle120", 28),
        ["filter120 ranking120", "encoding120 mapping120", "record120 candle120"],
    ),
    (
        ("ranking120 encoding120 mapping120 record120 candle120 thread120", 6),
        ["ranking120", "encoding120", "mapping120", "record120", "candle120", "thread120"],
    ),
    (
        ("ranking120 encoding120 mapping120 record120 candle120 thread120", 10),
        ["ranking120", "encoding120", "mapping120", "record120", "candle120", "thread120"],
    ),
    (
        ("ranking120 encoding120 mapping120 record120 candle120 thread120", 18),
        ["ranking120", "encoding120", "mapping120", "record120", "candle120", "thread120"],
    ),
    (
        ("ranking120 encoding120 mapping120 record120 candle120 thread120", 28),
        ["ranking120 encoding120", "mapping120 record120", "candle120 thread120"],
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
