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
        ("round 89: the quick brown fox jumps over the lazy dog", 4),
        ["round", "89:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 89: the quick brown fox jumps over the lazy dog", 8),
        ["round", "89: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 89: the quick brown fox jumps over the lazy dog", 12),
        ["round 89:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 89: the quick brown fox jumps over the lazy dog", 16),
        ["round 89: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 89: the quick brown fox jumps over the lazy dog", 24),
        ["round 89: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 89: the quick brown fox jumps over the lazy dog", 32),
        ["round 89: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 89: agentuniverse is a framework for multi agents", 4),
        ["round", "89:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 89: agentuniverse is a framework for multi agents", 8),
        ["round", "89:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 89: agentuniverse is a framework for multi agents", 12),
        ["round 89:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 89: agentuniverse is a framework for multi agents", 16),
        ["round 89:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 89: agentuniverse is a framework for multi agents", 24),
        ["round 89: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 89: agentuniverse is a framework for multi agents", 32),
        ["round 89: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 89: knowledge stored as vectors enables retrieval", 4),
        ["round", "89:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 89: knowledge stored as vectors enables retrieval", 8),
        ["round", "89:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 89: knowledge stored as vectors enables retrieval", 12),
        ["round 89:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 89: knowledge stored as vectors enables retrieval", 16),
        ["round 89:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 89: knowledge stored as vectors enables retrieval", 24),
        ["round 89: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 89: knowledge stored as vectors enables retrieval", 32),
        ["round 89: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 89: the processor reads the record then stops", 4),
        ["round", "89:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 89: the processor reads the record then stops", 8),
        ["round", "89: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 89: the processor reads the record then stops", 12),
        ["round 89:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 89: the processor reads the record then stops", 16),
        ["round 89: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 89: the processor reads the record then stops", 24),
        ["round 89: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 89: the processor reads the record then stops", 32),
        ["round 89: the processor reads", "the record then stops"],
    ),
    (
        ("round 89: a worker pulls the next task from the queue", 4),
        ["round", "89:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 89: a worker pulls the next task from the queue", 8),
        ["round", "89: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 89: a worker pulls the next task from the queue", 12),
        ["round 89: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 89: a worker pulls the next task from the queue", 16),
        ["round 89: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 89: a worker pulls the next task from the queue", 24),
        ["round 89: a worker pulls", "the next task from the", "queue"],
    ),
    (
        ("round 89: a worker pulls the next task from the queue", 32),
        ["round 89: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 89: signals travel through the network layer", 4),
        ["round", "89:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 89: signals travel through the network layer", 8),
        ["round", "89:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 89: signals travel through the network layer", 12),
        ["round 89:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 89: signals travel through the network layer", 16),
        ["round 89:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 89: signals travel through the network layer", 24),
        ["round 89: signals travel", "through the network", "layer"],
    ),
    (
        ("round 89: signals travel through the network layer", 32),
        ["round 89: signals travel through", "the network layer"],
    ),
    (
        ("round 89: the gateway routes each request by policy", 4),
        ["round", "89:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 89: the gateway routes each request by policy", 8),
        ["round", "89: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 89: the gateway routes each request by policy", 12),
        ["round 89:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 89: the gateway routes each request by policy", 16),
        ["round 89: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 89: the gateway routes each request by policy", 24),
        ["round 89: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 89: the gateway routes each request by policy", 32),
        ["round 89: the gateway routes", "each request by policy"],
    ),
    (
        ("round 89: memory grows until the buffer is full", 4),
        ["round", "89:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 89: memory grows until the buffer is full", 8),
        ["round", "89:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 89: memory grows until the buffer is full", 12),
        ["round 89:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 89: memory grows until the buffer is full", 16),
        ["round 89: memory", "grows until the", "buffer is full"],
    ),
    (("round 89: memory grows until the buffer is full", 24), ["round 89: memory grows", "until the buffer is full"]),
    (("round 89: memory grows until the buffer is full", 32), ["round 89: memory grows until the", "buffer is full"]),
    (
        ("round 89: the cluster mirrors every packet twice", 4),
        ["round", "89:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 89: the cluster mirrors every packet twice", 8),
        ["round", "89: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 89: the cluster mirrors every packet twice", 12),
        ["round 89:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 89: the cluster mirrors every packet twice", 16),
        ["round 89: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 89: the cluster mirrors every packet twice", 24),
        ["round 89: the cluster", "mirrors every packet", "twice"],
    ),
    (("round 89: the cluster mirrors every packet twice", 32), ["round 89: the cluster mirrors", "every packet twice"]),
    (
        ("round 89: ranking uses tokens learned from the corpus", 4),
        ["round", "89:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 89: ranking uses tokens learned from the corpus", 8),
        ["round", "89:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 89: ranking uses tokens learned from the corpus", 12),
        ["round 89:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 89: ranking uses tokens learned from the corpus", 16),
        ["round 89:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 89: ranking uses tokens learned from the corpus", 24),
        ["round 89: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 89: ranking uses tokens learned from the corpus", 32),
        ["round 89: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 89: a long session ends when the candle dies", 4),
        ["round", "89:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 89: a long session ends when the candle dies", 8),
        ["round", "89: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 89: a long session ends when the candle dies", 12),
        ["round 89: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 89: a long session ends when the candle dies", 16),
        ["round 89: a long", "session ends", "when the candle", "dies"],
    ),
    (
        ("round 89: a long session ends when the candle dies", 24),
        ["round 89: a long session", "ends when the candle", "dies"],
    ),
    (
        ("round 89: a long session ends when the candle dies", 32),
        ["round 89: a long session ends", "when the candle dies"],
    ),
    (
        ("round 89: encode the prompt then map the result", 4),
        ["round", "89:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 89: encode the prompt then map the result", 8),
        ["round", "89:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 89: encode the prompt then map the result", 12),
        ["round 89:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 89: encode the prompt then map the result", 16),
        ["round 89: encode", "the prompt then", "map the result"],
    ),
    (
        ("round 89: encode the prompt then map the result", 24),
        ["round 89: encode the", "prompt then map the", "result"],
    ),
    (("round 89: encode the prompt then map the result", 32), ["round 89: encode the prompt then", "map the result"]),
    (
        ("round 89: the kernel wakes the worker at dawn", 4),
        ["round", "89:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 89: the kernel wakes the worker at dawn", 8),
        ["round", "89: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 89: the kernel wakes the worker at dawn", 12),
        ["round 89:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 89: the kernel wakes the worker at dawn", 16), ["round 89: the", "kernel wakes the", "worker at dawn"]),
    (("round 89: the kernel wakes the worker at dawn", 24), ["round 89: the kernel", "wakes the worker at dawn"]),
    (("round 89: the kernel wakes the worker at dawn", 32), ["round 89: the kernel wakes the", "worker at dawn"]),
    (
        ("round 89: service latency drops after the patch", 4),
        ["round", "89:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 89: service latency drops after the patch", 8),
        ["round", "89:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 89: service latency drops after the patch", 12),
        ["round 89:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 89: service latency drops after the patch", 16),
        ["round 89:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 89: service latency drops after the patch", 24),
        ["round 89: service", "latency drops after the", "patch"],
    ),
    (("round 89: service latency drops after the patch", 32), ["round 89: service latency drops", "after the patch"]),
    (
        ("round 89: the library caches every vector it sees", 4),
        ["round", "89:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 89: the library caches every vector it sees", 8),
        ["round", "89: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 89: the library caches every vector it sees", 12),
        ["round 89:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 89: the library caches every vector it sees", 16),
        ["round 89: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 89: the library caches every vector it sees", 24),
        ["round 89: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 89: the library caches every vector it sees", 32),
        ["round 89: the library caches", "every vector it sees"],
    ),
    (
        ("round 89: agents argue then the debate resolves", 4),
        ["round", "89:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 89: agents argue then the debate resolves", 8),
        ["round", "89:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 89: agents argue then the debate resolves", 12),
        ["round 89:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 89: agents argue then the debate resolves", 16),
        ["round 89: agents", "argue then the", "debate resolves"],
    ),
    (("round 89: agents argue then the debate resolves", 24), ["round 89: agents argue", "then the debate resolves"]),
    (("round 89: agents argue then the debate resolves", 32), ["round 89: agents argue then the", "debate resolves"]),
    (
        ("round 89: the filter keeps only strong matches", 4),
        ["round", "89:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 89: the filter keeps only strong matches", 8),
        ["round", "89: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 89: the filter keeps only strong matches", 12),
        ["round 89:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 89: the filter keeps only strong matches", 16),
        ["round 89: the", "filter keeps", "only strong", "matches"],
    ),
    (("round 89: the filter keeps only strong matches", 24), ["round 89: the filter", "keeps only strong", "matches"]),
    (("round 89: the filter keeps only strong matches", 32), ["round 89: the filter keeps only", "strong matches"]),
    (
        ("round 89: the model answers with a short reply", 4),
        ["round", "89:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 89: the model answers with a short reply", 8),
        ["round", "89: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 89: the model answers with a short reply", 12),
        ["round 89:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 89: the model answers with a short reply", 16),
        ["round 89: the", "model answers", "with a short", "reply"],
    ),
    (("round 89: the model answers with a short reply", 24), ["round 89: the model", "answers with a short", "reply"]),
    (("round 89: the model answers with a short reply", 32), ["round 89: the model answers with", "a short reply"]),
    (
        ("round 89: the recorder stores the reasoning trace", 4),
        ["round", "89:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 89: the recorder stores the reasoning trace", 8),
        ["round", "89: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 89: the recorder stores the reasoning trace", 12),
        ["round 89:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 89: the recorder stores the reasoning trace", 16),
        ["round 89: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 89: the recorder stores the reasoning trace", 24),
        ["round 89: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 89: the recorder stores the reasoning trace", 32),
        ["round 89: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 89: the angel watches the processor run", 4),
        ["round", "89:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 89: the angel watches the processor run", 8),
        ["round", "89: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 89: the angel watches the processor run", 12),
        ["round 89:", "the angel", "watches the", "processor", "run"],
    ),
    (("round 89: the angel watches the processor run", 16), ["round 89: the", "angel watches", "the processor", "run"]),
    (("round 89: the angel watches the processor run", 24), ["round 89: the angel", "watches the processor", "run"]),
    (("round 89: the angel watches the processor run", 32), ["round 89: the angel watches the", "processor run"]),
    (
        ("round 89: angle of the vector decides the match", 4),
        ["round", "89:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 89: angle of the vector decides the match", 8),
        ["round", "89:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 89: angle of the vector decides the match", 12),
        ["round 89:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 89: angle of the vector decides the match", 16),
        ["round 89: angle", "of the vector", "decides the", "match"],
    ),
    (("round 89: angle of the vector decides the match", 24), ["round 89: angle of the", "vector decides the match"]),
    (("round 89: angle of the vector decides the match", 32), ["round 89: angle of the vector", "decides the match"]),
    (
        ("round 89: the candle burns twice as long at night", 4),
        ["round", "89:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 89: the candle burns twice as long at night", 8),
        ["round", "89: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 89: the candle burns twice as long at night", 12),
        ["round 89:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 89: the candle burns twice as long at night", 16),
        ["round 89: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 89: the candle burns twice as long at night", 24),
        ["round 89: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 89: the candle burns twice as long at night", 32),
        ["round 89: the candle burns twice", "as long at night"],
    ),
    (
        ("round 89: a mirror of the universe in one line", 4),
        ["round", "89:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 89: a mirror of the universe in one line", 8),
        ["round", "89: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 89: a mirror of the universe in one line", 12),
        ["round 89: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 89: a mirror of the universe in one line", 16),
        ["round 89: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 89: a mirror of the universe in one line", 24), ["round 89: a mirror of", "the universe in one line"]),
    (("round 89: a mirror of the universe in one line", 32), ["round 89: a mirror of the", "universe in one line"]),
    (
        ("round 89: the queue drains before the storm", 4),
        ["round", "89:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 89: the queue drains before the storm", 8),
        ["round", "89: the", "queue", "drains", "before", "the", "storm"],
    ),
    (("round 89: the queue drains before the storm", 12), ["round 89:", "the queue", "drains", "before the", "storm"]),
    (("round 89: the queue drains before the storm", 16), ["round 89: the", "queue drains", "before the storm"]),
    (("round 89: the queue drains before the storm", 24), ["round 89: the queue", "drains before the storm"]),
    (("round 89: the queue drains before the storm", 32), ["round 89: the queue drains", "before the storm"]),
    (
        ("kitten89 sitting89 agent89 angle89 universe89 memory89", 6),
        ["kitten89", "sitting89", "agent89", "angle89", "universe89", "memory89"],
    ),
    (
        ("kitten89 sitting89 agent89 angle89 universe89 memory89", 10),
        ["kitten89", "sitting89", "agent89", "angle89", "universe89", "memory89"],
    ),
    (
        ("kitten89 sitting89 agent89 angle89 universe89 memory89", 18),
        ["kitten89 sitting89", "agent89 angle89", "universe89", "memory89"],
    ),
    (
        ("kitten89 sitting89 agent89 angle89 universe89 memory89", 28),
        ["kitten89 sitting89 agent89", "angle89 universe89 memory89"],
    ),
    (
        ("sitting89 agent89 angle89 universe89 memory89 stream89", 6),
        ["sitting89", "agent89", "angle89", "universe89", "memory89", "stream89"],
    ),
    (
        ("sitting89 agent89 angle89 universe89 memory89 stream89", 10),
        ["sitting89", "agent89", "angle89", "universe89", "memory89", "stream89"],
    ),
    (
        ("sitting89 agent89 angle89 universe89 memory89 stream89", 18),
        ["sitting89 agent89", "angle89 universe89", "memory89 stream89"],
    ),
    (
        ("sitting89 agent89 angle89 universe89 memory89 stream89", 28),
        ["sitting89 agent89 angle89", "universe89 memory89 stream89"],
    ),
    (
        ("agent89 angle89 universe89 memory89 stream89 context89", 6),
        ["agent89", "angle89", "universe89", "memory89", "stream89", "context89"],
    ),
    (
        ("agent89 angle89 universe89 memory89 stream89 context89", 10),
        ["agent89", "angle89", "universe89", "memory89", "stream89", "context89"],
    ),
    (
        ("agent89 angle89 universe89 memory89 stream89 context89", 18),
        ["agent89 angle89", "universe89", "memory89 stream89", "context89"],
    ),
    (
        ("agent89 angle89 universe89 memory89 stream89 context89", 28),
        ["agent89 angle89 universe89", "memory89 stream89 context89"],
    ),
    (
        ("angle89 universe89 memory89 stream89 context89 knowledge89", 6),
        ["angle89", "universe89", "memory89", "stream89", "context89", "knowledge89"],
    ),
    (
        ("angle89 universe89 memory89 stream89 context89 knowledge89", 10),
        ["angle89", "universe89", "memory89", "stream89", "context89", "knowledge89"],
    ),
    (
        ("angle89 universe89 memory89 stream89 context89 knowledge89", 18),
        ["angle89 universe89", "memory89 stream89", "context89", "knowledge89"],
    ),
    (
        ("angle89 universe89 memory89 stream89 context89 knowledge89", 28),
        ["angle89 universe89 memory89", "stream89 context89", "knowledge89"],
    ),
    (
        ("universe89 memory89 stream89 context89 knowledge89 vector89", 6),
        ["universe89", "memory89", "stream89", "context89", "knowledge89", "vector89"],
    ),
    (
        ("universe89 memory89 stream89 context89 knowledge89 vector89", 10),
        ["universe89", "memory89", "stream89", "context89", "knowledge89", "vector89"],
    ),
    (
        ("universe89 memory89 stream89 context89 knowledge89 vector89", 18),
        ["universe89", "memory89 stream89", "context89", "knowledge89", "vector89"],
    ),
    (
        ("universe89 memory89 stream89 context89 knowledge89 vector89", 28),
        ["universe89 memory89 stream89", "context89 knowledge89", "vector89"],
    ),
    (
        ("memory89 stream89 context89 knowledge89 vector89 processor89", 6),
        ["memory89", "stream89", "context89", "knowledge89", "vector89", "processor89"],
    ),
    (
        ("memory89 stream89 context89 knowledge89 vector89 processor89", 10),
        ["memory89", "stream89", "context89", "knowledge89", "vector89", "processor89"],
    ),
    (
        ("memory89 stream89 context89 knowledge89 vector89 processor89", 18),
        ["memory89 stream89", "context89", "knowledge89", "vector89", "processor89"],
    ),
    (
        ("memory89 stream89 context89 knowledge89 vector89 processor89", 28),
        ["memory89 stream89 context89", "knowledge89 vector89", "processor89"],
    ),
    (
        ("stream89 context89 knowledge89 vector89 processor89 reasoning89", 6),
        ["stream89", "context89", "knowledge89", "vector89", "processor89", "reasoning89"],
    ),
    (
        ("stream89 context89 knowledge89 vector89 processor89 reasoning89", 10),
        ["stream89", "context89", "knowledge89", "vector89", "processor89", "reasoning89"],
    ),
    (
        ("stream89 context89 knowledge89 vector89 processor89 reasoning89", 18),
        ["stream89 context89", "knowledge89", "vector89", "processor89", "reasoning89"],
    ),
    (
        ("stream89 context89 knowledge89 vector89 processor89 reasoning89", 28),
        ["stream89 context89", "knowledge89 vector89", "processor89 reasoning89"],
    ),
    (
        ("context89 knowledge89 vector89 processor89 reasoning89 machine89", 6),
        ["context89", "knowledge89", "vector89", "processor89", "reasoning89", "machine89"],
    ),
    (
        ("context89 knowledge89 vector89 processor89 reasoning89 machine89", 10),
        ["context89", "knowledge89", "vector89", "processor89", "reasoning89", "machine89"],
    ),
    (
        ("context89 knowledge89 vector89 processor89 reasoning89 machine89", 18),
        ["context89", "knowledge89", "vector89", "processor89", "reasoning89", "machine89"],
    ),
    (
        ("context89 knowledge89 vector89 processor89 reasoning89 machine89", 28),
        ["context89 knowledge89", "vector89 processor89", "reasoning89 machine89"],
    ),
    (
        ("knowledge89 vector89 processor89 reasoning89 machine89 learning89", 6),
        ["knowledge89", "vector89", "processor89", "reasoning89", "machine89", "learning89"],
    ),
    (
        ("knowledge89 vector89 processor89 reasoning89 machine89 learning89", 10),
        ["knowledge89", "vector89", "processor89", "reasoning89", "machine89", "learning89"],
    ),
    (
        ("knowledge89 vector89 processor89 reasoning89 machine89 learning89", 18),
        ["knowledge89", "vector89", "processor89", "reasoning89", "machine89", "learning89"],
    ),
    (
        ("knowledge89 vector89 processor89 reasoning89 machine89 learning89", 28),
        ["knowledge89 vector89", "processor89 reasoning89", "machine89 learning89"],
    ),
    (
        ("vector89 processor89 reasoning89 machine89 learning89 model89", 6),
        ["vector89", "processor89", "reasoning89", "machine89", "learning89", "model89"],
    ),
    (
        ("vector89 processor89 reasoning89 machine89 learning89 model89", 10),
        ["vector89", "processor89", "reasoning89", "machine89", "learning89", "model89"],
    ),
    (
        ("vector89 processor89 reasoning89 machine89 learning89 model89", 18),
        ["vector89", "processor89", "reasoning89", "machine89", "learning89 model89"],
    ),
    (
        ("vector89 processor89 reasoning89 machine89 learning89 model89", 28),
        ["vector89 processor89", "reasoning89 machine89", "learning89 model89"],
    ),
    (
        ("processor89 reasoning89 machine89 learning89 model89 token89", 6),
        ["processor89", "reasoning89", "machine89", "learning89", "model89", "token89"],
    ),
    (
        ("processor89 reasoning89 machine89 learning89 model89 token89", 10),
        ["processor89", "reasoning89", "machine89", "learning89", "model89", "token89"],
    ),
    (
        ("processor89 reasoning89 machine89 learning89 model89 token89", 18),
        ["processor89", "reasoning89", "machine89", "learning89 model89", "token89"],
    ),
    (
        ("processor89 reasoning89 machine89 learning89 model89 token89", 28),
        ["processor89 reasoning89", "machine89 learning89 model89", "token89"],
    ),
    (
        ("reasoning89 machine89 learning89 model89 token89 prompt89", 6),
        ["reasoning89", "machine89", "learning89", "model89", "token89", "prompt89"],
    ),
    (
        ("reasoning89 machine89 learning89 model89 token89 prompt89", 10),
        ["reasoning89", "machine89", "learning89", "model89", "token89", "prompt89"],
    ),
    (
        ("reasoning89 machine89 learning89 model89 token89 prompt89", 18),
        ["reasoning89", "machine89", "learning89 model89", "token89 prompt89"],
    ),
    (
        ("reasoning89 machine89 learning89 model89 token89 prompt89", 28),
        ["reasoning89 machine89", "learning89 model89 token89", "prompt89"],
    ),
    (
        ("machine89 learning89 model89 token89 prompt89 session89", 6),
        ["machine89", "learning89", "model89", "token89", "prompt89", "session89"],
    ),
    (
        ("machine89 learning89 model89 token89 prompt89 session89", 10),
        ["machine89", "learning89", "model89", "token89", "prompt89", "session89"],
    ),
    (
        ("machine89 learning89 model89 token89 prompt89 session89", 18),
        ["machine89", "learning89 model89", "token89 prompt89", "session89"],
    ),
    (
        ("machine89 learning89 model89 token89 prompt89 session89", 28),
        ["machine89 learning89 model89", "token89 prompt89 session89"],
    ),
    (
        ("learning89 model89 token89 prompt89 session89 library89", 6),
        ["learning89", "model89", "token89", "prompt89", "session89", "library89"],
    ),
    (
        ("learning89 model89 token89 prompt89 session89 library89", 10),
        ["learning89", "model89", "token89", "prompt89", "session89", "library89"],
    ),
    (
        ("learning89 model89 token89 prompt89 session89 library89", 18),
        ["learning89 model89", "token89 prompt89", "session89", "library89"],
    ),
    (
        ("learning89 model89 token89 prompt89 session89 library89", 28),
        ["learning89 model89 token89", "prompt89 session89 library89"],
    ),
    (
        ("model89 token89 prompt89 session89 library89 service89", 6),
        ["model89", "token89", "prompt89", "session89", "library89", "service89"],
    ),
    (
        ("model89 token89 prompt89 session89 library89 service89", 10),
        ["model89", "token89", "prompt89", "session89", "library89", "service89"],
    ),
    (
        ("model89 token89 prompt89 session89 library89 service89", 18),
        ["model89 token89", "prompt89 session89", "library89", "service89"],
    ),
    (
        ("model89 token89 prompt89 session89 library89 service89", 28),
        ["model89 token89 prompt89", "session89 library89", "service89"],
    ),
    (
        ("token89 prompt89 session89 library89 service89 gateway89", 6),
        ["token89", "prompt89", "session89", "library89", "service89", "gateway89"],
    ),
    (
        ("token89 prompt89 session89 library89 service89 gateway89", 10),
        ["token89", "prompt89", "session89", "library89", "service89", "gateway89"],
    ),
    (
        ("token89 prompt89 session89 library89 service89 gateway89", 18),
        ["token89 prompt89", "session89", "library89", "service89", "gateway89"],
    ),
    (
        ("token89 prompt89 session89 library89 service89 gateway89", 28),
        ["token89 prompt89 session89", "library89 service89", "gateway89"],
    ),
    (
        ("prompt89 session89 library89 service89 gateway89 storage89", 6),
        ["prompt89", "session89", "library89", "service89", "gateway89", "storage89"],
    ),
    (
        ("prompt89 session89 library89 service89 gateway89 storage89", 10),
        ["prompt89", "session89", "library89", "service89", "gateway89", "storage89"],
    ),
    (
        ("prompt89 session89 library89 service89 gateway89 storage89", 18),
        ["prompt89 session89", "library89", "service89", "gateway89", "storage89"],
    ),
    (
        ("prompt89 session89 library89 service89 gateway89 storage89", 28),
        ["prompt89 session89 library89", "service89 gateway89", "storage89"],
    ),
    (
        ("session89 library89 service89 gateway89 storage89 network89", 6),
        ["session89", "library89", "service89", "gateway89", "storage89", "network89"],
    ),
    (
        ("session89 library89 service89 gateway89 storage89 network89", 10),
        ["session89", "library89", "service89", "gateway89", "storage89", "network89"],
    ),
    (
        ("session89 library89 service89 gateway89 storage89 network89", 18),
        ["session89", "library89", "service89", "gateway89", "storage89", "network89"],
    ),
    (
        ("session89 library89 service89 gateway89 storage89 network89", 28),
        ["session89 library89", "service89 gateway89", "storage89 network89"],
    ),
    (
        ("library89 service89 gateway89 storage89 network89 latency89", 6),
        ["library89", "service89", "gateway89", "storage89", "network89", "latency89"],
    ),
    (
        ("library89 service89 gateway89 storage89 network89 latency89", 10),
        ["library89", "service89", "gateway89", "storage89", "network89", "latency89"],
    ),
    (
        ("library89 service89 gateway89 storage89 network89 latency89", 18),
        ["library89", "service89", "gateway89", "storage89", "network89", "latency89"],
    ),
    (
        ("library89 service89 gateway89 storage89 network89 latency89", 28),
        ["library89 service89", "gateway89 storage89", "network89 latency89"],
    ),
    (
        ("service89 gateway89 storage89 network89 latency89 buffer89", 6),
        ["service89", "gateway89", "storage89", "network89", "latency89", "buffer89"],
    ),
    (
        ("service89 gateway89 storage89 network89 latency89 buffer89", 10),
        ["service89", "gateway89", "storage89", "network89", "latency89", "buffer89"],
    ),
    (
        ("service89 gateway89 storage89 network89 latency89 buffer89", 18),
        ["service89", "gateway89", "storage89", "network89", "latency89 buffer89"],
    ),
    (
        ("service89 gateway89 storage89 network89 latency89 buffer89", 28),
        ["service89 gateway89", "storage89 network89", "latency89 buffer89"],
    ),
    (
        ("gateway89 storage89 network89 latency89 buffer89 queue89", 6),
        ["gateway89", "storage89", "network89", "latency89", "buffer89", "queue89"],
    ),
    (
        ("gateway89 storage89 network89 latency89 buffer89 queue89", 10),
        ["gateway89", "storage89", "network89", "latency89", "buffer89", "queue89"],
    ),
    (
        ("gateway89 storage89 network89 latency89 buffer89 queue89", 18),
        ["gateway89", "storage89", "network89", "latency89 buffer89", "queue89"],
    ),
    (
        ("gateway89 storage89 network89 latency89 buffer89 queue89", 28),
        ["gateway89 storage89", "network89 latency89 buffer89", "queue89"],
    ),
    (
        ("storage89 network89 latency89 buffer89 queue89 worker89", 6),
        ["storage89", "network89", "latency89", "buffer89", "queue89", "worker89"],
    ),
    (
        ("storage89 network89 latency89 buffer89 queue89 worker89", 10),
        ["storage89", "network89", "latency89", "buffer89", "queue89", "worker89"],
    ),
    (
        ("storage89 network89 latency89 buffer89 queue89 worker89", 18),
        ["storage89", "network89", "latency89 buffer89", "queue89 worker89"],
    ),
    (
        ("storage89 network89 latency89 buffer89 queue89 worker89", 28),
        ["storage89 network89", "latency89 buffer89 queue89", "worker89"],
    ),
    (
        ("network89 latency89 buffer89 queue89 worker89 kernel89", 6),
        ["network89", "latency89", "buffer89", "queue89", "worker89", "kernel89"],
    ),
    (
        ("network89 latency89 buffer89 queue89 worker89 kernel89", 10),
        ["network89", "latency89", "buffer89", "queue89", "worker89", "kernel89"],
    ),
    (
        ("network89 latency89 buffer89 queue89 worker89 kernel89", 18),
        ["network89", "latency89 buffer89", "queue89 worker89", "kernel89"],
    ),
    (
        ("network89 latency89 buffer89 queue89 worker89 kernel89", 28),
        ["network89 latency89 buffer89", "queue89 worker89 kernel89"],
    ),
    (
        ("latency89 buffer89 queue89 worker89 kernel89 signal89", 6),
        ["latency89", "buffer89", "queue89", "worker89", "kernel89", "signal89"],
    ),
    (
        ("latency89 buffer89 queue89 worker89 kernel89 signal89", 10),
        ["latency89", "buffer89", "queue89", "worker89", "kernel89", "signal89"],
    ),
    (
        ("latency89 buffer89 queue89 worker89 kernel89 signal89", 18),
        ["latency89 buffer89", "queue89 worker89", "kernel89 signal89"],
    ),
    (
        ("latency89 buffer89 queue89 worker89 kernel89 signal89", 28),
        ["latency89 buffer89 queue89", "worker89 kernel89 signal89"],
    ),
    (
        ("buffer89 queue89 worker89 kernel89 signal89 packet89", 6),
        ["buffer89", "queue89", "worker89", "kernel89", "signal89", "packet89"],
    ),
    (
        ("buffer89 queue89 worker89 kernel89 signal89 packet89", 10),
        ["buffer89", "queue89", "worker89", "kernel89", "signal89", "packet89"],
    ),
    (
        ("buffer89 queue89 worker89 kernel89 signal89 packet89", 18),
        ["buffer89 queue89", "worker89 kernel89", "signal89 packet89"],
    ),
    (
        ("buffer89 queue89 worker89 kernel89 signal89 packet89", 28),
        ["buffer89 queue89 worker89", "kernel89 signal89 packet89"],
    ),
    (
        ("queue89 worker89 kernel89 signal89 packet89 router89", 6),
        ["queue89", "worker89", "kernel89", "signal89", "packet89", "router89"],
    ),
    (
        ("queue89 worker89 kernel89 signal89 packet89 router89", 10),
        ["queue89", "worker89", "kernel89", "signal89", "packet89", "router89"],
    ),
    (
        ("queue89 worker89 kernel89 signal89 packet89 router89", 18),
        ["queue89 worker89", "kernel89 signal89", "packet89 router89"],
    ),
    (
        ("queue89 worker89 kernel89 signal89 packet89 router89", 28),
        ["queue89 worker89 kernel89", "signal89 packet89 router89"],
    ),
    (
        ("worker89 kernel89 signal89 packet89 router89 cluster89", 6),
        ["worker89", "kernel89", "signal89", "packet89", "router89", "cluster89"],
    ),
    (
        ("worker89 kernel89 signal89 packet89 router89 cluster89", 10),
        ["worker89", "kernel89", "signal89", "packet89", "router89", "cluster89"],
    ),
    (
        ("worker89 kernel89 signal89 packet89 router89 cluster89", 18),
        ["worker89 kernel89", "signal89 packet89", "router89 cluster89"],
    ),
    (
        ("worker89 kernel89 signal89 packet89 router89 cluster89", 28),
        ["worker89 kernel89 signal89", "packet89 router89 cluster89"],
    ),
    (
        ("kernel89 signal89 packet89 router89 cluster89 mirror89", 6),
        ["kernel89", "signal89", "packet89", "router89", "cluster89", "mirror89"],
    ),
    (
        ("kernel89 signal89 packet89 router89 cluster89 mirror89", 10),
        ["kernel89", "signal89", "packet89", "router89", "cluster89", "mirror89"],
    ),
    (
        ("kernel89 signal89 packet89 router89 cluster89 mirror89", 18),
        ["kernel89 signal89", "packet89 router89", "cluster89 mirror89"],
    ),
    (
        ("kernel89 signal89 packet89 router89 cluster89 mirror89", 28),
        ["kernel89 signal89 packet89", "router89 cluster89 mirror89"],
    ),
    (
        ("signal89 packet89 router89 cluster89 mirror89 filter89", 6),
        ["signal89", "packet89", "router89", "cluster89", "mirror89", "filter89"],
    ),
    (
        ("signal89 packet89 router89 cluster89 mirror89 filter89", 10),
        ["signal89", "packet89", "router89", "cluster89", "mirror89", "filter89"],
    ),
    (
        ("signal89 packet89 router89 cluster89 mirror89 filter89", 18),
        ["signal89 packet89", "router89 cluster89", "mirror89 filter89"],
    ),
    (
        ("signal89 packet89 router89 cluster89 mirror89 filter89", 28),
        ["signal89 packet89 router89", "cluster89 mirror89 filter89"],
    ),
    (
        ("packet89 router89 cluster89 mirror89 filter89 ranking89", 6),
        ["packet89", "router89", "cluster89", "mirror89", "filter89", "ranking89"],
    ),
    (
        ("packet89 router89 cluster89 mirror89 filter89 ranking89", 10),
        ["packet89", "router89", "cluster89", "mirror89", "filter89", "ranking89"],
    ),
    (
        ("packet89 router89 cluster89 mirror89 filter89 ranking89", 18),
        ["packet89 router89", "cluster89 mirror89", "filter89 ranking89"],
    ),
    (
        ("packet89 router89 cluster89 mirror89 filter89 ranking89", 28),
        ["packet89 router89 cluster89", "mirror89 filter89 ranking89"],
    ),
    (
        ("router89 cluster89 mirror89 filter89 ranking89 encoding89", 6),
        ["router89", "cluster89", "mirror89", "filter89", "ranking89", "encoding89"],
    ),
    (
        ("router89 cluster89 mirror89 filter89 ranking89 encoding89", 10),
        ["router89", "cluster89", "mirror89", "filter89", "ranking89", "encoding89"],
    ),
    (
        ("router89 cluster89 mirror89 filter89 ranking89 encoding89", 18),
        ["router89 cluster89", "mirror89 filter89", "ranking89", "encoding89"],
    ),
    (
        ("router89 cluster89 mirror89 filter89 ranking89 encoding89", 28),
        ["router89 cluster89 mirror89", "filter89 ranking89", "encoding89"],
    ),
    (
        ("cluster89 mirror89 filter89 ranking89 encoding89 mapping89", 6),
        ["cluster89", "mirror89", "filter89", "ranking89", "encoding89", "mapping89"],
    ),
    (
        ("cluster89 mirror89 filter89 ranking89 encoding89 mapping89", 10),
        ["cluster89", "mirror89", "filter89", "ranking89", "encoding89", "mapping89"],
    ),
    (
        ("cluster89 mirror89 filter89 ranking89 encoding89 mapping89", 18),
        ["cluster89 mirror89", "filter89 ranking89", "encoding89", "mapping89"],
    ),
    (
        ("cluster89 mirror89 filter89 ranking89 encoding89 mapping89", 28),
        ["cluster89 mirror89 filter89", "ranking89 encoding89", "mapping89"],
    ),
    (
        ("mirror89 filter89 ranking89 encoding89 mapping89 record89", 6),
        ["mirror89", "filter89", "ranking89", "encoding89", "mapping89", "record89"],
    ),
    (
        ("mirror89 filter89 ranking89 encoding89 mapping89 record89", 10),
        ["mirror89", "filter89", "ranking89", "encoding89", "mapping89", "record89"],
    ),
    (
        ("mirror89 filter89 ranking89 encoding89 mapping89 record89", 18),
        ["mirror89 filter89", "ranking89", "encoding89", "mapping89 record89"],
    ),
    (
        ("mirror89 filter89 ranking89 encoding89 mapping89 record89", 28),
        ["mirror89 filter89 ranking89", "encoding89 mapping89", "record89"],
    ),
    (
        ("filter89 ranking89 encoding89 mapping89 record89 candle89", 6),
        ["filter89", "ranking89", "encoding89", "mapping89", "record89", "candle89"],
    ),
    (
        ("filter89 ranking89 encoding89 mapping89 record89 candle89", 10),
        ["filter89", "ranking89", "encoding89", "mapping89", "record89", "candle89"],
    ),
    (
        ("filter89 ranking89 encoding89 mapping89 record89 candle89", 18),
        ["filter89 ranking89", "encoding89", "mapping89 record89", "candle89"],
    ),
    (
        ("filter89 ranking89 encoding89 mapping89 record89 candle89", 28),
        ["filter89 ranking89", "encoding89 mapping89", "record89 candle89"],
    ),
    (
        ("ranking89 encoding89 mapping89 record89 candle89 thread89", 6),
        ["ranking89", "encoding89", "mapping89", "record89", "candle89", "thread89"],
    ),
    (
        ("ranking89 encoding89 mapping89 record89 candle89 thread89", 10),
        ["ranking89", "encoding89", "mapping89", "record89", "candle89", "thread89"],
    ),
    (
        ("ranking89 encoding89 mapping89 record89 candle89 thread89", 18),
        ["ranking89", "encoding89", "mapping89 record89", "candle89 thread89"],
    ),
    (
        ("ranking89 encoding89 mapping89 record89 candle89 thread89", 28),
        ["ranking89 encoding89", "mapping89 record89 candle89", "thread89"],
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
