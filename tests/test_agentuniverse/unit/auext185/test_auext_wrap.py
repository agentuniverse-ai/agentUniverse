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
        ("round 185: the quick brown fox jumps over the lazy dog", 4),
        ["round", "185:", "the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"],
    ),
    (
        ("round 185: the quick brown fox jumps over the lazy dog", 8),
        ["round", "185: the", "quick", "brown", "fox", "jumps", "over the", "lazy dog"],
    ),
    (
        ("round 185: the quick brown fox jumps over the lazy dog", 12),
        ["round 185:", "the quick", "brown fox", "jumps over", "the lazy dog"],
    ),
    (
        ("round 185: the quick brown fox jumps over the lazy dog", 16),
        ["round 185: the", "quick brown fox", "jumps over the", "lazy dog"],
    ),
    (
        ("round 185: the quick brown fox jumps over the lazy dog", 24),
        ["round 185: the quick", "brown fox jumps over the", "lazy dog"],
    ),
    (
        ("round 185: the quick brown fox jumps over the lazy dog", 32),
        ["round 185: the quick brown fox", "jumps over the lazy dog"],
    ),
    (
        ("round 185: agentuniverse is a framework for multi agents", 4),
        ["round", "185:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 185: agentuniverse is a framework for multi agents", 8),
        ["round", "185:", "agentuniverse", "is a", "framework", "for", "multi", "agents"],
    ),
    (
        ("round 185: agentuniverse is a framework for multi agents", 12),
        ["round 185:", "agentuniverse", "is a", "framework", "for multi", "agents"],
    ),
    (
        ("round 185: agentuniverse is a framework for multi agents", 16),
        ["round 185:", "agentuniverse is", "a framework for", "multi agents"],
    ),
    (
        ("round 185: agentuniverse is a framework for multi agents", 24),
        ["round 185: agentuniverse", "is a framework for multi", "agents"],
    ),
    (
        ("round 185: agentuniverse is a framework for multi agents", 32),
        ["round 185: agentuniverse is a", "framework for multi agents"],
    ),
    (
        ("round 185: knowledge stored as vectors enables retrieval", 4),
        ["round", "185:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 185: knowledge stored as vectors enables retrieval", 8),
        ["round", "185:", "knowledge", "stored", "as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 185: knowledge stored as vectors enables retrieval", 12),
        ["round 185:", "knowledge", "stored as", "vectors", "enables", "retrieval"],
    ),
    (
        ("round 185: knowledge stored as vectors enables retrieval", 16),
        ["round 185:", "knowledge stored", "as vectors", "enables", "retrieval"],
    ),
    (
        ("round 185: knowledge stored as vectors enables retrieval", 24),
        ["round 185: knowledge", "stored as vectors", "enables retrieval"],
    ),
    (
        ("round 185: knowledge stored as vectors enables retrieval", 32),
        ["round 185: knowledge stored as", "vectors enables retrieval"],
    ),
    (
        ("round 185: the processor reads the record then stops", 4),
        ["round", "185:", "the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 185: the processor reads the record then stops", 8),
        ["round", "185: the", "processor", "reads", "the", "record", "then", "stops"],
    ),
    (
        ("round 185: the processor reads the record then stops", 12),
        ["round 185:", "the", "processor", "reads the", "record then", "stops"],
    ),
    (
        ("round 185: the processor reads the record then stops", 16),
        ["round 185: the", "processor reads", "the record then", "stops"],
    ),
    (
        ("round 185: the processor reads the record then stops", 24),
        ["round 185: the processor", "reads the record then", "stops"],
    ),
    (
        ("round 185: the processor reads the record then stops", 32),
        ["round 185: the processor reads", "the record then stops"],
    ),
    (
        ("round 185: a worker pulls the next task from the queue", 4),
        ["round", "185:", "a", "worker", "pulls", "the", "next", "task", "from", "the", "queue"],
    ),
    (
        ("round 185: a worker pulls the next task from the queue", 8),
        ["round", "185: a", "worker", "pulls", "the next", "task", "from the", "queue"],
    ),
    (
        ("round 185: a worker pulls the next task from the queue", 12),
        ["round 185: a", "worker pulls", "the next", "task from", "the queue"],
    ),
    (
        ("round 185: a worker pulls the next task from the queue", 16),
        ["round 185: a", "worker pulls the", "next task from", "the queue"],
    ),
    (
        ("round 185: a worker pulls the next task from the queue", 24),
        ["round 185: a worker", "pulls the next task from", "the queue"],
    ),
    (
        ("round 185: a worker pulls the next task from the queue", 32),
        ["round 185: a worker pulls the", "next task from the queue"],
    ),
    (
        ("round 185: signals travel through the network layer", 4),
        ["round", "185:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 185: signals travel through the network layer", 8),
        ["round", "185:", "signals", "travel", "through", "the", "network", "layer"],
    ),
    (
        ("round 185: signals travel through the network layer", 12),
        ["round 185:", "signals", "travel", "through the", "network", "layer"],
    ),
    (
        ("round 185: signals travel through the network layer", 16),
        ["round 185:", "signals travel", "through the", "network layer"],
    ),
    (
        ("round 185: signals travel through the network layer", 24),
        ["round 185: signals", "travel through the", "network layer"],
    ),
    (
        ("round 185: signals travel through the network layer", 32),
        ["round 185: signals travel", "through the network layer"],
    ),
    (
        ("round 185: the gateway routes each request by policy", 4),
        ["round", "185:", "the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 185: the gateway routes each request by policy", 8),
        ["round", "185: the", "gateway", "routes", "each", "request", "by", "policy"],
    ),
    (
        ("round 185: the gateway routes each request by policy", 12),
        ["round 185:", "the gateway", "routes each", "request by", "policy"],
    ),
    (
        ("round 185: the gateway routes each request by policy", 16),
        ["round 185: the", "gateway routes", "each request by", "policy"],
    ),
    (
        ("round 185: the gateway routes each request by policy", 24),
        ["round 185: the gateway", "routes each request by", "policy"],
    ),
    (
        ("round 185: the gateway routes each request by policy", 32),
        ["round 185: the gateway routes", "each request by policy"],
    ),
    (
        ("round 185: memory grows until the buffer is full", 4),
        ["round", "185:", "memory", "grows", "until", "the", "buffer", "is", "full"],
    ),
    (
        ("round 185: memory grows until the buffer is full", 8),
        ["round", "185:", "memory", "grows", "until", "the", "buffer", "is full"],
    ),
    (
        ("round 185: memory grows until the buffer is full", 12),
        ["round 185:", "memory grows", "until the", "buffer is", "full"],
    ),
    (
        ("round 185: memory grows until the buffer is full", 16),
        ["round 185:", "memory grows", "until the buffer", "is full"],
    ),
    (("round 185: memory grows until the buffer is full", 24), ["round 185: memory grows", "until the buffer is full"]),
    (("round 185: memory grows until the buffer is full", 32), ["round 185: memory grows until", "the buffer is full"]),
    (
        ("round 185: the cluster mirrors every packet twice", 4),
        ["round", "185:", "the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 185: the cluster mirrors every packet twice", 8),
        ["round", "185: the", "cluster", "mirrors", "every", "packet", "twice"],
    ),
    (
        ("round 185: the cluster mirrors every packet twice", 12),
        ["round 185:", "the cluster", "mirrors", "every packet", "twice"],
    ),
    (
        ("round 185: the cluster mirrors every packet twice", 16),
        ["round 185: the", "cluster mirrors", "every packet", "twice"],
    ),
    (
        ("round 185: the cluster mirrors every packet twice", 24),
        ["round 185: the cluster", "mirrors every packet", "twice"],
    ),
    (
        ("round 185: the cluster mirrors every packet twice", 32),
        ["round 185: the cluster mirrors", "every packet twice"],
    ),
    (
        ("round 185: ranking uses tokens learned from the corpus", 4),
        ["round", "185:", "ranking", "uses", "tokens", "learned", "from", "the", "corpus"],
    ),
    (
        ("round 185: ranking uses tokens learned from the corpus", 8),
        ["round", "185:", "ranking", "uses", "tokens", "learned", "from the", "corpus"],
    ),
    (
        ("round 185: ranking uses tokens learned from the corpus", 12),
        ["round 185:", "ranking uses", "tokens", "learned from", "the corpus"],
    ),
    (
        ("round 185: ranking uses tokens learned from the corpus", 16),
        ["round 185:", "ranking uses", "tokens learned", "from the corpus"],
    ),
    (
        ("round 185: ranking uses tokens learned from the corpus", 24),
        ["round 185: ranking uses", "tokens learned from the", "corpus"],
    ),
    (
        ("round 185: ranking uses tokens learned from the corpus", 32),
        ["round 185: ranking uses tokens", "learned from the corpus"],
    ),
    (
        ("round 185: a long session ends when the candle dies", 4),
        ["round", "185:", "a", "long", "session", "ends", "when", "the", "candle", "dies"],
    ),
    (
        ("round 185: a long session ends when the candle dies", 8),
        ["round", "185: a", "long", "session", "ends", "when the", "candle", "dies"],
    ),
    (
        ("round 185: a long session ends when the candle dies", 12),
        ["round 185: a", "long session", "ends when", "the candle", "dies"],
    ),
    (
        ("round 185: a long session ends when the candle dies", 16),
        ["round 185: a", "long session", "ends when the", "candle dies"],
    ),
    (
        ("round 185: a long session ends when the candle dies", 24),
        ["round 185: a long", "session ends when the", "candle dies"],
    ),
    (
        ("round 185: a long session ends when the candle dies", 32),
        ["round 185: a long session ends", "when the candle dies"],
    ),
    (
        ("round 185: encode the prompt then map the result", 4),
        ["round", "185:", "encode", "the", "prompt", "then", "map", "the", "result"],
    ),
    (
        ("round 185: encode the prompt then map the result", 8),
        ["round", "185:", "encode", "the", "prompt", "then map", "the", "result"],
    ),
    (
        ("round 185: encode the prompt then map the result", 12),
        ["round 185:", "encode the", "prompt then", "map the", "result"],
    ),
    (
        ("round 185: encode the prompt then map the result", 16),
        ["round 185:", "encode the", "prompt then map", "the result"],
    ),
    (
        ("round 185: encode the prompt then map the result", 24),
        ["round 185: encode the", "prompt then map the", "result"],
    ),
    (("round 185: encode the prompt then map the result", 32), ["round 185: encode the prompt", "then map the result"]),
    (
        ("round 185: the kernel wakes the worker at dawn", 4),
        ["round", "185:", "the", "kernel", "wakes", "the", "worker", "at", "dawn"],
    ),
    (
        ("round 185: the kernel wakes the worker at dawn", 8),
        ["round", "185: the", "kernel", "wakes", "the", "worker", "at dawn"],
    ),
    (
        ("round 185: the kernel wakes the worker at dawn", 12),
        ["round 185:", "the kernel", "wakes the", "worker at", "dawn"],
    ),
    (("round 185: the kernel wakes the worker at dawn", 16), ["round 185: the", "kernel wakes the", "worker at dawn"]),
    (("round 185: the kernel wakes the worker at dawn", 24), ["round 185: the kernel", "wakes the worker at dawn"]),
    (("round 185: the kernel wakes the worker at dawn", 32), ["round 185: the kernel wakes the", "worker at dawn"]),
    (
        ("round 185: service latency drops after the patch", 4),
        ["round", "185:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 185: service latency drops after the patch", 8),
        ["round", "185:", "service", "latency", "drops", "after", "the", "patch"],
    ),
    (
        ("round 185: service latency drops after the patch", 12),
        ["round 185:", "service", "latency", "drops after", "the patch"],
    ),
    (
        ("round 185: service latency drops after the patch", 16),
        ["round 185:", "service latency", "drops after the", "patch"],
    ),
    (
        ("round 185: service latency drops after the patch", 24),
        ["round 185: service", "latency drops after the", "patch"],
    ),
    (("round 185: service latency drops after the patch", 32), ["round 185: service latency drops", "after the patch"]),
    (
        ("round 185: the library caches every vector it sees", 4),
        ["round", "185:", "the", "library", "caches", "every", "vector", "it", "sees"],
    ),
    (
        ("round 185: the library caches every vector it sees", 8),
        ["round", "185: the", "library", "caches", "every", "vector", "it sees"],
    ),
    (
        ("round 185: the library caches every vector it sees", 12),
        ["round 185:", "the library", "caches every", "vector it", "sees"],
    ),
    (
        ("round 185: the library caches every vector it sees", 16),
        ["round 185: the", "library caches", "every vector it", "sees"],
    ),
    (
        ("round 185: the library caches every vector it sees", 24),
        ["round 185: the library", "caches every vector it", "sees"],
    ),
    (
        ("round 185: the library caches every vector it sees", 32),
        ["round 185: the library caches", "every vector it sees"],
    ),
    (
        ("round 185: agents argue then the debate resolves", 4),
        ["round", "185:", "agents", "argue", "then", "the", "debate", "resolves"],
    ),
    (
        ("round 185: agents argue then the debate resolves", 8),
        ["round", "185:", "agents", "argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 185: agents argue then the debate resolves", 12),
        ["round 185:", "agents argue", "then the", "debate", "resolves"],
    ),
    (
        ("round 185: agents argue then the debate resolves", 16),
        ["round 185:", "agents argue", "then the debate", "resolves"],
    ),
    (("round 185: agents argue then the debate resolves", 24), ["round 185: agents argue", "then the debate resolves"]),
    (("round 185: agents argue then the debate resolves", 32), ["round 185: agents argue then the", "debate resolves"]),
    (
        ("round 185: the filter keeps only strong matches", 4),
        ["round", "185:", "the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 185: the filter keeps only strong matches", 8),
        ["round", "185: the", "filter", "keeps", "only", "strong", "matches"],
    ),
    (
        ("round 185: the filter keeps only strong matches", 12),
        ["round 185:", "the filter", "keeps only", "strong", "matches"],
    ),
    (
        ("round 185: the filter keeps only strong matches", 16),
        ["round 185: the", "filter keeps", "only strong", "matches"],
    ),
    (
        ("round 185: the filter keeps only strong matches", 24),
        ["round 185: the filter", "keeps only strong", "matches"],
    ),
    (("round 185: the filter keeps only strong matches", 32), ["round 185: the filter keeps only", "strong matches"]),
    (
        ("round 185: the model answers with a short reply", 4),
        ["round", "185:", "the", "model", "answers", "with", "a", "short", "reply"],
    ),
    (
        ("round 185: the model answers with a short reply", 8),
        ["round", "185: the", "model", "answers", "with a", "short", "reply"],
    ),
    (
        ("round 185: the model answers with a short reply", 12),
        ["round 185:", "the model", "answers with", "a short", "reply"],
    ),
    (
        ("round 185: the model answers with a short reply", 16),
        ["round 185: the", "model answers", "with a short", "reply"],
    ),
    (
        ("round 185: the model answers with a short reply", 24),
        ["round 185: the model", "answers with a short", "reply"],
    ),
    (("round 185: the model answers with a short reply", 32), ["round 185: the model answers", "with a short reply"]),
    (
        ("round 185: the recorder stores the reasoning trace", 4),
        ["round", "185:", "the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 185: the recorder stores the reasoning trace", 8),
        ["round", "185: the", "recorder", "stores", "the", "reasoning", "trace"],
    ),
    (
        ("round 185: the recorder stores the reasoning trace", 12),
        ["round 185:", "the recorder", "stores the", "reasoning", "trace"],
    ),
    (
        ("round 185: the recorder stores the reasoning trace", 16),
        ["round 185: the", "recorder stores", "the reasoning", "trace"],
    ),
    (
        ("round 185: the recorder stores the reasoning trace", 24),
        ["round 185: the recorder", "stores the reasoning", "trace"],
    ),
    (
        ("round 185: the recorder stores the reasoning trace", 32),
        ["round 185: the recorder stores", "the reasoning trace"],
    ),
    (
        ("round 185: the angel watches the processor run", 4),
        ["round", "185:", "the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 185: the angel watches the processor run", 8),
        ["round", "185: the", "angel", "watches", "the", "processor", "run"],
    ),
    (
        ("round 185: the angel watches the processor run", 12),
        ["round 185:", "the angel", "watches the", "processor", "run"],
    ),
    (
        ("round 185: the angel watches the processor run", 16),
        ["round 185: the", "angel watches", "the processor", "run"],
    ),
    (("round 185: the angel watches the processor run", 24), ["round 185: the angel", "watches the processor", "run"]),
    (("round 185: the angel watches the processor run", 32), ["round 185: the angel watches the", "processor run"]),
    (
        ("round 185: angle of the vector decides the match", 4),
        ["round", "185:", "angle", "of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 185: angle of the vector decides the match", 8),
        ["round", "185:", "angle of", "the", "vector", "decides", "the", "match"],
    ),
    (
        ("round 185: angle of the vector decides the match", 12),
        ["round 185:", "angle of the", "vector", "decides the", "match"],
    ),
    (
        ("round 185: angle of the vector decides the match", 16),
        ["round 185: angle", "of the vector", "decides the", "match"],
    ),
    (("round 185: angle of the vector decides the match", 24), ["round 185: angle of the", "vector decides the match"]),
    (("round 185: angle of the vector decides the match", 32), ["round 185: angle of the vector", "decides the match"]),
    (
        ("round 185: the candle burns twice as long at night", 4),
        ["round", "185:", "the", "candle", "burns", "twice", "as", "long", "at", "night"],
    ),
    (
        ("round 185: the candle burns twice as long at night", 8),
        ["round", "185: the", "candle", "burns", "twice as", "long at", "night"],
    ),
    (
        ("round 185: the candle burns twice as long at night", 12),
        ["round 185:", "the candle", "burns twice", "as long at", "night"],
    ),
    (
        ("round 185: the candle burns twice as long at night", 16),
        ["round 185: the", "candle burns", "twice as long at", "night"],
    ),
    (
        ("round 185: the candle burns twice as long at night", 24),
        ["round 185: the candle", "burns twice as long at", "night"],
    ),
    (
        ("round 185: the candle burns twice as long at night", 32),
        ["round 185: the candle burns", "twice as long at night"],
    ),
    (
        ("round 185: a mirror of the universe in one line", 4),
        ["round", "185:", "a", "mirror", "of", "the", "universe", "in", "one", "line"],
    ),
    (
        ("round 185: a mirror of the universe in one line", 8),
        ["round", "185: a", "mirror", "of the", "universe", "in one", "line"],
    ),
    (
        ("round 185: a mirror of the universe in one line", 12),
        ["round 185: a", "mirror of", "the universe", "in one line"],
    ),
    (
        ("round 185: a mirror of the universe in one line", 16),
        ["round 185: a", "mirror of the", "universe in one", "line"],
    ),
    (("round 185: a mirror of the universe in one line", 24), ["round 185: a mirror of", "the universe in one line"]),
    (("round 185: a mirror of the universe in one line", 32), ["round 185: a mirror of the", "universe in one line"]),
    (
        ("round 185: the queue drains before the storm", 4),
        ["round", "185:", "the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 185: the queue drains before the storm", 8),
        ["round", "185: the", "queue", "drains", "before", "the", "storm"],
    ),
    (
        ("round 185: the queue drains before the storm", 12),
        ["round 185:", "the queue", "drains", "before the", "storm"],
    ),
    (("round 185: the queue drains before the storm", 16), ["round 185: the", "queue drains", "before the storm"]),
    (("round 185: the queue drains before the storm", 24), ["round 185: the queue", "drains before the storm"]),
    (("round 185: the queue drains before the storm", 32), ["round 185: the queue drains", "before the storm"]),
    (
        ("kitten185 sitting185 agent185 angle185 universe185 memory185", 6),
        ["kitten185", "sitting185", "agent185", "angle185", "universe185", "memory185"],
    ),
    (
        ("kitten185 sitting185 agent185 angle185 universe185 memory185", 10),
        ["kitten185", "sitting185", "agent185", "angle185", "universe185", "memory185"],
    ),
    (
        ("kitten185 sitting185 agent185 angle185 universe185 memory185", 18),
        ["kitten185", "sitting185", "agent185 angle185", "universe185", "memory185"],
    ),
    (
        ("kitten185 sitting185 agent185 angle185 universe185 memory185", 28),
        ["kitten185 sitting185", "agent185 angle185", "universe185 memory185"],
    ),
    (
        ("sitting185 agent185 angle185 universe185 memory185 stream185", 6),
        ["sitting185", "agent185", "angle185", "universe185", "memory185", "stream185"],
    ),
    (
        ("sitting185 agent185 angle185 universe185 memory185 stream185", 10),
        ["sitting185", "agent185", "angle185", "universe185", "memory185", "stream185"],
    ),
    (
        ("sitting185 agent185 angle185 universe185 memory185 stream185", 18),
        ["sitting185", "agent185 angle185", "universe185", "memory185", "stream185"],
    ),
    (
        ("sitting185 agent185 angle185 universe185 memory185 stream185", 28),
        ["sitting185 agent185 angle185", "universe185 memory185", "stream185"],
    ),
    (
        ("agent185 angle185 universe185 memory185 stream185 context185", 6),
        ["agent185", "angle185", "universe185", "memory185", "stream185", "context185"],
    ),
    (
        ("agent185 angle185 universe185 memory185 stream185 context185", 10),
        ["agent185", "angle185", "universe185", "memory185", "stream185", "context185"],
    ),
    (
        ("agent185 angle185 universe185 memory185 stream185 context185", 18),
        ["agent185 angle185", "universe185", "memory185", "stream185", "context185"],
    ),
    (
        ("agent185 angle185 universe185 memory185 stream185 context185", 28),
        ["agent185 angle185", "universe185 memory185", "stream185 context185"],
    ),
    (
        ("angle185 universe185 memory185 stream185 context185 knowledge185", 6),
        ["angle185", "universe185", "memory185", "stream185", "context185", "knowledge185"],
    ),
    (
        ("angle185 universe185 memory185 stream185 context185 knowledge185", 10),
        ["angle185", "universe185", "memory185", "stream185", "context185", "knowledge185"],
    ),
    (
        ("angle185 universe185 memory185 stream185 context185 knowledge185", 18),
        ["angle185", "universe185", "memory185", "stream185", "context185", "knowledge185"],
    ),
    (
        ("angle185 universe185 memory185 stream185 context185 knowledge185", 28),
        ["angle185 universe185", "memory185 stream185", "context185 knowledge185"],
    ),
    (
        ("universe185 memory185 stream185 context185 knowledge185 vector185", 6),
        ["universe185", "memory185", "stream185", "context185", "knowledge185", "vector185"],
    ),
    (
        ("universe185 memory185 stream185 context185 knowledge185 vector185", 10),
        ["universe185", "memory185", "stream185", "context185", "knowledge185", "vector185"],
    ),
    (
        ("universe185 memory185 stream185 context185 knowledge185 vector185", 18),
        ["universe185", "memory185", "stream185", "context185", "knowledge185", "vector185"],
    ),
    (
        ("universe185 memory185 stream185 context185 knowledge185 vector185", 28),
        ["universe185 memory185", "stream185 context185", "knowledge185 vector185"],
    ),
    (
        ("memory185 stream185 context185 knowledge185 vector185 processor185", 6),
        ["memory185", "stream185", "context185", "knowledge185", "vector185", "processor185"],
    ),
    (
        ("memory185 stream185 context185 knowledge185 vector185 processor185", 10),
        ["memory185", "stream185", "context185", "knowledge185", "vector185", "processor185"],
    ),
    (
        ("memory185 stream185 context185 knowledge185 vector185 processor185", 18),
        ["memory185", "stream185", "context185", "knowledge185", "vector185", "processor185"],
    ),
    (
        ("memory185 stream185 context185 knowledge185 vector185 processor185", 28),
        ["memory185 stream185", "context185 knowledge185", "vector185 processor185"],
    ),
    (
        ("stream185 context185 knowledge185 vector185 processor185 reasoning185", 6),
        ["stream185", "context185", "knowledge185", "vector185", "processor185", "reasoning185"],
    ),
    (
        ("stream185 context185 knowledge185 vector185 processor185 reasoning185", 10),
        ["stream185", "context185", "knowledge185", "vector185", "processor185", "reasoning185"],
    ),
    (
        ("stream185 context185 knowledge185 vector185 processor185 reasoning185", 18),
        ["stream185", "context185", "knowledge185", "vector185", "processor185", "reasoning185"],
    ),
    (
        ("stream185 context185 knowledge185 vector185 processor185 reasoning185", 28),
        ["stream185 context185", "knowledge185 vector185", "processor185 reasoning185"],
    ),
    (
        ("context185 knowledge185 vector185 processor185 reasoning185 machine185", 6),
        ["context185", "knowledge185", "vector185", "processor185", "reasoning185", "machine185"],
    ),
    (
        ("context185 knowledge185 vector185 processor185 reasoning185 machine185", 10),
        ["context185", "knowledge185", "vector185", "processor185", "reasoning185", "machine185"],
    ),
    (
        ("context185 knowledge185 vector185 processor185 reasoning185 machine185", 18),
        ["context185", "knowledge185", "vector185", "processor185", "reasoning185", "machine185"],
    ),
    (
        ("context185 knowledge185 vector185 processor185 reasoning185 machine185", 28),
        ["context185 knowledge185", "vector185 processor185", "reasoning185 machine185"],
    ),
    (
        ("knowledge185 vector185 processor185 reasoning185 machine185 learning185", 6),
        ["knowledge185", "vector185", "processor185", "reasoning185", "machine185", "learning185"],
    ),
    (
        ("knowledge185 vector185 processor185 reasoning185 machine185 learning185", 10),
        ["knowledge185", "vector185", "processor185", "reasoning185", "machine185", "learning185"],
    ),
    (
        ("knowledge185 vector185 processor185 reasoning185 machine185 learning185", 18),
        ["knowledge185", "vector185", "processor185", "reasoning185", "machine185", "learning185"],
    ),
    (
        ("knowledge185 vector185 processor185 reasoning185 machine185 learning185", 28),
        ["knowledge185 vector185", "processor185 reasoning185", "machine185 learning185"],
    ),
    (
        ("vector185 processor185 reasoning185 machine185 learning185 model185", 6),
        ["vector185", "processor185", "reasoning185", "machine185", "learning185", "model185"],
    ),
    (
        ("vector185 processor185 reasoning185 machine185 learning185 model185", 10),
        ["vector185", "processor185", "reasoning185", "machine185", "learning185", "model185"],
    ),
    (
        ("vector185 processor185 reasoning185 machine185 learning185 model185", 18),
        ["vector185", "processor185", "reasoning185", "machine185", "learning185", "model185"],
    ),
    (
        ("vector185 processor185 reasoning185 machine185 learning185 model185", 28),
        ["vector185 processor185", "reasoning185 machine185", "learning185 model185"],
    ),
    (
        ("processor185 reasoning185 machine185 learning185 model185 token185", 6),
        ["processor185", "reasoning185", "machine185", "learning185", "model185", "token185"],
    ),
    (
        ("processor185 reasoning185 machine185 learning185 model185 token185", 10),
        ["processor185", "reasoning185", "machine185", "learning185", "model185", "token185"],
    ),
    (
        ("processor185 reasoning185 machine185 learning185 model185 token185", 18),
        ["processor185", "reasoning185", "machine185", "learning185", "model185 token185"],
    ),
    (
        ("processor185 reasoning185 machine185 learning185 model185 token185", 28),
        ["processor185 reasoning185", "machine185 learning185", "model185 token185"],
    ),
    (
        ("reasoning185 machine185 learning185 model185 token185 prompt185", 6),
        ["reasoning185", "machine185", "learning185", "model185", "token185", "prompt185"],
    ),
    (
        ("reasoning185 machine185 learning185 model185 token185 prompt185", 10),
        ["reasoning185", "machine185", "learning185", "model185", "token185", "prompt185"],
    ),
    (
        ("reasoning185 machine185 learning185 model185 token185 prompt185", 18),
        ["reasoning185", "machine185", "learning185", "model185 token185", "prompt185"],
    ),
    (
        ("reasoning185 machine185 learning185 model185 token185 prompt185", 28),
        ["reasoning185 machine185", "learning185 model185", "token185 prompt185"],
    ),
    (
        ("machine185 learning185 model185 token185 prompt185 session185", 6),
        ["machine185", "learning185", "model185", "token185", "prompt185", "session185"],
    ),
    (
        ("machine185 learning185 model185 token185 prompt185 session185", 10),
        ["machine185", "learning185", "model185", "token185", "prompt185", "session185"],
    ),
    (
        ("machine185 learning185 model185 token185 prompt185 session185", 18),
        ["machine185", "learning185", "model185 token185", "prompt185", "session185"],
    ),
    (
        ("machine185 learning185 model185 token185 prompt185 session185", 28),
        ["machine185 learning185", "model185 token185 prompt185", "session185"],
    ),
    (
        ("learning185 model185 token185 prompt185 session185 library185", 6),
        ["learning185", "model185", "token185", "prompt185", "session185", "library185"],
    ),
    (
        ("learning185 model185 token185 prompt185 session185 library185", 10),
        ["learning185", "model185", "token185", "prompt185", "session185", "library185"],
    ),
    (
        ("learning185 model185 token185 prompt185 session185 library185", 18),
        ["learning185", "model185 token185", "prompt185", "session185", "library185"],
    ),
    (
        ("learning185 model185 token185 prompt185 session185 library185", 28),
        ["learning185 model185", "token185 prompt185", "session185 library185"],
    ),
    (
        ("model185 token185 prompt185 session185 library185 service185", 6),
        ["model185", "token185", "prompt185", "session185", "library185", "service185"],
    ),
    (
        ("model185 token185 prompt185 session185 library185 service185", 10),
        ["model185", "token185", "prompt185", "session185", "library185", "service185"],
    ),
    (
        ("model185 token185 prompt185 session185 library185 service185", 18),
        ["model185 token185", "prompt185", "session185", "library185", "service185"],
    ),
    (
        ("model185 token185 prompt185 session185 library185 service185", 28),
        ["model185 token185 prompt185", "session185 library185", "service185"],
    ),
    (
        ("token185 prompt185 session185 library185 service185 gateway185", 6),
        ["token185", "prompt185", "session185", "library185", "service185", "gateway185"],
    ),
    (
        ("token185 prompt185 session185 library185 service185 gateway185", 10),
        ["token185", "prompt185", "session185", "library185", "service185", "gateway185"],
    ),
    (
        ("token185 prompt185 session185 library185 service185 gateway185", 18),
        ["token185 prompt185", "session185", "library185", "service185", "gateway185"],
    ),
    (
        ("token185 prompt185 session185 library185 service185 gateway185", 28),
        ["token185 prompt185", "session185 library185", "service185 gateway185"],
    ),
    (
        ("prompt185 session185 library185 service185 gateway185 storage185", 6),
        ["prompt185", "session185", "library185", "service185", "gateway185", "storage185"],
    ),
    (
        ("prompt185 session185 library185 service185 gateway185 storage185", 10),
        ["prompt185", "session185", "library185", "service185", "gateway185", "storage185"],
    ),
    (
        ("prompt185 session185 library185 service185 gateway185 storage185", 18),
        ["prompt185", "session185", "library185", "service185", "gateway185", "storage185"],
    ),
    (
        ("prompt185 session185 library185 service185 gateway185 storage185", 28),
        ["prompt185 session185", "library185 service185", "gateway185 storage185"],
    ),
    (
        ("session185 library185 service185 gateway185 storage185 network185", 6),
        ["session185", "library185", "service185", "gateway185", "storage185", "network185"],
    ),
    (
        ("session185 library185 service185 gateway185 storage185 network185", 10),
        ["session185", "library185", "service185", "gateway185", "storage185", "network185"],
    ),
    (
        ("session185 library185 service185 gateway185 storage185 network185", 18),
        ["session185", "library185", "service185", "gateway185", "storage185", "network185"],
    ),
    (
        ("session185 library185 service185 gateway185 storage185 network185", 28),
        ["session185 library185", "service185 gateway185", "storage185 network185"],
    ),
    (
        ("library185 service185 gateway185 storage185 network185 latency185", 6),
        ["library185", "service185", "gateway185", "storage185", "network185", "latency185"],
    ),
    (
        ("library185 service185 gateway185 storage185 network185 latency185", 10),
        ["library185", "service185", "gateway185", "storage185", "network185", "latency185"],
    ),
    (
        ("library185 service185 gateway185 storage185 network185 latency185", 18),
        ["library185", "service185", "gateway185", "storage185", "network185", "latency185"],
    ),
    (
        ("library185 service185 gateway185 storage185 network185 latency185", 28),
        ["library185 service185", "gateway185 storage185", "network185 latency185"],
    ),
    (
        ("service185 gateway185 storage185 network185 latency185 buffer185", 6),
        ["service185", "gateway185", "storage185", "network185", "latency185", "buffer185"],
    ),
    (
        ("service185 gateway185 storage185 network185 latency185 buffer185", 10),
        ["service185", "gateway185", "storage185", "network185", "latency185", "buffer185"],
    ),
    (
        ("service185 gateway185 storage185 network185 latency185 buffer185", 18),
        ["service185", "gateway185", "storage185", "network185", "latency185", "buffer185"],
    ),
    (
        ("service185 gateway185 storage185 network185 latency185 buffer185", 28),
        ["service185 gateway185", "storage185 network185", "latency185 buffer185"],
    ),
    (
        ("gateway185 storage185 network185 latency185 buffer185 queue185", 6),
        ["gateway185", "storage185", "network185", "latency185", "buffer185", "queue185"],
    ),
    (
        ("gateway185 storage185 network185 latency185 buffer185 queue185", 10),
        ["gateway185", "storage185", "network185", "latency185", "buffer185", "queue185"],
    ),
    (
        ("gateway185 storage185 network185 latency185 buffer185 queue185", 18),
        ["gateway185", "storage185", "network185", "latency185", "buffer185 queue185"],
    ),
    (
        ("gateway185 storage185 network185 latency185 buffer185 queue185", 28),
        ["gateway185 storage185", "network185 latency185", "buffer185 queue185"],
    ),
    (
        ("storage185 network185 latency185 buffer185 queue185 worker185", 6),
        ["storage185", "network185", "latency185", "buffer185", "queue185", "worker185"],
    ),
    (
        ("storage185 network185 latency185 buffer185 queue185 worker185", 10),
        ["storage185", "network185", "latency185", "buffer185", "queue185", "worker185"],
    ),
    (
        ("storage185 network185 latency185 buffer185 queue185 worker185", 18),
        ["storage185", "network185", "latency185", "buffer185 queue185", "worker185"],
    ),
    (
        ("storage185 network185 latency185 buffer185 queue185 worker185", 28),
        ["storage185 network185", "latency185 buffer185", "queue185 worker185"],
    ),
    (
        ("network185 latency185 buffer185 queue185 worker185 kernel185", 6),
        ["network185", "latency185", "buffer185", "queue185", "worker185", "kernel185"],
    ),
    (
        ("network185 latency185 buffer185 queue185 worker185 kernel185", 10),
        ["network185", "latency185", "buffer185", "queue185", "worker185", "kernel185"],
    ),
    (
        ("network185 latency185 buffer185 queue185 worker185 kernel185", 18),
        ["network185", "latency185", "buffer185 queue185", "worker185", "kernel185"],
    ),
    (
        ("network185 latency185 buffer185 queue185 worker185 kernel185", 28),
        ["network185 latency185", "buffer185 queue185 worker185", "kernel185"],
    ),
    (
        ("latency185 buffer185 queue185 worker185 kernel185 signal185", 6),
        ["latency185", "buffer185", "queue185", "worker185", "kernel185", "signal185"],
    ),
    (
        ("latency185 buffer185 queue185 worker185 kernel185 signal185", 10),
        ["latency185", "buffer185", "queue185", "worker185", "kernel185", "signal185"],
    ),
    (
        ("latency185 buffer185 queue185 worker185 kernel185 signal185", 18),
        ["latency185", "buffer185 queue185", "worker185", "kernel185", "signal185"],
    ),
    (
        ("latency185 buffer185 queue185 worker185 kernel185 signal185", 28),
        ["latency185 buffer185", "queue185 worker185 kernel185", "signal185"],
    ),
    (
        ("buffer185 queue185 worker185 kernel185 signal185 packet185", 6),
        ["buffer185", "queue185", "worker185", "kernel185", "signal185", "packet185"],
    ),
    (
        ("buffer185 queue185 worker185 kernel185 signal185 packet185", 10),
        ["buffer185", "queue185", "worker185", "kernel185", "signal185", "packet185"],
    ),
    (
        ("buffer185 queue185 worker185 kernel185 signal185 packet185", 18),
        ["buffer185 queue185", "worker185", "kernel185", "signal185", "packet185"],
    ),
    (
        ("buffer185 queue185 worker185 kernel185 signal185 packet185", 28),
        ["buffer185 queue185 worker185", "kernel185 signal185", "packet185"],
    ),
    (
        ("queue185 worker185 kernel185 signal185 packet185 router185", 6),
        ["queue185", "worker185", "kernel185", "signal185", "packet185", "router185"],
    ),
    (
        ("queue185 worker185 kernel185 signal185 packet185 router185", 10),
        ["queue185", "worker185", "kernel185", "signal185", "packet185", "router185"],
    ),
    (
        ("queue185 worker185 kernel185 signal185 packet185 router185", 18),
        ["queue185 worker185", "kernel185", "signal185", "packet185", "router185"],
    ),
    (
        ("queue185 worker185 kernel185 signal185 packet185 router185", 28),
        ["queue185 worker185 kernel185", "signal185 packet185", "router185"],
    ),
    (
        ("worker185 kernel185 signal185 packet185 router185 cluster185", 6),
        ["worker185", "kernel185", "signal185", "packet185", "router185", "cluster185"],
    ),
    (
        ("worker185 kernel185 signal185 packet185 router185 cluster185", 10),
        ["worker185", "kernel185", "signal185", "packet185", "router185", "cluster185"],
    ),
    (
        ("worker185 kernel185 signal185 packet185 router185 cluster185", 18),
        ["worker185", "kernel185", "signal185", "packet185", "router185", "cluster185"],
    ),
    (
        ("worker185 kernel185 signal185 packet185 router185 cluster185", 28),
        ["worker185 kernel185", "signal185 packet185", "router185 cluster185"],
    ),
    (
        ("kernel185 signal185 packet185 router185 cluster185 mirror185", 6),
        ["kernel185", "signal185", "packet185", "router185", "cluster185", "mirror185"],
    ),
    (
        ("kernel185 signal185 packet185 router185 cluster185 mirror185", 10),
        ["kernel185", "signal185", "packet185", "router185", "cluster185", "mirror185"],
    ),
    (
        ("kernel185 signal185 packet185 router185 cluster185 mirror185", 18),
        ["kernel185", "signal185", "packet185", "router185", "cluster185", "mirror185"],
    ),
    (
        ("kernel185 signal185 packet185 router185 cluster185 mirror185", 28),
        ["kernel185 signal185", "packet185 router185", "cluster185 mirror185"],
    ),
    (
        ("signal185 packet185 router185 cluster185 mirror185 filter185", 6),
        ["signal185", "packet185", "router185", "cluster185", "mirror185", "filter185"],
    ),
    (
        ("signal185 packet185 router185 cluster185 mirror185 filter185", 10),
        ["signal185", "packet185", "router185", "cluster185", "mirror185", "filter185"],
    ),
    (
        ("signal185 packet185 router185 cluster185 mirror185 filter185", 18),
        ["signal185", "packet185", "router185", "cluster185", "mirror185", "filter185"],
    ),
    (
        ("signal185 packet185 router185 cluster185 mirror185 filter185", 28),
        ["signal185 packet185", "router185 cluster185", "mirror185 filter185"],
    ),
    (
        ("packet185 router185 cluster185 mirror185 filter185 ranking185", 6),
        ["packet185", "router185", "cluster185", "mirror185", "filter185", "ranking185"],
    ),
    (
        ("packet185 router185 cluster185 mirror185 filter185 ranking185", 10),
        ["packet185", "router185", "cluster185", "mirror185", "filter185", "ranking185"],
    ),
    (
        ("packet185 router185 cluster185 mirror185 filter185 ranking185", 18),
        ["packet185", "router185", "cluster185", "mirror185", "filter185", "ranking185"],
    ),
    (
        ("packet185 router185 cluster185 mirror185 filter185 ranking185", 28),
        ["packet185 router185", "cluster185 mirror185", "filter185 ranking185"],
    ),
    (
        ("router185 cluster185 mirror185 filter185 ranking185 encoding185", 6),
        ["router185", "cluster185", "mirror185", "filter185", "ranking185", "encoding185"],
    ),
    (
        ("router185 cluster185 mirror185 filter185 ranking185 encoding185", 10),
        ["router185", "cluster185", "mirror185", "filter185", "ranking185", "encoding185"],
    ),
    (
        ("router185 cluster185 mirror185 filter185 ranking185 encoding185", 18),
        ["router185", "cluster185", "mirror185", "filter185", "ranking185", "encoding185"],
    ),
    (
        ("router185 cluster185 mirror185 filter185 ranking185 encoding185", 28),
        ["router185 cluster185", "mirror185 filter185", "ranking185 encoding185"],
    ),
    (
        ("cluster185 mirror185 filter185 ranking185 encoding185 mapping185", 6),
        ["cluster185", "mirror185", "filter185", "ranking185", "encoding185", "mapping185"],
    ),
    (
        ("cluster185 mirror185 filter185 ranking185 encoding185 mapping185", 10),
        ["cluster185", "mirror185", "filter185", "ranking185", "encoding185", "mapping185"],
    ),
    (
        ("cluster185 mirror185 filter185 ranking185 encoding185 mapping185", 18),
        ["cluster185", "mirror185", "filter185", "ranking185", "encoding185", "mapping185"],
    ),
    (
        ("cluster185 mirror185 filter185 ranking185 encoding185 mapping185", 28),
        ["cluster185 mirror185", "filter185 ranking185", "encoding185 mapping185"],
    ),
    (
        ("mirror185 filter185 ranking185 encoding185 mapping185 record185", 6),
        ["mirror185", "filter185", "ranking185", "encoding185", "mapping185", "record185"],
    ),
    (
        ("mirror185 filter185 ranking185 encoding185 mapping185 record185", 10),
        ["mirror185", "filter185", "ranking185", "encoding185", "mapping185", "record185"],
    ),
    (
        ("mirror185 filter185 ranking185 encoding185 mapping185 record185", 18),
        ["mirror185", "filter185", "ranking185", "encoding185", "mapping185", "record185"],
    ),
    (
        ("mirror185 filter185 ranking185 encoding185 mapping185 record185", 28),
        ["mirror185 filter185", "ranking185 encoding185", "mapping185 record185"],
    ),
    (
        ("filter185 ranking185 encoding185 mapping185 record185 candle185", 6),
        ["filter185", "ranking185", "encoding185", "mapping185", "record185", "candle185"],
    ),
    (
        ("filter185 ranking185 encoding185 mapping185 record185 candle185", 10),
        ["filter185", "ranking185", "encoding185", "mapping185", "record185", "candle185"],
    ),
    (
        ("filter185 ranking185 encoding185 mapping185 record185 candle185", 18),
        ["filter185", "ranking185", "encoding185", "mapping185", "record185", "candle185"],
    ),
    (
        ("filter185 ranking185 encoding185 mapping185 record185 candle185", 28),
        ["filter185 ranking185", "encoding185 mapping185", "record185 candle185"],
    ),
    (
        ("ranking185 encoding185 mapping185 record185 candle185 thread185", 6),
        ["ranking185", "encoding185", "mapping185", "record185", "candle185", "thread185"],
    ),
    (
        ("ranking185 encoding185 mapping185 record185 candle185 thread185", 10),
        ["ranking185", "encoding185", "mapping185", "record185", "candle185", "thread185"],
    ),
    (
        ("ranking185 encoding185 mapping185 record185 candle185 thread185", 18),
        ["ranking185", "encoding185", "mapping185", "record185", "candle185", "thread185"],
    ),
    (
        ("ranking185 encoding185 mapping185 record185 candle185 thread185", 28),
        ["ranking185 encoding185", "mapping185 record185", "candle185 thread185"],
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
