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
        ("round 188: the quick brown fox jumps over the lazy dog", 4),
        ["round", "188:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 188: the quick brown fox jumps over the lazy dog", 8),
        ["round", "188: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 188: the quick brown fox jumps over the lazy dog", 12),
        ["round 188:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 188: the quick brown fox jumps over the lazy dog", 16),
        ["round 188: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 188: the quick brown fox jumps over the lazy dog", 24),
        ["round 188: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 188: the quick brown fox jumps over the lazy dog", 32),
        ["round 188: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 188: agentuniverse is a framework for multi agents", 4),
        ["round", "188:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 188: agentuniverse is a framework for multi agents", 8),
        ["round", "188:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 188: agentuniverse is a framework for multi agents", 12),
        ["round 188:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 188: agentuniverse is a framework for multi agents", 16),
        ["round 188:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 188: agentuniverse is a framework for multi agents", 24),
        ["round 188: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 188: agentuniverse is a framework for multi agents", 32),
        ["round 188: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 188: knowledge stored as vectors enables retrieval", 4),
        ["round", "188:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 188: knowledge stored as vectors enables retrieval", 8),
        ["round", "188:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 188: knowledge stored as vectors enables retrieval", 12),
        ["round 188:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 188: knowledge stored as vectors enables retrieval", 16),
        ["round 188:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 188: knowledge stored as vectors enables retrieval", 24),
        ["round 188: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 188: knowledge stored as vectors enables retrieval", 32),
        ["round 188: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 188: the processor reads the record then stops", 4),
        ["round", "188:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 188: the processor reads the record then stops", 8),
        ["round", "188: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 188: the processor reads the record then stops", 12),
        ["round 188:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 188: the processor reads the record then stops", 16),
        ["round 188: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 188: the processor reads the record then stops", 24),
        ["round 188: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 188: the processor reads the record then stops", 32),
        ["round 188: the processor reads", "the record then stops"],
    ),
    (
        ("round 188: a worker pulls the next task from the queue", 4),
        ["round", "188:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 188: a worker pulls the next task from the queue", 8),
        ["round", "188: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 188: a worker pulls the next task from the queue", 12),
        ["round 188: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 188: a worker pulls the next task from the queue", 16),
        ["round 188: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 188: a worker pulls the next task from the queue", 24),
        ["round 188: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 188: a worker pulls the next task from the queue", 32),
        ["round 188: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 188: signals travel through the network layer", 4),
        ["round", "188:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 188: signals travel through the network layer", 8),
        ["round", "188:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 188: signals travel through the network layer", 12),
        ["round 188:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 188: signals travel through the network layer", 16),
        ["round 188:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 188: signals travel through the network layer", 24),
        ["round 188: signals", "travel through the", "network layer"],
    ),
    (
        ("round 188: signals travel through the network layer", 32),
        ["round 188: signals travel", "through the network layer"],
    ),
    (
        ("round 188: the gateway routes each request by policy", 4),
        ["round", "188:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 188: the gateway routes each request by policy", 8),
        ["round", "188: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 188: the gateway routes each request by policy", 12),
        ["round 188:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 188: the gateway routes each request by policy", 16),
        ["round 188: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 188: the gateway routes each request by policy", 24),
        ["round 188: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 188: the gateway routes each request by policy", 32),
        ["round 188: the gateway routes", "each request by policy"],
    ),
    (
        ("round 188: memory grows until the buffer is full", 4),
        ["round", "188:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 188: memory grows until the buffer is full", 8),
        ["round", "188:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 188: memory grows until the buffer is full", 12),
        ["round 188:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 188: memory grows until the buffer is full", 16),
        ["round 188:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 188: memory grows until the buffer is full", 24), ["round 188: memory grows", "until the buffer is full"]),
    (("round 188: memory grows until the buffer is full", 32), ["round 188: memory grows until", "the buffer is full"]),
    (
        ("round 188: the cluster mirrors every packet twice", 4),
        ["round", "188:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 188: the cluster mirrors every packet twice", 8),
        ["round", "188: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 188: the cluster mirrors every packet twice", 12),
        ["round 188:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 188: the cluster mirrors every packet twice", 16),
        ["round 188: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 188: the cluster mirrors every packet twice", 24),
        ["round 188: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 188: the cluster mirrors every packet twice", 32),
        ["round 188: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 188: ranking uses tokens learned from the corpus", 4),
        ["round", "188:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 188: ranking uses tokens learned from the corpus", 8),
        ["round", "188:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 188: ranking uses tokens learned from the corpus", 12),
        ["round 188:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 188: ranking uses tokens learned from the corpus", 16),
        ["round 188:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 188: ranking uses tokens learned from the corpus", 24),
        ["round 188: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 188: ranking uses tokens learned from the corpus", 32),
        ["round 188: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 188: a long session ends when the candle dies", 4),
        ["round", "188:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 188: a long session ends when the candle dies", 8),
        ["round", "188: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 188: a long session ends when the candle dies", 12),
        ["round 188: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 188: a long session ends when the candle dies", 16),
        ["round 188: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 188: a long session ends when the candle dies", 24),
        ["round 188: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 188: a long session ends when the candle dies", 32),
        ["round 188: a long session ends", "when the candle dies"],
    ),
    (
        ("round 188: encode the prompt then map the result", 4),
        ["round", "188:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 188: encode the prompt then map the result", 8),
        ["round", "188:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 188: encode the prompt then map the result", 12),
        ["round 188:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 188: encode the prompt then map the result", 16),
        ["round 188:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 188: encode the prompt then map the result", 24),
        ["round 188: encode the", "prompt then map the", "result"],
    ),
    (("round 188: encode the prompt then map the result", 32), ["round 188: encode the prompt", "then map the result"]),
    (
        ("round 188: the kernel wakes the worker at dawn", 4),
        ["round", "188:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 188: the kernel wakes the worker at dawn", 8),
        ["round", "188: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 188: the kernel wakes the worker at dawn", 12),
        ["round 188:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 188: the kernel wakes the worker at dawn", 16), ["round 188: the", "kernel wakes the", "worker at dawn"]),
    (("round 188: the kernel wakes the worker at dawn", 24), ["round 188: the kernel", "wakes the worker at dawn"]),
    (("round 188: the kernel wakes the worker at dawn", 32), ["round 188: the kernel wakes the", "worker at dawn"]),
    (
        ("round 188: service latency drops after the patch", 4),
        ["round", "188:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 188: service latency drops after the patch", 8),
        ["round", "188:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 188: service latency drops after the patch", 12),
        ["round 188:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 188: service latency drops after the patch", 16),
        ["round 188:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 188: service latency drops after the patch", 24),
        ["round 188: service", "latency drops after the", "patch"],
    ),
    (("round 188: service latency drops after the patch", 32), ["round 188: service latency drops", "after the patch"]),
    (
        ("round 188: the library caches every vector it sees", 4),
        ["round", "188:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 188: the library caches every vector it sees", 8),
        ["round", "188: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 188: the library caches every vector it sees", 12),
        ["round 188:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 188: the library caches every vector it sees", 16),
        ["round 188: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 188: the library caches every vector it sees", 24),
        ["round 188: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 188: the library caches every vector it sees", 32),
        ["round 188: the library caches", "every vector it sees"],
    ),
    (
        ("round 188: agents argue then the debate resolves", 4),
        ["round", "188:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 188: agents argue then the debate resolves", 8),
        ["round", "188:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 188: agents argue then the debate resolves", 12),
        ["round 188:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 188: agents argue then the debate resolves", 16),
        ["round 188:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 188: agents argue then the debate resolves", 24), ["round 188: agents argue", "then the debate resolves"]),
    (("round 188: agents argue then the debate resolves", 32), ["round 188: agents argue then the", "debate resolves"]),
    (
        ("round 188: the filter keeps only strong matches", 4),
        ["round", "188:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 188: the filter keeps only strong matches", 8),
        ["round", "188: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 188: the filter keeps only strong matches", 12),
        ["round 188:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 188: the filter keeps only strong matches", 16),
        ["round 188: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 188: the filter keeps only strong matches", 24),
        ["round 188: the filter", "keeps only strong", "matches"],
    ),
    (("round 188: the filter keeps only strong matches", 32), ["round 188: the filter keeps only", "strong matches"]),
    (
        ("round 188: the model answers with a short reply", 4),
        ["round", "188:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 188: the model answers with a short reply", 8),
        ["round", "188: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 188: the model answers with a short reply", 12),
        ["round 188:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 188: the model answers with a short reply", 16),
        ["round 188: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 188: the model answers with a short reply", 24),
        ["round 188: the model", "answers with a short", "reply"],
    ),
    (("round 188: the model answers with a short reply", 32), ["round 188: the model answers", "with a short reply"]),
    (
        ("round 188: the recorder stores the reasoning trace", 4),
        ["round", "188:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 188: the recorder stores the reasoning trace", 8),
        ["round", "188: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 188: the recorder stores the reasoning trace", 12),
        ["round 188:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 188: the recorder stores the reasoning trace", 16),
        ["round 188: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 188: the recorder stores the reasoning trace", 24),
        ["round 188: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 188: the recorder stores the reasoning trace", 32),
        ["round 188: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 188: the angel watches the processor run", 4),
        ["round", "188:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 188: the angel watches the processor run", 8),
        ["round", "188: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 188: the angel watches the processor run", 12),
        ["round 188:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 188: the angel watches the processor run", 16),
        ["round 188: the", "angel watches", "the processor", "run"],
    ),
    (("round 188: the angel watches the processor run", 24), ["round 188: the angel", "watches the processor", "run"]),
    (("round 188: the angel watches the processor run", 32), ["round 188: the angel watches the", "processor run"]),
    (
        ("round 188: angle of the vector decides the match", 4),
        ["round", "188:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 188: angle of the vector decides the match", 8),
        ["round", "188:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 188: angle of the vector decides the match", 12),
        ["round 188:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 188: angle of the vector decides the match", 16),
        ["round 188: angle", "of the vector", "decides the", "match"],
    ),
    (("round 188: angle of the vector decides the match", 24), ["round 188: angle of the", "vector decides the match"]),
    (("round 188: angle of the vector decides the match", 32), ["round 188: angle of the vector", "decides the match"]),
    (
        ("round 188: the candle burns twice as long at night", 4),
        ["round", "188:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 188: the candle burns twice as long at night", 8),
        ["round", "188: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 188: the candle burns twice as long at night", 12),
        ["round 188:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 188: the candle burns twice as long at night", 16),
        ["round 188: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 188: the candle burns twice as long at night", 24),
        ["round 188: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 188: the candle burns twice as long at night", 32),
        ["round 188: the candle burns", "twice as long at night"],
    ),
    (
        ("round 188: a mirror of the universe in one line", 4),
        ["round", "188:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 188: a mirror of the universe in one line", 8),
        ["round", "188: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 188: a mirror of the universe in one line", 12),
        ["round 188: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 188: a mirror of the universe in one line", 16),
        ["round 188: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 188: a mirror of the universe in one line", 24), ["round 188: a mirror of", "the universe in one line"]),
    (("round 188: a mirror of the universe in one line", 32), ["round 188: a mirror of the", "universe in one line"]),
    (
        ("round 188: the queue drains before the storm", 4),
        ["round", "188:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 188: the queue drains before the storm", 8),
        ["round", "188: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 188: the queue drains before the storm", 12),
        ["round 188:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 188: the queue drains before the storm", 16), ["round 188: the", "queue drains", "before the storm"]),
    (("round 188: the queue drains before the storm", 24), ["round 188: the queue", "drains before the storm"]),
    (("round 188: the queue drains before the storm", 32), ["round 188: the queue drains", "before the storm"]),
    (
        ("kitten188 sitting188 agent188 angle188 universe188 memory188", 6),
        ["kitten188", "sitting188", "agent188", "angle188", "universe188", "memory188"],
    ),
    (
        ("kitten188 sitting188 agent188 angle188 universe188 memory188", 10),
        ["kitten188", "sitting188", "agent188", "angle188", "universe188", "memory188"],
    ),
    (
        ("kitten188 sitting188 agent188 angle188 universe188 memory188", 18),
        ["kitten188", "sitting188", "agent188 angle188", "universe188", "memory188"],
    ),
    (
        ("kitten188 sitting188 agent188 angle188 universe188 memory188", 28),
        ["kitten188 sitting188", "agent188 angle188", "universe188 memory188"],
    ),
    (
        ("sitting188 agent188 angle188 universe188 memory188 stream188", 6),
        ["sitting188", "agent188", "angle188", "universe188", "memory188", "stream188"],
    ),
    (
        ("sitting188 agent188 angle188 universe188 memory188 stream188", 10),
        ["sitting188", "agent188", "angle188", "universe188", "memory188", "stream188"],
    ),
    (
        ("sitting188 agent188 angle188 universe188 memory188 stream188", 18),
        ["sitting188", "agent188 angle188", "universe188", "memory188", "stream188"],
    ),
    (
        ("sitting188 agent188 angle188 universe188 memory188 stream188", 28),
        ["sitting188 agent188 angle188", "universe188 memory188", "stream188"],
    ),
    (
        ("agent188 angle188 universe188 memory188 stream188 context188", 6),
        ["agent188", "angle188", "universe188", "memory188", "stream188", "context188"],
    ),
    (
        ("agent188 angle188 universe188 memory188 stream188 context188", 10),
        ["agent188", "angle188", "universe188", "memory188", "stream188", "context188"],
    ),
    (
        ("agent188 angle188 universe188 memory188 stream188 context188", 18),
        ["agent188 angle188", "universe188", "memory188", "stream188", "context188"],
    ),
    (
        ("agent188 angle188 universe188 memory188 stream188 context188", 28),
        ["agent188 angle188", "universe188 memory188", "stream188 context188"],
    ),
    (
        ("angle188 universe188 memory188 stream188 context188 knowledge188", 6),
        ["angle188", "universe188", "memory188", "stream188", "context188", "knowledge188"],
    ),
    (
        ("angle188 universe188 memory188 stream188 context188 knowledge188", 10),
        ["angle188", "universe188", "memory188", "stream188", "context188", "knowledge188"],
    ),
    (
        ("angle188 universe188 memory188 stream188 context188 knowledge188", 18),
        ["angle188", "universe188", "memory188", "stream188", "context188", "knowledge188"],
    ),
    (
        ("angle188 universe188 memory188 stream188 context188 knowledge188", 28),
        ["angle188 universe188", "memory188 stream188", "context188 knowledge188"],
    ),
    (
        ("universe188 memory188 stream188 context188 knowledge188 vector188", 6),
        ["universe188", "memory188", "stream188", "context188", "knowledge188", "vector188"],
    ),
    (
        ("universe188 memory188 stream188 context188 knowledge188 vector188", 10),
        ["universe188", "memory188", "stream188", "context188", "knowledge188", "vector188"],
    ),
    (
        ("universe188 memory188 stream188 context188 knowledge188 vector188", 18),
        ["universe188", "memory188", "stream188", "context188", "knowledge188", "vector188"],
    ),
    (
        ("universe188 memory188 stream188 context188 knowledge188 vector188", 28),
        ["universe188 memory188", "stream188 context188", "knowledge188 vector188"],
    ),
    (
        ("memory188 stream188 context188 knowledge188 vector188 processor188", 6),
        ["memory188", "stream188", "context188", "knowledge188", "vector188", "processor188"],
    ),
    (
        ("memory188 stream188 context188 knowledge188 vector188 processor188", 10),
        ["memory188", "stream188", "context188", "knowledge188", "vector188", "processor188"],
    ),
    (
        ("memory188 stream188 context188 knowledge188 vector188 processor188", 18),
        ["memory188", "stream188", "context188", "knowledge188", "vector188", "processor188"],
    ),
    (
        ("memory188 stream188 context188 knowledge188 vector188 processor188", 28),
        ["memory188 stream188", "context188 knowledge188", "vector188 processor188"],
    ),
    (
        ("stream188 context188 knowledge188 vector188 processor188 reasoning188", 6),
        ["stream188", "context188", "knowledge188", "vector188", "processor188", "reasoning188"],
    ),
    (
        ("stream188 context188 knowledge188 vector188 processor188 reasoning188", 10),
        ["stream188", "context188", "knowledge188", "vector188", "processor188", "reasoning188"],
    ),
    (
        ("stream188 context188 knowledge188 vector188 processor188 reasoning188", 18),
        ["stream188", "context188", "knowledge188", "vector188", "processor188", "reasoning188"],
    ),
    (
        ("stream188 context188 knowledge188 vector188 processor188 reasoning188", 28),
        ["stream188 context188", "knowledge188 vector188", "processor188 reasoning188"],
    ),
    (
        ("context188 knowledge188 vector188 processor188 reasoning188 machine188", 6),
        ["context188", "knowledge188", "vector188", "processor188", "reasoning188", "machine188"],
    ),
    (
        ("context188 knowledge188 vector188 processor188 reasoning188 machine188", 10),
        ["context188", "knowledge188", "vector188", "processor188", "reasoning188", "machine188"],
    ),
    (
        ("context188 knowledge188 vector188 processor188 reasoning188 machine188", 18),
        ["context188", "knowledge188", "vector188", "processor188", "reasoning188", "machine188"],
    ),
    (
        ("context188 knowledge188 vector188 processor188 reasoning188 machine188", 28),
        ["context188 knowledge188", "vector188 processor188", "reasoning188 machine188"],
    ),
    (
        ("knowledge188 vector188 processor188 reasoning188 machine188 learning188", 6),
        ["knowledge188", "vector188", "processor188", "reasoning188", "machine188", "learning188"],
    ),
    (
        ("knowledge188 vector188 processor188 reasoning188 machine188 learning188", 10),
        ["knowledge188", "vector188", "processor188", "reasoning188", "machine188", "learning188"],
    ),
    (
        ("knowledge188 vector188 processor188 reasoning188 machine188 learning188", 18),
        ["knowledge188", "vector188", "processor188", "reasoning188", "machine188", "learning188"],
    ),
    (
        ("knowledge188 vector188 processor188 reasoning188 machine188 learning188", 28),
        ["knowledge188 vector188", "processor188 reasoning188", "machine188 learning188"],
    ),
    (
        ("vector188 processor188 reasoning188 machine188 learning188 model188", 6),
        ["vector188", "processor188", "reasoning188", "machine188", "learning188", "model188"],
    ),
    (
        ("vector188 processor188 reasoning188 machine188 learning188 model188", 10),
        ["vector188", "processor188", "reasoning188", "machine188", "learning188", "model188"],
    ),
    (
        ("vector188 processor188 reasoning188 machine188 learning188 model188", 18),
        ["vector188", "processor188", "reasoning188", "machine188", "learning188", "model188"],
    ),
    (
        ("vector188 processor188 reasoning188 machine188 learning188 model188", 28),
        ["vector188 processor188", "reasoning188 machine188", "learning188 model188"],
    ),
    (
        ("processor188 reasoning188 machine188 learning188 model188 token188", 6),
        ["processor188", "reasoning188", "machine188", "learning188", "model188", "token188"],
    ),
    (
        ("processor188 reasoning188 machine188 learning188 model188 token188", 10),
        ["processor188", "reasoning188", "machine188", "learning188", "model188", "token188"],
    ),
    (
        ("processor188 reasoning188 machine188 learning188 model188 token188", 18),
        ["processor188", "reasoning188", "machine188", "learning188", "model188 token188"],
    ),
    (
        ("processor188 reasoning188 machine188 learning188 model188 token188", 28),
        ["processor188 reasoning188", "machine188 learning188", "model188 token188"],
    ),
    (
        ("reasoning188 machine188 learning188 model188 token188 prompt188", 6),
        ["reasoning188", "machine188", "learning188", "model188", "token188", "prompt188"],
    ),
    (
        ("reasoning188 machine188 learning188 model188 token188 prompt188", 10),
        ["reasoning188", "machine188", "learning188", "model188", "token188", "prompt188"],
    ),
    (
        ("reasoning188 machine188 learning188 model188 token188 prompt188", 18),
        ["reasoning188", "machine188", "learning188", "model188 token188", "prompt188"],
    ),
    (
        ("reasoning188 machine188 learning188 model188 token188 prompt188", 28),
        ["reasoning188 machine188", "learning188 model188", "token188 prompt188"],
    ),
    (
        ("machine188 learning188 model188 token188 prompt188 session188", 6),
        ["machine188", "learning188", "model188", "token188", "prompt188", "session188"],
    ),
    (
        ("machine188 learning188 model188 token188 prompt188 session188", 10),
        ["machine188", "learning188", "model188", "token188", "prompt188", "session188"],
    ),
    (
        ("machine188 learning188 model188 token188 prompt188 session188", 18),
        ["machine188", "learning188", "model188 token188", "prompt188", "session188"],
    ),
    (
        ("machine188 learning188 model188 token188 prompt188 session188", 28),
        ["machine188 learning188", "model188 token188 prompt188", "session188"],
    ),
    (
        ("learning188 model188 token188 prompt188 session188 library188", 6),
        ["learning188", "model188", "token188", "prompt188", "session188", "library188"],
    ),
    (
        ("learning188 model188 token188 prompt188 session188 library188", 10),
        ["learning188", "model188", "token188", "prompt188", "session188", "library188"],
    ),
    (
        ("learning188 model188 token188 prompt188 session188 library188", 18),
        ["learning188", "model188 token188", "prompt188", "session188", "library188"],
    ),
    (
        ("learning188 model188 token188 prompt188 session188 library188", 28),
        ["learning188 model188", "token188 prompt188", "session188 library188"],
    ),
    (
        ("model188 token188 prompt188 session188 library188 service188", 6),
        ["model188", "token188", "prompt188", "session188", "library188", "service188"],
    ),
    (
        ("model188 token188 prompt188 session188 library188 service188", 10),
        ["model188", "token188", "prompt188", "session188", "library188", "service188"],
    ),
    (
        ("model188 token188 prompt188 session188 library188 service188", 18),
        ["model188 token188", "prompt188", "session188", "library188", "service188"],
    ),
    (
        ("model188 token188 prompt188 session188 library188 service188", 28),
        ["model188 token188 prompt188", "session188 library188", "service188"],
    ),
    (
        ("token188 prompt188 session188 library188 service188 gateway188", 6),
        ["token188", "prompt188", "session188", "library188", "service188", "gateway188"],
    ),
    (
        ("token188 prompt188 session188 library188 service188 gateway188", 10),
        ["token188", "prompt188", "session188", "library188", "service188", "gateway188"],
    ),
    (
        ("token188 prompt188 session188 library188 service188 gateway188", 18),
        ["token188 prompt188", "session188", "library188", "service188", "gateway188"],
    ),
    (
        ("token188 prompt188 session188 library188 service188 gateway188", 28),
        ["token188 prompt188", "session188 library188", "service188 gateway188"],
    ),
    (
        ("prompt188 session188 library188 service188 gateway188 storage188", 6),
        ["prompt188", "session188", "library188", "service188", "gateway188", "storage188"],
    ),
    (
        ("prompt188 session188 library188 service188 gateway188 storage188", 10),
        ["prompt188", "session188", "library188", "service188", "gateway188", "storage188"],
    ),
    (
        ("prompt188 session188 library188 service188 gateway188 storage188", 18),
        ["prompt188", "session188", "library188", "service188", "gateway188", "storage188"],
    ),
    (
        ("prompt188 session188 library188 service188 gateway188 storage188", 28),
        ["prompt188 session188", "library188 service188", "gateway188 storage188"],
    ),
    (
        ("session188 library188 service188 gateway188 storage188 network188", 6),
        ["session188", "library188", "service188", "gateway188", "storage188", "network188"],
    ),
    (
        ("session188 library188 service188 gateway188 storage188 network188", 10),
        ["session188", "library188", "service188", "gateway188", "storage188", "network188"],
    ),
    (
        ("session188 library188 service188 gateway188 storage188 network188", 18),
        ["session188", "library188", "service188", "gateway188", "storage188", "network188"],
    ),
    (
        ("session188 library188 service188 gateway188 storage188 network188", 28),
        ["session188 library188", "service188 gateway188", "storage188 network188"],
    ),
    (
        ("library188 service188 gateway188 storage188 network188 latency188", 6),
        ["library188", "service188", "gateway188", "storage188", "network188", "latency188"],
    ),
    (
        ("library188 service188 gateway188 storage188 network188 latency188", 10),
        ["library188", "service188", "gateway188", "storage188", "network188", "latency188"],
    ),
    (
        ("library188 service188 gateway188 storage188 network188 latency188", 18),
        ["library188", "service188", "gateway188", "storage188", "network188", "latency188"],
    ),
    (
        ("library188 service188 gateway188 storage188 network188 latency188", 28),
        ["library188 service188", "gateway188 storage188", "network188 latency188"],
    ),
    (
        ("service188 gateway188 storage188 network188 latency188 buffer188", 6),
        ["service188", "gateway188", "storage188", "network188", "latency188", "buffer188"],
    ),
    (
        ("service188 gateway188 storage188 network188 latency188 buffer188", 10),
        ["service188", "gateway188", "storage188", "network188", "latency188", "buffer188"],
    ),
    (
        ("service188 gateway188 storage188 network188 latency188 buffer188", 18),
        ["service188", "gateway188", "storage188", "network188", "latency188", "buffer188"],
    ),
    (
        ("service188 gateway188 storage188 network188 latency188 buffer188", 28),
        ["service188 gateway188", "storage188 network188", "latency188 buffer188"],
    ),
    (
        ("gateway188 storage188 network188 latency188 buffer188 queue188", 6),
        ["gateway188", "storage188", "network188", "latency188", "buffer188", "queue188"],
    ),
    (
        ("gateway188 storage188 network188 latency188 buffer188 queue188", 10),
        ["gateway188", "storage188", "network188", "latency188", "buffer188", "queue188"],
    ),
    (
        ("gateway188 storage188 network188 latency188 buffer188 queue188", 18),
        ["gateway188", "storage188", "network188", "latency188", "buffer188 queue188"],
    ),
    (
        ("gateway188 storage188 network188 latency188 buffer188 queue188", 28),
        ["gateway188 storage188", "network188 latency188", "buffer188 queue188"],
    ),
    (
        ("storage188 network188 latency188 buffer188 queue188 worker188", 6),
        ["storage188", "network188", "latency188", "buffer188", "queue188", "worker188"],
    ),
    (
        ("storage188 network188 latency188 buffer188 queue188 worker188", 10),
        ["storage188", "network188", "latency188", "buffer188", "queue188", "worker188"],
    ),
    (
        ("storage188 network188 latency188 buffer188 queue188 worker188", 18),
        ["storage188", "network188", "latency188", "buffer188 queue188", "worker188"],
    ),
    (
        ("storage188 network188 latency188 buffer188 queue188 worker188", 28),
        ["storage188 network188", "latency188 buffer188", "queue188 worker188"],
    ),
    (
        ("network188 latency188 buffer188 queue188 worker188 kernel188", 6),
        ["network188", "latency188", "buffer188", "queue188", "worker188", "kernel188"],
    ),
    (
        ("network188 latency188 buffer188 queue188 worker188 kernel188", 10),
        ["network188", "latency188", "buffer188", "queue188", "worker188", "kernel188"],
    ),
    (
        ("network188 latency188 buffer188 queue188 worker188 kernel188", 18),
        ["network188", "latency188", "buffer188 queue188", "worker188", "kernel188"],
    ),
    (
        ("network188 latency188 buffer188 queue188 worker188 kernel188", 28),
        ["network188 latency188", "buffer188 queue188 worker188", "kernel188"],
    ),
    (
        ("latency188 buffer188 queue188 worker188 kernel188 signal188", 6),
        ["latency188", "buffer188", "queue188", "worker188", "kernel188", "signal188"],
    ),
    (
        ("latency188 buffer188 queue188 worker188 kernel188 signal188", 10),
        ["latency188", "buffer188", "queue188", "worker188", "kernel188", "signal188"],
    ),
    (
        ("latency188 buffer188 queue188 worker188 kernel188 signal188", 18),
        ["latency188", "buffer188 queue188", "worker188", "kernel188", "signal188"],
    ),
    (
        ("latency188 buffer188 queue188 worker188 kernel188 signal188", 28),
        ["latency188 buffer188", "queue188 worker188 kernel188", "signal188"],
    ),
    (
        ("buffer188 queue188 worker188 kernel188 signal188 packet188", 6),
        ["buffer188", "queue188", "worker188", "kernel188", "signal188", "packet188"],
    ),
    (
        ("buffer188 queue188 worker188 kernel188 signal188 packet188", 10),
        ["buffer188", "queue188", "worker188", "kernel188", "signal188", "packet188"],
    ),
    (
        ("buffer188 queue188 worker188 kernel188 signal188 packet188", 18),
        ["buffer188 queue188", "worker188", "kernel188", "signal188", "packet188"],
    ),
    (
        ("buffer188 queue188 worker188 kernel188 signal188 packet188", 28),
        ["buffer188 queue188 worker188", "kernel188 signal188", "packet188"],
    ),
    (
        ("queue188 worker188 kernel188 signal188 packet188 router188", 6),
        ["queue188", "worker188", "kernel188", "signal188", "packet188", "router188"],
    ),
    (
        ("queue188 worker188 kernel188 signal188 packet188 router188", 10),
        ["queue188", "worker188", "kernel188", "signal188", "packet188", "router188"],
    ),
    (
        ("queue188 worker188 kernel188 signal188 packet188 router188", 18),
        ["queue188 worker188", "kernel188", "signal188", "packet188", "router188"],
    ),
    (
        ("queue188 worker188 kernel188 signal188 packet188 router188", 28),
        ["queue188 worker188 kernel188", "signal188 packet188", "router188"],
    ),
    (
        ("worker188 kernel188 signal188 packet188 router188 cluster188", 6),
        ["worker188", "kernel188", "signal188", "packet188", "router188", "cluster188"],
    ),
    (
        ("worker188 kernel188 signal188 packet188 router188 cluster188", 10),
        ["worker188", "kernel188", "signal188", "packet188", "router188", "cluster188"],
    ),
    (
        ("worker188 kernel188 signal188 packet188 router188 cluster188", 18),
        ["worker188", "kernel188", "signal188", "packet188", "router188", "cluster188"],
    ),
    (
        ("worker188 kernel188 signal188 packet188 router188 cluster188", 28),
        ["worker188 kernel188", "signal188 packet188", "router188 cluster188"],
    ),
    (
        ("kernel188 signal188 packet188 router188 cluster188 mirror188", 6),
        ["kernel188", "signal188", "packet188", "router188", "cluster188", "mirror188"],
    ),
    (
        ("kernel188 signal188 packet188 router188 cluster188 mirror188", 10),
        ["kernel188", "signal188", "packet188", "router188", "cluster188", "mirror188"],
    ),
    (
        ("kernel188 signal188 packet188 router188 cluster188 mirror188", 18),
        ["kernel188", "signal188", "packet188", "router188", "cluster188", "mirror188"],
    ),
    (
        ("kernel188 signal188 packet188 router188 cluster188 mirror188", 28),
        ["kernel188 signal188", "packet188 router188", "cluster188 mirror188"],
    ),
    (
        ("signal188 packet188 router188 cluster188 mirror188 filter188", 6),
        ["signal188", "packet188", "router188", "cluster188", "mirror188", "filter188"],
    ),
    (
        ("signal188 packet188 router188 cluster188 mirror188 filter188", 10),
        ["signal188", "packet188", "router188", "cluster188", "mirror188", "filter188"],
    ),
    (
        ("signal188 packet188 router188 cluster188 mirror188 filter188", 18),
        ["signal188", "packet188", "router188", "cluster188", "mirror188", "filter188"],
    ),
    (
        ("signal188 packet188 router188 cluster188 mirror188 filter188", 28),
        ["signal188 packet188", "router188 cluster188", "mirror188 filter188"],
    ),
    (
        ("packet188 router188 cluster188 mirror188 filter188 ranking188", 6),
        ["packet188", "router188", "cluster188", "mirror188", "filter188", "ranking188"],
    ),
    (
        ("packet188 router188 cluster188 mirror188 filter188 ranking188", 10),
        ["packet188", "router188", "cluster188", "mirror188", "filter188", "ranking188"],
    ),
    (
        ("packet188 router188 cluster188 mirror188 filter188 ranking188", 18),
        ["packet188", "router188", "cluster188", "mirror188", "filter188", "ranking188"],
    ),
    (
        ("packet188 router188 cluster188 mirror188 filter188 ranking188", 28),
        ["packet188 router188", "cluster188 mirror188", "filter188 ranking188"],
    ),
    (
        ("router188 cluster188 mirror188 filter188 ranking188 encoding188", 6),
        ["router188", "cluster188", "mirror188", "filter188", "ranking188", "encoding188"],
    ),
    (
        ("router188 cluster188 mirror188 filter188 ranking188 encoding188", 10),
        ["router188", "cluster188", "mirror188", "filter188", "ranking188", "encoding188"],
    ),
    (
        ("router188 cluster188 mirror188 filter188 ranking188 encoding188", 18),
        ["router188", "cluster188", "mirror188", "filter188", "ranking188", "encoding188"],
    ),
    (
        ("router188 cluster188 mirror188 filter188 ranking188 encoding188", 28),
        ["router188 cluster188", "mirror188 filter188", "ranking188 encoding188"],
    ),
    (
        ("cluster188 mirror188 filter188 ranking188 encoding188 mapping188", 6),
        ["cluster188", "mirror188", "filter188", "ranking188", "encoding188", "mapping188"],
    ),
    (
        ("cluster188 mirror188 filter188 ranking188 encoding188 mapping188", 10),
        ["cluster188", "mirror188", "filter188", "ranking188", "encoding188", "mapping188"],
    ),
    (
        ("cluster188 mirror188 filter188 ranking188 encoding188 mapping188", 18),
        ["cluster188", "mirror188", "filter188", "ranking188", "encoding188", "mapping188"],
    ),
    (
        ("cluster188 mirror188 filter188 ranking188 encoding188 mapping188", 28),
        ["cluster188 mirror188", "filter188 ranking188", "encoding188 mapping188"],
    ),
    (
        ("mirror188 filter188 ranking188 encoding188 mapping188 record188", 6),
        ["mirror188", "filter188", "ranking188", "encoding188", "mapping188", "record188"],
    ),
    (
        ("mirror188 filter188 ranking188 encoding188 mapping188 record188", 10),
        ["mirror188", "filter188", "ranking188", "encoding188", "mapping188", "record188"],
    ),
    (
        ("mirror188 filter188 ranking188 encoding188 mapping188 record188", 18),
        ["mirror188", "filter188", "ranking188", "encoding188", "mapping188", "record188"],
    ),
    (
        ("mirror188 filter188 ranking188 encoding188 mapping188 record188", 28),
        ["mirror188 filter188", "ranking188 encoding188", "mapping188 record188"],
    ),
    (
        ("filter188 ranking188 encoding188 mapping188 record188 candle188", 6),
        ["filter188", "ranking188", "encoding188", "mapping188", "record188", "candle188"],
    ),
    (
        ("filter188 ranking188 encoding188 mapping188 record188 candle188", 10),
        ["filter188", "ranking188", "encoding188", "mapping188", "record188", "candle188"],
    ),
    (
        ("filter188 ranking188 encoding188 mapping188 record188 candle188", 18),
        ["filter188", "ranking188", "encoding188", "mapping188", "record188", "candle188"],
    ),
    (
        ("filter188 ranking188 encoding188 mapping188 record188 candle188", 28),
        ["filter188 ranking188", "encoding188 mapping188", "record188 candle188"],
    ),
    (
        ("ranking188 encoding188 mapping188 record188 candle188 thread188", 6),
        ["ranking188", "encoding188", "mapping188", "record188", "candle188", "thread188"],
    ),
    (
        ("ranking188 encoding188 mapping188 record188 candle188 thread188", 10),
        ["ranking188", "encoding188", "mapping188", "record188", "candle188", "thread188"],
    ),
    (
        ("ranking188 encoding188 mapping188 record188 candle188 thread188", 18),
        ["ranking188", "encoding188", "mapping188", "record188", "candle188", "thread188"],
    ),
    (
        ("ranking188 encoding188 mapping188 record188 candle188 thread188", 28),
        ["ranking188 encoding188", "mapping188 record188", "candle188 thread188"],
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
