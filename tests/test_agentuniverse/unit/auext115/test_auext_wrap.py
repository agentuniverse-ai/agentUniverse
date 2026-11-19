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
        ("round 115: the quick brown fox jumps over the lazy dog", 4),
        ["round", "115:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 115: the quick brown fox jumps over the lazy dog", 8),
        ["round", "115: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 115: the quick brown fox jumps over the lazy dog", 12),
        ["round 115:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 115: the quick brown fox jumps over the lazy dog", 16),
        ["round 115: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 115: the quick brown fox jumps over the lazy dog", 24),
        ["round 115: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 115: the quick brown fox jumps over the lazy dog", 32),
        ["round 115: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 115: agentuniverse is a framework for multi agents", 4),
        ["round", "115:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 115: agentuniverse is a framework for multi agents", 8),
        ["round", "115:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 115: agentuniverse is a framework for multi agents", 12),
        ["round 115:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 115: agentuniverse is a framework for multi agents", 16),
        ["round 115:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 115: agentuniverse is a framework for multi agents", 24),
        ["round 115: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 115: agentuniverse is a framework for multi agents", 32),
        ["round 115: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 115: knowledge stored as vectors enables retrieval", 4),
        ["round", "115:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 115: knowledge stored as vectors enables retrieval", 8),
        ["round", "115:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 115: knowledge stored as vectors enables retrieval", 12),
        ["round 115:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 115: knowledge stored as vectors enables retrieval", 16),
        ["round 115:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 115: knowledge stored as vectors enables retrieval", 24),
        ["round 115: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 115: knowledge stored as vectors enables retrieval", 32),
        ["round 115: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 115: the processor reads the record then stops", 4),
        ["round", "115:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 115: the processor reads the record then stops", 8),
        ["round", "115: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 115: the processor reads the record then stops", 12),
        ["round 115:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 115: the processor reads the record then stops", 16),
        ["round 115: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 115: the processor reads the record then stops", 24),
        ["round 115: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 115: the processor reads the record then stops", 32),
        ["round 115: the processor reads", "the record then stops"],
    ),
    (
        ("round 115: a worker pulls the next task from the queue", 4),
        ["round", "115:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 115: a worker pulls the next task from the queue", 8),
        ["round", "115: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 115: a worker pulls the next task from the queue", 12),
        ["round 115: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 115: a worker pulls the next task from the queue", 16),
        ["round 115: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 115: a worker pulls the next task from the queue", 24),
        ["round 115: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 115: a worker pulls the next task from the queue", 32),
        ["round 115: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 115: signals travel through the network layer", 4),
        ["round", "115:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 115: signals travel through the network layer", 8),
        ["round", "115:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 115: signals travel through the network layer", 12),
        ["round 115:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 115: signals travel through the network layer", 16),
        ["round 115:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 115: signals travel through the network layer", 24),
        ["round 115: signals", "travel through the", "network layer"],
    ),
    (
        ("round 115: signals travel through the network layer", 32),
        ["round 115: signals travel", "through the network layer"],
    ),
    (
        ("round 115: the gateway routes each request by policy", 4),
        ["round", "115:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 115: the gateway routes each request by policy", 8),
        ["round", "115: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 115: the gateway routes each request by policy", 12),
        ["round 115:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 115: the gateway routes each request by policy", 16),
        ["round 115: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 115: the gateway routes each request by policy", 24),
        ["round 115: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 115: the gateway routes each request by policy", 32),
        ["round 115: the gateway routes", "each request by policy"],
    ),
    (
        ("round 115: memory grows until the buffer is full", 4),
        ["round", "115:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 115: memory grows until the buffer is full", 8),
        ["round", "115:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 115: memory grows until the buffer is full", 12),
        ["round 115:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 115: memory grows until the buffer is full", 16),
        ["round 115:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 115: memory grows until the buffer is full", 24), ["round 115: memory grows", "until the buffer is full"]),
    (("round 115: memory grows until the buffer is full", 32), ["round 115: memory grows until", "the buffer is full"]),
    (
        ("round 115: the cluster mirrors every packet twice", 4),
        ["round", "115:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 115: the cluster mirrors every packet twice", 8),
        ["round", "115: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 115: the cluster mirrors every packet twice", 12),
        ["round 115:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 115: the cluster mirrors every packet twice", 16),
        ["round 115: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 115: the cluster mirrors every packet twice", 24),
        ["round 115: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 115: the cluster mirrors every packet twice", 32),
        ["round 115: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 115: ranking uses tokens learned from the corpus", 4),
        ["round", "115:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 115: ranking uses tokens learned from the corpus", 8),
        ["round", "115:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 115: ranking uses tokens learned from the corpus", 12),
        ["round 115:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 115: ranking uses tokens learned from the corpus", 16),
        ["round 115:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 115: ranking uses tokens learned from the corpus", 24),
        ["round 115: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 115: ranking uses tokens learned from the corpus", 32),
        ["round 115: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 115: a long session ends when the candle dies", 4),
        ["round", "115:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 115: a long session ends when the candle dies", 8),
        ["round", "115: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 115: a long session ends when the candle dies", 12),
        ["round 115: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 115: a long session ends when the candle dies", 16),
        ["round 115: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 115: a long session ends when the candle dies", 24),
        ["round 115: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 115: a long session ends when the candle dies", 32),
        ["round 115: a long session ends", "when the candle dies"],
    ),
    (
        ("round 115: encode the prompt then map the result", 4),
        ["round", "115:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 115: encode the prompt then map the result", 8),
        ["round", "115:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 115: encode the prompt then map the result", 12),
        ["round 115:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 115: encode the prompt then map the result", 16),
        ["round 115:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 115: encode the prompt then map the result", 24),
        ["round 115: encode the", "prompt then map the", "result"],
    ),
    (("round 115: encode the prompt then map the result", 32), ["round 115: encode the prompt", "then map the result"]),
    (
        ("round 115: the kernel wakes the worker at dawn", 4),
        ["round", "115:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 115: the kernel wakes the worker at dawn", 8),
        ["round", "115: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 115: the kernel wakes the worker at dawn", 12),
        ["round 115:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 115: the kernel wakes the worker at dawn", 16), ["round 115: the", "kernel wakes the", "worker at dawn"]),
    (("round 115: the kernel wakes the worker at dawn", 24), ["round 115: the kernel", "wakes the worker at dawn"]),
    (("round 115: the kernel wakes the worker at dawn", 32), ["round 115: the kernel wakes the", "worker at dawn"]),
    (
        ("round 115: service latency drops after the patch", 4),
        ["round", "115:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 115: service latency drops after the patch", 8),
        ["round", "115:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 115: service latency drops after the patch", 12),
        ["round 115:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 115: service latency drops after the patch", 16),
        ["round 115:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 115: service latency drops after the patch", 24),
        ["round 115: service", "latency drops after the", "patch"],
    ),
    (("round 115: service latency drops after the patch", 32), ["round 115: service latency drops", "after the patch"]),
    (
        ("round 115: the library caches every vector it sees", 4),
        ["round", "115:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 115: the library caches every vector it sees", 8),
        ["round", "115: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 115: the library caches every vector it sees", 12),
        ["round 115:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 115: the library caches every vector it sees", 16),
        ["round 115: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 115: the library caches every vector it sees", 24),
        ["round 115: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 115: the library caches every vector it sees", 32),
        ["round 115: the library caches", "every vector it sees"],
    ),
    (
        ("round 115: agents argue then the debate resolves", 4),
        ["round", "115:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 115: agents argue then the debate resolves", 8),
        ["round", "115:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 115: agents argue then the debate resolves", 12),
        ["round 115:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 115: agents argue then the debate resolves", 16),
        ["round 115:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 115: agents argue then the debate resolves", 24), ["round 115: agents argue", "then the debate resolves"]),
    (("round 115: agents argue then the debate resolves", 32), ["round 115: agents argue then the", "debate resolves"]),
    (
        ("round 115: the filter keeps only strong matches", 4),
        ["round", "115:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 115: the filter keeps only strong matches", 8),
        ["round", "115: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 115: the filter keeps only strong matches", 12),
        ["round 115:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 115: the filter keeps only strong matches", 16),
        ["round 115: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 115: the filter keeps only strong matches", 24),
        ["round 115: the filter", "keeps only strong", "matches"],
    ),
    (("round 115: the filter keeps only strong matches", 32), ["round 115: the filter keeps only", "strong matches"]),
    (
        ("round 115: the model answers with a short reply", 4),
        ["round", "115:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 115: the model answers with a short reply", 8),
        ["round", "115: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 115: the model answers with a short reply", 12),
        ["round 115:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 115: the model answers with a short reply", 16),
        ["round 115: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 115: the model answers with a short reply", 24),
        ["round 115: the model", "answers with a short", "reply"],
    ),
    (("round 115: the model answers with a short reply", 32), ["round 115: the model answers", "with a short reply"]),
    (
        ("round 115: the recorder stores the reasoning trace", 4),
        ["round", "115:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 115: the recorder stores the reasoning trace", 8),
        ["round", "115: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 115: the recorder stores the reasoning trace", 12),
        ["round 115:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 115: the recorder stores the reasoning trace", 16),
        ["round 115: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 115: the recorder stores the reasoning trace", 24),
        ["round 115: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 115: the recorder stores the reasoning trace", 32),
        ["round 115: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 115: the angel watches the processor run", 4),
        ["round", "115:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 115: the angel watches the processor run", 8),
        ["round", "115: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 115: the angel watches the processor run", 12),
        ["round 115:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 115: the angel watches the processor run", 16),
        ["round 115: the", "angel watches", "the processor", "run"],
    ),
    (("round 115: the angel watches the processor run", 24), ["round 115: the angel", "watches the processor", "run"]),
    (("round 115: the angel watches the processor run", 32), ["round 115: the angel watches the", "processor run"]),
    (
        ("round 115: angle of the vector decides the match", 4),
        ["round", "115:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 115: angle of the vector decides the match", 8),
        ["round", "115:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 115: angle of the vector decides the match", 12),
        ["round 115:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 115: angle of the vector decides the match", 16),
        ["round 115: angle", "of the vector", "decides the", "match"],
    ),
    (("round 115: angle of the vector decides the match", 24), ["round 115: angle of the", "vector decides the match"]),
    (("round 115: angle of the vector decides the match", 32), ["round 115: angle of the vector", "decides the match"]),
    (
        ("round 115: the candle burns twice as long at night", 4),
        ["round", "115:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 115: the candle burns twice as long at night", 8),
        ["round", "115: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 115: the candle burns twice as long at night", 12),
        ["round 115:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 115: the candle burns twice as long at night", 16),
        ["round 115: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 115: the candle burns twice as long at night", 24),
        ["round 115: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 115: the candle burns twice as long at night", 32),
        ["round 115: the candle burns", "twice as long at night"],
    ),
    (
        ("round 115: a mirror of the universe in one line", 4),
        ["round", "115:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 115: a mirror of the universe in one line", 8),
        ["round", "115: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 115: a mirror of the universe in one line", 12),
        ["round 115: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 115: a mirror of the universe in one line", 16),
        ["round 115: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 115: a mirror of the universe in one line", 24), ["round 115: a mirror of", "the universe in one line"]),
    (("round 115: a mirror of the universe in one line", 32), ["round 115: a mirror of the", "universe in one line"]),
    (
        ("round 115: the queue drains before the storm", 4),
        ["round", "115:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 115: the queue drains before the storm", 8),
        ["round", "115: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 115: the queue drains before the storm", 12),
        ["round 115:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 115: the queue drains before the storm", 16), ["round 115: the", "queue drains", "before the storm"]),
    (("round 115: the queue drains before the storm", 24), ["round 115: the queue", "drains before the storm"]),
    (("round 115: the queue drains before the storm", 32), ["round 115: the queue drains", "before the storm"]),
    (
        ("kitten115 sitting115 agent115 angle115 universe115 memory115", 6),
        ["kitten115", "sitting115", "agent115", "angle115", "universe115", "memory115"],
    ),
    (
        ("kitten115 sitting115 agent115 angle115 universe115 memory115", 10),
        ["kitten115", "sitting115", "agent115", "angle115", "universe115", "memory115"],
    ),
    (
        ("kitten115 sitting115 agent115 angle115 universe115 memory115", 18),
        ["kitten115", "sitting115", "agent115 angle115", "universe115", "memory115"],
    ),
    (
        ("kitten115 sitting115 agent115 angle115 universe115 memory115", 28),
        ["kitten115 sitting115", "agent115 angle115", "universe115 memory115"],
    ),
    (
        ("sitting115 agent115 angle115 universe115 memory115 stream115", 6),
        ["sitting115", "agent115", "angle115", "universe115", "memory115", "stream115"],
    ),
    (
        ("sitting115 agent115 angle115 universe115 memory115 stream115", 10),
        ["sitting115", "agent115", "angle115", "universe115", "memory115", "stream115"],
    ),
    (
        ("sitting115 agent115 angle115 universe115 memory115 stream115", 18),
        ["sitting115", "agent115 angle115", "universe115", "memory115", "stream115"],
    ),
    (
        ("sitting115 agent115 angle115 universe115 memory115 stream115", 28),
        ["sitting115 agent115 angle115", "universe115 memory115", "stream115"],
    ),
    (
        ("agent115 angle115 universe115 memory115 stream115 context115", 6),
        ["agent115", "angle115", "universe115", "memory115", "stream115", "context115"],
    ),
    (
        ("agent115 angle115 universe115 memory115 stream115 context115", 10),
        ["agent115", "angle115", "universe115", "memory115", "stream115", "context115"],
    ),
    (
        ("agent115 angle115 universe115 memory115 stream115 context115", 18),
        ["agent115 angle115", "universe115", "memory115", "stream115", "context115"],
    ),
    (
        ("agent115 angle115 universe115 memory115 stream115 context115", 28),
        ["agent115 angle115", "universe115 memory115", "stream115 context115"],
    ),
    (
        ("angle115 universe115 memory115 stream115 context115 knowledge115", 6),
        ["angle115", "universe115", "memory115", "stream115", "context115", "knowledge115"],
    ),
    (
        ("angle115 universe115 memory115 stream115 context115 knowledge115", 10),
        ["angle115", "universe115", "memory115", "stream115", "context115", "knowledge115"],
    ),
    (
        ("angle115 universe115 memory115 stream115 context115 knowledge115", 18),
        ["angle115", "universe115", "memory115", "stream115", "context115", "knowledge115"],
    ),
    (
        ("angle115 universe115 memory115 stream115 context115 knowledge115", 28),
        ["angle115 universe115", "memory115 stream115", "context115 knowledge115"],
    ),
    (
        ("universe115 memory115 stream115 context115 knowledge115 vector115", 6),
        ["universe115", "memory115", "stream115", "context115", "knowledge115", "vector115"],
    ),
    (
        ("universe115 memory115 stream115 context115 knowledge115 vector115", 10),
        ["universe115", "memory115", "stream115", "context115", "knowledge115", "vector115"],
    ),
    (
        ("universe115 memory115 stream115 context115 knowledge115 vector115", 18),
        ["universe115", "memory115", "stream115", "context115", "knowledge115", "vector115"],
    ),
    (
        ("universe115 memory115 stream115 context115 knowledge115 vector115", 28),
        ["universe115 memory115", "stream115 context115", "knowledge115 vector115"],
    ),
    (
        ("memory115 stream115 context115 knowledge115 vector115 processor115", 6),
        ["memory115", "stream115", "context115", "knowledge115", "vector115", "processor115"],
    ),
    (
        ("memory115 stream115 context115 knowledge115 vector115 processor115", 10),
        ["memory115", "stream115", "context115", "knowledge115", "vector115", "processor115"],
    ),
    (
        ("memory115 stream115 context115 knowledge115 vector115 processor115", 18),
        ["memory115", "stream115", "context115", "knowledge115", "vector115", "processor115"],
    ),
    (
        ("memory115 stream115 context115 knowledge115 vector115 processor115", 28),
        ["memory115 stream115", "context115 knowledge115", "vector115 processor115"],
    ),
    (
        ("stream115 context115 knowledge115 vector115 processor115 reasoning115", 6),
        ["stream115", "context115", "knowledge115", "vector115", "processor115", "reasoning115"],
    ),
    (
        ("stream115 context115 knowledge115 vector115 processor115 reasoning115", 10),
        ["stream115", "context115", "knowledge115", "vector115", "processor115", "reasoning115"],
    ),
    (
        ("stream115 context115 knowledge115 vector115 processor115 reasoning115", 18),
        ["stream115", "context115", "knowledge115", "vector115", "processor115", "reasoning115"],
    ),
    (
        ("stream115 context115 knowledge115 vector115 processor115 reasoning115", 28),
        ["stream115 context115", "knowledge115 vector115", "processor115 reasoning115"],
    ),
    (
        ("context115 knowledge115 vector115 processor115 reasoning115 machine115", 6),
        ["context115", "knowledge115", "vector115", "processor115", "reasoning115", "machine115"],
    ),
    (
        ("context115 knowledge115 vector115 processor115 reasoning115 machine115", 10),
        ["context115", "knowledge115", "vector115", "processor115", "reasoning115", "machine115"],
    ),
    (
        ("context115 knowledge115 vector115 processor115 reasoning115 machine115", 18),
        ["context115", "knowledge115", "vector115", "processor115", "reasoning115", "machine115"],
    ),
    (
        ("context115 knowledge115 vector115 processor115 reasoning115 machine115", 28),
        ["context115 knowledge115", "vector115 processor115", "reasoning115 machine115"],
    ),
    (
        ("knowledge115 vector115 processor115 reasoning115 machine115 learning115", 6),
        ["knowledge115", "vector115", "processor115", "reasoning115", "machine115", "learning115"],
    ),
    (
        ("knowledge115 vector115 processor115 reasoning115 machine115 learning115", 10),
        ["knowledge115", "vector115", "processor115", "reasoning115", "machine115", "learning115"],
    ),
    (
        ("knowledge115 vector115 processor115 reasoning115 machine115 learning115", 18),
        ["knowledge115", "vector115", "processor115", "reasoning115", "machine115", "learning115"],
    ),
    (
        ("knowledge115 vector115 processor115 reasoning115 machine115 learning115", 28),
        ["knowledge115 vector115", "processor115 reasoning115", "machine115 learning115"],
    ),
    (
        ("vector115 processor115 reasoning115 machine115 learning115 model115", 6),
        ["vector115", "processor115", "reasoning115", "machine115", "learning115", "model115"],
    ),
    (
        ("vector115 processor115 reasoning115 machine115 learning115 model115", 10),
        ["vector115", "processor115", "reasoning115", "machine115", "learning115", "model115"],
    ),
    (
        ("vector115 processor115 reasoning115 machine115 learning115 model115", 18),
        ["vector115", "processor115", "reasoning115", "machine115", "learning115", "model115"],
    ),
    (
        ("vector115 processor115 reasoning115 machine115 learning115 model115", 28),
        ["vector115 processor115", "reasoning115 machine115", "learning115 model115"],
    ),
    (
        ("processor115 reasoning115 machine115 learning115 model115 token115", 6),
        ["processor115", "reasoning115", "machine115", "learning115", "model115", "token115"],
    ),
    (
        ("processor115 reasoning115 machine115 learning115 model115 token115", 10),
        ["processor115", "reasoning115", "machine115", "learning115", "model115", "token115"],
    ),
    (
        ("processor115 reasoning115 machine115 learning115 model115 token115", 18),
        ["processor115", "reasoning115", "machine115", "learning115", "model115 token115"],
    ),
    (
        ("processor115 reasoning115 machine115 learning115 model115 token115", 28),
        ["processor115 reasoning115", "machine115 learning115", "model115 token115"],
    ),
    (
        ("reasoning115 machine115 learning115 model115 token115 prompt115", 6),
        ["reasoning115", "machine115", "learning115", "model115", "token115", "prompt115"],
    ),
    (
        ("reasoning115 machine115 learning115 model115 token115 prompt115", 10),
        ["reasoning115", "machine115", "learning115", "model115", "token115", "prompt115"],
    ),
    (
        ("reasoning115 machine115 learning115 model115 token115 prompt115", 18),
        ["reasoning115", "machine115", "learning115", "model115 token115", "prompt115"],
    ),
    (
        ("reasoning115 machine115 learning115 model115 token115 prompt115", 28),
        ["reasoning115 machine115", "learning115 model115", "token115 prompt115"],
    ),
    (
        ("machine115 learning115 model115 token115 prompt115 session115", 6),
        ["machine115", "learning115", "model115", "token115", "prompt115", "session115"],
    ),
    (
        ("machine115 learning115 model115 token115 prompt115 session115", 10),
        ["machine115", "learning115", "model115", "token115", "prompt115", "session115"],
    ),
    (
        ("machine115 learning115 model115 token115 prompt115 session115", 18),
        ["machine115", "learning115", "model115 token115", "prompt115", "session115"],
    ),
    (
        ("machine115 learning115 model115 token115 prompt115 session115", 28),
        ["machine115 learning115", "model115 token115 prompt115", "session115"],
    ),
    (
        ("learning115 model115 token115 prompt115 session115 library115", 6),
        ["learning115", "model115", "token115", "prompt115", "session115", "library115"],
    ),
    (
        ("learning115 model115 token115 prompt115 session115 library115", 10),
        ["learning115", "model115", "token115", "prompt115", "session115", "library115"],
    ),
    (
        ("learning115 model115 token115 prompt115 session115 library115", 18),
        ["learning115", "model115 token115", "prompt115", "session115", "library115"],
    ),
    (
        ("learning115 model115 token115 prompt115 session115 library115", 28),
        ["learning115 model115", "token115 prompt115", "session115 library115"],
    ),
    (
        ("model115 token115 prompt115 session115 library115 service115", 6),
        ["model115", "token115", "prompt115", "session115", "library115", "service115"],
    ),
    (
        ("model115 token115 prompt115 session115 library115 service115", 10),
        ["model115", "token115", "prompt115", "session115", "library115", "service115"],
    ),
    (
        ("model115 token115 prompt115 session115 library115 service115", 18),
        ["model115 token115", "prompt115", "session115", "library115", "service115"],
    ),
    (
        ("model115 token115 prompt115 session115 library115 service115", 28),
        ["model115 token115 prompt115", "session115 library115", "service115"],
    ),
    (
        ("token115 prompt115 session115 library115 service115 gateway115", 6),
        ["token115", "prompt115", "session115", "library115", "service115", "gateway115"],
    ),
    (
        ("token115 prompt115 session115 library115 service115 gateway115", 10),
        ["token115", "prompt115", "session115", "library115", "service115", "gateway115"],
    ),
    (
        ("token115 prompt115 session115 library115 service115 gateway115", 18),
        ["token115 prompt115", "session115", "library115", "service115", "gateway115"],
    ),
    (
        ("token115 prompt115 session115 library115 service115 gateway115", 28),
        ["token115 prompt115", "session115 library115", "service115 gateway115"],
    ),
    (
        ("prompt115 session115 library115 service115 gateway115 storage115", 6),
        ["prompt115", "session115", "library115", "service115", "gateway115", "storage115"],
    ),
    (
        ("prompt115 session115 library115 service115 gateway115 storage115", 10),
        ["prompt115", "session115", "library115", "service115", "gateway115", "storage115"],
    ),
    (
        ("prompt115 session115 library115 service115 gateway115 storage115", 18),
        ["prompt115", "session115", "library115", "service115", "gateway115", "storage115"],
    ),
    (
        ("prompt115 session115 library115 service115 gateway115 storage115", 28),
        ["prompt115 session115", "library115 service115", "gateway115 storage115"],
    ),
    (
        ("session115 library115 service115 gateway115 storage115 network115", 6),
        ["session115", "library115", "service115", "gateway115", "storage115", "network115"],
    ),
    (
        ("session115 library115 service115 gateway115 storage115 network115", 10),
        ["session115", "library115", "service115", "gateway115", "storage115", "network115"],
    ),
    (
        ("session115 library115 service115 gateway115 storage115 network115", 18),
        ["session115", "library115", "service115", "gateway115", "storage115", "network115"],
    ),
    (
        ("session115 library115 service115 gateway115 storage115 network115", 28),
        ["session115 library115", "service115 gateway115", "storage115 network115"],
    ),
    (
        ("library115 service115 gateway115 storage115 network115 latency115", 6),
        ["library115", "service115", "gateway115", "storage115", "network115", "latency115"],
    ),
    (
        ("library115 service115 gateway115 storage115 network115 latency115", 10),
        ["library115", "service115", "gateway115", "storage115", "network115", "latency115"],
    ),
    (
        ("library115 service115 gateway115 storage115 network115 latency115", 18),
        ["library115", "service115", "gateway115", "storage115", "network115", "latency115"],
    ),
    (
        ("library115 service115 gateway115 storage115 network115 latency115", 28),
        ["library115 service115", "gateway115 storage115", "network115 latency115"],
    ),
    (
        ("service115 gateway115 storage115 network115 latency115 buffer115", 6),
        ["service115", "gateway115", "storage115", "network115", "latency115", "buffer115"],
    ),
    (
        ("service115 gateway115 storage115 network115 latency115 buffer115", 10),
        ["service115", "gateway115", "storage115", "network115", "latency115", "buffer115"],
    ),
    (
        ("service115 gateway115 storage115 network115 latency115 buffer115", 18),
        ["service115", "gateway115", "storage115", "network115", "latency115", "buffer115"],
    ),
    (
        ("service115 gateway115 storage115 network115 latency115 buffer115", 28),
        ["service115 gateway115", "storage115 network115", "latency115 buffer115"],
    ),
    (
        ("gateway115 storage115 network115 latency115 buffer115 queue115", 6),
        ["gateway115", "storage115", "network115", "latency115", "buffer115", "queue115"],
    ),
    (
        ("gateway115 storage115 network115 latency115 buffer115 queue115", 10),
        ["gateway115", "storage115", "network115", "latency115", "buffer115", "queue115"],
    ),
    (
        ("gateway115 storage115 network115 latency115 buffer115 queue115", 18),
        ["gateway115", "storage115", "network115", "latency115", "buffer115 queue115"],
    ),
    (
        ("gateway115 storage115 network115 latency115 buffer115 queue115", 28),
        ["gateway115 storage115", "network115 latency115", "buffer115 queue115"],
    ),
    (
        ("storage115 network115 latency115 buffer115 queue115 worker115", 6),
        ["storage115", "network115", "latency115", "buffer115", "queue115", "worker115"],
    ),
    (
        ("storage115 network115 latency115 buffer115 queue115 worker115", 10),
        ["storage115", "network115", "latency115", "buffer115", "queue115", "worker115"],
    ),
    (
        ("storage115 network115 latency115 buffer115 queue115 worker115", 18),
        ["storage115", "network115", "latency115", "buffer115 queue115", "worker115"],
    ),
    (
        ("storage115 network115 latency115 buffer115 queue115 worker115", 28),
        ["storage115 network115", "latency115 buffer115", "queue115 worker115"],
    ),
    (
        ("network115 latency115 buffer115 queue115 worker115 kernel115", 6),
        ["network115", "latency115", "buffer115", "queue115", "worker115", "kernel115"],
    ),
    (
        ("network115 latency115 buffer115 queue115 worker115 kernel115", 10),
        ["network115", "latency115", "buffer115", "queue115", "worker115", "kernel115"],
    ),
    (
        ("network115 latency115 buffer115 queue115 worker115 kernel115", 18),
        ["network115", "latency115", "buffer115 queue115", "worker115", "kernel115"],
    ),
    (
        ("network115 latency115 buffer115 queue115 worker115 kernel115", 28),
        ["network115 latency115", "buffer115 queue115 worker115", "kernel115"],
    ),
    (
        ("latency115 buffer115 queue115 worker115 kernel115 signal115", 6),
        ["latency115", "buffer115", "queue115", "worker115", "kernel115", "signal115"],
    ),
    (
        ("latency115 buffer115 queue115 worker115 kernel115 signal115", 10),
        ["latency115", "buffer115", "queue115", "worker115", "kernel115", "signal115"],
    ),
    (
        ("latency115 buffer115 queue115 worker115 kernel115 signal115", 18),
        ["latency115", "buffer115 queue115", "worker115", "kernel115", "signal115"],
    ),
    (
        ("latency115 buffer115 queue115 worker115 kernel115 signal115", 28),
        ["latency115 buffer115", "queue115 worker115 kernel115", "signal115"],
    ),
    (
        ("buffer115 queue115 worker115 kernel115 signal115 packet115", 6),
        ["buffer115", "queue115", "worker115", "kernel115", "signal115", "packet115"],
    ),
    (
        ("buffer115 queue115 worker115 kernel115 signal115 packet115", 10),
        ["buffer115", "queue115", "worker115", "kernel115", "signal115", "packet115"],
    ),
    (
        ("buffer115 queue115 worker115 kernel115 signal115 packet115", 18),
        ["buffer115 queue115", "worker115", "kernel115", "signal115", "packet115"],
    ),
    (
        ("buffer115 queue115 worker115 kernel115 signal115 packet115", 28),
        ["buffer115 queue115 worker115", "kernel115 signal115", "packet115"],
    ),
    (
        ("queue115 worker115 kernel115 signal115 packet115 router115", 6),
        ["queue115", "worker115", "kernel115", "signal115", "packet115", "router115"],
    ),
    (
        ("queue115 worker115 kernel115 signal115 packet115 router115", 10),
        ["queue115", "worker115", "kernel115", "signal115", "packet115", "router115"],
    ),
    (
        ("queue115 worker115 kernel115 signal115 packet115 router115", 18),
        ["queue115 worker115", "kernel115", "signal115", "packet115", "router115"],
    ),
    (
        ("queue115 worker115 kernel115 signal115 packet115 router115", 28),
        ["queue115 worker115 kernel115", "signal115 packet115", "router115"],
    ),
    (
        ("worker115 kernel115 signal115 packet115 router115 cluster115", 6),
        ["worker115", "kernel115", "signal115", "packet115", "router115", "cluster115"],
    ),
    (
        ("worker115 kernel115 signal115 packet115 router115 cluster115", 10),
        ["worker115", "kernel115", "signal115", "packet115", "router115", "cluster115"],
    ),
    (
        ("worker115 kernel115 signal115 packet115 router115 cluster115", 18),
        ["worker115", "kernel115", "signal115", "packet115", "router115", "cluster115"],
    ),
    (
        ("worker115 kernel115 signal115 packet115 router115 cluster115", 28),
        ["worker115 kernel115", "signal115 packet115", "router115 cluster115"],
    ),
    (
        ("kernel115 signal115 packet115 router115 cluster115 mirror115", 6),
        ["kernel115", "signal115", "packet115", "router115", "cluster115", "mirror115"],
    ),
    (
        ("kernel115 signal115 packet115 router115 cluster115 mirror115", 10),
        ["kernel115", "signal115", "packet115", "router115", "cluster115", "mirror115"],
    ),
    (
        ("kernel115 signal115 packet115 router115 cluster115 mirror115", 18),
        ["kernel115", "signal115", "packet115", "router115", "cluster115", "mirror115"],
    ),
    (
        ("kernel115 signal115 packet115 router115 cluster115 mirror115", 28),
        ["kernel115 signal115", "packet115 router115", "cluster115 mirror115"],
    ),
    (
        ("signal115 packet115 router115 cluster115 mirror115 filter115", 6),
        ["signal115", "packet115", "router115", "cluster115", "mirror115", "filter115"],
    ),
    (
        ("signal115 packet115 router115 cluster115 mirror115 filter115", 10),
        ["signal115", "packet115", "router115", "cluster115", "mirror115", "filter115"],
    ),
    (
        ("signal115 packet115 router115 cluster115 mirror115 filter115", 18),
        ["signal115", "packet115", "router115", "cluster115", "mirror115", "filter115"],
    ),
    (
        ("signal115 packet115 router115 cluster115 mirror115 filter115", 28),
        ["signal115 packet115", "router115 cluster115", "mirror115 filter115"],
    ),
    (
        ("packet115 router115 cluster115 mirror115 filter115 ranking115", 6),
        ["packet115", "router115", "cluster115", "mirror115", "filter115", "ranking115"],
    ),
    (
        ("packet115 router115 cluster115 mirror115 filter115 ranking115", 10),
        ["packet115", "router115", "cluster115", "mirror115", "filter115", "ranking115"],
    ),
    (
        ("packet115 router115 cluster115 mirror115 filter115 ranking115", 18),
        ["packet115", "router115", "cluster115", "mirror115", "filter115", "ranking115"],
    ),
    (
        ("packet115 router115 cluster115 mirror115 filter115 ranking115", 28),
        ["packet115 router115", "cluster115 mirror115", "filter115 ranking115"],
    ),
    (
        ("router115 cluster115 mirror115 filter115 ranking115 encoding115", 6),
        ["router115", "cluster115", "mirror115", "filter115", "ranking115", "encoding115"],
    ),
    (
        ("router115 cluster115 mirror115 filter115 ranking115 encoding115", 10),
        ["router115", "cluster115", "mirror115", "filter115", "ranking115", "encoding115"],
    ),
    (
        ("router115 cluster115 mirror115 filter115 ranking115 encoding115", 18),
        ["router115", "cluster115", "mirror115", "filter115", "ranking115", "encoding115"],
    ),
    (
        ("router115 cluster115 mirror115 filter115 ranking115 encoding115", 28),
        ["router115 cluster115", "mirror115 filter115", "ranking115 encoding115"],
    ),
    (
        ("cluster115 mirror115 filter115 ranking115 encoding115 mapping115", 6),
        ["cluster115", "mirror115", "filter115", "ranking115", "encoding115", "mapping115"],
    ),
    (
        ("cluster115 mirror115 filter115 ranking115 encoding115 mapping115", 10),
        ["cluster115", "mirror115", "filter115", "ranking115", "encoding115", "mapping115"],
    ),
    (
        ("cluster115 mirror115 filter115 ranking115 encoding115 mapping115", 18),
        ["cluster115", "mirror115", "filter115", "ranking115", "encoding115", "mapping115"],
    ),
    (
        ("cluster115 mirror115 filter115 ranking115 encoding115 mapping115", 28),
        ["cluster115 mirror115", "filter115 ranking115", "encoding115 mapping115"],
    ),
    (
        ("mirror115 filter115 ranking115 encoding115 mapping115 record115", 6),
        ["mirror115", "filter115", "ranking115", "encoding115", "mapping115", "record115"],
    ),
    (
        ("mirror115 filter115 ranking115 encoding115 mapping115 record115", 10),
        ["mirror115", "filter115", "ranking115", "encoding115", "mapping115", "record115"],
    ),
    (
        ("mirror115 filter115 ranking115 encoding115 mapping115 record115", 18),
        ["mirror115", "filter115", "ranking115", "encoding115", "mapping115", "record115"],
    ),
    (
        ("mirror115 filter115 ranking115 encoding115 mapping115 record115", 28),
        ["mirror115 filter115", "ranking115 encoding115", "mapping115 record115"],
    ),
    (
        ("filter115 ranking115 encoding115 mapping115 record115 candle115", 6),
        ["filter115", "ranking115", "encoding115", "mapping115", "record115", "candle115"],
    ),
    (
        ("filter115 ranking115 encoding115 mapping115 record115 candle115", 10),
        ["filter115", "ranking115", "encoding115", "mapping115", "record115", "candle115"],
    ),
    (
        ("filter115 ranking115 encoding115 mapping115 record115 candle115", 18),
        ["filter115", "ranking115", "encoding115", "mapping115", "record115", "candle115"],
    ),
    (
        ("filter115 ranking115 encoding115 mapping115 record115 candle115", 28),
        ["filter115 ranking115", "encoding115 mapping115", "record115 candle115"],
    ),
    (
        ("ranking115 encoding115 mapping115 record115 candle115 thread115", 6),
        ["ranking115", "encoding115", "mapping115", "record115", "candle115", "thread115"],
    ),
    (
        ("ranking115 encoding115 mapping115 record115 candle115 thread115", 10),
        ["ranking115", "encoding115", "mapping115", "record115", "candle115", "thread115"],
    ),
    (
        ("ranking115 encoding115 mapping115 record115 candle115 thread115", 18),
        ["ranking115", "encoding115", "mapping115", "record115", "candle115", "thread115"],
    ),
    (
        ("ranking115 encoding115 mapping115 record115 candle115 thread115", 28),
        ["ranking115 encoding115", "mapping115 record115", "candle115 thread115"],
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
